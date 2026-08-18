from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.domain.errors import DomainError


@dataclass(frozen=True)
class AuditEvent:
    actor_id: int | None
    action: str
    entity_type: str
    entity_id: str
    reason: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AuditLog:
    """Small append-only domain port; the database adapter persists the same shape."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(
        self,
        *,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: str,
        reason: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            reason=reason,
            before=before,
            after=after,
        )
        self.events.append(event)
        return event

    def update(self, _event_id: str, _payload: dict[str, Any]) -> None:
        raise DomainError("AUDIT_APPEND_ONLY", "Audit events cannot be updated.")

    def delete(self, _event_id: str) -> None:
        raise DomainError("AUDIT_APPEND_ONLY", "Audit events cannot be deleted.")
