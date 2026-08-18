"""Persist the group-state transition that belongs to each result write."""

from alembic import op


revision = "0007_result_history"
down_revision = "0006_auth_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE session_results
            ADD COLUMN IF NOT EXISTS before_group_status group_status,
            ADD COLUMN IF NOT EXISTS after_group_status group_status;
        CREATE INDEX IF NOT EXISTS session_results_entered_at_idx
            ON session_results (entered_at);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS session_results_entered_at_idx;
        ALTER TABLE session_results
            DROP COLUMN IF EXISTS before_group_status,
            DROP COLUMN IF EXISTS after_group_status;
        """
    )
