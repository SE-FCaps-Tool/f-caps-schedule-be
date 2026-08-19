# Phase 05 — Schedule versions, draft sessions, and activation

## Objective

Map the existing solver/version implementation to the target nested schedule API.

## Scope

- Schedule generate, list, detail, set-active, and discard actions under the round path.
- Nested round schedule/session list and detail routes.
- Durable draft persistence, activation preconditions, idempotency, and conflict reporting.
- Preserve room-free solver behavior and immutable council assignments.

## Tests to write first

- Generate creates a durable draft and no published session.
- List/detail/set-active/discard state machine tests.
- Activation prevents multiple active versions and guards archived rounds.
- H1–H13 validator regression and 74-group benchmark.

## Acceptance criteria

Spec sections 26–29 and 58–64 are covered; checklist B1 is closed; existing scheduler benchmarks remain under the documented limit.
