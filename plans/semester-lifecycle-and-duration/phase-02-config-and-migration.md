# Phase 02 — Configuration và database migration

## Goal

Persist semester period and lifecycle values safely across existing databases.

## Files

- `apps/api/app/config.py`
- `apps/api/migrations/versions/0013_semester_lifecycle.py` (new, down revision `0012_excel_import_data`)
- relevant migration/schema tests

## Tasks

1. Add settings:
   - `semester_min_duration_days = 105` from `SEMESTER_MIN_DURATION_DAYS`.
   - `semester_max_duration_days = 120` from `SEMESTER_MAX_DURATION_DAYS`.
2. Add `start_date DATE` and `end_date DATE` to `semesters`.
3. Backfill existing rows from Phase 01 mapping before applying `NOT NULL`.
4. Add a database check for `end_date >= start_date`; keep the configurable 105–120 duration
   validation in the API so environment overrides remain possible.
5. Replace `semester_status` values with `UPCOMING`, `ACTIVE`, `CLOSED`.
6. Convert existing `DRAFT` rows to `UPCOMING` before removing the old enum value.
7. Recreate/retain the partial unique index allowing only one `ACTIVE` semester.
8. Make migration downgrade-safe where PostgreSQL enum/data constraints permit; document any irreversible enum step.

## Acceptance

- `alembic upgrade head` is transactional and succeeds with the current row.
- Existing semester ID/code and all round foreign keys are unchanged.
- The current row is `UPCOMING` and has the approved dates.
- Invalid date ordering cannot be persisted.
