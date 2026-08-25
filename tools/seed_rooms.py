"""Seed the local room catalog and allow those room types for a round.

This is intentionally idempotent.  The scheduler may reuse a room across
different non-overlapping timeslots, but never for overlapping sessions.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DEFAULT_DATABASE_URL = "postgresql+psycopg://scheduler:scheduler@localhost:5432/scheduler"


@dataclass(frozen=True)
class RoomSeed:
    code: str
    name: str
    room_type: str
    capacity: int


ROOMS = (
    RoomSeed("NVH G.01", "NVH G.01", "NORMAL", 40),
    RoomSeed("NVH G.02", "NVH G.02", "NORMAL", 18),
    RoomSeed("NVH G.04", "NVH G.04", "NORMAL", 8),
    RoomSeed("NVH G.05", "NVH G.05", "NORMAL", 4),
    RoomSeed("NVH 420", "NVH 420", "NORMAL", 999),
    RoomSeed("NVH 421", "NVH 421", "NORMAL", 2),
    RoomSeed("NVH.301", "NVH.301", "NORMAL", 13),
    RoomSeed("NVH.306", "NVH.306", "NORMAL", 5),
    RoomSeed("NVH.414", "NVH.414", "NORMAL", 14),
    RoomSeed("NVH.415", "NVH.415", "NORMAL", 12),
    RoomSeed("LB21 (Thư viện Campus)", "LB21 (Thư viện Campus)", "SEMINAR", 8),
)


def seed_rooms(session: Session, round_id: int | None) -> dict[str, Any]:
    upserted = 0
    for room in ROOMS:
        session.execute(
            text(
                "INSERT INTO rooms (code, name, capacity, room_type, active) "
                "VALUES (:code, :name, :capacity, CAST(:room_type AS room_type), TRUE) "
                "ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, "
                "capacity = EXCLUDED.capacity, room_type = EXCLUDED.room_type, active = TRUE"
            ),
            {
                "code": room.code,
                "name": room.name,
                "capacity": room.capacity,
                "room_type": room.room_type,
            },
        )
        upserted += 1

    bound_types: list[str] = []
    if round_id is not None:
        for room_type in sorted({room.room_type for room in ROOMS}):
            inserted = session.execute(
                text(
                    "INSERT INTO round_room_types (round_id, room_type) "
                    "VALUES (:round_id, CAST(:room_type AS room_type)) "
                    "ON CONFLICT DO NOTHING RETURNING room_type"
                ),
                {"round_id": round_id, "room_type": room_type},
            ).scalar_one_or_none()
            if inserted is not None:
                bound_types.append(str(inserted))

    session.execute(
        text(
            "INSERT INTO audit_events "
            "(actor_id, action, entity_type, entity_id, reason, after_json) "
            "VALUES (NULL, 'ROOM_CATALOG_SEEDED', 'room_catalog', 'rooms', "
            ":reason, CAST(:after_json AS JSONB))"
        ),
        {
            "reason": "Seed local room catalog; rooms are reused only across non-overlapping timeslots",
            "after_json": json.dumps(
                {
                    "rooms": len(ROOMS),
                    "round_id": round_id,
                    "bound_room_types": sorted(
                        {room.room_type for room in ROOMS}
                    ),
                }
            ),
        },
    )
    return {
        "rooms_upserted": upserted,
        "round_id": round_id,
        "new_round_room_type_bindings": bound_types,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
    )
    parser.add_argument(
        "--round-id",
        type=int,
        help="Also allow NORMAL and SEMINAR for this round.",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    engine = create_engine(args.database_url, pool_pre_ping=True)
    with Session(engine) as session:
        round_id = args.round_id
        if round_id is not None:
            exists = session.execute(
                text("SELECT 1 FROM rounds WHERE id = :round_id"),
                {"round_id": round_id},
            ).scalar_one_or_none()
            if exists is None:
                raise SystemExit(f"Round does not exist: {round_id}")

        result: dict[str, Any] = {
            "mode": "apply" if args.apply else "dry-run",
            "rooms": [room.__dict__ for room in ROOMS],
            "round_id": round_id,
        }
        if args.apply:
            session.rollback()
            with session.begin():
                result.update(seed_rooms(session, round_id))
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
