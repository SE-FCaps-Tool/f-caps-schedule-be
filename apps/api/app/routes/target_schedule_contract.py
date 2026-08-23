"""Nested schedule-version and draft-session contract routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api_contract import external_id, success_payload
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


@router.get("/rounds/{roundId}/schedules")
def list_target_schedules(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    rows = list_schedule_versions(round_id, db, user)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/rounds/{roundId}/schedules/generate", status_code=201)
def generate_target_schedule(round_id: Annotated[int, Path(alias="roundId")], payload: ScheduleRunPayload, db: Db, user: User) -> dict[str, Any]:
    result = run_scheduler(round_id, payload, db, user)
    return success_payload({
        "versionId": external_id(result["version_id"], "sv") if result.get("version_id") else None,
        "versionNumber": result.get("version_number", result.get("version_id")),
        "status": result.get("status", "DRAFT"),
        "scheduledCount": result.get("scheduled_count", 0),
        "unscheduledCount": len(result.get("unscheduled", [])),
        "overallScore": result.get("overall_score", result.get("soft_scores", {}).get("overall", 0)),
        "scores": result.get("scores", result.get("soft_scores", {})),
        "unscheduled": result.get("unscheduled", []),
    })


@router.get("/rounds/{roundId}/schedules/{scheduleId}")
def target_schedule_detail(round_id: Annotated[int, Path(alias="roundId")], schedule_id: Annotated[int, Path(alias="scheduleId")], db: Db, user: User) -> dict[str, Any]:
    result = schedule_version_detail(schedule_id, db, user)
    if result.get("round_id") not in {None, round_id}:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "Schedule is outside this round."})
    return success_payload(result)


@router.post("/rounds/{roundId}/schedules/{scheduleId}/actions/set-active")
def set_target_schedule_active(round_id: Annotated[int, Path(alias="roundId")], schedule_id: Annotated[int, Path(alias="scheduleId")], db: Db, user: User) -> dict[str, Any]:
    return success_payload(activate_schedule_version(schedule_id, db, user))


@router.post("/rounds/{roundId}/schedules/{scheduleId}/actions/discard")
def discard_target_schedule(round_id: Annotated[int, Path(alias="roundId")], schedule_id: Annotated[int, Path(alias="scheduleId")], db: Db, user: User) -> dict[str, Any]:
    return success_payload(delete_draft_version(schedule_id, db, user))


@router.get("/rounds/{roundId}/sessions")
def list_target_sessions(
    round_id: Annotated[int, Path(alias="roundId")],
    db: Db,
    user: User,
    schedule_id: int | None = Query(default=None, alias="versionId"),
) -> dict[str, Any]:
    rows = list_sessions(db, user, round_id=round_id, version_id=schedule_id)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
