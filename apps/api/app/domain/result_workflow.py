from app.domain.errors import DomainError
from app.domain.round_types import (
    DEFENSE_1_1_TYPES,
    DEFENSE_1_2_TYPES,
    REVIEW_1_1_TYPES,
    REVIEW_2_1_TYPES,
)

_ALLOWED_OUTCOMES = {
    **{round_type: {"PASS", "NEEDS_FIX", "FAIL"} for round_type in REVIEW_1_1_TYPES | REVIEW_2_1_TYPES},
    **{round_type: {"LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"} for round_type in DEFENSE_1_1_TYPES},
    **{round_type: {"COMPLETED"} for round_type in DEFENSE_1_2_TYPES},
    "DEFENSE_2": {"PASS", "FAIL"},
}


def validate_result_outcome(round_type: str, outcome: str) -> bool:
    if outcome not in _ALLOWED_OUTCOMES.get(round_type, set()):
        raise DomainError("OUTCOME_NOT_ALLOWED", f"{outcome} is not valid for {round_type}.")
    return True


def validate_remediation_verifier(verifier_id: int, reviewer_ids: set[int]) -> bool:
    if verifier_id not in reviewer_ids:
        raise DomainError("VERIFIER_NOT_REVIEWER", "The Remediation Verifier must be a Reviewer of the source session.")
    return True
