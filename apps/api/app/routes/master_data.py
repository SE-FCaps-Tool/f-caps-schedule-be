from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal, Self

from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api_contract import external_id, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.config import Settings, get_settings
from app.database import get_db
from app.domain.availability import invitation_response
from app.domain.enums import RoundStatus, SystemRole
from app.domain.errors import DomainError
from app.domain.master_data import (
    normalize_code,
    validate_conflict_declaration,
    validate_group_members,
    validate_project_supervisors,
)
from app.domain.registration_phase import RegistrationPhase, resolve_registration_phase
from app.domain.round_setup import validate_round_configuration
from app.domain.seed import seed_fixture_v1
from app.domain.status_compat import project_from_legacy
from app.domain.transitions import transition_round
from app.response_models import (
    AccountResponse,
    AccountRoleResponse,
    ActionResponse,
    AuditResponse,
    AvailabilityWriteResponse,
    ConflictResponse,
    DropoutResponse,
    GroupMutationResponse,
    GroupResponse,
    InvitationActionResponse,
    InvitationCreateResponse,
    LeaderChangeResponse,
    LecturerResponse,
    MajorResponse,
    MyAvailabilityResponse,
    MyInvitationResponse,
    MyRoundResponse,
    ProjectMutationResponse,
    ProjectResponse,
    RegistrationResponse,
    RoomResponse,
    RoundDayCreateResponse,
    RoundResourceResponse,
    RoundResponse,
    SeedFixtureResponse,
    SemesterResponse,
    StudentResponse,
)
from app.services.access import (
    is_active_group_leader,
    lecturer_id_for_account,
    student_id_for_account,
)
from app.services.seed_loader import load_seed_fixture
from app.services.semester_queries import (
    SEMESTER_LIFECYCLE_LOCK_KEY,
    academic_year_for_start,
    ensure_round_semester_writable,
    ensure_semester_writable,
    semester_or_404,
    semester_rows,
)

router = APIRouter(prefix="/api/v1", tags=["management"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def registration_phase_for_round(db: Session, round_id: int) -> tuple[dict[str, object], RegistrationPhase]:
    row = db.execute(
        text(
            "SELECT status::text AS status, registration_deadline, group_preference_deadline, "
            "group_selection_mode, lecturer_registration_closed_at "
            "FROM rounds WHERE id = :round_id"
        ),
        {"round_id": round_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    phase = resolve_registration_phase(
        round_status=row["status"],
        registration_deadline=row["registration_deadline"],
        group_preference_deadline=row["group_preference_deadline"],
        lecturer_registration_closed_at=row["lecturer_registration_closed_at"],
        now=datetime.now(UTC),
    )
    return dict(row), phase


def require_registration_phase(db: Session, round_id: int, expected: RegistrationPhase) -> dict[str, object]:
    row, actual = registration_phase_for_round(db, round_id)
    if actual is not expected:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "REGISTRATION_PHASE_INVALID",
                "message": f"This action requires the {expected.value} registration phase; current phase is {actual.value}.",
            },
        )
    return row
SettingsDep = Annotated[Settings, Depends(get_settings)]
password_hasher = PasswordHasher()


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text("SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)"),
        {"role": user.role},
    ).scalar_one_or_none()


class SemesterCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=160)
    note: str | None = Field(default=None, max_length=1000)
    start_date: date
    end_date: date
    status: Literal["PLANNING", "ACTIVE"] = "ACTIVE"

    @field_validator("code")
    @classmethod
    def normalize_semester_code(cls, value: str) -> str:
        return normalize_code(value)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return value.strip() if value is not None and value.strip() else None


class SemesterTransitionPayload(BaseModel):
    target_status: Literal["PLANNING", "ACTIVE", "CLOSED", "ARCHIVED"]
    reason: str = Field(min_length=1, max_length=1000)


class RoundCreate(BaseModel):
    semester_id: int = Field(gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    type: str
    reviewer_count: int = Field(gt=0)
    start_date: date | None = None
    end_date: date | None = None
    result_owner_mode: bool = False
    group_selection_mode: bool = False
    group_preference_deadline: datetime | None = None
    session_duration_minutes: int = Field(gt=0, le=480)
    registration_deadline: datetime | None = None
    h12_sessions_per_part: int = Field(default=4, gt=0)
    h12_sessions_per_day: int = Field(default=8, gt=0)
    h12_semester_quota: int | None = Field(default=None, gt=0)
    max_groups_per_timeslot: int | None = Field(default=None, gt=0)
    max_minutes_per_part: int | None = Field(default=None, gt=0)
    max_minutes_per_day: int | None = Field(default=None, gt=0)
    soft_weights: dict[str, int] = Field(default_factory=dict)
    room_types: list[Literal["NORMAL", "SEMINAR", "LAB"]] = Field(min_length=1)

    @field_validator("soft_weights")
    @classmethod
    def validate_soft_weights(cls, value: dict[str, int]) -> dict[str, int]:
        allowed = {f"S{index}" for index in range(1, 10)}
        if set(value) - allowed or any(weight < 0 for weight in value.values()):
            raise ValueError("soft_weights must contain non-negative S1-S9 values")
        return value

    @model_validator(mode="after")
    def validate_registration_deadlines(self) -> Self:
        if self.registration_deadline is not None and self.registration_deadline.tzinfo is None:
            raise ValueError("registration_deadline must include a timezone offset")
        if self.group_preference_deadline is not None and self.group_preference_deadline.tzinfo is None:
            raise ValueError("group_preference_deadline must include a timezone offset")
        if self.group_selection_mode:
            if self.registration_deadline is None or self.group_preference_deadline is None:
                raise ValueError("both registration deadlines are required when group_selection_mode is enabled")
            if self.group_preference_deadline <= self.registration_deadline:
                raise ValueError("group_preference_deadline must be after registration_deadline")
        return self


class RoundTransitionPayload(BaseModel):
    target_status: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)


class RoundResources(BaseModel):
    model_config = ConfigDict(extra="allow")
    group_ids: list[int] = Field(min_length=1)
    timeslot_ids: list[int] = Field(min_length=1)
    room_types: list[Literal["NORMAL", "SEMINAR", "LAB"]] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_room_selection(self) -> "RoundResources":
        if not self.room_types and not (self.model_extra or {}).get("room_ids"):
            raise ValueError("room_types must contain at least one allowed type")
        return self


class SlotCreate(BaseModel):
    start_at: datetime
    end_at: datetime


class RoundDayCreate(BaseModel):
    day_date: date
    slots: list[SlotCreate] = Field(min_length=1)


class AvailabilitySubmit(BaseModel):
    selected_timeslot_ids: list[int] = Field(default_factory=list)
    load_preference: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"


class InvitationCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    lecturer_ids: list[int] = Field(min_length=1, alias="lecturerIds")


class InvitationResponsePayload(BaseModel):
    response: Literal["ACCEPTED", "DECLINED", "REJECTED"]
    reason: str | None = None


class ConflictCreate(BaseModel):
    project_id: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=500)


class LecturerCreate(BaseModel):
    lecturer_code: str = Field(min_length=1, max_length=32)
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=12, max_length=256)


class AccountCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=12, max_length=256)
    role: Literal["ADMIN", "MANAGER", "LECTURER", "STUDENT"]


class AccountStatusPayload(BaseModel):
    status: Literal["ACTIVE", "INACTIVE"]
    reason: str = Field(min_length=1, max_length=1000)


class AccountRolePayload(BaseModel):
    role: Literal["ADMIN", "MANAGER", "LECTURER", "STUDENT"]
    reason: str = Field(min_length=1, max_length=1000)


class UnlockPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class RoomCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=160)
    capacity: int = Field(gt=0, le=500)
    room_type: Literal["NORMAL", "SEMINAR", "LAB"] = "NORMAL"


class ProjectCreate(BaseModel):
    semester_id: int = Field(gt=0)
    major_id: int = Field(gt=0)
    code: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    supervisors: list[str] = Field(min_length=1, max_length=2)


class MemberPayload(BaseModel):
    student_code: str = Field(min_length=1, max_length=32, description="Mã sinh viên đã tồn tại trong hệ thống.")
    role: Literal["MEMBER", "LEADER"] = Field(
        default="MEMBER",
        description="Vai trò trong nhóm; mỗi nhóm phải có đúng một LEADER.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {"student_code": "SE001", "role": "LEADER"}
        }
    }


class GroupCreate(BaseModel):
    project_id: int | None = Field(
        default=None, gt=0, description="ID project mà nhóm thuộc về. Có thể để trống và gán project sau."
    )
    code: str = Field(min_length=1, max_length=64, description="Mã nhóm, ví dụ G001.")
    members: list[MemberPayload] = Field(
        min_length=4,
        max_length=5,
        description="Danh sách 4–5 sinh viên; phải có đúng một LEADER.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": 12,
                "code": "G001",
                "members": [
                    {"student_code": "SE001", "role": "LEADER"},
                    {"student_code": "SE002", "role": "MEMBER"},
                    {"student_code": "SE003", "role": "MEMBER"},
                    {"student_code": "SE004", "role": "MEMBER"},
                ],
            }
        }
    }


class DropoutPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class LeaderPayload(BaseModel):
    student_id: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=1000)


@router.get("/semesters", response_model=list[SemesterResponse])
def list_semesters(
    db: Db,
    user: User,
    search: str | None = None,
    status_filter: Literal["PLANNING", "ACTIVE", "CLOSED", "ARCHIVED"] | None = Query(default=None, alias="status"),
    academic_year: str | None = None,
) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    return semester_rows(
        db,
        search=search,
        status=status_filter,
        academic_year=academic_year,
    )


@router.get("/semesters/{semester_id}", response_model=SemesterResponse)
def get_semester(semester_id: int, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    return semester_or_404(db, semester_id)


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(db: Db, user: User) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT a.id, a.email, a.display_name, a.status, a.created_at, "
            "COALESCE(MIN(ar.role::text), '') AS role "
            "FROM accounts a "
            "LEFT JOIN account_roles ar ON ar.account_id = a.id "
            "GROUP BY a.id ORDER BY a.email"
        )
    ).mappings().all()
    return [dict(row) for row in rows]


@router.post("/accounts", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
def create_account(payload: AccountCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    try:
        with db.begin():
            account_id = db.execute(text("INSERT INTO accounts (email, display_name, password_hash) VALUES (:email, :display_name, :password_hash) RETURNING id"), {"email": payload.email.strip().lower(), "display_name": payload.display_name.strip(), "password_hash": password_hasher.hash(payload.password)}).scalar_one()
            db.execute(text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, CAST(:role AS system_role))"), {"account_id": account_id, "role": payload.role})
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'ACCOUNT_CREATED', 'account', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(account_id), "after_json": _json({"email": payload.email.strip().lower(), "role": payload.role})})
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail={"code": "ACCOUNT_DUPLICATE", "message": "Email already exists."}) from exc
    return {"id": account_id, "email": payload.email.strip().lower(), "display_name": payload.display_name.strip(), "role": payload.role, "status": "ACTIVE"}


@router.patch("/accounts/{account_id}/status", response_model=ActionResponse, response_model_exclude_none=True)
def update_account_status(account_id: int, payload: AccountStatusPayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    require_change_reason = payload.reason.strip()
    with db.begin():
        row = db.execute(text("SELECT status FROM accounts WHERE id = :id FOR UPDATE"), {"id": account_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "ACCOUNT_NOT_FOUND", "message": "Account does not exist."})
        db.execute(text("UPDATE accounts SET status = CAST(:status AS account_status) WHERE id = :id"), {"status": payload.status, "id": account_id})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'ACCOUNT_STATUS_CHANGED', 'account', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(account_id), "reason": require_change_reason, "before_json": _json({"status": row["status"]}), "after_json": _json({"status": payload.status})})
    return {"id": account_id, "status": payload.status}


@router.post("/accounts/{account_id}/roles", response_model=AccountRoleResponse, response_model_exclude_none=True)
def add_account_role(account_id: int, payload: AccountRolePayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    with db.begin():
        if db.execute(text("SELECT 1 FROM accounts WHERE id = :id"), {"id": account_id}).scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail={"code": "ACCOUNT_NOT_FOUND", "message": "Account does not exist."})
        db.execute(text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, CAST(:role AS system_role)) ON CONFLICT DO NOTHING"), {"account_id": account_id, "role": payload.role})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'ACCOUNT_ROLE_ADDED', 'account', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(account_id), "reason": payload.reason.strip(), "after_json": _json({"role": payload.role})})
    return {"id": account_id, "role": payload.role}


@router.delete("/accounts/{account_id}/roles/{role}", response_model=AccountRoleResponse, response_model_exclude_none=True)
def remove_account_role(account_id: int, role: str, reason: str, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    normalized_role = role.upper()
    if normalized_role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"} or not reason.strip():
        raise HTTPException(status_code=422, detail={"code": "ACCOUNT_ROLE_INVALID", "message": "A valid role and reason are required."})
    with db.begin():
        if db.execute(text("SELECT 1 FROM accounts WHERE id = :id"), {"id": account_id}).scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail={"code": "ACCOUNT_NOT_FOUND", "message": "Account does not exist."})
        role_count = db.execute(text("SELECT COUNT(*) FROM account_roles WHERE account_id = :id"), {"id": account_id}).scalar_one()
        removed = db.execute(text("DELETE FROM account_roles WHERE account_id = :id AND role = CAST(:role AS system_role) RETURNING account_id"), {"id": account_id, "role": normalized_role}).scalar_one_or_none()
        if removed is None:
            raise HTTPException(status_code=404, detail={"code": "ACCOUNT_ROLE_NOT_FOUND", "message": "Account role does not exist."})
        if role_count <= 1:
            raise HTTPException(status_code=422, detail={"code": "ACCOUNT_ROLE_LAST", "message": "An account must retain at least one system role."})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'ACCOUNT_ROLE_REMOVED', 'account', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(account_id), "reason": reason.strip(), "after_json": _json({"role": normalized_role})})
    return {"id": account_id, "role": normalized_role, "status": "REMOVED"}


@router.get("/audit", response_model=list[AuditResponse])
def list_audit_events(
    db: Db,
    user: User,
    actor_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT id, actor_id, action, entity_type, entity_id, reason, before_json, after_json, occurred_at "
            "FROM audit_events WHERE (CAST(:actor_id AS BIGINT) IS NULL OR actor_id = CAST(:actor_id AS BIGINT)) "
            "AND (CAST(:action AS TEXT) IS NULL OR action = CAST(:action AS TEXT)) "
            "AND (CAST(:entity_type AS TEXT) IS NULL OR entity_type = CAST(:entity_type AS TEXT)) "
            "ORDER BY occurred_at DESC, id DESC LIMIT :limit"
        ),
        {"actor_id": actor_id, "action": action, "entity_type": entity_type, "limit": min(max(limit, 1), 500)},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.get("/majors", response_model=list[MajorResponse])
def list_majors(db: Db, user: User) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(text("SELECT id, code, name FROM majors ORDER BY code")).mappings()
    return [dict(row) for row in rows]


@router.get("/students", response_model=list[StudentResponse])
def list_students(db: Db, user: User) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT st.id, st.student_code, a.display_name, a.email "
            "FROM students st LEFT JOIN accounts a ON a.id = st.account_id "
            "ORDER BY st.student_code"
        )
    ).mappings()
    return [dict(row) for row in rows]


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Db, user: User, semester_id: int | None = None) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT p.id, p.code, p.title, p.status, p.semester_id, sem.code AS semester_code, "
             "m.code AS major_code, COUNT(ps.lecturer_id) AS supervisor_count, "
             "COALESCE(jsonb_agg(jsonb_build_object('lecturer_code', sl.lecturer_code, 'display_name', sa.display_name, 'type', ps.supervisor_type)) FILTER (WHERE sl.id IS NOT NULL), '[]'::jsonb) AS supervisors "
             "FROM projects p JOIN semesters sem ON sem.id = p.semester_id "
             "JOIN majors m ON m.id = p.major_id LEFT JOIN project_supervisors ps ON ps.project_id = p.id "
             "LEFT JOIN lecturers sl ON sl.id = ps.lecturer_id LEFT JOIN accounts sa ON sa.id = sl.account_id "
             "WHERE (CAST(:semester_id AS BIGINT) IS NULL OR p.semester_id = CAST(:semester_id AS BIGINT)) "
             "GROUP BY p.id, sem.code, m.code ORDER BY p.id DESC"
        )
        , {"semester_id": semester_id}).mappings().all()
    return [dict(row) for row in rows]


