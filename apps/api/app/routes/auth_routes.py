import base64
import hashlib
import json
import math
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.auth import CurrentUser, get_current_user
from app.config import Settings, get_settings
from app.database import get_db
from app.response_models import LoginResponse, LogoutResponse, MeResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
Db = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
User = Annotated[CurrentUser, Depends(get_current_user)]
password_hasher = PasswordHasher()
GOOGLE_STATE_COOKIE = "scheduler_google_state"
GOOGLE_PKCE_COOKIE = "scheduler_google_pkce"
GOOGLE_NONCE_COOKIE = "scheduler_google_nonce"
GOOGLE_COOKIE_PATH = "/api/v1/auth/google"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


class LoginPayload(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginPayload, response: Response, request: Request, db: Db, settings: SettingsDep) -> dict[str, str]:
    client_host = request.client.host if request.client else None
    throttle = _record_login_attempt(db, payload.email, client_host)
    if throttle["blocked"]:
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.", headers={"Retry-After": str(throttle["retry_after"])})
    row = db.execute(
        text(
            "SELECT a.id, a.password_hash, a.status, ar.role FROM accounts a "
            "JOIN account_roles ar ON ar.account_id = a.id WHERE lower(a.email) = lower(:email) "
            "ORDER BY ar.role LIMIT 1"
        ),
        {"email": payload.email.strip()},
    ).mappings().one_or_none()
    if row is None or str(row["status"]) != "ACTIVE":
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        password_hasher.verify(row["password_hash"], payload.password)
    except (VerificationError, VerifyMismatchError, TypeError) as exc:
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials") from exc
    db.execute(text("DELETE FROM auth_login_throttles WHERE identifier = :identifier"), {"identifier": _login_identifier(payload.email, client_host)})
    expires = _create_session(db, row["id"], str(row["role"]), response, settings, provider="password")
    return {"role": str(row["role"]), "expires_at": expires.isoformat()}


@router.get("/google/start", include_in_schema=True)
def google_start(settings: SettingsDep) -> RedirectResponse:
    _require_google_configuration(settings)
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    nonce = secrets.token_urlsafe(32)
    code_challenge = _pkce_challenge(code_verifier)
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "online",
            "prompt": "select_account",
        }
    )
    response = RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}", status_code=status.HTTP_303_SEE_OTHER)
    secure = settings.app_env not in {"development", "test"}
    for name, value in ((GOOGLE_STATE_COOKIE, state), (GOOGLE_PKCE_COOKIE, code_verifier), (GOOGLE_NONCE_COOKIE, nonce)):
        response.set_cookie(name, value, httponly=True, secure=secure, samesite="lax", max_age=600, path=GOOGLE_COOKIE_PATH)
    return response


