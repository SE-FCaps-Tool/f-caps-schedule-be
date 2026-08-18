"""Create the Scheduler-only domain model and database backstops."""

from alembic import op

revision = "0002_domain_model"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.execute(
        """
        CREATE TYPE account_status AS ENUM ('ACTIVE', 'INACTIVE');
        CREATE TYPE system_role AS ENUM ('ADMIN', 'MANAGER', 'LECTURER', 'STUDENT');
        CREATE TYPE semester_status AS ENUM ('DRAFT', 'ACTIVE', 'CLOSED');
        CREATE TYPE project_status AS ENUM ('ACTIVE', 'ARCHIVED');
        CREATE TYPE group_status AS ENUM (
            'PENDING_D11', 'ELIGIBLE_D12', 'D12_CONDITIONAL', 'PENDING_D2',
            'COMPLETED', 'FAILED', 'DROPPED'
        );
        CREATE TYPE membership_role AS ENUM ('MEMBER', 'LEADER');
        CREATE TYPE membership_status AS ENUM ('ACTIVE', 'DROPPED');
        CREATE TYPE supervisor_type AS ENUM ('MAIN', 'CO');
        CREATE TYPE round_type AS ENUM ('REVIEW_1', 'REVIEW_2', 'DEFENSE_1_1', 'DEFENSE_1_2', 'DEFENSE_2');
        CREATE TYPE round_status AS ENUM (
            'DRAFT', 'OPEN_REGISTRATION', 'REGISTRATION_CLOSED', 'SCHEDULING',
            'SCHEDULED', 'PUBLISHED', 'ONGOING', 'POSTPONED', 'COMPLETED',
            'LOCKED', 'CANCELLED'
        );
        CREATE TYPE invitation_status AS ENUM ('PENDING', 'ACCEPTED', 'DECLINED');
        CREATE TYPE availability_state AS ENUM ('AVAILABLE', 'UNAVAILABLE');
        CREATE TYPE schedule_version_status AS ENUM ('DRAFT', 'VALID', 'PUBLISHED', 'SUPERSEDED');
        CREATE TYPE session_status AS ENUM ('SCHEDULED', 'ONGOING', 'COMPLETED', 'POSTPONED', 'CANCELLED');
        CREATE TYPE assignment_role AS ENUM (
            'SUPERVISOR', 'REVIEWER', 'RESULT_OWNER', 'REMEDIATION_VERIFIER', 'PROJECT_LEADER'
        );
        CREATE TYPE result_outcome AS ENUM (
            'LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4', 'PASS', 'NEEDS_FIX', 'FAIL', 'CONDITIONAL'
        );
        CREATE TYPE remediation_status AS ENUM ('OPEN', 'PASSED', 'FAILED', 'OVERDUE');
        CREATE TYPE verify_status AS ENUM ('PENDING', 'VERIFIED', 'REJECTED');
        CREATE TYPE reschedule_status AS ENUM ('REQUESTED', 'APPROVED', 'REJECTED', 'APPLIED');
        CREATE TYPE notification_status AS ENUM ('PENDING', 'SENT', 'FAILED');
        CREATE TYPE outbox_status AS ENUM ('PENDING', 'PROCESSING', 'SENT', 'FAILED');
        """
    )

    op.execute(
        """
        CREATE TABLE accounts (
            id BIGSERIAL PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            display_name VARCHAR(160) NOT NULL,
            password_hash TEXT NOT NULL,
            status account_status NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE account_roles (
            account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            role system_role NOT NULL,
            PRIMARY KEY (account_id, role)
        );
        CREATE TABLE semesters (
            id BIGSERIAL PRIMARY KEY,
            code VARCHAR(32) NOT NULL UNIQUE,
            name VARCHAR(160) NOT NULL,
            status semester_status NOT NULL DEFAULT 'DRAFT',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE UNIQUE INDEX uq_active_semester ON semesters (status) WHERE status = 'ACTIVE';
        CREATE TABLE majors (
            id BIGSERIAL PRIMARY KEY,
            code VARCHAR(32) NOT NULL UNIQUE,
            name VARCHAR(160) NOT NULL
        );
        CREATE TABLE lecturers (
            id BIGSERIAL PRIMARY KEY,
            account_id BIGINT NOT NULL UNIQUE REFERENCES accounts(id),
            lecturer_code VARCHAR(32) NOT NULL UNIQUE
        );
        CREATE TABLE students (
            id BIGSERIAL PRIMARY KEY,
            account_id BIGINT UNIQUE REFERENCES accounts(id),
            student_code VARCHAR(32) NOT NULL UNIQUE
        );
        CREATE TABLE rooms (
            id BIGSERIAL PRIMARY KEY,
            code VARCHAR(32) NOT NULL UNIQUE,
            name VARCHAR(160) NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            active BOOLEAN NOT NULL DEFAULT TRUE
        );
        CREATE TABLE projects (
            id BIGSERIAL PRIMARY KEY,
            semester_id BIGINT NOT NULL REFERENCES semesters(id),
            major_id BIGINT NOT NULL REFERENCES majors(id),
            code VARCHAR(64) NOT NULL,
            title VARCHAR(255) NOT NULL,
            status project_status NOT NULL DEFAULT 'ACTIVE',
            UNIQUE (semester_id, code)
        );
        CREATE TABLE groups (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL UNIQUE REFERENCES projects(id),
            code VARCHAR(64) NOT NULL,
            status group_status NOT NULL DEFAULT 'PENDING_D11',
            UNIQUE (project_id, code)
        );
        CREATE TABLE group_memberships (
            id BIGSERIAL PRIMARY KEY,
            group_id BIGINT NOT NULL REFERENCES groups(id),
            student_id BIGINT NOT NULL REFERENCES students(id),
            membership_role membership_role NOT NULL DEFAULT 'MEMBER',
            status membership_status NOT NULL DEFAULT 'ACTIVE',
            joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            left_at TIMESTAMPTZ,
            reason TEXT,
            CHECK (left_at IS NULL OR left_at > joined_at),
            CHECK ((status = 'ACTIVE' AND left_at IS NULL) OR (status = 'DROPPED' AND left_at IS NOT NULL))
        );
        CREATE UNIQUE INDEX uq_active_group_student
            ON group_memberships (group_id, student_id) WHERE status = 'ACTIVE';
        CREATE UNIQUE INDEX uq_active_group_leader
            ON group_memberships (group_id) WHERE status = 'ACTIVE' AND membership_role = 'LEADER';
        CREATE TABLE project_supervisors (
            project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            supervisor_type supervisor_type NOT NULL,
            PRIMARY KEY (project_id, lecturer_id)
        );
        CREATE TABLE rounds (
            id BIGSERIAL PRIMARY KEY,
            semester_id BIGINT NOT NULL REFERENCES semesters(id),
            type round_type NOT NULL,
            status round_status NOT NULL DEFAULT 'DRAFT',
            session_duration_minutes INTEGER NOT NULL CHECK (session_duration_minutes > 0),
            reviewer_count INTEGER NOT NULL DEFAULT 2 CHECK (reviewer_count > 0),
            registration_deadline TIMESTAMPTZ,
            result_owner_mode BOOLEAN NOT NULL DEFAULT FALSE,
            h12_sessions_per_part INTEGER NOT NULL DEFAULT 4 CHECK (h12_sessions_per_part > 0),
            h12_sessions_per_day INTEGER NOT NULL DEFAULT 8 CHECK (h12_sessions_per_day > 0),
            h12_semester_quota INTEGER CHECK (h12_semester_quota IS NULL OR h12_semester_quota > 0),
            soft_weights JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_by BIGINT REFERENCES accounts(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE round_days (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            day_date DATE NOT NULL,
            UNIQUE (round_id, day_date)
        );
        CREATE TABLE timeslots (
            id BIGSERIAL PRIMARY KEY,
            round_day_id BIGINT NOT NULL REFERENCES round_days(id) ON DELETE CASCADE,
            start_at TIMESTAMPTZ NOT NULL,
            end_at TIMESTAMPTZ NOT NULL,
            CHECK (end_at > start_at),
            UNIQUE (round_day_id, start_at, end_at)
        );
        CREATE TABLE round_groups (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            group_id BIGINT NOT NULL REFERENCES groups(id),
            PRIMARY KEY (round_id, group_id)
        );
        CREATE TABLE round_rooms (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            room_id BIGINT NOT NULL REFERENCES rooms(id),
            PRIMARY KEY (round_id, room_id)
        );
        CREATE TABLE round_invitations (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            status invitation_status NOT NULL DEFAULT 'PENDING',
            response_reason TEXT,
            responded_at TIMESTAMPTZ,
            PRIMARY KEY (round_id, lecturer_id)
        );
        CREATE TABLE lecturer_availabilities (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            timeslot_id BIGINT NOT NULL REFERENCES timeslots(id),
            state availability_state NOT NULL,
            load_preference VARCHAR(16) NOT NULL DEFAULT 'MEDIUM'
                CHECK (load_preference IN ('LOW', 'MEDIUM', 'HIGH')),
            source VARCHAR(32) NOT NULL DEFAULT 'FORM',
            updated_by BIGINT REFERENCES accounts(id),
            PRIMARY KEY (round_id, lecturer_id, timeslot_id)
        );
        CREATE TABLE group_slot_preferences (
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            group_id BIGINT NOT NULL REFERENCES groups(id),
            timeslot_id BIGINT NOT NULL REFERENCES timeslots(id),
            selected BOOLEAN NOT NULL DEFAULT TRUE,
            source VARCHAR(32) NOT NULL DEFAULT 'FORM',
            updated_by BIGINT REFERENCES accounts(id),
            PRIMARY KEY (round_id, group_id, timeslot_id)
        );
        CREATE TABLE conflict_declarations (
            id BIGSERIAL PRIMARY KEY,
            lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
            project_id BIGINT NOT NULL REFERENCES projects(id),
            reason TEXT NOT NULL,
            created_by BIGINT REFERENCES accounts(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (lecturer_id, project_id)
        );
        CREATE TABLE schedule_versions (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            version_no INTEGER NOT NULL CHECK (version_no > 0),
            status schedule_version_status NOT NULL DEFAULT 'DRAFT',
            input_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
            algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
            random_seed BIGINT,
            solver_status VARCHAR(32),
            total_score NUMERIC,
            soft_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_by BIGINT REFERENCES accounts(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            activated_at TIMESTAMPTZ,
            UNIQUE (round_id, version_no)
        );
        CREATE TABLE sessions (
            id BIGSERIAL PRIMARY KEY,
            schedule_version_id BIGINT NOT NULL REFERENCES schedule_versions(id) ON DELETE CASCADE,
            group_id BIGINT NOT NULL REFERENCES groups(id),
            timeslot_id BIGINT NOT NULL REFERENCES timeslots(id),
            room_id BIGINT REFERENCES rooms(id),
            start_at TIMESTAMPTZ NOT NULL,
            end_at TIMESTAMPTZ NOT NULL,
            time_range TSTZRANGE GENERATED ALWAYS AS (tstzrange(start_at, end_at, '[)')) STORED,
            status session_status NOT NULL DEFAULT 'SCHEDULED',
            CHECK (end_at > start_at),
            UNIQUE (schedule_version_id, group_id),
            EXCLUDE USING gist (
                schedule_version_id WITH =,
                room_id WITH =,
                time_range WITH &&
            )
        );
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
            EXCLUDE USING gist (
                schedule_version_id WITH =,
                lecturer_id WITH =,
                time_range WITH &&
            )
        );
        CREATE TABLE session_results (
            id BIGSERIAL PRIMARY KEY,
            session_id BIGINT NOT NULL UNIQUE REFERENCES sessions(id),
            outcome result_outcome NOT NULL,
            note TEXT,
            entered_by BIGINT NOT NULL REFERENCES accounts(id),
            entered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            correction_reason TEXT,
            before_json JSONB,
            after_json JSONB,
            remediation_due_at TIMESTAMPTZ,
            verifier_lecturer_id BIGINT REFERENCES lecturers(id),
            verify_status verify_status NOT NULL DEFAULT 'PENDING'
        );
        CREATE TABLE remediation_cases (
            id BIGSERIAL PRIMARY KEY,
            session_result_id BIGINT NOT NULL UNIQUE REFERENCES session_results(id),
            group_id BIGINT NOT NULL REFERENCES groups(id),
            due_at TIMESTAMPTZ NOT NULL,
            status remediation_status NOT NULL DEFAULT 'OPEN',
            verifier_lecturer_id BIGINT REFERENCES lecturers(id),
            verified_at TIMESTAMPTZ,
            note TEXT
        );
        CREATE TABLE h11_waivers (
            id BIGSERIAL PRIMARY KEY,
            round_id BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            group_id BIGINT NOT NULL REFERENCES groups(id),
            granted_by BIGINT NOT NULL REFERENCES accounts(id),
            reason TEXT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (round_id, group_id)
        );
        CREATE TABLE reschedule_requests (
            id BIGSERIAL PRIMARY KEY,
            session_id BIGINT NOT NULL REFERENCES sessions(id),
            requested_by BIGINT NOT NULL REFERENCES accounts(id),
            reason TEXT NOT NULL,
            status reschedule_status NOT NULL DEFAULT 'REQUESTED',
            reviewed_by BIGINT REFERENCES accounts(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            reviewed_at TIMESTAMPTZ
        );
        CREATE TABLE notifications (
            id BIGSERIAL PRIMARY KEY,
            recipient_account_id BIGINT NOT NULL REFERENCES accounts(id),
            event_type VARCHAR(64) NOT NULL,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            status notification_status NOT NULL DEFAULT 'PENDING',
            sent_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE outbox_jobs (
            id BIGSERIAL PRIMARY KEY,
            topic VARCHAR(128) NOT NULL,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            status outbox_status NOT NULL DEFAULT 'PENDING',
            attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            processed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE audit_events (
            id BIGSERIAL PRIMARY KEY,
            actor_id BIGINT REFERENCES accounts(id),
            action VARCHAR(96) NOT NULL,
            entity_type VARCHAR(96) NOT NULL,
            entity_id VARCHAR(96) NOT NULL,
            reason TEXT,
            before_json JSONB,
            after_json JSONB,
            occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE FUNCTION reject_audit_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'AUDIT_APPEND_ONLY: audit events cannot be updated or deleted';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER audit_events_append_only
            BEFORE UPDATE OR DELETE ON audit_events
            FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS audit_events, outbox_jobs, notifications, reschedule_requests,
            h11_waivers, remediation_cases, session_results, session_reviewers, sessions, schedule_versions,
            conflict_declarations, group_slot_preferences, lecturer_availabilities,
            round_invitations, round_rooms, round_groups, timeslots, round_days, rounds,
            project_supervisors, group_memberships, groups, projects, rooms, students,
            lecturers, majors, semesters, account_roles, accounts CASCADE;
        DROP TYPE IF EXISTS outbox_status, notification_status, reschedule_status,
            verify_status, remediation_status, result_outcome, assignment_role, session_status,
            schedule_version_status, availability_state, invitation_status,
            round_status, round_type, supervisor_type, membership_status, membership_role,
            group_status, project_status, semester_status, system_role, account_status CASCADE;
        DROP FUNCTION IF EXISTS reject_audit_mutation();
        """
    )