@router.get("/semesters/{semester_id}/projects", tags=["target-groups-projects"])
def list_semester_projects(
    semester_id: int,
    db: Db,
    user: User,
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    supervisor_id: str | int | None = Query(default=None, alias="supervisorId"),
    has_group: bool | None = Query(default=None, alias="hasGroup"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=200),
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    semester_or_404(db, semester_id)
    supervisor_db_id = parse_external_id(supervisor_id, prefix="lec") if supervisor_id is not None else None
    offset = (page - 1) * page_size
    rows = db.execute(
        text(
            "SELECT p.id, p.code, p.title, p.status::text AS status, g.id AS group_id, g.code AS group_code, "
            "(SELECT jsonb_build_object('id', l.id, 'code', l.lecturer_code, 'fullName', a.display_name) "
            " FROM project_supervisors ps JOIN lecturers l ON l.id = ps.lecturer_id "
            " JOIN accounts a ON a.id = l.account_id "
            " WHERE ps.project_id = p.id AND ps.supervisor_type = 'MAIN' LIMIT 1) AS main_supervisor, "
            "(SELECT jsonb_build_object('id', l.id, 'code', l.lecturer_code, 'fullName', a.display_name) "
            " FROM project_supervisors ps JOIN lecturers l ON l.id = ps.lecturer_id "
            " JOIN accounts a ON a.id = l.account_id "
            " WHERE ps.project_id = p.id AND ps.supervisor_type = 'CO' LIMIT 1) AS co_supervisor, "
            "COUNT(*) OVER() AS total_count "
            "FROM projects p LEFT JOIN groups g ON g.project_id = p.id "
            "WHERE p.semester_id = :semester_id "
            "AND (CAST(:search AS text) IS NULL OR p.code ILIKE '%' || CAST(:search AS text) || '%' OR p.title ILIKE '%' || CAST(:search AS text) || '%') "
            "AND (CAST(:status AS text) IS NULL OR p.status::text = CAST(:status AS text)) "
            "AND (CAST(:has_group AS boolean) IS NULL OR (g.id IS NOT NULL) = CAST(:has_group AS boolean)) "
            "AND (CAST(:supervisor_id AS BIGINT) IS NULL OR EXISTS (SELECT 1 FROM project_supervisors ps WHERE ps.project_id = p.id AND ps.lecturer_id = CAST(:supervisor_id AS BIGINT))) "
            "GROUP BY p.id, g.id, g.code ORDER BY p.code LIMIT :limit OFFSET :offset"
        ),
        {
            "semester_id": semester_id, "search": search, "status": status_filter,
            "has_group": has_group, "supervisor_id": supervisor_db_id,
            "limit": page_size, "offset": offset,
        },
    ).mappings().all()
    total = rows[0]["total_count"] if rows else 0
    items = [
        {
            "id": external_id(row["id"], "prj"),
            "code": row["code"],
            "name": row["title"],
            "nameVi": row["title"],
            "status": project_from_legacy(row["status"], has_group=row["group_id"] is not None).value,
            "mainSupervisor": (
                {**dict(row["main_supervisor"]), "id": external_id(row["main_supervisor"]["id"], "lec")}
                if row["main_supervisor"] is not None else None
            ),
            "coSupervisor": (
                {**dict(row["co_supervisor"]), "id": external_id(row["co_supervisor"]["id"], "lec")}
                if row["co_supervisor"] is not None else None
            ),
            "group": (
                {"id": external_id(row["group_id"], "grp"), "code": row["group_code"]}
                if row["group_id"] is not None else None
            ),
        }
        for row in rows
    ]
    return success_payload(items, meta={"page": page, "pageSize": page_size, "total": total})


@router.get("/lecturers", response_model=list[LecturerResponse])
def list_lecturers(db: Db, user: User) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT l.id, l.lecturer_code, l.account_id, a.email, a.display_name, "
            "a.status AS account_status, "
            "COALESCE("
            "jsonb_agg("
            "jsonb_build_object('project_id', cd.project_id, 'reason', cd.reason) "
            "ORDER BY cd.project_id"
            ") FILTER (WHERE cd.id IS NOT NULL), '[]'::jsonb"
            ") AS conflicts "
            "FROM lecturers l "
            "JOIN accounts a ON a.id = l.account_id "
            "LEFT JOIN conflict_declarations cd ON cd.lecturer_id = l.id "
            "GROUP BY l.id, l.lecturer_code, l.account_id, a.email, a.display_name, a.status "
            "ORDER BY l.lecturer_code"
        )
    ).mappings()
    return [dict(row) for row in rows]


@router.post("/lecturers", status_code=status.HTTP_201_CREATED, response_model=LecturerResponse)
def create_lecturer(payload: LecturerCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        code = normalize_code(payload.lecturer_code)
        with db.begin():
            account_id = db.execute(
                text(
                    "INSERT INTO accounts (email, display_name, password_hash) "
                    "VALUES (:email, :display_name, :password_hash) RETURNING id"
                ),
                {"email": payload.email.strip().lower(), "display_name": payload.display_name.strip(), "password_hash": password_hasher.hash(payload.password)},
            ).scalar_one()
            db.execute(
                text("INSERT INTO account_roles (account_id, role) VALUES (:account_id, 'LECTURER')"),
                {"account_id": account_id},
            )
            row = db.execute(
                text(
                    "INSERT INTO lecturers (account_id, lecturer_code) VALUES (:account_id, :code) "
                    "RETURNING id, lecturer_code, account_id"
                ),
                {"account_id": account_id, "code": code},
            ).mappings().one()
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'MASTER_DATA_CREATED', 'lecturer', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {"actor_id": _actor_id(db, user), "entity_id": str(row["id"]), "after_json": _json({"lecturer_code": code, "account_id": account_id})},
            )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "DATA_DUPLICATE", "message": "Lecturer email or code already exists."},
        ) from exc
    return dict(row)


@router.get("/rooms", response_model=list[RoomResponse])
def list_rooms(db: Db, user: User) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text("SELECT id, code, name, capacity, active, room_type FROM rooms ORDER BY code")
    ).mappings()
    return [dict(row) for row in rows]


@router.post("/rooms", status_code=status.HTTP_201_CREATED, response_model=RoomResponse)
def create_room(payload: RoomCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            row = db.execute(
                text(
                    "INSERT INTO rooms (code, name, capacity, room_type) "
                    "VALUES (:code, :name, :capacity, :room_type) "
                    "RETURNING id, code, name, capacity, active, room_type"
                ),
                {
                    "code": normalize_code(payload.code),
                    "name": payload.name.strip(),
                    "capacity": payload.capacity,
                    "room_type": payload.room_type,
                },
            ).mappings().one()
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'MASTER_DATA_CREATED', 'room', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {"actor_id": _actor_id(db, user), "entity_id": str(row["id"]), "after_json": _json({"code": row["code"], "capacity": row["capacity"]})},
            )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "DATA_DUPLICATE", "message": "Room code already exists."},
        ) from exc
    return dict(row)


@router.get("/groups", response_model=list[GroupResponse])
def list_groups(db: Db, user: User, semester_id: int | None = None) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            """
            SELECT g.id, g.code, g.status, g.project_id, p.code AS project_code, p.title
                   , COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_member_count
                   , COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leader_count
                   , MAX(a.display_name) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leader_name
             FROM groups g LEFT JOIN projects p ON p.id = g.project_id
             LEFT JOIN group_memberships gm ON gm.group_id = g.id
             LEFT JOIN students st ON st.id = gm.student_id LEFT JOIN accounts a ON a.id = st.account_id
             WHERE (CAST(:semester_id AS BIGINT) IS NULL OR p.semester_id = CAST(:semester_id AS BIGINT))
             GROUP BY g.id, g.code, g.status, g.project_id, p.code, p.title
            ORDER BY g.code
            """
        )
        , {"semester_id": semester_id}).mappings()
    status_alias = {"PENDING_D11": "ACTIVE", "ELIGIBLE_D12": "ACTIVE", "D12_CONDITIONAL": "WAITING", "PENDING_D2": "WAITING", "COMPLETED": "COMPLETED", "FAILED": "FAILED", "DROPPED": "DROPPED"}
    return [{**dict(row), "ui_status": status_alias.get(str(row["status"]), row["status"])} for row in rows]


@router.post("/projects", status_code=status.HTTP_201_CREATED, response_model=ProjectMutationResponse)
def create_project(payload: ProjectCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        validate_project_supervisors(payload.supervisors)
        with db.begin():
            ensure_semester_writable(db, payload.semester_id)
            lecturer_ids = {}
            for assignment in payload.supervisors:
                lecturer_code = normalize_code(assignment.split(":", maxsplit=1)[0])
                lecturer_id = db.execute(
                    text("SELECT id FROM lecturers WHERE lecturer_code = :code"),
                    {"code": lecturer_code},
                ).scalar_one_or_none()
                if lecturer_id is None:
                    raise DomainError("SUPERVISOR_NOT_FOUND", "Supervisor lecturer code does not exist.")
                lecturer_ids[lecturer_code] = lecturer_id
            project_id = db.execute(
                text(
                    "INSERT INTO projects (semester_id, major_id, code, title) "
                    "VALUES (:semester_id, :major_id, :code, :title) RETURNING id"
                ),
                {
                    "semester_id": payload.semester_id,
                    "major_id": payload.major_id,
                    "code": normalize_code(payload.code),
                    "title": payload.title.strip(),
                },
            ).scalar_one()
            for assignment in payload.supervisors:
                lecturer_code, supervisor_type = assignment.split(":", maxsplit=1)
                db.execute(
                    text(
                        "INSERT INTO project_supervisors (project_id, lecturer_id, supervisor_type) "
                        "VALUES (:project_id, :lecturer_id, :supervisor_type)"
                    ),
                    {
                        "project_id": project_id,
                        "lecturer_id": lecturer_ids[normalize_code(lecturer_code)],
                        "supervisor_type": supervisor_type.strip().upper(),
                    },
                )
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'MASTER_DATA_CREATED', 'project', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {"actor_id": _actor_id(db, user), "entity_id": str(project_id), "after_json": _json({"code": normalize_code(payload.code), "supervisors": payload.supervisors})},
            )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "DATA_INVALID", "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "DATA_DUPLICATE", "message": "Project code already exists in this semester."},
        ) from exc
    return {"id": project_id, "code": normalize_code(payload.code), "title": payload.title.strip()}


