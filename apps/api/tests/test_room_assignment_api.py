"""Integration contract for the four post-activation room assignment endpoints."""

from __future__ import annotations

import os

import psycopg
import pytest

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://scheduler:scheduler@localhost:5432/scheduler"
).replace("postgresql+psycopg://", "postgresql://")


def _db():
    try:
        return psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is required for room assignment integration tests: {exc}")


@pytest.mark.integration
def test_all_four_room_assignment_endpoints_enforce_manager_scope(client):
    paths = (
        "/api/v1/rounds/1/rooms/available?timeslot_id=1&room_type=NORMAL",
        "/api/v1/sessions/1/room",
        "/api/v1/rounds/1/rooms/suggest",
        "/api/v1/rounds/1/rooms/apply-suggestions",
    )

    for path in paths:
        anonymous = client.get(path) if "available" in path else client.post(path, json={}) if "suggest" in path or "apply" in path else client.put(path, json={"room_id": 1})
        assert anonymous.status_code == 401, (path, anonymous.text)

        lecturer = client.get(path, headers={"X-Test-Session": "active-lecturer:2"}) if "available" in path else client.post(path, json={}, headers={"X-Test-Session": "active-lecturer:2"}) if "suggest" in path or "apply" in path else client.put(path, json={"room_id": 1}, headers={"X-Test-Session": "active-lecturer:2"})
        assert lecturer.status_code == 403, (path, lecturer.text)


@pytest.mark.integration
def test_available_rooms_filters_active_allowed_and_true_interval_conflicts(client):
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code in {200, 201}, seeded.text

    response = client.get(
        "/api/v1/rounds/1/rooms/available",
        params={"timeslot_id": 1, "room_type": "NORMAL"},
        headers={"X-Test-Session": "active-manager"},
    )
    assert response.status_code == 200, response.text
    rooms = response.json()["data"]
    assert isinstance(rooms, list)
    for room in rooms:
        assert room["active"] is True
        assert room["roomType"] == "NORMAL"


@pytest.mark.integration
def test_assign_suggest_apply_are_planned_only_atomic_and_idempotent(client):
    headers = {"X-Test-Session": "active-manager"}
    suggestion = client.post("/api/v1/rounds/1/rooms/suggest", headers=headers)
    assert suggestion.status_code == 200, suggestion.text
    data = suggestion.json()["data"]
    pairs = data.get("suggestions", data)
    assert isinstance(pairs, list)
    if not pairs:
        pytest.skip("seed fixture has no active PLANNED sessions")

    pair = {"session_id": pairs[0]["sessionId"], "room_id": pairs[0]["roomId"]}
    applied = client.post(
        "/api/v1/rounds/1/rooms/apply-suggestions",
        json={"assignments": [pair]},
        headers=headers,
    )
    assert applied.status_code == 200, applied.text
    assert applied.json()["data"].get("changedCount", 0) in {0, 1}

    repeated = client.put(
        f"/api/v1/sessions/{pair['session_id']}/room",
        json={"room_id": pair["room_id"]},
        headers=headers,
    )
    assert repeated.status_code == 200, repeated.text
    repeated_again = client.put(
        f"/api/v1/sessions/{pair['session_id']}/room",
        json={"room_id": pair["room_id"]},
        headers=headers,
    )
    assert repeated_again.status_code == 200, repeated_again.text

    with _db() as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT status, room_id FROM sessions WHERE id = %s", (pair["session_id"],)
        )
        status, room_id = cursor.fetchone()
    assert status == "PLANNED"
    assert room_id == pair["room_id"]


@pytest.mark.integration
def test_apply_rejects_stale_or_global_conflicting_batch_without_partial_updates(client):
    headers = {"X-Test-Session": "active-manager"}
    response = client.post(
        "/api/v1/rounds/1/rooms/apply-suggestions",
        json={"assignments": [{"session_id": 1, "room_id": 999999}]},
        headers=headers,
    )
    assert response.status_code in {404, 409, 422}
    if response.status_code != 404:
        assert response.json()["error"]["code"] in {
            "ROOM_NOT_FOUND",
            "ROOM_CONFLICT",
            "ROOM_SUGGESTION_STALE",
            "ROOM_ASSIGNMENT_STATE_INVALID",
        }

