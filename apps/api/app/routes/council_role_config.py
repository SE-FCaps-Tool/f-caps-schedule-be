"""Council role configuration API — Manager assigns lecturer tiers for Chair/Secretary roles."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.database import get_db
from app.domain.errors import DomainError

Db = Annotated[Session, __import__("fastapi").Depends(get_db)]
User = Annotated[CurrentUser, __import__("fastapi").Depends(__import__("app.auth", fromlist=["get_current_user"]).get_current_user)]

router = APIRouter(prefix="/api/v1", tags=["council-role-config"])


def _require_manager(user: CurrentUser) -> None:
    if user.role not in {"ADMIN", "MANAGER"}:
        raise DomainError("AUTH_FORBIDDEN", "Chỉ Manager/Admin mới có quyền cấu hình phân vai hội đồng.")


# --------------- Request / Response models ---------------

class ChairConfig(BaseModel):
    lecturer_id: int = Field(gt=0)
    quota: int = Field(ge=0, description="Tổng số phiên làm chủ tịch")
    daily_quota: dict[str, int] | None = Field(default=None, description="Quota theo ngày: {'2026-10-04': 8, ...}")


class SecretaryConfig(BaseModel):
    lecturer_id: int = Field(gt=0)
    max_sessions: int = Field(ge=0, default=10, description="Số phiên tối đa làm thư ký")


class LecturerReplacementConfig(BaseModel):
    old_lecturer_id: int = Field(ge=0)
    new_lecturer_id: int = Field(ge=0)


class CouncilRoleConfigPayload(BaseModel):
    chairs: list[ChairConfig] = Field(default_factory=list)
    secretaries: list[SecretaryConfig] = Field(default_factory=list)
    replacements: list[LecturerReplacementConfig] = Field(default_factory=list)


class CouncilRoleConfigResponse(BaseModel):
    round_id: int
    chairs: list[dict[str, Any]] = Field(default_factory=list)
    secretaries: list[dict[str, Any]] = Field(default_factory=list)
    replacements: list[dict[str, Any]] = Field(default_factory=list)
    lecturers: list[dict[str, Any]] = Field(default_factory=list, description="All lecturers in the round for the picker")


# --------------- Endpoints ---------------

@router.get("/rounds/{roundId}/role-config")
def get_role_config(
    round_id: Annotated[int, Path(alias="roundId")],
    db: Db,
    user: User,
) -> dict[str, Any]:
    """Return the current council role configuration for a round."""
    _require_manager(user)
    row = db.execute(
        text("SELECT type, council_config FROM rounds WHERE id = :round_id"),
        {"round_id": round_id},
    ).mappings().one_or_none()
    if row is None:
        raise DomainError("ROUND_NOT_FOUND", "Không tìm thấy đợt đánh giá.")
    config = row["council_config"] or {}
    round_type = row["type"]

    # Calculate base_lecturer_ids
    base_reviewer_ids: set[int] = set()
    if round_type == "DEFENSE_2":
        base_reviewer_ids = set(
            db.execute(
                text(
                    """
                    SELECT DISTINCT cm.lecturer_id
                    FROM council_members cm
                    JOIN councils c ON c.id = cm.council_id
                    JOIN sessions s ON s.council_id = c.id
                    JOIN schedule_versions sv ON sv.id = s.schedule_version_id
                    JOIN rounds r ON r.id = sv.round_id
                    WHERE r.type IN ('DEFENSE_1_1', 'DEFENSE_1')
                      AND sv.status IN ('ACTIVE', 'PUBLISHED')
                    """
                )
            ).scalars()
        )
    if not base_reviewer_ids:
        base_reviewer_ids = set(
            db.execute(
                text(
                    "SELECT lecturer_id FROM round_invitations "
                    "WHERE round_id = :round_id AND status = 'ACCEPTED'"
                ),
                {"round_id": round_id},
            ).scalars()
        )

    # Also return all lecturers invited to this round for the UI picker
    lecturers = db.execute(
        text(
            "SELECT l.id AS lecturer_id, a.display_name, a.email, ri.status "
            "FROM round_invitations ri "
            "JOIN lecturers l ON l.id = ri.lecturer_id "
            "JOIN accounts a ON a.id = l.account_id "
            "WHERE ri.round_id = :round_id "
            "ORDER BY a.display_name"
        ),
        {"round_id": round_id},
    ).mappings().all()

    # Return timeslots grouped by day for the daily quota UI
    days = db.execute(
        text(
            "SELECT rd.day_date, COUNT(ts.id) AS slot_count "
            "FROM round_days rd "
            "JOIN timeslots ts ON ts.round_day_id = rd.id AND ts.active = TRUE "
            "WHERE rd.round_id = :round_id "
            "GROUP BY rd.day_date ORDER BY rd.day_date"
        ),
        {"round_id": round_id},
    ).mappings().all()

    return {
        "data": {
            "roundId": round_id,
            "chairs": config.get("chairs", []),
            "secretaries": config.get("secretaries", []),
            "replacements": config.get("replacements", []),
            "base_lecturer_ids": list(base_reviewer_ids) if base_reviewer_ids else [],
            "lecturers": [dict(row) for row in lecturers],
            "days": [dict(row) for row in days],
        }
    }


@router.put("/rounds/{roundId}/role-config")
def put_role_config(
    round_id: Annotated[int, Path(alias="roundId")],
    payload: CouncilRoleConfigPayload,
    db: Db,
    user: User,
) -> dict[str, Any]:
    """Save the council role configuration for a round."""
    _require_manager(user)

    # Verify round exists
    round_row = db.execute(
        text("SELECT id, status FROM rounds WHERE id = :round_id"),
        {"round_id": round_id},
    ).one_or_none()
    if round_row is None:
        raise DomainError("ROUND_NOT_FOUND", "Không tìm thấy đợt đánh giá.")

    # Validate lecturer IDs exist
    all_lecturer_ids = [
        i for i in (
            [c.lecturer_id for c in payload.chairs]
            + [s.lecturer_id for s in payload.secretaries]
            + [r.old_lecturer_id for r in payload.replacements]
            + [r.new_lecturer_id for r in payload.replacements]
        ) if i > 0
    ]
    if all_lecturer_ids:
        existing = set(
            db.execute(
                text("SELECT id FROM lecturers WHERE id = ANY(:ids)"),
                {"ids": all_lecturer_ids},
            ).scalars()
        )
        missing = set(all_lecturer_ids) - existing
        if missing:
            raise DomainError("LECTURER_NOT_FOUND", f"Không tìm thấy giảng viên: {sorted(missing)}")

    # Build config JSON
    config = {
        "chairs": [c.model_dump() for c in payload.chairs],
        "secretaries": [s.model_dump() for s in payload.secretaries],
        "replacements": [r.model_dump() for r in payload.replacements],
    }

    import json
    db.execute(
        text("UPDATE rounds SET council_config = CAST(:config AS JSONB) WHERE id = :round_id"),
        {"round_id": round_id, "config": json.dumps(config, default=str)},
    )
    db.commit()

    return {
        "data": {
            "roundId": round_id,
            "chairs": config["chairs"],
            "secretaries": config["secretaries"],
            "replacements": config["replacements"],
            "message": "Đã lưu cấu hình phân vai hội đồng.",
        }
    }
