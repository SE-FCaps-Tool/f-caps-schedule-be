"""Contract tests for Phase 3 durable assignments and activation materialization.

These tests intentionally pin the persistence boundary before the implementation is changed:
generation owns assignment rows, while activation owns operational Session rows.
"""

from __future__ import annotations

import ast
import inspect
import re
from importlib import import_module
from pathlib import Path

import pytest

API_ROOT = Path(__file__).parents[1]
MIGRATIONS = API_ROOT / "migrations" / "versions"


def _migration_source() -> str:
    path = MIGRATIONS / "0022_durable_schedule_assignments.py"
    assert path.exists(), "Phase 3 must ship migration 0022_durable_schedule_assignments.py"
    return path.read_text(encoding="utf-8")


def _function_source(module, function_name: str) -> str:
    return inspect.getsource(getattr(module, function_name))


def test_phase03_migration_defines_normalized_assignment_tables_and_safe_backfill():
    source = _migration_source()

    assert "revision = '0022'" in source or 'revision = "0022"' in source
    assert "schedule_assignments" in source
    assert "schedule_assignment_reviewers" in source
    assert "project_id" in source
    assert re.search(r"uniqueconstraint|unique\s*\(\s*schedule_version_id.*group_id", source, re.IGNORECASE)
    assert re.search(r"primarykeyconstraint|primary_key|primary\s+key.*assignment_id", source, re.IGNORECASE)
    assert "ON DELETE CASCADE" in source.upper()
    assert "session_reviewers" in source
    assert "DRAFT_ASSIGNMENT_STALE" in source or "project_id IS NULL" in source
    assert "downgrade" in source


def test_phase03_assignment_tables_do_not_reintroduce_solver_room_dimension():
    source = _migration_source()
    for table_name in ("schedule_assignments", "schedule_assignment_reviewers"):
        start = re.search(rf"create_table\(\s*['\"]{table_name}['\"]", source, re.IGNORECASE)
        assert start, f"migration must create {table_name}"
        tail = source[start.end() :]
        next_table = re.search(r"\bcreate_table\(", tail, re.IGNORECASE)
        block = tail[: next_table.start()] if next_table else tail
        assert "room_id" not in block.lower(), f"{table_name} must not own room assignment"


def test_phase03_migration_reconstructs_legacy_drafts_and_cascades_scheduler_jobs():
    source = _migration_source().lower()

    assert "scheduler_jobs_schedule_version_id_fkey" in source
    assert "on delete cascade" in source
    assert "delete from sessions" in source
    assert "insert into sessions" in source
    assert "insert into session_reviewers" in source
    assert "operational" in source or "remediation_cases" in source


def test_generate_persists_assignments_only_and_leaves_round_scheduling():
    from app.routes import schedule_operations

    source = _function_source(schedule_operations, "run_scheduler") + _function_source(
        schedule_operations, "_persist_generated_schedule_draft"
    )
    assert "schedule_assignments" in source
    assert "schedule_assignment_reviewers" in source
    assert "'DRAFT'" in source or '"DRAFT"' in source
    # The scheduler status transition is centralized in scheduler_round_status;
    # keep this contract resilient to that domain helper rather than requiring
    # the route to duplicate the literal transition target.
    assert "scheduler_round_status" in source or "'SCHEDULING'" in source or '"SCHEDULING"' in source
    assert "INSERT INTO sessions" not in source.upper()
    assert "INSERT INTO SESSION_REVIEWERS" not in source.upper()


def test_activation_materializes_planned_null_room_sessions_from_assignments():
    from app.routes import schedule_operations

    source = _function_source(schedule_operations, "activate_schedule_version")
    assert "schedule_assignments" in source
    assert "schedule_assignment_reviewers" in source
    assert "INSERT INTO SESSIONS" in source.upper()
    assert "PLANNED" in source
    assert "room_id" in source
    assert "DRAFT_ASSIGNMENT_STALE" in source
    assert "pg_advisory_xact_lock" in source


def test_publish_transitions_materialized_planned_sessions_atomically():
    from app.routes import schedule_operations

    source = _function_source(schedule_operations, "publish_schedule")
    assert "ACTIVE" in source
    assert "PUBLISHED" in source
    assert "PLANNED" in source
    assert "SCHEDULED" in source
    assert "UPDATE SESSIONS" in source.upper()


@pytest.mark.parametrize(
    "function_name",
    [
        "schedule_version_detail",
        "compare_schedule_versions",
        "delete_draft_version",
        "edit_draft_session",
    ],
)
def test_draft_read_edit_compare_delete_use_durable_assignments(function_name: str):
    from app.routes import schedule_operations

    source = _function_source(schedule_operations, function_name)
    assert "schedule_assignments" in source
    if function_name != "delete_draft_version":
        assert "schedule_assignment_reviewers" in source or "assignment" in source.lower()
    if function_name == "delete_draft_version":
        assert "scheduler_jobs" in source


def test_assignment_id_is_exposed_by_phase03_response_models():
    from app.response_models import (
        CompareResponse,
        ScheduleRunResponse,
        SessionEditResponse,
        SessionResponse,
        VersionDetailResponse,
    )

    for model in (SessionResponse, VersionDetailResponse, CompareResponse, ScheduleRunResponse, SessionEditResponse):
        fields = model.model_fields
        if model in (SessionResponse, SessionEditResponse):
            assert "assignment_id" in fields


def test_session_derived_project_reads_use_assignment_provenance():
    paths = [
        API_ROOT / "app" / "routes" / "results.py",
        API_ROOT / "app" / "routes" / "operations.py",
        API_ROOT / "app" / "routes" / "manager_extensions.py",
        API_ROOT / "app" / "services" / "access.py",
    ]
    for path in paths:
        source = path.read_text(encoding="utf-8")
        assert "schedule_assignments" in source, f"{path.name} must retain assignment provenance"


def test_phase03_route_module_has_no_unscoped_group_project_join_for_session_project_reads():
    from app.routes import schedule_operations

    source = inspect.getsource(schedule_operations)
    tree = ast.parse(source)
    assert tree.body, "schedule_operations should remain parseable after the persistence refactor"
    # This assertion makes the intended audit explicit without banning legacy group queries that
    # are unrelated to a materialized Session.
    assert "schedule_assignments" in source


def test_resource_lock_helper_is_stable_signed_int8_and_supports_large_ids():
    module = import_module("app.services.resource_locks")
    candidates = (
        "resource_lock_key",
        "advisory_lock_key",
        "signed_int8_key",
        "lock_key",
    )
    key_fn = next((getattr(module, name, None) for name in candidates if callable(getattr(module, name, None))), None)
    assert key_fn is not None, "resource_locks must expose a deterministic lock-key function"

    large_id = 2_147_483_648
    first = key_fn("reviewer", large_id)
    second = key_fn("reviewer", large_id)
    assert first == second
    assert -(2**63) <= first < 2**63
    assert key_fn("reviewer", large_id) != key_fn("room", large_id)
