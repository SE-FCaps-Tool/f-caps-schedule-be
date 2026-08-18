from app.domain.errors import DomainError


def ensure_publishable(version_status: str, validation_valid: bool) -> bool:
    if version_status != "VALID":
        raise DomainError("VERSION_NOT_VALID", "Only a valid ScheduleVersion can be published.")
    if not validation_valid:
        raise DomainError("SCHEDULE_HAS_VIOLATIONS", "The schedule still contains hard violations.")
    return True


def require_change_reason(reason: str) -> str:
    normalized = reason.strip()
    if not normalized:
        raise DomainError("CHANGE_REASON_REQUIRED", "A reason is required for every schedule change.")
    return normalized


def ensure_reschedule_allowed(*, role: str, assigned: bool, is_leader: bool = False) -> bool:
    if role == "MANAGER":
        return True
    if role == "LECTURER" and assigned:
        return True
    if role == "STUDENT" and assigned and is_leader:
        return True
    raise DomainError("RESCHEDULE_FORBIDDEN", "Only an assigned Lecturer, group Leader or Manager may request a change.")
