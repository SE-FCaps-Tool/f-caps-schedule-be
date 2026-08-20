from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.enums import RoundStatus
from app.domain.errors import DomainError
from app.domain.schedule_operations import (
    ensure_publishable,
    ensure_reschedule_allowed,
    require_change_reason,
)
from app.domain.transitions import transition_round
from app.response_models import (
    ActionResponse,
    CompareResponse,
    ControlledChangeResponse,
    PublishResponse,
    ReplacementSuggestionResponse,
    ResultOwnerResponse,
    ScheduleRunResponse,
    SessionEditResponse,
    VersionDetailResponse,
    VersionSummaryResponse,
)
from app.scheduler.candidates import generate_candidates
from app.scheduler.models import RoundInput, ScheduledSession
from app.scheduler.scheduler import solve_schedule
from app.scheduler.snapshot import build_input_snapshot
from app.scheduler.validator import validate_schedule
from app.services.access import (
    affected_schedule_recipients,
    can_read_session,
    is_active_group_leader,
    visible_session_ids,
)
from app.services.councils import (
    CouncilError,
    create_council,
    load_council_members,
    lock_reviewer_ids,
    validate_council_change,
)
from app.services.room_assignment import (
    RoomAssignmentError,
    allowed_room,
    find_room_conflict,
    lock_room_ids,
    validate_publish_room_readiness,
)
from app.services.semester_queries import ensure_round_semester_writable

router = APIRouter(prefix="/api/v1", tags=["schedule-operations"])
CONTROLLED_CHANGE_PATH = "/schedule/versions/{version_id}/sessions/{session_id}/controlled-change"
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


class ScheduleRunPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    random_seed: int = Field(default=0, alias="randomSeed")
    time_limit_seconds: float = Field(default=10, alias="timeLimitSeconds", gt=0, le=300)


class SessionEditPayload(BaseModel):
    timeslot_id: int | None = Field(default=None, gt=0)
    reviewer_ids: list[int] | None = None
    result_owner_id: int | None = Field(default=None, gt=0)
    reason: str = Field(min_length=1, max_length=1000)


class ControlledChangePayload(SessionEditPayload):
    room_id: int | None = Field(default=None, gt=0)


class RescheduleRequestPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class RescheduleDecisionPayload(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    note: str = Field(min_length=1, max_length=1000)


class MakeupSessionPayload(BaseModel):
    timeslot_id: int = Field(gt=0)
    room_id: int | None = Field(default=None, gt=0)
    reviewer_ids: list[int] | None = None
    reason: str = Field(min_length=1, max_length=1000)


class RoundOperationPayload(BaseModel):
    action: Literal["POSTPONED", "CANCELLED"]
    reason: str = Field(min_length=1, max_length=1000)


class H11WaiverPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class ResultOwnerPayload(BaseModel):
    lecturer_id: int = Field(gt=0)


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text(
            "SELECT COALESCE((SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)), "
            "(SELECT MIN(id) FROM accounts))"
        ),
        {"role": user.role},
    ).scalar_one_or_none()


def _queue_schedule_changed(
    db: Session,
    recipient_ids: set[int],
    *,
    round_id: int,
    source_version_id: int,
    replacement_version_id: int | None,
    session_id: int,
    change_kind: str,
    reason: str,
) -> None:
    """Queue schedule-change notifications in the same transaction as the mutation."""
    for recipient_id in sorted(recipient_ids):
        payload = _json(
            {
                "round_id": round_id,
                "source_version_id": source_version_id,
                "replacement_version_id": replacement_version_id,
                "session_id": session_id,
                "change_kind": change_kind,
                "reason": reason,
                "recipient_id": recipient_id,
            }
        )
        key = f"schedule-changed:{source_version_id}:{replacement_version_id or source_version_id}:{session_id}:{recipient_id}"
        db.execute(
            text(
                "INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) "
                "VALUES (:recipient_id, 'SCHEDULE_CHANGED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
            ),
            {"recipient_id": recipient_id, "payload": payload, "key": key},
        )
        db.execute(
            text(
                "INSERT INTO outbox_jobs (topic, payload, dedupe_key) "
                "VALUES ('SCHEDULE_CHANGED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
            ),
            {"payload": payload, "key": key},
        )


def _round_input(
    db: Session, round_id: int
) -> tuple[
    RoundInput, list[int], list[tuple[int, datetime, datetime, str, str]], list[int]
]:
    round_row = (
        db.execute(
            text(
                "SELECT semester_id, type, reviewer_count, result_owner_mode, group_selection_mode, h12_sessions_per_part, h12_sessions_per_day, "
                "h12_semester_quota, max_groups_per_timeslot, max_minutes_per_part, max_minutes_per_day, soft_weights FROM rounds WHERE id = :id"
            ),
            {"id": round_id},
        )
        .mappings()
        .one_or_none()
    )
    if round_row is None:
        raise DomainError("ROUND_NOT_FOUND", "Round does not exist.")
    group_rows = (
        db.execute(
            text(
                "SELECT g.id, g.status, g.project_id, "
                "COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leader_count "
                "FROM round_groups rg JOIN groups g ON g.id = rg.group_id "
                "LEFT JOIN group_memberships gm ON gm.group_id = g.id "
                "WHERE rg.round_id = :round_id GROUP BY g.id, g.status, g.project_id ORDER BY g.id"
            ),
            {"round_id": round_id},
        )
        .mappings()
        .all()
    )
    project_ids = [row["project_id"] for row in group_rows]
    supervisors = (
        db.execute(
            text(
                "SELECT project_id, lecturer_id FROM project_supervisors "
                "WHERE project_id = ANY(:project_ids)"
            ),
            {"project_ids": project_ids or [0]},
        )
        .mappings()
        .all()
    )
    supervisor_map: dict[int, set[int]] = {}
    for row in supervisors:
        supervisor_map.setdefault(row["project_id"], set()).add(row["lecturer_id"])
    day_slots = (
        db.execute(
            text(
                "SELECT ts.id, ts.start_at, ts.end_at, rd.day_date, "
                "CASE WHEN EXTRACT(HOUR FROM ts.start_at AT TIME ZONE 'Asia/Ho_Chi_Minh') < 13 "
                "THEN 'AM' ELSE 'PM' END AS part "
                "FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id "
                "JOIN rounds r ON r.id = rd.round_id WHERE r.id = :round_id AND ts.active = TRUE ORDER BY ts.start_at"
            ),
            {"round_id": round_id},
        )
        .mappings()
        .all()
    )
    timeslots = [
        (row["id"], row["start_at"], row["end_at"], str(row["day_date"]), row["part"])
        for row in day_slots
    ]
    accepted_reviewer_ids = [
        row[0]
        for row in db.execute(
            text(
                "SELECT lecturer_id FROM round_invitations "
                "WHERE round_id = :round_id AND status = 'ACCEPTED' ORDER BY lecturer_id"
            ),
            {"round_id": round_id},
        ).all()
    ]
    availability_rows = db.execute(
        text(
            "SELECT lecturer_id, timeslot_id FROM lecturer_availabilities "
            "WHERE round_id = :round_id AND state = 'AVAILABLE'"
        ),
        {"round_id": round_id},
    ).all()
    available_reviewer_ids = sorted({row[0] for row in availability_rows})
    reviewer_ids = accepted_reviewer_ids or available_reviewer_ids
    existing_load_rows = db.execute(
        text(
            "SELECT cm.lecturer_id, COUNT(*) AS session_count "
            "FROM council_members cm JOIN sessions s ON s.council_id = cm.council_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds previous_round ON previous_round.id = sv.round_id "
            "WHERE previous_round.semester_id = :semester_id AND previous_round.id <> :round_id "
            "AND sv.status IN ('ACTIVE', 'PUBLISHED') GROUP BY cm.lecturer_id"
        ),
        {"semester_id": round_row["semester_id"], "round_id": round_id},
    ).all()
    existing_semester_load = {row[0]: int(row[1]) for row in existing_load_rows}
    selected_rows = db.execute(
        text(
            "SELECT group_id, timeslot_id FROM group_slot_preferences "
            "WHERE round_id = :round_id AND selected = TRUE"
        ),
        {"round_id": round_id},
    ).all()
    waiver_rows = (
        db.execute(
            text(
                "SELECT group_id, granted_by, reason FROM h11_waivers "
                "WHERE round_id = :round_id AND active = TRUE"
            ),
            {"round_id": round_id},
        )
        .mappings()
        .all()
    )
    prior_rows: list[Any] = []
    if round_row["type"] == "DEFENSE_1_2":
        prior_rows = db.execute(
            text(
                "SELECT s.group_id, cm.lecturer_id FROM sessions s "
                "JOIN council_members cm ON cm.council_id = s.council_id "
                "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                "JOIN rounds previous_round ON previous_round.id = sv.round_id "
                "WHERE s.group_id = ANY(:group_ids) AND previous_round.type = 'DEFENSE_1_1' "
                "AND sv.status IN ('ACTIVE', 'PUBLISHED')"
            ),
            {"group_ids": [row["id"] for row in group_rows] or [0]},
        ).all()
    prior: dict[int, set[int]] = {}
    for row in prior_rows:
        prior.setdefault(row[0], set()).add(row[1])
    remediation_verifiers: dict[int, set[int]] = {}
    for group_id, verifier_id in db.execute(
        text(
            "SELECT group_id, verifier_lecturer_id FROM remediation_cases "
            "WHERE status IN ('OPEN', 'OVERDUE', 'PASSED') AND group_id = ANY(:group_ids)"
        ),
        {"group_ids": [row["id"] for row in group_rows] or [0]},
    ).all():
        if verifier_id is not None:
            remediation_verifiers.setdefault(group_id, set()).add(verifier_id)
    input_data = RoundInput(
        round_type=str(round_row["type"]),
        expected_reviewer_count=round_row["reviewer_count"],
        result_owner_mode=round_row["result_owner_mode"],
        group_status={row["id"]: str(row["status"]) for row in group_rows},
        group_leader_valid={row["id"]: int(row["leader_count"]) == 1 for row in group_rows},
        group_project={row["id"]: row["project_id"] for row in group_rows},
        project_supervisors=supervisor_map,
        lecturer_availability=set(availability_rows),
        conflicts=set(
            db.execute(text("SELECT lecturer_id, project_id FROM conflict_declarations")).all()
        ),
        group_selected_slots={},
        group_selection_mode=bool(round_row["group_selection_mode"]),
        prior_reviewer_ids=prior,
        remediation_verifier_ids=remediation_verifiers,
        h11_waiver_groups={row["group_id"] for row in waiver_rows},
        h12_sessions_per_part=round_row["h12_sessions_per_part"],
        h12_sessions_per_day=round_row["h12_sessions_per_day"],
        h12_semester_quota=round_row["h12_semester_quota"],
        existing_semester_load=existing_semester_load,
        max_groups_per_timeslot=round_row["max_groups_per_timeslot"],
        max_minutes_per_part=round_row["max_minutes_per_part"],
        max_minutes_per_day=round_row["max_minutes_per_day"],
        soft_weights=round_row["soft_weights"] or {},
        h11_waiver_actors={row["group_id"]: "MANAGER" for row in waiver_rows},
        h11_waiver_reasons={row["group_id"]: row["reason"] for row in waiver_rows},
    )
    for group_id, timeslot_id in selected_rows:
        input_data.group_selected_slots.setdefault(group_id, set()).add(timeslot_id)
    return input_data, [row["id"] for row in group_rows], timeslots, reviewer_ids


