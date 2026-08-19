"""Nested schedule-version and draft-session contract routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.manager_extensions import list_sessions
from app.routes.schedule_operations import (
    ScheduleRunPayload,
    activate_schedule_version,
    delete_draft_version,
    list_schedule_versions,
    run_scheduler,
    schedule_version_detail,
)

router = APIRouter(prefix="/api/v1", tags=["target-schedules"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/rounds/{round_id}/schedules")
def list_target_schedules(round_id: int, db: Db, user: User) -> dict[str, Any]:
    rows = list_schedule_versions(round_id, db, user)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/rounds/{round_id}/schedules/generate", status_code=201)
def generate_target_schedule(round_id: int, payload: ScheduleRunPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(run_scheduler(round_id, payload, db, user))


@router.get("/rounds/{round_id}/schedules/{schedule_id}")
def target_schedule_detail(round_id: int, schedule_id: int, db: Db, user: User) -> dict[str, Any]:
    result = schedule_version_detail(schedule_id, db, user)
    if result.get("round_id") not in {None, round_id}:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "Schedule is outside this round."})
    return success_payload(result)


@router.post("/rounds/{round_id}/schedules/{schedule_id}/actions/set-active")
def set_target_schedule_active(round_id: int, schedule_id: int, db: Db, user: User) -> dict[str, Any]:
    return success_payload(activate_schedule_version(schedule_id, db, user))


@router.post("/rounds/{round_id}/schedules/{schedule_id}/actions/discard")
def discard_target_schedule(round_id: int, schedule_id: int, db: Db, user: User) -> dict[str, Any]:
    return success_payload(delete_draft_version(schedule_id, db, user))


@router.get("/rounds/{round_id}/sessions")
def list_target_sessions(round_id: int, db: Db, user: User, schedule_id: int | None = None) -> dict[str, Any]:
    rows = list_sessions(db, user, round_id=round_id, version_id=schedule_id)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
