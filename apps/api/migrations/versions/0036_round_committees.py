"""Bind Committees to Rounds so a Round resolves its own reviewer pool."""

import sqlalchemy as sa
from alembic import op

revision = "0036_round_committees"
down_revision = "0035_round_type_rename"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "round_committees",
        sa.Column("round_id", sa.BigInteger(), nullable=False),
        sa.Column("committee_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("accounts.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["round_id"],
            ["rounds.id"],
            name="fk_round_committees_round_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["committee_id"],
            ["committees.id"],
            name="fk_round_committees_committee_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("round_id", "committee_id"),
    )
    op.create_index("ix_round_committees_committee_id", "round_committees", ["committee_id"])


def downgrade() -> None:
    op.drop_index("ix_round_committees_committee_id", table_name="round_committees")
    op.drop_table("round_committees")
