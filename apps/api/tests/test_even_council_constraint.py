from datetime import UTC, datetime

from app.scheduler.models import RoundInput
from app.scheduler.scheduler import solve_schedule
from app.scheduler.validator import validate_schedule


def test_even_council_constraint_enforced_for_all_lecturers():
    """Verify every lecturer is assigned an even number of sessions (0, 2, 4, ...)."""
    context = RoundInput(
        round_type="DEFENSE_1_1",
        expected_reviewer_count=3,
        group_status={1: "PENDING_D11", 2: "PENDING_D11", 3: "PENDING_D11", 4: "PENDING_D11"},
        group_project={1: 10, 2: 11, 3: 12, 4: 13},
        project_supervisors={10: {99}, 11: {98}, 12: {97}, 13: {96}},
        lecturer_availability={
            (101, 1), (102, 1), (103, 1), (104, 1), (105, 1), (106, 1),
            (101, 2), (102, 2), (103, 2), (104, 2), (105, 2), (106, 2),
            (101, 3), (102, 3), (103, 3), (104, 3), (105, 3), (106, 3),
            (101, 4), (102, 4), (103, 4), (104, 4), (105, 4), (106, 4),
        },
        conflicts=set(),
        group_selected_slots={},
        group_selection_mode=False,
        prior_reviewer_ids={},
        remediation_verifier_ids={},
        h11_waiver_groups={1, 2, 3, 4},
        h11_waiver_actors={1: "MANAGER", 2: "MANAGER", 3: "MANAGER", 4: "MANAGER"},
        h11_waiver_reasons={1: "waiver", 2: "waiver", 3: "waiver", 4: "waiver"},
        h12_sessions_per_part=4,
        h12_sessions_per_day=8,
        h12_semester_quota=None,
        existing_semester_load={},
    )
    timeslots = [
        (1, datetime(2026, 10, 1, 8, tzinfo=UTC), datetime(2026, 10, 1, 9, tzinfo=UTC), "2026-10-01", "AM"),
        (2, datetime(2026, 10, 1, 9, tzinfo=UTC), datetime(2026, 10, 1, 10, tzinfo=UTC), "2026-10-01", "AM"),
        (3, datetime(2026, 10, 1, 10, tzinfo=UTC), datetime(2026, 10, 1, 11, tzinfo=UTC), "2026-10-01", "AM"),
        (4, datetime(2026, 10, 1, 11, tzinfo=UTC), datetime(2026, 10, 1, 12, tzinfo=UTC), "2026-10-01", "AM"),
    ]
    reviewers = [101, 102, 103, 104, 105, 106]

    result = solve_schedule(
        context,
        groups=[1, 2, 3, 4],
        timeslots=timeslots,
        reviewers=reviewers,
        time_limit_seconds=5,
        random_seed=42,
    )

    assert result.status in {"OPTIMAL", "FEASIBLE"}
    assert len(result.sessions) == 4
    assert validate_schedule(result.sessions, context).valid

    # Check that every reviewer has an even count (0, 2, 4, 6...)
    counts = {r: 0 for r in reviewers}
    for session in result.sessions:
        for reviewer_id in session.reviewer_ids:
            counts[reviewer_id] += 1

    for reviewer_id, count in counts.items():
        assert count % 2 == 0, f"Reviewer {reviewer_id} has odd count {count}!"
