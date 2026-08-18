"""Add database-backed local sessions for the V1 login boundary."""

from alembic import op


revision = "0006_auth_sessions"
down_revision = "0005_result_completion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE auth_sessions (
            id BIGSERIAL PRIMARY KEY,
            account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            csrf_token_hash VARCHAR(128) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ
        );
        CREATE INDEX auth_sessions_active_idx ON auth_sessions (token_hash, expires_at) WHERE revoked_at IS NULL;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_sessions")
