import pytest

from app.domain.errors import DomainError
from app.domain.round_setup import can_enter_scheduling, validate_round_configuration


def test_round_configuration_uses_spec_reviewer_count_and_result_owner_rules():
    config = {
        "type": "REVIEW_3",
        "reviewer_count": 3,
        "result_owner_mode": True,
        "groups": [1],
        "timeslots": [1],
        "rooms": [1],
    }
    assert validate_round_configuration(config) is True
    with pytest.raises(DomainError, match="REVIEWER_COUNT_INVALID"):
        validate_round_configuration({**config, "type": "REVIEW_1", "reviewer_count": 3})
    with pytest.raises(DomainError, match="RESULT_OWNER_NOT_ALLOWED"):
        validate_round_configuration({**config, "type": "DEFENSE_1"})


def test_round_cannot_enter_scheduling_without_all_required_inputs():
    with pytest.raises(DomainError, match="ROUND_INPUTS_INCOMPLETE"):
        can_enter_scheduling(
            type="REVIEW_3",
            groups=[],
            timeslots=[1],
            rooms=[1],
            reviewer_count=3,
        )


@pytest.mark.parametrize(
    ("round_type", "reviewer_count"),
    [
        ("REVIEW_1_1", 2),
        ("REVIEW_2_1", 2),
        ("DEFENSE_1_1", 3),
        ("DEFENSE_1_2", 5),
        ("DEFENSE_2", 5),
    ],
)
def test_canonical_round_types_are_supported(round_type, reviewer_count):
    assert validate_round_configuration(
        {
            "type": round_type,
            "reviewer_count": reviewer_count,
            "result_owner_mode": round_type in {"DEFENSE_1_1", "DEFENSE_2"},
            "groups": [1],
            "timeslots": [1],
            "rooms": [1],
        }
    ) is True

