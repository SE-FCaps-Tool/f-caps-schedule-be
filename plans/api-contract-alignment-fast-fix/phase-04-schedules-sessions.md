# Phase 4 — Schedule generation, versions, and sessions

## Objective

Expose the existing scheduler/version state machine through the exact generate, version, active,
discard, and session response contract expected by the frontend.

## Scope

- Normalize `POST /rounds/{roundId}/schedules/generate` request `{}` and response fields:
  `versionId`, `versionNumber`, `status`, `scheduledCount`, `unscheduledCount`, `overallScore`,
  `scores`.
- Normalize `GET /rounds/{roundId}/schedules`, detail, set-active, discard, and
  `GET /rounds/{roundId}/sessions`; accept `scheduleId`/`versionId` aliases.
- Expose unscheduled diagnostics and score names without leaking internal database names or solver
  objects. Preserve partial-solution persistence and no-duplicate-session behavior.
- Add documented readiness counts/blocking issues/warnings and transition guards.

## Likely files and ownership

- `apps/api/app/routes/target_schedule_contract.py` — target paths and DTO mapping.
- `apps/api/app/routes/schedule_operations.py`, `app/scheduler/versions.py`, `snapshot.py` — delegate
  state transitions and persistence.
- `apps/api/app/response_models.py` — schedule/session DTOs.
- `apps/api/tests/test_target_schedule_contract.py`, `test_phase05_api.py`, benchmark fixtures.

## Tests to write first

- Generate returns exact target fields for complete and partial solutions.
- Version list/detail/set-active/discard path IDs and state conflicts.
- Active version materializes planned sessions once; draft generation does not duplicate sessions.
- Session response includes round/group/room/council fields and excludes solver internals.
- Readiness is blocked with stable diagnostics and passes when all required inputs exist.

## Acceptance criteria

- FE sample in spec §§57–64 validates against target response models.
- Target `versionId` and `sessionId` are prefixed strings; old integer IDs remain accepted.
- H1–H13, partial-solution, immutable-council, activation, and benchmark tests remain green.
- No room is introduced into solver input; room assignment remains Phase 5.

## Rollback

Keep the legacy `/schedule/run` and `/schedule/versions` handlers as a fallback. Disable target
schedule aliases without deleting versions or sessions.

