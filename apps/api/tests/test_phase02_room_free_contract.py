"""Contract tests for the room-free scheduler boundary (Phase 2)."""

from dataclasses import fields
from datetime import UTC, datetime, timedelta
from inspect import getsource, signature
from typing import get_type_hints

from app.scheduler.candidates import generate_candidates, reason_for_unscheduled
from app.scheduler.models import Candidate, RoundInput, ScheduledSession
from app.scheduler.scheduler import (
    _aggregate_soft_scores,
    _candidate_soft_scores,
    solve_schedule,
)
from app.scheduler.snapshot import build_input_snapshot


def context() -> RoundInput:
    return RoundInput(
        round_type="REVIEW_3",
        expected_reviewer_count=3,
        group_status={1: "PENDING_D11"},
        group_project={1: 10},
        project_supervisors={10: set()},
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


def timeslot(slot_id: int = 1) -> tuple[int, datetime, datetime, str, str]:
    start = datetime(2030, 1, 1, 9, tzinfo=UTC)
    return slot_id, start, start + timedelta(minutes=30), "2030-01-01", "AM"


def test_candidate_and_scheduled_session_models_have_the_expected_room_boundary():
    assert "room_id" not in {field.name for field in fields(Candidate)}
    assert get_type_hints(ScheduledSession)["room_id"] == int | None


def test_candidate_generation_has_no_room_input_or_candidate_dimension():
    candidates = generate_candidates(
        context(),
        groups=[1],
        timeslots=[timeslot()],
        reviewers=[2, 3, 4],
    )

    assert len(candidates) == 1
    assert not hasattr(candidates[0], "room_id")


def test_unscheduled_diagnostics_do_not_require_or_report_room_inventory():
    reason = reason_for_unscheduled(1, context(), reviewers=[2, 3, 4], timeslots=[1])

    assert reason.code != "NO_ROOM"
    assert "room" not in f"{reason.explanation} {reason.remediation_hint}".lower()


def test_solver_accepts_no_rooms_and_emits_unassigned_sessions():
    result = solve_schedule(
        context(),
        groups=[1],
        timeslots=[timeslot()],
        reviewers=[2, 3, 4],
        time_limit_seconds=2,
        random_seed=7,
    )

    assert len(result.sessions) == 1
    assert result.sessions[0].room_id is None
    assert result.soft_scores["S8"] == 0


def test_snapshot_has_no_solver_room_provenance_dimension():
    snapshot = build_input_snapshot(
        round_id=7,
        context=context(),
        groups=[1],
        timeslots=[1],
        reviewer_assignments={1: [2, 3, 4]},
        soft_weights={"S1": 2},
    )

    assert "rooms" not in snapshot


def test_solver_signatures_and_scoring_keys_are_room_free():
    assert "rooms" not in signature(generate_candidates).parameters
    assert "rooms" not in signature(reason_for_unscheduled).parameters
    assert "rooms" not in signature(solve_schedule).parameters
    assert "rooms" not in signature(_candidate_soft_scores).parameters

    candidate = generate_candidates(
        context(), groups=[1], timeslots=[timeslot()], reviewers=[2, 3, 4]
    )[0]
    assert _candidate_soft_scores(candidate, context())["S8"] == 0
    assert _aggregate_soft_scores([{"S8": 0}], [candidate], [candidate])["S8"] == 0


def test_solver_sources_contain_no_room_dimension_or_no_room_diagnostic():
    from app.scheduler import candidates, scheduler

    for module in (candidates, scheduler):
        source = getsource(module)
        assert "room_id" not in source
        assert "rooms" not in source
        assert "NO_ROOM" not in source
