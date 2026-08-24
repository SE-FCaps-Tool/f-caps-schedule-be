from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.services.notification_dispatcher import process_availability_reminders


@pytest.mark.integration
def test_manager_operations_and_report_surfaces_have_provenance(client):
    headers = {"X-Test-Session": "active-manager"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text

    dashboard = client.get("/api/v1/dashboard", headers=headers)
    assert dashboard.status_code == 200, dashboard.text
    assert {"currentSemester", "availability", "groups", "lecturerLoad", "attentionGroups"}.issubset(dashboard.json())
    current_semester = dashboard.json()["currentSemester"]
    assert current_semester is not None
    assert current_semester["status"] == "ACTIVE"
    assert {"id", "code", "name", "status"} <= current_semester.keys()

    for path in ("/api/v1/reports/lecturer-load", "/api/v1/reports/quality", "/api/v1/reports/remediation", "/api/v1/reports/outcomes"):
        response = client.get(path, headers=headers)
        assert response.status_code == 200, response.text
        assert "version" in response.json()

    notifications = client.get("/api/v1/notifications", headers=headers)
    assert notifications.status_code == 200, notifications.text
    personal = client.get("/api/v1/my/schedule", headers=headers)
    assert personal.status_code == 200, personal.text
    assert "sessions" in personal.json()
    remediation = client.get("/api/v1/remediation", headers=headers)
    assert remediation.status_code == 200, remediation.text


@pytest.mark.integration
def test_admin_account_lifecycle_is_audited(client):
    admin_headers = {"X-Test-Session": "active-admin"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers=admin_headers)
    assert seeded.status_code == 201, seeded.text

    created = client.post(
        "/api/v1/accounts",
        json={"email": f"operator-{uuid4().hex[:8]}@example.test", "display_name": "Operator", "password": "LongEnoughDemo!2026", "role": "MANAGER"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    account_id = created.json()["id"]
    accounts = client.get("/api/v1/accounts", headers=admin_headers)
    assert accounts.status_code == 200, accounts.text
    created_account = next(item for item in accounts.json() if item["id"] == account_id)
    assert created_account["role"] == "MANAGER"
    disabled = client.patch(
        f"/api/v1/accounts/{account_id}/status",
        json={"status": "INACTIVE", "reason": "End of local pilot"},
        headers=admin_headers,
    )
    assert disabled.status_code == 200, disabled.text
    assert disabled.json()["status"] == "INACTIVE"
    audit = client.get("/api/v1/audit", headers=admin_headers)
    assert audit.status_code == 200, audit.text
    assert any(item["action"] == "ACCOUNT_STATUS_CHANGED" for item in audit.json())


@pytest.mark.integration
def test_round_configuration_conflict_scope_and_invitation_notification(client):
    manager_headers = {"X-Test-Session": "active-manager"}
    registration_deadline = (datetime.now(UTC) + timedelta(hours=2)).isoformat()
    group_preference_deadline = (datetime.now(UTC) + timedelta(hours=4)).isoformat()
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text
    semester_id = next(item["id"] for item in client.get("/api/v1/semesters", headers=manager_headers).json()["data"] if item["code"] == "SE-2026-2027")
    round_response = client.post(
        "/api/v1/rounds",
        json={
            "semester_id": semester_id,
            "type": "REVIEW_3",
            "reviewer_count": 3,
            "room_types": ["NORMAL"],
            "result_owner_mode": True,
            "group_selection_mode": True,
            "registration_deadline": registration_deadline,
            "group_preference_deadline": group_preference_deadline,
            "session_duration_minutes": 30,
            "start_date": "2030-01-25",
            "end_date": "2030-03-01",
            "h12_sessions_per_part": 3,
            "h12_sessions_per_day": 7,
            "h12_semester_quota": 24,
            "soft_weights": {"S1": 1, "S8": 2},
        },
        headers=manager_headers,
    )
    assert round_response.status_code == 201, round_response.text
    round_id = round_response.json()["id"]
    assert round_response.json()["h12_sessions_per_part"] == 3
    assert round_response.json()["soft_weights"] == {"S1": 1, "S8": 2}
    availability_view = client.get(f"/api/v1/rounds/{round_response.json()['id']}/my-availability", headers=manager_headers)
    assert availability_view.status_code == 200, availability_view.text
    assert "timeslots" in availability_view.json()
    incomplete_transition = client.post(f"/api/v1/rounds/{round_id}/transition", json={"target_status": "SCHEDULING"}, headers=manager_headers)
    assert incomplete_transition.status_code == 422, incomplete_transition.text

    lecturer = client.get("/api/v1/lecturers", headers=manager_headers).json()["data"][0]
    invited = client.post(f"/api/v1/rounds/{round_id}/invitations", json={"lecturer_ids": [lecturer["id"]]}, headers=manager_headers)
    assert invited.status_code == 200, invited.text
    lecturer_headers = {"X-Test-Session": f"active-lecturer:{lecturer['account_id']}"}
    pending_write = client.post(
        f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
        json={"selected_timeslot_ids": []},
        headers=lecturer_headers,
    )
    assert pending_write.status_code == 403, pending_write.text
    pending_read = client.get(f"/api/v1/rounds/{round_id}/my-availability", headers=lecturer_headers)
    assert pending_read.status_code == 403, pending_read.text
    accepted = client.post(
        f"/api/v1/rounds/{round_id}/invitations/{lecturer['id']}/response",
        json={"response": "ACCEPTED"},
        headers=lecturer_headers,
    )
    assert accepted.status_code == 200, accepted.text
    draft_write = client.post(
        f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
        json={"selected_timeslot_ids": []},
        headers=lecturer_headers,
    )
    assert draft_write.status_code == 409, draft_write.text
    opened = client.post(
        f"/api/v1/rounds/{round_id}/transition",
        json={"target_status": "OPEN_REGISTRATION"},
        headers=manager_headers,
    )
    assert opened.status_code == 200, opened.text
    accepted_write = client.post(
        f"/api/v1/rounds/{round_id}/lecturers/{lecturer['id']}/availability",
        json={"selected_timeslot_ids": []},
        headers=lecturer_headers,
    )
    assert accepted_write.status_code == 200, accepted_write.text
    target_read = client.get(f"/api/v1/rounds/{round_id}/availability/me", headers=lecturer_headers)
    assert target_read.status_code == 200, target_read.text
    with Session(get_engine(get_settings().database_url)) as db, db.begin():
        db.execute(
            text(
                "UPDATE rounds SET registration_deadline = :closed_at, "
                "group_preference_deadline = :closed_at WHERE id = :round_id"
            ),
            {"closed_at": datetime.now(UTC) - timedelta(minutes=1), "round_id": round_id},
        )
    closed_target_read = client.get(f"/api/v1/rounds/{round_id}/availability/me", headers=lecturer_headers)
    assert closed_target_read.status_code == 200, closed_target_read.text
    closed_target_write = client.put(
        f"/api/v1/rounds/{round_id}/availability/me",
        json={"preferredLoad": "HIGH", "slots": []},
        headers=lecturer_headers,
    )
    assert closed_target_write.status_code == 409, closed_target_write.text
    invitations = client.get("/api/v1/my/invitations", headers=lecturer_headers)
    assert invitations.status_code == 200, invitations.text
    assert any(item["round_id"] == round_id and item["lecturer_id"] == lecturer["id"] and item["status"] == "ACCEPTED" for item in invitations.json())
    lecturer_remediation = client.get("/api/v1/remediation", headers=lecturer_headers)
    assert lecturer_remediation.status_code == 200, lecturer_remediation.text
    notifications = client.get("/api/v1/notifications", headers=manager_headers).json()
    assert any(item["event_type"] == "REVIEW_INVITATION" and item["payload"]["round_id"] == round_id for item in notifications)

    major_id = client.get("/api/v1/majors", headers=manager_headers).json()[0]["id"]
    project = client.post(
        "/api/v1/projects",
        json={"semester_id": semester_id, "major_id": major_id, "code": f"CONFLICT-{uuid4().hex[:8]}", "title": "Conflict scope test", "supervisors": ["GV01:MAIN"]},
        headers=manager_headers,
    )
    assert project.status_code == 201, project.text
    projects = client.get("/api/v1/projects", headers=manager_headers)
    assert projects.status_code == 200, projects.text
    assert any(item["id"] == project.json()["id"] for item in projects.json())
    own_headers = {"X-Test-Session": f"active-lecturer:{lecturer['account_id']}"}
    conflict = client.post(f"/api/v1/lecturers/{lecturer['id']}/conflicts", json={"project_id": project.json()["id"], "reason": "Declared conflict"}, headers=own_headers)
    assert conflict.status_code == 200, conflict.text
    lecturers = client.get("/api/v1/lecturers", headers=manager_headers)
    assert lecturers.status_code == 200, lecturers.text
    lecturer_details = next(item for item in lecturers.json()["data"] if item["id"] == lecturer["id"])
    assert lecturer_details["account_id"] == lecturer["account_id"]
    assert lecturer_details["email"]
    assert lecturer_details["display_name"]
    assert lecturer_details["account_status"] in {"ACTIVE", "INACTIVE"}
    assert {item["project_id"] for item in lecturer_details["conflicts"]} >= {project.json()["id"]}


@pytest.mark.integration
def test_worker_creates_availability_reminder_from_shared_event_source(client):
    manager_headers = {"X-Test-Session": "active-manager"}
    seeded = client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"})
    assert seeded.status_code == 201, seeded.text
    semester_id = next(item["id"] for item in client.get("/api/v1/semesters", headers=manager_headers).json()["data"] if item["code"] == "SE-2026-2027")
    deadline = (datetime.now(UTC) + timedelta(hours=12)).isoformat()
    round_response = client.post(
        "/api/v1/rounds",
        json={"semester_id": semester_id, "type": "REVIEW_1", "reviewer_count": 2, "room_types": ["NORMAL"], "session_duration_minutes": 30, "registration_deadline": deadline},
        headers=manager_headers,
    )
    assert round_response.status_code == 201, round_response.text
    round_id = round_response.json()["id"]
    lecturer = client.get("/api/v1/lecturers", headers=manager_headers).json()["data"][0]
    assert client.post(f"/api/v1/rounds/{round_id}/invitations", json={"lecturer_ids": [lecturer["id"]]}, headers=manager_headers).status_code == 200
    lecturer_headers = {"X-Test-Session": f"active-lecturer:{lecturer['account_id']}"}
    assert client.post(f"/api/v1/rounds/{round_id}/invitations/{lecturer['id']}/response", json={"response": "ACCEPTED"}, headers=lecturer_headers).status_code == 200
    manager_rounds = client.get("/api/v1/my/rounds", headers=manager_headers)
    assert manager_rounds.status_code == 200, manager_rounds.text
    assert any(item["id"] == round_id for item in manager_rounds.json())
    lecturer_rounds = client.get("/api/v1/my/rounds", headers=lecturer_headers)
    assert lecturer_rounds.status_code == 200, lecturer_rounds.text
    assert any(item["id"] == round_id for item in lecturer_rounds.json())
    with Session(get_engine(get_settings().database_url)) as db:
        assert process_availability_reminders(db) >= 1
    notifications = client.get("/api/v1/notifications", headers=manager_headers).json()
    assert any(item["event_type"] == "AVAILABILITY_REMINDER" and item["payload"]["round_id"] == round_id for item in notifications)
