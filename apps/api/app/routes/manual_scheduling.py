"""Manual scheduling draft board and publication endpoints."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date as Date
from datetime import datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api_contract import RequestModel, parse_external_id, success_payload
from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.domain.enums import RoundStatus
from app.domain.round_types import (
    DEFENSE_1_1_TYPES,
    DEFENSE_1_2_TYPES,
    REVIEW_1_1_TYPES,
    REVIEW_2_1_TYPES,
)
from app.routes.schedule_operations import _actor_id
from app.services.councils import create_council
from app.services.semester_queries import ensure_round_semester_writable

router = APIRouter(prefix="/api/v1", tags=["manual-scheduling"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
ALL_ROUND_STATUSES = frozenset(status.value for status in RoundStatus)
EDITABLE_ROUND_STATUSES = ALL_ROUND_STATUSES
# A published round keeps its public version immutable, but Manager may edit
# the DB-backed workspace draft and publish a new version after validation.
PUBLISHABLE_ROUND_STATUSES = EDITABLE_ROUND_STATUSES - {"ONGOING", "POSTPONED", "COMPLETED", "LOCKED", "CANCELLED"}
MANUAL_SESSION_PREFIX = "manual_session_"
BLOCKED_REASON_LABELS = {
    "SESSION_INCOMPLETE": "Phiên chưa đầy đủ thông tin.",
    "ROLE_STRUCTURE_INVALID": "Sai cấu trúc vai trò của đợt.",
    "LECTURER_MULTI_ROLE": "Một giảng viên đang được chọn nhiều vai.",
    "GROUP_NOT_ELIGIBLE": "Nhóm không đủ điều kiện.",
    "SUPERVISOR_REVIEW_CONFLICT": "GVHD không được chấm nhóm mình hướng dẫn.",
    "GROUP_DUPLICATED": "Nhóm đã được xếp ở phiên khác.",
    "SESSION_LIMIT_EXCEEDED": "Khung giờ vượt giới hạn số hội đồng.",
    "ROOM_DOUBLE_BOOKED": "Phòng bị trùng lịch.",
    "LECTURER_DOUBLE_BOOKED": "Giảng viên bị trùng lịch.",
    "ROOM_NOT_FOUND": "Không tìm thấy phòng.",
    "ROOM_NOT_ACTIVE": "Phòng không hoạt động.",
    "ROOM_TYPE_NOT_ALLOWED": "Loại phòng không được phép cho đợt này.",
    "LECTURER_NOT_ACCEPTED": "Giảng viên chưa chấp nhận lời mời.",
    "LECTURER_NOT_AVAILABLE": "Giảng viên không rảnh ở khung giờ này.",
    "GROUP_SLOT_NOT_SELECTED": "Nhóm chưa chọn khung giờ này.",
    "LECTURER_CONFLICT_OF_INTEREST": "Giảng viên có xung đột lợi ích với đề tài.",
    "PREVIOUS_REVIEWER_REQUIRED": "Thiếu giảng viên đã chấm ở vòng trước.",
    "LECTURER_LOAD_EXCEEDED": "Giảng viên vượt giới hạn tải.",
    "UNSCHEDULED_GROUPS": "Còn nhóm chưa được xếp lịch.",
    "H14_ROLE_SKILL_NOT_CONFIGURED": "Chưa có dữ liệu kỹ năng để kiểm tra vai trò Chủ tịch/Thư ký. Cảnh báo này không chặn công bố.",
    "H15_SUPERVISOR_RATIO_NOT_CONFIGURED": "Chưa có cấu hình batch/tỉ lệ GVHD để kiểm tra phân bổ nhóm. Cảnh báo này không chặn công bố.",
}


def _blocked_reason(codes: list[str]) -> str | None:
    if not codes:
        return None
    return "; ".join(BLOCKED_REASON_LABELS.get(code, code) for code in codes)


def _require_manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise HTTPException(status_code=403, detail={"code": "AUTH_FORBIDDEN", "message": "Bạn cần quyền Quản lý để thực hiện thao tác này."})


def _json(value: Any) -> str:
    return json.dumps(value, default=str)


def _manual_session_id(value: Any) -> int:
    if isinstance(value, int) and value > 0:
        return value
    raw = str(value).strip()
    raw = raw.removeprefix(MANUAL_SESSION_PREFIX)
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    raise HTTPException(status_code=422, detail={"code": "SESSION_NOT_FOUND", "message": "Mã phiên thủ công không hợp lệ."})


def _manual_external(session_id: int) -> str:
    return f"{MANUAL_SESSION_PREFIX}{session_id}"


def _external_group(group_id: int) -> str:
    return f"grp_{group_id}"


def _parse_positive_id(value: Any, *, prefix: str, code: str) -> int:
    try:
        return parse_external_id(value, prefix=prefix)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail={"code": code, "message": "Mã định danh không hợp lệ."}) from exc


def _role_schema(reviewer_count: int) -> list[dict[str, Any]]:
    if reviewer_count <= 0:
        return []
    if reviewer_count == 2:
        return [
            {"key": "REVIEWER_1", "label": "Review 1", "order": 1},
            {"key": "REVIEWER_2", "label": "Review 2", "order": 2},
        ]
    roles = [
        {"key": "CHAIR", "label": "Chủ tịch", "order": 1},
        {"key": "SECRETARY", "label": "Thư kí", "order": 2},
    ]
    for order in range(3, reviewer_count + 1):
        roles.append({"key": f"MEMBER_{order - 2}", "label": f"Thành viên {order - 2}", "order": order})
    return roles


def _role_lookup(reviewer_count: int) -> dict[str, dict[str, Any]]:
    return {role["key"]: role for role in _role_schema(reviewer_count)}


def _role_metadata(reviewer_count: int, role_key: str) -> dict[str, Any] | None:
    role = _role_lookup(reviewer_count).get(role_key)
    if role is None:
        return None
    return {"role_key": role["key"], "role_order": int(role["order"]), "role_label": role["label"]}


def _constraint_statuses(round_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose validation coverage so missing rule inputs are not reported as pass."""

    h11_applies = str(round_row["round_type"]) in DEFENSE_1_2_TYPES
    return [
        {
            "code": "H11_PREVIOUS_REVIEWER",
            "status": "enforced" if h11_applies else "notApplicable",
            "source": "lịch vòng trước đã công bố hoặc đang hoạt động trong cùng kỳ",
            "message": (
                "H11 đang được kiểm tra từ lịch đã công bố hoặc đang hoạt động cùng kỳ."
                if h11_applies
                else "H11 chỉ áp dụng cho đợt Bảo vệ 1.2."
            ),
        },
        {
            "code": "H14_ROLE_SKILL",
            "status": "notConfigured",
            "message": "Chưa có dữ liệu kỹ năng để kiểm tra vai trò Chủ tịch/Thư ký. Cảnh báo này không chặn công bố.",
        },
        {
            "code": "H15_SUPERVISOR_RATIO",
            "status": "notConfigured",
            "message": "Chưa có cấu hình batch/tỉ lệ GVHD để kiểm tra phân bổ nhóm. Cảnh báo này không chặn công bố.",
        },
    ]


def _not_configured_warnings(round_row: dict[str, Any]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for item in _constraint_statuses(round_row):
        if item["status"] == "notConfigured":
            warnings.append(
                _blocker(
                    f"{item['code']}_NOT_CONFIGURED",
                    str(item["message"]),
                    status="notConfigured",
                )
            )
    return warnings


def _eligible_group_status(round_type: str, status_value: str) -> bool:
    if status_value in {"FAILED", "DROPPED"}:
        return False
    expected: dict[str, set[str]] = {"DEFENSE_2": {"PENDING_D2"}}
    expected.update({round_type: {"PENDING_D11", "ELIGIBLE_D12", "D12_CONDITIONAL", "PENDING_D2"} for round_type in REVIEW_1_1_TYPES | REVIEW_2_1_TYPES})
    expected.update({round_type: {"PENDING_D11"} for round_type in DEFENSE_1_1_TYPES})
    expected.update({round_type: {"ELIGIBLE_D12", "D12_CONDITIONAL"} for round_type in DEFENSE_1_2_TYPES})
    return status_value in expected.get(round_type, set())


def _round_or_404(db: Session, round_id: int, *, for_update: bool = False) -> dict[str, Any]:
    if for_update:
        locked = db.execute(
            text("SELECT id FROM rounds WHERE id = :round_id FOR UPDATE"),
            {"round_id": round_id},
        ).scalar_one_or_none()
        if locked is None:
            raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Không tìm thấy đợt."})
    row = db.execute(
        text(
            "SELECT r.id, r.semester_id, r.type::text AS round_type, r.status::text AS round_status, "
            "r.session_duration_minutes, r.reviewer_count, r.max_groups_per_timeslot, "
            "r.group_selection_mode, r.h12_sessions_per_part, r.h12_sessions_per_day, "
            "r.h12_semester_quota, r.max_minutes_per_part, r.max_minutes_per_day, "
            "COALESCE(array_agg(rrt.room_type::text ORDER BY rrt.room_type::text) "
            "FILTER (WHERE rrt.room_type IS NOT NULL), ARRAY[]::text[]) AS room_types "
            "FROM rounds r LEFT JOIN round_room_types rrt ON rrt.round_id = r.id "
            "WHERE r.id = :round_id GROUP BY r.id"
        ),
        {"round_id": round_id},
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "ROUND_NOT_FOUND", "message": "Không tìm thấy đợt."})
    return dict(row)


