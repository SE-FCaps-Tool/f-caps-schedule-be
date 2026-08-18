import pytest

from app.domain.enums import AssignmentRole, SystemRole
from app.domain.errors import AuthorizationError
from app.domain.policy import PolicyContext, authorize


@pytest.mark.parametrize("role", [SystemRole.ADMIN, SystemRole.MANAGER])
def test_admin_and_manager_can_manage_rounds(role):
    assert authorize(PolicyContext(role=role), "manage_round") is True


def test_lecturer_can_submit_availability_but_cannot_publish_schedule():
    context = PolicyContext(role=SystemRole.LECTURER)
    assert authorize(context, "submit_availability") is True
    with pytest.raises(AuthorizationError, match="AUTH_FORBIDDEN"):
        authorize(context, "publish_schedule")


def test_contextual_reviewer_can_enter_result_only_for_assigned_session():
    assigned = PolicyContext(
        role=SystemRole.LECTURER,
        assignment=AssignmentRole.REVIEWER,
        assigned_session=True,
    )
    unassigned = assigned.__class__(
        role=SystemRole.LECTURER,
        assignment=AssignmentRole.REVIEWER,
        assigned_session=False,
    )
    assert authorize(assigned, "enter_result") is True
    with pytest.raises(AuthorizationError, match="AUTH_ASSIGNMENT_REQUIRED"):
        authorize(unassigned, "enter_result")


def test_result_owner_is_contextual_not_a_system_role():
    owner = PolicyContext(
        role=SystemRole.LECTURER,
        assignment=AssignmentRole.RESULT_OWNER,
        assigned_session=True,
    )
    assert authorize(owner, "enter_result") is True
    assert authorize(owner, "correct_result") is False


def test_manager_correction_requires_reason_and_is_allowed():
    context = PolicyContext(role=SystemRole.MANAGER)
    assert authorize(context, "correct_result", reason="attendance correction") is True
    with pytest.raises(AuthorizationError, match="AUTH_REASON_REQUIRED"):
        authorize(context, "correct_result")


def test_student_cannot_manage_scheduler_resources():
    with pytest.raises(AuthorizationError, match="AUTH_FORBIDDEN"):
        authorize(PolicyContext(role=SystemRole.STUDENT), "manage_round")


def test_h11_waiver_requires_manager_scope_and_reason():
    manager = PolicyContext(role=SystemRole.MANAGER)
    assert authorize(manager, "grant_h11_waiver", scope="H11", reason="approved exception") is True
    with pytest.raises(AuthorizationError, match="AUTH_WAIVER_SCOPE"):
        authorize(manager, "grant_h11_waiver", scope="H12", reason="wrong rule")
    with pytest.raises(AuthorizationError, match="AUTH_REASON_REQUIRED"):
        authorize(manager, "grant_h11_waiver", scope="H11")

