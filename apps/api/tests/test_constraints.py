from datetime import UTC as UTC_TZ
from datetime import datetime, timedelta

import pytest

from app.scheduler.models import RoundInput, ScheduledSession
from app.scheduler.validator import validate_schedule

UTC = UTC_TZ


def session(
    session_id: int,
    *,
    group_id: int = 1,
    project_id: int = 10,
    room_id: int = 1,
    reviewer_ids: tuple[int, ...] = (2, 3, 4),
    slot_id: int = 1,
    start_hour: int = 9,
) -> ScheduledSession:
    start = datetime(2030, 1, 1, start_hour, tzinfo=UTC)
    return ScheduledSession(
        session_id=session_id,
        group_id=group_id,
        project_id=project_id,
        timeslot_id=slot_id,
        room_id=room_id,
        start_at=start,
        end_at=start + timedelta(minutes=30),
        reviewer_ids=reviewer_ids,
        day="2030-01-01",
        part="AM",
    )


def base_input(**overrides: object) -> RoundInput:
    values: dict[str, object] = {
        "round_type": "DEFENSE_1_1",
        "expected_reviewer_count": 3,
        "group_status": {1: "PENDING_D11"},
        "group_project": {1: 10},
        "project_supervisors": {10: {99}},
        "lecturer_availability": {(2, 1), (3, 1), (4, 1)},
        "conflicts": set(),
        "group_selected_slots": {},
        "group_selection_mode": False,
        "prior_reviewer_ids": {},
        "remediation_verifier_ids": {},
        "h11_waiver_groups": set(),
        "h12_sessions_per_part": 4,
        "h12_sessions_per_day": 8,
        "h12_semester_quota": None,
        "existing_semester_load": {},
    }
    values.update(overrides)
    return RoundInput(**values)


@pytest.mark.parametrize(
    ("rule", "schedule", "context"),
    [
        ("H1", [session(1, reviewer_ids=(99, 2, 3))], base_input()),
        ("H2", [session(1), session(2, group_id=2, project_id=11, slot_id=2)], base_input(group_status={1: "PENDING_D11", 2: "PENDING_D11"}, group_project={1: 10, 2: 11}, lecturer_availability={(2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2)})),
        ("H3", [session(1), session(2, group_id=2, project_id=11, reviewer_ids=(5, 6, 7), slot_id=2)], base_input(group_status={1: "PENDING_D11", 2: "PENDING_D11"}, group_project={1: 10, 2: 11}, project_supervisors={10: {99}, 11: {98}}, lecturer_availability={(2, 1), (3, 1), (4, 1), (5, 2), (6, 2), (7, 2)})),
        ("H4", [session(1), session(2)], base_input()),
        ("H5", [session(1, reviewer_ids=(2, 3))], base_input(expected_reviewer_count=3)),
        ("H6", [session(1, reviewer_ids=(2, 2, 3))], base_input()),
        ("H7", [session(1, reviewer_ids=(2, 3, 4), slot_id=2)], base_input()),
        ("H8", [session(1, reviewer_ids=(2, 3, 4))], base_input(conflicts={(2, 10)})),
        ("H9", [session(1)], base_input(round_type="DEFENSE_1_2", group_status={1: "PENDING_D11"})),
        ("H10", [session(1, slot_id=1)], base_input(group_selection_mode=True, group_selected_slots={1: {2}})),
        ("H11", [session(1)], base_input(round_type="DEFENSE_1_2", prior_reviewer_ids={1: {55}}, group_status={1: "ELIGIBLE_D12"})),
        ("H12", [session(1), session(2, group_id=2, project_id=11, slot_id=2, start_hour=10)], base_input(group_status={1: "PENDING_D11", 2: "PENDING_D11"}, group_project={1: 10, 2: 11}, project_supervisors={10: {99}, 11: {98}}, lecturer_availability={(2, 1), (3, 1), (4, 1), (2, 2), (3, 2), (4, 2)}, h12_sessions_per_part=1)),
    ],
)
def test_each_hard_constraint_returns_its_stable_rule_code(rule, schedule, context):
    result = validate_schedule(schedule, context)
    assert rule in {violation.rule for violation in result.violations}


def test_h11_waiver_allows_missing_continuity_but_is_not_a_general_waiver():
    context = base_input(
        round_type="DEFENSE_1_2",
        group_status={1: "ELIGIBLE_D12"},
        prior_reviewer_ids={1: {55}},
        h11_waiver_groups={1},
        h11_waiver_actors={1: "MANAGER"},
        h11_waiver_reasons={1: "Prior Reviewer unavailable."},
    )
    assert validate_schedule([session(1)], context).valid is True


@pytest.mark.parametrize("actor", ["ADMIN", "LECTURER", ""])
def test_h11_waiver_requires_manager_actor_and_reason(actor):
    context = base_input(
        round_type="DEFENSE_1_2",
        group_status={1: "ELIGIBLE_D12"},
        prior_reviewer_ids={1: {55}},
        h11_waiver_groups={1},
        h11_waiver_actors={1: actor},
        h11_waiver_reasons={1: "reason" if actor else ""},
    )
    assert "H11" in {violation.rule for violation in validate_schedule([session(1)], context).violations}
