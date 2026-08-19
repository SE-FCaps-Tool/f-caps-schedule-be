"""Replace physical round room pools with allowed room types.

Room assignment happens after activation.  A round therefore owns the set of
room *types* it permits, while the physical room selected for a session lives
on the session itself.
"""

from alembic import op

revision = "0023_round_room_types"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    op.execute(
        """
        CREATE TABLE round_room_types (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            room_type room_type NOT NULL,
            PRIMARY KEY (round_id, room_type)
        )
        """
    )
    op.execute(
        """
        INSERT INTO round_room_types (round_id, room_type)
        SELECT DISTINCT rr.round_id, r.room_type
        FROM round_rooms rr
        JOIN rooms r ON r.id = rr.room_id
        """
    )
    missing = bind.exec_driver_sql(
        """
        SELECT rr.round_id
        FROM round_rooms rr
        GROUP BY rr.round_id
        HAVING NOT EXISTS (
            SELECT 1 FROM round_room_types rrt WHERE rrt.round_id = rr.round_id
        )
        """
    ).scalars().all()
    if missing:
        raise RuntimeError(
            "Unable to backfill allowed room types for rounds: "
            + ", ".join(str(round_id) for round_id in missing)
        )
    op.execute("DROP TABLE round_rooms")


def downgrade() -> None:
    op.execute(
        """
        CREATE TABLE round_rooms (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            room_id BIGINT NOT NULL REFERENCES rooms(id),
            PRIMARY KEY (round_id, room_id)
        )
        """
    )
    # This downgrade intentionally expands a type allow-list to every room of
    # that type.  The forward migration cannot recover a narrower old pool.
    op.execute(
        """
        INSERT INTO round_rooms (round_id, room_id)
        SELECT rrt.round_id, r.id
        FROM round_room_types rrt
        JOIN rooms r ON r.room_type = rrt.room_type
        ON CONFLICT DO NOTHING
        """
    )
    op.execute("DROP TABLE round_room_types")
