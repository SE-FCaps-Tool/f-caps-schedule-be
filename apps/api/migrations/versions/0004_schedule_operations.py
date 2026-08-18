"""Add publish/change history and idempotent event keys."""

from alembic import op


revision = "0004_schedule_operations"
down_revision = "0003_scheduler_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE outbox_jobs ADD COLUMN IF NOT EXISTS dedupe_key VARCHAR(180);
        CREATE UNIQUE INDEX IF NOT EXISTS outbox_jobs_dedupe_key_idx
            ON outbox_jobs (dedupe_key) WHERE dedupe_key IS NOT NULL;
        ALTER TABLE notifications ADD COLUMN IF NOT EXISTS dedupe_key VARCHAR(180);
        CREATE UNIQUE INDEX IF NOT EXISTS notifications_dedupe_key_idx
            ON notifications (dedupe_key) WHERE dedupe_key IS NOT NULL;
        CREATE TABLE schedule_change_records (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            schedule_version_id BIGINT NOT NULL REFERENCES schedule_versions(id),
            session_id BIGINT REFERENCES sessions(id),
            actor_id BIGINT NOT NULL REFERENCES accounts(id),
            reason TEXT NOT NULL,
            before_json JSONB NOT NULL,
            after_json JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE round_operation_records (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            actor_id BIGINT NOT NULL REFERENCES accounts(id),
            action VARCHAR(32) NOT NULL,
            reason TEXT NOT NULL,
            before_status VARCHAR(32) NOT NULL,
            after_status VARCHAR(32) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX schedule_change_records_session_idx ON schedule_change_records (session_id, created_at);
        CREATE INDEX round_operation_records_round_idx ON round_operation_records (round_id, created_at);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS round_operation_records, schedule_change_records;
        DROP INDEX IF EXISTS notifications_dedupe_key_idx;
        DROP INDEX IF EXISTS outbox_jobs_dedupe_key_idx;
        ALTER TABLE notifications DROP COLUMN IF EXISTS dedupe_key;
        ALTER TABLE outbox_jobs DROP COLUMN IF EXISTS dedupe_key;
        """
    )
