"""Add canonical Defense 1.1 and Defense 1.2 round type values."""

from alembic import op

revision = "0037_round_type_vocab"
down_revision = "0036_round_committees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE round_type ADD VALUE IF NOT EXISTS 'REVIEW_1_1'")
    op.execute("ALTER TYPE round_type ADD VALUE IF NOT EXISTS 'REVIEW_2_1'")
    op.execute("ALTER TYPE round_type ADD VALUE IF NOT EXISTS 'DEFENSE_1_1'")
    op.execute("ALTER TYPE round_type ADD VALUE IF NOT EXISTS 'DEFENSE_1_2'")


def downgrade() -> None:
    # PostgreSQL cannot remove enum labels safely.  The legacy values remain
    # available for compatibility; a later maintenance migration can rebuild
    # the enum once all clients have moved to the canonical labels.
    pass
