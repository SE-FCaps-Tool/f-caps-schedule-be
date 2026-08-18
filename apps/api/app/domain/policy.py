from dataclasses import dataclass

from app.domain.enums import AssignmentRole, SystemRole
from app.domain.errors import AuthorizationError


@dataclass(frozen=True)
class PolicyContext:
    role: SystemRole
    assignment: AssignmentRole | None = None
    assigned_session: bool = False
    same_group: bool = False


def _deny(code: str, message: str) -> None:
    raise AuthorizationError(code, message)


def authorize(context: PolicyContext, action: str, **kwargs: str) -> bool:
    role = SystemRole(context.role)
    if action in {"manage_accounts", "manage_master_data"}:
        allowed = role is SystemRole.ADMIN
    elif action in {"manage_round", "run_scheduler", "publish_schedule"}:
        allowed = role in {SystemRole.ADMIN, SystemRole.MANAGER}
    elif action == "submit_availability":
        allowed = role in {SystemRole.ADMIN, SystemRole.MANAGER, SystemRole.LECTURER}
    elif action == "view_group":
        allowed = role in {
            SystemRole.ADMIN,
            SystemRole.MANAGER,
            SystemRole.LECTURER,
            SystemRole.STUDENT,
        }
    elif action == "enter_result":
        if role is not SystemRole.LECTURER:
            allowed = False
        elif context.assignment not in {
            AssignmentRole.REVIEWER,
            AssignmentRole.RESULT_OWNER,
        }:
            _deny("AUTH_ASSIGNMENT_REQUIRED", "Only an assigned reviewer or result owner may enter a result.")
        elif not context.assigned_session:
            _deny("AUTH_ASSIGNMENT_REQUIRED", "The lecturer is not assigned to this session.")
        else:
            allowed = True
    elif action == "correct_result":
        if role not in {SystemRole.ADMIN, SystemRole.MANAGER}:
            return False
        if not kwargs.get("reason", "").strip():
            _deny("AUTH_REASON_REQUIRED", "A correction reason is required.")
        allowed = True
    elif action == "grant_h11_waiver":
        if role not in {SystemRole.ADMIN, SystemRole.MANAGER}:
            _deny("AUTH_FORBIDDEN", "Only Admin or Manager may grant an H11 waiver.")
        if kwargs.get("scope") != "H11":
            _deny("AUTH_WAIVER_SCOPE", "Waivers are supported only for H11.")
        if not kwargs.get("reason", "").strip():
            _deny("AUTH_REASON_REQUIRED", "An H11 waiver reason is required.")
        allowed = True
    else:
        _deny("AUTH_FORBIDDEN", f"Action {action!r} is not available to this role.")

    if not allowed:
        _deny("AUTH_FORBIDDEN", f"Role {role} cannot perform {action}.")
    return True

