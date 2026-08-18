"""Add the explicit completion outcome used by Defense 1.2."""

from alembic import op


revision = "0005_result_completion"
down_revision = "0004_schedule_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE result_outcome ADD VALUE 'COMPLETED'")


def downgrade() -> None:
    # PostgreSQL does not safely remove enum values in a transactional migration.
    pass
