from collections import defaultdict

from app.scheduler.models import RoundInput, ScheduledSession, ValidationResult, Violation


def _overlaps(left: ScheduledSession, right: ScheduledSession) -> bool:
    return left.start_at < right.end_at and right.start_at < left.end_at


def _violation(rule: str, explanation: str, hint: str, *objects: object) -> Violation:
    return Violation(
        rule=rule,
        objects=tuple(str(obj) for obj in objects),
        severity="HARD",
        explanation=explanation,
        remediation_hint=hint,
    )


def _eligible(round_type: str, status: str) -> bool:
    if status in {"FAILED", "DROPPED"}:
        return False
    expected = {
        "DEFENSE_1_1": {"PENDING_D11"},
        "DEFENSE_1_2": {"ELIGIBLE_D12"},
        "DEFENSE_2": {"PENDING_D2"},
        "REVIEW_1": {"PENDING_D11", "ELIGIBLE_D12", "D12_CONDITIONAL", "PENDING_D2"},
        "REVIEW_2": {"PENDING_D11", "ELIGIBLE_D12", "D12_CONDITIONAL", "PENDING_D2"},
    }
    return status in expected.get(round_type, set())


def valid_h11_waiver(context: RoundInput, group_id: int) -> bool:
    return (
        group_id in context.h11_waiver_groups
        and context.h11_waiver_actors.get(group_id) == "MANAGER"
        and bool(context.h11_waiver_reasons.get(group_id, "").strip())
    )