def _session_rows(db: Session, version_id: int) -> list[dict[str, Any]]:
    sessions = (
        db.execute(
            text(
                "SELECT s.id, a.id AS assignment_id, s.group_id, g.code AS group_code, a.project_id, s.timeslot_id, s.room_id, s.council_id, "
                "s.start_at, s.end_at, s.status "
                "FROM sessions s JOIN groups g ON g.id = s.group_id JOIN schedule_assignments a ON a.schedule_version_id=s.schedule_version_id AND a.group_id=s.group_id WHERE s.schedule_version_id = :version_id ORDER BY s.id"
            ),
            {"version_id": version_id},
        )
        .mappings()
        .all()
    )
    reviewers = db.execute(
        text(
            "SELECT s.id AS session_id, cm.lecturer_id, cm.is_result_owner, cm.snapshot_name "
            "FROM council_members cm JOIN sessions s ON s.council_id = cm.council_id "
            "WHERE s.schedule_version_id = :version_id ORDER BY cm.lecturer_id"
        ),
        {"version_id": version_id},
    ).all()
    by_session: dict[int, list[int]] = {}
    owners: dict[int, list[int]] = {}
    names: dict[int, dict[int, str]] = {}
    for session_id, lecturer_id, is_owner, snapshot_name in reviewers:
        by_session.setdefault(session_id, []).append(lecturer_id)
        names.setdefault(session_id, {})[lecturer_id] = snapshot_name
        if is_owner:
            owners.setdefault(session_id, []).append(lecturer_id)
    return [
        {
            **dict(row),
            "reviewer_ids": tuple(by_session.get(row["id"], [])),
            "result_owner_ids": tuple(owners.get(row["id"], [])),
            "reviewer_names": names.get(row["id"], {}),
        }
        for row in sessions
    ]


def _assignment_rows(db: Session, version_id: int) -> list[dict[str, Any]]:
    """Load the durable solver record, including reviewer snapshots."""
    rows = db.execute(text(
        "SELECT a.id AS assignment_id, a.id, a.schedule_version_id, a.group_id, g.code AS group_code, "
        "a.project_id, a.timeslot_id, a.start_at, a.end_at FROM schedule_assignments a "
        "JOIN groups g ON g.id=a.group_id WHERE a.schedule_version_id=:version_id ORDER BY a.id"
    ), {"version_id": version_id}).mappings().all()
    reviewers = db.execute(text(
        "SELECT r.assignment_id, r.lecturer_id, r.is_result_owner, r.snapshot_name "
        "FROM schedule_assignment_reviewers r JOIN schedule_assignments a ON a.id=r.assignment_id "
        "WHERE a.schedule_version_id=:version_id ORDER BY r.assignment_id,r.lecturer_id"
    ), {"version_id": version_id}).all()
    by_assignment: dict[int, list[int]] = {}
    owners: dict[int, list[int]] = {}
    names: dict[int, dict[int, str]] = {}
    for aid, lecturer_id, is_owner, snapshot_name in reviewers:
        by_assignment.setdefault(aid, []).append(lecturer_id)
        names.setdefault(aid, {})[lecturer_id] = snapshot_name
        if is_owner:
            owners.setdefault(aid, []).append(lecturer_id)
    return [{**dict(row), "room_id": None, "status": "PLANNED", "reviewer_ids": tuple(by_assignment.get(row["assignment_id"], [])),
             "result_owner_ids": tuple(owners.get(row["assignment_id"], [])),
             "reviewer_names": names.get(row["assignment_id"], {})} for row in rows]


def _to_domain_sessions(rows: list[dict[str, Any]]) -> list[ScheduledSession]:
    return [
        ScheduledSession(
            session_id=row["id"],
            group_id=row["group_id"],
            project_id=row["project_id"],
            timeslot_id=row["timeslot_id"],
            room_id=row["room_id"],
            start_at=row["start_at"],
            end_at=row["end_at"],
            reviewer_ids=row["reviewer_ids"],
            day=str(row["start_at"].date()),
            part="AM" if row["start_at"].hour < 13 else "PM",
        )
        for row in rows
    ]


