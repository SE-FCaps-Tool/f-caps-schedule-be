"""Persist scheduler job lifecycle and retry metadata."""

from alembic import op


revision = "0003_scheduler_jobs"
down_revision = "0002_domain_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE scheduler_jobs (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            status VARCHAR(16) NOT NULL DEFAULT 'QUEUED',
            attempt INTEGER NOT NULL DEFAULT 1 CHECK (attempt > 0),
            idempotency_key VARCHAR(160),
            input_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
            algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
            random_seed BIGINT NOT NULL,
            schedule_version_id BIGINT REFERENCES schedule_versions(id),
            error TEXT,
            queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            started_at TIMESTAMPTZ,
            finished_at TIMESTAMPTZ,
            CHECK (status IN ('QUEUED', 'RUNNING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELLED')),
            UNIQUE (schedule_version_id)
        );
        CREATE UNIQUE INDEX scheduler_jobs_idempotency_key_idx
            ON scheduler_jobs (round_id, idempotency_key)
            WHERE idempotency_key IS NOT NULL;
        CREATE INDEX scheduler_jobs_queue_idx ON scheduler_jobs (status, queued_at);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS scheduler_jobs")
