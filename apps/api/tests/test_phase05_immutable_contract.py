"""Contract tests for Phase 5 immutable Council storage and change semantics.

These tests intentionally describe the migration and application boundary before the
implementation lands.  They are mostly source contracts because the PostgreSQL
immutability guarantees are covered by the integration tests in this phase.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

API_ROOT = Path(__file__).parents[1]
APP_ROOT = API_ROOT / "app"
MIGRATIONS = API_ROOT / "migrations" / "versions"


def _council_migration() -> Path:
    matches = sorted(MIGRATIONS.glob("*_immutable_councils.py"))
    assert len(matches) == 1, "Phase 5 must ship exactly one immutable Council migration"
    return matches[0]


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_immutable_council_migration_is_rebased_after_session_makeup():
    migration = _council_migration()
    source = _source(migration)

    assert migration.name.startswith("0025_")
    assert 'revision = "0025_immutable_councils"' in source or "revision = '0025_immutable_councils'" in source
    assert 'down_revision = "0024_session_makeup"' in source or "down_revision = '0024_session_makeup'" in source


def test_migration_creates_councils_members_and_non_null_session_reference():
    source = _source(_council_migration()).lower()

    for token in ("councils", "council_members", "council_id", "supersedes_council_id", "sealed_at"):
        assert token in source
    assert "session_reviewers" in source
    assert "insert into councils" in source
    assert "insert into council_members" in source
    assert re.search(r"council_id\s+set\s+(?:not\s+null|not_null)", source)
    assert "drop table session_reviewers" in source


def test_migration_installs_immutability_and_cross_round_attachment_guards():
    source = _source(_council_migration()).lower()

    assert "create function" in source
    assert "create trigger" in source
    assert "sealed_at" in source
    assert "insert" in source and "update" in source and "delete" in source
    assert "round_id" in source
    assert "schedule_version" in source
    assert "restrict" in source or "no action" in source
    assert "unsealed" in source or "immutable" in source


def test_downgrade_reconstructs_legacy_reviewer_rows_and_checks_conflicts():
    source = _source(_council_migration()).lower()

    downgrade = source[source.index("def downgrade") :]
    assert "session_reviewers" in downgrade
    assert "insert into session_reviewers" in downgrade
    assert "time_range" in downgrade
    assert "exclude" in downgrade
    assert "council_members" in downgrade
    # The exclusion constraint is intentionally recreated before the backfill;
    # PostgreSQL aborts the downgrade itself if historical rows conflict.
    assert "constraint" in downgrade or "exclude" in downgrade


def test_council_service_exposes_lock_create_load_conflict_and_validation_helpers():
    from app.services import councils

    for name in (
        "lock_reviewer_ids",
        "create_council",
        "load_council_members",
        "find_reviewer_conflicts",
        "validate_council_change",
    ):
        assert callable(getattr(councils, name, None)), name

    source = inspect.getsource(councils)
    assert "reviewer:" in source
    assert "pg_advisory_xact_lock" in source
    assert "sorted" in source


def test_council_creation_uses_unsealed_build_then_seal_protocol():
    from app.services import councils

    source = inspect.getsource(councils.create_council).lower()
    assert "insert into councils" in source
    assert "insert into council_members" in source
    assert "sealed_at" in source
    assert "update councils" in source
    assert "reason" in source


def test_activation_materializes_sessions_with_councils_and_never_writes_legacy_rows():
    from app.routes import schedule_operations

    source = inspect.getsource(schedule_operations.activate_schedule_version)
    lowered = source.lower()
    assert "schedule_assignment_reviewers" in lowered
    assert "create_council" in lowered or "councils" in lowered
    assert "council_id" in lowered
    assert "lock_reviewer_ids" in lowered or "reviewer" in lowered
    assert "insert into session_reviewers" not in lowered
    assert "update session_reviewers" not in lowered
    assert "delete from session_reviewers" not in lowered


@pytest.mark.parametrize(
    "module_name",
    ["access", "operations", "results", "manager_extensions", "master_data"],
)
def test_all_materialized_consumers_use_council_members(module_name: str):
    path = APP_ROOT / "routes" / f"{module_name}.py"
    if module_name == "access":
        path = APP_ROOT / "services" / "access.py"
    source = _source(path).lower()
    assert "council" in source
    assert "council_members" in source
    assert "session_reviewers" not in source


def test_application_has_no_session_reviewer_references_after_cutover():
    hits: list[str] = []
    for path in APP_ROOT.rglob("*.py"):
        source = _source(path)
        if "session_reviewers" in source:
            hits.append(str(path.relative_to(APP_ROOT)))
    assert hits == [], "application consumers must be Council-backed: " + ", ".join(hits)


def test_session_and_council_response_models_expose_immutable_identity_and_members():
    from app.response_models import ControlledChangeResponse, SessionResponse

    assert "council_id" in SessionResponse.model_fields
    assert "council_id" in ControlledChangeResponse.model_fields or "after_council_id" in ControlledChangeResponse.model_fields

    from app.response_models import CouncilMemberResponse, CouncilResponse

    assert "members" in CouncilResponse.model_fields
    assert {"lecturer_id", "assignment", "is_result_owner"}.issubset(CouncilMemberResponse.model_fields)


def test_controlled_change_response_is_explicitly_branch_aware():
    from app.response_models import ControlledChangeResponse

    fields = ControlledChangeResponse.model_fields
    assert {"change_kind", "schedule_version_id", "replacement_version_id", "session_id", "status"}.issubset(fields)
    assert {"before_council_id", "after_council_id"}.issubset(fields)

    from app.routes import schedule_operations

    source = inspect.getsource(schedule_operations.controlled_change).lower()
    for token in ("reviewer-only", "time/room", "mixed", "council_replaced", "version_replaced", "mixed_replacement"):
        assert token in source
    assert "reason" in source
    assert "audit" in source


def test_result_owner_change_repoints_a_new_council_without_mutating_members():
    from app.routes import schedule_operations

    source = inspect.getsource(schedule_operations.assign_result_owner).lower()
    assert "create_council" in source or "insert into councils" in source
    assert "council_id" in source
    assert "update session_reviewers" not in source
    assert "update council_members" not in source


def test_reviewer_conflict_validation_is_cross_round_and_live_version_scoped():
    from app.services import councils

    source = inspect.getsource(councils.find_reviewer_conflicts).lower()
    assert "active" in source and "published" in source
    assert "round_id" in source
    assert "schedule_versions" in source
    assert "overlap" in source or "start_at" in source


def test_controlled_change_acquires_locks_in_mandatory_resource_order():
    from app.routes import schedule_operations

    source = inspect.getsource(schedule_operations.controlled_change).lower()
    positions = [source.index(token) for token in ("round", "version", "session", "room", "reviewer")]
    assert positions == sorted(positions)
    assert "pg_advisory_xact_lock" in source or "lock_" in source
