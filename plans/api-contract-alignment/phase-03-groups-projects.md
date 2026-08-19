# Phase 03 — Group and project target routes

## Objective

Implement the nested group/project APIs and the missing member, leader, assignment, progression, and result views.

## Scope

- Semester-scoped group/project list and create routes.
- Group members detail, change-leader, leave/drop, and project assignment routes.
- Project detail, progression, and results routes.
- `POST /api/v1/semesters/{semesterId}/projects/import` multipart import with row-level success/error reporting, plus target import route aliases and manager authorization.
- Pagination, filtering, `{data,meta}`, and audit events.

## Tests to write first

- Nested list/create/detail route contract tests.
- Atomic leader change and leave/drop authorization tests.
- Nullable project assignment and reassignment tests.
- Multipart project import tests covering invalid rows, duplicate keys, partial-failure policy, and audit output.
- Progression/result visibility tests for manager, leader, lecturer, and student.

## Acceptance criteria

The phase closes checklist A1, A3, A8, and A9 and covers spec sections 11–18 and 41–48. Existing flat aliases remain green.

## Dependencies and rollback

Depends on Phase 2 DTO/status helpers. Disable target routes without changing group/project rows if rollback is required.