@router.post("/groups", status_code=status.HTTP_201_CREATED, response_model=GroupMutationResponse, response_model_exclude_none=True)
def create_group(payload: GroupCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    members = [member.model_dump() for member in payload.members]
    try:
        validate_group_members(members)
        with db.begin():
            if payload.project_id is not None:
                project_exists = db.execute(
                    text("SELECT semester_id FROM projects WHERE id = :project_id FOR UPDATE"), {"project_id": payload.project_id}
                ).scalar_one_or_none()
                if project_exists is None:
                    raise DomainError("PROJECT_NOT_FOUND", "Project does not exist.")
                ensure_semester_writable(db, int(project_exists))
            student_ids = {}
            for member in members:
                student_code = normalize_code(member["student_code"])
                student_id = db.execute(
                    text("SELECT id FROM students WHERE student_code = :student_code"),
                    {"student_code": student_code},
                ).scalar_one_or_none()
                if student_id is None:
                    raise DomainError("STUDENT_NOT_FOUND", "Student code does not exist.")
                student_ids[student_code] = student_id
            group_id = db.execute(
                text("INSERT INTO groups (project_id, code) VALUES (:project_id, :code) RETURNING id"),
                {"project_id": payload.project_id, "code": normalize_code(payload.code)},
            ).scalar_one()
            for member in members:
                db.execute(
                    text(
                        "INSERT INTO group_memberships (group_id, student_id, membership_role) "
                        "VALUES (:group_id, :student_id, :membership_role)"
                    ),
                    {
                        "group_id": group_id,
                        "student_id": student_ids[normalize_code(member["student_code"])],
                        "membership_role": member["role"],
                    },
                )
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'MASTER_DATA_CREATED', 'group', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {"actor_id": _actor_id(db, user), "entity_id": str(group_id), "after_json": _json({"code": normalize_code(payload.code), "member_count": len(members)})},
            )
            member_rows = db.execute(
                text(
                    "SELECT st.id AS student_id, st.student_code, a.display_name, a.email, "
                    "gm.membership_role AS role, gm.status "
                    "FROM group_memberships gm "
                    "JOIN students st ON st.id = gm.student_id "
                    "LEFT JOIN accounts a ON a.id = st.account_id "
                    "WHERE gm.group_id = :group_id "
                    "ORDER BY gm.membership_role DESC, st.student_code"
                ),
                {"group_id": group_id},
            ).mappings().all()
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "DATA_DUPLICATE", "message": "Group or membership already exists."},
        ) from exc
    return {
        "id": group_id,
        "code": normalize_code(payload.code),
        "member_count": len(members),
        "members": [dict(row) for row in member_rows],
    }


@router.post("/groups/{group_id}/members/{student_id}/drop", response_model=DropoutResponse)
def approve_dropout(group_id: int, student_id: int, payload: DropoutPayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        project_semester_id = db.execute(
            text("SELECT p.semester_id FROM groups g JOIN projects p ON p.id = g.project_id WHERE g.id = :group_id FOR UPDATE"),
            {"group_id": group_id},
        ).scalar_one_or_none()
        if project_semester_id is not None:
            ensure_semester_writable(db, int(project_semester_id))
        row = db.execute(text("SELECT id, membership_role, status FROM group_memberships WHERE group_id = :group_id AND student_id = :student_id AND status = 'ACTIVE' FOR UPDATE"), {"group_id": group_id, "student_id": student_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Active membership does not exist."})
        actor_id = _actor_id(db, user)
        db.execute(text("UPDATE group_memberships SET status = 'DROPPED', left_at = now(), reason = :reason, drop_requested_by = :actor_id, drop_approved_by = :actor_id WHERE id = :id"), {"reason": payload.reason.strip(), "actor_id": actor_id, "id": row["id"]})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'DROPOUT_APPROVED', 'group_membership', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(row["id"]), "reason": payload.reason.strip(), "before_json": _json({"status": row["status"], "membership_role": row["membership_role"]}), "after_json": _json({"status": "DROPPED", "left_at": "now"})})
    return {"group_id": group_id, "student_id": student_id, "status": "DROPPED", "warning": "GROUP_BELOW_MINIMUM_MAY_CONTINUE"}


@router.post("/groups/{group_id}/leader", response_model=LeaderChangeResponse)
def change_group_leader(group_id: int, payload: LeaderPayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        project_semester_id = db.execute(
            text("SELECT p.semester_id FROM groups g JOIN projects p ON p.id = g.project_id WHERE g.id = :group_id FOR UPDATE"),
            {"group_id": group_id},
        ).scalar_one_or_none()
        if project_semester_id is not None:
            ensure_semester_writable(db, int(project_semester_id))
        target = db.execute(text("SELECT id, membership_role, status FROM group_memberships WHERE group_id = :group_id AND student_id = :student_id AND status = 'ACTIVE' FOR UPDATE"), {"group_id": group_id, "student_id": payload.student_id}).mappings().one_or_none()
        if target is None:
            raise HTTPException(status_code=404, detail={"code": "LEADER_MEMBER_NOT_FOUND", "message": "The new Leader must be an active group member."})
        db.execute(text("UPDATE group_memberships SET membership_role = 'MEMBER' WHERE group_id = :group_id AND status = 'ACTIVE' AND membership_role = 'LEADER'"), {"group_id": group_id})
        db.execute(text("UPDATE group_memberships SET membership_role = 'LEADER' WHERE id = :id"), {"id": target["id"]})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'LEADER_CHANGED', 'group', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(group_id), "reason": payload.reason.strip(), "before_json": _json({"leader_changed": True}), "after_json": _json({"student_id": payload.student_id})})
    return {"group_id": group_id, "leader_student_id": payload.student_id}


@router.post("/semesters", status_code=status.HTTP_201_CREATED, response_model=SemesterResponse)
def create_semester(
    payload: SemesterCreate, db: Db, user: User, settings: SettingsDep
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    if payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=422,
            detail={"code": "SEMESTER_DATE_INVALID", "message": "end_date must be after start_date."},
        )
    duration_days = (payload.end_date - payload.start_date).days + 1
    if not settings.semester_min_duration_days <= duration_days <= settings.semester_max_duration_days:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "SEMESTER_DURATION_INVALID",
                "message": (
                    "Semester duration must be between "
                    f"{settings.semester_min_duration_days} and "
                    f"{settings.semester_max_duration_days} inclusive days."
                ),
            },
        )
    academic_year = academic_year_for_start(payload.start_date)
    try:
        with db.begin():
            db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": SEMESTER_LIFECYCLE_LOCK_KEY},
            )
            actor_id = _actor_id(db, user)
            row = db.execute(
                text(
                    """
                    INSERT INTO semesters
                        (code, name, note, start_date, end_date, academic_year,
                         status, created_by, updated_by, updated_at)
                    VALUES
                        (:code, :name, :note, :start_date, :end_date, :academic_year,
                         :status, :actor_id, :actor_id, now())
                    RETURNING id, code, name, note, start_date, end_date,
                              academic_year, status, created_at, updated_at,
                              created_by, updated_by
                    """
                ),
                {
                    **payload.model_dump(),
                    "academic_year": academic_year,
                    "status": payload.status,
                    "actor_id": actor_id,
                },
            ).mappings().one()
            db.execute(
                text(
                    """
                    INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json)
                    VALUES (:actor_id, 'SEMESTER_CREATED', 'semester', :entity_id, CAST(:after_json AS JSONB))
                    """
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(row["id"]),
                    "after_json": _json(
                        {
                            **payload.model_dump(mode="json"),
                            "academic_year": academic_year,
                            "status": payload.status,
                        }
                    ),
                },
            )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        constraint = str(getattr(exc, "orig", exc))
        if "uq_active_semester" in constraint:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ACTIVE_SEMESTER_EXISTS",
                    "message": "Only one semester may be ACTIVE.",
                },
            ) from exc
        raise HTTPException(
            status_code=409,
            detail={"code": "DATA_DUPLICATE", "message": "Semester code already exists."},
        ) from exc
    return semester_or_404(db, int(row["id"]))


@router.post("/semesters/{semester_id}/transition", response_model=ActionResponse, response_model_exclude_none=True)
def transition_semester(
    semester_id: int,
    payload: SemesterTransitionPayload,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": SEMESTER_LIFECYCLE_LOCK_KEY},
            )
            row = db.execute(
                text("SELECT id, status FROM semesters WHERE id = :id FOR UPDATE"),
                {"id": semester_id},
            ).mappings().one_or_none()
            if row is None:
                raise DomainError("SEMESTER_NOT_FOUND", "Semester does not exist.")

            current_status = str(row["status"])
            allowed = {
                "PLANNING": {"ACTIVE"},
                "ACTIVE": {"CLOSED"},
                "CLOSED": {"ARCHIVED"},
                "ARCHIVED": set(),
            }
            if payload.target_status not in allowed.get(current_status, set()):
                raise DomainError(
                    "SEMESTER_STATUS_INVALID",
                    f"Invalid semester transition: {current_status} -> {payload.target_status}.",
                )
            actor_id = _actor_id(db, user)
            db.execute(
                text(
                    "UPDATE semesters SET status = CAST(:status AS semester_status), "
                    "updated_by = :actor_id, updated_at = now() WHERE id = :id"
                ),
                {"status": payload.target_status, "id": semester_id, "actor_id": actor_id},
            )
            db.execute(
                text(
                    "INSERT INTO audit_events "
                    "(actor_id, action, entity_type, entity_id, reason, before_json, after_json) "
                    "VALUES (:actor_id, 'SEMESTER_STATUS_CHANGED', 'semester', :entity_id, :reason, "
                    "CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(semester_id),
                    "reason": payload.reason.strip(),
                    "before_json": _json({"status": current_status}),
                    "after_json": _json({"status": payload.target_status}),
                },
            )
    except DomainError as exc:
        raise HTTPException(
            status_code=422 if exc.code != "SEMESTER_NOT_FOUND" else 404,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "ACTIVE_SEMESTER_EXISTS", "message": "Only one semester may be ACTIVE."},
        ) from exc
    return {"id": semester_id, "status": payload.target_status}


