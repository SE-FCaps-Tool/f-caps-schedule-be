import pytest

from app.domain.status_compat import (
    GroupTargetStatus,
    InvitationTargetStatus,
    ProjectTargetStatus,
    SessionTargetStatus,
    group_from_legacy,
    group_to_legacy,
    invitation_from_legacy,
    project_from_legacy,
)
from app.response_models import ApiDataEnvelope, ApiErrorEnvelope, PaginationMeta


@pytest.mark.parametrize(
    ("legacy", "expected"),
    [
        ("PENDING_D11", GroupTargetStatus.FORMING),
        ("ELIGIBLE_D12", GroupTargetStatus.FORMED),
        ("DROPPED", GroupTargetStatus.DISBANDED),
    ],
)
def test_group_status_mapping_preserves_legacy_values(legacy, expected):
    assert group_from_legacy(legacy) is expected
    assert group_to_legacy(expected) in {"PENDING_D11", "ELIGIBLE_D12", "DROPPED"}


def test_assigned_group_mapping_uses_project_context():
    assert group_from_legacy("ELIGIBLE_D12", project_assigned=True) is GroupTargetStatus.ASSIGNED
    assert group_to_legacy(GroupTargetStatus.ASSIGNED) == "ELIGIBLE_D12"


def test_project_and_invitation_mappings_cover_historical_and_target_values():
    assert project_from_legacy("ARCHIVED") is ProjectTargetStatus.CANCELLED
    assert project_from_legacy("DRAFT") is ProjectTargetStatus.DRAFT
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