def _edited_rows(
    rows: list[dict[str, Any]],
    session_id: int,
    payload: SessionEditPayload,
    timeslots: list[tuple[int, datetime, datetime, str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    target = next((row for row in rows if row["id"] == session_id), None)
    if target is None:
        raise DomainError("SESSION_NOT_FOUND", "Session does not exist in this version.")
    slot_map = {slot[0]: slot for slot in timeslots}
    next_slot_id = payload.timeslot_id or target["timeslot_id"]
    if next_slot_id not in slot_map:
        raise DomainError("TIMESLOT_NOT_IN_ROUND", "The requested timeslot is not attached to this round.")
    slot = slot_map[next_slot_id]
    changed = {
        **target,
        "timeslot_id": next_slot_id,
        "room_id": getattr(payload, "room_id", None) or target["room_id"],
        "start_at": slot[1],
        "end_at": slot[2],
        "reviewer_ids": tuple(payload.reviewer_ids) if payload.reviewer_ids is not None else target["reviewer_ids"],
    }
    result = [changed if row["id"] == session_id else row for row in rows]
    return result, {"before": target, "after": changed}


def _owner_for_edit(
    db: Session,
    *,
    session_id: int,
    round_id: int,
    reviewer_ids: tuple[int, ...],
    requested_owner_id: int | None,
) -> int | None:
    round_row = db.execute(
        text("SELECT type, result_owner_mode FROM rounds WHERE id = :round_id"),
        {"round_id": round_id},
    ).mappings().one()
    if not round_row["result_owner_mode"] or round_row["type"] not in {"DEFENSE_1_1", "DEFENSE_2"}:
        return None
    current_owner = db.execute(
        text("SELECT cm.lecturer_id FROM council_members cm JOIN sessions s ON s.council_id = cm.council_id "
             "WHERE s.id = :session_id AND cm.is_result_owner = TRUE "
             "UNION ALL SELECT lecturer_id FROM schedule_assignment_reviewers WHERE assignment_id = :session_id AND is_result_owner = TRUE"),
        {"session_id": session_id},
    ).all()
    owner_id = requested_owner_id or (current_owner[0][0] if len(current_owner) == 1 else None)
    if owner_id is None or owner_id not in reviewer_ids:
        raise DomainError(
            "RESULT_OWNER_REQUIRED",
            "Exactly one Result Owner from the session Reviewers is required.",
        )
    return owner_id


@router.get("/rounds/{round_id}/schedule/versions", response_model=list[VersionSummaryResponse])
def list_schedule_versions(round_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    rows = (
        db.execute(
            text(
                "SELECT id, round_id, version_no, status, solver_status, total_score, soft_scores, "
                "random_seed, created_at, activated_at FROM schedule_versions WHERE round_id = :round_id ORDER BY version_no"
            ),
            {"round_id": round_id},
        )
        .mappings()
        .all()
    )
    if user.role in {"ADMIN", "MANAGER"}:
        return [_version_ui(row) for row in rows]
    visible = visible_session_ids(db, user)
    visible_versions = {
        row[0]
        for row in db.execute(
            text("SELECT DISTINCT schedule_version_id FROM sessions WHERE id = ANY(:ids)"),
            {"ids": list(visible) or [0]},
        ).all()
    }
    return [_version_ui(row) for row in rows if row["id"] in visible_versions]


@router.get("/schedule/versions/{version_id}", response_model=VersionDetailResponse)
def schedule_version_detail(version_id: int, db: Db, user: User) -> dict[str, Any]:
    # Drafts are sourced from schedule_assignments; Sessions are materialized later.
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    version = (
        db.execute(text("SELECT * FROM schedule_versions WHERE id = :id"), {"id": version_id})
        .mappings()
        .one_or_none()
    )
    if version is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."},
        )
    assignments = _assignment_rows(db, version_id)
    sessions = [] if version["status"] == "DRAFT" else _session_rows(db, version_id)
    if user.role not in {"ADMIN", "MANAGER"}:
        visible = visible_session_ids(db, user, version_id=version_id)
        sessions = [row for row in sessions if row["id"] in visible]
        if not sessions:
            raise HTTPException(status_code=403, detail="Schedule is outside the actor's scope.")
    return {**_version_ui(version), "sessions": sessions, "assignments": assignments}


def _version_ui(row: Any) -> dict[str, Any]:
    payload = dict(row)
    payload["is_active"] = payload.get("status") in {"ACTIVE", "PUBLISHED"}
    payload["ui_status"] = payload.get("status")
    return payload


@router.get("/schedule/versions/compare/{version_a}/{version_b}", response_model=CompareResponse)
def compare_schedule_versions(version_a: int, version_b: int, db: Db, user: User) -> dict[str, Any]:
    """Return a stable, FE-friendly diff between two versions in one round."""
    _require(user, "ADMIN", "MANAGER")
    versions = db.execute(
        text("SELECT id, round_id, version_no, status, total_score, soft_scores, created_at FROM schedule_versions WHERE id = ANY(:ids)"),
        {"ids": [version_a, version_b]},
    ).mappings().all()
    if len(versions) != 2 or versions[0]["round_id"] != versions[1]["round_id"]:
        raise HTTPException(status_code=404, detail={"code": "VERSION_COMPARE_INVALID", "message": "Both versions must exist in the same round."})
    sessions = db.execute(text(
        "SELECT a.schedule_version_id, a.group_id, a.project_id, a.timeslot_id, "
        "COALESCE(array_agg(ar.lecturer_id ORDER BY ar.lecturer_id) "
        "FILTER (WHERE ar.lecturer_id IS NOT NULL), ARRAY[]::bigint[]) AS reviewer_ids "
        "FROM schedule_assignments a LEFT JOIN schedule_assignment_reviewers ar ON ar.assignment_id = a.id "
        "WHERE a.schedule_version_id = ANY(:ids) "
        "GROUP BY a.schedule_version_id, a.group_id, a.project_id, a.timeslot_id"
    ), {"ids": [version_a, version_b]}).mappings().all()
    by_version = {version_a: {}, version_b: {}}
    for row in sessions:
        by_version[row["schedule_version_id"]][row["group_id"]] = dict(row)
    changes = []
    for group_id in sorted(set(by_version[version_a]) | set(by_version[version_b])):
        left = by_version[version_a].get(group_id)
        right = by_version[version_b].get(group_id)
        if left != right:
            changes.append({"group_id": group_id, "version_a": left, "version_b": right})
    return {"version_a": dict(next(item for item in versions if item["id"] == version_a)), "version_b": dict(next(item for item in versions if item["id"] == version_b)), "changed_sessions": changes}


@router.delete("/schedule/versions/{version_id}", response_model=ActionResponse, response_model_exclude_none=True)
def delete_draft_version(version_id: int, db: Db, user: User) -> dict[str, Any]:
    # schedule_assignments and scheduler_jobs are owned by the version cascade.
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        version_ref = db.execute(text("SELECT round_id FROM schedule_versions WHERE id = :id"), {"id": version_id}).mappings().one_or_none()
        if version_ref is None:
            raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
        ensure_round_semester_writable(db, int(version_ref["round_id"]))
        row = db.execute(text("SELECT id, round_id, status, activated_at FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": version_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
        if row["status"] != "DRAFT":
            raise HTTPException(status_code=409, detail={"code": "VERSION_DELETE_FORBIDDEN", "message": "Only an unused draft/valid version can be deleted."})
        dependency_count = db.execute(text("SELECT COUNT(*) FROM schedule_change_records WHERE schedule_version_id=:id"), {"id": version_id}).scalar_one()
        if dependency_count:
            raise HTTPException(status_code=409, detail={"code": "VERSION_DELETE_HAS_DEPENDENCIES", "message": "Version has dependent schedule or audit records and cannot be deleted."})
        db.execute(text("DELETE FROM schedule_versions WHERE id = :id"), {"id": version_id})
    return {"id": version_id, "deleted": True}


@router.post("/rounds/{round_id}/schedule/run", status_code=status.HTTP_201_CREATED, response_model=ScheduleRunResponse)
def run_scheduler(round_id: int, payload: ScheduleRunPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            ensure_round_semester_writable(db, round_id)
            round_row = db.execute(
                text("SELECT status, reviewer_count FROM rounds WHERE id = :round_id FOR UPDATE"),
                {"round_id": round_id},
            ).mappings().one_or_none()
            if round_row is None:
                raise DomainError("ROUND_NOT_FOUND", "Round does not exist.")
            current_status = RoundStatus(round_row["status"])
            if current_status is not RoundStatus.SCHEDULING:
                next_status = transition_round(current_status, RoundStatus("SCHEDULING"))
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
                if not counts["groups"] or not counts["timeslots"] or reviewer_count < round_row["reviewer_count"]:
                    raise DomainError("ROUND_INPUTS_INCOMPLETE", "Round needs groups, timeslots and enough available Reviewers before scheduling.")
                db.execute(
                    text("UPDATE rounds SET status = CAST(:status AS round_status) WHERE id = :round_id"),
                    {"status": next_status.value, "round_id": round_id},
                )
            context, groups, timeslots, reviewers = _round_input(db, round_id)
            if not groups or not timeslots or not reviewers:
                raise DomainError("ROUND_INPUTS_INCOMPLETE", "Round needs groups, timeslots and at least one available Reviewer before scheduling.")
            result = solve_schedule(
                context,
                groups=groups,
                timeslots=timeslots,
                reviewers=reviewers,
                time_limit_seconds=payload.time_limit_seconds,
                random_seed=payload.random_seed,
            )
            snapshot = build_input_snapshot(
                round_id=round_id,
                context=context,
                groups=groups,
                timeslots=[row[0] for row in timeslots],
                reviewer_assignments={
                    session.group_id: list(session.reviewer_ids) for session in result.sessions
                },
                soft_weights=context.soft_weights,
            )
            snapshot["unscheduled"] = [reason.__dict__ for reason in result.unscheduled]
            version_no = db.execute(
                text(
                    "SELECT COALESCE(MAX(version_no), 0) + 1 FROM schedule_versions WHERE round_id = :round_id"
                ),
                {"round_id": round_id},
            ).scalar_one()
            actor_id = _actor_id(db, user)
            version_id = db.execute(
                text(
                    "INSERT INTO schedule_versions (round_id, version_no, status, input_snapshot, algorithm_parameters, "
                    "random_seed, solver_status, total_score, soft_scores, created_by) VALUES "
                    "(:round_id, :version_no, 'DRAFT', CAST(:snapshot AS JSONB), CAST(:parameters AS JSONB), :seed, "
                    ":solver_status, :score, CAST(:soft_scores AS JSONB), :created_by) RETURNING id"
                ),
                {
                    "round_id": round_id,
                    "version_no": version_no,
                    "snapshot": _json(snapshot),
                    "parameters": _json(payload.model_dump()),
                    "seed": result.random_seed,
                    "solver_status": result.status,
                    "score": result.objective,
                    "soft_scores": _json(result.soft_scores),
                    "created_by": actor_id,
                },
            ).scalar_one()
            for session in result.sessions:
                assignment_id = db.execute(text(
                    "INSERT INTO schedule_assignments(schedule_version_id,group_id,project_id,timeslot_id,start_at,end_at) "
                    "VALUES (:version_id,:group_id,:project_id,:timeslot_id,:start_at,:end_at) RETURNING id"
                ), {"version_id": version_id, "group_id": session.group_id,
                    "project_id": context.group_project[session.group_id], "timeslot_id": session.timeslot_id,
                    "start_at": session.start_at, "end_at": session.end_at}).scalar_one()
                names = db.execute(
                    text(
                        "SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id "
                        "WHERE l.id = ANY(:ids)"
                    ),
                    {"ids": list(session.reviewer_ids) or [0]},
                ).all()
                name_map = {row[0]: row[1] for row in names}
                for reviewer_index, lecturer_id in enumerate(session.reviewer_ids):
                    db.execute(
                        text(
                        "INSERT INTO schedule_assignment_reviewers (assignment_id, lecturer_id, is_result_owner, snapshot_name) "
                        "VALUES (:assignment_id, :lecturer_id, :is_owner, :snapshot_name)"
                        ),
                        {
                            "assignment_id": assignment_id,
                            "lecturer_id": lecturer_id,
                            "is_owner": context.result_owner_mode and context.round_type in {"DEFENSE_1_1", "DEFENSE_2"} and reviewer_index == 0,
                            "snapshot_name": name_map.get(lecturer_id, str(lecturer_id)),
                        },
                    )
            job_status = "PARTIAL" if result.unscheduled else "COMPLETED"
            db.execute(
                text(
                    "INSERT INTO scheduler_jobs (round_id, status, input_snapshot, algorithm_parameters, random_seed, schedule_version_id) "
                    "VALUES (:round_id, :status, CAST(:snapshot AS JSONB), CAST(:parameters AS JSONB), :seed, :version_id)"
                ),
                {
                    "round_id": round_id,
                    "status": job_status,
                    "snapshot": _json(snapshot),
                    "parameters": _json(payload.model_dump()),
                    "seed": result.random_seed,
                    "version_id": version_id,
                },
            )
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'SCHEDULER_RUN', 'schedule_version', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(version_id),
                    "after_json": _json({"round_id": round_id, "status": result.status}),
                },
            )
        return {
            "version_id": version_id,
            "status": "DRAFT",
            "scheduled_count": len(result.sessions),
            "unscheduled": [reason.__dict__ for reason in result.unscheduled],
            "soft_scores": result.soft_scores,
        }
    except (DomainError, IntegrityError) as exc:
        if isinstance(exc, DomainError):
            raise HTTPException(
                status_code=422, detail={"code": exc.code, "message": str(exc)}
            ) from exc
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SCHEDULE_PERSIST_FAILED",
                "message": "Schedule could not be persisted.",
            },
        ) from exc


@router.post("/rounds/{round_id}/groups/{group_id}/h11-waiver", response_model=ActionResponse, response_model_exclude_none=True)
def grant_h11_waiver(round_id: int, group_id: int, payload: H11WaiverPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        ensure_round_semester_writable(db, round_id)
        attached = db.execute(text("SELECT 1 FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"), {"round_id": round_id, "group_id": group_id}).scalar_one_or_none()
        if attached is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_GROUP_NOT_FOUND", "message": "The group is not attached to this round."})
        actor_id = _actor_id(db, user)
        row = db.execute(text("INSERT INTO h11_waivers (round_id, group_id, granted_by, reason, active) VALUES (:round_id, :group_id, :actor_id, :reason, TRUE) ON CONFLICT (round_id, group_id) DO UPDATE SET granted_by = EXCLUDED.granted_by, reason = EXCLUDED.reason, active = TRUE, created_at = now() RETURNING id, active"), {"round_id": round_id, "group_id": group_id, "actor_id": actor_id, "reason": payload.reason.strip()}).mappings().one()
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'H11_WAIVER_GRANTED', 'h11_waiver', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": f"{round_id}:{group_id}", "reason": payload.reason.strip(), "after_json": _json({"active": True, "scope": "H11"})})
    return {"id": row["id"], "round_id": round_id, "group_id": group_id, "active": row["active"]}


@router.delete("/rounds/{round_id}/groups/{group_id}/h11-waiver", response_model=ActionResponse, response_model_exclude_none=True)
def revoke_h11_waiver(round_id: int, group_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    with db.begin():
        ensure_round_semester_writable(db, round_id)
        updated = db.execute(text("UPDATE h11_waivers SET active = FALSE WHERE round_id = :round_id AND group_id = :group_id AND active = TRUE RETURNING id"), {"round_id": round_id, "group_id": group_id}).mappings().one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "H11_WAIVER_NOT_FOUND", "message": "Active H11 waiver does not exist."})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'H11_WAIVER_REVOKED', 'h11_waiver', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": f"{round_id}:{group_id}", "after_json": _json({"active": False})})
    return {"id": updated["id"], "round_id": round_id, "group_id": group_id, "active": False}


@router.post("/schedule/versions/{version_id}/activate", response_model=ActionResponse, response_model_exclude_none=True)
def activate_schedule_version(version_id: int, db: Db, user: User) -> dict[str, Any]:
    # acquire_resource_locks issues pg_advisory_xact_lock for every Reviewer.
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        version = (
            db.execute(
                text("SELECT round_id FROM schedule_versions WHERE id = :id"),
                {"id": version_id},
            )
            .mappings()
            .one_or_none()
        )
        if version is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."},
            )
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version["round_id"]})
        ensure_round_semester_writable(db, int(version["round_id"]))
        # The round lock serializes all activations for this round. Re-read the
        # target after acquiring it so a concurrent activation cannot activate
        # a stale DRAFT snapshot.
        version = (
            db.execute(
                text("SELECT round_id, status FROM schedule_versions WHERE id = :id FOR UPDATE"),
                {"id": version_id},
            )
            .mappings()
            .one_or_none()
        )
        if version is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."},
            )
        if version["status"] != "DRAFT":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "VERSION_NOT_VALID",
                    "message": "Only a draft version can become active.",
                },
            )
        group_ids = [row[0] for row in db.execute(text(
            "SELECT DISTINCT group_id FROM schedule_assignments WHERE schedule_version_id=:version_id ORDER BY group_id"
        ), {"version_id": version_id}).all()]
        db.execute(text("SELECT id FROM groups WHERE id=ANY(:group_ids) ORDER BY id FOR UPDATE"), {"group_ids": group_ids or [0]}).all()
        assignments = db.execute(text(
            "SELECT id, group_id, project_id, timeslot_id, start_at, end_at FROM schedule_assignments "
            "WHERE schedule_version_id=:version_id ORDER BY id FOR UPDATE"
        ), {"version_id": version_id}).mappings().all()
        stale = db.execute(text(
            "SELECT a.group_id FROM schedule_assignments a JOIN groups g ON g.id=a.group_id "
            "WHERE a.schedule_version_id=:version_id AND g.project_id IS DISTINCT FROM a.project_id"
        ), {"version_id": version_id}).all()
        if stale:
            raise HTTPException(status_code=409, detail={"code": "DRAFT_ASSIGNMENT_STALE", "message": "Group project provenance changed; regenerate the draft."})
        reviewer_ids = [row[0] for row in db.execute(text(
            "SELECT lecturer_id FROM schedule_assignment_reviewers r JOIN schedule_assignments a ON a.id=r.assignment_id WHERE a.schedule_version_id=:version_id"
        ), {"version_id": version_id}).all()]
        validation_rows = [dict(item) for item in assignments]
        reviewer_map: dict[int, list[int]] = {}
        for assignment_id, lecturer_id in db.execute(text(
            "SELECT assignment_id, lecturer_id FROM schedule_assignment_reviewers WHERE assignment_id=ANY(:assignment_ids) ORDER BY assignment_id, lecturer_id"
        ), {"assignment_ids": [item["id"] for item in assignments] or [0]}).all():
            reviewer_map.setdefault(assignment_id, []).append(lecturer_id)
        for item in validation_rows:
            item["reviewer_ids"] = tuple(reviewer_map.get(item["id"], []))
            item["room_id"] = None
            item["status"] = "PLANNED"
        activation_context, _, _, _ = _round_input(db, version["round_id"])
        activation_validation = validate_schedule(_to_domain_sessions(validation_rows), activation_context)
        if not activation_validation.valid:
            raise HTTPException(status_code=422, detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [item.__dict__ for item in activation_validation.violations]})
        # acquire_resource_locks issues pg_advisory_xact_lock(bigint) for each
        # reviewer key before the global overlap re-check.
        lock_reviewer_ids(db, reviewer_ids)
        # Re-check conflicts against every live schedule, including other rounds.
        conflict = db.execute(text(
            "SELECT 1 FROM schedule_assignment_reviewers ar JOIN schedule_assignments a ON a.id=ar.assignment_id "
            "JOIN sessions s ON s.start_at < a.end_at AND s.end_at > a.start_at "
            "JOIN council_members cm ON cm.council_id=s.council_id AND cm.lecturer_id=ar.lecturer_id "
            "JOIN schedule_versions sv ON sv.id=s.schedule_version_id "
            "WHERE a.schedule_version_id=:version_id AND s.schedule_version_id<>:version_id "
            "AND sv.status IN ('ACTIVE','PUBLISHED') LIMIT 1"
        ), {"version_id": version_id}).first()
        if conflict:
            raise HTTPException(status_code=409, detail={"code": "REVIEWER_OVERLAP", "message": "A Reviewer is already assigned in an overlapping live schedule."})
        for assignment in assignments:
            reviewers = db.execute(text(
                "SELECT lecturer_id,is_result_owner,snapshot_name FROM schedule_assignment_reviewers WHERE assignment_id=:assignment_id ORDER BY lecturer_id"
            ), {"assignment_id": assignment["id"]}).mappings().all()
            council_id = create_council(
                db,
                int(version["round_id"]),
                [dict(reviewer) for reviewer in reviewers],
                created_by=_actor_id(db, user),
                reason="Schedule activation",
            )
            db.execute(text(
                "INSERT INTO sessions (schedule_version_id,group_id,timeslot_id,room_id,council_id,start_at,end_at,status) "
                "VALUES (:version_id,:group_id,:timeslot_id,NULL,:council_id,:start_at,:end_at,'PLANNED') RETURNING id"
            ), {"version_id": version_id, **dict(assignment), "council_id": council_id}).scalar_one()
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'DISCARDED' WHERE round_id = :round_id AND status IN ('DRAFT', 'ACTIVE') AND id <> :id"
            ),
            {"round_id": version["round_id"], "id": version_id},
        )
        db.execute(
            text("UPDATE schedule_versions SET status = 'ACTIVE', activated_at = now() WHERE id = :id"),
            {"id": version_id},
        )
        db.execute(
            text("UPDATE rounds SET status = 'SCHEDULED' WHERE id = :round_id AND status = 'SCHEDULING'"),
            {"round_id": version["round_id"]},
        )
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'SCHEDULE_VERSION_ACTIVATED', 'schedule_version', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": _actor_id(db, user),
                "entity_id": str(version_id),
                "after_json": _json({"round_id": version["round_id"], "status": "ACTIVE"}),
            },
        )
    return {"version_id": version_id, "status": "ACTIVE"}


