"""Add semester dates and replace the legacy DRAFT status with UPCOMING."""

from alembic import op


revision = "0013_semester_lifecycle"
down_revision = "0012_excel_import_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE semesters ADD COLUMN start_date DATE")
    op.execute("ALTER TABLE semesters ADD COLUMN end_date DATE")
    op.execute(
        """
        UPDATE semesters
        SET start_date = DATE '2026-05-11',
            end_date = DATE '2026-08-23'
        WHERE start_date IS NULL OR end_date IS NULL
        """
    )
    op.execute("ALTER TABLE semesters ALTER COLUMN start_date SET NOT NULL")
    op.execute("ALTER TABLE semesters ALTER COLUMN end_date SET NOT NULL")
    op.execute(
        "ALTER TABLE semesters ADD CONSTRAINT ck_semesters_date_order "
        "CHECK (end_date >= start_date)"
    )

    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text"
    )
    op.execute("UPDATE semesters SET status = 'UPCOMING' WHERE status = 'DRAFT'")
    op.execute("DROP TYPE semester_status")
    op.execute("CREATE TYPE semester_status AS ENUM ('UPCOMING', 'ACTIVE', 'CLOSED')")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE semester_status "
        "USING status::semester_status"
    )
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status SET DEFAULT 'UPCOMING'::semester_status"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_active_semester ON semesters (status) "
        "WHERE status = 'ACTIVE'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text"
    )
    op.execute("UPDATE semesters SET status = 'DRAFT' WHERE status = 'UPCOMING'")
    op.execute("DROP TYPE semester_status")
    op.execute("CREATE TYPE semester_status AS ENUM ('DRAFT', 'ACTIVE', 'CLOSED')")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE semester_status "
        "USING status::semester_status"
    )
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status SET DEFAULT 'DRAFT'::semester_status"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_active_semester ON semesters (status) "
        "WHERE status = 'ACTIVE'"
    )
    op.execute("ALTER TABLE semesters DROP CONSTRAINT ck_semesters_date_order")
    op.execute("ALTER TABLE semesters DROP COLUMN end_date")
    op.execute("ALTER TABLE semesters DROP COLUMN start_date")
