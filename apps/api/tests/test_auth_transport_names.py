"""Authentication transport names are protocol constants, not JSON fields."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import get_current_user
from app.config import Settings


def _request_without_cookies() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/me",
            "headers": [],
            "query_string": b"",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
    )


@pytest.mark.integration
def test_login_keeps_protocol_cookie_names_and_csrf_guard(client):
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@gmail.com", "password": "12345@Abc"},
    )
    assert login.status_code == 200, login.text
    assert "scheduler_session" in login.cookies
    assert "scheduler_csrf" in login.cookies

    set_cookie_headers = login.headers.get_list("set-cookie")
    session_cookie = next(header for header in set_cookie_headers if header.startswith("scheduler_session="))
    csrf_cookie = next(header for header in set_cookie_headers if header.startswith("scheduler_csrf="))
    assert "HttpOnly" in session_cookie
    assert "HttpOnly" not in csrf_cookie

    blocked = client.post(
        "/api/v1/rounds/1/transition",
        json={"target_status": "OPEN_REGISTRATION"},
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "CSRF_INVALID"


def test_test_session_header_is_disabled_outside_test_environment():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            _request_without_cookies(),
            "active-admin",
            Settings(app_env="development"),
            None,
        )

    assert exc_info.value.status_code == 401
