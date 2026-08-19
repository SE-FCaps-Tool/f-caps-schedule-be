"""Shared post-activation room-assignment rules.

The route layer owns HTTP concerns; this module owns eligibility, locking,
conflict detection, and the deterministic suggestion algorithm so all room
mutation entry points use the same protocol.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.resource_locks import acquire_resource_locks


@dataclass(frozen=True)
class RoomAssignmentError(Exception):
    code: str
    message: str
    status_code: int = 409
    details: dict[str, object] | None = None

    def __str__(self) -> str:
        return self.message


def lock_room_ids(db: Session, room_ids: Iterable[int]) -> None:
    """Lock physical rooms in deterministic order for the current transaction."""

    # resource_locks executes pg_advisory_xact_lock(bigint) with the stable
    # ``room:<id>`` namespace.
    acquire_resource_locks(db, "room", sorted({int(room_id) for room_id in room_ids}))


def allowed_room(db: Session, round_id: int, room_id: int):
    """Return an active room allowed by a round's room-type policy, if any."""

    return db.execute(
        text(
            """
            SELECT r.id, r.code, r.name, r.capacity, r.active, r.room_type
            FROM rooms r
            WHERE r.id = :room_id
              AND r.active = TRUE
              AND EXISTS (
                  SELECT 1 FROM round_room_types rrt
                  WHERE rrt.round_id = :round_id AND rrt.room_type = r.room_type
              )
            """
        ),
        {"round_id": round_id, "room_id": room_id},
    ).mappings().one_or_none()


def find_room_conflict(
    db: Session,
    room_id: int,
    start_at: datetime,
    end_at: datetime,
    *,
    exclude_session_ids: Iterable[int] = (),
):
    """Find the first overlapping session in any live schedule version."""

    excluded = [int(session_id) for session_id in exclude_session_ids]
    return db.execute(
        text(
            """
            SELECT s.id AS session_id, sv.round_id, s.schedule_version_id,
                   s.start_at, s.end_at, r.type AS round_type,
                   sv.status AS version_status
            FROM sessions s
            JOIN schedule_versions sv ON sv.id = s.schedule_version_id
            JOIN rounds r ON r.id = sv.round_id
            WHERE s.room_id = :room_id
              AND sv.status IN ('ACTIVE', 'PUBLISHED')
              AND s.start_at < :end_at
              AND s.end_at > :start_at
              AND (cardinality(CAST(:excluded AS BIGINT[])) = 0 OR s.id <> ALL(CAST(:excluded AS BIGINT[])))
            ORDER BY s.start_at, s.id
            LIMIT 1
            """
        ),
        {
            "room_id": room_id,
            "start_at": start_at,
            "end_at": end_at,
            "excluded": excluded,
        },
    ).mappings().one_or_none()