def _ensure_mutable_round(row: dict[str, Any]) -> None:
    if row["round_status"] not in EDITABLE_ROUND_STATUSES:
        raise HTTPException(
            status_code=409,
            detail={"code": "ROUND_STATUS_INVALID", "message": "Đợt hiện không cho phép chỉnh lịch thủ công."},
        )


def _ensure_publishable_round(row: dict[str, Any]) -> None:
    if row["round_status"] not in PUBLISHABLE_ROUND_STATUSES:
        raise HTTPException(
            status_code=409,
            detail={"code": "ROUND_STATUS_INVALID", "message": "Đợt hiện không cho phép công bố lịch thủ công."},
        )


def _ensure_draft_row(db: Session, round_id: int, actor_id: int | None) -> int:
    return int(
        db.execute(
            text(
                "INSERT INTO manual_schedule_drafts(round_id, revision, created_by, updated_by) "
                "VALUES (:round_id, 0, :actor_id, :actor_id) "
                "ON CONFLICT (round_id) DO UPDATE SET updated_at = manual_schedule_drafts.updated_at "
                "RETURNING revision"
            ),
            {"round_id": round_id, "actor_id": actor_id},
        ).scalar_one()
    )


def _check_revision(db: Session, round_id: int, client_revision: int | None) -> int:
    revision = db.execute(
        text("SELECT revision FROM manual_schedule_drafts WHERE round_id = :round_id FOR UPDATE"),
        {"round_id": round_id},
    ).scalar_one()
    if client_revision is not None and int(client_revision) != int(revision):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "STALE_MANUAL_SCHEDULE_REVISION",
                "message": "Bản nháp lịch thủ công đã được thay đổi bởi yêu cầu khác.",
                "currentRevision": int(revision),
            },
        )
    return int(revision)


def _bump_revision(db: Session, round_id: int, actor_id: int | None) -> int:
    return int(
        db.execute(
            text(
                "UPDATE manual_schedule_drafts "
                "SET revision = revision + 1, updated_by = :actor_id, updated_at = now() "
                "WHERE round_id = :round_id RETURNING revision"
            ),
            {"round_id": round_id, "actor_id": actor_id},
        ).scalar_one()
    )


def _timeslot_id_for(
    db: Session,
    round_id: int,
    value: Any,
    *,
    session_date: Date | None,
) -> int:
    try:
        timeslot_id = parse_external_id(value, prefix="ts")
    except (TypeError, ValueError):
        raw = str(value).strip()
        match = re.fullmatch(r"slot_(\d{4})", raw)
        if match is None or session_date is None:
            raise HTTPException(status_code=422, detail={"code": "TIMESLOT_NOT_IN_ROUND", "message": "Khung giờ không thuộc đợt này."})
        timeslot_id = db.execute(
            text(
                "SELECT ts.id FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id "
                "WHERE rd.round_id = :round_id AND rd.day_date = :day "
                "AND to_char(ts.start_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'HH24MI') = :hhmm "
                "ORDER BY ts.id LIMIT 1"
            ),
            {"round_id": round_id, "day": session_date, "hhmm": match.group(1)},
        ).scalar_one_or_none()
        if timeslot_id is None:
            raise HTTPException(status_code=422, detail={"code": "TIMESLOT_NOT_IN_ROUND", "message": "Khung giờ không thuộc đợt này."})
    row = db.execute(
        text(
            "SELECT ts.id FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id "
            "WHERE ts.id = :timeslot_id AND rd.round_id = :round_id AND ts.active = TRUE"
        ),
        {"timeslot_id": int(timeslot_id), "round_id": round_id},
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=422, detail={"code": "TIMESLOT_NOT_IN_ROUND", "message": "Khung giờ không thuộc đợt này."})
    if session_date is not None:
        day = db.execute(
            text("SELECT rd.day_date FROM timeslots ts JOIN round_days rd ON rd.id = ts.round_day_id WHERE ts.id = :id"),
            {"id": int(timeslot_id)},
        ).scalar_one()
        if day != session_date:
            raise HTTPException(status_code=422, detail={"code": "TIMESLOT_NOT_IN_ROUND", "message": "Ngày của khung giờ không khớp với ngày trong request."})
    return int(timeslot_id)


def _query_list(request: Request, *names: str, parsed: list[str] | None = None) -> list[str]:
    values = list(parsed or [])
    for name in names:
        values.extend(request.query_params.getlist(name))
    return values


class ManualReviewerPayload(RequestModel):
    lecturer_id: str | int = Field(alias="lecturerId")
    role: str = Field(min_length=1, max_length=32)
    order: int | None = Field(default=None, gt=0)


class ManualSessionPayload(RequestModel):
    date: Date | None = None
    round_timeslot_id: str | int = Field(alias="roundTimeslotId")
    group_ids: list[str | int] = Field(default_factory=list, alias="groupIds")
    room_id: str | int | None = Field(default=None, alias="roomId")
    reviewers: list[ManualReviewerPayload] = Field(default_factory=list)
    client_revision: int | None = Field(default=None, alias="clientRevision")


class BulkManualSessionPayload(RequestModel):
    id: str | int | None = None
    date: Date | None = None
    round_timeslot_id: str | int = Field(alias="roundTimeslotId")
    group_ids: list[str | int] = Field(default_factory=list, alias="groupIds")
    room_id: str | int | None = Field(default=None, alias="roomId")
    reviewers: list[ManualReviewerPayload] = Field(default_factory=list)


class BulkUpsertPayload(RequestModel):
    client_revision: int | None = Field(default=None, alias="clientRevision")
    allow_draft_incomplete: bool = Field(default=False, alias="allowDraftIncomplete")
    sessions: list[BulkManualSessionPayload] = Field(default_factory=list)
    deleted_session_ids: list[str | int] = Field(default_factory=list, alias="deletedSessionIds")
    source_schedule_version_id: int | None = Field(default=None, alias="sourceVersionId", gt=0)


class ValidatePayload(RequestModel):
    client_revision: int | None = Field(default=None, alias="clientRevision")


class PublishPayload(RequestModel):
    client_revision: int | None = Field(default=None, alias="clientRevision")
    confirm_warnings: list[str] = Field(default_factory=list, alias="confirmWarnings")
    reason: str | None = Field(default=None, max_length=1000)


def _normalize_reviewers(
    db: Session,
    reviewers: list[ManualReviewerPayload],
    reviewer_count: int,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen_lecturers: set[int] = set()
    seen_roles: set[str] = set()
    for item in reviewers:
        lecturer_id = _parse_positive_id(item.lecturer_id, prefix="lec", code="LECTURER_NOT_FOUND")
        role_key = item.role.strip().upper()
        role_meta = _role_metadata(reviewer_count, role_key)
        if role_meta is None:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "ROLE_STRUCTURE_INVALID",
                    "message": "Vai trò giảng viên phản biện không thuộc cấu trúc vai trò của đợt.",
                    "role": role_key,
                    "expectedRoles": [role["key"] for role in _role_schema(reviewer_count)],
                },
            )
        if lecturer_id in seen_lecturers:
            raise HTTPException(
                status_code=422,
                detail={"code": "LECTURER_MULTI_ROLE", "message": "Một giảng viên chỉ được giữ một vai trò trong một hội đồng."},
            )
        if role_key in seen_roles:
            raise HTTPException(
                status_code=422,
                detail={"code": "ROLE_STRUCTURE_INVALID", "message": "Mỗi vai trò trong hội đồng chỉ được chọn một lần."},
            )
        seen_lecturers.add(lecturer_id)
        seen_roles.add(role_key)
        snapshot_name = db.execute(
            text("SELECT a.display_name FROM lecturers l JOIN accounts a ON a.id = l.account_id WHERE l.id = :id"),
            {"id": lecturer_id},
        ).scalar_one_or_none()
        normalized.append(
            {
                "lecturer_id": lecturer_id,
                "role_key": role_key,
                "role_order": role_meta["role_order"],
                "snapshot_name": str(snapshot_name or lecturer_id)[:160],
            }
        )
    return normalized


def _replace_session_children(
    db: Session,
    session_id: int,
    payload: ManualSessionPayload | BulkManualSessionPayload,
    reviewer_count: int,
) -> None:
    db.execute(text("DELETE FROM manual_schedule_session_groups WHERE session_id = :id"), {"id": session_id})
    db.execute(text("DELETE FROM manual_schedule_session_" "reviewers WHERE session_id = :id"), {"id": session_id})
    seen_groups: set[int] = set()
    for position, raw_group_id in enumerate(payload.group_ids, start=1):
        group_id = _parse_positive_id(raw_group_id, prefix="grp", code="GROUP_NOT_ELIGIBLE")
        if group_id in seen_groups:
            continue
        seen_groups.add(group_id)
        db.execute(
            text(
                "INSERT INTO manual_schedule_session_groups(session_id, group_id, position) "
                "VALUES (:session_id, :group_id, :position)"
            ),
            {"session_id": session_id, "group_id": group_id, "position": position},
        )
    for reviewer in _normalize_reviewers(db, payload.reviewers, reviewer_count):
        db.execute(
            text(
                "INSERT INTO manual_schedule_session_"
                "reviewers(session_id, lecturer_id, role_key, role_order, snapshot_name) "
                "VALUES (:session_id, :lecturer_id, :role_key, :role_order, :snapshot_name)"
            ),
            {"session_id": session_id, **reviewer},
        )