@router.post("/schedule/versions/{version_id}/sessions/{session_id}/result-owner", response_model=ResultOwnerResponse)
def assign_result_owner(version_id: int, session_id: int, payload: ResultOwnerPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    lecturer_id = payload.lecturer_id
    try:
        with db.begin():
            session_ref = db.execute(
                text("SELECT sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :session_id AND s.schedule_version_id = :version_id"),
                {"session_id": session_id, "version_id": version_id},
            ).mappings().one_or_none()
            if session_ref is None:
                raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist in this version."})
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": session_ref["round_id"]})
            ensure_round_semester_writable(db, int(session_ref["round_id"]))
            session = db.execute(text(
                "SELECT s.status, s.council_id, s.start_at, s.end_at, r.id AS round_id, r.type, "
                "r.result_owner_mode FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                "JOIN rounds r ON r.id = sv.round_id WHERE s.id = :session_id AND s.schedule_version_id = :version_id FOR UPDATE"
            ), {"session_id": session_id, "version_id": version_id}).mappings().one_or_none()
            if session is None:
                raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist in this version."})
            if session["status"] in {"COMPLETED", "GROUP_ABSENT", "POSTPONED", "CANCELLED"}:
                raise HTTPException(status_code=422, detail={"code": "SESSION_IMMUTABLE", "message": "This session's Council ownership is immutable."})
            before_recipients = affected_schedule_recipients(db, version_id)
            if not session["result_owner_mode"] or session["type"] not in {"DEFENSE_1_1", "DEFENSE_2"}:
                raise HTTPException(status_code=422, detail={"code": "RESULT_OWNER_NOT_ALLOWED", "message": "Result Owner mode is disabled for this session."})
            members = load_council_members(db, int(session["council_id"]))
            if lecturer_id not in {int(member["lecturer_id"]) for member in members}:
                raise HTTPException(status_code=422, detail={"code": "RESULT_OWNER_MUST_BE_REVIEWER", "message": "The Result Owner must be one of this session's Reviewers."})
            validate_council_change(db, session_id, int(session["round_id"]), [member["lecturer_id"] for member in members], session["start_at"], session["end_at"])
            next_members = [{**member, "is_result_owner": int(member["lecturer_id"]) == lecturer_id} for member in members]
            council_id = create_council(db, int(session["round_id"]), next_members, created_by=_actor_id(db, user), reason="Result Owner reassignment", supersedes_council_id=int(session["council_id"]))
            db.execute(text("UPDATE sessions SET council_id = :council_id WHERE id = :session_id"), {"council_id": council_id, "session_id": session_id})
            after_recipients = affected_schedule_recipients(db, version_id)
            _queue_schedule_changed(
                db,
                before_recipients | after_recipients,
                round_id=int(session["round_id"]),
                source_version_id=version_id,
                replacement_version_id=None,
                session_id=session_id,
                change_kind="COUNCIL_REPLACED",
                reason="Result Owner reassignment",
            )
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'RESULT_OWNER_ASSIGNED', 'session', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "after_json": _json({"lecturer_id": lecturer_id, "version_id": version_id, "before_council_id": session["council_id"], "after_council_id": council_id})})
        return {"version_id": version_id, "session_id": session_id, "result_owner_id": lecturer_id}
    except CouncilError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc), **(exc.details or {})}) from exc