def validate_schedule(
    sessions: list[ScheduledSession] | tuple[ScheduledSession, ...], context: RoundInput
) -> ValidationResult:
    violations: list[Violation] = []
    for current in sessions:
        supervisors = context.project_supervisors.get(current.project_id, set())
        if supervisors.intersection(current.reviewer_ids):
            violations.append(
                _violation(
                    "H1",
                    "A project Supervisor is assigned as a Reviewer of the same project.",
                    "Replace that Reviewer with a Lecturer outside the project supervision team.",
                    current.session_id,
                )
            )
        if len(current.reviewer_ids) != context.expected_reviewer_count:
            violations.append(
                _violation(
                    "H5",
                    f"The session has {len(current.reviewer_ids)} Reviewers; {context.expected_reviewer_count} are required.",
                    "Invite or assign the required number of Reviewers.",
                    current.session_id,
                )
            )
        if len(set(current.reviewer_ids)) != len(current.reviewer_ids):
            violations.append(
                _violation(
                    "H6",
                    "A Lecturer appears more than once in the same session.",
                    "Remove duplicate Reviewer assignments.",
                    current.session_id,
                )
            )
        if not _eligible(context.round_type, context.group_status.get(current.group_id, "")):
            violations.append(
                _violation(
                    "H9",
                    "The group status is not eligible for this round type.",
                    "Resolve the group result/remediation state before scheduling it.",
                    current.group_id,
                )
            )
        if current.group_id in context.group_leader_valid and not context.group_leader_valid[current.group_id]:
            violations.append(
                _violation(
                    "GROUP_LEADER",
                    "The group has no exactly one active Project Leader.",
                    "Assign exactly one active Leader before registering or scheduling the group.",
                    current.group_id,
                )
            )
        if context.group_selection_mode and current.group_id in context.group_selected_slots and (
            current.timeslot_id not in context.group_selected_slots[current.group_id]
        ):
            violations.append(
                _violation(
                    "H10",
                    "The session is outside the group's selected availability slots.",
                    "Move the session to a selected group slot or disable group selection mode.",
                    current.group_id,
                    current.timeslot_id,
                )
            )
        for reviewer_id in current.reviewer_ids:
            if (reviewer_id, current.timeslot_id) not in context.lecturer_availability:
                violations.append(
                    _violation(
                        "H7",
                        "A Reviewer is not available in the assigned timeslot.",
                        "Choose a registered available slot or record Manager-entered availability first.",
                        reviewer_id,
                        current.timeslot_id,
                    )
                )
            if (reviewer_id, current.project_id) in context.conflicts:
                violations.append(
                    _violation(
                        "H8",
                        "A Reviewer declared a conflict with this project.",
                        "Replace the Reviewer or resolve the conflict declaration.",
                        reviewer_id,
                        current.project_id,
                    )
                )
        waiver_requested = current.group_id in context.h11_waiver_groups
        if waiver_requested and not valid_h11_waiver(context, current.group_id):
            violations.append(
                _violation(
                    "H11",
                    "The H11 waiver is missing a Manager actor or a reason for this group and round.",
                    "Record a Manager-approved waiver with a non-empty reason for this group in this round.",
                    current.group_id,
                )
            )
        if context.round_type == "DEFENSE_1_2" and not valid_h11_waiver(context, current.group_id):
            continuity = set(context.prior_reviewer_ids.get(current.group_id, set()))
            continuity.update(context.remediation_verifier_ids.get(current.group_id, set()))
            if not continuity.intersection(current.reviewer_ids):
                violations.append(
                    _violation(
                        "H11",
                        "Defense 1.2 has no Reviewer with continuity from Defense 1.1.",
                        "Assign a prior Reviewer, choose the Remediation Verifier, or obtain an audited H11 waiver.",
                        current.group_id,
                    )
                )

    for index, current in enumerate(sessions):
        for other in sessions[index + 1 :]:
            if _overlaps(current, other):
                if set(current.reviewer_ids).intersection(other.reviewer_ids):
                    violations.append(
                        _violation(
                            "H2",
                            "A Lecturer is assigned to overlapping sessions.",
                            "Move one session or replace the shared Lecturer.",
                            current.session_id,
                            other.session_id,
                        )
                    )
                if current.room_id == other.room_id:
                    violations.append(
                        _violation(
                            "H3",
                            "A room is assigned to overlapping sessions.",
                            "Move one session to another room or non-overlapping timeslot.",
                            current.room_id,
                            current.session_id,
                            other.session_id,
                        )
                    )
    groups: dict[int, list[int]] = defaultdict(list)
    for current in sessions:
        groups[current.group_id].append(current.session_id)
    for group_id, session_ids in groups.items():
        if len(session_ids) > 1:
            violations.append(
                _violation(
                    "H4",
                    "A group has more than one session in this ScheduleVersion.",
                    "Keep exactly one session for the group in the active version.",
                    group_id,
                )
            )

    part_load: dict[tuple[int, str, str], int] = defaultdict(int)
    day_load: dict[tuple[int, str], int] = defaultdict(int)
    semester_load: dict[int, int] = defaultdict(int, context.existing_semester_load)
    for current in sessions:
        for reviewer_id in current.reviewer_ids:
            part_load[(reviewer_id, current.day, current.part)] += 1
            day_load[(reviewer_id, current.day)] += 1
            semester_load[reviewer_id] += 1
    for (reviewer_id, day, part), count in part_load.items():
        if count > context.h12_sessions_per_part:
            violations.append(
                _violation(
                    "H12",
                    f"Lecturer {reviewer_id} has {count} sessions in {part}; the limit is {context.h12_sessions_per_part}.",
                    "Move a session or adjust the configured session-count quota.",
                    reviewer_id,
                    day,
                    part,
                )
            )
    for (reviewer_id, day), count in day_load.items():
        if count > context.h12_sessions_per_day:
            violations.append(
                _violation(
                    "H12",
                    f"Lecturer {reviewer_id} has {count} sessions on {day}; the daily limit is {context.h12_sessions_per_day}.",
                    "Move a session to another day or use another Lecturer.",
                    reviewer_id,
                    day,
                )
            )
    if context.h12_semester_quota is not None:
        for reviewer_id, count in semester_load.items():
            if count > context.h12_semester_quota:
                violations.append(
                    _violation(
                        "H12",
                        f"Lecturer {reviewer_id} exceeds the semester session quota.",
                        "Choose another Lecturer or configure a valid semester session quota.",
                        reviewer_id,
                    )
                )
    return ValidationResult(tuple(violations))
