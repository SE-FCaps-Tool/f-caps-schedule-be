from typing import Any

from app.scheduler.models import RoundInput


def build_input_snapshot(
    *,
    round_id: int,
    context: RoundInput,
    groups: list[int],
    timeslots: list[int],
    reviewer_assignments: dict[int, list[int]],
    soft_weights: dict[str, int],
) -> dict[str, Any]:
    return {
        "round_id": round_id,
        "round_type": context.round_type,
        "expected_reviewer_count": context.expected_reviewer_count,
        "result_owner_mode": context.result_owner_mode,
        "group_selection_mode": context.group_selection_mode,
        "groups": sorted(groups),
        "group_status": {str(group_id): context.group_status.get(group_id, "") for group_id in sorted(groups)},
        "group_project": {str(group_id): context.group_project[group_id] for group_id in sorted(groups)},
        "project_supervisors": {
            str(project_id): sorted(lecturers)
            for project_id, lecturers in sorted(context.project_supervisors.items())
        },
        "group_selected_slots": {
            str(group_id): sorted(slots)
            for group_id, slots in sorted(context.group_selected_slots.items())
        },
        "timeslots": sorted(timeslots),
        "reviewer_assignments": {
            str(group_id): sorted(reviewers)
            for group_id, reviewers in sorted(reviewer_assignments.items())
        },
        "availability": [
            {"lecturer_id": lecturer_id, "timeslot_id": timeslot_id}
            for lecturer_id, timeslot_id in sorted(context.lecturer_availability)
        ],
        "conflicts": [
            {"lecturer_id": lecturer_id, "project_id": project_id}
            for lecturer_id, project_id in sorted(context.conflicts)
        ],
        "h_rules": {
            "H11": {
                "waiver_groups": sorted(context.h11_waiver_groups),
                "waiver_actors": {
                    str(group_id): context.h11_waiver_actors[group_id]
                    for group_id in sorted(context.h11_waiver_actors)
                },
                "waiver_reasons": {
                    str(group_id): context.h11_waiver_reasons[group_id]
                    for group_id in sorted(context.h11_waiver_reasons)
                },
            },
            "H12": {
                "sessions_per_part": context.h12_sessions_per_part,
                "sessions_per_day": context.h12_sessions_per_day,
                "semester_quota": context.h12_semester_quota,
            },
        },
        "prior_reviewer_continuity": {
            str(group_id): sorted(reviewers)
            for group_id, reviewers in sorted(context.prior_reviewer_ids.items())
        },
        "committee_constraints": [list(member_ids) for member_ids in context.committee_reviewer_sets],
        "committee_constraints_active": context.has_assigned_committees,
        "soft_weights": {key: soft_weights[key] for key in sorted(soft_weights)},
        "lecturer_load_preferences": {
            str(lecturer_id): context.lecturer_load_preferences[lecturer_id]
            for lecturer_id in sorted(context.lecturer_load_preferences)
        },
    }
