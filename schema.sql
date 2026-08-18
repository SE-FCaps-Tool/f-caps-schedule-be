-- =============================================================================
-- Capstone Defense Scheduler — PostgreSQL Schema v1.0
-- Khoa Kỹ thuật Phần mềm, Đại học FPT
-- Target: PostgreSQL 14+
-- =============================================================================
-- Quy ước:
--   * PK kỹ thuật: BIGINT GENERATED ALWAYS AS IDENTITY. Mã nghiệp vụ là UNIQUE riêng.
--   * Soft delete: cột deleted_at TIMESTAMPTZ NULL trên các bảng nghiệp vụ chính.
--   * Tập giá trị: native ENUM.
--   * Mọi cột thời điểm dùng TIMESTAMPTZ; giờ trong ngày dùng TIME.
-- =============================================================================

BEGIN;

-- =============================================================================
-- 0. ENUM TYPES
-- =============================================================================

CREATE TYPE user_role          AS ENUM ('ADMIN','MANAGER','LECTURER','STUDENT');
CREATE TYPE semester_status    AS ENUM ('PLANNING','ACTIVE','CLOSED');
CREATE TYPE project_status     AS ENUM ('ACTIVE','CANCELLED','COMPLETED','FAILED');
CREATE TYPE supervisor_role    AS ENUM ('MAIN','CO');
CREATE TYPE group_status       AS ENUM (
    'ACTIVE',            -- đang thực hiện
    'ELIGIBLE_D12',      -- đủ điều kiện ra Defense 1.2
    'D12_CONDITIONAL',   -- kết luận mức 2, chờ xác nhận khắc phục
    'PENDING_D2',        -- kết luận mức 3, chờ Defense 2
    'COMPLETED',         -- hoàn thành
    'FAILED'             -- trượt, làm lại kỳ sau
);
CREATE TYPE member_role        AS ENUM ('LEADER','MEMBER');
CREATE TYPE membership_status  AS ENUM ('ACTIVE','DROPPED');
CREATE TYPE round_type         AS ENUM ('REVIEW_1','REVIEW_2','DEFENSE_1_1','DEFENSE_1_2','DEFENSE_2');
CREATE TYPE round_status       AS ENUM (
    'DRAFT','OPEN_REGISTRATION','REGISTRATION_CLOSED','SCHEDULING',
    'SCHEDULED','PUBLISHED','ONGOING','COMPLETED','LOCKED'
);
CREATE TYPE part_of_day        AS ENUM ('MORNING','AFTERNOON');
CREATE TYPE invitation_status  AS ENUM ('INVITED','ACCEPTED','DECLINED');
CREATE TYPE load_level         AS ENUM ('LOW','MEDIUM','HIGH');
CREATE TYPE availability_source AS ENUM ('SELF','MANAGER');
CREATE TYPE session_status     AS ENUM ('SCHEDULED','ONGOING','COMPLETED','POSTPONED','CANCELLED');
CREATE TYPE outcome_code       AS ENUM (
    'REVIEW_PASS','REVIEW_NEEDS_FIX','REVIEW_FAIL',   -- Review 1 & 2
    'DEFENSE_L1','DEFENSE_L2','DEFENSE_L3','DEFENSE_L4' -- Defense: 4 mức kết luận
);
CREATE TYPE verify_status      AS ENUM ('PENDING','PASSED','FAILED');
CREATE TYPE request_status     AS ENUM ('PENDING','APPROVED','REJECTED');
CREATE TYPE notification_channel AS ENUM ('IN_APP','EMAIL','BOTH');

-- =============================================================================
-- 1. MASTER DATA
-- =============================================================================

CREATE TABLE majors (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code        VARCHAR(10)  NOT NULL UNIQUE,        -- 'SE', 'IS', 'ES'
    name        VARCHAR(150) NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email          VARCHAR(255) NOT NULL,
    full_name      VARCHAR(200) NOT NULL,
    password_hash  VARCHAR(255),                     -- NULL nếu chỉ dùng SSO
    sso_subject    VARCHAR(255) UNIQUE,
    role           user_role    NOT NULL,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login_at  TIMESTAMPTZ,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at     TIMESTAMPTZ
);
-- Email chỉ unique trong phạm vi tài khoản chưa xoá
CREATE UNIQUE INDEX ux_users_email_alive ON users (lower(email)) WHERE deleted_at IS NULL;
CREATE INDEX ix_users_role ON users (role) WHERE deleted_at IS NULL;

