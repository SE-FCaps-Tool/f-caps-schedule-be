from collections import defaultdict
from datetime import datetime
from itertools import pairwise
from typing import Any

from ortools.sat.python import cp_model

from app.domain.errors import DomainError
from app.scheduler.candidates import generate_candidates, reason_for_unscheduled
from app.scheduler.models import (
    Candidate,
    RoundInput,
    ScheduledSession,
    SchedulerObjectiveProfile,
    SolverResult,
)
from app.scheduler.validator import validate_schedule


def _overlap(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return left_start < right_end and right_start < left_end


def solve_schedule(
    context: RoundInput,
    *,
    groups: list[int],
    timeslots: list[tuple[int, datetime, datetime, str, str]],
    reviewers: list[int],
    time_limit_seconds: float = 10,
    random_seed: int = 0,
    objective_profile: SchedulerObjectiveProfile = "LEGACY",
    candidate_pool: list[Candidate] | None = None,
) -> SolverResult:
    candidates = candidate_pool if candidate_pool is not None else generate_candidates(
        context, groups=groups, timeslots=timeslots, reviewers=reviewers
    )
    if not candidates:
        unscheduled = tuple(
            reason_for_unscheduled(
                group_id,
                context,
                reviewers=reviewers,
                timeslots=[timeslot[0] for timeslot in timeslots],
            )
            for group_id in sorted(groups)
        )
        return SolverResult(
            "PARTIAL",
            (),
            unscheduled,
            _empty_soft_scores(),
            random_seed,
            0,
            objective_profile,
            _schedule_metrics(()),
        )

    model = cp_model.CpModel()
    variables = [model.new_bool_var(f"candidate_{index}") for index in range(len(candidates))]
    candidate_soft_scores = [_candidate_soft_scores(candidate, context) for candidate in candidates]
    weighted_scores = [
        sum(context.soft_weights.get(rule, 0) * score for rule, score in scores.items())
        for scores in candidate_soft_scores
    ]
    by_group: dict[int, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        by_group[candidate.group_id].append(index)
    for indexes in by_group.values():
        model.add_at_most_one(variables[index] for index in indexes)

    if context.max_groups_per_timeslot is not None:
        by_timeslot: dict[int, list[int]] = defaultdict(list)
        for index, candidate in enumerate(candidates):
            by_timeslot[candidate.timeslot_id].append(index)
        for indexes in by_timeslot.values():
            model.add(sum(variables[index] for index in indexes) <= context.max_groups_per_timeslot)
    for reviewer_id in reviewers:
        _add_resource_overlap_constraints(model, variables, candidates, "reviewer", reviewer_id)

    for reviewer_id in reviewers:
        for day, part, limit in _load_limits(candidates, reviewer_id, context):
            indexes = [
                index
                for index, candidate in enumerate(candidates)
                if reviewer_id in candidate.reviewer_ids and candidate.day == day and candidate.part == part
            ]
            if indexes:
                model.add(sum(variables[index] for index in indexes) <= limit)
        if context.h12_semester_quota is not None:
            indexes = [index for index, candidate in enumerate(candidates) if reviewer_id in candidate.reviewer_ids]
            if indexes:
                model.add(
                    sum(variables[index] for index in indexes)
                    <= max(0, context.h12_semester_quota - context.existing_semester_load.get(reviewer_id, 0))
                )
        if context.max_minutes_per_part is not None:
            for day, part in {(candidate.day, candidate.part) for candidate in candidates if reviewer_id in candidate.reviewer_ids}:
                indexes = [
                    index for index, candidate in enumerate(candidates)
                    if reviewer_id in candidate.reviewer_ids and candidate.day == day and candidate.part == part
                ]
                if indexes:
                    model.add(sum(max(0, int((candidates[index].end_at - candidates[index].start_at).total_seconds() // 60)) * variables[index] for index in indexes) <= context.max_minutes_per_part)
        if context.max_minutes_per_day is not None:
            for day in {candidate.day for candidate in candidates if reviewer_id in candidate.reviewer_ids}:
                indexes = [index for index, candidate in enumerate(candidates) if reviewer_id in candidate.reviewer_ids and candidate.day == day]
                if indexes:
                    model.add(sum(max(0, int((candidates[index].end_at - candidates[index].start_at).total_seconds() // 60)) * variables[index] for index in indexes) <= context.max_minutes_per_day)

    secondary_bound = sum(abs(score) for score in weighted_scores)
    balance_weight = (
        max(0, context.soft_weights.get("S1", 1))
        if context.h12_semester_quota is not None and objective_profile == "LEGACY"
        else 0
    )
    balance_expression = 0
    balance_bound = 0
    if balance_weight:
        existing_load_max = max(context.existing_semester_load.values(), default=0)
        load_upper_bound = existing_load_max + len(groups)
        reviewer_loads = []
        for reviewer_id in reviewers:
            load = model.new_int_var(0, load_upper_bound, f"reviewer_load_{reviewer_id}")
            assigned = sum(
                variables[index]
                for index, candidate in enumerate(candidates)
                if reviewer_id in candidate.reviewer_ids
            )
            model.add(load == context.existing_semester_load.get(reviewer_id, 0) + assigned)
            reviewer_loads.append(load)
        minimum_load = model.new_int_var(0, load_upper_bound, "minimum_reviewer_load")
        maximum_load = model.new_int_var(0, load_upper_bound, "maximum_reviewer_load")
        model.add_min_equality(minimum_load, reviewer_loads)
        model.add_max_equality(maximum_load, reviewer_loads)
        balance_expression = balance_weight * (minimum_load - maximum_load)
        balance_bound = balance_weight * load_upper_bound

    profile_expression = 0
    profile_bound = 0
    if objective_profile == "LECTURER_COMPACT":
        profile_expression, profile_bound = _add_compactness_objective(
            model, variables, candidates, reviewers
        )
    elif objective_profile == "LOAD_BALANCED":
        profile_expression, profile_bound = _add_load_balance_objective(
            model, variables, candidates, reviewers, groups, context
        )
    elif objective_profile == "EARLY_FINISH":
        profile_expression, profile_bound = _add_early_finish_objective(
            model, variables, candidates
        )

    primary_bonus = secondary_bound + balance_bound + profile_bound + 1
    model.maximize(
        sum((primary_bonus + weighted_scores[index]) * variables[index] for index in range(len(candidates)))
        + balance_expression
        + profile_expression
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.random_seed = random_seed
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    status_name = solver.status_name(status)
    if status_name not in {"OPTIMAL", "FEASIBLE"}:
        # CpSolver.value() is undefined for UNKNOWN/INFEASIBLE/MODEL_INVALID.
        # Reading those values can fabricate overlapping sessions that the
        # shared validator correctly rejects as SOLVER_OUTPUT_INVALID.
        unscheduled = tuple(
            reason_for_unscheduled(
                group_id,
                context,
                reviewers=reviewers,
                timeslots=[timeslot[0] for timeslot in timeslots],
            )
            for group_id in sorted(groups)
        )
        return SolverResult(
            "PARTIAL",
            (),
            unscheduled,
            _empty_soft_scores(),
            random_seed,
            0,
            objective_profile,
            _schedule_metrics(()),
        )
    selected = [candidate for index, candidate in enumerate(candidates) if solver.value(variables[index])]
    sessions = tuple(
        ScheduledSession(
            candidate.group_id,
            candidate.group_id,
            context.group_project[candidate.group_id],
            candidate.timeslot_id,
            None,
            candidate.start_at,
            candidate.end_at,
            candidate.reviewer_ids,
            candidate.day,
            candidate.part,
        )
        for candidate in sorted(selected, key=lambda item: item.group_id)
    )
    validation = validate_schedule(sessions, context)
    if not validation.valid:
        raise DomainError(
            "SOLVER_OUTPUT_INVALID",
            "The solver returned a schedule that violates the shared hard-constraint validator.",
        )
    scheduled_groups = {session.group_id for session in sessions}
    unscheduled = tuple(
        reason_for_unscheduled(
            group_id,
            context,
            reviewers=reviewers,
            timeslots=[timeslot[0] for timeslot in timeslots],
        )
        for group_id in sorted(groups)
        if group_id not in scheduled_groups
    )
    solver_status = "PARTIAL" if unscheduled and status_name in {"OPTIMAL", "FEASIBLE"} else status_name
    soft_scores = _aggregate_soft_scores(
        candidate_soft_scores,
        candidates,
        selected,
    )
    return SolverResult(
        solver_status,
        sessions,
        unscheduled,
        soft_scores,
        random_seed,
        int(solver.objective_value),
        objective_profile,
        _schedule_metrics(sessions),
    )


def _load_limits(candidates: list[object], reviewer_id: int, context: RoundInput):
    seen = {(candidate.day, candidate.part) for candidate in candidates if reviewer_id in candidate.reviewer_ids}
    return [(day, part, context.h12_sessions_per_part) for day, part in sorted(seen)]


def _add_resource_overlap_constraints(
    model: cp_model.CpModel,
    variables: list[cp_model.IntVar],
    candidates: list[object],
    resource: str,
    resource_id: int | None = None,
) -> None:
    buckets: dict[int, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        if resource == "reviewer" and resource_id in candidate.reviewer_ids:
            key = resource_id
        else:
            continue
        buckets[key].append(index)
    for indexes in buckets.values():
        active: list[int] = []
        for index in sorted(indexes, key=lambda item: (candidates[item].start_at, item)):
            current = candidates[index]
            active = [
                other_index
                for other_index in active
                if candidates[other_index].end_at > current.start_at
            ]
            for other_index in active:
                if _overlap(
                    candidates[other_index].start_at,
                    candidates[other_index].end_at,
                    current.start_at,
                    current.end_at,
                ):
                    model.add(variables[other_index] + variables[index] <= 1)
            active.append(index)


def _empty_soft_scores() -> dict[str, int]:
    return {f"S{i}": 0 for i in range(1, 10)}


def _add_compactness_objective(
    model: cp_model.CpModel,
    variables: list[cp_model.IntVar],
    candidates: list[Candidate],
    reviewers: list[int],
) -> tuple[cp_model.LinearExpr, int]:
    """Reward directly adjacent occupied slots for each reviewer/day.

    A reviewer can only occupy one candidate at a time because the overlap
    constraints are already installed. The occupancy variables therefore let
    the objective prefer one compact work block without changing feasibility.
    Breaks represented by a real time gap are intentionally not considered
    adjacent, so availability and configured breaks remain respected.
    """
    slots_by_reviewer_day: dict[tuple[int, str], dict[int, list[int]]] = defaultdict(dict)
    slot_times: dict[tuple[str, int], tuple[datetime, datetime]] = {}
    for index, candidate in enumerate(candidates):
        slot_times[(candidate.day, candidate.timeslot_id)] = (candidate.start_at, candidate.end_at)
        for reviewer_id in candidate.reviewer_ids:
            bucket = slots_by_reviewer_day.setdefault((reviewer_id, candidate.day), {})
            bucket.setdefault(candidate.timeslot_id, []).append(index)

    adjacency_terms: list[cp_model.IntVar] = []
    possible_edges = 0
    for (reviewer_id, day), slot_map in slots_by_reviewer_day.items():
        ordered_slots = sorted(
            slot_map,
            key=lambda slot_id: (slot_times[(day, slot_id)][0], slot_times[(day, slot_id)][1], slot_id),
        )
        occupied: list[cp_model.IntVar] = []
        for slot_id in ordered_slots:
            occupied_var = model.new_bool_var(f"occupied_{reviewer_id}_{day}_{slot_id}")
            indexes = slot_map[slot_id]
            model.add(occupied_var == sum(variables[index] for index in indexes))
            occupied.append(occupied_var)
        for previous_slot, current_slot, previous, current in zip(
            ordered_slots, ordered_slots[1:], occupied, occupied[1:]
        ):
            previous_end = slot_times[(day, previous_slot)][1]
            current_start = slot_times[(day, current_slot)][0]
            if previous_end != current_start:
                continue
            possible_edges += 1
            adjacent = model.new_bool_var(f"adjacent_{reviewer_id}_{day}_{current_slot}")
            model.add_bool_and([previous, current]).only_enforce_if(adjacent)
            model.add_bool_or([previous.Not(), current.Not()]).only_enforce_if(adjacent.Not())
            adjacency_terms.append(adjacent)

    return 100 * sum(adjacency_terms), possible_edges * 100


def _add_load_balance_objective(
    model: cp_model.CpModel,
    variables: list[cp_model.IntVar],
    candidates: list[Candidate],
    reviewers: list[int],
    groups: list[int],
    context: RoundInput,
) -> tuple[cp_model.LinearExpr, int]:
    if not reviewers:
        return 0, 0
    load_upper_bound = max(context.existing_semester_load.values(), default=0) + len(groups)
    loads: list[cp_model.IntVar] = []
    minutes: list[cp_model.IntVar] = []
    max_duration = max(
        (max(0, int((candidate.end_at - candidate.start_at).total_seconds() // 60)) for candidate in candidates),
        default=0,
    )
    minute_upper_bound = max_duration * len(groups)
    for reviewer_id in reviewers:
        load = model.new_int_var(0, load_upper_bound, f"profile_load_{reviewer_id}")
        assigned = sum(
            variables[index]
            for index, candidate in enumerate(candidates)
            if reviewer_id in candidate.reviewer_ids
        )
        model.add(load == context.existing_semester_load.get(reviewer_id, 0) + assigned)
        loads.append(load)
        minute_load = model.new_int_var(0, minute_upper_bound, f"profile_minutes_{reviewer_id}")
        model.add(
            minute_load
            == sum(
                max(0, int((candidate.end_at - candidate.start_at).total_seconds() // 60))
                * variables[index]
                for index, candidate in enumerate(candidates)
                if reviewer_id in candidate.reviewer_ids
            )
        )
        minutes.append(minute_load)

    minimum_load = model.new_int_var(0, load_upper_bound, "profile_minimum_load")
    maximum_load = model.new_int_var(0, load_upper_bound, "profile_maximum_load")
    model.add_min_equality(minimum_load, loads)
    model.add_max_equality(maximum_load, loads)
    minimum_minutes = model.new_int_var(0, minute_upper_bound, "profile_minimum_minutes")
    maximum_minutes = model.new_int_var(0, minute_upper_bound, "profile_maximum_minutes")
    model.add_min_equality(minimum_minutes, minutes)
    model.add_max_equality(maximum_minutes, minutes)
    load_spread = maximum_load - minimum_load
    minute_spread = maximum_minutes - minimum_minutes
    compactness_expression, compactness_bound = _add_compactness_objective(
        model, variables, candidates, reviewers
    )
    return (
        -1000 * load_spread - minute_spread + compactness_expression,
        load_upper_bound * 1000 + minute_upper_bound + compactness_bound,
    )


def _add_early_finish_objective(
    model: cp_model.CpModel,
    variables: list[cp_model.IntVar],
    candidates: list[Candidate],
) -> tuple[cp_model.LinearExpr, int]:
    if not candidates:
        return 0, 0
    origin = min(candidate.start_at for candidate in candidates)
    end_offsets = [max(0, int((candidate.end_at - origin).total_seconds() // 60)) for candidate in candidates]
    start_offsets = [max(0, int((candidate.start_at - origin).total_seconds() // 60)) for candidate in candidates]
    latest_end = model.new_int_var(0, max(end_offsets), "profile_latest_end")
    for variable, end_offset in zip(variables, end_offsets):
        model.add(latest_end >= end_offset).only_enforce_if(variable)
    expression = -1000 * latest_end - sum(
        start_offsets[index] * variables[index] for index in range(len(candidates))
    )
    return expression, max(end_offsets) * 1000 + max(start_offsets) * len(candidates)


def _schedule_metrics(sessions: tuple[ScheduledSession, ...]) -> dict[str, Any]:
    by_reviewer_day: dict[tuple[int, str], list[ScheduledSession]] = defaultdict(list)
    loads: dict[int, int] = defaultdict(int)
    minute_loads: dict[int, int] = defaultdict(int)
    for session in sessions:
        duration = max(0, int((session.end_at - session.start_at).total_seconds() // 60))
        for reviewer_id in session.reviewer_ids:
            by_reviewer_day[(reviewer_id, session.day)].append(session)
            loads[reviewer_id] += 1
            minute_loads[reviewer_id] += duration

    block_count = 0
    idle_minutes = 0
    for reviewer_sessions in by_reviewer_day.values():
        ordered = sorted(reviewer_sessions, key=lambda session: (session.start_at, session.end_at, session.group_id))
        if not ordered:
            continue
        block_count += 1
        for previous, current in pairwise(ordered):
            gap = max(0, int((current.start_at - previous.end_at).total_seconds() // 60))
            idle_minutes += gap
            if gap > 0:
                block_count += 1

    latest_end = max((session.end_at for session in sessions), default=None)
    load_values = list(loads.values())
    minute_values = list(minute_loads.values())
    return {
        "reviewer_block_count": block_count,
        "reviewer_idle_minutes": idle_minutes,
        "reviewer_load_spread": max(load_values, default=0) - min(load_values, default=0),
        "reviewer_minute_spread": max(minute_values, default=0) - min(minute_values, default=0),
        "latest_end_at": latest_end.isoformat() if latest_end is not None else None,
        "scheduled_groups": len(sessions),
    }


def _candidate_soft_scores(candidate: object, context: RoundInput) -> dict[str, int]:
    scores = _empty_soft_scores()
    quota = context.h12_semester_quota
    if quota is not None:
        scores["S1"] = sum(
            max(0, quota - context.existing_semester_load.get(reviewer_id, 0))
            * {"LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(
                context.lecturer_load_preferences.get(reviewer_id, "MEDIUM"), 2
            )
            for reviewer_id in candidate.reviewer_ids
        )
    prior = context.prior_reviewer_ids.get(candidate.group_id, set())
    if context.round_type in {"REVIEW_2", "REVIEW_2_1"} and prior and set(candidate.reviewer_ids) == prior:
        scores["S2"] = 1
    if context.round_type in {"DEFENSE_1", "DEFENSE_1_2"}:
        scores["S3"] = len(set(candidate.reviewer_ids).intersection(prior))
    # S4-S7 are deliberately additive soft bonuses.  They never participate
    # in feasibility decisions, so H1-H13 semantics remain unchanged while
    # the target API exposes the complete objective vocabulary.
    scores["S4"] = 1 if candidate.part in {"AM", "MORNING"} else 0
    scores["S5"] = 1 if candidate.day else 0
    scores["S6"] = len(set(candidate.reviewer_ids).intersection(prior))
    supervisors = context.project_supervisors.get(context.group_project.get(candidate.group_id, -1), set())
    scores["S7"] = len(set(candidate.reviewer_ids) - set(supervisors))
    return scores


def _aggregate_soft_scores(
    score_maps: list[dict[str, int]],
    candidates: list[object],
    selected: list[object],
) -> dict[str, int]:
    selected_keys = {
        (candidate.group_id, candidate.timeslot_id, candidate.reviewer_ids)
        for candidate in selected
    }
    totals = _empty_soft_scores()
    for candidate, scores in zip(candidates, score_maps):
        key = (candidate.group_id, candidate.timeslot_id, candidate.reviewer_ids)
        if key in selected_keys:
            for rule, score in scores.items():
                totals[rule] += score
    return totals
