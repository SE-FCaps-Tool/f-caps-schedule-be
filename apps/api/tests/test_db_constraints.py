import os
from uuid import uuid4

import psycopg
import pytest
from psycopg.errors import DatabaseError, ExclusionViolation

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://scheduler:scheduler@localhost:5432/scheduler"
).replace("postgresql+psycopg://", "postgresql://")


@pytest.mark.integration
def test_database_rejects_overlapping_room_sessions_in_one_schedule_version():
    try:
        connection = psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is required for the Phase 02 constraint test: {exc}")

    suffix = uuid4().hex[:12]
    with connection, connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO accounts (email, display_name, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (f"constraint-{suffix}@example.test", "Constraint Tester", "test"),
        )
        account_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO semesters (code, name) VALUES (%s, %s) RETURNING id",
            (f"TEST-{suffix}", "Constraint Test"),
        )
        semester_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO majors (code, name) VALUES (%s, %s) RETURNING id",
            (f"M-{suffix}", "Test Major"),
        )
        major_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO projects (semester_id, major_id, code, title) VALUES (%s, %s, %s, %s) RETURNING id",
            (semester_id, major_id, f"P-{suffix}", "Constraint Project"),
        )
        project_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO groups (project_id, code) VALUES (%s, %s) RETURNING id",
            (project_id, f"G-{suffix}"),
        )
        group_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO projects (semester_id, major_id, code, title) VALUES (%s, %s, %s, %s) RETURNING id",
            (semester_id, major_id, f"P2-{suffix}", "Constraint Project 2"),
        )
        project_two_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO groups (project_id, code) VALUES (%s, %s) RETURNING id",
            (project_two_id, f"G2-{suffix}"),
        )
        group_two_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO rounds (semester_id, type, session_duration_minutes, created_by) "
            "VALUES (%s, 'DEFENSE_1_1', 30, %s) RETURNING id",
            (semester_id, account_id),
        )
        round_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO round_days (round_id, day_date) VALUES (%s, DATE '2030-01-01') RETURNING id",
            (round_id,),
        )
        day_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO timeslots (round_day_id, start_at, end_at) "
            "VALUES (%s, TIMESTAMPTZ '2030-01-01 09:00+07', TIMESTAMPTZ '2030-01-01 09:30+07') RETURNING id",
            (day_id,),
        )
        timeslot_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO rooms (code, name, capacity) VALUES (%s, %s, 10) RETURNING id",
            (f"R-{suffix}", "Constraint Room"),
        )
        room_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO schedule_versions (round_id, version_no, created_by) VALUES (%s, 1, %s) RETURNING id",
            (round_id, account_id),
        )
        version_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at) "
            "VALUES (%s, %s, %s, %s, TIMESTAMPTZ '2030-01-01 09:00+07', TIMESTAMPTZ '2030-01-01 09:30+07')",
            (version_id, group_id, timeslot_id, room_id),
        )

        cursor.execute("SAVEPOINT overlap_check")
        with pytest.raises(ExclusionViolation):
            cursor.execute(
                "INSERT INTO sessions (schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at) "
                "VALUES (%s, %s, %s, %s, TIMESTAMPTZ '2030-01-01 09:15+07', TIMESTAMPTZ '2030-01-01 09:45+07')",
                (version_id, group_two_id, timeslot_id, room_id),
            )
        cursor.execute("ROLLBACK TO SAVEPOINT overlap_check")


@pytest.mark.integration
def test_database_audit_events_are_append_only():
    try:
        connection = psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.fail(f"PostgreSQL is required for the Phase 02 audit test: {exc}")

    with connection, connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO audit_events (action, entity_type, entity_id) "
            "VALUES ('TEST', 'test', %s) RETURNING id",
            (uuid4().hex,),
        )
        event_id = cursor.fetchone()[0]
        cursor.execute("SAVEPOINT audit_update_check")
        with pytest.raises(DatabaseError, match="AUDIT_APPEND_ONLY"):
            cursor.execute("UPDATE audit_events SET reason = 'tampered' WHERE id = %s", (event_id,))
        cursor.execute("ROLLBACK TO SAVEPOINT audit_update_check")

        cursor.execute("SAVEPOINT audit_delete_check")
        with pytest.raises(DatabaseError, match="AUDIT_APPEND_ONLY"):
            cursor.execute("DELETE FROM audit_events WHERE id = %s", (event_id,))
        cursor.execute("ROLLBACK TO SAVEPOINT audit_delete_check")
