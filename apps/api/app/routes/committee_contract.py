"""Committee catalog contract: bulk-create, list, detail and delete."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api_contract import ApiDataEnvelope, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.response_models import (
    CommitteeBulkCreateEnvelopeResponse,
    CommitteeBulkDeleteEnvelopeResponse,
    CommitteeEnvelopeResponse,
    CommitteeListEnvelopeResponse,
    CommitteePreviewEnvelopeResponse,
    TargetEntityStatusResponse,
)
from app.services.committee_service import (
    bulk_delete_committees,
    create_committees,
    delete_committee,
    get_committee,
    list_committees,
    preview_committees,
)

router = APIRouter(prefix="/api/v1", tags=["target-committees"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class CommitteeGroupPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str = Field(min_length=1, max_length=32)
    member_ids: list[str | int] = Field(alias="memberIds", min_length=1, max_length=15)


class CommitteeBatchPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    groups: list[CommitteeGroupPayload] = Field(min_length=1, max_length=200)


class CommitteeBulkDeletePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    committee_ids: list[str | int] = Field(alias="committeeIds", min_length=1, max_length=200)


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Manager access is required."})


def _groups_payload(payload: CommitteeBatchPayload) -> list[dict[str, Any]]:
    groups = []
    for group in payload.groups:
        member_ids = [parse_external_id(value, prefix="lec") for value in group.member_ids]
        groups.append({"code": group.code, "member_ids": member_ids})
    return groups


@router.post("/committees/preview", response_model=CommitteePreviewEnvelopeResponse)
def preview(payload: CommitteeBatchPayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    result = preview_committees(db, _groups_payload(payload))
    return success_payload(result)


@router.post(
    "/committees",
    status_code=status.HTTP_201_CREATED,
    response_model=CommitteeBulkCreateEnvelopeResponse,
)
def create(payload: CommitteeBatchPayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    result = create_committees(db, user, _groups_payload(payload))
    return success_payload(result)


@router.get("/committees", response_model=CommitteeListEnvelopeResponse)
def list_all(
    db: Db,
    user: User,
    lecturer_id: str | None = Query(default=None, alias="lecturerId"),
) -> dict[str, Any]:
    _manager(user)
    resolved = parse_external_id(lecturer_id, prefix="lec") if lecturer_id is not None else None
    rows = list_committees(db, lecturer_id=resolved)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get("/committees/{committeeId}", response_model=CommitteeEnvelopeResponse)
def get_one(committee_id: Annotated[str, Path(alias="committeeId")], db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    resolved = parse_external_id(committee_id, prefix="cmt")
    return success_payload(get_committee(db, resolved))


@router.delete(
    "/committees/{committeeId}",
    response_model=ApiDataEnvelope[TargetEntityStatusResponse],
    response_model_exclude_unset=True,
)
def remove(committee_id: Annotated[str, Path(alias="committeeId")], db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    resolved = parse_external_id(committee_id, prefix="cmt")
    delete_committee(db, resolved)
    return success_payload({"id": resolved, "status": "DELETED"})


@router.post("/committees/bulk-delete", response_model=CommitteeBulkDeleteEnvelopeResponse)
def bulk_delete(payload: CommitteeBulkDeletePayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    ids = [parse_external_id(value, prefix="cmt") for value in payload.committee_ids]
    return success_payload(bulk_delete_committees(db, ids))