def _ensure_registered_timeslot(
    db: Session,
    round_id: int,
    timeslot_id: int,
    payload: ManualSessionPayload | BulkManualSessionPayload,
) -> None:
    """Manual edits may only move a selected group into one of its chosen slots."""
    group_ids = {
        _parse_positive_id(raw_group_id, prefix="grp", code="GROUP_NOT_ELIGIBLE")
        for raw_group_id in payload.group_ids
    }
    if not group_ids:
        return

    mode_enabled = db.execute(
        text("SELECT group_selection_mode FROM rounds WHERE id = :round_id"),
        {"round_id": round_id},
    ).scalar_one_or_none()
    if not mode_enabled:
        return

    selected_rows = db.execute(
        text(
            "SELECT group_id, timeslot_id FROM group_slot_preferences "
            "WHERE round_id = :round_id AND selected = TRUE "
            "AND group_id = ANY(CAST(:group_ids AS BIGINT[]))"
        ),
        {"round_id": round_id, "group_ids": sorted(group_ids)},
    ).all()
    selected_by_group: dict[int, set[int]] = defaultdict(set)
    for group_id, selected_timeslot_id in selected_rows:
        selected_by_group[int(group_id)].add(int(selected_timeslot_id))

    invalid_groups = sorted(
        group_id
        for group_id, selected_timeslots in selected_by_group.items()
        if timeslot_id not in selected_timeslots
    )
    if invalid_groups:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "GROUP_SLOT_NOT_SELECTED",
                "message": "Chỉ được xếp nhóm vào khung giờ mà nhóm đã đăng ký.",
                "groupIds": [_external_group(group_id) for group_id in invalid_groups],
                "roundTimeslotId": str(timeslot_id),
            },
        )


def _upsert_session(
    db: Session,
    round_id: int,
    payload: ManualSessionPayload | BulkManualSessionPayload,
    *,
    reviewer_count: int,
    actor_id: int | None,
    session_id: int | None = None,
) -> int:
    timeslot_id = _timeslot_id_for(db, round_id, payload.round_timeslot_id, session_date=payload.date)
    _ensure_registered_timeslot(db, round_id, timeslot_id, payload)
    room_id = None if payload.room_id is None else _parse_positive_id(payload.room_id, prefix="room", code="ROOM_NOT_FOUND")
    if session_id is None:
        session_id = int(
            db.execute(
                text(
                    "INSERT INTO manual_schedule_sessions(round_id, timeslot_id, room_id, status, created_by, updated_by) "
                    "VALUES (:round_id, :timeslot_id, :room_id, 'DRAFT', :actor_id, :actor_id) RETURNING id"
                ),
                {"round_id": round_id, "timeslot_id": timeslot_id, "room_id": room_id, "actor_id": actor_id},
            ).scalar_one()
        )
    else:
        # This updates only the manual draft row. A published_session_id is kept
        # as the live baseline; the actual published session is never mutated.
        updated = db.execute(
            text(
                "UPDATE manual_schedule_sessions SET timeslot_id = :timeslot_id, room_id = :room_id, "
                "status = 'DRAFT', updated_by = :actor_id, updated_at = now() "
                "WHERE id = :id AND round_id = :round_id RETURNING id"
            ),
            {
                "id": session_id,
                "round_id": round_id,
                "timeslot_id": timeslot_id,
                "room_id": room_id,
                "actor_id": actor_id,
            },
        ).scalar_one_or_none()
        if updated is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Không tìm thấy phiên lịch thủ công."})
    _replace_session_children(db, session_id, payload, reviewer_count)
    return int(session_id)


def _load_revision(db: Session, round_id: int) -> int:
    return int(
        db.execute(
            text("SELECT COALESCE((SELECT revision FROM manual_schedule_drafts WHERE round_id = :round_id), 0)"),
            {"round_id": round_id},
        ).scalar_one()
    )


def _load_manual_sessions(db: Session, round_id: int) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT ms.id, ms.round_id, ms.timeslot_id, ms.room_id, ms.status, ms.published_session_id, "
            "rd.day_date, ts.start_at, ts.end_at, rm.code AS room_code, rm.name AS room_name, "
            "rm.room_type::text AS room_type, rm.capacity AS room_capacity "
            "FROM manual_schedule_sessions ms "
            "JOIN timeslots ts ON ts.id = ms.timeslot_id JOIN round_days rd ON rd.id = ts.round_day_id "
            "LEFT JOIN rooms rm ON rm.id = ms.room_id "
            "WHERE ms.round_id = :round_id ORDER BY ts.start_at, ms.id"
        ),
        {"round_id": round_id},
    ).mappings().all()
    session_ids = [int(row["id"]) for row in rows]
    group_rows = db.execute(
        text(
            "SELECT msg.session_id, g.id AS group_id, g.code AS group_code, g.status::text AS group_status, "
            "g.project_id, COALESCE(member_counts.active_member_count, 0) AS active_member_count, "
            "leader.display_name AS leader_name, "
            "COALESCE(array_agg(DISTINCT ps.lecturer_id::text) FILTER (WHERE ps.lecturer_id IS NOT NULL), ARRAY[]::text[]) AS supervisor_ids "
            "FROM manual_schedule_session_groups msg JOIN groups g ON g.id = msg.group_id "
            "LEFT JOIN project_supervisors ps ON ps.project_id = g.project_id "
            "LEFT JOIN LATERAL ( "
            "  SELECT COUNT(*)::int AS active_member_count FROM group_memberships gm "
            "  WHERE gm.group_id = g.id AND gm.status = 'ACTIVE' "
            ") member_counts ON TRUE "
            "LEFT JOIN LATERAL ( "
            "  SELECT a.display_name FROM group_memberships gm "
            "  JOIN students st ON st.id = gm.student_id JOIN accounts a ON a.id = st.account_id "
            "  WHERE gm.group_id = g.id AND gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER' "
            "  ORDER BY gm.id LIMIT 1 "
            ") leader ON TRUE "
            "WHERE msg.session_id = ANY(CAST(:session_ids AS BIGINT[])) "
            "GROUP BY msg.session_id, msg.position, g.id, g.code, g.status, g.project_id, "
            "member_counts.active_member_count, leader.display_name ORDER BY msg.session_id, msg.position"
        ),
        {"session_ids": session_ids or [0]},
    ).mappings().all()
    reviewer_rows = db.execute(
        text(
            "SELECT msr.session_id, l.id AS lecturer_id, l.lecturer_code, a.display_name AS lecturer_name, "
            "msr.role_key, msr.role_order, msr.snapshot_name "
            "FROM manual_schedule_session_"
            "reviewers msr "
            "JOIN lecturers l ON l.id = msr.lecturer_id JOIN accounts a ON a.id = l.account_id "
            "WHERE msr.session_id = ANY(CAST(:session_ids AS BIGINT[])) "
            "ORDER BY msr.session_id, msr.role_order, msr.lecturer_id"
        ),
        {"session_ids": session_ids or [0]},
    ).mappings().all()
    groups_by_session: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in group_rows:
        groups_by_session[int(row["session_id"])].append(
            {
                "groupId": _external_group(int(row["group_id"])),
                "groupCode": row["group_code"],
                "leaderName": row["leader_name"],
                "activeMemberCount": int(row["active_member_count"] or 0),
                "supervisorIds": list(row["supervisor_ids"] or []),
                "_group_id": int(row["group_id"]),
                "_project_id": row["project_id"],
                "_group_status": row["group_status"],
            }
        )
    reviewers_by_session: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in reviewer_rows:
        reviewers_by_session[int(row["session_id"])].append(
            {
                "lecturerId": str(row["lecturer_id"]),
                "lecturerCode": row["lecturer_code"],
                "lecturerName": row["lecturer_name"],
                "role": row["role_key"],
                "roleLabel": _role_label(row["role_key"]),
                "order": int(row["role_order"]),
                "_lecturer_id": int(row["lecturer_id"]),
            }
        )
    result: list[dict[str, Any]] = []
    for row in rows:
        local_start = row["start_at"].astimezone(VN_TZ)
        local_end = row["end_at"].astimezone(VN_TZ)
        room = None
        if row["room_id"] is not None:
            room = {
                "roomId": int(row["room_id"]),
                "roomCode": row["room_code"],
                "roomName": row["room_name"],
                "type": row["room_type"],
                "capacity": row["room_capacity"],
            }
        result.append(
            {
                "id": _manual_external(int(row["id"])),
                "date": row["day_date"].isoformat(),
                "roundTimeslotId": str(row["timeslot_id"]),
                "startTime": local_start.strftime("%H:%M"),
                "endTime": local_end.strftime("%H:%M"),
                "status": row["status"],
                "groups": groups_by_session.get(int(row["id"]), []),
                "room": room,
                "reviewers": reviewers_by_session.get(int(row["id"]), []),
                "blockers": [],
                "warnings": [],
                "_id": int(row["id"]),
                "_timeslot_id": int(row["timeslot_id"]),
                "_room_id": row["room_id"],
                "_start_at": row["start_at"],
                "_end_at": row["end_at"],
                "_day": row["day_date"].isoformat(),
            }
        )
    return result


