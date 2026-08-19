from uuid import uuid4

import pytest


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
    assert me.json()["account_id"] is not None

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
