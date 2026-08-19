from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.domain.registration_phase import RegistrationPhase, resolve_registration_phase
from app.routes.master_data import RoundCreate
from app.routes.target_round_contract import TargetRoundCreate


def test_registration_phases_are_sequential_at_deadline_boundaries():
    lecturer_deadline = datetime(2030, 1, 10, tzinfo=UTC)
    group_deadline = datetime(2030, 1, 12, tzinfo=UTC)

    assert resolve_registration_phase(
        round_status="DRAFT",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        now=lecturer_deadline - timedelta(days=1),
    ) is RegistrationPhase.INACTIVE
    assert resolve_registration_phase(
        round_status="OPEN_REGISTRATION",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        now=lecturer_deadline,
    ) is RegistrationPhase.LECTURER
    assert resolve_registration_phase(
        round_status="OPEN_REGISTRATION",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        now=lecturer_deadline + timedelta(seconds=1),
    ) is RegistrationPhase.GROUP
    assert resolve_registration_phase(
        round_status="OPEN_REGISTRATION",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        now=group_deadline,
    ) is RegistrationPhase.GROUP
    assert resolve_registration_phase(
        round_status="OPEN_REGISTRATION",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        now=group_deadline + timedelta(seconds=1),
    ) is RegistrationPhase.CLOSED


def test_manual_lecturer_handoff_opens_group_phase_before_deadline():
    lecturer_deadline = datetime(2030, 1, 10, tzinfo=UTC)
    group_deadline = datetime(2030, 1, 12, tzinfo=UTC)
    now = datetime(2030, 1, 5, tzinfo=UTC)

    assert resolve_registration_phase(
        round_status="OPEN_REGISTRATION",
        registration_deadline=lecturer_deadline,
        group_preference_deadline=group_deadline,
        lecturer_registration_closed_at=now,
        now=now,
    ) is RegistrationPhase.GROUP


def test_round_create_requires_group_deadline_after_lecturer_deadline():
    with pytest.raises(ValueError, match="groupPreferenceDeadline must be after registrationDeadline"):
        TargetRoundCreate.model_validate(
            {
                "name": "Review",
                "type": "REVIEW_1",
                "durationMinutes": 60,
                "reviewerCount": 2,
                "maxGroupsPerTimeslot": 3,
                "registrationDeadline": "2030-01-10T23:59:00+07:00",
                "groupSelectionMode": True,
                "groupPreferenceDeadline": "2030-01-10T22:00:00+07:00",
                "resultOwnerMode": False,
                "roomTypes": ["NORMAL"],
                "days": [{"date": "2030-01-20", "slots": [{"startTime": "08:00", "endTime": "09:00"}]}],
            }
        )


def test_legacy_round_create_enforces_sequential_deadlines():
    with pytest.raises(ValueError, match="both registration deadlines are required"):
        RoundCreate.model_validate(
            {
                "semester_id": 1,
                "type": "REVIEW_1",
                "reviewer_count": 2,
                "group_selection_mode": True,
                "session_duration_minutes": 60,
                "room_types": ["NORMAL"],
                "start_date": "2030-01-01",
                "end_date": "2030-03-01",
            }
        )


