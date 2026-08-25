from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.services.room_assignment import allocate_room_assignments

SCHEDULE_OPERATIONS_SOURCE = (
    Path(__file__).parents[1] / "app" / "routes" / "schedule_operations.py"
).read_text(encoding="utf-8")


def _session(group_id: int, start: datetime, *, end: datetime | None = None) -> dict[str, object]:
    return {
        "session_id": group_id,
        "group_id": group_id,
        "start_at": start,
        "end_at": end or start + timedelta(minutes=45),
        "day": start.date().isoformat(),
    }


def test_allocator_keeps_a_room_across_adjacent_slots_and_splits_parallel_sessions() -> None:
    start = datetime(2026, 9, 4, 7, 0, tzinfo=UTC)
    sessions = [
        _session(1, start),
        _session(2, start + timedelta(minutes=45)),
        _session(3, start + timedelta(minutes=45)),
    ]
    rooms = [
        {"id": 10, "code": "A"},
        {"id": 20, "code": "B"},
    ]

    result = allocate_room_assignments(sessions, rooms)

    assert [row["room_id"] for row in result] == [10, 10, 20]


def test_allocator_leaves_session_unassigned_when_every_room_overlaps() -> None:
    start = datetime(2026, 9, 4, 7, 0, tzinfo=UTC)
    result = allocate_room_assignments(
        [_session(1, start)],
        [{"id": 10, "code": "A"}],
        [{"session_id": 99, "room_id": 10, "start_at": start, "end_at": start + timedelta(minutes=45)}],
    )

    assert result[0]["room_id"] is None


def test_solver_run_does_not_assign_rooms_before_activation() -> None:
    assert "auto_assign_schedule_rooms" not in SCHEDULE_OPERATIONS_SOURCE
    assert "_assign_rooms_to_solver_result" not in SCHEDULE_OPERATIONS_SOURCE

    activation_start = SCHEDULE_OPERATIONS_SOURCE.index("def activate_schedule_version")
    activation_end = SCHEDULE_OPERATIONS_SOURCE.index("def assign_result_owner", activation_start)
    activation_source = SCHEDULE_OPERATIONS_SOURCE[activation_start:activation_end]
    assert "validate_publish_room_readiness" not in activation_source
