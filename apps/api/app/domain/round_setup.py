from collections.abc import Sequence

from app.domain.errors import DomainError

_REVIEW_TYPES = {"REVIEW_1", "REVIEW_2"}
_DEFENSE_TYPES = {"DEFENSE_1_1", "DEFENSE_1_2", "DEFENSE_2"}


def validate_round_configuration(config: dict[str, object]) -> bool:
    round_type = str(config.get("type", ""))
    expected_reviewers = 2 if round_type in _REVIEW_TYPES else 3
    if round_type not in _REVIEW_TYPES | _DEFENSE_TYPES:
        raise DomainError("ROUND_TYPE_INVALID", "Round type is not supported in Scheduler-only V1.")
    if config.get("reviewer_count") != expected_reviewers:
        raise DomainError("REVIEWER_COUNT_INVALID", f"{round_type} requires {expected_reviewers} Reviewers.")
    if config.get("result_owner_mode") and round_type not in {"DEFENSE_1_1", "DEFENSE_2"}:
        raise DomainError("RESULT_OWNER_NOT_ALLOWED", "Result Owner mode is only available for Defense 1.1 and 2.")
    for key in ("groups", "timeslots", "rooms"):
        if not config.get(key):
            raise DomainError("ROUND_INPUTS_INCOMPLETE", f"Round requires at least one {key}.")
    return True


def can_enter_scheduling(
    *,
    type: str,
    groups: Sequence[object],
    timeslots: Sequence[object],
    rooms: Sequence[object],
    reviewer_count: int,
) -> bool:
    validate_round_configuration(
        {
            "type": type,
            "reviewer_count": reviewer_count,
            "result_owner_mode": False,
            "groups": groups,
            "timeslots": timeslots,
            "rooms": rooms,
        }
    )
    return True

