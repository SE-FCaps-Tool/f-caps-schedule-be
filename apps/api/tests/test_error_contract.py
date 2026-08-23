import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import create_app

MANAGER = {"X-Test-Session": "active-manager"}


@pytest.fixture()
def app_with_probe():
    app = create_app()

    @app.get("/api/v1/_probe/detail-dict", tags=["system"])
    def probe_detail_dict():
        raise HTTPException(
            status_code=409,
            detail={
                "code": "HARD_CONSTRAINT_VIOLATION",
                "message": "Conflict.",
                "violations": [{"rule_code": "H1", "group_id": 7}],
            },
        )

    @app.get("/api/v1/_probe/detail-string", tags=["system"])
    def probe_detail_string():
        raise HTTPException(status_code=409, detail="Plain conflict")

    return app


def test_anonymous_request_returns_the_shared_envelope(client):
    body = client.get("/api/v1/me").json()

    assert set(body["error"]) == {"code", "message", "details"}
    assert "detail" not in body


def test_csrf_rejection_uses_a_stable_code(client):
    response = client.post(
        "/api/v1/rounds/1/transition",
        json={"target_status": "OPEN_REGISTRATION"},
        cookies={"scheduler_session": "opaque-session"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CSRF_INVALID"


def test_legacy_and_target_routes_share_one_error_shape(client):
    legacy = client.post("/api/v1/rounds", json={}, headers=MANAGER)
    target = client.post("/api/v1/semesters/1/rounds", json={}, headers=MANAGER)

    assert legacy.status_code == target.status_code == 422
    for body in (legacy.json(), target.json()):
        assert "detail" not in body
        assert body["error"]["code"] == "VALIDATION_ERROR"


def test_validation_locator_keeps_the_name_the_caller_sent(client):
    """`loc` holds submitted names, so it is data and must not be camelized.

    Since Phase 3 both spellings reach the same field, and each caller is told
    off in the spelling it used.  A field the caller omitted has no submitted
    name, so Pydantic falls back to the alias — the camelCase one.
    """

    snake = client.post("/api/v1/rounds", json={"reviewer_count": "x"}, headers=MANAGER).json()
    camel = client.post("/api/v1/rounds", json={"reviewerCount": "x"}, headers=MANAGER).json()
    omitted = client.post("/api/v1/rounds", json={}, headers=MANAGER).json()

    def fields(body: dict) -> set[str]:
        return {error["loc"][-1] for error in body["error"]["details"]["errors"]}

    assert "reviewer_count" in fields(snake)
    assert "reviewerCount" in fields(camel)
    assert "reviewerCount" in fields(omitted)


def test_validation_errors_never_echo_the_submitted_body(client):
    body = client.post(
        "/api/v1/rounds",
        json={"semester_id": 1, "secret_note": "should not come back"},
        headers=MANAGER,
    ).json()

    errors = body["error"]["details"]["errors"]
    assert errors
    assert all(set(error) <= {"type", "loc", "msg"} for error in errors)
    assert "should not come back" not in repr(body)


def test_extra_detail_keys_survive_inside_details(app_with_probe):
    body = TestClient(app_with_probe).get("/api/v1/_probe/detail-dict", headers=MANAGER).json()

    assert body["error"]["code"] == "HARD_CONSTRAINT_VIOLATION"
    assert body["error"]["details"]["violations"] == [{"ruleCode": "H1", "groupId": 7}]


def test_plain_string_detail_becomes_the_message(app_with_probe):
    body = TestClient(app_with_probe).get("/api/v1/_probe/detail-string", headers=MANAGER).json()

    assert body["error"] == {"code": "HTTP_ERROR", "message": "Plain conflict", "details": {}}


def test_every_api_operation_declares_the_error_envelope(client):
    spec = client.app.openapi()
    ref = {"$ref": "#/components/schemas/ApiErrorEnvelope"}

    assert "ApiErrorEnvelope" in spec["components"]["schemas"]
    for path, operations in spec["paths"].items():
        if not path.startswith("/api/"):
            continue
        for method, operation in operations.items():
            responses = operation["responses"]
            assert responses["default"]["content"]["application/json"]["schema"] == ref, (path, method)
            if "422" in responses:
                assert responses["422"]["content"]["application/json"]["schema"] == ref, (path, method)
