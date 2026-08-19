"""Target result/progression and remediation workflow aliases."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.results import (
    OverdueFailPayload,
    RemediationDecisionPayload,
    ResultPayload,
    decide_remediation,
    fail_overdue_remediation,
    record_result,
)

router = APIRouter(prefix="/api/v1", tags=["target-results-remediation"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class TargetRemediation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deadline: datetime
    verifier_id: str | int = Field(alias="verifierId")


class TargetResultPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    result: str = Field(min_length=1, max_length=32)
    note: str | None = None
    remediation: TargetRemediation | None = None


@router.post("/remediations/{remediation_id}/verify")
def verify_remediation(remediation_id: int, payload: RemediationDecisionPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(decide_remediation(remediation_id, payload, db, user))


@router.post("/sessions/{session_id}/result", status_code=201)
def create_target_result(session_id: int, payload: TargetResultPayload, db: Db, user: User) -> dict[str, Any]:
    verifier_id = None
    remediation_due_at = None
    if payload.remediation is not None:
        from app.api_contract import parse_external_id

        verifier_id = parse_external_id(payload.remediation.verifier_id, prefix="lec")
        remediation_due_at = payload.remediation.deadline
    legacy = ResultPayload(
        result=payload.result,
        note=payload.note,
        remediationDueAt=remediation_due_at,
        verifierLecturerId=verifier_id,
    )
    return success_payload(record_result(session_id, legacy, db, user))


@router.post("/remediations/{remediation_id}/actions/overdue-fail")
def overdue_fail_remediation(remediation_id: int, payload: OverdueFailPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(fail_overdue_remediation(remediation_id, payload, db, user))


@router.get("/semesters/{semester_id}/remediations")
def list_semester_remediations(semester_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Remediation access is not available."})
    rows = db.execute(
        text(
            "SELECT rc.id, rc.group_id, g.code AS group_code, rc.status, rc.due_at, "
            "rc.verifier_lecturer_id, rc.note, r.type AS round_type "
            "FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id "
            "JOIN session_results sr ON sr.id = rc.session_result_id "
            "JOIN sessions s ON s.id = sr.session_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id "
            "WHERE r.semester_id = :semester_id ORDER BY rc.due_at, rc.id"
        ),
        {"semester_id": semester_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
