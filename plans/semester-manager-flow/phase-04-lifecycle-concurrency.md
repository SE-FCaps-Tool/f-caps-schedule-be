# Phase 04 — Close and set-current lifecycle

## Goal

Implement safe semester switching while preserving one active semester.

## Changes

- Transition endpoint accepts only `ACTIVE → CLOSED`, sets updater metadata,
  and writes `SEMESTER_STATUS_CHANGED`.
- Add `POST /api/v1/semesters/{semester_id}/set-current`.
- Use `pg_advisory_xact_lock` with one fixed lifecycle key, then lock target and
  existing active rows in deterministic ID order.
- Close the old active row before activating the target; update both rows and
  write `SEMESTER_SET_CURRENT` events with before/after snapshots.
- Return the complete target representation; already-active target is idempotent.

## Acceptance

- Closed target becomes active and previous active becomes closed atomically.
- Concurrent set-current requests leave exactly one active row.
- Missing target returns typed 404.
