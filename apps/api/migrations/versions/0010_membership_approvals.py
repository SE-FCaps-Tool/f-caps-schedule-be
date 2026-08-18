"""Record who requested and approved a membership dropout."""

from alembic import op


revision = "0010_membership_approvals"
down_revision = "0009_round_selection_mode"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE group_memberships
            ADD COLUMN IF NOT EXISTS drop_requested_by BIGINT REFERENCES accounts(id),
            ADD COLUMN IF NOT EXISTS drop_approved_by BIGINT REFERENCES accounts(id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE group_memberships
            DROP COLUMN IF EXISTS drop_requested_by,
            DROP COLUMN IF EXISTS drop_approved_by;
        """
    )
