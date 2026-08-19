# Phase 03 — Create, update, and audit metadata

## Goal

Make create/edit operations populate system fields and append-only audit events.

## Changes

- Create under the semester lifecycle advisory lock with status `ACTIVE`,
  `created_by`, `updated_by`, and `updated_at`.
- Write `SEMESTER_CREATED` with a complete after snapshot.
- Refactor PATCH to lock the row, merge fields, normalize code/name/note, validate
  dates and 105–120 inclusive duration, and update only an explicit column
  whitelist.
- Write `SEMESTER_UPDATED` with before/after snapshots.
- Return the shared complete representation from create and PATCH.

## Acceptance

- Second active create returns `409 ACTIVE_SEMESTER_EXISTS`.
- PATCH cannot mutate status or academic year directly.
- `note` is optional, persisted, returned, and included in before/after audit snapshots.
- Creator/updater actors and timestamps are visible in responses.
