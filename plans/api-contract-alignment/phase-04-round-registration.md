# Phase 04 — Round lifecycle, registration, invitations, and availability

## Objective

Expose the target round lifecycle and self-service registration APIs while preserving transition rules.

## Scope

- Semester-scoped round list/create and round detail.
- Eligible projects, registration summary, scheduling readiness, and publish readiness inputs.
- Open/close registration actions.
- Lecturer invitation list/respond/remind and self availability.
- Group preferences GET/PUT and manager override routes.

## Tests to write first

- Valid/invalid round transitions and archived-semester rejection.
- Registration summary/readiness calculations.
- Invitation response/reminder idempotency and authorization.
- Lecturer availability and group preference visibility/mutation tests.

## Acceptance criteria

Target routes cover spec sections 19–25 and 49–57, and close checklist B4, B5, and B10. Legacy `/transition`, `/registration`, and `/my-*` aliases remain compatible.
