"""Add project topic type and lecturer seniority metadata."""

from alembic import op


revision = "0044_project_topic_lecturer_seniority"
down_revision = "0043_manual_schedule_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE topic_type AS ENUM "
        "('APPLICATION', 'RESEARCH', 'INTEGRATED', 'REGULAR')"
    )
    op.execute(
        "CREATE TYPE lecturer_seniority_level AS ENUM "
        "('Senior', 'MidLevel', 'Junior', 'Rookie')"
    )
    op.execute(
        "ALTER TABLE projects ADD COLUMN topic_type topic_type "
        "NOT NULL DEFAULT 'REGULAR'"
    )
    op.execute(
        "ALTER TABLE lecturers ADD COLUMN seniority_level "
        "lecturer_seniority_level NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE lecturers DROP COLUMN seniority_level")
    op.execute("ALTER TABLE projects DROP COLUMN topic_type")
    op.execute("DROP TYPE lecturer_seniority_level")
    op.execute("DROP TYPE topic_type")
