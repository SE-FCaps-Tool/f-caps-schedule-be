from dataclasses import dataclass

from app.domain.audit import AuditLog
from app.domain.enums import SystemRole
from app.domain.policy import PolicyContext, authorize


@dataclass(frozen=True)
class H11Waiver:
    round_id: int
    group_id: int
    scope: str
    reason: str
    active: bool = True


def grant_h11_waiver(
    *,
    actor_role: SystemRole,
    round_id: int,
    group_id: int,
    reason: str,
    audit_log: AuditLog,
) -> H11Waiver:
    authorize(
        PolicyContext(role=actor_role),
        "grant_h11_waiver",
        scope="H11",
        reason=reason,
    )
    waiver = H11Waiver(round_id=round_id, group_id=group_id, scope="H11", reason=reason)
    audit_log.append(
        actor_id=None,
        action="H11_WAIVER_GRANTED",
        entity_type="h11_waiver",
        entity_id=f"{round_id}:{group_id}",
        reason=reason,
        after={"scope": waiver.scope, "active": waiver.active},
    )
    return waiver
