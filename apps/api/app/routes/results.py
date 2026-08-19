from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.enums import DefenseType, GroupStatus, ResultOutcome
from app.domain.errors import DomainError
from app.domain.result_workflow import validate_remediation_verifier, validate_result_outcome
from app.domain.schedule_operations import require_change_reason
from app.domain.transitions import transition_group
from app.response_models import (
    ActionResponse,
    RemediationResponse,
    ResultDetailResponse,
    ResultWriteResponse,
)
from app.routes.schedule_operations import _actor_id
from app.services.access import (
    affected_group_recipients,
    can_read_session,
    lecturer_id_for_account,
)
from app.services.semester_queries import ensure_round_semester_writable

router = APIRouter(prefix="/api/v1", tags=["results"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


class ResultPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    outcome: str = Field(alias="result", min_length=1, max_length=32)
    note: str | None = Field(default=None, max_length=2000)
    remediation_due_at: datetime | None = Field(default=None, alias="remediationDueAt")
    verifier_lecturer_id: int | None = Field(default=None, alias="verifierLecturerId", gt=0)
    correction_reason: str | None = Field(default=None, alias="correctionReason", max_length=1000)


class RemediationDecisionPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    outcome: str = Field(alias="decision", pattern="^(PASSED|FAILED)$")
    note: str | None = Field(default=None, max_length=2000)


class OverdueFailPayload(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


def _session_context(db: Session, session_id: int) -> dict[str, Any]:
    row = (
        db.execute(
            text(
                "SELECT s.id, s.group_id, a.project_id, s.status AS session_status, g.status AS group_status, "
                "sv.id AS version_id, r.id AS round_id, r.type, r.result_owner_mode "
                "FROM sessions s JOIN groups g ON g.id = s.group_id "
                "JOIN schedule_assignments a ON a.schedule_version_id=s.schedule_version_id AND a.group_id=s.group_id "
                "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
                "JOIN rounds r ON r.id = sv.round_id WHERE s.id = :id"
            ),
            {"id": session_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "SESSION_NOT_FOUND", "message": "Session does not exist."},
        )
    reviewer_rows = db.execute(
        text(
            "SELECT cm.lecturer_id, cm.is_result_owner FROM council_members cm "
            "JOIN sessions s ON s.council_id = cm.council_id WHERE s.id = :session_id"
        ),
        {"session_id": session_id},
    ).all()
    result = (
        db.execute(
            text("SELECT * FROM session_results WHERE session_id = :session_id"),
            {"session_id": session_id},
        )
        .mappings()
        .one_or_none()
    )
    return {
        **dict(row),
        "reviewer_ids": {item[0] for item in reviewer_rows},
        "owner_ids": {item[0] for item in reviewer_rows if item[1]},
        "lecturer_id_by_account": {},
        "result": dict(result) if result else None,
    }


def _can_write(db: Session, user: CurrentUser, context: dict[str, Any]) -> bool:
    if user.role == "MANAGER":
        return True
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if user.role != "LECTURER" or lecturer_id not in context["reviewer_ids"]:
        return False
    if context["result_owner_mode"] and context["type"] in {"DEFENSE_1_1", "DEFENSE_2"}:
        return lecturer_id in context["owner_ids"]
    return True


def _queue_event(
    db: Session, *, event_type: str, payload: dict[str, Any], recipient_ids: set[int]
) -> None:
    import json

    for recipient_id in recipient_ids:
        key = f"{event_type}:{payload.get('session_id', payload.get('remediation_id'))}:{recipient_id}"
        data = json.dumps({**payload, "recipient_id": recipient_id}, default=str)
        db.execute(
            text(
                "INSERT INTO notifications (recipient_account_id, event_type, payload, dedupe_key) VALUES (:recipient_id, :event_type, CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
            ),
            {"recipient_id": recipient_id, "event_type": event_type, "payload": data, "key": key},
        )
        db.execute(
            text(
                "INSERT INTO outbox_jobs (topic, payload, dedupe_key) VALUES (:event_type, CAST(:payload AS JSONB), :key) ON CONFLICT DO NOTHING"
            ),
            {"event_type": event_type, "payload": data, "key": key},
        )


@router.get("/sessions/{session_id}/result", response_model=ResultDetailResponse)
def get_result(session_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    if not can_read_session(db, user, session_id):
        raise HTTPException(status_code=403, detail="Result is outside the actor's scope.")
    context = _session_context(db, session_id)
    return {
        "session_id": session_id,
        "round_type": context["type"],
        "group_status": context["group_status"],
        "result": context["result"],
    }


@router.get("/remediation", response_model=list[RemediationResponse])
def list_remediation_cases(db: Db, user: User) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    query = (
        "SELECT rc.id, rc.group_id, g.code AS group_code, rc.status, rc.due_at, "
        "rc.verifier_lecturer_id, rc.note, r.type AS round_type "
        "FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id "
        "JOIN session_results sr ON sr.id = rc.session_result_id "
        "JOIN sessions s ON s.id = sr.session_id "
        "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
        "JOIN rounds r ON r.id = sv.round_id"
    )
    params: dict[str, object] = {}
    if user.role == "LECTURER":
        query += " JOIN lecturers verifier ON verifier.id = rc.verifier_lecturer_id WHERE verifier.account_id = :account_id"
        params["account_id"] = user.account_id
    elif user.role == "STUDENT":
        query += " JOIN group_memberships gm ON gm.group_id = rc.group_id JOIN students student ON student.id = gm.student_id WHERE gm.status = 'ACTIVE' AND student.account_id = :account_id"
        params["account_id"] = user.account_id
        query += " ORDER BY rc.due_at"
    else:
        query += " ORDER BY rc.due_at"
    rows = [dict(row) for row in db.execute(text(query), params).mappings().all()]
    for row in rows:
        row["ui_status"] = "PENDING" if row["status"] == "OPEN" else row["status"]
    return rows


@router.post("/sessions/{session_id}/result", status_code=status.HTTP_201_CREATED, response_model=ResultWriteResponse)
def record_result(session_id: int, payload: ResultPayload, db: Db, user: User) -> dict[str, Any]:
    _require(user, "MANAGER", "LECTURER")
    context = _session_context(db, session_id)
    if context["session_status"] in {"GROUP_ABSENT", "POSTPONED", "CANCELLED"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "RESULT_SESSION_NOT_OPERATIONAL",
                "message": "Results cannot be entered for an absent, postponed, or cancelled session.",
            },
        )
    if not _can_write(db, user, context):
        raise HTTPException(
            status_code=403, detail="Only an assigned Reviewer or Manager may enter a result."
        )
    if (
        context["result_owner_mode"]
        and context["type"] in {"DEFENSE_1_1", "DEFENSE_2"}
        and len(context["owner_ids"]) != 1
    ):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "RESULT_OWNER_REQUIRED",
                "message": "Exactly one Result Owner must be assigned before entering this result.",
            },
        )
    try:
        validate_result_outcome(str(context["type"]), payload.outcome)
        if context["type"] == "DEFENSE_1_1" and payload.outcome == "LEVEL_2":
            if payload.remediation_due_at is None or payload.verifier_lecturer_id is None:
                raise DomainError(
                    "REMEDIATION_FIELDS_REQUIRED",
                    "Level 2 requires a due date and Reviewer verifier.",
                )
            validate_remediation_verifier(payload.verifier_lecturer_id, context["reviewer_ids"])
        if context["type"] != "DEFENSE_1_1" and (
            payload.remediation_due_at or payload.verifier_lecturer_id
        ):
            raise DomainError(
                "REMEDIATION_NOT_ALLOWED", "Only Defense 1.1 Level 2 creates remediation."
            )
        if context["result"] is not None:
            if user.role != "MANAGER":
                raise DomainError(
                    "RESULT_CORRECTION_FORBIDDEN", "Only Manager may correct an existing result."
                )
            require_change_reason(payload.correction_reason or "")
        if context["type"] == "DEFENSE_1_1" and context["result"] is not None:
            remediation = db.execute(
                text("SELECT status FROM remediation_cases WHERE session_result_id = :result_id"),
                {"result_id": context["result"]["id"]},
            ).scalar_one_or_none()
            if remediation in {"PASSED", "FAILED"}:
                raise DomainError("RESULT_AFTER_REMEDIATION", "A result with a completed remediation case cannot be corrected.")
        db.commit()
        with db.begin():
            db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": session_id})
            locked_context = _session_context(db, session_id)
            ensure_round_semester_writable(db, int(locked_context["round_id"]))
            if locked_context["session_status"] in {"GROUP_ABSENT", "POSTPONED", "CANCELLED"}:
                raise DomainError("RESULT_SESSION_NOT_OPERATIONAL", "Results cannot be entered for an absent, postponed, or cancelled session.")
            if locked_context["session_status"] != context["session_status"] or locked_context["group_status"] != context["group_status"]:
                raise DomainError("RESULT_CONCURRENT_UPDATE", "The session or group changed while this result was being prepared.")
            initial_result_at = context["result"].get("entered_at") if context["result"] is not None else None
            locked_result_at = locked_context["result"].get("entered_at") if locked_context["result"] is not None else None
            if initial_result_at != locked_result_at:
                raise DomainError("RESULT_CONCURRENT_UPDATE", "Another result update was committed before this request.")
            actor_id = _actor_id(db, user)
            before = context["result"]
            base_group_status = (
                before.get("before_group_status")
                if before is not None and before.get("before_group_status")
                else context["group_status"]
            )
            result_id = db.execute(
                text(
                    "INSERT INTO session_results (session_id, outcome, note, entered_by, correction_reason, before_json, after_json, "
                    "remediation_due_at, verifier_lecturer_id, before_group_status, after_group_status) VALUES (:session_id, CAST(:outcome AS result_outcome), :note, :entered_by, "
                    ":correction_reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB), :due_at, :verifier_id, "
                    "CAST(:before_group_status AS group_status), CAST(:after_group_status AS group_status)) "
                    "ON CONFLICT (session_id) DO UPDATE SET outcome = EXCLUDED.outcome, note = EXCLUDED.note, entered_by = EXCLUDED.entered_by, "
                    "entered_at = now(), correction_reason = EXCLUDED.correction_reason, before_json = EXCLUDED.before_json, after_json = EXCLUDED.after_json, "
                    "remediation_due_at = EXCLUDED.remediation_due_at, verifier_lecturer_id = EXCLUDED.verifier_lecturer_id, "
                    "before_group_status = EXCLUDED.before_group_status, after_group_status = EXCLUDED.after_group_status RETURNING id"
                ),
                {
                    "session_id": session_id,
                    "outcome": payload.outcome,
                    "note": payload.note,
                    "entered_by": actor_id,
                    "correction_reason": payload.correction_reason,
                    "before_json": _json(before),
                    "after_json": _json(payload.model_dump()),
                    "due_at": payload.remediation_due_at,
                    "verifier_id": payload.verifier_lecturer_id,
                    "before_group_status": base_group_status,
                    "after_group_status": None,
                },
            ).scalar_one()
            after_status = None
            if context["type"] in {"DEFENSE_1_1", "DEFENSE_1_2", "DEFENSE_2"}:
                outcome = (
                    ResultOutcome.COMPLETED
                    if payload.outcome == "COMPLETED"
                    else ResultOutcome(payload.outcome)
                )
                after_status = transition_group(
                    GroupStatus(base_group_status), DefenseType(context["type"]), outcome
                ).value
                db.execute(
                    text(
                        "UPDATE groups SET status = CAST(:status AS group_status) WHERE id = :group_id"
                    ),
                    {"status": after_status, "group_id": context["group_id"]},
                )
            if context["type"] == "DEFENSE_1_2" and payload.outcome == "COMPLETED":
                db.execute(
                    text("UPDATE sessions SET status = 'COMPLETED' WHERE id = :session_id"),
                    {"session_id": session_id},
                )
            db.execute(
                text("UPDATE session_results SET after_group_status = CAST(:status AS group_status) WHERE id = :result_id"),
                {"status": after_status or base_group_status, "result_id": result_id},
            )
            if context["type"] == "DEFENSE_1_1" and payload.outcome == "LEVEL_2":
                db.execute(
                    text(
                        "INSERT INTO remediation_cases (session_result_id, group_id, due_at, verifier_lecturer_id) VALUES (:result_id, :group_id, :due_at, :verifier_id) ON CONFLICT (session_result_id) DO UPDATE SET due_at = EXCLUDED.due_at, verifier_lecturer_id = EXCLUDED.verifier_lecturer_id, status = 'OPEN'"
                    ),
                    {
                        "result_id": result_id,
                        "group_id": context["group_id"],
                        "due_at": payload.remediation_due_at,
                        "verifier_id": payload.verifier_lecturer_id,
                    },
                )
            elif context["type"] == "DEFENSE_1_1" and before is not None:
                db.execute(
                    text("DELETE FROM remediation_cases WHERE session_result_id = :result_id AND status = 'OPEN'"),
                    {"result_id": result_id},
                )
            recipient_ids = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT a.id FROM council_members cm JOIN sessions s ON s.council_id = cm.council_id "
                        "JOIN lecturers l ON l.id = cm.lecturer_id JOIN accounts a ON a.id = l.account_id WHERE s.id = :session_id"
                    ),
                    {"session_id": session_id},
                ).all()
            }
            recipient_ids.update(
                affected_group_recipients(
                    db,
                    context["group_id"],
                    schedule_version_id=context["version_id"],
                )
            )
            _queue_event(
                db,
                event_type="RESULT_RECORDED",
                payload={
                    "session_id": session_id,
                    "result_id": result_id,
                    "outcome": payload.outcome,
                },
                recipient_ids=recipient_ids,
            )
            if context["type"] == "DEFENSE_1_1" and payload.outcome == "LEVEL_2":
                verifier_account = db.execute(
                    text("SELECT account_id FROM lecturers WHERE id = :lecturer_id"),
                    {"lecturer_id": payload.verifier_lecturer_id},
                ).scalar_one_or_none()
                if verifier_account is not None:
                    _queue_event(
                        db,
                        event_type="REMEDIATION_CREATED",
                        payload={"session_id": session_id, "remediation_id": result_id, "due_at": payload.remediation_due_at},
                        recipient_ids={int(verifier_account)},
                    )
            db.execute(
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) "
                    "VALUES (:actor_id, :action, 'session_result', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "action": "RESULT_CORRECTED" if before is not None else "RESULT_RECORDED",
                    "entity_id": str(result_id),
                    "reason": payload.correction_reason,
                    "before_json": _json(before),
                    "after_json": _json(payload.model_dump()),
                },
            )
        return {
            "id": result_id,
            "session_id": session_id,
            "outcome": payload.outcome,
            "group_status": after_status or context["group_status"],
        }
    except DomainError as exc:
        raise HTTPException(
            status_code=422, detail={"code": exc.code, "message": str(exc)}
        ) from exc


