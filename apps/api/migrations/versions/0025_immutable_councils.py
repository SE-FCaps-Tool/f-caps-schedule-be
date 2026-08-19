"""Replace materialized session reviewer rows with immutable Councils.

Councils use a short construction window (``sealed_at IS NULL``).  The
application creates the parent and all members, seals it, and only then
attaches it to a Session.  Database triggers enforce that protocol even when
SQL is issued outside the application.
"""

from alembic import op

revision = "0025_immutable_councils"
down_revision = "0024_session_makeup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    op.execute(
        """
        CREATE TABLE councils (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE RESTRICT,
            supersedes_council_id BIGINT REFERENCES councils(id) ON DELETE RESTRICT,
            created_by BIGINT REFERENCES accounts(id),
            reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            sealed_at TIMESTAMPTZ
        );
        CREATE TABLE council_members (
            council_id BIGINT NOT NULL REFERENCES councils(id) ON DELETE RESTRICT,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            assignment assignment_role NOT NULL DEFAULT 'REVIEWER',
            is_result_owner BOOLEAN NOT NULL DEFAULT FALSE,
            snapshot_name VARCHAR(160) NOT NULL,
            PRIMARY KEY (council_id, lecturer_id)
        );
        ALTER TABLE sessions ADD COLUMN council_id BIGINT REFERENCES councils(id) ON DELETE RESTRICT;
        """
    )

    # A temporary mapping keeps the backfill deterministic without adding a
    # legacy-only column to the new immutable model.
    bind.exec_driver_sql(
        "CREATE TEMP TABLE _council_backfill (session_id BIGINT PRIMARY KEY, council_id BIGINT NOT NULL) ON COMMIT DROP"
    )
    sessions = bind.exec_driver_sql(
        "SELECT s.id, sv.round_id FROM sessions s JOIN schedule_versions sv ON sv.id=s.schedule_version_id ORDER BY s.id"
    ).all()
    for session_id, round_id in sessions:
        council_id = bind.exec_driver_sql(
            "INSERT INTO councils(round_id, reason) VALUES (%s, %s) RETURNING id",
            (round_id, "Backfilled from session_reviewers"),
        ).scalar_one()
        bind.exec_driver_sql(
            "INSERT INTO _council_backfill(session_id, council_id) VALUES (%s, %s)",
            (session_id, council_id),
        )
        bind.exec_driver_sql(
            """
            INSERT INTO council_members(council_id, lecturer_id, assignment, is_result_owner, snapshot_name)
            SELECT %s, lecturer_id, assignment, is_result_owner, snapshot_name
            FROM session_reviewers WHERE session_id = %s
            """,
            (council_id, session_id),
        )

    bind.exec_driver_sql(
        """
        UPDATE sessions s SET council_id = b.council_id
        FROM _council_backfill b WHERE b.session_id = s.id
        """
    )

    missing = bind.exec_driver_sql("SELECT id FROM sessions WHERE council_id IS NULL").all()
    if missing:
        raise RuntimeError("Every Session must have a Council: " + ", ".join(str(row[0]) for row in missing))
    mismatch = bind.exec_driver_sql(
        """
        SELECT s.id FROM sessions s
        JOIN schedule_versions sv ON sv.id=s.schedule_version_id
        JOIN councils c ON c.id=s.council_id
        WHERE c.round_id <> sv.round_id
        """
    ).all()
    if mismatch:
        raise RuntimeError("Council round does not match Session schedule version: " + ", ".join(str(row[0]) for row in mismatch))
    counts = bind.exec_driver_sql(
        """
        SELECT s.id
        FROM sessions s
        LEFT JOIN session_reviewers old ON old.session_id=s.id
        LEFT JOIN council_members current ON current.council_id=s.council_id
        GROUP BY s.id
        HAVING COUNT(old.lecturer_id) <> COUNT(current.lecturer_id)
            OR COUNT(old.lecturer_id) FILTER (WHERE old.is_result_owner) <>
               COUNT(current.lecturer_id) FILTER (WHERE current.is_result_owner)
        """
    ).all()
    if counts:
        raise RuntimeError("Council membership does not match session_reviewers: " + ", ".join(str(row[0]) for row in counts))

    bind.exec_driver_sql("UPDATE councils SET sealed_at=now()")
    bind.exec_driver_sql("ALTER TABLE sessions ALTER COLUMN council_id SET NOT NULL")

    # Councils may only be sealed once; metadata is immutable thereafter.
    bind.exec_driver_sql(
        """
        CREATE FUNCTION prevent_council_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'councils are immutable';
            END IF;
            IF OLD.sealed_at IS NOT NULL THEN
                RAISE EXCEPTION 'sealed councils are immutable';
            END IF;
            IF NEW.id <> OLD.id OR NEW.round_id <> OLD.round_id
               OR NEW.supersedes_council_id IS DISTINCT FROM OLD.supersedes_council_id
               OR NEW.created_by IS DISTINCT FROM OLD.created_by
               OR NEW.reason IS DISTINCT FROM OLD.reason
               OR NEW.created_at IS DISTINCT FROM OLD.created_at
               OR NEW.sealed_at IS NULL THEN
                RAISE EXCEPTION 'a Council may only transition from unsealed to sealed';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER councils_immutable
            BEFORE UPDATE OR DELETE ON councils
            FOR EACH ROW EXECUTE FUNCTION prevent_council_mutation();

        CREATE FUNCTION prevent_council_member_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF (SELECT sealed_at FROM councils WHERE id=NEW.council_id) IS NOT NULL THEN
                    RAISE EXCEPTION 'sealed councils cannot receive members';
                END IF;
                RETURN NEW;
            END IF;
            RAISE EXCEPTION 'council members are immutable';
        END;
        $$;
        CREATE TRIGGER council_members_immutable
            BEFORE INSERT OR UPDATE OR DELETE ON council_members
            FOR EACH ROW EXECUTE FUNCTION prevent_council_member_mutation();

        CREATE FUNCTION validate_session_council() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            council_round BIGINT;
            version_round BIGINT;
            council_sealed TIMESTAMPTZ;
        BEGIN
            SELECT c.round_id, c.sealed_at INTO council_round, council_sealed
            FROM councils c WHERE c.id=NEW.council_id;
            IF council_round IS NULL THEN
                RAISE EXCEPTION 'Session must reference an existing Council';
            END IF;
            IF council_sealed IS NULL THEN
                RAISE EXCEPTION 'Session cannot attach to an unsealed Council';
            END IF;
            SELECT sv.round_id INTO version_round FROM schedule_versions sv
            WHERE sv.id=NEW.schedule_version_id;
            IF version_round IS DISTINCT FROM council_round THEN
                RAISE EXCEPTION 'Council and Session ScheduleVersion must belong to the same Round';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER sessions_council_valid
            AFTER INSERT OR UPDATE OF council_id ON sessions
            DEFERRABLE INITIALLY IMMEDIATE
            FOR EACH ROW EXECUTE FUNCTION validate_session_council();
        """
    )
    bind.exec_driver_sql("DROP TABLE session_reviewers")


