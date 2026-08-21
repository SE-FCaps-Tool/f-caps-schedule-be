from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine


@pytest.mark.integration
def test_scheduler_requires_accepted_lecturers_and_intersects_group_preference(client):
    admin = {"X-Test-Session": "active-admin"}
    manager = {"X-Test-Session": "active-manager"}

    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin)
    assert seeded.status_code in (200, 201), seeded.text

    semester = next(
        item
        for item in client.get("/api/v1/semesters", headers=manager).json()["data"]
        if item["code"] == "SE-2026-2027"
    )
    with Session(get_engine(get_settings().database_url)) as db, db.begin():
        lecturer_count = db.execute(text("SELECT COUNT(*) FROM lecturers")).scalar_one()
        for index in range(max(0, 3 - lecturer_count)):
            account_id = db.execute(
                text(
                    "INSERT INTO accounts (email, display_name, password_hash) "
                    "VALUES (:email, :display_name, :password_hash) RETURNING id"
                ),
                {
                    "email": f"e2e-lecturer-{uuid4().hex[:8]}@example.com",
                    "display_name": f"E2E Lecturer {index + 2}",
                    "password_hash": "e2e-test-hash",
                },
            ).scalar_one()
            db.execute(
                text(
                    "INSERT INTO account_roles (account_id, role) "
                    "VALUES (:account_id, CAST('LECTURER' AS system_role))"
                ),
                {"account_id": account_id},
            )
            db.execute(
                text(
                    "INSERT INTO lecturers (account_id, lecturer_code) "
                    "VALUES (:account_id, :lecturer_code)"
                ),
                {
                    "account_id": account_id,
                    "lecturer_code": f"E2E-{uuid4().hex[:8].upper()}",
                },
            )

    lecturers = client.get("/api/v1/lecturers", headers=manager).json()["data"][:3]
    assert len(lecturers) == 3
    with Session(get_engine(get_settings().database_url)) as db:
        student_rows = db.execute(
            text(
                "SELECT st.id, st.account_id FROM students st "
                "WHERE NOT EXISTS ("
                "SELECT 1 FROM group_memberships gm "
                "JOIN groups g ON g.id = gm.group_id "
                "LEFT JOIN projects p ON p.id = g.project_id "
                "WHERE gm.student_id = st.id AND gm.status = 'ACTIVE' "
                "AND (p.semester_id = :semester_id OR g.project_id IS NULL)"
                ") ORDER BY st.id LIMIT 2"
            ),
            {"semester_id": semester["id"]},
        ).all()
        assert len(student_rows) == 2
        leader_student_id = student_rows[0][0]
        leader_account_id = student_rows[0][1]
        lecturer_accounts = dict(
            db.execute(
                text("SELECT id, account_id FROM lecturers WHERE id = ANY(:ids)"),
                {"ids": [lecturer["id"] for lecturer in lecturers]},
            ).all()
        )

    project_response = client.post(
        f"/api/v1/semesters/{semester['id']}/projects",
        json={
            "code": f"E2E-P-{uuid4().hex[:8].upper()}",
            "nameVi": "E2E scheduler project",
            "mainSupervisorId": lecturers[0]["id"],
        },
        headers=manager,
    )
    assert project_response.status_code == 201, project_response.text
    project_id = project_response.json()["data"]["id"]

    group_response = client.post(
        f"/api/v1/semesters/{semester['id']}/groups",
        json={
            "code": f"E2E-G-{uuid4().hex[:8].upper()}",
            "studentIds": [row[0] for row in student_rows],
            "leaderId": leader_student_id,
        },
        headers=manager,
    )
    assert group_response.status_code == 201, group_response.text
    group_id = group_response.json()["data"]["id"]
    group_numeric_id = int(str(group_id).split("_", 1)[1])

    assigned = client.put(
        f"/api/v1/groups/{group_id}/project",
        json={"projectId": project_id},
        headers=manager,
    )
    assert assigned.status_code == 200, assigned.text

    round_response = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester["id"],
            "type": "REVIEW_1",
            "reviewer_count": 2,
            "group_selection_mode": True,
            "registration_deadline": "2046-04-01T12:00:00+00:00",
            "group_preference_deadline": "2046-04-01T13:00:00+00:00",
            "room_types": ["NORMAL"],
            "session_duration_minutes": 30,
            "start_date": "2046-04-01",
            "end_date": "2046-04-30",
        },
        headers=manager,
    )
    assert round_response.status_code == 201, round_response.text
    round_id = round_response.json()["id"]

    day_response = client.post(
        f"/api/v1/rounds/{round_id}/days",
        json={
            "day_date": "2046-04-01",
            "slots": [
                {
                    "start_at": "2046-04-01T09:00:00+07:00",
                    "end_at": "2046-04-01T09:30:00+07:00",
                }
            ],
        },
        headers=manager,
    )
    assert day_response.status_code == 201, day_response.text
    timeslot_id = day_response.json()["timeslot_ids"][0]

    with Session(get_engine(get_settings().database_url)) as db, db.begin():
        db.execute(
            text("INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id)"),
            {"round_id": round_id, "group_id": group_numeric_id},
        )

    invitation_response = client.post(
        f"/api/v1/rounds/{round_id}/invitations",
        json={"lecturer_ids": [lecturer["id"] for lecturer in lecturers]},
        headers=manager,
    )
    assert invitation_response.status_code == 200, invitation_response.text

    opened = client.post(
        f"/api/v1/rounds/{round_id}/transition",
        json={"target_status": "OPEN_REGISTRATION"},
        headers=manager,
    )
    assert opened.status_code == 200, opened.text

    first_lecturer = lecturers[0]
    first_lecturer_headers = {
        "X-Test-Session": f"active-lecturer:{lecturer_accounts[first_lecturer['id']]}"
    }
    before_accept = client.put(
        f"/api/v1/rounds/{round_id}/availability/me",
        json={
            "preferredLoad": "MEDIUM",
            "slots": [{"timeslotId": timeslot_id, "available": True}],
        },
        headers=first_lecturer_headers,
    )
    assert before_accept.status_code == 403, before_accept.text

    for lecturer in lecturers:
        lecturer_headers = {
            "X-Test-Session": f"active-lecturer:{lecturer_accounts[lecturer['id']]}"
        }
        accepted = client.post(
            f"/api/v1/rounds/{round_id}/invitations/me/respond",
            json={"decision": "ACCEPTED"},
            headers=lecturer_headers,
        )
        assert accepted.status_code == 200, accepted.text

        availability = client.put(
            f"/api/v1/rounds/{round_id}/availability/me",
            json={
                "preferredLoad": "MEDIUM",
                "slots": [{"timeslotId": timeslot_id, "available": True}],
            },
            headers=lecturer_headers,
        )
        assert availability.status_code == 200, availability.text

    student_preferences = client.put(
        f"/api/v1/rounds/{round_id}/groups/{group_numeric_id}/preferences",
        json={"timeslotIds": [timeslot_id]},
        headers={"X-Test-Session": f"active-student:{leader_account_id}"},
    )
    assert student_preferences.status_code == 200, student_preferences.text

    closed = client.post(
        f"/api/v1/rounds/{round_id}/actions/close-registration",
        headers=manager,
    )
    assert closed.status_code == 200, closed.text

    run = client.post(
        f"/api/v1/rounds/{round_id}/schedule/run",
        json={"time_limit_seconds": 5, "random_seed": 17},
        headers=manager,
    )
    assert run.status_code == 201, run.text
    body = run.json()
    assert body["scheduled_count"] == 1
    assert body["unscheduled"] == []

    activated = client.post(
        f"/api/v1/schedule/versions/{body['version_id']}/activate",
        headers=manager,
    )
    assert activated.status_code == 200, activated.text

    detail = client.get(
        f"/api/v1/schedule/versions/{body['version_id']}", headers=manager
    )
    assert detail.status_code == 200, detail.text
    session = detail.json()["sessions"][0]
    assert session["timeslot_id"] == timeslot_id
    assert set(session["reviewer_ids"]).issubset({lecturer["id"] for lecturer in lecturers})

    assigned_lecturer_id = session["reviewer_ids"][0]
    lecturer_sessions = client.get(
        "/api/v1/lecturer/me/sessions",
        headers={
            "X-Test-Session": f"active-lecturer:{lecturer_accounts[assigned_lecturer_id]}"
        },
    )
    assert lecturer_sessions.status_code == 200, lecturer_sessions.text
    assert any(item["roundId"] == round_id for item in lecturer_sessions.json()["data"])
