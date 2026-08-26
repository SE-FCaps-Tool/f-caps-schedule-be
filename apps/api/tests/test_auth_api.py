import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine


def _create_multi_role_account(client, admin_headers) -> tuple[int, str, str]:
    """Creates an account with MANAGER + ADMIN roles. Returns (account_id, email, password)."""
    password = "LongEnoughDemo!2026"
    email = f"multi-role-{uuid4().hex[:8]}@example.test"
    created = client.post(
        "/api/v1/accounts",
        json={"email": email, "display_name": "Multi Role", "password": password, "role": "MANAGER"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    account_id = created.json()["id"]
    assigned = client.post(
        f"/api/v1/accounts/{account_id}/roles",
        json={"role": "ADMIN", "reason": "test fixture: multi-role account"},
        headers=admin_headers,
    )
    assert assigned.status_code == 200, assigned.text
    return account_id, email, password


@pytest.mark.integration
def test_local_login_sets_session_and_csrf_and_logout_revokes_session(client):
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@gmail.com", "password": "12345@Abc"},
    )
    assert login.status_code == 200, login.text
    assert "scheduler_session" in login.cookies
    assert "scheduler_csrf" in login.cookies

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["role"] == "MANAGER"
    assert me.json()["accountId"] is not None
    assert me.json()["email"] == "manager@gmail.com"
    assert me.json()["displayName"]

    blocked = client.post("/api/v1/rounds/1/transition", json={"target_status": "OPEN_REGISTRATION"})
    assert blocked.status_code == 403

    csrf = client.cookies.get("scheduler_csrf")
    allowed = client.post(
        "/api/v1/rounds/1/transition",
        json={"target_status": "OPEN_REGISTRATION"},
        headers={"X-CSRF-Token": csrf},
    )
    assert allowed.status_code in {200, 404, 422}

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.integration
def test_login_throttle_returns_retry_after_after_repeated_failures(client):
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text
    email = f"missing-{uuid4().hex}@example.test"
    for _ in range(10):
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
        assert response.status_code == 401
    blocked = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


@pytest.mark.integration
def test_switch_role_creates_new_session_and_revokes_old(client):
    admin_headers = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin_headers)
    assert seeded.status_code == 201, seeded.text
    _account_id, email, password = _create_multi_role_account(client, admin_headers)

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    assert login.json()["requiresRoleSelection"] is True
    assert set(login.json()["availableRoles"]) == {"ADMIN", "MANAGER"}

    picked = client.post("/api/v1/auth/select-role", json={"role": "MANAGER"})
    assert picked.status_code == 200, picked.text
    assert picked.json()["role"] == "MANAGER"
    old_session_cookie = client.cookies.get("scheduler_session")
    assert old_session_cookie
    assert client.get("/api/v1/auth/me").json()["role"] == "MANAGER"

    csrf = client.cookies.get("scheduler_csrf")
    switched = client.post(
        "/api/v1/auth/select-role",
        json={"role": "ADMIN"},
        headers={"X-CSRF-Token": csrf},
    )
    assert switched.status_code == 200, switched.text
    assert switched.json()["role"] == "ADMIN"
    assert client.get("/api/v1/auth/me").json()["role"] == "ADMIN"

    # The old session must be dead, not just superseded client-side.
    stale = client.get("/api/v1/auth/me", cookies={"scheduler_session": old_session_cookie})
    assert stale.status_code == 401, stale.text


@pytest.mark.integration
def test_switch_role_to_unowned_role_is_rejected_and_keeps_session(client):
    admin_headers = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin_headers)
    assert seeded.status_code == 201, seeded.text
    _account_id, email, password = _create_multi_role_account(client, admin_headers)

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    picked = client.post("/api/v1/auth/select-role", json={"role": "MANAGER"})
    assert picked.status_code == 200, picked.text

    csrf = client.cookies.get("scheduler_csrf")
    rejected = client.post(
        "/api/v1/auth/select-role",
        json={"role": "STUDENT"},
        headers={"X-CSRF-Token": csrf},
    )
    assert rejected.status_code == 403, rejected.text
    assert rejected.json()["error"]["code"] == "ROLE_NOT_ASSIGNED"

    # A rejected switch attempt must not touch the caller's live session.
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["role"] == "MANAGER"


@pytest.mark.integration
def test_relogin_with_challenge_revokes_a_still_live_session(client):
    admin_headers = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin_headers)
    assert seeded.status_code == 201, seeded.text
    _account_id, email, password = _create_multi_role_account(client, admin_headers)

    first_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert first_login.status_code == 200, first_login.text
    first_pick = client.post("/api/v1/auth/select-role", json={"role": "MANAGER"})
    assert first_pick.status_code == 200, first_pick.text
    first_session_cookie = client.cookies.get("scheduler_session")
    assert first_session_cookie

    # Re-authenticate from scratch while the first session is still live —
    # mints a fresh login_challenge without ever calling /logout. The first
    # session's cookie is still in the jar at this point, so csrf_guard now
    # requires X-CSRF-Token on select-role too (it only skips CSRF when no
    # session cookie exists yet — true for a first-ever login, not this
    # already-logged-in-elsewhere case). The real FE client attaches this
    # header automatically for every mutating call when the CSRF cookie is
    # present (lib/api/core.ts), regardless of call site.
    second_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert second_login.status_code == 200, second_login.text
    csrf = client.cookies.get("scheduler_csrf")
    second_pick = client.post(
        "/api/v1/auth/select-role",
        json={"role": "ADMIN"},
        headers={"X-CSRF-Token": csrf},
    )
    assert second_pick.status_code == 200, second_pick.text

    # The first session must not survive as an orphan under its own token.
    stale = client.get("/api/v1/auth/me", cookies={"scheduler_session": first_session_cookie})
    assert stale.status_code == 401, stale.text


@pytest.mark.integration
def test_heartbeat_write_only_lands_after_the_configured_window(client):
    admin_headers = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin_headers)
    assert seeded.status_code == 201, seeded.text
    login = client.post("/api/v1/auth/login", json={"email": "manager@gmail.com", "password": "12345@Abc"})
    assert login.status_code == 200, login.text
    session_token = client.cookies.get("scheduler_session")
    assert session_token
    token_hash = hashlib.sha256(session_token.encode()).hexdigest()

    settings = get_settings()
    backdated = datetime.now(UTC) - timedelta(seconds=settings.session_heartbeat_seconds + 30)
    with Session(get_engine(settings.database_url)) as db, db.begin():
        db.execute(
            text("UPDATE auth_sessions SET last_seen_at = :backdated WHERE token_hash = :token_hash"),
            {"backdated": backdated, "token_hash": token_hash},
        )

    assert client.get("/api/v1/auth/me").status_code == 200
    with Session(get_engine(settings.database_url)) as db:
        after_first_hit = db.execute(
            text("SELECT last_seen_at FROM auth_sessions WHERE token_hash = :token_hash"),
            {"token_hash": token_hash},
        ).scalar_one()
    # Heartbeat window had elapsed -> the conditional UPDATE's rowcount > 0
    # branch ran and advanced last_seen_at (not just the read/idle-check path).
    assert after_first_hit > backdated

    assert client.get("/api/v1/auth/me").status_code == 200
    with Session(get_engine(settings.database_url)) as db:
        after_second_hit = db.execute(
            text("SELECT last_seen_at FROM auth_sessions WHERE token_hash = :token_hash"),
            {"token_hash": token_hash},
        ).scalar_one()
    # Immediately re-hit, still inside the window -> throttled: no write
    # (the rowcount == 0 / rollback branch), same as before this change.
    assert after_second_hit == after_first_hit