def downgrade() -> None:
    bind = op.get_bind()
    bind.exec_driver_sql("DROP TRIGGER IF EXISTS sessions_council_valid ON sessions")
    bind.exec_driver_sql("DROP TRIGGER IF EXISTS council_members_immutable ON council_members")
    bind.exec_driver_sql("DROP TRIGGER IF EXISTS councils_immutable ON councils")
    bind.exec_driver_sql("DROP FUNCTION IF EXISTS validate_session_council()")
    bind.exec_driver_sql("DROP FUNCTION IF EXISTS prevent_council_member_mutation()")
    bind.exec_driver_sql("DROP FUNCTION IF EXISTS prevent_council_mutation()")
    bind.exec_driver_sql(
        """
        CREATE TABLE session_reviewers (
            session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            schedule_version_id BIGINT NOT NULL REFERENCES schedule_versions(id) ON DELETE CASCADE,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            assignment assignment_role NOT NULL DEFAULT 'REVIEWER',
            is_result_owner BOOLEAN NOT NULL DEFAULT FALSE,
            snapshot_name VARCHAR(160) NOT NULL,
            start_at TIMESTAMPTZ NOT NULL,
            end_at TIMESTAMPTZ NOT NULL,
            time_range TSTZRANGE GENERATED ALWAYS AS (tstzrange(start_at, end_at, '[)')) STORED,
            PRIMARY KEY (session_id, lecturer_id),
            CHECK (end_at > start_at),
            EXCLUDE USING gist (schedule_version_id WITH =, lecturer_id WITH =, time_range WITH &&)
        )
        """
    )
    # The exclusion constraint is deliberately not suppressed: a conflicting
    # historical row must abort downgrade rather than silently lose a member.
    bind.exec_driver_sql(
        """
        INSERT INTO session_reviewers(session_id, schedule_version_id, lecturer_id, assignment,
                                      is_result_owner, snapshot_name, start_at, end_at)
        SELECT s.id, s.schedule_version_id, cm.lecturer_id, cm.assignment,
               cm.is_result_owner, cm.snapshot_name, s.start_at, s.end_at
        FROM sessions s JOIN council_members cm ON cm.council_id=s.council_id
        ORDER BY s.id, cm.lecturer_id
        """
    )
    bind.exec_driver_sql("ALTER TABLE sessions DROP COLUMN council_id")
    bind.exec_driver_sql("DROP TABLE council_members")
    bind.exec_driver_sql("DROP TABLE councils")
