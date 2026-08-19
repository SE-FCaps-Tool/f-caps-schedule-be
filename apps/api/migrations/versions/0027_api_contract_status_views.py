"""Expose target status vocabularies without rewriting historical enum data."""

from alembic import op


revision = "0027_api_contract_status_views"
down_revision = "0026_semester_four_states"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW api_group_statuses AS
        SELECT g.id,
               g.status::text AS legacy_status,
               CASE
                   WHEN g.status::text = 'DROPPED' THEN 'DISBANDED'
                   WHEN g.status::text = 'PENDING_D11' THEN 'FORMING'
                   WHEN g.project_id IS NOT NULL THEN 'ASSIGNED'
                   ELSE 'FORMED'
               END AS target_status
        FROM groups g
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW api_project_statuses AS
        SELECT p.id,
               p.status::text AS legacy_status,
               CASE WHEN p.status::text = 'ARCHIVED' THEN 'CANCELLED'
                    ELSE p.status::text END AS target_status
        FROM projects p
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW api_invitation_statuses AS
        SELECT i.round_id,
               i.lecturer_id,
               i.status::text AS legacy_status,
               i.status::text AS target_status
        FROM round_invitations i
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW api_session_statuses AS
        SELECT s.id,
               s.status::text AS legacy_status,
               s.status::text AS target_status
        FROM sessions s
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS api_session_statuses")
    op.execute("DROP VIEW IF EXISTS api_invitation_statuses")
    op.execute("DROP VIEW IF EXISTS api_project_statuses")
    op.execute("DROP VIEW IF EXISTS api_group_statuses")
