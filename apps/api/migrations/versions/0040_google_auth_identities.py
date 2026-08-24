"""Store external identities linked to local accounts."""

from alembic import op


revision = "0040_google_auth_identities"
down_revision = "0039_manual_scheduling"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE auth_identities (
            id BIGSERIAL PRIMARY KEY,
            account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            provider VARCHAR(32) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            email VARCHAR(320) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_login_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT auth_identities_provider_check CHECK (provider IN ('google')),
            CONSTRAINT auth_identities_provider_subject_unique UNIQUE (provider, subject),
            CONSTRAINT auth_identities_account_provider_unique UNIQUE (account_id, provider)
        );
        CREATE INDEX auth_identities_account_idx ON auth_identities (account_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_identities")
