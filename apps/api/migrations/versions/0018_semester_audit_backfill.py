"""Correct audit timestamps for semester rows created before metadata existed."""

from alembic import op


revision = "0018_semester_audit_backfill"
down_revision = "0017_semester_manager_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE semesters SET updated_at = created_at "
        "WHERE updated_by IS NULL AND updated_at > created_at"
    )
    op.execute(
        "UPDATE semesters SET academic_year = CONCAT(EXTRACT(YEAR FROM start_date)::int, '-', "
        "(EXTRACT(YEAR FROM start_date)::int + 1)) "
        "WHERE academic_year IS NULL AND start_date IS NOT NULL"
    )


def downgrade() -> None:
    pass
