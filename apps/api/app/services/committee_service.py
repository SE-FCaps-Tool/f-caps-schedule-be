"""Persistence for the Committee catalog (reusable, mutable groups of Lecturers)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from psycopg.errors import ForeignKeyViolation
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.domain.committees import (
    assign_roles,
    label_role,
    validate_group,
    validate_round_committee_sizes,
)
from app.domain.errors import DomainError

ROUND_COMMITTEE_FK = "fk_round_committees_committee_id"


def _error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _committee_in_use_error() -> HTTPException:
    return _error(409, "COMMITTEE_IN_USE", "Committee is assigned to a Round and cannot be deleted.")


def _is_round_committee_fk_violation(exc: IntegrityError) -> bool:
    """Only a Round assignment may be reported as in-use; other failures must surface."""
    cause = getattr(exc, "orig", None)
    if not isinstance(cause, ForeignKeyViolation):
        return False
    diag = getattr(cause, "diag", None)
    return (getattr(diag, "constraint_name", None) or "") == ROUND_COMMITTEE_FK


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text("SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)"),
        {"role": user.role},
    ).scalar_one_or_none()


def _lecturer_lookup(db: Session, lecturer_ids: set[int]) -> dict[int, dict[str, Any]]:
    if not lecturer_ids:
        return {}
    rows = db.execute(
        text(
            "SELECT l.id, l.lecturer_code, a.display_name "
            "FROM lecturers l JOIN accounts a ON a.id = l.account_id "
            "WHERE l.id = ANY(:ids)"
        ),
        {"ids": sorted(lecturer_ids)},
    ).mappings().all()
    return {int(row["id"]): dict(row) for row in rows}


def _member_payload(lecturer_id: int, role: str, position: int, lookup: dict[int, dict[str, Any]]) -> dict[str, Any]:
    lecturer = lookup.get(lecturer_id)
    return {
        "lecturer_id": lecturer_id,
        "lecturer_code": lecturer["lecturer_code"] if lecturer else None,
        "display_name": lecturer["display_name"] if lecturer else None,
        "role": role,
        "sequence_number": position,
        "role_label": label_role(role, position),
    }


def preview_committees(db: Session, groups: list[dict[str, Any]]) -> dict[str, Any]:
    all_lecturer_ids = {int(member_id) for group in groups for member_id in group["member_ids"]}
    lookup = _lecturer_lookup(db, all_lecturer_ids)
    seen_codes: set[str] = set()
    results: list[dict[str, Any]] = []
    for group in groups:
        raw_code = str(group.get("code") or "")
        member_ids = [int(value) for value in group["member_ids"]]
        errors: list[dict[str, str]] = []
        normalized_code = raw_code.strip().upper()
        try:
            normalized_code = validate_group(raw_code, member_ids)
        except DomainError as exc:
            errors.append({"code": exc.code, "message": str(exc).partition(": ")[2]})
        if normalized_code and normalized_code in seen_codes:
            errors.append({"code": "COMMITTEE_CODE_DUPLICATE", "message": "This code is used by another group in the same batch."})
        seen_codes.add(normalized_code)
        missing = [member_id for member_id in member_ids if member_id not in lookup]
        if missing:
            errors.append({
                "code": "COMMITTEE_LECTURER_NOT_FOUND",
                "message": f"Unknown lecturer id(s): {', '.join(str(value) for value in missing)}.",
            })
        members = [
            _member_payload(lecturer_id, role, position, lookup)
            for lecturer_id, role, position in assign_roles(member_ids)
        ]
        results.append({
            "code": normalized_code or raw_code,
            "member_count": len(member_ids),
            "ok": not errors,
            "members": members,
            "errors": errors,
        })
    return {"groups": results}


def create_committees(db: Session, user: CurrentUser, groups: list[dict[str, Any]]) -> dict[str, Any]:
    all_lecturer_ids = {int(member_id) for group in groups for member_id in group["member_ids"]}
    created = 0
    errors: list[dict[str, Any]] = []
    committees: list[dict[str, Any]] = []
    with db.begin():
        lookup = _lecturer_lookup(db, all_lecturer_ids)
        actor_id = _actor_id(db, user)
        for index, group in enumerate(groups):
            raw_code = str(group.get("code") or "")
            member_ids = [int(value) for value in group["member_ids"]]
            try:
                normalized_code = validate_group(raw_code, member_ids)
            except DomainError as exc:
                errors.append({"index": index, "code": exc.code, "message": str(exc).partition(": ")[2]})
                continue
            missing = [member_id for member_id in member_ids if member_id not in lookup]
            if missing:
                errors.append({
                    "index": index,
                    "code": "COMMITTEE_LECTURER_NOT_FOUND",
                    "message": f"Unknown lecturer id(s): {', '.join(str(value) for value in missing)}.",
                })
                continue
            assignments = assign_roles(member_ids)
            try:
                with db.begin_nested():
                    committee_id = db.execute(
                        text(
                            "INSERT INTO committees (code, member_count, created_by) "
                            "VALUES (:code, :member_count, :created_by) RETURNING id"
                        ),
                        {"code": normalized_code, "member_count": len(member_ids), "created_by": actor_id},
                    ).scalar_one()
                    for lecturer_id, role, position in assignments:
                        db.execute(
                            text(
                                "INSERT INTO committee_members (committee_id, lecturer_id, role, sequence_number) "
                                "VALUES (:committee_id, :lecturer_id, CAST(:role AS committee_role), :position)"
                            ),
                            {"committee_id": committee_id, "lecturer_id": lecturer_id, "role": role, "position": position},
                        )
            except IntegrityError:
                errors.append({
                    "index": index,
                    "code": "COMMITTEE_CODE_DUPLICATE",
                    "message": "This committee code already exists.",
                })
                continue
            created += 1
            committees.append({
                "id": committee_id,
                "code": normalized_code,
                "member_count": len(member_ids),
                "members": [_member_payload(lecturer_id, role, position, lookup) for lecturer_id, role, position in assignments],
            })
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'COMMITTEES_CREATED', 'committee', 'bulk', CAST(:after_json AS JSONB))"
            ),
            {"actor_id": actor_id, "after_json": json.dumps({"created": created, "skipped": len(errors)})},
        )
    return {"created": created, "skipped": len(errors), "errors": errors, "committees": committees}


def list_committees(db: Session, *, lecturer_id: int | None = None) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT c.id, c.code, c.member_count, c.created_by, c.created_at "
            "FROM committees c "
            "WHERE (CAST(:lecturer_id AS BIGINT) IS NULL OR EXISTS ("
            "  SELECT 1 FROM committee_members cm WHERE cm.committee_id = c.id AND cm.lecturer_id = CAST(:lecturer_id AS BIGINT)"
            ")) "
            "ORDER BY c.created_at DESC, c.id DESC"
        ),
        {"lecturer_id": lecturer_id},
    ).mappings().all()
    return [_load_committee_detail(db, int(row["id"]), row) for row in rows]


def list_round_committees(db: Session, round_id: int) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT c.id, c.code, c.member_count, c.created_by, c.created_at "
            "FROM round_committees rc JOIN committees c ON c.id = rc.committee_id "
            "WHERE rc.round_id = :round_id "
            "ORDER BY c.code, c.id"
        ),
        {"round_id": round_id},
    ).mappings().all()
    return [_load_committee_detail(db, int(row["id"]), row) for row in rows]


def unusable_round_committees(db: Session, round_id: int) -> list[dict[str, Any]]:
    """Assigned Committees the scheduler would silently drop, and who is missing.

    Mirrors ``_round_input``'s ``accepted_reviewer_ids or available_reviewer_ids``
    pool exactly: a Committee is only usable when every member is in that pool,
    so a manager needs to see the gap before running the solver rather than
    reading it out of an all-UNSCHEDULED result.
    """

    rows = db.execute(
        text(
            "WITH accepted AS ("
            " SELECT lecturer_id FROM round_invitations "
            " WHERE round_id = :round_id AND status = 'ACCEPTED'"
            "), pool AS ("
            " SELECT lecturer_id FROM accepted"
            " UNION"
            " SELECT lecturer_id FROM lecturer_availabilities"
            " WHERE round_id = :round_id AND state = 'AVAILABLE'"
            "   AND NOT EXISTS (SELECT 1 FROM accepted)"
            ") "
            "SELECT c.id, c.code, "
            " array_agg(cm.lecturer_id ORDER BY cm.lecturer_id) "
            "  FILTER (WHERE cm.lecturer_id NOT IN (SELECT lecturer_id FROM pool)) AS missing "
            "FROM round_committees rc "
            "JOIN committees c ON c.id = rc.committee_id "
            "JOIN committee_members cm ON cm.committee_id = c.id "
            "WHERE rc.round_id = :round_id "
            "GROUP BY c.id, c.code "
            "HAVING COUNT(*) FILTER (WHERE cm.lecturer_id NOT IN (SELECT lecturer_id FROM pool)) > 0 "
            "ORDER BY c.code, c.id"
        ),
        {"round_id": round_id},
    ).mappings().all()
    return [
        {
            "committee_id": int(row["id"]),
            "code": row["code"],
            "missing_lecturer_ids": [int(value) for value in (row["missing"] or [])],
        }
        for row in rows
    ]


def replace_round_committees(
    db: Session,
    round_id: int,
    user: CurrentUser,
    committee_ids: list[int],
) -> list[dict[str, Any]]:
    """Replace the whole Committee set bound to a Round; an empty list clears it."""

    if len(set(committee_ids)) != len(committee_ids):
        raise _error(
            422,
            "ROUND_COMMITTEE_DUPLICATE_ID",
            "The same committee cannot be assigned twice to one round.",
        )
    db.rollback()
    with db.begin():
        actor_id = _actor_id(db, user)
        current_round = db.execute(
            text("SELECT status, reviewer_count FROM rounds WHERE id = :id FOR UPDATE"),
            {"id": round_id},
        ).mappings().one_or_none()
        if current_round is None:
            raise _error(404, "ROUND_NOT_FOUND", "Round does not exist.")
        if str(current_round["status"]) not in {"DRAFT", "OPEN_REGISTRATION"}:
            raise _error(
                409,
                "ROUND_CONFIG_LOCKED",
                "Round configuration can only be edited before scheduling.",
            )
        if committee_ids:
            found = db.execute(
                text("SELECT id, code, member_count FROM committees WHERE id = ANY(:ids)"),
                {"ids": sorted(committee_ids)},
            ).mappings().all()
            missing = sorted(set(committee_ids) - {int(row["id"]) for row in found})
            if missing:
                raise _error(
                    404,
                    "COMMITTEE_NOT_FOUND",
                    f"Unknown committee id(s): {', '.join(str(value) for value in missing)}.",
                )
            try:
                validate_round_committee_sizes(int(current_round["reviewer_count"]), [dict(row) for row in found])
            except DomainError as exc:
                raise _error(422, exc.code, str(exc).partition(": ")[2]) from exc
        db.execute(text("DELETE FROM round_committees WHERE round_id = :round_id"), {"round_id": round_id})
        for committee_id in committee_ids:
            db.execute(
                text(
                    "INSERT INTO round_committees (round_id, committee_id, created_by) "
                    "VALUES (:round_id, :committee_id, :created_by)"
                ),
                {"round_id": round_id, "committee_id": committee_id, "created_by": actor_id},
            )
        db.execute(
            text(
                "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                "VALUES (:actor_id, 'ROUND_COMMITTEES_REPLACED', 'round', :entity_id, CAST(:after_json AS JSONB))"
            ),
            {
                "actor_id": actor_id,
                "entity_id": str(round_id),
                "after_json": json.dumps({"committee_ids": committee_ids}),
            },
        )
    return list_round_committees(db, round_id)


def _load_committee_detail(db: Session, committee_id: int, row: Any) -> dict[str, Any]:
    members = db.execute(
        text(
            "SELECT cm.lecturer_id, cm.role, cm.sequence_number, l.lecturer_code, a.display_name "
            "FROM committee_members cm "
            "JOIN lecturers l ON l.id = cm.lecturer_id "
            "JOIN accounts a ON a.id = l.account_id "
            "WHERE cm.committee_id = :committee_id "
            "ORDER BY cm.sequence_number"
        ),
        {"committee_id": committee_id},
    ).mappings().all()
    return {
        "id": row["id"],
        "code": row["code"],
        "member_count": row["member_count"],
        "created_by": row["created_by"],
        "created_at": row["created_at"],
        "members": [
            {
                "lecturer_id": member["lecturer_id"],
                "lecturer_code": member["lecturer_code"],
                "display_name": member["display_name"],
                "role": member["role"],
                "sequence_number": member["sequence_number"],
                "role_label": label_role(member["role"], member["sequence_number"]),
            }
            for member in members
        ],
    }


def get_committee(db: Session, committee_id: int) -> dict[str, Any]:
    row = db.execute(
        text("SELECT id, code, member_count, created_by, created_at FROM committees WHERE id = :id"),
        {"id": committee_id},
    ).mappings().one_or_none()
    if row is None:
        raise _error(404, "COMMITTEE_NOT_FOUND", "Committee not found.")
    return _load_committee_detail(db, committee_id, row)


def _assigned_committee_ids(db: Session, committee_ids: list[int]) -> set[int]:
    if not committee_ids:
        return set()
    rows = db.execute(
        text("SELECT DISTINCT committee_id FROM round_committees WHERE committee_id = ANY(:ids)"),
        {"ids": sorted(committee_ids)},
    ).scalars().all()
    return {int(value) for value in rows}


def delete_committee(db: Session, committee_id: int) -> None:
    with db.begin():
        if _assigned_committee_ids(db, [committee_id]):
            raise _committee_in_use_error()
        try:
            deleted = db.execute(
                text("DELETE FROM committees WHERE id = :id RETURNING id"),
                {"id": committee_id},
            ).scalar_one_or_none()
        except IntegrityError as exc:
            if not _is_round_committee_fk_violation(exc):
                raise
            raise _committee_in_use_error() from exc
        if deleted is None:
            raise _error(404, "COMMITTEE_NOT_FOUND", "Committee not found.")


def bulk_delete_committees(db: Session, committee_ids: list[int]) -> dict[str, Any]:
    with db.begin():
        in_use_ids = _assigned_committee_ids(db, committee_ids)
        deleted_ids: list[int] = []
        for committee_id in committee_ids:
            if committee_id in in_use_ids:
                continue
            try:
                with db.begin_nested():
                    deleted = db.execute(
                        text("DELETE FROM committees WHERE id = :id RETURNING id"),
                        {"id": committee_id},
                    ).scalar_one_or_none()
            except IntegrityError as exc:
                if not _is_round_committee_fk_violation(exc):
                    raise
                in_use_ids.add(committee_id)
                continue
            if deleted is not None:
                deleted_ids.append(int(deleted))
    return {
        "deleted": len(deleted_ids),
        "deleted_ids": deleted_ids,
        "in_use_ids": sorted(in_use_ids),
    }
