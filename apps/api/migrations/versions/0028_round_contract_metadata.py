"""Store target round metadata required by the nested create contract."""

from alembic import op

revision = "0028_round_contract_metadata"
down_revision = "0027_api_contract_status_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS name TEXT")
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS description TEXT")
    op.execute("ALTER TABLE rounds ADD COLUMN IF NOT EXISTS group_preference_deadline TIMESTAMPTZ")


def downgrade() -> None:
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS group_preference_deadline")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS description")
    op.execute("ALTER TABLE rounds DROP COLUMN IF EXISTS name")
