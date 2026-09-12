from datetime import UTC, datetime, timedelta
from itertools import combinations
from math import comb

from app.domain.round_types import DEFENSE_1_2_TYPES
from app.scheduler.models import Candidate, RoundInput, UnscheduledReason
from app.scheduler.validator import _eligible, valid_h11_waiver

# A free Reviewer pool can contain many mathematically valid groups of reviewers.
# Materialising every combination makes a large round (for example C(26, 5)
# combinations for one group/slot) dominate the scheduler before CP-SAT starts.
# Keep a deterministic, diverse sample when the full pool is too large. Assigned
# Committees remain exact and are not subject to this cap.
FREE_POOL_REVIEWER_TUPLE_CAP = 40


def generate_candidates(
    context: RoundInput,
    *,
    groups: list[int],
    timeslots: list[tuple[object, ...]],
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
            if context.round_type in DEFENSE_1_2_TYPES and not valid_h11_waiver(context, group_id):
                continuity = set(context.prior_reviewer_ids.get(group_id, set()))
                continuity.update(context.remediation_verifier_ids.get(group_id, set()))
                available = [reviewer_id for reviewer_id in available if reviewer_id in continuity]
            for reviewer_ids in _reviewer_tuples(
                context,
                available,
                day=day,
                rotation_seed=group_id * 1_000_003 + timeslot_id,
            ):
                candidates.append(
                    Candidate(
                        group_id=group_id,
                        timeslot_id=timeslot_id,
                        start_at=start_at,
                        end_at=end_at,
                        day=day,
                        part=part,
                        reviewer_ids=reviewer_ids,
                    )
                )
    return candidates


def _council_config_reviewer_tuples(
    context: RoundInput,
    available: list[int],
    *,
    day: str = "",
    rotation_seed: int = 0,
) -> list[tuple[int, ...]] | None:
    config = context.council_config or {}
    chairs = config.get("chairs", [])
    secretaries = config.get("secretaries", [])
    if not chairs and not secretaries:
        return None

    reviewer_count = context.expected_reviewer_count
    avail_set = set(available)

    # 1. Determine eligible chairs
    chair_ids = [c["lecturer_id"] for c in chairs if "lecturer_id" in c]
    if chair_ids:
        valid_chairs = []
        for c in chairs:
            cid = c.get("lecturer_id")
            if cid in avail_set:
                daily = c.get("daily_quota")
                if daily is not None and len(daily) > 0:
                    if day and daily.get(day, 0) > 0:
                        valid_chairs.append(cid)
                else:
                    valid_chairs.append(cid)
    else:
        valid_chairs = list(available)

    if not valid_chairs:
        return []

    # 2. Determine eligible secretaries
    sec_ids = [s["lecturer_id"] for s in secretaries if "lecturer_id" in s]
    valid_secretaries = [sid for sid in sec_ids if sid in avail_set and sid not in chair_ids]

    tuples: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()

    tuples_per_chair = max(4, FREE_POOL_REVIEWER_TUPLE_CAP // len(valid_chairs))

    for chair_idx, cid in enumerate(valid_chairs):
        chair_tuples_count = 0
        remaining_for_sec = [r for r in available if r != cid and r not in chair_ids]
        sec_candidates = [s for s in valid_secretaries if s != cid]
        if not sec_candidates:
            sec_candidates = remaining_for_sec

        for sid_offset in range(len(sec_candidates)):
            sid = sec_candidates[(rotation_seed + chair_idx + sid_offset) % len(sec_candidates)]
            other_avail = [r for r in remaining_for_sec if r != sid]
            needed = max(reviewer_count - 2, 0)
            if needed == 0:
                t = (cid, sid)
                if t not in seen:
                    seen.add(t)
                    tuples.append(t)
                    chair_tuples_count += 1
                    if chair_tuples_count >= tuples_per_chair:
                        break
            else:
                total_other = len(other_avail)
                if total_other < needed:
                    continue
                member_base_offset = (rotation_seed + chair_idx * 7) % total_other
                for step in range(1, total_other + 1):
                    for member_offset in range(total_other):
                        offset = (member_base_offset + member_offset) % total_other
                        other_members = tuple(
                            sorted(
                                other_avail[(offset + step * pos) % total_other]
                                for pos in range(needed)
                            )
                        )
                        if len(set(other_members)) != needed:
                            continue
                        t = (cid, sid, *other_members)
                        if t not in seen:
                            seen.add(t)
                            tuples.append(t)
                            chair_tuples_count += 1
                            if chair_tuples_count >= tuples_per_chair:
                                break
                    if chair_tuples_count >= tuples_per_chair:
                        break
            if chair_tuples_count >= tuples_per_chair:
                break

    return tuples


def _reviewer_tuples(
    context: RoundInput,
    available: list[int],
    *,
    day: str = "",
    rotation_seed: int = 0,
) -> list[tuple[int, ...]]:
    """Reviewer sets allowed for one (group, timeslot) after the hard filters.

    A Round bound to Committees may only be staffed by a whole Committee, so a
    Committee losing any member here drops out entirely rather than being
    topped up from the free pool.
    """

    if not context.has_assigned_committees:
        council_tuples = _council_config_reviewer_tuples(
            context, available, day=day, rotation_seed=rotation_seed
        )
        if council_tuples is not None:
            return council_tuples

        reviewer_count = context.expected_reviewer_count
        total = comb(len(available), reviewer_count)
        if total <= FREE_POOL_REVIEWER_TUPLE_CAP:
            return list(combinations(available, reviewer_count))
        return _bounded_free_pool_tuples(
            available, reviewer_count, total, rotation_seed=rotation_seed
        )
    eligible = set(available)
    return [
        tuple(member_ids)
        for member_ids in context.committee_reviewer_sets
        if len(member_ids) == context.expected_reviewer_count and eligible.issuperset(member_ids)
    ]


def _bounded_free_pool_tuples(
    available: list[int], reviewer_count: int, total: int, *, rotation_seed: int = 0
) -> list[tuple[int, ...]]:
    """Return a deterministic and evenly rotated subset of free-pool tuples.

    Consecutive windows and stepped windows rotate every Reviewer through the
    tuple positions before falling back to lexicographic combinations. This
    preserves reviewer coverage while keeping the CP-SAT model bounded.
    """

    target = min(total, FREE_POOL_REVIEWER_TUPLE_CAP)
    selected: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    reviewer_total = len(available)

    for step in range(1, reviewer_total + 1):
        for offset_index in range(reviewer_total):
            offset = (rotation_seed + offset_index) % reviewer_total
            reviewer_ids = tuple(
                sorted(
                    available[(offset + step * position) % reviewer_total]
                    for position in range(reviewer_count)
                )
            )
            if len(set(reviewer_ids)) != reviewer_count or reviewer_ids in seen:
                continue
            seen.add(reviewer_ids)
            selected.append(reviewer_ids)
            if len(selected) >= target:
                return selected

    # This is normally unnecessary, but keeps the helper correct for unusual
    # pool sizes where the rotated patterns do not reach the target.
    for reviewer_ids in combinations(available, reviewer_count):
        if reviewer_ids in seen:
            continue
        selected.append(reviewer_ids)
        if len(selected) >= target:
            break
    return selected


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
    if context.round_type in DEFENSE_1_2_TYPES and not valid_h11_waiver(context, group_id):
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
    return UnscheduledReason(
        "NO_TIMESLOT",
        "No combination of hard constraints produced a candidate session.",
        "Add availability or timeslots, then run the scheduler again.",
    )
