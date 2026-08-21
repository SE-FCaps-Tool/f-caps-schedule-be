"""Bind Rounds to an immutable Timeframe revision."""

from alembic import op
import sqlalchemy as sa


revision = "0033_round_timeframe_binding"
down_revision = "0032_manual_timelines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rounds",
        sa.Column(
            "timeframe_id",
            sa.BigInteger(),
            sa.ForeignKey("timeframes.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "rounds",
        sa.Column(
            "timeframe_version_id",
            sa.BigInteger(),
            sa.ForeignKey("timeframe_versions.id"),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_round_timeframe_binding_pair",
        "rounds",
        "(timeframe_id IS NULL AND timeframe_version_id IS NULL) "
        "OR (timeframe_id IS NOT NULL AND timeframe_version_id IS NOT NULL)",
    )
    op.create_index(
        "ix_rounds_timeframe_id",
        "rounds",
        ["timeframe_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_rounds_timeframe_id", table_name="rounds")
    op.drop_constraint("ck_round_timeframe_binding_pair", "rounds", type_="check")
    op.drop_column("rounds", "timeframe_version_id")
    op.drop_column("rounds", "timeframe_id")
