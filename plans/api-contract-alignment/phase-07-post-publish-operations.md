# Phase 07 — Post-publish controlled operations

## Objective

Expose the target controlled-change actions without weakening published schedule invariants.

## Scope

- Change-room, replace-reviewer, and postpone action routes.
- Preserve immutable council policy, makeup-session rules, reschedule request/decision workflow, and audit trails.
- Add compatibility aliases for current session operation paths.

## Tests to write first

- Role/scope checks for each controlled action.
- Replacement eligibility and council immutability tests.
- Postpone/makeup state transitions and duplicate-request handling.
- Cross-version audit/event consistency.

## Acceptance criteria

Spec sections 71–73 are covered and the existing Phase 5/6 scheduling invariants remain passing.
