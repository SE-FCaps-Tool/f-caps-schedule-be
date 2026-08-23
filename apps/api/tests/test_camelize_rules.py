import pytest

from app.api_contract import camelize


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            {"totals": {"OPEN_REGISTRATION": 5, "DRAFT": 2}},
            {"totals": {"OPEN_REGISTRATION": 5, "DRAFT": 2}},
        ),
        (
            {"soft_weights": {"S1": 3, "S9": 1}},
            {"softWeights": {"S1": 3, "S9": 1}},
        ),
        (
            {"attention": {"no_leader": 1, "under_four": 2}},
            {"attention": {"noLeader": 1, "underFour": 2}},
        ),
        (
            {"payload": {"remediation_id": 7}},
            {"payload": {"remediationId": 7}},
        ),
        (
            {"counts": {"group_members": 12}},
            {"counts": {"groupMembers": 12}},
        ),
        (
            {"byGroup": {"SE1701": 3, "GRP_02": 1}},
            {"byGroup": {"SE1701": 3, "GRP_02": 1}},
        ),
        (
            {"h12_sessions_per_day": 7},
            {"h12SessionsPerDay": 7},
        ),
        (
            {"round_type": "DEFENSE_1_2"},
            {"roundType": "DEFENSE_1_2"},
        ),
    ],
)
def test_camelize_converts_contract_keys_without_mutating_data_keys_or_values(
    source: dict[str, object], expected: dict[str, object]
) -> None:
    assert camelize(source) == expected
