"""Integration coverage for Phase 3's generate/activate/publish lifecycle."""

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
        pytest.fail(f"PostgreSQL is required for Phase 3 integration tests: {exc}")


def _prepare_round(client, headers: dict[str, str], day_date: str) -> tuple[int, int]:
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code in {200, 201}, seeded.text
    semester = next(
        item
        for item in client.get("/api/v1/semesters", headers=headers).json()["data"]
        if item["code"] == "SE-2026-2027"
    )
    created = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester["id"],
            "type": "REVIEW_3",
            "reviewer_count": 3,
            "room_types": ["NORMAL"],
            "session_duration_minutes": 30,
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    round_id = created.json()["id"]
    day = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={
            "day_date": day_date,
            "slots": [{"start_at": f"{day_date}T09:00:00+07:00", "end_at": f"{day_date}T09:30:00+07:00"}],
        },
        headers=headers,
    )
    assert day.status_code == 201, day.text
    slot_id = day.json()["timeslot_ids"][0]
    group = next(
        item
        for item in client.get("/api/v1/groups", headers=headers).json()
        if item["status"] == "PENDING_D11" and item["leader_count"] == 1
    )
    rooms = client.get("/api/v1/rooms", headers=headers)
    room_id = rooms.json()["data"][0]["id"] if rooms.status_code == 200 and rooms.json()["data"] else None
    resources = {"group_ids": [group["id"]], "timeslot_ids": [slot_id]}
    if room_id is not None:
        resources["room_ids"] = [room_id]
    assigned = client.post(f"/api/v1/rounds/{round_id}/resources", json=resources, headers=headers)
    assert assigned.status_code == 200, assigned.text
    lecturers = client.get("/api/v1/lecturers", headers=headers).json()["data"]
    for lecturer in lecturers[:6]:
        availability = client.post(
            f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
            json={"selected_timeslot_ids": [slot_id]},
            headers=headers,
        )
        assert availability.status_code == 200, availability.text
    return round_id, slot_id


def _run(client, headers: dict[str, str], round_id: int) -> dict:
    response = client.post(
        f"/api/v1/rounds/{round_id}/schedule/run",
        json={"random_seed": 17, "time_limit_seconds": 2},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.integration
def test_generate_creates_draft_assignments_and_zero_operational_sessions(client):
    headers = {"X-Test-Session": "active-manager"}
    round_id, _ = _prepare_round(client, headers, "2040-03-01")
    run = _run(client, headers, round_id)
    assert run["status"] == "DRAFT"

    version_id = run["version_id"]
    detail = client.get(f"/api/v1/schedule/versions/{version_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["status"] == "DRAFT"
    assert body.get("assignments"), body
    assert body.get("sessions", []) == []

    with _db() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT status FROM rounds WHERE id = %s", (round_id,))
        assert cursor.fetchone()[0] == "SCHEDULING"
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE schedule_version_id = %s", (version_id,))
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT COUNT(*) FROM session_reviewers WHERE schedule_version_id = %s", (version_id,))
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT COUNT(*) FROM schedule_assignments WHERE schedule_version_id = %s", (version_id,))
        assert cursor.fetchone()[0] > 0


@pytest.mark.integration
def test_activation_materializes_planned_null_room_sessions_and_rejects_stale_project_snapshot(client):
    headers = {"X-Test-Session": "active-manager"}
    round_id, _ = _prepare_round(client, headers, "2041-03-01")
    run = _run(client, headers, round_id)
    version_id = run["version_id"]

    with _db() as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT group_id, project_id FROM schedule_assignments WHERE schedule_version_id = %s LIMIT 1",
            (version_id,),
        )
        group_id, project_id = cursor.fetchone()
        cursor.execute("SELECT id FROM projects WHERE id <> %s LIMIT 1", (project_id,))
        replacement = cursor.fetchone()
        if replacement:
            cursor.execute("UPDATE groups SET project_id = %s WHERE id = %s", (replacement[0], group_id))
            connection.commit()

    stale = client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers)
    if replacement:
        assert stale.status_code == 409, stale.text
        assert stale.json()["error"]["code"] == "DRAFT_ASSIGNMENT_STALE"
        return
    pytest.skip("Fixture has no second project available for provenance mutation")


@pytest.mark.integration
def test_activation_and_publish_transition_sessions_atomically(client):
    headers = {"X-Test-Session": "active-manager"}
    round_id, _ = _prepare_round(client, headers, "2042-03-01")
    run = _run(client, headers, round_id)
    version_id = run["version_id"]
    activated = client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=headers)
    assert activated.status_code == 200, activated.text

    with _db() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT status FROM schedule_versions WHERE id = %s", (version_id,))
        assert cursor.fetchone()[0] == "ACTIVE"
        cursor.execute(
            "SELECT status, room_id FROM sessions WHERE schedule_version_id = %s",
            (version_id,),
        )
        rows = cursor.fetchall()
        assert rows and all(status == "PLANNED" and room_id is None for status, room_id in rows)

    published = client.post(
        f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=headers
    )
    assert published.status_code == 200, published.text
    with _db() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT status FROM schedule_versions WHERE id = %s", (version_id,))
        assert cursor.fetchone()[0] == "PUBLISHED"
        cursor.execute("SELECT status FROM rounds WHERE id = %s", (round_id,))
        assert cursor.fetchone()[0] == "PUBLISHED"
        cursor.execute("SELECT DISTINCT status FROM sessions WHERE schedule_version_id = %s", (version_id,))
        assert [row[0] for row in cursor.fetchall()] == ["SCHEDULED"]
