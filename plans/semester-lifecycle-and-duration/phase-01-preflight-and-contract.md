# Phase 01 — Preflight và contract

## Goal

Confirm the current database backfill requirement and freeze the HTTP contract before
touching migration or route code.

## Tasks

1. Query all existing `semesters` rows, their status, dependent rounds and foreign keys.
2. Apply the deterministic backfill mapping for legacy `DRAFT` rows. Current local row:
   `SE-2026-2027` / `Excel import: SE_CapstoneProject_SP26_ReviewDefense_New` becomes:

   ```text
   start_date = 2026-05-11
   end_date   = 2026-08-23
   duration   = 105 inclusive calendar days
   ```

   This is a reasonable 3.5-month period aligned with the SP26 Excel source.
4. Update request/response examples in `docs/api/master-data.md`, `docs/api/schemas.md`
   and `docs/api/README.md`.
5. Define transition endpoint:

   ```http
   POST /api/v1/semesters/{semester_id}/transition
   {
     "target_status": "ACTIVE",
     "reason": "Semester is ready to open."
   }
   ```

## Acceptance

- Every legacy semester has a deterministic backfill date pair; the current `SE-2026-2027`
  row uses `2026-05-11` through `2026-08-23`.
- OpenAPI contract explicitly omits create-time status and documents `UPCOMING` default.
- Transition matrix is documented as `UPCOMING → ACTIVE → CLOSED` only.
