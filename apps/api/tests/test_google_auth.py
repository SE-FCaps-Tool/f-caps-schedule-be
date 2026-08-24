from __future__ import annotations

import base64
import hashlib

from app.config import Settings
from app.routes.auth_routes import _pkce_challenge, google_start


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
