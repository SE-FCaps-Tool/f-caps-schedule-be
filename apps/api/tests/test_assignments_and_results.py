import pytest

from app.domain.audit import AuditLog
from app.domain.enums import AssignmentRole, DefenseType, SystemRole
from app.domain.errors import DomainError
from app.domain.results import correct_result, validate_result_owner_mode
from app.domain.waivers import grant_h11_waiver


def test_result_owner_is_required_only_for_defense_when_mode_is_enabled():
    assert validate_result_owner_mode(
        DefenseType.DEFENSE_2,
        enabled=True,
        assignments=[AssignmentRole.REVIEWER, AssignmentRole.RESULT_OWNER],
    ) is True
    with pytest.raises(DomainError, match="RESULT_OWNER_REQUIRED"):
        validate_result_owner_mode(DefenseType.DEFENSE_2, enabled=True, assignments=[])
    with pytest.raises(DomainError, match="RESULT_OWNER_MODE_DISABLED"):
        validate_result_owner_mode(
            DefenseType.DEFENSE_2,
            enabled=False,
            assignments=[AssignmentRole.RESULT_OWNER],
        )
    assert validate_result_owner_mode(
        DefenseType.DEFENSE_1,
        enabled=True,
        assignments=[],
    ) is True
    with pytest.raises(DomainError, match="RESULT_OWNER_NOT_ALLOWED"):
        validate_result_owner_mode(
            DefenseType.DEFENSE_1,
            enabled=True,
            assignments=[AssignmentRole.RESULT_OWNER],
        )


def test_review_never_has_result_owner():
    with pytest.raises(DomainError, match="REVIEW_NO_RESULT_OWNER"):
        validate_result_owner_mode(
            DefenseType.REVIEW,
            enabled=True,
            assignments=[AssignmentRole.RESULT_OWNER],
        )
    with pytest.raises(DomainError, match="REVIEW_NO_RESULT_OWNER"):
        validate_result_owner_mode(
            DefenseType.REVIEW_2,
            enabled=True,
            assignments=[AssignmentRole.RESULT_OWNER],
        )


def test_manager_correction_creates_audit_event_with_reason():
    audit = AuditLog()
    event = correct_result(
        actor_role=SystemRole.MANAGER,
        result_id="result-1",
        reason="attendance correction",
        before={"outcome": "PASS"},
        after={"outcome": "FAIL"},
        audit_log=audit,
    )
    assert event.action == "RESULT_CORRECTED"
    assert audit.events[0].reason == "attendance correction"


def test_h11_waiver_is_scoped_and_audited():
    audit = AuditLog()
    waiver = grant_h11_waiver(
        actor_role=SystemRole.MANAGER,
        round_id=3,
        group_id=7,
        reason="approved special case",
        audit_log=audit,
    )
    assert waiver.scope == "H11"
    assert audit.events[0].action == "H11_WAIVER_GRANTED"
