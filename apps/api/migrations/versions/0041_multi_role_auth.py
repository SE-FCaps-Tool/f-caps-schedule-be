"""Bind sessions to a selected role and support pending role selection."""

from alembic import op

revision = "0041_multi_role_auth"
down_revision = "0040_google_auth_identities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE auth_sessions ADD COLUMN role VARCHAR(32);
        UPDATE auth_sessions s
        SET role = selected.role
        FROM (
            SELECT ar.account_id, MIN(ar.role::text) AS role
            FROM account_roles ar
            GROUP BY ar.account_id
        ) selected
        WHERE selected.account_id = s.account_id;
        ALTER TABLE auth_sessions
            ALTER COLUMN role SET NOT NULL,
            ADD CONSTRAINT auth_sessions_role_check
                CHECK (role IN ('ADMIN', 'MANAGER', 'LECTURER', 'STUDENT'));

        CREATE TABLE auth_login_challenges (
            id BIGSERIAL PRIMARY KEY,
            account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            provider VARCHAR(32) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ,
            CONSTRAINT auth_login_challenges_provider_check
                CHECK (provider IN ('password', 'google'))
        );
        CREATE INDEX auth_login_challenges_active_idx
            ON auth_login_challenges (token_hash, expires_at)
            WHERE used_at IS NULL;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_login_challenges")
    op.execute("ALTER TABLE auth_sessions DROP CONSTRAINT IF EXISTS auth_sessions_role_check")
    op.execute("ALTER TABLE auth_sessions DROP COLUMN IF EXISTS role")
