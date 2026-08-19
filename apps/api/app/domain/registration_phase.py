from datetime import datetime
from enum import StrEnum


class RegistrationPhase(StrEnum):
    INACTIVE = "INACTIVE"
    LECTURER = "LECTURER"
    GROUP = "GROUP"
    CLOSED = "CLOSED"


def resolve_registration_phase(
    *,
    round_status: str,
    registration_deadline: datetime | None,
    group_preference_deadline: datetime | None,
    now: datetime,
) -> RegistrationPhase:
    if round_status != "OPEN_REGISTRATION":
        return RegistrationPhase.INACTIVE
    if registration_deadline is None:
        return RegistrationPhase.INACTIVE
    if now <= registration_deadline:
        return RegistrationPhase.LECTURER
    if group_preference_deadline is not None and now <= group_preference_deadline:
        return RegistrationPhase.GROUP
    return RegistrationPhase.CLOSED
