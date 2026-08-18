# Spec: Semester lifecycle và thời lượng học kỳ

**Date:** 2026-08-18
**Status:** Ready

---

## Problem Statement

API tạo semester hiện chỉ lưu code, name và status, chưa lưu thời gian bắt đầu/kết thúc.
Frontend cần biết một kỳ kéo dài bao lâu và hệ thống cần có trạng thái chuẩn
`UPCOMING`, `ACTIVE`, `CLOSED` để phân biệt kỳ sắp diễn ra, kỳ đang chạy và kỳ đã kết thúc.

---

## User Stories

- **[P1]** As a `MANAGER` or `ADMIN`, I want to create a semester with start and end dates so that frontend and backend can display the semester period.
  Accepted when: `POST /api/v1/semesters` accepts `start_date` and `end_date` in `YYYY-MM-DD` format and the `201` response returns both values.

- **[P1]** As a `MANAGER` or `ADMIN`, I want a new semester to default to `UPCOMING` so that a newly created semester is not accidentally treated as the current active semester.
  Accepted when: omitting `status` from `POST /api/v1/semesters` persists and returns `status: "UPCOMING"`.

- **[P1]** As the system, I want to validate the configured semester duration so that a semester is limited to approximately 3.5–4 months.
  Accepted when: the request is accepted only when the inclusive date difference is between the configured minimum and maximum duration; invalid duration returns `422` with a stable error code.

- **[P1]** As a frontend developer, I want semester list responses to include lifecycle and period fields so that I can render filters, badges and date ranges without another request.
  Accepted when: `GET /api/v1/semesters` returns `id`, `code`, `name`, `start_date`, `end_date`, `status` and `created_at` for every row.

- **[P1]** As an administrator, I want to change a semester from `UPCOMING` to `ACTIVE` and then `CLOSED` so that the lifecycle can be managed after creation.
  Accepted when: a dedicated status transition API validates the allowed transitions, enforces one active semester and records an audit event.

- **[P3]** _(out of scope — noted for future)_ Automatically derive semester status from the current date without an explicit manager/admin action.

---

## Functional Requirements

1. FR-01: Extend `SemesterCreate` with required `start_date: date` and `end_date: date` fields. Accept ISO `YYYY-MM-DD` values only.
2. FR-02: Keep `code`, `name` and existing role authorization. `POST /api/v1/semesters` remains available only to `ADMIN` and `MANAGER`.
3. FR-03: Change the semester status enum to exactly `UPCOMING`, `ACTIVE`, `CLOSED`; `POST /api/v1/semesters` must not allow a caller-supplied status and always creates `UPCOMING`.
4. FR-04: Add configurable duration limits to application settings, with defaults representing 3.5–4 months (105–120 inclusive calendar days): `SEMESTER_MIN_DURATION_DAYS=105` and `SEMESTER_MAX_DURATION_DAYS=120`.
5. FR-05: Validate `end_date >= start_date` and `duration_days = (end_date - start_date).days + 1` against the configured inclusive limits. Return `422` with code `SEMESTER_DURATION_INVALID` when validation fails.
6. FR-06: Preserve the existing unique semester code rule and return `409 DATA_DUPLICATE` when the code already exists.
7. FR-07: Preserve the rule that at most one semester can have status `ACTIVE`; transitioning another semester to `ACTIVE` returns `422 ACTIVE_SEMESTER_EXISTS`.
8. FR-08: Return the persisted date and status fields from `POST /api/v1/semesters` with `201 Created`.
9. FR-09: Return the persisted date and status fields from `GET /api/v1/semesters` with `200 OK`.
10. FR-10: Add an Alembic migration for the enum/date columns and migrate existing `DRAFT` rows to `UPCOMING` before removing the old enum value.
11. FR-11: Keep audit logging for semester creation and include `start_date`, `end_date` and `status` in the audit payload.
12. FR-12: Add API, migration and validation tests for valid duration, too-short duration, too-long duration, reversed dates, default status, duplicate code and active-semester uniqueness.
13. FR-13: Add `POST /api/v1/semesters/{semester_id}/transition` for `ADMIN` and `MANAGER` with body `{ "target_status": "ACTIVE|CLOSED", "reason": "..." }`.
14. FR-14: Allow only `UPCOMING → ACTIVE` and `ACTIVE → CLOSED`; reject reverse transitions and direct `UPCOMING → CLOSED` with `422 SEMESTER_STATUS_INVALID`.
15. FR-15: Return `{ "id": semester_id, "status": target_status }` from a successful transition and write an audit event containing actor, reason, previous status and new status.

---

## Non-Functional Requirements

- Performance: semester create/list validation adds no more than one database query beyond the current create/list path; `GET /api/v1/semesters` p95 remains below 500 ms for 1,000 semester rows.
- Security: only `ADMIN` and `MANAGER` may create/list semesters; mutation requests continue to require the session cookie and CSRF header.
- Availability: migration must be transactional and must not truncate existing semester or round data.
- Compatibility: existing clients that omit `status` receive `UPCOMING`; clients must be updated to send the new date fields once this spec is implemented.

---

## Success Criteria

- [x] `POST /api/v1/semesters` with a 105–120 day inclusive period returns `201` and persists `UPCOMING` by default.
- [x] Requests with duration `< 105` or `> 120` days return `422 SEMESTER_DURATION_INVALID`.
- [x] Requests with `end_date < start_date` return `422 SEMESTER_DURATION_INVALID`.
- [x] `GET /api/v1/semesters` returns `start_date`, `end_date` and one of `UPCOMING`, `ACTIVE`, `CLOSED` for every row.
- [x] Existing `DRAFT` semester rows are migrated to `UPCOMING` without data loss.
- [x] Existing duplicate-code and one-active-semester constraints continue to pass their regression tests.

---

## Out of Scope

- Importing semester dates from Excel.
- Automatically changing status based on the current date.
- Changing round status or schedule status as a side effect of semester status changes.
- Adding timezone-aware timestamps; this spec uses calendar dates.
- Designing the frontend screens; FE only consumes the expanded API contract.

---

## Assumptions

- A semester period is represented by calendar dates, not datetimes.
- The configured 3.5–4 month range is represented as 105–120 inclusive calendar days.
- Existing `DRAFT` data is legacy data and should become `UPCOMING`.
- The current one-active-semester database rule remains valid.
- Frontend may pre-validate the date range, but backend validation remains the source of truth.
