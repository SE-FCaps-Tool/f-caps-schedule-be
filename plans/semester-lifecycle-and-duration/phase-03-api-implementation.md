# Phase 03 — API implementation

## Goal

Implement create/list validation and explicit lifecycle transitions while preserving role
authorization and error conventions.

## Files

- `apps/api/app/routes/master_data.py`
- `apps/api/app/domain` only if a reusable semester transition function is needed
- `apps/api/app/config.py` settings dependency usage

## Tasks

1. Change `SemesterCreate` to require `start_date` and `end_date`; remove caller-controlled status.
2. Validate inclusive duration against configured settings and return:

   ```json
   {
     "detail": {
       "code": "SEMESTER_DURATION_INVALID",
       "message": "Semester duration must be between the configured limits."
     }
   }
   ```

3. Create semesters as `UPCOMING` in the insert statement.
4. Return dates/status from `POST /semesters` and `GET /semesters`.
5. Add `SemesterTransitionPayload` with `target_status` and required `reason`.
6. Add `POST /semesters/{semester_id}/transition` for `ADMIN` and `MANAGER`.
7. Lock the target row, validate transition, enforce one active semester and update atomically.
8. Write audit event with actor, reason, before status and after status.
9. Preserve `401`, `403`, `404`, `409` and `422` conventions.

## Acceptance

- New semester always returns `UPCOMING`, even if an old client sends a status field.
- `UPCOMING → ACTIVE` and `ACTIVE → CLOSED` succeed.
- `UPCOMING → CLOSED`, reverse transitions and missing reason fail with stable `422` errors.
- A second active transition fails with `ACTIVE_SEMESTER_EXISTS`.