@router.post("/semesters/{semester_id}/set-current", response_model=SemesterResponse)
def set_current_semester(semester_id: int, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": SEMESTER_LIFECYCLE_LOCK_KEY},
            )
            locked = db.execute(
                text(
                    "SELECT id, status FROM semesters "
                    "WHERE status = 'ACTIVE' OR id = :target_id "
                    "ORDER BY id FOR UPDATE"
                ),
                {"target_id": semester_id},
            ).mappings().all()
            target = next((row for row in locked if row["id"] == semester_id), None)
            if target is None:
                raise DomainError("SEMESTER_NOT_FOUND", "Semester does not exist.")
            if str(target["status"]) == "ACTIVE":
                return semester_or_404(db, semester_id)
            if str(target["status"]) == "ARCHIVED":
                raise DomainError("SEMESTER_ARCHIVED", "An archived semester is read-only and cannot become current.")

            active = next((row for row in locked if str(row["status"]) == "ACTIVE"), None)
            actor_id = _actor_id(db, user)
            if active is not None:
                db.execute(
                    text(
                        "UPDATE semesters SET status = 'CLOSED', updated_by = :actor_id, "
                        "updated_at = now() WHERE id = :id"
                    ),
                    {"id": active["id"], "actor_id": actor_id},
                )
                db.execute(
                    text(
                        "INSERT INTO audit_events "
                        "(actor_id, action, entity_type, entity_id, before_json, after_json) "
                        "VALUES (:actor_id, 'SEMESTER_SET_CURRENT', 'semester', :entity_id, "
                        "CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
                    ),
                    {
                        "actor_id": actor_id,
                        "entity_id": str(active["id"]),
                        "before_json": _json({"status": str(active["status"])}),
                        "after_json": _json({"status": "CLOSED"}),
                    },
                )
            db.execute(
                text(
                    "UPDATE semesters SET status = 'ACTIVE', updated_by = :actor_id, "
                    "updated_at = now() WHERE id = :id"
                ),
                {"id": semester_id, "actor_id": actor_id},
            )
            db.execute(
                text(
                    "INSERT INTO audit_events "
                    "(actor_id, action, entity_type, entity_id, before_json, after_json) "
                    "VALUES (:actor_id, 'SEMESTER_SET_CURRENT', 'semester', :entity_id, "
                    "CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(semester_id),
                    "before_json": _json({"status": str(target["status"])}),
                    "after_json": _json({"status": "ACTIVE"}),
                },
            )
    except DomainError as exc:
        raise HTTPException(
            status_code=404 if exc.code == "SEMESTER_NOT_FOUND" else 422,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return semester_or_404(db, semester_id)


@router.post("/admin/seed-fixture", status_code=status.HTTP_201_CREATED, response_model=SeedFixtureResponse)
def seed_fixture(db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    try:
        actor_id = _actor_id(db, user)
        db.commit()
        counts = load_seed_fixture(db, seed_fixture_v1(), actor_id=actor_id)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "SEED_INVALID", "message": "Seed fixture could not be applied atomically."},
        ) from exc
    return {"fixture": counts["version"], "counts": counts}


@router.get("/rounds", response_model=list[RoundResponse])
def list_rounds(db: Db, user: User, semester_id: int | None = None) -> list[dict[str, object]]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            """
             SELECT id, semester_id, name, description, type, status, reviewer_count, result_owner_mode, group_selection_mode,
                    session_duration_minutes, start_date, end_date, registration_deadline,
                    group_preference_deadline,
                    h12_sessions_per_part, h12_sessions_per_day, h12_semester_quota,
                    max_groups_per_timeslot, max_minutes_per_part, max_minutes_per_day, soft_weights,
                    COALESCE((SELECT array_agg(rrt.room_type::text ORDER BY rrt.room_type::text)
                              FROM round_room_types rrt WHERE rrt.round_id = rounds.id), ARRAY[]::text[]) AS room_types
             FROM rounds WHERE (CAST(:semester_id AS BIGINT) IS NULL OR semester_id = CAST(:semester_id AS BIGINT)) ORDER BY id DESC
            """
        )
        , {"semester_id": semester_id}).mappings()
    return [dict(row) for row in rows]


@router.post("/rounds", status_code=status.HTTP_201_CREATED, response_model=RoundResponse)
def create_round(
    payload: RoundCreate,
    db: Db,
    user: User,
) -> dict[str, object]:
    return create_round_with_days(payload, db, user)


def create_round_with_days(
    payload: RoundCreate,
    db: Db,
    user: User,
    days: list[RoundDayCreate] | None = None,
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail={"code": "ROUND_DATE_INVALID", "message": "end_date must be after start_date."})
    try:
        validate_round_configuration(
            {
                "type": payload.type,
                "reviewer_count": payload.reviewer_count,
                "result_owner_mode": payload.result_owner_mode,
                "groups": [1],
                "timeslots": [1],
                "rooms": [1],
            }
        )
        with db.begin():
            semester_status = db.execute(
                text("SELECT status FROM semesters WHERE id = :semester_id FOR UPDATE"),
                {"semester_id": payload.semester_id},
            ).scalar_one_or_none()
            if semester_status is None:
                raise DomainError("SEMESTER_NOT_FOUND", "Semester does not exist.")
            if str(semester_status) != "ACTIVE":
                raise DomainError(
                    "SEMESTER_NOT_ACTIVE",
                    "Evaluation Rounds may only be created in an ACTIVE semester.",
                )
            row = db.execute(
                text(
                    """
                    INSERT INTO rounds (
                        semester_id, name, description, type, reviewer_count, result_owner_mode, group_selection_mode,
                         group_preference_deadline,
                         session_duration_minutes, start_date, end_date, registration_deadline,
                         h12_sessions_per_part, h12_sessions_per_day, h12_semester_quota,
                         max_groups_per_timeslot, max_minutes_per_part, max_minutes_per_day, soft_weights, created_by
                    ) VALUES (
                        :semester_id, :name, :description, :type, :reviewer_count, :result_owner_mode, :group_selection_mode,
                         :group_preference_deadline,
                         :session_duration_minutes, :start_date, :end_date, :registration_deadline,
                         :h12_sessions_per_part, :h12_sessions_per_day, :h12_semester_quota,
                         :max_groups_per_timeslot, :max_minutes_per_part, :max_minutes_per_day, CAST(:soft_weights AS JSONB), :created_by
                    )
                    RETURNING id, semester_id, name, description, type, status, reviewer_count, result_owner_mode, group_selection_mode,
                               session_duration_minutes, start_date, end_date, registration_deadline,
                               group_preference_deadline,
                               h12_sessions_per_part, h12_sessions_per_day, h12_semester_quota,
                               max_groups_per_timeslot, max_minutes_per_part, max_minutes_per_day, soft_weights
                    """
                ),
                {**payload.model_dump(), "soft_weights": _json(payload.soft_weights), "created_by": _actor_id(db, user)},
            ).mappings().one()
            for room_type in payload.room_types:
                db.execute(
                    text("INSERT INTO round_room_types (round_id, room_type) VALUES (:round_id, CAST(:room_type AS room_type)) ON CONFLICT DO NOTHING"),
                    {"round_id": row["id"], "room_type": room_type},
                )
            if days:
                for day in days:
                    day_id = db.execute(
                        text("INSERT INTO round_days (round_id, day_date) VALUES (:round_id, :day_date) RETURNING id"),
                        {"round_id": row["id"], "day_date": day.day_date},
                    ).scalar_one()
                    for slot in day.slots:
                        db.execute(
                            text(
                                "INSERT INTO timeslots (round_day_id, start_at, end_at, part) "
                                "VALUES (:round_day_id, :start_at, :end_at, :part)"
                            ),
                            {
                                "round_day_id": day_id,
                                "start_at": slot.start_at,
                                "end_at": slot.end_at,
                                "part": "AM" if slot.start_at.hour < 13 else "PM",
                            },
                        )
            row = {**dict(row), "room_types": list(payload.room_types)}
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'ROUND_CREATED', 'round', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(row["id"]), "after_json": _json(payload.model_dump())})
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "ROUND_SEMESTER_INVALID", "message": "Semester does not exist."},
        ) from exc
    return dict(row)


