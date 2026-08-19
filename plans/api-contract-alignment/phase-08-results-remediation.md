# Phase 08 — Results, progression, and remediation

## Objective

Align result entry, project progression, remediation verification, and manager remediation views.

## Scope

- Target session result contract and result visibility.
- Project progression/results views for manager and leader.
- Lecturer remediation verification route.
- Semester remediation list, overdue detection, and `POST /api/v1/remediations/{remediationId}/actions/overdue-fail` with Manager authorization, deadline validation, idempotency, and audit output.

## Tests to write first

- Result validation by round type and reviewer role.
- Progression calculations for pass, conditional, failed, and remedial outcomes.
- Verifier scope, duplicate verification, overdue, and fail transitions.
- Overdue-fail action tests for before/after deadline, repeated requests, already-verified rows, and forbidden roles.
- Leader/manager privacy tests.

## Acceptance criteria

Spec sections 35–36 and 74–76 are covered; checklist A6, A8, A9, and B8 are closed; result history remains auditable.