CREATE TABLE lecturers (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        BIGINT      NOT NULL UNIQUE REFERENCES users(id),
    lecturer_code  VARCHAR(30) NOT NULL UNIQUE,      -- 'TaiNT51'
    major_id       BIGINT      NOT NULL REFERENCES majors(id),
    department     VARCHAR(150),
    can_be_reviewer BOOLEAN    NOT NULL DEFAULT TRUE, -- cờ chặn khỏi danh sách mời
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at     TIMESTAMPTZ
);
CREATE INDEX ix_lecturers_major ON lecturers (major_id) WHERE deleted_at IS NULL;

CREATE TABLE students (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       BIGINT      NOT NULL UNIQUE REFERENCES users(id),
    student_code  VARCHAR(30) NOT NULL UNIQUE,       -- 'SE160123'
    major_id      BIGINT      NOT NULL REFERENCES majors(id),
    intake        VARCHAR(20),                       -- khoá, VD 'K16'
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at    TIMESTAMPTZ
);

CREATE TABLE rooms (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code          VARCHAR(50)  NOT NULL UNIQUE,      -- 'P.004'
    campus        VARCHAR(100) NOT NULL,             -- 'Khu CNC'
    capacity      SMALLINT,
    has_projector BOOLEAN NOT NULL DEFAULT TRUE,
    is_online     BOOLEAN NOT NULL DEFAULT FALSE,    -- phòng ảo (MS Teams)
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE semesters (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code        VARCHAR(20)  NOT NULL UNIQUE,        -- 'SU26'
    name        VARCHAR(100) NOT NULL,
    start_date  DATE         NOT NULL,
    end_date    DATE         NOT NULL,
    status      semester_status NOT NULL DEFAULT 'PLANNING',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ck_semesters_dates CHECK (end_date > start_date)
);
-- BR-SEM-02: chỉ một học kỳ ACTIVE tại một thời điểm
CREATE UNIQUE INDEX ux_semesters_single_active ON semesters ((status)) WHERE status = 'ACTIVE';

-- Hạn mức số phiên/kỳ cho từng giảng viên (FR-1.2b) — gốc của mục tiêu cân bằng tải S1
CREATE TABLE lecturer_semester_quotas (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lecturer_id   BIGINT   NOT NULL REFERENCES lecturers(id),
    semester_id   BIGINT   NOT NULL REFERENCES semesters(id),
    max_sessions  SMALLINT NOT NULL,
    note          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_quota UNIQUE (lecturer_id, semester_id),
    CONSTRAINT ck_quota_positive CHECK (max_sessions > 0)
);

-- =============================================================================
-- 2. ĐỀ TÀI — NHÓM — SINH VIÊN
-- =============================================================================

CREATE TABLE projects (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    semester_id         BIGINT       NOT NULL REFERENCES semesters(id),
    major_id            BIGINT       NOT NULL REFERENCES majors(id),
    project_code        VARCHAR(30)  NOT NULL,       -- 'SU26SE017'
    title_vi            TEXT         NOT NULL,
    title_en            TEXT,
    status              project_status NOT NULL DEFAULT 'ACTIVE',
    previous_project_id BIGINT REFERENCES projects(id),  -- retake: trỏ về đề tài kỳ trước
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT uq_projects_code UNIQUE (semester_id, project_code)
);
CREATE INDEX ix_projects_semester ON projects (semester_id) WHERE deleted_at IS NULL;

CREATE TABLE project_supervisors (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id   BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    lecturer_id  BIGINT NOT NULL REFERENCES lecturers(id),
    role         supervisor_role NOT NULL,
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_proj_sup UNIQUE (project_id, lecturer_id)
);
-- BR-PRJ-01: đúng 1 GVHD chính mỗi đề tài
CREATE UNIQUE INDEX ux_project_one_main_supervisor
    ON project_supervisors (project_id) WHERE role = 'MAIN';
CREATE INDEX ix_proj_sup_lecturer ON project_supervisors (lecturer_id);

CREATE TABLE groups (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id  BIGINT      NOT NULL UNIQUE REFERENCES projects(id),  -- BR-PRJ-02: 1-1
    semester_id BIGINT      NOT NULL REFERENCES semesters(id),
    group_code  VARCHAR(30) NOT NULL,
    status      group_status NOT NULL DEFAULT 'ACTIVE',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ,
    CONSTRAINT uq_groups_code UNIQUE (semester_id, group_code)
);
CREATE INDEX ix_groups_status ON groups (semester_id, status) WHERE deleted_at IS NULL;

CREATE TABLE group_members (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    group_id             BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    student_id           BIGINT NOT NULL REFERENCES students(id),
    member_role          member_role       NOT NULL DEFAULT 'MEMBER',
    status               membership_status NOT NULL DEFAULT 'ACTIVE',
    joined_at            DATE   NOT NULL DEFAULT CURRENT_DATE,
    left_at              DATE,                       -- ngày hiệu lực drop out
    drop_reason          TEXT,
    drop_requested_by    BIGINT REFERENCES users(id),
    drop_approved_by     BIGINT REFERENCES users(id),
    drop_approved_at     TIMESTAMPTZ,
    CONSTRAINT uq_group_student UNIQUE (group_id, student_id),
    CONSTRAINT ck_drop_consistency CHECK (
        (status = 'ACTIVE'  AND left_at IS NULL)
     OR (status = 'DROPPED' AND left_at IS NOT NULL)
    )
);
-- BR-GRP-03: đúng 1 trưởng nhóm đang hoạt động
CREATE UNIQUE INDEX ux_group_one_active_leader
    ON group_members (group_id) WHERE member_role = 'LEADER' AND status = 'ACTIVE';
CREATE INDEX ix_group_members_student ON group_members (student_id);

-- H8: khai báo xung đột lợi ích
CREATE TABLE conflict_declarations (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lecturer_id  BIGINT NOT NULL REFERENCES lecturers(id),
    project_id   BIGINT NOT NULL REFERENCES projects(id),
    reason       TEXT   NOT NULL,
    declared_by  BIGINT NOT NULL REFERENCES users(id),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_conflict UNIQUE (lecturer_id, project_id)
);

-- =============================================================================
-- 3. ĐỢT ĐÁNH GIÁ — NGÀY — KHUNG GIỜ
-- =============================================================================

CREATE TABLE rounds (
    id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    semester_id              BIGINT      NOT NULL REFERENCES semesters(id),
    major_id                 BIGINT      NOT NULL REFERENCES majors(id),
    round_type               round_type  NOT NULL,
    name                     VARCHAR(150) NOT NULL,
    status                   round_status NOT NULL DEFAULT 'DRAFT',

    -- Thông số theo loại đợt (mặc định do ứng dụng điền, Moderator sửa được)
    session_duration_minutes SMALLINT    NOT NULL,   -- 45 / 60 / 90
    council_size             SMALLINT    NOT NULL,   -- 2 / 3 / 5
    max_groups_per_timeslot  SMALLINT    NOT NULL,   -- H13, áp cho cả đợt

    -- Trần tải giảng viên (H12) — tính theo PHÚT để đúng với mọi độ dài phiên
    max_minutes_per_part     SMALLINT    NOT NULL DEFAULT 240,
    max_minutes_per_day      SMALLINT    NOT NULL DEFAULT 480,

    -- Cấu hình hành vi
    registration_deadline    TIMESTAMPTZ,
    group_selection_mode     BOOLEAN     NOT NULL DEFAULT FALSE, -- FR-4.10
    result_owner_mode        BOOLEAN     NOT NULL DEFAULT TRUE,  -- FR-7.3
    council_reuse_mode       BOOLEAN     NOT NULL DEFAULT FALSE, -- E5: bật cho R1/R2/D1.1
    soft_weights             JSONB       NOT NULL DEFAULT '{}'::jsonb,

    published_at             TIMESTAMPTZ,
    published_by             BIGINT REFERENCES users(id),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at               TIMESTAMPTZ,

    CONSTRAINT ck_rounds_duration CHECK (session_duration_minutes BETWEEN 15 AND 240),
    CONSTRAINT ck_rounds_council  CHECK (council_size BETWEEN 1 AND 9),
    CONSTRAINT ck_rounds_maxgroup CHECK (max_groups_per_timeslot > 0)
);
CREATE INDEX ix_rounds_semester ON rounds (semester_id, round_type) WHERE deleted_at IS NULL;

CREATE TABLE round_days (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id        BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    day_date        DATE   NOT NULL,
    morning_start   TIME,
    morning_end     TIME,
    afternoon_start TIME,
    afternoon_end   TIME,
    note            TEXT,
    CONSTRAINT uq_round_day UNIQUE (round_id, day_date),
    CONSTRAINT ck_morning   CHECK (morning_end   IS NULL OR morning_start   < morning_end),
    CONSTRAINT ck_afternoon CHECK (afternoon_end IS NULL OR afternoon_start < afternoon_end)
);

CREATE TABLE timeslots (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_day_id BIGINT      NOT NULL REFERENCES round_days(id) ON DELETE CASCADE,
    round_id     BIGINT      NOT NULL REFERENCES rounds(id),   -- phi chuẩn hoá cho truy vấn
    start_time   TIME        NOT NULL,
    end_time     TIME        NOT NULL,
    part         part_of_day NOT NULL,
    seq          SMALLINT    NOT NULL,
    CONSTRAINT uq_timeslot UNIQUE (round_day_id, start_time),
    CONSTRAINT ck_timeslot_range CHECK (start_time < end_time)
);
CREATE INDEX ix_timeslots_round ON timeslots (round_id);

-- Nhóm tham gia đợt
CREATE TABLE round_groups (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id   BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    group_id   BIGINT NOT NULL REFERENCES groups(id),
    added_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_round_group UNIQUE (round_id, group_id)
);

-- Phòng khả dụng cho đợt
CREATE TABLE round_rooms (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id  BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    room_id   BIGINT NOT NULL REFERENCES rooms(id),
    CONSTRAINT uq_round_room UNIQUE (round_id, room_id)
);

-- =============================================================================
-- 4. MỜI GIẢNG VIÊN & ĐĂNG KÝ LỊCH RẢNH
-- =============================================================================

CREATE TABLE round_invitations (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id             BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    lecturer_id          BIGINT NOT NULL REFERENCES lecturers(id),
    status               invitation_status NOT NULL DEFAULT 'INVITED',
    decline_reason       TEXT,
    preferred_load_level load_level,                 -- BR-AVL-03
    invited_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    responded_at         TIMESTAMPTZ,
    CONSTRAINT uq_round_invitation UNIQUE (round_id, lecturer_id),
    CONSTRAINT ck_decline_reason CHECK (status <> 'DECLINED' OR decline_reason IS NOT NULL)
);

CREATE TABLE lecturer_availabilities (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id     BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    lecturer_id  BIGINT NOT NULL REFERENCES lecturers(id),
    timeslot_id  BIGINT NOT NULL REFERENCES timeslots(id) ON DELETE CASCADE,
    source       availability_source NOT NULL DEFAULT 'SELF',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_availability UNIQUE (lecturer_id, timeslot_id)
);
CREATE INDEX ix_avail_round_slot ON lecturer_availabilities (round_id, timeslot_id);

CREATE TABLE group_slot_preferences (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id     BIGINT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    group_id     BIGINT NOT NULL REFERENCES groups(id),
    timeslot_id  BIGINT NOT NULL REFERENCES timeslots(id) ON DELETE CASCADE,
    selected_by  BIGINT NOT NULL REFERENCES students(id),   -- trưởng nhóm
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_group_slot UNIQUE (group_id, timeslot_id)
);
CREATE INDEX ix_gsp_round ON group_slot_preferences (round_id, timeslot_id);

-- =============================================================================
-- 5. HỘI ĐỒNG
-- =============================================================================
-- E4: councils tái sử dụng được cho nhiều phiên liên tiếp (bật qua council_reuse_mode).
-- E6: council_members BẤT BIẾN. Đổi người ⇒ tạo council mới, derived_from_council_id
--     trỏ về council cũ, rồi trỏ lại các phiên bị ảnh hưởng.
-- =============================================================================

CREATE TABLE councils (
    id                     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id               BIGINT      NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    code                   VARCHAR(30) NOT NULL,     -- 'HD1', 'HD2'...
    derived_from_council_id BIGINT REFERENCES councils(id),
    change_reason          TEXT,                     -- bắt buộc khi derived_from IS NOT NULL
    created_by             BIGINT REFERENCES users(id),
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_council_code UNIQUE (round_id, code),
    CONSTRAINT ck_council_change_reason
        CHECK (derived_from_council_id IS NULL OR change_reason IS NOT NULL)
);

CREATE TABLE council_members (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    council_id  BIGINT NOT NULL REFERENCES councils(id) ON DELETE CASCADE,
    lecturer_id BIGINT NOT NULL REFERENCES lecturers(id),
    CONSTRAINT uq_council_member UNIQUE (council_id, lecturer_id)
);
CREATE INDEX ix_council_members_lecturer ON council_members (lecturer_id);

-- =============================================================================
-- 6. LỊCH — PHƯƠNG ÁN, PHIÊN, NGƯỜI CHẤM
-- =============================================================================

CREATE TABLE schedule_versions (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    round_id          BIGINT   NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    version_no        SMALLINT NOT NULL,
    is_active         BOOLEAN  NOT NULL DEFAULT FALSE,
    algorithm_params  JSONB    NOT NULL DEFAULT '{}'::jsonb,
    soft_scores       JSONB    NOT NULL DEFAULT '{}'::jsonb,  -- điểm từng ràng buộc mềm S1..S8
    unscheduled_count SMALLINT NOT NULL DEFAULT 0,
    generated_by      BIGINT REFERENCES users(id),
    generated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    note              TEXT,
    CONSTRAINT uq_schedule_version UNIQUE (round_id, version_no)
);
-- Đúng một phương án đang hoạt động cho mỗi đợt
CREATE UNIQUE INDEX ux_schedule_one_active ON schedule_versions (round_id) WHERE is_active;

CREATE TABLE sessions (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schedule_version_id BIGINT NOT NULL REFERENCES schedule_versions(id) ON DELETE CASCADE,
    round_id            BIGINT NOT NULL REFERENCES rounds(id),   -- phi chuẩn hoá cho truy vấn
    timeslot_id         BIGINT NOT NULL REFERENCES timeslots(id),
    room_id             BIGINT NOT NULL REFERENCES rooms(id),
    group_id            BIGINT NOT NULL REFERENCES groups(id),
    council_id          BIGINT NOT NULL REFERENCES councils(id),
    status              session_status NOT NULL DEFAULT 'SCHEDULED',
    note                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- H4: mỗi nhóm đúng 1 phiên trong 1 phương án
    CONSTRAINT uq_session_group UNIQUE (schedule_version_id, group_id),
    -- H3: một phòng không có 2 phiên trùng khung giờ
    CONSTRAINT uq_session_room  UNIQUE (schedule_version_id, timeslot_id, room_id)
);
CREATE INDEX ix_sessions_timeslot ON sessions (schedule_version_id, timeslot_id);
CREATE INDEX ix_sessions_council  ON sessions (council_id);
CREATE INDEX ix_sessions_round    ON sessions (round_id, status);

-- Ảnh chụp danh sách người chấm thực tế của từng phiên.
-- Đồng bộ từ council_members qua trigger; tồn tại để CƯỠNG CHẾ H2 bằng UNIQUE
-- (một giảng viên không thể ở 2 phiên trùng khung giờ) — điều mà council_members
-- không diễn đạt được ở mức khai báo.
CREATE TABLE session_reviewers (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    lecturer_id         BIGINT NOT NULL REFERENCES lecturers(id),
    schedule_version_id BIGINT NOT NULL,             -- phi chuẩn hoá phục vụ UNIQUE bên dưới
    timeslot_id         BIGINT NOT NULL,             -- phi chuẩn hoá phục vụ UNIQUE bên dưới
    assigned_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_session_reviewer UNIQUE (session_id, lecturer_id),
    -- H2: một giảng viên không ở 2 phiên cùng khung giờ trong cùng phương án
    CONSTRAINT uq_lecturer_timeslot UNIQUE (schedule_version_id, timeslot_id, lecturer_id)
);
CREATE INDEX ix_session_reviewers_lecturer ON session_reviewers (lecturer_id);

-- Nhóm không xếp được (FR-5.4)
CREATE TABLE unscheduled_groups (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schedule_version_id BIGINT NOT NULL REFERENCES schedule_versions(id) ON DELETE CASCADE,
    group_id            BIGINT NOT NULL REFERENCES groups(id),
    reason_code         VARCHAR(50) NOT NULL,  -- NO_AVAILABLE_LECTURER, SLOT_FULL, H1_CONFLICT...
    reason_detail       TEXT,
    CONSTRAINT uq_unscheduled UNIQUE (schedule_version_id, group_id)
);

-- =============================================================================
-- 7. KẾT QUẢ & KHẮC PHỤC
-- =============================================================================

CREATE TABLE session_results (
    id                        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id                BIGINT       NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    outcome                   outcome_code NOT NULL,
    note                      TEXT,
    recorded_by_lecturer_id   BIGINT       NOT NULL REFERENCES lecturers(id),
    recorded_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),

    -- Chỉ dùng khi outcome = 'DEFENSE_L2' (BR-REM, theo dõi gọn)
    remediation_due_at        DATE,
    verifier_lecturer_id      BIGINT REFERENCES lecturers(id),
    verify_status             verify_status,
    verified_at               TIMESTAMPTZ,

    -- Manager chốt chuyển mức 2 quá hạn sang Không đạt (FR-7.8)
    overdue_closed_by         BIGINT REFERENCES users(id),
    overdue_closed_at         TIMESTAMPTZ,
    overdue_close_reason      TEXT,

    updated_at                TIMESTAMPTZ  NOT NULL DEFAULT now(),

    -- Kết luận mức 2 bắt buộc có hạn và người xác nhận
    CONSTRAINT ck_result_remediation CHECK (
        outcome <> 'DEFENSE_L2'
        OR (remediation_due_at IS NOT NULL
            AND verifier_lecturer_id IS NOT NULL
            AND verify_status IS NOT NULL)
    ),
    -- Các mức khác không được mang dữ liệu khắc phục
    CONSTRAINT ck_result_no_remediation CHECK (
        outcome = 'DEFENSE_L2' OR remediation_due_at IS NULL
    )
);
CREATE INDEX ix_results_overdue
    ON session_results (remediation_due_at)
    WHERE outcome = 'DEFENSE_L2' AND verify_status = 'PENDING';

