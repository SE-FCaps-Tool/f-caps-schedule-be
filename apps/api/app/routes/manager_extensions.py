"""Manager-facing compatibility endpoints for the current UI mock flow.

These endpoints deliberately keep the existing numeric identifiers and domain
statuses.  The mock UI can use the extra display fields while the core
schedule state machine remains unchanged.
"""

from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
import re
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook, load_workbook
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.config import get_settings
from app.domain.errors import DomainError
from app.domain.round_setup import validate_round_configuration

router = APIRouter(prefix="/api/v1", tags=["manager-ui-compatibility"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


def _json(value: Any) -> str:
    import json

    return json.dumps(value, default=str)


class ProjectUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    supervisors: list[str] | None = None


class GroupUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=64)


class RoundUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    session_duration_minutes: int | None = Field(default=None, gt=0, le=480)
    reviewer_count: int | None = Field(default=None, gt=0)
    result_owner_mode: bool | None = None
    group_selection_mode: bool | None = None
    registration_deadline: datetime | None = None
    h12_sessions_per_part: int | None = Field(default=None, gt=0)
    h12_sessions_per_day: int | None = Field(default=None, gt=0)
    h12_semester_quota: int | None = Field(default=None, gt=0)
    max_groups_per_timeslot: int | None = Field(default=None, gt=0)
    max_minutes_per_part: int | None = Field(default=None, gt=0)
    max_minutes_per_day: int | None = Field(default=None, gt=0)


class TimeslotUpdate(BaseModel):
    start_at: datetime | None = None
    end_at: datetime | None = None
    active: bool | None = None
    part: str | None = Field(default=None, pattern="^(AM|PM)$")


class QuotaUpdate(BaseModel):
    quota: int = Field(gt=0)


class SemesterUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    start_date: date | None = None
    end_date: date | None = None


def _row_with_json(row: Any) -> dict[str, Any]:
    return dict(row)


@router.patch("/semesters/{semester_id}")
def update_semester(semester_id: int, payload: SemesterUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    current = db.execute(text("SELECT code, name, start_date, end_date, status FROM semesters WHERE id = :id"), {"id": semester_id}).mappings().one_or_none()
    db.rollback()
    if current is None:
        raise HTTPException(status_code=404, detail={"code": "SEMESTER_NOT_FOUND", "message": "Semester does not exist."})
    values = {**dict(current), **payload.model_dump(exclude_unset=True)}
    if values["end_date"] < values["start_date"]:
        raise HTTPException(status_code=422, detail={"code": "SEMESTER_DATE_INVALID", "message": "end_date must be after start_date."})
    settings = get_settings()
    inclusive_days = (values["end_date"] - values["start_date"]).days + 1
    if not settings.semester_min_duration_days <= inclusive_days <= settings.semester_max_duration_days:
        raise HTTPException(status_code=422, detail={"code": "SEMESTER_DURATION_INVALID", "message": "Semester duration is outside the configured range."})
    changed = {key: value for key, value in payload.model_dump(exclude_unset=True).items()}
    if not changed:
        return {"id": semester_id, **dict(current)}
    with db.begin():
        changed["id"] = semester_id
        assignments = ", ".join(f"{key} = :{key}" for key in changed if key != "id")
        db.execute(text(f"UPDATE semesters SET {assignments} WHERE id = :id"), changed)
    return dict(db.execute(text("SELECT id, code, name, start_date, end_date, status, created_at FROM semesters WHERE id = :id"), {"id": semester_id}).mappings().one())


@router.get("/rounds/{round_id}")
def get_round_detail(round_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    row = db.execute(
        text(
            """
            SELECT r.*, s.code AS semester_code, s.name AS semester_name,
                   COALESCE((SELECT MIN(day_date) FROM round_days WHERE round_id = r.id), r.start_date) AS effective_start_date,
                   COALESCE((SELECT MAX(day_date) FROM round_days WHERE round_id = r.id), r.end_date) AS effective_end_date,
                   (SELECT COUNT(*) FROM round_groups WHERE round_id = r.id) AS group_count,
                   (SELECT COUNT(*) FROM round_rooms WHERE round_id = r.id) AS room_count,
                   (SELECT COUNT(*) FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = r.id AND ts.active) AS active_timeslot_count
            FROM rounds r JOIN semesters s ON s.id = r.semester_id WHERE r.id = :id
            """
        ),
        {"id": round_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    days = db.execute(
        text(
            "SELECT rd.id, rd.day_date, ts.id AS timeslot_id, ts.start_at, ts.end_at, ts.part, ts.active "
            "FROM round_days rd LEFT JOIN timeslots ts ON ts.round_day_id = rd.id WHERE rd.round_id = :id "
            "ORDER BY rd.day_date, ts.start_at"
        ),
        {"id": round_id},
    ).mappings().all()
    return {**dict(row), "days": [dict(item) for item in days]}


@router.patch("/rounds/{round_id}")
def update_round(round_id: int, payload: RoundUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return get_round_detail(round_id, db, user)
    if values.get("start_date") and values.get("end_date") and values["end_date"] < values["start_date"]:
        raise HTTPException(status_code=422, detail={"code": "ROUND_DATE_INVALID", "message": "end_date must be after start_date."})
    columns = {"start_date", "end_date", "session_duration_minutes", "reviewer_count", "result_owner_mode", "group_selection_mode", "registration_deadline", "h12_sessions_per_part", "h12_sessions_per_day", "h12_semester_quota", "max_groups_per_timeslot", "max_minutes_per_part", "max_minutes_per_day"}
    assignments = [f"{key} = :{key}" for key in values if key in columns]
    if not assignments:
        raise HTTPException(status_code=422, detail={"code": "ROUND_UPDATE_EMPTY", "message": "No editable round fields supplied."})
    values["id"] = round_id
    with db.begin():
        current_round = db.execute(text("SELECT status, type, reviewer_count, result_owner_mode, start_date, end_date FROM rounds WHERE id = :id FOR UPDATE"), {"id": round_id}).mappings().one_or_none()
        if current_round is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
        if str(current_round["status"]) not in {"DRAFT", "OPEN_REGISTRATION"}:
            raise HTTPException(status_code=409, detail={"code": "ROUND_CONFIG_LOCKED", "message": "Round configuration can only be edited before scheduling."})
        merged_start = values.get("start_date", current_round["start_date"])
        merged_end = values.get("end_date", current_round["end_date"])
        if merged_start is not None and merged_end is not None and merged_end < merged_start:
            raise HTTPException(status_code=422, detail={"code": "ROUND_DATE_INVALID", "message": "end_date must be after start_date."})
        try:
            validate_round_configuration({"type": str(current_round["type"]), "reviewer_count": values.get("reviewer_count", current_round["reviewer_count"]), "result_owner_mode": values.get("result_owner_mode", current_round["result_owner_mode"]), "groups": [1], "timeslots": [1], "rooms": [1]})
        except DomainError as exc:
            raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
        updated = db.execute(text(f"UPDATE rounds SET {', '.join(assignments)} WHERE id = :id RETURNING id"), values).scalar_one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    return get_round_detail(round_id, db, user)


@router.patch("/projects/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    values = payload.model_dump(exclude_unset=True)
    try:
        with db.begin():
            row = db.execute(text("SELECT id, code, title FROM projects WHERE id = :id FOR UPDATE"), {"id": project_id}).mappings().one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project does not exist."})
            scalar = {key: values[key] for key in ("code", "title") if key in values}
            if scalar:
                assignments = ", ".join(f"{key} = :{key}" for key in scalar)
                scalar["id"] = project_id
                db.execute(text(f"UPDATE projects SET {assignments} WHERE id = :id"), scalar)
            if "supervisors" in values:
                db.execute(text("DELETE FROM project_supervisors WHERE project_id = :id"), {"id": project_id})
                for assignment in values["supervisors"] or []:
                    code, _, supervisor_type = assignment.partition(":")
                    lecturer_id = db.execute(text("SELECT id FROM lecturers WHERE lecturer_code = :code"), {"code": code.strip().upper()}).scalar_one_or_none()
                    if lecturer_id is None or supervisor_type not in {"MAIN", "CO"}:
                        raise HTTPException(status_code=422, detail={"code": "SUPERVISOR_INVALID", "message": "Supervisor code/type is invalid."})
                    db.execute(text("INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type) VALUES (:project_id, :lecturer_id, CAST(:type AS supervisor_type))"), {"project_id": project_id, "lecturer_id": lecturer_id, "type": supervisor_type})
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail={"code": "PROJECT_DUPLICATE", "message": "Project code or supervisor assignment already exists."}) from exc
    return dict(db.execute(text("SELECT id, code, title, status, semester_id FROM projects WHERE id = :id"), {"id": project_id}).mappings().one())


@router.get("/projects/{project_id}")
def get_project_detail(project_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    row = db.execute(
        text(
            "SELECT p.id, p.code, p.title, p.status, p.semester_id, s.code AS semester_code, m.code AS major_code "
            "FROM projects p JOIN semesters s ON s.id = p.semester_id JOIN majors m ON m.id = p.major_id WHERE p.id = :id"
        ),
        {"id": project_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "PROJECT_NOT_FOUND", "message": "Project does not exist."})
    supervisors = db.execute(
        text("SELECT l.id, l.lecturer_code, a.display_name, ps.supervisor_type FROM project_supervisors ps JOIN lecturers l ON l.id = ps.lecturer_id JOIN accounts a ON a.id = l.account_id WHERE ps.project_id = :id ORDER BY ps.supervisor_type"),
        {"id": project_id},
    ).mappings().all()
    group = db.execute(text("SELECT id, code, status FROM groups WHERE project_id = :id"), {"id": project_id}).mappings().one_or_none()
    return {**dict(row), "supervisors": [dict(item) for item in supervisors], "group": dict(group) if group else None}


@router.patch("/groups/{group_id}")
def update_group(group_id: int, payload: GroupUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    if payload.code is None:
        row = db.execute(text("SELECT id, code, status, project_id FROM groups WHERE id = :id"), {"id": group_id}).mappings().one_or_none()
    else:
        try:
            with db.begin():
                row = db.execute(text("UPDATE groups SET code = :code WHERE id = :id RETURNING id, code, status, project_id"), {"id": group_id, "code": payload.code.strip()}).mappings().one_or_none()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail={"code": "GROUP_DUPLICATE", "message": "Group code already exists."}) from exc
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND", "message": "Group does not exist."})
    return dict(row)


@router.get("/groups/{group_id}")
def get_group_detail(group_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    row = db.execute(
        text(
            "SELECT g.id, g.code, g.status, p.id AS project_id, p.code AS project_code, p.title "
            "FROM groups g JOIN projects p ON p.id = g.project_id WHERE g.id = :id"
        ),
        {"id": group_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND", "message": "Group does not exist."})
    members = db.execute(
        text("SELECT st.id AS student_id, st.student_code, a.display_name, gm.membership_role AS role, gm.status FROM group_memberships gm JOIN students st ON st.id = gm.student_id LEFT JOIN accounts a ON a.id = st.account_id WHERE gm.group_id = :id ORDER BY gm.membership_role DESC, st.student_code"),
        {"id": group_id},
    ).mappings().all()
    return {**dict(row), "members": [dict(item) for item in members]}


@router.get("/rounds/{round_id}/invitations")
def list_round_invitations(round_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT ri.round_id, ri.lecturer_id, l.lecturer_code, a.display_name, a.email, "
            "CASE WHEN ri.status = 'DECLINED' THEN 'REJECTED' ELSE ri.status::text END AS status, "
            "ri.response_reason, ri.responded_at, COUNT(la.timeslot_id) FILTER (WHERE la.state = 'AVAILABLE') AS available_slot_count, "
            "MAX(la.load_preference) AS load_preference "
            "FROM round_invitations ri JOIN lecturers l ON l.id = ri.lecturer_id JOIN accounts a ON a.id = l.account_id "
            "LEFT JOIN lecturer_availabilities la ON la.round_id = ri.round_id AND la.lecturer_id = ri.lecturer_id "
            "WHERE ri.round_id = :round_id GROUP BY ri.round_id, ri.lecturer_id, l.lecturer_code, a.display_name, a.email, ri.status, ri.response_reason, ri.responded_at "
            "ORDER BY l.lecturer_code"
        ),
        {"round_id": round_id},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.post("/rounds/{round_id}/invitations/{lecturer_id}/resend")
def resend_invitation(round_id: int, lecturer_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        exists = db.execute(text("SELECT 1 FROM round_invitations WHERE round_id = :round_id AND lecturer_id = :lecturer_id"), {"round_id": round_id, "lecturer_id": lecturer_id}).scalar_one_or_none()
        if exists is None:
            raise HTTPException(status_code=404, detail={"code": "INVITATION_NOT_FOUND", "message": "Invitation does not exist."})
        db.execute(text("UPDATE round_invitations SET status = 'PENDING'::invitation_status, response_reason = NULL, responded_at = NULL WHERE round_id = :round_id AND lecturer_id = :lecturer_id"), {"round_id": round_id, "lecturer_id": lecturer_id})
    return {"round_id": round_id, "lecturer_id": lecturer_id, "status": "PENDING", "resent": True}


@router.get("/rounds/{round_id}/groups")
def list_round_groups(round_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT g.id AS group_id, g.code AS group_code, g.status, p.code AS project_code, p.title, "
            "COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_member_count, "
            "MAX(a.display_name) FILTER (WHERE gm.membership_role = 'LEADER' AND gm.status = 'ACTIVE') AS leader_name, "
            "COUNT(DISTINCT gsp.timeslot_id) FILTER (WHERE gsp.selected) AS selected_slot_count "
            "FROM round_groups rg JOIN groups g ON g.id = rg.group_id JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN group_memberships gm ON gm.group_id = g.id LEFT JOIN students st ON st.id = gm.student_id "
            "LEFT JOIN accounts a ON a.id = st.account_id LEFT JOIN group_slot_preferences gsp ON gsp.round_id = rg.round_id AND gsp.group_id = g.id "
            "WHERE rg.round_id = :round_id GROUP BY g.id, g.code, g.status, p.code, p.title ORDER BY g.code"
        ),
        {"round_id": round_id},
    ).mappings().all()
    status_alias = {"PENDING_D11": "ACTIVE", "ELIGIBLE_D12": "ACTIVE", "D12_CONDITIONAL": "WAITING", "PENDING_D2": "WAITING", "COMPLETED": "COMPLETED", "FAILED": "FAILED", "DROPPED": "DROPPED"}
    return [{**dict(row), "ui_status": status_alias.get(str(row["status"]), row["status"])} for row in rows]


@router.patch("/timeslots/{timeslot_id}")
def update_timeslot(timeslot_id: int, payload: TimeslotUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    values = payload.model_dump(exclude_unset=True)
    if values.get("start_at") and values.get("end_at") and values["end_at"] <= values["start_at"]:
        raise HTTPException(status_code=422, detail={"code": "TIMESLOT_INVALID", "message": "end_at must be after start_at."})
    if not values:
        values = {}
    with db.begin():
        row = db.execute(text("SELECT ts.id, ts.start_at, ts.end_at, r.status FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id JOIN rounds r ON r.id = rd.round_id WHERE ts.id = :id FOR UPDATE"), {"id": timeslot_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "TIMESLOT_NOT_FOUND", "message": "Timeslot does not exist."})
        if str(row["status"]) not in {"DRAFT", "OPEN_REGISTRATION"}:
            raise HTTPException(status_code=409, detail={"code": "TIMESLOT_LOCKED", "message": "Timeslot cannot be changed after scheduling starts."})
        merged_start = values.get("start_at", row["start_at"])
        merged_end = values.get("end_at", row["end_at"])
        if merged_end <= merged_start:
            raise HTTPException(status_code=422, detail={"code": "TIMESLOT_INVALID", "message": "end_at must be after start_at."})
        if values:
            assignments = ", ".join(f"{key} = :{key}" for key in values)
            values["id"] = timeslot_id
            db.execute(text(f"UPDATE timeslots SET {assignments} WHERE id = :id"), values)
    return dict(db.execute(text("SELECT id, round_day_id, start_at, end_at, part, active FROM timeslots WHERE id = :id"), {"id": timeslot_id}).mappings().one())


@router.delete("/timeslots/{timeslot_id}")
def disable_timeslot(timeslot_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        row = db.execute(text("SELECT ts.id, r.status FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id JOIN rounds r ON r.id = rd.round_id WHERE ts.id = :id FOR UPDATE"), {"id": timeslot_id}).mappings().one_or_none()
        if row is not None and str(row["status"]) not in {"DRAFT", "OPEN_REGISTRATION"}:
            raise HTTPException(status_code=409, detail={"code": "TIMESLOT_LOCKED", "message": "Timeslot cannot be changed after scheduling starts."})
        row = db.execute(text("UPDATE timeslots SET active = FALSE WHERE id = :id RETURNING id, active"), {"id": timeslot_id}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "TIMESLOT_NOT_FOUND", "message": "Timeslot does not exist."})
    return dict(row)


@router.get("/semesters/{semester_id}/lecturer-quotas")
def list_lecturer_quotas(semester_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT l.id AS lecturer_id, l.lecturer_code, a.display_name, COALESCE(q.quota, 0) AS quota, "
            "COUNT(sr.session_id) AS used "
            "FROM lecturers l JOIN accounts a ON a.id = l.account_id LEFT JOIN semester_lecturer_quotas q ON q.lecturer_id = l.id AND q.semester_id = :semester_id "
            "LEFT JOIN rounds r ON r.semester_id = :semester_id LEFT JOIN schedule_versions sv ON sv.round_id = r.id AND sv.status IN ('VALID', 'PUBLISHED') "
            "LEFT JOIN session_reviewers sr ON sr.lecturer_id = l.id AND sr.schedule_version_id = sv.id "
            "GROUP BY l.id, l.lecturer_code, a.display_name, q.quota ORDER BY l.lecturer_code"
        ),
        {"semester_id": semester_id},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.put("/semesters/{semester_id}/lecturer-quotas/{lecturer_id}")
def set_lecturer_quota(semester_id: int, lecturer_id: int, payload: QuotaUpdate, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        row = db.execute(
            text(
                "INSERT INTO semester_lecturer_quotas (semester_id, lecturer_id, quota, updated_by) VALUES (:semester_id, :lecturer_id, :quota, :updated_by) "
                "ON CONFLICT (semester_id, lecturer_id) DO UPDATE SET quota = EXCLUDED.quota, updated_by = EXCLUDED.updated_by, updated_at = now() "
                "RETURNING semester_id, lecturer_id, quota, updated_at"
            ),
            {"semester_id": semester_id, "lecturer_id": lecturer_id, "quota": payload.quota, "updated_by": user.account_id},
        ).mappings().one()
    return dict(row)


@router.get("/sessions")
def list_sessions(db: Db, user: User, round_id: int | None = None, version_id: int | None = None, status_filter: str | None = None) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT s.id, s.schedule_version_id AS version_id, sv.round_id, s.group_id, g.code AS group_code, p.code AS project_code, "
            "s.timeslot_id, s.room_id, rm.code AS room_code, s.start_at, s.end_at, s.status, "
            "jsonb_agg(DISTINCT jsonb_build_object('id', l.id, 'code', l.lecturer_code, 'name', a.display_name)) FILTER (WHERE l.id IS NOT NULL) AS reviewers "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN groups g ON g.id = s.group_id JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN rooms rm ON rm.id = s.room_id LEFT JOIN session_reviewers sr ON sr.session_id = s.id LEFT JOIN lecturers l ON l.id = sr.lecturer_id LEFT JOIN accounts a ON a.id = l.account_id "
            "WHERE (CAST(:round_id AS BIGINT) IS NULL OR sv.round_id = CAST(:round_id AS BIGINT)) AND (CAST(:version_id AS BIGINT) IS NULL OR s.schedule_version_id = CAST(:version_id AS BIGINT)) AND (CAST(:status_filter AS TEXT) IS NULL OR s.status::text = CAST(:status_filter AS TEXT)) "
            "GROUP BY s.id, sv.round_id, g.code, p.code, rm.code ORDER BY s.start_at, s.id"
        ),
        {"round_id": round_id, "version_id": version_id, "status_filter": status_filter},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    rows = list_sessions(db, user)
    for row in rows:
        if row["id"] == session_id:
            return row
    raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})


@router.get("/reschedule-requests")
def list_reschedule_requests(db: Db, user: User, status_filter: str | None = None) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT rr.id, rr.session_id, rr.requested_by, aa.display_name AS requester_name, rr.reason, rr.status, rr.reviewed_by, rr.created_at, rr.reviewed_at, "
            "s.group_id, g.code AS group_code, s.start_at, s.end_at, rm.code AS room_code "
            "FROM reschedule_requests rr JOIN sessions s ON s.id = rr.session_id JOIN groups g ON g.id = s.group_id JOIN accounts aa ON aa.id = rr.requested_by LEFT JOIN rooms rm ON rm.id = s.room_id "
            "WHERE (CAST(:status_filter AS TEXT) IS NULL OR rr.status::text = CAST(:status_filter AS TEXT)) ORDER BY rr.created_at DESC"
        ),
        {"status_filter": status_filter},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.get("/reports/group-progress")
def group_progress_report(semester_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "WITH latest_results AS ("
            " SELECT s.group_id, r.type, sr.outcome::text AS outcome, sr.entered_at, sr.verifier_lecturer_id, "
            " ROW_NUMBER() OVER (PARTITION BY s.group_id, r.type ORDER BY sr.entered_at DESC, sr.id DESC) AS rn "
            " FROM session_results sr JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            " JOIN rounds r ON r.id = sv.round_id WHERE r.semester_id = :semester_id AND sv.status IN ('VALID', 'PUBLISHED')"
            "), latest_remediation AS ("
            " SELECT rc.group_id, rc.status::text AS remediation_status, rc.due_at, rc.verifier_lecturer_id, "
            " ROW_NUMBER() OVER (PARTITION BY rc.group_id ORDER BY rc.due_at DESC, rc.id DESC) AS rn "
            " FROM remediation_cases rc JOIN groups rg ON rg.id = rc.group_id JOIN projects rp ON rp.id = rg.project_id WHERE rp.semester_id = :semester_id"
            ") SELECT g.id AS group_id, g.code AS group_code, p.title AS project_name, g.status AS group_status, "
            "MAX(lr.outcome) FILTER (WHERE lr.type = 'REVIEW_1' AND lr.rn = 1) AS review_1, "
            "MAX(lr.outcome) FILTER (WHERE lr.type = 'REVIEW_2' AND lr.rn = 1) AS review_2, "
            "MAX(lr.outcome) FILTER (WHERE lr.type = 'DEFENSE_1_1' AND lr.rn = 1) AS defense_1_1, "
            "MAX(lr.outcome) FILTER (WHERE lr.type = 'DEFENSE_1_2' AND lr.rn = 1) AS defense_1_2, "
            "MAX(lr.outcome) FILTER (WHERE lr.type = 'DEFENSE_2' AND lr.rn = 1) AS defense_2, "
            "MAX(lr.verifier_lecturer_id) FILTER (WHERE lr.type = 'DEFENSE_1_1' AND lr.rn = 1) AS result_verifier_lecturer_id, "
            "MAX(lm.remediation_status) FILTER (WHERE lm.rn = 1) AS remediation_status, "
            "MAX(lm.due_at) FILTER (WHERE lm.rn = 1) AS remediation_due_at, "
            "MAX(lm.verifier_lecturer_id) FILTER (WHERE lm.rn = 1) AS remediation_verifier_lecturer_id "
            "FROM groups g JOIN projects p ON p.id = g.project_id LEFT JOIN latest_results lr ON lr.group_id = g.id "
            "LEFT JOIN latest_remediation lm ON lm.group_id = g.id WHERE p.semester_id = :semester_id "
            "GROUP BY g.id, g.code, p.title, g.status ORDER BY g.code"
        ),
        {"semester_id": semester_id},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.get("/results")
def list_results(db: Db, user: User, round_id: int | None = None) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT sr.id, sr.session_id, s.group_id, g.code AS group_code, r.type AS round_type, sr.outcome, sr.note, sr.entered_at, sr.verify_status, sr.remediation_due_at, sr.verifier_lecturer_id "
            "FROM session_results sr JOIN sessions s ON s.id = sr.session_id JOIN groups g ON g.id = s.group_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id WHERE (CAST(:round_id AS BIGINT) IS NULL OR r.id = CAST(:round_id AS BIGINT)) ORDER BY sr.entered_at DESC"
        ),
        {"round_id": round_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def _normalise_header(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").strip().lower())


def _workbook_rows(upload: UploadFile) -> dict[str, list[dict[str, Any]]]:
    try:
        workbook = load_workbook(upload.file, read_only=True, data_only=True)
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"code": "IMPORT_INVALID_FILE", "message": "Only a readable .xlsx file is supported."}) from exc
    result: dict[str, list[dict[str, Any]]] = {}
    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [_normalise_header(item) for item in rows[0]]
        result[_normalise_header(sheet.title)] = [
            {headers[index]: row[index] for index in range(min(len(headers), len(row))) if headers[index]}
            for row in rows[1:] if any(value is not None for value in row)
        ]
    return result


@router.post("/projects/import", status_code=status.HTTP_201_CREATED)
async def import_projects(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    sheets = _workbook_rows(file)
    rows = sheets.get("projects") or next(iter(sheets.values()), [])
    created = 0
    errors: list[dict[str, Any]] = []
    with db.begin():
        for index, row in enumerate(rows, start=2):
            code = str(row.get("code") or row.get("projectcode") or "").strip()
            title = str(row.get("title") or row.get("project") or row.get("name") or code).strip()
            semester_code = str(row.get("semestercode") or row.get("semester") or "").strip()
            major_code = str(row.get("majorcode") or row.get("major") or "").strip()
            if not code or not semester_code or not major_code:
                errors.append({"row": index, "code": "REQUIRED_FIELD_MISSING"})
                continue
            semester_id = db.execute(text("SELECT id FROM semesters WHERE code = :code"), {"code": semester_code}).scalar_one_or_none()
            major_id = db.execute(text("SELECT id FROM majors WHERE code = :code"), {"code": major_code}).scalar_one_or_none()
            if semester_id is None or major_id is None:
                errors.append({"row": index, "code": "SEMESTER_OR_MAJOR_NOT_FOUND"})
                continue
            try:
                with db.begin_nested():
                    db.execute(text("INSERT INTO projects (semester_id, major_id, code, title) VALUES (:semester_id, :major_id, :code, :title)"), {"semester_id": semester_id, "major_id": major_id, "code": code, "title": title})
                created += 1
            except Exception:
                errors.append({"row": index, "code": "PROJECT_DUPLICATE_OR_INVALID"})
    return {"created": created, "skipped": len(errors), "errors": errors}


@router.post("/groups/import", status_code=status.HTTP_201_CREATED)
async def import_groups(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    sheets = _workbook_rows(file)
    rows = sheets.get("groups") or next(iter(sheets.values()), [])
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        project = str(row.get("projectcode") or row.get("project") or "").strip()
        group = str(row.get("groupcode") or row.get("group") or row.get("code") or "").strip()
        semester = str(row.get("semestercode") or row.get("semester") or "").strip()
        if project and group:
            grouped.setdefault((project, group, semester), []).append(row)
    created = 0
    errors: list[dict[str, Any]] = []
    with db.begin():
        for (project_code, group_code, semester_code), members in grouped.items():
            project_query = "SELECT p.id FROM projects p JOIN semesters s ON s.id = p.semester_id WHERE p.code = :code"
            project_params: dict[str, Any] = {"code": project_code}
            if semester_code:
                project_query += " AND s.code = :semester_code"
                project_params["semester_code"] = semester_code
            project_ids = db.execute(text(project_query), project_params).scalars().all()
            project_id = project_ids[0] if len(project_ids) == 1 else None
            if project_id is None:
                errors.append({"group_code": group_code, "code": "PROJECT_NOT_FOUND_OR_AMBIGUOUS"})
                continue
            try:
                with db.begin_nested():
                    group_id = db.execute(text("INSERT INTO groups (project_id, code) VALUES (:project_id, :code) RETURNING id"), {"project_id": project_id, "code": group_code}).scalar_one()
                    leader_count = 0
                    for member in members:
                        student_code = str(member.get("studentcode") or member.get("student") or member.get("studentid") or "").strip()
                        if not student_code:
                            continue
                        student_id = db.execute(text("SELECT id FROM students WHERE student_code = :code"), {"code": student_code}).scalar_one_or_none()
                        if student_id is None:
                            raise ValueError(f"Student {student_code} not found")
                        role = "LEADER" if str(member.get("role") or "MEMBER").upper() == "LEADER" else "MEMBER"
                        leader_count += role == "LEADER"
                        db.execute(text("INSERT INTO group_memberships (group_id, student_id, membership_role) VALUES (:group_id, :student_id, CAST(:role AS membership_role))"), {"group_id": group_id, "student_id": student_id, "role": role})
                    if leader_count != 1:
                        raise ValueError("Exactly one leader is required")
                created += 1
            except Exception:
                errors.append({"group_code": group_code, "code": "GROUP_INVALID", "message": "Invalid group row; verify project, students and exactly one leader."})
    return {"created": created, "skipped": len(errors), "errors": errors}


def _xlsx_response(workbook: Workbook, filename: str) -> StreamingResponse:
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/exports/round/{round_id}.xlsx")
def export_round(round_id: int, db: Db, user: User) -> StreamingResponse:
    _require(user, "ADMIN", "MANAGER")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Schedule"
    sheet.append(["Session", "Group", "Round", "Start", "End", "Room", "Status"])
    rows = db.execute(text("SELECT s.id, g.code AS group_code, r.type, s.start_at, s.end_at, rm.code AS room_code, s.status FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id LEFT JOIN rooms rm ON rm.id = s.room_id WHERE r.id = :round_id AND sv.activated_at IS NOT NULL AND sv.status IN ('VALID', 'PUBLISHED') ORDER BY s.start_at"), {"round_id": round_id}).mappings().all()
    for row in rows:
        sheet.append([row[key] for key in ("id", "group_code", "type", "start_at", "end_at", "room_code", "status")])
    return _xlsx_response(workbook, f"round-{round_id}.xlsx")


@router.get("/exports/semester/{semester_id}/schedule.xlsx")
def export_semester_schedule(semester_id: int, db: Db, user: User) -> StreamingResponse:
    _require(user, "ADMIN", "MANAGER")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Semester Schedule"
    sheet.append(["Session", "Group", "Round", "Start", "End", "Room", "Status"])
    rows = db.execute(text("SELECT s.id, g.code AS group_code, r.type, s.start_at, s.end_at, rm.code AS room_code, s.status FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id LEFT JOIN rooms rm ON rm.id = s.room_id WHERE r.semester_id = :semester_id AND sv.activated_at IS NOT NULL AND sv.status IN ('VALID', 'PUBLISHED') ORDER BY s.start_at"), {"semester_id": semester_id}).mappings().all()
    for row in rows:
        sheet.append([row[key] for key in ("id", "group_code", "type", "start_at", "end_at", "room_code", "status")])
    return _xlsx_response(workbook, f"semester-{semester_id}-schedule.xlsx")


@router.get("/exports/semester/{semester_id}/results.xlsx")
def export_semester_results(semester_id: int, db: Db, user: User) -> StreamingResponse:
    _require(user, "ADMIN", "MANAGER")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Results"
    sheet.append(["Group", "Round", "Outcome", "Entered At", "Verify Status"])
    rows = db.execute(text("SELECT g.code AS group_code, r.type, sr.outcome, sr.entered_at, sr.verify_status FROM session_results sr JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id WHERE r.semester_id = :semester_id AND sv.activated_at IS NOT NULL AND sv.status IN ('VALID', 'PUBLISHED') ORDER BY sr.entered_at"), {"semester_id": semester_id}).mappings().all()
    for row in rows:
        sheet.append([row[key] for key in ("group_code", "type", "outcome", "entered_at", "verify_status")])
    return _xlsx_response(workbook, f"semester-{semester_id}-results.xlsx")
