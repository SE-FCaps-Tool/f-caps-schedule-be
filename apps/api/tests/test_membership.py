import pytest

from app.domain.errors import DomainError
from app.domain.membership import MembershipLedger


def test_membership_ledger_enforces_one_active_leader_and_preserves_dropout_history():
    ledger = MembershipLedger()
    ledger.add(group_id=1, student_id=10, role="LEADER")
    ledger.add(group_id=1, student_id=11, role="MEMBER")
    with pytest.raises(DomainError, match="MEMBERSHIP_LEADER_EXISTS"):
        ledger.add(group_id=1, student_id=12, role="LEADER")

    ledger.drop(group_id=1, student_id=11, reason="approved withdrawal")
    active = ledger.active_members(group_id=1)
    history = ledger.history(group_id=1, student_id=11)
    assert [member.student_id for member in active] == [10]
    assert history[0].status == "DROPPED"
    assert history[0].reason == "approved withdrawal"