-- =============================================================================
-- 8. YÊU CẦU ĐỔI LỊCH, THÔNG BÁO, AUDIT
-- =============================================================================

CREATE TABLE reschedule_requests (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    requested_by        BIGINT NOT NULL REFERENCES users(id),
    reason              TEXT   NOT NULL,
    status              request_status NOT NULL DEFAULT 'PENDING',
    decided_by          BIGINT REFERENCES users(id),
    decided_at          TIMESTAMPTZ,
    decision_note       TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_reschedule_pending ON reschedule_requests (status) WHERE status = 'PENDING';

CREATE TABLE notifications (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type                VARCHAR(60)  NOT NULL,   -- ROUND_INVITED, SCHEDULE_PUBLISHED...
    title               VARCHAR(255) NOT NULL,
    body                TEXT,
    channel             notification_channel NOT NULL DEFAULT 'BOTH',
    related_entity_type VARCHAR(50),
    related_entity_id   BIGINT,
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent_at       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_at             TIMESTAMPTZ
);
CREATE INDEX ix_notifications_unread ON notifications (user_id, created_at DESC) WHERE NOT is_read;

CREATE TABLE audit_logs (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type   VARCHAR(60) NOT NULL,   -- 'session', 'council', 'session_result'...
    entity_id     BIGINT      NOT NULL,
    action        VARCHAR(40) NOT NULL,   -- CREATE, UPDATE, DELETE, PUBLISH, REPLACE_MEMBER...
    actor_user_id BIGINT REFERENCES users(id),
    reason        TEXT,
    old_value     JSONB,
    new_value     JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_audit_entity ON audit_logs (entity_type, entity_id, created_at DESC);
CREATE INDEX ix_audit_actor  ON audit_logs (actor_user_id, created_at DESC);

-- Nhật ký import dữ liệu đầu kỳ (FR-2.9, FR-2.10)
CREATE TABLE import_batches (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    semester_id  BIGINT      NOT NULL REFERENCES semesters(id),
    file_name    VARCHAR(255) NOT NULL,
    imported_by  BIGINT      NOT NULL REFERENCES users(id),
    status       VARCHAR(30) NOT NULL,   -- VALIDATING, VALIDATED, COMMITTED, REJECTED
    summary      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;

-- =============================================================================
-- PHỤ LỤC A — RÀNG BUỘC KHÔNG DIỄN ĐẠT ĐƯỢC BẰNG DDL, CẦN TRIGGER HOẶC TẦNG ỨNG DỤNG
-- =============================================================================
--
-- H1  GVHD không được chấm đề tài mình hướng dẫn.
--     Kiểm tra khi INSERT session_reviewers:
--         NOT EXISTS (SELECT 1 FROM project_supervisors ps
--                     JOIN groups g ON g.project_id = ps.project_id
--                     JOIN sessions s ON s.group_id = g.id
--                     WHERE s.id = NEW.session_id AND ps.lecturer_id = NEW.lecturer_id)
--     Lưu ý: khi council_reuse_mode = TRUE, phải kiểm tra với TẤT CẢ các nhóm
--     mà council đó phụ trách, không chỉ nhóm của phiên hiện tại.
--
-- H5  Số người trong hội đồng = rounds.council_size.
--     Kiểm tra deferred ở cuối giao dịch (COUNT council_members vs council_size).
--
-- H7  Chỉ xếp giảng viên vào khung giờ đã đăng ký rảnh.
--     EXISTS trong lecturer_availabilities(lecturer_id, timeslot_id).
--
-- H8  Không xếp giảng viên đã khai báo xung đột với đề tài.
--
-- H9  Nhóm phải ở đúng group_status để được thêm vào round_groups:
--         REVIEW_1/REVIEW_2/DEFENSE_1_1 → 'ACTIVE'
--         DEFENSE_1_2                   → 'ELIGIBLE_D12' hoặc 'D12_CONDITIONAL'
--         DEFENSE_2                     → 'PENDING_D2'
--
-- H10 Khi group_selection_mode = TRUE và nhóm đã chọn slot:
--     sessions.timeslot_id phải nằm trong group_slot_preferences của nhóm.
--
-- H11 Defense 1.2: hội đồng phải chứa ≥1 giảng viên đã chấm Defense 1.1 của nhóm đó.
--
-- H12 Trần tải theo phút: SUM(rounds.session_duration_minutes) của các phiên cùng
--     buổi / cùng ngày cho một giảng viên ≤ max_minutes_per_part / max_minutes_per_day.
--
-- H13 COUNT(sessions) trong một timeslot ≤ rounds.max_groups_per_timeslot.
--
-- BR-STU-03  Nhóm dưới 4 thành viên vẫn được xếp lịch — chỉ CẢNH BÁO, không chặn.
--
-- FLOW  Sau khi ghi session_results, cập nhật groups.status theo bảng điều hướng:
--         DEFENSE_L1 → ELIGIBLE_D12      DEFENSE_L3 → PENDING_D2
--         DEFENSE_L2 → D12_CONDITIONAL   DEFENSE_L4 → FAILED
--       Kết quả Review KHÔNG đổi group_status (BR-FLOW-01).
--
-- outcome ↔ round_type: giá trị REVIEW_* chỉ hợp lệ với round_type REVIEW_1/REVIEW_2;
--       DEFENSE_L* chỉ hợp lệ với các đợt Defense. Cần trigger vì CHECK không
--       tham chiếu được bảng khác.
-- =============================================================================
