"""Target round lifecycle and self-service registration routes."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import external_id, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.registration_phase import RegistrationPhase, resolve_registration_phase
from app.routes.manager_extensions import resend_invitation
from app.routes.master_data import (
    AvailabilitySubmit,
    InvitationResponsePayload,
    RoundCreate,
    RoundDayCreate,
    RoundTransitionPayload,
    SlotCreate,
    _build_my_availability,
    create_round_with_days,
    list_rounds,
    registration_dashboard,
    require_registration_phase,
    respond_to_invitation,
    submit_group_availability,
    submit_lecturer_availability,
    transition_round_status,
)
from app.scheduler.validator import _eligible
from app.services.access import is_active_group_leader, lecturer_id_for_account

router = APIRouter(prefix="/api/v1", tags=["target-rounds"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]

# BR-STU-03: a group under this size only produces a warning, never a block.
MIN_RECOMMENDED_MEMBERS = 4


class RegistrationAction(BaseModel):
    reason: str | None = None


class GroupPreferencePayload(AvailabilitySubmit):
    pass


class TargetAvailabilitySlot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    timeslot_id: str | int = Field(alias="timeslotId")
    available: bool = True


class TargetAvailabilitySubmit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    preferred_load: str = Field(default="MEDIUM", alias="preferredLoad", pattern="^(LOW|MEDIUM|HIGH)$")
    slots: list[TargetAvailabilitySlot] = Field(default_factory=list)


class TargetGroupPreferences(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    timeslot_ids: list[str | int] = Field(default_factory=list, alias="timeslotIds")


class TargetInvitationCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    lecturer_ids: list[str | int] = Field(alias="lecturerIds", min_length=1)


class TargetInvitationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    decision: str = Field(pattern="^(ACCEPTED|DECLINED)$")
    reason: str | None = None


class TargetRoundSlot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")


class TargetRoundDay(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    day_date: date = Field(alias="date")
    slots: list[TargetRoundSlot] = Field(min_length=1)


class TargetRoundCreate(BaseModel):
    """Spec-shaped request for the semester-scoped round endpoint.

    The legacy ``POST /rounds`` route remains snake_case.  This model keeps the
    target route aligned with the frontend contract without changing that
    existing API.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    type: str
    description: str | None = Field(default=None, max_length=2000)
    duration_minutes: int = Field(alias="durationMinutes", gt=0, le=480)
    reviewer_count: int = Field(alias="reviewerCount", gt=0)
    max_groups_per_timeslot: int = Field(alias="maxGroupsPerTimeslot", gt=0)
    registration_deadline: datetime = Field(alias="registrationDeadline")
    group_selection_mode: bool = Field(alias="groupSelectionMode")
    group_preference_deadline: datetime | None = Field(default=None, alias="groupPreferenceDeadline")
    result_owner_mode: bool = Field(alias="resultOwnerMode")
    room_types: list[str] = Field(alias="roomTypes", min_length=1)
    days: list[TargetRoundDay] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_days(self) -> TargetRoundCreate:
        expected_reviewers = {
            "REVIEW_1": 2,
            "REVIEW_2": 2,
            "DEFENSE_1_1": 3,
            "DEFENSE_1_2": 5,
            "DEFENSE_2": 5,
        }.get(self.type)
        if expected_reviewers is None:
            raise ValueError("type is not a supported round type")
        if self.reviewer_count != expected_reviewers:
            raise ValueError(f"{self.type} requires {expected_reviewers} reviewers")
        if self.result_owner_mode and self.type not in {"DEFENSE_1_1", "DEFENSE_2"}:
            raise ValueError("resultOwnerMode is only available for DEFENSE_1_1 and DEFENSE_2")
        if self.registration_deadline.tzinfo is None:
            raise ValueError("registrationDeadline must include a timezone offset")
        if self.group_selection_mode and self.group_preference_deadline is None:
            raise ValueError("groupPreferenceDeadline is required when groupSelectionMode is enabled")
        if self.group_preference_deadline is not None and self.group_preference_deadline.tzinfo is None:
            raise ValueError("groupPreferenceDeadline must include a timezone offset")
        if self.group_selection_mode and self.group_preference_deadline <= self.registration_deadline:
            raise ValueError("groupPreferenceDeadline must be after registrationDeadline")
        if any(room_type not in {"NORMAL", "SEMINAR", "LAB"} for room_type in self.room_types):
            raise ValueError("roomTypes must contain only NORMAL, SEMINAR, or LAB")

        dates: set[date] = set()
        for day in self.days:
            if day.day_date in dates:
                raise ValueError("days must not contain duplicate dates")
            dates.add(day.day_date)
            ordered = sorted(day.slots, key=lambda slot: slot.start_time)
            previous_end: time | None = None
            for slot in ordered:
                if slot.end_time <= slot.start_time:
                    raise ValueError("endTime must be after startTime")
                duration = datetime.combine(day.day_date, slot.end_time) - datetime.combine(day.day_date, slot.start_time)
                if duration != timedelta(minutes=self.duration_minutes):
                    raise ValueError("slot duration must equal durationMinutes")
                if previous_end is not None and slot.start_time < previous_end:
                    raise ValueError("slots on the same day must not overlap")
                previous_end = slot.end_time
        return self

    def to_legacy(self, semester_id: int) -> tuple[RoundCreate, list[RoundDayCreate]]:
        vietnam_tz = ZoneInfo("Asia/Ho_Chi_Minh")
        days = [
            RoundDayCreate(
                day_date=day.day_date,
                slots=[
                    SlotCreate(
                        start_at=datetime.combine(day.day_date, slot.start_time, tzinfo=vietnam_tz),
                        end_at=datetime.combine(day.day_date, slot.end_time, tzinfo=vietnam_tz),
                    )
                    for slot in day.slots
                ],
            )
            for day in self.days
        ]
        boundary_dates = [day.day_date for day in self.days]
        boundary_dates.append(self.registration_deadline.date())
        if self.group_preference_deadline is not None:
            boundary_dates.append(self.group_preference_deadline.date())
        legacy = RoundCreate(
            semester_id=semester_id,
            name=self.name,
            description=self.description,
            type=self.type,
            reviewer_count=self.reviewer_count,
            start_date=min(boundary_dates),
            end_date=max(boundary_dates),
            result_owner_mode=self.result_owner_mode,
            group_selection_mode=self.group_selection_mode,
            group_preference_deadline=self.group_preference_deadline,
            session_duration_minutes=self.duration_minutes,
            registration_deadline=self.registration_deadline.isoformat(),
            max_groups_per_timeslot=self.max_groups_per_timeslot,
            room_types=self.room_types,
        )
        return legacy, days


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


