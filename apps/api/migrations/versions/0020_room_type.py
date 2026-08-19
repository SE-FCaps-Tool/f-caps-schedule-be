"""Add room_type (NORMAL/SEMINAR/LAB) to rooms."""

from alembic import op

revision = "0020_room_type"
down_revision = "0019_nullable_group_project"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE room_type AS ENUM ('NORMAL', 'SEMINAR', 'LAB')")
    op.execute(
        "ALTER TABLE rooms ADD COLUMN room_type room_type NOT NULL DEFAULT 'NORMAL'"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE rooms DROP COLUMN room_type")
    op.execute("DROP TYPE room_type")
