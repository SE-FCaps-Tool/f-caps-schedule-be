"""Add flexible break configuration to Timeframe revisions."""

import sqlalchemy as sa
from alembic import op

revision = "0031_timeframe_breaks"
down_revision = "0030_global_timeframes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "timeframe_versions",
        sa.Column(
            "break_between_blocks_minutes",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "ck_timeframe_versions_block_break",
        "timeframe_versions",
        "break_between_blocks_minutes >= 0",
    )
    op.create_table(
        "timeframe_break_windows",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "timeframe_version_id",
            sa.BigInteger(),
            sa.ForeignKey("timeframe_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.CheckConstraint(
            "sequence_number > 0",
            name="ck_timeframe_break_windows_sequence",
        ),
        sa.CheckConstraint(
            "end_time > start_time",
            name="ck_timeframe_break_windows_range",
        ),
        sa.UniqueConstraint(
            "timeframe_version_id",
            "sequence_number",
            name="uq_timeframe_break_windows_sequence",
        ),
    )
    op.create_index(
        "ix_timeframe_break_windows_version",
        "timeframe_break_windows",
        ["timeframe_version_id", "start_time"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_timeframe_break_windows_version",
        table_name="timeframe_break_windows",
    )
    op.drop_table("timeframe_break_windows")
    op.drop_constraint(
        "ck_timeframe_versions_block_break",
        "timeframe_versions",
        type_="check",
    )
    op.drop_column("timeframe_versions", "break_between_blocks_minutes")
