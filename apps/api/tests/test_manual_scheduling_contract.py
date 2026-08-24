import pytest
from fastapi import HTTPException
from starlette.datastructures import QueryParams

from app.routes.manual_scheduling import (
    ALL_ROUND_STATUSES,
    EDITABLE_ROUND_STATUSES,
    PUBLISHABLE_ROUND_STATUSES,
    ManualReviewerPayload,
    ManualSessionPayload,
    _constraint_statuses,
    _ensure_mutable_round,
    _ensure_publishable_round,
    _manual_session_id,
    _normalize_reviewers,
    _query_list,
    _role_schema,
    router,
)


class _ScalarResult:
    def scalar_one_or_none(self):
        return "Lecturer Name"


class _FakeDb:
    def execute(self, *_args, **_kwargs):
        return _ScalarResult()


class _FakeRequest:
    def __init__(self, query: str):
        self.query_params = QueryParams(query)


def test_manual_role_schema_follows_reviewer_count_contract():
    assert _role_schema(2) == [
        {"key": "REVIEWER_1", "label": "Review 1", "order": 1},
        {"key": "REVIEWER_2", "label": "Review 2", "order": 2},
    ]
    assert _role_schema(3) == [
        {"key": "CHAIR", "label": "Chủ tịch", "order": 1},
        {"key": "SECRETARY", "label": "Thư kí", "order": 2},
        {"key": "MEMBER_1", "label": "Thành viên 1", "order": 3},
    ]
    assert [role["key"] for role in _role_schema(5)] == [
        "CHAIR",
        "SECRETARY",
        "MEMBER_1",
        "MEMBER_2",
        "MEMBER_3",
    ]


def test_manual_session_payload_accepts_frontend_aliases():
    payload = ManualSessionPayload(
        date="2030-01-01",
        roundTimeslotId="ts_123",
        groupIds=["grp_44", "grp_61"],
        roomId="room_3",
        reviewers=[{"lecturerId": "lec_11", "role": "CHAIR", "order": 1}],
        clientRevision=4,
    )

    assert payload.round_timeslot_id == "ts_123"
    assert payload.group_ids == ["grp_44", "grp_61"]
    assert payload.room_id == "room_3"
    assert payload.reviewers[0].lecturer_id == "lec_11"
    assert payload.client_revision == 4


def test_manual_reviewer_order_is_derived_from_role_schema():
    reviewers = [
        ManualReviewerPayload(lecturerId="lec_11", role="CHAIR", order=99),
        ManualReviewerPayload(lecturerId="lec_22", role="SECRETARY", order=98),
        ManualReviewerPayload(lecturerId="lec_33", role="MEMBER_1", order=97),
    ]

    normalized = _normalize_reviewers(_FakeDb(), reviewers, reviewer_count=3)

    assert [item["role_order"] for item in normalized] == [1, 2, 3]


def test_manual_reviewer_rejects_roles_outside_round_schema():
    reviewers = [ManualReviewerPayload(lecturerId="lec_11", role="CHAIR", order=1)]

    with pytest.raises(HTTPException) as exc_info:
        _normalize_reviewers(_FakeDb(), reviewers, reviewer_count=2)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "ROLE_STRUCTURE_INVALID"


def test_manual_options_accepts_bracketed_array_query_names():
    request = _FakeRequest("reviewerIds[]=lec_11&reviewerIds[]=lec_22")

    assert _query_list(request, "reviewerIds[]", parsed=None) == ["lec_11", "lec_22"]


def test_manual_constraint_statuses_do_not_report_unconfigured_rules_as_passed():
    statuses = {item["code"]: item["status"] for item in _constraint_statuses({"round_type": "DEFENSE_1"})}

    assert statuses["H11_PREVIOUS_REVIEWER"] == "enforced"
    assert statuses["H14_ROLE_SKILL"] == "notConfigured"
    assert statuses["H15_SUPERVISOR_RATIO"] == "notConfigured"


def test_manual_session_external_ids_are_accepted():
    assert _manual_session_id("manual_session_42") == 42
    assert _manual_session_id("42") == 42


def test_manual_schedule_editing_is_available_for_every_round_status():
    assert EDITABLE_ROUND_STATUSES == ALL_ROUND_STATUSES

    for round_status in ALL_ROUND_STATUSES:
        _ensure_mutable_round({"round_status": round_status})


def test_manual_schedule_publish_keeps_terminal_rounds_locked():
    for round_status in PUBLISHABLE_ROUND_STATUSES:
        _ensure_publishable_round({"round_status": round_status})

    for round_status in ("ONGOING", "POSTPONED", "COMPLETED", "LOCKED", "CANCELLED"):
        with pytest.raises(HTTPException) as exc_info:
            _ensure_publishable_round({"round_status": round_status})

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["code"] == "ROUND_STATUS_INVALID"


def test_manual_scheduling_router_exposes_required_endpoints():
    routes = {(next(iter(route.methods)), route.path) for route in router.routes}

    assert ("GET", "/api/v1/rounds/{roundId}/manual-schedule") in routes
    assert ("GET", "/api/v1/rounds/{roundId}/manual-schedule/options") in routes
    assert ("POST", "/api/v1/rounds/{roundId}/manual-schedule/sessions") in routes
    assert ("POST", "/api/v1/rounds/{roundId}/manual-schedule/sessions/bulk-upsert") in routes
    assert ("PATCH", "/api/v1/rounds/{roundId}/manual-schedule/sessions/{sessionId}") in routes
    assert ("DELETE", "/api/v1/rounds/{roundId}/manual-schedule/sessions/{sessionId}") in routes
    assert ("POST", "/api/v1/rounds/{roundId}/manual-schedule/validate") in routes
    assert ("GET", "/api/v1/rounds/{roundId}/manual-schedule/publish-readiness") in routes
    assert ("POST", "/api/v1/rounds/{roundId}/manual-schedule/publish") in routes
