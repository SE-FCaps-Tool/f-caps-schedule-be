import pytest
from pydantic import ValidationError

from app.main import create_app
from app.routes.target_round_contract import TargetRoundCreate, _progression_allowed


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
    assert legacy.start_date.isoformat() == "2026-08-25"
    assert legacy.end_date.isoformat() == "2026-08-25"
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
        "registrationDeadline": "2026-08-23T23:59:00+07:00",
        "groupPreferenceDeadline": "2026-08-24T23:59:00+07:00",
    }
    payload.pop("days")

    model = TargetRoundCreate.model_validate(payload)
    legacy, days = model.to_legacy(1)

    assert legacy.timeframe_id == 12
    assert legacy.start_date.isoformat() == "2026-08-25"
    assert legacy.end_date.isoformat() == "2026-08-27"
    assert days == []


def test_target_round_create_accepts_deadline_on_grading_start_date():
    payload = _spec_round_payload() | {
        "durationMinutes": 45,
        "timeframeId": 12,
        "startDate": "2026-08-25",
        "endDate": "2026-08-27",
        "registrationDeadline": "2026-08-25T09:00:00+07:00",
        "groupPreferenceDeadline": "2026-08-25T10:00:00+07:00",
    }
    payload.pop("days")

    TargetRoundCreate.model_validate(payload)


def test_target_round_create_rejects_deadline_after_grading_start():
    payload = _spec_round_payload() | {
        "durationMinutes": 45,
        "timeframeId": 12,
        "startDate": "2026-08-25",
        "endDate": "2026-08-27",
        "registrationDeadline": "2026-08-26T23:59:00+07:00",
        "groupPreferenceDeadline": "2026-08-27T23:59:00+07:00",
    }
    payload.pop("days")

    with pytest.raises(ValidationError, match="registrationDeadline must be on or before startDate"):
        TargetRoundCreate.model_validate(payload)


def test_target_round_create_rejects_group_deadline_before_registration_deadline():
    payload = _spec_round_payload() | {
        "groupPreferenceDeadline": "2026-08-19T23:59:00+07:00",
    }

    with pytest.raises(ValidationError, match="groupPreferenceDeadline must be later than registrationDeadline"):
        TargetRoundCreate.model_validate(payload)


def test_target_round_create_allows_deadlines_on_grading_start_date():
    payload = _spec_round_payload() | {
        "timeframeId": 12,
        "startDate": "2026-08-25",
        "endDate": "2026-08-27",
        "registrationDeadline": "2026-08-25T08:00:00+07:00",
        "groupPreferenceDeadline": "2026-08-25T23:59:00+07:00",
    }
    payload.pop("days")

    target = TargetRoundCreate.model_validate(payload)

    assert target.start_date.isoformat() == "2026-08-25"
    assert target.group_preference_deadline is not None


def test_defense_12_progression_accepts_unattached_eligible_group():
    assert _progression_allowed("DEFENSE_1_2", "ELIGIBLE_D12", has_prior_review_1=False)
    assert not _progression_allowed("DEFENSE_1_2", "PENDING_D11", has_prior_review_1=False)


def test_review_1_progression_rejects_group_already_reviewed():
    assert _progression_allowed("REVIEW_1", "PENDING_D11", has_prior_review_1=False)
    assert not _progression_allowed("REVIEW_1", "PENDING_D11", has_prior_review_1=True)
