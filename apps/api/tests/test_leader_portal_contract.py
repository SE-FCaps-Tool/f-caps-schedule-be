from datetime import UTC, datetime, timedelta
from inspect import getsource
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.routes.master_data import submit_group_availability
from app.routes.target_portals import leader_dashboard


def test_leader_contract_queries_lock_replacement_and_ignore_cancelled_sessions():
    dashboard_source = getsource(leader_dashboard)
    preference_source = getsource(submit_group_availability)

    assert "(sem.status::text = 'ACTIVE') DESC NULLS LAST" in dashboard_source
    assert "r.status::text = 'OPEN_REGISTRATION'" in dashboard_source
    assert "s.status::text = 'SCHEDULED'" in dashboard_source
    assert "FROM round_groups" in preference_source
    assert "FOR UPDATE" in preference_source
    assert preference_source.index("FOR UPDATE") < preference_source.index("DELETE FROM group_slot_preferences")


@pytest.mark.integration
def test_leader_dashboard_uses_singular_nullable_fe_contract(client):
    assert client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"}).status_code == 201
    engine = get_engine(get_settings().database_url)
    marker = uuid4().hex[:10]

    with Session(engine) as db, db.begin():
        account_id = db.execute(
            text(
                "INSERT INTO accounts (email, display_name, password_hash) "
                "VALUES (:email, 'No Group', 'unused') RETURNING id"
            ),
            {"email": f"no-group-{marker}@example.test"},
        ).scalar_one()
        db.execute(
            text("INSERT INTO students (account_id, student_code) VALUES (:account_id, :code)"),
            {"account_id": account_id, "code": f"NG-{marker}"},
        )
        leader_account_id = db.execute(
            text(
                "INSERT INTO accounts (email, display_name, password_hash) "
                "VALUES (:email, 'Leader', 'unused') RETURNING id"
            ),
            {"email": f"leader-{marker}@example.test"},
        ).scalar_one()
        leader_student_id = db.execute(
            text("INSERT INTO students (account_id, student_code) VALUES (:account_id, :code) RETURNING id"),
            {"account_id": leader_account_id, "code": f"LD-{marker}"},
        ).scalar_one()
        semester_id = db.execute(text("SELECT id FROM semesters ORDER BY id LIMIT 1")).scalar_one()
        major_id = db.execute(text("SELECT id FROM majors ORDER BY id LIMIT 1")).scalar_one()
        project_id = db.execute(
            text(
                "INSERT INTO projects (semester_id, major_id, code, title) "
                "VALUES (:semester_id, :major_id, :code, 'Portal contract') RETURNING id"
            ),
            {"semester_id": semester_id, "major_id": major_id, "code": f"PC-{marker}"},
        ).scalar_one()
        group_id = db.execute(
            text("INSERT INTO groups (project_id, code) VALUES (:project_id, :code) RETURNING id"),
            {"project_id": project_id, "code": f"G-{marker}"},
        ).scalar_one()
        db.execute(
            text(
                "INSERT INTO group_memberships (group_id, student_id, membership_role) "
                "VALUES (:group_id, :student_id, 'LEADER')"
            ),
            {"group_id": group_id, "student_id": leader_student_id},
        )
        projectless_group_id = db.execute(
            text("INSERT INTO groups (project_id, code) VALUES (NULL, :code) RETURNING id"),
            {"code": f"A-{marker}"},
        ).scalar_one()
        db.execute(
            text(
                "INSERT INTO group_memberships (group_id, student_id, membership_role) "
                "VALUES (:group_id, :student_id, 'LEADER')"
            ),
            {"group_id": projectless_group_id, "student_id": leader_student_id},
        )
        lecturer_id = db.execute(text("SELECT id FROM lecturers ORDER BY id LIMIT 1")).scalar_one()
        db.execute(
            text(
                "INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type) "
                "VALUES (:project_id, :lecturer_id, 'MAIN')"
            ),
            {"project_id": project_id, "lecturer_id": lecturer_id},
        )
        deadline = datetime.now(UTC) + timedelta(days=2)
        round_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, name, type, status, reviewer_count, session_duration_minutes, "
                "group_selection_mode, registration_deadline, group_preference_deadline) "
                "VALUES (:semester_id, 'Portal Review', 'REVIEW_1', 'OPEN_REGISTRATION', 2, 60, TRUE, "
                ":lecturer_deadline, :group_deadline) RETURNING id"
            ),
            {"semester_id": semester_id, "lecturer_deadline": deadline - timedelta(days=1), "group_deadline": deadline},
        ).scalar_one()
        db.execute(
            text("INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id)"),
            {"round_id": round_id, "group_id": group_id},
        )
        day_id = db.execute(
            text("INSERT INTO round_days (round_id, day_date) VALUES (:round_id, :day) RETURNING id"),
            {"round_id": round_id, "day": (deadline + timedelta(days=1)).date()},
        ).scalar_one()
        preference_slot_id = db.execute(
            text(
                "INSERT INTO timeslots (round_day_id, start_at, end_at) "
                "VALUES (:day_id, :start, :end) RETURNING id"
            ),
            {"day_id": day_id, "start": deadline + timedelta(days=1), "end": deadline + timedelta(days=1, hours=1)},
        ).scalar_one()

    try:
        empty = client.get(
            "/api/v1/leader/me/dashboard",
            headers={"X-Test-Session": f"active-student:{account_id}"},
        )
        assert empty.status_code == 200, empty.text
        assert empty.json() == {
            "data": {
                "group": None,
                "project": None,
                "mainSupervisor": None,
                "coSupervisor": None,
                "currentRound": None,
                "preferenceStatus": None,
                "deadline": None,
                "upcomingSession": None,
                "latestResult": None,
                "remediation": None,
            }
        }

        populated = client.get(
            "/api/v1/leader/me/dashboard",
            headers={"X-Test-Session": f"active-student:{leader_account_id}"},
        )
        assert populated.status_code == 200, populated.text
        data = populated.json()["data"]
        assert set(data) == {
            "group",
            "project",
            "mainSupervisor",
            "coSupervisor",
            "currentRound",
            "preferenceStatus",
            "deadline",
            "upcomingSession",
            "latestResult",
            "remediation",
        }
        assert isinstance(data["group"]["id"], str)
        assert data["group"]["id"] == str(group_id)
        assert data["group"]["maxMembers"] == 5
        assert data["group"]["memberCount"] >= 1
        assert data["project"]["status"] == "ACTIVE"
        assert data["mainSupervisor"]["id"] == str(lecturer_id)
        assert data["currentRound"] == {
            "id": str(round_id),
            "name": "Portal Review",
            "type": "REVIEW_1",
            "status": "OPEN_REGISTRATION",
        }
        assert data["preferenceStatus"] == "PENDING"
        assert data["deadline"] == deadline.isoformat().replace("+00:00", "Z")

        with Session(engine) as db, db.begin():
            db.execute(
                text(
                    "INSERT INTO group_slot_preferences (round_id, group_id, timeslot_id, selected) "
                    "VALUES (:round_id, :group_id, :timeslot_id, TRUE)"
                ),
                {"round_id": round_id, "group_id": group_id, "timeslot_id": preference_slot_id},
            )
        submitted = client.get(
            "/api/v1/leader/me/dashboard",
            headers={"X-Test-Session": f"active-student:{leader_account_id}"},
        )
        assert submitted.status_code == 200, submitted.text
        assert submitted.json()["data"]["preferenceStatus"] == "SUBMITTED"

        with Session(engine) as db, db.begin():
            db.execute(text("UPDATE groups SET status = 'ELIGIBLE_D12' WHERE id = :group_id"), {"group_id": group_id})
            db.execute(text("UPDATE rounds SET status = 'CANCELLED' WHERE id = :round_id"), {"round_id": round_id})
        inactive = client.get(
            "/api/v1/leader/me/dashboard",
            headers={"X-Test-Session": f"active-student:{leader_account_id}"},
        )
        assert inactive.status_code == 200, inactive.text
        assert inactive.json()["data"]["project"]["status"] == "ELIGIBLE_D12"
        assert inactive.json()["data"]["currentRound"] is None
        assert inactive.json()["data"]["preferenceStatus"] == "NOT_REQUIRED"
        assert inactive.json()["data"]["deadline"] is None
    finally:
        with Session(engine) as db, db.begin():
            db.execute(text("DELETE FROM rounds WHERE id = :round_id"), {"round_id": round_id})
            db.execute(
                text("DELETE FROM group_memberships WHERE group_id = :group_id"),
                {"group_id": projectless_group_id},
            )
            db.execute(text("DELETE FROM groups WHERE id = :group_id"), {"group_id": projectless_group_id})
            db.execute(text("DELETE FROM group_memberships WHERE group_id = :group_id"), {"group_id": group_id})
            db.execute(text("DELETE FROM groups WHERE id = :group_id"), {"group_id": group_id})
            db.execute(text("DELETE FROM projects WHERE id = :project_id"), {"project_id": project_id})
            db.execute(
                text("DELETE FROM notifications WHERE recipient_account_id IN (:leader_account_id, :account_id)"),
                {"leader_account_id": leader_account_id, "account_id": account_id},
            )
            db.execute(text("DELETE FROM students WHERE account_id = :account_id"), {"account_id": leader_account_id})
            db.execute(text("DELETE FROM accounts WHERE id = :account_id"), {"account_id": leader_account_id})
            db.execute(text("DELETE FROM students WHERE account_id = :account_id"), {"account_id": account_id})
            db.execute(text("DELETE FROM accounts WHERE id = :account_id"), {"account_id": account_id})


