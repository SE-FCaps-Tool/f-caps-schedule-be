"""Keep the Manager's reschedule decision note with the request."""

from alembic import op


revision = "0008_reschedule_decisions"
down_revision = "0007_result_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE reschedule_requests ADD COLUMN IF NOT EXISTS decision_note TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE reschedule_requests DROP COLUMN IF EXISTS decision_note")
