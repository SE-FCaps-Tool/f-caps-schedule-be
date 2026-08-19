# Phase 06 — Room assignment, publish readiness, and publishing

## Objective

Complete the target room and publication contract after schedule activation.

## Scope

- Room CRUD with explicit `GET /api/v1/rooms`, `POST /api/v1/rooms`, and `PATCH /api/v1/rooms/{roomId}` contracts, target `RoomType`/`RoomStatus` values, and archived guards.
- Available-room, suggest, and apply-suggestions routes with the target request body.
- Publish-readiness and publish action routes with structured blockers.
- Global room conflict validation and audit events.

## Tests to write first

- Room status/type validation and update authorization.
- Room list/create/update contract tests, including duplicate room codes and inactive-room filtering.
- Suggest/apply idempotency, stale suggestion rejection, and conflict serialization.
- Publish readiness blocker matrix and publish transition tests.

## Acceptance criteria

Spec sections 28–30 and 65–70 are covered; checklist A4, B2, and B3 are closed; publication never bypasses readiness or immutable-council rules.
