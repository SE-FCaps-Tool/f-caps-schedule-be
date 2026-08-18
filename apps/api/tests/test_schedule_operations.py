import pytest

from app.domain.errors import DomainError
from app.domain.schedule_operations import (
    ensure_publishable,
    ensure_reschedule_allowed,
    require_change_reason,
)


def test_publish_requires_valid_version_and_validation():
    assert ensure_publishable("VALID", True) is True
    with pytest.raises(DomainError, match="VERSION_NOT_VALID"):
        ensure_publishable("DRAFT", True)
    with pytest.raises(DomainError, match="SCHEDULE_HAS_VIOLATIONS"):
        ensure_publishable("VALID", False)


def test_manual_and_post_publish_changes_require_a_reason():
    with pytest.raises(DomainError, match="CHANGE_REASON_REQUIRED"):
        require_change_reason("  ")
    assert require_change_reason("Emergency room replacement") == "Emergency room replacement"


def test_only_assigned_lecturer_or_group_leader_can_request_reschedule():
    assert ensure_reschedule_allowed(role="LECTURER", assigned=True) is True
    assert ensure_reschedule_allowed(role="STUDENT", assigned=True, is_leader=True) is True
    with pytest.raises(DomainError, match="RESCHEDULE_FORBIDDEN"):
        ensure_reschedule_allowed(role="STUDENT", assigned=True, is_leader=False)
    with pytest.raises(DomainError, match="RESCHEDULE_FORBIDDEN"):
        ensure_reschedule_allowed(role="LECTURER", assigned=False)