def _overlaps(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return bool(left["start_at"] < right["end_at"] and right["start_at"] < left["end_at"])


def validate_assignment_batch(
    db: Session,
    round_id: int,
    assignments: Sequence[Mapping[str, int]],
    *,
    active_version_id: int | None = None,
) -> list[dict[str, object]]:
    """Validate every requested assignment before any caller performs UPDATEs.

    The return value contains the locked/validated session rows and is useful to
    callers that need timestamps for audit responses.  ``RoomAssignmentError``
    carries structured API-safe failure data.
    """

    if not assignments:
        # Empty batches are a safe no-op.
        return []
    normalized = [
        {"session_id": int(item["session_id"]), "room_id": int(item["room_id"])}
        for item in assignments
    ]
    if len({item["session_id"] for item in normalized}) != len(normalized):
        raise RoomAssignmentError("ROOM_SUGGESTION_STALE", "A session appears more than once in the batch.")

    version = db.execute(
        text(
            """
            SELECT sv.id, sv.round_id
            FROM schedule_versions sv
            WHERE sv.round_id = :round_id AND sv.status = 'ACTIVE'
            ORDER BY sv.id DESC LIMIT 1
            """
        ),
        {"round_id": round_id},
    ).mappings().one_or_none()
    if version is None or (active_version_id is not None and version["id"] != active_version_id):
        raise RoomAssignmentError("ROOM_ASSIGNMENT_STATE_INVALID", "The round has no current ACTIVE schedule version.")

    rows = db.execute(
        text(
            """
            SELECT s.id AS session_id, s.group_id, s.schedule_version_id,
                   s.room_id AS current_room_id, s.start_at, s.end_at,
                   s.status
            FROM sessions s
            WHERE s.schedule_version_id = :version_id
              AND s.id = ANY(CAST(:session_ids AS BIGINT[]))
            FOR UPDATE
            """
        ),
        {"version_id": version["id"], "session_ids": [item["session_id"] for item in normalized]},
    ).mappings().all()
    by_id = {int(row["session_id"]): row for row in rows}
    if len(by_id) != len(normalized):
        raise RoomAssignmentError("ROOM_SUGGESTION_STALE", "One or more sessions no longer belongs to this ACTIVE version.")

    candidate_rows: list[dict[str, object]] = []
    for item in normalized:
        row = by_id[item["session_id"]]
        if str(row["status"]) != "PLANNED":
            raise RoomAssignmentError(
                "ROOM_ASSIGNMENT_STATE_INVALID",
                "Only PLANNED sessions in the ACTIVE version may receive an initial room.",
            )
        room = allowed_room(db, round_id, item["room_id"])
        if room is None:
            exists = db.execute(text("SELECT id, active, room_type FROM rooms WHERE id = :id"), {"id": item["room_id"]}).mappings().one_or_none()
            if exists is None:
                raise RoomAssignmentError("ROOM_NOT_FOUND", "Room does not exist.", 404, {"room_id": item["room_id"]})
            if not exists["active"]:
                raise RoomAssignmentError("ROOM_INACTIVE", "Room is not active.", 422, {"room_id": item["room_id"]})
            raise RoomAssignmentError("ROOM_TYPE_NOT_ALLOWED", "Room type is not allowed for this round.", 422, {"room_id": item["room_id"]})
        candidate_rows.append({**dict(row), "room_id": item["room_id"]})

    for index, left in enumerate(candidate_rows):
        for right in candidate_rows[index + 1 :]:
            if left["room_id"] == right["room_id"] and _overlaps(left, right):
                raise RoomAssignmentError(
                    "ROOM_CONFLICT",
                    "Submitted room assignments overlap.",
                    409,
                    {"room_id": left["room_id"], "session_id": right["session_id"]},
                )
        conflict = find_room_conflict(
            db,
            int(left["room_id"]),
            left["start_at"],
            left["end_at"],
            exclude_session_ids=[int(left["session_id"])],
        )
        if conflict is not None:
            raise RoomAssignmentError(
                "ROOM_CONFLICT",
                "Room is already occupied during this session.",
                409,
                {"room_id": left["room_id"], **dict(conflict)},
            )
    return candidate_rows


def build_room_suggestions(db: Session, round_id: int) -> list[dict[str, object]]:
    """Build deterministic least-overlap suggestions for the current ACTIVE version."""

    sessions = db.execute(
        text(
            """
            SELECT s.id AS session_id, s.group_id, s.start_at, s.end_at,
                   s.room_id, sv.id AS schedule_version_id
            FROM sessions s
            JOIN schedule_versions sv ON sv.id = s.schedule_version_id
            WHERE sv.round_id = :round_id AND sv.status = 'ACTIVE'
              AND s.status = 'PLANNED'
            ORDER BY s.start_at, s.id
            """
        ),
        {"round_id": round_id},
    ).mappings().all()
    rooms = db.execute(
        text(
            """
            SELECT r.id, r.code, r.room_type
            FROM rooms r
            WHERE r.active = TRUE
              AND EXISTS (SELECT 1 FROM round_room_types rrt
                          WHERE rrt.round_id = :round_id AND rrt.room_type = r.room_type)
            ORDER BY r.code, r.id
            """
        ),
        {"round_id": round_id},
    ).mappings().all()
    live = db.execute(
        text(
            """
            SELECT s.id AS session_id, room_id, start_at, end_at
            FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id
            WHERE room_id IS NOT NULL AND sv.status IN ('ACTIVE', 'PUBLISHED')
            """
        )
    ).mappings().all()
    occupancy: dict[int, list[Mapping[str, object]]] = {int(room["id"]): [] for room in rooms}
    for row in live:
        if int(row["room_id"]) in occupancy:
            occupancy[int(row["room_id"])].append(row)
    suggestions: list[dict[str, object]] = []
    for session in sessions:
        choices = []
        for room in rooms:
            conflicts = [item for item in occupancy[int(room["id"])] if _overlaps(session, item)]
            choices.append(
                (
                    len(conflicts),
                    len(occupancy[int(room["id"])]),
                    str(room["code"]),
                    int(room["id"]),
                    room,
                )
            )
        if not choices:
            continue
        # Prefer conflict-free rooms, then the least-used room and stable code/id
        # tie-breakers. If every eligible room is occupied, least conflicts wins.
        conflict_free = [choice for choice in choices if choice[0] == 0]
        _, _, _, room_id, room = min(conflict_free or choices)
        suggestion = {**dict(session), "room_id": room_id, "room_code": room["code"], "room_type": room["room_type"]}
        suggestions.append(suggestion)
        occupancy[room_id].append(session)
    return suggestions


def validate_publish_room_readiness(db: Session, round_id: int, version_id: int) -> list[dict[str, object]]:
    """Require every live session to have an eligible room with no global conflict."""

    rows = db.execute(
        text(
            """
            SELECT s.id AS session_id, s.room_id, s.start_at, s.end_at,
                   r.active, r.room_type,
                   EXISTS (SELECT 1 FROM round_room_types rrt
                           WHERE rrt.round_id = :round_id AND rrt.room_type = r.room_type) AS allowed
            FROM sessions s LEFT JOIN rooms r ON r.id = s.room_id
            WHERE s.schedule_version_id = :version_id
            ORDER BY s.id
            FOR UPDATE OF s
            """
        ),
        {"round_id": round_id, "version_id": version_id},
    ).mappings().all()
    if any(row["room_id"] is None for row in rows):
        raise RoomAssignmentError("ROOM_INACTIVE", "Every session must have an active room before publishing.", 422)
    for row in rows:
        if not row["active"]:
            raise RoomAssignmentError("ROOM_INACTIVE", "A session is assigned to an inactive room.", 422, {"room_id": row["room_id"]})
        if not row["allowed"]:
            raise RoomAssignmentError("ROOM_TYPE_NOT_ALLOWED", "A session is assigned to a room type not allowed by the round.", 422, {"room_id": row["room_id"]})
    lock_room_ids(db, [int(row["room_id"]) for row in rows])
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if left["room_id"] == right["room_id"] and _overlaps(left, right):
                raise RoomAssignmentError("ROOM_CONFLICT", "Published sessions overlap in the same room.", 409, {"room_id": left["room_id"], "session_id": right["session_id"]})
        conflict = find_room_conflict(db, int(left["room_id"]), left["start_at"], left["end_at"], exclude_session_ids=[int(item["session_id"]) for item in rows])
        if conflict is not None:
            raise RoomAssignmentError("ROOM_CONFLICT", "A live schedule already occupies this room.", 409, {"room_id": left["room_id"], **dict(conflict)})
    return [dict(row) for row in rows]
