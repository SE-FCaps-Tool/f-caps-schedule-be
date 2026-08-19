from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
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

router = APIRouter(prefix="/api/v1", tags=["schedule-operations"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


class ScheduleRunPayload(BaseModel):
    random_seed: int = 0
    time_limit_seconds: float = Field(default=10, gt=0, le=300)


class SessionEditPayload(BaseModel):
    timeslot_id: int | None = Field(default=None, gt=0)
    room_id: int | None = Field(default=None, gt=0)
    reviewer_ids: list[int] | None = None
    result_owner_id: int | None = Field(default=None, gt=0)
    reason: str = Field(min_length=1, max_length=1000)


class RescheduleRequestPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class RescheduleDecisionPayload(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    note: str = Field(min_length=1, max_length=1000)


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


def _round_input(
    db: Session, round_id: int
) -> tuple[
    RoundInput, list[int], list[tuple[int, datetime, datetime, str, str]], list[int], list[int]
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
    room_ids = [
        row[0]
        for row in db.execute(
            text("SELECT room_id FROM round_rooms WHERE round_id = :round_id ORDER BY room_id"),
            {"round_id": round_id},
        ).all()
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
            "SELECT sr.lecturer_id, COUNT(*) AS session_count "
            "FROM session_reviewers sr JOIN sessions s ON s.id = sr.session_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds previous_round ON previous_round.id = sv.round_id "
            "WHERE previous_round.semester_id = :semester_id AND previous_round.id <> :round_id "
            "AND sv.status IN ('VALID', 'PUBLISHED') GROUP BY sr.lecturer_id"
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
                "SELECT s.group_id, sr.lecturer_id FROM sessions s "
                "JOIN session_reviewers sr ON sr.session_id = s.id "
                "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                "JOIN rounds previous_round ON previous_round.id = sv.round_id "
                "WHERE s.group_id = ANY(:group_ids) AND previous_round.type = 'DEFENSE_1_1' "
                "AND sv.status IN ('VALID', 'PUBLISHED')"
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
    return input_data, [row["id"] for row in group_rows], timeslots, room_ids, reviewer_ids


def _session_rows(db: Session, version_id: int) -> list[dict[str, Any]]:
    sessions = (
        db.execute(
            text(
                "SELECT s.id, s.group_id, g.code AS group_code, g.project_id, s.timeslot_id, s.room_id, "
                "s.start_at, s.end_at, s.status "
                "FROM sessions s JOIN groups g ON g.id = s.group_id WHERE s.schedule_version_id = :version_id ORDER BY s.id"
            ),
            {"version_id": version_id},
        )
        .mappings()
        .all()
    )
    reviewers = db.execute(
        text(
            "SELECT sr.session_id, sr.lecturer_id, sr.is_result_owner, sr.snapshot_name "
            "FROM session_reviewers sr WHERE sr.schedule_version_id = :version_id ORDER BY sr.lecturer_id"
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
        "room_id": payload.room_id or target["room_id"],
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
        text("SELECT lecturer_id FROM session_reviewers WHERE session_id = :session_id AND is_result_owner = TRUE"),
        {"session_id": session_id},
    ).all()
    owner_id = requested_owner_id or (current_owner[0][0] if len(current_owner) == 1 else None)
    if owner_id is None or owner_id not in reviewer_ids:
        raise DomainError(
            "RESULT_OWNER_REQUIRED",
            "Exactly one Result Owner from the session Reviewers is required.",
        )
    return owner_id


@router.get("/rounds/{round_id}/schedule/versions")
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


@router.get("/schedule/versions/{version_id}")
def schedule_version_detail(version_id: int, db: Db, user: User) -> dict[str, Any]:
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
    sessions = _session_rows(db, version_id)
    if user.role not in {"ADMIN", "MANAGER"}:
        visible = visible_session_ids(db, user, version_id=version_id)
        sessions = [row for row in sessions if row["id"] in visible]
        if not sessions:
            raise HTTPException(status_code=403, detail="Schedule is outside the actor's scope.")
    return {**_version_ui(version), "sessions": sessions}


def _version_ui(row: Any) -> dict[str, Any]:
    payload = dict(row)
    payload["is_active"] = payload.get("activated_at") is not None and payload.get("status") in {"VALID", "PUBLISHED"}
    payload["ui_status"] = "ACTIVE" if payload["is_active"] else payload.get("status")
    return payload


@router.get("/schedule/versions/compare/{version_a}/{version_b}")
def compare_schedule_versions(version_a: int, version_b: int, db: Db, user: User) -> dict[str, Any]:
    """Return a stable, FE-friendly diff between two versions in one round."""
    _require(user, "ADMIN", "MANAGER")
    versions = db.execute(
        text("SELECT id, round_id, version_no, status, total_score, soft_scores, created_at FROM schedule_versions WHERE id = ANY(:ids)"),
        {"ids": [version_a, version_b]},
    ).mappings().all()
    if len(versions) != 2 or versions[0]["round_id"] != versions[1]["round_id"]:
        raise HTTPException(status_code=404, detail={"code": "VERSION_COMPARE_INVALID", "message": "Both versions must exist in the same round."})
    sessions = db.execute(
        text("SELECT schedule_version_id, group_id, timeslot_id, room_id FROM sessions WHERE schedule_version_id = ANY(:ids)"),
        {"ids": [version_a, version_b]},
    ).mappings().all()
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


@router.delete("/schedule/versions/{version_id}")
def delete_draft_version(version_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        row = db.execute(text("SELECT id, status, activated_at FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": version_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
        if row["activated_at"] is not None or row["status"] in {"PUBLISHED", "SUPERSEDED"}:
            raise HTTPException(status_code=409, detail={"code": "VERSION_DELETE_FORBIDDEN", "message": "Only an unused draft/valid version can be deleted."})
        dependency_count = db.execute(
            text(
                "SELECT "
                "(SELECT COUNT(*) FROM scheduler_jobs WHERE schedule_version_id = :id) + "
                "(SELECT COUNT(*) FROM schedule_change_records WHERE schedule_version_id = :id) + "
                "(SELECT COUNT(*) FROM sessions WHERE schedule_version_id = :id) + "
                "(SELECT COUNT(*) FROM session_reviewers WHERE schedule_version_id = :id)"
            ),
            {"id": version_id},
        ).scalar_one()
        if dependency_count:
            raise HTTPException(status_code=409, detail={"code": "VERSION_DELETE_HAS_DEPENDENCIES", "message": "Version has dependent schedule or audit records and cannot be deleted."})
        db.execute(text("DELETE FROM schedule_versions WHERE id = :id"), {"id": version_id})
    return {"id": version_id, "deleted": True}


@router.post("/rounds/{round_id}/schedule/run", status_code=status.HTTP_201_CREATED)
def run_scheduler(round_id: int, payload: ScheduleRunPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    try:
        with db.begin():
            round_status = db.execute(
                text("SELECT status FROM rounds WHERE id = :round_id FOR UPDATE"),
                {"round_id": round_id},
            ).scalar_one_or_none()
            if round_status is None:
                raise DomainError("ROUND_NOT_FOUND", "Round does not exist.")
            if str(round_status) in {"PUBLISHED", "ONGOING", "COMPLETED", "LOCKED", "CANCELLED"}:
                raise DomainError(
                    "SCHEDULE_RERUN_FORBIDDEN",
                    "A published or terminal round must use the controlled-change workflow.",
                )
            if str(round_status) == "POSTPONED":
                raise DomainError("ROUND_POSTPONED", "A postponed round must be reopened before scheduling.")
            if str(round_status) != "SCHEDULING":
                db.execute(
                    text("UPDATE rounds SET status = 'SCHEDULING' WHERE id = :round_id"),
                    {"round_id": round_id},
                )
            context, groups, timeslots, rooms, reviewers = _round_input(db, round_id)
            if not groups or not timeslots or not rooms or not reviewers:
                raise DomainError("ROUND_INPUTS_INCOMPLETE", "Round needs groups, timeslots, rooms and at least one available Reviewer before scheduling.")
            result = solve_schedule(
                context,
                groups=groups,
                timeslots=timeslots,
                rooms=rooms,
                reviewers=reviewers,
                time_limit_seconds=payload.time_limit_seconds,
                random_seed=payload.random_seed,
            )
            snapshot = build_input_snapshot(
                round_id=round_id,
                context=context,
                groups=groups,
                timeslots=[row[0] for row in timeslots],
                rooms=rooms,
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
                    "(:round_id, :version_no, 'VALID', CAST(:snapshot AS JSONB), CAST(:parameters AS JSONB), :seed, "
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
                session_id = db.execute(
                    text(
                        "INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at) "
                        "VALUES (:version_id, :group_id, :timeslot_id, :room_id, :start_at, :end_at) RETURNING id"
                    ),
                    {
                        "version_id": version_id,
                        "group_id": session.group_id,
                        "timeslot_id": session.timeslot_id,
                        "room_id": session.room_id,
                        "start_at": session.start_at,
                        "end_at": session.end_at,
                    },
                ).scalar_one()
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
                            "INSERT INTO session_reviewers (session_id, schedule_version_id, lecturer_id, is_result_owner, snapshot_name, start_at, end_at) "
                            "VALUES (:session_id, :version_id, :lecturer_id, :is_owner, :snapshot_name, :start_at, :end_at)"
                        ),
                        {
                            "session_id": session_id,
                            "version_id": version_id,
                            "lecturer_id": lecturer_id,
                            "is_owner": context.result_owner_mode and context.round_type in {"DEFENSE_1_1", "DEFENSE_2"} and reviewer_index == 0,
                            "snapshot_name": name_map.get(lecturer_id, str(lecturer_id)),
                            "start_at": session.start_at,
                            "end_at": session.end_at,
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
                text("UPDATE rounds SET status = 'SCHEDULED' WHERE id = :round_id"),
                {"round_id": round_id},
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
            "status": result.status,
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


@router.post("/rounds/{round_id}/groups/{group_id}/h11-waiver")
def grant_h11_waiver(round_id: int, group_id: int, payload: H11WaiverPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        attached = db.execute(text("SELECT 1 FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"), {"round_id": round_id, "group_id": group_id}).scalar_one_or_none()
        if attached is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_GROUP_NOT_FOUND", "message": "The group is not attached to this round."})
        actor_id = _actor_id(db, user)
        row = db.execute(text("INSERT INTO h11_waivers (round_id, group_id, granted_by, reason, active) VALUES (:round_id, :group_id, :actor_id, :reason, TRUE) ON CONFLICT (round_id, group_id) DO UPDATE SET granted_by = EXCLUDED.granted_by, reason = EXCLUDED.reason, active = TRUE, created_at = now() RETURNING id, active"), {"round_id": round_id, "group_id": group_id, "actor_id": actor_id, "reason": payload.reason.strip()}).mappings().one()
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) VALUES (:actor_id, 'H11_WAIVER_GRANTED', 'h11_waiver', :entity_id, :reason, CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": f"{round_id}:{group_id}", "reason": payload.reason.strip(), "after_json": _json({"active": True, "scope": "H11"})})
    return {"id": row["id"], "round_id": round_id, "group_id": group_id, "active": row["active"]}


@router.delete("/rounds/{round_id}/groups/{group_id}/h11-waiver")
def revoke_h11_waiver(round_id: int, group_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    with db.begin():
        updated = db.execute(text("UPDATE h11_waivers SET active = FALSE WHERE round_id = :round_id AND group_id = :group_id AND active = TRUE RETURNING id"), {"round_id": round_id, "group_id": group_id}).mappings().one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "H11_WAIVER_NOT_FOUND", "message": "Active H11 waiver does not exist."})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'H11_WAIVER_REVOKED', 'h11_waiver', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": f"{round_id}:{group_id}", "after_json": _json({"active": False})})
    return {"id": updated["id"], "round_id": round_id, "group_id": group_id, "active": False}


@router.post("/schedule/versions/{version_id}/activate")
def activate_schedule_version(version_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
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
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version["round_id"]})
        if version["status"] != "VALID":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "VERSION_NOT_VALID",
                    "message": "Only a valid version can become active.",
                },
            )
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'SUPERSEDED' WHERE round_id = :round_id AND status = 'VALID' AND id <> :id"
            ),
            {"round_id": version["round_id"], "id": version_id},
        )
        db.execute(
            text("UPDATE schedule_versions SET activated_at = now() WHERE id = :id"),
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
                "after_json": _json({"round_id": version["round_id"], "status": "VALID"}),
            },
        )
    return {"version_id": version_id, "status": "VALID"}


@router.post("/schedule/versions/{version_id}/sessions/{session_id}/result-owner")
def assign_result_owner(version_id: int, session_id: int, payload: ResultOwnerPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER")
    lecturer_id = payload.lecturer_id
    with db.begin():
        session = db.execute(text("SELECT s.status, r.type, r.result_owner_mode, s.group_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id WHERE s.id = :session_id AND s.schedule_version_id = :version_id FOR UPDATE"), {"session_id": session_id, "version_id": version_id}).mappings().one_or_none()
        if session is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist in this version."})
        if session["status"] == "COMPLETED":
            raise HTTPException(status_code=422, detail={"code": "COMPLETED_SESSION_IMMUTABLE", "message": "A completed session's Reviewer ownership is immutable."})
        if not session["result_owner_mode"] or session["type"] not in {"DEFENSE_1_1", "DEFENSE_2"}:
            raise HTTPException(status_code=422, detail={"code": "RESULT_OWNER_NOT_ALLOWED", "message": "Result Owner mode is disabled for this session."})
        assigned = db.execute(text("SELECT 1 FROM session_reviewers WHERE session_id = :session_id AND lecturer_id = :lecturer_id"), {"session_id": session_id, "lecturer_id": lecturer_id}).scalar_one_or_none()
        if assigned is None:
            raise HTTPException(status_code=422, detail={"code": "RESULT_OWNER_MUST_BE_REVIEWER", "message": "The Result Owner must be one of this session's Reviewers."})
        db.execute(text("UPDATE session_reviewers SET is_result_owner = FALSE WHERE session_id = :session_id"), {"session_id": session_id})
        db.execute(text("UPDATE session_reviewers SET is_result_owner = TRUE WHERE session_id = :session_id AND lecturer_id = :lecturer_id"), {"session_id": session_id, "lecturer_id": lecturer_id})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) VALUES (:actor_id, 'RESULT_OWNER_ASSIGNED', 'session', :entity_id, CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "after_json": _json({"lecturer_id": lecturer_id, "version_id": version_id})})
    return {"version_id": version_id, "session_id": session_id, "result_owner_id": lecturer_id}


@router.post("/schedule/versions/{version_id}/sessions/{session_id}/edit")
def edit_draft_session(version_id: int, session_id: int, payload: SessionEditPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    version = db.execute(text("SELECT round_id, status FROM schedule_versions WHERE id = :id"), {"id": version_id}).mappings().one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
    if version["status"] != "VALID":
        raise HTTPException(status_code=422, detail={"code": "DRAFT_EDIT_REQUIRED", "message": "Only the active valid version can be edited."})
    context, _, timeslots, _, _ = _round_input(db, version["round_id"])
    rows = _session_rows(db, version_id)
    try:
        edited, change = _edited_rows(rows, session_id, payload, timeslots)
        validation = validate_schedule(_to_domain_sessions(edited), context)
        if not validation.valid:
            raise HTTPException(
                status_code=422,
                detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [violation.__dict__ for violation in validation.violations]},
            )
        owner_id = _owner_for_edit(
            db,
            session_id=session_id,
            round_id=version["round_id"],
            reviewer_ids=change["after"]["reviewer_ids"],
            requested_owner_id=payload.result_owner_id,
        )
        prepared_before = change["before"]
        db.commit()
        with db.begin():
            locked_version = db.execute(
                text("SELECT round_id, status FROM schedule_versions WHERE id = :id FOR UPDATE"),
                {"id": version_id},
            ).mappings().one_or_none()
            if locked_version is None or locked_version["status"] != "VALID":
                raise HTTPException(
                    status_code=409,
                    detail={"code": "DRAFT_EDIT_CONCURRENT_UPDATE", "message": "The draft version changed while this request was being prepared."},
                )
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": locked_version["round_id"]})
            fresh_context, _, fresh_timeslots, _, _ = _round_input(db, locked_version["round_id"])
            fresh_rows = _session_rows(db, version_id)
            fresh_target = next((row for row in fresh_rows if row["id"] == session_id), None)
            compared_fields = ("timeslot_id", "room_id", "start_at", "end_at", "status", "reviewer_ids", "result_owner_ids")
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
            owner_id = _owner_for_edit(
                db,
                session_id=session_id,
                round_id=locked_version["round_id"],
                reviewer_ids=change["after"]["reviewer_ids"],
                requested_owner_id=payload.result_owner_id,
            )
            db.execute(text("UPDATE sessions SET timeslot_id = :timeslot_id, room_id = :room_id, start_at = :start_at, end_at = :end_at WHERE id = :session_id AND schedule_version_id = :version_id"), {"timeslot_id": change["after"]["timeslot_id"], "room_id": change["after"]["room_id"], "start_at": change["after"]["start_at"], "end_at": change["after"]["end_at"], "session_id": session_id, "version_id": version_id})
            db.execute(text("DELETE FROM session_reviewers WHERE session_id = :session_id"), {"session_id": session_id})
            names = db.execute(text("SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id WHERE l.id = ANY(:ids)"), {"ids": list(change["after"]["reviewer_ids"]) or [0]}).all()
            name_map = {row[0]: row[1] for row in names}
            for lecturer_id in change["after"]["reviewer_ids"]:
                db.execute(text("INSERT INTO session_reviewers (session_id, schedule_version_id, lecturer_id, is_result_owner, snapshot_name, start_at, end_at) VALUES (:session_id, :version_id, :lecturer_id, :is_owner, :snapshot_name, :start_at, :end_at)"), {"session_id": session_id, "version_id": version_id, "lecturer_id": lecturer_id, "is_owner": lecturer_id == owner_id, "snapshot_name": name_map.get(lecturer_id, str(lecturer_id)), "start_at": change["after"]["start_at"], "end_at": change["after"]["end_at"]})
            actor_id = _actor_id(db, user)
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'SCHEDULE_SESSION_EDITED', 'session', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(session_id), "reason": payload.reason.strip(), "before_json": _json(change["before"]), "after_json": _json(change["after"])})
        return {"session_id": session_id, "version_id": version_id, "status": "UPDATED"}
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc


@router.post("/schedule/versions/{version_id}/sessions/{session_id}/controlled-change")
def controlled_change(version_id: int, session_id: int, payload: SessionEditPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    version = db.execute(text("SELECT * FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": version_id}).mappings().one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
    db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version["round_id"]})
    if version["status"] != "PUBLISHED":
        raise HTTPException(status_code=422, detail={"code": "CONTROLLED_CHANGE_REQUIRES_PUBLISHED", "message": "Controlled change is only for a published version."})
    context, _, timeslots, _, _ = _round_input(db, version["round_id"])
    rows = _session_rows(db, version_id)
    target = next((row for row in rows if row["id"] == session_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist in this version."})
    if target["status"] == "COMPLETED":
        raise HTTPException(status_code=422, detail={"code": "COMPLETED_SESSION_IMMUTABLE", "message": "A completed session's Reviewer history cannot be changed."})
    try:
        edited, change = _edited_rows(rows, session_id, payload, timeslots)
        validation = validate_schedule(_to_domain_sessions(edited), context)
        if not validation.valid:
            raise HTTPException(status_code=422, detail={"code": "HARD_CONSTRAINT_VIOLATION", "violations": [violation.__dict__ for violation in validation.violations]})
        owner_id = _owner_for_edit(
            db,
            session_id=session_id,
            round_id=version["round_id"],
            reviewer_ids=change["after"]["reviewer_ids"],
            requested_owner_id=payload.result_owner_id,
        )
        db.commit()
        with db.begin():
            locked_version = db.execute(text("SELECT status FROM schedule_versions WHERE id = :id FOR UPDATE"), {"id": version_id}).mappings().one_or_none()
            if locked_version is None or locked_version["status"] != "PUBLISHED":
                raise HTTPException(status_code=409, detail={"code": "CONTROLLED_CHANGE_CONCURRENT_UPDATE", "message": "The published version changed while this request was being prepared."})
            db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": version["round_id"]})
            new_version_no = db.execute(text("SELECT COALESCE(MAX(version_no), 0) + 1 FROM schedule_versions WHERE round_id = :round_id"), {"round_id": version["round_id"]}).scalar_one()
            new_version_id = db.execute(text("INSERT INTO schedule_versions (round_id, version_no, status, input_snapshot, algorithm_parameters, random_seed, solver_status, total_score, soft_scores, created_by) VALUES (:round_id, :version_no, 'VALID', CAST(:snapshot AS JSONB), CAST(:parameters AS JSONB), :seed, 'CONTROLLED_CHANGE', :score, CAST(:soft_scores AS JSONB), :created_by) RETURNING id"), {"round_id": version["round_id"], "version_no": new_version_no, "snapshot": _json(version["input_snapshot"]), "parameters": _json(version["algorithm_parameters"]), "seed": version["random_seed"], "score": version["total_score"], "soft_scores": _json(version["soft_scores"]), "created_by": _actor_id(db, user)}).scalar_one()
            new_session_ids: dict[int, int] = {}
            for row in edited:
                new_id = db.execute(text("INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at, status) VALUES (:version_id, :group_id, :timeslot_id, :room_id, :start_at, :end_at, CAST(:status AS session_status)) RETURNING id"), {"version_id": new_version_id, "group_id": row["group_id"], "timeslot_id": row["timeslot_id"], "room_id": row["room_id"], "start_at": row["start_at"], "end_at": row["end_at"], "status": row["status"]}).scalar_one()
                new_session_ids[row["id"]] = new_id
                names = db.execute(text("SELECT l.id, a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id WHERE l.id = ANY(:ids)"), {"ids": list(row["reviewer_ids"]) or [0]}).all()
                name_map = {item[0]: item[1] for item in names}
                owner_ids = set(row.get("result_owner_ids", ()))
                if row["id"] == session_id:
                    owner_ids = {owner_id} if owner_id is not None else set()
                for lecturer_id in row["reviewer_ids"]:
                    db.execute(text("INSERT INTO session_reviewers (session_id, schedule_version_id, lecturer_id, is_result_owner, snapshot_name, start_at, end_at) VALUES (:session_id, :version_id, :lecturer_id, :is_owner, :snapshot_name, :start_at, :end_at)"), {"session_id": new_id, "version_id": new_version_id, "lecturer_id": lecturer_id, "is_owner": lecturer_id in owner_ids, "snapshot_name": name_map.get(lecturer_id, str(lecturer_id)), "start_at": row["start_at"], "end_at": row["end_at"]})
                previous_result = db.execute(text("SELECT outcome, note, entered_by, entered_at, correction_reason, before_json, after_json, remediation_due_at, verifier_lecturer_id, verify_status, before_group_status, after_group_status FROM session_results WHERE session_id = :session_id"), {"session_id": row["id"]}).mappings().one_or_none()
                if previous_result is not None:
                    new_result_id = db.execute(text("INSERT INTO session_results (session_id, outcome, note, entered_by, entered_at, correction_reason, before_json, after_json, remediation_due_at, verifier_lecturer_id, verify_status, before_group_status, after_group_status) VALUES (:session_id, CAST(:outcome AS result_outcome), :note, :entered_by, :entered_at, :correction_reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB), :due_at, :verifier_id, CAST(:verify_status AS verify_status), CAST(:before_group_status AS group_status), CAST(:after_group_status AS group_status)) RETURNING id"), {"session_id": new_id, **dict(previous_result)}).scalar_one()
                    previous_case = db.execute(text("SELECT due_at, status, verifier_lecturer_id, verified_at, note FROM remediation_cases WHERE session_result_id = :result_id"), {"result_id": db.execute(text("SELECT id FROM session_results WHERE session_id = :session_id"), {"session_id": row["id"]}).scalar_one()}).mappings().one_or_none()
                    if previous_case is not None:
                        db.execute(text("INSERT INTO remediation_cases (session_result_id, group_id, due_at, status, verifier_lecturer_id, verified_at, note) VALUES (:result_id, :group_id, :due_at, CAST(:status AS remediation_status), :verifier_lecturer_id, :verified_at, :note) ON CONFLICT (session_result_id) DO NOTHING"), {"result_id": new_result_id, "group_id": row["group_id"], **dict(previous_case)})
            db.execute(text("INSERT INTO schedule_change_records (round_id, schedule_version_id, session_id, actor_id, reason, before_json, after_json) VALUES (:round_id, :version_id, :session_id, :actor_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"round_id": version["round_id"], "version_id": new_version_id, "session_id": session_id, "actor_id": _actor_id(db, user), "reason": payload.reason.strip(), "before_json": _json(change["before"]), "after_json": _json(change["after"])})
            db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'SCHEDULE_CONTROLLED_CHANGE', 'schedule_version', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(new_version_id), "reason": payload.reason.strip(), "before_json": _json(change["before"]), "after_json": _json(change["after"])})
            for recipient_id in affected_schedule_recipients(db, new_version_id):
                key = f"change:{new_version_id}:{recipient_id}"
                payload_json = _json({"source_version_id": version_id, "version_id": new_version_id, "session_id": session_id, "recipient_id": recipient_id})
                db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'SCHEDULE_CHANGED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": payload_json, "key": key})
                db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('SCHEDULE_CHANGED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": payload_json, "key": key})
        return {"version_id": new_version_id, "source_version_id": version_id, "session_id": new_session_ids[session_id], "status": "VALID"}
    except DomainError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc


@router.get("/sessions/{session_id}/replacement-suggestions")
def replacement_suggestions(session_id: int, db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER")
    row = db.execute(text("SELECT s.*, sv.round_id, g.project_id FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN groups g ON g.id = s.group_id WHERE s.id = :id"), {"id": session_id}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
    context, _, timeslots, rooms, reviewers = _round_input(db, row["round_id"])
    current_reviewers = {item[0] for item in db.execute(text("SELECT lecturer_id FROM session_reviewers WHERE session_id = :id"), {"id": session_id}).all()}
    existing_rows = [item for item in _session_rows(db, row["schedule_version_id"]) if item["id"] != session_id]
    candidates = generate_candidates(context, groups=[row["group_id"]], timeslots=timeslots, rooms=rooms, reviewers=reviewers)
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
            room_id=candidate.room_id,
            start_at=candidate.start_at,
            end_at=candidate.end_at,
            reviewer_ids=candidate.reviewer_ids,
            day=candidate.day,
            part=candidate.part,
        )
        if not validate_schedule(_to_domain_sessions(existing_rows) + [candidate_session], context).valid:
            continue
        suggestions.append({"timeslot_id": candidate.timeslot_id, "room_id": candidate.room_id, "reviewer_ids": list(candidate.reviewer_ids), "replaces": sorted(current_reviewers - overlap)})
        if len(suggestions) >= 50:
            break
    return suggestions


@router.post("/sessions/{session_id}/postpone")
def postpone_session(session_id: int, payload: RescheduleRequestPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        session_row = db.execute(text("SELECT s.id, s.schedule_version_id FROM sessions s WHERE s.id = :id FOR UPDATE"), {"id": session_id}).mappings().one_or_none()
        if session_row is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
        updated = db.execute(text("UPDATE sessions SET status = 'POSTPONED' WHERE id = :id AND status IN ('SCHEDULED', 'ONGOING') RETURNING id, status"), {"id": session_id}).mappings().one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_POSTPONABLE", "message": "Session is not in an operational state."})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason) VALUES (:actor_id, 'SESSION_POSTPONED', 'session', :entity_id, :reason)"), {"actor_id": _actor_id(db, user), "entity_id": str(session_id), "reason": payload.reason.strip()})
        for recipient_id in affected_schedule_recipients(db, session_row["schedule_version_id"]):
            key = f"postponed:{session_id}:{recipient_id}"
            event_payload = _json({"session_id": session_id, "reason": payload.reason.strip(), "recipient_id": recipient_id})
            db.execute(text("INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, 'SESSION_POSTPONED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"recipient_id": recipient_id, "payload": event_payload, "key": key})
            db.execute(text("INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES ('SESSION_POSTPONED', CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"), {"payload": event_payload, "key": key})
    return dict(updated)


@router.post("/rounds/{round_id}/schedule/publish/{version_id}")
def publish_schedule(round_id: int, version_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
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
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_id})
        context, _, _, _, _ = _round_input(db, round_id)
        try:
            if version["activated_at"] is None and version["status"] == "VALID":
                raise DomainError("VERSION_NOT_ACTIVE", "Activate the selected version before publishing it.")
            ensure_publishable(
                str(version["status"]),
                validate_schedule(
                    _to_domain_sessions(_session_rows(db, version_id)), context
                ).valid,
            )
        except DomainError as exc:
            raise HTTPException(
                status_code=422, detail={"code": exc.code, "message": str(exc)}
            ) from exc
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'SUPERSEDED' WHERE round_id = :round_id AND status = 'PUBLISHED'"
            ),
            {"round_id": round_id},
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


@router.post("/sessions/{session_id}/reschedule-requests", status_code=status.HTTP_201_CREATED)
def request_reschedule(
    session_id: int, payload: RescheduleRequestPayload, db: Db, user: User
) -> dict[str, Any]:
    require_change_reason(payload.reason)
    _require(user, "MANAGER", "LECTURER", "STUDENT")
    row = db.execute(
        text(
            "SELECT s.group_id FROM sessions s WHERE s.id = :id"
        ),
        {"id": session_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."})
    assigned = user.role == "MANAGER" or can_read_session(db, user, session_id)
    ensure_reschedule_allowed(role=user.role, assigned=assigned, is_leader=is_active_group_leader(db, user, row["group_id"]))
    db.commit()
    with db.begin():
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


@router.post("/reschedule-requests/{request_id}/decision")
def decide_reschedule(
    request_id: int, payload: RescheduleDecisionPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
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


@router.post("/rounds/{round_id}/operation")
def operate_round(
    round_id: int, payload: RoundOperationPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
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
