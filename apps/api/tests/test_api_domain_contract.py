import pytest

from app.api_contract import ApiDataEnvelope, ApiErrorEnvelope, PaginationMeta
from app.domain.status_compat import (
    GroupTargetStatus,
    InvitationTargetStatus,
    MembershipTargetStatus,
    ProjectTargetStatus,
    SessionTargetStatus,
    group_from_legacy,
    group_to_legacy,
    invitation_from_legacy,
    membership_from_legacy,
    project_from_legacy,
    project_to_legacy,
)


@pytest.mark.parametrize(
    ("legacy", "expected"),
    [
        ("PENDING_D11", GroupTargetStatus.FORMED),
        ("ELIGIBLE_D12", GroupTargetStatus.FORMED),
        ("DROPPED", GroupTargetStatus.DISBANDED),
    ],
)
def test_group_status_mapping_derives_spec_vocabulary(legacy, expected):
    assert group_from_legacy(legacy) is expected
    assert group_to_legacy(expected) in {"PENDING_D11", "DROPPED"}


def test_assigned_group_mapping_uses_project_context():
    assert group_from_legacy("ELIGIBLE_D12", project_assigned=True) is GroupTargetStatus.ASSIGNED
    assert group_from_legacy("DROPPED", project_assigned=True) is GroupTargetStatus.DISBANDED
    assert group_to_legacy(GroupTargetStatus.ASSIGNED) == "PENDING_D11"


def test_project_mapping_derives_spec_vocabulary_from_group_assignment():
    assert project_from_legacy("ARCHIVED") is ProjectTargetStatus.CANCELLED
    assert project_from_legacy("ACTIVE", has_group=False) is ProjectTargetStatus.DRAFT
    assert project_from_legacy("ACTIVE", has_group=True) is ProjectTargetStatus.ACTIVE
    assert project_to_legacy(ProjectTargetStatus.DRAFT) == "ACTIVE"
    assert project_to_legacy(ProjectTargetStatus.CANCELLED) == "ARCHIVED"


def test_membership_and_invitation_mappings_cover_historical_and_target_values():
    assert membership_from_legacy("DROPPED") is MembershipTargetStatus.LEFT
    assert membership_from_legacy("ACTIVE") is MembershipTargetStatus.ACTIVE
    assert invitation_from_legacy("EXPIRED") is InvitationTargetStatus.EXPIRED
    assert invitation_from_legacy("WITHDRAWN") is InvitationTargetStatus.WITHDRAWN


def test_target_status_enums_include_session_lifecycle_values():
    assert SessionTargetStatus.PLANNED.value == "PLANNED"
    assert SessionTargetStatus.GROUP_ABSENT.value == "GROUP_ABSENT"


def test_typed_envelopes_serialize_nested_data_and_meta():
    response = ApiDataEnvelope[dict](
        data={"groupId": "42"},
        meta=PaginationMeta(page=1, page_size=20, total=1),
    )
    assert response.model_dump() == {
        "data": {"groupId": "42"},
        "meta": {"page": 1, "page_size": 20, "total": 1},
    }
    error = ApiErrorEnvelope(code="GROUP_NOT_FOUND", message="Group does not exist.")
    assert error.model_dump() == {
        "error": {"code": "GROUP_NOT_FOUND", "message": "Group does not exist.", "details": {}}
    }
