import os
from pathlib import Path

import psycopg
import pytest

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://scheduler:scheduler@localhost:5432/scheduler"
).replace("postgresql+psycopg://", "postgresql://")


def test_phase01_migration_contains_legacy_lifecycle_preflight_and_downgrade_mapping():
    migration_path = Path(__file__).parents[1] / "migrations" / "versions" / "0021_schedule_lifecycle_vocab.py"
    assert migration_path.exists(), "Phase 01 must ship the lifecycle enum migration."
    source = migration_path.read_text(encoding="utf-8")

    assert "activated_at IS NULL" in source
    assert "SUPERSEDED" in source and "DISCARDED" in source
    assert "GROUP_ABSENT" in source
    assert "PLANNED" in source
    assert "downgrade" in source


@pytest.mark.integration
def test_phase01_postgres_status_enums_and_defaults_match_contract():
    try:
        connection = psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is required for the Phase 01 schema test: {exc}")

    with connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT typname, enumlabel FROM pg_type JOIN pg_enum ON pg_enum.enumtypid = pg_type.oid "
            "WHERE typname IN ('schedule_version_status', 'session_status') ORDER BY typname, enumsortorder"
        )
        labels: dict[str, list[str]] = {}
        for type_name, label in cursor.fetchall():
            labels.setdefault(type_name, []).append(label)

        assert labels["schedule_version_status"] == [
            "DRAFT",
            "ACTIVE",
            "PUBLISHED",
            "DISCARDED",
        ]
        assert labels["session_status"] == [
            "PLANNED",
            "SCHEDULED",
            "COMPLETED",
            "POSTPONED",
            "GROUP_ABSENT",
            "CANCELLED",
        ]

        cursor.execute(
            "SELECT table_name, column_name, column_default FROM information_schema.columns "
            "WHERE table_schema = 'public' AND ((table_name = 'schedule_versions' AND column_name = 'status') "
            "OR (table_name = 'sessions' AND column_name = 'status')) ORDER BY table_name"
        )
        defaults = {(table, column): default for table, column, default in cursor.fetchall()}
        assert "'DRAFT'::schedule_version_status" in defaults[("schedule_versions", "status")]
        assert "'PLANNED'::session_status" in defaults[("sessions", "status")]
