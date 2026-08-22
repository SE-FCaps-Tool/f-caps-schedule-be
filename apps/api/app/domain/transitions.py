from app.domain.enums import DefenseType, GroupStatus, ResultOutcome, RoundStatus
from app.domain.errors import DomainError

_ROUND_TRANSITIONS: dict[RoundStatus, frozenset[RoundStatus]] = {
    RoundStatus.DRAFT: frozenset({RoundStatus.OPEN_REGISTRATION, RoundStatus.CANCELLED}),
    RoundStatus.OPEN_REGISTRATION: frozenset(
        {RoundStatus.REGISTRATION_CLOSED, RoundStatus.CANCELLED}
    ),
    RoundStatus.REGISTRATION_CLOSED: frozenset({RoundStatus.SCHEDULING, RoundStatus.CANCELLED}),
    RoundStatus.SCHEDULING: frozenset({RoundStatus.SCHEDULED, RoundStatus.CANCELLED}),
    RoundStatus.SCHEDULED: frozenset({RoundStatus.PUBLISHED, RoundStatus.CANCELLED}),
    RoundStatus.PUBLISHED: frozenset(
        {RoundStatus.ONGOING, RoundStatus.POSTPONED, RoundStatus.CANCELLED}
    ),
    RoundStatus.ONGOING: frozenset(
        {RoundStatus.COMPLETED, RoundStatus.POSTPONED, RoundStatus.CANCELLED}
    ),
    RoundStatus.POSTPONED: frozenset({RoundStatus.SCHEDULING, RoundStatus.CANCELLED}),
    RoundStatus.COMPLETED: frozenset({RoundStatus.LOCKED, RoundStatus.CANCELLED}),
    RoundStatus.LOCKED: frozenset(),
    RoundStatus.CANCELLED: frozenset(),
}


def transition_round(current: RoundStatus, target: RoundStatus) -> RoundStatus:
    current = RoundStatus(current)
    target = RoundStatus(target)
    if current is RoundStatus.LOCKED:
        raise DomainError("ROUND_LOCKED", "A locked round cannot be changed.")
    if current is RoundStatus.CANCELLED:
        raise DomainError("ROUND_TERMINAL", "A cancelled round is terminal.")
    if target not in _ROUND_TRANSITIONS[current]:
        raise DomainError(
            "ROUND_TRANSITION_NOT_ALLOWED",
            f"Cannot transition a round from {current} to {target}.",
        )
    return target


def transition_group(
    current: GroupStatus,
    defense: DefenseType,
    outcome: ResultOutcome,
) -> GroupStatus:
    current = GroupStatus(current)
    defense = DefenseType(defense)
    outcome = ResultOutcome(outcome)

    if current is GroupStatus.DROPPED:
        raise DomainError("GROUP_TERMINAL", "A dropped group cannot receive a result.")
    if defense in {DefenseType.REVIEW, DefenseType.REVIEW_1, DefenseType.REVIEW_2}:
        return current
    if defense is DefenseType.REMEDIATION:
        if current is GroupStatus.D12_CONDITIONAL and outcome is ResultOutcome.PASS:
            return GroupStatus.ELIGIBLE_D12
        if current is GroupStatus.D12_CONDITIONAL and outcome is ResultOutcome.FAIL:
            return GroupStatus.FAILED
    elif defense is DefenseType.REVIEW_3:
        if current is GroupStatus.PENDING_D11:
            next_status = {
                ResultOutcome.LEVEL_1: GroupStatus.ELIGIBLE_D12,
                ResultOutcome.LEVEL_2: GroupStatus.D12_CONDITIONAL,
                ResultOutcome.LEVEL_3: GroupStatus.PENDING_D2,
                ResultOutcome.LEVEL_4: GroupStatus.FAILED,
            }.get(outcome)
            if next_status is not None:
                return next_status
    elif defense is DefenseType.DEFENSE_1:
        if current is GroupStatus.ELIGIBLE_D12 and outcome is ResultOutcome.COMPLETED:
            return GroupStatus.COMPLETED
    elif defense is DefenseType.DEFENSE_2:
        if current is GroupStatus.PENDING_D2 and outcome is ResultOutcome.PASS:
            return GroupStatus.COMPLETED
        if current is GroupStatus.PENDING_D2 and outcome is ResultOutcome.FAIL:
            return GroupStatus.FAILED

    raise DomainError(
        "GROUP_RESULT_NOT_ALLOWED",
        f"{defense} with {outcome} is invalid for group status {current}.",
    )
