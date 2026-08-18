"""Store normalized data imported from the Excel operational workbook."""

from alembic import op


revision = "0012_excel_import_data"
down_revision = "0011_auth_rate_limit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE round_type ADD VALUE IF NOT EXISTS 'REVIEW_3'")
    op.execute(
        """
        CREATE TABLE excel_import_batches (
            id BIGSERIAL PRIMARY KEY,
            source_file_name VARCHAR(255) NOT NULL,
            source_path TEXT NOT NULL,
            imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            notes TEXT
        );

        CREATE TABLE excel_sheet_rows (
            id BIGSERIAL PRIMARY KEY,
            batch_id BIGINT NOT NULL REFERENCES excel_import_batches(id) ON DELETE CASCADE,
            sheet_name VARCHAR(128) NOT NULL,
            row_number INTEGER NOT NULL CHECK (row_number > 0),
            values_jsonb JSONB NOT NULL,
            formulas_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
            non_empty BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (batch_id, sheet_name, row_number)
        );

        CREATE TABLE excel_projects (
            id BIGSERIAL PRIMARY KEY,
            batch_id BIGINT NOT NULL REFERENCES excel_import_batches(id) ON DELETE CASCADE,
            excel_row INTEGER NOT NULL CHECK (excel_row > 0),
            project_code VARCHAR(64) NOT NULL,
            group_code VARCHAR(64) NOT NULL,
            title_en TEXT,
            title_vi TEXT,
            supervisor_display_name VARCHAR(160),
            supervisor_1_code VARCHAR(64),
            supervisor_2_code VARCHAR(64),
            canonical_project_id BIGINT REFERENCES projects(id) ON DELETE SET NULL,
            canonical_group_id BIGINT REFERENCES groups(id) ON DELETE SET NULL,
            raw_values JSONB NOT NULL,
            UNIQUE (batch_id, excel_row)
        );

        CREATE TABLE excel_review_schedule_rows (
            id BIGSERIAL PRIMARY KEY,
            batch_id BIGINT NOT NULL REFERENCES excel_import_batches(id) ON DELETE CASCADE,
            review_type VARCHAR(16) NOT NULL,
            excel_row INTEGER NOT NULL CHECK (excel_row > 0),
            schedule_code VARCHAR(64) NOT NULL,
            week_code INTEGER,
            day_code INTEGER,
            slot_number INTEGER,
            wds_code INTEGER,
            group_number INTEGER,
            schedule_date DATE,
            date_of_week VARCHAR(16),
            room_name VARCHAR(160),
            reviewer_1_code VARCHAR(64),
            reviewer_2_code VARCHAR(64),
            count_value INTEGER,
            canonical_round_id BIGINT REFERENCES rounds(id) ON DELETE SET NULL,
            canonical_session_id BIGINT REFERENCES sessions(id) ON DELETE SET NULL,
            raw_values JSONB NOT NULL,
            UNIQUE (batch_id, review_type, excel_row)
        );

        CREATE TABLE excel_defense_councils (
            id BIGSERIAL PRIMARY KEY,
            batch_id BIGINT NOT NULL REFERENCES excel_import_batches(id) ON DELETE CASCADE,
            defense_type VARCHAR(16) NOT NULL,
            excel_row INTEGER NOT NULL CHECK (excel_row > 0),
            council_code VARCHAR(64) NOT NULL,
            council_date DATE,
            day_code INTEGER,
            chair_code VARCHAR(64),
            secretary_code VARCHAR(64),
            member_1_code VARCHAR(64),
            member_2_code VARCHAR(64),
            member_3_code VARCHAR(64),
            member_count INTEGER NOT NULL DEFAULT 0 CHECK (member_count >= 0),
            group_count INTEGER,
            member_list TEXT,
            canonical_round_id BIGINT REFERENCES rounds(id) ON DELETE SET NULL,
            raw_values JSONB NOT NULL,
            UNIQUE (batch_id, defense_type, excel_row)
        );

        CREATE TABLE excel_council_groups (
            council_id BIGINT NOT NULL REFERENCES excel_defense_councils(id) ON DELETE CASCADE,
            project_code VARCHAR(64) NOT NULL,
            group_code VARCHAR(64) NOT NULL,
            project_id BIGINT REFERENCES projects(id) ON DELETE SET NULL,
            group_id BIGINT REFERENCES groups(id) ON DELETE SET NULL,
            PRIMARY KEY (council_id, group_code)
        );

        CREATE TABLE excel_summary_workloads (
            id BIGSERIAL PRIMARY KEY,
            batch_id BIGINT NOT NULL REFERENCES excel_import_batches(id) ON DELETE CASCADE,
            excel_row INTEGER NOT NULL CHECK (excel_row > 0),
            lecturer_code VARCHAR(64),
            department VARCHAR(64),
            review_1_count INTEGER,
            review_2_count INTEGER,
            review_3_count INTEGER,
            defense_1_count INTEGER,
            defense_2_count INTEGER,
            raw_values JSONB NOT NULL,
            UNIQUE (batch_id, excel_row)
        );

        CREATE INDEX ix_excel_sheet_rows_batch_sheet
            ON excel_sheet_rows (batch_id, sheet_name);
        CREATE INDEX ix_excel_projects_batch_codes
            ON excel_projects (batch_id, project_code, group_code);
        CREATE INDEX ix_excel_review_schedule_batch_type
            ON excel_review_schedule_rows (batch_id, review_type, schedule_date);
        CREATE INDEX ix_excel_defense_councils_batch_type
            ON excel_defense_councils (batch_id, defense_type, council_date);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS excel_summary_workloads, excel_council_groups,
            excel_defense_councils, excel_review_schedule_rows, excel_projects,
            excel_sheet_rows, excel_import_batches CASCADE;
        """
    )
