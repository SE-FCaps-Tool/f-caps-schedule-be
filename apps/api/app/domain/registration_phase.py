from datetime import datetime
from enum import StrEnum


class RegistrationPhase(StrEnum):
    INACTIVE = "INACTIVE"
    REGISTRATION = "REGISTRATION"
    CLOSED = "CLOSED"


def effective_registration_deadline(
    registration_deadline: datetime,
    group_preference_deadline: datetime | None,
) -> datetime:
    """Return the last configured deadline for the shared registration window."""

    return max(registration_deadline, group_preference_deadline) if group_preference_deadline is not None else registration_deadline


def resolve_registration_phase(
    *,
    round_status: str,
    registration_deadline: datetime | None,
    group_preference_deadline: datetime | None,
    lecturer_registration_closed_at: datetime | None = None,
    now: datetime,
) -> RegistrationPhase:
    """Resolve the shared registration window.

    ``lecturer_registration_closed_at`` remains an accepted compatibility
    parameter for callers that still load the legacy column; parallel mode
    intentionally does not use it to shorten the shared window.
    """

    if round_status != "OPEN_REGISTRATION":
        return RegistrationPhase.INACTIVE
    if registration_deadline is None:
        return RegistrationPhase.INACTIVE
    deadline = effective_registration_deadline(registration_deadline, group_preference_deadline)
    if now <= deadline:
        return RegistrationPhase.REGISTRATION
    return RegistrationPhase.CLOSED
