from collections.abc import Sequence
from typing import Any

from app.domain.audit import AuditEvent, AuditLog
from app.domain.enums import AssignmentRole, DefenseType, SystemRole
from app.domain.errors import DomainError
from app.domain.policy import PolicyContext, authorize


def validate_result_owner_mode(
    defense: DefenseType,
    *,
    enabled: bool,
    assignments: Sequence[AssignmentRole],
) -> bool:
    owner_count = sum(assignment is AssignmentRole.RESULT_OWNER for assignment in assignments)
    if defense in {DefenseType.REVIEW, DefenseType.REVIEW_1, DefenseType.REVIEW_2} and owner_count:
        raise DomainError("REVIEW_NO_RESULT_OWNER", "Review sessions cannot have a Result Owner.")
    if defense is DefenseType.DEFENSE_1 and owner_count:
        raise DomainError("RESULT_OWNER_NOT_ALLOWED", "Defense 1 does not use a Result Owner.")
    if not enabled and owner_count:
        raise DomainError("RESULT_OWNER_MODE_DISABLED", "Result Owner mode is disabled for this round.")
    if enabled and defense in {DefenseType.REVIEW_3, DefenseType.DEFENSE_2} and owner_count != 1:
        raise DomainError("RESULT_OWNER_REQUIRED", "Defense sessions require exactly one Result Owner.")
    return True


def correct_result(
    *,
    actor_role: SystemRole,
    result_id: str,
    reason: str,
    before: dict[str, Any],
    after: dict[str, Any],
    audit_log: AuditLog,
) -> AuditEvent:
    authorize(PolicyContext(role=actor_role), "correct_result", reason=reason)
    return audit_log.append(
        actor_id=None,
        action="RESULT_CORRECTED",
        entity_type="session_result",
        entity_id=result_id,
        reason=reason,
        before=before,
        after=after,
    )
