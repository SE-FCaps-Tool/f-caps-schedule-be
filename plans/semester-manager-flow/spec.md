# Spec: Hoàn thiện Semester Manager Flow

**Date:** 2026-08-19
**Status:** Ready

---

## Problem Statement

Màn quản lý học kỳ của Manager cần hiển thị đầy đủ thống kê, bộ lọc, chi tiết
và các action vòng đời. API hiện tại mới trả dữ liệu cơ bản và chưa có audit
fields hoặc thao tác chuyển một kỳ đã đóng thành kỳ hiện tại. Phạm vi này là
backend contract hoàn chỉnh, đủ để FE tích hợp ngay sau khi API được triển khai.

## User Stories

- **[P1]** As a `MANAGER`, I want to list semesters with project/group/round counts so that I can see the scope of each semester without opening multiple screens.
  Accepted when: every list item returns `project_count`, `group_count`, and `round_count` calculated by `semester_id`.

- **[P1]** As a `MANAGER`, I want to filter semesters by search text, status, and academic year so that I can find a semester quickly.
  Accepted when: `search`, `status`, and `academic_year` are optional query parameters and combined with AND semantics.

- **[P1]** As a `MANAGER`, I want to view one semester's complete detail so that the detail/edit screen has one stable API contract.
  Accepted when: `GET /api/v1/semesters/{semester_id}` returns fields, counts, and audit actor/timestamp fields or a typed 404.

- **[P1]** As a `MANAGER`, I want to create and edit a semester so that its code, name, note, and date range remain correct.
  Accepted when: create defaults status to `ACTIVE`; code is unique; dates are ordered and inclusive duration is 105–120 days; PATCH updates `note`, `updated_by`, and `updated_at`.

- **[P1]** As a `MANAGER`, I want to close a semester so that completed academic data cannot remain current.
  Accepted when: only `ACTIVE → CLOSED` is accepted by the transition endpoint and the action is audited.

- **[P1]** As a `MANAGER`, I want to select a closed semester as current so that the system can switch the active academic context.
  Accepted when: one transaction changes the selected semester to `ACTIVE`, changes the previous active semester to `CLOSED`, and writes audit events for every changed row.

- **[P2]** As a `MANAGER`, I want actor names in audit fields so that I can understand who created or last edited a semester.
  Accepted when: response actor fields include account id, email, and display name when the account is known.

## Functional Requirements

1. FR-01: Semester status enum exposed by the API and database is exactly `ACTIVE | CLOSED`.
2. FR-02: `POST /api/v1/semesters` persists `ACTIVE` and rejects creation when the unique active-semester constraint is violated with `409 ACTIVE_SEMESTER_EXISTS`.
3. FR-03: `GET /api/v1/semesters` supports optional `search`, `status`, and `academic_year` filters and returns counts for projects, groups, and rounds.
4. FR-04: Search is case-insensitive and matches semester code or name; status accepts only `ACTIVE` or `CLOSED`.
5. FR-05: Academic-year filtering uses the requested `YYYY-YYYY` value against the semester date range/year metadata and is deterministic for a semester spanning two calendar years.
6. FR-06: `GET /api/v1/semesters/{semester_id}` returns the same complete shape as a list item plus full audit fields.
7. FR-07: `PATCH /api/v1/semesters/{semester_id}` allows code, name, note, start date, and end date; it cannot directly mutate status or academic year.
8. FR-08: Add `note TEXT NULL`, `academic_year VARCHAR(9)`, `created_by`, `updated_by`, and `updated_at` columns to `semesters`; retain `created_at`. Actor IDs reference `accounts` and may be null for imported legacy rows.
9. FR-09: Create, edit, close, and set-current operations write append-only audit events with before/after JSON and actor id.
10. FR-10: `POST /api/v1/semesters/{semester_id}/transition` accepts only `{ "target_status": "CLOSED", "reason": string }`.
11. FR-11: Add `POST /api/v1/semesters/{semester_id}/set-current`; it accepts an existing `ACTIVE` or `CLOSED` semester, locks all semester rows involved, and atomically enforces exactly one `ACTIVE` semester.
12. FR-12: Setting the already-active semester as current is idempotent and returns its complete semester representation.
13. FR-13: Existing legacy `UPCOMING` rows are migrated to `ACTIVE` or `CLOSED` while preserving the one-active invariant; no `UPCOMING` value remains after migration.

## Non-Functional Requirements

- Performance: list and detail queries must use indexed semester joins and return within 500 ms for 10,000 semesters and 100,000 projects/groups/rounds in local benchmark conditions.
- Security: all management endpoints require `ADMIN` or `MANAGER`; mutations require the existing CSRF protection.
- Consistency: set-current must be a single database transaction and be safe under concurrent requests.
- Compatibility: existing list/create/PATCH/transition routes remain available; the new fields are additive except for removal of `UPCOMING`.

## Success Criteria

- [ ] `GET /api/v1/semesters` returns all form fields including `note`, three counts, and four audit fields.
- [ ] Search/status/academic-year filters return only matching rows and can be combined.
- [ ] Detail, create, patch, close, and set-current endpoints have passing API tests for success, 404, validation, permission, duplicate, and concurrent-active cases.
- [ ] Database migration leaves enum values exactly `ACTIVE,CLOSED` and at most one active semester.
- [ ] `docker compose up --build` completes `db-init` and seed data without any `UPCOMING` rows.

## Out of Scope

- Deleting semesters.
- Editing project/group/round data through the semester endpoint.
- A separate `is_current` column; `ACTIVE` is the current semester marker.
- Rebuilding historical audit events whose actor cannot be inferred.

## Assumptions

- There is at most one `ACTIVE` semester at any time.
- Creating a semester always attempts `ACTIVE`; callers must close/switch the current one before creating another active semester.
- Legacy imported rows without actor metadata retain null actor fields.

## [NEEDS CLARIFICATION]

<!-- None. -->
