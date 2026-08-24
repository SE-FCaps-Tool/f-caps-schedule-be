"""Scoped lecturer and leader portal read models for the separated frontend."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import ApiDataEnvelope, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.registration_phase import effective_registration_deadline
from app.response_models import (
    TargetLeaderDashboardResponse,
    TargetLeaderPortalSessionResponse,
    TargetLecturerPortalSessionResponse,
    TargetPortalInvitationResponse,
    TargetPortalRemediationResponse,
    TargetSupervisedProjectResponse,
)
from app.services.access import lecturer_id_for_account, student_id_for_account

router = APIRouter(prefix="/api/v1", tags=["target-portals"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


def _invitation_status(status: str, deadline: datetime | None) -> str:
    if status == "PENDING" and deadline is not None and deadline < datetime.now(UTC):
        return "EXPIRED"
    return status


def _lecturer_id(db: Session, user: CurrentUser) -> int:
    if user.role != "LECTURER":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer portal access is required."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    return int(lecturer_id)


def _student_id(db: Session, user: CurrentUser) -> int:
    if user.role != "STUDENT":
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Leader portal access is required."})
    student_id = student_id_for_account(db, user.account_id)
    if student_id is None:
        raise HTTPException(status_code=403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Student profile is not linked."})
    return int(student_id)


@router.get(
    "/lecturer/me/invitations",
    response_model=ApiDataEnvelope[list[TargetPortalInvitationResponse]],
    response_model_exclude_unset=True,
)
def lecturer_invitations(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT ri.round_id, ri.lecturer_id, ri.status::text AS status, ri.responded_at, "
            "r.name AS round_name, r.type::text AS round_type, "
            "r.registration_deadline, r.group_preference_deadline "
            "FROM round_invitations ri JOIN rounds r ON r.id = ri.round_id "
            "WHERE ri.lecturer_id = :lecturer_id "
            "ORDER BY r.id DESC"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    invitations = [
        {
            "id": f"inv_{row['round_id']}_{row['lecturer_id']}",
            "round": {
                # Keep this a JSON string while remaining compatible with the
                # existing integer round path parameter used by the respond API.
                "id": str(row["round_id"]),
                "name": row["round_name"] or row["round_type"],
                "type": row["round_type"],
                "registrationDeadline": effective_registration_deadline(
                    row["registration_deadline"], row["group_preference_deadline"]
                ) if row["registration_deadline"] is not None else None,
            },
            "status": _invitation_status(
                row["status"],
                effective_registration_deadline(
                    row["registration_deadline"], row["group_preference_deadline"]
                ) if row["registration_deadline"] is not None else None,
            ),
            "respondedAt": row["responded_at"],
        }
        for row in rows
    ]
    return success_payload(invitations)


@router.get(
    "/lecturer/me/sessions",
    response_model=ApiDataEnvelope[list[TargetLecturerPortalSessionResponse]],
    response_model_exclude_unset=True,
)
def lecturer_sessions(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT DISTINCT s.id, sv.round_id, s.start_at, s.end_at, s.status, "
            "g.id AS group_id, g.code AS group_code, p.code AS project_code, "
            "rm.code AS room_code, r.type AS round_type "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id "
            "JOIN projects p ON p.id = g.project_id LEFT JOIN rooms rm ON rm.id = s.room_id "
            "JOIN council_members cm ON cm.council_id = s.council_id "
            "WHERE cm.lecturer_id = :lecturer_id AND sv.status IN ('ACTIVE', 'PUBLISHED') "
            "ORDER BY s.start_at, s.id"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


@router.get(
    "/lecturer/me/supervised-projects",
    response_model=ApiDataEnvelope[list[TargetSupervisedProjectResponse]],
    response_model_exclude_unset=True,
)
def lecturer_supervised_projects(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT p.id, p.code, COALESCE(p.title_en, p.title_vi, p.title) AS title, "
            "p.title_vi, p.title_en, p.status::text AS status, p.semester_id, "
            "s.code AS semester_code, ps.supervisor_type, "
            "grp.id AS group_id, grp.code AS group_code, grp.member_count, "
            "grp.leader, grp.members "
            "FROM project_supervisors ps JOIN projects p ON p.id = ps.project_id "
            "JOIN semesters s ON s.id = p.semester_id "
            "LEFT JOIN LATERAL ( "
            "  SELECT g.id, g.code, member_data.member_count, "
            "         member_data.members, member_data.members -> 0 AS leader "
            "  FROM groups g "
            "  LEFT JOIN LATERAL ( "
            "    SELECT COUNT(*)::int AS member_count, "
            "           COALESCE(jsonb_agg( "
            "             jsonb_build_object( "
            "               'id', st.id, "
            "               'code', st.student_code, "
            "               'name', a.display_name, "
            "               'role', gm.membership_role::text, "
            "               'status', gm.status::text "
            "             ) ORDER BY CASE WHEN gm.membership_role::text = 'LEADER' THEN 0 ELSE 1 END, st.id "
            "           ), '[]'::jsonb) AS members "
            "    FROM group_memberships gm "
            "    JOIN students st ON st.id = gm.student_id "
            "    JOIN accounts a ON a.id = st.account_id "
            "    WHERE gm.group_id = g.id AND gm.status::text = 'ACTIVE' "
            "  ) member_data ON TRUE "
            "  WHERE g.project_id = p.id ORDER BY g.id LIMIT 1 "
            ") grp ON TRUE "
            "WHERE ps.lecturer_id = :lecturer_id "
            "ORDER BY s.id DESC, p.code"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    projects = []
    for row in rows:
        project = dict(row)
        group_id = project.pop("group_id", None)
        group_code = project.pop("group_code", None)
        member_count = project.pop("member_count", None)
        leader = project.pop("leader", None)
        members = project.pop("members", None)
        if group_id is None:
            project["group"] = None
        else:
            project["group"] = {
                "id": group_id,
                "code": group_code,
                "member_count": int(member_count or 0),
                "leader": (
                    {key: leader.get(key) for key in ("id", "name", "code")}
                    if isinstance(leader, dict)
                    else None
                ),
                "members": members if isinstance(members, list) else [],
            }
        projects.append(project)
    return success_payload(projects, meta={"page": 1, "pageSize": len(projects), "total": len(projects)})


@router.get(
    "/lecturer/me/remediations",
    response_model=ApiDataEnvelope[list[TargetPortalRemediationResponse]],
    response_model_exclude_unset=True,
)
def lecturer_remediations(db: Db, user: User) -> dict[str, Any]:
    lecturer_id = _lecturer_id(db, user)
    rows = db.execute(
        text(
            "SELECT rc.id, rc.group_id, g.code AS group_code, rc.status, rc.due_at, "
            "rc.verifier_lecturer_id, rc.note, r.type AS round_type "
            "FROM remediation_cases rc JOIN groups g ON g.id = rc.group_id "
            "JOIN session_results sr ON sr.id = rc.session_result_id JOIN sessions s ON s.id = sr.session_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id JOIN rounds r ON r.id = sv.round_id "
            "WHERE rc.verifier_lecturer_id = :lecturer_id ORDER BY rc.due_at, rc.id"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})


def _leader_group_ids(db: Session, student_id: int) -> list[int]:
    return [int(row[0]) for row in db.execute(text("SELECT group_id FROM group_memberships WHERE student_id = :student_id AND membership_role = 'LEADER' AND status = 'ACTIVE'"), {"student_id": student_id}).all()]


def _local_session(session: Any | None) -> dict[str, Any] | None:
    if session is None:
        return None
    local_start = session["start_at"].astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
    local_end = session["end_at"].astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
    return {
        "id": str(session["id"]),
        "date": local_start.date().isoformat(),
        "startTime": local_start.strftime("%H:%M"),
        "endTime": local_end.strftime("%H:%M"),
        "room": session["room_code"],
    }


@router.get(
    "/leader/me/dashboard",
    response_model=ApiDataEnvelope[TargetLeaderDashboardResponse],
    response_model_exclude_unset=True,
)
def leader_dashboard(db: Db, user: User) -> dict[str, Any]:
    student_id = _student_id(db, user)
    group = db.execute(
        text(
            "SELECT g.id, g.code, g.status::text AS group_status, g.project_id, "
            "COUNT(active_members.id) AS member_count, "
            "p.code AS project_code, COALESCE(p.title_en, p.title_vi, p.title) AS project_title, "
            "p.title_vi AS project_title_vi, p.title_en AS project_title_en, p.status::text AS project_status "
            "FROM group_memberships leader "
            "JOIN groups g ON g.id = leader.group_id "
            "LEFT JOIN group_memberships active_members ON active_members.group_id = g.id AND active_members.status = 'ACTIVE' "
            "LEFT JOIN projects p ON p.id = g.project_id "
            "LEFT JOIN semesters sem ON sem.id = p.semester_id "
            "WHERE leader.student_id = :student_id AND leader.membership_role = 'LEADER' AND leader.status = 'ACTIVE' "
            "GROUP BY g.id, g.code, g.status, g.project_id, p.code, p.title, p.title_vi, p.title_en, p.status, sem.status "
            "ORDER BY (sem.status::text = 'ACTIVE') DESC NULLS LAST, g.code, g.id LIMIT 1"
        ),
        {"student_id": student_id},
    ).mappings().one_or_none()
    if group is None:
        return success_payload(
            {
                "group": None,
                "project": None,
                "mainSupervisor": None,
                "coSupervisor": None,
                "currentRound": None,
                "preferenceStatus": None,
                "deadline": None,
                "upcomingSession": None,
                "latestResult": None,
                "remediation": None,
            }
        )

    group_id = int(group["id"])
    supervisors = db.execute(
        text(
            "SELECT ps.supervisor_type::text AS supervisor_type, l.id, a.display_name "
            "FROM project_supervisors ps JOIN lecturers l ON l.id = ps.lecturer_id "
            "JOIN accounts a ON a.id = l.account_id "
            "WHERE ps.project_id = :project_id ORDER BY ps.supervisor_type, l.id"
        ),
        {"project_id": group["project_id"] or 0},
    ).mappings().all()
    supervisor_by_type = {row["supervisor_type"]: {"id": str(row["id"]), "name": row["display_name"]} for row in supervisors}

    current_round = db.execute(
        text(
            "SELECT r.id, r.name, r.type::text AS type, r.status::text AS status, "
            "r.group_selection_mode, r.registration_deadline, r.group_preference_deadline "
            "FROM round_groups rg JOIN rounds r ON r.id = rg.round_id "
            "WHERE rg.group_id = :group_id AND r.status::text = 'OPEN_REGISTRATION' "
            "ORDER BY r.id DESC LIMIT 1"
        ),
        {"group_id": group_id},
    ).mappings().one_or_none()
    preference_status = "NOT_REQUIRED"
    if current_round is not None and current_round["group_selection_mode"]:
        submitted = db.execute(
            text(
                "SELECT 1 FROM group_slot_preferences "
                "WHERE round_id = :round_id AND group_id = :group_id AND selected = TRUE LIMIT 1"
            ),
            {"round_id": current_round["id"], "group_id": group_id},
        ).scalar_one_or_none()
        preference_status = "SUBMITTED" if submitted is not None else "PENDING"

    upcoming = db.execute(
        text(
            "SELECT s.id, s.start_at, s.end_at, rm.code AS room_code "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "LEFT JOIN rooms rm ON rm.id = s.room_id "
            "WHERE s.group_id = :group_id AND sv.status::text = 'PUBLISHED' "
            "AND s.status::text = 'SCHEDULED' AND s.start_at >= now() "
            "ORDER BY s.start_at, s.id LIMIT 1"
        ),
        {"group_id": group_id},
    ).mappings().one_or_none()
    result = db.execute(
        text(
            "SELECT r.type::text AS round_type, sr.outcome::text AS outcome, sr.entered_at "
            "FROM session_results sr JOIN sessions s ON s.id = sr.session_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id "
            "WHERE s.group_id = :group_id AND sv.status::text IN ('ACTIVE', 'PUBLISHED') "
            "ORDER BY sr.entered_at DESC, sr.id DESC LIMIT 1"
        ),
        {"group_id": group_id},
    ).mappings().one_or_none()
    remediation = db.execute(
        text(
            "SELECT due_at, status::text AS status FROM remediation_cases "
            "WHERE group_id = :group_id ORDER BY due_at DESC, id DESC LIMIT 1"
        ),
        {"group_id": group_id},
    ).mappings().one_or_none()

    project = None
    if group["project_id"] is not None:
        project_status = "CANCELLED" if group["project_status"] == "ARCHIVED" else "ACTIVE"
        if group["project_status"] != "ARCHIVED" and group["group_status"] in {
            "ELIGIBLE_D12",
            "D12_CONDITIONAL",
            "PENDING_D2",
            "COMPLETED",
            "FAILED",
        }:
            project_status = group["group_status"]
        project = {
            "id": str(group["project_id"]),
            "code": group["project_code"],
            "titleVi": group["project_title_vi"] or group["project_title"],
            "titleEn": group["project_title_en"],
            "status": project_status,
        }
    round_payload = None
    if current_round is not None:
        round_payload = {
            "id": str(current_round["id"]),
            "name": current_round["name"] or current_round["type"],
            "type": current_round["type"],
            "status": current_round["status"],
        }
    result_payload = None
    if result is not None:
        local_result = result["entered_at"].astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        result_payload = {
            "roundType": result["round_type"],
            "kind": "REVIEW" if result["round_type"].startswith("REVIEW_") else "DEFENSE",
            "value": result["outcome"],
            "date": local_result.date().isoformat(),
        }
    return success_payload(
        {
            "group": {"id": str(group_id), "code": group["code"], "memberCount": int(group["member_count"]), "maxMembers": 5},
            "project": project,
            "mainSupervisor": supervisor_by_type.get("MAIN"),
            "coSupervisor": supervisor_by_type.get("CO"),
            "currentRound": round_payload,
            "preferenceStatus": preference_status,
            "deadline": effective_registration_deadline(
                current_round["registration_deadline"], current_round["group_preference_deadline"]
            ) if current_round is not None and current_round["registration_deadline"] is not None else None,
            "upcomingSession": _local_session(upcoming),
            "latestResult": result_payload,
            "remediation": None
            if remediation is None
            else {
                "deadline": remediation["due_at"],
                "status": "PENDING" if remediation["status"] == "OPEN" else remediation["status"],
            },
        }
    )


@router.get(
    "/leader/me/sessions",
    response_model=ApiDataEnvelope[list[TargetLeaderPortalSessionResponse]],
    response_model_exclude_unset=True,
)
def leader_sessions(db: Db, user: User) -> dict[str, Any]:
    student_id = _student_id(db, user)
    group_ids = _leader_group_ids(db, student_id)
    rows = db.execute(
        text(
            "SELECT s.id, sv.round_id, s.group_id, g.code AS group_code, p.code AS project_code, "
            "s.start_at, s.end_at, s.room_id, rm.code AS room_code, s.status, r.type AS round_type "
            "FROM sessions s JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds r ON r.id = sv.round_id JOIN groups g ON g.id = s.group_id "
            "LEFT JOIN projects p ON p.id = g.project_id LEFT JOIN rooms rm ON rm.id = s.room_id "
            "WHERE s.group_id = ANY(:group_ids) AND sv.status IN ('ACTIVE', 'PUBLISHED') "
            "ORDER BY s.start_at, s.id"
        ),
        {"group_ids": group_ids or [0]},
    ).mappings().all()
    return success_payload([dict(row) for row in rows], meta={"page": 1, "pageSize": len(rows), "total": len(rows)})