@router.post("/remediation/{case_id}/decision", response_model=ActionResponse, response_model_exclude_none=True)
def decide_remediation(
    case_id: int, payload: RemediationDecisionPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "LECTURER")
    with db.begin():
        round_ref = db.execute(
            text("SELECT sv.round_id FROM remediation_cases rc JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE rc.id = :id"),
            {"id": case_id},
        ).scalar_one_or_none()
        if round_ref is None:
            raise HTTPException(status_code=404, detail={"code": "REMEDIATION_NOT_FOUND", "message": "Remediation case does not exist."})
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_ref})
        ensure_round_semester_writable(db, int(round_ref))
        case = (
            db.execute(
                text(
                    "SELECT rc.*, g.status AS group_status, sr.session_id, s.group_id, sv.round_id FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE rc.id = :id FOR UPDATE"
                ),
                {"id": case_id},
            )
            .mappings()
            .one_or_none()
        )
        if case is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "REMEDIATION_NOT_FOUND",
                    "message": "Remediation case does not exist.",
                },
            )
        lecturer_id = lecturer_id_for_account(db, user.account_id)
        if lecturer_id != case["verifier_lecturer_id"]:
            raise HTTPException(status_code=403, detail={"code": "REMEDIATION_VERIFIER_REQUIRED", "message": "Only the assigned Remediation Verifier may decide this case."})
        if case["status"] not in {"OPEN", "OVERDUE"}:
            raise HTTPException(status_code=409, detail={"code": "REMEDIATION_ALREADY_DECIDED", "message": "This remediation case has already been decided."})
        actor_id = _actor_id(db, user)
        status_value = "PASSED" if payload.outcome == "PASSED" else "FAILED"
        db.execute(
            text(
                "UPDATE remediation_cases SET status = CAST(:status AS remediation_status), verified_at = now(), note = :note WHERE id = :id"
            ),
            {"status": status_value, "note": payload.note, "id": case_id},
        )
        db.execute(text("UPDATE session_results SET verify_status = 'VERIFIED' WHERE id = :result_id"), {"result_id": case["session_result_id"]})
        next_status = transition_group(
            GroupStatus(case["group_status"]),
            DefenseType.REMEDIATION,
            ResultOutcome.PASS if status_value == "PASSED" else ResultOutcome.FAIL,
        ).value
        db.execute(text("UPDATE groups SET status = CAST(:status AS group_status) WHERE id = :group_id"), {"status": next_status, "group_id": case["group_id"]})
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'REMEDIATION_DECISION', 'remediation_case', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": actor_id, "entity_id": str(case_id), "reason": payload.note, "before_json": _json({"status": case["status"], "group_status": case["group_status"]}), "after_json": _json({"status": status_value, "group_status": next_status})})
        version_id = db.execute(
            text(
                "SELECT s.schedule_version_id FROM session_results sr "
                "JOIN sessions s ON s.id = sr.session_id WHERE sr.id = :result_id"
            ),
            {"result_id": case["session_result_id"]},
        ).scalar_one_or_none()
        _queue_event(db, event_type="REMEDIATION_DECIDED", payload={"remediation_id": case_id, "outcome": status_value}, recipient_ids=affected_group_recipients(db, case["group_id"], schedule_version_id=version_id))
    return {"id": case_id, "status": status_value}


