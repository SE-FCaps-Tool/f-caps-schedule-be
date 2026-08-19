"""Track an explicit handoff from lecturer to group registration."""

from alembic import op

revision = "0029_manual_registration_phase"
down_revision = "0028_round_contract_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS lecturer_registration_closed_at TIMESTAMPTZ")


def downgrade() -> None:
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS lecturer_registration_closed_at")
