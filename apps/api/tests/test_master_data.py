import pytest

from app.domain.errors import DomainError
from app.domain.master_data import (
    normalize_code,
    validate_conflict_declaration,
    validate_group_members,
    validate_project_supervisors,
)


def test_master_data_normalizes_codes_and_rejects_blank_values():
    assert normalize_code("  se-01  ") == "SE-01"
    with pytest.raises(DomainError, match="DATA_REQUIRED"):
        normalize_code("   ")


def test_group_requires_four_to_five_members_and_one_leader():
    members = [{"student_code": f"S{i}", "role": "LEADER" if i == 1 else "MEMBER"} for i in range(1, 5)]
    assert validate_group_members(members) is True
    with pytest.raises(DomainError, match="GROUP_SIZE_INVALID"):
        validate_group_members(members[:3])
    with pytest.raises(DomainError, match="LEADER_REQUIRED"):
        validate_group_members([{**member, "role": "MEMBER"} for member in members])
    with pytest.raises(DomainError, match="MEMBERSHIP_DUPLICATE"):
        validate_group_members(members + [{"student_code": "S1", "role": "MEMBER"}])


def test_project_requires_one_or_two_supervisors_and_exactly_one_main():
    assert validate_project_supervisors(["GV01:MAIN", "GV02:CO"]) is True
    with pytest.raises(DomainError, match="SUPERVISOR_COUNT_INVALID"):
        validate_project_supervisors([])
    with pytest.raises(DomainError, match="SUPERVISOR_MAIN_INVALID"):
        validate_project_supervisors(["GV01:CO"])
    with pytest.raises(DomainError, match="SUPERVISOR_MAIN_INVALID"):
        validate_project_supervisors(["GV01:MAIN", "GV02:MAIN"])


def test_conflict_declaration_requires_real_resources_and_reason():
    assert validate_conflict_declaration(lecturer_id=1, project_id=2, reason="prior collaboration") is True
    with pytest.raises(DomainError, match="CONFLICT_REASON_REQUIRED"):
        validate_conflict_declaration(lecturer_id=1, project_id=2, reason=" ")
