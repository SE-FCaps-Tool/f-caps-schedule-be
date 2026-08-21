"""Persistence for global, reusable Timeframe templates."""

from __future__ import annotations

import json
from datetime import time
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.domain.errors import DomainError
from app.domain.timeframes import (
    GeneratedTimeframeTemplate,
    ManualTimeline,
    TimeframeBreakWindow,
    generate_manual_timeframe_template,
    generate_timeframe_template,
)


def _error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _actor_id(db: Session, user: CurrentUser) -> int | None:
    if user.account_id is not None:
        return user.account_id
    return db.execute(
        text("SELECT MIN(account_id) FROM account_roles WHERE role = CAST(:role AS system_role)"),
        {"role": user.role},
    ).scalar_one_or_none()


def _manual_timeline_payload(value: GeneratedTimeframeTemplate) -> list[dict[str, Any]]:
    return [
        {
            "start_time": block.start_time,
            "end_time": block.end_time,
            "groups_per_slot": len(block.group_slots),
        }
        for block in value.blocks
    ]


def _generated_payload(
    value: GeneratedTimeframeTemplate,
    *,
    manual_timelines: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "start_time": value.start_time,
        "end_time": value.end_time,
        "block_duration_minutes": value.block_duration_minutes,
        "group_duration_minutes": value.group_duration_minutes,
        "break_between_blocks_minutes": value.break_between_blocks_minutes,
        "break_windows": [
            {
                "name": window.name,
                "start_time": window.start_time,
                "end_time": window.end_time,
            }
            for window in value.break_windows
        ],
        "blocks_per_day": value.blocks_per_day,
        "groups_per_block": value.groups_per_block,
        "capacity_per_day": value.capacity_per_day,
        "unused_minutes": value.unused_minutes,
        "break_window_minutes": value.break_window_minutes,
        "applied_block_break_minutes": value.applied_block_break_minutes,
        "total_break_minutes": value.total_break_minutes,
        "blocks": [
            {
                "sequence_number": block.sequence_number,
                "start_time": block.start_time,
                "end_time": block.end_time,
                "duration_minutes": len(block.group_slots) * value.group_duration_minutes,
                "groups_per_block": len(block.group_slots),
                "group_duration_minutes": value.group_duration_minutes,
                "group_slots": [
                    {
                        "sequence_number": slot.sequence_number,
                        "start_time": slot.start_time,
                        "end_time": slot.end_time,
                    }
                    for slot in block.group_slots
                ],
            }
            for block in value.blocks
        ],
    }
    payload["manual_timelines"] = manual_timelines
    return payload


def _generate_template(
    *,
    start_time: time,
    end_time: time,
    block_duration_minutes: int,
    group_duration_minutes: int,
    break_between_blocks_minutes: int,
    break_windows: list[dict[str, Any]],
) -> GeneratedTimeframeTemplate:
    return generate_timeframe_template(
        start_time=start_time,
        end_time=end_time,
        block_duration_minutes=block_duration_minutes,
        group_duration_minutes=group_duration_minutes,
        break_between_blocks_minutes=break_between_blocks_minutes,
        break_windows=tuple(
            TimeframeBreakWindow(
                name=str(window["name"]),
                start_time=window["start_time"],
                end_time=window["end_time"],
            )
            for window in break_windows
        ),
    )


def _generate_manual_template(
    *,
    group_duration_minutes: int,
    timelines: list[dict[str, Any]],
) -> GeneratedTimeframeTemplate:
    return generate_manual_timeframe_template(
        group_duration_minutes=group_duration_minutes,
        timelines=tuple(
            ManualTimeline(
                start_time=timeline["start_time"],
                end_time=timeline["end_time"],
                groups_per_slot=int(timeline["groups_per_slot"]),
            )
            for timeline in timelines
        ),
    )


