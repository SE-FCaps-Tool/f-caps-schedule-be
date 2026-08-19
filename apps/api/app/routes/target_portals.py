"""Scoped lecturer and leader portal read models for the separated frontend."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.services.access import lecturer_id_for_account, student_id_for_account

router = APIRouter(prefix="/api/v1", tags=["target-portals"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _invitation_status(status: str, registration_deadline: datetime | None) -> str:
    if status == "PENDING" and registration_deadline is not None and registration_deadline < datetime.now(UTC):
        return "EXPIRED"
    return status


def _lecturer_id(db: Session, user: CurrentUser) -> int:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer portal access is required."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    return int(lecturer_id)


def _student_id(db: Session, user: CurrentUser) -> int:
    if user.role != "STUDENT":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Leader portal access is required."})
    student_id = student_id_for_account(db, user.account_id)
    if student_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Student profile is not linked."})
    return int(student_id)


@router.get("/lecturer/me/invitations")
def lecturer_invitations(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT ri.round_id, ri.lecturer_id, ri.status::text AS status, ri.responded_at, "
            "r.name AS round_name, r.type::text AS round_type, r.registration_deadline "
            "FROM round_invitations ri JOIN rounds r ON r.id = ri.round_id "
            "WHERE ri.lecturer_id = :lecturer_id "
            "ORDER BY r.id DESC"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    invitations = [
        {
            "id": f"inv_{row['round_id']}_{row['lecturer_id']}",
            "round": {
                # Keep this a JSON string while remaining compatible with the
                # existing integer round path parameter used by the respond API.
                "id": str(row["round_id"]),
                "name": row["round_name"] or row["round_type"],
                "type": row["round_type"],
                "registrationDeadline": row["registration_deadline"],
            },
            "status": _invitation_status(row["status"], row["registration_deadline"]),
            "respondedAt": row["responded_at"],
        }
        for row in rows
    ]
    return success_payload(invitations)


@router.get("/lecturer/me/sessions")
def lecturer_sessions(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT DISTINCT s.id, sv.round_id, s.start_at, s.end_at, s.status, "
            "g.id AS group_id, g.code AS group_code, p.code AS project_code, "
            "rm.code AS room_code, r.type AS round_type "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id "
            "JOIN projects p ON p.id = g.project_id LEFT JOIN rooms rm ON rm.id = s.room_id "
            "JOIN council_members cm ON cm.council_id = s.council_id "
            "WHERE cm.lecturer_id = :lecturer_id ORDER BY s.start_at, s.id"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get("/lecturer/me/supervised-projects")
def lecturer_supervised_projects(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT p.id, p.code, p.title, p.status::text AS status, p.semester_id, "
            "s.code AS semester_code, ps.supervisor_type "
            "FROM project_supervisors ps JOIN projects p ON p.id = ps.project_id "
            "JOIN semesters s ON s.id = p.semester_id WHERE ps.lecturer_id = :lecturer_id "
            "ORDER BY s.id DESC, p.code"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get("/lecturer/me/remediations")
def lecturer_remediations(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT rc.id, rc.group_id, g.code AS group_code, rc.status, rc.due_at, "
            "rc.verifier_lecturer_id, rc.note, r.type AS round_type "
            "FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id "
            "JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id "
            "WHERE rc.verifier_lecturer_id = :lecturer_id ORDER BY rc.due_at, rc.id"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


def _leader_group_ids(db: Session, student_id: int) -> list[int]:
    return [int(row[0]) for row in db.execute(text("SELECT group_id FROM group_memberships WHERE student_id = :student_id AND membership_role = 'LEADER' AND status = 'ACTIVE'"), {"student_id": student_id}).all()]


@router.get("/leader/me/dashboard")
def leader_dashboard(db: Db, user: User) -> dict[str, Any]:
    student_id = _student_id(db, user)
    group_ids = _leader_group_ids(db, student_id)
    groups = db.execute(
        text("SELECT g.id, g.code, g.status::text AS status, p.id AS project_id, p.code AS project_code, p.title FROM groups g LEFT JOIN projects p ON p.id = g.project_id WHERE g.id = ANY(:group_ids) ORDER BY g.code"),
        {"group_ids": group_ids or [0]},
    ).mappings().all()
    return success_payload({"groups": [dict(row) for row in groups], "groupCount": len(groups)})


@router.get("/leader/me/sessions")
def leader_sessions(db: Db, user: User) -> dict[str, Any]:
    student_id = _student_id(db, user)
    group_ids = _leader_group_ids(db, student_id)
    rows = db.execute(
        text(
            "SELECT s.id, sv.round_id, s.group_id, g.code AS group_code, p.code AS project_code, "
            "s.start_at, s.end_at, s.room_id, rm.code AS room_code, s.status, r.type AS round_type "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id "
            "LEFT JOIN projects p ON p.id = g.project_id LEFT JOIN rooms rm ON rm.id = s.room_id "
            "WHERE s.group_id = ANY(:group_ids) ORDER BY s.start_at, s.id"
        ),
        {"group_ids": group_ids or [0]},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
