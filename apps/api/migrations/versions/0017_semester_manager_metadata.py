"""Add complete Manager semester metadata and audit ownership."""

from alembic import op


revision = "0017_semester_manager_metadata"
down_revision = "0016_semester_active_closed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE semesters ADD COLUMN IF NOT EXISTS note TEXT")
    op.execute("ALTER TABLE semesters ADD COLUMN IF NOT EXISTS academic_year VARCHAR(9)")
    op.execute(
        "ALTER TABLE semesters ADD COLUMN IF NOT EXISTS created_by BIGINT "
        "REFERENCES accounts(id)"
    )
    op.execute(
        "ALTER TABLE semesters ADD COLUMN IF NOT EXISTS updated_by BIGINT "
        "REFERENCES accounts(id)"
    )
    op.execute(
        "ALTER TABLE semesters ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ"
    )
    op.execute("UPDATE semesters SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN updated_at SET DEFAULT now(), "
        "ALTER COLUMN updated_at SET NOT NULL"
    )
    op.execute(
        "UPDATE semesters SET academic_year = CONCAT(EXTRACT(YEAR FROM start_date)::int, '-', "
        "(EXTRACT(YEAR FROM start_date)::int + 1)) "
        "WHERE academic_year IS NULL AND start_date IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_semesters_academic_year "
        "ON semesters (academic_year)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rounds_semester_id "
        "ON rounds (semester_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_rounds_semester_id")
    op.execute("DROP INDEX IF EXISTS ix_semesters_academic_year")
    op.execute("ALTER TABLE semesters DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE semesters DROP COLUMN IF EXISTS updated_by")
    op.execute("ALTER TABLE semesters DROP COLUMN IF EXISTS created_by")
    op.execute("ALTER TABLE semesters DROP COLUMN IF EXISTS academic_year")
    op.execute("ALTER TABLE semesters DROP COLUMN IF EXISTS note")