@router.post("/rounds/{round_id}/transition", response_model=ActionResponse, response_model_exclude_none=True)
def transition_round_status(round_id: int, payload: RoundTransitionPayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            row = db.execute(text("SELECT status, reviewer_count FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_id}).mappings().one_or_none()
            if row is None:
                raise DomainError("ROUND_NOT_FOUND", "Round does not exist.")
            before = RoundStatus(row["status"])
            after = transition_round(before, RoundStatus(payload.target_status))
            if after is RoundStatus.SCHEDULING:
                counts = db.execute(
                    text(
                        "SELECT "
                        "(SELECT COUNT(*) FROM round_groups WHERE round_id = :round_id) AS groups, "
                        "(SELECT COUNT(*) FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = :round_id) AS timeslots, "
                        "(SELECT COUNT(*) FROM round_invitations WHERE round_id = :round_id AND status = 'ACCEPTED') AS accepted_reviewers, "
                        "(SELECT COUNT(DISTINCT lecturer_id) FROM lecturer_availabilities WHERE round_id = :round_id AND state = 'AVAILABLE') AS available_reviewers"
                    ),
                    {"round_id": round_id},
                ).mappings().one()
                reviewer_count = counts["accepted_reviewers"] or counts["available_reviewers"]
                if not counts["groups"] or not counts["timeslots"] or reviewer_count < row["reviewer_count"]:
                    raise DomainError("ROUND_INPUTS_INCOMPLETE", "Round needs groups, timeslots and enough available Reviewers before scheduling.")
            db.execute(
                text(
                    "UPDATE rounds SET status = CAST(:status AS round_status), "
                    "lecturer_registration_closed_at = CASE WHEN :status = 'OPEN_REGISTRATION' "
                    "THEN NULL ELSE lecturer_registration_closed_at END WHERE id = :round_id"
                ),
                {"status": after.value, "round_id": round_id},
            )
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'ROUND_TRANSITION', 'round', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(round_id), "reason": payload.reason, "before_json": _json({"status": before.value}), "after_json": _json({"status": after.value})})
    except (DomainError, ValueError) as exc:
        code = getattr(exc, "code", "ROUND_STATUS_INVALID")
        raise HTTPException(status_code=422, detail={"code": code, "message": str(exc)}) from exc
    return {"round_id": round_id, "status": after.value}


@router.post("/rounds/{round_id}/unlock", response_model=ActionResponse, response_model_exclude_none=True)
def unlock_round(round_id: int, payload: UnlockPayload, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN")
    with db.begin():
        ensure_round_semester_writable(db, round_id)
        row = db.execute(text("SELECT status FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
        if row["status"] != "LOCKED":
            raise HTTPException(status_code=409, detail={"code": "ROUND_NOT_LOCKED", "message": "Only a locked round can be unlocked."})
        actor_id = _actor_id(db, user)
        db.execute(text("UPDATE rounds SET status = 'COMPLETED' WHERE id = :round_id"), {"round_id": round_id})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'ROUND_UNLOCKED', 'round', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(round_id), "reason": payload.reason.strip(), "before_json": _json({"status": "LOCKED"}), "after_json": _json({"status": "COMPLETED"})})
    return {"round_id": round_id, "status": "COMPLETED"}


@router.post("/rounds/{round_id}/resources", response_model=RoundResourceResponse)
def attach_round_resources(
    round_id: int,
    payload: RoundResources,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            if db.execute(text("SELECT 1 FROM rounds WHERE id = :id"), {"id": round_id}).scalar_one_or_none() is None:
                raise DomainError("ROUND_NOT_FOUND", "Round does not exist.")
            for group_id in set(payload.group_ids):
                db.execute(
                    text(
                        "INSERT INTO round_groups (round_id, group_id) VALUES (:round_id, :group_id) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {"round_id": round_id, "group_id": group_id},
                )
            room_types = set(payload.room_types)
            legacy_room_ids = (payload.model_extra or {}).get("room_ids", [])
            for room_id in set(legacy_room_ids or []):
                room = db.execute(text("SELECT room_type::text FROM rooms WHERE id = :id AND active = TRUE"), {"id": room_id}).scalar_one_or_none()
                if room is None:
                    raise DomainError("ROUND_RESOURCE_INVALID", "Room does not exist or is inactive.")
                room_types.add(str(room))
            for room_type in sorted(room_types):
                db.execute(
                    text("INSERT INTO round_room_types (round_id, room_type) VALUES (:round_id, CAST(:room_type AS room_type)) ON CONFLICT DO NOTHING"),
                    {"round_id": round_id, "room_type": room_type},
                )
            for timeslot_id in set(payload.timeslot_ids):
                if db.execute(
                    text(
                        """
                        SELECT 1 FROM timeslots ts
                        JOIN round_days rd ON rd.id = ts.round_day_id
                        WHERE ts.id = :timeslot_id AND rd.round_id = :round_id
                        """
                    ),
                    {"timeslot_id": timeslot_id, "round_id": round_id},
                ).scalar_one_or_none() is None:
                    raise DomainError("ROUND_RESOURCE_INVALID", "Timeslot does not belong to the round.")
            counts = {
                "groups": len(set(payload.group_ids)),
                "timeslots": len(set(payload.timeslot_ids)),
                "rooms": db.execute(text("SELECT COUNT(*) FROM rooms r JOIN round_room_types rrt ON rrt.room_type = r.room_type WHERE rrt.round_id = :round_id AND r.active = TRUE"), {"round_id": round_id}).scalar_one(),
                "room_types": sorted(room_types),
            }
    except DomainError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "ROUND_RESOURCE_INVALID", "message": "A selected round resource does not exist."},
        ) from exc
    return {"round_id": round_id, **counts}


@router.post("/rounds/{round_id}/days", status_code=status.HTTP_201_CREATED, response_model=RoundDayCreateResponse)
def create_round_day(
    round_id: int,
    payload: RoundDayCreate,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")
    try:
        if any(slot.end_at <= slot.start_at for slot in payload.slots):
            raise DomainError("TIMESLOT_INVALID", "Timeslot end must be after its start.")
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            day_id = db.execute(
                text(
                    "INSERT INTO round_days (round_id, day_date) VALUES (:round_id, :day_date) "
                    "RETURNING id"
                ),
                {"round_id": round_id, "day_date": payload.day_date},
            ).scalar_one()
            slot_ids = []
            for slot in payload.slots:
                slot_ids.append(
                    db.execute(
                        text(
                            """
                            INSERT INTO timeslots (round_day_id, start_at, end_at, part)
                            VALUES (:round_day_id, :start_at, :end_at, :part) RETURNING id
                            """
                        ),
                        {
                            "round_day_id": day_id,
                            "start_at": slot.start_at,
                            "end_at": slot.end_at,
                            "part": "AM" if slot.start_at.hour < 13 else "PM",
                        },
                    ).scalar_one()
                )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "TIMESLOT_DUPLICATE", "message": "Round day or timeslot already exists."},
        ) from exc
    return {"round_id": round_id, "day_id": day_id, "timeslot_ids": slot_ids}


@router.post("/rounds/{round_id}/lecturers/{lecturer_id}/availability", response_model=AvailabilityWriteResponse)
def submit_lecturer_availability(
    round_id: int,
    lecturer_id: int,
    payload: AvailabilitySubmit,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER", "LECTURER")
    if user.role == "LECTURER":
        own_lecturer_id = lecturer_id_for_account(db, user.account_id)
        if own_lecturer_id is None or own_lecturer_id != lecturer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "A Lecturer may edit only their own availability."})
        accepted = db.execute(
            text("SELECT 1 FROM round_invitations WHERE round_id = :round_id AND lecturer_id = :lecturer_id AND status = 'ACCEPTED'"),
            {"round_id": round_id, "lecturer_id": lecturer_id},
        ).scalar_one_or_none()
        if accepted is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "A Lecturer may edit availability only after accepting the round invitation."})
        require_registration_phase(db, round_id, RegistrationPhase.LECTURER)
        db.commit()
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            slot_rows = db.execute(
                text(
                    """
                    SELECT ts.id FROM timeslots ts
                    JOIN round_days rd ON rd.id = ts.round_day_id
                    WHERE rd.round_id = :round_id AND ts.active = TRUE ORDER BY ts.id
                    """
                ),
                {"round_id": round_id},
            ).scalars().all()
            selected = set(payload.selected_timeslot_ids)
            if not selected.issubset(set(slot_rows)):
                raise DomainError("AVAILABILITY_SLOT_INVALID", "Selection contains a slot outside the round.")
            state = {slot_id: ("AVAILABLE" if slot_id in selected else "UNAVAILABLE") for slot_id in slot_rows}
            for timeslot_id, slot_state in state.items():
                db.execute(
                    text(
                        """
                        INSERT INTO lecturer_availabilities
                            (round_id, lecturer_id, timeslot_id, state, load_preference, source, updated_by)
                        VALUES (:round_id, :lecturer_id, :timeslot_id, :state, :load_preference, :source, :updated_by)
                        ON CONFLICT (round_id, lecturer_id, timeslot_id) DO UPDATE SET
                            state = EXCLUDED.state,
                            load_preference = EXCLUDED.load_preference,
                            source = EXCLUDED.source,
                            updated_by = EXCLUDED.updated_by
                        """
                    ),
                    {
                        "round_id": round_id,
                        "lecturer_id": lecturer_id,
                        "timeslot_id": timeslot_id,
                        "state": slot_state,
                        "load_preference": payload.load_preference,
                        "source": "MANAGER" if user.role == "MANAGER" else "FORM",
                        "updated_by": user.account_id,
                    },
                )
            db.execute(
                text(
                    """
                    INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json)
                    VALUES (:actor_id, 'AVAILABILITY_ENTERED', 'lecturer_availability', :entity_id, CAST(:after_json AS JSONB))
                    """
                ),
                {
                    "entity_id": f"{round_id}:{lecturer_id}",
                    "after_json": _json({"source": "MANAGER" if user.role == "MANAGER" else "FORM", "selected_count": len(selected)}),
                    "actor_id": user.account_id,
                },
            )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    return {
        "round_id": round_id,
        "lecturer_id": lecturer_id,
        "selected_count": len(selected),
        "total_slots": len(slot_rows),
        "source": "MANAGER" if user.role == "MANAGER" else "FORM",
    }


