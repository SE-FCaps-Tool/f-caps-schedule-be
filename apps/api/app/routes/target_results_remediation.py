"""Target result/progression and remediation workflow aliases."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.results import (
    OverdueFailPayload,
    RemediationDecisionPayload,
    decide_remediation,
    fail_overdue_remediation,
)

router = APIRouter(prefix="/api/v1", tags=["target-results-remediation"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


@router.post("/remediations/{remediation_id}/verify")
def verify_remediation(remediation_id: int, payload: RemediationDecisionPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(decide_remediation(remediation_id, payload, db, user))


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
