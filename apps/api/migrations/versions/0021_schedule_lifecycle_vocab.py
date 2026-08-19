"""Replace legacy schedule lifecycle vocabulary with the public contract.

The enum types are rebuilt instead of using ``ALTER TYPE ... ADD VALUE`` so the
legacy labels can be removed.  The preflight checks intentionally fail before
the type rewrite when data cannot be mapped without losing history.
"""

from alembic import op

revision = "0021_schedule_lifecycle_vocab"
down_revision = "0020_room_type"
branch_labels = None
depends_on = None


def _assert_no_unmapped(table: str, column: str, allowed: str) -> None:
    row = op.get_bind().exec_driver_sql(
        f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL OR {column} NOT IN ({allowed})"
    ).scalar_one()
    if row:
        raise RuntimeError(f"{table}.{column} contains {row} NULL or unmapped value(s)")


def upgrade() -> None:
    bind = op.get_bind()
    # Do this before changing any types, so a failed migration leaves the
    # database untouched and identifies all ambiguous rounds in one error.
    duplicate_rows = bind.exec_driver_sql(
        "SELECT round_id, string_agg(id::text, ',' ORDER BY id) AS version_ids "
        "FROM schedule_versions WHERE status::text = 'VALID' AND activated_at IS NOT NULL "
        "GROUP BY round_id HAVING COUNT(*) > 1"
    ).all()
    if duplicate_rows:
        details = "; ".join(f"round {row[0]} versions [{row[1]}]" for row in duplicate_rows)
        raise RuntimeError("Cannot classify multiple activated VALID versions: " + details)

    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE sessions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status TYPE text USING status::text")
    op.execute("ALTER TABLE sessions ALTER COLUMN status TYPE text USING status::text")

    # Classify the owning version first.  A draft/active version must not hide
    # an already terminal session during the legacy-to-new vocabulary change.
    terminal = bind.exec_driver_sql(
        "SELECT s.id, s.status, s.schedule_version_id FROM sessions s "
        "JOIN schedule_versions sv ON sv.id = s.schedule_version_id "
        "WHERE sv.status IN ('DRAFT', 'ACTIVE', 'VALID') "
        "AND s.status NOT IN ('SCHEDULED', 'ONGOING')"
    ).all()
    if terminal:
        details = ", ".join(f"session {row[0]} ({row[1]}) version {row[2]}" for row in terminal)
        raise RuntimeError("Cannot map terminal sessions owned by DRAFT/ACTIVE versions: " + details)

    op.execute(
        "UPDATE schedule_versions SET status = CASE "
        "WHEN status = 'VALID' AND activated_at IS NULL THEN 'DRAFT' "
        "WHEN status = 'VALID' THEN 'ACTIVE' "
        "WHEN status = 'SUPERSEDED' THEN 'DISCARDED' ELSE status END"
    )
    op.execute(
        "UPDATE sessions SET status = CASE "
        "WHEN schedule_version_id IN (SELECT id FROM schedule_versions WHERE status IN ('DRAFT','ACTIVE')) THEN 'PLANNED' "
        "WHEN status = 'ONGOING' THEN 'SCHEDULED' ELSE status END"
    )
    _assert_no_unmapped("schedule_versions", "status", "'DRAFT','ACTIVE','PUBLISHED','DISCARDED'")
    _assert_no_unmapped("sessions", "status", "'PLANNED','SCHEDULED','COMPLETED','POSTPONED','GROUP_ABSENT','CANCELLED'")

    op.execute("DROP TYPE schedule_version_status")
    op.execute("DROP TYPE session_status")
    op.execute("CREATE TYPE schedule_version_status AS ENUM ('DRAFT','ACTIVE','PUBLISHED','DISCARDED')")
    op.execute("CREATE TYPE session_status AS ENUM ('PLANNED','SCHEDULED','COMPLETED','POSTPONED','GROUP_ABSENT','CANCELLED')")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status TYPE schedule_version_status USING status::text::schedule_version_status")
    op.execute("ALTER TABLE sessions ALTER COLUMN status TYPE session_status USING status::text::session_status")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status SET DEFAULT 'DRAFT'")
    op.execute("ALTER TABLE sessions ALTER COLUMN status SET DEFAULT 'PLANNED'")


def downgrade() -> None:
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE sessions ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status TYPE text USING status::text")
    op.execute("ALTER TABLE sessions ALTER COLUMN status TYPE text USING status::text")
    op.execute("UPDATE schedule_versions SET status = CASE WHEN status = 'ACTIVE' THEN 'VALID' WHEN status = 'DISCARDED' THEN 'SUPERSEDED' ELSE status END")
    op.execute("UPDATE sessions SET status = CASE WHEN status = 'PLANNED' THEN 'SCHEDULED' WHEN status = 'GROUP_ABSENT' THEN 'CANCELLED' ELSE status END")
    op.execute("DROP TYPE schedule_version_status")
    op.execute("DROP TYPE session_status")
    op.execute("CREATE TYPE schedule_version_status AS ENUM ('DRAFT','VALID','PUBLISHED','SUPERSEDED')")
    op.execute("CREATE TYPE session_status AS ENUM ('SCHEDULED','ONGOING','COMPLETED','POSTPONED','CANCELLED')")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status TYPE schedule_version_status USING status::text::schedule_version_status")
    op.execute("ALTER TABLE sessions ALTER COLUMN status TYPE session_status USING status::text::session_status")
    op.execute("ALTER TABLE schedule_versions ALTER COLUMN status SET DEFAULT 'DRAFT'")
    op.execute("ALTER TABLE sessions ALTER COLUMN status SET DEFAULT 'SCHEDULED'")
