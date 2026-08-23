"""Target room CRUD and publication readiness routes."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.room_assignment import (
    RoomAssignmentPayload,
    RoomSuggestionPayload,
    apply_room_suggestions,
    assign_session_room,
    list_available_rooms,
    suggest_rooms,
)
from app.routes.schedule_operations import publish_schedule
from app.services.room_assignment import RoomAssignmentError, validate_publish_room_readiness

router = APIRouter(prefix="/api/v1", tags=["target-rooms-publish"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class RoomUpdateTarget(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    capacity: int | None = Field(default=None, gt=0, le=500)
    active: bool | None = None
    room_type: Literal["NORMAL", "SEMINAR", "LAB"] | None = Field(default=None, alias="roomType")


class PublishTargetPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    version_id: int = Field(alias="versionId", gt=0)


@router.get("/rounds/{roundId}/rooms/available")
def target_available_rooms(
    round_id: Annotated[int, Path(alias="roundId")],
    db: Db,
    user: User,
    timeslot_id: int | None = Query(default=None, alias="timeslotId", gt=0),
    room_type: Literal["NORMAL", "SEMINAR", "LAB"] | None = Query(default=None, alias="type"),
) -> dict[str, Any]:
    rows = list_available_rooms(round_id, db, user, timeslot_id=timeslot_id, room_type=room_type)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.put("/sessions/{sessionId}/room")
def target_assign_room(session_id: Annotated[int, Path(alias="sessionId")], payload: RoomAssignmentPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(assign_session_room(session_id, payload, db, user))


@router.post("/rounds/{roundId}/rooms/suggest")
def target_suggest_rooms(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    return success_payload(suggest_rooms(round_id, db, user))


@router.post("/rounds/{roundId}/rooms/apply-suggestions")
def target_apply_room_suggestions(round_id: Annotated[int, Path(alias="roundId")], payload: RoomSuggestionPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(apply_room_suggestions(round_id, payload, db, user))


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


@router.patch("/rooms/{roomId}")
def update_room(room_id: Annotated[int, Path(alias="roomId")], payload: RoomUpdateTarget, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    current = db.execute(text("SELECT id, code, name, capacity, active, room_type::text AS room_type FROM rooms WHERE id = :id"), {"id": room_id}).mappings().one_or_none()
    db.rollback()
    if current is None:
        raise HTTPException(status_code=404, detail={"code": "ROOM_NOT_FOUND", "message": "Room does not exist."})
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return success_payload(dict(current))
    params: dict[str, Any] = {"id": room_id, **changes}
    assignments: list[str] = []
    for key in ("code", "name", "capacity", "active"):
        if key in changes:
            assignments.append(f"{key} = :{key}")
    if "room_type" in changes:
        assignments.append("room_type = CAST(:room_type AS room_type)")
    try:
        with db.begin():
            row = db.execute(text(f"UPDATE rooms SET {', '.join(assignments)} WHERE id = :id RETURNING id, code, name, capacity, active, room_type::text AS room_type"), params).mappings().one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail={"code": "ROOM_NOT_FOUND", "message": "Room does not exist."})
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'ROOM_UPDATED', 'room', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": user.account_id, "entity_id": str(room_id), "after_json": json.dumps(dict(row), default=str)})
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail={"code": "ROOM_DUPLICATE", "message": "Room code already exists."}) from exc
    return success_payload(dict(row))


@router.get("/rounds/{roundId}/publish-readiness")
def publish_readiness(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    version = db.execute(text("SELECT id, status::text AS status FROM schedule_versions WHERE round_id = :round_id AND status = 'ACTIVE' ORDER BY id DESC LIMIT 1"), {"round_id": round_id}).mappings().one_or_none()
    db.rollback()
    if version is None:
        return success_payload({"ready": False, "versionId": None, "blockers": [{"code": "VERSION_NOT_ACTIVE", "message": "Activate a schedule version before publishing."}]})
    try:
        validate_publish_room_readiness(db, round_id, int(version["id"]))
        blockers: list[dict[str, Any]] = []
    except RoomAssignmentError as exc:
        blockers = [{"code": exc.code, "message": str(exc), **(exc.details or {})}]
    finally:
        db.rollback()
    return success_payload({"ready": not blockers, "versionId": int(version["id"]), "blockers": blockers})


@router.post("/rounds/{roundId}/actions/publish")
def publish_target_schedule(round_id: Annotated[int, Path(alias="roundId")], payload: PublishTargetPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(publish_schedule(round_id, payload.version_id, db, user))