@router.get("/google/callback", include_in_schema=True)
def google_callback(
    request: Request,
    db: Db,
    settings: SettingsDep,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    response = _frontend_redirect(settings)
    _clear_google_cookies(response)
    if error:
        return _oauth_error_redirect(settings, "google_access_denied")
    expected_state = request.cookies.get(GOOGLE_STATE_COOKIE)
    code_verifier = request.cookies.get(GOOGLE_PKCE_COOKIE)
    expected_nonce = request.cookies.get(GOOGLE_NONCE_COOKIE)
    if not code or not state or not expected_state or not secrets.compare_digest(state, expected_state):
        return _oauth_error_redirect(settings, "oauth_state_invalid")
    if not code_verifier or not expected_nonce:
        return _oauth_error_redirect(settings, "oauth_session_expired")
    try:
        claims = _verify_google_code(code, code_verifier, expected_nonce, settings)
    except GoogleOAuthError:
        return _oauth_error_redirect(settings, "google_verification_failed")

    account = db.execute(
        text("SELECT id, status FROM accounts WHERE lower(email) = :email"),
        {"email": claims["email"]},
    ).mappings().one_or_none()
    if account is None:
        db.rollback()
        return _oauth_error_redirect(settings, "account_not_provisioned")
    if str(account["status"]) != "ACTIVE":
        db.rollback()
        return _oauth_error_redirect(settings, "account_inactive")

    account_id = int(account["id"])
    identity = db.execute(
        text("SELECT account_id FROM auth_identities WHERE provider = 'google' AND subject = :subject"),
        {"subject": claims["subject"]},
    ).scalar_one_or_none()
    if identity is not None and int(identity) != account_id:
        db.rollback()
        return _oauth_error_redirect(settings, "google_identity_conflict")
    linked_identity = db.execute(
        text("SELECT subject FROM auth_identities WHERE provider = 'google' AND account_id = :account_id"),
        {"account_id": account_id},
    ).scalar_one_or_none()
    if linked_identity is not None and str(linked_identity) != claims["subject"]:
        db.rollback()
        return _oauth_error_redirect(settings, "google_account_already_linked")
    role = db.execute(
        text("SELECT role FROM account_roles WHERE account_id = :account_id ORDER BY role LIMIT 1"),
        {"account_id": account_id},
    ).scalar_one_or_none()
    if role is None:
        db.rollback()
        return _oauth_error_redirect(settings, "account_role_missing")
    try:
        if identity is None:
            db.execute(
                text(
                    "INSERT INTO auth_identities (account_id, provider, subject, email) "
                    "VALUES (:account_id, 'google', :subject, :email)"
                ),
                {"account_id": account_id, "subject": claims["subject"], "email": claims["email"]},
            )
        else:
            db.execute(
                text("UPDATE auth_identities SET email = :email, last_login_at = now() WHERE provider = 'google' AND subject = :subject"),
                {"email": claims["email"], "subject": claims["subject"]},
            )
        _create_session(db, account_id, str(role), response, settings, provider="google")
    except IntegrityError:
        db.rollback()
        return _oauth_error_redirect(settings, "google_identity_conflict")
    return response


@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response, request: Request, db: Db, settings: SettingsDep) -> dict[str, str]:
    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token:
        row = db.execute(text("UPDATE auth_sessions SET revoked_at = now() WHERE token_hash = :token_hash RETURNING account_id"), {"token_hash": _hash(session_token)}).mappings().one_or_none()
        if row is not None:
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'LOGOUT', 'account', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": row["account_id"], "entity_id": str(row["account_id"]), "after_json": '{"session": "revoked"}'})
        db.commit()
    cookie_domain = settings.cookie_domain or None
    # scheduler_session remains host-only, so delete it without a Domain
    # attribute even when the CSRF cookie is shared with the FE subdomain.
    response.delete_cookie(settings.session_cookie_name)
    # Remove both the old host-only cookie and the cross-subdomain cookie so
    # an existing browser cannot send two scheduler_csrf values after rollout.
    response.delete_cookie("scheduler_csrf")
    if cookie_domain:
        response.delete_cookie("scheduler_csrf", domain=cookie_domain)
    return {"status": "signed_out"}


@router.get("/me", response_model=MeResponse)
def authenticated_me(user: User) -> dict[str, str | int | None]:
    return {"role": user.role, "status": user.status, "account_id": user.account_id}


class GoogleOAuthError(Exception):
    """Raised when Google authorization data cannot be trusted or exchanged."""


def _require_google_configuration(settings: Settings) -> None:
    if not settings.google_client_id or not settings.google_client_secret or not settings.google_redirect_uri:
        raise HTTPException(status_code=503, detail={"code": "GOOGLE_OAUTH_NOT_CONFIGURED", "message": "Google login is not configured."})


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def _verify_google_code(code: str, code_verifier: str, nonce: str, settings: Settings) -> dict[str, str]:
    try:
        body = urlencode(
            {
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            }
        ).encode()
        request = UrlRequest(GOOGLE_TOKEN_URL, data=body, headers={"Accept": "application/json"}, method="POST")
        with urlopen(request, timeout=10) as token_response:
            token_payload = json.loads(token_response.read().decode())
        id_token_value = token_payload.get("id_token")
        if not isinstance(id_token_value, str):
            raise GoogleOAuthError("Google did not return an ID token")
        claims = google_id_token.verify_oauth2_token(id_token_value, GoogleRequest(), settings.google_client_id)
    except (GoogleAuthError, HTTPError, URLError, OSError, ValueError, TypeError, GoogleOAuthError) as exc:
        raise GoogleOAuthError("Google authorization failed") from exc
    if claims.get("nonce") != nonce or claims.get("email_verified") is not True:
        raise GoogleOAuthError("Google identity proof is invalid")
    subject = claims.get("sub")
    email = claims.get("email")
    if not isinstance(subject, str) or not subject or not isinstance(email, str) or not email.strip():
        raise GoogleOAuthError("Google identity is incomplete")
    return {
        "subject": subject,
        "email": email.strip().lower(),
        "display_name": str(claims.get("name") or email.strip()),
    }


