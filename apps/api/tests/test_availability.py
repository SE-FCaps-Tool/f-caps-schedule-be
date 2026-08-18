import pytest

from app.domain.availability import (
    invitation_response,
    normalize_selection,
    validate_availability_actor,
)
from app.domain.enums import AssignmentRole, SystemRole
from app.domain.errors import AuthorizationError, DomainError
from app.domain.policy import PolicyContext


def test_no_selection_fallback_differs_for_lecturer_and_group():
    assert normalize_selection(all_slots=[1, 2], selected=[], subject="LECTURER") == {
        1: "UNAVAILABLE",
        2: "UNAVAILABLE",
    }
    assert normalize_selection(all_slots=[1, 2], selected=[], subject="GROUP") == {
        1: "AVAILABLE",
        2: "AVAILABLE",
    }


def test_availability_is_scoped_to_lecturer_or_active_project_leader():
    assert validate_availability_actor(
        PolicyContext(role=SystemRole.LECTURER), subject="LECTURER", same_resource=True
    ) is True
    assert validate_availability_actor(
        PolicyContext(
            role=SystemRole.STUDENT,
            assignment=AssignmentRole.PROJECT_LEADER,
            same_group=True,
        ),
        subject="GROUP",
        same_resource=True,
    ) is True
    with pytest.raises(AuthorizationError, match="AUTH_RESOURCE_SCOPE"):
        validate_availability_actor(
            PolicyContext(role=SystemRole.STUDENT), subject="GROUP", same_resource=False
        )


def test_invitation_decline_requires_reason_and_deadline_override_is_manager_only():
    assert invitation_response("DECLINED", reason="unavailable") is True
    with pytest.raises(DomainError, match="INVITATION_REASON_REQUIRED"):
        invitation_response("DECLINED")
    with pytest.raises(DomainError, match="INVITATION_DEADLINE_PASSED"):
        invitation_response("ACCEPTED", deadline_passed=True, actor_role=SystemRole.LECTURER)
    assert invitation_response("ACCEPTED", deadline_passed=True, actor_role=SystemRole.MANAGER) is True