@router.get("/semesters/{semester_id}/rounds")
def list_semester_rounds(semester_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    rows = list_rounds(db, user, semester_id=semester_id)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/semesters/{semester_id}/rounds", status_code=status.HTTP_201_CREATED)
def create_semester_round(semester_id: int, payload: TargetRoundCreate, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    legacy_payload, days = payload.to_legacy(semester_id)
    return success_payload(create_round_with_days(legacy_payload, db, user, days=days))


@router.get("/rounds/{round_id}/eligible-projects")
def eligible_projects(round_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    round_row = db.execute(text("SELECT type::text AS type FROM rounds WHERE id = :id"), {"id": round_id}).mappings().one_or_none()
    if round_row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    rows = db.execute(
        text(
            "SELECT p.id AS project_id, g.id AS group_id, g.status::text AS group_status, "
            "EXISTS (SELECT 1 FROM group_memberships gm WHERE gm.group_id = g.id AND gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS has_active_leader, "
            "EXISTS (SELECT 1 FROM project_supervisors ps WHERE ps.project_id = p.id AND ps.supervisor_type = 'MAIN') AS has_main_supervisor, "
            "(SELECT COUNT(*) FROM group_memberships gm WHERE gm.group_id = g.id AND gm.status = 'ACTIVE') AS active_member_count, "
            "EXISTS (SELECT 1 FROM round_groups previous_rg JOIN rounds previous_round ON previous_round.id = previous_rg.round_id "
            "WHERE previous_rg.group_id = g.id AND previous_rg.round_id <> :round_id "
            "AND previous_round.type = 'REVIEW_1' AND previous_round.status <> 'CANCELLED') AS has_prior_review_1 "
            "FROM projects p JOIN rounds r ON r.semester_id = p.semester_id "
            "LEFT JOIN groups g ON g.project_id = p.id "
            "WHERE r.id = :round_id AND p.status::text <> 'ARCHIVED' "
            "AND NOT EXISTS (SELECT 1 FROM round_groups rg WHERE rg.round_id = :round_id AND rg.group_id = g.id) "
            "ORDER BY p.code"
        ),
        {"round_id": round_id},
    ).mappings().all()
    round_type = round_row["type"]
    items = []
    for row in rows:
        has_group = row["group_id"] is not None
        has_active_leader = bool(row["has_active_leader"]) if has_group else False
        has_main_supervisor = bool(row["has_main_supervisor"])
        has_prior_review_1 = bool(row["has_prior_review_1"]) if has_group else False
        progression_allowed = (
            has_group
            and _eligible(round_type, row["group_status"] or "")
            and not (round_type == "REVIEW_1" and has_prior_review_1)
        )
        eligible = has_group and has_active_leader and has_main_supervisor and progression_allowed
        blocking_reasons = []
        if not has_group:
            blocking_reasons.append("No Group")
        if has_group and not has_active_leader:
            blocking_reasons.append("No Active Leader")
        if not has_main_supervisor:
            blocking_reasons.append("No Main Supervisor")
        if has_group and not progression_allowed:
            blocking_reasons.append(
                "Group already has a non-cancelled REVIEW_1 round."
                if round_type == "REVIEW_1" and has_prior_review_1
                else "Progression incompatible"
            )
        warnings = []
        if has_group and (row["active_member_count"] or 0) < MIN_RECOMMENDED_MEMBERS:
            warnings.append({"code": "MEMBER_COUNT_BELOW_MIN", "message": "Group has fewer than recommended members."})
        items.append({
            "projectId": external_id(row["project_id"], "prj"),
            "groupId": external_id(row["group_id"], "grp") if has_group else None,
            "eligible": eligible,
            "checks": {
                "hasGroup": has_group,
                "hasActiveLeader": has_active_leader,
                "hasMainSupervisor": has_main_supervisor,
                "progressionAllowed": progression_allowed,
            },
            "blockingReasons": blocking_reasons,
            "warnings": warnings,
        })
    return success_payload(items, meta={"page": 1, "pageSize": len(items), "total": len(items)})


@router.get("/rounds/{round_id}/registration-summary")
def registration_summary(round_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    return success_payload(registration_dashboard(round_id, db, user))


@router.get("/rounds/{round_id}/scheduling-readiness")
def scheduling_readiness(round_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    row = db.execute(
        text(
            "SELECT r.id, r.status::text AS status, "
            "(SELECT COUNT(*) FROM round_groups WHERE round_id = r.id) AS groups, "
            "(SELECT COUNT(*) FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE rd.round_id = r.id) AS timeslots, "
            "(SELECT COUNT(*) FROM round_invitations WHERE round_id = r.id AND status = 'ACCEPTED') AS accepted_invitations "
            "FROM rounds r WHERE r.id = :round_id"
        ),
        {"round_id": round_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
    blockers: list[str] = []
    if not row["groups"]:
        blockers.append("NO_GROUPS")
    if not row["timeslots"]:
        blockers.append("NO_TIMESLOTS")
    return success_payload({"ready": not blockers, "blockers": blockers, **dict(row)})


def _transition(
    round_id: int,
    target_status: str,
    payload: RegistrationAction | None,
    db: Session,
    user: CurrentUser,
) -> dict[str, Any]:
    _manager(user)
    transition = RoundTransitionPayload(target_status=target_status, reason=payload.reason if payload else None)
    return success_payload(transition_round_status(round_id, transition, db, user))


@router.post("/rounds/{round_id}/actions/open-registration")
def open_registration(round_id: int, db: Db, user: User, payload: RegistrationAction | None = None) -> dict[str, Any]:
    return _transition(round_id, "OPEN_REGISTRATION", payload, db, user)


@router.post("/rounds/{round_id}/actions/open-group-registration")
def open_group_registration(round_id: int, db: Db, user: User) -> dict[str, Any]:
    """Manually hand the open round from lecturer availability to student preferences."""

    _manager(user)
    with db.begin():
        row = db.execute(
            text(
                "SELECT status::text AS status, group_selection_mode, registration_deadline, "
                "group_preference_deadline, lecturer_registration_closed_at "
                "FROM rounds WHERE id = :round_id FOR UPDATE"
            ),
            {"round_id": round_id},
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
        if row["status"] != "OPEN_REGISTRATION":
            raise HTTPException(status_code=409, detail={"code": "ROUND_STATUS_INVALID", "message": "Round must be OPEN_REGISTRATION."})
        if not row["group_selection_mode"]:
            raise HTTPException(status_code=409, detail={"code": "GROUP_SELECTION_DISABLED", "message": "Group slot selection is disabled for this round."})
        if row["group_preference_deadline"] is None:
            raise HTTPException(status_code=422, detail={"code": "ROUND_DEADLINE_INVALID", "message": "groupPreferenceDeadline is required."})
        phase = resolve_registration_phase(
            round_status=row["status"],
            registration_deadline=row["registration_deadline"],
            group_preference_deadline=row["group_preference_deadline"],
            lecturer_registration_closed_at=row["lecturer_registration_closed_at"],
            now=datetime.now(ZoneInfo("UTC")),
        )
        if phase is RegistrationPhase.CLOSED:
            raise HTTPException(status_code=409, detail={"code": "REGISTRATION_CLOSED", "message": "The group preference deadline has passed."})
        db.execute(
            text("UPDATE rounds SET lecturer_registration_closed_at = COALESCE(lecturer_registration_closed_at, now()) WHERE id = :round_id"),
            {"round_id": round_id},
        )
    return success_payload({"roundId": external_id(round_id, "rnd"), "status": "OPEN_REGISTRATION", "registrationPhase": "GROUP"})


@router.post("/rounds/{round_id}/actions/close-registration")
def close_registration(round_id: int, db: Db, user: User, payload: RegistrationAction | None = None) -> dict[str, Any]:
    return _transition(round_id, "REGISTRATION_CLOSED", payload, db, user)


@router.get("/rounds/{round_id}/availability/me")
def get_my_availability(round_id: int, db: Db, user: User) -> dict[str, Any]:
    # Reading a submitted availability remains allowed after the registration
    # window closes; only the PUT endpoint enforces the active phase.
    return success_payload(_build_my_availability(round_id, db, user, enforce_registration_phase=False))


@router.put("/rounds/{round_id}/availability/me")
def put_my_availability(round_id: int, payload: TargetAvailabilitySubmit, db: Db, user: User) -> dict[str, Any]:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only a Lecturer may edit personal availability."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    selected = [parse_external_id(slot.timeslot_id, prefix="ts") for slot in payload.slots if slot.available]
    legacy = AvailabilitySubmit(selected_timeslot_ids=selected, load_preference=payload.preferred_load)
    return success_payload(submit_lecturer_availability(round_id, lecturer_id, legacy, db, user))


@router.post("/rounds/{round_id}/invitations/me/respond")
def respond_my_invitation(round_id: int, payload: TargetInvitationResponse, db: Db, user: User) -> dict[str, Any]:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only a Lecturer may respond to an invitation."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    legacy = InvitationResponsePayload(response="DECLINED" if payload.decision == "DECLINED" else "ACCEPTED", reason=payload.reason)
    return success_payload(respond_to_invitation(round_id, lecturer_id, legacy, db, user))


@router.post("/rounds/{round_id}/invitations", status_code=status.HTTP_201_CREATED)
def create_target_invitations(round_id: int, payload: TargetInvitationCreate, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    lecturer_ids = [parse_external_id(value, prefix="lec") for value in payload.lecturer_ids]
    with db.begin():
        for lecturer_id in set(lecturer_ids):
            exists = db.execute(text("SELECT 1 FROM lecturers WHERE id = :lecturer_id"), {"lecturer_id": lecturer_id}).scalar_one_or_none()
            if exists is None:
                raise HTTPException(status_code=422, detail={"code": "INVITATION_RESOURCE_INVALID", "message": "Lecturer does not exist."})
            db.execute(text("INSERT INTO round_invitations (round_id, lecturer_id) VALUES (:round_id, :lecturer_id) ON CONFLICT DO NOTHING"), {"round_id": round_id, "lecturer_id": lecturer_id})
    return success_payload({"roundId": external_id(round_id, "rnd"), "invitedCount": len(set(lecturer_ids))})


@router.post("/rounds/{round_id}/invitations/{invitation_id}/remind")
def remind_invitation(round_id: int, invitation_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    return success_payload(resend_invitation(round_id, invitation_id, db, user))


@router.get("/rounds/{round_id}/groups/{group_id}/preferences")
def get_group_preferences(round_id: int, group_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Group preference access is not available."})
    if user.role == "STUDENT" and not is_active_group_leader(db, user, group_id):
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only the active Leader of this group may view group preferences."})
    attached = db.execute(
        text("SELECT 1 FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"),
        {"round_id": round_id, "group_id": group_id},
    ).scalar_one_or_none()
    if attached is None:
        error_status = 403 if user.role == "STUDENT" else 422
        raise HTTPException(status_code=error_status, detail={"code": "GROUP_NOT_IN_ROUND", "message": "The group is not registered for this round."})
    if user.role == "STUDENT":
        # Reading previously submitted preferences remains allowed after the
        # registration window closes. The PUT route keeps the phase guard.
        round_row = db.execute(
            text("SELECT group_selection_mode FROM rounds WHERE id = :round_id"),
            {"round_id": round_id},
        ).mappings().one_or_none()
        if round_row is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."})
        if not round_row["group_selection_mode"]:
            raise HTTPException(status_code=409, detail={"code": "GROUP_SELECTION_DISABLED", "message": "Group slot selection is disabled for this round."})
    rows = db.execute(
        text(
            "SELECT ts.id AS timeslot_id, ts.start_at, ts.end_at, gsp.selected, gsp.source "
            "FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id "
            "LEFT JOIN group_slot_preferences gsp ON gsp.timeslot_id = ts.id AND gsp.round_id = :round_id AND gsp.group_id = :group_id "
            "WHERE rd.round_id = :round_id AND ts.active = TRUE"
            + " ORDER BY ts.start_at"
        ),
        {"round_id": round_id, "group_id": group_id},
    ).mappings().all()
    return success_payload({"roundId": round_id, "groupId": group_id, "timeslots": [dict(row) for row in rows]})


@router.put("/rounds/{round_id}/groups/{group_id}/preferences")
def put_group_preferences(round_id: int, group_id: int, payload: TargetGroupPreferences, db: Db, user: User) -> dict[str, Any]:
    selected = [parse_external_id(value, prefix="ts") for value in payload.timeslot_ids]
    legacy = AvailabilitySubmit(selected_timeslot_ids=selected, load_preference="MEDIUM")
    return success_payload(submit_group_availability(round_id, group_id, legacy, db, user))