def _create_session(db: Session, account_id: int, role: str, response: Response, settings: Settings, provider: str) -> datetime:
    token = secrets.token_urlsafe(48)
    csrf_token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(hours=settings.session_absolute_hours)
    db.execute(
        text(
            "INSERT INTO auth_sessions (account_id, token_hash, csrf_token_hash, expires_at) "
            "VALUES (:account_id, :token_hash, :csrf_token_hash, :expires_at)"
        ),
        {"account_id": account_id, "token_hash": _hash(token), "csrf_token_hash": _hash(csrf_token), "expires_at": expires},
    )
    db.execute(
        text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'LOGIN_SUCCESS', 'account', :entity_id, CAST(:after_json AS JSONB))"),
        {"actor_id": account_id, "entity_id": str(account_id), "after_json": json.dumps({"session": "created", "provider": provider})},
    )
    db.commit()
    secure = settings.app_env not in {"development", "test"}
    cookie_domain = settings.cookie_domain or None
    response.set_cookie(
        settings.session_cookie_name,
        token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.session_absolute_hours * 3600,
    )
    response.set_cookie(
        "scheduler_csrf",
        csrf_token,
        httponly=False,
        secure=secure,
        samesite="lax",
        domain=cookie_domain,
        max_age=settings.session_absolute_hours * 3600,
    )
    return expires


def _frontend_redirect(settings: Settings) -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url.rstrip('/')}/auth/callback", status_code=status.HTTP_303_SEE_OTHER)


def _oauth_error_redirect(settings: Settings, code: str) -> RedirectResponse:
    response = RedirectResponse(
        f"{settings.frontend_url.rstrip('/')}/login?{urlencode({'oauth_error': code})}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    _clear_google_cookies(response)
    return response


def _clear_google_cookies(response: Response) -> None:
    for name in (GOOGLE_STATE_COOKIE, GOOGLE_PKCE_COOKIE, GOOGLE_NONCE_COOKIE):
        response.delete_cookie(name, path=GOOGLE_COOKIE_PATH)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _login_identifier(email: str, client_host: str | None) -> str:
    return _hash(f"{email.strip().lower()}|{client_host or 'unknown'}")


def _record_login_attempt(db: Session, email: str, client_host: str | None) -> dict[str, int | bool]:
    identifier = _login_identifier(email, client_host)
    row = db.execute(
        text(
            "INSERT INTO auth_login_throttles (identifier, window_started_at, attempts, updated_at) VALUES (:identifier, now(), 1, now()) "
            "ON CONFLICT (identifier) DO UPDATE SET "
            "attempts = CASE WHEN auth_login_throttles.window_started_at <= now() - interval '15 minutes' THEN 1 ELSE auth_login_throttles.attempts + 1 END, "
            "window_started_at = CASE WHEN auth_login_throttles.window_started_at <= now() - interval '15 minutes' THEN now() ELSE auth_login_throttles.window_started_at END, "
            "updated_at = now() RETURNING attempts, window_started_at"
        ),
        {"identifier": identifier},
    ).mappings().one()
    now = datetime.now(UTC)
    retry_after = max(1, math.ceil(((row["window_started_at"] + timedelta(minutes=15)) - now).total_seconds()))
    return {"blocked": int(row["attempts"]) > 10, "retry_after": retry_after}
