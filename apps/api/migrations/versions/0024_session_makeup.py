"""Add a self-referential make-up link for postponed Sessions.

Spec section 73 (Postpone / Make-up): postponing a Session never rewrites
it into a new time slot; it only flips status to POSTPONED. A separate
action creates a new Session that carries makeupOfSessionId = original.id.
This migration adds the nullable link column and a partial unique index
enforcing one make-up per postponed Session.
"""

from alembic import op

revision = "0024_session_makeup"
down_revision = "0023_round_room_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE sessions ADD COLUMN makeup_of_session_id BIGINT REFERENCES sessions(id)"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ux_sessions_makeup_of_session_id
            ON sessions (makeup_of_session_id)
            WHERE makeup_of_session_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX ux_sessions_makeup_of_session_id")
    op.execute("ALTER TABLE sessions DROP COLUMN makeup_of_session_id")
