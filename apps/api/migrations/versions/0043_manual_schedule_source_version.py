"""Track which generated schedule version was copied into the manual draft."""

import sqlalchemy as sa
from alembic import op


revision = "0043_manual_schedule_source"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "manual_schedule_drafts",
        sa.Column("source_schedule_version_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_manual_schedule_drafts_source_schedule_version",
        "manual_schedule_drafts",
        "schedule_versions",
        ["source_schedule_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_manual_schedule_drafts_source_schedule_version",
        "manual_schedule_drafts",
        type_="foreignkey",
    )
    op.drop_column("manual_schedule_drafts", "source_schedule_version_id")
