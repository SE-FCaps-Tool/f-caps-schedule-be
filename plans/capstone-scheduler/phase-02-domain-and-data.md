# Phase 02 — Domain model, migrations, state machines, policy and audit

## Goal

Establish the authoritative persistence model and reusable domain services before scheduling any data.

## Stories covered

US-1 Admin master data; US-3 Manager academic data; US-4 round setup; US-10 Manager monitoring/result authority.

## Tasks

1. Reconcile PRD/ERD/schema against `spec.md`; document removed H13 and minute-based H12 fields.
2. Create enums and migrations for account status, system roles, semesters, projects, groups, membership history, round lifecycle, session status, result outcomes and audit actions.
3. Model rounds, round days, timeslots, rooms, invited reviewers, schedule versions, sessions and session reviewers with immutable version identity.
4. Model contextual assignments and result-owner assignment without creating independent account roles.
5. Add remediation, H11 waiver, reschedule request, notification and outbox job entities; do not add an Excel/import-batch contract.
6. Add database uniqueness/check constraints and range/exclusion constraints for real-time overlap backstops.
7. Implement explicit round transition service and group transition service, including postponed/cancelled behavior.
8. Implement authorization policy service and audit service; mutation routes must call both.
9. Define the stable seed-fixture contract; load the 26 Lecturer / 74 group fixture in Phase 03 with the master-data forms.

## Tests to write first

- Every allowed/forbidden round transition, including `POSTPONED`, `CANCELLED` and `LOCKED`.
- Every Defense 1.1, Defense 1.2 and Defense 2 group transition from the spec.
- Result Owner mode on/off, Review no-owner rule, and Manager correction audit.
- Admin/Manager/Lecturer/Student resource authorization matrix.
- H11 waiver requires Manager, scope, reason and active audit; no waiver path for H1–H10/H12.
- Membership/Leader invariants and approved dropout history.
- Database rollback and overlap exclusion tests.

## Exit criteria

- New migrations represent the spec without H13 or minute-based H12 enforcement.
- Domain transition/policy/audit services have stable codes and test coverage.
- Existing docs are marked as reconciled inputs; implementation has one source of truth.
