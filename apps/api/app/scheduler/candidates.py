from datetime import UTC, datetime, timedelta
from itertools import combinations

from app.scheduler.models import Candidate, RoundInput, UnscheduledReason
from app.scheduler.validator import _eligible, valid_h11_waiver


def generate_candidates(
    context: RoundInput,
    *,
    groups: list[int],
    timeslots: list[tuple[object, ...]],
    rooms: list[int],
    reviewers: list[int],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for group_id in sorted(groups):
        if group_id in context.group_leader_valid and not context.group_leader_valid[group_id]:
            continue
        project_id = context.group_project[group_id]
        if not _eligible(context.round_type, context.group_status.get(group_id, "")):
            continue
        allowed_reviewers = [
            reviewer_id
            for reviewer_id in sorted(reviewers)
            if (reviewer_id, project_id) not in context.conflicts
            and reviewer_id not in context.project_supervisors.get(project_id, set())
        ]
        for raw_timeslot in sorted(timeslots, key=lambda value: value[0]):
            timeslot_id, start_at, end_at, day, part = _normalize_timeslot(raw_timeslot)
            if context.group_selection_mode and group_id in context.group_selected_slots and (
                timeslot_id not in context.group_selected_slots[group_id]
            ):
                continue
            available = [
                reviewer_id
                for reviewer_id in allowed_reviewers
                if (reviewer_id, timeslot_id) in context.lecturer_availability
            ]
            if context.round_type == "DEFENSE_1_2" and not valid_h11_waiver(context, group_id):
                continuity = set(context.prior_reviewer_ids.get(group_id, set()))
                continuity.update(context.remediation_verifier_ids.get(group_id, set()))
                available = [reviewer_id for reviewer_id in available if reviewer_id in continuity]
            for reviewer_ids in combinations(available, context.expected_reviewer_count):
                for room_id in sorted(rooms):
                    candidates.append(
                        Candidate(
                            group_id=group_id,
                            timeslot_id=timeslot_id,
                            room_id=room_id,
                            start_at=start_at,
                            end_at=end_at,
                            day=day,
                            part=part,
                            reviewer_ids=reviewer_ids,
                        )
                    )
    return candidates


def _normalize_timeslot(raw_timeslot: tuple[object, ...]):
    if len(raw_timeslot) == 5:
        return raw_timeslot
    if len(raw_timeslot) == 3:
        timeslot_id, day, part = raw_timeslot
        start_at = datetime(1970, 1, 1, 0, 0, tzinfo=UTC)
        end_at = start_at + timedelta(minutes=30)
        return timeslot_id, start_at, end_at, day, part
    raise ValueError("A timeslot must contain id, start, end, day and part.")


def reason_for_unscheduled(
    group_id: int,
    context: RoundInput,
    *,
    reviewers: list[int],
    timeslots: list[int],
    rooms: list[int],
) -> UnscheduledReason:
    project_id = context.group_project.get(group_id)
    if not reviewers:
        return UnscheduledReason(
            "NO_REVIEWER_AVAILABILITY",
            "No Reviewer is available for this group.",
            "Invite more Reviewers or collect more availability.",
        )
    if group_id in context.group_leader_valid and not context.group_leader_valid[group_id]:
        return UnscheduledReason(
            "MISSING_LEADER",
            "The group has no exactly one active Project Leader.",
            "Assign exactly one active Leader before running the scheduler.",
        )
    if project_id is not None and context.project_supervisors.get(project_id, set()).intersection(reviewers):
        return UnscheduledReason(
            "H1_CONFLICT",
            "Available Reviewers include the project's Supervisor, which is forbidden by H1.",
            "Choose a Reviewer outside the project supervision team.",
        )
    if project_id is not None and any((reviewer_id, project_id) in context.conflicts for reviewer_id in reviewers):
        return UnscheduledReason(
            "H8_CONFLICT",
            "Available Reviewers have conflict declarations for this project.",
            "Resolve the conflict or invite another Reviewer.",
        )
    if not timeslots:
        return UnscheduledReason(
            "NO_TIMESLOT",
            "The round has no usable timeslot for this group.",
            "Add a valid timeslot or collect group availability.",
        )
    usable_timeslots = set(timeslots)
    if context.group_selection_mode and group_id in context.group_selected_slots:
        usable_timeslots.intersection_update(context.group_selected_slots[group_id])
    available_reviewers = {
        reviewer_id
        for reviewer_id in reviewers
        if any((reviewer_id, timeslot_id) in context.lecturer_availability for timeslot_id in usable_timeslots)
    }
    if not available_reviewers:
        return UnscheduledReason(
            "NO_REVIEWER_AVAILABILITY",
            "No eligible Reviewer has availability in the usable group slots.",
            "Invite more Reviewers or collect availability for the round slots.",
        )
    if context.round_type == "DEFENSE_1_2" and not valid_h11_waiver(context, group_id):
        continuity = set(context.prior_reviewer_ids.get(group_id, set()))
        continuity.update(context.remediation_verifier_ids.get(group_id, set()))
        if not continuity.intersection(reviewers):
            return UnscheduledReason(
                "H11_CONTINUITY",
                "No available Reviewer satisfies Defense 1.2 continuity.",
                "Assign a prior Reviewer, the Verifier, or record an approved H11 waiver.",
            )
        if not continuity.intersection(available_reviewers):
            return UnscheduledReason(
                "H11_CONTINUITY",
                "No available Reviewer satisfies Defense 1.2 continuity.",
                "Assign a prior Reviewer, the Verifier, or record an approved H11 waiver.",
            )
    if not rooms:
        return UnscheduledReason(
            "NO_ROOM",
            "The round has no usable room for this group.",
            "Add an active room to the round.",
        )
    return UnscheduledReason(
        "NO_TIMESLOT",
        "No combination of hard constraints produced a candidate session.",
        "Add availability, timeslots or rooms, then run the scheduler again.",
    )
