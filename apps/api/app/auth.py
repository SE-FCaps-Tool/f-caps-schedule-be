from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import Settings, get_settings
from .database import get_db


@dataclass(frozen=True)
class CurrentUser:
    role: str
    status: str = "active"
    account_id: int | None = None


def get_current_user(
    request: Request,
    test_session: Annotated[str | None, Header(alias="X-Test-Session")] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> CurrentUser:
    """Temporary local vertical-slice auth seam until the login UI is implemented."""
    test_roles = {
        "active-admin": "ADMIN",
        "active-manager": "MANAGER",
        "active-lecturer": "LECTURER",
        "active-student": "STUDENT",
    }
    if settings.app_env == "test" and test_session:
        role, _, account = test_session.partition(":")
        if role in test_roles:
            return CurrentUser(role=test_roles[role], account_id=int(account) if account.isdigit() else None)
    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token:
        import hashlib

        token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        row = db.execute(
            text(
                "SELECT s.account_id, a.status, ar.role FROM auth_sessions s "
                "JOIN accounts a ON a.id = s.account_id JOIN account_roles ar ON ar.account_id = a.id "
                "WHERE s.token_hash = :token_hash AND s.revoked_at IS NULL AND s.expires_at > now() "
                "AND s.last_seen_at > now() - (:idle_minutes * interval '1 minute') "
                "ORDER BY ar.role LIMIT 1"
            ),
            {"token_hash": token_hash, "idle_minutes": settings.session_idle_minutes},
        ).mappings().one_or_none()
        if row is not None and str(row["status"]) == "ACTIVE":
            db.execute(text("UPDATE auth_sessions SET last_seen_at = now() WHERE token_hash = :token_hash"), {"token_hash": token_hash})
            db.commit()
            return CurrentUser(role=str(row["role"]), status="active", account_id=row["account_id"])
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )
