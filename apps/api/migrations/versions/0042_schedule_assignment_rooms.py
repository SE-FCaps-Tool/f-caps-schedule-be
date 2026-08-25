"""Persist the room selected for a solver assignment."""

import sqlalchemy as sa
from alembic import op


revision = "0042"
down_revision = "0041_multi_role_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "schedule_assignments",
        sa.Column("room_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_schedule_assignments_room_id",
        "schedule_assignments",
        "rooms",
        ["room_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_schedule_assignments_room_id",
        "schedule_assignments",
        type_="foreignkey",
    )
    op.drop_column("schedule_assignments", "room_id")
