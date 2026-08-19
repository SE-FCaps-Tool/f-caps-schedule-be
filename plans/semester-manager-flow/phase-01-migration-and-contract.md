# Phase 01 — Migration and data contract

## Goal

Add semester metadata required by the Manager list/detail contract without
breaking imported legacy rows.

## Changes

- Add migration `0017_semester_manager_metadata`:
  - `note TEXT NULL`;
  - `academic_year VARCHAR(9)`;
  - `created_by BIGINT NULL REFERENCES accounts(id)`;
  - `updated_by BIGINT NULL REFERENCES accounts(id)`;
  - `updated_at TIMESTAMPTZ` backfilled from `created_at`;
  - backfill `academic_year` as `start_year-start_year+1`;
  - index `semesters.academic_year` and `rounds.semester_id`.
- Keep actor IDs nullable for Excel/imported rows.
- Add response models for actor summaries and semester counts/audit fields.
- Add typed query/request models for `status`, `academic_year`, and set-current.

## Acceptance

- Alembic upgrade succeeds from the current head.
- Existing rows retain code/name/dates/status and receive deterministic academic year.
- Existing rows receive null note/actor values unless a reliable source exists.
- Enum remains exactly `ACTIVE,CLOSED`; no `UPCOMING` rows exist.
