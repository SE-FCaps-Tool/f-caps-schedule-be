"""Store editable manual timeline snapshots on Timeframe revisions."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0032_manual_timelines"
down_revision = "0031_timeframe_breaks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "timeframe_versions",
        sa.Column("manual_timelines", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.alter_column(
        "timeframe_versions",
        "block_duration_minutes",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(
        "UPDATE timeframe_versions SET block_duration_minutes = group_duration_minutes "
        "WHERE block_duration_minutes IS NULL"
    )
    op.alter_column(
        "timeframe_versions",
        "block_duration_minutes",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("timeframe_versions", "manual_timelines")
