# Phase 08 — Hardening, benchmark, security and release readiness

## Goal

Prove the measurable success criteria and produce a reproducible demo/release package for the capstone.

## Stories covered

All P1/P2 stories and all non-functional requirements.

## Tasks

1. Run full unit, integration, contract, property, Playwright and migration tests.
2. Run the 74/26/40/4 scheduler benchmark repeatedly; record p50/p95, solver status, scheduled count and soft-score breakdown.
3. Run concurrency tests for publish, manual edit, result correction, multi-record mutation and worker retries.
4. Run authorization matrix tests and security checks for cookie/session, CSRF, file upload, SQL injection, IDOR and audit leakage.
5. Verify audit append-only behavior and backup/restore rehearsal.
6. Verify browser compatibility for the two latest Chrome, Edge and Safari versions available in the target environment.
7. Execute acceptance checklist against every SC-01–SC-13 and attach evidence paths.
8. Prepare seed/demo data, operator guide, deployment variables, migration instructions and rollback procedure.
9. Review stale documentation and mark the implementation contract/source precedence.

## Tests to write first

- Full success-criteria acceptance suite.
- Load/benchmark regression threshold test.
- Restore-from-backup smoke test.
- Session expiry/CSRF/IDOR/security regression suite.
- Browser and accessibility smoke matrix.

## Exit criteria

- All success criteria have executable evidence or an explicitly documented pilot measurement.
- No release-blocking hard-constraint, authorization, transition, audit or data-loss defect remains.
- Demo can be recreated from a clean checkout with documented commands.

Current evidence index: [success-criteria-matrix.md](../../docs/success-criteria-matrix.md), [Phase 08 evidence](../../docs/phase-08-evidence-2026-08-18.md) and [release checklist](../../docs/release-checklist.md). Automated gates are passing; pilot completion remains intentionally open for the criteria marked “Pilot measurement open”.
