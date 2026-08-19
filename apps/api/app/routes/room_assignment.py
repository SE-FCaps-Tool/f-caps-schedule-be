"""Post-activation room assignment endpoints."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.response_models import (
    AvailableRoomResponse,
    RoomAssignmentResponse,
    RoomSuggestionApplyResponse,
    RoomSuggestionsResponse,
)
from app.services.room_assignment import (
    RoomAssignmentError,
    build_room_suggestions,
    lock_room_ids,
    validate_assignment_batch,
)
from app.services.semester_queries import ensure_round_semester_writable

router = APIRouter(prefix="/api/v1", tags=["room-assignment"])
# Structured failures: ROOM_NOT_FOUND, ROOM_INACTIVE, ROOM_TYPE_NOT_ALLOWED,
# ROOM_ASSIGNMENT_STATE_INVALID, ROOM_CONFLICT, and ROOM_SUGGESTION_STALE.
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class RoomAssignmentPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    room_id: int = Field(alias="roomId", gt=0)


class RoomAssignmentItem(BaseModel):
    session_id: int = Field(gt=0)
    room_id: int = Field(gt=0)


class RoomSuggestionPayload(BaseModel):
    assignments: list[RoomAssignmentItem] = Field(default_factory=list)


def _require(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail="Insufficient permission")


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text(
            "SELECT COALESCE((SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)), "
            "(SELECT MIN(id) FROM accounts))"
        ),
        {"role": user.role},
    ).scalar_one_or_none()


def _json(value: object) -> str:
    return json.dumps(value, default=str)


def _error(exc: RoomAssignmentError) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={"code": exc.code, "message": exc.message, **(exc.details or {})},
    )


def _round_or_404(db: Session, round_id: int) -> None:
    if db.execute(text("SELECT id FROM rounds WHERE id = :id"), {"id": round_id}).scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})


def _active_version_or_error(db: Session, round_id: int) -> int:
    version_id = db.execute(
        text("SELECT id FROM schedule_versions WHERE round_id = :round_id AND status = 'ACTIVE' ORDER BY id DESC LIMIT 1"),
        {"round_id": round_id},
    ).scalar_one_or_none()
    if version_id is None:
        raise _error(RoomAssignmentError("ROOM_ASSIGNMENT_STATE_INVALID", "The round has no current ACTIVE schedule version."))
    return int(version_id)


@router.get("/rounds/{round_id}/rooms/available", response_model=list[AvailableRoomResponse])
def list_available_rooms(
    round_id: int,
    db: Db,
    user: User,
    timeslot_id: int | None = Query(default=None, gt=0),
    room_type: Literal["NORMAL", "SEMINAR", "LAB"] | None = Query(default=None),
) -> list[dict[str, object]]:
    _require(user)
    _round_or_404(db, round_id)
    _active_version_or_error(db, round_id)
    params: dict[str, object] = {"round_id": round_id, "room_type": room_type}
    interval = ""
    if timeslot_id is not None:
        slot = db.execute(
            text(
                "SELECT ts.id, ts.start_at, ts.end_at FROM timeslots ts "
                "JOIN round_days rd ON rd.id = ts.round_day_id "
                "WHERE ts.id = :timeslot_id AND rd.round_id = :round_id"
            ),
            {"timeslot_id": timeslot_id, "round_id": round_id},
        ).mappings().one_or_none()
        if slot is None:
            raise HTTPException(status_code=404, detail={"code": "TIMESLOT_NOT_FOUND", "message": "Timeslot does not belong to this round."})
        params.update({"start_at": slot["start_at"], "end_at": slot["end_at"]})
        interval = " AND NOT EXISTS (SELECT 1 FROM sessions sx JOIN schedule_versions vx ON vx.id = sx.schedule_version_id WHERE sx.room_id = r.id AND vx.status IN ('ACTIVE','PUBLISHED') AND sx.start_at < :end_at AND sx.end_at > :start_at)"
    rows = db.execute(
        text(
            "SELECT r.id, r.code, r.name, r.capacity, r.active, r.room_type "
            "FROM rooms r WHERE r.active = TRUE "
            "AND EXISTS (SELECT 1 FROM round_room_types rrt WHERE rrt.round_id = :round_id AND rrt.room_type = r.room_type) "
            "AND (:room_type IS NULL OR r.room_type = CAST(:room_type AS room_type))" + interval + " ORDER BY r.code, r.id"
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


@router.put("/sessions/{session_id}/room", response_model=RoomAssignmentResponse)
def assign_session_room(
    session_id: int,
    payload: RoomAssignmentPayload,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user)
    try:
        with db.begin():
            session = db.execute(
                text(
                    "SELECT s.id, s.schedule_version_id, s.group_id, s.room_id, s.start_at, s.end_at, s.status, "
                    "sv.round_id, sv.status AS version_status FROM sessions s JOIN schedule_versions sv ON sv.id=s.schedule_version_id "
                    "WHERE s.id = :id"
                ),
                {"id": session_id},
            ).mappings().one_or_none()
            if session is None:
                raise RoomAssignmentError("SESSION_NOT_FOUND", "Session does not exist.", 404)
            ensure_round_semester_writable(db, int(session["round_id"]))
            db.execute(text("SELECT id FROM rounds WHERE id = :id FOR UPDATE"), {"id": session["round_id"]})
            db.execute(text("SELECT id FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": session["schedule_version_id"]})
            session = db.execute(
                text(
                    "SELECT s.id, s.schedule_version_id, s.group_id, s.room_id, s.start_at, s.end_at, s.status, "
                    "sv.round_id, sv.status AS version_status FROM sessions s JOIN schedule_versions sv ON sv.id=s.schedule_version_id "
                    "WHERE s.id = :id FOR UPDATE"
                ),
                {"id": session_id},
            ).mappings().one_or_none()
            if session is None:
                raise RoomAssignmentError("SESSION_NOT_FOUND", "Session does not exist.", 404)
            if str(session["version_status"]) != "ACTIVE" or str(session["status"]) != "PLANNED":
                raise RoomAssignmentError("ROOM_ASSIGNMENT_STATE_INVALID", "Only PLANNED sessions in the ACTIVE version may receive a room.")
            lock_room_ids(db, [payload.room_id])
            validated = validate_assignment_batch(
                db,
                int(session["round_id"]),
                [{"session_id": session_id, "room_id": payload.room_id}],
                active_version_id=int(session["schedule_version_id"]),
            )
            changed = session["room_id"] != payload.room_id
            if changed:
                db.execute(text("UPDATE sessions SET room_id = :room_id WHERE id = :id"), {"room_id": payload.room_id, "id": session_id})
                db.execute(
                    text(
                        "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                        "VALUES (:actor_id, 'ROOM_ASSIGNED', 'session', :entity_id, CAST(:after_json AS JSONB))"
                    ),
                    {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "after_json": _json({"room_id": payload.room_id})},
                )
        return {"session_id": session_id, "room_id": payload.room_id, "changed": changed, "start_at": validated[0]["start_at"], "end_at": validated[0]["end_at"]}
    except RoomAssignmentError as exc:
        raise _error(exc) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail={"code": "ROOM_CONFLICT", "message": "Room is already occupied during this session.", "room_id": payload.room_id}) from exc


@router.post("/rounds/{round_id}/rooms/suggest", response_model=RoomSuggestionsResponse)
def suggest_rooms(round_id: int, db: Db, user: User) -> dict[str, object]:
    _require(user)
    _round_or_404(db, round_id)
    _active_version_or_error(db, round_id)
    return {"suggestions": build_room_suggestions(db, round_id)}


@router.post("/rounds/{round_id}/rooms/apply-suggestions", response_model=RoomSuggestionApplyResponse)
def apply_room_suggestions(
    round_id: int,
    payload: RoomSuggestionPayload,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user)
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            db.execute(text("SELECT id FROM rounds WHERE id = :id FOR UPDATE"), {"id": round_id})
            version = db.execute(
                text("SELECT id FROM schedule_versions WHERE round_id = :round_id AND status = 'ACTIVE' ORDER BY id DESC LIMIT 1 FOR UPDATE"),
                {"round_id": round_id},
            ).scalar_one_or_none()
            if version is None:
                raise RoomAssignmentError("ROOM_ASSIGNMENT_STATE_INVALID", "The round has no current ACTIVE schedule version.")
            lock_room_ids(db, [item.room_id for item in payload.assignments])
            validated = validate_assignment_batch(
                db,
                round_id,
                [item.model_dump() for item in payload.assignments],
                active_version_id=int(version),
            )
            changed = 0
            unchanged = 0
            actor_id = _actor_id(db, user)
            for row in validated:
                if row["current_room_id"] == row["room_id"]:
                    unchanged += 1
                    continue
                db.execute(text("UPDATE sessions SET room_id = :room_id WHERE id = :id"), {"room_id": row["room_id"], "id": row["session_id"]})
                changed += 1
                db.execute(
                    text(
                        "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                        "VALUES (:actor_id, 'ROOM_ASSIGNED', 'session', :entity_id, CAST(:after_json AS JSONB))"
                    ),
                    {"actor_id": actor_id, "entity_id": str(row["session_id"]), "after_json": _json({"room_id": row["room_id"], "batch": True})},
                )
        return {"round_id": round_id, "changed_count": changed, "unchanged_count": unchanged, "assignments": [{"session_id": row["session_id"], "room_id": row["room_id"]} for row in validated]}
    except RoomAssignmentError as exc:
        raise _error(exc) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail={"code": "ROOM_CONFLICT", "message": "One or more rooms are already occupied."}) from exc