@router.post("/rounds/{round_id}/groups/{group_id}/availability", response_model=AvailabilityWriteResponse)
def submit_group_availability(
    round_id: int,
    group_id: int,
    payload: AvailabilitySubmit,
    db: Db,
    user: User,
) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER", "STUDENT")
    if user.role == "STUDENT" and not is_active_group_leader(db, user, group_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only the active Leader of this group may edit group availability."})
    attached = db.execute(text("SELECT 1 FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"), {"round_id": round_id, "group_id": group_id}).scalar_one_or_none()
    if attached is None:
        error_status = 403 if user.role == "STUDENT" else 422
        raise HTTPException(status_code=error_status, detail={"code": "GROUP_NOT_IN_ROUND", "message": "The group is not registered for this round."})
    round_row, _ = registration_phase_for_round(db, round_id)
    if not round_row["group_selection_mode"]:
        raise HTTPException(status_code=409, detail={"code": "GROUP_SELECTION_DISABLED", "message": "Group slot selection is disabled for this round."})
    if user.role == "STUDENT":
        require_registration_phase(db, round_id, RegistrationPhase.GROUP)
    db.commit()
    try:
        with db.begin():
            locked_attachment = db.execute(
                text(
                    "SELECT 1 FROM round_groups "
                    "WHERE round_id = :round_id AND group_id = :group_id FOR UPDATE"
                ),
                {"round_id": round_id, "group_id": group_id},
            ).scalar_one_or_none()
            if locked_attachment is None:
                error_status = 403 if user.role == "STUDENT" else 422
                raise HTTPException(
                    status_code=error_status,
                    detail={"code": "GROUP_NOT_IN_ROUND", "message": "The group is not registered for this round."},
                )
            ensure_round_semester_writable(db, round_id)
            slot_rows = db.execute(
                text(
                    """
                    SELECT ts.id FROM timeslots ts
                    JOIN round_days rd ON rd.id = ts.round_day_id
                    WHERE rd.round_id = :round_id AND ts.active = TRUE ORDER BY ts.id
                    """
                ),
                {"round_id": round_id},
            ).scalars().all()
            selected = set(payload.selected_timeslot_ids)
            if not selected.issubset(set(slot_rows)):
                raise DomainError("AVAILABILITY_SLOT_INVALID", "Selection contains a slot outside the round.")
            effective_slots = selected
            db.execute(
                text(
                    "DELETE FROM group_slot_preferences "
                    "WHERE round_id = :round_id AND group_id = :group_id"
                ),
                {"round_id": round_id, "group_id": group_id},
            )
            for timeslot_id in selected:
                db.execute(
                    text(
                        """
                        INSERT INTO group_slot_preferences (round_id, group_id, timeslot_id, selected, source, updated_by)
                        VALUES (:round_id, :group_id, :timeslot_id, TRUE, :source, :updated_by)
                        """
                    ),
                    {"round_id": round_id, "group_id": group_id, "timeslot_id": timeslot_id, "source": "MANAGER" if user.role in {"ADMIN", "MANAGER"} else "FORM", "updated_by": user.account_id},
                )
            db.execute(
                text(
                    """
                    INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json)
                    VALUES (:actor_id, 'AVAILABILITY_ENTERED', 'group_availability', :entity_id, CAST(:after_json AS JSONB))
                    """
                ),
                {"actor_id": user.account_id, "entity_id": f"{round_id}:{group_id}", "after_json": _json({"source": "MANAGER" if user.role in {"ADMIN", "MANAGER"} else "FORM", "selected_count": len(effective_slots)})},
            )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    return {
        "round_id": round_id,
        "group_id": group_id,
        "selected_count": len(effective_slots),
        "total_slots": len(slot_rows),
        "source": "MANAGER" if user.role in {"ADMIN", "MANAGER"} else "FORM",
    }


@router.post("/rounds/{round_id}/invitations", response_model=InvitationCreateResponse)
def invite_reviewers(
    round_id: int,
    payload: InvitationCreate,
    db: Db,
    user: User,
) -> dict[str, int]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            for lecturer_id in set(payload.lecturer_ids):
                lecturer = db.execute(
                    text("SELECT account_id FROM lecturers WHERE id = :lecturer_id"),
                    {"lecturer_id": lecturer_id},
                ).mappings().one_or_none()
                if lecturer is None:
                    raise DomainError("INVITATION_RESOURCE_INVALID", "Lecturer does not exist.")
                db.execute(
                    text(
                        "INSERT INTO round_invitations (round_id, lecturer_id) VALUES (:round_id, :lecturer_id) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {"round_id": round_id, "lecturer_id": lecturer_id},
                )
                if lecturer["account_id"] is not None:
                    key = f"invitation:{round_id}:{lecturer_id}"
                    event_payload = _json({"round_id": round_id, "lecturer_id": lecturer_id, "recipient_id": lecturer["account_id"]})
                    db.execute(
                        text(
                            "INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) "
                            "VALUES (:recipient_id, 'REVIEW_INVITATION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
                        ),
                        {"recipient_id": lecturer["account_id"], "payload": event_payload, "key": key},
                    )
                    db.execute(
                        text(
                            "INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES "
                            "('REVIEW_INVITATION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
                        ),
                        {"payload": event_payload, "key": key},
                    )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVITATION_RESOURCE_INVALID", "message": "Round or Lecturer does not exist."},
        ) from exc
    return {"round_id": round_id, "invited_count": len(set(payload.lecturer_ids))}


@router.post("/rounds/{round_id}/invitations/{lecturer_id}/response", response_model=InvitationActionResponse)
def respond_to_invitation(
    round_id: int,
    lecturer_id: int,
    payload: InvitationResponsePayload,
    db: Db,
    user: User,
) -> dict[str, str | int]:
    _require(user, "ADMIN", "MANAGER", "LECTURER")
    if user.role == "LECTURER" and lecturer_id_for_account(db, user.account_id) != lecturer_id:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "A Lecturer may respond only to their own invitation."})
    round_row = db.execute(
        text("SELECT registration_deadline FROM rounds WHERE id = :round_id"), {"round_id": round_id}
    ).mappings().one_or_none()
    if round_row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    ensure_round_semester_writable(db, round_id)
    deadline = round_row["registration_deadline"]
    try:
        stored_response = "DECLINED" if payload.response == "REJECTED" else payload.response
        invitation_response(
            stored_response,
            reason=payload.reason,
            deadline_passed=deadline is not None and deadline < datetime.now(UTC),
            actor_role=SystemRole(user.role),
        )
        updated = db.execute(
            text(
                """
                UPDATE round_invitations
                SET status = :response, response_reason = :reason, responded_at = now()
                WHERE round_id = :round_id AND lecturer_id = :lecturer_id
                """
            ),
            {
                "response": stored_response,
                "reason": payload.reason,
                "round_id": round_id,
                "lecturer_id": lecturer_id,
            },
        ).rowcount
        if updated == 0:
            raise DomainError("INVITATION_NOT_FOUND", "The invitation does not exist for this round.")
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'INVITATION_RESPONDED', 'round_invitation', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": f"{round_id}:{lecturer_id}", "reason": payload.reason, "after_json": _json({"response": stored_response})})
        db.commit()
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    return {"round_id": round_id, "lecturer_id": lecturer_id, "response": "REJECTED" if stored_response == "DECLINED" else stored_response}


