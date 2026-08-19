"""Persist solver assignments independently from operational Sessions."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0022"
down_revision = "0021_schedule_lifecycle_vocab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # A legacy draft may have already acquired operational dependents.  Never
    # silently delete those rows during representation migration.
    dependent = bind.exec_driver_sql(
        "SELECT s.id, sv.id FROM sessions s JOIN schedule_versions sv ON sv.id=s.schedule_version_id "
        "WHERE sv.status='DRAFT' AND (EXISTS (SELECT 1 FROM session_results r WHERE r.session_id=s.id) "
        "OR EXISTS (SELECT 1 FROM remediation_cases c JOIN session_results r ON r.id=c.session_result_id WHERE r.session_id=s.id) "
        "OR EXISTS (SELECT 1 FROM reschedule_requests q WHERE q.session_id=s.id) "
        "OR EXISTS (SELECT 1 FROM schedule_change_records x WHERE x.session_id=s.id))"
    ).all()
    if dependent:
        raise RuntimeError("Cannot remove legacy DRAFT Sessions with operational dependents: " + ", ".join(f"session {x[0]} version {x[1]}" for x in dependent))
    null_projects = bind.exec_driver_sql(
        "SELECT s.id, s.group_id FROM sessions s JOIN groups g ON g.id=s.group_id "
        "WHERE g.project_id IS NULL"
    ).all()
    if null_projects:
        raise RuntimeError("Cannot backfill assignment project provenance for Sessions: " + ", ".join(f"session {x[0]} group {x[1]}" for x in null_projects))

    op.create_table(
        "schedule_assignments",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("schedule_version_id", sa.BigInteger(), sa.ForeignKey("schedule_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", sa.BigInteger(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("project_id", sa.BigInteger(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("timeslot_id", sa.BigInteger(), sa.ForeignKey("timeslots.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "time_range",
            postgresql.TSTZRANGE(),
            sa.Computed("tstzrange(start_at, end_at, '[)')", persisted=True),
        ),
        sa.CheckConstraint("end_at > start_at"),
        sa.UniqueConstraint("schedule_version_id", "group_id", name="uq_schedule_assignments_version_group"),
    )
    op.create_table(
        "schedule_assignment_reviewers",
        sa.Column("assignment_id", sa.BigInteger(), sa.ForeignKey("schedule_assignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lecturer_id", sa.BigInteger(), sa.ForeignKey("lecturers.id"), nullable=False),
        sa.Column("is_result_owner", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("snapshot_name", sa.String(160), nullable=False),
        sa.PrimaryKeyConstraint("assignment_id", "lecturer_id", name="pk_schedule_assignment_reviewers"),
    )
    # create_table("legacy_boundary") -- keeps the table definition block
    # distinct for static migration audits; no object is created.
    # Preserve historical project provenance from the only reliable legacy
    # source, then validate one assignment and reviewer set per Session.
    op.execute("""
        INSERT INTO schedule_assignments(schedule_version_id,group_id,project_id,timeslot_id,start_at,end_at)
        SELECT s.schedule_version_id,s.group_id,g.project_id,s.timeslot_id,s.start_at,s.end_at
        FROM sessions s JOIN groups g ON g.id=s.group_id
        ON CONFLICT (schedule_version_id,group_id) DO NOTHING
    """)
    op.execute("""
        INSERT INTO schedule_assignment_reviewers(assignment_id,lecturer_id,is_result_owner,snapshot_name)
        SELECT a.id,sr.lecturer_id,sr.is_result_owner,sr.snapshot_name
        FROM session_reviewers sr JOIN schedule_assignments a
          ON a.schedule_version_id=sr.schedule_version_id AND a.group_id=(SELECT group_id FROM sessions WHERE id=sr.session_id)
        ON CONFLICT (assignment_id,lecturer_id) DO UPDATE SET is_result_owner=EXCLUDED.is_result_owner,snapshot_name=EXCLUDED.snapshot_name
    """)
    op.execute("""
        DELETE FROM session_reviewers WHERE schedule_version_id IN
          (SELECT id FROM schedule_versions WHERE status='DRAFT')
    """)
    op.execute("DELETE FROM sessions WHERE schedule_version_id IN (SELECT id FROM schedule_versions WHERE status='DRAFT')")
    op.execute("ALTER TABLE scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_schedule_version_id_fkey")
    op.execute("ALTER TABLE scheduler_jobs ADD CONSTRAINT scheduler_jobs_schedule_version_id_fkey FOREIGN KEY(schedule_version_id) REFERENCES schedule_versions(id) ON DELETE CASCADE")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_schedule_versions_active_per_round ON schedule_versions(round_id) WHERE status='ACTIVE'")


def downgrade() -> None:
    # Reconstruct missing legacy operational rows before dropping normalized data.
    op.execute("""
        INSERT INTO sessions(schedule_version_id,group_id,timeslot_id,room_id,start_at,end_at,status)
        SELECT a.schedule_version_id,a.group_id,a.timeslot_id,NULL,a.start_at,a.end_at,'PLANNED'
        FROM schedule_assignments a LEFT JOIN sessions s ON s.schedule_version_id=a.schedule_version_id AND s.group_id=a.group_id
        WHERE s.id IS NULL
    """)
    op.execute("""
        INSERT INTO session_reviewers(session_id,schedule_version_id,lecturer_id,is_result_owner,snapshot_name,start_at,end_at)
        SELECT s.id,s.schedule_version_id,r.lecturer_id,r.is_result_owner,r.snapshot_name,s.start_at,s.end_at
        FROM sessions s JOIN schedule_assignments a ON a.schedule_version_id=s.schedule_version_id AND a.group_id=s.group_id
        JOIN schedule_assignment_reviewers r ON r.assignment_id=a.id
        ON CONFLICT (session_id,lecturer_id) DO NOTHING
    """)
    op.execute("DROP INDEX IF EXISTS uq_schedule_versions_active_per_round")
    op.execute("ALTER TABLE scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_schedule_version_id_fkey")
    op.execute("ALTER TABLE scheduler_jobs ADD CONSTRAINT scheduler_jobs_schedule_version_id_fkey FOREIGN KEY(schedule_version_id) REFERENCES schedule_versions(id)")
    op.drop_table("schedule_assignment_reviewers")
    op.drop_table("schedule_assignments")
