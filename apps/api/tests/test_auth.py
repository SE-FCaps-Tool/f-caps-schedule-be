def test_protected_me_endpoint_rejects_anonymous_user(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_protected_me_endpoint_accepts_active_session(client):
    response = client.get(
        "/api/v1/me",
        headers={"X-Test-Session": "active-admin"},
    )

    assert response.status_code == 200
    assert response.json() == {"role": "ADMIN", "status": "active"}


def test_cookie_mutation_requires_double_submit_csrf(client):
    response = client.post(
        "/api/v1/rounds/1/transition",
        json={"target_status": "OPEN_REGISTRATION"},
        cookies={"scheduler_session": "opaque-session"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF validation failed"
