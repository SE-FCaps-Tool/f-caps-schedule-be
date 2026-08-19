from collections import defaultdict
from datetime import datetime

from ortools.sat.python import cp_model

from app.domain.errors import DomainError
from app.scheduler.candidates import generate_candidates, reason_for_unscheduled
from app.scheduler.models import RoundInput, ScheduledSession, SolverResult
from app.scheduler.validator import validate_schedule


def _overlap(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return left_start < right_end and right_start < left_end


def solve_schedule(
    context: RoundInput,
    *,
    groups: list[int],
    timeslots: list[tuple[int, datetime, datetime, str, str]],
    rooms: list[int],
    reviewers: list[int],
    time_limit_seconds: float = 10,
    random_seed: int = 0,
) -> SolverResult:
    candidates = generate_candidates(
        context,
        groups=groups,
        timeslots=timeslots,
        rooms=rooms,
        reviewers=reviewers,
    )
    if not candidates:
        unscheduled = tuple(
            reason_for_unscheduled(
                group_id,
                context,
                reviewers=reviewers,
                timeslots=[timeslot[0] for timeslot in timeslots],
                rooms=rooms,
            )
            for group_id in sorted(groups)
        )
        return SolverResult("PARTIAL", (), unscheduled, _empty_soft_scores(), random_seed, 0)

    model = cp_model.CpModel()
    variables = [model.new_bool_var(f"candidate_{index}") for index in range(len(candidates))]
    candidate_soft_scores = [_candidate_soft_scores(candidate, context, rooms) for candidate in candidates]
    weighted_scores = [
        sum(context.soft_weights.get(rule, 0) * score for rule, score in scores.items())
        for scores in candidate_soft_scores
    ]
    by_group: dict[int, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        by_group[candidate.group_id].append(index)
    for indexes in by_group.values():
        model.add_at_most_one(variables[index] for index in indexes)

    _add_resource_overlap_constraints(model, variables, candidates, "room")
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
        if context.h12_semester_quota is not None
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

    primary_bonus = secondary_bound + balance_bound + 1
    model.maximize(
        sum((primary_bonus + weighted_scores[index]) * variables[index] for index in range(len(candidates)))
        + balance_expression
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.random_seed = random_seed
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    status_name = solver.status_name(status)
    selected = [candidate for index, candidate in enumerate(candidates) if solver.value(variables[index])]
    sessions = tuple(
        ScheduledSession(
            session_id=candidate.group_id,
            group_id=candidate.group_id,
            project_id=context.group_project[candidate.group_id],
            timeslot_id=candidate.timeslot_id,
            room_id=candidate.room_id,
            start_at=candidate.start_at,
            end_at=candidate.end_at,
            reviewer_ids=candidate.reviewer_ids,
            day=candidate.day,
            part=candidate.part,
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
            rooms=rooms,
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
        if resource == "room":
            key = candidate.room_id
        elif resource == "reviewer" and resource_id in candidate.reviewer_ids:
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


def _candidate_soft_scores(candidate: object, context: RoundInput, rooms: list[int]) -> dict[str, int]:
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
    if context.round_type == "REVIEW_2" and prior and set(candidate.reviewer_ids) == prior:
        scores["S2"] = 1
    if context.round_type == "DEFENSE_1_2":
        scores["S3"] = len(set(candidate.reviewer_ids).intersection(prior))
    if rooms and candidate.room_id == min(rooms):
        scores["S8"] = 1
    return scores


def _aggregate_soft_scores(
    score_maps: list[dict[str, int]],
    candidates: list[object],
    selected: list[object],
) -> dict[str, int]:
    selected_keys = {
        (candidate.group_id, candidate.timeslot_id, candidate.room_id, candidate.reviewer_ids)
        for candidate in selected
    }
    totals = _empty_soft_scores()
    for candidate, scores in zip(candidates, score_maps):
        key = (candidate.group_id, candidate.timeslot_id, candidate.room_id, candidate.reviewer_ids)
        if key in selected_keys:
            for rule, score in scores.items():
                totals[rule] += score
    return totals
