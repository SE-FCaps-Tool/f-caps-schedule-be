# Phase 09 — Lecturer and leader portal APIs

## Objective

Provide the exact self-service portal routes required by the separated frontend.

## Scope

- Lecturer: invitations, availability, sessions/detail, supervised projects, and remediations.
- Leader: dashboard, sessions/detail, group preferences, and result/progression views.
- Enforce contextual assignments without treating Reviewer/Supervisor/Leader as system roles.
- Remove internal solver fields from student/lecturer payloads.

## Tests to write first

- Role matrix and object-scope tests for every `/lecturer/me/*` and `/leader/me/*` route.
- Session privacy tests for reviewer/student/leader perspectives.
- Portal pagination and empty-state contract tests.

## Acceptance criteria

Spec sections 31–40 are covered; checklist B4–B11 is closed; portal payloads use the shared envelope and stable identifiers.
