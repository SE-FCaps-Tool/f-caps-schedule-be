"""Allow a Group to exist before being assigned to a Project."""

from alembic import op


revision = "0019_nullable_group_project"
down_revision = "0018_semester_audit_backfill"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE groups ALTER COLUMN project_id DROP NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE groups ALTER COLUMN project_id SET NOT NULL")
