"""Add students.full_name for students imported without a login account."""

from alembic import op

revision = "0045_student_full_name"
down_revision = "d0c6d4db6f4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE students ADD COLUMN full_name VARCHAR(160) NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE students DROP COLUMN full_name")
