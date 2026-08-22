from dataclasses import replace

from app.scheduler.candidates import generate_candidates
from app.scheduler.models import RoundInput
from app.scheduler.snapshot import build_input_snapshot

SLOT_A = (1, "2030-01-01", "AM")
SLOT_B = (2, "2030-01-01", "PM")


def committee_input(**overrides) -> RoundInput:
    """Two reviewers per session, four lecturers available across two slots."""

    base = RoundInput(
        round_type="REVIEW_1",
        expected_reviewer_count=2,
        group_status={1: "PENDING_D11"},
        group_project={1: 10},
        project_supervisors={},
        lecturer_availability={(2, 1), (3, 1), (4, 1), (5, 1), (2, 2), (3, 2), (4, 2), (5, 2)},
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
    return replace(base, **overrides)


def generate(context: RoundInput, timeslots=(SLOT_A,), reviewers=(2, 3, 4, 5)):
    return generate_candidates(
        context,
        groups=[1],
        timeslots=list(timeslots),
        reviewers=list(reviewers),
    )


def test_without_committees_the_free_pool_combinations_are_unchanged():
    candidates = generate(committee_input())

    assert {candidate.reviewer_ids for candidate in candidates} == {
        (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)
    }


def test_assigned_committees_restrict_candidates_to_their_exact_member_sets():
    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3), (4, 5)),
    )

    candidates = generate(context)

    assert {candidate.reviewer_ids for candidate in candidates} == {(2, 3), (4, 5)}


def test_partial_availability_never_mixes_members_of_two_committees():
    """Only 2 and 4 are free in this slot, one from each Committee."""

    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3), (4, 5)),
        lecturer_availability={(2, 1), (4, 1)},
    )

    assert generate(context) == []


def test_a_committee_losing_one_member_drops_out_for_that_slot_only():
    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3),),
        lecturer_availability={(2, 1), (2, 2), (3, 2)},
    )

    candidates = generate(context, timeslots=(SLOT_A, SLOT_B))

    assert [(candidate.timeslot_id, candidate.reviewer_ids) for candidate in candidates] == [(2, (2, 3))]


def test_supervisor_conflict_excludes_the_whole_committee():
    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3), (4, 5)),
        project_supervisors={10: {3}},
    )

    candidates = generate(context)

    assert {candidate.reviewer_ids for candidate in candidates} == {(4, 5)}
    assert all(3 not in candidate.reviewer_ids for candidate in candidates)


def test_declared_conflict_excludes_the_whole_committee():
    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3), (4, 5)),
        conflicts={(5, 10)},
    )

    candidates = generate(context)

    assert {candidate.reviewer_ids for candidate in candidates} == {(2, 3)}


def test_h11_continuity_excludes_partially_matching_committees():
    context = committee_input(
        round_type="DEFENSE_1",
        group_status={1: "ELIGIBLE_D12"},
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3), (4, 5)),
        prior_reviewer_ids={1: {2, 3, 4}},
    )

    candidates = generate(context)

    assert {candidate.reviewer_ids for candidate in candidates} == {(2, 3)}


def test_assigned_but_fully_ineligible_committees_produce_no_candidates():
    """The empty tuple must not be read as "no Committee bound to this Round"."""

    context = committee_input(has_assigned_committees=True, committee_reviewer_sets=())

    assert generate(context) == []


def test_a_committee_sized_against_another_round_is_skipped():
    context = committee_input(
        has_assigned_committees=True,
        committee_reviewer_sets=((2, 3, 4),),
    )

    assert generate(context) == []


def test_snapshot_separates_no_committees_from_none_eligible():
    def snapshot_for(context: RoundInput) -> dict:
        return build_input_snapshot(
            round_id=7,
            context=context,
            groups=[1],
            timeslots=[1],
            reviewer_assignments={1: [2, 3]},
            soft_weights={},
        )

    none_bound = snapshot_for(committee_input())
    assert none_bound["committee_constraints"] == []
    assert none_bound["committee_constraints_active"] is False

    bound = snapshot_for(
        committee_input(has_assigned_committees=True, committee_reviewer_sets=((2, 3), (4, 5)))
    )
    assert bound["committee_constraints"] == [[2, 3], [4, 5]]
    assert bound["committee_constraints_active"] is True

    all_filtered = snapshot_for(committee_input(has_assigned_committees=True))
    assert all_filtered["committee_constraints"] == []
    assert all_filtered["committee_constraints_active"] is True
