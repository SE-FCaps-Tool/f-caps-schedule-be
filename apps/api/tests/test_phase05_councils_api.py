"""PostgreSQL-backed acceptance tests for immutable Councils and change branches."""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.config import get_settings
from app.database import get_engine


def _prepare_published_session(client, day_date: str) -> dict:
    manager = {"X-Test-Session": "active-manager"}
    admin = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin)
    assert seeded.status_code in (200, 201), seeded.text
    semester = next(
        row for row in client.get("/api/v1/semesters", headers=manager).json()["data"] if row["code"] == "SE-2026-2027"
    )
    round_response = client.post(
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
    assert round_response.status_code == 201, round_response.text
    round_id = round_response.json()["id"]
    day_response = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={"day_date": day_date, "slots": [{"start_at": f"{day_date}T09:00:00+07:00", "end_at": f"{day_date}T09:30:00+07:00"}]},
        headers=manager,
    )
    assert day_response.status_code == 201, day_response.text
    timeslot_id = day_response.json()["timeslotIds"][0]
    group = next(
        item for item in client.get("/api/v1/groups", headers=manager).json() if item["status"] == "PENDING_D11" and item["leaderCount"] == 1
    )
    rooms = client.get("/api/v1/rooms", headers=manager).json()["data"]
    resource_response = client.post(
        f"/api/v1/rounds/{round_id}/resources",
        json={"groupIds": [group["id"]], "timeslotIds": [timeslot_id], "room_ids": [rooms[0]["id"]]},
        headers=manager,
    )
    assert resource_response.status_code == 200, resource_response.text
    lecturers = client.get("/api/v1/lecturers", headers=manager).json()["data"]
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
        json={"timeLimitSeconds": 2, "randomSeed": 7},
        headers=manager,
    )
    assert run.status_code == 201, run.text
    version_id = run.json()["versionId"]
    detail = client.get(f"/api/v1/schedule/versions/{version_id}", headers=manager)
    assert detail.status_code == 200, detail.text
    activated = client.post(f"/api/v1/schedule/versions/{version_id}/activate", headers=manager)
    assert activated.status_code == 200, activated.text
    session = client.get(f"/api/v1/schedule/versions/{version_id}", headers=manager).json()["sessions"][0]
    room = client.put(f"/api/v1/sessions/{session['id']}/room", json={"roomId": rooms[0]["id"]}, headers=manager)
    assert room.status_code == 200, room.text
    published = client.post(f"/api/v1/rounds/{round_id}/schedule/publish/{version_id}", headers=manager)
    assert published.status_code == 200, published.text
    return {
        "manager": manager,
        "round_id": round_id,
        "version_id": version_id,
        "session": client.get(f"/api/v1/schedule/versions/{version_id}", headers=manager).json()["sessions"][0],
        "lecturers": lecturers,
        "rooms": rooms,
    }


@pytest.mark.integration
def test_activation_persists_one_sealed_council_per_materialized_session(client):
    state = _prepare_published_session(client, "2054-05-01")
    engine = get_engine(get_settings().database_url)
    with engine.begin() as db:
        rows = db.execute(
            text(
                "SELECT s.id, s.council_id, c.round_id, c.sealed_at "
                "FROM sessions s JOIN councils c ON c.id = s.council_id "
                "WHERE s.schedule_version_id = :version_id"
            ),
            {"version_id": state["version_id"]},
        ).mappings().all()
        assert len(rows) == 1
        assert rows[0]["council_id"] is not None
        assert rows[0]["round_id"] == state["round_id"]
        assert rows[0]["sealed_at"] is not None
        member_count = db.execute(
            text("SELECT COUNT(*) FROM council_members WHERE council_id = :council_id"),
            {"council_id": rows[0]["council_id"]},
        ).scalar_one()
    assert member_count == len(state["session"]["reviewerIds"])
    assert state["session"]["councilId"] == rows[0]["council_id"]


