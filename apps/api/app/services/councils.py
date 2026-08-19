"""Immutable Council construction and cross-schedule reviewer validation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.resource_locks import acquire_resource_locks


@dataclass(frozen=True)
class CouncilError(Exception):
    """Structured domain error raised by Council helpers."""

    code: str
    message: str
    status_code: int = 409
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


def lock_reviewer_ids(db: Session, reviewer_ids: Iterable[int]) -> None:
    """Acquire stable reviewer advisory locks in deterministic ID order."""

    # resource_locks issues pg_advisory_xact_lock(bigint) using the shared
    # ``reviewer:<id>`` namespace; activation and controlled changes therefore
    # serialize on the same lock identity.
    acquire_resource_locks(db, "reviewer", sorted({int(value) for value in reviewer_ids}))


def _member_values(member: Mapping[str, Any] | Sequence[Any]) -> tuple[int, str, bool, str]:
    if isinstance(member, Mapping):
        lecturer_id = int(member["lecturer_id"])
        assignment = str(member.get("assignment", "REVIEWER"))
        is_owner = bool(member.get("is_result_owner", False))
        snapshot_name = str(member.get("snapshot_name") or lecturer_id)
    else:
        values = list(member)
        if len(values) < 1:
            raise CouncilError("COUNCIL_MEMBER_INVALID", "A Council member requires a lecturer ID.", 422)
        lecturer_id = int(values[0])
        assignment = str(values[1]) if len(values) > 1 else "REVIEWER"
        is_owner = bool(values[2]) if len(values) > 2 else False
        snapshot_name = str(values[3]) if len(values) > 3 and values[3] else str(lecturer_id)
    if not snapshot_name or len(snapshot_name) > 160:
        raise CouncilError("COUNCIL_MEMBER_INVALID", "snapshot_name must be 1-160 characters.", 422)
    return lecturer_id, assignment, is_owner, snapshot_name


def create_council(
    db: Session,
    round_id: int,
    members: Iterable[Mapping[str, Any] | Sequence[Any]],
    *,
    created_by: int | None = None,
    reason: str | None = None,
    supersedes_council_id: int | None = None,
) -> int:
    """Build, seal, and return a Council ID in the caller's transaction.

    The construction order is intentionally observable in the SQL: member
    rows are inserted while ``sealed_at`` is NULL, then the one permitted
    Council update seals the complete set.  Callers can attach the returned
    Council to a Session only after this function returns.
    """

    normalized = [_member_values(member) for member in members]
    if not normalized:
        raise CouncilError("COUNCIL_MEMBER_INVALID", "A Council must contain at least one member.", 422)
    if len({item[0] for item in normalized}) != len(normalized):
        raise CouncilError("COUNCIL_MEMBER_INVALID", "A lecturer may appear only once in a Council.", 422)
    council_id = db.execute(
        text(
            """
            INSERT INTO councils(round_id, supersedes_council_id, created_by, reason)
            VALUES (:round_id, :supersedes_council_id, :created_by, :reason)
            RETURNING id
            """
        ),
        {
            "round_id": int(round_id),
            "supersedes_council_id": supersedes_council_id,
            "created_by": created_by,
            "reason": reason,
        },
    ).scalar_one()
    for lecturer_id, assignment, is_owner, snapshot_name in normalized:
        db.execute(
            text(
                """
                INSERT INTO council_members(council_id, lecturer_id, assignment, is_result_owner, snapshot_name)
                VALUES (:council_id, :lecturer_id, CAST(:assignment AS assignment_role), :is_owner, :snapshot_name)
                """
            ),
            {
                "council_id": council_id,
                "lecturer_id": lecturer_id,
                "assignment": assignment,
                "is_owner": is_owner,
                "snapshot_name": snapshot_name,
            },
        )
    db.execute(text("UPDATE councils SET sealed_at = now() WHERE id = :id"), {"id": council_id})
    return int(council_id)


def load_council_members(db: Session, council_id: int) -> list[dict[str, Any]]:
    """Load a stable, ordered Council member snapshot."""

    rows = db.execute(
        text(
            """
            SELECT cm.council_id, cm.lecturer_id, cm.assignment,
                   cm.is_result_owner, cm.snapshot_name
            FROM council_members cm
            WHERE cm.council_id = :council_id
            ORDER BY cm.lecturer_id
            """
        ),
        {"council_id": int(council_id)},
    ).mappings().all()
    return [dict(row) for row in rows]


def find_reviewer_conflicts(
    db: Session,
    reviewer_ids: Iterable[int],
    start_at: datetime,
    end_at: datetime,
    *,
    exclude_session_ids: Iterable[int] = (),
) -> list[dict[str, Any]]:
    """Find overlapping reviewer assignments in every ACTIVE/PUBLISHED round."""

    reviewers = sorted({int(value) for value in reviewer_ids})
    excluded = sorted({int(value) for value in exclude_session_ids})
    if not reviewers:
        return []
    rows = db.execute(
        text(
            """
            SELECT s.id AS session_id, s.schedule_version_id, sv.round_id,
                   s.start_at, s.end_at, cm.lecturer_id,
                   cm.assignment, cm.is_result_owner, sv.status AS version_status
            FROM sessions s
            JOIN schedule_versions sv ON sv.id = s.schedule_version_id
            JOIN council_members cm ON cm.council_id = s.council_id
            WHERE sv.status IN ('ACTIVE', 'PUBLISHED')
              AND cm.lecturer_id = ANY(CAST(:reviewer_ids AS BIGINT[]))
              AND s.start_at < :end_at
              AND s.end_at > :start_at
              AND (cardinality(CAST(:excluded AS BIGINT[])) = 0
                   OR s.id <> ALL(CAST(:excluded AS BIGINT[])))
            ORDER BY cm.lecturer_id, s.start_at, s.id
            """
        ),
        {
            "reviewer_ids": reviewers,
            "excluded": excluded,
            "start_at": start_at,
            "end_at": end_at,
        },
    ).mappings().all()
    return [dict(row) for row in rows]


def validate_council_change(
    db: Session,
    session_id: int,
    round_id: int,
    reviewer_ids: Iterable[int],
    start_at: datetime,
    end_at: datetime,
    *,
    exclude_session_ids: Iterable[int] = (),
) -> list[dict[str, Any]]:
    """Lock reviewers and reject a proposed assignment with live overlaps."""

    normalized_ids = sorted({int(value) for value in reviewer_ids})
    lock_reviewer_ids(db, normalized_ids)
    conflicts = find_reviewer_conflicts(
        db,
        normalized_ids,
        start_at,
        end_at,
        exclude_session_ids=set(exclude_session_ids) | {int(session_id)},
    )
    if conflicts:
        raise CouncilError(
            "REVIEWER_OVERLAP",
            "A reviewer already has an overlapping live session.",
            409,
            {"session_id": int(session_id), "round_id": int(round_id), "conflicts": conflicts},
        )
    return conflicts
