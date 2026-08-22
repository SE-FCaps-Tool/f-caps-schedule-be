"""Simplify round_type: DEFENSE_1_1 -> REVIEW_3, DEFENSE_1_2 -> DEFENSE_1."""

from alembic import op

revision = "0035_round_type_rename"
down_revision = "0034_committees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE round_type_new AS ENUM ('REVIEW_1', 'REVIEW_2', 'REVIEW_3', 'DEFENSE_1', 'DEFENSE_2')"
    )
    op.execute(
        "ALTER TABLE rounds ALTER COLUMN type TYPE round_type_new USING ("
        "  CASE type::text"
        "    WHEN 'DEFENSE_1_1' THEN 'REVIEW_3'"
        "    WHEN 'DEFENSE_1_2' THEN 'DEFENSE_1'"
        "    ELSE type::text"
        "  END"
        ")::round_type_new"
    )
    op.execute("DROP TYPE round_type")
    op.execute("ALTER TYPE round_type_new RENAME TO round_type")


def downgrade() -> None:
    op.execute(
        "CREATE TYPE round_type_old AS ENUM ('REVIEW_1', 'REVIEW_2', 'REVIEW_3', 'DEFENSE_1_1', 'DEFENSE_1_2', 'DEFENSE_2')"
    )
    op.execute(
        "ALTER TABLE rounds ALTER COLUMN type TYPE round_type_old USING ("
        "  CASE type::text"
        "    WHEN 'REVIEW_3' THEN 'DEFENSE_1_1'"
        "    WHEN 'DEFENSE_1' THEN 'DEFENSE_1_2'"
        "    ELSE type::text"
        "  END"
        ")::round_type_old"
    )
    op.execute("DROP TYPE round_type")
    op.execute("ALTER TYPE round_type_old RENAME TO round_type")
