"""Compatibility mappings for status vocabularies during API migration."""

from __future__ import annotations

from enum import StrEnum


class GroupTargetStatus(StrEnum):
    FORMING = "FORMING"
    FORMED = "FORMED"
    ASSIGNED = "ASSIGNED"
    DISBANDED = "DISBANDED"


class ProjectTargetStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ELIGIBLE_D12 = "ELIGIBLE_D12"
    D12_CONDITIONAL = "D12_CONDITIONAL"
    PENDING_D2 = "PENDING_D2"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class InvitationTargetStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"


class SessionTargetStatus(StrEnum):
    PLANNED = "PLANNED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    POSTPONED = "POSTPONED"
    GROUP_ABSENT = "GROUP_ABSENT"
    CANCELLED = "CANCELLED"


_GROUP_FROM_LEGACY = {
    "PENDING_D11": GroupTargetStatus.FORMING,
    "ELIGIBLE_D12": GroupTargetStatus.FORMED,
    "D12_CONDITIONAL": GroupTargetStatus.FORMED,
    "PENDING_D2": GroupTargetStatus.FORMED,
    "COMPLETED": GroupTargetStatus.FORMED,
    "FAILED": GroupTargetStatus.FORMED,
    "DROPPED": GroupTargetStatus.DISBANDED,
}


def group_from_legacy(value: str, *, project_assigned: bool = False) -> GroupTargetStatus:
    target = _GROUP_FROM_LEGACY.get(str(value), GroupTargetStatus.FORMED)
    if project_assigned and target is GroupTargetStatus.FORMED:
        return GroupTargetStatus.ASSIGNED
    return target


def group_to_legacy(value: GroupTargetStatus | str) -> str:
    return {
        GroupTargetStatus.FORMING: "PENDING_D11",
        GroupTargetStatus.FORMED: "ELIGIBLE_D12",
        GroupTargetStatus.ASSIGNED: "ELIGIBLE_D12",
        GroupTargetStatus.DISBANDED: "DROPPED",
    }[GroupTargetStatus(value)]


def project_from_legacy(value: str) -> ProjectTargetStatus:
    normalized = str(value)
    if normalized == "ARCHIVED":
        return ProjectTargetStatus.CANCELLED
    try:
        return ProjectTargetStatus(normalized)
    except ValueError:
        return ProjectTargetStatus.ACTIVE


def invitation_from_legacy(value: str) -> InvitationTargetStatus:
    try:
        return InvitationTargetStatus(str(value))
    except ValueError:
        return InvitationTargetStatus.PENDING
