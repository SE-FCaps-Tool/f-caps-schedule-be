"""Restrict semester lifecycle to ACTIVE and CLOSED."""

from alembic import op


revision = "0016_semester_active_closed"
down_revision = "0015_round_minute_limits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text")

    # Keep one active semester. If one already exists, legacy UPCOMING rows are
    # closed; otherwise promote the newest legacy row to ACTIVE.
    op.execute(
        "UPDATE semesters SET status = 'CLOSED' "
        "WHERE status = 'UPCOMING' AND EXISTS "
        "(SELECT 1 FROM semesters WHERE status = 'ACTIVE')"
    )
    op.execute(
        "UPDATE semesters SET status = 'ACTIVE' "
        "WHERE status = 'UPCOMING' AND id = "
        "(SELECT MAX(id) FROM semesters WHERE status = 'UPCOMING')"
    )
    op.execute("UPDATE semesters SET status = 'CLOSED' WHERE status = 'UPCOMING'")

    op.execute("DROP TYPE semester_status")
    op.execute("CREATE TYPE semester_status AS ENUM ('ACTIVE', 'CLOSED')")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE semester_status "
        "USING status::semester_status"
    )
    op.execute("ALTER TABLE semesters ALTER COLUMN status SET DEFAULT 'ACTIVE'::semester_status")
    op.execute(
        "CREATE UNIQUE INDEX uq_active_semester ON semesters (status) "
        "WHERE status = 'ACTIVE'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text")
    op.execute("UPDATE semesters SET status = 'UPCOMING' WHERE status = 'ACTIVE'")
    op.execute("DROP TYPE semester_status")
    op.execute("CREATE TYPE semester_status AS ENUM ('UPCOMING', 'ACTIVE', 'CLOSED')")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE semester_status "
        "USING status::semester_status"
    )
    op.execute("ALTER TABLE semesters ALTER COLUMN status SET DEFAULT 'UPCOMING'::semester_status")
    op.execute(
        "CREATE UNIQUE INDEX uq_active_semester ON semesters (status) "
        "WHERE status = 'ACTIVE'"
    )