@router.post("/schedule/versions/{version_id}/sessions/{session_id}/edit", response_model=SessionEditResponse)
def edit_draft_session(version_id: int, session_id: int, payload: SessionEditPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    version = db.execute(text("SELECT round_id, status FROM schedule_versions WHERE id = :id"), {"id": version_id}).mappings().one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
    ensure_round_semester_writable(db, int(version["round_id"]))
    if version["status"] != "DRAFT":
        raise HTTPException(status_code=422, detail={"code": "DRAFT_EDIT_REQUIRED", "message": "Only a draft version can be edited."})
    context, _, timeslots, _ = _round_input(db, version["round_id"])
    rows = _assignment_rows(db, version_id)
    try:
        edited, change = _edited_rows(rows, session_id, payload, timeslots)
        validation = validate_schedule(_to_domain_sessions(edited), context)
        if not validation.valid:
            raise HTTPException(
                status_code=422,
                detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [violation.__dict__ for violation in validation.violations]},
            )
        owner_id = _owner_for_edit(db, session_id=session_id, round_id=version["round_id"], reviewer_ids=change["after"]["reviewer_ids"], requested_owner_id=payload.result_owner_id)
        prepared_before = change["before"]
        db.commit()
        with db.begin():
            ensure_round_semester_writable(db, int(version["round_id"]))
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version["round_id"]})
            locked_version = db.execute(
                text("SELECT round_id, status FROM schedule_versions WHERE id = :id FOR UPDATE"),
                {"id": version_id},
            ).mappings().one_or_none()
            if locked_version is None or locked_version["status"] != "DRAFT":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "DRAFT_EDIT_CONCURRENT_UPDATE", "message": "The draft version changed while this request was being prepared."},
                )
            fresh_context, _, fresh_timeslots, _ = _round_input(db, locked_version["round_id"])
            fresh_rows = _assignment_rows(db, version_id)
            fresh_target = next((row for row in fresh_rows if row["id"] == session_id), None)
            compared_fields = ("timeslot_id", "start_at", "end_at", "reviewer_ids", "result_owner_ids")
            if fresh_target is None or any(fresh_target[field] != prepared_before[field] for field in compared_fields):
                raise HTTPException(
                    status_code=409,
                    detail={"code": "DRAFT_EDIT_CONCURRENT_UPDATE", "message": "The session changed while this request was being prepared."},
                )
            edited, change = _edited_rows(fresh_rows, session_id, payload, fresh_timeslots)
            validation = validate_schedule(_to_domain_sessions(edited), fresh_context)
            if not validation.valid:
                raise HTTPException(
                    status_code=422,
                    detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [violation.__dict__ for violation in validation.violations]},
                )
            owner_id = _owner_for_edit(db, session_id=session_id, round_id=locked_version["round_id"], reviewer_ids=change["after"]["reviewer_ids"], requested_owner_id=payload.result_owner_id)
            db.execute(text("UPDATE schedule_assignments SET timeslot_id=:timeslot_id,start_at=:start_at,end_at=:end_at WHERE id=:assignment_id AND schedule_version_id=:version_id"), {"timeslot_id": change["after"]["timeslot_id"], "start_at": change["after"]["start_at"], "end_at": change["after"]["end_at"], "assignment_id": session_id, "version_id": version_id})
            db.execute(text("DELETE FROM schedule_assignment_reviewers WHERE assignment_id=:assignment_id"), {"assignment_id": session_id})
            names = db.execute(text("SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id WHERE l.id = ANY(:ids)"), {"ids": list(change["after"]["reviewer_ids"]) or [0]}).all()
            name_map = {row[0]: row[1] for row in names}
            for lecturer_id in change["after"]["reviewer_ids"]:
                db.execute(text("INSERT INTO schedule_assignment_reviewers (assignment_id, lecturer_id, is_result_owner, snapshot_name) VALUES (:assignment_id, :lecturer_id, :is_owner, :snapshot_name)"), {"assignment_id": session_id, "lecturer_id": lecturer_id, "is_owner": lecturer_id == owner_id, "snapshot_name": name_map.get(lecturer_id, str(lecturer_id))})
            actor_id = _actor_id(db, user)
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'SCHEDULE_SESSION_EDITED', 'session', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(session_id), "reason": payload.reason.strip(), "before_json": _json(change["before"]), "after_json": _json(change["after"])})
        return {"session_id": session_id, "assignment_id": session_id, "version_id": version_id, "status": "UPDATED"}
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc


@router.post(CONTROLLED_CHANGE_PATH, response_model=ControlledChangeResponse)
def controlled_change(
    round_scope: int | None = Query(default=None, include_in_schema=False),
    *,
    version_id: int,
    session_id: int,
    payload: ControlledChangePayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    """Lock round/version/session/room/reviewer resources. Branches: reviewer-only, time/room, or mixed."""
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    reviewer_changed = False
    topology_changed = False
    try:
        with db.begin():
            version_ref = db.execute(
                text("SELECT round_id FROM schedule_versions WHERE id = :id"),
                {"id": version_id},
            ).mappings().one_or_none()
            if version_ref is None:
                raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
            # Controlled-change lock order is Round -> ScheduleVersion -> Sessions
            # -> Rooms -> Reviewers. The initial version lookup is non-locking so
            # the round can be serialized before the version row is locked.
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version_ref["round_id"]})
            ensure_round_semester_writable(db, int(version_ref["round_id"]))
            version = db.execute(
                text("SELECT * FROM schedule_versions WHERE id = :id AND round_id = :round_id FOR UPDATE"),
                {"id": version_id, "round_id": version_ref["round_id"]},
            ).mappings().one_or_none()
            if version is None:
                raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
            locked_source_ids = [
                int(row[0])
                for row in db.execute(
                    text("SELECT id FROM sessions WHERE schedule_version_id = :version_id ORDER BY id FOR UPDATE"),
                    {"version_id": version_id},
                ).all()
            ]
            if version["status"] != "PUBLISHED":
                raise HTTPException(status_code=422, detail={"code": "CONTROLLED_CHANGE_REQUIRES_PUBLISHED", "message": "Controlled change is only for a published version."})
            context, _, timeslots, _ = _round_input(db, version["round_id"])
            rows = _session_rows(db, version_id)
            target = next((row for row in rows if row["id"] == session_id), None)
            if target is None:
                raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist in this version."})
            if target["status"] in {"COMPLETED", "GROUP_ABSENT", "POSTPONED", "CANCELLED"}:
                raise HTTPException(status_code=422, detail={"code": "SESSION_IMMUTABLE", "message": "This session's history is immutable."})
            current_owner_ids = set(target.get("result_owner_ids", ()))
            reviewer_changed = payload.reviewer_ids is not None and set(payload.reviewer_ids) != set(target["reviewer_ids"])
            reviewer_changed = reviewer_changed or (payload.result_owner_id is not None and payload.result_owner_id not in current_owner_ids)
            topology_changed = (payload.timeslot_id is not None and payload.timeslot_id != target["timeslot_id"]) or (payload.room_id is not None and payload.room_id != target["room_id"])
            if not reviewer_changed and not topology_changed:
                raise HTTPException(status_code=422, detail={"code": "CONTROLLED_CHANGE_EMPTY", "message": "Provide a reviewer, result-owner, time, or room change."})
            edited, change = _edited_rows(rows, session_id, payload, timeslots)
            before_recipients = affected_schedule_recipients(db, version_id)
            validation = validate_schedule(_to_domain_sessions(edited), context)
            if not validation.valid:
                raise HTTPException(status_code=422, detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [item.__dict__ for item in validation.violations]})
            owner_id = _owner_for_edit(db, session_id=session_id, round_id=version["round_id"], reviewer_ids=change["after"]["reviewer_ids"], requested_owner_id=payload.result_owner_id)
            # reviewer-only: preserve the published Version and repoint only one Session.
            if reviewer_changed and not topology_changed:
                names = db.execute(text("SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id=l.account_id WHERE l.id=ANY(:ids)"), {"ids": list(change["after"]["reviewer_ids"]) or [0]}).all()
                name_map = {row[0]: row[1] for row in names}
                next_members = [{"lecturer_id": lecturer_id, "is_result_owner": lecturer_id == owner_id, "snapshot_name": name_map.get(lecturer_id, str(lecturer_id))} for lecturer_id in change["after"]["reviewer_ids"]]
                validate_council_change(db, session_id, int(version["round_id"]), change["after"]["reviewer_ids"], target["start_at"], target["end_at"])
                council_id = create_council(db, int(version["round_id"]), next_members, created_by=_actor_id(db, user), reason=payload.reason.strip(), supersedes_council_id=int(target["council_id"]))
                db.execute(text("UPDATE sessions SET council_id=:council_id WHERE id=:session_id"), {"council_id": council_id, "session_id": session_id})
                after_recipients = affected_schedule_recipients(db, version_id)
                db.execute(text("INSERT INTO schedule_change_records (round_id,schedule_version_id,session_id,actor_id,reason,before_json,after_json) VALUES (:round_id,:version_id,:session_id,:actor_id,:reason,CAST(:before_json AS JSONB),CAST(:after_json AS JSONB))"), {"round_id": version["round_id"], "version_id": version_id, "session_id": session_id, "actor_id": _actor_id(db, user), "reason": payload.reason.strip(), "before_json": _json({"council_id": target["council_id"]}), "after_json": _json({"council_id": council_id})})
                db.execute(text("INSERT INTO audit_events (actor_id,action,entity_type,entity_id,reason,before_json,after_json) VALUES (:actor_id,'COUNCIL_REPLACED','session',:entity_id,:reason,CAST(:before_json AS JSONB),CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "reason": payload.reason.strip(), "before_json": _json({"council_id": target["council_id"]}), "after_json": _json({"council_id": council_id})})
                _queue_schedule_changed(
                    db,
                    before_recipients | after_recipients,
                    round_id=int(version["round_id"]),
                    source_version_id=version_id,
                    replacement_version_id=None,
                    session_id=session_id,
                    change_kind="COUNCIL_REPLACED",
                    reason=payload.reason.strip(),
                )
                return {"change_kind": "COUNCIL_REPLACED", "schedule_version_id": version_id, "replacement_version_id": None, "session_id": session_id, "status": "PUBLISHED", "before_council_id": target["council_id"], "after_council_id": council_id, "version_id": version_id, "source_version_id": version_id}
            # time/room and mixed changes retain the PUBLISHED-to-PUBLISHED clone path.
            lock_room_ids(db, [row["room_id"] for row in edited if row.get("room_id") is not None])
            lock_reviewer_ids(db, [reviewer_id for row in edited for reviewer_id in row["reviewer_ids"]])
            source_session_ids = locked_source_ids
            for row in edited:
                if row.get("room_id") is not None:
                    conflict = find_room_conflict(db, int(row["room_id"]), row["start_at"], row["end_at"], exclude_session_ids=source_session_ids)
                    if conflict is not None:
                        raise HTTPException(status_code=409, detail={"code": "ROOM_CONFLICT", "message": "Controlled change conflicts with another live room assignment."})
                validate_council_change(db, int(row["id"]), int(version["round_id"]), row["reviewer_ids"], row["start_at"], row["end_at"], exclude_session_ids=source_session_ids)
            new_version_no = db.execute(text("SELECT COALESCE(MAX(version_no),0)+1 FROM schedule_versions WHERE round_id=:round_id"), {"round_id": version["round_id"]}).scalar_one()
            new_version_id = db.execute(text("INSERT INTO schedule_versions (round_id,version_no,status,activated_at,input_snapshot,algorithm_parameters,random_seed,solver_status,total_score,soft_scores,created_by) VALUES (:round_id,:version_no,'PUBLISHED',now(),CAST(:snapshot AS JSONB),CAST(:parameters AS JSONB),:seed,'CONTROLLED_CHANGE',:score,CAST(:soft_scores AS JSONB),:created_by) RETURNING id"), {"round_id": version["round_id"], "version_no": new_version_no, "snapshot": _json(version["input_snapshot"]), "parameters": _json(version["algorithm_parameters"]), "seed": version["random_seed"], "score": version["total_score"], "soft_scores": _json(version["soft_scores"]), "created_by": _actor_id(db, user)}).scalar_one()
            new_session_ids: dict[int, int] = {}
            after_target_council = target["council_id"]
            for row in edited:
                assignment_id = db.execute(text("INSERT INTO schedule_assignments(schedule_version_id,group_id,project_id,timeslot_id,start_at,end_at) VALUES (:version_id,:group_id,:project_id,:timeslot_id,:start_at,:end_at) RETURNING id"), {"version_id": new_version_id, **{key: row[key] for key in ("group_id", "project_id", "timeslot_id", "start_at", "end_at")}}).scalar_one()
                council_id = int(row["council_id"]) if "council_id" in row else int(next(item["council_id"] for item in rows if item["id"] == row["id"]))
                if row["id"] == session_id and reviewer_changed:
                    names = db.execute(text("SELECT l.id,a.display_name FROM lecturers l JOIN accounts a ON a.id=l.account_id WHERE l.id=ANY(:ids)"), {"ids": list(row["reviewer_ids"]) or [0]}).all()
                    name_map = {item[0]: item[1] for item in names}
                    council_id = create_council(db, int(version["round_id"]), [{"lecturer_id": lecturer_id, "is_result_owner": lecturer_id == owner_id, "snapshot_name": name_map.get(lecturer_id, str(lecturer_id))} for lecturer_id in row["reviewer_ids"]], created_by=_actor_id(db, user), reason=payload.reason.strip(), supersedes_council_id=council_id)
                    after_target_council = council_id
                new_id = db.execute(text("INSERT INTO sessions(schedule_version_id,group_id,timeslot_id,room_id,council_id,start_at,end_at,status) VALUES (:version_id,:group_id,:timeslot_id,:room_id,:council_id,:start_at,:end_at,'SCHEDULED') RETURNING id"), {"version_id": new_version_id, "group_id": row["group_id"], "timeslot_id": row["timeslot_id"], "room_id": row["room_id"], "council_id": council_id, "start_at": row["start_at"], "end_at": row["end_at"]}).scalar_one()
                new_session_ids[row["id"]] = new_id
                for member in load_council_members(db, council_id):
                    db.execute(text("INSERT INTO schedule_assignment_reviewers(assignment_id,lecturer_id,is_result_owner,snapshot_name) VALUES (:assignment_id,:lecturer_id,:is_owner,:snapshot_name)"), {"assignment_id": assignment_id, "lecturer_id": member["lecturer_id"], "is_owner": member["is_result_owner"], "snapshot_name": member["snapshot_name"]})
                source_result = db.execute(
                    text("SELECT * FROM session_results WHERE session_id = :session_id"),
                    {"session_id": row["id"]},
                ).mappings().one_or_none()
                if source_result is not None:
                    new_result_id = db.execute(
                        text(
                            "INSERT INTO session_results "
                            "(session_id,outcome,note,entered_by,entered_at,correction_reason,before_json,after_json,remediation_due_at,verifier_lecturer_id,verify_status,before_group_status,after_group_status) "
                            "VALUES (:session_id,:outcome,:note,:entered_by,:entered_at,:correction_reason,CAST(:before_json AS JSONB),CAST(:after_json AS JSONB),:remediation_due_at,:verifier_lecturer_id,:verify_status,CAST(:before_group_status AS group_status),CAST(:after_group_status AS group_status)) "
                            "RETURNING id"
                        ),
                        {
                            "session_id": new_id,
                            "outcome": source_result["outcome"],
                            "note": source_result["note"],
                            "entered_by": source_result["entered_by"],
                            "entered_at": source_result["entered_at"],
                            "correction_reason": source_result["correction_reason"],
                            "before_json": _json(source_result["before_json"]) if source_result["before_json"] is not None else None,
                            "after_json": _json(source_result["after_json"]) if source_result["after_json"] is not None else None,
                            "remediation_due_at": source_result["remediation_due_at"],
                            "verifier_lecturer_id": source_result["verifier_lecturer_id"],
                            "verify_status": source_result["verify_status"],
                            "before_group_status": source_result["before_group_status"],
                            "after_group_status": source_result["after_group_status"],
                        },
                    ).scalar_one()
                    source_case = db.execute(
                        text("SELECT * FROM remediation_cases WHERE session_result_id = :result_id"),
                        {"result_id": source_result["id"]},
                    ).mappings().one_or_none()
                    if source_case is not None:
                        db.execute(
                            text(
                                "INSERT INTO remediation_cases "
                                "(session_result_id,group_id,due_at,status,verifier_lecturer_id,verified_at,note) "
                                "VALUES (:session_result_id,:group_id,:due_at,:status,:verifier_lecturer_id,:verified_at,:note)"
                            ),
                            {
                                "session_result_id": new_result_id,
                                "group_id": source_case["group_id"],
                                "due_at": source_case["due_at"],
                                "status": source_case["status"],
                                "verifier_lecturer_id": source_case["verifier_lecturer_id"],
                                "verified_at": source_case["verified_at"],
                                "note": source_case["note"],
                            },
                        )
            after_recipients = affected_schedule_recipients(db, new_version_id)
            db.execute(text("UPDATE schedule_versions SET status='DISCARDED' WHERE id=:id"), {"id": version_id})
            db.execute(text("INSERT INTO schedule_change_records(round_id,schedule_version_id,session_id,actor_id,reason,before_json,after_json) VALUES (:round_id,:version_id,:session_id,:actor_id,:reason,CAST(:before_json AS JSONB),CAST(:after_json AS JSONB))"), {"round_id": version["round_id"], "version_id": new_version_id, "session_id": session_id, "actor_id": _actor_id(db, user), "reason": payload.reason.strip(), "before_json": _json({"council_id": target["council_id"], "version_id": version_id}), "after_json": _json({"council_id": after_target_council, "version_id": new_version_id})})
            db.execute(text("INSERT INTO audit_events(actor_id,action,entity_type,entity_id,reason,before_json,after_json) VALUES (:actor_id,'SCHEDULE_CONTROLLED_CHANGE','schedule_version',:entity_id,:reason,CAST(:before_json AS JSONB),CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(new_version_id), "reason": payload.reason.strip(), "before_json": _json({"version_id": version_id}), "after_json": _json({"version_id": new_version_id, "change_kind": "MIXED_REPLACEMENT" if reviewer_changed else "VERSION_REPLACED"})})
            _queue_schedule_changed(
                db,
                before_recipients | after_recipients,
                round_id=int(version["round_id"]),
                source_version_id=version_id,
                replacement_version_id=new_version_id,
                session_id=session_id,
                change_kind="MIXED_REPLACEMENT" if reviewer_changed else "VERSION_REPLACED",
                reason=payload.reason.strip(),
            )
            return {"change_kind": "MIXED_REPLACEMENT" if reviewer_changed else "VERSION_REPLACED", "schedule_version_id": version_id, "replacement_version_id": new_version_id, "session_id": session_id, "status": "PUBLISHED", "before_council_id": target["council_id"], "after_council_id": after_target_council, "version_id": new_version_id, "source_version_id": version_id}
    except (DomainError, CouncilError) as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 422), detail={"code": exc.code, "message": str(exc), **(getattr(exc, "details", None) or {})}) from exc


@router.get("/sessions/{session_id}/replacement-suggestions", response_model=list[ReplacementSuggestionResponse])
def replacement_suggestions(session_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    row = db.execute(text("SELECT s.*, sv.round_id, a.project_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN groups g ON g.id = s.group_id JOIN schedule_assignments a ON a.schedule_version_id=s.schedule_version_id AND a.group_id=s.group_id WHERE s.id = :id"), {"id": session_id}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
    context, _, timeslots, reviewers = _round_input(db, row["round_id"])
    current_reviewers = {item[0] for item in db.execute(text("SELECT cm.lecturer_id FROM council_members cm JOIN sessions s ON s.council_id=cm.council_id WHERE s.id = :id"), {"id": session_id}).all()}
    existing_rows = [item for item in _session_rows(db, row["schedule_version_id"]) if item["id"] != session_id]
    candidates = generate_candidates(context, groups=[row["group_id"]], timeslots=timeslots, reviewers=reviewers)
    suggestions: list[dict[str, Any]] = []
    for candidate in candidates:
        overlap = current_reviewers.intersection(candidate.reviewer_ids)
        if overlap == current_reviewers:
            continue
        candidate_session = ScheduledSession(
            session_id=session_id,
            group_id=candidate.group_id,
            project_id=row["project_id"],
            timeslot_id=candidate.timeslot_id,
            room_id=None,
            start_at=candidate.start_at,
            end_at=candidate.end_at,
            reviewer_ids=candidate.reviewer_ids,
            day=candidate.day,
            part=candidate.part,
        )
        if not validate_schedule(_to_domain_sessions(existing_rows) + [candidate_session], context).valid:
            continue
        suggestions.append({"timeslot_id": candidate.timeslot_id, "room_id": None, "reviewer_ids": list(candidate.reviewer_ids), "replaces": sorted(current_reviewers - overlap)})
        if len(suggestions) >= 50:
            break
    return suggestions


@router.post("/sessions/{session_id}/postpone", response_model=ActionResponse, response_model_exclude_none=True)
def postpone_session(session_id: int, payload: RescheduleRequestPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        round_id_ref = db.execute(text("SELECT sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :id"), {"id": session_id}).scalar_one_or_none()
        if round_id_ref is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_id_ref})
        ensure_round_semester_writable(db, int(round_id_ref))
        session_row = db.execute(text("SELECT s.id, s.schedule_version_id, sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :id FOR UPDATE"), {"id": session_id}).mappings().one_or_none()
        if session_row is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
        updated = db.execute(text("UPDATE sessions SET status = 'POSTPONED' WHERE id = :id AND status = 'SCHEDULED' RETURNING id, status"), {"id": session_id}).mappings().one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_POSTPONABLE", "message": "Session is not in an operational state."})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason) VALUES (:actor_id, 'SESSION_POSTPONED', 'session', :entity_id, :reason)"), {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "reason": payload.reason.strip()})
        for recipient_id in affected_schedule_recipients(db, session_row["schedule_version_id"]):
            key = f"postponed:{session_id}:{recipient_id}"
            event_payload = _json({"session_id": session_id, "reason": payload.reason.strip(), "recipient_id": recipient_id})
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'SESSION_POSTPONED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('SESSION_POSTPONED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return dict(updated)


@router.post("/sessions/{session_id}/makeup", response_model=ActionResponse, response_model_exclude_none=True)
def create_makeup_session(session_id: int, payload: MakeupSessionPayload, db: Db, user: User) -> dict[str, Any]:
    """Create a new operational Session for a postponed Session (spec §73)."""
    _require(user, "ADMIN", "MANAGER")
    try:
        reason = require_change_reason(payload.reason)
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    try:
        with db.begin():
            original_ref = db.execute(
                text("SELECT sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :id"),
                {"id": session_id},
            ).scalar_one_or_none()
            if original_ref is None:
                raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": original_ref})
            ensure_round_semester_writable(db, int(original_ref))
            original = db.execute(
                text(
                    "SELECT s.id, s.status, s.schedule_version_id, s.group_id, s.council_id, a.project_id, "
                    "sv.round_id, sv.status AS version_status "
                    "FROM sessions s "
                    "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                    "JOIN schedule_assignments a ON a.schedule_version_id = s.schedule_version_id AND a.group_id = s.group_id "
                    "WHERE s.id = :id FOR UPDATE"
                ),
                {"id": session_id},
            ).mappings().one_or_none()
            if original is None:
                raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
            if original["version_status"] != "PUBLISHED":
                raise HTTPException(status_code=403, detail={"code": "SESSION_OUT_OF_SCOPE", "message": "Only a session in a published schedule can receive a make-up."})
            if original["status"] != "POSTPONED":
                raise HTTPException(status_code=409, detail={"code": "SESSION_NOT_POSTPONED", "message": "Only a postponed session can receive a make-up."})
            existing_makeup = db.execute(
                text("SELECT id FROM sessions WHERE makeup_of_session_id = :id FOR UPDATE"),
                {"id": session_id},
            ).scalar_one_or_none()
            if existing_makeup is not None:
                raise HTTPException(status_code=409, detail={"code": "MAKEUP_ALREADY_EXISTS", "message": "This session already has a make-up session."})
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": original["round_id"]})
            db.execute(text("SELECT id FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": original["schedule_version_id"]})
            context, _, timeslots, _ = _round_input(db, original["round_id"])
            slot = next((item for item in timeslots if item[0] == payload.timeslot_id), None)
            if slot is None:
                raise HTTPException(status_code=404, detail={"code": "TIMESLOT_NOT_FOUND", "message": "Timeslot does not belong to this round."})
            _, start_at, end_at, _, _ = slot
            original_members = load_council_members(db, int(original["council_id"]))
            original_owner_ids = {int(member["lecturer_id"]) for member in original_members if member["is_result_owner"]}
            if payload.reviewer_ids is not None:
                normalized_ids = sorted(set(payload.reviewer_ids))
                names = db.execute(
                    text("SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id WHERE l.id = ANY(:ids)"),
                    {"ids": normalized_ids or [0]},
                ).all()
                name_map = {row[0]: row[1] for row in names}
                members = [
                    {
                        "lecturer_id": lecturer_id,
                        "assignment": "REVIEWER",
                        "is_result_owner": lecturer_id in original_owner_ids,
                        "snapshot_name": name_map.get(lecturer_id, str(lecturer_id)),
                    }
                    for lecturer_id in normalized_ids
                ]
            else:
                members = original_members
                normalized_ids = [int(member["lecturer_id"]) for member in members]
            reviewer_ids = tuple(normalized_ids)
            candidate = ScheduledSession(
                session_id=-1,
                group_id=original["group_id"],
                project_id=original["project_id"],
                timeslot_id=payload.timeslot_id,
                room_id=None,
                start_at=start_at,
                end_at=end_at,
                reviewer_ids=reviewer_ids,
                day=str(start_at.date()),
                part="AM" if start_at.hour < 13 else "PM",
            )
            existing_rows = [row for row in _session_rows(db, original["schedule_version_id"]) if row["id"] != session_id]
            validation = validate_schedule(_to_domain_sessions(existing_rows) + [candidate], context)
            if not validation.valid:
                raise HTTPException(
                    status_code=422,
                    detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [violation.__dict__ for violation in validation.violations]},
                )
            validate_council_change(
                db,
                session_id,
                int(original["round_id"]),
                reviewer_ids,
                start_at,
                end_at,
                exclude_session_ids=[session_id],
            )
            room_id = payload.room_id
            if room_id is not None:
                lock_room_ids(db, [room_id])
                room = allowed_room(db, original["round_id"], room_id)
                if room is None:
                    exists = db.execute(text("SELECT id, active FROM rooms WHERE id = :id"), {"id": room_id}).mappings().one_or_none()
                    if exists is None:
                        raise HTTPException(status_code=404, detail={"code": "ROOM_NOT_FOUND", "message": "Room does not exist."})
                    if not exists["active"]:
                        raise HTTPException(status_code=422, detail={"code": "ROOM_INACTIVE", "message": "Room is not active."})
                    raise HTTPException(status_code=422, detail={"code": "ROOM_TYPE_NOT_ALLOWED", "message": "Room type is not allowed for this round."})
                room_conflict = find_room_conflict(db, room_id, start_at, end_at)
                if room_conflict is not None:
                    raise HTTPException(status_code=409, detail={"code": "ROOM_CONFLICT", "message": "Room is already occupied during this session."})
            actor_id = _actor_id(db, user)
            council_id = create_council(
                db,
                int(original["round_id"]),
                members,
                created_by=actor_id,
                reason=reason,
            )
            try:
                new_session_id = db.execute(
                    text(
                        "INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, council_id, start_at, end_at, status, makeup_of_session_id) "
                        "VALUES (:version_id, :group_id, :timeslot_id, :room_id, :council_id, :start_at, :end_at, 'SCHEDULED', :makeup_of_session_id) RETURNING id"
                    ),
                    {
                        "version_id": original["schedule_version_id"],
                        "group_id": original["group_id"],
                        "timeslot_id": payload.timeslot_id,
                        "room_id": room_id,
                        "council_id": council_id,
                        "start_at": start_at,
                        "end_at": end_at,
                        "makeup_of_session_id": session_id,
                    },
                ).scalar_one()
            except IntegrityError as exc:
                raise HTTPException(status_code=409, detail={"code": "ROOM_CONFLICT", "message": "Room is already occupied during this session."}) from exc
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) "
                    "VALUES (:actor_id, 'SESSION_MAKEUP_CREATED', 'session', :entity_id, :reason, CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(new_session_id),
                    "reason": reason,
                    "after_json": _json({
                        "makeup_of_session_id": session_id,
                        "timeslot_id": payload.timeslot_id,
                        "room_id": room_id,
                        "council_id": council_id,
                        "reviewer_ids": list(reviewer_ids),
                    }),
                },
            )
            for recipient_id in affected_schedule_recipients(db, original["schedule_version_id"]):
                key = f"makeup:{new_session_id}:{recipient_id}"
                event_payload = _json({"session_id": new_session_id, "makeup_of_session_id": session_id, "reason": reason, "recipient_id": recipient_id})
                db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'SESSION_MAKEUP_CREATED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
                db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('SESSION_MAKEUP_CREATED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    except CouncilError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc), **(exc.details or {})}) from exc
    return {"id": new_session_id, "session_id": new_session_id, "status": "SCHEDULED", "makeup_of_session_id": session_id}


@router.post("/sessions/{session_id}/group-absent", response_model=ActionResponse, response_model_exclude_none=True)
def mark_group_absent(session_id: int, payload: RescheduleRequestPayload, db: Db, user: User) -> dict[str, Any]:
    """Mark a published operational session absent when its group does not attend."""
    _require(user, "ADMIN", "MANAGER")
    try:
        reason = require_change_reason(payload.reason)
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    with db.begin():
        session_ref = db.execute(
            text("SELECT sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :id"),
            {"id": session_id},
        ).scalar_one_or_none()
        if session_ref is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": session_ref})
        ensure_round_semester_writable(db, int(session_ref))
        session_row = db.execute(
            text(
                "SELECT s.id, s.status, s.schedule_version_id, sv.round_id, sv.status AS version_status "
                "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                "WHERE s.id = :id FOR UPDATE"
            ),
            {"id": session_id},
        ).mappings().one_or_none()
        if session_row is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
        if session_row["version_status"] != "PUBLISHED":
            raise HTTPException(status_code=403, detail={"code": "SESSION_OUT_OF_SCOPE", "message": "Only a published session can be marked absent."})
        updated = db.execute(
            text("UPDATE sessions SET status = 'GROUP_ABSENT' WHERE id = :id AND status = 'SCHEDULED' RETURNING id, status"),
            {"id": session_id},
        ).mappings().one_or_none()
        if updated is None:
            raise HTTPException(status_code=422, detail={"code": "SESSION_NOT_ABSENTABLE", "message": "Only a scheduled session can be marked absent."})
        actor_id = _actor_id(db, user)
        db.execute(
            text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'GROUP_MARKED_ABSENT', 'session', :entity_id, :reason, CAST(:after_json AS JSONB))"),
            {"actor_id": actor_id, "entity_id": str(session_id), "reason": reason, "after_json": _json({"status": "GROUP_ABSENT", "reason": reason})},
        )
        for recipient_id in affected_schedule_recipients(db, session_row["schedule_version_id"]):
            key = f"group-absent:{session_id}:{recipient_id}"
            event_payload = _json({"session_id": session_id, "reason": reason, "recipient_id": recipient_id})
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'GROUP_ABSENT', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('GROUP_ABSENT', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return {"id": session_id, "status": "GROUP_ABSENT"}


@router.post("/rounds/{round_id}/schedule/publish/{version_id}", response_model=PublishResponse)
def publish_schedule(round_id: int, version_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        # Publish lifecycle lock order is Round -> ScheduleVersion -> Sessions -> Rooms.
        ensure_round_semester_writable(db, round_id)
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_id})
        version = (
            db.execute(
                text(
                    "SELECT * FROM schedule_versions WHERE id = :id AND round_id = :round_id FOR UPDATE"
                ),
                {"id": version_id, "round_id": round_id},
            )
            .mappings()
            .one_or_none()
        )
        if version is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."},
            )
        context, _, _, _ = _round_input(db, round_id)
        try:
            if version["status"] != "ACTIVE":
                raise DomainError("VERSION_NOT_ACTIVE", "Activate the selected version before publishing it.")
            assignment_count = db.execute(text(
                "SELECT COUNT(*) FROM schedule_assignments WHERE schedule_version_id=:version_id"
            ), {"version_id": version_id}).scalar_one()
            session_count = db.execute(text(
                "SELECT COUNT(*) FROM sessions WHERE schedule_version_id=:version_id"
            ), {"version_id": version_id}).scalar_one()
            incomplete = assignment_count != session_count or db.execute(text(
                "SELECT 1 FROM schedule_assignments a WHERE a.schedule_version_id=:version_id AND ("
                "(SELECT COUNT(*) FROM sessions s WHERE s.schedule_version_id=a.schedule_version_id AND s.group_id=a.group_id) <> 1 OR "
                "(SELECT COUNT(*) FROM schedule_assignment_reviewers ar WHERE ar.assignment_id=a.id) <> "
                "(SELECT COUNT(*) FROM council_members cm JOIN sessions s ON s.council_id=cm.council_id WHERE s.schedule_version_id=a.schedule_version_id AND s.group_id=a.group_id) OR "
                "EXISTS (SELECT lecturer_id FROM schedule_assignment_reviewers ar WHERE ar.assignment_id=a.id EXCEPT SELECT cm.lecturer_id FROM council_members cm JOIN sessions s ON s.council_id=cm.council_id WHERE s.schedule_version_id=a.schedule_version_id AND s.group_id=a.group_id)"
                ") LIMIT 1"
            ), {"version_id": version_id}).first()
            if incomplete:
                raise DomainError("MATERIALIZATION_INCOMPLETE", "Every assignment must have exactly one materialized Session and reviewer set before publishing.")
            # Room readiness reads round_room_types and raises ROOM_INACTIVE,
            # ROOM_TYPE_NOT_ALLOWED, or ROOM_CONFLICT.
            validate_publish_room_readiness(db, round_id, version_id)
            ensure_publishable(
                str(version["status"]),
                validate_schedule(
                    _to_domain_sessions(_session_rows(db, version_id)), context
                ).valid,
            )
        except (DomainError, RoomAssignmentError) as exc:
            raise HTTPException(
                status_code=getattr(exc, "status_code", 422), detail={"code": exc.code, "message": str(exc), **(getattr(exc, "details", None) or {})}
            ) from exc
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'DISCARDED' WHERE round_id = :round_id AND status = 'PUBLISHED' AND id <> :id"
            ),
            {"round_id": round_id, "id": version_id},
        )
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'PUBLISHED', activated_at = now() WHERE id = :id"
            ),
            {"id": version_id},
        )
        db.execute(
            text("UPDATE rounds SET status = 'PUBLISHED' WHERE id = :round_id"),
            {"round_id": round_id},
        )
        db.execute(
            text("UPDATE sessions SET status = 'SCHEDULED' WHERE schedule_version_id = :version_id AND status = 'PLANNED'"),
            {"version_id": version_id},
        )
        recipients = [(recipient_id,) for recipient_id in sorted(affected_schedule_recipients(db, version_id))]
        for (recipient_id,) in recipients:
            key = f"publish:{version_id}:{recipient_id}"
            db.execute(
                text(
                    "INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'SCHEDULE_PUBLISHED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
                ),
                {
                    "recipient_id": recipient_id,
                    "payload": _json({"round_id": round_id, "version_id": version_id}),
                    "key": key,
                },
            )
            db.execute(
                text(
                    "INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('SCHEDULE_PUBLISHED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
                ),
                {
                    "payload": _json(
                        {
                            "round_id": round_id,
                            "version_id": version_id,
                            "recipient_id": recipient_id,
                        }
                    ),
                    "key": key,
                },
            )
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'SCHEDULE_PUBLISHED', 'schedule_version', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": _actor_id(db, user),
                "entity_id": str(version_id),
                "after_json": _json({"round_id": round_id, "recipient_count": len(recipients)}),
            },
        )
    return {
        "round_id": round_id,
        "version_id": version_id,
        "status": "PUBLISHED",
        "recipient_count": len(recipients),
    }


