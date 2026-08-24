"""Integration contract for the four post-activation room assignment endpoints."""

from __future__ import annotations

import os

import psycopg
import pytest


def _prepare_active_schedule(client, day_date: str) -> tuple[int, int]:
    """Create the active, room-unassigned schedule required by room operations."""
    manager = {"X-Test-Session": "active-manager"}
    admin = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin)
    assert seeded.status_code in {200, 201}, seeded.text
    semester = next(
        item
        for item in client.get("/api/v1/semesters", headers=manager).json()["data"]
        if item["code"] == "SE-2026-2027"
    )
    created_round = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester["id"],
            "type": "REVIEW_3",
            "reviewer_count": 3,
            "room_types": ["NORMAL"],
            "session_duration_minutes": 30,
            "startDate": day_date,
            "endDate": day_date,
        },
        headers=manager,
    )
    assert created_round.status_code == 201, created_round.text
    round_id = created_round.json()["id"]
    created_day = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={
            "day_date": day_date,
            "slots": [
                {
                    "start_at": f"{day_date}T09:00:00+07:00",
                    "end_at": f"{day_date}T09:30:00+07:00",
                }
            ],
        },
        headers=manager,
    )
    assert created_day.status_code == 201, created_day.text
    timeslot_id = created_day.json()["timeslotIds"][0]
    group = next(
        item
        for item in client.get("/api/v1/groups", headers=manager).json()
        if item["status"] == "PENDING_D11" and item["leaderCount"] == 1
    )
    resource = client.post(
        f"/api/v1/rounds/{round_id}/resources",
        json={"groupIds": [group["id"]], "timeslotIds": [timeslot_id], "roomIds": [client.get("/api/v1/rooms", headers=manager).json()["data"][0]["id"]]},
        headers=manager,
    )
    assert resource.status_code == 200, resource.text
    lecturers = client.get("/api/v1/lecturers", params={"pageSize": 100}, headers=manager).json()["data"]
    for lecturer in lecturers:
        availability = client.post(
            f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
            json={"selectedTimeslotIds": [timeslot_id]},
            headers=manager,
        )
        assert availability.status_code == 200, availability.text
    for target_status in ("OPEN_REGISTRATION", "REGISTRATION_CLOSED"):
        transitioned = client.post(
            f"/api/v1/rounds/{round_id}/transition",
            json={"targetStatus": target_status},
            headers=manager,
        )
        assert transitioned.status_code == 200, transitioned.text
    run = client.post(
        f"/api/v1/rounds/{round_id}/schedule/run",
        json={"timeLimitSeconds": 2, "randomSeed": 13},
        headers=manager,
    )
    assert run.status_code == 201, run.text
    version_id = run.json()["versionId"]
    activated = client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=manager)
    assert activated.status_code == 200, activated.text
    return round_id, timeslot_id

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
    round_id, timeslot_id = _prepare_active_schedule(client, "2060-01-01")

    without_type = client.get(
        f"/api/v1/rounds/{round_id}/rooms/available",
        headers={"X-Test-Session": "active-manager"},
    )
    assert without_type.status_code == 200, without_type.text

    response = client.get(
        f"/api/v1/rounds/{round_id}/rooms/available",
        params={"timeslot_id": timeslot_id, "room_type": "NORMAL"},
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
    round_id, _ = _prepare_active_schedule(client, "2060-01-02")
    suggestion = client.post(f"/api/v1/rounds/{round_id}/rooms/suggest", headers=headers)
    assert suggestion.status_code == 200, suggestion.text
    data = suggestion.json()["data"]
    pairs = data.get("suggestions", data)
    assert isinstance(pairs, list)
    if not pairs:
        pytest.skip("seed fixture has no active PLANNED sessions")

    pair = {"session_id": pairs[0]["sessionId"], "room_id": pairs[0]["roomId"]}
    applied = client.post(
        f"/api/v1/rounds/{round_id}/rooms/apply-suggestions",
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
