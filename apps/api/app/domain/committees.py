"""Pure validation and role-labeling rules for the Committee catalog."""

from __future__ import annotations

from app.domain.errors import DomainError
from app.domain.master_data import normalize_code

MIN_MEMBERS = 1
MAX_MEMBERS = 15
REVIEWER_ONLY_MAX = 3


def label_role(role: str, position: int) -> str:
    if role == "CHAIR":
        return "Chủ tịch"
    if role == "SECRETARY":
        return "Thư ký"
    if role == "REVIEWER":
        return f"Reviewer {position}"
    return f"Thành viên {position - 2}"


def assign_roles(member_ids: list[int]) -> list[tuple[int, str, int]]:
    """Return (lecturer_id, role, sequence_number) for each member, in order."""

    count = len(member_ids)
    assignments: list[tuple[int, str, int]] = []
    if count <= REVIEWER_ONLY_MAX:
        for position, lecturer_id in enumerate(member_ids, start=1):
            assignments.append((lecturer_id, "REVIEWER", position))
        return assignments
    for position, lecturer_id in enumerate(member_ids, start=1):
        if position == 1:
            role = "CHAIR"
        elif position == 2:
            role = "SECRETARY"
        else:
            role = "MEMBER"
        assignments.append((lecturer_id, role, position))
    return assignments


def validate_round_committee_sizes(round_reviewer_count: int, committees: list[dict[str, object]]) -> None:
    """A Committee may only serve a Round whose reviewer count it can staff exactly."""

    mismatched = [
        str(committee["code"])
        for committee in committees
        if int(committee["member_count"]) != round_reviewer_count
    ]
    if mismatched:
        raise DomainError(
            "ROUND_COMMITTEE_SIZE_MISMATCH",
            f"Committee(s) {', '.join(mismatched)} do not have {round_reviewer_count} members.",
        )


def validate_group(code: str, member_ids: list[int]) -> str:
    """Validate a batch input group and return its normalized code."""

    if not code or not code.strip():
        raise DomainError("COMMITTEE_CODE_REQUIRED", "A committee code is required.")
    normalized = normalize_code(code)
    if len(normalized) > 32:
        raise DomainError("COMMITTEE_CODE_REQUIRED", "A committee code must be at most 32 characters.")
    if not MIN_MEMBERS <= len(member_ids) <= MAX_MEMBERS:
        raise DomainError(
            "COMMITTEE_MEMBER_COUNT_INVALID",
            f"A committee must have between {MIN_MEMBERS} and {MAX_MEMBERS} members.",
        )
    if len(set(member_ids)) != len(member_ids):
        raise DomainError("COMMITTEE_MEMBER_DUPLICATE", "A lecturer cannot appear twice in one committee.")
    return normalized
