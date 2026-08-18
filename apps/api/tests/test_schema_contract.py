import os

import psycopg
import pytest

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://scheduler:scheduler@localhost:5432/scheduler"
).replace("postgresql+psycopg://", "postgresql://")


@pytest.mark.integration
def test_domain_schema_contains_no_h13_or_minute_based_h12_fields():
    try:
        connection = psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is required for the Phase 02 schema test: {exc}")

    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'rounds'
            """
        )
        columns = {row[0] for row in cursor.fetchall()}
        assert {"h12_sessions_per_part", "h12_sessions_per_day"}.issubset(columns)
        assert "h13_max_groups_per_timeslot" not in columns
        assert not any("h12" in column and "minute" in column for column in columns)

        cursor.execute(
            """
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'public.sessions'::regclass
              AND contype = 'x'
            """
        )
        assert cursor.fetchone() is not None
