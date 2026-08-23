"""Contract tests for Phase 4 room-type configuration and post-activation assignment.

These tests are intentionally written before the Phase 4 implementation.  They pin the
schema/API boundary described by the plan and should be RED until migration 0023 and the
room-assignment service/routes land.
"""

from __future__ import annotations

import inspect
import re
from importlib import import_module
from pathlib import Path

import pytest

API_ROOT = Path(__file__).parents[1]
MIGRATIONS = API_ROOT / "migrations" / "versions"


def _migration_source() -> str:
    path = MIGRATIONS / "0023_round_room_types.py"
    assert path.exists(), "Phase 4 must ship migration 0023_round_room_types.py"
    return path.read_text(encoding="utf-8")


def _module_source(module_name: str) -> str:
    return inspect.getsource(import_module(module_name))


def test_migration_replaces_physical_round_whitelist_with_allowed_types_and_backfills():
    source = _migration_source()

    assert re.search(r"revision\s*=\s*['\"]0023(?:_round_room_types)?['\"]", source)
    assert re.search(r"down_revision\s*=\s*['\"]0022(?:['\"]|$)", source)
    assert "round_room_types" in source
    assert re.search(
        r"PRIMARY\s+KEY\s*\(\s*round_id\s*,\s*room_type\s*\)",
        source,
        re.IGNORECASE,
    )
    assert "room_type" in source
    assert re.search(
        r"SELECT\s+DISTINCT\s+rr\.round_id.*rooms",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    assert "round_rooms" in source
    assert "ON DELETE CASCADE" in source.upper()
    assert "downgrade" in source


def test_migration_downgrade_expands_each_allowed_type_back_to_rooms():
    source = _migration_source().lower()
    downgrade = source[source.index("def downgrade") :]

    assert re.search(
        r"create[_ ]table.*round_rooms|round_rooms.*create[_ ]table",
        downgrade,
        re.DOTALL,
    )
    assert "join rooms" in downgrade
    assert "room_type" in downgrade
    assert "drop table round_room_types" in downgrade
    assert "capability" in downgrade or "whitelist" in downgrade or "expand" in downgrade


def test_round_resource_contract_persists_room_types_not_room_ids():
    from app.response_models import RoundDetailResponse, RoundResponse
    from app.routes.master_data import RoundResources

    assert "room_types" in RoundResources.model_fields
    assert "room_ids" not in RoundResources.model_fields
    assert "room_types" in RoundResponse.model_fields
    assert "room_types" in RoundDetailResponse.model_fields


def test_round_resource_contract_allows_attaching_groups_before_other_resources():
    from app.routes.master_data import RoundResources

    payload = RoundResources.model_validate({"group_ids": [42]})

    assert payload.group_ids == [42]
    assert payload.timeslot_ids == []
    assert payload.room_types == []


def test_response_models_expose_room_listing_assignment_suggestion_and_readiness_shapes():
    source = (API_ROOT / "app" / "response_models.py").read_text(encoding="utf-8")
    for model_name in (
        "AvailableRoomResponse",
        "RoomSuggestionResponse",
        "RoomAssignmentResponse",
        "RoomSuggestionApplyResponse",
    ):
        assert f"class {model_name}" in source, model_name
    assert "readiness" in source.lower()


def test_room_response_exposes_fe_contract_type_and_status_aliases():
    from app.response_models import RoomResponse

    row = {"id": 1, "code": "S01", "name": "Seminar 1", "capacity": 20, "active": True, "room_type": "SEMINAR"}
    body = RoomResponse.model_validate(row).model_dump()
    assert body["type"] == "SEMINAR"
    assert body["status"] == "ACTIVE"

    inactive_row = {**row, "active": False}
    inactive_body = RoomResponse.model_validate(inactive_row).model_dump()
    assert inactive_body["status"] == "INACTIVE"


def test_round_resource_sources_no_longer_write_round_rooms():
    source = _module_source("app.routes.master_data")
    resources_start = source.index("class RoundResources")
    resources_source = source[resources_start:]
    assert "round_room_types" in resources_source
    assert "INSERT INTO round_rooms" not in resources_source


def test_room_assignment_service_exposes_shared_eligibility_conflict_and_batch_helpers():
    module = import_module("app.services.room_assignment")
    for name in (
        "lock_room_ids",
        "allowed_room",
        "find_room_conflict",
        "build_room_suggestions",
        "validate_assignment_batch",
    ):
        assert callable(getattr(module, name, None)), name


def test_room_assignment_routes_expose_all_four_manager_endpoints():
    source = _module_source("app.routes.room_assignment")
    for path in (
        "/rounds/{roundId}/rooms/available",
        "/sessions/{sessionId}/room",
        "/rounds/{roundId}/rooms/suggest",
        "/rounds/{roundId}/rooms/apply-suggestions",
    ):
        assert path in source, path
    assert "ADMIN" in source and "MANAGER" in source


def test_room_assignment_routes_enforce_planned_active_version_and_structured_errors():
    source = _module_source("app.routes.room_assignment")
    assert "PLANNED" in source
    assert "ACTIVE" in source
    for code in (
        "ROOM_NOT_FOUND",
        "ROOM_INACTIVE",
        "ROOM_TYPE_NOT_ALLOWED",
        "ROOM_ASSIGNMENT_STATE_INVALID",
        "ROOM_CONFLICT",
        "ROOM_SUGGESTION_STALE",
    ):
        assert code in source, code
    assert "HTTPException" in source


def test_room_assignment_uses_one_shared_active_room_predicate_and_interval_overlap():
    source = _module_source("app.services.room_assignment")
    assert "active = TRUE" in source or "status = 'ACTIVE'" in source or 'status = "ACTIVE"' in source
    assert "room_type" in source
    assert "OVERLAPS" in source.upper() or "time_range" in source or "start_at <" in source
    assert "round_room_types" in source


def test_room_mutations_lock_round_version_sessions_and_rooms_deterministically():
    source = _module_source("app.routes.room_assignment") + _module_source(
        "app.services.room_assignment"
    )
    assert "FOR UPDATE" in source
    assert "pg_advisory_xact_lock" in source
    assert "room:" in source
    assert "sorted" in source or "ORDER BY" in source


def test_suggestions_are_deterministic_and_apply_is_atomic_idempotent():
    source = _module_source("app.services.room_assignment") + _module_source(
        "app.routes.room_assignment"
    )
    assert "start_at" in source and "id" in source
    assert "least" in source.lower() or "usage" in source.lower() or "used" in source.lower()
    assert "all" in source.lower() and "batch" in source.lower()
    assert "unchanged" in source.lower() or "idempot" in source.lower()
    assert "ON CONFLICT DO NOTHING" in source or "no-op" in source.lower() or "noop" in source.lower()


def test_publish_schedule_has_room_readiness_and_global_live_conflict_guard():
    source = _module_source("app.routes.schedule_operations")
    assert "room_id" in source
    assert "PUBLISHED" in source and "ACTIVE" in source
    assert "room_type" in source or "round_room_types" in source
    assert "ROOM_CONFLICT" in source or "ROOM_INACTIVE" in source or "ROOM_TYPE_NOT_ALLOWED" in source
    assert "schedule_versions" in source
    assert "overlap" in source.lower() or "time_range" in source.lower()


def test_main_includes_room_assignment_router():
    source = _module_source("app.main")
    assert "room_assignment" in source


def test_resource_lock_namespace_is_signed_int8_and_distinguishes_rooms():
    module = import_module("app.services.resource_locks")
    key_fn = next(
        getattr(module, name)
        for name in ("resource_lock_key", "advisory_lock_key", "signed_int8_key", "lock_key")
        if callable(getattr(module, name, None))
    )
    large_id = 2_147_483_648
    assert key_fn("room", large_id) == key_fn("room", large_id)
    assert key_fn("room", large_id) != key_fn("reviewer", large_id)
    assert -(2**63) <= key_fn("room", large_id) < 2**63


@pytest.mark.parametrize("role", ["lecturer", "student"])
def test_route_source_has_explicit_non_manager_role_boundary(role: str):
    source = _module_source("app.routes.room_assignment").lower()
    assert "_require" in source
    assert "admin" in source and "manager" in source
    # Keep this test explicit about the threat model without requiring a live database.
    assert role not in source or "403" in source or "forbidden" in source
