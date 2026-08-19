"""Target controlled-change action aliases for published sessions."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.schedule_operations import (
    RescheduleRequestPayload,
    SessionEditPayload,
    controlled_change,
    postpone_session,
)

router = APIRouter(prefix="/api/v1", tags=["target-operations"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class ChangeRoomPayload(BaseModel):
    room_id: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=1000)


class ReplaceReviewerPayload(BaseModel):
    reviewer_ids: list[int] = Field(min_length=1)
    result_owner_id: int | None = Field(default=None, gt=0)
    reason: str = Field(min_length=1, max_length=1000)


def _version_for_session(session_id: int, db: Session) -> int:
    version_id = db.execute(text("SELECT schedule_version_id FROM sessions WHERE id = :id"), {"id": session_id}).scalar_one_or_none()
    db.rollback()
    if version_id is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
    return int(version_id)


@router.post("/sessions/{session_id}/actions/change-room")
def change_session_room(session_id: int, payload: ChangeRoomPayload, db: Db, user: User) -> dict[str, Any]:
    version_id = _version_for_session(session_id, db)
    edit = SessionEditPayload(room_id=payload.room_id, reason=payload.reason)
    return success_payload(controlled_change(version_id=version_id, session_id=session_id, payload=edit, db=db, user=user))


@router.post("/sessions/{session_id}/actions/replace-reviewer")
def replace_session_reviewer(session_id: int, payload: ReplaceReviewerPayload, db: Db, user: User) -> dict[str, Any]:
    version_id = _version_for_session(session_id, db)
    edit = SessionEditPayload(reviewer_ids=payload.reviewer_ids, result_owner_id=payload.result_owner_id, reason=payload.reason)
    return success_payload(controlled_change(version_id=version_id, session_id=session_id, payload=edit, db=db, user=user))


@router.post("/sessions/{session_id}/actions/postpone")
def postpone_target_session(session_id: int, payload: RescheduleRequestPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(postpone_session(session_id, payload, db, user))
