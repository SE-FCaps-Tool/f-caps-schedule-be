"""Persist whether groups choose their own timeslots for a round."""

from alembic import op


revision = "0009_round_selection_mode"
down_revision = "0008_reschedule_decisions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS group_selection_mode BOOLEAN NOT NULL DEFAULT FALSE")


def downgrade() -> None:
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS group_selection_mode")