@router.post("/remediation/{case_id}/overdue-fail", response_model=ActionResponse, response_model_exclude_none=True)
def fail_overdue_remediation(
    case_id: int, payload: OverdueFailPayload, db: Db, user: User
) -> dict[str, Any]:
    _require(user, "MANAGER")
    require_change_reason(payload.reason)
    with db.begin():
        round_ref = db.execute(
            text("SELECT sv.round_id FROM remediation_cases rc JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE rc.id = :id"),
            {"id": case_id},
        ).scalar_one_or_none()
        if round_ref is None:
            raise HTTPException(status_code=404, detail={"code": "REMEDIATION_NOT_FOUND", "message": "Remediation case does not exist."})
        db.execute(text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"), {"round_id": round_ref})
        ensure_round_semester_writable(db, int(round_ref))
        case = (
            db.execute(
                text("SELECT rc.group_id, rc.status, rc.due_at, sv.round_id FROM remediation_cases rc JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE rc.id = :id FOR UPDATE"),
                {"id": case_id},
            )
            .mappings()
            .one_or_none()
        )
        if case is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "REMEDIATION_NOT_FOUND",
                    "message": "Remediation case does not exist.",
                },
            )
        if case["status"] not in {"OPEN", "OVERDUE"}:
            raise HTTPException(status_code=409, detail={"code": "REMEDIATION_ALREADY_DECIDED", "message": "This remediation case has already been decided."})
        if case["due_at"] > datetime.now(UTC):
            raise HTTPException(status_code=422, detail={"code": "REMEDIATION_NOT_OVERDUE", "message": "Manager may fail a remediation case only after its due date."})
        db.execute(
            text("UPDATE remediation_cases SET status = 'FAILED', note = :reason WHERE id = :id"),
            {"reason": payload.reason.strip(), "id": case_id},
        )
        db.execute(
            text(
                "UPDATE groups SET status = 'FAILED' WHERE id = :group_id AND status = 'D12_CONDITIONAL'"
            ),
            {"group_id": case["group_id"]},
        )
        db.execute(text("INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json) VALUES (:actor_id, 'REMEDIATION_OVERDUE_FAILED', 'remediation_case', :entity_id, :reason, CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))"), {"actor_id": _actor_id(db, user), "entity_id": str(case_id), "reason": payload.reason.strip(), "before_json": _json({"status": case["status"]}), "after_json": _json({"status": "FAILED", "group_status": "FAILED"})})
        version_id = db.execute(
            text(
                "SELECT s.schedule_version_id FROM session_results sr "
                "JOIN sessions s ON s.id = sr.session_id WHERE sr.id = "
                "(SELECT session_result_id FROM remediation_cases WHERE id = :case_id)"
            ),
            {"case_id": case_id},
        ).scalar_one_or_none()
        _queue_event(db, event_type="REMEDIATION_OVERDUE", payload={"remediation_id": case_id, "outcome": "FAILED"}, recipient_ids=affected_group_recipients(db, case["group_id"], schedule_version_id=version_id))
    return {"id": case_id, "status": "FAILED"}


def _json(value: Any) -> str:
    import json

    return json.dumps(value, default=str)


_PHASE3_PROVENANCE_TABLE = "schedule_assignments"