@router.get("/rounds/{round_id}/registration", response_model=RegistrationResponse)
def registration_dashboard(round_id: int, db: Db, user: User) -> dict[str, int]:
    _require(user, "ADMIN", "MANAGER")
    counts = db.execute(
        text(
            """
            SELECT
                (SELECT count(*) FROM round_invitations WHERE round_id = :round_id) AS invited,
                (SELECT count(*) FROM round_invitations WHERE round_id = :round_id AND status <> 'PENDING') AS responded,
                (SELECT count(DISTINCT lecturer_id) FROM lecturer_availabilities WHERE round_id = :round_id) AS lecturer_availability,
                (SELECT count(DISTINCT group_id) FROM group_slot_preferences WHERE round_id = :round_id) AS group_availability
            """
        ),
        {"round_id": round_id},
    ).mappings().one()
    return {key: int(value) for key, value in counts.items()}


@router.get("/rounds/{round_id}/my-availability", response_model=MyAvailabilityResponse)
def my_availability(round_id: int, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    round_row = db.execute(text("SELECT id, type, status::text AS status, group_selection_mode, registration_deadline, group_preference_deadline FROM rounds WHERE id = :round_id"), {"round_id": round_id}).mappings().one_or_none()
    if round_row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    slots = db.execute(text("SELECT ts.id, ts.start_at, ts.end_at, rd.day_date FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = :round_id ORDER BY ts.start_at"), {"round_id": round_id}).mappings().all()
    response: dict[str, object] = {"round": dict(round_row), "timeslots": [dict(row) for row in slots]}
    if user.role == "LECTURER":
        lecturer_id = lecturer_id_for_account(db, user.account_id)
        if lecturer_id is None:
            raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
        accepted = db.execute(
            text("SELECT 1 FROM round_invitations WHERE round_id = :round_id AND lecturer_id = :lecturer_id AND status = 'ACCEPTED'"),
            {"round_id": round_id, "lecturer_id": lecturer_id},
        ).scalar_one_or_none()
        if accepted is None:
            raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "This round is not available to the Lecturer."})
        require_registration_phase(db, round_id, RegistrationPhase.LECTURER)
        response["lecturer_id"] = lecturer_id
        response["selected_timeslot_ids"] = [row["timeslot_id"] for row in db.execute(text("SELECT timeslot_id FROM lecturer_availabilities WHERE round_id = :round_id AND lecturer_id = :lecturer_id AND state = 'AVAILABLE'"), {"round_id": round_id, "lecturer_id": lecturer_id}).mappings().all()]
    elif user.role == "STUDENT":
        student_id = student_id_for_account(db, user.account_id)
        groups = db.execute(text("SELECT DISTINCT g.id, g.code FROM groups g JOIN group_memberships gm ON gm.group_id = g.id JOIN round_groups rg ON rg.group_id = g.id WHERE rg.round_id = :round_id AND gm.student_id = :student_id AND gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER'"), {"round_id": round_id, "student_id": student_id or 0}).mappings().all()
        if not groups:
            raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "This round has no active group belonging to the Student."})
        if not round_row["group_selection_mode"]:
            raise HTTPException(status_code=409, detail={"code": "GROUP_SELECTION_DISABLED", "message": "Group slot selection is disabled for this round."})
        require_registration_phase(db, round_id, RegistrationPhase.GROUP)
        response["groups"] = [dict(row) for row in groups]
        response["selected_by_group"] = {row["id"]: [item["timeslot_id"] for item in db.execute(text("SELECT timeslot_id FROM group_slot_preferences WHERE round_id = :round_id AND group_id = :group_id AND selected = TRUE"), {"round_id": round_id, "group_id": row["id"]}).mappings().all()] for row in groups}
    else:
        response["selected_by_lecturer"] = [dict(row) for row in db.execute(text("SELECT lecturer_id, timeslot_id, state, load_preference, source FROM lecturer_availabilities WHERE round_id = :round_id ORDER BY lecturer_id, timeslot_id"), {"round_id": round_id}).mappings().all()]
        response["selected_by_group"] = [dict(row) for row in db.execute(text("SELECT group_id, timeslot_id, selected, source FROM group_slot_preferences WHERE round_id = :round_id ORDER BY group_id, timeslot_id"), {"round_id": round_id}).mappings().all()]
    return response


@router.get("/my/rounds", response_model=list[MyRoundResponse])
def list_my_rounds(db: Db, user: User) -> list[dict[str, object]]:
    """Return rounds relevant to the current actor without widening data scope."""
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    if user.role in {"ADMIN", "MANAGER"}:
        rows = db.execute(
            text(
                "SELECT r.id, r.semester_id, s.code AS semester_code, r.type, r.status, "
                "r.group_selection_mode, r.registration_deadline "
                "FROM rounds r JOIN semesters s ON s.id = r.semester_id ORDER BY r.id DESC"
            )
        ).mappings().all()
    elif user.role == "LECTURER":
        rows = db.execute(
            text(
                "SELECT DISTINCT r.id, r.semester_id, s.code AS semester_code, r.type, r.status, "
                "r.group_selection_mode, r.registration_deadline "
                "FROM rounds r JOIN semesters s ON s.id = r.semester_id "
                "LEFT JOIN round_invitations ri ON ri.round_id = r.id "
                "LEFT JOIN lecturers l ON l.id = ri.lecturer_id "
                "WHERE (l.account_id = :account_id AND ri.status = 'ACCEPTED') "
                "OR EXISTS (SELECT 1 FROM council_members cm JOIN sessions cs ON cs.council_id = cm.council_id "
                "JOIN schedule_versions sv ON sv.id = cs.schedule_version_id JOIN lecturers sl ON sl.id = cm.lecturer_id "
                "WHERE sv.round_id = r.id AND sl.account_id = :account_id) "
                "ORDER BY r.id DESC"
            ),
            {"account_id": user.account_id},
        ).mappings().all()
    else:
        rows = db.execute(
            text(
                "SELECT DISTINCT r.id, r.semester_id, s.code AS semester_code, r.type, r.status, "
                "r.group_selection_mode, r.registration_deadline "
                "FROM rounds r JOIN semesters s ON s.id = r.semester_id "
                "JOIN round_groups rg ON rg.round_id = r.id "
                "JOIN group_memberships gm ON gm.group_id = rg.group_id "
                "JOIN students st ON st.id = gm.student_id "
                "WHERE st.account_id = :account_id AND gm.status = 'ACTIVE' ORDER BY r.id DESC"
            ),
            {"account_id": user.account_id},
        ).mappings().all()
    return [dict(row) for row in rows]


@router.get("/my/invitations", response_model=list[MyInvitationResponse])
def list_my_invitations(db: Db, user: User) -> list[dict[str, object]]:
    """Return only invitations belonging to the authenticated Lecturer."""
    _require(user, "LECTURER")
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    rows = db.execute(
        text(
            "SELECT ri.round_id, ri.lecturer_id, ri.status, ri.response_reason, ri.responded_at, "
            "r.type, r.registration_deadline, s.code AS semester_code "
            "FROM round_invitations ri JOIN rounds r ON r.id = ri.round_id "
            "JOIN semesters s ON s.id = r.semester_id "
            "WHERE ri.lecturer_id = :lecturer_id ORDER BY ri.round_id DESC"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.post("/lecturers/{lecturer_id}/conflicts", response_model=ConflictResponse)
def declare_conflict(
    lecturer_id: int,
    payload: ConflictCreate,
    db: Db,
    user: User,
) -> dict[str, int | str]:
    _require(user, "ADMIN", "MANAGER", "LECTURER")
    if user.role == "LECTURER" and lecturer_id_for_account(db, user.account_id) != lecturer_id:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "A Lecturer may declare only their own conflict."})
    db.commit()
    try:
        validate_conflict_declaration(
            lecturer_id=lecturer_id, project_id=payload.project_id, reason=payload.reason
        )
        with db.begin():
            semester_id = db.execute(
                text("SELECT semester_id FROM projects WHERE id = :project_id FOR UPDATE"),
                {"project_id": payload.project_id},
            ).scalar_one_or_none()
            if semester_id is not None:
                ensure_semester_writable(db, int(semester_id))
            conflict_id = db.execute(
                text(
                    """
                    INSERT INTO conflict_declarations (lecturer_id, project_id, reason)
                    VALUES (:lecturer_id, :project_id, :reason)
                    ON CONFLICT (lecturer_id, project_id) DO UPDATE SET reason = EXCLUDED.reason
                    RETURNING id
                    """
                ),
                {"lecturer_id": lecturer_id, "project_id": payload.project_id, "reason": payload.reason.strip()},
            ).scalar_one()
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) "
                    "VALUES (:actor_id, 'CONFLICT_DECLARED', 'conflict_declaration', :entity_id, :reason, CAST(:after_json AS JSONB))"
                ),
                {"actor_id": _actor_id(db, user), "entity_id": str(conflict_id), "reason": payload.reason.strip(), "after_json": _json({"lecturer_id": lecturer_id, "project_id": payload.project_id})},
            )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "CONFLICT_RESOURCE_INVALID", "message": "Lecturer or project does not exist."},
        ) from exc
    return {"id": conflict_id, "lecturer_id": lecturer_id, "project_id": payload.project_id}


def _json(value: object) -> str:
    import json

    return json.dumps(value, default=str)
