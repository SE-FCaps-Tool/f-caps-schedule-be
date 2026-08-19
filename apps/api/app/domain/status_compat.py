"""Compatibility mappings for status vocabularies during API migration.

The DB's group/project/membership status enums encode an assessment-pipeline
lifecycle (PENDING_D11 -> ELIGIBLE_D12 -> ... -> COMPLETED/FAILED, DROPPED)
that is orthogonal to the target API spec's coarser formation/assignment
lifecycle (FORMED/ASSIGNED/DISBANDED, DRAFT/ACTIVE/CANCELLED, ACTIVE/LEFT).
Rather than migrating the schema, target statuses are derived from existing
signals (group.project_id presence, membership.status) with no new columns.
"""

from __future__ import annotations

from enum import StrEnum


class GroupTargetStatus(StrEnum):
    FORMED = "FORMED"
    ASSIGNED = "ASSIGNED"
    DISBANDED = "DISBANDED"


class ProjectTargetStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class InvitationTargetStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"


class MembershipTargetStatus(StrEnum):
    ACTIVE = "ACTIVE"
    LEFT = "LEFT"


class SessionTargetStatus(StrEnum):
    PLANNED = "PLANNED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    POSTPONED = "POSTPONED"
    GROUP_ABSENT = "GROUP_ABSENT"
    CANCELLED = "CANCELLED"


def group_from_legacy(value: str, *, project_assigned: bool = False) -> GroupTargetStatus:
    if str(value) == "DROPPED":
        return GroupTargetStatus.DISBANDED
    return GroupTargetStatus.ASSIGNED if project_assigned else GroupTargetStatus.FORMED


def group_to_legacy(value: GroupTargetStatus | str) -> str:
    return {
        GroupTargetStatus.FORMED: "PENDING_D11",
        GroupTargetStatus.ASSIGNED: "PENDING_D11",
        GroupTargetStatus.DISBANDED: "DROPPED",
    }[GroupTargetStatus(value)]


def project_from_legacy(value: str, *, has_group: bool = False) -> ProjectTargetStatus:
    if str(value) == "ARCHIVED":
        return ProjectTargetStatus.CANCELLED
    return ProjectTargetStatus.ACTIVE if has_group else ProjectTargetStatus.DRAFT


def project_to_legacy(value: ProjectTargetStatus | str) -> str:
    return {
        ProjectTargetStatus.DRAFT: "ACTIVE",
        ProjectTargetStatus.ACTIVE: "ACTIVE",
        ProjectTargetStatus.CANCELLED: "ARCHIVED",
    }[ProjectTargetStatus(value)]


def membership_from_legacy(value: str) -> MembershipTargetStatus:
    return MembershipTargetStatus.LEFT if str(value) == "DROPPED" else MembershipTargetStatus.ACTIVE


def invitation_from_legacy(value: str) -> InvitationTargetStatus:
    try:
        return InvitationTargetStatus(str(value))
    except ValueError:
        return InvitationTargetStatus.PENDING
