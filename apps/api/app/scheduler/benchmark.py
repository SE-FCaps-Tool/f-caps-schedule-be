from datetime import UTC, datetime, timedelta

from app.scheduler.models import RoundInput


def build_target_fixture() -> tuple[RoundInput, list[int], list[tuple[int, datetime, datetime, str, str]], list[int]]:
    """Build the deterministic CI fixture named by the Phase 04 exit criteria."""
    reviewers = list(range(1, 27))
    groups = list(range(1, 75))
    group_project = {group_id: 10_000 + group_id for group_id in groups}
    timeslots: list[tuple[int, datetime, datetime, str, str]] = []
    availability: set[tuple[int, int]] = set()
    base = datetime(2030, 1, 7, 9, 0, tzinfo=UTC)
    for slot_index in range(40):
        start_at = base + timedelta(minutes=30 * slot_index)
        end_at = start_at + timedelta(minutes=30)
        day = start_at.date().isoformat()
        part = "AM" if start_at.hour < 13 else "PM"
        timeslots.append((slot_index + 1, start_at, end_at, day, part))
        slot_reviewers = [reviewers[(slot_index * 3 + offset) % len(reviewers)] for offset in range(3)]
        availability.update((reviewer_id, slot_index + 1) for reviewer_id in slot_reviewers)
    context = RoundInput(
        round_type="DEFENSE_1_1",
        expected_reviewer_count=3,
        group_status={group_id: "PENDING_D11" for group_id in groups},
        group_project=group_project,
        project_supervisors={project_id: set() for project_id in group_project.values()},
        lecturer_availability=availability,
        conflicts=set(),
        group_selected_slots={group_id: {(group_id - 1) % 40 + 1} for group_id in groups},
        group_selection_mode=True,
        prior_reviewer_ids={},
        remediation_verifier_ids={},
        h11_waiver_groups=set(),
        h12_sessions_per_part=4,
        h12_sessions_per_day=8,
        h12_semester_quota=None,
        existing_semester_load={},
    )
    return context, groups, timeslots, reviewers
