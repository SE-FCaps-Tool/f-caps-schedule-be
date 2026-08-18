# Phase 06 — Results, remediation and group transitions

## Goal

Record only Scheduler-only final outcomes and deterministically move groups through the approved state machine.

## Stories covered

US-10 result entry/monitoring; supports US-9 visibility.

## Tasks

1. Build result command/read models for Review, Defense 1.1, Defense 1.2 and Defense 2.
2. Enforce Result Owner only for Defense 1.1/Defense 2 when mode is enabled; Review and Defense 1.2 follow spec rules.
3. Implement Manager direct entry/correction with required reason and before/after audit.
4. Implement Defense 1.1 four-level mapping, remediation deadline/verifier and overdue warning.
5. Implement verifier pass/fail and Manager-only overdue fail decision; do not auto-fail.
6. Implement Defense 1.2 completion-only outcome and no accidental failure transition from operational postponement/cancellation.
7. Implement Defense 2 binary PASS/FAIL, final transition, no remediation and no reviewer continuity.
8. Add result visibility controls for Manager, authorized Reviewer, Supervisor, Leader and Student.
9. Add reminder/overdue events through the outbox.

## Tests to write first

- Exhaustive transition table for each round type/outcome and invalid outcome rejection.
- D1.1 levels 1/2/3/4 and remediation pass/overdue paths.
- D1.2 completed/postponed/cancelled session paths.
- D2 PASS/FAIL final paths and rejected remediation/continuity attempts.
- Result Owner mode, Manager correction and audit evidence.
- Result privacy query matrix.

## Exit criteria

- 100% of result transitions in the spec have isolated tests.
- No detailed scoring/ballot/evidence data exists in the V1 result model.
- Group state and session history remain consistent after retries.