@router.post("/sessions/{session_id}/reschedule-requests", status_code=status.HTTP_201_CREATED, response_model=ActionResponse, response_model_exclude_none=True)
def request_reschedule(
    session_id: int, payload: RescheduleRequestPayload, db: Db, user: User
) -> dict[str, Any]:
    require_change_reason(payload.reason)
    _require(user, "MANAGER", "LECTURER", "STUDENT")
    row = db.execute(
        text(
            "SELECT s.group_id, sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE s.id = :id"
        ),
        {"id": session_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
    assigned = user.role == "MANAGER" or can_read_session(db, user, session_id)
    ensure_reschedule_allowed(role=user.role, assigned=assigned, is_leader=is_active_group_leader(db, user, row["group_id"]))
    db.commit()
    with db.begin():
        ensure_round_semester_writable(db, int(row["round_id"]))
        actor_id = _actor_id(db, user)
        request_id = db.execute(
            text(
                "INSERT INTO reschedule_requests (session_id, requested_by, reason) VALUES (:session_id, :actor_id, :reason) RETURNING id"
            ),
            {"session_id": session_id, "actor_id": actor_id, "reason": payload.reason.strip()},
        ).scalar_one()
        for (recipient_id,) in db.execute(text("SELECT account_id FROM account_roles WHERE role = 'MANAGER'" )).all():
            key = f"reschedule-request:{request_id}:{recipient_id}"
            event_payload = _json({"request_id": request_id, "session_id": session_id, "reason": payload.reason.strip(), "recipient_id": recipient_id})
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'RESCHEDULE_REQUESTED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('RESCHEDULE_REQUESTED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return {"id": request_id, "status": "REQUESTED"}


@router.post("/reschedule-requests/{request_id}/decision", response_model=ActionResponse, response_model_exclude_none=True)
def decide_reschedule(
    request_id: int, payload: RescheduleDecisionPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        request_round = db.execute(
            text("SELECT sv.round_id FROM reschedule_requests rr JOIN sessions s ON s.id = rr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE rr.id = :id FOR UPDATE"),
            {"id": request_id},
        ).scalar_one_or_none()
        if request_round is not None:
            ensure_round_semester_writable(db, int(request_round))
        actor_id = _actor_id(db, user)
        updated = (
            db.execute(
                text(
                    "UPDATE reschedule_requests SET status = CAST(:decision AS reschedule_status), reviewed_by = :actor_id, reviewed_at = now(), decision_note = :note WHERE id = :id AND status = 'REQUESTED' RETURNING id, status, decision_note"
                ),
                {"decision": payload.decision, "actor_id": actor_id, "id": request_id, "note": payload.note.strip()},
            )
            .mappings()
            .one_or_none()
        )
        if updated is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "RESCHEDULE_REQUEST_NOT_FOUND",
                    "message": "Open request does not exist.",
                },
            )
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'RESCHEDULE_DECISION', 'reschedule_request', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(request_id), "reason": payload.note.strip(), "after_json": _json({"decision": payload.decision})})
        requester_id = db.execute(text("SELECT requested_by FROM reschedule_requests WHERE id = :id"), {"id": request_id}).scalar_one_or_none()
        if requester_id is not None:
            event_payload = _json({"request_id": request_id, "decision": payload.decision, "note": payload.note.strip(), "recipient_id": requester_id})
            key = f"reschedule-decision:{request_id}:{requester_id}"
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'RESCHEDULE_DECISION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": requester_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('RESCHEDULE_DECISION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return dict(updated)