@pytest.mark.integration
def test_manager_can_handoff_open_round_to_group_registration(client):
    assert client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"}).status_code == 201
    engine = get_engine(get_settings().database_url)
    now = datetime.now(UTC)
    with Session(engine) as db, db.begin():
        semester_id = db.execute(text("SELECT id FROM semesters WHERE status = 'ACTIVE' ORDER BY id LIMIT 1")).scalar_one()
        round_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, type, status, reviewer_count, session_duration_minutes, "
                "group_selection_mode, registration_deadline, group_preference_deadline) "
                "VALUES (:semester_id, CAST('REVIEW_1' AS round_type), CAST('OPEN_REGISTRATION' AS round_status), "
                "2, 60, TRUE, :registration_deadline, :group_deadline) RETURNING id"
            ),
            {"semester_id": semester_id, "registration_deadline": now + timedelta(hours=2), "group_deadline": now + timedelta(hours=4)},
        ).scalar_one()
    try:
        response = client.post(
            f"/api/v1/rounds/{round_id}/actions/open-group-registration",
            headers={"X-Test-Session": "active-manager"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["registrationPhase"] == "GROUP"
        detail = client.get(f"/api/v1/rounds/{round_id}", headers={"X-Test-Session": "active-manager"})
        assert detail.status_code == 200, detail.text
        assert detail.json()["data"]["registrationPhase"] == "GROUP"
        closed = client.post(
            f"/api/v1/rounds/{round_id}/actions/close-registration",
            headers={"X-Test-Session": "active-manager"},
        )
        assert closed.status_code == 200, closed.text
        assert closed.json()["data"]["status"] == "REGISTRATION_CLOSED"
        with Session(engine) as db:
            closed_at = db.execute(text("SELECT lecturer_registration_closed_at FROM rounds WHERE id = :round_id"), {"round_id": round_id}).scalar_one()
        assert closed_at is not None
    finally:
        with Session(engine) as db, db.begin():
            db.execute(text("DELETE FROM rounds WHERE id = :round_id"), {"round_id": round_id})


def test_round_create_rejects_mixed_timezone_deadlines_as_validation_error():
    with pytest.raises(ValueError, match="timezone offset"):
        TargetRoundCreate.model_validate(
            {
                "name": "Review",
                "type": "REVIEW_1",
                "durationMinutes": 60,
                "reviewerCount": 2,
                "maxGroupsPerTimeslot": 3,
                "registrationDeadline": "2030-01-10T23:59:00+07:00",
                "groupSelectionMode": True,
                "groupPreferenceDeadline": "2030-01-12T22:00:00",
                "resultOwnerMode": False,
                "roomTypes": ["NORMAL"],
                "days": [{"date": "2030-01-20", "slots": [{"startTime": "08:00", "endTime": "09:00"}]}],
            }
        )


@pytest.mark.integration
def test_student_group_preferences_are_open_only_between_the_two_deadlines(client):
    assert client.post("/api/v1/admin/seed-fixture", headers={"X-Test-Session": "active-admin"}).status_code == 201
    engine = get_engine(get_settings().database_url)
    now = datetime.now(UTC)

    with Session(engine) as db, db.begin():
        leader = db.execute(
            text(
                "SELECT g.id AS group_id, st.account_id, p.semester_id "
                "FROM groups g JOIN projects p ON p.id = g.project_id "
                "JOIN group_memberships gm ON gm.group_id = g.id AND gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER' "
                "JOIN students st ON st.id = gm.student_id LIMIT 1"
            )
        ).mappings().one()
        member_account_id = db.execute(
            text(
                    "SELECT st.account_id FROM students st "
                    "WHERE st.account_id <> :leader_account_id ORDER BY st.id LIMIT 1"
                ),
                {"leader_account_id": leader["account_id"]},
        ).scalar_one()
        round_id = db.execute(
            text(
                "INSERT INTO rounds (semester_id, type, status, reviewer_count, session_duration_minutes, "
                "group_selection_mode, registration_deadline, group_preference_deadline) "
                "VALUES (:semester_id, CAST('REVIEW_1' AS round_type), CAST('OPEN_REGISTRATION' AS round_status), "
                "2, 60, TRUE, :registration_deadline, :group_deadline) RETURNING id"
            ),
            {
                "semester_id": leader["semester_id"],
                "registration_deadline": now + timedelta(hours=1),
                "group_deadline": now + timedelta(hours=2),
            },
        ).scalar_one()
        db.execute(
            text("INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id)"),
            {"round_id": round_id, "group_id": leader["group_id"]},
        )

    headers = {"X-Test-Session": f"active-student:{leader['account_id']}"}
    path = f"/api/v1/rounds/{round_id}/groups/{leader['group_id']}/preferences"
    try:
        lecturer_phase = client.put(path, json={"timeslotIds": []}, headers=headers)
        assert lecturer_phase.status_code == 409, lecturer_phase.text

        with Session(engine) as db, db.begin():
            db.execute(
                text("UPDATE rounds SET registration_deadline = :deadline WHERE id = :round_id"),
                {"deadline": now - timedelta(seconds=1), "round_id": round_id},
            )
        group_phase = client.put(path, json={"timeslotIds": []}, headers=headers)
        assert group_phase.status_code == 200, group_phase.text
        assert client.get(path, headers=headers).status_code == 200
        assert client.get(path, headers={"X-Test-Session": "active-lecturer"}).status_code == 403
        member_view = client.get(
            f"/api/v1/rounds/{round_id}/availability/me",
            headers={"X-Test-Session": f"active-student:{member_account_id}"},
        )
        assert member_view.status_code == 403, member_view.text

        with Session(engine) as db, db.begin():
            db.execute(
                text("DELETE FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"),
                {"round_id": round_id, "group_id": leader["group_id"]},
            )
        detached = client.get(path, headers=headers)
        assert detached.status_code == 403, detached.text

        with Session(engine) as db, db.begin():
            db.execute(
                text("INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id)"),
                {"round_id": round_id, "group_id": leader["group_id"]},
            )
            db.execute(
                text("UPDATE rounds SET group_preference_deadline = :deadline WHERE id = :round_id"),
                {"deadline": now - timedelta(seconds=1), "round_id": round_id},
            )
        closed = client.put(path, json={"timeslotIds": []}, headers=headers)
        assert closed.status_code == 409, closed.text
    finally:
        with Session(engine) as db, db.begin():
            db.execute(text("DELETE FROM rounds WHERE id = :round_id"), {"round_id": round_id})
