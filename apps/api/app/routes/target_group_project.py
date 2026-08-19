"""Target group/project routes introduced for the FE contract migration."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api_contract import external_id, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.status_compat import group_from_legacy, membership_from_legacy, project_from_legacy

# Reuse the established validators and write paths; this module only supplies
# the target nested URLs and translates their responses to the new envelope.
from app.routes.manager_extensions import GroupUpdate, update_group
from app.routes.master_data import LeaderPayload, change_group_leader
from app.services.semester_queries import ensure_semester_writable, semester_or_404

router = APIRouter(prefix="/api/v1", tags=["target-groups-projects"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]

# BR-STU-03: a group under this size only produces a warning, never a block.
MIN_RECOMMENDED_MEMBERS = 4


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


class TargetChangeLeaderPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    leader_id: str | int = Field(alias="leaderId")
    reason: str = Field(min_length=1, max_length=1000)


class TargetLeaveGroupPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    effective_date: date = Field(alias="effectiveDate")
    reason: str = Field(min_length=1, max_length=1000)


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


def _require_manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text("SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)"),
        {"role": user.role},
    ).scalar_one_or_none()


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
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=200),
) -> dict[str, Any]:
    _require_manager(user)
    offset = (page - 1) * page_size
    below_min_only = warning == "MEMBER_COUNT_BELOW_MIN"
    rows = db.execute(
        text(
            "SELECT g.id, g.code, g.status::text AS status, g.project_id, "
            "p.code AS project_code, p.title AS project_title, p.status::text AS project_status, "
            "(SELECT COUNT(*) FROM group_memberships gm WHERE gm.group_id = g.id AND gm.status = 'ACTIVE') AS member_count, "
            "ldr.id AS leader_id, ldr.student_code AS leader_code, la.display_name AS leader_name, "
            "COUNT(*) OVER() AS total_count "
            "FROM groups g "
            "LEFT JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN group_memberships lm ON lm.group_id = g.id AND lm.status = 'ACTIVE' AND lm.membership_role = 'LEADER' "
            "LEFT JOIN students ldr ON ldr.id = lm.student_id "
            "LEFT JOIN accounts la ON la.id = ldr.account_id "
            "WHERE (p.semester_id = :semester_id OR g.project_id IS NULL) "
            "AND (CAST(:search AS text) IS NULL OR g.code ILIKE '%' || CAST(:search AS text) || '%' OR p.code ILIKE '%' || CAST(:search AS text) || '%') "
            "AND (CAST(:status AS text) IS NULL OR g.status::text = CAST(:status AS text)) "
            "AND (CAST(:has_project AS boolean) IS NULL OR (g.project_id IS NOT NULL) = CAST(:has_project AS boolean)) "
            "AND (CAST(:has_leader AS boolean) IS NULL OR (lm.id IS NOT NULL) = CAST(:has_leader AS boolean)) "
            "AND (NOT CAST(:below_min_only AS boolean) OR "
            "(SELECT COUNT(*) FROM group_memberships gm2 WHERE gm2.group_id = g.id AND gm2.status = 'ACTIVE') < :min_members) "
            "ORDER BY g.code LIMIT :limit OFFSET :offset"
        ),
        {
            "semester_id": semester_id, "search": search, "status": status,
            "has_project": has_project, "has_leader": has_leader,
            "below_min_only": below_min_only, "min_members": MIN_RECOMMENDED_MEMBERS,
            "limit": page_size, "offset": offset,
        },
    ).mappings().all()
    total = rows[0]["total_count"] if rows else 0
    items = []
    for row in rows:
        project_assigned = row["project_id"] is not None
        member_count = row["member_count"] or 0
        warnings = []
        if member_count < MIN_RECOMMENDED_MEMBERS:
            warnings.append({"code": "MEMBER_COUNT_BELOW_MIN", "message": "Group has fewer than recommended members."})
        items.append({
            "id": external_id(row["id"], "grp"),
            "code": row["code"],
            "status": group_from_legacy(row["status"], project_assigned=project_assigned).value,
            "memberCount": member_count,
            "leader": {
                "id": external_id(row["leader_id"], "stu"),
                "code": row["leader_code"],
                "fullName": row["leader_name"],
            } if row["leader_id"] is not None else None,
            "project": {
                "id": external_id(row["project_id"], "prj"),
                "code": row["project_code"],
                "name": row["project_title"],
                "status": project_from_legacy(row["project_status"], has_group=True).value,
            } if project_assigned else None,
            "warnings": warnings,
        })
    return success_payload(items, meta={"page": page, "pageSize": page_size, "total": total})


@router.post("/semesters/{semester_id}/groups", status_code=status.HTTP_201_CREATED)
def create_semester_group(semester_id: int, payload: TargetGroupCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    semester_or_404(db, semester_id)
    student_ids = [parse_external_id(value, prefix="stu") for value in payload.student_ids]
    leader_id = parse_external_id(payload.leader_id, prefix="stu") if payload.leader_id is not None else student_ids[0]
    code = payload.code.strip().upper()
    db.rollback()
    with db.begin():
        ensure_semester_writable(db, semester_id)
        existing_students = db.execute(
            text("SELECT id FROM students WHERE id = ANY(:ids)"), {"ids": student_ids}
        ).scalars().all()
        if set(existing_students) != set(student_ids):
            raise HTTPException(status_code=422, detail={"code": "STUDENT_NOT_ENROLLED", "message": "One or more students do not exist."})
        already_active = db.execute(
            text(
                "SELECT gm.student_id FROM group_memberships gm "
                "JOIN groups g ON g.id = gm.group_id LEFT JOIN projects p ON p.id = g.project_id "
                "WHERE gm.status = 'ACTIVE' AND gm.student_id = ANY(:ids) "
                "AND (p.semester_id = :semester_id OR g.project_id IS NULL)"
            ),
            {"ids": student_ids, "semester_id": semester_id},
        ).scalars().all()
        if already_active:
            raise HTTPException(status_code=409, detail={"code": "STUDENT_ALREADY_IN_GROUP", "message": "One or more students are already active in another group this semester."})
        duplicate = db.execute(
            text(
                "SELECT 1 FROM groups g LEFT JOIN projects p ON p.id = g.project_id "
                "WHERE g.code = :code AND (p.semester_id = :semester_id OR g.project_id IS NULL)"
            ),
            {"code": code, "semester_id": semester_id},
        ).scalar_one_or_none()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail={"code": "GROUP_CODE_DUPLICATE", "message": "Group code already exists."})
        group_id = db.execute(text("INSERT INTO groups (project_id, code) VALUES (NULL, :code) RETURNING id"), {"code": code}).scalar_one()
        for student_id in student_ids:
            db.execute(
                text("INSERT INTO group_memberships (group_id, student_id, membership_role) VALUES (:group_id, :student_id, :role)"),
                {"group_id": group_id, "student_id": student_id, "role": "LEADER" if student_id == leader_id else "MEMBER"},
            )
    status_value = group_from_legacy("PENDING_D11", project_assigned=False).value
    return success_payload({"id": external_id(group_id, "grp"), "code": code, "status": status_value})


@router.get("/groups/{group_id}/members")
def list_group_members(group_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Group access is not available."})
    rows = db.execute(
        text(
            "SELECT gm.id AS membership_id, st.id AS student_id, st.student_code, a.display_name, a.email, "
            "gm.membership_role AS role, gm.status "
            "FROM group_memberships gm JOIN students st ON st.id = gm.student_id "
            "LEFT JOIN accounts a ON a.id = st.account_id "
            "WHERE gm.group_id = :group_id ORDER BY gm.membership_role DESC, st.student_code"
        ),
        {"group_id": group_id},
    ).mappings().all()
    if not rows and db.execute(text("SELECT 1 FROM groups WHERE id = :id"), {"id": group_id}).scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND", "message": "Group does not exist."})
    members = []
    for row in rows:
        member = dict(row)
        member["membership_id"] = external_id(member["membership_id"], "mem")
        member["student_id"] = external_id(member["student_id"], "stu")
        member["status"] = membership_from_legacy(member["status"]).value
        members.append(member)
    return success_payload(members, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/groups/{group_id}/actions/change-leader")
def target_change_group_leader(group_id: int, payload: TargetChangeLeaderPayload, db: Db, user: User) -> dict[str, Any]:
    student_id = parse_external_id(payload.leader_id, prefix="stu")
    try:
        result = change_group_leader(group_id, LeaderPayload(student_id=student_id, reason=payload.reason), db, user)
    except HTTPException as exc:
        # Error translation happens at the target boundary only; the legacy
        # handler keeps its own LEADER_MEMBER_NOT_FOUND code unchanged.
        if isinstance(exc.detail, dict) and exc.detail.get("code") == "LEADER_MEMBER_NOT_FOUND":
            raise HTTPException(
                status_code=exc.status_code,
                detail={"code": "LEADER_NOT_ACTIVE_MEMBER", "message": exc.detail.get("message", "")},
            ) from exc
        raise
    return success_payload(result)


@router.post("/groups/{group_id}/members/{membership_id}/actions/leave")
def target_leave_group(group_id: int, membership_id: str | int, payload: TargetLeaveGroupPayload, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    membership_id = parse_external_id(membership_id, prefix="mem")
    with db.begin():
        project_semester_id = db.execute(
            text("SELECT p.semester_id FROM groups g JOIN projects p ON p.id = g.project_id WHERE g.id = :group_id FOR UPDATE"),
            {"group_id": group_id},
        ).scalar_one_or_none()
        if project_semester_id is not None:
            ensure_semester_writable(db, int(project_semester_id))
        row = db.execute(
            text("SELECT id, student_id, membership_role, status FROM group_memberships WHERE id = :membership_id AND group_id = :group_id FOR UPDATE"),
            {"membership_id": membership_id, "group_id": group_id},
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership does not exist."})
        if row["status"] != "ACTIVE":
            raise HTTPException(status_code=409, detail={"code": "MEMBERSHIP_NOT_ACTIVE", "message": "Membership has already ended."})
        actor_id = _actor_id(db, user)
        try:
            db.execute(
                text(
                    "UPDATE group_memberships SET status = 'DROPPED', left_at = :left_at, reason = :reason, "
                    "drop_requested_by = :actor_id, drop_approved_by = :actor_id WHERE id = :id"
                ),
                {"left_at": payload.effective_date, "reason": payload.reason.strip(), "actor_id": actor_id, "id": row["id"]},
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "effectiveDate must be after the membership's join date."}) from exc
        member_count = db.execute(
            text("SELECT COUNT(*) FROM group_memberships WHERE group_id = :group_id AND status = 'ACTIVE'"),
            {"group_id": group_id},
        ).scalar_one()
        new_leader = db.execute(
            text(
                "SELECT student_id FROM group_memberships WHERE group_id = :group_id AND status = 'ACTIVE' AND membership_role = 'LEADER'"
            ),
            {"group_id": group_id},
        ).scalar_one_or_none()
    return success_payload({
        "groupId": external_id(group_id, "grp"),
        "membershipId": external_id(membership_id, "mem"),
        "status": membership_from_legacy("DROPPED").value,
        "memberCount": member_count,
        "leaderId": external_id(new_leader, "stu") if new_leader is not None else None,
    })


@router.put("/groups/{group_id}/project")
def assign_group_project(group_id: int, payload: ProjectAssignment, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    if payload.project_id is None:
        result = dict(update_group(group_id, GroupUpdate(project_id=None), db, user))
        result["status"] = group_from_legacy(result["status"], project_assigned=False).value
        return success_payload(result)
    project_id = parse_external_id(payload.project_id, prefix="prj")
    with db.begin():
        group_row = db.execute(
            text(
                "SELECT g.id, g.status::text AS status, g.code, p.semester_id AS current_semester_id "
                "FROM groups g LEFT JOIN projects p ON p.id = g.project_id WHERE g.id = :id FOR UPDATE OF g"
            ),
            {"id": group_id},
        ).mappings().one_or_none()
        if group_row is None:
            raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND", "message": "Group does not exist."})
        if group_row["status"] == "DROPPED":
            raise HTTPException(status_code=409, detail={"code": "GROUP_DISBANDED", "message": "Group is disbanded."})
        project_row = db.execute(
            text("SELECT id, semester_id, status::text AS status FROM projects WHERE id = :id FOR UPDATE"),
            {"id": project_id},
        ).mappings().one_or_none()
        if project_row is None:
            raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project does not exist."})
        if project_row["status"] == "ARCHIVED":
            raise HTTPException(status_code=409, detail={"code": "PROJECT_CANCELLED", "message": "Project is cancelled."})
        already_assigned = db.execute(
            text("SELECT 1 FROM groups WHERE project_id = :project_id AND id <> :group_id"),
            {"project_id": project_id, "group_id": group_id},
        ).scalar_one_or_none()
        if already_assigned is not None:
            raise HTTPException(status_code=409, detail={"code": "PROJECT_ALREADY_ASSIGNED", "message": "Project is already assigned to another group."})
        if group_row["current_semester_id"] is not None and int(group_row["current_semester_id"]) != int(project_row["semester_id"]):
            raise HTTPException(status_code=409, detail={"code": "SEMESTER_MISMATCH", "message": "Group and project must be in the same semester."})
        ensure_semester_writable(db, int(project_row["semester_id"]))
        if group_row["current_semester_id"] is not None:
            ensure_semester_writable(db, int(group_row["current_semester_id"]))
        db.execute(text("UPDATE groups SET project_id = :project_id WHERE id = :id"), {"project_id": project_id, "id": group_id})
    return success_payload({
        "id": external_id(group_id, "grp"),
        "code": group_row["code"],
        "status": group_from_legacy(group_row["status"], project_assigned=True).value,
        "projectId": external_id(project_id, "prj"),
    })


@router.post("/semesters/{semester_id}/projects", status_code=status.HTTP_201_CREATED)
def create_semester_project(semester_id: int, payload: TargetProjectCreate, db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    semester_or_404(db, semester_id)
    supervisor_ids = [parse_external_id(payload.main_supervisor_id, prefix="lec")]
    if payload.co_supervisor_id is not None:
        supervisor_ids.append(parse_external_id(payload.co_supervisor_id, prefix="lec"))
    code = payload.code.strip().upper()
    db.rollback()
    with db.begin():
        ensure_semester_writable(db, semester_id)
        existing_lecturers = db.execute(
            text("SELECT id FROM lecturers WHERE id = ANY(:ids)"), {"ids": supervisor_ids}
        ).scalars().all()
        if set(existing_lecturers) != set(supervisor_ids):
            raise HTTPException(status_code=422, detail={"code": "LECTURER_NOT_FOUND", "message": "One or more supervisors do not exist."})
        duplicate = db.execute(
            text("SELECT 1 FROM projects WHERE semester_id = :semester_id AND code = :code"),
            {"semester_id": semester_id, "code": code},
        ).scalar_one_or_none()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail={"code": "PROJECT_CODE_DUPLICATE", "message": "Project code already exists in this semester."})
        major_id = db.execute(text("SELECT id FROM majors ORDER BY id LIMIT 1")).scalar_one_or_none()
        if major_id is None:
            raise HTTPException(status_code=422, detail={"code": "MAJOR_NOT_FOUND", "message": "No major is configured."})
        project_id = db.execute(
            text("INSERT INTO projects (semester_id, major_id, code, title) VALUES (:semester_id, :major_id, :code, :title) RETURNING id"),
            {"semester_id": semester_id, "major_id": major_id, "code": code, "title": payload.name_vi.strip()},
        ).scalar_one()
        for index, lecturer_id in enumerate(supervisor_ids):
            db.execute(
                text("INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type) VALUES (:project_id, :lecturer_id, :kind)"),
                {"project_id": project_id, "lecturer_id": lecturer_id, "kind": "MAIN" if index == 0 else "CO"},
            )
    status_value = project_from_legacy("ACTIVE", has_group=False).value
    return success_payload({"id": external_id(project_id, "prj"), "code": code, "nameVi": payload.name_vi.strip(), "nameEn": payload.name_en, "status": status_value})


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
    result = dict(row)
    has_group = result["group_id"] is not None
    result["project_status"] = project_from_legacy(result["project_status"], has_group=has_group).value
    if has_group:
        result["group_status"] = group_from_legacy(result["group_status"], project_assigned=True).value
    return success_payload(result)


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
