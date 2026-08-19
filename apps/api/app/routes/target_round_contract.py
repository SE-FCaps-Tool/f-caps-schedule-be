"""Target round lifecycle and self-service registration routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.routes.manager_extensions import resend_invitation
from app.routes.master_data import (
    AvailabilitySubmit,
    InvitationResponsePayload,
    RoundCreate,
    RoundTransitionPayload,
    create_round,
    list_rounds,
    my_availability,
    registration_dashboard,
    respond_to_invitation,
    submit_group_availability,
    submit_lecturer_availability,
    transition_round_status,
)
from app.services.access import lecturer_id_for_account

router = APIRouter(prefix="/api/v1", tags=["target-rounds"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


class RegistrationAction(BaseModel):
    reason: str | None = None


class GroupPreferencePayload(AvailabilitySubmit):
    pass


def _manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Manager permission required."})


@router.get("/semesters/{semester_id}/rounds")
def list_semester_rounds(semester_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    rows = list_rounds(db, user, semester_id=semester_id)
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.post("/semesters/{semester_id}/rounds", status_code=status.HTTP_201_CREATED)
def create_semester_round(semester_id: int, payload: RoundCreate, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    return success_payload(create_round(payload.model_copy(update={"semester_id": semester_id}), db, user))


@router.get("/rounds/{round_id}/eligible-projects")
def eligible_projects(round_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    rows = db.execute(
        text(
            "SELECT p.id, p.code, p.title, p.status::text AS status, p.semester_id "
            "FROM projects p JOIN rounds r ON r.semester_id = p.semester_id "
            "WHERE r.id = :round_id AND p.status::text <> 'ARCHIVED' "
            "AND NOT EXISTS (SELECT 1 FROM round_groups rg JOIN groups g ON g.id = rg.group_id WHERE rg.round_id = :round_id AND g.project_id = p.id) "
            "ORDER BY p.code"
        ),
        {"round_id": round_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


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


def _transition(round_id: int, target_status: str, payload: RegistrationAction, db: Session, user: CurrentUser) -> dict[str, Any]:
    _manager(user)
    transition = RoundTransitionPayload(target_status=target_status, reason=payload.reason)
    return success_payload(transition_round_status(round_id, transition, db, user))


@router.post("/rounds/{round_id}/actions/open-registration")
def open_registration(round_id: int, payload: RegistrationAction, db: Db, user: User) -> dict[str, Any]:
    return _transition(round_id, "OPEN_REGISTRATION", payload, db, user)


@router.post("/rounds/{round_id}/actions/close-registration")
def close_registration(round_id: int, payload: RegistrationAction, db: Db, user: User) -> dict[str, Any]:
    return _transition(round_id, "REGISTRATION_CLOSED", payload, db, user)


@router.get("/rounds/{round_id}/availability/me")
def get_my_availability(round_id: int, db: Db, user: User) -> dict[str, Any]:
    return success_payload(my_availability(round_id, db, user))


@router.put("/rounds/{round_id}/availability/me")
def put_my_availability(round_id: int, payload: AvailabilitySubmit, db: Db, user: User) -> dict[str, Any]:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only a Lecturer may edit personal availability."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    return success_payload(submit_lecturer_availability(round_id, lecturer_id, payload, db, user))


@router.post("/rounds/{round_id}/invitations/me/respond")
def respond_my_invitation(round_id: int, payload: InvitationResponsePayload, db: Db, user: User) -> dict[str, Any]:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Only a Lecturer may respond to an invitation."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    return success_payload(respond_to_invitation(round_id, lecturer_id, payload, db, user))


@router.post("/rounds/{round_id}/invitations/{invitation_id}/remind")
def remind_invitation(round_id: int, invitation_id: int, db: Db, user: User) -> dict[str, Any]:
    _manager(user)
    return success_payload(resend_invitation(round_id, invitation_id, db, user))


@router.get("/rounds/{round_id}/groups/{group_id}/preferences")
def get_group_preferences(round_id: int, group_id: int, db: Db, user: User) -> dict[str, Any]:
    if user.role not in {"ADMIN", "MANAGER", "LECTURER", "STUDENT"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Group preference access is not available."})
    rows = db.execute(
        text(
            "SELECT ts.id AS timeslot_id, ts.start_at, ts.end_at, gsp.selected, gsp.source "
            "FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id "
            "LEFT JOIN group_slot_preferences gsp ON gsp.timeslot_id = ts.id AND gsp.round_id = :round_id AND gsp.group_id = :group_id "
            "WHERE rd.round_id = :round_id ORDER BY ts.start_at"
        ),
        {"round_id": round_id, "group_id": group_id},
    ).mappings().all()
    return success_payload({"roundId": round_id, "groupId": group_id, "timeslots": [dict(row) for row in rows]})


@router.put("/rounds/{round_id}/groups/{group_id}/preferences")
def put_group_preferences(round_id: int, group_id: int, payload: GroupPreferencePayload, db: Db, user: User) -> dict[str, Any]:
    return success_payload(submit_group_availability(round_id, group_id, payload, db, user))
