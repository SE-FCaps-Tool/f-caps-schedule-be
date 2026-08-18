import pytest

from app.domain.errors import DomainError
from app.domain.result_workflow import validate_remediation_verifier, validate_result_outcome


@pytest.mark.parametrize("outcome", ["PASS", "NEEDS_FIX", "FAIL"])
def test_review_accepts_only_scheduler_review_outcomes(outcome):
    assert validate_result_outcome("REVIEW_1", outcome) is True


@pytest.mark.parametrize("outcome", ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"])
def test_defense_1_1_accepts_four_levels(outcome):
    assert validate_result_outcome("DEFENSE_1_1", outcome) is True


def test_defense_1_2_is_completion_only_and_defense_2_is_binary():
    assert validate_result_outcome("DEFENSE_1_2", "COMPLETED") is True
    assert validate_result_outcome("DEFENSE_2", "PASS") is True
    with pytest.raises(DomainError, match="OUTCOME_NOT_ALLOWED"):
        validate_result_outcome("DEFENSE_1_2", "LEVEL_1")
    with pytest.raises(DomainError, match="OUTCOME_NOT_ALLOWED"):
        validate_result_outcome("DEFENSE_2", "NEEDS_FIX")


def test_remediation_verifier_must_be_a_session_reviewer():
    assert validate_remediation_verifier(7, {7, 8}) is True
    with pytest.raises(DomainError, match="VERIFIER_NOT_REVIEWER"):
        validate_remediation_verifier(9, {7, 8})
