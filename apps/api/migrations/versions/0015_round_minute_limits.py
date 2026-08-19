"""Add optional minute-based H12 limits for Manager round configuration."""

from alembic import op


revision = "0015_round_minute_limits"
down_revision = "0014_manager_mock_alignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE rounds ADD COLUMN IF NOT EXISTS max_minutes_per_part INTEGER "
        "CHECK (max_minutes_per_part IS NULL OR max_minutes_per_part > 0)"
    )
    op.execute(
        "ALTER TABLE rounds ADD COLUMN IF NOT EXISTS max_minutes_per_day INTEGER "
        "CHECK (max_minutes_per_day IS NULL OR max_minutes_per_day > 0)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS max_minutes_per_day")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS max_minutes_per_part")
