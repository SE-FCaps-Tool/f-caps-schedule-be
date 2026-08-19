"""Target group/project routes introduced for the FE contract migration."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db

# Reuse the established validators and write paths; this module only supplies
# the target nested URLs and translates their responses to the new envelope.
from app.routes.manager_extensions import GroupUpdate, update_group
from app.routes.master_data import (
    DropoutPayload,
    GroupCreate,
    LeaderPayload,
    ProjectCreate,
    approve_dropout,
    change_group_leader,
    create_group,
    create_project,
)

router = APIRouter(prefix="/api/v1", tags=["target-groups-projects"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class ProjectAssignment(BaseModel):
    project_id: int | None = Field(default=None, gt=0)


def _require_manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


@router.get("/semesters/{semester_id}/groups")
def list_semester_groups(semester_id: int, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    rows = db.execute(
        text(
            "SELECT g.id, g.code, g.status::text AS status, g.project_id, "
            "p.code AS project_code, p.title, "
            "COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_member_count "
            "FROM groups g LEFT JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN group_memberships gm ON gm.group_id = g.id "
            "WHERE p.semester_id = :semester_id OR (g.project_id IS NULL AND FALSE) "
            "GROUP BY g.id, p.code, p.title ORDER BY g.code"
        ),
        {"semester_id": semester_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/semesters/{semester_id}/groups", status_code=status.HTTP_201_CREATED)
def create_semester_group(semester_id: int, payload: GroupCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    if payload.project_id is None:
        raise HTTPException(status_code=422, detail={"code": "GROUP_PROJECT_REQUIRED", "message": "A semester-scoped group must select a project."})
    belongs = db.execute(
        text("SELECT 1 FROM projects WHERE id = :project_id AND semester_id = :semester_id"),
        {"project_id": payload.project_id, "semester_id": semester_id},
    ).scalar_one_or_none()
    if belongs is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_IN_SEMESTER", "message": "Project does not belong to this semester."})
    return success_payload(create_group(payload, db, user))


@router.get("/groups/{group_id}/members")
def list_group_members(group_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Group access is not available."})
    rows = db.execute(
        text(
            "SELECT st.id AS student_id, st.student_code, a.display_name, a.email, "
            "gm.membership_role AS role, gm.status "
            "FROM group_memberships gm JOIN students st ON st.id = gm.student_id "
            "LEFT JOIN accounts a ON a.id = st.account_id "
            "WHERE gm.group_id = :group_id ORDER BY gm.membership_role DESC, st.student_code"
        ),
        {"group_id": group_id},
    ).mappings().all()
    if not rows and db.execute(text("SELECT 1 FROM groups WHERE id = :id"), {"id": group_id}).scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND", "message": "Group does not exist."})
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/groups/{group_id}/actions/change-leader")
def target_change_group_leader(group_id: int, payload: LeaderPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(change_group_leader(group_id, payload, db, user))


@router.post("/groups/{group_id}/members/{membership_id}/actions/leave")
def target_leave_group(group_id: int, membership_id: int, payload: DropoutPayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(approve_dropout(group_id, membership_id, payload, db, user))


@router.put("/groups/{group_id}/project")
def assign_group_project(group_id: int, payload: ProjectAssignment, db: Db, user: User) -> dict[str, Any]:
    return success_payload(update_group(group_id, GroupUpdate(project_id=payload.project_id), db, user))


@router.post("/semesters/{semester_id}/projects", status_code=status.HTTP_201_CREATED)
def create_semester_project(semester_id: int, payload: ProjectCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    if payload.semester_id != semester_id:
        payload = payload.model_copy(update={"semester_id": semester_id})
    return success_payload(create_project(payload, db, user))


@router.get("/projects/{project_id}/progression")
def project_progression(project_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Project access is not available."})
    row = db.execute(
        text(
            "SELECT p.id AS project_id, p.code, p.title, p.status::text AS project_status, "
            "g.id AS group_id, g.status::text AS group_status "
            "FROM projects p LEFT JOIN groups g ON g.project_id = p.id WHERE p.id = :id"
        ),
        {"id": project_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project does not exist."})
    return success_payload(dict(row))


@router.get("/projects/{project_id}/results")
def project_results(project_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Project access is not available."})
    rows = db.execute(
        text(
            "SELECT sr.id, sr.session_id, r.type AS round_type, sr.outcome, sr.note, "
            "sr.entered_at, sr.verify_status, sr.remediation_due_at "
            "FROM session_results sr JOIN sessions s ON s.id = sr.session_id "
            "JOIN groups g ON g.id = s.group_id JOIN rounds r ON r.id = "
            "(SELECT sv.round_id FROM schedule_versions sv WHERE sv.id = s.schedule_version_id) "
            "WHERE g.project_id = :project_id ORDER BY sr.entered_at DESC, sr.id DESC"
        ),
        {"project_id": project_id},
    ).mappings().all()
    if db.execute(text("SELECT 1 FROM projects WHERE id = :id"), {"id": project_id}).scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project does not exist."})
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