def _role_label(role_key: str) -> str:
    if role_key == "CHAIR":
        return "Chủ tịch"
    if role_key == "SECRETARY":
        return "Thư kí"
    if role_key.startswith("MEMBER_"):
        return "Thành viên " + role_key.split("_", 1)[1]
    if role_key.startswith("REVIEWER_"):
        return "Review " + role_key.split("_", 1)[1]
    return role_key


def _public_sessions(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public: list[dict[str, Any]] = []
    for session in sessions:
        item = {key: value for key, value in session.items() if not key.startswith("_")}
        item["groups"] = [
            {key: value for key, value in group.items() if not key.startswith("_")}
            for group in item["groups"]
        ]
        item["reviewers"] = [
            {key: value for key, value in reviewer.items() if not key.startswith("_")}
            for reviewer in item["reviewers"]
        ]
        public.append(item)
    return public


def _blocker(
    code: str,
    message: str,
    *,
    session_id: int | None = None,
    field: str | None = None,
    related_session_ids: list[int] | None = None,
    **details: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
        "sessionId": _manual_external(session_id) if session_id is not None else None,
        "field": field,
    }
    if related_session_ids:
        payload["relatedSessionIds"] = [_manual_external(item) for item in related_session_ids]
    payload.update(details)
    return payload


def _validate_manual(db: Session, round_row: dict[str, Any], sessions: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = _not_configured_warnings(round_row)
    expected_roles = _role_schema(int(round_row["reviewer_count"]))
    expected_role_keys = {role["key"] for role in expected_roles}
    scheduled_group_ids: list[int] = []

    group_to_sessions: dict[int, list[int]] = defaultdict(list)
    slot_to_sessions: dict[int, list[int]] = defaultdict(list)
    room_slot: dict[tuple[int, int], list[int]] = defaultdict(list)
    reviewer_slot: dict[tuple[int, int], list[int]] = defaultdict(list)
    part_minutes: dict[tuple[int, str, str], int] = defaultdict(int)
    day_minutes: dict[tuple[int, str], int] = defaultdict(int)
    part_count: dict[tuple[int, str, str], int] = defaultdict(int)
    day_count: dict[tuple[int, str], int] = defaultdict(int)

    for session in sessions:
        sid = int(session["_id"])
        timeslot_id = int(session["_timeslot_id"])
        slot_to_sessions[timeslot_id].append(sid)
        if not session["groups"]:
            blockers.append(_blocker("SESSION_INCOMPLETE", "Phiên chưa có nhóm.", session_id=sid, field="groupIds"))
        if session["_room_id"] is None:
            blockers.append(_blocker("SESSION_INCOMPLETE", "Phiên chưa có phòng.", session_id=sid, field="roomId"))
        else:
            room_slot[(int(session["_room_id"]), timeslot_id)].append(sid)
        if len(session["reviewers"]) != int(round_row["reviewer_count"]):
            blockers.append(
                _blocker(
                    "SESSION_INCOMPLETE",
                    f"Phiên cần đủ {round_row['reviewer_count']} giảng viên phản biện.",
                    session_id=sid,
                    field="reviewers",
                )
            )
        role_keys = {reviewer["role"] for reviewer in session["reviewers"]}
        if role_keys and role_keys != expected_role_keys:
            blockers.append(
                _blocker(
                    "ROLE_STRUCTURE_INVALID",
                    "Vai trò giảng viên không khớp cấu trúc của đợt.",
                    session_id=sid,
                    field="reviewers",
                    expectedRoles=[role["key"] for role in expected_roles],
                )
            )
        reviewer_ids = [int(reviewer["_lecturer_id"]) for reviewer in session["reviewers"]]
        if len(set(reviewer_ids)) != len(reviewer_ids):
            blockers.append(_blocker("LECTURER_MULTI_ROLE", "Một giảng viên chỉ được giữ một vai trò trong một hội đồng.", session_id=sid, field="reviewers"))
        for reviewer_id in reviewer_ids:
            reviewer_slot[(reviewer_id, timeslot_id)].append(sid)
            duration_minutes = max(0, int((session["_end_at"] - session["_start_at"]).total_seconds() // 60))
            day = str(session["_day"])
            part = "AM" if session["_start_at"].astimezone(VN_TZ).hour < 13 else "PM"
            part_minutes[(reviewer_id, day, part)] += duration_minutes
            day_minutes[(reviewer_id, day)] += duration_minutes
            part_count[(reviewer_id, day, part)] += 1
            day_count[(reviewer_id, day)] += 1
        for group in session["groups"]:
            group_id = int(group["_group_id"])
            scheduled_group_ids.append(group_id)
            group_to_sessions[group_id].append(sid)
            if not _eligible_group_status(str(round_row["round_type"]), str(group["_group_status"])):
                blockers.append(
                    _blocker(
                        "GROUP_NOT_ELIGIBLE",
                        "Trạng thái nhóm không đủ điều kiện cho loại đợt này.",
                        session_id=sid,
                        field="groupIds",
                        groupId=_external_group(group_id),
                    )
                )
            supervisors = {int(value) for value in group.get("supervisorIds") or []}
            conflict_supervisors = supervisors.intersection(reviewer_ids)
            if conflict_supervisors:
                blockers.append(
                    _blocker(
                        "SUPERVISOR_REVIEW_CONFLICT",
                        "GVHD không được chấm nhóm mình hướng dẫn.",
                        session_id=sid,
                        field="reviewers",
                        groupId=_external_group(group_id),
                        lecturerIds=[str(value) for value in sorted(conflict_supervisors)],
                    )
                )
    for group_id, session_ids in group_to_sessions.items():
        if len(session_ids) > 1:
            blockers.append(
                _blocker(
                    "GROUP_DUPLICATED",
                    "Nhóm đã được xếp ở hơn một phiên thủ công.",
                    session_id=session_ids[0],
                    field="groupIds",
                    related_session_ids=session_ids[1:],
                    groupId=_external_group(group_id),
                )
            )
    if round_row["max_groups_per_timeslot"] is not None:
        for timeslot_id, session_ids in slot_to_sessions.items():
            if len(session_ids) > int(round_row["max_groups_per_timeslot"]):
                blockers.append(
                    _blocker(
                        "SESSION_LIMIT_EXCEEDED",
                        "Khung giờ vượt giới hạn số hội đồng được phép.",
                        session_id=session_ids[0],
                        related_session_ids=session_ids[1:],
                        roundTimeslotId=str(timeslot_id),
                        limit=int(round_row["max_groups_per_timeslot"]),
                        count=len(session_ids),
                    )
                )
    for session_ids in room_slot.values():
        if len(session_ids) > 1:
            blockers.append(
                _blocker(
                    "ROOM_DOUBLE_BOOKED",
                    "Phòng đã được dùng bởi phiên khác cùng khung giờ.",
                    session_id=session_ids[0],
                    field="roomId",
                    related_session_ids=session_ids[1:],
                )
            )
    for session_ids in reviewer_slot.values():
        if len(session_ids) > 1:
            blockers.append(
                _blocker(
                    "LECTURER_DOUBLE_BOOKED",
                    "Giảng viên đã được xếp ở phiên khác cùng khung giờ.",
                    session_id=session_ids[0],
                    field="reviewers",
                    related_session_ids=session_ids[1:],
                )
            )

    _validate_against_database(db, round_row, sessions, blockers)

    h12_part_limit = int(round_row["max_minutes_per_part"] or 0) or None
    h12_day_limit = int(round_row["max_minutes_per_day"] or 0) or None
    if h12_part_limit is None:
        h12_part_session_limit = int(round_row["h12_sessions_per_part"] or 0) or None
    else:
        h12_part_session_limit = None
    if h12_day_limit is None:
        h12_day_session_limit = int(round_row["h12_sessions_per_day"] or 0) or None
    else:
        h12_day_session_limit = None
    for (lecturer_id, day, part), minutes in part_minutes.items():
        if h12_part_limit is not None and minutes > h12_part_limit:
            blockers.append(_blocker("LECTURER_LOAD_EXCEEDED", "Giảng viên vượt giới hạn số phút trong buổi.", field="reviewers", lecturerId=str(lecturer_id), date=day, part=part))
    for (lecturer_id, day), minutes in day_minutes.items():
        if h12_day_limit is not None and minutes > h12_day_limit:
            blockers.append(_blocker("LECTURER_LOAD_EXCEEDED", "Giảng viên vượt giới hạn số phút trong ngày.", field="reviewers", lecturerId=str(lecturer_id), date=day))
    for (lecturer_id, day, part), count in part_count.items():
        if h12_part_session_limit is not None and count > h12_part_session_limit:
            blockers.append(_blocker("LECTURER_LOAD_EXCEEDED", "Giảng viên vượt giới hạn số phiên trong buổi.", field="reviewers", lecturerId=str(lecturer_id), date=day, part=part))
    for (lecturer_id, day), count in day_count.items():
        if h12_day_session_limit is not None and count > h12_day_session_limit:
            blockers.append(_blocker("LECTURER_LOAD_EXCEEDED", "Giảng viên vượt giới hạn số phiên trong ngày.", field="reviewers", lecturerId=str(lecturer_id), date=day))

    eligible_group_ids = {
        int(row[0])
        for row in db.execute(text("SELECT group_id FROM round_groups WHERE round_id = :round_id"), {"round_id": round_row["id"]}).all()
    }
    unscheduled = sorted(eligible_group_ids - set(scheduled_group_ids))
    if unscheduled:
        blockers.append(
            _blocker(
                "UNSCHEDULED_GROUPS",
                "Còn nhóm trong đợt chưa được xếp lịch.",
                groupIds=[_external_group(group_id) for group_id in unscheduled],
            )
        )

    session_blockers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for blocker in blockers:
        if blocker.get("sessionId"):
            session_blockers[str(blocker["sessionId"])].append(blocker)
    incomplete_session_ids = [
        session["id"]
        for session in sessions
        if not session["groups"]
        or session["_room_id"] is None
        or len(session["reviewers"]) != int(round_row["reviewer_count"])
    ]
    return {
        "valid": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            "eligibleGroupCount": len(eligible_group_ids),
            "scheduledGroupCount": len(set(scheduled_group_ids)),
            "unscheduledGroupIds": [_external_group(group_id) for group_id in unscheduled],
            "incompleteSessionIds": incomplete_session_ids,
            "sessionCount": len(sessions),
            "incompleteSessionCount": len(incomplete_session_ids),
            "blockerCount": len(blockers),
            "warningCount": len(warnings),
        },
        "sessionBlockers": session_blockers,
    }


def _validate_against_database(
    db: Session,
    round_row: dict[str, Any],
    sessions: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> None:
    round_id = int(round_row["id"])
    room_types = set(round_row["room_types"] or [])
    accepted = {
        int(row[0])
        for row in db.execute(
            text("SELECT lecturer_id FROM round_invitations WHERE round_id = :round_id AND status = 'ACCEPTED'"),
            {"round_id": round_id},
        ).all()
    }
    availability = {
        (int(row[0]), int(row[1]))
        for row in db.execute(
            text("SELECT lecturer_id, timeslot_id FROM lecturer_availabilities WHERE round_id = :round_id AND state = 'AVAILABLE'"),
            {"round_id": round_id},
        ).all()
    }
    group_slots = {
        (int(row[0]), int(row[1]))
        for row in db.execute(
            text("SELECT group_id, timeslot_id FROM group_slot_preferences WHERE round_id = :round_id AND selected = TRUE"),
            {"round_id": round_id},
        ).all()
    }
    conflicts = {
        (int(row[0]), int(row[1]))
        for row in db.execute(text("SELECT lecturer_id, project_id FROM conflict_declarations")).all()
    }
    group_ids = [
        int(group["_group_id"])
        for session in sessions
        for group in session["groups"]
    ]
    prior = _prior_reviewers_for_groups(db, round_row, group_ids)
    waiver_groups = {
        int(row[0])
        for row in db.execute(
            text("SELECT group_id FROM h11_waivers WHERE round_id = :round_id AND active = TRUE"),
            {"round_id": round_id},
        ).all()
    }
    for session in sessions:
        sid = int(session["_id"])
        timeslot_id = int(session["_timeslot_id"])
        reviewer_ids = [int(reviewer["_lecturer_id"]) for reviewer in session["reviewers"]]
        if session["_room_id"] is not None:
            room = db.execute(
                text("SELECT id, active, room_type::text AS room_type FROM rooms WHERE id = :id"),
                {"id": int(session["_room_id"])},
            ).mappings().one_or_none()
            if room is None:
                blockers.append(_blocker("ROOM_NOT_FOUND", "Không tìm thấy phòng.", session_id=sid, field="roomId"))
            elif not room["active"]:
                blockers.append(_blocker("ROOM_NOT_ACTIVE", "Phòng không hoạt động.", session_id=sid, field="roomId"))
            elif room_types and room["room_type"] not in room_types:
                blockers.append(_blocker("ROOM_TYPE_NOT_ALLOWED", "Loại phòng không được phép cho đợt này.", session_id=sid, field="roomId"))
        for reviewer_id in reviewer_ids:
            if reviewer_id not in accepted:
                blockers.append(_blocker("LECTURER_NOT_ACCEPTED", "Giảng viên chưa chấp nhận lời mời tham gia đợt.", session_id=sid, field="reviewers", lecturerId=str(reviewer_id)))
            if (reviewer_id, timeslot_id) not in availability:
                blockers.append(_blocker("LECTURER_NOT_AVAILABLE", "Giảng viên không rảnh ở khung giờ này.", session_id=sid, field="reviewers", lecturerId=str(reviewer_id)))
        for group in session["groups"]:
            group_id = int(group["_group_id"])
            project_id = group["_project_id"]
            in_round = db.execute(
                text("SELECT 1 FROM round_groups WHERE round_id = :round_id AND group_id = :group_id"),
                {"round_id": round_id, "group_id": group_id},
            ).scalar_one_or_none()
            if in_round is None:
                blockers.append(_blocker("GROUP_NOT_ELIGIBLE", "Nhóm không thuộc đợt này.", session_id=sid, field="groupIds", groupId=_external_group(group_id)))
            if project_id is None:
                blockers.append(_blocker("GROUP_NOT_ELIGIBLE", "Nhóm chưa có đề tài được gán.", session_id=sid, field="groupIds", groupId=_external_group(group_id)))
            if round_row["group_selection_mode"] and group_slots and (group_id, timeslot_id) not in group_slots:
                blockers.append(_blocker("GROUP_SLOT_NOT_SELECTED", "Nhóm chưa chọn khung giờ này.", session_id=sid, field="groupIds", groupId=_external_group(group_id)))
            if project_id is not None:
                for reviewer_id in reviewer_ids:
                    if (reviewer_id, int(project_id)) in conflicts:
                        blockers.append(_blocker("LECTURER_CONFLICT_OF_INTEREST", "Giảng viên đã khai báo xung đột lợi ích với đề tài này.", session_id=sid, field="reviewers", groupId=_external_group(group_id), lecturerId=str(reviewer_id)))
            if (
                str(round_row["round_type"]) in DEFENSE_1_2_TYPES
                and group_id not in waiver_groups
                and not prior.get(group_id, set()).intersection(reviewer_ids)
            ):
                blockers.append(_blocker("PREVIOUS_REVIEWER_REQUIRED", "Bảo vệ 1.2 yêu cầu có ít nhất một giảng viên đã chấm ở vòng trước.", session_id=sid, field="reviewers", groupId=_external_group(group_id)))


def _summary_from_validation(validation: dict[str, Any]) -> dict[str, Any]:
    return validation["summary"]


def _prior_reviewers_for_groups(
    db: Session,
    round_row: dict[str, Any],
    group_ids: list[int],
) -> dict[int, set[int]]:
    if str(round_row["round_type"]) not in DEFENSE_1_2_TYPES or not group_ids:
        return {}
    rows = db.execute(
        text(
            "SELECT COALESCE(sg.group_id, s.group_id) AS group_id, cm.lecturer_id FROM sessions s "
            "LEFT JOIN session_groups sg ON sg.session_id = s.id "
            "JOIN council_members cm ON cm.council_id = s.council_id "
            "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
            "JOIN rounds previous_round ON previous_round.id = sv.round_id "
            "WHERE COALESCE(sg.group_id, s.group_id) = ANY(CAST(:group_ids AS BIGINT[])) "
            "AND previous_round.semester_id = :semester_id "
            "AND previous_round.id <> :round_id "
            "AND previous_round.type::text = ANY(CAST(:source_types AS TEXT[])) "
            "AND sv.status IN ('ACTIVE', 'PUBLISHED')"
        ),
        {
            "group_ids": group_ids,
            "round_id": int(round_row["id"]),
            "semester_id": int(round_row["semester_id"]),
            "source_types": sorted(DEFENSE_1_1_TYPES),
        },
    ).all()
    prior: dict[int, set[int]] = defaultdict(set)
    for group_id, lecturer_id in rows:
        prior[int(group_id)].add(int(lecturer_id))
    return prior


def _decorate_sessions_with_validation(sessions: list[dict[str, Any]], validation: dict[str, Any]) -> list[dict[str, Any]]:
    by_session = validation.get("sessionBlockers", {})
    warning_by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for warning in validation.get("warnings", []):
        if warning.get("sessionId"):
            warning_by_session[str(warning["sessionId"])].append(warning)
    for session in sessions:
        blockers = by_session.get(session["id"], [])
        warnings = warning_by_session.get(session["id"], [])
        session["blockers"] = blockers
        session["warnings"] = warnings
        if session["status"] != "PUBLISHED":
            complete = session["groups"] and session["_room_id"] is not None and blockers == []
            session["status"] = "READY" if complete else "DRAFT"
    return sessions


def _board_payload(db: Session, round_id: int) -> dict[str, Any]:
    round_row = _round_or_404(db, round_id)
    sessions = _load_manual_sessions(db, round_id)
    validation = _validate_manual(db, round_row, sessions)
    sessions = _decorate_sessions_with_validation(sessions, validation)
    source_version_id = db.execute(
        text("SELECT source_schedule_version_id FROM manual_schedule_drafts WHERE round_id = :round_id"),
        {"round_id": round_id},
    ).scalar_one_or_none()
    return {
        "roundId": str(round_id),
        "roundStatus": round_row["round_status"],
        "reviewerCount": int(round_row["reviewer_count"]),
        "maxGroupsPerTimeslot": round_row["max_groups_per_timeslot"],
        "revision": _load_revision(db, round_id),
        "sourceVersionId": int(source_version_id) if source_version_id is not None else None,
        "roles": _role_schema(int(round_row["reviewer_count"])),
        "config": {
            "roomTypes": list(round_row["room_types"] or []),
            "batchSize": None,
            "chairMinLevel": None,
            "secretaryMinLevel": None,
            "maxSameSupervisorRatio": None,
            "eligibleProjectStatuses": ["ACTIVE"],
            "constraints": _constraint_statuses(round_row),
        },
        "summary": _summary_from_validation(validation),
        "sessions": _public_sessions(sessions),
    }


@router.get("/rounds/{roundId}/manual-schedule")
def get_manual_schedule(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    return success_payload(_board_payload(db, round_id))


@router.get("/rounds/{roundId}/manual-schedule/options")
def manual_schedule_options(
    round_id: Annotated[int, Path(alias="roundId")],
    db: Db,
    user: User,
    request: Request,
    session_date: Annotated[Date | None, Query(alias="date")] = None,
    round_timeslot_id: Annotated[str | int | None, Query(alias="roundTimeslotId")] = None,
    session_id: Annotated[str | None, Query(alias="sessionId")] = None,
    role: Annotated[str | None, Query(alias="role")] = None,
    reviewer_ids: Annotated[list[str] | None, Query(alias="reviewerIds")] = None,
    group_ids: Annotated[list[str] | None, Query(alias="groupIds")] = None,
    room_id: Annotated[str | int | None, Query(alias="roomId")] = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 50,
) -> dict[str, Any]:
    _require_manager(user)
    round_row = _round_or_404(db, round_id)
    timeslot_id = _timeslot_id_for(db, round_id, round_timeslot_id, session_date=session_date) if round_timeslot_id is not None else None
    current_session_id = _manual_session_id(session_id) if session_id else None
    selected_reviewers = [
        _parse_positive_id(value, prefix="lec", code="LECTURER_NOT_FOUND")
        for value in _query_list(request, "reviewerIds[]", parsed=reviewer_ids)
    ]
    selected_groups = [
        _parse_positive_id(value, prefix="grp", code="GROUP_NOT_ELIGIBLE")
        for value in _query_list(request, "groupIds[]", parsed=group_ids)
    ]
    selected_room_id = None if room_id is None else _parse_positive_id(room_id, prefix="room", code="ROOM_NOT_FOUND")
    payload = _options_payload(
        db,
        round_row,
        timeslot_id=timeslot_id,
        current_session_id=current_session_id,
        role=(role or "").upper() or None,
        selected_reviewer_ids=selected_reviewers,
        selected_group_ids=selected_groups,
        room_id=selected_room_id,
        search=search,
    )
    start = (page - 1) * page_size
    # Keep pagination metadata simple: each collection is capped independently.
    for key in ("lecturers", "groups", "rooms"):
        payload[key] = payload[key][start : start + page_size]
    return success_payload(payload, meta={"page": page, "pageSize": page_size})


def _options_payload(
    db: Session,
    round_row: dict[str, Any],
    *,
    timeslot_id: int | None,
    current_session_id: int | None,
    role: str | None,
    selected_reviewer_ids: list[int],
    selected_group_ids: list[int],
    room_id: int | None,
    search: str | None,
) -> dict[str, Any]:
    round_id = int(round_row["id"])
    sessions = _load_manual_sessions(db, round_id)
    occupied_groups = {
        int(group["_group_id"])
        for session in sessions
        if current_session_id is None or int(session["_id"]) != current_session_id
        for group in session["groups"]
    }
    occupied_reviewers_in_slot = {
        int(reviewer["_lecturer_id"])
        for session in sessions
        if (current_session_id is None or int(session["_id"]) != current_session_id)
        and (timeslot_id is None or int(session["_timeslot_id"]) == timeslot_id)
        for reviewer in session["reviewers"]
    }
    occupied_rooms_in_slot = {
        int(session["_room_id"])
        for session in sessions
        if session["_room_id"] is not None
        and (current_session_id is None or int(session["_id"]) != current_session_id)
        and (timeslot_id is None or int(session["_timeslot_id"]) == timeslot_id)
    }
    selected_group_projects = {
        int(row["id"]): row["project_id"]
        for row in db.execute(
            text("SELECT id, project_id FROM groups WHERE id = ANY(CAST(:ids AS BIGINT[]))"),
            {"ids": selected_group_ids or [0]},
        ).mappings().all()
    }
    selected_supervisors = {
        int(row[0])
        for row in db.execute(
            text("SELECT lecturer_id FROM project_supervisors WHERE project_id = ANY(CAST(:ids AS BIGINT[]))"),
            {"ids": [pid for pid in selected_group_projects.values() if pid is not None] or [0]},
        ).all()
    }
    prior_reviewers = _prior_reviewers_for_groups(db, round_row, selected_group_ids)
    search_like = f"%{search.strip()}%" if search and search.strip() else "%"
    groups = _group_options(db, round_row, timeslot_id, occupied_groups, selected_reviewer_ids, search_like)
    lecturers = _lecturer_options(
        db,
        round_row,
        timeslot_id,
        occupied_reviewers_in_slot,
        selected_supervisors,
        selected_group_projects,
        selected_reviewer_ids,
        prior_reviewers,
        role,
        search_like,
    )
    rooms = _room_options(db, round_row, timeslot_id, occupied_rooms_in_slot, room_id, search_like)
    return {"lecturers": lecturers, "groups": groups, "rooms": rooms}


def _group_options(
    db: Session,
    round_row: dict[str, Any],
    timeslot_id: int | None,
    occupied_groups: set[int],
    selected_reviewers: list[int],
    search_like: str,
) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT g.id, g.code, g.status::text AS status, g.project_id, "
            "COALESCE(array_agg(DISTINCT ps.lecturer_id::text) FILTER (WHERE ps.lecturer_id IS NOT NULL), ARRAY[]::text[]) AS supervisor_ids, "
            "EXISTS (SELECT 1 FROM group_slot_preferences gp WHERE gp.round_id = :round_id AND gp.group_id = g.id "
            "AND (:timeslot_id IS NULL OR gp.timeslot_id = :timeslot_id) AND gp.selected = TRUE) AS selected_by_group "
            "FROM round_groups rg JOIN groups g ON g.id = rg.group_id "
            "LEFT JOIN project_supervisors ps ON ps.project_id = g.project_id "
            "WHERE rg.round_id = :round_id AND g.code ILIKE :search "
            "GROUP BY g.id, g.code, g.status, g.project_id ORDER BY g.code"
        ),
        {"round_id": round_row["id"], "timeslot_id": timeslot_id, "search": search_like},
    ).mappings().all()
    result = []
    selected_reviewer_set = set(selected_reviewers)
    conflicts = {
        (int(row[0]), int(row[1]))
        for row in db.execute(
            text("SELECT lecturer_id, project_id FROM conflict_declarations WHERE lecturer_id = ANY(CAST(:ids AS BIGINT[]))"),
            {"ids": selected_reviewers or [0]},
        ).all()
    }
    for row in rows:
        blocked: list[str] = []
        if int(row["id"]) in occupied_groups:
            blocked.append("GROUP_DUPLICATED")
        if not _eligible_group_status(str(round_row["round_type"]), str(row["status"])):
            blocked.append("GROUP_NOT_ELIGIBLE")
        if round_row["group_selection_mode"] and timeslot_id is not None and not row["selected_by_group"]:
            blocked.append("GROUP_SLOT_NOT_SELECTED")
        supervisors = {int(value) for value in row["supervisor_ids"] or []}
        if supervisors.intersection(selected_reviewer_set):
            blocked.append("SUPERVISOR_REVIEW_CONFLICT")
        if row["project_id"] is not None and any((reviewer_id, int(row["project_id"])) in conflicts for reviewer_id in selected_reviewer_set):
            blocked.append("LECTURER_CONFLICT_OF_INTEREST")
        result.append(
            {
                "groupId": _external_group(int(row["id"])),
                "groupCode": row["code"],
                "supervisorIds": list(row["supervisor_ids"] or []),
                "selectedByGroup": bool(row["selected_by_group"]),
                "available": not blocked,
                "blockedCodes": blocked,
                "blockedReason": _blocked_reason(blocked),
            }
        )
    return result


def _lecturer_options(
    db: Session,
    round_row: dict[str, Any],
    timeslot_id: int | None,
    occupied_reviewers_in_slot: set[int],
    selected_supervisors: set[int],
    selected_group_projects: dict[int, Any],
    selected_reviewer_ids: list[int],
    prior_reviewers_by_group: dict[int, set[int]],
    role: str | None,
    search_like: str,
) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT l.id, l.lecturer_code, a.display_name, ri.status::text AS invitation_status, "
            "EXISTS (SELECT 1 FROM lecturer_availabilities la WHERE la.round_id = :round_id "
            "AND la.lecturer_id = l.id AND (:timeslot_id IS NULL OR la.timeslot_id = :timeslot_id) "
            "AND la.state = 'AVAILABLE') AS available_in_slot "
            "FROM round_invitations ri JOIN lecturers l ON l.id = ri.lecturer_id "
            "JOIN accounts a ON a.id = l.account_id "
            "WHERE ri.round_id = :round_id AND (l.lecturer_code ILIKE :search OR a.display_name ILIKE :search) "
            "ORDER BY l.lecturer_code, l.id"
        ),
        {"round_id": round_row["id"], "timeslot_id": timeslot_id, "search": search_like},
    ).mappings().all()
    conflicts = {
        (int(row[0]), int(row[1]))
        for row in db.execute(text("SELECT lecturer_id, project_id FROM conflict_declarations")).all()
    }
    role_keys = [item["key"] for item in _role_schema(int(round_row["reviewer_count"]))]
    selected_reviewer_set = set(selected_reviewer_ids)
    h11_unsatisfied_groups = {
        group_id: prior_ids
        for group_id, prior_ids in prior_reviewers_by_group.items()
        if prior_ids and not prior_ids.intersection(selected_reviewer_set)
    }
    result = []
    for row in rows:
        lecturer_id = int(row["id"])
        blocked: list[str] = []
        if row["invitation_status"] != "ACCEPTED":
            blocked.append("LECTURER_NOT_ACCEPTED")
        if timeslot_id is not None and not row["available_in_slot"]:
            blocked.append("LECTURER_NOT_AVAILABLE")
        if lecturer_id in occupied_reviewers_in_slot:
            blocked.append("LECTURER_DOUBLE_BOOKED")
        if lecturer_id in selected_supervisors:
            blocked.append("SUPERVISOR_REVIEW_CONFLICT")
        if any((lecturer_id, int(project_id)) in conflicts for project_id in selected_group_projects.values() if project_id is not None):
            blocked.append("LECTURER_CONFLICT_OF_INTEREST")
        if any(lecturer_id not in prior_ids for prior_ids in h11_unsatisfied_groups.values()):
            blocked.append("PREVIOUS_REVIEWER_REQUIRED")
        eligible_roles = role_keys
        if role is not None and role not in role_keys:
            blocked.append("ROLE_STRUCTURE_INVALID")
            eligible_roles = []
        result.append(
            {
                "lecturerId": str(lecturer_id),
                "lecturerCode": row["lecturer_code"],
                "lecturerName": row["display_name"],
                "eligibleRoles": eligible_roles,
                "available": not blocked,
                "blockedCodes": blocked,
                "blockedReason": _blocked_reason(blocked),
            }
        )
    return result


def _room_options(
    db: Session,
    round_row: dict[str, Any],
    timeslot_id: int | None,
    occupied_rooms_in_slot: set[int],
    room_id: int | None,
    search_like: str,
) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT r.id, r.code, r.name, r.capacity, r.active, r.room_type::text AS room_type "
            "FROM rooms r WHERE (r.code ILIKE :search OR r.name ILIKE :search) ORDER BY r.code"
        ),
        {"search": search_like},
    ).mappings().all()
    allowed_types = set(round_row["room_types"] or [])
    result = []
    for row in rows:
        blocked: list[str] = []
        if not row["active"]:
            blocked.append("ROOM_NOT_ACTIVE")
        if allowed_types and row["room_type"] not in allowed_types:
            blocked.append("ROOM_TYPE_NOT_ALLOWED")
        if timeslot_id is not None and int(row["id"]) in occupied_rooms_in_slot and int(row["id"]) != room_id:
            blocked.append("ROOM_DOUBLE_BOOKED")
        result.append(
            {
                "roomId": int(row["id"]),
                "roomCode": row["code"],
                "roomName": row["name"],
                "type": row["room_type"],
                "capacity": int(row["capacity"]),
                "available": not blocked,
                "blockedCodes": blocked,
                "blockedReason": _blocked_reason(blocked),
            }
        )
    return result


