"""Add Committee catalog (reusable, mutable groups of Lecturers)."""

import sqlalchemy as sa
from alembic import op

revision = "0034_committees"
down_revision = "0033_round_timeframe_binding"
branch_labels = None
depends_on = None

committee_role = sa.Enum("REVIEWER", "CHAIR", "SECRETARY", "MEMBER", name="committee_role")


def upgrade() -> None:
    op.create_table(
        "committees",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("member_count", sa.SmallInteger(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("accounts.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("member_count BETWEEN 1 AND 15", name="ck_committees_member_count"),
    )
    op.create_table(
        "committee_members",
        sa.Column("committee_id", sa.BigInteger(), sa.ForeignKey("committees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lecturer_id", sa.BigInteger(), sa.ForeignKey("lecturers.id"), nullable=False),
        sa.Column("role", committee_role, nullable=False),
        sa.Column("sequence_number", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("committee_id", "lecturer_id"),
        sa.CheckConstraint("sequence_number >= 1", name="ck_committee_members_sequence"),
        sa.UniqueConstraint("committee_id", "sequence_number", name="uq_committee_members_sequence"),
    )


def downgrade() -> None:
    op.drop_table("committee_members")
    op.drop_table("committees")
    committee_role.drop(op.get_bind())
