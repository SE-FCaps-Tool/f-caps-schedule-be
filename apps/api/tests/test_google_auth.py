from __future__ import annotations

import base64
import hashlib

from app.config import Settings
from app.routes.auth_routes import (
    _frontend_redirect,
    _pkce_challenge,
    google_callback,
    google_start,
)


def test_pkce_challenge_uses_base64url_sha256_without_padding() -> None:
    verifier = "test-verifier"
    expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

    assert _pkce_challenge(verifier) == expected


def test_google_start_requires_server_configuration() -> None:
    settings = Settings(app_env="test")

    try:
        google_start(settings)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 503
        assert exc.detail["code"] == "GOOGLE_OAUTH_NOT_CONFIGURED"
    else:
        raise AssertionError("Google start should reject missing OAuth configuration")


def test_google_start_redirects_with_pkce_and_oidc_parameters() -> None:
    response = google_start(
        Settings(
            app_env="test",
            google_client_id="client-id",
            google_client_secret="client-secret",
            google_redirect_uri="http://localhost:8000/api/v1/auth/google/callback",
        )
    )

    assert response.status_code == 303
    assert "accounts.google.com/o/oauth2/v2/auth" in response.headers["location"]
    assert "code_challenge_method=S256" in response.headers["location"]
    assert "nonce=" in response.headers["location"]


def test_google_start_scopes_flow_cookies_to_shared_parent_domain(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routes.auth_routes._require_google_configuration",
        lambda _: None,
    )
    response = google_start(
        Settings(
            app_env="production",
            cookie_domain=".f-caps.net",
        )
    )

    set_cookie_headers = response.headers.getlist("set-cookie")

    assert len(set_cookie_headers) == 3
    assert all("Domain=.f-caps.net" in header for header in set_cookie_headers)
    assert all("Path=/api/v1/auth/google" in header for header in set_cookie_headers)


def test_google_callback_success_path_passes_settings_to_cookie_cleanup(monkeypatch) -> None:
    class FakeResult:
        def __init__(self, *, mapping=None, scalar=None) -> None:
            self.mapping = mapping
            self.scalar = scalar

        def mappings(self):
            return self

        def one_or_none(self):
            return self.mapping

        def scalar_one_or_none(self):
            return self.scalar

    class FakeDb:
        def __init__(self) -> None:
            self.results = [
                FakeResult(mapping={"id": 1, "status": "ACTIVE"}),
                FakeResult(),
                FakeResult(scalar=None),
                FakeResult(scalar=None),
                FakeResult(),
            ]

        def execute(self, *args, **kwargs):
            return self.results.pop(0)

        def rollback(self) -> None:
            pass

    class FakeRequest:
        def __init__(self) -> None:
            self.cookies = {
                "scheduler_google_state": "state",
                "scheduler_google_pkce": "verifier",
                "scheduler_google_nonce": "nonce",
            }

    monkeypatch.setattr(
        "app.routes.auth_routes._verify_google_code",
        lambda *args: {"subject": "google-subject", "email": "person@example.com", "display_name": "Person"},
    )
    monkeypatch.setattr("app.routes.auth_routes._roles_for_account", lambda *args: ["ADMIN"])
    monkeypatch.setattr("app.routes.auth_routes._create_session", lambda *args, **kwargs: None)

    response = google_callback(
        FakeRequest(),
        FakeDb(),
        Settings(
            app_env="production",
            cookie_domain=".f-caps.net",
            frontend_url="https://schedule.f-caps.net",
        ),
        code="authorization-code",
        state="state",
    )

    assert response.status_code == 303
    assert response.headers["location"] == "https://schedule.f-caps.net/auth/callback?roles=ADMIN"


def test_frontend_redirect_carries_server_resolved_roles() -> None:
    response = _frontend_redirect(
        Settings(app_env="test", frontend_url="https://schedule.example.com"),
        ["ADMIN", "MANAGER"],
    )

    assert response.headers["location"] == "https://schedule.example.com/auth/callback?roles=ADMIN%2CMANAGER"