@pytest.mark.integration
def test_group_preferences_replace_selection_and_exclude_inactive_slots(client):
    assert client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"}).status_code == 201
    engine = get_engine(get_settings().database_url)
    now = datetime.now(UTC)
    marker = uuid4().hex[:10]

    with Session(engine) as db, db.begin():
        semester_id = db.execute(text("SELECT id FROM semesters ORDER BY id LIMIT 1")).scalar_one()
        major_id = db.execute(text("SELECT id FROM majors ORDER BY id LIMIT 1")).scalar_one()
        student = db.execute(
            text("SELECT id, account_id FROM students WHERE account_id IS NOT NULL ORDER BY id LIMIT 1")
        ).mappings().one()
        account_id = student["account_id"]
        student_id = student["id"]
        project_id = db.execute(
            text("INSERT INTO projects (semester_id, major_id, code, title) VALUES (:semester_id, :major_id, :code, 'Preference') RETURNING id"),
            {"semester_id": semester_id, "major_id": major_id, "code": f"PF-{marker}"},
        ).scalar_one()
        group_id = db.execute(
            text("INSERT INTO groups (project_id, code) VALUES (:project_id, :code) RETURNING id"),
            {"project_id": project_id, "code": f"PF-{marker}"},
        ).scalar_one()
        db.execute(
            text("INSERT INTO group_memberships (group_id, student_id, membership_role) VALUES (:group_id, :student_id, 'LEADER')"),
            {"group_id": group_id, "student_id": student_id},
        )
        round_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, type, status, reviewer_count, session_duration_minutes, "
                "group_selection_mode, registration_deadline, group_preference_deadline) "
                "VALUES (:semester_id, 'REVIEW_1', 'OPEN_REGISTRATION', 2, 60, TRUE, :lecturer_deadline, "
                ":group_deadline) RETURNING id"
            ),
            {
                "semester_id": semester_id,
                "lecturer_deadline": now - timedelta(minutes=1),
                "group_deadline": now + timedelta(hours=1),
            },
        ).scalar_one()
        day_id = db.execute(
            text("INSERT INTO round_days (round_id, day_date) VALUES (:round_id, :day) RETURNING id"),
            {"round_id": round_id, "day": (now + timedelta(days=2)).date()},
        ).scalar_one()
        slot_ids = []
        for offset, active in ((0, True), (1, True), (2, False)):
            start = now + timedelta(days=2, hours=offset)
            slot_ids.append(
                db.execute(
                    text(
                        "INSERT INTO timeslots (round_day_id, start_at, end_at, active) "
                        "VALUES (:day_id, :start, :end, :active) RETURNING id"
                    ),
                    {"day_id": day_id, "start": start, "end": start + timedelta(minutes=60), "active": active},
                ).scalar_one()
            )
        db.execute(
            text("INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id)"),
            {"round_id": round_id, "group_id": group_id},
        )

    headers = {"X-Test-Session": f"active-student:{account_id}"}
    path = f"/api/v1/rounds/{round_id}/groups/{group_id}/preferences"
    try:
        listed = client.get(path, headers=headers)
        assert listed.status_code == 200, listed.text
        assert [item["timeslotId"] for item in listed.json()["data"]["timeslots"]] == slot_ids[:2]

        for selection in (slot_ids[:2], slot_ids[:1], []):
            response = client.put(path, json={"timeslotIds": [str(value) for value in selection]}, headers=headers)
            assert response.status_code == 200, response.text
            assert response.json()["data"]["selectedCount"] == len(selection)
            with Session(engine) as db:
                stored = db.execute(
                    text(
                        "SELECT timeslot_id FROM group_slot_preferences "
                        "WHERE round_id = :round_id AND group_id = :group_id AND selected = TRUE "
                        "ORDER BY timeslot_id"
                    ),
                    {"round_id": round_id, "group_id": group_id},
                ).scalars().all()
            assert stored == selection

        inactive = client.put(path, json={"timeslotIds": [str(slot_ids[2])]}, headers=headers)
        assert inactive.status_code == 422, inactive.text
        assert inactive.json()["error"]["code"] == "AVAILABILITY_SLOT_INVALID"
    finally:
        with Session(engine) as db, db.begin():
            db.execute(text("DELETE FROM rounds WHERE id = :round_id"), {"round_id": round_id})
            db.execute(text("DELETE FROM group_memberships WHERE group_id = :group_id"), {"group_id": group_id})
            db.execute(text("DELETE FROM groups WHERE id = :group_id"), {"group_id": group_id})
            db.execute(text("DELETE FROM projects WHERE id = :project_id"), {"project_id": project_id})
