from app.scheduler.candidates import generate_candidates, reason_for_unscheduled
from app.scheduler.models import RoundInput
from app.scheduler.snapshot import build_input_snapshot


def candidate_input() -> RoundInput:
    return RoundInput(
        round_type="REVIEW_3",
        expected_reviewer_count=3,
        group_status={1: "PENDING_D11"},
        group_project={1: 10},
        project_supervisors={10: {99}},
        lecturer_availability={(2, 1), (3, 1), (4, 1), (2, 2), (3, 2), (4, 2)},
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


def test_candidate_generator_filters_supervisor_and_unavailable_reviewer():
    context = candidate_input()
    candidates = generate_candidates(
        context,
        groups=[1],
        timeslots=[(1, "2030-01-01", "AM")],
        reviewers=[2, 3, 4, 99],
    )
    assert candidates
    assert all(99 not in candidate.reviewer_ids for candidate in candidates)
    assert all(set(candidate.reviewer_ids) == {2, 3, 4} for candidate in candidates)


def test_unscheduled_reason_has_one_stable_reason_code():
    context = candidate_input()
    reason = reason_for_unscheduled(1, context, reviewers=[], timeslots=[1])
    assert reason.code == "NO_REVIEWER_AVAILABILITY"
    assert reason.explanation
    assert reason.remediation_hint


def test_snapshot_is_deterministic_and_contains_provenance():
    context = candidate_input()
    first = build_input_snapshot(
        round_id=7,
        context=context,
        groups=[1],
        timeslots=[1, 2],
        reviewer_assignments={1: [2, 3, 4]},
        soft_weights={"S1": 2, "S2": 1},
    )
    second = build_input_snapshot(
        round_id=7,
        context=context,
        groups=[1],
        timeslots=[1, 2],
        reviewer_assignments={1: [2, 3, 4]},
        soft_weights={"S1": 2, "S2": 1},
    )
    assert first == second
    assert first["round_id"] == 7
    assert first["h_rules"]["H12"]["sessions_per_part"] == 4
