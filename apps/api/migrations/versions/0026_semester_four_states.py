"""Restore the four-state Semester lifecycle required by the FE contract."""

from alembic import op

revision = "0026_semester_four_states"
down_revision = "0025_immutable_councils"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text")
    op.execute("DROP TYPE semester_status")
    op.execute("CREATE TYPE semester_status AS ENUM ('PLANNING', 'ACTIVE', 'CLOSED', 'ARCHIVED')")
    op.execute(
        "ALTER TABLE semesters ALTER COLUMN status TYPE semester_status "
        "USING status::semester_status"
    )
    # Keep legacy create-semester behavior compatible; callers may explicitly
    # request PLANNING, while seeded/legacy rows remain ACTIVE or CLOSED.
    op.execute("ALTER TABLE semesters ALTER COLUMN status SET DEFAULT 'ACTIVE'::semester_status")
    op.execute(
        "CREATE UNIQUE INDEX uq_active_semester ON semesters (status) "
        "WHERE status = 'ACTIVE'"
    )


def downgrade() -> None:
    # PLANNING/ARCHIVED have no representation in the legacy two-state model.
    op.execute("DROP INDEX IF EXISTS uq_active_semester")
    op.execute("ALTER TABLE semesters ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE semesters ALTER COLUMN status TYPE TEXT USING status::text")
    op.execute("UPDATE semesters SET status = 'CLOSED' WHERE status IN ('PLANNING', 'ARCHIVED')")
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
