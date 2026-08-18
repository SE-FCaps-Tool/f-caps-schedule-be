from app.domain.errors import DomainError

_ALLOWED_OUTCOMES = {
    "REVIEW_1": {"PASS", "NEEDS_FIX", "FAIL"},
    "REVIEW_2": {"PASS", "NEEDS_FIX", "FAIL"},
    "DEFENSE_1_1": {"LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"},
    "DEFENSE_1_2": {"COMPLETED"},
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
