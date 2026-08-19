"""Target group/project routes introduced for the FE contract migration."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import external_id, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db

# Reuse the established validators and write paths; this module only supplies
# the target nested URLs and translates their responses to the new envelope.
from app.routes.manager_extensions import GroupUpdate, update_group
from app.routes.master_data import (
    DropoutPayload,
    LeaderPayload,
    approve_dropout,
    change_group_leader,
)

router = APIRouter(prefix="/api/v1", tags=["target-groups-projects"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class ProjectAssignment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    project_id: str | int | None = Field(default=None, alias="projectId")

    @model_validator(mode="after")
    def validate_id(self) -> ProjectAssignment:
        if self.project_id is not None:
            parse_external_id(self.project_id, prefix="prj")
        return self


class TargetGroupCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str = Field(min_length=1, max_length=64)
    student_ids: list[str | int] = Field(alias="studentIds", min_length=1)
    leader_id: str | int | None = Field(default=None, alias="leaderId")

    @model_validator(mode="after")
    def validate_leader(self) -> TargetGroupCreate:
        if self.leader_id is not None and str(self.leader_id) not in {str(item) for item in self.student_ids}:
            raise ValueError("leaderId must be one of studentIds")
        return self


class TargetProjectCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str = Field(min_length=1, max_length=64)
    name_vi: str = Field(alias="nameVi", min_length=1, max_length=255)
    name_en: str | None = Field(default=None, alias="nameEn", max_length=255)
    main_supervisor_id: str | int = Field(alias="mainSupervisorId")
    co_supervisor_id: str | int | None = Field(default=None, alias="coSupervisorId")

    @model_validator(mode="after")
    def supervisors_differ(self) -> TargetProjectCreate:
        if self.co_supervisor_id is not None and str(self.co_supervisor_id) == str(self.main_supervisor_id):
            raise ValueError("mainSupervisorId and coSupervisorId must differ")
        return self


def _target_row(row: dict[str, Any], *, resource: str) -> dict[str, Any]:
    result = dict(row)
    if "id" in result and result["id"] is not None:
        result["id"] = external_id(result["id"], resource)
    for key, prefix in (("project_id", "prj"), ("group_id", "grp"), ("student_id", "stu")):
        if key in result and result[key] is not None:
            result[key] = external_id(result[key], prefix)
    return result


def _require_manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


@router.get("/semesters/{semester_id}/groups")
def list_semester_groups(
    semester_id: int,
    db: Db,
    user: User,
    search: str | None = None,
    status: str | None = None,
    has_project: bool | None = Query(default=None, alias="hasProject"),
    has_leader: bool | None = Query(default=None, alias="hasLeader"),
    warning: str | None = None,
    page: int = 1,
    page_size: int = Query(default=20, alias="pageSize"),
) -> dict[str, Any]:
    _require_manager(user)
    rows = db.execute(
        text(
            "SELECT g.id, g.code, g.status::text AS status, g.project_id, "
            "p.code AS project_code, p.title, "
            "COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_member_count, "
            "COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leader_count "
            "FROM groups g LEFT JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN group_memberships gm ON gm.group_id = g.id "
            "WHERE (p.semester_id = :semester_id OR g.project_id IS NULL) "
            "AND (:search IS NULL OR g.code ILIKE '%' || :search || '%' OR p.code ILIKE '%' || :search || '%') "
            "AND (:status IS NULL OR g.status::text = :status) "
            "GROUP BY g.id, p.code, p.title ORDER BY g.code"
        ),
        {"semester_id": semester_id, "search": search, "status": status},
    ).mappings().all()
    items = [_target_row(dict(row), resource="grp") for row in rows]
    if has_project is not None:
        items = [item for item in items if (item.get("project_id") is not None) == has_project]
    if has_leader is not None:
        items = [item for item in items if ((item.get("leader_count") or 0) > 0) == has_leader]
    return success_payload(items, meta={"page": page, "pageSize": page_size, "total": len(items)})


@router.post("/semesters/{semester_id}/groups", status_code=status.HTTP_201_CREATED)
def create_semester_group(semester_id: int, payload: TargetGroupCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    student_ids = [parse_external_id(value, prefix="stu") for value in payload.student_ids]
    leader_id = parse_external_id(payload.leader_id, prefix="stu") if payload.leader_id is not None else student_ids[0]
    with db.begin():
        duplicate = db.execute(text("SELECT 1 FROM groups WHERE project_id IS NULL AND code = :code"), {"code": payload.code.strip().upper()}).scalar_one_or_none()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail={"code": "GROUP_CODE_DUPLICATE", "message": "Group code already exists."})
        group_id = db.execute(text("INSERT INTO groups (project_id, code) VALUES (NULL, :code) RETURNING id"), {"code": payload.code.strip().upper()}).scalar_one()
        for student_id in student_ids:
            db.execute(
                text("INSERT INTO group_memberships (group_id, student_id, membership_role) VALUES (:group_id, :student_id, :role)"),
                {"group_id": group_id, "student_id": student_id, "role": "LEADER" if student_id == leader_id else "MEMBER"},
            )
    return success_payload({"id": external_id(group_id, "grp"), "code": payload.code.strip().upper(), "status": "FORMED"})


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
def create_semester_project(semester_id: int, payload: TargetProjectCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    supervisor_ids = [parse_external_id(payload.main_supervisor_id, prefix="lec")]
    if payload.co_supervisor_id is not None:
        supervisor_ids.append(parse_external_id(payload.co_supervisor_id, prefix="lec"))
    with db.begin():
        major_id = db.execute(text("SELECT id FROM majors ORDER BY id LIMIT 1")).scalar_one_or_none()
        if major_id is None:
            raise HTTPException(status_code=422, detail={"code": "MAJOR_NOT_FOUND", "message": "No major is configured."})
        project_id = db.execute(
            text("INSERT INTO projects (semester_id, major_id, code, title) VALUES (:semester_id, :major_id, :code, :title) RETURNING id"),
            {"semester_id": semester_id, "major_id": major_id, "code": payload.code.strip().upper(), "title": payload.name_vi.strip()},
        ).scalar_one()
        for index, lecturer_id in enumerate(supervisor_ids):
            db.execute(
                text("INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type) VALUES (:project_id, :lecturer_id, :kind)"),
                {"project_id": project_id, "lecturer_id": lecturer_id, "kind": "MAIN" if index == 0 else "CO"},
            )
    return success_payload({"id": external_id(project_id, "prj"), "code": payload.code.strip().upper(), "nameVi": payload.name_vi.strip(), "nameEn": payload.name_en, "status": "DRAFT"})


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
