"""Add Manager UI configuration and quota data used by the mock flow."""

from alembic import op


revision = "0014_manager_mock_alignment"
down_revision = "0013_semester_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS start_date DATE")
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS end_date DATE")
    op.execute(
        "ALTER TABLE rounds ADD COLUMN IF NOT EXISTS max_groups_per_timeslot INTEGER "
        "CHECK (max_groups_per_timeslot IS NULL OR max_groups_per_timeslot > 0)"
    )
    op.execute(
        "ALTER TABLE rounds ADD COLUMN IF NOT EXISTS max_minutes_per_part INTEGER "
        "CHECK (max_minutes_per_part IS NULL OR max_minutes_per_part > 0)"
    )
    op.execute(
        "ALTER TABLE rounds ADD COLUMN IF NOT EXISTS max_minutes_per_day INTEGER "
        "CHECK (max_minutes_per_day IS NULL OR max_minutes_per_day > 0)"
    )
    op.execute(
        """
        UPDATE rounds r
        SET start_date = COALESCE(r.start_date, d.start_date),
            end_date = COALESCE(r.end_date, d.end_date)
        FROM (
            SELECT round_id, MIN(day_date) AS start_date, MAX(day_date) AS end_date
            FROM round_days GROUP BY round_id
        ) d
        WHERE r.id = d.round_id AND (r.start_date IS NULL OR r.end_date IS NULL)
        """
    )
    op.execute("ALTER TABLE timeslots ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute(
        "ALTER TABLE timeslots ADD COLUMN IF NOT EXISTS part VARCHAR(8) NOT NULL DEFAULT 'AM' "
        "CHECK (part IN ('AM', 'PM'))"
    )
    op.execute(
        """
        UPDATE timeslots
        SET part = CASE
            WHEN EXTRACT(HOUR FROM start_at AT TIME ZONE 'Asia/Ho_Chi_Minh') < 13 THEN 'AM'
            ELSE 'PM'
        END
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS semester_lecturer_quotas (
            semester_id BIGINT NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id) ON DELETE CASCADE,
            quota INTEGER NOT NULL CHECK (quota > 0),
            updated_by BIGINT REFERENCES accounts(id),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (semester_id, lecturer_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS semester_lecturer_quotas")
    op.execute("ALTER TABLE timeslots DROP COLUMN IF EXISTS part")
    op.execute("ALTER TABLE timeslots DROP COLUMN IF EXISTS active")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS max_groups_per_timeslot")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS max_minutes_per_day")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS max_minutes_per_part")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS end_date")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS start_date")
