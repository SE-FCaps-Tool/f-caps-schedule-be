from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.services.access import is_management_user, visible_session_ids
from app.services.ical import build_ical
from app.response_models import (
    DashboardResponse,
    LecturerLoadReportResponse,
    NotificationResponse,
    NotificationRetryResponse,
    OutcomesReportResponse,
    PersonalScheduleResponse,
    QualityReportResponse,
    RemediationReportResponse,
    UnscheduledReportResponse,
    VersionSummaryResponse,
)

_PHASE3_PROVENANCE_TABLE = "schedule_assignments"
router = APIRouter(prefix="/api/v1", tags=["operations"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


def _version_scope(db: Session, round_id: int | None = None, semester_id: int | None = None) -> dict[str, Any] | None:
    row = db.execute(
        text(
            "SELECT sv.id AS version_id, sv.round_id, sv.status, sv.created_at, "
            "r.type, r.semester_id, s.code AS semester_code "
            "FROM schedule_versions sv JOIN rounds r ON r.id = sv.round_id "
            "JOIN semesters s ON s.id = r.semester_id "
            "WHERE (CAST(:round_id AS INTEGER) IS NULL OR sv.round_id = CAST(:round_id AS INTEGER)) "
            "AND (CAST(:semester_id AS INTEGER) IS NULL OR r.semester_id = CAST(:semester_id AS INTEGER)) "
            "AND sv.status IN ('PUBLISHED', 'ACTIVE') ORDER BY "
            "CASE WHEN sv.status = 'PUBLISHED' THEN 0 ELSE 1 END, sv.activated_at DESC NULLS LAST, sv.id DESC LIMIT 1"
        ),
        {"round_id": round_id, "semester_id": semester_id},
    ).mappings().one_or_none()
    return {**dict(row), "generated_at": datetime.now(UTC)} if row else None


@router.get("/dashboard", response_model=DashboardResponse)
def manager_dashboard(db: Db, user: User, round_id: int | None = None, semester_id: int | None = None) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    params = {"round_id": round_id, "semester_id": semester_id}
    availability = db.execute(
        text(
            "SELECT COUNT(DISTINCT ri.lecturer_id) AS invited, "
            "COUNT(DISTINCT CASE WHEN la.lecturer_id IS NOT NULL THEN ri.lecturer_id END) AS responded "
            "FROM round_invitations ri JOIN rounds ar ON ar.id = ri.round_id LEFT JOIN lecturer_availabilities la "
            "ON la.round_id = ri.round_id AND la.lecturer_id = ri.lecturer_id "
            "WHERE (CAST(:round_id AS INTEGER) IS NULL OR ri.round_id = CAST(:round_id AS INTEGER)) "
            "AND (CAST(:semester_id AS INTEGER) IS NULL OR ar.semester_id = CAST(:semester_id AS INTEGER))"
        ),
        params,
    ).mappings().one()
    selected = _version_scope(db, round_id, semester_id)
    if selected:
        groups = db.execute(
            text(
                "SELECT COUNT(*) AS total, COUNT(s.id) AS scheduled FROM round_groups rg "
                "LEFT JOIN sessions s ON s.group_id = rg.group_id AND s.schedule_version_id = :version_id "
                "WHERE rg.round_id = (SELECT round_id FROM schedule_versions WHERE id = :version_id)"
            ),
            {"round_id": round_id, "version_id": selected["version_id"]},
        ).mappings().one()
    else:
        groups = {"total": 0, "scheduled": 0}
    load = db.execute(
        text(
            "SELECT l.id, l.lecturer_code, a.display_name, COUNT(ls.id) AS session_count "
            "FROM lecturers l JOIN accounts a ON a.id = l.account_id LEFT JOIN council_members cm ON cm.lecturer_id = l.id "
            "LEFT JOIN sessions ls ON ls.council_id = cm.council_id AND (:version_id IS NULL OR ls.schedule_version_id = :version_id) "
            "LEFT JOIN schedule_versions lsv ON lsv.id = ls.schedule_version_id LEFT JOIN rounds lr ON lr.id = lsv.round_id "
            "WHERE (CAST(:semester_id AS INTEGER) IS NULL OR lr.semester_id = CAST(:semester_id AS INTEGER)) "
            "GROUP BY l.id, l.lecturer_code, a.display_name ORDER BY session_count DESC, l.lecturer_code LIMIT 10"
        ),
        {"version_id": selected["version_id"] if selected else None, "semester_id": semester_id},
    ).mappings().all()
    scope_semester = semester_id if semester_id is not None else (db.execute(
        text("SELECT semester_id FROM rounds WHERE id = :round_id"), {"round_id": round_id}
    ).scalar_one_or_none() if round_id is not None else db.execute(
        text("SELECT id FROM semesters WHERE status = 'ACTIVE' ORDER BY id DESC LIMIT 1")
    ).scalar_one_or_none())
    totals = db.execute(
        text(
            "SELECT "
            "(SELECT COUNT(*) FROM projects WHERE (CAST(:semester_id AS BIGINT) IS NULL OR semester_id = CAST(:semester_id AS BIGINT))) AS projects, "
            "(SELECT COUNT(*) FROM groups g JOIN projects p ON p.id = g.project_id WHERE (CAST(:semester_id AS BIGINT) IS NULL OR p.semester_id = CAST(:semester_id AS BIGINT))) AS groups, "
            "(SELECT COUNT(*) FROM students st JOIN group_memberships gm ON gm.student_id = st.id JOIN groups g ON g.id = gm.group_id JOIN projects p ON p.id = g.project_id WHERE gm.status = 'ACTIVE' AND (CAST(:semester_id AS BIGINT) IS NULL OR p.semester_id = CAST(:semester_id AS BIGINT))) AS students, "
            "(SELECT COUNT(*) FROM lecturers) AS lecturers"
        ),
        {"semester_id": scope_semester},
    ).mappings().one()
    attention = db.execute(
        text(
            "SELECT "
            "COUNT(*) FILTER (WHERE active_members < 4) AS under_four, "
            "COUNT(*) FILTER (WHERE leaders <> 1) AS no_leader "
            "FROM (SELECT g.id, COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_members, COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leaders "
            "FROM groups g JOIN projects p ON p.id = g.project_id LEFT JOIN group_memberships gm ON gm.group_id = g.id "
            "WHERE (CAST(:semester_id AS BIGINT) IS NULL OR p.semester_id = CAST(:semester_id AS BIGINT)) GROUP BY g.id) q"
        ),
        {"semester_id": scope_semester},
    ).mappings().one()
    remediation_overdue = db.execute(text("SELECT COUNT(*) FROM remediation_cases rc JOIN session_results rs ON rs.id = rc.session_result_id JOIN sessions s ON s.id = rs.session_id JOIN schedule_assignments sa ON sa.schedule_version_id = s.schedule_version_id AND sa.group_id = s.group_id JOIN projects rp ON rp.id = sa.project_id WHERE (rc.status = 'OVERDUE' OR (rc.status = 'OPEN' AND rc.due_at < now())) AND (CAST(:semester_id AS INTEGER) IS NULL OR rp.semester_id = CAST(:semester_id AS INTEGER))"), {"semester_id": scope_semester}).scalar_one()
    current_semester = db.execute(
        text("SELECT id, code, name, status FROM semesters WHERE id = :id"),
        {"id": scope_semester},
    ).mappings().one_or_none()
    return {
        "current_semester": dict(current_semester) if current_semester else None,
        "totals": {key: int(value or 0) for key, value in totals.items()},
        "availability": {"invited": availability["invited"], "responded": availability["responded"]},
        "groups": {"total": groups["total"], "scheduled": groups["scheduled"], "unscheduled": groups["total"] - groups["scheduled"]},
        "pending_reschedule_requests": db.execute(text("SELECT COUNT(*) FROM reschedule_requests rr WHERE rr.status = 'REQUESTED' AND (CAST(:semester_id AS INTEGER) IS NULL OR EXISTS (SELECT 1 FROM sessions ss JOIN schedule_versions svv ON svv.id = ss.schedule_version_id JOIN rounds rrr ON rrr.id = svv.round_id WHERE ss.id = rr.session_id AND rrr.semester_id = CAST(:semester_id AS INTEGER)))"), {"semester_id": scope_semester}).scalar_one(),
        "changes": db.execute(text("SELECT COUNT(*) FROM schedule_change_records scr WHERE CAST(:semester_id AS INTEGER) IS NULL OR EXISTS (SELECT 1 FROM schedule_versions svv JOIN rounds rrr ON rrr.id = svv.round_id WHERE svv.id = scr.schedule_version_id AND rrr.semester_id = CAST(:semester_id AS INTEGER))"), {"semester_id": scope_semester}).scalar_one(),
        "version": selected,
        "lecturer_load": [dict(row) for row in load],
        "attention_groups": [dict(row) for row in db.execute(text("SELECT g.id, g.code, g.status FROM groups g JOIN projects p ON p.id = g.project_id WHERE g.status IN ('D12_CONDITIONAL', 'FAILED', 'DROPPED') AND (CAST(:semester_id AS INTEGER) IS NULL OR p.semester_id = CAST(:semester_id AS INTEGER)) ORDER BY g.id LIMIT 20"), {"semester_id": scope_semester}).mappings().all()],
        "attention": {"no_leader": int(attention["no_leader"] or 0), "under_four": int(attention["under_four"] or 0), "remediation_overdue": int(remediation_overdue or 0), "unscheduled": int(groups["total"] - groups["scheduled"])},
    }


@router.get("/reports/lecturer-load", response_model=LecturerLoadReportResponse)
def lecturer_load_report(db: Db, user: User, round_id: int | None = None, semester_id: int | None = None) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    selected = _version_scope(db, round_id, semester_id)
    rows = db.execute(
        text(
            "SELECT l.id AS lecturer_id, l.lecturer_code, a.display_name, COUNT(ls.id) AS session_count, "
            "r.h12_semester_quota AS quota, CASE WHEN r.h12_semester_quota > 0 THEN ROUND(COUNT(ls.id)::numeric * 100 / r.h12_semester_quota, 1) ELSE NULL END AS quota_percent "
            "FROM lecturers l JOIN accounts a ON a.id = l.account_id "
            "LEFT JOIN council_members cm ON cm.lecturer_id = l.id "
            "LEFT JOIN sessions ls ON ls.council_id = cm.council_id AND ls.schedule_version_id = :version_id "
            "LEFT JOIN schedule_versions sv ON sv.id = :version_id LEFT JOIN rounds r ON r.id = sv.round_id "
            "WHERE (CAST(:round_id AS INTEGER) IS NULL OR r.id = CAST(:round_id AS INTEGER)) AND (CAST(:semester_id AS INTEGER) IS NULL OR r.semester_id = CAST(:semester_id AS INTEGER)) GROUP BY l.id, l.lecturer_code, a.display_name, r.h12_semester_quota "
            "ORDER BY l.lecturer_code"
        ),
        {"round_id": round_id, "semester_id": semester_id, "version_id": selected["version_id"] if selected else None},
    ).mappings().all()
    return {"round_id": round_id, "version": selected, "rows": [dict(row) for row in rows]}


@router.get("/reports/unscheduled", response_model=UnscheduledReportResponse)
def unscheduled_report(db: Db, user: User, round_id: int) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    generated_at = datetime.now(UTC)
    rows = db.execute(text("SELECT sv.id, sv.version_no, sv.status, sv.input_snapshot, sv.created_at, r.type, s.code AS semester_code FROM schedule_versions sv JOIN rounds r ON r.id = sv.round_id JOIN semesters s ON s.id = r.semester_id WHERE sv.round_id = :round_id ORDER BY sv.version_no DESC"), {"round_id": round_id}).mappings().all()
    return {"round_id": round_id, "generated_at": generated_at, "versions": [{"version_id": row["id"], "version_no": row["version_no"], "status": row["status"], "created_at": row["created_at"], "unscheduled": (row["input_snapshot"] or {}).get("unscheduled", []), "provenance": {"semester_code": row["semester_code"], "round_type": row["type"], "version_id": row["id"], "generated_at": generated_at}} for row in rows]}


@router.get("/reports/provenance/{version_id}", response_model=VersionSummaryResponse)
def report_provenance(version_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    if user.role not in {"ADMIN", "MANAGER"} and not visible_session_ids(db, user, version_id=version_id):
        raise HTTPException(status_code=403, detail="Report is outside the actor's scope.")
    row = db.execute(text("SELECT sv.id AS version_id, sv.version_no, sv.status, sv.created_at, r.id AS round_id, r.type, s.code AS semester_code FROM schedule_versions sv JOIN rounds r ON r.id = sv.round_id JOIN semesters s ON s.id = r.semester_id WHERE sv.id = :version_id"), {"version_id": version_id}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
    return {**dict(row), "generated_at": datetime.now(UTC)}


@router.get("/reports/quality", response_model=QualityReportResponse)
def group_quality_report(db: Db, user: User, semester_id: int | None = None) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(text("SELECT g.id, g.code, COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') AS active_members, COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leaders FROM groups g JOIN projects p ON p.id = g.project_id LEFT JOIN group_memberships gm ON gm.group_id = g.id WHERE (CAST(:semester_id AS INTEGER) IS NULL OR p.semester_id = CAST(:semester_id AS INTEGER)) GROUP BY g.id, g.code HAVING COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE') < 4 OR COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') <> 1 ORDER BY g.code"), {"semester_id": semester_id}).mappings().all()
    return {"version": _version_scope(db, None, semester_id), "rows": [dict(row) for row in rows]}


@router.get("/reports/remediation", response_model=RemediationReportResponse)
def remediation_report(db: Db, user: User, round_id: int | None = None, semester_id: int | None = None) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    selected = _version_scope(db, round_id, semester_id)
    rows = db.execute(text("SELECT rc.id, rc.group_id, g.code AS group_code, rc.due_at, rc.status, rc.verifier_lecturer_id FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id LEFT JOIN session_results sr ON sr.id = rc.session_result_id LEFT JOIN sessions s ON s.id = sr.session_id LEFT JOIN schedule_assignments sa ON sa.schedule_version_id=s.schedule_version_id AND sa.group_id=s.group_id LEFT JOIN projects p ON p.id = sa.project_id LEFT JOIN schedule_versions sv ON sv.id = s.schedule_version_id WHERE (CAST(:round_id AS INTEGER) IS NULL OR sv.round_id = CAST(:round_id AS INTEGER)) AND (CAST(:semester_id AS INTEGER) IS NULL OR p.semester_id = CAST(:semester_id AS INTEGER)) ORDER BY rc.due_at"), {"round_id": round_id, "semester_id": semester_id}).mappings().all()
    return {"round_id": round_id, "version": selected, "rows": [dict(row) for row in rows]}


@router.get("/reports/outcomes", response_model=OutcomesReportResponse)
def outcomes_report(db: Db, user: User, round_id: int | None = None, semester_id: int | None = None) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    selected = _version_scope(db, round_id, semester_id)
    rows = db.execute(text("SELECT r.type, sr.outcome, COUNT(*) AS count FROM session_results sr JOIN sessions s ON s.id = sr.session_id JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id WHERE (CAST(:round_id AS INTEGER) IS NULL OR r.id = CAST(:round_id AS INTEGER)) AND (CAST(:semester_id AS INTEGER) IS NULL OR r.semester_id = CAST(:semester_id AS INTEGER)) GROUP BY r.type, sr.outcome ORDER BY r.type, sr.outcome"), {"round_id": round_id, "semester_id": semester_id}).mappings().all()
    return {"round_id": round_id, "version": selected, "rows": [dict(row) for row in rows]}


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(db: Db, user: User, limit: int = 50) -> list[dict[str, Any]]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    scope = "" if user.account_id is None and is_management_user(user) else "WHERE recipient_account_id = :account_id"
    rows = db.execute(text(f"SELECT id, event_type, payload, status, sent_at, created_at FROM notifications {scope} ORDER BY created_at DESC LIMIT :limit"), {"limit": min(max(limit, 1), 100), "account_id": user.account_id}).mappings().all()
    return [dict(row) for row in rows]


@router.post("/notifications/{notification_id}/retry", response_model=NotificationRetryResponse)
def retry_notification(notification_id: int, db: Db, user: User) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER")
    with db.begin():
        row = db.execute(text("UPDATE notifications SET status = 'PENDING', sent_at = NULL WHERE id = :id AND status = 'FAILED' RETURNING id, status, dedupe_key"), {"id": notification_id}).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "NOTIFICATION_NOT_RETRYABLE", "message": "Failed notification does not exist."})
        db.execute(text("UPDATE outbox_jobs SET status = 'PENDING', available_at = now() WHERE dedupe_key = :dedupe_key AND status = 'FAILED'"), {"dedupe_key": row["dedupe_key"]})
    return dict(row)


@router.get("/schedule/versions/{version_id}/calendar.ics")
def calendar_export(version_id: int, db: Db, user: User) -> Response:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    if user.role not in {"ADMIN", "MANAGER"} and not visible_session_ids(db, user, version_id=version_id):
        raise HTTPException(status_code=403, detail="Calendar is outside the actor's scope.")
    session_ids = visible_session_ids(db, user, version_id=version_id)
    scope = "" if user.role in {"ADMIN", "MANAGER"} else "AND s.id = ANY(:session_ids)"
    rows = db.execute(text(f"SELECT s.id, g.code AS group_code, rm.code AS room_code, s.start_at, s.end_at FROM sessions s JOIN groups g ON g.id = s.group_id JOIN schedule_assignments sa ON sa.schedule_version_id=s.schedule_version_id AND sa.group_id=s.group_id LEFT JOIN rooms rm ON rm.id = s.room_id WHERE s.schedule_version_id = :version_id {scope} ORDER BY s.start_at"), {"version_id": version_id, "session_ids": list(session_ids) or [0]}).mappings().all()
    if not rows:
        exists = db.execute(text("SELECT 1 FROM schedule_versions WHERE id = :id"), {"id": version_id}).scalar_one_or_none()
        if exists is None:
            raise HTTPException(status_code=404, detail={"code": "VERSION_NOT_FOUND", "message": "ScheduleVersion does not exist."})
    content = build_ical([dict(row) for row in rows], calendar_name=f"Capstone Scheduler {version_id}")
    return Response(content=content, media_type="text/calendar; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="schedule-{version_id}.ics"'})


@router.get("/my/schedule", response_model=PersonalScheduleResponse)
def personal_schedule(
    db: Db,
    user: User,
    version_id: int | None = None,
    from_at: datetime | None = None,
    to_at: datetime | None = None,
) -> dict[str, Any]:
    _require(user, "ADMIN", "MANAGER", "LECTURER", "STUDENT")
    selected = _version_scope(db) if version_id is None else db.execute(
        text(
            "SELECT sv.id AS version_id, sv.round_id, sv.status, sv.created_at, r.type, r.semester_id, s.code AS semester_code "
            "FROM schedule_versions sv JOIN rounds r ON r.id = sv.round_id JOIN semesters s ON s.id = r.semester_id WHERE sv.id = :version_id"
        ),
        {"version_id": version_id},
    ).mappings().one_or_none()
    if selected is None:
        return {"version": None, "generated_at": datetime.now(UTC), "sessions": []}
    visible = visible_session_ids(db, user, version_id=int(selected["version_id"]))
    if not visible:
        return {"version": selected, "generated_at": datetime.now(UTC), "sessions": []}
    rows = db.execute(
        text(
            "SELECT s.id, s.group_id, g.code AS group_code, sa.project_id, s.start_at, s.end_at, s.room_id, rm.code AS room_code, s.status "
            "FROM sessions s JOIN groups g ON g.id = s.group_id JOIN schedule_assignments sa ON sa.schedule_version_id=s.schedule_version_id AND sa.group_id=s.group_id LEFT JOIN rooms rm ON rm.id = s.room_id "
            "WHERE s.schedule_version_id = :version_id AND s.id = ANY(:session_ids) "
            "AND (CAST(:from_at AS TIMESTAMPTZ) IS NULL OR s.end_at > CAST(:from_at AS TIMESTAMPTZ)) "
            "AND (CAST(:to_at AS TIMESTAMPTZ) IS NULL OR s.start_at < CAST(:to_at AS TIMESTAMPTZ)) ORDER BY s.start_at, s.id"
        ),
        {"version_id": int(selected["version_id"]), "session_ids": list(visible), "from_at": from_at, "to_at": to_at},
    ).mappings().all()
    return {"version": selected, "generated_at": datetime.now(UTC), "sessions": [dict(row) for row in rows]}
