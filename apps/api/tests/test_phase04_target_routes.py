import pytest
from pydantic import ValidationError

from app.main import create_app
from app.routes.target_round_contract import TargetRoundCreate


def test_phase04_target_round_registration_routes_are_in_openapi():
    paths = create_app().openapi()["paths"]
    expected = {
        ("get", "/api/v1/semesters/{semester_id}/rounds"),
        ("post", "/api/v1/semesters/{semester_id}/rounds"),
        ("get", "/api/v1/rounds/{round_id}/eligible-projects"),
        ("get", "/api/v1/rounds/{round_id}/registration-summary"),
        ("get", "/api/v1/rounds/{round_id}/scheduling-readiness"),
        ("post", "/api/v1/rounds/{round_id}/actions/open-registration"),
        ("post", "/api/v1/rounds/{round_id}/actions/close-registration"),
        ("get", "/api/v1/rounds/{round_id}/availability/me"),
        ("put", "/api/v1/rounds/{round_id}/availability/me"),
        ("post", "/api/v1/rounds/{round_id}/invitations/me/respond"),
        ("post", "/api/v1/rounds/{round_id}/invitations/{invitation_id}/remind"),
        ("get", "/api/v1/rounds/{round_id}/groups/{group_id}/preferences"),
        ("put", "/api/v1/rounds/{round_id}/groups/{group_id}/preferences"),
    }
    assert {(method, path) for path, item in paths.items() for method in item} >= expected


def _spec_round_payload() -> dict:
    return {
        "name": "Review 3",
        "type": "REVIEW_3",
        "description": "demo",
        "durationMinutes": 60,
        "reviewerCount": 3,
        "maxGroupsPerTimeslot": 3,
        "registrationDeadline": "2026-08-20T23:59:00+07:00",
        "groupSelectionMode": True,
        "groupPreferenceDeadline": "2026-08-22T23:59:00+07:00",
        "resultOwnerMode": True,
        "roomTypes": ["NORMAL"],
        "days": [{"date": "2026-08-25", "slots": [{"startTime": "08:00", "endTime": "09:00"}]}],
    }


def test_target_round_create_accepts_spec_camel_case_and_builds_legacy_rows():
    payload = TargetRoundCreate.model_validate(_spec_round_payload())

    legacy, days = payload.to_legacy(1)

    assert legacy.semester_id == 1
    assert legacy.session_duration_minutes == 60
    assert legacy.reviewer_count == 3
    assert legacy.room_types == ["NORMAL"]
    assert days[0].day_date.isoformat() == "2026-08-25"
    assert days[0].slots[0].start_at.isoformat() == "2026-08-25T08:00:00+07:00"


def test_target_round_create_rejects_incompatible_result_owner_mode():
    payload = _spec_round_payload() | {"type": "REVIEW_1", "reviewerCount": 2}

    with pytest.raises(ValidationError, match="resultOwnerMode"):
        TargetRoundCreate.model_validate(payload)


def test_target_round_create_rejects_slot_duration_mismatch():
    payload = _spec_round_payload() | {
        "days": [{"date": "2026-08-25", "slots": [{"startTime": "08:00", "endTime": "08:30"}]}]
    }

    with pytest.raises(ValidationError, match="slot duration"):
        TargetRoundCreate.model_validate(payload)


def test_target_round_create_accepts_timeframe_without_explicit_days():
    payload = _spec_round_payload() | {
        "durationMinutes": 45,
        "timeframeId": 12,
        "startDate": "2026-08-25",
        "endDate": "2026-08-27",
        "registrationDeadline": "2026-08-26T23:59:00+07:00",
        "groupPreferenceDeadline": "2026-08-27T23:59:00+07:00",
    }
    payload.pop("days")

    model = TargetRoundCreate.model_validate(payload)
    legacy, days = model.to_legacy(1)

    assert legacy.timeframe_id == 12
    assert legacy.start_date.isoformat() == "2026-08-25"
    assert legacy.end_date.isoformat() == "2026-08-27"
    assert days == []
