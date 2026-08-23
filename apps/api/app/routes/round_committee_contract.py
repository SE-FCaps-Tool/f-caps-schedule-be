"""Round to Committee binding contract: replace and list a Round's Committees."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api_contract import parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.response_models import CommitteeListEnvelopeResponse
from app.services.committee_service import list_round_committees, replace_round_committees

router = APIRouter(prefix="/api/v1", tags=["target-round-committees"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class RoundCommitteeReplacePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    committee_ids: list[str | int] = Field(alias="committeeIds", max_length=200)


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Manager access is required."})


@router.put("/rounds/{roundId}/committees", response_model=CommitteeListEnvelopeResponse)
def replace(round_id: Annotated[int, Path(alias="roundId")], payload: RoundCommitteeReplacePayload, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    ids = [parse_external_id(value, prefix="cmt") for value in payload.committee_ids]
    rows = replace_round_committees(db, round_id, user, ids)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get("/rounds/{roundId}/committees", response_model=CommitteeListEnvelopeResponse)
def list_for_round(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    rows = list_round_committees(db, round_id)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
