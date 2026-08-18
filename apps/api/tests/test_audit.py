import pytest

from app.domain.audit import AuditLog
from app.domain.errors import DomainError


def test_audit_log_is_append_only_and_keeps_before_after_snapshots():
    log = AuditLog()
    event = log.append(
        actor_id=7,
        action="RESULT_CORRECTED",
        entity_type="session_result",
        entity_id="result-1",
        reason="attendance correction",
        before={"outcome": "PASS"},
        after={"outcome": "FAIL"},
    )
    assert event.action == "RESULT_CORRECTED"
    assert event.before == {"outcome": "PASS"}
    assert event.after == {"outcome": "FAIL"}
    assert log.events == [event]


def test_audit_log_rejects_update_and_delete():
    log = AuditLog()
    with pytest.raises(DomainError, match="AUDIT_APPEND_ONLY"):
        log.update("event-1", {})
    with pytest.raises(DomainError, match="AUDIT_APPEND_ONLY"):
        log.delete("event-1")

