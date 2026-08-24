"""Add manual scheduling draft tables."""

import sqlalchemy as sa
from alembic import op

revision = "0039_manual_scheduling"
down_revision = "0038_project_bilingual_titles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manual_schedule_drafts",
        sa.Column("round_id", sa.BigInteger(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("published_schedule_version_id", sa.BigInteger()),
        sa.ForeignKeyConstraint(["round_id"], ["rounds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["published_schedule_version_id"], ["schedule_versions.id"]),
        sa.CheckConstraint("revision >= 0", name="ck_manual_schedule_revision_nonnegative"),
        sa.PrimaryKeyConstraint("round_id"),
    )
    op.create_table(
        "manual_schedule_sessions",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("round_id", sa.BigInteger(), nullable=False),
        sa.Column("timeslot_id", sa.BigInteger(), nullable=False),
        sa.Column("room_id", sa.BigInteger()),
        sa.Column("status", sa.String(16), nullable=False, server_default="DRAFT"),
        sa.Column("published_session_id", sa.BigInteger()),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["round_id"], ["manual_schedule_drafts.round_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["timeslot_id"], ["timeslots.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.ForeignKeyConstraint(["published_session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["accounts.id"]),
        sa.CheckConstraint("status IN ('DRAFT', 'READY', 'PUBLISHED')", name="ck_manual_schedule_session_status"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_manual_schedule_sessions_round_timeslot",
        "manual_schedule_sessions",
        ["round_id", "timeslot_id"],
    )
    op.create_table(
        "manual_schedule_session_groups",
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["session_id"], ["manual_schedule_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.CheckConstraint("position > 0", name="ck_manual_schedule_group_position"),
        sa.PrimaryKeyConstraint("session_id", "group_id"),
        sa.UniqueConstraint("session_id", "position", name="uq_manual_schedule_group_position"),
    )
    op.create_index("ix_manual_schedule_session_groups_group", "manual_schedule_session_groups", ["group_id"])
    op.create_table(
        "manual_schedule_session_reviewers",
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("lecturer_id", sa.BigInteger(), nullable=False),
        sa.Column("role_key", sa.String(32), nullable=False),
        sa.Column("role_order", sa.Integer(), nullable=False),
        sa.Column("snapshot_name", sa.String(160), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["manual_schedule_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lecturer_id"], ["lecturers.id"]),
        sa.CheckConstraint("role_order > 0", name="ck_manual_schedule_reviewer_order"),
        sa.PrimaryKeyConstraint("session_id", "lecturer_id"),
        sa.UniqueConstraint("session_id", "role_key", name="uq_manual_schedule_reviewer_role"),
        sa.UniqueConstraint("session_id", "role_order", name="uq_manual_schedule_reviewer_order"),
    )
    op.create_index(
        "ix_manual_schedule_session_reviewers_lecturer",
        "manual_schedule_session_reviewers",
        ["lecturer_id"],
    )
    op.create_table(
        "session_groups",
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.CheckConstraint("position > 0", name="ck_session_groups_position"),
        sa.PrimaryKeyConstraint("session_id", "group_id"),
        sa.UniqueConstraint("session_id", "position", name="uq_session_groups_position"),
    )
    op.create_index("ix_session_groups_group", "session_groups", ["group_id"])


def downgrade() -> None:
    op.drop_index("ix_session_groups_group", table_name="session_groups")
    op.drop_table("session_groups")
    op.drop_index("ix_manual_schedule_session_reviewers_lecturer", table_name="manual_schedule_session_reviewers")
    op.drop_table("manual_schedule_session_reviewers")
    op.drop_index("ix_manual_schedule_session_groups_group", table_name="manual_schedule_session_groups")
    op.drop_table("manual_schedule_session_groups")
    op.drop_index("ix_manual_schedule_sessions_round_timeslot", table_name="manual_schedule_sessions")
    op.drop_table("manual_schedule_sessions")
    op.drop_table("manual_schedule_drafts")
