"""Shared semester read/query helpers used by management endpoints."""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

SEMESTER_LIFECYCLE_LOCK_KEY = 918273645
_ACADEMIC_YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")


def ensure_semester_writable(db: Session, semester_id: int) -> str:
    """Lock a Semester and reject mutations once it is archived."""
    status = db.execute(
        text("SELECT status FROM semesters WHERE id = :semester_id FOR UPDATE"),
        {"semester_id": semester_id},
    ).scalar_one_or_none()
    if status is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "SEMESTER_NOT_FOUND", "message": "Semester does not exist."},
        )
    if str(status) == "ARCHIVED":
        raise HTTPException(
            status_code=409,
            detail={"code": "SEMESTER_ARCHIVED", "message": "An archived semester is read-only."},
        )
    return str(status)


def ensure_round_semester_writable(db: Session, round_id: int) -> str:
    """Lock a round's parent semester and reject writes for archived rounds."""
    semester_id = db.execute(
        text("SELECT semester_id FROM rounds WHERE id = :round_id FOR UPDATE"),
        {"round_id": round_id},
    ).scalar_one_or_none()
    if semester_id is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "ROUND_NOT_FOUND", "message": "Round does not exist."},
        )
    return ensure_semester_writable(db, int(semester_id))


def academic_year_for_start(start_date: Any) -> str:
    year = int(start_date.year)
    return f"{year:04d}-{year + 1:04d}"


def validate_academic_year(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    match = _ACADEMIC_YEAR_RE.fullmatch(normalized)
    if match is None or int(match.group(2)) != int(match.group(1)) + 1:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "ACADEMIC_YEAR_INVALID",
                "message": "academic_year must use YYYY-YYYY with consecutive years.",
            },
        )
    return normalized


def _actor(row: dict[str, Any], prefix: str) -> dict[str, Any] | None:
    actor_id = row.pop(f"{prefix}_id", None)
    email = row.pop(f"{prefix}_email", None)
    display_name = row.pop(f"{prefix}_display_name", None)
    if actor_id is None and email is None and display_name is None:
        return None
    return {"id": actor_id, "email": email, "display_name": display_name}


def _serialize(row: Any) -> dict[str, Any]:
    data = dict(row)
    data["created_by"] = _actor(data, "created_by")
    data["updated_by"] = _actor(data, "updated_by")
    for key in ("project_count", "group_count", "round_count"):
        data[key] = int(data.get(key) or 0)
    return data


def semester_rows(
    db: Session,
    *,
    semester_id: int | None = None,
    search: str | None = None,
    status: str | None = None,
    academic_year: str | None = None,
) -> list[dict[str, Any]]:
    academic_year = validate_academic_year(academic_year)
    rows = db.execute(
        text(
            """
            SELECT s.id, s.code, s.name, s.note, s.start_date, s.end_date,
                   s.academic_year, s.status, s.created_at, s.updated_at,
                   s.created_by AS created_by_id,
                   created.email AS created_by_email,
                   created.display_name AS created_by_display_name,
                   s.updated_by AS updated_by_id,
                   updated.email AS updated_by_email,
                   updated.display_name AS updated_by_display_name,
                   COALESCE(project_counts.project_count, 0) AS project_count,
                   COALESCE(group_counts.group_count, 0) AS group_count,
                   COALESCE(round_counts.round_count, 0) AS round_count
            FROM semesters s
            LEFT JOIN accounts created ON created.id = s.created_by
            LEFT JOIN accounts updated ON updated.id = s.updated_by
            LEFT JOIN (
                SELECT semester_id, COUNT(*) AS project_count
                FROM projects GROUP BY semester_id
            ) project_counts ON project_counts.semester_id = s.id
            LEFT JOIN (
                SELECT p.semester_id, COUNT(g.id) AS group_count
                FROM projects p LEFT JOIN groups g ON g.project_id = p.id
                GROUP BY p.semester_id
            ) group_counts ON group_counts.semester_id = s.id
            LEFT JOIN (
                SELECT semester_id, COUNT(*) AS round_count
                FROM rounds GROUP BY semester_id
            ) round_counts ON round_counts.semester_id = s.id
            WHERE (CAST(:semester_id AS BIGINT) IS NULL OR s.id = CAST(:semester_id AS BIGINT))
              AND (CAST(:search AS TEXT) IS NULL OR s.code ILIKE :search_pattern OR s.name ILIKE :search_pattern)
              AND (CAST(:status AS TEXT) IS NULL OR s.status::text = CAST(:status AS TEXT))
              AND (CAST(:academic_year AS TEXT) IS NULL OR s.academic_year = CAST(:academic_year AS TEXT))
            ORDER BY s.code, s.id
            """
        ),
        {
            "semester_id": semester_id,
            "search": search.strip() if search and search.strip() else None,
            "search_pattern": f"%{search.strip()}%" if search and search.strip() else None,
            "status": status,
            "academic_year": academic_year,
        },
    ).mappings().all()
    return [_serialize(row) for row in rows]


def semester_or_404(db: Session, semester_id: int) -> dict[str, Any]:
    row = semester_rows(db, semester_id=semester_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "SEMESTER_NOT_FOUND", "message": "Semester does not exist."},
        )
    return row[0]
