from collections import Counter
from datetime import UTC, datetime, timedelta

from app.scheduler.models import RoundInput
from app.scheduler.scheduler import solve_schedule
from app.scheduler.validator import validate_schedule


def test_solver_returns_validator_safe_partial_schedule_with_reason_codes():
    context = RoundInput(
        round_type="REVIEW_3",
        expected_reviewer_count=3,
        group_status={1: "PENDING_D11", 2: "PENDING_D11"},
        group_project={1: 10, 2: 11},
        project_supervisors={10: {99}, 11: {98}},
        lecturer_availability={(2, 1), (3, 1), (4, 1)},
        conflicts=set(),
        group_selected_slots={},
        group_selection_mode=False,
        prior_reviewer_ids={},
        remediation_verifier_ids={},
        h11_waiver_groups=set(),
        h12_sessions_per_part=4,
        h12_sessions_per_day=8,
        h12_semester_quota=None,
        existing_semester_load={},
    )
    result = solve_schedule(
        context,
        groups=[1, 2],
        timeslots=[(1, datetime(2030, 1, 1, 9, tzinfo=UTC), datetime(2030, 1, 1, 9, 30, tzinfo=UTC), "2030-01-01", "AM")],
        reviewers=[2, 3, 4],
        time_limit_seconds=2,
        random_seed=7,
    )
    assert result.status in {"OPTIMAL", "FEASIBLE", "PARTIAL"}
    assert validate_schedule(result.sessions, context).valid
    assert len(result.unscheduled) == 1
    assert result.unscheduled[0].code == "NO_TIMESLOT"
    assert result.soft_scores == solve_schedule(
        context,
        groups=[1, 2],
        timeslots=[(1, datetime(2030, 1, 1, 9, tzinfo=UTC), datetime(2030, 1, 1, 9, 30, tzinfo=UTC), "2030-01-01", "AM")],
            reviewers=[2, 3, 4],
        time_limit_seconds=2,
        random_seed=7,
    ).soft_scores


def test_solver_balances_reviewer_load_when_quota_and_s1_are_configured():
    groups = list(range(1, 9))
    reviewers = list(range(1, 5))
    base = datetime(2030, 1, 7, 9, tzinfo=UTC)
    timeslots = []
    for day_index in range(2):
        for slot_index in range(4):
            timeslot_id = day_index * 4 + slot_index + 1
            start_at = base + timedelta(days=day_index, minutes=30 * slot_index)
            timeslots.append(
                (
                    timeslot_id,
                    start_at,
                    start_at + timedelta(minutes=30),
                    start_at.date().isoformat(),
                    "AM",
                )
            )
    context = RoundInput(
        round_type="REVIEW_3",
        expected_reviewer_count=3,
        group_status={group_id: "PENDING_D11" for group_id in groups},
        group_project={group_id: 1000 + group_id for group_id in groups},
        project_supervisors={1000 + group_id: set() for group_id in groups},
        lecturer_availability={(reviewer_id, slot[0]) for reviewer_id in reviewers for slot in timeslots},
        conflicts=set(),
        group_selected_slots={},
        group_selection_mode=False,
        prior_reviewer_ids={},
        remediation_verifier_ids={},
        h11_waiver_groups=set(),
        h12_sessions_per_part=4,
        h12_sessions_per_day=8,
        h12_semester_quota=8,
        existing_semester_load={},
        soft_weights={"S1": 1},
    )

    result = solve_schedule(
        context,
        groups=groups,
        timeslots=timeslots,
        reviewers=reviewers,
        time_limit_seconds=5,
        random_seed=17,
    )

    loads = Counter(reviewer_id for session in result.sessions for reviewer_id in session.reviewer_ids)
    assert len(result.sessions) == len(groups)
    assert set(loads) == set(reviewers)
    assert max(loads.values()) / min(loads.values()) <= 1.5
    assert validate_schedule(result.sessions, context).valid
