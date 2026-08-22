"""Store English and Vietnamese project titles separately."""

from alembic import op

revision = "0038_project_bilingual_titles"
down_revision = "0037_round_type_vocab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS title_vi VARCHAR(255)")
    op.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS title_en VARCHAR(255)")

    # Preserve the current canonical title for rows created before bilingual
    # fields existed.  Prefer the latest linked Excel staging row when one is
    # available because it contains both source-language values.
    op.execute(
        """
        UPDATE projects p
        SET title_vi = COALESCE(
                (
                    SELECT NULLIF(ep.title_vi, '')
                    FROM excel_projects ep
                    WHERE ep.canonical_project_id = p.id OR ep.project_code = p.code
                    ORDER BY ep.id DESC
                    LIMIT 1
                ),
                p.title
            ),
            title_en = (
                SELECT NULLIF(ep.title_en, '')
                FROM excel_projects ep
                WHERE ep.canonical_project_id = p.id OR ep.project_code = p.code
                ORDER BY ep.id DESC
                LIMIT 1
            )
        WHERE p.title_vi IS NULL
        """
    )
    op.execute("UPDATE projects SET title_vi = title WHERE title_vi IS NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP COLUMN IF EXISTS title_en")
    op.execute("ALTER TABLE projects DROP COLUMN IF EXISTS title_vi")