@router.post("/rounds/{roundId}/manual-schedule/sessions", status_code=status.HTTP_201_CREATED)
def create_manual_session(
    round_id: Annotated[int, Path(alias="roundId")],
    payload: ManualSessionPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require_manager(user)
    with db.begin():
        actor_id = _actor_id(db, user)
        ensure_round_semester_writable(db, round_id)
        round_row = _round_or_404(db, round_id, for_update=True)
        _ensure_mutable_round(round_row)
        _ensure_draft_row(db, round_id, actor_id)
        _check_revision(db, round_id, payload.client_revision)
        session_id = _upsert_session(db, round_id, payload, reviewer_count=int(round_row["reviewer_count"]), actor_id=actor_id)
        revision = _bump_revision(db, round_id, actor_id)
        db.execute(
            text(
                "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'MANUAL_SESSION_CREATED', 'manual_schedule_session', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {"actor_id": actor_id, "entity_id": str(session_id), "after_json": _json({"round_id": round_id, "revision": revision})},
        )
    board = _board_payload(db, round_id)
    created = next(item for item in board["sessions"] if item["id"] == _manual_external(session_id))
    return success_payload({"revision": board["revision"], "session": created})


@router.post("/rounds/{roundId}/manual-schedule/sessions/bulk-upsert")
def bulk_upsert_manual_sessions(
    round_id: Annotated[int, Path(alias="roundId")],
    payload: BulkUpsertPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require_manager(user)
    with db.begin():
        actor_id = _actor_id(db, user)
        ensure_round_semester_writable(db, round_id)
        round_row = _round_or_404(db, round_id, for_update=True)
        _ensure_mutable_round(round_row)
        _ensure_draft_row(db, round_id, actor_id)
        _check_revision(db, round_id, payload.client_revision)
        if payload.source_schedule_version_id is not None:
            source_version = db.execute(
                text("SELECT round_id FROM schedule_versions WHERE id = :id"),
                {"id": payload.source_schedule_version_id},
            ).mappings().one_or_none()
            if source_version is None:
                raise HTTPException(
                    status_code=404,
                    detail={"code": "VERSION_NOT_FOUND", "message": "Schedule version source does not exist."},
                )
            if int(source_version["round_id"]) != round_id:
                raise HTTPException(
                    status_code=422,
                    detail={"code": "VERSION_ROUND_MISMATCH", "message": "Schedule version source does not belong to this round."},
                )
            db.execute(
                text(
                    "UPDATE manual_schedule_drafts SET source_schedule_version_id = :version_id, "
                    "updated_by = :actor_id, updated_at = now() WHERE round_id = :round_id"
                ),
                {"version_id": payload.source_schedule_version_id, "actor_id": actor_id, "round_id": round_id},
            )
        deleted_ids = [_manual_session_id(value) for value in payload.deleted_session_ids]
        if deleted_ids:
            db.execute(
                text("DELETE FROM manual_schedule_sessions WHERE round_id = :round_id AND id = ANY(CAST(:ids AS BIGINT[]))"),
                {"round_id": round_id, "ids": deleted_ids},
            )
        upserted: list[int] = []
        for item in payload.sessions:
            sid = _manual_session_id(item.id) if item.id is not None else None
            upserted.append(_upsert_session(db, round_id, item, reviewer_count=int(round_row["reviewer_count"]), actor_id=actor_id, session_id=sid))
        revision = _bump_revision(db, round_id, actor_id)
        db.execute(
            text(
                "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'MANUAL_SESSION_BULK_UPSERTED', 'round', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": actor_id,
                "entity_id": str(round_id),
                "after_json": _json({"upserted": upserted, "deleted": deleted_ids, "revision": revision}),
            },
        )
    return success_payload(_board_payload(db, round_id))


@router.patch("/rounds/{roundId}/manual-schedule/sessions/{sessionId}")
def update_manual_session(
    round_id: Annotated[int, Path(alias="roundId")],
    session_id: Annotated[str, Path(alias="sessionId")],
    payload: ManualSessionPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require_manager(user)
    sid = _manual_session_id(session_id)
    with db.begin():
        actor_id = _actor_id(db, user)
        ensure_round_semester_writable(db, round_id)
        round_row = _round_or_404(db, round_id, for_update=True)
        _ensure_mutable_round(round_row)
        _ensure_draft_row(db, round_id, actor_id)
        _check_revision(db, round_id, payload.client_revision)
        _upsert_session(db, round_id, payload, reviewer_count=int(round_row["reviewer_count"]), actor_id=actor_id, session_id=sid)
        revision = _bump_revision(db, round_id, actor_id)
        db.execute(
            text(
                "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'MANUAL_SESSION_UPDATED', 'manual_schedule_session', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {"actor_id": actor_id, "entity_id": str(sid), "after_json": _json({"round_id": round_id, "revision": revision})},
        )
    board = _board_payload(db, round_id)
    updated = next(item for item in board["sessions"] if item["id"] == _manual_external(sid))
    return success_payload({"revision": board["revision"], "session": updated})


@router.delete("/rounds/{roundId}/manual-schedule/sessions/{sessionId}")
def delete_manual_session(
    round_id: Annotated[int, Path(alias="roundId")],
    session_id: Annotated[str, Path(alias="sessionId")],
    db: Db,
    user: User,
    client_revision: Annotated[int | None, Query(alias="clientRevision")] = None,
) -> dict[str, Any]:
    _require_manager(user)
    sid = _manual_session_id(session_id)
    with db.begin():
        actor_id = _actor_id(db, user)
        ensure_round_semester_writable(db, round_id)
        round_row = _round_or_404(db, round_id, for_update=True)
        _ensure_mutable_round(round_row)
        _ensure_draft_row(db, round_id, actor_id)
        _check_revision(db, round_id, client_revision)
        deleted = db.execute(
            text("DELETE FROM manual_schedule_sessions WHERE round_id = :round_id AND id = :id RETURNING id"),
            {"round_id": round_id, "id": sid},
        ).scalar_one_or_none()
        if deleted is None:
            raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Không tìm thấy phiên lịch thủ công."})
        revision = _bump_revision(db, round_id, actor_id)
        db.execute(
            text(
                "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'MANUAL_SESSION_DELETED', 'manual_schedule_session', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {"actor_id": actor_id, "entity_id": str(sid), "after_json": _json({"round_id": round_id, "revision": revision})},
        )
    return success_payload({"id": _manual_external(sid), "deleted": True, "revision": _load_revision(db, round_id)})


@router.post("/rounds/{roundId}/manual-schedule/validate")
def validate_manual_schedule(
    round_id: Annotated[int, Path(alias="roundId")],
    payload: ValidatePayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require_manager(user)
    round_row = _round_or_404(db, round_id)
    revision = _load_revision(db, round_id)
    if payload.client_revision is not None and payload.client_revision != revision:
        raise HTTPException(
            status_code=409,
            detail={"code": "STALE_MANUAL_SCHEDULE_REVISION", "message": "Bản nháp lịch thủ công đã được thay đổi bởi yêu cầu khác.", "currentRevision": revision},
        )
    sessions = _load_manual_sessions(db, round_id)
    validation = _validate_manual(db, round_row, sessions)
    db.rollback()
    return success_payload({"revision": revision, **{key: value for key, value in validation.items() if key != "sessionBlockers"}})


@router.get("/rounds/{roundId}/manual-schedule/publish-readiness")
def manual_publish_readiness(round_id: Annotated[int, Path(alias="roundId")], db: Db, user: User) -> dict[str, Any]:
    _require_manager(user)
    round_row = _round_or_404(db, round_id)
    revision = _load_revision(db, round_id)
    sessions = _load_manual_sessions(db, round_id)
    validation = _validate_manual(db, round_row, sessions)
    checks = [
        {
            "code": "ROUND_STATUS",
            "passed": round_row["round_status"] in PUBLISHABLE_ROUND_STATUSES,
            "count": 0 if round_row["round_status"] in PUBLISHABLE_ROUND_STATUSES else 1,
        },
        {
            "code": "ALL_GROUPS_SCHEDULED",
            "passed": not validation["summary"]["unscheduledGroupIds"],
            "count": len(validation["summary"]["unscheduledGroupIds"]),
        },
        {
            "code": "ALL_SESSIONS_HAVE_ROOM",
            "passed": all(session["_room_id"] is not None for session in sessions),
            "count": sum(1 for session in sessions if session["_room_id"] is None),
        },
        {
            "code": "ALL_SESSIONS_HAVE_REVIEWERS",
            "passed": all(len(session["reviewers"]) == int(round_row["reviewer_count"]) for session in sessions),
            "count": sum(1 for session in sessions if len(session["reviewers"]) != int(round_row["reviewer_count"])),
        },
        {"code": "HARD_CONSTRAINTS", "passed": not validation["blockers"], "count": len(validation["blockers"])},
        {"code": "WARNINGS_CONFIRMED", "passed": True, "count": len(validation["warnings"])},
    ]
    return success_payload(
        {
            "ready": all(check["passed"] for check in checks),
            "revision": revision,
            "checks": checks,
            "blockers": validation["blockers"],
            "warnings": validation["warnings"],
        }
    )


@router.post("/rounds/{roundId}/manual-schedule/publish")
def publish_manual_schedule(
    round_id: Annotated[int, Path(alias="roundId")],
    payload: PublishPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    _require_manager(user)
    with db.begin():
        actor_id = _actor_id(db, user)
        ensure_round_semester_writable(db, round_id)
        round_row = _round_or_404(db, round_id, for_update=True)
        _ensure_publishable_round(round_row)
        _ensure_draft_row(db, round_id, actor_id)
        revision = _check_revision(db, round_id, payload.client_revision)
        sessions = _load_manual_sessions(db, round_id)
        validation = _validate_manual(db, round_row, sessions)
        if validation["blockers"]:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "PUBLISH_BLOCKED",
                    "message": "Lịch thủ công còn lỗi chặn nên chưa thể công bố.",
                    "blockers": validation["blockers"],
                },
            )
        version_no = int(
            db.execute(
                text("SELECT COALESCE(MAX(version_no), 0) + 1 FROM schedule_versions WHERE round_id = :round_id"),
                {"round_id": round_id},
            ).scalar_one()
        )
        version_id = int(
            db.execute(
                text(
                    "INSERT INTO schedule_versions(round_id, version_no, status, input_snapshot, algorithm_parameters, "
                    "solver_status, created_by, activated_at) VALUES "
                    "(:round_id, :version_no, 'PUBLISHED', CAST(:snapshot AS JSONB), CAST(:parameters AS JSONB), "
                    "'MANUAL', :created_by, now()) RETURNING id"
                ),
                {
                    "round_id": round_id,
                    "version_no": version_no,
                    "snapshot": _json({"manual_schedule_revision": revision, "sessions": _public_sessions(sessions)}),
                    "parameters": _json({"mode": "MANUAL", "reason": payload.reason}),
                    "created_by": actor_id,
                },
            ).scalar_one()
        )
        db.execute(
            text(
                "UPDATE schedule_versions SET status = 'DISCARDED' "
                "WHERE round_id = :round_id AND status IN ('ACTIVE', 'PUBLISHED') AND id <> :version_id"
            ),
            {"round_id": round_id, "version_id": version_id},
        )
        for manual_session in sessions:
            reviewer_members = [
                {
                    "lecturer_id": reviewer["_lecturer_id"],
                    "assignment": "REVIEWER",
                    "is_result_owner": False,
                    "snapshot_name": reviewer["lecturerName"],
                }
                for reviewer in manual_session["reviewers"]
            ]
            council_id = create_council(db, round_id, reviewer_members, created_by=actor_id, reason="Manual schedule publish")
            primary_group = manual_session["groups"][0]
            session_id = int(
                db.execute(
                    text(
                        "INSERT INTO sessions(schedule_version_id, group_id, timeslot_id, room_id, council_id, start_at, end_at, status) "
                        "VALUES (:version_id, :group_id, :timeslot_id, :room_id, :council_id, :start_at, :end_at, 'SCHEDULED') "
                        "RETURNING id"
                    ),
                    {
                        "version_id": version_id,
                        "group_id": primary_group["_group_id"],
                        "timeslot_id": manual_session["_timeslot_id"],
                        "room_id": manual_session["_room_id"],
                        "council_id": council_id,
                        "start_at": manual_session["_start_at"],
                        "end_at": manual_session["_end_at"],
                    },
                ).scalar_one()
            )
            for position, group in enumerate(manual_session["groups"], start=1):
                db.execute(
                    text(
                        "INSERT INTO session_groups(session_id, group_id, position) "
                        "VALUES (:session_id, :group_id, :position)"
                    ),
                    {"session_id": session_id, "group_id": group["_group_id"], "position": position},
                )
                assignment_id = int(
                    db.execute(
                        text(
                            "INSERT INTO schedule_assignments(schedule_version_id, group_id, project_id, timeslot_id, start_at, end_at) "
                            "VALUES (:version_id, :group_id, :project_id, :timeslot_id, :start_at, :end_at) RETURNING id"
                        ),
                        {
                            "version_id": version_id,
                            "group_id": group["_group_id"],
                            "project_id": group["_project_id"],
                            "timeslot_id": manual_session["_timeslot_id"],
                            "start_at": manual_session["_start_at"],
                            "end_at": manual_session["_end_at"],
                        },
                    ).scalar_one()
                )
                for reviewer in manual_session["reviewers"]:
                    db.execute(
                        text(
                            "INSERT INTO schedule_assignment_reviewers(assignment_id, lecturer_id, is_result_owner, snapshot_name) "
                            "VALUES (:assignment_id, :lecturer_id, FALSE, :snapshot_name)"
                        ),
                        {
                            "assignment_id": assignment_id,
                            "lecturer_id": reviewer["_lecturer_id"],
                            "snapshot_name": reviewer["lecturerName"],
                        },
                    )
            db.execute(
                text(
                    "UPDATE manual_schedule_sessions SET status = 'PUBLISHED', published_session_id = :published_session_id, "
                    "updated_by = :actor_id, updated_at = now() WHERE id = :id"
                ),
                {"published_session_id": session_id, "actor_id": actor_id, "id": manual_session["_id"]},
            )
        db.execute(text("UPDATE rounds SET status = 'PUBLISHED' WHERE id = :round_id"), {"round_id": round_id})
        db.execute(
            text(
                "UPDATE manual_schedule_drafts SET published_schedule_version_id = :version_id, updated_by = :actor_id, "
                "updated_at = now() WHERE round_id = :round_id"
            ),
            {"version_id": version_id, "actor_id": actor_id, "round_id": round_id},
        )
        db.execute(
            text(
                "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, reason, after_json) "
                "VALUES (:actor_id, 'MANUAL_SCHEDULE_PUBLISHED', 'schedule_version', :entity_id, :reason, CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": actor_id,
                "entity_id": str(version_id),
                "reason": payload.reason,
                "after_json": _json({"round_id": round_id, "manual_session_count": len(sessions)}),
            },
        )
    return success_payload(
        {
            "roundId": str(round_id),
            "versionId": str(version_id),
            "status": "PUBLISHED",
            "publishedAt": datetime.now(VN_TZ).isoformat(),
            "publishedBy": str(actor_id) if actor_id is not None else None,
            "summary": validation["summary"],
        }
    )
