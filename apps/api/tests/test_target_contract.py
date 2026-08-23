"""Contract tests for the shared target boundary (Phase 1 of
plans/api-contract-alignment-fast-fix): camelCase response bodies and the
spec's {"error": {code, message, details}} envelope on target-tagged routes,
while legacy routes keep their existing {"detail": ...} shape.
"""

from app.api_contract import camelize, success_payload


def test_camelize_converts_nested_snake_case_keys():
    payload = {
        "round_id": 1,
        "group_preference_deadline": "2026-01-01",
        "items": [{"session_id": 2, "start_at": "2026-01-01T09:00:00"}],
        "already_camel": {"roomId": 3},
    }
    result = camelize(payload)
    assert result == {
        "roundId": 1,
        "groupPreferenceDeadline": "2026-01-01",
        "items": [{"sessionId": 2, "startAt": "2026-01-01T09:00:00"}],
        "alreadyCamel": {"roomId": 3},
    }


def test_camelize_is_idempotent_on_already_camel_keys():
    assert camelize({"roomId": 1, "code": "S01"}) == {"roomId": 1, "code": "S01"}


def test_success_payload_camelizes_data_and_meta():
    body = success_payload([{"session_id": 1}], meta={"page": 1, "page_size": 20, "total": 1})
    assert body == {"data": [{"sessionId": 1}], "meta": {"page": 1, "pageSize": 20, "total": 1}}


_VALID_ROUND_BODY = {
    "name": "Review 1",
    "type": "REVIEW_1",
    "durationMinutes": 60,
    "reviewerCount": 2,
    "maxGroupsPerTimeslot": 3,
    "registrationDeadline": "2026-08-09T22:31:00+07:00",
    "groupSelectionMode": False,
    "resultOwnerMode": False,
    "roomTypes": ["NORMAL"],
    "days": [{"date": "2026-08-20", "slots": [{"startTime": "08:00", "endTime": "09:00"}]}],
}


def test_target_route_403_uses_structured_error_envelope(client):
    response = client.post(
        "/api/v1/semesters/1/rounds",
        json=_VALID_ROUND_BODY,
        headers={"X-Test-Session": "active-lecturer"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "error" in body, body
    assert body["error"]["code"] == "AUTH_FORBIDDEN"
    assert "message" in body["error"]
    assert "detail" not in body


def test_target_route_422_uses_structured_error_envelope(client):
    response = client.post(
        "/api/v1/semesters/1/rounds",
        json={"name": "x"},
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 422
    body = response.json()
    assert "error" in body, body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "detail" not in body


def test_legacy_route_403_uses_the_shared_error_envelope(client):
    response = client.post(
        "/api/v1/admin/seed-fixture",
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "detail" not in body, body
    assert set(body["error"]) == {"code", "message", "details"}