def _manual_timelines_from_storage(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    return [
        {
            "start_time": (
                item["start_time"]
                if isinstance(item["start_time"], time)
                else time.fromisoformat(item["start_time"])
            ),
            "end_time": (
                item["end_time"]
                if isinstance(item["end_time"], time)
                else time.fromisoformat(item["end_time"])
            ),
            "groups_per_slot": int(item["groups_per_slot"]),
        }
        for item in value
    ]


def load_timeframe_template(
    db: Session,
    *,
    timeframe_id: int,
    version_id: int | None = None,
) -> tuple[int, GeneratedTimeframeTemplate]:
    """Load a Timeframe revision for Round generation.

    A new Round resolves the active revision.  Existing Round updates pass the
    pinned ``version_id`` so a later global Timeframe edit cannot change their
    generated slots.
    """
    version_filter = "tv.status = 'ACTIVE' AND tf.archived_at IS NULL"
    params: dict[str, Any] = {"timeframe_id": timeframe_id}
    if version_id is not None:
        version_filter = "tv.id = :version_id"
        params["version_id"] = version_id
    query = (
        "SELECT tf.id AS timeframe_id, tv.id AS version_id, "
        "tv.start_time, tv.end_time, tv.block_duration_minutes, "
        "tv.group_duration_minutes, tv.break_between_blocks_minutes, "
        "tv.manual_timelines "
        "FROM timeframes tf "
        "JOIN timeframe_versions tv ON tv.timeframe_id = tf.id "
        "WHERE tf.id = :timeframe_id AND "
        f"{version_filter} "
        "ORDER BY tv.version_number DESC LIMIT 1"
    )
    row = db.execute(
        text(query),
        params,
    ).mappings().one_or_none()
    if row is None:
        raise DomainError(
            "TIMEFRAME_NOT_FOUND",
            "The selected Timeframe does not have a usable revision.",
        )

    if row["manual_timelines"]:
        generated = _generate_manual_template(
            group_duration_minutes=int(row["group_duration_minutes"]),
            timelines=_manual_timelines_from_storage(row["manual_timelines"]),
        )
    else:
        breaks = db.execute(
            text(
                "SELECT name, start_time, end_time "
                "FROM timeframe_break_windows "
                "WHERE timeframe_version_id = :version_id "
                "ORDER BY sequence_number"
            ),
            {"version_id": row["version_id"]},
        ).mappings().all()
        generated = _generate_template(
            start_time=row["start_time"],
            end_time=row["end_time"],
            block_duration_minutes=int(row["block_duration_minutes"]),
            group_duration_minutes=int(row["group_duration_minutes"]),
            break_between_blocks_minutes=int(row["break_between_blocks_minutes"] or 0),
            break_windows=[dict(item) for item in breaks],
        )
    return int(row["version_id"]), generated


def preview_timeframe(
    *,
    start_time: time,
    end_time: time,
    block_duration_minutes: int,
    group_duration_minutes: int,
    break_between_blocks_minutes: int,
    break_windows: list[dict[str, Any]],
) -> dict[str, Any]:
    return _generated_payload(
        _generate_template(
            start_time=start_time,
            end_time=end_time,
            block_duration_minutes=block_duration_minutes,
            group_duration_minutes=group_duration_minutes,
            break_between_blocks_minutes=break_between_blocks_minutes,
            break_windows=break_windows,
        )
    )


def preview_manual_timeframe(
    *,
    group_duration_minutes: int,
    timelines: list[dict[str, Any]],
) -> dict[str, Any]:
    generated = _generate_manual_template(
        group_duration_minutes=group_duration_minutes,
        timelines=timelines,
    )
    return _generated_payload(
        generated,
        manual_timelines=_manual_timeline_payload(generated),
    )


def _audit(
    db: Session,
    actor_id: int | None,
    action: str,
    timeframe_id: int,
    reason: str | None,
    after: dict[str, Any],
) -> None:
    db.execute(
        text(
            "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, after_json) "
            "VALUES (:actor_id, :action, 'timeframe', :entity_id, :reason, CAST(:after_json AS JSONB))"
        ),
        {
            "actor_id": actor_id,
            "action": action,
            "entity_id": str(timeframe_id),
            "reason": reason,
            "after_json": json.dumps(after, default=str),
        },
    )


def _insert_version(
    db: Session,
    *,
    timeframe_id: int,
    version_number: int,
    generated: GeneratedTimeframeTemplate,
    actor_id: int | None,
    reason: str | None,
    manual_timelines: list[dict[str, Any]] | None = None,
) -> int:
    version_id = int(
        db.execute(
            text(
                """
                INSERT INTO timeframe_versions (
                  timeframe_id, version_number, status, start_time, end_time,
                  block_duration_minutes, group_duration_minutes,
                  break_between_blocks_minutes, manual_timelines,
                  change_reason, created_by
                ) VALUES (
                  :timeframe_id, :version_number, 'ACTIVE', :start_time, :end_time,
                  :block_duration_minutes, :group_duration_minutes,
                  :break_between_blocks_minutes, CAST(:manual_timelines AS JSONB),
                  :reason, :actor_id
                ) RETURNING id
                """
            ),
            {
                "timeframe_id": timeframe_id,
                "version_number": version_number,
                "start_time": generated.start_time,
                "end_time": generated.end_time,
                "block_duration_minutes": generated.block_duration_minutes,
                "group_duration_minutes": generated.group_duration_minutes,
                "break_between_blocks_minutes": generated.break_between_blocks_minutes or 0,
                "manual_timelines": (
                    json.dumps(manual_timelines, default=str)
                    if manual_timelines is not None
                    else None
                ),
                "reason": reason,
                "actor_id": actor_id,
            },
        ).scalar_one()
    )
    for sequence_number, window in enumerate(generated.break_windows, start=1):
        db.execute(
            text(
                "INSERT INTO timeframe_break_windows ("
                "timeframe_version_id, sequence_number, name, start_time, end_time"
                ") VALUES (:version_id, :sequence_number, :name, :start_time, :end_time)"
            ),
            {
                "version_id": version_id,
                "sequence_number": sequence_number,
                "name": window.name,
                "start_time": window.start_time,
                "end_time": window.end_time,
            },
        )
    return version_id


def create_timeframe(
    db: Session,
    user: CurrentUser,
    *,
    name: str,
    kind: str,
    start_time: time,
    end_time: time,
    block_duration_minutes: int,
    group_duration_minutes: int,
    break_between_blocks_minutes: int,
    break_windows: list[dict[str, Any]],
    reason: str | None,
) -> dict[str, Any]:
    clean_name = name.strip()
    clean_kind = kind.strip().upper()
    if not clean_name or not clean_kind:
        raise _error(422, "TIMEFRAME_IDENTITY_INVALID", "name and type must not be blank.")
    generated = _generate_template(
        start_time=start_time,
        end_time=end_time,
        block_duration_minutes=block_duration_minutes,
        group_duration_minutes=group_duration_minutes,
        break_between_blocks_minutes=break_between_blocks_minutes,
        break_windows=break_windows,
    )
    try:
        with db.begin():
            actor_id = _actor_id(db, user)
            timeframe_id = int(
                db.execute(
                    text(
                        "INSERT INTO timeframes (name, kind, created_by) "
                        "VALUES (:name, :kind, :actor_id) RETURNING id"
                    ),
                    {"name": clean_name, "kind": clean_kind, "actor_id": actor_id},
                ).scalar_one()
            )
            _insert_version(
                db,
                timeframe_id=timeframe_id,
                version_number=1,
                generated=generated,
                actor_id=actor_id,
                reason=reason,
            )
            _audit(db, actor_id, "TIMEFRAME_CREATED", timeframe_id, reason, _generated_payload(generated))
    except IntegrityError as exc:
        raise _error(409, "TIMEFRAME_NAME_DUPLICATE", "An active Timeframe with this name already exists.") from exc
    return get_timeframe(db, timeframe_id)


def create_manual_timeframe(
    db: Session,
    user: CurrentUser,
    *,
    name: str,
    kind: str,
    group_duration_minutes: int,
    timelines: list[dict[str, Any]],
    reason: str | None,
) -> dict[str, Any]:
    clean_name = name.strip()
    clean_kind = kind.strip().upper()
    if not clean_name or not clean_kind:
        raise _error(422, "TIMEFRAME_IDENTITY_INVALID", "name and type must not be blank.")
    generated = _generate_manual_template(
        group_duration_minutes=group_duration_minutes,
        timelines=timelines,
    )
    manual_timelines = _manual_timeline_payload(generated)
    try:
        with db.begin():
            actor_id = _actor_id(db, user)
            timeframe_id = int(
                db.execute(
                    text(
                        "INSERT INTO timeframes (name, kind, created_by) "
                        "VALUES (:name, :kind, :actor_id) RETURNING id"
                    ),
                    {"name": clean_name, "kind": clean_kind, "actor_id": actor_id},
                ).scalar_one()
            )
            _insert_version(
                db,
                timeframe_id=timeframe_id,
                version_number=1,
                generated=generated,
                actor_id=actor_id,
                reason=reason,
                manual_timelines=manual_timelines,
            )
            _audit(
                db,
                actor_id,
                "TIMEFRAME_MANUAL_CREATED",
                timeframe_id,
                reason,
                _generated_payload(generated, manual_timelines=manual_timelines),
            )
    except IntegrityError as exc:
        raise _error(
            409,
            "TIMEFRAME_NAME_DUPLICATE",
            "An active Timeframe with this name already exists.",
        ) from exc
    return get_timeframe(db, timeframe_id)


def update_timeframe(
    db: Session,
    user: CurrentUser,
    *,
    timeframe_id: int,
    name: str,
    kind: str,
    start_time: time,
    end_time: time,
    block_duration_minutes: int,
    group_duration_minutes: int,
    break_between_blocks_minutes: int,
    break_windows: list[dict[str, Any]],
    reason: str | None,
) -> dict[str, Any]:
    clean_name = name.strip()
    clean_kind = kind.strip().upper()
    if not clean_name or not clean_kind:
        raise _error(422, "TIMEFRAME_IDENTITY_INVALID", "name and type must not be blank.")
    generated = _generate_template(
        start_time=start_time,
        end_time=end_time,
        block_duration_minutes=block_duration_minutes,
        group_duration_minutes=group_duration_minutes,
        break_between_blocks_minutes=break_between_blocks_minutes,
        break_windows=break_windows,
    )
    try:
        with db.begin():
            row = db.execute(
                text("SELECT id FROM timeframes WHERE id = :id AND archived_at IS NULL FOR UPDATE"),
                {"id": timeframe_id},
            ).scalar_one_or_none()
            if row is None:
                raise _error(404, "TIMEFRAME_NOT_FOUND", "Active Timeframe does not exist.")
            current = db.execute(
                text(
                    "SELECT id, version_number FROM timeframe_versions "
                    "WHERE timeframe_id = :id AND status = 'ACTIVE' FOR UPDATE"
                ),
                {"id": timeframe_id},
            ).mappings().one()
            actor_id = _actor_id(db, user)
            db.execute(
                text("UPDATE timeframe_versions SET status = 'SUPERSEDED' WHERE id = :id"),
                {"id": current["id"]},
            )
            _insert_version(
                db,
                timeframe_id=timeframe_id,
                version_number=int(current["version_number"]) + 1,
                generated=generated,
                actor_id=actor_id,
                reason=reason,
            )
            db.execute(
                text("UPDATE timeframes SET name = :name, kind = :kind, updated_at = now() WHERE id = :id"),
                {"id": timeframe_id, "name": clean_name, "kind": clean_kind},
            )
            _audit(db, actor_id, "TIMEFRAME_UPDATED", timeframe_id, reason, _generated_payload(generated))
    except IntegrityError as exc:
        raise _error(409, "TIMEFRAME_NAME_DUPLICATE", "An active Timeframe with this name already exists.") from exc
    return get_timeframe(db, timeframe_id)


def update_manual_timeframe(
    db: Session,
    user: CurrentUser,
    *,
    timeframe_id: int,
    name: str,
    kind: str,
    group_duration_minutes: int,
    timelines: list[dict[str, Any]],
    reason: str | None,
) -> dict[str, Any]:
    clean_name = name.strip()
    clean_kind = kind.strip().upper()
    if not clean_name or not clean_kind:
        raise _error(422, "TIMEFRAME_IDENTITY_INVALID", "name and type must not be blank.")
    generated = _generate_manual_template(
        group_duration_minutes=group_duration_minutes,
        timelines=timelines,
    )
    manual_timelines = _manual_timeline_payload(generated)
    try:
        with db.begin():
            row = db.execute(
                text("SELECT id FROM timeframes WHERE id = :id AND archived_at IS NULL FOR UPDATE"),
                {"id": timeframe_id},
            ).scalar_one_or_none()
            if row is None:
                raise _error(404, "TIMEFRAME_NOT_FOUND", "Active Timeframe does not exist.")
            current = db.execute(
                text(
                    "SELECT id, version_number FROM timeframe_versions "
                    "WHERE timeframe_id = :id AND status = 'ACTIVE' FOR UPDATE"
                ),
                {"id": timeframe_id},
            ).mappings().one()
            actor_id = _actor_id(db, user)
            db.execute(
                text("UPDATE timeframe_versions SET status = 'SUPERSEDED' WHERE id = :id"),
                {"id": current["id"]},
            )
            _insert_version(
                db,
                timeframe_id=timeframe_id,
                version_number=int(current["version_number"]) + 1,
                generated=generated,
                actor_id=actor_id,
                reason=reason,
                manual_timelines=manual_timelines,
            )
            db.execute(
                text("UPDATE timeframes SET name = :name, kind = :kind, updated_at = now() WHERE id = :id"),
                {"id": timeframe_id, "name": clean_name, "kind": clean_kind},
            )
            _audit(
                db,
                actor_id,
                "TIMEFRAME_MANUAL_UPDATED",
                timeframe_id,
                reason,
                _generated_payload(generated, manual_timelines=manual_timelines),
            )
    except IntegrityError as exc:
        raise _error(
            409,
            "TIMEFRAME_NAME_DUPLICATE",
            "An active Timeframe with this name already exists.",
        ) from exc
    return get_timeframe(db, timeframe_id)


def archive_timeframe(
    db: Session,
    user: CurrentUser,
    *,
    timeframe_id: int,
    reason: str | None,
) -> dict[str, Any]:
    with db.begin():
        exists = db.execute(
            text("SELECT id FROM timeframes WHERE id = :id AND archived_at IS NULL FOR UPDATE"),
            {"id": timeframe_id},
        ).scalar_one_or_none()
        if exists is None:
            raise _error(404, "TIMEFRAME_NOT_FOUND", "Active Timeframe does not exist.")
        actor_id = _actor_id(db, user)
        db.execute(
            text("UPDATE timeframes SET archived_at = now(), updated_at = now() WHERE id = :id"),
            {"id": timeframe_id},
        )
        _audit(db, actor_id, "TIMEFRAME_ARCHIVED", timeframe_id, reason, {"archived": True})
    return get_timeframe(db, timeframe_id)


def _timeframe_headers(
    db: Session,
    *,
    timeframe_id: int | None = None,
    include_archived: bool = False,
) -> list[Any]:
    return list(
        db.execute(
            text(
                """
                SELECT tf.id, tf.name, tf.kind, tf.archived_at, tf.created_at, tf.updated_at,
                       tv.id AS version_id, tv.version_number, tv.status AS version_status,
                       tv.start_time, tv.end_time, tv.block_duration_minutes,
                       tv.group_duration_minutes, tv.break_between_blocks_minutes,
                       tv.manual_timelines,
                       tv.change_reason, tv.created_at AS version_created_at
                FROM timeframes tf
                JOIN LATERAL (
                  SELECT * FROM timeframe_versions WHERE timeframe_id = tf.id
                  ORDER BY version_number DESC LIMIT 1
                ) tv ON TRUE
                WHERE (
                  CAST(:timeframe_id AS BIGINT) IS NULL
                  OR tf.id = CAST(:timeframe_id AS BIGINT)
                )
                  AND (:include_archived OR tf.archived_at IS NULL)
                ORDER BY tf.archived_at NULLS FIRST, tf.name, tf.id
                """
            ),
            {
                "timeframe_id": timeframe_id,
                "include_archived": include_archived,
            },
        ).mappings()
    )


def _assemble_timeframes(db: Session, headers: list[Any]) -> list[dict[str, Any]]:
    if not headers:
        return []
    timeframe_ids = [int(header["id"]) for header in headers]
    revisions = db.execute(
        text(
            "SELECT id, timeframe_id, version_number, status, start_time, end_time, "
            "block_duration_minutes, group_duration_minutes, break_between_blocks_minutes, "
            "manual_timelines, "
            "change_reason, created_by, created_at FROM timeframe_versions "
            "WHERE timeframe_id = ANY(CAST(:timeframe_ids AS BIGINT[])) "
            "ORDER BY timeframe_id, version_number DESC"
        ),
        {"timeframe_ids": timeframe_ids},
    ).mappings().all()
    break_rows = db.execute(
        text(
            "SELECT tbw.timeframe_version_id, tbw.sequence_number, tbw.name, "
            "tbw.start_time, tbw.end_time "
            "FROM timeframe_break_windows tbw "
            "JOIN timeframe_versions tv ON tv.id = tbw.timeframe_version_id "
            "WHERE tv.timeframe_id = ANY(CAST(:timeframe_ids AS BIGINT[])) "
            "ORDER BY tv.timeframe_id, tbw.timeframe_version_id, tbw.sequence_number"
        ),
        {"timeframe_ids": timeframe_ids},
    ).mappings().all()
    breaks_by_version: dict[int, list[dict[str, Any]]] = {}
    for row in break_rows:
        breaks_by_version.setdefault(int(row["timeframe_version_id"]), []).append(
            {
                "name": row["name"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
            }
        )
    revisions_by_timeframe: dict[int, list[dict[str, Any]]] = {}
    for row in revisions:
        revision = dict(row)
        stored_manual = _manual_timelines_from_storage(row["manual_timelines"])
        revision["manual_timelines"] = stored_manual or None
        if stored_manual:
            revision_generated = _generate_manual_template(
                group_duration_minutes=int(row["group_duration_minutes"]),
                timelines=stored_manual,
            )
            revision["start_time"] = revision_generated.start_time
            revision["end_time"] = revision_generated.end_time
            revision["block_duration_minutes"] = revision_generated.block_duration_minutes
            revision["break_between_blocks_minutes"] = None
            revision["break_windows"] = [
                {
                    "name": item.name,
                    "start_time": item.start_time,
                    "end_time": item.end_time,
                }
                for item in revision_generated.break_windows
            ]
        else:
            revision["break_windows"] = breaks_by_version.get(int(row["id"]), [])
        revisions_by_timeframe.setdefault(int(row["timeframe_id"]), []).append(revision)

    result = []
    for header in headers:
        latest_manual = _manual_timelines_from_storage(header["manual_timelines"])
        if latest_manual:
            generated = _generate_manual_template(
                group_duration_minutes=int(header["group_duration_minutes"]),
                timelines=latest_manual,
            )
        else:
            latest_breaks = breaks_by_version.get(int(header["version_id"]), [])
            generated = _generate_template(
                start_time=header["start_time"],
                end_time=header["end_time"],
                block_duration_minutes=int(header["block_duration_minutes"]),
                group_duration_minutes=int(header["group_duration_minutes"]),
                break_between_blocks_minutes=int(header["break_between_blocks_minutes"]),
                break_windows=latest_breaks,
            )
        result.append(
            {
                "id": int(header["id"]),
                "name": header["name"],
                "type": header["kind"],
                "archived_at": header["archived_at"],
                "created_at": header["created_at"],
                "updated_at": header["updated_at"],
                "version": {
                    "id": int(header["version_id"]),
                    "number": int(header["version_number"]),
                    "status": header["version_status"],
                    "reason": header["change_reason"],
                    "created_at": header["version_created_at"],
                },
                "revisions": revisions_by_timeframe.get(int(header["id"]), []),
                **_generated_payload(
                    generated,
                    manual_timelines=latest_manual or None,
                ),
            }
        )
    return result


def get_timeframe(db: Session, timeframe_id: int) -> dict[str, Any]:
    rows = _assemble_timeframes(
        db,
        _timeframe_headers(db, timeframe_id=timeframe_id, include_archived=True),
    )
    if not rows:
        raise _error(404, "TIMEFRAME_NOT_FOUND", "Timeframe does not exist.")
    return rows[0]


def list_timeframes(db: Session, *, include_archived: bool = False) -> list[dict[str, Any]]:
    return _assemble_timeframes(
        db,
        _timeframe_headers(db, include_archived=include_archived),
    )
