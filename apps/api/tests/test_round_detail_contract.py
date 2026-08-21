from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine
from app.routes.manager_extensions import RoundUpdate


def test_round_update_payload_supports_group_preference_deadline():
    deadline = datetime(2030, 1, 21, 16, 59, tzinfo=UTC)
    payload = RoundUpdate(group_preference_deadline=deadline)

    assert payload.group_preference_deadline == deadline


def test_round_update_payload_accepts_frontend_contract_aliases():
    payload = RoundUpdate(
        durationMinutes=75,
        reviewerCount=2,
        groupSelectionMode=True,
        roomTypes=["NORMAL"],
    )

    assert payload.model_dump(exclude_unset=True) == {
        "session_duration_minutes": 75,
        "reviewer_count": 2,
        "group_selection_mode": True,
        "room_types": ["NORMAL"],
    }


@pytest.mark.integration
def test_round_detail_matches_frontend_contract_and_groups_active_slots(client):
    headers = {"X-Test-Session": "active-manager"}
    engine = get_engine(get_settings().database_url)

    with Session(engine) as db, db.begin():
        semester_id = db.execute(text("SELECT MIN(id) FROM semesters")).scalar_one()
        round_id = db.execute(
            text(
                "INSERT INTO rounds "
                "(semester_id, name, description, type, status, session_duration_minutes, "
                "reviewer_count, max_groups_per_timeslot, registration_deadline, "
                "group_selection_mode, group_preference_deadline, result_owner_mode) "
                "VALUES (:semester_id, 'Contract Round', 'Round detail contract', "
                "CAST('REVIEW_1' AS round_type), CAST('DRAFT' AS round_status), 60, 2, 3, "
                "CAST('2030-01-20T16:59:00Z' AS timestamptz), TRUE, "
                "CAST('2030-01-21T16:59:00Z' AS timestamptz), FALSE) RETURNING id"
            ),
            {"semester_id": semester_id},
        ).scalar_one()
        db.execute(
            text(
                "INSERT INTO round_room_types (round_id, room_type) "
                "VALUES (:round_id, CAST('NORMAL' AS room_type))"
            ),
            {"round_id": round_id},
        )
        active_day_id = db.execute(
            text(
                "INSERT INTO round_days (round_id, day_date) "
                "VALUES (:round_id, DATE '2030-02-01') RETURNING id"
            ),
            {"round_id": round_id},
        ).scalar_one()
        empty_day_id = db.execute(
            text(
                "INSERT INTO round_days (round_id, day_date) "
                "VALUES (:round_id, DATE '2030-02-02') RETURNING id"
            ),
            {"round_id": round_id},
        ).scalar_one()
        active_slot_id = db.execute(
            text(
                "INSERT INTO timeslots (round_day_id, start_at, end_at, active) "
                "VALUES (:day_id, CAST('2030-02-01T01:00:00Z' AS timestamptz), "
                "CAST('2030-02-01T02:00:00Z' AS timestamptz), TRUE) RETURNING id"
            ),
            {"day_id": active_day_id},
        ).scalar_one()
        db.execute(
            text(
                "INSERT INTO timeslots (round_day_id, start_at, end_at, active) "
                "VALUES (:day_id, CAST('2030-02-02T03:00:00Z' AS timestamptz), "
                "CAST('2030-02-02T04:00:00Z' AS timestamptz), FALSE)"
            ),
            {"day_id": empty_day_id},
        )

    try:
        response = client.get(f"/api/v1/rounds/{round_id}", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json() == {
            "data": {
                "id": str(round_id),
                "semesterId": str(semester_id),
                "name": "Contract Round",
                "type": "REVIEW_1",
                "status": "DRAFT",
                "description": "Round detail contract",
                "durationMinutes": 60,
                "reviewerCount": 2,
                "maxGroupsPerTimeslot": 3,
                "registrationDeadline": "2030-01-20T16:59:00Z",
                "groupSelectionMode": True,
                "groupPreferenceDeadline": "2030-01-21T16:59:00Z",
                "resultOwnerMode": False,
                "roomTypes": ["NORMAL"],
                "days": [
                    {
                        "date": "2030-02-01",
                        "slots": [
                            {"id": str(active_slot_id), "startTime": "08:00", "endTime": "09:00"}
                        ],
                    },
                    {"date": "2030-02-02", "slots": []},
                ],
            }
        }

        patch_response = client.patch(
            f"/api/v1/rounds/{round_id}",
            headers=headers,
            json={"durationMinutes": 75},
        )
        assert patch_response.status_code == 200, patch_response.text

        get_after_patch = client.get(f"/api/v1/rounds/{round_id}", headers=headers)
        assert get_after_patch.status_code == 200, get_after_patch.text
        assert patch_response.json() == get_after_patch.json()
        assert patch_response.json()["data"]["durationMinutes"] == 75

        empty_patch_response = client.patch(f"/api/v1/rounds/{round_id}", headers=headers, json={})
        assert empty_patch_response.status_code == 200, empty_patch_response.text
        assert empty_patch_response.json() == get_after_patch.json()
    finally:
        with Session(engine) as db, db.begin():
            db.execute(text("DELETE FROM rounds WHERE id = :id"), {"id": round_id})
