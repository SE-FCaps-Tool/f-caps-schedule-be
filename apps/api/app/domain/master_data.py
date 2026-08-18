from collections.abc import Sequence

from app.domain.errors import DomainError


def normalize_code(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise DomainError("DATA_REQUIRED", "A code is required.")
    return normalized


def validate_group_members(members: Sequence[dict[str, str]]) -> bool:
    if not 4 <= len(members) <= 5:
        raise DomainError("GROUP_SIZE_INVALID", "A new group must have 4 to 5 students.")
    codes = [normalize_code(member.get("student_code", "")) for member in members]
    if len(set(codes)) != len(codes):
        raise DomainError("MEMBERSHIP_DUPLICATE", "A student cannot appear twice in one group.")
    leaders = [member for member in members if member.get("role", "MEMBER").upper() == "LEADER"]
    if len(leaders) != 1:
        raise DomainError("LEADER_REQUIRED", "A group must have exactly one active Leader.")
    return True


def validate_project_supervisors(supervisors: Sequence[str]) -> bool:
    if not 1 <= len(supervisors) <= 2:
        raise DomainError("SUPERVISOR_COUNT_INVALID", "A project must have one or two Supervisors.")
    parsed: list[tuple[str, str]] = []
    for assignment in supervisors:
        parts = assignment.split(":", maxsplit=1)
        if len(parts) != 2:
            raise DomainError("SUPERVISOR_MAIN_INVALID", "Supervisor assignment must include MAIN or CO.")
        parsed.append((normalize_code(parts[0]), parts[1].strip().upper()))
    if len({code for code, _ in parsed}) != len(parsed):
        raise DomainError("SUPERVISOR_DUPLICATE", "A lecturer cannot be assigned twice to one project.")
    if sum(role == "MAIN" for _, role in parsed) != 1:
        raise DomainError("SUPERVISOR_MAIN_INVALID", "A project must have exactly one MAIN Supervisor.")
    if any(role not in {"MAIN", "CO"} for _, role in parsed):
        raise DomainError("SUPERVISOR_ROLE_INVALID", "Supervisor role must be MAIN or CO.")
    return True


def validate_conflict_declaration(*, lecturer_id: int, project_id: int, reason: str) -> bool:
    if lecturer_id <= 0 or project_id <= 0:
        raise DomainError("CONFLICT_RESOURCE_INVALID", "Lecturer and project are required.")
    if not reason.strip():
        raise DomainError("CONFLICT_REASON_REQUIRED", "A conflict declaration requires a reason.")
    return True