@pytest.mark.integration
def test_sealed_council_rejects_member_insert_update_delete(client):
    state = _prepare_published_session(client, "2054-05-02")
    engine = get_engine(get_settings().database_url)
    with engine.begin() as db:
        council_id, lecturer_id = db.execute(
            text("SELECT council_id, lecturer_id FROM council_members WHERE council_id = (SELECT council_id FROM sessions WHERE schedule_version_id = :version_id) LIMIT 1"),
            {"version_id": state["version_id"]},
        ).one()
        other_lecturer_id = db.execute(
            text("SELECT id FROM lecturers WHERE id <> :lecturer_id ORDER BY id LIMIT 1"),
            {"lecturer_id": lecturer_id},
        ).scalar_one()
        for statement, params in (
            (
                "INSERT INTO council_members(council_id, lecturer_id, snapshot_name) VALUES (:council_id, :lecturer_id, 'late')",
                {"council_id": council_id, "lecturer_id": other_lecturer_id},
            ),
            (
                "UPDATE council_members SET snapshot_name = 'tampered' WHERE council_id = :council_id AND lecturer_id = :lecturer_id",
                {"council_id": council_id, "lecturer_id": lecturer_id},
            ),
            (
                "DELETE FROM council_members WHERE council_id = :council_id AND lecturer_id = :lecturer_id",
                {"council_id": council_id, "lecturer_id": lecturer_id},
            ),
        ):
            with pytest.raises(DBAPIError), db.begin_nested():
                db.execute(text(statement), params)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("name", "payload_delta", "expected_kind", "replacement"),
    [
        ("reviewer_only", {"reviewer_offset": 3}, "COUNCIL_REPLACED", False),
        ("time_room_only", {"room_offset": 1}, "VERSION_REPLACED", True),
        ("mixed", {"reviewer_offset": 3, "room_offset": 1}, "MIXED_REPLACEMENT", True),
    ],
)
def test_controlled_change_has_explicit_council_and_version_branch(client, name, payload_delta, expected_kind, replacement):
    state = _prepare_published_session(client, f"2054-05-{3 + ['reviewer_only', 'time_room_only', 'mixed'].index(name):02d}")
    session = state["session"]
    reviewers = session["reviewerIds"]
    if payload_delta.get("reviewer_offset"):
        with get_engine(get_settings().database_url).begin() as db:
            supervisor_ids = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT ps.lecturer_id FROM project_supervisors ps "
                        "JOIN schedule_assignments sa ON sa.project_id = ps.project_id "
                        "JOIN sessions s ON s.id = :session_id AND s.schedule_version_id = sa.schedule_version_id "
                        "WHERE sa.group_id = s.group_id"
                    ),
                    {"session_id": session["id"]},
                ).all()
            }
        reviewers = [
            item["id"]
            for item in state["lecturers"]
            if item["id"] not in supervisor_ids and item["id"] not in session["reviewerIds"]
        ][:3]
    payload = {
        "timeslotId": session["timeslotId"],
        "roomId": state["rooms"][payload_delta.get("room_offset", 0)]["id"],
        "reviewerIds": reviewers,
        "reason": f"Phase 5 {name}",
    }
    response = client.post(
        f"/api/v1/schedule/versions/{state['version_id']}/sessions/{session['id']}/controlled-change",
        json=payload,
        headers=state["manager"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["changeKind"] == expected_kind
    assert body["scheduleVersionId"] == state["version_id"]
    assert (body["replacementVersionId"] is not None) is replacement
    assert body["sessionId"] == session["id"]
    assert body["status"] in {"PUBLISHED", "REPLACED"}
    if not replacement:
        assert body["beforeCouncilId"] != body["afterCouncilId"]
        assert body["replacementVersionId"] is None
    else:
        source = client.get(f"/api/v1/schedule/versions/{state['version_id']}", headers=state["manager"]).json()
        assert source["status"] == "DISCARDED"
