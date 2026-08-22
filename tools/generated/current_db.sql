--
-- PostgreSQL database dump
--

\restrict XDR8nbrReKDDnhFWmI8sCo7dplCN6p2qxSfbDAB7DlwZdvifhuCIPxrXDg5PJ8D

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.timeslots DROP CONSTRAINT IF EXISTS timeslots_round_day_id_fkey;
ALTER TABLE IF EXISTS ONLY public.timeframes DROP CONSTRAINT IF EXISTS timeframes_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.timeframe_versions DROP CONSTRAINT IF EXISTS timeframe_versions_timeframe_id_fkey;
ALTER TABLE IF EXISTS ONLY public.timeframe_versions DROP CONSTRAINT IF EXISTS timeframe_versions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.timeframe_break_windows DROP CONSTRAINT IF EXISTS timeframe_break_windows_timeframe_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_timeslot_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_schedule_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_room_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_makeup_of_session_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_council_id_fkey;
ALTER TABLE IF EXISTS ONLY public.session_results DROP CONSTRAINT IF EXISTS session_results_verifier_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.session_results DROP CONSTRAINT IF EXISTS session_results_session_id_fkey;
ALTER TABLE IF EXISTS ONLY public.session_results DROP CONSTRAINT IF EXISTS session_results_entered_by_fkey;
ALTER TABLE IF EXISTS ONLY public.semesters DROP CONSTRAINT IF EXISTS semesters_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.semesters DROP CONSTRAINT IF EXISTS semesters_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.semester_lecturer_quotas DROP CONSTRAINT IF EXISTS semester_lecturer_quotas_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.semester_lecturer_quotas DROP CONSTRAINT IF EXISTS semester_lecturer_quotas_semester_id_fkey;
ALTER TABLE IF EXISTS ONLY public.semester_lecturer_quotas DROP CONSTRAINT IF EXISTS semester_lecturer_quotas_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_schedule_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_versions DROP CONSTRAINT IF EXISTS schedule_versions_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_versions DROP CONSTRAINT IF EXISTS schedule_versions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_change_records DROP CONSTRAINT IF EXISTS schedule_change_records_session_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_change_records DROP CONSTRAINT IF EXISTS schedule_change_records_schedule_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_change_records DROP CONSTRAINT IF EXISTS schedule_change_records_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_change_records DROP CONSTRAINT IF EXISTS schedule_change_records_actor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS schedule_assignments_timeslot_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS schedule_assignments_schedule_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS schedule_assignments_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS schedule_assignments_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignment_reviewers DROP CONSTRAINT IF EXISTS schedule_assignment_reviewers_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignment_reviewers DROP CONSTRAINT IF EXISTS schedule_assignment_reviewers_assignment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rounds DROP CONSTRAINT IF EXISTS rounds_timeframe_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rounds DROP CONSTRAINT IF EXISTS rounds_timeframe_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rounds DROP CONSTRAINT IF EXISTS rounds_semester_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rounds DROP CONSTRAINT IF EXISTS rounds_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.round_room_types DROP CONSTRAINT IF EXISTS round_room_types_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_operation_records DROP CONSTRAINT IF EXISTS round_operation_records_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_operation_records DROP CONSTRAINT IF EXISTS round_operation_records_actor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_invitations DROP CONSTRAINT IF EXISTS round_invitations_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_invitations DROP CONSTRAINT IF EXISTS round_invitations_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_groups DROP CONSTRAINT IF EXISTS round_groups_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_groups DROP CONSTRAINT IF EXISTS round_groups_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_days DROP CONSTRAINT IF EXISTS round_days_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.round_committees DROP CONSTRAINT IF EXISTS round_committees_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.reschedule_requests DROP CONSTRAINT IF EXISTS reschedule_requests_session_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reschedule_requests DROP CONSTRAINT IF EXISTS reschedule_requests_reviewed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.reschedule_requests DROP CONSTRAINT IF EXISTS reschedule_requests_requested_by_fkey;
ALTER TABLE IF EXISTS ONLY public.remediation_cases DROP CONSTRAINT IF EXISTS remediation_cases_verifier_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.remediation_cases DROP CONSTRAINT IF EXISTS remediation_cases_session_result_id_fkey;
ALTER TABLE IF EXISTS ONLY public.remediation_cases DROP CONSTRAINT IF EXISTS remediation_cases_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_semester_id_fkey;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_major_id_fkey;
ALTER TABLE IF EXISTS ONLY public.project_supervisors DROP CONSTRAINT IF EXISTS project_supervisors_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.project_supervisors DROP CONSTRAINT IF EXISTS project_supervisors_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_recipient_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.lecturers DROP CONSTRAINT IF EXISTS lecturers_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.lecturer_availabilities DROP CONSTRAINT IF EXISTS lecturer_availabilities_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.lecturer_availabilities DROP CONSTRAINT IF EXISTS lecturer_availabilities_timeslot_id_fkey;
ALTER TABLE IF EXISTS ONLY public.lecturer_availabilities DROP CONSTRAINT IF EXISTS lecturer_availabilities_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.lecturer_availabilities DROP CONSTRAINT IF EXISTS lecturer_availabilities_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.h11_waivers DROP CONSTRAINT IF EXISTS h11_waivers_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.h11_waivers DROP CONSTRAINT IF EXISTS h11_waivers_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.h11_waivers DROP CONSTRAINT IF EXISTS h11_waivers_granted_by_fkey;
ALTER TABLE IF EXISTS ONLY public.groups DROP CONSTRAINT IF EXISTS groups_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_slot_preferences DROP CONSTRAINT IF EXISTS group_slot_preferences_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.group_slot_preferences DROP CONSTRAINT IF EXISTS group_slot_preferences_timeslot_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_slot_preferences DROP CONSTRAINT IF EXISTS group_slot_preferences_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_slot_preferences DROP CONSTRAINT IF EXISTS group_slot_preferences_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_memberships DROP CONSTRAINT IF EXISTS group_memberships_student_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_memberships DROP CONSTRAINT IF EXISTS group_memberships_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.group_memberships DROP CONSTRAINT IF EXISTS group_memberships_drop_requested_by_fkey;
ALTER TABLE IF EXISTS ONLY public.group_memberships DROP CONSTRAINT IF EXISTS group_memberships_drop_approved_by_fkey;
ALTER TABLE IF EXISTS ONLY public.round_committees DROP CONSTRAINT IF EXISTS fk_round_committees_round_id;
ALTER TABLE IF EXISTS ONLY public.round_committees DROP CONSTRAINT IF EXISTS fk_round_committees_committee_id;
ALTER TABLE IF EXISTS ONLY public.excel_summary_workloads DROP CONSTRAINT IF EXISTS excel_summary_workloads_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_sheet_rows DROP CONSTRAINT IF EXISTS excel_sheet_rows_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_review_schedule_rows DROP CONSTRAINT IF EXISTS excel_review_schedule_rows_canonical_session_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_review_schedule_rows DROP CONSTRAINT IF EXISTS excel_review_schedule_rows_canonical_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_review_schedule_rows DROP CONSTRAINT IF EXISTS excel_review_schedule_rows_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_projects DROP CONSTRAINT IF EXISTS excel_projects_canonical_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_projects DROP CONSTRAINT IF EXISTS excel_projects_canonical_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_projects DROP CONSTRAINT IF EXISTS excel_projects_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_defense_councils DROP CONSTRAINT IF EXISTS excel_defense_councils_canonical_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_defense_councils DROP CONSTRAINT IF EXISTS excel_defense_councils_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_council_groups DROP CONSTRAINT IF EXISTS excel_council_groups_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_council_groups DROP CONSTRAINT IF EXISTS excel_council_groups_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.excel_council_groups DROP CONSTRAINT IF EXISTS excel_council_groups_council_id_fkey;
ALTER TABLE IF EXISTS ONLY public.councils DROP CONSTRAINT IF EXISTS councils_supersedes_council_id_fkey;
ALTER TABLE IF EXISTS ONLY public.councils DROP CONSTRAINT IF EXISTS councils_round_id_fkey;
ALTER TABLE IF EXISTS ONLY public.councils DROP CONSTRAINT IF EXISTS councils_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.council_members DROP CONSTRAINT IF EXISTS council_members_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.council_members DROP CONSTRAINT IF EXISTS council_members_council_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conflict_declarations DROP CONSTRAINT IF EXISTS conflict_declarations_project_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conflict_declarations DROP CONSTRAINT IF EXISTS conflict_declarations_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conflict_declarations DROP CONSTRAINT IF EXISTS conflict_declarations_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.committees DROP CONSTRAINT IF EXISTS committees_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.committee_members DROP CONSTRAINT IF EXISTS committee_members_lecturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.committee_members DROP CONSTRAINT IF EXISTS committee_members_committee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auth_sessions DROP CONSTRAINT IF EXISTS auth_sessions_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_events DROP CONSTRAINT IF EXISTS audit_events_actor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.account_roles DROP CONSTRAINT IF EXISTS account_roles_account_id_fkey;
DROP TRIGGER IF EXISTS sessions_council_valid ON public.sessions;
DROP TRIGGER IF EXISTS councils_immutable ON public.councils;
DROP TRIGGER IF EXISTS council_members_immutable ON public.council_members;
DROP TRIGGER IF EXISTS audit_events_append_only ON public.audit_events;
DROP INDEX IF EXISTS public.ux_sessions_makeup_of_session_id;
DROP INDEX IF EXISTS public.uq_timeframes_active_name;
DROP INDEX IF EXISTS public.uq_timeframe_versions_active;
DROP INDEX IF EXISTS public.uq_schedule_versions_active_per_round;
DROP INDEX IF EXISTS public.uq_active_semester;
DROP INDEX IF EXISTS public.uq_active_group_student;
DROP INDEX IF EXISTS public.uq_active_group_leader;
DROP INDEX IF EXISTS public.session_results_entered_at_idx;
DROP INDEX IF EXISTS public.scheduler_jobs_queue_idx;
DROP INDEX IF EXISTS public.scheduler_jobs_idempotency_key_idx;
DROP INDEX IF EXISTS public.schedule_change_records_session_idx;
DROP INDEX IF EXISTS public.round_operation_records_round_idx;
DROP INDEX IF EXISTS public.outbox_jobs_dedupe_key_idx;
DROP INDEX IF EXISTS public.notifications_dedupe_key_idx;
DROP INDEX IF EXISTS public.ix_timeframe_break_windows_version;
DROP INDEX IF EXISTS public.ix_semesters_academic_year;
DROP INDEX IF EXISTS public.ix_rounds_timeframe_id;
DROP INDEX IF EXISTS public.ix_rounds_semester_id;
DROP INDEX IF EXISTS public.ix_round_committees_committee_id;
DROP INDEX IF EXISTS public.ix_excel_sheet_rows_batch_sheet;
DROP INDEX IF EXISTS public.ix_excel_review_schedule_batch_type;
DROP INDEX IF EXISTS public.ix_excel_projects_batch_codes;
DROP INDEX IF EXISTS public.ix_excel_defense_councils_batch_type;
DROP INDEX IF EXISTS public.auth_sessions_active_idx;
ALTER TABLE IF EXISTS ONLY public.timeframe_versions DROP CONSTRAINT IF EXISTS uq_timeframe_versions_number;
ALTER TABLE IF EXISTS ONLY public.timeframe_break_windows DROP CONSTRAINT IF EXISTS uq_timeframe_break_windows_sequence;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS uq_schedule_assignments_version_group;
ALTER TABLE IF EXISTS ONLY public.committee_members DROP CONSTRAINT IF EXISTS uq_committee_members_sequence;
ALTER TABLE IF EXISTS ONLY public.timeslots DROP CONSTRAINT IF EXISTS timeslots_round_day_id_start_at_end_at_key;
ALTER TABLE IF EXISTS ONLY public.timeslots DROP CONSTRAINT IF EXISTS timeslots_pkey;
ALTER TABLE IF EXISTS ONLY public.timeframes DROP CONSTRAINT IF EXISTS timeframes_pkey;
ALTER TABLE IF EXISTS ONLY public.timeframe_versions DROP CONSTRAINT IF EXISTS timeframe_versions_pkey;
ALTER TABLE IF EXISTS ONLY public.timeframe_break_windows DROP CONSTRAINT IF EXISTS timeframe_break_windows_pkey;
ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_student_code_key;
ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_pkey;
ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_account_id_key;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_schedule_version_id_room_id_time_range_excl;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_schedule_version_id_group_id_key;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_pkey;
ALTER TABLE IF EXISTS ONLY public.session_results DROP CONSTRAINT IF EXISTS session_results_session_id_key;
ALTER TABLE IF EXISTS ONLY public.session_results DROP CONSTRAINT IF EXISTS session_results_pkey;
ALTER TABLE IF EXISTS ONLY public.semesters DROP CONSTRAINT IF EXISTS semesters_pkey;
ALTER TABLE IF EXISTS ONLY public.semesters DROP CONSTRAINT IF EXISTS semesters_code_key;
ALTER TABLE IF EXISTS ONLY public.semester_lecturer_quotas DROP CONSTRAINT IF EXISTS semester_lecturer_quotas_pkey;
ALTER TABLE IF EXISTS ONLY public.schema_meta DROP CONSTRAINT IF EXISTS schema_meta_pkey;
ALTER TABLE IF EXISTS ONLY public.scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_schedule_version_id_key;
ALTER TABLE IF EXISTS ONLY public.scheduler_jobs DROP CONSTRAINT IF EXISTS scheduler_jobs_pkey;
ALTER TABLE IF EXISTS ONLY public.schedule_versions DROP CONSTRAINT IF EXISTS schedule_versions_round_id_version_no_key;
ALTER TABLE IF EXISTS ONLY public.schedule_versions DROP CONSTRAINT IF EXISTS schedule_versions_pkey;
ALTER TABLE IF EXISTS ONLY public.schedule_change_records DROP CONSTRAINT IF EXISTS schedule_change_records_pkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignments DROP CONSTRAINT IF EXISTS schedule_assignments_pkey;
ALTER TABLE IF EXISTS ONLY public.rounds DROP CONSTRAINT IF EXISTS rounds_pkey;
ALTER TABLE IF EXISTS ONLY public.round_room_types DROP CONSTRAINT IF EXISTS round_room_types_pkey;
ALTER TABLE IF EXISTS ONLY public.round_operation_records DROP CONSTRAINT IF EXISTS round_operation_records_pkey;
ALTER TABLE IF EXISTS ONLY public.round_invitations DROP CONSTRAINT IF EXISTS round_invitations_pkey;
ALTER TABLE IF EXISTS ONLY public.round_groups DROP CONSTRAINT IF EXISTS round_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.round_days DROP CONSTRAINT IF EXISTS round_days_round_id_day_date_key;
ALTER TABLE IF EXISTS ONLY public.round_days DROP CONSTRAINT IF EXISTS round_days_pkey;
ALTER TABLE IF EXISTS ONLY public.round_committees DROP CONSTRAINT IF EXISTS round_committees_pkey;
ALTER TABLE IF EXISTS ONLY public.rooms DROP CONSTRAINT IF EXISTS rooms_pkey;
ALTER TABLE IF EXISTS ONLY public.rooms DROP CONSTRAINT IF EXISTS rooms_code_key;
ALTER TABLE IF EXISTS ONLY public.reschedule_requests DROP CONSTRAINT IF EXISTS reschedule_requests_pkey;
ALTER TABLE IF EXISTS ONLY public.remediation_cases DROP CONSTRAINT IF EXISTS remediation_cases_session_result_id_key;
ALTER TABLE IF EXISTS ONLY public.remediation_cases DROP CONSTRAINT IF EXISTS remediation_cases_pkey;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_semester_id_code_key;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_pkey;
ALTER TABLE IF EXISTS ONLY public.project_supervisors DROP CONSTRAINT IF EXISTS project_supervisors_pkey;
ALTER TABLE IF EXISTS ONLY public.schedule_assignment_reviewers DROP CONSTRAINT IF EXISTS pk_schedule_assignment_reviewers;
ALTER TABLE IF EXISTS ONLY public.outbox_jobs DROP CONSTRAINT IF EXISTS outbox_jobs_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.majors DROP CONSTRAINT IF EXISTS majors_pkey;
ALTER TABLE IF EXISTS ONLY public.majors DROP CONSTRAINT IF EXISTS majors_code_key;
ALTER TABLE IF EXISTS ONLY public.lecturers DROP CONSTRAINT IF EXISTS lecturers_pkey;
ALTER TABLE IF EXISTS ONLY public.lecturers DROP CONSTRAINT IF EXISTS lecturers_lecturer_code_key;
ALTER TABLE IF EXISTS ONLY public.lecturers DROP CONSTRAINT IF EXISTS lecturers_account_id_key;
ALTER TABLE IF EXISTS ONLY public.lecturer_availabilities DROP CONSTRAINT IF EXISTS lecturer_availabilities_pkey;
ALTER TABLE IF EXISTS ONLY public.h11_waivers DROP CONSTRAINT IF EXISTS h11_waivers_round_id_group_id_key;
ALTER TABLE IF EXISTS ONLY public.h11_waivers DROP CONSTRAINT IF EXISTS h11_waivers_pkey;
ALTER TABLE IF EXISTS ONLY public.groups DROP CONSTRAINT IF EXISTS groups_project_id_key;
ALTER TABLE IF EXISTS ONLY public.groups DROP CONSTRAINT IF EXISTS groups_project_id_code_key;
ALTER TABLE IF EXISTS ONLY public.groups DROP CONSTRAINT IF EXISTS groups_pkey;
ALTER TABLE IF EXISTS ONLY public.group_slot_preferences DROP CONSTRAINT IF EXISTS group_slot_preferences_pkey;
ALTER TABLE IF EXISTS ONLY public.group_memberships DROP CONSTRAINT IF EXISTS group_memberships_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_summary_workloads DROP CONSTRAINT IF EXISTS excel_summary_workloads_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_summary_workloads DROP CONSTRAINT IF EXISTS excel_summary_workloads_batch_id_excel_row_key;
ALTER TABLE IF EXISTS ONLY public.excel_sheet_rows DROP CONSTRAINT IF EXISTS excel_sheet_rows_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_sheet_rows DROP CONSTRAINT IF EXISTS excel_sheet_rows_batch_id_sheet_name_row_number_key;
ALTER TABLE IF EXISTS ONLY public.excel_review_schedule_rows DROP CONSTRAINT IF EXISTS excel_review_schedule_rows_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_review_schedule_rows DROP CONSTRAINT IF EXISTS excel_review_schedule_rows_batch_id_review_type_excel_row_key;
ALTER TABLE IF EXISTS ONLY public.excel_projects DROP CONSTRAINT IF EXISTS excel_projects_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_projects DROP CONSTRAINT IF EXISTS excel_projects_batch_id_excel_row_key;
ALTER TABLE IF EXISTS ONLY public.excel_import_batches DROP CONSTRAINT IF EXISTS excel_import_batches_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_defense_councils DROP CONSTRAINT IF EXISTS excel_defense_councils_pkey;
ALTER TABLE IF EXISTS ONLY public.excel_defense_councils DROP CONSTRAINT IF EXISTS excel_defense_councils_batch_id_defense_type_excel_row_key;
ALTER TABLE IF EXISTS ONLY public.excel_council_groups DROP CONSTRAINT IF EXISTS excel_council_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.db_cleanup_backup_20260822_160826 DROP CONSTRAINT IF EXISTS db_cleanup_backup_20260822_160826_pkey;
ALTER TABLE IF EXISTS ONLY public.councils DROP CONSTRAINT IF EXISTS councils_pkey;
ALTER TABLE IF EXISTS ONLY public.council_members DROP CONSTRAINT IF EXISTS council_members_pkey;
ALTER TABLE IF EXISTS ONLY public.conflict_declarations DROP CONSTRAINT IF EXISTS conflict_declarations_pkey;
ALTER TABLE IF EXISTS ONLY public.conflict_declarations DROP CONSTRAINT IF EXISTS conflict_declarations_lecturer_id_project_id_key;
ALTER TABLE IF EXISTS ONLY public.committees DROP CONSTRAINT IF EXISTS committees_pkey;
ALTER TABLE IF EXISTS ONLY public.committees DROP CONSTRAINT IF EXISTS committees_code_key;
ALTER TABLE IF EXISTS ONLY public.committee_members DROP CONSTRAINT IF EXISTS committee_members_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_sessions DROP CONSTRAINT IF EXISTS auth_sessions_token_hash_key;
ALTER TABLE IF EXISTS ONLY public.auth_sessions DROP CONSTRAINT IF EXISTS auth_sessions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_login_throttles DROP CONSTRAINT IF EXISTS auth_login_throttles_pkey;
ALTER TABLE IF EXISTS ONLY public.audit_events DROP CONSTRAINT IF EXISTS audit_events_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.accounts DROP CONSTRAINT IF EXISTS accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.accounts DROP CONSTRAINT IF EXISTS accounts_email_key;
ALTER TABLE IF EXISTS ONLY public.account_roles DROP CONSTRAINT IF EXISTS account_roles_pkey;
ALTER TABLE IF EXISTS public.timeslots ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.students ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sessions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.session_results ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.semesters ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.scheduler_jobs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.schedule_versions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.schedule_change_records ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.rounds ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.round_operation_records ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.round_days ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.rooms ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.reschedule_requests ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.remediation_cases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.projects ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.outbox_jobs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.notifications ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.majors ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.lecturers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.h11_waivers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.group_memberships ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_summary_workloads ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_sheet_rows ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_review_schedule_rows ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_projects ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_import_batches ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.excel_defense_councils ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.councils ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.conflict_declarations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auth_sessions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.audit_events ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.accounts ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.timeslots_id_seq;
DROP TABLE IF EXISTS public.timeslots;
DROP TABLE IF EXISTS public.timeframes;
DROP TABLE IF EXISTS public.timeframe_versions;
DROP TABLE IF EXISTS public.timeframe_break_windows;
DROP SEQUENCE IF EXISTS public.students_id_seq;
DROP TABLE IF EXISTS public.students;
DROP SEQUENCE IF EXISTS public.sessions_id_seq;
DROP SEQUENCE IF EXISTS public.session_results_id_seq;
DROP TABLE IF EXISTS public.session_results;
DROP SEQUENCE IF EXISTS public.semesters_id_seq;
DROP TABLE IF EXISTS public.semesters;
DROP TABLE IF EXISTS public.semester_lecturer_quotas;
DROP TABLE IF EXISTS public.schema_meta;
DROP SEQUENCE IF EXISTS public.scheduler_jobs_id_seq;
DROP TABLE IF EXISTS public.scheduler_jobs;
DROP SEQUENCE IF EXISTS public.schedule_versions_id_seq;
DROP TABLE IF EXISTS public.schedule_versions;
DROP SEQUENCE IF EXISTS public.schedule_change_records_id_seq;
DROP TABLE IF EXISTS public.schedule_change_records;
DROP TABLE IF EXISTS public.schedule_assignments;
DROP TABLE IF EXISTS public.schedule_assignment_reviewers;
DROP SEQUENCE IF EXISTS public.rounds_id_seq;
DROP TABLE IF EXISTS public.rounds;
DROP TABLE IF EXISTS public.round_room_types;
DROP SEQUENCE IF EXISTS public.round_operation_records_id_seq;
DROP TABLE IF EXISTS public.round_operation_records;
DROP TABLE IF EXISTS public.round_groups;
DROP SEQUENCE IF EXISTS public.round_days_id_seq;
DROP TABLE IF EXISTS public.round_days;
DROP TABLE IF EXISTS public.round_committees;
DROP SEQUENCE IF EXISTS public.rooms_id_seq;
DROP TABLE IF EXISTS public.rooms;
DROP SEQUENCE IF EXISTS public.reschedule_requests_id_seq;
DROP TABLE IF EXISTS public.reschedule_requests;
DROP SEQUENCE IF EXISTS public.remediation_cases_id_seq;
DROP TABLE IF EXISTS public.remediation_cases;
DROP SEQUENCE IF EXISTS public.projects_id_seq;
DROP TABLE IF EXISTS public.project_supervisors;
DROP SEQUENCE IF EXISTS public.outbox_jobs_id_seq;
DROP TABLE IF EXISTS public.outbox_jobs;
DROP SEQUENCE IF EXISTS public.notifications_id_seq;
DROP TABLE IF EXISTS public.notifications;
DROP SEQUENCE IF EXISTS public.majors_id_seq;
DROP TABLE IF EXISTS public.majors;
DROP SEQUENCE IF EXISTS public.lecturers_id_seq;
DROP TABLE IF EXISTS public.lecturers;
DROP TABLE IF EXISTS public.lecturer_availabilities;
DROP SEQUENCE IF EXISTS public.h11_waivers_id_seq;
DROP TABLE IF EXISTS public.h11_waivers;
DROP SEQUENCE IF EXISTS public.groups_id_seq;
DROP TABLE IF EXISTS public.group_slot_preferences;
DROP SEQUENCE IF EXISTS public.group_memberships_id_seq;
DROP TABLE IF EXISTS public.group_memberships;
DROP SEQUENCE IF EXISTS public.excel_summary_workloads_id_seq;
DROP TABLE IF EXISTS public.excel_summary_workloads;
DROP SEQUENCE IF EXISTS public.excel_sheet_rows_id_seq;
DROP TABLE IF EXISTS public.excel_sheet_rows;
DROP SEQUENCE IF EXISTS public.excel_review_schedule_rows_id_seq;
DROP TABLE IF EXISTS public.excel_review_schedule_rows;
DROP SEQUENCE IF EXISTS public.excel_projects_id_seq;
DROP TABLE IF EXISTS public.excel_projects;
DROP SEQUENCE IF EXISTS public.excel_import_batches_id_seq;
DROP TABLE IF EXISTS public.excel_import_batches;
DROP SEQUENCE IF EXISTS public.excel_defense_councils_id_seq;
DROP TABLE IF EXISTS public.excel_defense_councils;
DROP TABLE IF EXISTS public.excel_council_groups;
DROP TABLE IF EXISTS public.db_cleanup_backup_20260822_160826;
DROP SEQUENCE IF EXISTS public.councils_id_seq;
DROP TABLE IF EXISTS public.councils;
DROP TABLE IF EXISTS public.council_members;
DROP SEQUENCE IF EXISTS public.conflict_declarations_id_seq;
DROP TABLE IF EXISTS public.conflict_declarations;
DROP TABLE IF EXISTS public.committees;
DROP TABLE IF EXISTS public.committee_members;
DROP SEQUENCE IF EXISTS public.auth_sessions_id_seq;
DROP TABLE IF EXISTS public.auth_sessions;
DROP TABLE IF EXISTS public.auth_login_throttles;
DROP SEQUENCE IF EXISTS public.audit_events_id_seq;
DROP TABLE IF EXISTS public.audit_events;
DROP VIEW IF EXISTS public.api_session_statuses;
DROP TABLE IF EXISTS public.sessions;
DROP VIEW IF EXISTS public.api_project_statuses;
DROP TABLE IF EXISTS public.projects;
DROP VIEW IF EXISTS public.api_invitation_statuses;
DROP TABLE IF EXISTS public.round_invitations;
DROP VIEW IF EXISTS public.api_group_statuses;
DROP TABLE IF EXISTS public.groups;
DROP TABLE IF EXISTS public.alembic_version;
DROP SEQUENCE IF EXISTS public.accounts_id_seq;
DROP TABLE IF EXISTS public.accounts;
DROP TABLE IF EXISTS public.account_roles;
DROP FUNCTION IF EXISTS public.validate_session_council();
DROP FUNCTION IF EXISTS public.reject_audit_mutation();
DROP FUNCTION IF EXISTS public.prevent_council_mutation();
DROP FUNCTION IF EXISTS public.prevent_council_member_mutation();
DROP TYPE IF EXISTS public.verify_status;
DROP TYPE IF EXISTS public.system_role;
DROP TYPE IF EXISTS public.supervisor_type;
DROP TYPE IF EXISTS public.session_status;
DROP TYPE IF EXISTS public.semester_status;
DROP TYPE IF EXISTS public.schedule_version_status;
DROP TYPE IF EXISTS public.round_type;
DROP TYPE IF EXISTS public.round_status;
DROP TYPE IF EXISTS public.room_type;
DROP TYPE IF EXISTS public.result_outcome;
DROP TYPE IF EXISTS public.reschedule_status;
DROP TYPE IF EXISTS public.remediation_status;
DROP TYPE IF EXISTS public.project_status;
DROP TYPE IF EXISTS public.outbox_status;
DROP TYPE IF EXISTS public.notification_status;
DROP TYPE IF EXISTS public.membership_status;
DROP TYPE IF EXISTS public.membership_role;
DROP TYPE IF EXISTS public.invitation_status;
DROP TYPE IF EXISTS public.group_status;
DROP TYPE IF EXISTS public.committee_role;
DROP TYPE IF EXISTS public.availability_state;
DROP TYPE IF EXISTS public.assignment_role;
DROP TYPE IF EXISTS public.account_status;
DROP EXTENSION IF EXISTS btree_gist;
--
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- Name: account_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.account_status AS ENUM (
    'ACTIVE',
    'INACTIVE'
);


--
-- Name: assignment_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.assignment_role AS ENUM (
    'SUPERVISOR',
    'REVIEWER',
    'RESULT_OWNER',
    'REMEDIATION_VERIFIER',
    'PROJECT_LEADER'
);


--
-- Name: availability_state; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.availability_state AS ENUM (
    'AVAILABLE',
    'UNAVAILABLE'
);


--
-- Name: committee_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.committee_role AS ENUM (
    'REVIEWER',
    'CHAIR',
    'SECRETARY',
    'MEMBER'
);


--
-- Name: group_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.group_status AS ENUM (
    'PENDING_D11',
    'ELIGIBLE_D12',
    'D12_CONDITIONAL',
    'PENDING_D2',
    'COMPLETED',
    'FAILED',
    'DROPPED'
);


--
-- Name: invitation_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.invitation_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'DECLINED'
);


--
-- Name: membership_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.membership_role AS ENUM (
    'MEMBER',
    'LEADER'
);


--
-- Name: membership_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.membership_status AS ENUM (
    'ACTIVE',
    'DROPPED'
);


--
-- Name: notification_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.notification_status AS ENUM (
    'PENDING',
    'SENT',
    'FAILED'
);


--
-- Name: outbox_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.outbox_status AS ENUM (
    'PENDING',
    'PROCESSING',
    'SENT',
    'FAILED'
);


--
-- Name: project_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.project_status AS ENUM (
    'ACTIVE',
    'ARCHIVED'
);


--
-- Name: remediation_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.remediation_status AS ENUM (
    'OPEN',
    'PASSED',
    'FAILED',
    'OVERDUE'
);


--
-- Name: reschedule_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.reschedule_status AS ENUM (
    'REQUESTED',
    'APPROVED',
    'REJECTED',
    'APPLIED'
);


--
-- Name: result_outcome; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.result_outcome AS ENUM (
    'LEVEL_1',
    'LEVEL_2',
    'LEVEL_3',
    'LEVEL_4',
    'PASS',
    'NEEDS_FIX',
    'FAIL',
    'CONDITIONAL',
    'COMPLETED'
);


--
-- Name: room_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.room_type AS ENUM (
    'NORMAL',
    'SEMINAR',
    'LAB'
);


--
-- Name: round_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.round_status AS ENUM (
    'DRAFT',
    'OPEN_REGISTRATION',
    'REGISTRATION_CLOSED',
    'SCHEDULING',
    'SCHEDULED',
    'PUBLISHED',
    'ONGOING',
    'POSTPONED',
    'COMPLETED',
    'LOCKED',
    'CANCELLED'
);


--
-- Name: round_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.round_type AS ENUM (
    'REVIEW_1',
    'REVIEW_2',
    'REVIEW_3',
    'DEFENSE_1',
    'DEFENSE_2',
    'REVIEW_1_1',
    'REVIEW_2_1',
    'DEFENSE_1_1',
    'DEFENSE_1_2'
);


--
-- Name: schedule_version_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.schedule_version_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'PUBLISHED',
    'DISCARDED'
);


--
-- Name: semester_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.semester_status AS ENUM (
    'PLANNING',
    'ACTIVE',
    'CLOSED',
    'ARCHIVED'
);


--
-- Name: session_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.session_status AS ENUM (
    'PLANNED',
    'SCHEDULED',
    'COMPLETED',
    'POSTPONED',
    'GROUP_ABSENT',
    'CANCELLED'
);


--
-- Name: supervisor_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.supervisor_type AS ENUM (
    'MAIN',
    'CO'
);


--
-- Name: system_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.system_role AS ENUM (
    'ADMIN',
    'MANAGER',
    'LECTURER',
    'STUDENT'
);


--
-- Name: verify_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.verify_status AS ENUM (
    'PENDING',
    'VERIFIED',
    'REJECTED'
);


--
-- Name: prevent_council_member_mutation(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_council_member_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF (SELECT sealed_at FROM councils WHERE id=NEW.council_id) IS NOT NULL THEN
                    RAISE EXCEPTION 'sealed councils cannot receive members';
                END IF;
                RETURN NEW;
            END IF;
            RAISE EXCEPTION 'council members are immutable';
        END;
        $$;


--
-- Name: prevent_council_mutation(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.prevent_council_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'councils are immutable';
            END IF;
            IF OLD.sealed_at IS NOT NULL THEN
                RAISE EXCEPTION 'sealed councils are immutable';
            END IF;
            IF NEW.id <> OLD.id OR NEW.round_id <> OLD.round_id
               OR NEW.supersedes_council_id IS DISTINCT FROM OLD.supersedes_council_id
               OR NEW.created_by IS DISTINCT FROM OLD.created_by
               OR NEW.reason IS DISTINCT FROM OLD.reason
               OR NEW.created_at IS DISTINCT FROM OLD.created_at
               OR NEW.sealed_at IS NULL THEN
                RAISE EXCEPTION 'a Council may only transition from unsealed to sealed';
            END IF;
            RETURN NEW;
        END;
        $$;


--
-- Name: reject_audit_mutation(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.reject_audit_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RAISE EXCEPTION 'AUDIT_APPEND_ONLY: audit events cannot be updated or deleted';
        END;
        $$;


--
-- Name: validate_session_council(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_session_council() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
            council_round BIGINT;
            version_round BIGINT;
            council_sealed TIMESTAMPTZ;
        BEGIN
            SELECT c.round_id, c.sealed_at INTO council_round, council_sealed
            FROM councils c WHERE c.id=NEW.council_id;
            IF council_round IS NULL THEN
                RAISE EXCEPTION 'Session must reference an existing Council';
            END IF;
            IF council_sealed IS NULL THEN
                RAISE EXCEPTION 'Session cannot attach to an unsealed Council';
            END IF;
            SELECT sv.round_id INTO version_round FROM schedule_versions sv
            WHERE sv.id=NEW.schedule_version_id;
            IF version_round IS DISTINCT FROM council_round THEN
                RAISE EXCEPTION 'Council and Session ScheduleVersion must belong to the same Round';
            END IF;
            RETURN NEW;
        END;
        $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.account_roles (
    account_id bigint NOT NULL,
    role public.system_role NOT NULL
);


--
-- Name: accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts (
    id bigint NOT NULL,
    email character varying(320) NOT NULL,
    display_name character varying(160) NOT NULL,
    password_hash text NOT NULL,
    status public.account_status DEFAULT 'ACTIVE'::public.account_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.accounts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.groups (
    id bigint NOT NULL,
    project_id bigint,
    code character varying(64) NOT NULL,
    status public.group_status DEFAULT 'PENDING_D11'::public.group_status NOT NULL
);


--
-- Name: api_group_statuses; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.api_group_statuses AS
 SELECT id,
    (status)::text AS legacy_status,
        CASE
            WHEN ((status)::text = 'DROPPED'::text) THEN 'DISBANDED'::text
            WHEN ((status)::text = 'PENDING_D11'::text) THEN 'FORMING'::text
            WHEN (project_id IS NOT NULL) THEN 'ASSIGNED'::text
            ELSE 'FORMED'::text
        END AS target_status
   FROM public.groups g;


--
-- Name: round_invitations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_invitations (
    round_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    status public.invitation_status DEFAULT 'PENDING'::public.invitation_status NOT NULL,
    response_reason text,
    responded_at timestamp with time zone
);


--
-- Name: api_invitation_statuses; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.api_invitation_statuses AS
 SELECT round_id,
    lecturer_id,
    (status)::text AS legacy_status,
    (status)::text AS target_status
   FROM public.round_invitations i;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    id bigint NOT NULL,
    semester_id bigint NOT NULL,
    major_id bigint NOT NULL,
    code character varying(64) NOT NULL,
    title character varying(255) NOT NULL,
    status public.project_status DEFAULT 'ACTIVE'::public.project_status NOT NULL,
    title_vi character varying(255),
    title_en character varying(255)
);


--
-- Name: api_project_statuses; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.api_project_statuses AS
 SELECT id,
    (status)::text AS legacy_status,
        CASE
            WHEN ((status)::text = 'ARCHIVED'::text) THEN 'CANCELLED'::text
            ELSE (status)::text
        END AS target_status
   FROM public.projects p;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions (
    id bigint NOT NULL,
    schedule_version_id bigint NOT NULL,
    group_id bigint NOT NULL,
    timeslot_id bigint NOT NULL,
    room_id bigint,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    time_range tstzrange GENERATED ALWAYS AS (tstzrange(start_at, end_at, '[)'::text)) STORED,
    status public.session_status DEFAULT 'PLANNED'::public.session_status NOT NULL,
    makeup_of_session_id bigint,
    council_id bigint NOT NULL,
    CONSTRAINT sessions_check CHECK ((end_at > start_at))
);


--
-- Name: api_session_statuses; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.api_session_statuses AS
 SELECT id,
    (status)::text AS legacy_status,
    (status)::text AS target_status
   FROM public.sessions s;


--
-- Name: audit_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_events (
    id bigint NOT NULL,
    actor_id bigint,
    action character varying(96) NOT NULL,
    entity_type character varying(96) NOT NULL,
    entity_id character varying(96) NOT NULL,
    reason text,
    before_json jsonb,
    after_json jsonb,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_events_id_seq OWNED BY public.audit_events.id;


--
-- Name: auth_login_throttles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_login_throttles (
    identifier character varying(128) NOT NULL,
    window_started_at timestamp with time zone DEFAULT now() NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT auth_login_throttles_attempts_check CHECK ((attempts >= 0))
);


--
-- Name: auth_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_sessions (
    id bigint NOT NULL,
    account_id bigint NOT NULL,
    token_hash character varying(128) NOT NULL,
    csrf_token_hash character varying(128) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone
);


--
-- Name: auth_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_sessions_id_seq OWNED BY public.auth_sessions.id;


--
-- Name: committee_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.committee_members (
    committee_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    role public.committee_role NOT NULL,
    sequence_number smallint NOT NULL,
    CONSTRAINT ck_committee_members_sequence CHECK ((sequence_number >= 1))
);


--
-- Name: committees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.committees (
    id bigint NOT NULL,
    code character varying(32) NOT NULL,
    member_count smallint NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_committees_member_count CHECK (((member_count >= 1) AND (member_count <= 15)))
);


--
-- Name: committees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.committees ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.committees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: conflict_declarations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conflict_declarations (
    id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    project_id bigint NOT NULL,
    reason text NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: conflict_declarations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conflict_declarations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conflict_declarations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conflict_declarations_id_seq OWNED BY public.conflict_declarations.id;


--
-- Name: council_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.council_members (
    council_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    assignment public.assignment_role DEFAULT 'REVIEWER'::public.assignment_role NOT NULL,
    is_result_owner boolean DEFAULT false NOT NULL,
    snapshot_name character varying(160) NOT NULL
);


--
-- Name: councils; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.councils (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    supersedes_council_id bigint,
    created_by bigint,
    reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    sealed_at timestamp with time zone
);


--
-- Name: councils_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.councils_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: councils_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.councils_id_seq OWNED BY public.councils.id;


--
-- Name: db_cleanup_backup_20260822_160826; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.db_cleanup_backup_20260822_160826 (
    backup_id bigint NOT NULL,
    table_name text NOT NULL,
    row_data jsonb NOT NULL,
    backed_up_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE db_cleanup_backup_20260822_160826; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.db_cleanup_backup_20260822_160826 IS 'Full public-table snapshot before cleanup/import';


--
-- Name: db_cleanup_backup_20260822_160826_backup_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.db_cleanup_backup_20260822_160826 ALTER COLUMN backup_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.db_cleanup_backup_20260822_160826_backup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: excel_council_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_council_groups (
    council_id bigint NOT NULL,
    project_code character varying(64) NOT NULL,
    group_code character varying(64) NOT NULL,
    project_id bigint,
    group_id bigint
);


--
-- Name: excel_defense_councils; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_defense_councils (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    defense_type character varying(16) NOT NULL,
    excel_row integer NOT NULL,
    council_code character varying(64) NOT NULL,
    council_date date,
    day_code integer,
    chair_code character varying(64),
    secretary_code character varying(64),
    member_1_code character varying(64),
    member_2_code character varying(64),
    member_3_code character varying(64),
    member_count integer DEFAULT 0 NOT NULL,
    group_count integer,
    member_list text,
    canonical_round_id bigint,
    raw_values jsonb NOT NULL,
    CONSTRAINT excel_defense_councils_excel_row_check CHECK ((excel_row > 0)),
    CONSTRAINT excel_defense_councils_member_count_check CHECK ((member_count >= 0))
);


--
-- Name: excel_defense_councils_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_defense_councils_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_defense_councils_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_defense_councils_id_seq OWNED BY public.excel_defense_councils.id;


--
-- Name: excel_import_batches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_import_batches (
    id bigint NOT NULL,
    source_file_name character varying(255) NOT NULL,
    source_path text NOT NULL,
    imported_at timestamp with time zone DEFAULT now() NOT NULL,
    notes text
);


--
-- Name: excel_import_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_import_batches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_import_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_import_batches_id_seq OWNED BY public.excel_import_batches.id;


--
-- Name: excel_projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_projects (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    excel_row integer NOT NULL,
    project_code character varying(64) NOT NULL,
    group_code character varying(64) NOT NULL,
    title_en text,
    title_vi text,
    supervisor_display_name character varying(160),
    supervisor_1_code character varying(64),
    supervisor_2_code character varying(64),
    canonical_project_id bigint,
    canonical_group_id bigint,
    raw_values jsonb NOT NULL,
    CONSTRAINT excel_projects_excel_row_check CHECK ((excel_row > 0))
);


--
-- Name: excel_projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_projects_id_seq OWNED BY public.excel_projects.id;


--
-- Name: excel_review_schedule_rows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_review_schedule_rows (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    review_type character varying(16) NOT NULL,
    excel_row integer NOT NULL,
    schedule_code character varying(64) NOT NULL,
    week_code integer,
    day_code integer,
    slot_number integer,
    wds_code integer,
    group_number integer,
    schedule_date date,
    date_of_week character varying(16),
    room_name character varying(160),
    reviewer_1_code character varying(64),
    reviewer_2_code character varying(64),
    count_value integer,
    canonical_round_id bigint,
    canonical_session_id bigint,
    raw_values jsonb NOT NULL,
    CONSTRAINT excel_review_schedule_rows_excel_row_check CHECK ((excel_row > 0))
);


--
-- Name: excel_review_schedule_rows_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_review_schedule_rows_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_review_schedule_rows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_review_schedule_rows_id_seq OWNED BY public.excel_review_schedule_rows.id;


--
-- Name: excel_sheet_rows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_sheet_rows (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    sheet_name character varying(128) NOT NULL,
    row_number integer NOT NULL,
    values_jsonb jsonb NOT NULL,
    formulas_jsonb jsonb DEFAULT '{}'::jsonb NOT NULL,
    non_empty boolean DEFAULT true NOT NULL,
    CONSTRAINT excel_sheet_rows_row_number_check CHECK ((row_number > 0))
);


--
-- Name: excel_sheet_rows_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_sheet_rows_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_sheet_rows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_sheet_rows_id_seq OWNED BY public.excel_sheet_rows.id;


--
-- Name: excel_summary_workloads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.excel_summary_workloads (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    excel_row integer NOT NULL,
    lecturer_code character varying(64),
    department character varying(64),
    review_1_count integer,
    review_2_count integer,
    review_3_count integer,
    defense_1_count integer,
    defense_2_count integer,
    raw_values jsonb NOT NULL,
    CONSTRAINT excel_summary_workloads_excel_row_check CHECK ((excel_row > 0))
);


--
-- Name: excel_summary_workloads_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.excel_summary_workloads_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: excel_summary_workloads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.excel_summary_workloads_id_seq OWNED BY public.excel_summary_workloads.id;


--
-- Name: group_memberships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_memberships (
    id bigint NOT NULL,
    group_id bigint NOT NULL,
    student_id bigint NOT NULL,
    membership_role public.membership_role DEFAULT 'MEMBER'::public.membership_role NOT NULL,
    status public.membership_status DEFAULT 'ACTIVE'::public.membership_status NOT NULL,
    joined_at timestamp with time zone DEFAULT now() NOT NULL,
    left_at timestamp with time zone,
    reason text,
    drop_requested_by bigint,
    drop_approved_by bigint,
    CONSTRAINT group_memberships_check CHECK (((left_at IS NULL) OR (left_at > joined_at))),
    CONSTRAINT group_memberships_check1 CHECK ((((status = 'ACTIVE'::public.membership_status) AND (left_at IS NULL)) OR ((status = 'DROPPED'::public.membership_status) AND (left_at IS NOT NULL))))
);


--
-- Name: group_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_memberships_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_memberships_id_seq OWNED BY public.group_memberships.id;


--
-- Name: group_slot_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_slot_preferences (
    round_id bigint NOT NULL,
    group_id bigint NOT NULL,
    timeslot_id bigint NOT NULL,
    selected boolean DEFAULT true NOT NULL,
    source character varying(32) DEFAULT 'FORM'::character varying NOT NULL,
    updated_by bigint
);


--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: h11_waivers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.h11_waivers (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    group_id bigint NOT NULL,
    granted_by bigint NOT NULL,
    reason text NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: h11_waivers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.h11_waivers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: h11_waivers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.h11_waivers_id_seq OWNED BY public.h11_waivers.id;


--
-- Name: lecturer_availabilities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lecturer_availabilities (
    round_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    timeslot_id bigint NOT NULL,
    state public.availability_state NOT NULL,
    load_preference character varying(16) DEFAULT 'MEDIUM'::character varying NOT NULL,
    source character varying(32) DEFAULT 'FORM'::character varying NOT NULL,
    updated_by bigint,
    CONSTRAINT lecturer_availabilities_load_preference_check CHECK (((load_preference)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying])::text[])))
);


--
-- Name: lecturers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lecturers (
    id bigint NOT NULL,
    account_id bigint NOT NULL,
    lecturer_code character varying(32) NOT NULL
);


--
-- Name: lecturers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lecturers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lecturers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lecturers_id_seq OWNED BY public.lecturers.id;


--
-- Name: majors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.majors (
    id bigint NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(160) NOT NULL
);


--
-- Name: majors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.majors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: majors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.majors_id_seq OWNED BY public.majors.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id bigint NOT NULL,
    recipient_account_id bigint NOT NULL,
    event_type character varying(64) NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    status public.notification_status DEFAULT 'PENDING'::public.notification_status NOT NULL,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    dedupe_key character varying(180)
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: outbox_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outbox_jobs (
    id bigint NOT NULL,
    topic character varying(128) NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    status public.outbox_status DEFAULT 'PENDING'::public.outbox_status NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    available_at timestamp with time zone DEFAULT now() NOT NULL,
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    dedupe_key character varying(180),
    CONSTRAINT outbox_jobs_attempts_check CHECK ((attempts >= 0))
);


--
-- Name: outbox_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.outbox_jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: outbox_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.outbox_jobs_id_seq OWNED BY public.outbox_jobs.id;


--
-- Name: project_supervisors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_supervisors (
    project_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    supervisor_type public.supervisor_type NOT NULL
);


--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: remediation_cases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.remediation_cases (
    id bigint NOT NULL,
    session_result_id bigint NOT NULL,
    group_id bigint NOT NULL,
    due_at timestamp with time zone NOT NULL,
    status public.remediation_status DEFAULT 'OPEN'::public.remediation_status NOT NULL,
    verifier_lecturer_id bigint,
    verified_at timestamp with time zone,
    note text
);


--
-- Name: remediation_cases_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.remediation_cases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: remediation_cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.remediation_cases_id_seq OWNED BY public.remediation_cases.id;


--
-- Name: reschedule_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reschedule_requests (
    id bigint NOT NULL,
    session_id bigint NOT NULL,
    requested_by bigint NOT NULL,
    reason text NOT NULL,
    status public.reschedule_status DEFAULT 'REQUESTED'::public.reschedule_status NOT NULL,
    reviewed_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    reviewed_at timestamp with time zone,
    decision_note text
);


--
-- Name: reschedule_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reschedule_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reschedule_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reschedule_requests_id_seq OWNED BY public.reschedule_requests.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rooms (
    id bigint NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(160) NOT NULL,
    capacity integer NOT NULL,
    active boolean DEFAULT true NOT NULL,
    room_type public.room_type DEFAULT 'NORMAL'::public.room_type NOT NULL,
    CONSTRAINT rooms_capacity_check CHECK ((capacity > 0))
);


--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: round_committees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_committees (
    round_id bigint NOT NULL,
    committee_id bigint NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: round_days; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_days (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    day_date date NOT NULL
);


--
-- Name: round_days_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.round_days_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: round_days_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.round_days_id_seq OWNED BY public.round_days.id;


--
-- Name: round_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_groups (
    round_id bigint NOT NULL,
    group_id bigint NOT NULL
);


--
-- Name: round_operation_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_operation_records (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    actor_id bigint NOT NULL,
    action character varying(32) NOT NULL,
    reason text NOT NULL,
    before_status character varying(32) NOT NULL,
    after_status character varying(32) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: round_operation_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.round_operation_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: round_operation_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.round_operation_records_id_seq OWNED BY public.round_operation_records.id;


--
-- Name: round_room_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.round_room_types (
    round_id bigint NOT NULL,
    room_type public.room_type NOT NULL
);


--
-- Name: rounds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rounds (
    id bigint NOT NULL,
    semester_id bigint NOT NULL,
    type public.round_type NOT NULL,
    status public.round_status DEFAULT 'DRAFT'::public.round_status NOT NULL,
    session_duration_minutes integer NOT NULL,
    reviewer_count integer DEFAULT 2 NOT NULL,
    registration_deadline timestamp with time zone,
    result_owner_mode boolean DEFAULT false NOT NULL,
    h12_sessions_per_part integer DEFAULT 4 NOT NULL,
    h12_sessions_per_day integer DEFAULT 8 NOT NULL,
    h12_semester_quota integer,
    soft_weights jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    group_selection_mode boolean DEFAULT false NOT NULL,
    start_date date,
    end_date date,
    max_groups_per_timeslot integer,
    max_minutes_per_part integer,
    max_minutes_per_day integer,
    name text,
    description text,
    group_preference_deadline timestamp with time zone,
    lecturer_registration_closed_at timestamp with time zone,
    timeframe_id bigint,
    timeframe_version_id bigint,
    CONSTRAINT ck_round_timeframe_binding_pair CHECK ((((timeframe_id IS NULL) AND (timeframe_version_id IS NULL)) OR ((timeframe_id IS NOT NULL) AND (timeframe_version_id IS NOT NULL)))),
    CONSTRAINT rounds_h12_semester_quota_check CHECK (((h12_semester_quota IS NULL) OR (h12_semester_quota > 0))),
    CONSTRAINT rounds_h12_sessions_per_day_check CHECK ((h12_sessions_per_day > 0)),
    CONSTRAINT rounds_h12_sessions_per_part_check CHECK ((h12_sessions_per_part > 0)),
    CONSTRAINT rounds_max_groups_per_timeslot_check CHECK (((max_groups_per_timeslot IS NULL) OR (max_groups_per_timeslot > 0))),
    CONSTRAINT rounds_max_minutes_per_day_check CHECK (((max_minutes_per_day IS NULL) OR (max_minutes_per_day > 0))),
    CONSTRAINT rounds_max_minutes_per_part_check CHECK (((max_minutes_per_part IS NULL) OR (max_minutes_per_part > 0))),
    CONSTRAINT rounds_reviewer_count_check CHECK ((reviewer_count > 0)),
    CONSTRAINT rounds_session_duration_minutes_check CHECK ((session_duration_minutes > 0))
);


--
-- Name: rounds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rounds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rounds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rounds_id_seq OWNED BY public.rounds.id;


--
-- Name: schedule_assignment_reviewers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_assignment_reviewers (
    assignment_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    is_result_owner boolean DEFAULT false NOT NULL,
    snapshot_name character varying(160) NOT NULL
);


--
-- Name: schedule_assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_assignments (
    id bigint NOT NULL,
    schedule_version_id bigint NOT NULL,
    group_id bigint NOT NULL,
    project_id bigint NOT NULL,
    timeslot_id bigint NOT NULL,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    time_range tstzrange GENERATED ALWAYS AS (tstzrange(start_at, end_at, '[)'::text)) STORED,
    CONSTRAINT schedule_assignments_check CHECK ((end_at > start_at))
);


--
-- Name: schedule_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.schedule_assignments ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.schedule_assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schedule_change_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_change_records (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    schedule_version_id bigint NOT NULL,
    session_id bigint,
    actor_id bigint NOT NULL,
    reason text NOT NULL,
    before_json jsonb NOT NULL,
    after_json jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: schedule_change_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.schedule_change_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: schedule_change_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.schedule_change_records_id_seq OWNED BY public.schedule_change_records.id;


--
-- Name: schedule_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_versions (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    version_no integer NOT NULL,
    status public.schedule_version_status DEFAULT 'DRAFT'::public.schedule_version_status NOT NULL,
    input_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    algorithm_parameters jsonb DEFAULT '{}'::jsonb NOT NULL,
    random_seed bigint,
    solver_status character varying(32),
    total_score numeric,
    soft_scores jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    activated_at timestamp with time zone,
    CONSTRAINT schedule_versions_version_no_check CHECK ((version_no > 0))
);


--
-- Name: schedule_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.schedule_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: schedule_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.schedule_versions_id_seq OWNED BY public.schedule_versions.id;


--
-- Name: scheduler_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduler_jobs (
    id bigint NOT NULL,
    round_id bigint NOT NULL,
    status character varying(16) DEFAULT 'QUEUED'::character varying NOT NULL,
    attempt integer DEFAULT 1 NOT NULL,
    idempotency_key character varying(160),
    input_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    algorithm_parameters jsonb DEFAULT '{}'::jsonb NOT NULL,
    random_seed bigint NOT NULL,
    schedule_version_id bigint,
    error text,
    queued_at timestamp with time zone DEFAULT now() NOT NULL,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    CONSTRAINT scheduler_jobs_attempt_check CHECK ((attempt > 0)),
    CONSTRAINT scheduler_jobs_status_check CHECK (((status)::text = ANY ((ARRAY['QUEUED'::character varying, 'RUNNING'::character varying, 'COMPLETED'::character varying, 'PARTIAL'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: scheduler_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduler_jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduler_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduler_jobs_id_seq OWNED BY public.scheduler_jobs.id;


--
-- Name: schema_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_meta (
    key character varying(80) NOT NULL,
    value character varying(255) NOT NULL
);


--
-- Name: semester_lecturer_quotas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.semester_lecturer_quotas (
    semester_id bigint NOT NULL,
    lecturer_id bigint NOT NULL,
    quota integer NOT NULL,
    updated_by bigint,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT semester_lecturer_quotas_quota_check CHECK ((quota > 0))
);


--
-- Name: semesters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.semesters (
    id bigint NOT NULL,
    code character varying(32) NOT NULL,
    name character varying(160) NOT NULL,
    status public.semester_status DEFAULT 'ACTIVE'::public.semester_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    note text,
    academic_year character varying(9),
    created_by bigint,
    updated_by bigint,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_semesters_date_order CHECK ((end_date >= start_date))
);


--
-- Name: semesters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.semesters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: semesters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.semesters_id_seq OWNED BY public.semesters.id;


--
-- Name: session_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.session_results (
    id bigint NOT NULL,
    session_id bigint NOT NULL,
    outcome public.result_outcome NOT NULL,
    note text,
    entered_by bigint NOT NULL,
    entered_at timestamp with time zone DEFAULT now() NOT NULL,
    correction_reason text,
    before_json jsonb,
    after_json jsonb,
    remediation_due_at timestamp with time zone,
    verifier_lecturer_id bigint,
    verify_status public.verify_status DEFAULT 'PENDING'::public.verify_status NOT NULL,
    before_group_status public.group_status,
    after_group_status public.group_status
);


--
-- Name: session_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.session_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: session_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.session_results_id_seq OWNED BY public.session_results.id;


--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.students (
    id bigint NOT NULL,
    account_id bigint,
    student_code character varying(32) NOT NULL
);


--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.students_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: timeframe_break_windows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timeframe_break_windows (
    id bigint NOT NULL,
    timeframe_version_id bigint NOT NULL,
    sequence_number integer NOT NULL,
    name character varying(255) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    CONSTRAINT ck_timeframe_break_windows_range CHECK ((end_time > start_time)),
    CONSTRAINT ck_timeframe_break_windows_sequence CHECK ((sequence_number > 0))
);


--
-- Name: timeframe_break_windows_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.timeframe_break_windows ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.timeframe_break_windows_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: timeframe_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timeframe_versions (
    id bigint NOT NULL,
    timeframe_id bigint NOT NULL,
    version_number integer NOT NULL,
    status character varying(16) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    block_duration_minutes integer,
    group_duration_minutes integer NOT NULL,
    change_reason text,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    break_between_blocks_minutes integer DEFAULT 0 NOT NULL,
    manual_timelines jsonb,
    CONSTRAINT ck_timeframe_versions_block_break CHECK ((break_between_blocks_minutes >= 0)),
    CONSTRAINT ck_timeframe_versions_block_duration CHECK ((block_duration_minutes > 0)),
    CONSTRAINT ck_timeframe_versions_group_duration CHECK ((group_duration_minutes > 0)),
    CONSTRAINT ck_timeframe_versions_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'SUPERSEDED'::character varying])::text[]))),
    CONSTRAINT ck_timeframe_versions_time_range CHECK ((end_time > start_time))
);


--
-- Name: timeframe_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.timeframe_versions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.timeframe_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: timeframes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timeframes (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    kind character varying(32) NOT NULL,
    archived_at timestamp with time zone,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: timeframes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.timeframes ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.timeframes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: timeslots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timeslots (
    id bigint NOT NULL,
    round_day_id bigint NOT NULL,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    active boolean DEFAULT true NOT NULL,
    part character varying(8) DEFAULT 'AM'::character varying NOT NULL,
    CONSTRAINT timeslots_check CHECK ((end_at > start_at)),
    CONSTRAINT timeslots_part_check CHECK (((part)::text = ANY ((ARRAY['AM'::character varying, 'PM'::character varying])::text[])))
);


--
-- Name: timeslots_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.timeslots_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: timeslots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.timeslots_id_seq OWNED BY public.timeslots.id;


--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: audit_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_events ALTER COLUMN id SET DEFAULT nextval('public.audit_events_id_seq'::regclass);


--
-- Name: auth_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions ALTER COLUMN id SET DEFAULT nextval('public.auth_sessions_id_seq'::regclass);


--
-- Name: conflict_declarations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations ALTER COLUMN id SET DEFAULT nextval('public.conflict_declarations_id_seq'::regclass);


--
-- Name: councils id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.councils ALTER COLUMN id SET DEFAULT nextval('public.councils_id_seq'::regclass);


--
-- Name: excel_defense_councils id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_defense_councils ALTER COLUMN id SET DEFAULT nextval('public.excel_defense_councils_id_seq'::regclass);


--
-- Name: excel_import_batches id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_import_batches ALTER COLUMN id SET DEFAULT nextval('public.excel_import_batches_id_seq'::regclass);


--
-- Name: excel_projects id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects ALTER COLUMN id SET DEFAULT nextval('public.excel_projects_id_seq'::regclass);


--
-- Name: excel_review_schedule_rows id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows ALTER COLUMN id SET DEFAULT nextval('public.excel_review_schedule_rows_id_seq'::regclass);


--
-- Name: excel_sheet_rows id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_sheet_rows ALTER COLUMN id SET DEFAULT nextval('public.excel_sheet_rows_id_seq'::regclass);


--
-- Name: excel_summary_workloads id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_summary_workloads ALTER COLUMN id SET DEFAULT nextval('public.excel_summary_workloads_id_seq'::regclass);


--
-- Name: group_memberships id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships ALTER COLUMN id SET DEFAULT nextval('public.group_memberships_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: h11_waivers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers ALTER COLUMN id SET DEFAULT nextval('public.h11_waivers_id_seq'::regclass);


--
-- Name: lecturers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturers ALTER COLUMN id SET DEFAULT nextval('public.lecturers_id_seq'::regclass);


--
-- Name: majors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.majors ALTER COLUMN id SET DEFAULT nextval('public.majors_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: outbox_jobs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbox_jobs ALTER COLUMN id SET DEFAULT nextval('public.outbox_jobs_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: remediation_cases id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases ALTER COLUMN id SET DEFAULT nextval('public.remediation_cases_id_seq'::regclass);


--
-- Name: reschedule_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reschedule_requests ALTER COLUMN id SET DEFAULT nextval('public.reschedule_requests_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: round_days id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_days ALTER COLUMN id SET DEFAULT nextval('public.round_days_id_seq'::regclass);


--
-- Name: round_operation_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_operation_records ALTER COLUMN id SET DEFAULT nextval('public.round_operation_records_id_seq'::regclass);


--
-- Name: rounds id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds ALTER COLUMN id SET DEFAULT nextval('public.rounds_id_seq'::regclass);


--
-- Name: schedule_change_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records ALTER COLUMN id SET DEFAULT nextval('public.schedule_change_records_id_seq'::regclass);


--
-- Name: schedule_versions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_versions ALTER COLUMN id SET DEFAULT nextval('public.schedule_versions_id_seq'::regclass);


--
-- Name: scheduler_jobs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduler_jobs ALTER COLUMN id SET DEFAULT nextval('public.scheduler_jobs_id_seq'::regclass);


--
-- Name: semesters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semesters ALTER COLUMN id SET DEFAULT nextval('public.semesters_id_seq'::regclass);


--
-- Name: session_results id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results ALTER COLUMN id SET DEFAULT nextval('public.session_results_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: timeslots id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeslots ALTER COLUMN id SET DEFAULT nextval('public.timeslots_id_seq'::regclass);


--
-- Data for Name: account_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.account_roles (account_id, role) FROM stdin;
1	ADMIN
2	MANAGER
2103	LECTURER
32	STUDENT
3	LECTURER
4	LECTURER
5	LECTURER
6	LECTURER
7	LECTURER
8	LECTURER
9	LECTURER
10	LECTURER
11	LECTURER
12	LECTURER
13	LECTURER
14	LECTURER
15	LECTURER
16	LECTURER
17	LECTURER
18	LECTURER
19	LECTURER
20	LECTURER
21	LECTURER
22	LECTURER
23	LECTURER
24	LECTURER
25	LECTURER
26	LECTURER
27	LECTURER
28	LECTURER
1999	STUDENT
2000	STUDENT
2001	STUDENT
2002	STUDENT
2003	STUDENT
2004	STUDENT
2005	STUDENT
2006	STUDENT
2007	STUDENT
2008	STUDENT
2009	STUDENT
2010	STUDENT
2011	STUDENT
2012	STUDENT
2013	STUDENT
2014	STUDENT
2015	STUDENT
2016	STUDENT
2017	STUDENT
2018	STUDENT
2019	STUDENT
2020	STUDENT
2021	STUDENT
2022	STUDENT
2023	STUDENT
2024	STUDENT
2025	STUDENT
2026	STUDENT
2027	STUDENT
2028	STUDENT
2029	STUDENT
2030	STUDENT
2031	STUDENT
2032	STUDENT
2033	STUDENT
2034	STUDENT
2035	STUDENT
2036	STUDENT
2037	STUDENT
2038	STUDENT
2039	STUDENT
2040	STUDENT
2041	STUDENT
2042	STUDENT
2043	STUDENT
2044	STUDENT
2045	STUDENT
2046	STUDENT
2047	STUDENT
2048	STUDENT
2049	STUDENT
2050	STUDENT
2051	STUDENT
2052	STUDENT
2053	STUDENT
2054	STUDENT
2055	STUDENT
2056	STUDENT
2057	STUDENT
2058	STUDENT
2059	STUDENT
2060	STUDENT
2061	STUDENT
2062	STUDENT
2063	STUDENT
2064	STUDENT
2065	STUDENT
2066	STUDENT
2067	STUDENT
2068	STUDENT
2069	STUDENT
2070	STUDENT
2071	STUDENT
2072	STUDENT
2073	STUDENT
2074	STUDENT
2075	STUDENT
2076	STUDENT
2077	STUDENT
2078	STUDENT
2079	STUDENT
2080	STUDENT
2081	STUDENT
2082	STUDENT
2083	STUDENT
2084	STUDENT
2085	STUDENT
2086	STUDENT
2087	STUDENT
2088	STUDENT
2089	STUDENT
2090	STUDENT
2091	STUDENT
2092	STUDENT
2093	STUDENT
2094	STUDENT
2095	STUDENT
2096	STUDENT
2097	STUDENT
2098	STUDENT
2099	STUDENT
2100	STUDENT
\.


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts (id, email, display_name, password_hash, status, created_at) FROM stdin;
1	admin@gmail.com	Admin	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 03:57:14.256588+00
3	phuonglhk@fpt.edu.vn	Lâm Hữu Khánh Phương	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
4	ducdnm@fpt.edu.vn	Đặng Ngọc Minh Đức	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
2	manager@gmail.com	Manager	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 03:57:14.256588+00
5	vanttn@fpt.edu.vn	Thân Thị Ngọc Vân	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
2103	lecturer@gmail.com	Lecturer 1	$argon2id$v=19$m=65536,t=3,p=4$+I4ZH5dSuIunx9oFUBFfwg$y2xfd4n7Hl2eq3ws9JYJqEYbg17B44eRa9XVR1cRZN8	ACTIVE	2026-08-22 10:10:03.650475+00
6	tampm@fpt.edu.vn	Phan Minh Tâm	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
7	nhandt@fpt.edu.vn	Đỗ Tấn Nhàn	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
8	phucnt@fpt.edu.vn	Nguyễn Tấn Phúc	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
9	sangnm@fpt.edu.vn	Nguyễn Minh Sang	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
10	hoangnt@fpt.edu.vn	Nguyễn Thế Hoàng	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
2006	student.se160929@fpt.edu.vn	Lê Quang Minh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2007	student.se161100@fpt.edu.vn	Bùi Đình Trọng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2008	student.se170167@fpt.edu.vn	Trần Gia Huy	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2009	student.se170183@fpt.edu.vn	Thái Công Đạt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2010	student.se170238@fpt.edu.vn	Nguyễn Minh Toàn	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2011	student.se170310@fpt.edu.vn	Nguyễn Nhật Minh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2012	student.se171339@fpt.edu.vn	Cù Thanh Thảo	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2013	student.se171719@fpt.edu.vn	Trần Đông Thạnh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2014	student.se171754@fpt.edu.vn	Trương Phạm Quỳnh Hoa	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2015	student.se171793@fpt.edu.vn	Hà Văn Phước	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2016	student.se172336@fpt.edu.vn	Trần Lạc Hồng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2017	student.se172340@fpt.edu.vn	Nguyễn Hoàng Long	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2018	student.se172384@fpt.edu.vn	Nguyễn Hoàng Ngọc Sơn	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2019	student.se172459@fpt.edu.vn	Lê Hoàng Lộc	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2020	student.se172478@fpt.edu.vn	Hoàng Trọng Khang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2021	student.se172485@fpt.edu.vn	Trương Hoàng Anh Vũ	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2022	student.se172486@fpt.edu.vn	Đoàn Mạnh Hiệp	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
11	longt@fpt.edu.vn	Trương Long	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
12	taint@fpt.edu.vn	Nguyễn Trọng Tài	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
13	lamnn@fpt.edu.vn	Nguyễn Ngọc Lâm	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
14	thongnt@fpt.edu.vn	Nguyễn Trí Thông	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
15	anndh@fpt.edu.vn	Ngô Đăng Hà An	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
16	duongvtt@fpt.edu.vn	Vũ Thị Thùy Dương	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
17	hungld@fpt.edu.vn	Lại Đức Hùng	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
18	nguyentt@fpt.edu.vn	Trần Thanh Nguyên	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
19	khanhkt@fpt.edu.vn	Kiều Trọng Khánh	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
20	huongntc@fpt.edu.vn	Nguyễn Thị Cẩm Hương	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
21	minhtth@fpt.edu.vn	Tôn Thất Hoàng Minh	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
22	thinhdp@fpt.edu.vn	Đỗ Phúc Thịnh	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
23	quynhtnn@fpt.edu.vn	Trần Ngọc Như Quỳnh	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
24	tript@fpt.edu.vn	Phạm Thanh Trí	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
25	chiltq@fpt.edu.vn	Lê Thị Quỳnh Chi	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
26	vulns@fpt.edu.vn	Lê Nguyễn Sơn Vũ	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
27	tripm@fpt.edu.vn	Phạm Minh Trí	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
28	huynx@fpt.edu.vn	Nguyễn Xuân Huy	$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y	ACTIVE	2026-08-22 07:49:29.170388+00
32	student1@gmail.com	Student 1	$argon2id$v=19$m=65536,t=3,p=4$LrmJZJKfKbcSOmue5usU1Q$hLKiGrWvONQb42SF5SioxK0zb+alCZOg77Mq9QBsiWY	ACTIVE	2026-08-22 07:56:01.318366+00
1999	student.de180732@fpt.edu.vn	Trần Nguyễn Duy Thông	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2000	student.qe180159@fpt.edu.vn	Lê Thị Hải Hà	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2001	student.se150831@fpt.edu.vn	Đỗ Thái Gia Khang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2002	student.se150863@fpt.edu.vn	Chu Tuấn Kiệt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2003	student.se151214@fpt.edu.vn	Hoàng Kim Phú	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2004	student.se151518@fpt.edu.vn	Trần Hoàng Tuấn	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2005	student.se160590@fpt.edu.vn	Nguyễn Trọng Tiến	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2023	student.se172575@fpt.edu.vn	Thái Tấn Tiến	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2024	student.se172634@fpt.edu.vn	Võ Văn Phúc Ân	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2025	student.se172870@fpt.edu.vn	Cao Hoàng Minh Trí	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2026	student.se173374@fpt.edu.vn	Võ Nhật Hưng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2027	student.se180305@fpt.edu.vn	Nguyễn Kỳ Vỹ	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2028	student.se180445@fpt.edu.vn	Bùi Phước Thắng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2029	student.se180473@fpt.edu.vn	Lê Đức Trí	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2030	student.se180486@fpt.edu.vn	Trần Phạm Thảo Nguyên	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2031	student.se180491@fpt.edu.vn	Trần Thị Thanh Trang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2032	student.se180500@fpt.edu.vn	Trần Gia Kiệt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2033	student.se180536@fpt.edu.vn	Hà Huy Nghĩa Hiệp	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2034	student.se180543@fpt.edu.vn	Hoàng Gia Phong	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2035	student.se180564@fpt.edu.vn	Bùi Minh Thắng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2036	student.se180573@fpt.edu.vn	Phan Quới An Phú	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2037	student.se180619@fpt.edu.vn	Nguyễn Anh Quân	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2038	student.se180717@fpt.edu.vn	Khuất Trường Huy	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2039	student.se181554@fpt.edu.vn	Nguyễn Thái Ngọc Nguyên	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2040	student.se181766@fpt.edu.vn	Nguyễn Nhật Quang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2041	student.se182019@fpt.edu.vn	Trần Việt Anh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2042	student.se182085@fpt.edu.vn	Lê Hữu Thông	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2043	student.se182115@fpt.edu.vn	Lê Quang Vinh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2044	student.se182172@fpt.edu.vn	Lê Thành Đạt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2045	student.se182227@fpt.edu.vn	Mạc Anh Hào	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2046	student.se182273@fpt.edu.vn	Ngô Phan Thành Công	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2047	student.se182281@fpt.edu.vn	Dương Hoàng Long	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2048	student.se182294@fpt.edu.vn	Phạm Ngọc Trung Nhân	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2049	student.se182311@fpt.edu.vn	Nguyễn Khang Bình	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2050	student.se182333@fpt.edu.vn	Nguyễn Như Thành	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2051	student.se182453@fpt.edu.vn	Lê Tiến Đạt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2052	student.se182463@fpt.edu.vn	Bùi Bá Cường	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2053	student.se182529@fpt.edu.vn	Đái Võ Ngọc Duy Khánh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2054	student.se182535@fpt.edu.vn	Đỗ Quốc Huy	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2055	student.se182547@fpt.edu.vn	Lê Minh Đức	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2056	student.se182548@fpt.edu.vn	Nguyễn Quốc Việt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2057	student.se182829@fpt.edu.vn	Lý Thế Vinh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2058	student.se182871@fpt.edu.vn	Nguyễn Minh Nam	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2059	student.se182945@fpt.edu.vn	Phan Thành Tú	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2060	student.se182998@fpt.edu.vn	Trần Quang Thuận	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2061	student.se183054@fpt.edu.vn	Đoàn Lê Thành Trung	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2062	student.se183109@fpt.edu.vn	Trần Minh Trí	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2063	student.se183153@fpt.edu.vn	Lương Nguyễn Xuân Minh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2064	student.se183522@fpt.edu.vn	Hoàng Đăng Khoa	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2065	student.se183609@fpt.edu.vn	Nguyễn Trung Hiền	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2066	student.se183632@fpt.edu.vn	Phạm Phương Minh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2067	student.se183642@fpt.edu.vn	Đỗ Trường Thịnh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2068	student.se183662@fpt.edu.vn	Nguyễn Trường Giang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2069	student.se183665@fpt.edu.vn	Nguyễn Phạm Công Hậu	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2070	student.se183725@fpt.edu.vn	Nguyễn Đình Đăng Khoa	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2071	student.se183727@fpt.edu.vn	Trần Hoàng Định	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2072	student.se183732@fpt.edu.vn	Đỗ Văn Thắng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2073	student.se183923@fpt.edu.vn	Mai Hồng Thái	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2074	student.se183965@fpt.edu.vn	Trần Nguyễn Việt Thành	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2075	student.se184090@fpt.edu.vn	Hoàng Xuân Hiệp	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2076	student.se184091@fpt.edu.vn	Đặng Nguyễn Gia Bảo	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2077	student.se184191@fpt.edu.vn	Trần Lê Sĩ Quỳnh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2078	student.se184214@fpt.edu.vn	Trần Chấn Quang Thiên	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2079	student.se184261@fpt.edu.vn	Nguyễn Phạm Thu Hà	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2080	student.se184306@fpt.edu.vn	Cung Nguyễn Bích Trâm	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2081	student.se184322@fpt.edu.vn	Lê Hoàng Việt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2082	student.se184339@fpt.edu.vn	Nguyễn Minh Thuận	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2083	student.se184354@fpt.edu.vn	Lương Hồng Mỹ	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2084	student.se184359@fpt.edu.vn	Trần Lê Nhật Viễn	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2085	student.se184402@fpt.edu.vn	Trần Vũ Quốc Đại	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2086	student.se184438@fpt.edu.vn	Dương Minh Nhật	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2087	student.se184443@fpt.edu.vn	Nguyễn Đức Hoàng	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2088	student.se184453@fpt.edu.vn	Đặng Thành Danh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2089	student.se184458@fpt.edu.vn	Phạm Quốc Thái	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2090	student.se184492@fpt.edu.vn	Nguyễn Đức Thịnh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2091	student.se184565@fpt.edu.vn	Ngô Bằng Giang	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2092	student.se184569@fpt.edu.vn	Lê Trương Thiên Bảo	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2093	student.se184622@fpt.edu.vn	Trịnh Hải Đức	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2094	student.se184629@fpt.edu.vn	Hỷ Minh Phát	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2095	student.se184638@fpt.edu.vn	Lê Tuấn Khanh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2096	student.se184767@fpt.edu.vn	Nguyễn Bùi Hoàng Phúc	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2097	student.se184821@fpt.edu.vn	Nguyễn Phúc Duy	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2098	student.se184940@fpt.edu.vn	Phạm Văn Học	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2099	student.se185063@fpt.edu.vn	Trương Tuấn Kiệt	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
2100	student.ss170152@fpt.edu.vn	Nguyễn Thị Như Quỳnh	$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4	ACTIVE	2026-08-22 09:08:50.914141+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
0038_project_bilingual_titles
\.


--
-- Data for Name: audit_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_events (id, actor_id, action, entity_type, entity_id, reason, before_json, after_json, occurred_at) FROM stdin;
1	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 07:55:17.263729+00
2	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:01.318366+00
3	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 07:56:01.944819+00
4	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 07:56:02.230838+00
5	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:02.498701+00
6	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 07:56:05.444136+00
7	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 07:56:05.876292+00
8	\N	TEST	test	c09aa75f4d4541bcb2047963f1b5c516	\N	\N	\N	2026-08-22 07:56:07.272883+00
9	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:10.029045+00
10	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:11.108905+00
11	32	AVAILABILITY_ENTERED	group_availability	3:5	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 07:56:11.319209+00
12	32	AVAILABILITY_ENTERED	group_availability	3:5	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 07:56:11.366091+00
13	32	AVAILABILITY_ENTERED	group_availability	3:5	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 07:56:11.402141+00
14	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:11.813041+00
15	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 07:56:12.39016+00
16	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:12.70443+00
17	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 07:56:13.002488+00
18	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:13.692971+00
19	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:16.34713+00
20	2	SEMESTER_CREATED	semester	9	\N	\N	{"code": "API-34EFEA76", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 07:56:16.605722+00
21	2	SEMESTER_SET_CURRENT	semester	9	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:16.657769+00
22	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 07:56:16.657769+00
23	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:17.085216+00
24	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:17.2518+00
25	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:17.556162+00
26	2	SEMESTER_CREATED	semester	13	\N	\N	{"code": "DURATION-F13B59FE", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 07:56:17.573411+00
27	2	SEMESTER_STATUS_CHANGED	semester	13	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:17.595333+00
28	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 07:56:17.613018+00
29	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:18.575306+00
30	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:18.854444+00
31	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:19.128638+00
32	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:19.401856+00
33	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:20.108142+00
34	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:20.417993+00
35	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:20.667858+00
36	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:24.111651+00
37	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:24.451752+00
38	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:24.750014+00
39	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:25.051043+00
40	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:26.476235+00
41	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:28.895444+00
42	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:29.201633+00
43	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:31.972691+00
44	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:33.975158+00
45	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:35.099205+00
46	1	ACCOUNT_CREATED	account	175	\N	\N	{"role": "MANAGER", "email": "operator-1c591b0e@example.test"}	2026-08-22 07:56:35.295288+00
47	1	ACCOUNT_STATUS_CHANGED	account	175	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 07:56:35.357015+00
48	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:35.737201+00
49	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:36.090044+00
50	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:38.914233+00
51	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:39.630099+00
52	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:42.553495+00
53	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:42.784323+00
54	2	ROUND_TRANSITION	round	4	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 07:56:43.021734+00
55	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:43.237708+00
56	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:44.133739+00
57	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:45.628974+00
58	2	ROUND_COMMITTEES_REPLACED	round	5	\N	\N	{"committee_ids": [4, 5]}	2026-08-22 07:56:45.670704+00
59	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:46.016676+00
60	2	ROUND_COMMITTEES_REPLACED	round	6	\N	\N	{"committee_ids": [7]}	2026-08-22 07:56:46.045837+00
61	2	ROUND_COMMITTEES_REPLACED	round	6	\N	\N	{"committee_ids": []}	2026-08-22 07:56:46.0682+00
62	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:46.386965+00
63	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:46.759608+00
64	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:47.543095+00
65	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:47.859949+00
66	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 07:56:48.174902+00
67	2	ROUND_COMMITTEES_REPLACED	round	12	\N	\N	{"committee_ids": [22]}	2026-08-22 07:56:48.199364+00
68	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:48.778017+00
69	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 07:56:49.233605+00
70	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:49.629434+00
71	2	SEMESTER_CREATED	semester	41	\N	\N	{"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 07:56:49.640504+00
72	2	SEMESTER_UPDATED	semester	41	\N	{"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 07:56:49.745753+00
73	2	SEMESTER_SET_CURRENT	semester	41	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 07:56:49.762322+00
74	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 07:56:49.762322+00
75	2	TIMEFRAME_MANUAL_CREATED	timeframe	1	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 07:56:52.862334+00
76	2	TIMEFRAME_MANUAL_UPDATED	timeframe	1	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 07:56:52.89813+00
77	2	TIMEFRAME_CREATED	timeframe	2	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 07:56:53.129239+00
78	2	TIMEFRAME_UPDATED	timeframe	2	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 07:56:53.167011+00
79	2	TIMEFRAME_ARCHIVED	timeframe	2	Archive test template	\N	{"archived": true}	2026-08-22 07:56:53.190431+00
80	2	TIMEFRAME_CREATED	timeframe	3	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 07:56:53.607532+00
81	2	ROUND_CREATED	round	14	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 3, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 5, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 07:56:53.632485+00
82	2	TIMEFRAME_UPDATED	timeframe	3	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 07:56:53.691487+00
83	2	TIMEFRAME_MANUAL_CREATED	timeframe	4	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 07:56:53.946295+00
84	2	ROUND_CREATED	round	15	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 4, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 7, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 07:56:53.976116+00
85	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:06.87455+00
86	2	ROUND_COMMITTEES_REPLACED	round	16	\N	\N	{"committee_ids": [25, 26]}	2026-08-22 08:05:06.922249+00
87	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:07.620358+00
88	2	ROUND_COMMITTEES_REPLACED	round	17	\N	\N	{"committee_ids": [28]}	2026-08-22 08:05:07.648443+00
89	2	ROUND_COMMITTEES_REPLACED	round	17	\N	\N	{"committee_ids": []}	2026-08-22 08:05:07.674908+00
90	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:08.391929+00
91	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:08.767046+00
92	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:09.713221+00
93	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:10.124146+00
94	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:10.501363+00
95	2	ROUND_COMMITTEES_REPLACED	round	23	\N	\N	{"committee_ids": [43]}	2026-08-22 08:05:10.542984+00
96	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:05:10.950413+00
97	2	ROUND_COMMITTEES_REPLACED	round	24	\N	\N	{"committee_ids": [46]}	2026-08-22 08:05:10.982471+00
98	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:40.762632+00
99	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:05:41.058063+00
100	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:05:41.276647+00
101	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:41.499107+00
102	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:05:43.473572+00
103	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:05:43.770199+00
104	\N	TEST	test	389bced1c7cc433ba1cef5bf7ec297d1	\N	\N	\N	2026-08-22 08:05:44.89428+00
105	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:47.07456+00
106	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:47.607878+00
107	32	AVAILABILITY_ENTERED	group_availability	27:10	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:05:47.787094+00
108	32	AVAILABILITY_ENTERED	group_availability	27:10	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:05:47.81165+00
109	32	AVAILABILITY_ENTERED	group_availability	27:10	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:05:47.831135+00
110	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:48.034567+00
111	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:05:48.369744+00
112	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:48.584116+00
113	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:05:48.758297+00
114	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:49.000781+00
115	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:05:53.342039+00
116	2	SEMESTER_CREATED	semester	51	\N	\N	{"code": "API-8B1E0622", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:05:53.367899+00
117	2	SEMESTER_SET_CURRENT	semester	51	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:05:53.415286+00
118	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:05:53.415286+00
119	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:53.610059+00
120	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:53.704068+00
121	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:05:53.88907+00
122	2	SEMESTER_CREATED	semester	55	\N	\N	{"code": "DURATION-F3238129", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:05:53.905758+00
123	2	SEMESTER_STATUS_CHANGED	semester	55	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:05:53.922999+00
124	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:05:53.939125+00
125	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:54.486428+00
126	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:54.723902+00
127	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:54.926089+00
128	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:55.133227+00
129	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:55.595839+00
130	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:55.806204+00
131	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:56.005936+00
132	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:58.850132+00
133	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:59.025352+00
134	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:59.213124+00
135	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:59.410942+00
136	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:59.60737+00
137	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:05:59.816472+00
138	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:00.048063+00
139	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:01.837158+00
140	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:02.996603+00
141	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:03.504612+00
142	1	ACCOUNT_CREATED	account	437	\N	\N	{"role": "MANAGER", "email": "operator-788da04a@example.test"}	2026-08-22 08:06:03.602805+00
143	1	ACCOUNT_STATUS_CHANGED	account	437	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:06:03.640564+00
144	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:03.804454+00
145	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:04.074126+00
146	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:05.500239+00
147	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:05.976343+00
148	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:08.042121+00
149	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:08.294862+00
150	2	ROUND_TRANSITION	round	28	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:06:08.487397+00
151	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:08.667863+00
152	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:09.467344+00
153	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:10.495656+00
154	2	ROUND_COMMITTEES_REPLACED	round	29	\N	\N	{"committee_ids": [52, 53]}	2026-08-22 08:06:10.533205+00
155	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:10.840276+00
156	2	ROUND_COMMITTEES_REPLACED	round	30	\N	\N	{"committee_ids": [55]}	2026-08-22 08:06:10.867511+00
157	2	ROUND_COMMITTEES_REPLACED	round	30	\N	\N	{"committee_ids": []}	2026-08-22 08:06:10.88809+00
158	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:11.153948+00
159	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:11.472064+00
160	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:12.011263+00
161	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:12.283806+00
162	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:12.61349+00
163	2	ROUND_COMMITTEES_REPLACED	round	36	\N	\N	{"committee_ids": [70]}	2026-08-22 08:06:12.645516+00
164	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:06:12.956966+00
165	2	ROUND_COMMITTEES_REPLACED	round	37	\N	\N	{"committee_ids": [73]}	2026-08-22 08:06:12.979596+00
166	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:13.544868+00
167	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:13.901599+00
168	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:14.109564+00
169	2	SEMESTER_CREATED	semester	83	\N	\N	{"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:06:14.126287+00
170	2	SEMESTER_UPDATED	semester	83	\N	{"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:06:14.286774+00
171	2	SEMESTER_SET_CURRENT	semester	83	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:14.311131+00
172	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:06:14.311131+00
173	2	TIMEFRAME_MANUAL_CREATED	timeframe	5	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:06:17.167404+00
174	2	TIMEFRAME_MANUAL_UPDATED	timeframe	5	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:06:17.196605+00
175	2	TIMEFRAME_CREATED	timeframe	6	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:06:17.562943+00
176	2	TIMEFRAME_UPDATED	timeframe	6	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:06:17.612376+00
177	2	TIMEFRAME_ARCHIVED	timeframe	6	Archive test template	\N	{"archived": true}	2026-08-22 08:06:17.636307+00
178	2	TIMEFRAME_CREATED	timeframe	7	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:06:17.894105+00
179	2	ROUND_CREATED	round	39	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 7, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 12, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:06:17.917097+00
180	2	TIMEFRAME_UPDATED	timeframe	7	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:06:17.963681+00
181	2	TIMEFRAME_MANUAL_CREATED	timeframe	8	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:06:18.246396+00
182	2	ROUND_CREATED	round	40	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 8, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 14, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:06:18.265339+00
183	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:29.362406+00
184	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:06:29.669389+00
185	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:06:29.863963+00
186	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:30.074558+00
187	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:06:32.110324+00
188	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:06:32.408804+00
189	\N	TEST	test	985085f935124ca4938e7f43f735d9dc	\N	\N	\N	2026-08-22 08:06:33.238343+00
190	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:35.144254+00
191	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:35.717898+00
192	32	AVAILABILITY_ENTERED	group_availability	43:15	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:06:35.900206+00
193	32	AVAILABILITY_ENTERED	group_availability	43:15	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:06:35.92043+00
194	32	AVAILABILITY_ENTERED	group_availability	43:15	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:06:35.939977+00
195	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:36.134583+00
196	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:06:36.539711+00
197	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:36.729531+00
198	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:06:36.902782+00
199	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:37.16493+00
200	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:38.530693+00
201	2	SEMESTER_CREATED	semester	93	\N	\N	{"code": "API-2B1264C3", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:06:38.548264+00
202	2	SEMESTER_SET_CURRENT	semester	93	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:38.587156+00
203	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:06:38.587156+00
204	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:38.785784+00
205	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:38.899201+00
206	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:39.235669+00
207	2	SEMESTER_CREATED	semester	97	\N	\N	{"code": "DURATION-C7D7D89A", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:06:39.253491+00
208	2	SEMESTER_STATUS_CHANGED	semester	97	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:06:39.275784+00
209	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:06:39.290746+00
210	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:39.885601+00
211	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:40.120556+00
212	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:40.366326+00
213	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:40.583241+00
214	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:41.112146+00
215	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:41.340941+00
216	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:41.535392+00
217	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:44.100691+00
218	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:44.319313+00
219	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:44.535407+00
220	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:44.746474+00
221	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:44.933849+00
222	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:45.129686+00
223	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:45.350351+00
224	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:47.255144+00
225	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:48.677458+00
226	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:49.164303+00
227	1	ACCOUNT_CREATED	account	664	\N	\N	{"role": "MANAGER", "email": "operator-da2ccb54@example.test"}	2026-08-22 08:06:49.284741+00
228	1	ACCOUNT_STATUS_CHANGED	account	664	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:06:49.317251+00
229	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:49.48831+00
230	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:49.704718+00
231	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:51.001361+00
232	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:51.493988+00
233	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:54.167227+00
234	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:54.413404+00
235	2	ROUND_TRANSITION	round	44	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:06:54.637559+00
236	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:54.816646+00
237	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:06:57.069918+00
238	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:00.762003+00
239	2	ROUND_COMMITTEES_REPLACED	round	45	\N	\N	{"committee_ids": [79, 80]}	2026-08-22 08:07:00.794644+00
240	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:01.099901+00
241	2	ROUND_COMMITTEES_REPLACED	round	46	\N	\N	{"committee_ids": [82]}	2026-08-22 08:07:01.124847+00
242	2	ROUND_COMMITTEES_REPLACED	round	46	\N	\N	{"committee_ids": []}	2026-08-22 08:07:01.144602+00
243	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:01.42112+00
244	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:01.717939+00
245	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:02.59051+00
246	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:02.864412+00
247	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:03.143198+00
248	2	ROUND_COMMITTEES_REPLACED	round	52	\N	\N	{"committee_ids": [97]}	2026-08-22 08:07:03.168161+00
249	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:07:03.537506+00
250	2	ROUND_COMMITTEES_REPLACED	round	53	\N	\N	{"committee_ids": [100]}	2026-08-22 08:07:03.572142+00
251	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:07:04.262606+00
252	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:07:05.181526+00
253	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:07:05.499165+00
254	2	SEMESTER_CREATED	semester	125	\N	\N	{"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:07:05.51429+00
255	2	SEMESTER_UPDATED	semester	125	\N	{"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:07:05.639768+00
256	2	SEMESTER_SET_CURRENT	semester	125	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:07:05.659861+00
257	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:07:05.659861+00
258	2	TIMEFRAME_MANUAL_CREATED	timeframe	9	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:07:08.910634+00
259	2	TIMEFRAME_MANUAL_UPDATED	timeframe	9	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:07:08.943396+00
260	2	TIMEFRAME_CREATED	timeframe	10	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:07:09.388303+00
261	2	TIMEFRAME_UPDATED	timeframe	10	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:07:09.433295+00
262	2	TIMEFRAME_ARCHIVED	timeframe	10	Archive test template	\N	{"archived": true}	2026-08-22 08:07:09.460538+00
263	2	TIMEFRAME_CREATED	timeframe	11	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:07:09.734242+00
264	2	ROUND_CREATED	round	55	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 11, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 19, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:07:09.761204+00
265	2	TIMEFRAME_UPDATED	timeframe	11	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:07:09.823568+00
266	2	TIMEFRAME_MANUAL_CREATED	timeframe	12	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:07:10.009344+00
267	2	ROUND_CREATED	round	56	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 12, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 21, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:07:10.026011+00
268	\N	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:09:59.668017+00
269	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:12.721349+00
270	2	ROUND_COMMITTEES_REPLACED	round	57	\N	\N	{"committee_ids": [103, 104]}	2026-08-22 08:10:12.77894+00
271	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:13.17133+00
272	2	ROUND_COMMITTEES_REPLACED	round	58	\N	\N	{"committee_ids": [106]}	2026-08-22 08:10:13.199279+00
273	2	ROUND_COMMITTEES_REPLACED	round	58	\N	\N	{"committee_ids": []}	2026-08-22 08:10:13.224065+00
274	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:13.652528+00
275	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:14.014474+00
276	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:14.797822+00
277	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:16.178534+00
278	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:18.529593+00
279	2	ROUND_COMMITTEES_REPLACED	round	64	\N	\N	{"committee_ids": [121]}	2026-08-22 08:10:18.558521+00
280	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:18.895548+00
281	2	ROUND_COMMITTEES_REPLACED	round	65	\N	\N	{"committee_ids": [124]}	2026-08-22 08:10:18.949237+00
282	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:10:19.388551+00
283	2	ROUND_COMMITTEES_REPLACED	round	66	\N	\N	{"committee_ids": [127]}	2026-08-22 08:10:19.412057+00
284	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:51.155727+00
285	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:12:51.440205+00
286	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:12:51.610617+00
287	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:51.795475+00
288	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:12:54.000256+00
289	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:12:54.297597+00
290	\N	TEST	test	d1f78fe833044563ac1b0fa304453d2f	\N	\N	\N	2026-08-22 08:12:55.332511+00
291	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:57.213585+00
292	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:57.836829+00
293	32	AVAILABILITY_ENTERED	group_availability	69:20	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:12:58.05847+00
294	32	AVAILABILITY_ENTERED	group_availability	69:20	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:12:58.087284+00
295	32	AVAILABILITY_ENTERED	group_availability	69:20	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:12:58.116999+00
296	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:58.369013+00
297	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:12:58.88311+00
298	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:12:59.27422+00
299	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:12:59.621597+00
300	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:00.029502+00
301	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:04.668511+00
302	2	SEMESTER_CREATED	semester	136	\N	\N	{"code": "API-A874680A", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:13:04.698839+00
303	2	SEMESTER_SET_CURRENT	semester	136	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:04.748585+00
304	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:13:04.748585+00
305	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:04.980189+00
306	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:05.111645+00
307	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:05.454918+00
308	2	SEMESTER_CREATED	semester	140	\N	\N	{"code": "DURATION-A5A229BE", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:13:05.478769+00
309	2	SEMESTER_STATUS_CHANGED	semester	140	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:05.508999+00
310	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:13:05.526204+00
311	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:06.019796+00
312	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:06.226721+00
313	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:06.433593+00
314	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:06.640945+00
315	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:07.131207+00
316	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:07.335596+00
317	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:07.539362+00
318	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:10.040275+00
319	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:10.294591+00
320	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:10.495238+00
321	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:10.692058+00
322	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:10.912334+00
323	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:11.110464+00
324	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:11.308884+00
325	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:13.433431+00
326	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:14.929776+00
327	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:15.432192+00
328	1	ACCOUNT_CREATED	account	940	\N	\N	{"role": "MANAGER", "email": "operator-e2f2b036@example.test"}	2026-08-22 08:13:15.533961+00
329	1	ACCOUNT_STATUS_CHANGED	account	940	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:13:15.572342+00
330	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:15.787451+00
331	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:15.999906+00
332	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:17.467912+00
333	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:17.972088+00
334	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:20.826598+00
335	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:21.184606+00
336	2	ROUND_TRANSITION	round	70	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:13:21.478112+00
337	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:21.781718+00
338	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:22.637479+00
339	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:23.697001+00
340	2	ROUND_COMMITTEES_REPLACED	round	71	\N	\N	{"committee_ids": [133, 134]}	2026-08-22 08:13:23.728727+00
341	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:24.03022+00
342	2	ROUND_COMMITTEES_REPLACED	round	72	\N	\N	{"committee_ids": [136]}	2026-08-22 08:13:24.053391+00
343	2	ROUND_COMMITTEES_REPLACED	round	72	\N	\N	{"committee_ids": []}	2026-08-22 08:13:24.068399+00
344	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:24.344749+00
345	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:24.715589+00
346	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:25.408045+00
347	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:25.661081+00
348	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:25.976972+00
349	2	ROUND_COMMITTEES_REPLACED	round	78	\N	\N	{"committee_ids": [151]}	2026-08-22 08:13:25.999277+00
350	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:26.290078+00
351	2	ROUND_COMMITTEES_REPLACED	round	79	\N	\N	{"committee_ids": [154]}	2026-08-22 08:13:26.330792+00
352	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:13:26.767619+00
353	2	ROUND_COMMITTEES_REPLACED	round	80	\N	\N	{"committee_ids": [157]}	2026-08-22 08:13:26.808754+00
354	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:27.327815+00
355	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:27.765709+00
356	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:28.04823+00
420	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:12.567322+00
357	2	SEMESTER_CREATED	semester	168	\N	\N	{"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:13:28.068888+00
358	2	SEMESTER_UPDATED	semester	168	\N	{"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:13:28.190505+00
359	2	SEMESTER_SET_CURRENT	semester	168	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:28.213853+00
360	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:13:28.213853+00
361	2	TIMEFRAME_MANUAL_CREATED	timeframe	13	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:13:31.651346+00
362	2	TIMEFRAME_MANUAL_UPDATED	timeframe	13	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:13:31.695382+00
363	2	TIMEFRAME_CREATED	timeframe	14	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:13:31.944857+00
364	2	TIMEFRAME_UPDATED	timeframe	14	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:13:31.99817+00
365	2	TIMEFRAME_ARCHIVED	timeframe	14	Archive test template	\N	{"archived": true}	2026-08-22 08:13:32.030616+00
366	2	TIMEFRAME_CREATED	timeframe	15	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:13:32.3675+00
367	2	ROUND_CREATED	round	82	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 15, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 26, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:13:32.398298+00
368	2	TIMEFRAME_UPDATED	timeframe	15	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:13:32.465541+00
369	2	TIMEFRAME_MANUAL_CREATED	timeframe	16	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:13:32.702614+00
370	2	ROUND_CREATED	round	83	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 16, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 28, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:13:32.720203+00
371	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:48.424848+00
372	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:13:48.621395+00
373	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:13:48.777071+00
374	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:48.941548+00
375	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:13:50.827225+00
376	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:13:51.115389+00
377	\N	TEST	test	19bb5d32157447b69bc9751e43db55d5	\N	\N	\N	2026-08-22 08:13:52.110046+00
378	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:53.905154+00
379	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:54.413695+00
380	32	AVAILABILITY_ENTERED	group_availability	86:25	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:13:54.56546+00
381	32	AVAILABILITY_ENTERED	group_availability	86:25	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:13:54.590975+00
382	32	AVAILABILITY_ENTERED	group_availability	86:25	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:13:54.615775+00
383	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:54.819133+00
384	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:13:55.146128+00
385	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:55.306905+00
386	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:13:55.447162+00
387	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:55.689503+00
388	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:56.867829+00
389	2	SEMESTER_CREATED	semester	178	\N	\N	{"code": "API-E26FDB4E", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:13:56.894098+00
390	2	SEMESTER_SET_CURRENT	semester	178	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:56.941776+00
391	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:13:56.941776+00
392	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:57.133937+00
393	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:57.241424+00
394	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:57.415837+00
395	2	SEMESTER_CREATED	semester	182	\N	\N	{"code": "DURATION-1D03C342", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:13:57.43494+00
396	2	SEMESTER_STATUS_CHANGED	semester	182	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:13:57.455119+00
397	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:13:57.471561+00
398	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:57.968756+00
399	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:58.209967+00
400	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:58.418368+00
401	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:58.617932+00
402	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:59.081949+00
403	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:59.282117+00
404	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:13:59.46967+00
405	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:01.91765+00
406	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:02.203146+00
407	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:02.447326+00
408	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:02.768069+00
409	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:03.115858+00
410	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:03.369268+00
411	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:03.561084+00
412	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:05.329413+00
413	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:06.683555+00
414	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:08.087633+00
415	1	ACCOUNT_CREATED	account	1172	\N	\N	{"role": "MANAGER", "email": "operator-c971018d@example.test"}	2026-08-22 08:14:10.194557+00
416	1	ACCOUNT_STATUS_CHANGED	account	1172	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:14:10.227485+00
417	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:10.417383+00
418	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:10.620582+00
419	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:12.028479+00
421	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:14.774323+00
422	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:14.988315+00
423	2	ROUND_TRANSITION	round	87	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:14:15.155229+00
424	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:15.328225+00
425	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:16.030545+00
426	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:17.048181+00
427	2	ROUND_COMMITTEES_REPLACED	round	88	\N	\N	{"committee_ids": [163, 164]}	2026-08-22 08:14:17.081248+00
428	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:17.347043+00
429	2	ROUND_COMMITTEES_REPLACED	round	89	\N	\N	{"committee_ids": [166]}	2026-08-22 08:14:17.369408+00
430	2	ROUND_COMMITTEES_REPLACED	round	89	\N	\N	{"committee_ids": []}	2026-08-22 08:14:17.3866+00
431	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:17.603539+00
432	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:17.90991+00
433	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:18.541005+00
434	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:18.815456+00
435	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:19.06264+00
436	2	ROUND_COMMITTEES_REPLACED	round	95	\N	\N	{"committee_ids": [181]}	2026-08-22 08:14:19.089002+00
437	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:19.389634+00
438	2	ROUND_COMMITTEES_REPLACED	round	96	\N	\N	{"committee_ids": [184]}	2026-08-22 08:14:19.435103+00
439	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:14:19.920317+00
440	2	ROUND_COMMITTEES_REPLACED	round	97	\N	\N	{"committee_ids": [187]}	2026-08-22 08:14:19.949112+00
441	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:20.387269+00
442	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:20.789064+00
443	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:20.993591+00
444	2	SEMESTER_CREATED	semester	210	\N	\N	{"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:14:21.005838+00
445	2	SEMESTER_UPDATED	semester	210	\N	{"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:14:21.119037+00
446	2	SEMESTER_SET_CURRENT	semester	210	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:21.142875+00
447	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:14:21.142875+00
448	2	TIMEFRAME_MANUAL_CREATED	timeframe	17	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:14:24.201705+00
449	2	TIMEFRAME_MANUAL_UPDATED	timeframe	17	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:14:24.232765+00
450	2	TIMEFRAME_CREATED	timeframe	18	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:14:24.427874+00
482	2	SEMESTER_CREATED	semester	224	\N	\N	{"code": "DURATION-16B43913", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:14:47.567173+00
483	2	SEMESTER_STATUS_CHANGED	semester	224	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:47.590065+00
451	2	TIMEFRAME_UPDATED	timeframe	18	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:14:24.474677+00
452	2	TIMEFRAME_ARCHIVED	timeframe	18	Archive test template	\N	{"archived": true}	2026-08-22 08:14:24.501532+00
453	2	TIMEFRAME_CREATED	timeframe	19	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:14:24.702058+00
454	2	ROUND_CREATED	round	99	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 19, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 33, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:14:24.726488+00
455	2	TIMEFRAME_UPDATED	timeframe	19	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:14:24.782573+00
456	2	TIMEFRAME_MANUAL_CREATED	timeframe	20	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:14:24.967028+00
457	2	ROUND_CREATED	round	100	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 20, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 35, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:14:24.99146+00
458	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:36.122673+00
459	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:14:36.352374+00
460	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:14:36.509186+00
461	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:36.675903+00
462	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:14:38.553849+00
463	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:14:38.897125+00
464	\N	TEST	test	d62cca16d4544105b5afb89aaa019af0	\N	\N	\N	2026-08-22 08:14:39.106959+00
465	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:43.789076+00
466	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:44.29379+00
467	32	AVAILABILITY_ENTERED	group_availability	103:30	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:14:44.478029+00
468	32	AVAILABILITY_ENTERED	group_availability	103:30	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:14:44.506206+00
469	32	AVAILABILITY_ENTERED	group_availability	103:30	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:14:44.530452+00
470	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:44.737892+00
471	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:14:45.093284+00
472	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:45.280794+00
473	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:14:45.430092+00
474	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:45.706133+00
475	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:46.799614+00
476	2	SEMESTER_CREATED	semester	220	\N	\N	{"code": "API-C06DA1C2", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:14:46.826847+00
477	2	SEMESTER_SET_CURRENT	semester	220	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:47.034727+00
478	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:14:47.034727+00
479	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:47.231695+00
480	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:47.331216+00
481	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:14:47.547083+00
484	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:14:47.606991+00
485	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:48.184723+00
486	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:48.382096+00
487	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:48.592724+00
488	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:48.772328+00
489	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:49.200103+00
490	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:49.374673+00
491	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:49.548862+00
492	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:51.993274+00
493	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:52.159509+00
494	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:52.33334+00
495	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:52.70125+00
496	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:52.914505+00
497	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:53.125822+00
498	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:53.312457+00
499	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:55.055979+00
500	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:56.09339+00
501	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:56.805973+00
502	1	ACCOUNT_CREATED	account	1404	\N	\N	{"role": "MANAGER", "email": "operator-81829306@example.test"}	2026-08-22 08:14:56.908+00
503	1	ACCOUNT_STATUS_CHANGED	account	1404	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:14:56.941569+00
504	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:57.109664+00
505	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:57.285654+00
506	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:58.663766+00
507	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:14:58.973421+00
508	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:01.265773+00
509	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:01.444407+00
510	2	ROUND_TRANSITION	round	104	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:15:01.775503+00
511	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:01.970174+00
512	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:02.452851+00
513	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:03.556298+00
514	2	ROUND_COMMITTEES_REPLACED	round	105	\N	\N	{"committee_ids": [193, 194]}	2026-08-22 08:15:03.598063+00
515	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:03.880777+00
516	2	ROUND_COMMITTEES_REPLACED	round	106	\N	\N	{"committee_ids": [196]}	2026-08-22 08:15:03.905607+00
517	2	ROUND_COMMITTEES_REPLACED	round	106	\N	\N	{"committee_ids": []}	2026-08-22 08:15:03.92282+00
518	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:04.19936+00
519	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:04.435736+00
520	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:05.018587+00
521	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:05.271482+00
522	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:05.530377+00
523	2	ROUND_COMMITTEES_REPLACED	round	112	\N	\N	{"committee_ids": [211]}	2026-08-22 08:15:05.560093+00
524	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:05.867433+00
525	2	ROUND_COMMITTEES_REPLACED	round	113	\N	\N	{"committee_ids": [214]}	2026-08-22 08:15:05.91039+00
526	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:06.349041+00
527	2	ROUND_COMMITTEES_REPLACED	round	114	\N	\N	{"committee_ids": [217]}	2026-08-22 08:15:06.370765+00
528	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:06.751127+00
529	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:07.13281+00
530	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:07.336381+00
531	2	SEMESTER_CREATED	semester	252	\N	\N	{"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:15:07.354104+00
532	2	SEMESTER_UPDATED	semester	252	\N	{"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	{"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}	2026-08-22 08:15:07.452476+00
533	2	SEMESTER_SET_CURRENT	semester	252	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:07.473444+00
534	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:15:07.473444+00
547	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:15:26.679182+00
548	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:26.852253+00
535	2	TIMEFRAME_MANUAL_CREATED	timeframe	21	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:15:10.520336+00
536	2	TIMEFRAME_MANUAL_UPDATED	timeframe	21	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:15:10.551843+00
537	2	TIMEFRAME_CREATED	timeframe	22	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:15:10.770451+00
538	2	TIMEFRAME_UPDATED	timeframe	22	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:15:10.809908+00
539	2	TIMEFRAME_ARCHIVED	timeframe	22	Archive test template	\N	{"archived": true}	2026-08-22 08:15:10.837342+00
540	2	TIMEFRAME_CREATED	timeframe	23	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:15:11.055642+00
541	2	ROUND_CREATED	round	116	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 23, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 40, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:15:11.077791+00
542	2	TIMEFRAME_UPDATED	timeframe	23	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:15:11.122346+00
543	2	TIMEFRAME_MANUAL_CREATED	timeframe	24	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:15:11.322293+00
544	2	ROUND_CREATED	round	117	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 24, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 42, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:15:11.338667+00
545	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:26.235891+00
546	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:15:26.504842+00
549	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:15:28.656609+00
550	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:15:28.956249+00
551	\N	TEST	test	51542b3b9e8e443f8b5a2bc57fe2d56f	\N	\N	\N	2026-08-22 08:15:29.132317+00
552	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:30.927312+00
553	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:31.38817+00
554	32	AVAILABILITY_ENTERED	group_availability	120:35	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:15:31.523426+00
555	32	AVAILABILITY_ENTERED	group_availability	120:35	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:15:31.544857+00
556	32	AVAILABILITY_ENTERED	group_availability	120:35	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:15:31.564539+00
557	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:31.736542+00
558	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:15:32.077975+00
559	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:32.241283+00
560	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:15:32.387492+00
561	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:32.647297+00
562	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:33.616778+00
563	2	SEMESTER_CREATED	semester	262	\N	\N	{"code": "API-DA7261BC", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:15:33.642419+00
564	2	SEMESTER_SET_CURRENT	semester	262	\N	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:33.846833+00
565	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:15:33.846833+00
566	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:34.01516+00
567	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:34.121048+00
568	2	SEMESTER_STATUS_CHANGED	semester	1	Prepare isolated API test	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:34.285026+00
569	2	SEMESTER_CREATED	semester	266	\N	\N	{"code": "DURATION-9046A2DF", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}	2026-08-22 08:15:34.302638+00
570	2	SEMESTER_STATUS_CHANGED	semester	266	Semester completed	{"status": "ACTIVE"}	{"status": "CLOSED"}	2026-08-22 08:15:34.323177+00
571	2	SEMESTER_SET_CURRENT	semester	1	\N	{"status": "CLOSED"}	{"status": "ACTIVE"}	2026-08-22 08:15:34.338992+00
572	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:34.8182+00
573	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:35.004576+00
574	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:35.18037+00
575	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:35.360321+00
576	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:35.81146+00
577	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:35.997033+00
578	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:36.175069+00
579	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:38.354249+00
580	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:38.529462+00
581	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:38.684816+00
582	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:38.960794+00
583	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:39.152212+00
584	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:39.342398+00
585	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:39.552818+00
586	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:41.287245+00
587	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:42.350272+00
588	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:43.016311+00
589	1	ACCOUNT_CREATED	account	1636	\N	\N	{"role": "MANAGER", "email": "operator-8f74a9c2@example.test"}	2026-08-22 08:15:43.12487+00
590	1	ACCOUNT_STATUS_CHANGED	account	1636	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:15:43.160781+00
591	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:43.320638+00
592	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:43.507657+00
593	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:44.750321+00
594	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:45.082661+00
595	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:50.741228+00
596	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:50.937786+00
597	2	ROUND_TRANSITION	round	121	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:15:51.334924+00
598	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:51.562906+00
599	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:52.145963+00
600	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:53.195882+00
601	2	ROUND_COMMITTEES_REPLACED	round	122	\N	\N	{"committee_ids": [223, 224]}	2026-08-22 08:15:53.237599+00
602	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:53.550508+00
603	2	ROUND_COMMITTEES_REPLACED	round	123	\N	\N	{"committee_ids": [226]}	2026-08-22 08:15:53.579375+00
604	2	ROUND_COMMITTEES_REPLACED	round	123	\N	\N	{"committee_ids": []}	2026-08-22 08:15:53.600218+00
605	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:53.853358+00
606	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:54.14197+00
607	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:54.82552+00
608	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:55.133029+00
609	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:55.410803+00
610	2	ROUND_COMMITTEES_REPLACED	round	129	\N	\N	{"committee_ids": [241]}	2026-08-22 08:15:55.436006+00
611	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:55.864996+00
612	2	ROUND_COMMITTEES_REPLACED	round	130	\N	\N	{"committee_ids": [244]}	2026-08-22 08:15:55.917446+00
613	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:15:56.388592+00
614	2	ROUND_COMMITTEES_REPLACED	round	131	\N	\N	{"committee_ids": [247]}	2026-08-22 08:15:56.417592+00
615	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:56.937024+00
616	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:15:57.350312+00
617	2	TIMEFRAME_MANUAL_CREATED	timeframe	25	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:00.20113+00
618	2	TIMEFRAME_MANUAL_UPDATED	timeframe	25	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:00.231967+00
619	2	TIMEFRAME_CREATED	timeframe	26	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:16:00.480128+00
620	2	TIMEFRAME_UPDATED	timeframe	26	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:16:00.530901+00
621	2	TIMEFRAME_ARCHIVED	timeframe	26	Archive test template	\N	{"archived": true}	2026-08-22 08:16:00.562241+00
622	2	TIMEFRAME_CREATED	timeframe	27	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:16:00.808671+00
623	2	ROUND_CREATED	round	133	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 27, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 47, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:16:00.848325+00
669	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:38.456657+00
670	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:38.640737+00
671	2	ROUND_TRANSITION	round	138	\N	{"status": "OPEN_REGISTRATION"}	{"status": "REGISTRATION_CLOSED"}	2026-08-22 08:16:38.794932+00
624	2	TIMEFRAME_UPDATED	timeframe	27	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:16:00.897272+00
625	2	TIMEFRAME_MANUAL_CREATED	timeframe	28	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:01.125957+00
626	2	ROUND_CREATED	round	134	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 28, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 49, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:16:01.148593+00
627	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:13.230824+00
628	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:16:13.481512+00
629	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:16:13.666519+00
630	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:13.832107+00
631	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 1}	2026-08-22 08:16:15.659096+00
632	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 2, "skipped": 0}	2026-08-22 08:16:15.929076+00
633	\N	TEST	test	4642dc0e5f2d428f8ba1b185ab9e9afe	\N	\N	\N	2026-08-22 08:16:16.097495+00
634	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:17.909267+00
635	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:18.366893+00
636	32	AVAILABILITY_ENTERED	group_availability	137:40	\N	\N	{"source": "FORM", "selected_count": 2}	2026-08-22 08:16:18.546993+00
637	32	AVAILABILITY_ENTERED	group_availability	137:40	\N	\N	{"source": "FORM", "selected_count": 1}	2026-08-22 08:16:18.57536+00
638	32	AVAILABILITY_ENTERED	group_availability	137:40	\N	\N	{"source": "FORM", "selected_count": 0}	2026-08-22 08:16:18.598043+00
639	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:18.784332+00
640	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:16:22.195771+00
641	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:22.395026+00
642	1	LECTURERS_IMPORTED	lecturer	bulk	\N	\N	{"created": 1, "skipped": 2}	2026-08-22 08:16:22.528508+00
643	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:22.793352+00
644	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:24.108888+00
645	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:24.225118+00
646	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:24.796189+00
647	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:24.950457+00
648	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:25.161832+00
649	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:25.340469+00
650	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:25.968014+00
651	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:26.163809+00
652	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:26.346661+00
653	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:29.139689+00
654	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:29.314366+00
655	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:29.479534+00
656	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:29.660078+00
657	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:29.961657+00
658	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:30.177297+00
659	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:30.378003+00
660	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:32.227456+00
661	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:33.379543+00
662	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:34.002694+00
663	1	ACCOUNT_CREATED	account	1868	\N	\N	{"role": "MANAGER", "email": "operator-4951c3f7@example.test"}	2026-08-22 08:16:34.102823+00
664	1	ACCOUNT_STATUS_CHANGED	account	1868	End of local pilot	{"status": "ACTIVE"}	{"status": "INACTIVE"}	2026-08-22 08:16:34.140024+00
665	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:34.312542+00
666	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:34.480133+00
667	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:35.693623+00
668	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:36.045002+00
672	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:38.968699+00
673	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:39.404352+00
674	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:40.52074+00
675	2	ROUND_COMMITTEES_REPLACED	round	139	\N	\N	{"committee_ids": [253, 254]}	2026-08-22 08:16:40.557934+00
676	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:40.857132+00
677	2	ROUND_COMMITTEES_REPLACED	round	140	\N	\N	{"committee_ids": [256]}	2026-08-22 08:16:40.878532+00
678	2	ROUND_COMMITTEES_REPLACED	round	140	\N	\N	{"committee_ids": []}	2026-08-22 08:16:40.893541+00
679	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:41.180159+00
680	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:41.441764+00
681	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:42.075035+00
682	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:42.368764+00
683	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:42.607509+00
684	2	ROUND_COMMITTEES_REPLACED	round	146	\N	\N	{"committee_ids": [271]}	2026-08-22 08:16:42.630548+00
685	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:43.068619+00
686	2	ROUND_COMMITTEES_REPLACED	round	147	\N	\N	{"committee_ids": [274]}	2026-08-22 08:16:43.103896+00
687	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:16:43.423029+00
688	2	ROUND_COMMITTEES_REPLACED	round	148	\N	\N	{"committee_ids": [277]}	2026-08-22 08:16:43.447919+00
689	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:43.867103+00
690	1	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 08:16:44.251356+00
691	2	TIMEFRAME_MANUAL_CREATED	timeframe	29	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:47.663152+00
692	2	TIMEFRAME_MANUAL_UPDATED	timeframe	29	Replace all edited timelines	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:47.701148+00
693	2	TIMEFRAME_CREATED	timeframe	30	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:16:47.925784+00
694	2	TIMEFRAME_UPDATED	timeframe	30	Move the shared template to 08:00	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:16:47.966845+00
695	2	TIMEFRAME_ARCHIVED	timeframe	30	Archive test template	\N	{"archived": true}	2026-08-22 08:16:47.993074+00
696	2	TIMEFRAME_CREATED	timeframe	31	Test reusable system configuration	\N	{"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}	2026-08-22 08:16:48.245022+00
733	\N	ROOM_CATALOG_SEEDED	room_catalog	rooms	Seed local room catalog; room reuse limits are intentionally ignored	\N	{"rooms": 11, "round_id": 164, "bound_room_types": ["NORMAL", "SEMINAR"]}	2026-08-22 10:26:36.868803+00
697	2	ROUND_CREATED	round	150	\N	\N	{"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 31, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 54, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:16:48.276045+00
698	2	TIMEFRAME_UPDATED	timeframe	31	Test reusable system configuration	\N	{"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}	2026-08-22 08:16:48.327137+00
699	2	TIMEFRAME_MANUAL_CREATED	timeframe	32	Save timelines edited from quick preview	\N	{"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}	2026-08-22 08:16:48.527602+00
700	2	ROUND_CREATED	round	151	\N	\N	{"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 32, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 56, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}	2026-08-22 08:16:48.549782+00
701	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:11.134136+00
702	2	ROUND_COMMITTEES_REPLACED	round	152	\N	\N	{"committee_ids": [280, 281]}	2026-08-22 08:19:11.17986+00
703	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:11.483498+00
704	2	ROUND_COMMITTEES_REPLACED	round	153	\N	\N	{"committee_ids": [283]}	2026-08-22 08:19:11.506807+00
705	2	ROUND_COMMITTEES_REPLACED	round	153	\N	\N	{"committee_ids": []}	2026-08-22 08:19:11.523238+00
706	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:11.787608+00
707	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:12.051973+00
708	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:12.697953+00
709	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:13.039363+00
710	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:13.286946+00
711	2	ROUND_COMMITTEES_REPLACED	round	159	\N	\N	{"committee_ids": [298]}	2026-08-22 08:19:13.311639+00
712	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:13.628841+00
713	2	ROUND_COMMITTEES_REPLACED	round	160	\N	\N	{"committee_ids": [301]}	2026-08-22 08:19:13.678611+00
714	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 3, "skipped": 0}	2026-08-22 08:19:14.014194+00
715	2	ROUND_COMMITTEES_REPLACED	round	161	\N	\N	{"committee_ids": [304]}	2026-08-22 08:19:14.037315+00
716	2	COMMITTEES_CREATED	committee	bulk	\N	\N	{"created": 1, "skipped": 0}	2026-08-22 08:31:51.771473+00
717	2	ROUND_COMMITTEES_REPLACED	round	163	\N	\N	{"committee_ids": [307]}	2026-08-22 08:31:51.849336+00
718	\N	EXCEL_PROJECTS_GVHD_IMPORTED	excel_import	su26_defense_1.2_SE.xlsx	One-sheet project and supervisor import	\N	{"projects": 74, "semester": "SU26", "supervisor_assignments": 80}	2026-08-22 08:31:59.411248+00
719	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 08:40:17.294181+00
720	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 08:40:19.723567+00
721	1	LOGIN_SUCCESS	account	1	\N	\N	{"session": "created"}	2026-08-22 08:42:10.994618+00
722	1	LOGIN_SUCCESS	account	1	\N	\N	{"session": "created"}	2026-08-22 08:42:24.433525+00
723	1	LOGIN_SUCCESS	account	1	\N	\N	{"session": "created"}	2026-08-22 08:42:32.730009+00
724	1	DATABASE_CLEANUP_AND_GROUP_IMPORT	database	db_cleanup_backup_20260822_160826	Removed test semesters/accounts and imported groups/students from defenserflowdb	\N	{"memberships": 104, "backup_table": "db_cleanup_backup_20260822_160826", "unique_students": 102, "projects_with_students": 29, "project_codes_considered": 74}	2026-08-22 09:08:50.914141+00
725	\N	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 10:10:03.650475+00
726	\N	SEED_FIXTURE_LOADED	seed_fixture	seed-v5	\N	\N	{"source": "VERSIONED_SEED"}	2026-08-22 10:10:06.358606+00
727	\N	EXCEL_PROJECTS_GVHD_IMPORTED	excel_import	su26_defense_1.2_SE.xlsx	One-sheet project and supervisor import	\N	{"projects": 74, "semester": "SU26", "supervisor_assignments": 80}	2026-08-22 10:11:02.583719+00
728	\N	EXCEL_DEFENSE_ELIGIBILITY_IMPORTED	round	164	Import Defense 1.2 eligible groups from SU26 workbook	\N	{"sheet": "Kỹ thuật phần mềm", "source": "su26_defense_1.2_SE.xlsx", "semester": "SU26", "linked_groups": 14, "usable_groups": 14, "status_updated": 14, "eligible_projects": 50}	2026-08-22 10:21:16.638371+00
729	2	LOGOUT	account	2	\N	\N	{"session": "revoked"}	2026-08-22 10:25:13.271371+00
730	1	LOGIN_SUCCESS	account	1	\N	\N	{"session": "created"}	2026-08-22 10:25:53.253208+00
731	1	LOGOUT	account	1	\N	\N	{"session": "revoked"}	2026-08-22 10:26:29.416908+00
732	2	LOGIN_SUCCESS	account	2	\N	\N	{"session": "created"}	2026-08-22 10:26:33.091327+00
\.


--
-- Data for Name: auth_login_throttles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_login_throttles (identifier, window_started_at, attempts, updated_at) FROM stdin;
7d7595e30cef2fc7129b99eaea74a800667fea48444f6629fd2f2c33c5d5a741	2026-08-22 07:56:03.197902+00	10	2026-08-22 07:56:03.351274+00
16fcea6fa28991a67f7df64702b3ef5b0b2ddde1d78d1b4b0b558490f08259fa	2026-08-22 08:14:37.047833+00	10	2026-08-22 08:14:37.175318+00
2c5d0a408d19ecd0b8f7e72026003c35345a94f81de350dc0f99bc821759c82a	2026-08-22 08:05:41.878958+00	10	2026-08-22 08:05:42.019244+00
63adbdec44e8291770a7867d40aa20612e48289a449d45581c8beb4b7a29db10	2026-08-22 08:15:27.177148+00	10	2026-08-22 08:15:27.301995+00
14ea465a8a4292847695141e09e49c322f93277a8d3ccc571739f118b1237d64	2026-08-22 08:06:30.581151+00	10	2026-08-22 08:06:30.687245+00
d1f81615f3efab9d578d8dd3f501477e9cd35b6bce46b895d44839ad9ff3e904	2026-08-22 08:12:52.138628+00	10	2026-08-22 08:12:52.288936+00
2780aedd448af8128fb21e07a06c54921bdf077f08759f3933e334a7a08558d3	2026-08-22 08:16:14.142054+00	10	2026-08-22 08:16:14.262502+00
db31af2c10f20ab0059fe245f148d873580b3c7792d7a508501ab18303b79d91	2026-08-22 08:13:49.283402+00	10	2026-08-22 08:13:49.438993+00
\.


--
-- Data for Name: auth_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_sessions (id, account_id, token_hash, csrf_token_hash, created_at, last_seen_at, expires_at, revoked_at) FROM stdin;
6	2	ab090d5cd63eaa16f4ab21331457f4a536ff441ada09e05e0e863fc276fdc0f0	50e4e91a7f6e223b34434f470fc8ecb83d9990a1792736da9d52d343976238c6	2026-08-22 08:13:48.621395+00	2026-08-22 08:13:48.753462+00	2026-08-29 08:13:48.697807+00	2026-08-22 08:13:48.777071+00
12	1	0be8b86dd450cb02c833b7950910502cb99c3e74b518cb85bd5f8927f10acf68	d46f198d7a95c8a10e9b6beb83a925adc15f1814682b5661b05a1e845f65b6a8	2026-08-22 08:42:24.433525+00	2026-08-22 08:42:24.573552+00	2026-08-29 08:42:24.54833+00	\N
7	2	900ffa2470f7f4c261b39d6fdcc54c247650af247101f5919996f6e571a73e28	3f24426433d8ceff3ce771e73557e69deb1425e2b05afcb92ee12b52a44b1ea4	2026-08-22 08:14:36.352374+00	2026-08-22 08:14:36.483484+00	2026-08-29 08:14:36.435556+00	2026-08-22 08:14:36.509186+00
14	1	bf29fd216cf8f6695cf9fc4f8aa603108e740d5e8867855f04105d86fdf4c3e9	8df48a834a652d3d214e62798ba6c090c5e50cf79289efa6d7516596cec31222	2026-08-22 10:25:53.253208+00	2026-08-22 10:25:53.814349+00	2026-08-29 10:25:53.430553+00	2026-08-22 10:26:29.416908+00
8	2	c99f539538d9c2511f9f093ca346982e41d0ba9d5b2239e9f7406e6d323d4955	d3a36ebc22d27f876a5045e0113d7631f2192dc68eb0f7a28a368b5b2338ddca	2026-08-22 08:15:26.504842+00	2026-08-22 08:15:26.650102+00	2026-08-29 08:15:26.595787+00	2026-08-22 08:15:26.679182+00
13	1	921baa70730fe6ae86fb40bd1486edf2521b95dfe3aac8175fa1875fc3b3a913	941166be4b8b327f27573db24137b181259eaea5907363c480ec8beb6c3137ce	2026-08-22 08:42:32.730009+00	2026-08-22 08:42:32.906047+00	2026-08-29 08:42:32.834611+00	\N
9	2	dd12d81e0627f230fb2d68005fd5dbb0f29f3011bcd600ac9d333c1bae5df02e	55fa02c492b974b9e9fe588db086aa27e286daa48316b51126a778ad429fe7d4	2026-08-22 08:16:13.481512+00	2026-08-22 08:16:13.640986+00	2026-08-29 08:16:13.57652+00	2026-08-22 08:16:13.666519+00
2	2	9b676a6e1cea880921b5710d906e64ce13a91da2ffbf5c120d7570ef013a50b2	a09752e6f256bbeb3856d08d82c55f35eee76dbde4fb4da24bb7c0d83ca5df9b	2026-08-22 07:56:01.944819+00	2026-08-22 07:56:02.205676+00	2026-08-29 07:56:02.125518+00	2026-08-22 07:56:02.230838+00
1	2	f64d9b7519db3efa6998300a8ece003a1ac9603946003de25bbd87e35e5136dd	1e78d5ca3231b35fac1b9f0ce0a8e6ab4e99c0e062dbef463c1d567144fc0b6f	2026-08-22 07:55:17.263729+00	2026-08-22 08:40:12.154916+00	2026-08-29 07:55:17.47368+00	2026-08-22 08:40:17.294181+00
3	2	0f3b9b7f35164aebdedc31b4e33a68152048f6b611574c28b8c64da04a501121	049d328a15c5d30f538d39989e2e05fb9f1c2f39149d1ef907810be840931d8f	2026-08-22 08:05:41.058063+00	2026-08-22 08:05:41.242876+00	2026-08-29 08:05:41.172421+00	2026-08-22 08:05:41.276647+00
4	2	62c8200c8f405c01f6011db4a0efad09b48e15626c0d8eeb0f298222abc4c8f6	b6533cb19517b74bb6c2e497c673d145b0d5458752417eefe74bddee94b02c1c	2026-08-22 08:06:29.669389+00	2026-08-22 08:06:29.84275+00	2026-08-29 08:06:29.786684+00	2026-08-22 08:06:29.863963+00
5	2	12d8d97d99c5b8d88ae40cad90001004993fc8f5b4cd146438673715f74017bd	1391c094c83bafd5ac4fedb52c5c07b20e26e56e954032ca9b5d8c2338fb73ac	2026-08-22 08:12:51.440205+00	2026-08-22 08:12:51.586906+00	2026-08-29 08:12:51.534233+00	2026-08-22 08:12:51.610617+00
15	2	e98bafb27e3227dee60149130c7317aed6d9bdca8c6f39c0f914c8c75c5276e5	a9872577976c8c9d665001d20ef0c783ee8cfe33f2bde73c075dae412a73daf1	2026-08-22 10:26:33.091327+00	2026-08-22 10:26:39.285521+00	2026-08-29 10:26:33.241915+00	\N
10	2	3a58aa2143f2e1c431ac81ab1936251d1bb3ca47ae5b221685282e65d6d4cce3	48edc120b5fa473b9456e64786cdd4b5479f4e5c2c9a2247928c9acb92fcb5b5	2026-08-22 08:40:19.723567+00	2026-08-22 10:25:11.398724+00	2026-08-29 08:40:19.860366+00	2026-08-22 10:25:13.271371+00
11	1	1b58c9f21d8fa6ff1e0b852f83f9b036c5223f1c4a76c3313e8af72250d19742	2b56193fd7a20ee69878a92ecfa494279420a4651f6917f67c05ec097f02654e	2026-08-22 08:42:10.994618+00	2026-08-22 08:42:11.132066+00	2026-08-29 08:42:11.112895+00	\N
\.


--
-- Data for Name: committee_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.committee_members (committee_id, lecturer_id, role, sequence_number) FROM stdin;
\.


--
-- Data for Name: committees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.committees (id, code, member_count, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: conflict_declarations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.conflict_declarations (id, lecturer_id, project_id, reason, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: council_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.council_members (council_id, lecturer_id, assignment, is_result_owner, snapshot_name) FROM stdin;
\.


--
-- Data for Name: councils; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.councils (id, round_id, supersedes_council_id, created_by, reason, created_at, sealed_at) FROM stdin;
\.


--
-- Data for Name: db_cleanup_backup_20260822_160826; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.db_cleanup_backup_20260822_160826 (backup_id, table_name, row_data, backed_up_at) FROM stdin;
1	accounts	{"id": 664, "email": "operator-da2ccb54@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:06:49.284741+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$l3V0wr4IOMbSCjK/aQw+QA$x4Yhp9OqXHUAQ2qC3PSe+dWoycaJRGMcwPu8ElNzTgg"}	2026-08-22 09:08:50.623502+00
2	accounts	{"id": 1404, "email": "operator-81829306@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:14:56.908+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$O+8iW+Kl8p+VT4gh7lGjog$HIgViq+3F0WHu9bQyWq4xc9roxDOZiXXhUZmTRJmvgU"}	2026-08-22 09:08:50.623502+00
3	accounts	{"id": 350, "email": "gvi.65f38067@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:05:48.369744+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$nftkESt4ZGCYifVRIMCQDQ$kvyPPFSM2/TUAqOoH6QT7scMsFvbQcHXIrWG3keWEy0"}	2026-08-22 09:08:50.623502+00
4	accounts	{"id": 3, "email": "phuonglhk@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Lâm Hữu Khánh Phương", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
5	accounts	{"id": 4, "email": "ducdnm@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Đặng Ngọc Minh Đức", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
6	accounts	{"id": 5, "email": "vanttn@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Thân Thị Ngọc Vân", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
7	accounts	{"id": 6, "email": "tampm@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Phan Minh Tâm", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
8	accounts	{"id": 577, "email": "gvi.b6888c19@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:06:36.539711+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$7zget1mNRXVhtluJYKTfFQ$CQl2tstmAlA8cCV0pGvEEFYnlwzgDlhLGxJ7E8gVhy0"}	2026-08-22 09:08:50.623502+00
9	accounts	{"id": 582, "email": "gvd.df44fcbf@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:06:36.902782+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$c7Kx995zkgCw2arodZ+zlQ$nSWy+PFZf63wxlS2H8sLgh2i7NoQeXf4NBPiMc1grHs"}	2026-08-22 09:08:50.623502+00
10	accounts	{"id": 7, "email": "nhandt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Đỗ Tấn Nhàn", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
11	accounts	{"id": 8, "email": "phucnt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Tấn Phúc", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
12	accounts	{"id": 9, "email": "sangnm@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Minh Sang", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
13	accounts	{"id": 10, "email": "hoangnt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Thế Hoàng", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
14	accounts	{"id": 1, "email": "admin@gmail.com", "status": "ACTIVE", "created_at": "2026-08-22T03:57:14.256588+00:00", "display_name": "Admin", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4"}	2026-08-22 09:08:50.623502+00
15	accounts	{"id": 2, "email": "manager@gmail.com", "status": "ACTIVE", "created_at": "2026-08-22T03:57:14.256588+00:00", "display_name": "Manager", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$En3fCFubxFcQV5wXlljPZA$Ch+nsVeUoLv7C5Lo43hrAW+H5FbTUJQiB2aOfSTYny4"}	2026-08-22 09:08:50.623502+00
16	accounts	{"id": 1172, "email": "operator-c971018d@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:14:10.194557+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$aXQbHOfH7+F9dSuBQQgDtw$j83PXGBMG7VMY01EoQA8I51JPdmDK5s1M71v5psagiU"}	2026-08-22 09:08:50.623502+00
17	accounts	{"id": 1085, "email": "gvi.5773c4ac@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:13:55.146128+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$cVIiLszjbR2J87qplP5mnQ$zLk/B0QLI2GD2CF5lytlMst4shYK1V9O/eRZvbB68rU"}	2026-08-22 09:08:50.623502+00
18	accounts	{"id": 1090, "email": "gvd.8e720508@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:13:55.447162+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$Hfp38mNDiYcCM1txmVm61g$VZfhia+SwejaCf9wy/9QzH6Yr/h4O15LkD0cKeaPDV4"}	2026-08-22 09:08:50.623502+00
19	accounts	{"id": 355, "email": "gvd.fe9d2c7a@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:05:48.758297+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$xGqg13YWO6/xo4kntmXxCw$AMAGJ4XUH0R0jqSDSfTU+0/UucuQJIVhqNGvJssJBdE"}	2026-08-22 09:08:50.623502+00
20	accounts	{"id": 437, "email": "operator-788da04a@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:06:03.602805+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$DsvKwOUFejmxg0+WiYdBHQ$MfEVn/yanqukZVCiGXSSfSeaYNM4wCicxEzF8d5Czes"}	2026-08-22 09:08:50.623502+00
21	accounts	{"id": 1317, "email": "gvi.b38c6eb5@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:14:45.093284+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$CYQk/krETJRnWBO0+b7yUg$1zTvp+EIZhkvcjtZZvFLucy10aYT3X8ZWLydZwULnyA"}	2026-08-22 09:08:50.623502+00
22	accounts	{"id": 1322, "email": "gvd.8caea377@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:14:45.430092+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$5qmABVNysuESD2+ZI7kvDQ$z2gGL4YmA5gnMyY+JVBADwwb1d4d0fEsRiRriJPivSk"}	2026-08-22 09:08:50.623502+00
23	accounts	{"id": 11, "email": "longt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Trương Long", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
101	account_roles	{"role": "LECTURER", "account_id": 350}	2026-08-22 09:08:50.623502+00
102	account_roles	{"role": "LECTURER", "account_id": 355}	2026-08-22 09:08:50.623502+00
24	accounts	{"id": 12, "email": "taint@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Trọng Tài", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
25	accounts	{"id": 13, "email": "lamnn@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Ngọc Lâm", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
26	accounts	{"id": 14, "email": "thongnt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Trí Thông", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
27	accounts	{"id": 15, "email": "anndh@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Ngô Đăng Hà An", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
28	accounts	{"id": 16, "email": "duongvtt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Vũ Thị Thùy Dương", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
29	accounts	{"id": 17, "email": "hungld@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Lại Đức Hùng", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
30	accounts	{"id": 18, "email": "nguyentt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Trần Thanh Nguyên", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
31	accounts	{"id": 19, "email": "khanhkt@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Kiều Trọng Khánh", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
32	accounts	{"id": 20, "email": "huongntc@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Thị Cẩm Hương", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
33	accounts	{"id": 21, "email": "minhtth@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Tôn Thất Hoàng Minh", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
34	accounts	{"id": 22, "email": "thinhdp@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Đỗ Phúc Thịnh", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
35	accounts	{"id": 23, "email": "quynhtnn@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Trần Ngọc Như Quỳnh", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
36	accounts	{"id": 24, "email": "tript@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Phạm Thanh Trí", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
37	accounts	{"id": 25, "email": "chiltq@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Lê Thị Quỳnh Chi", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
38	accounts	{"id": 26, "email": "vulns@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Lê Nguyễn Sơn Vũ", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
39	accounts	{"id": 27, "email": "tripm@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Phạm Minh Trí", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
40	accounts	{"id": 28, "email": "huynx@fpt.edu.vn", "status": "ACTIVE", "created_at": "2026-08-22T07:49:29.170388+00:00", "display_name": "Nguyễn Xuân Huy", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$QEohePsRe+9sKGJReruLoQ$Bd/17LcEMJHq+w0MduNsIh//wzB+ilKpN3YvwwKkX7Y"}	2026-08-22 09:08:50.623502+00
41	accounts	{"id": 32, "email": "student1@gmail.com", "status": "ACTIVE", "created_at": "2026-08-22T07:56:01.318366+00:00", "display_name": "Student 1", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$LrmJZJKfKbcSOmue5usU1Q$hLKiGrWvONQb42SF5SioxK0zb+alCZOg77Mq9QBsiWY"}	2026-08-22 09:08:50.623502+00
42	accounts	{"id": 1554, "email": "gvd.3822c4fe@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:15:32.387492+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$hXKNMwdWpbbiSPJN87Tbig$htHoMf2VgZQmY1xmzz5PF1LDHfLRQB4eOiFc4aNtGDs"}	2026-08-22 09:08:50.623502+00
43	accounts	{"id": 1781, "email": "gvi.1ed0e33d@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:16:22.195771+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$snOmL1aG5y8c26mPkVMa2Q$FLrsW2i7WSSy03GB5BTMoIlBEqoAsHhXHd6El8i3rnA"}	2026-08-22 09:08:50.623502+00
44	accounts	{"id": 1868, "email": "operator-4951c3f7@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:16:34.102823+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$Z2UH64a/j/iVdn0YHtjqVQ$cnOoq6DBrOFZf5HuXPMEFDwaz4+l2Zm8hP1pyw+hRVI"}	2026-08-22 09:08:50.623502+00
45	accounts	{"id": 1636, "email": "operator-8f74a9c2@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:15:43.12487+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$fQPN5Kn41EqX0d+PHE3G9Q$L4EpCiI1S1z610X7xbT4WY3/v0otRV2ImUofESk7p2U"}	2026-08-22 09:08:50.623502+00
46	accounts	{"id": 853, "email": "gvi.36b9697d@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:12:58.88311+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$1L6nEW0iLmkT9ICV8bk2Yg$nv8p/1TifFXRDLXwMd1jsWemxXT8MnITLD4OXIZ1Cbw"}	2026-08-22 09:08:50.623502+00
103	account_roles	{"role": "MANAGER", "account_id": 437}	2026-08-22 09:08:50.623502+00
104	account_roles	{"role": "LECTURER", "account_id": 1549}	2026-08-22 09:08:50.623502+00
47	accounts	{"id": 88, "email": "gvi.8d14c7f2@example.com", "status": "ACTIVE", "created_at": "2026-08-22T07:56:12.39016+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$Ex3KwjXio/j/uoLsEXR31A$vMu6Nm2YbMPjB/BY6LxMwpgLlGbzIxEUIOeNZUu8/ug"}	2026-08-22 09:08:50.623502+00
48	accounts	{"id": 175, "email": "operator-1c591b0e@example.test", "status": "INACTIVE", "created_at": "2026-08-22T07:56:35.295288+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$xJm1+KCMUHIm5wT0xthsKA$nNp9AEcCl/uoWyU8C9B5yOJH8aDXK9OKeQ0s7Fw27rg"}	2026-08-22 09:08:50.623502+00
49	accounts	{"id": 93, "email": "gvd.989a54db@example.com", "status": "ACTIVE", "created_at": "2026-08-22T07:56:13.002488+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$X3+x+1goZoPpMsPUDOQPcQ$6Rx3g+pFhCholp22DaRi/KY9RzAku0YeuKOlRpUvEqE"}	2026-08-22 09:08:50.623502+00
50	accounts	{"id": 940, "email": "operator-e2f2b036@example.test", "status": "INACTIVE", "created_at": "2026-08-22T08:13:15.533961+00:00", "display_name": "Operator", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$SpgfXq17vwrokognGijONQ$00GD5rtnF6z1f+pZjQa9IwMuymi5ANgCXbsklq7sC8M"}	2026-08-22 09:08:50.623502+00
51	accounts	{"id": 858, "email": "gvd.5d91fc71@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:12:59.621597+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$OtY476GU8bYb2Tp1PDUg7Q$gpINfnhQdyLLhXPNQ0JH0gQcGyDd5Jn+fHA+n/9Le28"}	2026-08-22 09:08:50.623502+00
52	accounts	{"id": 1549, "email": "gvi.b6e659e5@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:15:32.077975+00:00", "display_name": "Nguyen Van Import", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$fzm7hgl1YgHH1N9JV25GZg$gDX9ftFa4Z27YieimsCDm9mh9/qtg++euOK/R08uKbg"}	2026-08-22 09:08:50.623502+00
53	accounts	{"id": 1786, "email": "gvd.b76040ec@example.com", "status": "ACTIVE", "created_at": "2026-08-22T08:16:22.528508+00:00", "display_name": "Duplicate Row One", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$0BONVlvyzI7Xz0zbCcX2Cg$6EGXkzRrYtQFbo5NF4rNJ9vdRu4WqrgcKTJ/JIZkG5g"}	2026-08-22 09:08:50.623502+00
54	accounts	{"id": 31, "email": "lecturer@gmail.com", "status": "ACTIVE", "created_at": "2026-08-22T07:56:01.318366+00:00", "display_name": "Lecturer 1", "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$LrmJZJKfKbcSOmue5usU1Q$hLKiGrWvONQb42SF5SioxK0zb+alCZOg77Mq9QBsiWY"}	2026-08-22 09:08:50.623502+00
55	account_roles	{"role": "ADMIN", "account_id": 1}	2026-08-22 09:08:50.623502+00
56	account_roles	{"role": "MANAGER", "account_id": 2}	2026-08-22 09:08:50.623502+00
57	account_roles	{"role": "LECTURER", "account_id": 577}	2026-08-22 09:08:50.623502+00
58	account_roles	{"role": "LECTURER", "account_id": 582}	2026-08-22 09:08:50.623502+00
59	account_roles	{"role": "MANAGER", "account_id": 664}	2026-08-22 09:08:50.623502+00
60	account_roles	{"role": "MANAGER", "account_id": 1404}	2026-08-22 09:08:50.623502+00
61	account_roles	{"role": "LECTURER", "account_id": 3}	2026-08-22 09:08:50.623502+00
62	account_roles	{"role": "LECTURER", "account_id": 4}	2026-08-22 09:08:50.623502+00
63	account_roles	{"role": "LECTURER", "account_id": 5}	2026-08-22 09:08:50.623502+00
64	account_roles	{"role": "LECTURER", "account_id": 6}	2026-08-22 09:08:50.623502+00
65	account_roles	{"role": "LECTURER", "account_id": 7}	2026-08-22 09:08:50.623502+00
66	account_roles	{"role": "LECTURER", "account_id": 8}	2026-08-22 09:08:50.623502+00
67	account_roles	{"role": "LECTURER", "account_id": 9}	2026-08-22 09:08:50.623502+00
68	account_roles	{"role": "LECTURER", "account_id": 10}	2026-08-22 09:08:50.623502+00
69	account_roles	{"role": "LECTURER", "account_id": 11}	2026-08-22 09:08:50.623502+00
70	account_roles	{"role": "LECTURER", "account_id": 12}	2026-08-22 09:08:50.623502+00
71	account_roles	{"role": "LECTURER", "account_id": 13}	2026-08-22 09:08:50.623502+00
72	account_roles	{"role": "LECTURER", "account_id": 14}	2026-08-22 09:08:50.623502+00
73	account_roles	{"role": "LECTURER", "account_id": 15}	2026-08-22 09:08:50.623502+00
74	account_roles	{"role": "LECTURER", "account_id": 16}	2026-08-22 09:08:50.623502+00
75	account_roles	{"role": "LECTURER", "account_id": 17}	2026-08-22 09:08:50.623502+00
76	account_roles	{"role": "LECTURER", "account_id": 18}	2026-08-22 09:08:50.623502+00
77	account_roles	{"role": "LECTURER", "account_id": 19}	2026-08-22 09:08:50.623502+00
78	account_roles	{"role": "LECTURER", "account_id": 20}	2026-08-22 09:08:50.623502+00
79	account_roles	{"role": "LECTURER", "account_id": 21}	2026-08-22 09:08:50.623502+00
80	account_roles	{"role": "LECTURER", "account_id": 22}	2026-08-22 09:08:50.623502+00
81	account_roles	{"role": "LECTURER", "account_id": 23}	2026-08-22 09:08:50.623502+00
82	account_roles	{"role": "LECTURER", "account_id": 24}	2026-08-22 09:08:50.623502+00
83	account_roles	{"role": "LECTURER", "account_id": 25}	2026-08-22 09:08:50.623502+00
84	account_roles	{"role": "LECTURER", "account_id": 26}	2026-08-22 09:08:50.623502+00
85	account_roles	{"role": "LECTURER", "account_id": 27}	2026-08-22 09:08:50.623502+00
86	account_roles	{"role": "LECTURER", "account_id": 28}	2026-08-22 09:08:50.623502+00
87	account_roles	{"role": "LECTURER", "account_id": 31}	2026-08-22 09:08:50.623502+00
88	account_roles	{"role": "STUDENT", "account_id": 32}	2026-08-22 09:08:50.623502+00
89	account_roles	{"role": "LECTURER", "account_id": 1085}	2026-08-22 09:08:50.623502+00
90	account_roles	{"role": "LECTURER", "account_id": 1090}	2026-08-22 09:08:50.623502+00
91	account_roles	{"role": "MANAGER", "account_id": 1172}	2026-08-22 09:08:50.623502+00
92	account_roles	{"role": "LECTURER", "account_id": 1781}	2026-08-22 09:08:50.623502+00
93	account_roles	{"role": "LECTURER", "account_id": 88}	2026-08-22 09:08:50.623502+00
94	account_roles	{"role": "LECTURER", "account_id": 1786}	2026-08-22 09:08:50.623502+00
95	account_roles	{"role": "MANAGER", "account_id": 1868}	2026-08-22 09:08:50.623502+00
96	account_roles	{"role": "LECTURER", "account_id": 93}	2026-08-22 09:08:50.623502+00
97	account_roles	{"role": "MANAGER", "account_id": 175}	2026-08-22 09:08:50.623502+00
98	account_roles	{"role": "LECTURER", "account_id": 853}	2026-08-22 09:08:50.623502+00
99	account_roles	{"role": "LECTURER", "account_id": 858}	2026-08-22 09:08:50.623502+00
100	account_roles	{"role": "MANAGER", "account_id": 940}	2026-08-22 09:08:50.623502+00
105	account_roles	{"role": "LECTURER", "account_id": 1554}	2026-08-22 09:08:50.623502+00
106	account_roles	{"role": "MANAGER", "account_id": 1636}	2026-08-22 09:08:50.623502+00
107	account_roles	{"role": "LECTURER", "account_id": 1317}	2026-08-22 09:08:50.623502+00
108	account_roles	{"role": "LECTURER", "account_id": 1322}	2026-08-22 09:08:50.623502+00
109	lecturers	{"id": 1, "account_id": 3, "lecturer_code": "GV-PHUONG-LHK"}	2026-08-22 09:08:50.623502+00
110	lecturers	{"id": 2, "account_id": 4, "lecturer_code": "GV-DUC-DNM"}	2026-08-22 09:08:50.623502+00
111	lecturers	{"id": 3, "account_id": 5, "lecturer_code": "GV-VAN-TTN"}	2026-08-22 09:08:50.623502+00
112	lecturers	{"id": 4, "account_id": 6, "lecturer_code": "GV-TAM-PM"}	2026-08-22 09:08:50.623502+00
113	lecturers	{"id": 5, "account_id": 7, "lecturer_code": "GV-NHAN-DT"}	2026-08-22 09:08:50.623502+00
114	lecturers	{"id": 6, "account_id": 8, "lecturer_code": "GV-PHUC-NT"}	2026-08-22 09:08:50.623502+00
115	lecturers	{"id": 7, "account_id": 9, "lecturer_code": "GV-SANG-NM"}	2026-08-22 09:08:50.623502+00
116	lecturers	{"id": 8, "account_id": 10, "lecturer_code": "GV-HOANG-NT"}	2026-08-22 09:08:50.623502+00
117	lecturers	{"id": 9, "account_id": 11, "lecturer_code": "GV-LONG-T"}	2026-08-22 09:08:50.623502+00
118	lecturers	{"id": 10, "account_id": 12, "lecturer_code": "GV-TAI-NT"}	2026-08-22 09:08:50.623502+00
119	lecturers	{"id": 11, "account_id": 13, "lecturer_code": "GV-LAM-NN"}	2026-08-22 09:08:50.623502+00
120	lecturers	{"id": 12, "account_id": 14, "lecturer_code": "GV-THONG-NT"}	2026-08-22 09:08:50.623502+00
121	lecturers	{"id": 13, "account_id": 15, "lecturer_code": "GV-AN-NDH"}	2026-08-22 09:08:50.623502+00
122	lecturers	{"id": 14, "account_id": 16, "lecturer_code": "GV-DUONG-VTT"}	2026-08-22 09:08:50.623502+00
123	lecturers	{"id": 15, "account_id": 17, "lecturer_code": "GV-HUNG-LD"}	2026-08-22 09:08:50.623502+00
124	lecturers	{"id": 16, "account_id": 18, "lecturer_code": "GV-NGUYEN-TT"}	2026-08-22 09:08:50.623502+00
125	lecturers	{"id": 17, "account_id": 19, "lecturer_code": "GV-KHANH-KT"}	2026-08-22 09:08:50.623502+00
126	lecturers	{"id": 18, "account_id": 20, "lecturer_code": "GV-HUONG-NTC"}	2026-08-22 09:08:50.623502+00
127	lecturers	{"id": 19, "account_id": 21, "lecturer_code": "GV-MINH-TTH"}	2026-08-22 09:08:50.623502+00
128	lecturers	{"id": 20, "account_id": 22, "lecturer_code": "GV-THINH-DP"}	2026-08-22 09:08:50.623502+00
129	lecturers	{"id": 21, "account_id": 23, "lecturer_code": "GV-QUYNH-TNN"}	2026-08-22 09:08:50.623502+00
130	lecturers	{"id": 22, "account_id": 24, "lecturer_code": "GV-TRI-PT"}	2026-08-22 09:08:50.623502+00
131	lecturers	{"id": 23, "account_id": 25, "lecturer_code": "GV-CHI-LTQ"}	2026-08-22 09:08:50.623502+00
132	lecturers	{"id": 24, "account_id": 26, "lecturer_code": "GV-VU-LNS"}	2026-08-22 09:08:50.623502+00
133	lecturers	{"id": 25, "account_id": 27, "lecturer_code": "GV-TRI-PM"}	2026-08-22 09:08:50.623502+00
134	lecturers	{"id": 26, "account_id": 28, "lecturer_code": "GV-HUY-NX"}	2026-08-22 09:08:50.623502+00
135	lecturers	{"id": 27, "account_id": 31, "lecturer_code": "GV01"}	2026-08-22 09:08:50.623502+00
136	lecturers	{"id": 331, "account_id": 577, "lecturer_code": "GVIB6888C19"}	2026-08-22 09:08:50.623502+00
137	lecturers	{"id": 333, "account_id": 582, "lecturer_code": "GVDDF44FCBF"}	2026-08-22 09:08:50.623502+00
138	lecturers	{"id": 610, "account_id": 1085, "lecturer_code": "GVI5773C4AC"}	2026-08-22 09:08:50.623502+00
139	lecturers	{"id": 612, "account_id": 1090, "lecturer_code": "GVD8E720508"}	2026-08-22 09:08:50.623502+00
140	lecturers	{"id": 68, "account_id": 88, "lecturer_code": "GVI8D14C7F2"}	2026-08-22 09:08:50.623502+00
141	lecturers	{"id": 70, "account_id": 93, "lecturer_code": "GVD989A54DB"}	2026-08-22 09:08:50.623502+00
142	lecturers	{"id": 967, "account_id": 1781, "lecturer_code": "GVI1ED0E33D"}	2026-08-22 09:08:50.623502+00
143	lecturers	{"id": 969, "account_id": 1786, "lecturer_code": "GVDB76040EC"}	2026-08-22 09:08:50.623502+00
144	lecturers	{"id": 217, "account_id": 350, "lecturer_code": "GVI65F38067"}	2026-08-22 09:08:50.623502+00
145	lecturers	{"id": 219, "account_id": 355, "lecturer_code": "GVDFE9D2C7A"}	2026-08-22 09:08:50.623502+00
146	lecturers	{"id": 491, "account_id": 853, "lecturer_code": "GVI36B9697D"}	2026-08-22 09:08:50.623502+00
147	lecturers	{"id": 493, "account_id": 858, "lecturer_code": "GVD5D91FC71"}	2026-08-22 09:08:50.623502+00
148	lecturers	{"id": 848, "account_id": 1549, "lecturer_code": "GVIB6E659E5"}	2026-08-22 09:08:50.623502+00
149	lecturers	{"id": 850, "account_id": 1554, "lecturer_code": "GVD3822C4FE"}	2026-08-22 09:08:50.623502+00
150	lecturers	{"id": 729, "account_id": 1317, "lecturer_code": "GVIB38C6EB5"}	2026-08-22 09:08:50.623502+00
151	lecturers	{"id": 731, "account_id": 1322, "lecturer_code": "GVD8CAEA377"}	2026-08-22 09:08:50.623502+00
152	students	{"id": 1, "account_id": 32, "student_code": "SV001"}	2026-08-22 09:08:50.623502+00
153	majors	{"id": 1, "code": "SE", "name": "Software Engineering"}	2026-08-22 09:08:50.623502+00
154	project_supervisors	{"project_id": 33, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
155	project_supervisors	{"project_id": 34, "lecturer_id": 2, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
156	project_supervisors	{"project_id": 34, "lecturer_id": 3, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
157	project_supervisors	{"project_id": 35, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
158	project_supervisors	{"project_id": 36, "lecturer_id": 5, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
159	project_supervisors	{"project_id": 37, "lecturer_id": 6, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
160	project_supervisors	{"project_id": 38, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
161	project_supervisors	{"project_id": 39, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
162	project_supervisors	{"project_id": 40, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
163	project_supervisors	{"project_id": 41, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
164	project_supervisors	{"project_id": 41, "lecturer_id": 8, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
165	project_supervisors	{"project_id": 42, "lecturer_id": 3, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
166	project_supervisors	{"project_id": 43, "lecturer_id": 9, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
167	project_supervisors	{"project_id": 44, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
168	project_supervisors	{"project_id": 45, "lecturer_id": 10, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
169	project_supervisors	{"project_id": 46, "lecturer_id": 5, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
170	project_supervisors	{"project_id": 47, "lecturer_id": 5, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
171	project_supervisors	{"project_id": 48, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
172	project_supervisors	{"project_id": 49, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
173	project_supervisors	{"project_id": 50, "lecturer_id": 5, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
174	project_supervisors	{"project_id": 51, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
175	project_supervisors	{"project_id": 52, "lecturer_id": 11, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
176	project_supervisors	{"project_id": 53, "lecturer_id": 9, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
177	project_supervisors	{"project_id": 54, "lecturer_id": 12, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
178	project_supervisors	{"project_id": 55, "lecturer_id": 13, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
179	project_supervisors	{"project_id": 56, "lecturer_id": 14, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
180	project_supervisors	{"project_id": 57, "lecturer_id": 15, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
181	project_supervisors	{"project_id": 58, "lecturer_id": 16, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
182	project_supervisors	{"project_id": 59, "lecturer_id": 17, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
183	project_supervisors	{"project_id": 60, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
184	project_supervisors	{"project_id": 61, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
185	project_supervisors	{"project_id": 62, "lecturer_id": 13, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
186	project_supervisors	{"project_id": 63, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
187	project_supervisors	{"project_id": 64, "lecturer_id": 19, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
188	project_supervisors	{"project_id": 65, "lecturer_id": 4, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
189	project_supervisors	{"project_id": 66, "lecturer_id": 20, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
190	project_supervisors	{"project_id": 67, "lecturer_id": 21, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
191	project_supervisors	{"project_id": 68, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
192	project_supervisors	{"project_id": 69, "lecturer_id": 12, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
193	project_supervisors	{"project_id": 70, "lecturer_id": 20, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
194	project_supervisors	{"project_id": 71, "lecturer_id": 22, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
195	project_supervisors	{"project_id": 72, "lecturer_id": 21, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
196	project_supervisors	{"project_id": 73, "lecturer_id": 9, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
197	project_supervisors	{"project_id": 74, "lecturer_id": 23, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
198	project_supervisors	{"project_id": 75, "lecturer_id": 10, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
199	project_supervisors	{"project_id": 76, "lecturer_id": 10, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
200	project_supervisors	{"project_id": 77, "lecturer_id": 6, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
201	project_supervisors	{"project_id": 77, "lecturer_id": 24, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
202	project_supervisors	{"project_id": 78, "lecturer_id": 25, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
203	project_supervisors	{"project_id": 78, "lecturer_id": 2, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
204	project_supervisors	{"project_id": 79, "lecturer_id": 13, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
205	project_supervisors	{"project_id": 80, "lecturer_id": 15, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
206	project_supervisors	{"project_id": 81, "lecturer_id": 15, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
207	project_supervisors	{"project_id": 82, "lecturer_id": 12, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
208	project_supervisors	{"project_id": 83, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
209	project_supervisors	{"project_id": 84, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
210	project_supervisors	{"project_id": 85, "lecturer_id": 11, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
211	project_supervisors	{"project_id": 86, "lecturer_id": 11, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
212	project_supervisors	{"project_id": 87, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
213	project_supervisors	{"project_id": 88, "lecturer_id": 3, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
214	project_supervisors	{"project_id": 89, "lecturer_id": 8, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
215	project_supervisors	{"project_id": 90, "lecturer_id": 26, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
216	project_supervisors	{"project_id": 90, "lecturer_id": 10, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
217	project_supervisors	{"project_id": 91, "lecturer_id": 23, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
218	project_supervisors	{"project_id": 92, "lecturer_id": 5, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
219	project_supervisors	{"project_id": 93, "lecturer_id": 2, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
220	project_supervisors	{"project_id": 93, "lecturer_id": 3, "supervisor_type": "CO"}	2026-08-22 09:08:50.623502+00
221	project_supervisors	{"project_id": 94, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
222	project_supervisors	{"project_id": 95, "lecturer_id": 11, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
223	project_supervisors	{"project_id": 96, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
224	project_supervisors	{"project_id": 97, "lecturer_id": 1, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
225	project_supervisors	{"project_id": 98, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
226	project_supervisors	{"project_id": 99, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
227	project_supervisors	{"project_id": 100, "lecturer_id": 7, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
228	project_supervisors	{"project_id": 101, "lecturer_id": 20, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
229	project_supervisors	{"project_id": 102, "lecturer_id": 10, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
230	project_supervisors	{"project_id": 103, "lecturer_id": 20, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
231	project_supervisors	{"project_id": 104, "lecturer_id": 9, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
232	project_supervisors	{"project_id": 105, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
233	project_supervisors	{"project_id": 106, "lecturer_id": 18, "supervisor_type": "MAIN"}	2026-08-22 09:08:50.623502+00
234	projects	{"id": 33, "code": "SU26SE094", "title": "SAGA: Hệ thống đánh giá liên tục dựa trên Đồ thị Hoạt động Sinh viên cho học phần Kỹ thuật Phần mềm theo PBL", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
235	projects	{"id": 34, "code": "SU26SE068", "title": "Hệ thống quản lý rửa xe ô tô tự động thông minh với đặt lịch trước và chương trình khách hàng thân thiết", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
236	projects	{"id": 35, "code": "SU26SE043", "title": "Hệ thống Mô phỏng Phỏng vấn và Đánh giá Năng lực ứng dụng Trí tuệ Nhân tạo", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
237	projects	{"id": 36, "code": "SU26SE021", "title": "Nền tảng hỗ trợ thiết kế và thi công quán cà phê thông minh ứng dụng AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
238	projects	{"id": 37, "code": "SU26SE091", "title": "FurniSpace – Xây dựng hệ thống tương tác 3D cho thiết kế cửa hàng bán lẻ và cung cấp giải pháp nội thất kèm theo", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
239	projects	{"id": 38, "code": "SU26SE015", "title": "Không gian lưu trữ - Website cho phép đăng tải, tìm kiếm kho bãi và quản lí sau khi thuê", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
240	projects	{"id": 39, "code": "SU26SE093", "title": "FengDesk AI – Nền tảng thương mại điện tử về cây phong thủy kết hợp hệ thống đề xuất AI cho không gian làm việc", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
241	projects	{"id": 40, "code": "SU26SE111", "title": "Rogue-kie: Hiểm Họa Không Gian", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
242	projects	{"id": 41, "code": "SU26SE020", "title": "Nền tảng học tập trải nghiệm hỗ trợ AI với khả năng tự động tạo hồ sơ năng lực và nội dung đa phương tiện cho Obox STEAM", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
243	projects	{"id": 42, "code": "SU26SE112", "title": "WarpTalk - Nền tảng Dịch Giọng Nói Tự Nhiên Đa Ngôn Ngữ Theo Thời Gian Thực với Công Nghệ Sao Chép Giọng Nói và với sự hỗ trợ của AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
244	projects	{"id": 43, "code": "SU26SE003", "title": "GodotXR: Ứng dụng thực tế ảo hỗ trợ học tập cho trẻ chậm nói", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
245	projects	{"id": 44, "code": "SU26SE061", "title": "81 Ngày và Đêm – Game bắn súng góc nhìn thứ nhất tái hiện chiến dịch bảo vệ Thành Cổ Quảng Trị 1972", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
246	projects	{"id": 45, "code": "SU26SE041", "title": "Hệ thống thông minh quản lý thực nghiệm ươm trồng rau màu cho trường Đại học về Nông nghiệp", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
247	projects	{"id": 46, "code": "SU26SE002", "title": "Nền tảng tư vấn bất động sản ứng dụng AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
248	projects	{"id": 47, "code": "SU26SE010", "title": "Hệ thống đặt lịch & công cụ thử móng thông minh", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
249	projects	{"id": 48, "code": "SU26SE018", "title": "Thiết kế và triển khai hệ thống mô phỏng quy trình tuyển dụng doanh nghiệp ứng dụng AI với mô hình Phòng phỏng vấn ảo cho sinh viên ngành Kỹ thuật Phần mềm", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
250	projects	{"id": 49, "code": "SU26SE092", "title": "IceBot – Thiết kế và triển khai hệ thống bán kem tự động đa địa điểm tích hợp tay robot", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
251	projects	{"id": 50, "code": "SU26SE011", "title": "Robot di động tự hành tích hợp AI phục vụ điều hướng thông minh và hỗ trợ mua sắm trong môi trường siêu thị", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
252	projects	{"id": 51, "code": "SU26SE014", "title": "Nền tảng Chăm sóc Hoa Lan", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
253	projects	{"id": 52, "code": "SU26SE115", "title": "DaiPhat – Hệ thống quản lý bán vé số", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
254	projects	{"id": 53, "code": "SU26SE080", "title": "Xây dựng hệ thống quản lý chuỗi cung ứng ký gửi xuyên biên giới tích hợp AI Agent", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
255	projects	{"id": 54, "code": "SU26SE016", "title": "Taxmate - Nền tảng hỗ trợ nghĩa vụ thuế và quản lý bán hàng cho hộ kinh doanh nhỏ", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
256	projects	{"id": 55, "code": "SU26SE106", "title": "Xây dựng Hệ thống Quản lý Vận hành Nhân viên cho Công ty TNHH Vibe Solutions", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
257	projects	{"id": 56, "code": "SU26SE084", "title": "AlgoFlow: Trình mô phỏng tư duy tính toán trực quan với gợi ý của AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
258	projects	{"id": 57, "code": "SU26SE023", "title": "VietStage - Nghệ Sĩ Ảo Dạy Nhạc Cụ Dân Tộc Với Học Tập Dựa Trên Trò Chơi", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
259	projects	{"id": 58, "code": "SU26SE058", "title": "HỆ SINH THÁI TƯƠNG TÁC VÀ PHẢN HỒI DỊCH VỤ ĐÔ THỊ", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
260	projects	{"id": 59, "code": "SU26SE096", "title": "Hệ thống quản lý kinh doanh thuê và cho thuê lại bất động sản", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
261	projects	{"id": 60, "code": "SU26SE167", "title": "Chatbot tư vấn mua sắm thông minh tích hợp RAG trên catalog sản phẩm thực tế", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
262	projects	{"id": 61, "code": "SU26SE069", "title": "EduGuard: Nền tảng điểm danh tự động và giám thị thi trực tuyến hỗ trợ bởi AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
263	projects	{"id": 62, "code": "SU26SE104", "title": "Xây dựng Hệ thống Hồ sơ Đào tạo Điện tử cho Học viện Hàng không", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
264	projects	{"id": 63, "code": "SU26SE070", "title": "Trợ lý y khoa thông minh", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
265	projects	{"id": 64, "code": "SU26SE082", "title": "Resilience Housing Supply - Nền tảng kết nối và điều phối nguồn cung nhà ở xã hội thông minh", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
266	projects	{"id": 65, "code": "SU26SE102", "title": "IQGS – Hệ thống Sinh Câu hỏi Phỏng vấn sử dụng RAG và LLM", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
267	projects	{"id": 66, "code": "SU26SE071", "title": "Nền tảng cứu trợ và phân phối thực phẩm", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
268	projects	{"id": 67, "code": "SU26SE047", "title": "Nền tảng kết nối người bán đồ gia dụng cũ với đơn vị thu mua", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
269	projects	{"id": 68, "code": "SU26SE165", "title": "Ứng dụng hướng dẫn tham quan di tích lịch sử, bảo tàng thông qua thuyết minh tự động và AR", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
270	projects	{"id": 69, "code": "SU26SE072", "title": "Nền tảng chia sẻ kiến thức giữa các đồng nghiệp trong giới học thuật", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
271	projects	{"id": 70, "code": "SU26SE063", "title": "BoardVerse - Nền tảng Vận hành và Ghép đội dành cho Quán Board Game", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
272	projects	{"id": 71, "code": "SU26SE170", "title": "Rancour - Game 3D nhập vai góc nhìn thứ ba", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
273	projects	{"id": 72, "code": "SU26SE046", "title": "Hệ thống quản lý tiếp nhận và phân loại quần áo cũ cho từ thiện và tái chế", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
274	projects	{"id": 73, "code": "SU26SE079", "title": "Hệ thống Quản lý Dự án Xây dựng tích hợp AI – Nền tảng thông minh cho quản lý vật tư, tiến độ và nhân sự", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
275	projects	{"id": 74, "code": "SU26SE035", "title": "EvidencePilot – Nền tảng AI hỗ trợ lập bản đồ bằng chứng nghiên cứu và truy vết trích dẫn", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
276	projects	{"id": 75, "code": "SU26SE045", "title": "Hệ thống quản lý lập kế hoạch và phân bổ tài nguyên trại thực nghiệm lâm nghiệp tích hợp AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
277	projects	{"id": 76, "code": "SU26SE039", "title": "Nền tảng kết nối phòng trà âm nhạc và người nghe có tích hợp AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
1028	audit_events	{"id": 721, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 1, "entity_id": "1", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:42:10.994618+00:00"}	2026-08-22 09:08:50.623502+00
278	projects	{"id": 77, "code": "SU26SE169", "title": "GreenSlot — Nền tảng cho thuê vườn canh tác thẳng đứng tại đô thị tích hợp giám sát IoT và dịch vụ chăm sóc cây trồng tại chỗ", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
279	projects	{"id": 78, "code": "SU26SE053", "title": "Hệ thống quản lý đề tài nghiên cứu khoa học cấp Trường đại học FPT", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
280	projects	{"id": 79, "code": "SU26SE105", "title": "Xây dựng Hệ thống Quản lý Năng định Giảng viên cho Học viện Hàng không", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
281	projects	{"id": 80, "code": "SU26SE026", "title": "FinViet – Ứng Dụng Theo Dõi Tài Chính Cá Nhân Thông Minh và Tư Vấn Chi Tiêu Bằng AI cho Giới Trẻ Việt Nam", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
282	projects	{"id": 81, "code": "SU26SE083", "title": "SoloDesk – Hệ Thống Quản Lý Khách Hàng và Hợp Đồng Thông Minh Dành Cho Chuyên Gia Dịch Vụ Độc Lập Việt Nam", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
283	projects	{"id": 82, "code": "SU26SE089", "title": "Nền tảng kết nối khách hàng với quầy ăn tại chợ đêm dựa theo sở thích cá nhân bằng công cụ AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
284	projects	{"id": 83, "code": "SU26SE049", "title": "Ứng dụng báo cáo điểm rác thải và ô nhiễm môi trường", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
285	projects	{"id": 84, "code": "SU26SE017", "title": "Thiết kế và phát triển hệ thống CDE cho các dự án xây dựng dân dụng ứng dụng BIM", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
286	projects	{"id": 85, "code": "SU26SE116", "title": "GodotLaunch - Nền tảng phân phối trò chơi cho Godot Engine", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
287	projects	{"id": 86, "code": "SU26SE113", "title": "TaleX - Nền tảng phát triển video truyện tranh và hoạt hình ngắn", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
288	projects	{"id": 87, "code": "SU26SE098", "title": "Nền tảng Số hóa Vận hành và Kết nối Cafe Xe RC", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
289	projects	{"id": 88, "code": "SU26SE028", "title": "Phát triển Hệ thống POS và Điều hành Vận hành Nhà hàng", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
290	projects	{"id": 89, "code": "SU26SE109", "title": "Hệ thống quản lý kho, mượn trả thiết bị và đặt sảnh cho Trường Đại học FPT TP.HCM", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
291	projects	{"id": 90, "code": "SU26SE032", "title": "Family Care – Giải pháp quản lý gia đình số", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
292	projects	{"id": 91, "code": "SU26SE036", "title": "CultureQuest Lite – Nền tảng hành trình di sản và kể chuyện ngắn theo địa điểm cho du lịch văn hóa địa phương", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
293	projects	{"id": 92, "code": "SU26SE081", "title": "Hệ thống AI phân loại thông minh và điều phối luồng bệnh nhân khoa ngoại trú", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
294	projects	{"id": 93, "code": "SU26SE067", "title": "GlowScan — Hệ thống thương mại điện tử Beauty-Tech tích hợp AI phân tích da mặt và tư vấn skincare cá nhân hóa", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
295	projects	{"id": 94, "code": "SU26SE090", "title": "FreshFlow – Nền tảng trung gian thu mua và tối ưu hóa vận chuyển thực phẩm từ chợ đầu mối cho nhà hàng tại TP.HCM", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
296	projects	{"id": 95, "code": "SU26SE114", "title": "Waterbus - Hệ thống cung cấp thông tin và đặt vé tham quan trên sông Sài Gòn", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
297	projects	{"id": 96, "code": "SU26SE013", "title": "BookSwapHub - Nền tảng mua bán, trao đổi, đấu giá sách cũ trực tuyến có tích hợp AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
298	projects	{"id": 97, "code": "SU26SE019", "title": "Phát triển hệ thống căng tin thông minh ứng dụng cánh tay robot trong xử lý và phục vụ món ăn", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
299	projects	{"id": 98, "code": "SU26SE057", "title": "Hệ thống hỗ trợ đánh giá bài thi nói tiếng Anh", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
300	projects	{"id": 99, "code": "SU26SE101", "title": "VietRide - Nền tảng đặt vé, định vị và quản lý xe khách", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
301	projects	{"id": 100, "code": "SU26SE027", "title": "ColdChainX - Nền tảng giám sát và quản lý chuỗi lạnh thông minh", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
302	projects	{"id": 101, "code": "SU26SE064", "title": "HabitEvolve - Nền tảng game hóa đa người chơi hỗ trợ cải thiện lối sống", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
303	projects	{"id": 102, "code": "SU26SE038", "title": "Nền tảng chia sẻ và cho thuê lại mặt bằng kinh doanh theo khung thời gian có tích hợp AI", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
304	projects	{"id": 103, "code": "SU26SE065", "title": "CubeNexus - Nền tảng Speedcubing toàn diện quản lý giải đấu trực tiếp và ghép trận trực tuyến", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
305	projects	{"id": 104, "code": "SU26SE001", "title": "Hệ thống quản lý bảo trì pin lithium-ion năng lượng mặt trời – Nền tảng dựa trên model AI để giám sát và bảo trì", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
306	projects	{"id": 105, "code": "SU26SE051", "title": "Tutora — Nền tảng kết nối gia sư K-12 tích hợp AI hỗ trợ tìm gia sư và hướng dẫn giải bài tập", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
307	projects	{"id": 106, "code": "SU26SE166", "title": "Nền tảng kết nối trao đổi kỹ năng", "status": "ACTIVE", "major_id": 1, "semester_id": 1}	2026-08-22 09:08:50.623502+00
308	audit_events	{"id": 1, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T07:55:17.263729+00:00"}	2026-08-22 09:08:50.623502+00
309	audit_events	{"id": 2, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:01.318366+00:00"}	2026-08-22 09:08:50.623502+00
310	audit_events	{"id": 3, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T07:56:01.944819+00:00"}	2026-08-22 09:08:50.623502+00
311	audit_events	{"id": 4, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T07:56:02.230838+00:00"}	2026-08-22 09:08:50.623502+00
312	audit_events	{"id": 5, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:02.498701+00:00"}	2026-08-22 09:08:50.623502+00
313	audit_events	{"id": 6, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:05.444136+00:00"}	2026-08-22 09:08:50.623502+00
314	audit_events	{"id": 7, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:05.876292+00:00"}	2026-08-22 09:08:50.623502+00
315	audit_events	{"id": 8, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "c09aa75f4d4541bcb2047963f1b5c516", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T07:56:07.272883+00:00"}	2026-08-22 09:08:50.623502+00
316	audit_events	{"id": 9, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:10.029045+00:00"}	2026-08-22 09:08:50.623502+00
317	audit_events	{"id": 10, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:11.108905+00:00"}	2026-08-22 09:08:50.623502+00
318	audit_events	{"id": 11, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "3:5", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T07:56:11.319209+00:00"}	2026-08-22 09:08:50.623502+00
319	audit_events	{"id": 12, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "3:5", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T07:56:11.366091+00:00"}	2026-08-22 09:08:50.623502+00
320	audit_events	{"id": 13, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "3:5", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T07:56:11.402141+00:00"}	2026-08-22 09:08:50.623502+00
321	audit_events	{"id": 14, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:11.813041+00:00"}	2026-08-22 09:08:50.623502+00
322	audit_events	{"id": 15, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T07:56:12.39016+00:00"}	2026-08-22 09:08:50.623502+00
323	audit_events	{"id": 16, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:12.70443+00:00"}	2026-08-22 09:08:50.623502+00
324	audit_events	{"id": 17, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T07:56:13.002488+00:00"}	2026-08-22 09:08:50.623502+00
325	audit_events	{"id": 18, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:13.692971+00:00"}	2026-08-22 09:08:50.623502+00
326	audit_events	{"id": 19, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:16.34713+00:00"}	2026-08-22 09:08:50.623502+00
327	audit_events	{"id": 20, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "9", "after_json": {"code": "API-34EFEA76", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:16.605722+00:00"}	2026-08-22 09:08:50.623502+00
328	audit_events	{"id": 21, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "9", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:16.657769+00:00"}	2026-08-22 09:08:50.623502+00
329	audit_events	{"id": 22, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:16.657769+00:00"}	2026-08-22 09:08:50.623502+00
330	audit_events	{"id": 23, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:17.085216+00:00"}	2026-08-22 09:08:50.623502+00
331	audit_events	{"id": 24, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:17.2518+00:00"}	2026-08-22 09:08:50.623502+00
332	audit_events	{"id": 25, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:17.556162+00:00"}	2026-08-22 09:08:50.623502+00
333	audit_events	{"id": 26, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "13", "after_json": {"code": "DURATION-F13B59FE", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:17.573411+00:00"}	2026-08-22 09:08:50.623502+00
334	audit_events	{"id": 27, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "13", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:17.595333+00:00"}	2026-08-22 09:08:50.623502+00
335	audit_events	{"id": 28, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:17.613018+00:00"}	2026-08-22 09:08:50.623502+00
336	audit_events	{"id": 29, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:18.575306+00:00"}	2026-08-22 09:08:50.623502+00
337	audit_events	{"id": 30, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:18.854444+00:00"}	2026-08-22 09:08:50.623502+00
338	audit_events	{"id": 31, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:19.128638+00:00"}	2026-08-22 09:08:50.623502+00
339	audit_events	{"id": 32, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:19.401856+00:00"}	2026-08-22 09:08:50.623502+00
340	audit_events	{"id": 33, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:20.108142+00:00"}	2026-08-22 09:08:50.623502+00
341	audit_events	{"id": 34, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:20.417993+00:00"}	2026-08-22 09:08:50.623502+00
342	audit_events	{"id": 35, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:20.667858+00:00"}	2026-08-22 09:08:50.623502+00
343	audit_events	{"id": 36, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:24.111651+00:00"}	2026-08-22 09:08:50.623502+00
344	audit_events	{"id": 37, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:24.451752+00:00"}	2026-08-22 09:08:50.623502+00
345	audit_events	{"id": 38, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:24.750014+00:00"}	2026-08-22 09:08:50.623502+00
346	audit_events	{"id": 39, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:25.051043+00:00"}	2026-08-22 09:08:50.623502+00
347	audit_events	{"id": 40, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:26.476235+00:00"}	2026-08-22 09:08:50.623502+00
348	audit_events	{"id": 41, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:28.895444+00:00"}	2026-08-22 09:08:50.623502+00
349	audit_events	{"id": 42, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:29.201633+00:00"}	2026-08-22 09:08:50.623502+00
350	audit_events	{"id": 43, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:31.972691+00:00"}	2026-08-22 09:08:50.623502+00
351	audit_events	{"id": 44, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:33.975158+00:00"}	2026-08-22 09:08:50.623502+00
352	audit_events	{"id": 45, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:35.099205+00:00"}	2026-08-22 09:08:50.623502+00
353	audit_events	{"id": 46, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "175", "after_json": {"role": "MANAGER", "email": "operator-1c591b0e@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T07:56:35.295288+00:00"}	2026-08-22 09:08:50.623502+00
354	audit_events	{"id": 47, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "175", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T07:56:35.357015+00:00"}	2026-08-22 09:08:50.623502+00
355	audit_events	{"id": 48, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:35.737201+00:00"}	2026-08-22 09:08:50.623502+00
356	audit_events	{"id": 49, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:36.090044+00:00"}	2026-08-22 09:08:50.623502+00
357	audit_events	{"id": 50, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:38.914233+00:00"}	2026-08-22 09:08:50.623502+00
358	audit_events	{"id": 51, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:39.630099+00:00"}	2026-08-22 09:08:50.623502+00
359	audit_events	{"id": 52, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:42.553495+00:00"}	2026-08-22 09:08:50.623502+00
360	audit_events	{"id": 53, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:42.784323+00:00"}	2026-08-22 09:08:50.623502+00
361	audit_events	{"id": 54, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "4", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T07:56:43.021734+00:00"}	2026-08-22 09:08:50.623502+00
362	audit_events	{"id": 55, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:43.237708+00:00"}	2026-08-22 09:08:50.623502+00
363	audit_events	{"id": 56, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:44.133739+00:00"}	2026-08-22 09:08:50.623502+00
364	audit_events	{"id": 57, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:45.628974+00:00"}	2026-08-22 09:08:50.623502+00
365	audit_events	{"id": 58, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "5", "after_json": {"committee_ids": [4, 5]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:45.670704+00:00"}	2026-08-22 09:08:50.623502+00
366	audit_events	{"id": 59, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:46.016676+00:00"}	2026-08-22 09:08:50.623502+00
367	audit_events	{"id": 60, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "6", "after_json": {"committee_ids": [7]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:46.045837+00:00"}	2026-08-22 09:08:50.623502+00
368	audit_events	{"id": 61, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "6", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:46.0682+00:00"}	2026-08-22 09:08:50.623502+00
369	audit_events	{"id": 62, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:46.386965+00:00"}	2026-08-22 09:08:50.623502+00
370	audit_events	{"id": 63, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:46.759608+00:00"}	2026-08-22 09:08:50.623502+00
371	audit_events	{"id": 64, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:47.543095+00:00"}	2026-08-22 09:08:50.623502+00
372	audit_events	{"id": 65, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:47.859949+00:00"}	2026-08-22 09:08:50.623502+00
373	audit_events	{"id": 66, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T07:56:48.174902+00:00"}	2026-08-22 09:08:50.623502+00
374	audit_events	{"id": 67, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "12", "after_json": {"committee_ids": [22]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:48.199364+00:00"}	2026-08-22 09:08:50.623502+00
375	audit_events	{"id": 68, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:48.778017+00:00"}	2026-08-22 09:08:50.623502+00
376	audit_events	{"id": 69, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T07:56:49.233605+00:00"}	2026-08-22 09:08:50.623502+00
377	audit_events	{"id": 70, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:49.629434+00:00"}	2026-08-22 09:08:50.623502+00
378	audit_events	{"id": 71, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "41", "after_json": {"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:49.640504+00:00"}	2026-08-22 09:08:50.623502+00
379	audit_events	{"id": 72, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "41", "after_json": {"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:49.745753+00:00"}	2026-08-22 09:08:50.623502+00
380	audit_events	{"id": 73, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "41", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:49.762322+00:00"}	2026-08-22 09:08:50.623502+00
381	audit_events	{"id": 74, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T07:56:49.762322+00:00"}	2026-08-22 09:08:50.623502+00
382	audit_events	{"id": 75, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "1", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:52.862334+00:00"}	2026-08-22 09:08:50.623502+00
383	audit_events	{"id": 76, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "1", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:52.89813+00:00"}	2026-08-22 09:08:50.623502+00
384	audit_events	{"id": 77, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "2", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.129239+00:00"}	2026-08-22 09:08:50.623502+00
385	audit_events	{"id": 78, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "2", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.167011+00:00"}	2026-08-22 09:08:50.623502+00
386	audit_events	{"id": 79, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "2", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.190431+00:00"}	2026-08-22 09:08:50.623502+00
387	audit_events	{"id": 80, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "3", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.607532+00:00"}	2026-08-22 09:08:50.623502+00
388	audit_events	{"id": 81, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "14", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 3, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 5, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:53.632485+00:00"}	2026-08-22 09:08:50.623502+00
389	audit_events	{"id": 82, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "3", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.691487+00:00"}	2026-08-22 09:08:50.623502+00
390	audit_events	{"id": 83, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "4", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T07:56:53.946295+00:00"}	2026-08-22 09:08:50.623502+00
391	audit_events	{"id": 84, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "15", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 4, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 7, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T07:56:53.976116+00:00"}	2026-08-22 09:08:50.623502+00
392	audit_events	{"id": 85, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:06.87455+00:00"}	2026-08-22 09:08:50.623502+00
393	audit_events	{"id": 86, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "16", "after_json": {"committee_ids": [25, 26]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:05:06.922249+00:00"}	2026-08-22 09:08:50.623502+00
394	audit_events	{"id": 87, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:07.620358+00:00"}	2026-08-22 09:08:50.623502+00
395	audit_events	{"id": 88, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "17", "after_json": {"committee_ids": [28]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:05:07.648443+00:00"}	2026-08-22 09:08:50.623502+00
396	audit_events	{"id": 89, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "17", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:05:07.674908+00:00"}	2026-08-22 09:08:50.623502+00
397	audit_events	{"id": 90, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:08.391929+00:00"}	2026-08-22 09:08:50.623502+00
398	audit_events	{"id": 91, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:08.767046+00:00"}	2026-08-22 09:08:50.623502+00
399	audit_events	{"id": 92, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:09.713221+00:00"}	2026-08-22 09:08:50.623502+00
400	audit_events	{"id": 93, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:10.124146+00:00"}	2026-08-22 09:08:50.623502+00
401	audit_events	{"id": 94, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:10.501363+00:00"}	2026-08-22 09:08:50.623502+00
402	audit_events	{"id": 95, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "23", "after_json": {"committee_ids": [43]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:05:10.542984+00:00"}	2026-08-22 09:08:50.623502+00
403	audit_events	{"id": 96, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:10.950413+00:00"}	2026-08-22 09:08:50.623502+00
404	audit_events	{"id": 97, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "24", "after_json": {"committee_ids": [46]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:05:10.982471+00:00"}	2026-08-22 09:08:50.623502+00
405	audit_events	{"id": 98, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:40.762632+00:00"}	2026-08-22 09:08:50.623502+00
406	audit_events	{"id": 99, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:05:41.058063+00:00"}	2026-08-22 09:08:50.623502+00
407	audit_events	{"id": 100, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:05:41.276647+00:00"}	2026-08-22 09:08:50.623502+00
408	audit_events	{"id": 101, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:41.499107+00:00"}	2026-08-22 09:08:50.623502+00
409	audit_events	{"id": 102, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:43.473572+00:00"}	2026-08-22 09:08:50.623502+00
410	audit_events	{"id": 103, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:05:43.770199+00:00"}	2026-08-22 09:08:50.623502+00
411	audit_events	{"id": 104, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "389bced1c7cc433ba1cef5bf7ec297d1", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:05:44.89428+00:00"}	2026-08-22 09:08:50.623502+00
412	audit_events	{"id": 105, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:47.07456+00:00"}	2026-08-22 09:08:50.623502+00
413	audit_events	{"id": 106, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:47.607878+00:00"}	2026-08-22 09:08:50.623502+00
414	audit_events	{"id": 107, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "27:10", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:05:47.787094+00:00"}	2026-08-22 09:08:50.623502+00
415	audit_events	{"id": 108, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "27:10", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:05:47.81165+00:00"}	2026-08-22 09:08:50.623502+00
416	audit_events	{"id": 109, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "27:10", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:05:47.831135+00:00"}	2026-08-22 09:08:50.623502+00
417	audit_events	{"id": 110, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:48.034567+00:00"}	2026-08-22 09:08:50.623502+00
418	audit_events	{"id": 111, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:05:48.369744+00:00"}	2026-08-22 09:08:50.623502+00
419	audit_events	{"id": 112, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:48.584116+00:00"}	2026-08-22 09:08:50.623502+00
420	audit_events	{"id": 113, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:05:48.758297+00:00"}	2026-08-22 09:08:50.623502+00
421	audit_events	{"id": 114, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:49.000781+00:00"}	2026-08-22 09:08:50.623502+00
422	audit_events	{"id": 115, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.342039+00:00"}	2026-08-22 09:08:50.623502+00
423	audit_events	{"id": 116, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "51", "after_json": {"code": "API-8B1E0622", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.367899+00:00"}	2026-08-22 09:08:50.623502+00
424	audit_events	{"id": 117, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "51", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.415286+00:00"}	2026-08-22 09:08:50.623502+00
425	audit_events	{"id": 118, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.415286+00:00"}	2026-08-22 09:08:50.623502+00
426	audit_events	{"id": 119, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:53.610059+00:00"}	2026-08-22 09:08:50.623502+00
427	audit_events	{"id": 120, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:53.704068+00:00"}	2026-08-22 09:08:50.623502+00
428	audit_events	{"id": 121, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.88907+00:00"}	2026-08-22 09:08:50.623502+00
429	audit_events	{"id": 122, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "55", "after_json": {"code": "DURATION-F3238129", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.905758+00:00"}	2026-08-22 09:08:50.623502+00
430	audit_events	{"id": 123, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "55", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.922999+00:00"}	2026-08-22 09:08:50.623502+00
431	audit_events	{"id": 124, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:05:53.939125+00:00"}	2026-08-22 09:08:50.623502+00
432	audit_events	{"id": 125, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:54.486428+00:00"}	2026-08-22 09:08:50.623502+00
433	audit_events	{"id": 126, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:54.723902+00:00"}	2026-08-22 09:08:50.623502+00
434	audit_events	{"id": 127, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:54.926089+00:00"}	2026-08-22 09:08:50.623502+00
435	audit_events	{"id": 128, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:55.133227+00:00"}	2026-08-22 09:08:50.623502+00
436	audit_events	{"id": 129, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:55.595839+00:00"}	2026-08-22 09:08:50.623502+00
437	audit_events	{"id": 130, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:55.806204+00:00"}	2026-08-22 09:08:50.623502+00
438	audit_events	{"id": 131, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:56.005936+00:00"}	2026-08-22 09:08:50.623502+00
439	audit_events	{"id": 132, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:58.850132+00:00"}	2026-08-22 09:08:50.623502+00
440	audit_events	{"id": 133, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:59.025352+00:00"}	2026-08-22 09:08:50.623502+00
441	audit_events	{"id": 134, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:59.213124+00:00"}	2026-08-22 09:08:50.623502+00
442	audit_events	{"id": 135, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:59.410942+00:00"}	2026-08-22 09:08:50.623502+00
443	audit_events	{"id": 136, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:59.60737+00:00"}	2026-08-22 09:08:50.623502+00
444	audit_events	{"id": 137, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:05:59.816472+00:00"}	2026-08-22 09:08:50.623502+00
445	audit_events	{"id": 138, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:00.048063+00:00"}	2026-08-22 09:08:50.623502+00
446	audit_events	{"id": 139, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:01.837158+00:00"}	2026-08-22 09:08:50.623502+00
447	audit_events	{"id": 140, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:02.996603+00:00"}	2026-08-22 09:08:50.623502+00
448	audit_events	{"id": 141, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:03.504612+00:00"}	2026-08-22 09:08:50.623502+00
449	audit_events	{"id": 142, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "437", "after_json": {"role": "MANAGER", "email": "operator-788da04a@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:06:03.602805+00:00"}	2026-08-22 09:08:50.623502+00
450	audit_events	{"id": 143, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "437", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:06:03.640564+00:00"}	2026-08-22 09:08:50.623502+00
451	audit_events	{"id": 144, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:03.804454+00:00"}	2026-08-22 09:08:50.623502+00
452	audit_events	{"id": 145, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:04.074126+00:00"}	2026-08-22 09:08:50.623502+00
453	audit_events	{"id": 146, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:05.500239+00:00"}	2026-08-22 09:08:50.623502+00
454	audit_events	{"id": 147, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:05.976343+00:00"}	2026-08-22 09:08:50.623502+00
455	audit_events	{"id": 148, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:08.042121+00:00"}	2026-08-22 09:08:50.623502+00
456	audit_events	{"id": 149, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:08.294862+00:00"}	2026-08-22 09:08:50.623502+00
457	audit_events	{"id": 150, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "28", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:06:08.487397+00:00"}	2026-08-22 09:08:50.623502+00
458	audit_events	{"id": 151, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:08.667863+00:00"}	2026-08-22 09:08:50.623502+00
459	audit_events	{"id": 152, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:09.467344+00:00"}	2026-08-22 09:08:50.623502+00
460	audit_events	{"id": 153, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:10.495656+00:00"}	2026-08-22 09:08:50.623502+00
461	audit_events	{"id": 154, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "29", "after_json": {"committee_ids": [52, 53]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:10.533205+00:00"}	2026-08-22 09:08:50.623502+00
462	audit_events	{"id": 155, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:10.840276+00:00"}	2026-08-22 09:08:50.623502+00
463	audit_events	{"id": 156, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "30", "after_json": {"committee_ids": [55]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:10.867511+00:00"}	2026-08-22 09:08:50.623502+00
464	audit_events	{"id": 157, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "30", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:10.88809+00:00"}	2026-08-22 09:08:50.623502+00
465	audit_events	{"id": 158, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:11.153948+00:00"}	2026-08-22 09:08:50.623502+00
466	audit_events	{"id": 159, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:11.472064+00:00"}	2026-08-22 09:08:50.623502+00
467	audit_events	{"id": 160, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:12.011263+00:00"}	2026-08-22 09:08:50.623502+00
468	audit_events	{"id": 161, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:12.283806+00:00"}	2026-08-22 09:08:50.623502+00
469	audit_events	{"id": 162, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:12.61349+00:00"}	2026-08-22 09:08:50.623502+00
470	audit_events	{"id": 163, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "36", "after_json": {"committee_ids": [70]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:12.645516+00:00"}	2026-08-22 09:08:50.623502+00
471	audit_events	{"id": 164, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:12.956966+00:00"}	2026-08-22 09:08:50.623502+00
472	audit_events	{"id": 165, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "37", "after_json": {"committee_ids": [73]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:12.979596+00:00"}	2026-08-22 09:08:50.623502+00
473	audit_events	{"id": 166, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:13.544868+00:00"}	2026-08-22 09:08:50.623502+00
474	audit_events	{"id": 167, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:13.901599+00:00"}	2026-08-22 09:08:50.623502+00
475	audit_events	{"id": 168, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:14.109564+00:00"}	2026-08-22 09:08:50.623502+00
476	audit_events	{"id": 169, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "83", "after_json": {"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:14.126287+00:00"}	2026-08-22 09:08:50.623502+00
477	audit_events	{"id": 170, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "83", "after_json": {"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:14.286774+00:00"}	2026-08-22 09:08:50.623502+00
478	audit_events	{"id": 171, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "83", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:14.311131+00:00"}	2026-08-22 09:08:50.623502+00
479	audit_events	{"id": 172, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:14.311131+00:00"}	2026-08-22 09:08:50.623502+00
480	audit_events	{"id": 173, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "5", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.167404+00:00"}	2026-08-22 09:08:50.623502+00
481	audit_events	{"id": 174, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "5", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.196605+00:00"}	2026-08-22 09:08:50.623502+00
482	audit_events	{"id": 175, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "6", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.562943+00:00"}	2026-08-22 09:08:50.623502+00
497	audit_events	{"id": 190, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:35.144254+00:00"}	2026-08-22 09:08:50.623502+00
483	audit_events	{"id": 176, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "6", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.612376+00:00"}	2026-08-22 09:08:50.623502+00
484	audit_events	{"id": 177, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "6", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.636307+00:00"}	2026-08-22 09:08:50.623502+00
485	audit_events	{"id": 178, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "7", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.894105+00:00"}	2026-08-22 09:08:50.623502+00
486	audit_events	{"id": 179, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "39", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 7, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 12, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:17.917097+00:00"}	2026-08-22 09:08:50.623502+00
487	audit_events	{"id": 180, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "7", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:17.963681+00:00"}	2026-08-22 09:08:50.623502+00
488	audit_events	{"id": 181, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "8", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:06:18.246396+00:00"}	2026-08-22 09:08:50.623502+00
489	audit_events	{"id": 182, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "40", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 8, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 14, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:06:18.265339+00:00"}	2026-08-22 09:08:50.623502+00
490	audit_events	{"id": 183, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:29.362406+00:00"}	2026-08-22 09:08:50.623502+00
491	audit_events	{"id": 184, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:06:29.669389+00:00"}	2026-08-22 09:08:50.623502+00
492	audit_events	{"id": 185, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:06:29.863963+00:00"}	2026-08-22 09:08:50.623502+00
493	audit_events	{"id": 186, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:30.074558+00:00"}	2026-08-22 09:08:50.623502+00
494	audit_events	{"id": 187, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:32.110324+00:00"}	2026-08-22 09:08:50.623502+00
495	audit_events	{"id": 188, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:06:32.408804+00:00"}	2026-08-22 09:08:50.623502+00
496	audit_events	{"id": 189, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "985085f935124ca4938e7f43f735d9dc", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:06:33.238343+00:00"}	2026-08-22 09:08:50.623502+00
498	audit_events	{"id": 191, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:35.717898+00:00"}	2026-08-22 09:08:50.623502+00
499	audit_events	{"id": 192, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "43:15", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:06:35.900206+00:00"}	2026-08-22 09:08:50.623502+00
500	audit_events	{"id": 193, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "43:15", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:06:35.92043+00:00"}	2026-08-22 09:08:50.623502+00
501	audit_events	{"id": 194, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "43:15", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:06:35.939977+00:00"}	2026-08-22 09:08:50.623502+00
502	audit_events	{"id": 195, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:36.134583+00:00"}	2026-08-22 09:08:50.623502+00
503	audit_events	{"id": 196, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:06:36.539711+00:00"}	2026-08-22 09:08:50.623502+00
504	audit_events	{"id": 197, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:36.729531+00:00"}	2026-08-22 09:08:50.623502+00
505	audit_events	{"id": 198, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:06:36.902782+00:00"}	2026-08-22 09:08:50.623502+00
506	audit_events	{"id": 199, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:37.16493+00:00"}	2026-08-22 09:08:50.623502+00
507	audit_events	{"id": 200, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:38.530693+00:00"}	2026-08-22 09:08:50.623502+00
508	audit_events	{"id": 201, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "93", "after_json": {"code": "API-2B1264C3", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:38.548264+00:00"}	2026-08-22 09:08:50.623502+00
509	audit_events	{"id": 202, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "93", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:38.587156+00:00"}	2026-08-22 09:08:50.623502+00
510	audit_events	{"id": 203, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:38.587156+00:00"}	2026-08-22 09:08:50.623502+00
511	audit_events	{"id": 204, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:38.785784+00:00"}	2026-08-22 09:08:50.623502+00
512	audit_events	{"id": 205, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:38.899201+00:00"}	2026-08-22 09:08:50.623502+00
513	audit_events	{"id": 206, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:39.235669+00:00"}	2026-08-22 09:08:50.623502+00
514	audit_events	{"id": 207, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "97", "after_json": {"code": "DURATION-C7D7D89A", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:39.253491+00:00"}	2026-08-22 09:08:50.623502+00
515	audit_events	{"id": 208, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "97", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:39.275784+00:00"}	2026-08-22 09:08:50.623502+00
516	audit_events	{"id": 209, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:06:39.290746+00:00"}	2026-08-22 09:08:50.623502+00
517	audit_events	{"id": 210, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:39.885601+00:00"}	2026-08-22 09:08:50.623502+00
518	audit_events	{"id": 211, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:40.120556+00:00"}	2026-08-22 09:08:50.623502+00
519	audit_events	{"id": 212, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:40.366326+00:00"}	2026-08-22 09:08:50.623502+00
520	audit_events	{"id": 213, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:40.583241+00:00"}	2026-08-22 09:08:50.623502+00
521	audit_events	{"id": 214, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:41.112146+00:00"}	2026-08-22 09:08:50.623502+00
522	audit_events	{"id": 215, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:41.340941+00:00"}	2026-08-22 09:08:50.623502+00
523	audit_events	{"id": 216, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:41.535392+00:00"}	2026-08-22 09:08:50.623502+00
524	audit_events	{"id": 217, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:44.100691+00:00"}	2026-08-22 09:08:50.623502+00
525	audit_events	{"id": 218, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:44.319313+00:00"}	2026-08-22 09:08:50.623502+00
526	audit_events	{"id": 219, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:44.535407+00:00"}	2026-08-22 09:08:50.623502+00
527	audit_events	{"id": 220, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:44.746474+00:00"}	2026-08-22 09:08:50.623502+00
528	audit_events	{"id": 221, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:44.933849+00:00"}	2026-08-22 09:08:50.623502+00
529	audit_events	{"id": 222, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:45.129686+00:00"}	2026-08-22 09:08:50.623502+00
530	audit_events	{"id": 223, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:45.350351+00:00"}	2026-08-22 09:08:50.623502+00
531	audit_events	{"id": 224, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:47.255144+00:00"}	2026-08-22 09:08:50.623502+00
532	audit_events	{"id": 225, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:48.677458+00:00"}	2026-08-22 09:08:50.623502+00
533	audit_events	{"id": 226, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:49.164303+00:00"}	2026-08-22 09:08:50.623502+00
534	audit_events	{"id": 227, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "664", "after_json": {"role": "MANAGER", "email": "operator-da2ccb54@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:06:49.284741+00:00"}	2026-08-22 09:08:50.623502+00
535	audit_events	{"id": 228, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "664", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:06:49.317251+00:00"}	2026-08-22 09:08:50.623502+00
536	audit_events	{"id": 229, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:49.48831+00:00"}	2026-08-22 09:08:50.623502+00
537	audit_events	{"id": 230, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:49.704718+00:00"}	2026-08-22 09:08:50.623502+00
538	audit_events	{"id": 231, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:51.001361+00:00"}	2026-08-22 09:08:50.623502+00
539	audit_events	{"id": 232, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:51.493988+00:00"}	2026-08-22 09:08:50.623502+00
540	audit_events	{"id": 233, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:54.167227+00:00"}	2026-08-22 09:08:50.623502+00
541	audit_events	{"id": 234, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:54.413404+00:00"}	2026-08-22 09:08:50.623502+00
542	audit_events	{"id": 235, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "44", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:06:54.637559+00:00"}	2026-08-22 09:08:50.623502+00
543	audit_events	{"id": 236, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:54.816646+00:00"}	2026-08-22 09:08:50.623502+00
544	audit_events	{"id": 237, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:06:57.069918+00:00"}	2026-08-22 09:08:50.623502+00
545	audit_events	{"id": 238, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:00.762003+00:00"}	2026-08-22 09:08:50.623502+00
546	audit_events	{"id": 239, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "45", "after_json": {"committee_ids": [79, 80]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:00.794644+00:00"}	2026-08-22 09:08:50.623502+00
547	audit_events	{"id": 240, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:01.099901+00:00"}	2026-08-22 09:08:50.623502+00
548	audit_events	{"id": 241, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "46", "after_json": {"committee_ids": [82]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:01.124847+00:00"}	2026-08-22 09:08:50.623502+00
549	audit_events	{"id": 242, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "46", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:01.144602+00:00"}	2026-08-22 09:08:50.623502+00
550	audit_events	{"id": 243, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:01.42112+00:00"}	2026-08-22 09:08:50.623502+00
551	audit_events	{"id": 244, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:01.717939+00:00"}	2026-08-22 09:08:50.623502+00
552	audit_events	{"id": 245, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:02.59051+00:00"}	2026-08-22 09:08:50.623502+00
553	audit_events	{"id": 246, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:02.864412+00:00"}	2026-08-22 09:08:50.623502+00
554	audit_events	{"id": 247, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:03.143198+00:00"}	2026-08-22 09:08:50.623502+00
555	audit_events	{"id": 248, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "52", "after_json": {"committee_ids": [97]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:03.168161+00:00"}	2026-08-22 09:08:50.623502+00
556	audit_events	{"id": 249, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:07:03.537506+00:00"}	2026-08-22 09:08:50.623502+00
557	audit_events	{"id": 250, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "53", "after_json": {"committee_ids": [100]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:03.572142+00:00"}	2026-08-22 09:08:50.623502+00
558	audit_events	{"id": 251, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:07:04.262606+00:00"}	2026-08-22 09:08:50.623502+00
559	audit_events	{"id": 252, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:07:05.181526+00:00"}	2026-08-22 09:08:50.623502+00
560	audit_events	{"id": 253, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:07:05.499165+00:00"}	2026-08-22 09:08:50.623502+00
561	audit_events	{"id": 254, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "125", "after_json": {"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:07:05.51429+00:00"}	2026-08-22 09:08:50.623502+00
562	audit_events	{"id": 255, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "125", "after_json": {"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:07:05.639768+00:00"}	2026-08-22 09:08:50.623502+00
563	audit_events	{"id": 256, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "125", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:07:05.659861+00:00"}	2026-08-22 09:08:50.623502+00
564	audit_events	{"id": 257, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:07:05.659861+00:00"}	2026-08-22 09:08:50.623502+00
565	audit_events	{"id": 258, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "9", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:08.910634+00:00"}	2026-08-22 09:08:50.623502+00
566	audit_events	{"id": 259, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "9", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:08.943396+00:00"}	2026-08-22 09:08:50.623502+00
567	audit_events	{"id": 260, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "10", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:09.388303+00:00"}	2026-08-22 09:08:50.623502+00
568	audit_events	{"id": 261, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "10", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:09.433295+00:00"}	2026-08-22 09:08:50.623502+00
569	audit_events	{"id": 262, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "10", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:09.460538+00:00"}	2026-08-22 09:08:50.623502+00
570	audit_events	{"id": 263, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "11", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:09.734242+00:00"}	2026-08-22 09:08:50.623502+00
571	audit_events	{"id": 264, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "55", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 11, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 19, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:09.761204+00:00"}	2026-08-22 09:08:50.623502+00
572	audit_events	{"id": 265, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "11", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:09.823568+00:00"}	2026-08-22 09:08:50.623502+00
593	audit_events	{"id": 286, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:12:51.610617+00:00"}	2026-08-22 09:08:50.623502+00
573	audit_events	{"id": 266, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "12", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:07:10.009344+00:00"}	2026-08-22 09:08:50.623502+00
574	audit_events	{"id": 267, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "56", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 12, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 21, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:07:10.026011+00:00"}	2026-08-22 09:08:50.623502+00
575	audit_events	{"id": 268, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": null, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:09:59.668017+00:00"}	2026-08-22 09:08:50.623502+00
576	audit_events	{"id": 269, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:12.721349+00:00"}	2026-08-22 09:08:50.623502+00
577	audit_events	{"id": 270, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "57", "after_json": {"committee_ids": [103, 104]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:12.77894+00:00"}	2026-08-22 09:08:50.623502+00
578	audit_events	{"id": 271, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:13.17133+00:00"}	2026-08-22 09:08:50.623502+00
579	audit_events	{"id": 272, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "58", "after_json": {"committee_ids": [106]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:13.199279+00:00"}	2026-08-22 09:08:50.623502+00
580	audit_events	{"id": 273, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "58", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:13.224065+00:00"}	2026-08-22 09:08:50.623502+00
581	audit_events	{"id": 274, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:13.652528+00:00"}	2026-08-22 09:08:50.623502+00
582	audit_events	{"id": 275, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:14.014474+00:00"}	2026-08-22 09:08:50.623502+00
583	audit_events	{"id": 276, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:14.797822+00:00"}	2026-08-22 09:08:50.623502+00
584	audit_events	{"id": 277, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:16.178534+00:00"}	2026-08-22 09:08:50.623502+00
585	audit_events	{"id": 278, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:18.529593+00:00"}	2026-08-22 09:08:50.623502+00
586	audit_events	{"id": 279, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "64", "after_json": {"committee_ids": [121]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:18.558521+00:00"}	2026-08-22 09:08:50.623502+00
587	audit_events	{"id": 280, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:18.895548+00:00"}	2026-08-22 09:08:50.623502+00
588	audit_events	{"id": 281, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "65", "after_json": {"committee_ids": [124]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:18.949237+00:00"}	2026-08-22 09:08:50.623502+00
589	audit_events	{"id": 282, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:10:19.388551+00:00"}	2026-08-22 09:08:50.623502+00
590	audit_events	{"id": 283, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "66", "after_json": {"committee_ids": [127]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:10:19.412057+00:00"}	2026-08-22 09:08:50.623502+00
591	audit_events	{"id": 284, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:51.155727+00:00"}	2026-08-22 09:08:50.623502+00
592	audit_events	{"id": 285, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:12:51.440205+00:00"}	2026-08-22 09:08:50.623502+00
594	audit_events	{"id": 287, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:51.795475+00:00"}	2026-08-22 09:08:50.623502+00
595	audit_events	{"id": 288, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:12:54.000256+00:00"}	2026-08-22 09:08:50.623502+00
596	audit_events	{"id": 289, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:12:54.297597+00:00"}	2026-08-22 09:08:50.623502+00
597	audit_events	{"id": 290, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "d1f78fe833044563ac1b0fa304453d2f", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:12:55.332511+00:00"}	2026-08-22 09:08:50.623502+00
598	audit_events	{"id": 291, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:57.213585+00:00"}	2026-08-22 09:08:50.623502+00
599	audit_events	{"id": 292, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:57.836829+00:00"}	2026-08-22 09:08:50.623502+00
600	audit_events	{"id": 293, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "69:20", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:12:58.05847+00:00"}	2026-08-22 09:08:50.623502+00
601	audit_events	{"id": 294, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "69:20", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:12:58.087284+00:00"}	2026-08-22 09:08:50.623502+00
602	audit_events	{"id": 295, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "69:20", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:12:58.116999+00:00"}	2026-08-22 09:08:50.623502+00
603	audit_events	{"id": 296, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:58.369013+00:00"}	2026-08-22 09:08:50.623502+00
604	audit_events	{"id": 297, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:12:58.88311+00:00"}	2026-08-22 09:08:50.623502+00
605	audit_events	{"id": 298, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:12:59.27422+00:00"}	2026-08-22 09:08:50.623502+00
606	audit_events	{"id": 299, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:12:59.621597+00:00"}	2026-08-22 09:08:50.623502+00
607	audit_events	{"id": 300, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:00.029502+00:00"}	2026-08-22 09:08:50.623502+00
608	audit_events	{"id": 301, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:04.668511+00:00"}	2026-08-22 09:08:50.623502+00
609	audit_events	{"id": 302, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "136", "after_json": {"code": "API-A874680A", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:04.698839+00:00"}	2026-08-22 09:08:50.623502+00
610	audit_events	{"id": 303, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "136", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:04.748585+00:00"}	2026-08-22 09:08:50.623502+00
611	audit_events	{"id": 304, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:04.748585+00:00"}	2026-08-22 09:08:50.623502+00
612	audit_events	{"id": 305, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:04.980189+00:00"}	2026-08-22 09:08:50.623502+00
613	audit_events	{"id": 306, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:05.111645+00:00"}	2026-08-22 09:08:50.623502+00
614	audit_events	{"id": 307, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:05.454918+00:00"}	2026-08-22 09:08:50.623502+00
615	audit_events	{"id": 308, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "140", "after_json": {"code": "DURATION-A5A229BE", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:05.478769+00:00"}	2026-08-22 09:08:50.623502+00
616	audit_events	{"id": 309, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "140", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:05.508999+00:00"}	2026-08-22 09:08:50.623502+00
617	audit_events	{"id": 310, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:05.526204+00:00"}	2026-08-22 09:08:50.623502+00
618	audit_events	{"id": 311, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:06.019796+00:00"}	2026-08-22 09:08:50.623502+00
619	audit_events	{"id": 312, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:06.226721+00:00"}	2026-08-22 09:08:50.623502+00
620	audit_events	{"id": 313, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:06.433593+00:00"}	2026-08-22 09:08:50.623502+00
621	audit_events	{"id": 314, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:06.640945+00:00"}	2026-08-22 09:08:50.623502+00
622	audit_events	{"id": 315, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:07.131207+00:00"}	2026-08-22 09:08:50.623502+00
623	audit_events	{"id": 316, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:07.335596+00:00"}	2026-08-22 09:08:50.623502+00
624	audit_events	{"id": 317, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:07.539362+00:00"}	2026-08-22 09:08:50.623502+00
625	audit_events	{"id": 318, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:10.040275+00:00"}	2026-08-22 09:08:50.623502+00
626	audit_events	{"id": 319, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:10.294591+00:00"}	2026-08-22 09:08:50.623502+00
627	audit_events	{"id": 320, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:10.495238+00:00"}	2026-08-22 09:08:50.623502+00
628	audit_events	{"id": 321, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:10.692058+00:00"}	2026-08-22 09:08:50.623502+00
629	audit_events	{"id": 322, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:10.912334+00:00"}	2026-08-22 09:08:50.623502+00
630	audit_events	{"id": 323, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:11.110464+00:00"}	2026-08-22 09:08:50.623502+00
631	audit_events	{"id": 324, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:11.308884+00:00"}	2026-08-22 09:08:50.623502+00
632	audit_events	{"id": 325, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:13.433431+00:00"}	2026-08-22 09:08:50.623502+00
633	audit_events	{"id": 326, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:14.929776+00:00"}	2026-08-22 09:08:50.623502+00
634	audit_events	{"id": 327, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:15.432192+00:00"}	2026-08-22 09:08:50.623502+00
635	audit_events	{"id": 328, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "940", "after_json": {"role": "MANAGER", "email": "operator-e2f2b036@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:13:15.533961+00:00"}	2026-08-22 09:08:50.623502+00
636	audit_events	{"id": 329, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "940", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:13:15.572342+00:00"}	2026-08-22 09:08:50.623502+00
637	audit_events	{"id": 330, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:15.787451+00:00"}	2026-08-22 09:08:50.623502+00
638	audit_events	{"id": 331, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:15.999906+00:00"}	2026-08-22 09:08:50.623502+00
639	audit_events	{"id": 332, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:17.467912+00:00"}	2026-08-22 09:08:50.623502+00
640	audit_events	{"id": 333, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:17.972088+00:00"}	2026-08-22 09:08:50.623502+00
641	audit_events	{"id": 334, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:20.826598+00:00"}	2026-08-22 09:08:50.623502+00
642	audit_events	{"id": 335, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:21.184606+00:00"}	2026-08-22 09:08:50.623502+00
643	audit_events	{"id": 336, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "70", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:13:21.478112+00:00"}	2026-08-22 09:08:50.623502+00
644	audit_events	{"id": 337, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:21.781718+00:00"}	2026-08-22 09:08:50.623502+00
645	audit_events	{"id": 338, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:22.637479+00:00"}	2026-08-22 09:08:50.623502+00
646	audit_events	{"id": 339, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:23.697001+00:00"}	2026-08-22 09:08:50.623502+00
647	audit_events	{"id": 340, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "71", "after_json": {"committee_ids": [133, 134]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:23.728727+00:00"}	2026-08-22 09:08:50.623502+00
648	audit_events	{"id": 341, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:24.03022+00:00"}	2026-08-22 09:08:50.623502+00
649	audit_events	{"id": 342, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "72", "after_json": {"committee_ids": [136]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:24.053391+00:00"}	2026-08-22 09:08:50.623502+00
650	audit_events	{"id": 343, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "72", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:24.068399+00:00"}	2026-08-22 09:08:50.623502+00
651	audit_events	{"id": 344, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:24.344749+00:00"}	2026-08-22 09:08:50.623502+00
652	audit_events	{"id": 345, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:24.715589+00:00"}	2026-08-22 09:08:50.623502+00
653	audit_events	{"id": 346, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:25.408045+00:00"}	2026-08-22 09:08:50.623502+00
654	audit_events	{"id": 347, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:25.661081+00:00"}	2026-08-22 09:08:50.623502+00
655	audit_events	{"id": 348, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:25.976972+00:00"}	2026-08-22 09:08:50.623502+00
656	audit_events	{"id": 349, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "78", "after_json": {"committee_ids": [151]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:25.999277+00:00"}	2026-08-22 09:08:50.623502+00
657	audit_events	{"id": 350, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:26.290078+00:00"}	2026-08-22 09:08:50.623502+00
658	audit_events	{"id": 351, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "79", "after_json": {"committee_ids": [154]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:26.330792+00:00"}	2026-08-22 09:08:50.623502+00
659	audit_events	{"id": 352, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:26.767619+00:00"}	2026-08-22 09:08:50.623502+00
660	audit_events	{"id": 353, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "80", "after_json": {"committee_ids": [157]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:26.808754+00:00"}	2026-08-22 09:08:50.623502+00
661	audit_events	{"id": 354, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:27.327815+00:00"}	2026-08-22 09:08:50.623502+00
662	audit_events	{"id": 355, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:27.765709+00:00"}	2026-08-22 09:08:50.623502+00
663	audit_events	{"id": 356, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:28.04823+00:00"}	2026-08-22 09:08:50.623502+00
664	audit_events	{"id": 420, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:12.567322+00:00"}	2026-08-22 09:08:50.623502+00
665	audit_events	{"id": 357, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "168", "after_json": {"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:28.068888+00:00"}	2026-08-22 09:08:50.623502+00
666	audit_events	{"id": 358, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "168", "after_json": {"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:28.190505+00:00"}	2026-08-22 09:08:50.623502+00
667	audit_events	{"id": 359, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "168", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:28.213853+00:00"}	2026-08-22 09:08:50.623502+00
668	audit_events	{"id": 360, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:28.213853+00:00"}	2026-08-22 09:08:50.623502+00
669	audit_events	{"id": 361, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "13", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:31.651346+00:00"}	2026-08-22 09:08:50.623502+00
670	audit_events	{"id": 362, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "13", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:31.695382+00:00"}	2026-08-22 09:08:50.623502+00
671	audit_events	{"id": 363, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "14", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:31.944857+00:00"}	2026-08-22 09:08:50.623502+00
672	audit_events	{"id": 364, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "14", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:31.99817+00:00"}	2026-08-22 09:08:50.623502+00
673	audit_events	{"id": 365, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "14", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:32.030616+00:00"}	2026-08-22 09:08:50.623502+00
674	audit_events	{"id": 366, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "15", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:32.3675+00:00"}	2026-08-22 09:08:50.623502+00
675	audit_events	{"id": 367, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "82", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 15, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 26, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:32.398298+00:00"}	2026-08-22 09:08:50.623502+00
676	audit_events	{"id": 368, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "15", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:32.465541+00:00"}	2026-08-22 09:08:50.623502+00
677	audit_events	{"id": 369, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "16", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:13:32.702614+00:00"}	2026-08-22 09:08:50.623502+00
678	audit_events	{"id": 370, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "83", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 16, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 28, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:13:32.720203+00:00"}	2026-08-22 09:08:50.623502+00
679	audit_events	{"id": 371, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:48.424848+00:00"}	2026-08-22 09:08:50.623502+00
680	audit_events	{"id": 372, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:13:48.621395+00:00"}	2026-08-22 09:08:50.623502+00
681	audit_events	{"id": 373, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:13:48.777071+00:00"}	2026-08-22 09:08:50.623502+00
682	audit_events	{"id": 374, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:48.941548+00:00"}	2026-08-22 09:08:50.623502+00
683	audit_events	{"id": 375, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:50.827225+00:00"}	2026-08-22 09:08:50.623502+00
684	audit_events	{"id": 376, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:13:51.115389+00:00"}	2026-08-22 09:08:50.623502+00
685	audit_events	{"id": 377, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "19bb5d32157447b69bc9751e43db55d5", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:13:52.110046+00:00"}	2026-08-22 09:08:50.623502+00
686	audit_events	{"id": 378, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:53.905154+00:00"}	2026-08-22 09:08:50.623502+00
687	audit_events	{"id": 379, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:54.413695+00:00"}	2026-08-22 09:08:50.623502+00
688	audit_events	{"id": 380, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "86:25", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:13:54.56546+00:00"}	2026-08-22 09:08:50.623502+00
689	audit_events	{"id": 381, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "86:25", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:13:54.590975+00:00"}	2026-08-22 09:08:50.623502+00
690	audit_events	{"id": 382, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "86:25", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:13:54.615775+00:00"}	2026-08-22 09:08:50.623502+00
691	audit_events	{"id": 383, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:54.819133+00:00"}	2026-08-22 09:08:50.623502+00
692	audit_events	{"id": 384, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:13:55.146128+00:00"}	2026-08-22 09:08:50.623502+00
693	audit_events	{"id": 385, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:55.306905+00:00"}	2026-08-22 09:08:50.623502+00
694	audit_events	{"id": 386, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:13:55.447162+00:00"}	2026-08-22 09:08:50.623502+00
695	audit_events	{"id": 387, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:55.689503+00:00"}	2026-08-22 09:08:50.623502+00
696	audit_events	{"id": 388, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:56.867829+00:00"}	2026-08-22 09:08:50.623502+00
697	audit_events	{"id": 389, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "178", "after_json": {"code": "API-E26FDB4E", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:56.894098+00:00"}	2026-08-22 09:08:50.623502+00
698	audit_events	{"id": 390, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "178", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:56.941776+00:00"}	2026-08-22 09:08:50.623502+00
699	audit_events	{"id": 391, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:56.941776+00:00"}	2026-08-22 09:08:50.623502+00
700	audit_events	{"id": 392, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:57.133937+00:00"}	2026-08-22 09:08:50.623502+00
701	audit_events	{"id": 393, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:57.241424+00:00"}	2026-08-22 09:08:50.623502+00
702	audit_events	{"id": 394, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:57.415837+00:00"}	2026-08-22 09:08:50.623502+00
703	audit_events	{"id": 395, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "182", "after_json": {"code": "DURATION-1D03C342", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:57.43494+00:00"}	2026-08-22 09:08:50.623502+00
704	audit_events	{"id": 396, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "182", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:57.455119+00:00"}	2026-08-22 09:08:50.623502+00
705	audit_events	{"id": 397, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:13:57.471561+00:00"}	2026-08-22 09:08:50.623502+00
706	audit_events	{"id": 398, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:57.968756+00:00"}	2026-08-22 09:08:50.623502+00
707	audit_events	{"id": 399, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:58.209967+00:00"}	2026-08-22 09:08:50.623502+00
708	audit_events	{"id": 400, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:58.418368+00:00"}	2026-08-22 09:08:50.623502+00
709	audit_events	{"id": 401, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:58.617932+00:00"}	2026-08-22 09:08:50.623502+00
710	audit_events	{"id": 402, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:59.081949+00:00"}	2026-08-22 09:08:50.623502+00
711	audit_events	{"id": 403, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:59.282117+00:00"}	2026-08-22 09:08:50.623502+00
712	audit_events	{"id": 404, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:13:59.46967+00:00"}	2026-08-22 09:08:50.623502+00
713	audit_events	{"id": 405, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:01.91765+00:00"}	2026-08-22 09:08:50.623502+00
714	audit_events	{"id": 406, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:02.203146+00:00"}	2026-08-22 09:08:50.623502+00
715	audit_events	{"id": 407, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:02.447326+00:00"}	2026-08-22 09:08:50.623502+00
716	audit_events	{"id": 408, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:02.768069+00:00"}	2026-08-22 09:08:50.623502+00
717	audit_events	{"id": 409, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:03.115858+00:00"}	2026-08-22 09:08:50.623502+00
718	audit_events	{"id": 410, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:03.369268+00:00"}	2026-08-22 09:08:50.623502+00
719	audit_events	{"id": 411, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:03.561084+00:00"}	2026-08-22 09:08:50.623502+00
720	audit_events	{"id": 412, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:05.329413+00:00"}	2026-08-22 09:08:50.623502+00
721	audit_events	{"id": 413, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:06.683555+00:00"}	2026-08-22 09:08:50.623502+00
722	audit_events	{"id": 414, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:08.087633+00:00"}	2026-08-22 09:08:50.623502+00
723	audit_events	{"id": 415, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "1172", "after_json": {"role": "MANAGER", "email": "operator-c971018d@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:14:10.194557+00:00"}	2026-08-22 09:08:50.623502+00
724	audit_events	{"id": 416, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "1172", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:14:10.227485+00:00"}	2026-08-22 09:08:50.623502+00
725	audit_events	{"id": 417, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:10.417383+00:00"}	2026-08-22 09:08:50.623502+00
726	audit_events	{"id": 418, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:10.620582+00:00"}	2026-08-22 09:08:50.623502+00
727	audit_events	{"id": 419, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:12.028479+00:00"}	2026-08-22 09:08:50.623502+00
728	audit_events	{"id": 421, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:14.774323+00:00"}	2026-08-22 09:08:50.623502+00
729	audit_events	{"id": 422, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:14.988315+00:00"}	2026-08-22 09:08:50.623502+00
730	audit_events	{"id": 423, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "87", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:14:15.155229+00:00"}	2026-08-22 09:08:50.623502+00
731	audit_events	{"id": 424, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:15.328225+00:00"}	2026-08-22 09:08:50.623502+00
732	audit_events	{"id": 425, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:16.030545+00:00"}	2026-08-22 09:08:50.623502+00
733	audit_events	{"id": 426, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:17.048181+00:00"}	2026-08-22 09:08:50.623502+00
734	audit_events	{"id": 427, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "88", "after_json": {"committee_ids": [163, 164]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:17.081248+00:00"}	2026-08-22 09:08:50.623502+00
735	audit_events	{"id": 428, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:17.347043+00:00"}	2026-08-22 09:08:50.623502+00
736	audit_events	{"id": 429, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "89", "after_json": {"committee_ids": [166]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:17.369408+00:00"}	2026-08-22 09:08:50.623502+00
737	audit_events	{"id": 430, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "89", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:17.3866+00:00"}	2026-08-22 09:08:50.623502+00
738	audit_events	{"id": 431, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:17.603539+00:00"}	2026-08-22 09:08:50.623502+00
739	audit_events	{"id": 432, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:17.90991+00:00"}	2026-08-22 09:08:50.623502+00
740	audit_events	{"id": 433, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:18.541005+00:00"}	2026-08-22 09:08:50.623502+00
741	audit_events	{"id": 434, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:18.815456+00:00"}	2026-08-22 09:08:50.623502+00
742	audit_events	{"id": 435, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:19.06264+00:00"}	2026-08-22 09:08:50.623502+00
743	audit_events	{"id": 436, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "95", "after_json": {"committee_ids": [181]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:19.089002+00:00"}	2026-08-22 09:08:50.623502+00
744	audit_events	{"id": 437, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:19.389634+00:00"}	2026-08-22 09:08:50.623502+00
745	audit_events	{"id": 438, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "96", "after_json": {"committee_ids": [184]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:19.435103+00:00"}	2026-08-22 09:08:50.623502+00
746	audit_events	{"id": 439, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:19.920317+00:00"}	2026-08-22 09:08:50.623502+00
747	audit_events	{"id": 440, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "97", "after_json": {"committee_ids": [187]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:19.949112+00:00"}	2026-08-22 09:08:50.623502+00
748	audit_events	{"id": 441, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:20.387269+00:00"}	2026-08-22 09:08:50.623502+00
749	audit_events	{"id": 442, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:20.789064+00:00"}	2026-08-22 09:08:50.623502+00
750	audit_events	{"id": 443, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:20.993591+00:00"}	2026-08-22 09:08:50.623502+00
751	audit_events	{"id": 444, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "210", "after_json": {"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:21.005838+00:00"}	2026-08-22 09:08:50.623502+00
752	audit_events	{"id": 445, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "210", "after_json": {"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:21.119037+00:00"}	2026-08-22 09:08:50.623502+00
753	audit_events	{"id": 446, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "210", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:21.142875+00:00"}	2026-08-22 09:08:50.623502+00
754	audit_events	{"id": 447, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:21.142875+00:00"}	2026-08-22 09:08:50.623502+00
782	audit_events	{"id": 473, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:14:45.430092+00:00"}	2026-08-22 09:08:50.623502+00
755	audit_events	{"id": 448, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "17", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.201705+00:00"}	2026-08-22 09:08:50.623502+00
756	audit_events	{"id": 449, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "17", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.232765+00:00"}	2026-08-22 09:08:50.623502+00
757	audit_events	{"id": 450, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "18", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.427874+00:00"}	2026-08-22 09:08:50.623502+00
758	audit_events	{"id": 482, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "224", "after_json": {"code": "DURATION-16B43913", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.567173+00:00"}	2026-08-22 09:08:50.623502+00
759	audit_events	{"id": 483, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "224", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.590065+00:00"}	2026-08-22 09:08:50.623502+00
760	audit_events	{"id": 451, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "18", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.474677+00:00"}	2026-08-22 09:08:50.623502+00
761	audit_events	{"id": 452, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "18", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.501532+00:00"}	2026-08-22 09:08:50.623502+00
762	audit_events	{"id": 453, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "19", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.702058+00:00"}	2026-08-22 09:08:50.623502+00
763	audit_events	{"id": 454, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "99", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 19, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 33, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:24.726488+00:00"}	2026-08-22 09:08:50.623502+00
783	audit_events	{"id": 474, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:45.706133+00:00"}	2026-08-22 09:08:50.623502+00
764	audit_events	{"id": 455, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "19", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.782573+00:00"}	2026-08-22 09:08:50.623502+00
765	audit_events	{"id": 456, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "20", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:14:24.967028+00:00"}	2026-08-22 09:08:50.623502+00
766	audit_events	{"id": 457, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "100", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 20, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 35, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:14:24.99146+00:00"}	2026-08-22 09:08:50.623502+00
767	audit_events	{"id": 458, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:36.122673+00:00"}	2026-08-22 09:08:50.623502+00
768	audit_events	{"id": 459, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:14:36.352374+00:00"}	2026-08-22 09:08:50.623502+00
769	audit_events	{"id": 460, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:14:36.509186+00:00"}	2026-08-22 09:08:50.623502+00
770	audit_events	{"id": 461, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:36.675903+00:00"}	2026-08-22 09:08:50.623502+00
771	audit_events	{"id": 462, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:38.553849+00:00"}	2026-08-22 09:08:50.623502+00
772	audit_events	{"id": 463, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:14:38.897125+00:00"}	2026-08-22 09:08:50.623502+00
773	audit_events	{"id": 464, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "d62cca16d4544105b5afb89aaa019af0", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:14:39.106959+00:00"}	2026-08-22 09:08:50.623502+00
774	audit_events	{"id": 465, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:43.789076+00:00"}	2026-08-22 09:08:50.623502+00
775	audit_events	{"id": 466, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:44.29379+00:00"}	2026-08-22 09:08:50.623502+00
776	audit_events	{"id": 467, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "103:30", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:14:44.478029+00:00"}	2026-08-22 09:08:50.623502+00
777	audit_events	{"id": 468, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "103:30", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:14:44.506206+00:00"}	2026-08-22 09:08:50.623502+00
778	audit_events	{"id": 469, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "103:30", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:14:44.530452+00:00"}	2026-08-22 09:08:50.623502+00
779	audit_events	{"id": 470, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:44.737892+00:00"}	2026-08-22 09:08:50.623502+00
780	audit_events	{"id": 471, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:14:45.093284+00:00"}	2026-08-22 09:08:50.623502+00
781	audit_events	{"id": 472, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:45.280794+00:00"}	2026-08-22 09:08:50.623502+00
784	audit_events	{"id": 475, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:46.799614+00:00"}	2026-08-22 09:08:50.623502+00
785	audit_events	{"id": 476, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "220", "after_json": {"code": "API-C06DA1C2", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:46.826847+00:00"}	2026-08-22 09:08:50.623502+00
786	audit_events	{"id": 477, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "220", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.034727+00:00"}	2026-08-22 09:08:50.623502+00
787	audit_events	{"id": 478, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.034727+00:00"}	2026-08-22 09:08:50.623502+00
788	audit_events	{"id": 479, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:47.231695+00:00"}	2026-08-22 09:08:50.623502+00
789	audit_events	{"id": 480, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:47.331216+00:00"}	2026-08-22 09:08:50.623502+00
790	audit_events	{"id": 481, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.547083+00:00"}	2026-08-22 09:08:50.623502+00
791	audit_events	{"id": 484, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:14:47.606991+00:00"}	2026-08-22 09:08:50.623502+00
792	audit_events	{"id": 485, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:48.184723+00:00"}	2026-08-22 09:08:50.623502+00
793	audit_events	{"id": 486, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:48.382096+00:00"}	2026-08-22 09:08:50.623502+00
794	audit_events	{"id": 487, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:48.592724+00:00"}	2026-08-22 09:08:50.623502+00
795	audit_events	{"id": 488, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:48.772328+00:00"}	2026-08-22 09:08:50.623502+00
796	audit_events	{"id": 489, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:49.200103+00:00"}	2026-08-22 09:08:50.623502+00
797	audit_events	{"id": 490, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:49.374673+00:00"}	2026-08-22 09:08:50.623502+00
798	audit_events	{"id": 491, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:49.548862+00:00"}	2026-08-22 09:08:50.623502+00
799	audit_events	{"id": 492, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:51.993274+00:00"}	2026-08-22 09:08:50.623502+00
800	audit_events	{"id": 493, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:52.159509+00:00"}	2026-08-22 09:08:50.623502+00
801	audit_events	{"id": 494, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:52.33334+00:00"}	2026-08-22 09:08:50.623502+00
802	audit_events	{"id": 495, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:52.70125+00:00"}	2026-08-22 09:08:50.623502+00
803	audit_events	{"id": 496, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:52.914505+00:00"}	2026-08-22 09:08:50.623502+00
804	audit_events	{"id": 497, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:53.125822+00:00"}	2026-08-22 09:08:50.623502+00
805	audit_events	{"id": 498, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:53.312457+00:00"}	2026-08-22 09:08:50.623502+00
806	audit_events	{"id": 499, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:55.055979+00:00"}	2026-08-22 09:08:50.623502+00
807	audit_events	{"id": 500, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:56.09339+00:00"}	2026-08-22 09:08:50.623502+00
808	audit_events	{"id": 501, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:56.805973+00:00"}	2026-08-22 09:08:50.623502+00
809	audit_events	{"id": 502, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "1404", "after_json": {"role": "MANAGER", "email": "operator-81829306@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:14:56.908+00:00"}	2026-08-22 09:08:50.623502+00
810	audit_events	{"id": 503, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "1404", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:14:56.941569+00:00"}	2026-08-22 09:08:50.623502+00
811	audit_events	{"id": 504, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:57.109664+00:00"}	2026-08-22 09:08:50.623502+00
812	audit_events	{"id": 505, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:57.285654+00:00"}	2026-08-22 09:08:50.623502+00
813	audit_events	{"id": 506, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:58.663766+00:00"}	2026-08-22 09:08:50.623502+00
814	audit_events	{"id": 507, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:14:58.973421+00:00"}	2026-08-22 09:08:50.623502+00
815	audit_events	{"id": 508, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:01.265773+00:00"}	2026-08-22 09:08:50.623502+00
816	audit_events	{"id": 509, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:01.444407+00:00"}	2026-08-22 09:08:50.623502+00
817	audit_events	{"id": 510, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "104", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:15:01.775503+00:00"}	2026-08-22 09:08:50.623502+00
818	audit_events	{"id": 511, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:01.970174+00:00"}	2026-08-22 09:08:50.623502+00
819	audit_events	{"id": 512, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:02.452851+00:00"}	2026-08-22 09:08:50.623502+00
820	audit_events	{"id": 513, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:03.556298+00:00"}	2026-08-22 09:08:50.623502+00
821	audit_events	{"id": 514, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "105", "after_json": {"committee_ids": [193, 194]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:03.598063+00:00"}	2026-08-22 09:08:50.623502+00
822	audit_events	{"id": 515, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:03.880777+00:00"}	2026-08-22 09:08:50.623502+00
823	audit_events	{"id": 516, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "106", "after_json": {"committee_ids": [196]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:03.905607+00:00"}	2026-08-22 09:08:50.623502+00
824	audit_events	{"id": 517, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "106", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:03.92282+00:00"}	2026-08-22 09:08:50.623502+00
825	audit_events	{"id": 518, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:04.19936+00:00"}	2026-08-22 09:08:50.623502+00
826	audit_events	{"id": 519, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:04.435736+00:00"}	2026-08-22 09:08:50.623502+00
827	audit_events	{"id": 520, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:05.018587+00:00"}	2026-08-22 09:08:50.623502+00
828	audit_events	{"id": 521, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:05.271482+00:00"}	2026-08-22 09:08:50.623502+00
829	audit_events	{"id": 522, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:05.530377+00:00"}	2026-08-22 09:08:50.623502+00
830	audit_events	{"id": 523, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "112", "after_json": {"committee_ids": [211]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:05.560093+00:00"}	2026-08-22 09:08:50.623502+00
831	audit_events	{"id": 524, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:05.867433+00:00"}	2026-08-22 09:08:50.623502+00
832	audit_events	{"id": 525, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "113", "after_json": {"committee_ids": [214]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:05.91039+00:00"}	2026-08-22 09:08:50.623502+00
833	audit_events	{"id": 526, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:06.349041+00:00"}	2026-08-22 09:08:50.623502+00
834	audit_events	{"id": 527, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "114", "after_json": {"committee_ids": [217]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:06.370765+00:00"}	2026-08-22 09:08:50.623502+00
835	audit_events	{"id": 528, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:06.751127+00:00"}	2026-08-22 09:08:50.623502+00
836	audit_events	{"id": 529, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:07.13281+00:00"}	2026-08-22 09:08:50.623502+00
837	audit_events	{"id": 530, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:07.336381+00:00"}	2026-08-22 09:08:50.623502+00
838	audit_events	{"id": 531, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "252", "after_json": {"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:07.354104+00:00"}	2026-08-22 09:08:50.623502+00
839	audit_events	{"id": 532, "action": "SEMESTER_UPDATED", "reason": null, "actor_id": 2, "entity_id": "252", "after_json": {"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Updated note", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "before_json": {"code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Created by API test", "status": "ACTIVE", "end_date": "2036-04-15", "start_date": "2036-01-01", "academic_year": "2036-2037"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:07.452476+00:00"}	2026-08-22 09:08:50.623502+00
840	audit_events	{"id": 533, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "252", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:07.473444+00:00"}	2026-08-22 09:08:50.623502+00
841	audit_events	{"id": 534, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:07.473444+00:00"}	2026-08-22 09:08:50.623502+00
842	audit_events	{"id": 547, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:15:26.679182+00:00"}	2026-08-22 09:08:50.623502+00
843	audit_events	{"id": 548, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:26.852253+00:00"}	2026-08-22 09:08:50.623502+00
844	audit_events	{"id": 535, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "21", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:10.520336+00:00"}	2026-08-22 09:08:50.623502+00
853	audit_events	{"id": 544, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "117", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 24, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 42, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:11.338667+00:00"}	2026-08-22 09:08:50.623502+00
854	audit_events	{"id": 545, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:26.235891+00:00"}	2026-08-22 09:08:50.623502+00
855	audit_events	{"id": 546, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:15:26.504842+00:00"}	2026-08-22 09:08:50.623502+00
845	audit_events	{"id": 536, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "21", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:10.551843+00:00"}	2026-08-22 09:08:50.623502+00
846	audit_events	{"id": 537, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "22", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:10.770451+00:00"}	2026-08-22 09:08:50.623502+00
847	audit_events	{"id": 538, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "22", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:10.809908+00:00"}	2026-08-22 09:08:50.623502+00
848	audit_events	{"id": 539, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "22", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:10.837342+00:00"}	2026-08-22 09:08:50.623502+00
849	audit_events	{"id": 540, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "23", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:11.055642+00:00"}	2026-08-22 09:08:50.623502+00
850	audit_events	{"id": 541, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "116", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 23, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 40, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:11.077791+00:00"}	2026-08-22 09:08:50.623502+00
851	audit_events	{"id": 542, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "23", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:11.122346+00:00"}	2026-08-22 09:08:50.623502+00
852	audit_events	{"id": 543, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "24", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:15:11.322293+00:00"}	2026-08-22 09:08:50.623502+00
856	audit_events	{"id": 549, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:28.656609+00:00"}	2026-08-22 09:08:50.623502+00
857	audit_events	{"id": 550, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:28.956249+00:00"}	2026-08-22 09:08:50.623502+00
858	audit_events	{"id": 551, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "51542b3b9e8e443f8b5a2bc57fe2d56f", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:15:29.132317+00:00"}	2026-08-22 09:08:50.623502+00
859	audit_events	{"id": 552, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:30.927312+00:00"}	2026-08-22 09:08:50.623502+00
860	audit_events	{"id": 553, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:31.38817+00:00"}	2026-08-22 09:08:50.623502+00
861	audit_events	{"id": 554, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "120:35", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:15:31.523426+00:00"}	2026-08-22 09:08:50.623502+00
862	audit_events	{"id": 555, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "120:35", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:15:31.544857+00:00"}	2026-08-22 09:08:50.623502+00
863	audit_events	{"id": 556, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "120:35", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:15:31.564539+00:00"}	2026-08-22 09:08:50.623502+00
864	audit_events	{"id": 557, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:31.736542+00:00"}	2026-08-22 09:08:50.623502+00
865	audit_events	{"id": 558, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:15:32.077975+00:00"}	2026-08-22 09:08:50.623502+00
866	audit_events	{"id": 559, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:32.241283+00:00"}	2026-08-22 09:08:50.623502+00
867	audit_events	{"id": 560, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:15:32.387492+00:00"}	2026-08-22 09:08:50.623502+00
868	audit_events	{"id": 561, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:32.647297+00:00"}	2026-08-22 09:08:50.623502+00
869	audit_events	{"id": 562, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:33.616778+00:00"}	2026-08-22 09:08:50.623502+00
870	audit_events	{"id": 563, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "262", "after_json": {"code": "API-DA7261BC", "name": "API Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:33.642419+00:00"}	2026-08-22 09:08:50.623502+00
871	audit_events	{"id": 564, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "262", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:33.846833+00:00"}	2026-08-22 09:08:50.623502+00
872	audit_events	{"id": 565, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:33.846833+00:00"}	2026-08-22 09:08:50.623502+00
873	audit_events	{"id": 566, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:34.01516+00:00"}	2026-08-22 09:08:50.623502+00
874	audit_events	{"id": 567, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:34.121048+00:00"}	2026-08-22 09:08:50.623502+00
875	audit_events	{"id": 568, "action": "SEMESTER_STATUS_CHANGED", "reason": "Prepare isolated API test", "actor_id": 2, "entity_id": "1", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:34.285026+00:00"}	2026-08-22 09:08:50.623502+00
876	audit_events	{"id": 569, "action": "SEMESTER_CREATED", "reason": null, "actor_id": 2, "entity_id": "266", "after_json": {"code": "DURATION-9046A2DF", "name": "Duration Test Semester", "note": null, "status": "ACTIVE", "end_date": "2030-04-15", "start_date": "2030-01-01", "academic_year": "2030-2031"}, "before_json": null, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:34.302638+00:00"}	2026-08-22 09:08:50.623502+00
877	audit_events	{"id": 570, "action": "SEMESTER_STATUS_CHANGED", "reason": "Semester completed", "actor_id": 2, "entity_id": "266", "after_json": {"status": "CLOSED"}, "before_json": {"status": "ACTIVE"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:34.323177+00:00"}	2026-08-22 09:08:50.623502+00
878	audit_events	{"id": 571, "action": "SEMESTER_SET_CURRENT", "reason": null, "actor_id": 2, "entity_id": "1", "after_json": {"status": "ACTIVE"}, "before_json": {"status": "CLOSED"}, "entity_type": "semester", "occurred_at": "2026-08-22T08:15:34.338992+00:00"}	2026-08-22 09:08:50.623502+00
879	audit_events	{"id": 572, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:34.8182+00:00"}	2026-08-22 09:08:50.623502+00
880	audit_events	{"id": 573, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:35.004576+00:00"}	2026-08-22 09:08:50.623502+00
881	audit_events	{"id": 574, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:35.18037+00:00"}	2026-08-22 09:08:50.623502+00
882	audit_events	{"id": 575, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:35.360321+00:00"}	2026-08-22 09:08:50.623502+00
883	audit_events	{"id": 576, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:35.81146+00:00"}	2026-08-22 09:08:50.623502+00
884	audit_events	{"id": 577, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:35.997033+00:00"}	2026-08-22 09:08:50.623502+00
885	audit_events	{"id": 578, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:36.175069+00:00"}	2026-08-22 09:08:50.623502+00
886	audit_events	{"id": 579, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:38.354249+00:00"}	2026-08-22 09:08:50.623502+00
887	audit_events	{"id": 580, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:38.529462+00:00"}	2026-08-22 09:08:50.623502+00
888	audit_events	{"id": 581, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:38.684816+00:00"}	2026-08-22 09:08:50.623502+00
889	audit_events	{"id": 582, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:38.960794+00:00"}	2026-08-22 09:08:50.623502+00
890	audit_events	{"id": 583, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:39.152212+00:00"}	2026-08-22 09:08:50.623502+00
891	audit_events	{"id": 584, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:39.342398+00:00"}	2026-08-22 09:08:50.623502+00
892	audit_events	{"id": 585, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:39.552818+00:00"}	2026-08-22 09:08:50.623502+00
893	audit_events	{"id": 586, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:41.287245+00:00"}	2026-08-22 09:08:50.623502+00
894	audit_events	{"id": 587, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:42.350272+00:00"}	2026-08-22 09:08:50.623502+00
895	audit_events	{"id": 588, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:43.016311+00:00"}	2026-08-22 09:08:50.623502+00
896	audit_events	{"id": 589, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "1636", "after_json": {"role": "MANAGER", "email": "operator-8f74a9c2@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:15:43.12487+00:00"}	2026-08-22 09:08:50.623502+00
897	audit_events	{"id": 590, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "1636", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:15:43.160781+00:00"}	2026-08-22 09:08:50.623502+00
898	audit_events	{"id": 591, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:43.320638+00:00"}	2026-08-22 09:08:50.623502+00
899	audit_events	{"id": 592, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:43.507657+00:00"}	2026-08-22 09:08:50.623502+00
900	audit_events	{"id": 593, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:44.750321+00:00"}	2026-08-22 09:08:50.623502+00
901	audit_events	{"id": 594, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:45.082661+00:00"}	2026-08-22 09:08:50.623502+00
902	audit_events	{"id": 595, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:50.741228+00:00"}	2026-08-22 09:08:50.623502+00
903	audit_events	{"id": 596, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:50.937786+00:00"}	2026-08-22 09:08:50.623502+00
904	audit_events	{"id": 597, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "121", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:15:51.334924+00:00"}	2026-08-22 09:08:50.623502+00
905	audit_events	{"id": 598, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:51.562906+00:00"}	2026-08-22 09:08:50.623502+00
906	audit_events	{"id": 599, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:52.145963+00:00"}	2026-08-22 09:08:50.623502+00
907	audit_events	{"id": 600, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:53.195882+00:00"}	2026-08-22 09:08:50.623502+00
908	audit_events	{"id": 601, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "122", "after_json": {"committee_ids": [223, 224]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:53.237599+00:00"}	2026-08-22 09:08:50.623502+00
909	audit_events	{"id": 602, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:53.550508+00:00"}	2026-08-22 09:08:50.623502+00
910	audit_events	{"id": 603, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "123", "after_json": {"committee_ids": [226]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:53.579375+00:00"}	2026-08-22 09:08:50.623502+00
911	audit_events	{"id": 604, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "123", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:53.600218+00:00"}	2026-08-22 09:08:50.623502+00
912	audit_events	{"id": 605, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:53.853358+00:00"}	2026-08-22 09:08:50.623502+00
913	audit_events	{"id": 606, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:54.14197+00:00"}	2026-08-22 09:08:50.623502+00
914	audit_events	{"id": 607, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:54.82552+00:00"}	2026-08-22 09:08:50.623502+00
915	audit_events	{"id": 608, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:55.133029+00:00"}	2026-08-22 09:08:50.623502+00
916	audit_events	{"id": 609, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:55.410803+00:00"}	2026-08-22 09:08:50.623502+00
917	audit_events	{"id": 610, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "129", "after_json": {"committee_ids": [241]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:55.436006+00:00"}	2026-08-22 09:08:50.623502+00
918	audit_events	{"id": 611, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:55.864996+00:00"}	2026-08-22 09:08:50.623502+00
919	audit_events	{"id": 612, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "130", "after_json": {"committee_ids": [244]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:55.917446+00:00"}	2026-08-22 09:08:50.623502+00
920	audit_events	{"id": 613, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:15:56.388592+00:00"}	2026-08-22 09:08:50.623502+00
921	audit_events	{"id": 614, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "131", "after_json": {"committee_ids": [247]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:15:56.417592+00:00"}	2026-08-22 09:08:50.623502+00
922	audit_events	{"id": 615, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:56.937024+00:00"}	2026-08-22 09:08:50.623502+00
923	audit_events	{"id": 616, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:15:57.350312+00:00"}	2026-08-22 09:08:50.623502+00
952	audit_events	{"id": 642, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 2}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:16:22.528508+00:00"}	2026-08-22 09:08:50.623502+00
924	audit_events	{"id": 617, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "25", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.20113+00:00"}	2026-08-22 09:08:50.623502+00
925	audit_events	{"id": 618, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "25", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.231967+00:00"}	2026-08-22 09:08:50.623502+00
926	audit_events	{"id": 619, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "26", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.480128+00:00"}	2026-08-22 09:08:50.623502+00
927	audit_events	{"id": 620, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "26", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.530901+00:00"}	2026-08-22 09:08:50.623502+00
928	audit_events	{"id": 621, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "26", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.562241+00:00"}	2026-08-22 09:08:50.623502+00
929	audit_events	{"id": 622, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "27", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.808671+00:00"}	2026-08-22 09:08:50.623502+00
930	audit_events	{"id": 623, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "133", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 27, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 47, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:00.848325+00:00"}	2026-08-22 09:08:50.623502+00
931	audit_events	{"id": 669, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:38.456657+00:00"}	2026-08-22 09:08:50.623502+00
932	audit_events	{"id": 670, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:38.640737+00:00"}	2026-08-22 09:08:50.623502+00
933	audit_events	{"id": 671, "action": "ROUND_TRANSITION", "reason": null, "actor_id": 2, "entity_id": "138", "after_json": {"status": "REGISTRATION_CLOSED"}, "before_json": {"status": "OPEN_REGISTRATION"}, "entity_type": "round", "occurred_at": "2026-08-22T08:16:38.794932+00:00"}	2026-08-22 09:08:50.623502+00
934	audit_events	{"id": 624, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "27", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:00.897272+00:00"}	2026-08-22 09:08:50.623502+00
935	audit_events	{"id": 625, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "28", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:01.125957+00:00"}	2026-08-22 09:08:50.623502+00
936	audit_events	{"id": 626, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "134", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 28, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 49, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:01.148593+00:00"}	2026-08-22 09:08:50.623502+00
937	audit_events	{"id": 627, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:13.230824+00:00"}	2026-08-22 09:08:50.623502+00
938	audit_events	{"id": 628, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:16:13.481512+00:00"}	2026-08-22 09:08:50.623502+00
939	audit_events	{"id": 629, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:16:13.666519+00:00"}	2026-08-22 09:08:50.623502+00
940	audit_events	{"id": 630, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:13.832107+00:00"}	2026-08-22 09:08:50.623502+00
941	audit_events	{"id": 631, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 1}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:15.659096+00:00"}	2026-08-22 09:08:50.623502+00
942	audit_events	{"id": 632, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 2, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:15.929076+00:00"}	2026-08-22 09:08:50.623502+00
943	audit_events	{"id": 633, "action": "TEST", "reason": null, "actor_id": null, "entity_id": "4642dc0e5f2d428f8ba1b185ab9e9afe", "after_json": null, "before_json": null, "entity_type": "test", "occurred_at": "2026-08-22T08:16:16.097495+00:00"}	2026-08-22 09:08:50.623502+00
944	audit_events	{"id": 634, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:17.909267+00:00"}	2026-08-22 09:08:50.623502+00
945	audit_events	{"id": 635, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:18.366893+00:00"}	2026-08-22 09:08:50.623502+00
946	audit_events	{"id": 636, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "137:40", "after_json": {"source": "FORM", "selected_count": 2}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:16:18.546993+00:00"}	2026-08-22 09:08:50.623502+00
947	audit_events	{"id": 637, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "137:40", "after_json": {"source": "FORM", "selected_count": 1}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:16:18.57536+00:00"}	2026-08-22 09:08:50.623502+00
948	audit_events	{"id": 638, "action": "AVAILABILITY_ENTERED", "reason": null, "actor_id": 32, "entity_id": "137:40", "after_json": {"source": "FORM", "selected_count": 0}, "before_json": null, "entity_type": "group_availability", "occurred_at": "2026-08-22T08:16:18.598043+00:00"}	2026-08-22 09:08:50.623502+00
949	audit_events	{"id": 639, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:18.784332+00:00"}	2026-08-22 09:08:50.623502+00
950	audit_events	{"id": 640, "action": "LECTURERS_IMPORTED", "reason": null, "actor_id": 1, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "lecturer", "occurred_at": "2026-08-22T08:16:22.195771+00:00"}	2026-08-22 09:08:50.623502+00
951	audit_events	{"id": 641, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:22.395026+00:00"}	2026-08-22 09:08:50.623502+00
953	audit_events	{"id": 643, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:22.793352+00:00"}	2026-08-22 09:08:50.623502+00
954	audit_events	{"id": 644, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:24.108888+00:00"}	2026-08-22 09:08:50.623502+00
955	audit_events	{"id": 645, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:24.225118+00:00"}	2026-08-22 09:08:50.623502+00
956	audit_events	{"id": 646, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:24.796189+00:00"}	2026-08-22 09:08:50.623502+00
957	audit_events	{"id": 647, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:24.950457+00:00"}	2026-08-22 09:08:50.623502+00
958	audit_events	{"id": 648, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:25.161832+00:00"}	2026-08-22 09:08:50.623502+00
959	audit_events	{"id": 649, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:25.340469+00:00"}	2026-08-22 09:08:50.623502+00
960	audit_events	{"id": 650, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:25.968014+00:00"}	2026-08-22 09:08:50.623502+00
961	audit_events	{"id": 651, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:26.163809+00:00"}	2026-08-22 09:08:50.623502+00
962	audit_events	{"id": 652, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:26.346661+00:00"}	2026-08-22 09:08:50.623502+00
963	audit_events	{"id": 653, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:29.139689+00:00"}	2026-08-22 09:08:50.623502+00
964	audit_events	{"id": 654, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:29.314366+00:00"}	2026-08-22 09:08:50.623502+00
965	audit_events	{"id": 655, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:29.479534+00:00"}	2026-08-22 09:08:50.623502+00
966	audit_events	{"id": 656, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:29.660078+00:00"}	2026-08-22 09:08:50.623502+00
967	audit_events	{"id": 657, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:29.961657+00:00"}	2026-08-22 09:08:50.623502+00
968	audit_events	{"id": 658, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:30.177297+00:00"}	2026-08-22 09:08:50.623502+00
969	audit_events	{"id": 659, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:30.378003+00:00"}	2026-08-22 09:08:50.623502+00
970	audit_events	{"id": 660, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:32.227456+00:00"}	2026-08-22 09:08:50.623502+00
971	audit_events	{"id": 661, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:33.379543+00:00"}	2026-08-22 09:08:50.623502+00
972	audit_events	{"id": 662, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:34.002694+00:00"}	2026-08-22 09:08:50.623502+00
973	audit_events	{"id": 663, "action": "ACCOUNT_CREATED", "reason": null, "actor_id": 1, "entity_id": "1868", "after_json": {"role": "MANAGER", "email": "operator-4951c3f7@example.test"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:16:34.102823+00:00"}	2026-08-22 09:08:50.623502+00
974	audit_events	{"id": 664, "action": "ACCOUNT_STATUS_CHANGED", "reason": "End of local pilot", "actor_id": 1, "entity_id": "1868", "after_json": {"status": "INACTIVE"}, "before_json": {"status": "ACTIVE"}, "entity_type": "account", "occurred_at": "2026-08-22T08:16:34.140024+00:00"}	2026-08-22 09:08:50.623502+00
975	audit_events	{"id": 665, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:34.312542+00:00"}	2026-08-22 09:08:50.623502+00
976	audit_events	{"id": 666, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:34.480133+00:00"}	2026-08-22 09:08:50.623502+00
977	audit_events	{"id": 667, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:35.693623+00:00"}	2026-08-22 09:08:50.623502+00
978	audit_events	{"id": 668, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:36.045002+00:00"}	2026-08-22 09:08:50.623502+00
979	audit_events	{"id": 672, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:38.968699+00:00"}	2026-08-22 09:08:50.623502+00
980	audit_events	{"id": 673, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:39.404352+00:00"}	2026-08-22 09:08:50.623502+00
981	audit_events	{"id": 674, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:40.52074+00:00"}	2026-08-22 09:08:50.623502+00
982	audit_events	{"id": 675, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "139", "after_json": {"committee_ids": [253, 254]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:40.557934+00:00"}	2026-08-22 09:08:50.623502+00
983	audit_events	{"id": 676, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:40.857132+00:00"}	2026-08-22 09:08:50.623502+00
984	audit_events	{"id": 677, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "140", "after_json": {"committee_ids": [256]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:40.878532+00:00"}	2026-08-22 09:08:50.623502+00
985	audit_events	{"id": 678, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "140", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:40.893541+00:00"}	2026-08-22 09:08:50.623502+00
986	audit_events	{"id": 679, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:41.180159+00:00"}	2026-08-22 09:08:50.623502+00
987	audit_events	{"id": 680, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:41.441764+00:00"}	2026-08-22 09:08:50.623502+00
988	audit_events	{"id": 681, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:42.075035+00:00"}	2026-08-22 09:08:50.623502+00
989	audit_events	{"id": 682, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:42.368764+00:00"}	2026-08-22 09:08:50.623502+00
990	audit_events	{"id": 683, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:42.607509+00:00"}	2026-08-22 09:08:50.623502+00
991	audit_events	{"id": 684, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "146", "after_json": {"committee_ids": [271]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:42.630548+00:00"}	2026-08-22 09:08:50.623502+00
992	audit_events	{"id": 685, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:43.068619+00:00"}	2026-08-22 09:08:50.623502+00
993	audit_events	{"id": 686, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "147", "after_json": {"committee_ids": [274]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:43.103896+00:00"}	2026-08-22 09:08:50.623502+00
994	audit_events	{"id": 687, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:16:43.423029+00:00"}	2026-08-22 09:08:50.623502+00
995	audit_events	{"id": 688, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "148", "after_json": {"committee_ids": [277]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:43.447919+00:00"}	2026-08-22 09:08:50.623502+00
996	audit_events	{"id": 689, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:43.867103+00:00"}	2026-08-22 09:08:50.623502+00
997	audit_events	{"id": 690, "action": "SEED_FIXTURE_LOADED", "reason": null, "actor_id": 1, "entity_id": "seed-v5", "after_json": {"source": "VERSIONED_SEED"}, "before_json": null, "entity_type": "seed_fixture", "occurred_at": "2026-08-22T08:16:44.251356+00:00"}	2026-08-22 09:08:50.623502+00
1025	audit_events	{"id": 718, "action": "EXCEL_PROJECTS_GVHD_IMPORTED", "reason": "One-sheet project and supervisor import", "actor_id": null, "entity_id": "su26_defense_1.2_SE.xlsx", "after_json": {"projects": 74, "semester": "SU26", "supervisor_assignments": 80}, "before_json": null, "entity_type": "excel_import", "occurred_at": "2026-08-22T08:31:59.411248+00:00"}	2026-08-22 09:08:50.623502+00
998	audit_events	{"id": 691, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "29", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:47.663152+00:00"}	2026-08-22 09:08:50.623502+00
999	audit_events	{"id": 692, "action": "TIMEFRAME_MANUAL_UPDATED", "reason": "Replace all edited timelines", "actor_id": 2, "entity_id": "29", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 2, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "08:00:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "13:00:00", "start_time": "10:15:00"}], "blocks_per_day": 2, "unused_minutes": 0, "capacity_per_day": 5, "groups_per_block": null, "manual_timelines": [{"end_time": "10:15:00", "start_time": "08:00:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 165, "break_window_minutes": 165, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:47.701148+00:00"}	2026-08-22 09:08:50.623502+00
1000	audit_events	{"id": 693, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "30", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:47.925784+00:00"}	2026-08-22 09:08:50.623502+00
1001	audit_events	{"id": 694, "action": "TIMEFRAME_UPDATED", "reason": "Move the shared template to 08:00", "actor_id": 2, "entity_id": "30", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:30:00", "start_time": "13:15:00", "group_slots": [{"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 1}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 2}, {"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [{"name": "Nghi trua moi", "end_time": "13:15:00", "start_time": "12:30:00"}], "blocks_per_day": 3, "unused_minutes": 90, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 45, "break_window_minutes": 45, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:47.966845+00:00"}	2026-08-22 09:08:50.623502+00
1002	audit_events	{"id": 695, "action": "TIMEFRAME_ARCHIVED", "reason": "Archive test template", "actor_id": 2, "entity_id": "30", "after_json": {"archived": true}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:47.993074+00:00"}	2026-08-22 09:08:50.623502+00
1003	audit_events	{"id": 696, "action": "TIMEFRAME_CREATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "31", "after_json": {"blocks": [{"end_time": "09:15:00", "start_time": "07:00:00", "group_slots": [{"end_time": "07:45:00", "start_time": "07:00:00", "sequence_number": 1}, {"end_time": "08:30:00", "start_time": "07:45:00", "sequence_number": 2}, {"end_time": "09:15:00", "start_time": "08:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "11:45:00", "start_time": "09:30:00", "group_slots": [{"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 1}, {"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 2}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "15:15:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}, {"end_time": "15:15:00", "start_time": "14:30:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:30:00", "start_time": "07:00:00", "break_windows": [{"name": "Nghi trua", "end_time": "13:00:00", "start_time": "12:00:00"}], "blocks_per_day": 3, "unused_minutes": 150, "capacity_per_day": 9, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 75, "break_window_minutes": 60, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 15, "break_between_blocks_minutes": 15}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:48.245022+00:00"}	2026-08-22 09:08:50.623502+00
1004	audit_events	{"id": 697, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "150", "after_json": {"name": "Round From Quick Timeframe", "type": "REVIEW_1", "end_date": "2026-09-01", "room_types": ["NORMAL"], "start_date": "2026-09-01", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 31, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 54, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:48.276045+00:00"}	2026-08-22 09:08:50.623502+00
1005	audit_events	{"id": 698, "action": "TIMEFRAME_UPDATED", "reason": "Test reusable system configuration", "actor_id": 2, "entity_id": "31", "after_json": {"blocks": [{"end_time": "10:15:00", "start_time": "08:00:00", "group_slots": [{"end_time": "08:45:00", "start_time": "08:00:00", "sequence_number": 1}, {"end_time": "09:30:00", "start_time": "08:45:00", "sequence_number": 2}, {"end_time": "10:15:00", "start_time": "09:30:00", "sequence_number": 3}], "sequence_number": 1, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "12:30:00", "start_time": "10:15:00", "group_slots": [{"end_time": "11:00:00", "start_time": "10:15:00", "sequence_number": 1}, {"end_time": "11:45:00", "start_time": "11:00:00", "sequence_number": 2}, {"end_time": "12:30:00", "start_time": "11:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:45:00", "start_time": "12:30:00", "group_slots": [{"end_time": "13:15:00", "start_time": "12:30:00", "sequence_number": 1}, {"end_time": "14:00:00", "start_time": "13:15:00", "sequence_number": 2}, {"end_time": "14:45:00", "start_time": "14:00:00", "sequence_number": 3}], "sequence_number": 3, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "17:00:00", "start_time": "14:45:00", "group_slots": [{"end_time": "15:30:00", "start_time": "14:45:00", "sequence_number": 1}, {"end_time": "16:15:00", "start_time": "15:30:00", "sequence_number": 2}, {"end_time": "17:00:00", "start_time": "16:15:00", "sequence_number": 3}], "sequence_number": 4, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}], "end_time": "17:00:00", "start_time": "08:00:00", "break_windows": [], "blocks_per_day": 4, "unused_minutes": 0, "capacity_per_day": 12, "groups_per_block": 3, "manual_timelines": null, "total_break_minutes": 0, "break_window_minutes": 0, "block_duration_minutes": 135, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": 0}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:48.327137+00:00"}	2026-08-22 09:08:50.623502+00
1026	audit_events	{"id": 719, "action": "LOGOUT", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "revoked"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:40:17.294181+00:00"}	2026-08-22 09:08:50.623502+00
1006	audit_events	{"id": 699, "action": "TIMEFRAME_MANUAL_CREATED", "reason": "Save timelines edited from quick preview", "actor_id": 2, "entity_id": "32", "after_json": {"blocks": [{"end_time": "09:00:00", "start_time": "07:30:00", "group_slots": [{"end_time": "08:15:00", "start_time": "07:30:00", "sequence_number": 1}, {"end_time": "09:00:00", "start_time": "08:15:00", "sequence_number": 2}], "sequence_number": 1, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}, {"end_time": "11:30:00", "start_time": "09:15:00", "group_slots": [{"end_time": "10:00:00", "start_time": "09:15:00", "sequence_number": 1}, {"end_time": "10:45:00", "start_time": "10:00:00", "sequence_number": 2}, {"end_time": "11:30:00", "start_time": "10:45:00", "sequence_number": 3}], "sequence_number": 2, "duration_minutes": 135, "groups_per_block": 3, "group_duration_minutes": 45}, {"end_time": "14:30:00", "start_time": "13:00:00", "group_slots": [{"end_time": "13:45:00", "start_time": "13:00:00", "sequence_number": 1}, {"end_time": "14:30:00", "start_time": "13:45:00", "sequence_number": 2}], "sequence_number": 3, "duration_minutes": 90, "groups_per_block": 2, "group_duration_minutes": 45}], "end_time": "14:30:00", "start_time": "07:30:00", "break_windows": [{"name": "Khoảng nghỉ 1", "end_time": "09:15:00", "start_time": "09:00:00"}, {"name": "Khoảng nghỉ 2", "end_time": "13:00:00", "start_time": "11:30:00"}], "blocks_per_day": 3, "unused_minutes": 0, "capacity_per_day": 7, "groups_per_block": null, "manual_timelines": [{"end_time": "09:00:00", "start_time": "07:30:00", "groups_per_slot": 2}, {"end_time": "11:30:00", "start_time": "09:15:00", "groups_per_slot": 3}, {"end_time": "14:30:00", "start_time": "13:00:00", "groups_per_slot": 2}], "total_break_minutes": 105, "break_window_minutes": 105, "block_duration_minutes": null, "group_duration_minutes": 45, "applied_block_break_minutes": 0, "break_between_blocks_minutes": null}, "before_json": null, "entity_type": "timeframe", "occurred_at": "2026-08-22T08:16:48.527602+00:00"}	2026-08-22 09:08:50.623502+00
1007	audit_events	{"id": 700, "action": "ROUND_CREATED", "reason": null, "actor_id": 2, "entity_id": "151", "after_json": {"name": "Round From Manual Timeframe", "type": "REVIEW_1", "end_date": "2026-09-02", "room_types": ["NORMAL"], "start_date": "2026-09-02", "description": null, "semester_id": 1, "soft_weights": {}, "timeframe_id": 32, "reviewer_count": 2, "result_owner_mode": false, "h12_semester_quota": null, "timeframeVersionId": 56, "max_minutes_per_day": null, "group_selection_mode": false, "h12_sessions_per_day": 8, "max_minutes_per_part": null, "h12_sessions_per_part": 4, "registration_deadline": null, "max_groups_per_timeslot": 1, "session_duration_minutes": 45, "group_preference_deadline": null}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:16:48.549782+00:00"}	2026-08-22 09:08:50.623502+00
1008	audit_events	{"id": 701, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:11.134136+00:00"}	2026-08-22 09:08:50.623502+00
1009	audit_events	{"id": 702, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "152", "after_json": {"committee_ids": [280, 281]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:11.17986+00:00"}	2026-08-22 09:08:50.623502+00
1010	audit_events	{"id": 703, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:11.483498+00:00"}	2026-08-22 09:08:50.623502+00
1011	audit_events	{"id": 704, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "153", "after_json": {"committee_ids": [283]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:11.506807+00:00"}	2026-08-22 09:08:50.623502+00
1012	audit_events	{"id": 705, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "153", "after_json": {"committee_ids": []}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:11.523238+00:00"}	2026-08-22 09:08:50.623502+00
1013	audit_events	{"id": 706, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:11.787608+00:00"}	2026-08-22 09:08:50.623502+00
1014	audit_events	{"id": 707, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:12.051973+00:00"}	2026-08-22 09:08:50.623502+00
1015	audit_events	{"id": 708, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:12.697953+00:00"}	2026-08-22 09:08:50.623502+00
1016	audit_events	{"id": 709, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:13.039363+00:00"}	2026-08-22 09:08:50.623502+00
1017	audit_events	{"id": 710, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:13.286946+00:00"}	2026-08-22 09:08:50.623502+00
1018	audit_events	{"id": 711, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "159", "after_json": {"committee_ids": [298]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:13.311639+00:00"}	2026-08-22 09:08:50.623502+00
1019	audit_events	{"id": 712, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:13.628841+00:00"}	2026-08-22 09:08:50.623502+00
1020	audit_events	{"id": 713, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "160", "after_json": {"committee_ids": [301]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:13.678611+00:00"}	2026-08-22 09:08:50.623502+00
1021	audit_events	{"id": 714, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 3, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:19:14.014194+00:00"}	2026-08-22 09:08:50.623502+00
1022	audit_events	{"id": 715, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "161", "after_json": {"committee_ids": [304]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:19:14.037315+00:00"}	2026-08-22 09:08:50.623502+00
1023	audit_events	{"id": 716, "action": "COMMITTEES_CREATED", "reason": null, "actor_id": 2, "entity_id": "bulk", "after_json": {"created": 1, "skipped": 0}, "before_json": null, "entity_type": "committee", "occurred_at": "2026-08-22T08:31:51.771473+00:00"}	2026-08-22 09:08:50.623502+00
1024	audit_events	{"id": 717, "action": "ROUND_COMMITTEES_REPLACED", "reason": null, "actor_id": 2, "entity_id": "163", "after_json": {"committee_ids": [307]}, "before_json": null, "entity_type": "round", "occurred_at": "2026-08-22T08:31:51.849336+00:00"}	2026-08-22 09:08:50.623502+00
1027	audit_events	{"id": 720, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 2, "entity_id": "2", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:40:19.723567+00:00"}	2026-08-22 09:08:50.623502+00
1029	audit_events	{"id": 722, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 1, "entity_id": "1", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:42:24.433525+00:00"}	2026-08-22 09:08:50.623502+00
1030	audit_events	{"id": 723, "action": "LOGIN_SUCCESS", "reason": null, "actor_id": 1, "entity_id": "1", "after_json": {"session": "created"}, "before_json": null, "entity_type": "account", "occurred_at": "2026-08-22T08:42:32.730009+00:00"}	2026-08-22 09:08:50.623502+00
1031	auth_login_throttles	{"attempts": 10, "identifier": "7d7595e30cef2fc7129b99eaea74a800667fea48444f6629fd2f2c33c5d5a741", "updated_at": "2026-08-22T07:56:03.351274+00:00", "window_started_at": "2026-08-22T07:56:03.197902+00:00"}	2026-08-22 09:08:50.623502+00
1032	auth_login_throttles	{"attempts": 10, "identifier": "16fcea6fa28991a67f7df64702b3ef5b0b2ddde1d78d1b4b0b558490f08259fa", "updated_at": "2026-08-22T08:14:37.175318+00:00", "window_started_at": "2026-08-22T08:14:37.047833+00:00"}	2026-08-22 09:08:50.623502+00
1033	auth_login_throttles	{"attempts": 10, "identifier": "2c5d0a408d19ecd0b8f7e72026003c35345a94f81de350dc0f99bc821759c82a", "updated_at": "2026-08-22T08:05:42.019244+00:00", "window_started_at": "2026-08-22T08:05:41.878958+00:00"}	2026-08-22 09:08:50.623502+00
1034	auth_login_throttles	{"attempts": 10, "identifier": "63adbdec44e8291770a7867d40aa20612e48289a449d45581c8beb4b7a29db10", "updated_at": "2026-08-22T08:15:27.301995+00:00", "window_started_at": "2026-08-22T08:15:27.177148+00:00"}	2026-08-22 09:08:50.623502+00
1035	auth_login_throttles	{"attempts": 10, "identifier": "14ea465a8a4292847695141e09e49c322f93277a8d3ccc571739f118b1237d64", "updated_at": "2026-08-22T08:06:30.687245+00:00", "window_started_at": "2026-08-22T08:06:30.581151+00:00"}	2026-08-22 09:08:50.623502+00
1036	auth_login_throttles	{"attempts": 10, "identifier": "d1f81615f3efab9d578d8dd3f501477e9cd35b6bce46b895d44839ad9ff3e904", "updated_at": "2026-08-22T08:12:52.288936+00:00", "window_started_at": "2026-08-22T08:12:52.138628+00:00"}	2026-08-22 09:08:50.623502+00
1037	auth_login_throttles	{"attempts": 10, "identifier": "2780aedd448af8128fb21e07a06c54921bdf077f08759f3933e334a7a08558d3", "updated_at": "2026-08-22T08:16:14.262502+00:00", "window_started_at": "2026-08-22T08:16:14.142054+00:00"}	2026-08-22 09:08:50.623502+00
1038	auth_login_throttles	{"attempts": 10, "identifier": "db31af2c10f20ab0059fe245f148d873580b3c7792d7a508501ab18303b79d91", "updated_at": "2026-08-22T08:13:49.438993+00:00", "window_started_at": "2026-08-22T08:13:49.283402+00:00"}	2026-08-22 09:08:50.623502+00
1039	auth_sessions	{"id": 6, "account_id": 2, "created_at": "2026-08-22T08:13:48.621395+00:00", "expires_at": "2026-08-29T08:13:48.697807+00:00", "revoked_at": "2026-08-22T08:13:48.777071+00:00", "token_hash": "ab090d5cd63eaa16f4ab21331457f4a536ff441ada09e05e0e863fc276fdc0f0", "last_seen_at": "2026-08-22T08:13:48.753462+00:00", "csrf_token_hash": "50e4e91a7f6e223b34434f470fc8ecb83d9990a1792736da9d52d343976238c6"}	2026-08-22 09:08:50.623502+00
1040	auth_sessions	{"id": 12, "account_id": 1, "created_at": "2026-08-22T08:42:24.433525+00:00", "expires_at": "2026-08-29T08:42:24.54833+00:00", "revoked_at": null, "token_hash": "0be8b86dd450cb02c833b7950910502cb99c3e74b518cb85bd5f8927f10acf68", "last_seen_at": "2026-08-22T08:42:24.573552+00:00", "csrf_token_hash": "d46f198d7a95c8a10e9b6beb83a925adc15f1814682b5661b05a1e845f65b6a8"}	2026-08-22 09:08:50.623502+00
1041	auth_sessions	{"id": 7, "account_id": 2, "created_at": "2026-08-22T08:14:36.352374+00:00", "expires_at": "2026-08-29T08:14:36.435556+00:00", "revoked_at": "2026-08-22T08:14:36.509186+00:00", "token_hash": "900ffa2470f7f4c261b39d6fdcc54c247650af247101f5919996f6e571a73e28", "last_seen_at": "2026-08-22T08:14:36.483484+00:00", "csrf_token_hash": "3f24426433d8ceff3ce771e73557e69deb1425e2b05afcb92ee12b52a44b1ea4"}	2026-08-22 09:08:50.623502+00
1042	auth_sessions	{"id": 8, "account_id": 2, "created_at": "2026-08-22T08:15:26.504842+00:00", "expires_at": "2026-08-29T08:15:26.595787+00:00", "revoked_at": "2026-08-22T08:15:26.679182+00:00", "token_hash": "c99f539538d9c2511f9f093ca346982e41d0ba9d5b2239e9f7406e6d323d4955", "last_seen_at": "2026-08-22T08:15:26.650102+00:00", "csrf_token_hash": "d3a36ebc22d27f876a5045e0113d7631f2192dc68eb0f7a28a368b5b2338ddca"}	2026-08-22 09:08:50.623502+00
1043	auth_sessions	{"id": 13, "account_id": 1, "created_at": "2026-08-22T08:42:32.730009+00:00", "expires_at": "2026-08-29T08:42:32.834611+00:00", "revoked_at": null, "token_hash": "921baa70730fe6ae86fb40bd1486edf2521b95dfe3aac8175fa1875fc3b3a913", "last_seen_at": "2026-08-22T08:42:32.906047+00:00", "csrf_token_hash": "941166be4b8b327f27573db24137b181259eaea5907363c480ec8beb6c3137ce"}	2026-08-22 09:08:50.623502+00
1044	auth_sessions	{"id": 9, "account_id": 2, "created_at": "2026-08-22T08:16:13.481512+00:00", "expires_at": "2026-08-29T08:16:13.57652+00:00", "revoked_at": "2026-08-22T08:16:13.666519+00:00", "token_hash": "dd12d81e0627f230fb2d68005fd5dbb0f29f3011bcd600ac9d333c1bae5df02e", "last_seen_at": "2026-08-22T08:16:13.640986+00:00", "csrf_token_hash": "55fa02c492b974b9e9fe588db086aa27e286daa48316b51126a778ad429fe7d4"}	2026-08-22 09:08:50.623502+00
1045	auth_sessions	{"id": 2, "account_id": 2, "created_at": "2026-08-22T07:56:01.944819+00:00", "expires_at": "2026-08-29T07:56:02.125518+00:00", "revoked_at": "2026-08-22T07:56:02.230838+00:00", "token_hash": "9b676a6e1cea880921b5710d906e64ce13a91da2ffbf5c120d7570ef013a50b2", "last_seen_at": "2026-08-22T07:56:02.205676+00:00", "csrf_token_hash": "a09752e6f256bbeb3856d08d82c55f35eee76dbde4fb4da24bb7c0d83ca5df9b"}	2026-08-22 09:08:50.623502+00
1046	auth_sessions	{"id": 1, "account_id": 2, "created_at": "2026-08-22T07:55:17.263729+00:00", "expires_at": "2026-08-29T07:55:17.47368+00:00", "revoked_at": "2026-08-22T08:40:17.294181+00:00", "token_hash": "f64d9b7519db3efa6998300a8ece003a1ac9603946003de25bbd87e35e5136dd", "last_seen_at": "2026-08-22T08:40:12.154916+00:00", "csrf_token_hash": "1e78d5ca3231b35fac1b9f0ce0a8e6ab4e99c0e062dbef463c1d567144fc0b6f"}	2026-08-22 09:08:50.623502+00
1047	auth_sessions	{"id": 3, "account_id": 2, "created_at": "2026-08-22T08:05:41.058063+00:00", "expires_at": "2026-08-29T08:05:41.172421+00:00", "revoked_at": "2026-08-22T08:05:41.276647+00:00", "token_hash": "0f3b9b7f35164aebdedc31b4e33a68152048f6b611574c28b8c64da04a501121", "last_seen_at": "2026-08-22T08:05:41.242876+00:00", "csrf_token_hash": "049d328a15c5d30f538d39989e2e05fb9f1c2f39149d1ef907810be840931d8f"}	2026-08-22 09:08:50.623502+00
1048	auth_sessions	{"id": 10, "account_id": 2, "created_at": "2026-08-22T08:40:19.723567+00:00", "expires_at": "2026-08-29T08:40:19.860366+00:00", "revoked_at": null, "token_hash": "3a58aa2143f2e1c431ac81ab1936251d1bb3ca47ae5b221685282e65d6d4cce3", "last_seen_at": "2026-08-22T09:02:20.87202+00:00", "csrf_token_hash": "48edc120b5fa473b9456e64786cdd4b5479f4e5c2c9a2247928c9acb92fcb5b5"}	2026-08-22 09:08:50.623502+00
1049	auth_sessions	{"id": 4, "account_id": 2, "created_at": "2026-08-22T08:06:29.669389+00:00", "expires_at": "2026-08-29T08:06:29.786684+00:00", "revoked_at": "2026-08-22T08:06:29.863963+00:00", "token_hash": "62c8200c8f405c01f6011db4a0efad09b48e15626c0d8eeb0f298222abc4c8f6", "last_seen_at": "2026-08-22T08:06:29.84275+00:00", "csrf_token_hash": "b6533cb19517b74bb6c2e497c673d145b0d5458752417eefe74bddee94b02c1c"}	2026-08-22 09:08:50.623502+00
1050	auth_sessions	{"id": 5, "account_id": 2, "created_at": "2026-08-22T08:12:51.440205+00:00", "expires_at": "2026-08-29T08:12:51.534233+00:00", "revoked_at": "2026-08-22T08:12:51.610617+00:00", "token_hash": "12d8d97d99c5b8d88ae40cad90001004993fc8f5b4cd146438673715f74017bd", "last_seen_at": "2026-08-22T08:12:51.586906+00:00", "csrf_token_hash": "1391c094c83bafd5ac4fedb52c5c07b20e26e56e954032ca9b5d8c2338fb73ac"}	2026-08-22 09:08:50.623502+00
1051	auth_sessions	{"id": 11, "account_id": 1, "created_at": "2026-08-22T08:42:10.994618+00:00", "expires_at": "2026-08-29T08:42:11.112895+00:00", "revoked_at": null, "token_hash": "1b58c9f21d8fa6ff1e0b852f83f9b036c5223f1c4a76c3313e8af72250d19742", "last_seen_at": "2026-08-22T08:42:11.132066+00:00", "csrf_token_hash": "2b56193fd7a20ee69878a92ecfa494279420a4651f6917f67c05ec097f02654e"}	2026-08-22 09:08:50.623502+00
1052	semesters	{"id": 266, "code": "DURATION-9046A2DF", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:15:34.302638+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:15:34.323177+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1053	semesters	{"id": 51, "code": "API-8B1E0622", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:05:53.367899+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:05:53.415286+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1054	semesters	{"id": 93, "code": "API-2B1264C3", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:06:38.548264+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:06:38.587156+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1055	semesters	{"id": 9, "code": "API-34EFEA76", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T07:56:16.605722+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T07:56:16.657769+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1056	semesters	{"id": 55, "code": "DURATION-F3238129", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:05:53.905758+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:05:53.922999+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1057	semesters	{"id": 13, "code": "DURATION-F13B59FE", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T07:56:17.573411+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T07:56:17.595333+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1058	semesters	{"id": 97, "code": "DURATION-C7D7D89A", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:06:39.253491+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:06:39.275784+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1059	semesters	{"id": 136, "code": "API-A874680A", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:13:04.698839+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:13:04.748585+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1060	semesters	{"id": 140, "code": "DURATION-A5A229BE", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:13:05.478769+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:13:05.508999+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1061	semesters	{"id": 252, "code": "FAST-59B11380", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T08:15:07.354104+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T08:15:07.473444+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1062	semesters	{"id": 210, "code": "FAST-8320BD28", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T08:14:21.005838+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T08:14:21.142875+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1063	semesters	{"id": 178, "code": "API-E26FDB4E", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:13:56.894098+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:13:56.941776+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1064	semesters	{"id": 182, "code": "DURATION-1D03C342", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:13:57.43494+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:13:57.455119+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1065	semesters	{"id": 262, "code": "API-DA7261BC", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:15:33.642419+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:15:33.846833+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1066	semesters	{"id": 41, "code": "FAST-4EA09BA6", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T07:56:49.640504+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T07:56:49.762322+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1067	semesters	{"id": 125, "code": "FAST-8881BD33", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T08:07:05.51429+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T08:07:05.659861+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1068	semesters	{"id": 83, "code": "FAST-E97D005A", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T08:06:14.126287+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T08:06:14.311131+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1069	semesters	{"id": 1, "code": "SU26", "name": "Summer 2026", "note": null, "status": "ACTIVE", "end_date": "2026-08-23", "created_at": "2026-08-22T07:56:01.318366+00:00", "created_by": null, "start_date": "2026-05-11", "updated_at": "2026-08-22T08:16:44.251356+00:00", "updated_by": 2, "academic_year": "2026-2027"}	2026-08-22 09:08:50.623502+00
1070	semesters	{"id": 220, "code": "API-C06DA1C2", "name": "API Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:14:46.826847+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:14:47.034727+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
1071	semesters	{"id": 168, "code": "FAST-3B575A2E", "name": "Fast Track Semester", "note": "Updated note", "status": "CLOSED", "end_date": "2036-04-15", "created_at": "2026-08-22T08:13:28.068888+00:00", "created_by": 2, "start_date": "2036-01-01", "updated_at": "2026-08-22T08:13:28.213853+00:00", "updated_by": 2, "academic_year": "2036-2037"}	2026-08-22 09:08:50.623502+00
1072	semesters	{"id": 224, "code": "DURATION-16B43913", "name": "Duration Test Semester", "note": null, "status": "CLOSED", "end_date": "2030-04-15", "created_at": "2026-08-22T08:14:47.567173+00:00", "created_by": 2, "start_date": "2030-01-01", "updated_at": "2026-08-22T08:14:47.590065+00:00", "updated_by": 2, "academic_year": "2030-2031"}	2026-08-22 09:08:50.623502+00
\.


--
-- Data for Name: excel_council_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_council_groups (council_id, project_code, group_code, project_id, group_id) FROM stdin;
\.


--
-- Data for Name: excel_defense_councils; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_defense_councils (id, batch_id, defense_type, excel_row, council_code, council_date, day_code, chair_code, secretary_code, member_1_code, member_2_code, member_3_code, member_count, group_count, member_list, canonical_round_id, raw_values) FROM stdin;
\.


--
-- Data for Name: excel_import_batches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_import_batches (id, source_file_name, source_path, imported_at, notes) FROM stdin;
\.


--
-- Data for Name: excel_projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_projects (id, batch_id, excel_row, project_code, group_code, title_en, title_vi, supervisor_display_name, supervisor_1_code, supervisor_2_code, canonical_project_id, canonical_group_id, raw_values) FROM stdin;
\.


--
-- Data for Name: excel_review_schedule_rows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_review_schedule_rows (id, batch_id, review_type, excel_row, schedule_code, week_code, day_code, slot_number, wds_code, group_number, schedule_date, date_of_week, room_name, reviewer_1_code, reviewer_2_code, count_value, canonical_round_id, canonical_session_id, raw_values) FROM stdin;
\.


--
-- Data for Name: excel_sheet_rows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_sheet_rows (id, batch_id, sheet_name, row_number, values_jsonb, formulas_jsonb, non_empty) FROM stdin;
\.


--
-- Data for Name: excel_summary_workloads; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.excel_summary_workloads (id, batch_id, excel_row, lecturer_code, department, review_1_count, review_2_count, review_3_count, defense_1_count, defense_2_count, raw_values) FROM stdin;
\.


--
-- Data for Name: group_memberships; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.group_memberships (id, group_id, student_id, membership_role, status, joined_at, left_at, reason, drop_requested_by, drop_approved_by) FROM stdin;
25	41	318	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
26	41	335	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
27	41	369	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
28	41	380	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
29	41	404	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
30	42	329	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
31	42	331	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
32	42	405	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
33	42	406	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
34	43	321	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
35	43	332	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
36	43	358	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
37	43	387	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
38	44	308	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
39	44	320	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
40	44	334	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
41	44	370	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
42	45	348	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
43	45	350	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
44	45	359	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
45	45	403	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
46	46	373	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
47	46	374	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
48	46	375	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
49	46	377	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
50	47	307	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
51	48	386	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
52	49	309	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
53	49	311	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
54	49	333	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
55	49	367	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
56	49	368	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
57	50	349	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
58	50	352	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
59	50	379	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
60	50	384	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
61	50	407	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
62	51	354	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
63	51	390	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
64	51	397	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
65	52	360	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
66	52	361	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
67	52	362	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
68	52	378	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
69	53	337	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
70	53	339	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
71	53	341	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
72	53	342	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
73	53	344	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
74	54	306	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
75	54	385	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
76	54	388	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
77	54	389	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
78	54	391	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
79	55	340	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
80	55	343	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
81	55	400	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
82	55	401	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
83	55	402	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
84	56	345	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
85	56	381	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
86	56	382	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
87	56	383	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
88	56	399	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
89	57	310	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
90	57	313	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
91	57	376	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
92	57	398	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
93	58	312	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
94	58	322	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
95	58	326	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
96	58	351	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
97	59	336	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
98	60	314	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
99	60	316	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
100	60	323	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
101	61	317	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
102	61	347	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
103	61	363	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
104	61	364	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
105	62	324	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
106	62	325	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
107	62	330	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
108	62	355	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
109	63	334	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
110	64	407	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
111	65	365	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
112	65	366	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
113	65	371	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
114	65	372	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
115	66	319	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
116	66	327	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
117	66	328	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
118	66	338	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
119	67	315	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
120	68	392	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
121	68	393	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
122	68	394	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
123	68	395	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
124	68	396	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
125	69	346	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
126	69	353	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
127	69	356	MEMBER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
128	69	357	LEADER	ACTIVE	2026-08-22 09:08:50.914141+00	\N	\N	\N	\N
\.


--
-- Data for Name: group_slot_preferences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.group_slot_preferences (round_id, group_id, timeslot_id, selected, source, updated_by) FROM stdin;
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.groups (id, project_id, code, status) FROM stdin;
41	104	GRP-SU26SE001	PENDING_D11
43	96	GRP-SU26SE013	PENDING_D11
47	84	GRP-SU26SE017	PENDING_D11
48	48	GRP-SU26SE018	PENDING_D11
50	100	GRP-SU26SE027	PENDING_D11
51	88	GRP-SU26SE028	PENDING_D11
53	105	GRP-SU26SE051	PENDING_D11
54	98	GRP-SU26SE057	PENDING_D11
56	93	GRP-SU26SE067	PENDING_D11
59	66	GRP-SU26SE071	PENDING_D11
60	53	GRP-SU26SE080	PENDING_D11
63	87	GRP-SU26SE098	PENDING_D11
64	99	GRP-SU26SE101	PENDING_D11
66	55	GRP-SU26SE106	PENDING_D11
67	89	GRP-SU26SE109	PENDING_D11
52	35	GRP-SU26SE043	ELIGIBLE_D12
45	38	GRP-SU26SE015	ELIGIBLE_D12
68	40	GRP-SU26SE111	ELIGIBLE_D12
42	43	GRP-SU26SE003	ELIGIBLE_D12
55	44	GRP-SU26SE061	ELIGIBLE_D12
44	51	GRP-SU26SE014	ELIGIBLE_D12
46	54	GRP-SU26SE016	ELIGIBLE_D12
49	57	GRP-SU26SE023	ELIGIBLE_D12
62	59	GRP-SU26SE096	ELIGIBLE_D12
57	61	GRP-SU26SE069	ELIGIBLE_D12
58	63	GRP-SU26SE070	ELIGIBLE_D12
61	64	GRP-SU26SE082	ELIGIBLE_D12
65	65	GRP-SU26SE102	ELIGIBLE_D12
69	71	GRP-SU26SE170	ELIGIBLE_D12
\.


--
-- Data for Name: h11_waivers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.h11_waivers (id, round_id, group_id, granted_by, reason, active, created_at) FROM stdin;
\.


--
-- Data for Name: lecturer_availabilities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.lecturer_availabilities (round_id, lecturer_id, timeslot_id, state, load_preference, source, updated_by) FROM stdin;
\.


--
-- Data for Name: lecturers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.lecturers (id, account_id, lecturer_code) FROM stdin;
1	3	GV-PHUONG-LHK
2	4	GV-DUC-DNM
3	5	GV-VAN-TTN
4	6	GV-TAM-PM
5	7	GV-NHAN-DT
6	8	GV-PHUC-NT
7	9	GV-SANG-NM
8	10	GV-HOANG-NT
9	11	GV-LONG-T
10	12	GV-TAI-NT
11	13	GV-LAM-NN
12	14	GV-THONG-NT
13	15	GV-AN-NDH
14	16	GV-DUONG-VTT
15	17	GV-HUNG-LD
16	18	GV-NGUYEN-TT
17	19	GV-KHANH-KT
18	20	GV-HUONG-NTC
19	21	GV-MINH-TTH
20	22	GV-THINH-DP
21	23	GV-QUYNH-TNN
22	24	GV-TRI-PT
23	25	GV-CHI-LTQ
24	26	GV-VU-LNS
25	27	GV-TRI-PM
26	28	GV-HUY-NX
1090	2103	GV01
\.


--
-- Data for Name: majors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.majors (id, code, name) FROM stdin;
1	SE	Software Engineering
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, recipient_account_id, event_type, payload, status, sent_at, created_at, dedupe_key) FROM stdin;
\.


--
-- Data for Name: outbox_jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.outbox_jobs (id, topic, payload, status, attempts, available_at, processed_at, created_at, dedupe_key) FROM stdin;
\.


--
-- Data for Name: project_supervisors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_supervisors (project_id, lecturer_id, supervisor_type) FROM stdin;
33	1	MAIN
34	2	MAIN
34	3	CO
35	4	MAIN
36	5	MAIN
37	6	MAIN
38	7	MAIN
39	1	MAIN
40	4	MAIN
41	1	MAIN
41	8	CO
42	3	MAIN
43	9	MAIN
44	4	MAIN
45	10	MAIN
46	5	MAIN
47	5	MAIN
48	1	MAIN
49	1	MAIN
50	5	MAIN
51	7	MAIN
52	11	MAIN
53	9	MAIN
54	12	MAIN
55	13	MAIN
56	14	MAIN
57	15	MAIN
58	16	MAIN
59	17	MAIN
60	18	MAIN
61	4	MAIN
62	13	MAIN
63	4	MAIN
64	19	MAIN
65	4	MAIN
66	20	MAIN
67	21	MAIN
68	18	MAIN
69	12	MAIN
70	20	MAIN
71	22	MAIN
72	21	MAIN
73	9	MAIN
74	23	MAIN
75	10	MAIN
76	10	MAIN
77	6	MAIN
77	24	CO
78	25	MAIN
78	2	CO
79	13	MAIN
80	15	MAIN
81	15	MAIN
82	12	MAIN
83	18	MAIN
84	1	MAIN
85	11	MAIN
86	11	MAIN
87	7	MAIN
88	3	MAIN
89	8	MAIN
90	26	MAIN
90	10	CO
91	23	MAIN
92	5	MAIN
93	2	MAIN
93	3	CO
94	1	MAIN
95	11	MAIN
96	7	MAIN
97	1	MAIN
98	18	MAIN
99	7	MAIN
100	7	MAIN
101	20	MAIN
102	10	MAIN
103	20	MAIN
104	9	MAIN
105	18	MAIN
106	18	MAIN
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (id, semester_id, major_id, code, title, status, title_vi, title_en) FROM stdin;
43	1	1	SU26SE003	GodotXR: A Virtual Reality Learning Aid Application for Children with Speech Delay	ACTIVE	GodotXR: Ứng dụng thực tế ảo hỗ trợ học tập cho trẻ chậm nói	GodotXR: A Virtual Reality Learning Aid Application for Children with Speech Delay
44	1	1	SU26SE061	81 Days and Nights – A Historical First-Person Shooter Recreating the 1972 Battle of Quang Tri	ACTIVE	81 Ngày và Đêm – Game bắn súng góc nhìn thứ nhất tái hiện chiến dịch bảo vệ Thành Cổ Quảng Trị 1972	81 Days and Nights – A Historical First-Person Shooter Recreating the 1972 Battle of Quang Tri
45	1	1	SU26SE041	AI-powered system for managing experimental vegetable cultivation at the University of Agriculture	ACTIVE	Hệ thống thông minh quản lý thực nghiệm ươm trồng rau màu cho trường Đại học về Nông nghiệp	AI-powered system for managing experimental vegetable cultivation at the University of Agriculture
46	1	1	SU26SE002	AI-Powered Real Estate Advisory Platform	ACTIVE	Nền tảng tư vấn bất động sản ứng dụng AI	AI-Powered Real Estate Advisory Platform
47	1	1	SU26SE010	Advanced Nail Virtual Try-On and Booking System	ACTIVE	Hệ thống đặt lịch & công cụ thử móng thông minh	Advanced Nail Virtual Try-On and Booking System
48	1	1	SU26SE018	Design and Implementation of an AI-Powered Recruitment Process Simulation System with a Virtual AI Interview Room for Software Engineering Students	ACTIVE	Thiết kế và triển khai hệ thống mô phỏng quy trình tuyển dụng doanh nghiệp ứng dụng AI với mô hình Phòng phỏng vấn ảo cho sinh viên ngành Kỹ thuật Phần mềm	Design and Implementation of an AI-Powered Recruitment Process Simulation System with a Virtual AI Interview Room for Software Engineering Students
49	1	1	SU26SE092	IceBot – Design and Implementation of a Multi-Location Automated Ice Cream Vending System with Robotic Arm Integration	ACTIVE	IceBot – Thiết kế và triển khai hệ thống bán kem tự động đa địa điểm tích hợp tay robot	IceBot – Design and Implementation of a Multi-Location Automated Ice Cream Vending System with Robotic Arm Integration
50	1	1	SU26SE011	AI-Powered Autonomous Mobile Robot for Intelligent Supermarket Navigation and Shopping Assistance	ACTIVE	Robot di động tự hành tích hợp AI phục vụ điều hướng thông minh và hỗ trợ mua sắm trong môi trường siêu thị	AI-Powered Autonomous Mobile Robot for Intelligent Supermarket Navigation and Shopping Assistance
51	1	1	SU26SE014	LanCare Hub – Orchid Care Marketplace Platform	ACTIVE	Nền tảng Chăm sóc Hoa Lan	LanCare Hub – Orchid Care Marketplace Platform
52	1	1	SU26SE115	DaiPhat – A Lottery Sales Management System	ACTIVE	DaiPhat – Hệ thống quản lý bán vé số	DaiPhat – A Lottery Sales Management System
53	1	1	SU26SE080	Cross-Border Consignment Supply Chain Management System with Integrated AI Agent	ACTIVE	Xây dựng hệ thống quản lý chuỗi cung ứng ký gửi xuyên biên giới tích hợp AI Agent	Cross-Border Consignment Supply Chain Management System with Integrated AI Agent
54	1	1	SU26SE016	TaxMate - A platform to support tax obligations and sales management for small businesses	ACTIVE	Taxmate - Nền tảng hỗ trợ nghĩa vụ thuế và quản lý bán hàng cho hộ kinh doanh nhỏ	TaxMate - A platform to support tax obligations and sales management for small businesses
55	1	1	SU26SE106	Build an Employee Operations Management System for Vibe Solutions	ACTIVE	Xây dựng Hệ thống Quản lý Vận hành Nhân viên cho Công ty TNHH Vibe Solutions	Build an Employee Operations Management System for Vibe Solutions
56	1	1	SU26SE084	AlgoFlow: Visual Computational Thinking Simulator with AI Hints	ACTIVE	AlgoFlow: Trình mô phỏng tư duy tính toán trực quan với gợi ý của AI	AlgoFlow: Visual Computational Thinking Simulator with AI Hints
57	1	1	SU26SE023	VietStage - Virtual Artist for Vietnamese Traditional Instrument Education with Game-Based Learning	ACTIVE	VietStage - Nghệ Sĩ Ảo Dạy Nhạc Cụ Dân Tộc Với Học Tập Dựa Trên Trò Chơi	VietStage - Virtual Artist for Vietnamese Traditional Instrument Education with Game-Based Learning
58	1	1	SU26SE058	URBAN SERVICE INTERACTION AND FEEDBACK ECOSYSTEM	ACTIVE	HỆ SINH THÁI TƯƠNG TÁC VÀ PHẢN HỒI DỊCH VỤ ĐÔ THỊ	URBAN SERVICE INTERACTION AND FEEDBACK ECOSYSTEM
59	1	1	SU26SE096	Sub-leasing Management System	ACTIVE	Hệ thống quản lý kinh doanh thuê và cho thuê lại bất động sản	Sub-leasing Management System
60	1	1	SU26SE167	Smart Shopping Chatbot: RAG-integrated assistant on live product catalog	ACTIVE	Chatbot tư vấn mua sắm thông minh tích hợp RAG trên catalog sản phẩm thực tế	Smart Shopping Chatbot: RAG-integrated assistant on live product catalog
61	1	1	SU26SE069	AI-Powered Automated Attendance and Online Proctoring Platform	ACTIVE	EduGuard: Nền tảng điểm danh tự động và giám thị thi trực tuyến hỗ trợ bởi AI	AI-Powered Automated Attendance and Online Proctoring Platform
62	1	1	SU26SE104	Build an Electronic Training Record System for an Aviation Training Academy	ACTIVE	Xây dựng Hệ thống Hồ sơ Đào tạo Điện tử cho Học viện Hàng không	Build an Electronic Training Record System for an Aviation Training Academy
64	1	1	SU26SE082	Resilience Housing Supply - Intelligent Social Housing Coordination & Vetting Platform	ACTIVE	Resilience Housing Supply - Nền tảng kết nối và điều phối nguồn cung nhà ở xã hội thông minh	Resilience Housing Supply - Intelligent Social Housing Coordination & Vetting Platform
65	1	1	SU26SE102	IQGS – AI-Powered Interview Question Generation System Using RAG and LLM	ACTIVE	IQGS – Hệ thống Sinh Câu hỏi Phỏng vấn sử dụng RAG và LLM	IQGS – AI-Powered Interview Question Generation System Using RAG and LLM
66	1	1	SU26SE071	FoodResQ - Volunteer-based Food Rescue Platform	ACTIVE	Nền tảng cứu trợ và phân phối thực phẩm	FoodResQ - Volunteer-based Food Rescue Platform
67	1	1	SU26SE047	Used Household Goods Seller–Buyer Matching Platform	ACTIVE	Nền tảng kết nối người bán đồ gia dụng cũ với đơn vị thu mua	Used Household Goods Seller–Buyer Matching Platform
68	1	1	SU26SE165	Historical Site and Museum Audio Guide with Simple AR	ACTIVE	Ứng dụng hướng dẫn tham quan di tích lịch sử, bảo tàng thông qua thuyết minh tự động và AR	Historical Site and Museum Audio Guide with Simple AR
69	1	1	SU26SE072	The platform for sharing knowledge among colleagues in academia	ACTIVE	Nền tảng chia sẻ kiến thức giữa các đồng nghiệp trong giới học thuật	The platform for sharing knowledge among colleagues in academia
33	1	1	SU26SE094	SAGA: Student Activity Graph-Based Continuous Assessment for Software Engineering PBL	ACTIVE	SAGA: Hệ thống đánh giá liên tục dựa trên Đồ thị Hoạt động Sinh viên cho học phần Kỹ thuật Phần mềm theo PBL	SAGA: Student Activity Graph-Based Continuous Assessment for Software Engineering PBL
34	1	1	SU26SE068	Smart Automated Car Wash Management System with Advance Booking & Loyalty Program	ACTIVE	Hệ thống quản lý rửa xe ô tô tự động thông minh với đặt lịch trước và chương trình khách hàng thân thiết	Smart Automated Car Wash Management System with Advance Booking & Loyalty Program
35	1	1	SU26SE043	AI-Powered Interview Simulation and Assessment System	ACTIVE	Hệ thống Mô phỏng Phỏng vấn và Đánh giá Năng lực ứng dụng Trí tuệ Nhân tạo	AI-Powered Interview Simulation and Assessment System
36	1	1	SU26SE021	AI-Based Coffee Shop Design and Construction Management Platform	ACTIVE	Nền tảng hỗ trợ thiết kế và thi công quán cà phê thông minh ứng dụng AI	AI-Based Coffee Shop Design and Construction Management Platform
37	1	1	SU26SE091	FurniSpace – Build an Interactive 3D Sytem for Retail Store Design and Furniture Solutions	ACTIVE	FurniSpace – Xây dựng hệ thống tương tác 3D cho thiết kế cửa hàng bán lẻ và cung cấp giải pháp nội thất kèm theo	FurniSpace – Build an Interactive 3D Sytem for Retail Store Design and Furniture Solutions
38	1	1	SU26SE015	StockSpace - Website allows posting, searching for warehouse space and managing it after rental	ACTIVE	Không gian lưu trữ - Website cho phép đăng tải, tìm kiếm kho bãi và quản lí sau khi thuê	StockSpace - Website allows posting, searching for warehouse space and managing it after rental
39	1	1	SU26SE093	FengDesk AI – Intelligent Workspace Feng Shui Plant Recommendation & E-Commerce Platform	ACTIVE	FengDesk AI – Nền tảng thương mại điện tử về cây phong thủy kết hợp hệ thống đề xuất AI cho không gian làm việc	FengDesk AI – Intelligent Workspace Feng Shui Plant Recommendation & E-Commerce Platform
40	1	1	SU26SE111	Rogue-kie	ACTIVE	Rogue-kie: Hiểm Họa Không Gian	Rogue-kie
41	1	1	SU26SE020	AI-assisted Experiential Learning Platform with Automated Portfolio and Media Generation for Obox STEAM	ACTIVE	Nền tảng học tập trải nghiệm hỗ trợ AI với khả năng tự động tạo hồ sơ năng lực và nội dung đa phương tiện cho Obox STEAM	AI-assisted Experiential Learning Platform with Automated Portfolio and Media Generation for Obox STEAM
42	1	1	SU26SE112	WarpTalk – An AI Speech Translation Platform for Real-Time Multilingual Communication with Voice Cloning	ACTIVE	WarpTalk - Nền tảng Dịch Giọng Nói Tự Nhiên Đa Ngôn Ngữ Theo Thời Gian Thực với Công Nghệ Sao Chép Giọng Nói và với sự hỗ trợ của AI	WarpTalk – An AI Speech Translation Platform for Real-Time Multilingual Communication with Voice Cloning
70	1	1	SU26SE063	BoardVerse - An Operation and Matchmaking Platform for Board Game Cafes	ACTIVE	BoardVerse - Nền tảng Vận hành và Ghép đội dành cho Quán Board Game	BoardVerse - An Operation and Matchmaking Platform for Board Game Cafes
71	1	1	SU26SE170	Rancour - 3D Action Role-playing Game	ACTIVE	Rancour - Game 3D nhập vai góc nhìn thứ ba	Rancour - 3D Action Role-playing Game
72	1	1	SU26SE046	Used Clothing Intake and Classification System	ACTIVE	Hệ thống quản lý tiếp nhận và phân loại quần áo cũ cho từ thiện và tái chế	Used Clothing Intake and Classification System
73	1	1	SU26SE079	AI-Integrated Construction Project Management System – An Intelligent Platform for Material, Progress, and Resource Management	ACTIVE	Hệ thống Quản lý Dự án Xây dựng tích hợp AI – Nền tảng thông minh cho quản lý vật tư, tiến độ và nhân sự	AI-Integrated Construction Project Management System – An Intelligent Platform for Material, Progress, and Resource Management
63	1	1	SU26SE070	MediMate AI	ACTIVE	Trợ lý y khoa thông minh	MediMate AI
74	1	1	SU26SE035	EvidencePilot – AI-Assisted Research Evidence Mapping & Citation Traceability Platform	ACTIVE	EvidencePilot – Nền tảng AI hỗ trợ lập bản đồ bằng chứng nghiên cứu và truy vết trích dẫn	EvidencePilot – AI-Assisted Research Evidence Mapping & Citation Traceability Platform
75	1	1	SU26SE045	Forestry Resource Planning and Allocation Management System with AI Optimization	ACTIVE	Hệ thống quản lý lập kế hoạch và phân bổ tài nguyên trại thực nghiệm lâm nghiệp tích hợp AI	Forestry Resource Planning and Allocation Management System with AI Optimization
76	1	1	SU26SE039	Music Lounge and Audience Connection Platform with AI Integration	ACTIVE	Nền tảng kết nối phòng trà âm nhạc và người nghe có tích hợp AI	Music Lounge and Audience Connection Platform with AI Integration
77	1	1	SU26SE169	GreenSlot — Smart Urban Vertical Garden Rental Platform with IoT-based Monitoring and On-site Gardening Services	ACTIVE	GreenSlot — Nền tảng cho thuê vườn canh tác thẳng đứng tại đô thị tích hợp giám sát IoT và dịch vụ chăm sóc cây trồng tại chỗ	GreenSlot — Smart Urban Vertical Garden Rental Platform with IoT-based Monitoring and On-site Gardening Services
78	1	1	SU26SE053	FPT University Research Project Management System	ACTIVE	Hệ thống quản lý đề tài nghiên cứu khoa học cấp Trường đại học FPT	FPT University Research Project Management System
79	1	1	SU26SE105	Build an Instructor Qualification Management System for an Aviation Training Academy	ACTIVE	Xây dựng Hệ thống Quản lý Năng định Giảng viên cho Học viện Hàng không	Build an Instructor Qualification Management System for an Aviation Training Academy
80	1	1	SU26SE026	FinViet – AI-Powered Personal Finance Tracker and Spending Advisor for Vietnamese Gen Z	ACTIVE	FinViet – Ứng Dụng Theo Dõi Tài Chính Cá Nhân Thông Minh và Tư Vấn Chi Tiêu Bằng AI cho Giới Trẻ Việt Nam	FinViet – AI-Powered Personal Finance Tracker and Spending Advisor for Vietnamese Gen Z
81	1	1	SU26SE083	SoloDesk – Intelligent Client & Deal Management System for Independent Vietnamese Service Professionals	ACTIVE	SoloDesk – Hệ Thống Quản Lý Khách Hàng và Hợp Đồng Thông Minh Dành Cho Chuyên Gia Dịch Vụ Độc Lập Việt Nam	SoloDesk – Intelligent Client & Deal Management System for Independent Vietnamese Service Professionals
82	1	1	SU26SE089	The platform connects customers with food booths at night markets based on their personal preferences using AI tools	ACTIVE	Nền tảng kết nối khách hàng với quầy ăn tại chợ đêm dựa theo sở thích cá nhân bằng công cụ AI	The platform connects customers with food booths at night markets based on their personal preferences using AI tools
83	1	1	SU26SE049	Crowdsourced Application for Reporting Environmental Pollution	ACTIVE	Ứng dụng báo cáo điểm rác thải và ô nhiễm môi trường	Crowdsourced Application for Reporting Environmental Pollution
84	1	1	SU26SE017	Design and Implementation of a CDE System for BIM-enabled Civil Construction Projects	ACTIVE	Thiết kế và phát triển hệ thống CDE cho các dự án xây dựng dân dụng ứng dụng BIM	Design and Implementation of a CDE System for BIM-enabled Civil Construction Projects
85	1	1	SU26SE116	GodotLaunch – A Distribution Platform for Godot Engine Games	ACTIVE	GodotLaunch - Nền tảng phân phối trò chơi cho Godot Engine	GodotLaunch – A Distribution Platform for Godot Engine Games
86	1	1	SU26SE113	TaleX – A platform for short-video storytelling and digital comics	ACTIVE	TaleX - Nền tảng phát triển video truyện tranh và hoạt hình ngắn	TaleX – A platform for short-video storytelling and digital comics
87	1	1	SU26SE098	RCField – RC Cafe Operations & Marketplace Platform	ACTIVE	Nền tảng Số hóa Vận hành và Kết nối Cafe Xe RC	RCField – RC Cafe Operations & Marketplace Platform
88	1	1	SU26SE028	Build a Restaurant POS and Operations Management System	ACTIVE	Phát triển Hệ thống POS và Điều hành Vận hành Nhà hàng	Build a Restaurant POS and Operations Management System
89	1	1	SU26SE109	An Inventory, Borrowing and Hall Booking Management System for FPT University Ho Chi Minh City	ACTIVE	Hệ thống quản lý kho, mượn trả thiết bị và đặt sảnh cho Trường Đại học FPT TP.HCM	An Inventory, Borrowing and Hall Booking Management System for FPT University Ho Chi Minh City
90	1	1	SU26SE032	Family Care – Digital Family Management Solution	ACTIVE	Family Care – Giải pháp quản lý gia đình số	Family Care – Digital Family Management Solution
91	1	1	SU26SE036	CultureQuest Lite – Gamified Heritage Route & Short-Form Storytelling Platform for Local Tourism	ACTIVE	CultureQuest Lite – Nền tảng hành trình di sản và kể chuyện ngắn theo địa điểm cho du lịch văn hóa địa phương	CultureQuest Lite – Gamified Heritage Route & Short-Form Storytelling Platform for Local Tourism
92	1	1	SU26SE081	AI Intelligent Triage and Patient Flow Coordination System for Outpatient Department	ACTIVE	Hệ thống AI phân loại thông minh và điều phối luồng bệnh nhân khoa ngoại trú	AI Intelligent Triage and Patient Flow Coordination System for Outpatient Department
93	1	1	SU26SE067	GlowScan — AI-Powered Beauty-Tech E-Commerce System for Facial Skin Analysis and Personalized Skincare	ACTIVE	GlowScan — Hệ thống thương mại điện tử Beauty-Tech tích hợp AI phân tích da mặt và tư vấn skincare cá nhân hóa	GlowScan — AI-Powered Beauty-Tech E-Commerce System for Facial Skin Analysis and Personalized Skincare
106	1	1	SU26SE166	Peer-to-Peer Skill Exchange Platform	ACTIVE	Nền tảng kết nối trao đổi kỹ năng	Peer-to-Peer Skill Exchange Platform
94	1	1	SU26SE090	FreshFlow – An Intermediary Platform for Food Procurement and Logistics Optimization from Wholesale Markets for Restaurants in Ho Chi Minh City	ACTIVE	FreshFlow – Nền tảng trung gian thu mua và tối ưu hóa vận chuyển thực phẩm từ chợ đầu mối cho nhà hàng tại TP.HCM	FreshFlow – An Intermediary Platform for Food Procurement and Logistics Optimization from Wholesale Markets for Restaurants in Ho Chi Minh City
95	1	1	SU26SE114	Waterbus - System for providing information and booking tickets to visit Saigon River	ACTIVE	Waterbus - Hệ thống cung cấp thông tin và đặt vé tham quan trên sông Sài Gòn	Waterbus - System for providing information and booking tickets to visit Saigon River
96	1	1	SU26SE013	BookSwapHub - AI-Powered Old Book Marketplace, Exchange, and Real-Time Auction Platform	ACTIVE	BookSwapHub - Nền tảng mua bán, trao đổi, đấu giá sách cũ trực tuyến có tích hợp AI	BookSwapHub - AI-Powered Old Book Marketplace, Exchange, and Real-Time Auction Platform
97	1	1	SU26SE019	Development of a Smart Canteen System Using a Robotic Arm for Food Processing and Serving	ACTIVE	Phát triển hệ thống căng tin thông minh ứng dụng cánh tay robot trong xử lý và phục vụ món ăn	Development of a Smart Canteen System Using a Robotic Arm for Food Processing and Serving
98	1	1	SU26SE057	AI-based Oral Proficiency Assessment System for High school students	ACTIVE	Hệ thống hỗ trợ đánh giá bài thi nói tiếng Anh	AI-based Oral Proficiency Assessment System for High school students
99	1	1	SU26SE101	VietRide - A platform for booking, locating, and managing passenger buses	ACTIVE	VietRide - Nền tảng đặt vé, định vị và quản lý xe khách	VietRide - A platform for booking, locating, and managing passenger buses
100	1	1	SU26SE027	ColdChainX - Smart Cold Chain Monitoring and Management Platform	ACTIVE	ColdChainX - Nền tảng giám sát và quản lý chuỗi lạnh thông minh	ColdChainX - Smart Cold Chain Monitoring and Management Platform
101	1	1	SU26SE064	HabitEvolve - A Multiplayer Gamification Platform for Lifestyle Improvement	ACTIVE	HabitEvolve - Nền tảng game hóa đa người chơi hỗ trợ cải thiện lối sống	HabitEvolve - A Multiplayer Gamification Platform for Lifestyle Improvement
102	1	1	SU26SE038	AI-powered Shared Business Space Platform with Time-based Subleasing	ACTIVE	Nền tảng chia sẻ và cho thuê lại mặt bằng kinh doanh theo khung thời gian có tích hợp AI	AI-powered Shared Business Space Platform with Time-based Subleasing
103	1	1	SU26SE065	CubeNexus - A Comprehensive Speedcubing Platform for Offline Tournament Management and Online Matchmaking	ACTIVE	CubeNexus - Nền tảng Speedcubing toàn diện quản lý giải đấu trực tiếp và ghép trận trực tuyến	CubeNexus - A Comprehensive Speedcubing Platform for Offline Tournament Management and Online Matchmaking
104	1	1	SU26SE001	Solar Lithium-ion Battery Maintenance Management System – An AI-Powered Platform for Monitoring and Maintenance	ACTIVE	Hệ thống quản lý bảo trì pin lithium-ion năng lượng mặt trời – Nền tảng dựa trên model AI để giám sát và bảo trì	Solar Lithium-ion Battery Maintenance Management System – An AI-Powered Platform for Monitoring and Maintenance
105	1	1	SU26SE051	Tutora - K12 AI-Powered Tutoring Marketplace with AI system for tutor matching & homework helper	ACTIVE	Tutora — Nền tảng kết nối gia sư K-12 tích hợp AI hỗ trợ tìm gia sư và hướng dẫn giải bài tập	Tutora - K12 AI-Powered Tutoring Marketplace with AI system for tutor matching & homework helper
\.


--
-- Data for Name: remediation_cases; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.remediation_cases (id, session_result_id, group_id, due_at, status, verifier_lecturer_id, verified_at, note) FROM stdin;
\.


--
-- Data for Name: reschedule_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reschedule_requests (id, session_id, requested_by, reason, status, reviewed_by, created_at, reviewed_at, decision_note) FROM stdin;
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rooms (id, code, name, capacity, active, room_type) FROM stdin;
9	NVH G.01	NVH G.01	40	t	NORMAL
10	NVH G.02	NVH G.02	18	t	NORMAL
11	NVH G.04	NVH G.04	8	t	NORMAL
12	NVH G.05	NVH G.05	4	t	NORMAL
13	NVH 420	NVH 420	999	t	NORMAL
14	NVH 421	NVH 421	2	t	NORMAL
15	NVH.301	NVH.301	13	t	NORMAL
16	NVH.306	NVH.306	5	t	NORMAL
17	NVH.414	NVH.414	14	t	NORMAL
18	NVH.415	NVH.415	12	t	NORMAL
19	LB21 (Thư viện Campus)	LB21 (Thư viện Campus)	8	t	SEMINAR
\.


--
-- Data for Name: round_committees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_committees (round_id, committee_id, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: round_days; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_days (id, round_id, day_date) FROM stdin;
\.


--
-- Data for Name: round_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_groups (round_id, group_id) FROM stdin;
164	52
164	45
164	68
164	42
164	55
164	44
164	46
164	49
164	62
164	57
164	58
164	61
164	65
164	69
\.


--
-- Data for Name: round_invitations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_invitations (round_id, lecturer_id, status, response_reason, responded_at) FROM stdin;
\.


--
-- Data for Name: round_operation_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_operation_records (id, round_id, actor_id, action, reason, before_status, after_status, created_at) FROM stdin;
\.


--
-- Data for Name: round_room_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.round_room_types (round_id, room_type) FROM stdin;
164	NORMAL
164	SEMINAR
\.


--
-- Data for Name: rounds; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rounds (id, semester_id, type, status, session_duration_minutes, reviewer_count, registration_deadline, result_owner_mode, h12_sessions_per_part, h12_sessions_per_day, h12_semester_quota, soft_weights, created_by, created_at, group_selection_mode, start_date, end_date, max_groups_per_timeslot, max_minutes_per_part, max_minutes_per_day, name, description, group_preference_deadline, lecturer_registration_closed_at, timeframe_id, timeframe_version_id) FROM stdin;
164	1	DEFENSE_1_2	DRAFT	30	5	\N	f	4	8	\N	{}	1	2026-08-22 10:21:16.638371+00	f	2026-05-11	2026-08-23	\N	\N	\N	Bảo vệ kỳ 2 (Defense 1.2)	Imported from su26_defense_1.2_SE.xlsx; sheet Kỹ thuật phần mềm; Review 1.1 result = Bảo vệ kỳ 2.	\N	\N	\N	\N
\.


--
-- Data for Name: schedule_assignment_reviewers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedule_assignment_reviewers (assignment_id, lecturer_id, is_result_owner, snapshot_name) FROM stdin;
\.


--
-- Data for Name: schedule_assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedule_assignments (id, schedule_version_id, group_id, project_id, timeslot_id, start_at, end_at) FROM stdin;
\.


--
-- Data for Name: schedule_change_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedule_change_records (id, round_id, schedule_version_id, session_id, actor_id, reason, before_json, after_json, created_at) FROM stdin;
\.


--
-- Data for Name: schedule_versions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedule_versions (id, round_id, version_no, status, input_snapshot, algorithm_parameters, random_seed, solver_status, total_score, soft_scores, created_by, created_at, activated_at) FROM stdin;
\.


--
-- Data for Name: scheduler_jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduler_jobs (id, round_id, status, attempt, idempotency_key, input_snapshot, algorithm_parameters, random_seed, schedule_version_id, error, queued_at, started_at, finished_at) FROM stdin;
\.


--
-- Data for Name: schema_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schema_meta (key, value) FROM stdin;
product	capstone-defense-scheduler
\.


--
-- Data for Name: semester_lecturer_quotas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.semester_lecturer_quotas (semester_id, lecturer_id, quota, updated_by, updated_at) FROM stdin;
\.


--
-- Data for Name: semesters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.semesters (id, code, name, status, created_at, start_date, end_date, note, academic_year, created_by, updated_by, updated_at) FROM stdin;
1	SU26	Summer 2026	ACTIVE	2026-08-22 07:56:01.318366+00	2026-05-11	2026-08-23	\N	2026-2027	\N	2	2026-08-22 10:10:06.358606+00
\.


--
-- Data for Name: session_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.session_results (id, session_id, outcome, note, entered_by, entered_at, correction_reason, before_json, after_json, remediation_due_at, verifier_lecturer_id, verify_status, before_group_status, after_group_status) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sessions (id, schedule_version_id, group_id, timeslot_id, room_id, start_at, end_at, status, makeup_of_session_id, council_id) FROM stdin;
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.students (id, account_id, student_code) FROM stdin;
306	1999	DE180732
307	2000	QE180159
308	2001	SE150831
309	2002	SE150863
310	2003	SE151214
311	2004	SE151518
312	2005	SE160590
313	2006	SE160929
314	2007	SE161100
315	2008	SE170167
316	2009	SE170183
317	2010	SE170238
318	2011	SE170310
319	2012	SE171339
320	2013	SE171719
321	2014	SE171754
322	2015	SE171793
323	2016	SE172336
324	2017	SE172340
325	2018	SE172384
326	2019	SE172459
327	2020	SE172478
328	2021	SE172485
329	2022	SE172486
330	2023	SE172575
331	2024	SE172634
332	2025	SE172870
333	2026	SE173374
334	2027	SE180305
335	2028	SE180445
336	2029	SE180473
337	2030	SE180486
338	2031	SE180491
339	2032	SE180500
340	2033	SE180536
341	2034	SE180543
342	2035	SE180564
343	2036	SE180573
344	2037	SE180619
345	2038	SE180717
346	2039	SE181554
347	2040	SE181766
348	2041	SE182019
349	2042	SE182085
350	2043	SE182115
351	2044	SE182172
352	2045	SE182227
353	2046	SE182273
354	2047	SE182281
355	2048	SE182294
356	2049	SE182311
357	2050	SE182333
358	2051	SE182453
359	2052	SE182463
360	2053	SE182529
361	2054	SE182535
362	2055	SE182547
363	2056	SE182548
364	2057	SE182829
365	2058	SE182871
366	2059	SE182945
367	2060	SE182998
368	2061	SE183054
369	2062	SE183109
370	2063	SE183153
371	2064	SE183522
372	2065	SE183609
373	2066	SE183632
374	2067	SE183642
375	2068	SE183662
376	2069	SE183665
377	2070	SE183725
378	2071	SE183727
379	2072	SE183732
380	2073	SE183923
381	2074	SE183965
382	2075	SE184090
383	2076	SE184091
384	2077	SE184191
385	2078	SE184214
386	2079	SE184261
387	2080	SE184306
388	2081	SE184322
389	2082	SE184339
390	2083	SE184354
391	2084	SE184359
392	2085	SE184402
393	2086	SE184438
394	2087	SE184443
395	2088	SE184453
396	2089	SE184458
397	2090	SE184492
398	2091	SE184565
399	2092	SE184569
400	2093	SE184622
401	2094	SE184629
402	2095	SE184638
403	2096	SE184767
404	2097	SE184821
405	2098	SE184940
406	2099	SE185063
407	2100	SS170152
408	32	SV001
\.


--
-- Data for Name: timeframe_break_windows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.timeframe_break_windows (id, timeframe_version_id, sequence_number, name, start_time, end_time) FROM stdin;
\.


--
-- Data for Name: timeframe_versions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.timeframe_versions (id, timeframe_id, version_number, status, start_time, end_time, block_duration_minutes, group_duration_minutes, change_reason, created_by, created_at, break_between_blocks_minutes, manual_timelines) FROM stdin;
\.


--
-- Data for Name: timeframes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.timeframes (id, name, kind, archived_at, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: timeslots; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.timeslots (id, round_day_id, start_at, end_at, active, part) FROM stdin;
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_id_seq', 2108, true);


--
-- Name: audit_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_events_id_seq', 733, true);


--
-- Name: auth_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_sessions_id_seq', 15, true);


--
-- Name: committees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.committees_id_seq', 307, true);


--
-- Name: conflict_declarations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.conflict_declarations_id_seq', 1, false);


--
-- Name: councils_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.councils_id_seq', 1, false);


--
-- Name: db_cleanup_backup_20260822_160826_backup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.db_cleanup_backup_20260822_160826_backup_id_seq', 1072, true);


--
-- Name: excel_defense_councils_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_defense_councils_id_seq', 1, false);


--
-- Name: excel_import_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_import_batches_id_seq', 1, false);


--
-- Name: excel_projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_projects_id_seq', 1, false);


--
-- Name: excel_review_schedule_rows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_review_schedule_rows_id_seq', 1, false);


--
-- Name: excel_sheet_rows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_sheet_rows_id_seq', 1, false);


--
-- Name: excel_summary_workloads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.excel_summary_workloads_id_seq', 1, false);


--
-- Name: group_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.group_memberships_id_seq', 128, true);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.groups_id_seq', 69, true);


--
-- Name: h11_waivers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.h11_waivers_id_seq', 1, false);


--
-- Name: lecturers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.lecturers_id_seq', 1091, true);


--
-- Name: majors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.majors_id_seq', 299, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: outbox_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.outbox_jobs_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.projects_id_seq', 180, true);


--
-- Name: remediation_cases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.remediation_cases_id_seq', 1, false);


--
-- Name: reschedule_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reschedule_requests_id_seq', 1, false);


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rooms_id_seq', 19, true);


--
-- Name: round_days_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.round_days_id_seq', 76, true);


--
-- Name: round_operation_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.round_operation_records_id_seq', 1, false);


--
-- Name: rounds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rounds_id_seq', 164, true);


--
-- Name: schedule_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.schedule_assignments_id_seq', 1, false);


--
-- Name: schedule_change_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.schedule_change_records_id_seq', 1, false);


--
-- Name: schedule_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.schedule_versions_id_seq', 8, true);


--
-- Name: scheduler_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduler_jobs_id_seq', 1, false);


--
-- Name: semesters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.semesters_id_seq', 332, true);


--
-- Name: session_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.session_results_id_seq', 1, false);


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sessions_id_seq', 8, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.students_id_seq', 409, true);


--
-- Name: timeframe_break_windows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.timeframe_break_windows_id_seq', 64, true);


--
-- Name: timeframe_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.timeframe_versions_id_seq', 56, true);


--
-- Name: timeframes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.timeframes_id_seq', 32, true);


--
-- Name: timeslots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.timeslots_id_seq', 268, true);


--
-- Name: account_roles account_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_roles
    ADD CONSTRAINT account_roles_pkey PRIMARY KEY (account_id, role);


--
-- Name: accounts accounts_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_email_key UNIQUE (email);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_events audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (id);


--
-- Name: auth_login_throttles auth_login_throttles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_login_throttles
    ADD CONSTRAINT auth_login_throttles_pkey PRIMARY KEY (identifier);


--
-- Name: auth_sessions auth_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_pkey PRIMARY KEY (id);


--
-- Name: auth_sessions auth_sessions_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_token_hash_key UNIQUE (token_hash);


--
-- Name: committee_members committee_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committee_members
    ADD CONSTRAINT committee_members_pkey PRIMARY KEY (committee_id, lecturer_id);


--
-- Name: committees committees_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT committees_code_key UNIQUE (code);


--
-- Name: committees committees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT committees_pkey PRIMARY KEY (id);


--
-- Name: conflict_declarations conflict_declarations_lecturer_id_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations
    ADD CONSTRAINT conflict_declarations_lecturer_id_project_id_key UNIQUE (lecturer_id, project_id);


--
-- Name: conflict_declarations conflict_declarations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations
    ADD CONSTRAINT conflict_declarations_pkey PRIMARY KEY (id);


--
-- Name: council_members council_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.council_members
    ADD CONSTRAINT council_members_pkey PRIMARY KEY (council_id, lecturer_id);


--
-- Name: councils councils_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.councils
    ADD CONSTRAINT councils_pkey PRIMARY KEY (id);


--
-- Name: db_cleanup_backup_20260822_160826 db_cleanup_backup_20260822_160826_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.db_cleanup_backup_20260822_160826
    ADD CONSTRAINT db_cleanup_backup_20260822_160826_pkey PRIMARY KEY (backup_id);


--
-- Name: excel_council_groups excel_council_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_council_groups
    ADD CONSTRAINT excel_council_groups_pkey PRIMARY KEY (council_id, group_code);


--
-- Name: excel_defense_councils excel_defense_councils_batch_id_defense_type_excel_row_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_defense_councils
    ADD CONSTRAINT excel_defense_councils_batch_id_defense_type_excel_row_key UNIQUE (batch_id, defense_type, excel_row);


--
-- Name: excel_defense_councils excel_defense_councils_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_defense_councils
    ADD CONSTRAINT excel_defense_councils_pkey PRIMARY KEY (id);


--
-- Name: excel_import_batches excel_import_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_import_batches
    ADD CONSTRAINT excel_import_batches_pkey PRIMARY KEY (id);


--
-- Name: excel_projects excel_projects_batch_id_excel_row_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects
    ADD CONSTRAINT excel_projects_batch_id_excel_row_key UNIQUE (batch_id, excel_row);


--
-- Name: excel_projects excel_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects
    ADD CONSTRAINT excel_projects_pkey PRIMARY KEY (id);


--
-- Name: excel_review_schedule_rows excel_review_schedule_rows_batch_id_review_type_excel_row_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows
    ADD CONSTRAINT excel_review_schedule_rows_batch_id_review_type_excel_row_key UNIQUE (batch_id, review_type, excel_row);


--
-- Name: excel_review_schedule_rows excel_review_schedule_rows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows
    ADD CONSTRAINT excel_review_schedule_rows_pkey PRIMARY KEY (id);


--
-- Name: excel_sheet_rows excel_sheet_rows_batch_id_sheet_name_row_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_sheet_rows
    ADD CONSTRAINT excel_sheet_rows_batch_id_sheet_name_row_number_key UNIQUE (batch_id, sheet_name, row_number);


--
-- Name: excel_sheet_rows excel_sheet_rows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_sheet_rows
    ADD CONSTRAINT excel_sheet_rows_pkey PRIMARY KEY (id);


--
-- Name: excel_summary_workloads excel_summary_workloads_batch_id_excel_row_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_summary_workloads
    ADD CONSTRAINT excel_summary_workloads_batch_id_excel_row_key UNIQUE (batch_id, excel_row);


--
-- Name: excel_summary_workloads excel_summary_workloads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_summary_workloads
    ADD CONSTRAINT excel_summary_workloads_pkey PRIMARY KEY (id);


--
-- Name: group_memberships group_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_pkey PRIMARY KEY (id);


--
-- Name: group_slot_preferences group_slot_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_slot_preferences
    ADD CONSTRAINT group_slot_preferences_pkey PRIMARY KEY (round_id, group_id, timeslot_id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: groups groups_project_id_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_project_id_code_key UNIQUE (project_id, code);


--
-- Name: groups groups_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_project_id_key UNIQUE (project_id);


--
-- Name: h11_waivers h11_waivers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers
    ADD CONSTRAINT h11_waivers_pkey PRIMARY KEY (id);


--
-- Name: h11_waivers h11_waivers_round_id_group_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers
    ADD CONSTRAINT h11_waivers_round_id_group_id_key UNIQUE (round_id, group_id);


--
-- Name: lecturer_availabilities lecturer_availabilities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturer_availabilities
    ADD CONSTRAINT lecturer_availabilities_pkey PRIMARY KEY (round_id, lecturer_id, timeslot_id);


--
-- Name: lecturers lecturers_account_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturers
    ADD CONSTRAINT lecturers_account_id_key UNIQUE (account_id);


--
-- Name: lecturers lecturers_lecturer_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturers
    ADD CONSTRAINT lecturers_lecturer_code_key UNIQUE (lecturer_code);


--
-- Name: lecturers lecturers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturers
    ADD CONSTRAINT lecturers_pkey PRIMARY KEY (id);


--
-- Name: majors majors_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.majors
    ADD CONSTRAINT majors_code_key UNIQUE (code);


--
-- Name: majors majors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.majors
    ADD CONSTRAINT majors_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: outbox_jobs outbox_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbox_jobs
    ADD CONSTRAINT outbox_jobs_pkey PRIMARY KEY (id);


--
-- Name: schedule_assignment_reviewers pk_schedule_assignment_reviewers; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignment_reviewers
    ADD CONSTRAINT pk_schedule_assignment_reviewers PRIMARY KEY (assignment_id, lecturer_id);


--
-- Name: project_supervisors project_supervisors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_supervisors
    ADD CONSTRAINT project_supervisors_pkey PRIMARY KEY (project_id, lecturer_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: projects projects_semester_id_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_semester_id_code_key UNIQUE (semester_id, code);


--
-- Name: remediation_cases remediation_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases
    ADD CONSTRAINT remediation_cases_pkey PRIMARY KEY (id);


--
-- Name: remediation_cases remediation_cases_session_result_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases
    ADD CONSTRAINT remediation_cases_session_result_id_key UNIQUE (session_result_id);


--
-- Name: reschedule_requests reschedule_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reschedule_requests
    ADD CONSTRAINT reschedule_requests_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_code_key UNIQUE (code);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: round_committees round_committees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_committees
    ADD CONSTRAINT round_committees_pkey PRIMARY KEY (round_id, committee_id);


--
-- Name: round_days round_days_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_days
    ADD CONSTRAINT round_days_pkey PRIMARY KEY (id);


--
-- Name: round_days round_days_round_id_day_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_days
    ADD CONSTRAINT round_days_round_id_day_date_key UNIQUE (round_id, day_date);


--
-- Name: round_groups round_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT round_groups_pkey PRIMARY KEY (round_id, group_id);


--
-- Name: round_invitations round_invitations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_invitations
    ADD CONSTRAINT round_invitations_pkey PRIMARY KEY (round_id, lecturer_id);


--
-- Name: round_operation_records round_operation_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_operation_records
    ADD CONSTRAINT round_operation_records_pkey PRIMARY KEY (id);


--
-- Name: round_room_types round_room_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_room_types
    ADD CONSTRAINT round_room_types_pkey PRIMARY KEY (round_id, room_type);


--
-- Name: rounds rounds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT rounds_pkey PRIMARY KEY (id);


--
-- Name: schedule_assignments schedule_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT schedule_assignments_pkey PRIMARY KEY (id);


--
-- Name: schedule_change_records schedule_change_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records
    ADD CONSTRAINT schedule_change_records_pkey PRIMARY KEY (id);


--
-- Name: schedule_versions schedule_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_versions
    ADD CONSTRAINT schedule_versions_pkey PRIMARY KEY (id);


--
-- Name: schedule_versions schedule_versions_round_id_version_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_versions
    ADD CONSTRAINT schedule_versions_round_id_version_no_key UNIQUE (round_id, version_no);


--
-- Name: scheduler_jobs scheduler_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_pkey PRIMARY KEY (id);


--
-- Name: scheduler_jobs scheduler_jobs_schedule_version_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_schedule_version_id_key UNIQUE (schedule_version_id);


--
-- Name: schema_meta schema_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_meta
    ADD CONSTRAINT schema_meta_pkey PRIMARY KEY (key);


--
-- Name: semester_lecturer_quotas semester_lecturer_quotas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semester_lecturer_quotas
    ADD CONSTRAINT semester_lecturer_quotas_pkey PRIMARY KEY (semester_id, lecturer_id);


--
-- Name: semesters semesters_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_code_key UNIQUE (code);


--
-- Name: semesters semesters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_pkey PRIMARY KEY (id);


--
-- Name: session_results session_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results
    ADD CONSTRAINT session_results_pkey PRIMARY KEY (id);


--
-- Name: session_results session_results_session_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results
    ADD CONSTRAINT session_results_session_id_key UNIQUE (session_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_schedule_version_id_group_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_schedule_version_id_group_id_key UNIQUE (schedule_version_id, group_id);


--
-- Name: sessions sessions_schedule_version_id_room_id_time_range_excl; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_schedule_version_id_room_id_time_range_excl EXCLUDE USING gist (schedule_version_id WITH =, room_id WITH =, time_range WITH &&);


--
-- Name: students students_account_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_account_id_key UNIQUE (account_id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_student_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_student_code_key UNIQUE (student_code);


--
-- Name: timeframe_break_windows timeframe_break_windows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_break_windows
    ADD CONSTRAINT timeframe_break_windows_pkey PRIMARY KEY (id);


--
-- Name: timeframe_versions timeframe_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_versions
    ADD CONSTRAINT timeframe_versions_pkey PRIMARY KEY (id);


--
-- Name: timeframes timeframes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframes
    ADD CONSTRAINT timeframes_pkey PRIMARY KEY (id);


--
-- Name: timeslots timeslots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeslots
    ADD CONSTRAINT timeslots_pkey PRIMARY KEY (id);


--
-- Name: timeslots timeslots_round_day_id_start_at_end_at_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeslots
    ADD CONSTRAINT timeslots_round_day_id_start_at_end_at_key UNIQUE (round_day_id, start_at, end_at);


--
-- Name: committee_members uq_committee_members_sequence; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committee_members
    ADD CONSTRAINT uq_committee_members_sequence UNIQUE (committee_id, sequence_number);


--
-- Name: schedule_assignments uq_schedule_assignments_version_group; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT uq_schedule_assignments_version_group UNIQUE (schedule_version_id, group_id);


--
-- Name: timeframe_break_windows uq_timeframe_break_windows_sequence; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_break_windows
    ADD CONSTRAINT uq_timeframe_break_windows_sequence UNIQUE (timeframe_version_id, sequence_number);


--
-- Name: timeframe_versions uq_timeframe_versions_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_versions
    ADD CONSTRAINT uq_timeframe_versions_number UNIQUE (timeframe_id, version_number);


--
-- Name: auth_sessions_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_sessions_active_idx ON public.auth_sessions USING btree (token_hash, expires_at) WHERE (revoked_at IS NULL);


--
-- Name: ix_excel_defense_councils_batch_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_excel_defense_councils_batch_type ON public.excel_defense_councils USING btree (batch_id, defense_type, council_date);


--
-- Name: ix_excel_projects_batch_codes; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_excel_projects_batch_codes ON public.excel_projects USING btree (batch_id, project_code, group_code);


--
-- Name: ix_excel_review_schedule_batch_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_excel_review_schedule_batch_type ON public.excel_review_schedule_rows USING btree (batch_id, review_type, schedule_date);


--
-- Name: ix_excel_sheet_rows_batch_sheet; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_excel_sheet_rows_batch_sheet ON public.excel_sheet_rows USING btree (batch_id, sheet_name);


--
-- Name: ix_round_committees_committee_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_round_committees_committee_id ON public.round_committees USING btree (committee_id);


--
-- Name: ix_rounds_semester_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_rounds_semester_id ON public.rounds USING btree (semester_id);


--
-- Name: ix_rounds_timeframe_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_rounds_timeframe_id ON public.rounds USING btree (timeframe_id);


--
-- Name: ix_semesters_academic_year; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_semesters_academic_year ON public.semesters USING btree (academic_year);


--
-- Name: ix_timeframe_break_windows_version; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_timeframe_break_windows_version ON public.timeframe_break_windows USING btree (timeframe_version_id, start_time);


--
-- Name: notifications_dedupe_key_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX notifications_dedupe_key_idx ON public.notifications USING btree (dedupe_key) WHERE (dedupe_key IS NOT NULL);


--
-- Name: outbox_jobs_dedupe_key_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX outbox_jobs_dedupe_key_idx ON public.outbox_jobs USING btree (dedupe_key) WHERE (dedupe_key IS NOT NULL);


--
-- Name: round_operation_records_round_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX round_operation_records_round_idx ON public.round_operation_records USING btree (round_id, created_at);


--
-- Name: schedule_change_records_session_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX schedule_change_records_session_idx ON public.schedule_change_records USING btree (session_id, created_at);


--
-- Name: scheduler_jobs_idempotency_key_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX scheduler_jobs_idempotency_key_idx ON public.scheduler_jobs USING btree (round_id, idempotency_key) WHERE (idempotency_key IS NOT NULL);


--
-- Name: scheduler_jobs_queue_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX scheduler_jobs_queue_idx ON public.scheduler_jobs USING btree (status, queued_at);


--
-- Name: session_results_entered_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX session_results_entered_at_idx ON public.session_results USING btree (entered_at);


--
-- Name: uq_active_group_leader; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_active_group_leader ON public.group_memberships USING btree (group_id) WHERE ((status = 'ACTIVE'::public.membership_status) AND (membership_role = 'LEADER'::public.membership_role));


--
-- Name: uq_active_group_student; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_active_group_student ON public.group_memberships USING btree (group_id, student_id) WHERE (status = 'ACTIVE'::public.membership_status);


--
-- Name: uq_active_semester; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_active_semester ON public.semesters USING btree (status) WHERE (status = 'ACTIVE'::public.semester_status);


--
-- Name: uq_schedule_versions_active_per_round; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_schedule_versions_active_per_round ON public.schedule_versions USING btree (round_id) WHERE (status = 'ACTIVE'::public.schedule_version_status);


--
-- Name: uq_timeframe_versions_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_timeframe_versions_active ON public.timeframe_versions USING btree (timeframe_id) WHERE ((status)::text = 'ACTIVE'::text);


--
-- Name: uq_timeframes_active_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_timeframes_active_name ON public.timeframes USING btree (lower((name)::text)) WHERE (archived_at IS NULL);


--
-- Name: ux_sessions_makeup_of_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ux_sessions_makeup_of_session_id ON public.sessions USING btree (makeup_of_session_id) WHERE (makeup_of_session_id IS NOT NULL);


--
-- Name: audit_events audit_events_append_only; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER audit_events_append_only BEFORE DELETE OR UPDATE ON public.audit_events FOR EACH ROW EXECUTE FUNCTION public.reject_audit_mutation();


--
-- Name: council_members council_members_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER council_members_immutable BEFORE INSERT OR DELETE OR UPDATE ON public.council_members FOR EACH ROW EXECUTE FUNCTION public.prevent_council_member_mutation();


--
-- Name: councils councils_immutable; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER councils_immutable BEFORE DELETE OR UPDATE ON public.councils FOR EACH ROW EXECUTE FUNCTION public.prevent_council_mutation();


--
-- Name: sessions sessions_council_valid; Type: TRIGGER; Schema: public; Owner: -
--

CREATE CONSTRAINT TRIGGER sessions_council_valid AFTER INSERT OR UPDATE OF council_id ON public.sessions DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.validate_session_council();


--
-- Name: account_roles account_roles_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_roles
    ADD CONSTRAINT account_roles_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;


--
-- Name: audit_events audit_events_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.accounts(id);


--
-- Name: auth_sessions auth_sessions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;


--
-- Name: committee_members committee_members_committee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committee_members
    ADD CONSTRAINT committee_members_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES public.committees(id) ON DELETE CASCADE;


--
-- Name: committee_members committee_members_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committee_members
    ADD CONSTRAINT committee_members_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: committees committees_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT committees_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: conflict_declarations conflict_declarations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations
    ADD CONSTRAINT conflict_declarations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: conflict_declarations conflict_declarations_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations
    ADD CONSTRAINT conflict_declarations_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: conflict_declarations conflict_declarations_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conflict_declarations
    ADD CONSTRAINT conflict_declarations_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: council_members council_members_council_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.council_members
    ADD CONSTRAINT council_members_council_id_fkey FOREIGN KEY (council_id) REFERENCES public.councils(id) ON DELETE RESTRICT;


--
-- Name: council_members council_members_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.council_members
    ADD CONSTRAINT council_members_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: councils councils_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.councils
    ADD CONSTRAINT councils_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: councils councils_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.councils
    ADD CONSTRAINT councils_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE RESTRICT;


--
-- Name: councils councils_supersedes_council_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.councils
    ADD CONSTRAINT councils_supersedes_council_id_fkey FOREIGN KEY (supersedes_council_id) REFERENCES public.councils(id) ON DELETE RESTRICT;


--
-- Name: excel_council_groups excel_council_groups_council_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_council_groups
    ADD CONSTRAINT excel_council_groups_council_id_fkey FOREIGN KEY (council_id) REFERENCES public.excel_defense_councils(id) ON DELETE CASCADE;


--
-- Name: excel_council_groups excel_council_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_council_groups
    ADD CONSTRAINT excel_council_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE SET NULL;


--
-- Name: excel_council_groups excel_council_groups_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_council_groups
    ADD CONSTRAINT excel_council_groups_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE SET NULL;


--
-- Name: excel_defense_councils excel_defense_councils_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_defense_councils
    ADD CONSTRAINT excel_defense_councils_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.excel_import_batches(id) ON DELETE CASCADE;


--
-- Name: excel_defense_councils excel_defense_councils_canonical_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_defense_councils
    ADD CONSTRAINT excel_defense_councils_canonical_round_id_fkey FOREIGN KEY (canonical_round_id) REFERENCES public.rounds(id) ON DELETE SET NULL;


--
-- Name: excel_projects excel_projects_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects
    ADD CONSTRAINT excel_projects_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.excel_import_batches(id) ON DELETE CASCADE;


--
-- Name: excel_projects excel_projects_canonical_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects
    ADD CONSTRAINT excel_projects_canonical_group_id_fkey FOREIGN KEY (canonical_group_id) REFERENCES public.groups(id) ON DELETE SET NULL;


--
-- Name: excel_projects excel_projects_canonical_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_projects
    ADD CONSTRAINT excel_projects_canonical_project_id_fkey FOREIGN KEY (canonical_project_id) REFERENCES public.projects(id) ON DELETE SET NULL;


--
-- Name: excel_review_schedule_rows excel_review_schedule_rows_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows
    ADD CONSTRAINT excel_review_schedule_rows_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.excel_import_batches(id) ON DELETE CASCADE;


--
-- Name: excel_review_schedule_rows excel_review_schedule_rows_canonical_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows
    ADD CONSTRAINT excel_review_schedule_rows_canonical_round_id_fkey FOREIGN KEY (canonical_round_id) REFERENCES public.rounds(id) ON DELETE SET NULL;


--
-- Name: excel_review_schedule_rows excel_review_schedule_rows_canonical_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_review_schedule_rows
    ADD CONSTRAINT excel_review_schedule_rows_canonical_session_id_fkey FOREIGN KEY (canonical_session_id) REFERENCES public.sessions(id) ON DELETE SET NULL;


--
-- Name: excel_sheet_rows excel_sheet_rows_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_sheet_rows
    ADD CONSTRAINT excel_sheet_rows_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.excel_import_batches(id) ON DELETE CASCADE;


--
-- Name: excel_summary_workloads excel_summary_workloads_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.excel_summary_workloads
    ADD CONSTRAINT excel_summary_workloads_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.excel_import_batches(id) ON DELETE CASCADE;


--
-- Name: round_committees fk_round_committees_committee_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_committees
    ADD CONSTRAINT fk_round_committees_committee_id FOREIGN KEY (committee_id) REFERENCES public.committees(id) ON DELETE RESTRICT;


--
-- Name: round_committees fk_round_committees_round_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_committees
    ADD CONSTRAINT fk_round_committees_round_id FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: group_memberships group_memberships_drop_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_drop_approved_by_fkey FOREIGN KEY (drop_approved_by) REFERENCES public.accounts(id);


--
-- Name: group_memberships group_memberships_drop_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_drop_requested_by_fkey FOREIGN KEY (drop_requested_by) REFERENCES public.accounts(id);


--
-- Name: group_memberships group_memberships_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: group_memberships group_memberships_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: group_slot_preferences group_slot_preferences_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_slot_preferences
    ADD CONSTRAINT group_slot_preferences_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: group_slot_preferences group_slot_preferences_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_slot_preferences
    ADD CONSTRAINT group_slot_preferences_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: group_slot_preferences group_slot_preferences_timeslot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_slot_preferences
    ADD CONSTRAINT group_slot_preferences_timeslot_id_fkey FOREIGN KEY (timeslot_id) REFERENCES public.timeslots(id);


--
-- Name: group_slot_preferences group_slot_preferences_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_slot_preferences
    ADD CONSTRAINT group_slot_preferences_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.accounts(id);


--
-- Name: groups groups_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: h11_waivers h11_waivers_granted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers
    ADD CONSTRAINT h11_waivers_granted_by_fkey FOREIGN KEY (granted_by) REFERENCES public.accounts(id);


--
-- Name: h11_waivers h11_waivers_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers
    ADD CONSTRAINT h11_waivers_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: h11_waivers h11_waivers_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.h11_waivers
    ADD CONSTRAINT h11_waivers_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: lecturer_availabilities lecturer_availabilities_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturer_availabilities
    ADD CONSTRAINT lecturer_availabilities_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: lecturer_availabilities lecturer_availabilities_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturer_availabilities
    ADD CONSTRAINT lecturer_availabilities_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: lecturer_availabilities lecturer_availabilities_timeslot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturer_availabilities
    ADD CONSTRAINT lecturer_availabilities_timeslot_id_fkey FOREIGN KEY (timeslot_id) REFERENCES public.timeslots(id);


--
-- Name: lecturer_availabilities lecturer_availabilities_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturer_availabilities
    ADD CONSTRAINT lecturer_availabilities_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.accounts(id);


--
-- Name: lecturers lecturers_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecturers
    ADD CONSTRAINT lecturers_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- Name: notifications notifications_recipient_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_recipient_account_id_fkey FOREIGN KEY (recipient_account_id) REFERENCES public.accounts(id);


--
-- Name: project_supervisors project_supervisors_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_supervisors
    ADD CONSTRAINT project_supervisors_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: project_supervisors project_supervisors_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_supervisors
    ADD CONSTRAINT project_supervisors_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: projects projects_major_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_major_id_fkey FOREIGN KEY (major_id) REFERENCES public.majors(id);


--
-- Name: projects projects_semester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_semester_id_fkey FOREIGN KEY (semester_id) REFERENCES public.semesters(id);


--
-- Name: remediation_cases remediation_cases_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases
    ADD CONSTRAINT remediation_cases_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: remediation_cases remediation_cases_session_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases
    ADD CONSTRAINT remediation_cases_session_result_id_fkey FOREIGN KEY (session_result_id) REFERENCES public.session_results(id);


--
-- Name: remediation_cases remediation_cases_verifier_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_cases
    ADD CONSTRAINT remediation_cases_verifier_lecturer_id_fkey FOREIGN KEY (verifier_lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: reschedule_requests reschedule_requests_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reschedule_requests
    ADD CONSTRAINT reschedule_requests_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.accounts(id);


--
-- Name: reschedule_requests reschedule_requests_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reschedule_requests
    ADD CONSTRAINT reschedule_requests_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.accounts(id);


--
-- Name: reschedule_requests reschedule_requests_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reschedule_requests
    ADD CONSTRAINT reschedule_requests_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: round_committees round_committees_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_committees
    ADD CONSTRAINT round_committees_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: round_days round_days_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_days
    ADD CONSTRAINT round_days_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: round_groups round_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT round_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: round_groups round_groups_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_groups
    ADD CONSTRAINT round_groups_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: round_invitations round_invitations_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_invitations
    ADD CONSTRAINT round_invitations_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: round_invitations round_invitations_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_invitations
    ADD CONSTRAINT round_invitations_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: round_operation_records round_operation_records_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_operation_records
    ADD CONSTRAINT round_operation_records_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.accounts(id);


--
-- Name: round_operation_records round_operation_records_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_operation_records
    ADD CONSTRAINT round_operation_records_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: round_room_types round_room_types_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.round_room_types
    ADD CONSTRAINT round_room_types_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: rounds rounds_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT rounds_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: rounds rounds_semester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT rounds_semester_id_fkey FOREIGN KEY (semester_id) REFERENCES public.semesters(id);


--
-- Name: rounds rounds_timeframe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT rounds_timeframe_id_fkey FOREIGN KEY (timeframe_id) REFERENCES public.timeframes(id);


--
-- Name: rounds rounds_timeframe_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rounds
    ADD CONSTRAINT rounds_timeframe_version_id_fkey FOREIGN KEY (timeframe_version_id) REFERENCES public.timeframe_versions(id);


--
-- Name: schedule_assignment_reviewers schedule_assignment_reviewers_assignment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignment_reviewers
    ADD CONSTRAINT schedule_assignment_reviewers_assignment_id_fkey FOREIGN KEY (assignment_id) REFERENCES public.schedule_assignments(id) ON DELETE CASCADE;


--
-- Name: schedule_assignment_reviewers schedule_assignment_reviewers_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignment_reviewers
    ADD CONSTRAINT schedule_assignment_reviewers_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: schedule_assignments schedule_assignments_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT schedule_assignments_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: schedule_assignments schedule_assignments_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT schedule_assignments_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: schedule_assignments schedule_assignments_schedule_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT schedule_assignments_schedule_version_id_fkey FOREIGN KEY (schedule_version_id) REFERENCES public.schedule_versions(id) ON DELETE CASCADE;


--
-- Name: schedule_assignments schedule_assignments_timeslot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_assignments
    ADD CONSTRAINT schedule_assignments_timeslot_id_fkey FOREIGN KEY (timeslot_id) REFERENCES public.timeslots(id);


--
-- Name: schedule_change_records schedule_change_records_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records
    ADD CONSTRAINT schedule_change_records_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.accounts(id);


--
-- Name: schedule_change_records schedule_change_records_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records
    ADD CONSTRAINT schedule_change_records_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: schedule_change_records schedule_change_records_schedule_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records
    ADD CONSTRAINT schedule_change_records_schedule_version_id_fkey FOREIGN KEY (schedule_version_id) REFERENCES public.schedule_versions(id);


--
-- Name: schedule_change_records schedule_change_records_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_change_records
    ADD CONSTRAINT schedule_change_records_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: schedule_versions schedule_versions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_versions
    ADD CONSTRAINT schedule_versions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: schedule_versions schedule_versions_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_versions
    ADD CONSTRAINT schedule_versions_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: scheduler_jobs scheduler_jobs_round_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_round_id_fkey FOREIGN KEY (round_id) REFERENCES public.rounds(id) ON DELETE CASCADE;


--
-- Name: scheduler_jobs scheduler_jobs_schedule_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_schedule_version_id_fkey FOREIGN KEY (schedule_version_id) REFERENCES public.schedule_versions(id) ON DELETE CASCADE;


--
-- Name: semester_lecturer_quotas semester_lecturer_quotas_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semester_lecturer_quotas
    ADD CONSTRAINT semester_lecturer_quotas_lecturer_id_fkey FOREIGN KEY (lecturer_id) REFERENCES public.lecturers(id) ON DELETE CASCADE;


--
-- Name: semester_lecturer_quotas semester_lecturer_quotas_semester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semester_lecturer_quotas
    ADD CONSTRAINT semester_lecturer_quotas_semester_id_fkey FOREIGN KEY (semester_id) REFERENCES public.semesters(id) ON DELETE CASCADE;


--
-- Name: semester_lecturer_quotas semester_lecturer_quotas_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semester_lecturer_quotas
    ADD CONSTRAINT semester_lecturer_quotas_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.accounts(id);


--
-- Name: semesters semesters_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: semesters semesters_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semesters
    ADD CONSTRAINT semesters_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.accounts(id);


--
-- Name: session_results session_results_entered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results
    ADD CONSTRAINT session_results_entered_by_fkey FOREIGN KEY (entered_by) REFERENCES public.accounts(id);


--
-- Name: session_results session_results_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results
    ADD CONSTRAINT session_results_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- Name: session_results session_results_verifier_lecturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session_results
    ADD CONSTRAINT session_results_verifier_lecturer_id_fkey FOREIGN KEY (verifier_lecturer_id) REFERENCES public.lecturers(id);


--
-- Name: sessions sessions_council_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_council_id_fkey FOREIGN KEY (council_id) REFERENCES public.councils(id) ON DELETE RESTRICT;


--
-- Name: sessions sessions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: sessions sessions_makeup_of_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_makeup_of_session_id_fkey FOREIGN KEY (makeup_of_session_id) REFERENCES public.sessions(id);


--
-- Name: sessions sessions_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- Name: sessions sessions_schedule_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_schedule_version_id_fkey FOREIGN KEY (schedule_version_id) REFERENCES public.schedule_versions(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_timeslot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_timeslot_id_fkey FOREIGN KEY (timeslot_id) REFERENCES public.timeslots(id);


--
-- Name: students students_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- Name: timeframe_break_windows timeframe_break_windows_timeframe_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_break_windows
    ADD CONSTRAINT timeframe_break_windows_timeframe_version_id_fkey FOREIGN KEY (timeframe_version_id) REFERENCES public.timeframe_versions(id) ON DELETE CASCADE;


--
-- Name: timeframe_versions timeframe_versions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_versions
    ADD CONSTRAINT timeframe_versions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: timeframe_versions timeframe_versions_timeframe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframe_versions
    ADD CONSTRAINT timeframe_versions_timeframe_id_fkey FOREIGN KEY (timeframe_id) REFERENCES public.timeframes(id) ON DELETE CASCADE;


--
-- Name: timeframes timeframes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeframes
    ADD CONSTRAINT timeframes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.accounts(id);


--
-- Name: timeslots timeslots_round_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeslots
    ADD CONSTRAINT timeslots_round_day_id_fkey FOREIGN KEY (round_day_id) REFERENCES public.round_days(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict XDR8nbrReKDDnhFWmI8sCo7dplCN6p2qxSfbDAB7DlwZdvifhuCIPxrXDg5PJ8D

