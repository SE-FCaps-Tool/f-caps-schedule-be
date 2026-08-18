"""Persist a small database-backed login throttle for local deployments."""

from alembic import op

revision = "0011_auth_rate_limit"
down_revision = "0010_membership_approvals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_login_throttles (
            identifier VARCHAR(128) PRIMARY KEY,
            window_started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_login_throttles")