@router.post("/rounds/{round_id}/operation", response_model=ActionResponse, response_model_exclude_none=True)
def operate_round(
    round_id: int, payload: RoundOperationPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        ensure_round_semester_writable(db, round_id)
        row = (
            db.execute(
                text("SELECT status FROM rounds WHERE id = :id FOR UPDATE"), {"id": round_id}
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."},
            )
        try:
            after = transition_round(RoundStatus(row["status"]), RoundStatus(payload.action))
        except DomainError as exc:
            raise HTTPException(
                status_code=422, detail={"code": exc.code, "message": str(exc)}
            ) from exc
        actor_id = _actor_id(db, user)
        db.execute(
            text("UPDATE rounds SET status = CAST(:status AS round_status) WHERE id = :id"),
            {"status": after.value, "id": round_id},
        )
        db.execute(
            text(
                "INSERT INTO round_operation_records (round_id, actor_id, action, reason, before_status, after_status) VALUES (:round_id, :actor_id, :action, :reason, :before_status, :after_status)"
            ),
            {
                "round_id": round_id,
                "actor_id": actor_id,
                "action": payload.action,
                "reason": payload.reason.strip(),
                "before_status": row["status"],
                "after_status": after.value,
            },
        )
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) "
                "VALUES (:actor_id, 'ROUND_OPERATION', 'round', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": actor_id,
                "entity_id": str(round_id),
                "reason": payload.reason.strip(),
                "before_json": _json({"status": row["status"]}),
                "after_json": _json({"status": after.value, "action": payload.action}),
            },
        )
        version_ids = [
            item[0]
            for item in db.execute(
                text("SELECT id FROM schedule_versions WHERE round_id = :round_id"),
                {"round_id": round_id},
            ).all()
        ]
        recipients: set[int] = set()
        for version_id in version_ids:
            recipients.update(affected_schedule_recipients(db, version_id))
        for recipient_id in recipients:
            key = f"round-operation:{round_id}:{payload.action}:{recipient_id}"
            event_payload = _json({"round_id": round_id, "action": payload.action, "reason": payload.reason.strip(), "recipient_id": recipient_id})
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'ROUND_OPERATION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('ROUND_OPERATION', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return {"round_id": round_id, "status": after.value}


def _json(value: Any) -> str:
    import json

    return json.dumps(value, default=str)
