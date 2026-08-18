from collections.abc import Sequence

from app.domain.enums import AssignmentRole, SystemRole
from app.domain.errors import AuthorizationError, DomainError
from app.domain.policy import PolicyContext


def normalize_selection(*, all_slots: Sequence[int], selected: Sequence[int], subject: str) -> dict[int, str]:
    if subject not in {"LECTURER", "GROUP"}:
        raise DomainError("AVAILABILITY_SUBJECT_INVALID", "Availability subject is invalid.")
    selected_set = set(selected)
    if not selected_set.issubset(set(all_slots)):
        raise DomainError("AVAILABILITY_SLOT_INVALID", "Selection contains a slot outside the round.")
    fallback = "UNAVAILABLE" if subject == "LECTURER" else "AVAILABLE"
    return {slot: ("AVAILABLE" if slot in selected_set else fallback) for slot in all_slots}


def validate_availability_actor(
    context: PolicyContext,
    *,
    subject: str,
    same_resource: bool,
) -> bool:
    role = SystemRole(context.role)
    if role in {SystemRole.ADMIN, SystemRole.MANAGER}:
        return True
    if not same_resource:
        raise AuthorizationError("AUTH_RESOURCE_SCOPE", "Availability is outside the actor's scope.")
    if subject == "LECTURER" and role is SystemRole.LECTURER:
        return True
    if subject == "GROUP" and role is SystemRole.STUDENT:
        if context.assignment is not AssignmentRole.PROJECT_LEADER or not context.same_group:
            raise AuthorizationError("AUTH_ASSIGNMENT_REQUIRED", "Only the active Project Leader may edit group availability.")
        return True
    raise AuthorizationError("AUTH_FORBIDDEN", "The actor cannot edit this availability.")


def invitation_response(
    response: str,
    *,
    reason: str | None = None,
    deadline_passed: bool = False,
    actor_role: SystemRole | None = None,
) -> bool:
    response = response.upper()
    if response not in {"ACCEPTED", "DECLINED"}:
        raise DomainError("INVITATION_RESPONSE_INVALID", "Invitation response must be accepted or declined.")
    if response == "DECLINED" and not (reason or "").strip():
        raise DomainError("INVITATION_REASON_REQUIRED", "Declining an invitation requires a reason.")
    if deadline_passed and actor_role not in {SystemRole.ADMIN, SystemRole.MANAGER}:
        raise DomainError("INVITATION_DEADLINE_PASSED", "Only a Manager may respond after the deadline.")
    return True

