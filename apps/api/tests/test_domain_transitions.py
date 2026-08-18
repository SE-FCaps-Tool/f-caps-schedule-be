import pytest

from app.domain.enums import DefenseType, GroupStatus, ResultOutcome, RoundStatus
from app.domain.errors import DomainError
from app.domain.transitions import transition_group, transition_round


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (RoundStatus.DRAFT, RoundStatus.OPEN_REGISTRATION),
        (RoundStatus.OPEN_REGISTRATION, RoundStatus.REGISTRATION_CLOSED),
        (RoundStatus.REGISTRATION_CLOSED, RoundStatus.SCHEDULING),
        (RoundStatus.SCHEDULING, RoundStatus.SCHEDULED),
        (RoundStatus.SCHEDULED, RoundStatus.PUBLISHED),
        (RoundStatus.PUBLISHED, RoundStatus.ONGOING),
        (RoundStatus.ONGOING, RoundStatus.COMPLETED),
        (RoundStatus.COMPLETED, RoundStatus.LOCKED),
        (RoundStatus.PUBLISHED, RoundStatus.POSTPONED),
        (RoundStatus.POSTPONED, RoundStatus.SCHEDULING),
        (RoundStatus.DRAFT, RoundStatus.CANCELLED),
        (RoundStatus.COMPLETED, RoundStatus.CANCELLED),
    ],
)
def test_round_transition_allows_specified_path(current, target):
    assert transition_round(current, target) is target


def test_round_cancelled_and_locked_are_terminal_without_privileged_action():
    with pytest.raises(DomainError, match="ROUND_TERMINAL"):
        transition_round(RoundStatus.CANCELLED, RoundStatus.DRAFT)
    with pytest.raises(DomainError, match="ROUND_LOCKED"):
        transition_round(RoundStatus.LOCKED, RoundStatus.ONGOING)


def test_round_rejects_skipping_required_lifecycle_state():
    with pytest.raises(DomainError, match="ROUND_TRANSITION_NOT_ALLOWED"):
        transition_round(RoundStatus.DRAFT, RoundStatus.PUBLISHED)


@pytest.mark.parametrize(
    ("defense", "outcome", "expected"),
    [
        (DefenseType.DEFENSE_1_1, ResultOutcome.LEVEL_1, GroupStatus.ELIGIBLE_D12),
        (DefenseType.DEFENSE_1_1, ResultOutcome.LEVEL_2, GroupStatus.D12_CONDITIONAL),
        (DefenseType.DEFENSE_1_1, ResultOutcome.LEVEL_3, GroupStatus.PENDING_D2),
        (DefenseType.DEFENSE_1_1, ResultOutcome.LEVEL_4, GroupStatus.FAILED),
            (DefenseType.DEFENSE_1_2, ResultOutcome.COMPLETED, GroupStatus.COMPLETED),
        (DefenseType.DEFENSE_2, ResultOutcome.PASS, GroupStatus.COMPLETED),
        (DefenseType.DEFENSE_2, ResultOutcome.FAIL, GroupStatus.FAILED),
    ],
)
def test_defense_result_transitions_group(defense, outcome, expected):
    current = {
        DefenseType.DEFENSE_1_1: GroupStatus.PENDING_D11,
        DefenseType.DEFENSE_1_2: GroupStatus.ELIGIBLE_D12,
        DefenseType.DEFENSE_2: GroupStatus.PENDING_D2,
    }[defense]
    assert transition_group(current, defense, outcome) is expected


def test_d12_remediation_can_reenter_eligible_d12_but_review_does_not_change_group():
    assert transition_group(
        GroupStatus.D12_CONDITIONAL, DefenseType.REMEDIATION, ResultOutcome.PASS
    ) is GroupStatus.ELIGIBLE_D12
    assert transition_group(
        GroupStatus.ELIGIBLE_D12, DefenseType.REVIEW_1, ResultOutcome.NEEDS_FIX
    ) is GroupStatus.ELIGIBLE_D12


def test_defense_1_2_accepts_completion_only_and_rejects_failure_outcome():
    assert transition_group(
        GroupStatus.ELIGIBLE_D12, DefenseType.DEFENSE_1_2, ResultOutcome.COMPLETED
    ) is GroupStatus.COMPLETED
    with pytest.raises(DomainError, match="GROUP_RESULT_NOT_ALLOWED"):
        transition_group(GroupStatus.ELIGIBLE_D12, DefenseType.DEFENSE_1_2, ResultOutcome.FAIL)


def test_invalid_group_result_has_stable_error_code():
    with pytest.raises(DomainError, match="GROUP_RESULT_NOT_ALLOWED"):
        transition_group(GroupStatus.COMPLETED, DefenseType.DEFENSE_2, ResultOutcome.PASS)
    with pytest.raises(DomainError, match="GROUP_RESULT_NOT_ALLOWED"):
        transition_group(GroupStatus.PENDING_D11, DefenseType.DEFENSE_1_1, ResultOutcome.PASS)
