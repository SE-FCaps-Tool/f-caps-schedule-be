"""Global Timeframe template management contract."""

from datetime import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.errors import DomainError
from app.response_models import (
    TimeframeEnvelopeResponse,
    TimeframeListEnvelopeResponse,
    TimeframePreviewEnvelopeResponse,
)
from app.services.timeframe_service import (
    archive_timeframe,
    create_manual_timeframe,
    create_timeframe,
    get_timeframe,
    list_timeframes,
    preview_manual_timeframe,
    preview_timeframe,
    update_manual_timeframe,
    update_timeframe,
)

router = APIRouter(prefix="/api/v1", tags=["target-timeframes"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class TimeframeBreakWindowPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(min_length=1, max_length=255)
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")


class TimeframePreviewPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    block_duration_minutes: int = Field(alias="blockDurationMinutes", gt=0)
    group_duration_minutes: int = Field(alias="groupDurationMinutes", gt=0)
    break_between_blocks_minutes: int = Field(
        default=0,
        alias="breakBetweenBlocksMinutes",
        ge=0,
    )
    break_windows: list[TimeframeBreakWindowPayload] = Field(
        default_factory=list,
        alias="breakWindows",
        max_length=20,
    )


class TimeframeMutationPayload(TimeframePreviewPayload):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)


class ManualTimelinePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    groups_per_slot: int = Field(alias="groupsPerSlot")


class ManualTimeframePreviewPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    group_duration_minutes: int = Field(alias="groupDurationMinutes")
    timelines: list[ManualTimelinePayload] = Field(max_length=50)


class ManualTimeframeMutationPayload(ManualTimeframePreviewPayload):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)


class TimeframeArchivePayload(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Manager access is required."})


def _domain_error(exc: DomainError) -> HTTPException:
    return HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc).partition(": ")[2]})


@router.post("/timeframes/preview", response_model=TimeframePreviewEnvelopeResponse)
def preview(payload: TimeframePreviewPayload, user: User) -> dict[str, Any]:
    _manager(user)
    try:
        result = preview_timeframe(**payload.model_dump())
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.post(
    "/timeframes",
    status_code=status.HTTP_201_CREATED,
    response_model=TimeframeEnvelopeResponse,
)
def create(payload: TimeframeMutationPayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    values = payload.model_dump()
    kind = values.pop("type")
    try:
        result = create_timeframe(db, user, kind=kind, **values)
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.post(
    "/timeframes/manual/preview",
    response_model=TimeframePreviewEnvelopeResponse,
)
def preview_manual(payload: ManualTimeframePreviewPayload, user: User) -> dict[str, Any]:
    _manager(user)
    try:
        result = preview_manual_timeframe(**payload.model_dump())
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.post(
    "/timeframes/manual",
    status_code=status.HTTP_201_CREATED,
    response_model=TimeframeEnvelopeResponse,
)
def create_manual(
    payload: ManualTimeframeMutationPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _manager(user)
    values = payload.model_dump()
    kind = values.pop("type")
    try:
        result = create_manual_timeframe(db, user, kind=kind, **values)
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.get("/timeframes", response_model=TimeframeListEnvelopeResponse)
def list_all(
    db: Db,
    user: User,
    include_archived: bool = Query(default=False, alias="includeArchived"),
) -> dict[str, Any]:
    _manager(user)
    rows = list_timeframes(db, include_archived=include_archived)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get("/timeframes/{timeframe_id}", response_model=TimeframeEnvelopeResponse)
def get_one(timeframe_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    return success_payload(get_timeframe(db, timeframe_id))


@router.patch("/timeframes/{timeframe_id}", response_model=TimeframeEnvelopeResponse)
def update(timeframe_id: int, payload: TimeframeMutationPayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    values = payload.model_dump()
    kind = values.pop("type")
    try:
        result = update_timeframe(db, user, timeframe_id=timeframe_id, kind=kind, **values)
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.patch(
    "/timeframes/{timeframe_id}/manual",
    response_model=TimeframeEnvelopeResponse,
)
def update_manual(
    timeframe_id: int,
    payload: ManualTimeframeMutationPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _manager(user)
    values = payload.model_dump()
    kind = values.pop("type")
    try:
        result = update_manual_timeframe(
            db,
            user,
            timeframe_id=timeframe_id,
            kind=kind,
            **values,
        )
    except DomainError as exc:
        raise _domain_error(exc) from exc
    return success_payload(result)


@router.delete("/timeframes/{timeframe_id}", response_model=TimeframeEnvelopeResponse)
def archive(
    timeframe_id: int,
    db: Db,
    user: User,
    payload: TimeframeArchivePayload | None = None,
) -> dict[str, Any]:
    _manager(user)
    return success_payload(
        archive_timeframe(db, user, timeframe_id=timeframe_id, reason=payload.reason if payload else None)
    )
