"""Add global, versioned Timeframe templates."""

import sqlalchemy as sa
from alembic import op

revision = "0030_global_timeframes"
down_revision = "0029_manual_registration_phase"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "timeframes",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("accounts.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_timeframes_active_name "
        "ON timeframes(lower(name)) WHERE archived_at IS NULL"
    )
    op.create_table(
        "timeframe_versions",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("timeframe_id", sa.BigInteger(), sa.ForeignKey("timeframes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("block_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("group_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("change_reason", sa.Text()),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("accounts.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('ACTIVE', 'SUPERSEDED')", name="ck_timeframe_versions_status"),
        sa.CheckConstraint("end_time > start_time", name="ck_timeframe_versions_time_range"),
        sa.CheckConstraint("block_duration_minutes > 0", name="ck_timeframe_versions_block_duration"),
        sa.CheckConstraint("group_duration_minutes > 0", name="ck_timeframe_versions_group_duration"),
        sa.UniqueConstraint("timeframe_id", "version_number", name="uq_timeframe_versions_number"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_timeframe_versions_active "
        "ON timeframe_versions(timeframe_id) WHERE status = 'ACTIVE'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_timeframe_versions_active")
    op.drop_table("timeframe_versions")
    op.execute("DROP INDEX IF EXISTS uq_timeframes_active_name")
    op.drop_table("timeframes")
