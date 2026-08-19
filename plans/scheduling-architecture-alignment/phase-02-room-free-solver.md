# Phase 2: Room-Free Solver and Nullable H3

**Covers:** FR-01, FR-07, and P1 "scheduler owns Time + Council".
**Depends on:** Phase 1 status vocabulary.
**Risk:** high — removing a candidate dimension changes candidate cardinality, solver keys, soft
scores, unscheduled reasons, readiness checks, route persistence, and benchmark fixtures.

## Target contract

- `generate_candidates(context, groups, timeslots, reviewers)` and
  `solve_schedule(context, groups, timeslots, reviewers, ...)` have no rooms input.
- `Candidate` and every candidate-selection/deduplication/scoring key have no `room_id`.
- Solver-produced `ScheduledSession` objects use `room_id = None` only at the route/validator
  boundary; rooms never participate in CP-SAT variables, hard constraints, or soft scores.
- H13 remains the configured `max_groups_per_timeslot`; it is not derived from room count.
- H3 remains in the shared validator for post-activation schedules, but only compares two sessions
  when both `room_id` values are non-NULL. Two overlapping unassigned sessions are valid.
- Missing concrete room inventory or per-round physical-room selection never blocks generation,
  partial-solution diagnostics, or the benchmark. Phase 4 may require allowed room-type metadata as
  round configuration, but that metadata is never a solver input.

## Current-state evidence

- `Candidate.room_id` and `ScheduledSession.room_id: int` are mandatory in
  `app/scheduler/models.py`.
- `generate_candidates` takes `rooms` and creates the Cartesian product
  group × timeslot × reviewer-combination × room.
- `solve_schedule` calls `_add_resource_overlap_constraints(..., "room")`, awards an S8 score to
  the lowest room ID, includes room in selected keys, and reports `NO_ROOM`.
- `snapshot.build_input_snapshot` persists a `rooms` array as solver provenance.
- `schedule_operations._round_input` returns `room_ids`; `run_scheduler` rejects a round without
  rooms and writes the solver-selected room to each generated session.
- `replacement_suggestions` invokes the same room-bearing candidate generator.
- `validator.validate_schedule` currently treats `None == None` as H3, so merely making room
  nullable would falsely flag every pair of overlapping unassigned sessions.
- `sessions.room_id` is already nullable in `0002_domain_model.py`; no nullability migration is
  required.

## Exact files and symbols

- `apps/api/app/scheduler/models.py`: `Candidate`, `ScheduledSession`, `SolverResult`.
- `apps/api/app/scheduler/candidates.py`: `generate_candidates`, `reason_for_unscheduled`.
- `apps/api/app/scheduler/scheduler.py`: `solve_schedule`,
  `_add_resource_overlap_constraints`, `_candidate_soft_scores`, `_aggregate_soft_scores`.
- `apps/api/app/scheduler/validator.py`: H3 branch in `validate_schedule`.
- `apps/api/app/scheduler/snapshot.py`: `build_input_snapshot`.
- `apps/api/app/scheduler/benchmark.py`: `build_target_fixture` return shape.
- `apps/api/app/routes/schedule_operations.py`: `_round_input`, `run_scheduler`,
  `_to_domain_sessions`, `replacement_suggestions`.
- `apps/api/app/routes/master_data.py`: `transition_round_status` readiness/resource counts; room
  count must not gate entry to `SCHEDULING`.
- Tests: `test_candidates_and_snapshot.py`, `test_scheduler_engine.py`, `test_constraints.py`,
  `test_benchmark.py`, `test_phase05_api.py`, `test_phase06_api.py`, and readiness/transition tests.

## Migration design and downgrade implications

There is no schema migration. `sessions.room_id` remains nullable and the existing per-version
GiST exclusion constraint remains intact for assigned non-NULL rooms. Rollback is a code rollback,
but it would restore an obsolete requirement that rounds have concrete `round_rooms`; do not roll
back this phase independently after Phase 4 removes that table.

## Transaction and concurrency behavior

- Solver execution remains inside `run_scheduler`'s round-locked transaction in this phase; Phase 3
  changes persistence ownership, not the solve lock ordering.
- Reviewer overlap (H2), reviewer availability, workload/quota, group uniqueness, and H13 stay in
  CP-SAT and in the shared validator. Removing room overlap must not remove or weaken their locks or
  constraints.
- H3 is intentionally deferred. It is enforced when a room is written in Phase 4 under a room
  advisory lock and is rechecked by `validate_schedule` for publish readiness.
- The route must insert NULL when its temporary pre-Phase-3 session materialization calls for a
  room value; it must never synthesize a placeholder room.

## Implementation steps

1. Make `ScheduledSession.room_id` `int | None`; remove `room_id` from `Candidate`.
2. Remove the `rooms` parameter and nested room loop from candidate generation; remove the rooms
   parameter and `NO_ROOM` branch from unscheduled diagnosis and revise remediation text.
3. Remove rooms from `solve_schedule`, the room resource-overlap call, S8 room scoring, candidate
   selection keys, and constructed solver results. Keep reviewer overlap and H13 unchanged.
4. Change H3 to require
   `current.room_id is not None and other.room_id is not None and current.room_id == other.room_id`.
5. Remove rooms from `build_input_snapshot`; old snapshots remain readable JSON and need no data
   migration.
6. Refactor `_round_input` to return context, groups, timeslots, reviewers. Remove its
   `round_rooms` query and update every caller, including `replacement_suggestions`.
7. Remove room completeness from scheduler readiness and `run_scheduler`; write NULL in the
   transitional session insert until Phase 3 removes that insert entirely.
8. Update test/build fixtures and add explicit tests for assigned-vs-unassigned H3 behavior.
9. Run source searches to prove room traces are absent from `candidates.py` and `scheduler.py`.

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest tests/test_candidates_and_snapshot.py tests/test_scheduler_engine.py tests/test_constraints.py -q
uv run pytest tests/test_benchmark.py -q
uv run pytest -m "not integration" -q
```

Integration gate:

```powershell
docker compose exec -T api pytest tests/test_phase05_api.py tests/test_phase06_api.py -q
docker compose exec -T api pytest -q
```

Static audit:

```powershell
rg -n "rooms|room_id|NO_ROOM" app/scheduler/candidates.py app/scheduler/scheduler.py
```

The static audit must return no matches. It is acceptable and required for `room_id` to remain in
`models.ScheduledSession`, `validator.py`, route/session queries, and room-assignment work.

## Acceptance checklist

- [ ] Candidate generation and solver signatures contain no room input or room field.
- [ ] CP-SAT has no room variable, overlap constraint, score, selection key, or diagnostic.
- [ ] A round with groups, timeslots, and reviewers but no room resources can generate a draft.
- [ ] Two overlapping sessions with `room_id = None` produce no H3 violation; two overlapping
      sessions assigned the same concrete room do produce H3.
- [ ] H1/H2/H4–H13 tests still pass unchanged in meaning.
- [ ] The 74-group benchmark completes under 60 seconds with zero validator violations.
- [ ] Unit and integration suites pass.

## Explicit non-goals

- Creating Room Assignment routes or changing `round_rooms` (Phase 4).
- Moving draft assignments out of `sessions` (Phase 3).
- Removing `rooms`/`room_id` from materialized session APIs or the post-assignment validator.
- Reinterpreting H13 as physical room capacity.
