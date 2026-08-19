# Plan: Scheduling Architecture Alignment

**Source:** `plans/scheduling-architecture-alignment/spec.md`, derived from
`docs/capstone-fe-be-implementation-spec.md`
**Mode:** `--hard` (planner fallback; existing research was used)
**Risk:** high — four schema migrations, a CP-SAT model contract change, and lifecycle/concurrency
changes across scheduling, publishing, room allocation, results, and access-control queries.
**Test flag:** default; each phase adds or updates tests with the implementation.
**Status:** 🟡 In Progress

## Scope and spec quality

- **Exists?** The current API has scheduling, activation, draft editing, room-bearing sessions,
  publishing, and controlled changes, but its persistence boundaries contradict the target design.
- **Minimum?** Preserve current public routes where possible; change the underlying lifecycle and
  add only the four Room Assignment routes and the `GROUP_ABSENT` action required by the spec.
- **Spec quality:** PASS. P1/P2 behavior and measurable acceptance criteria exist. The P3
  Group/Project progression ownership question is explicitly resolved out of scope.
- **Migration premise:** the repository has no production dataset, but every migration still has a
  working downgrade. Downgrades may use documented semantic mappings where the old enum has no
  equivalent value.

## Locked architecture decisions

1. **Lifecycle vocabulary is real DB vocabulary.** There is no API-only alias. Legacy `VALID`
   rows are classified by `activated_at`: NULL becomes `DRAFT`, non-NULL becomes `ACTIVE`.
   `SUPERSEDED` becomes `DISCARDED`.
2. **Session `ONGOING` is removed, not renamed to a new session state.** The target model puts
   `ONGOING` on `rounds`; an in-progress session remains `SCHEDULED` until it becomes
   `COMPLETED`, `POSTPONED`, `GROUP_ABSENT`, or `CANCELLED`. Existing session rows with
   `ONGOING` migrate to `SCHEDULED`.
3. **The solver owns Time + Council only.** `Candidate`, `generate_candidates`, `solve_schedule`,
   solver scoring/deduplication, unscheduled diagnostics, benchmark input, and input snapshots
   contain no room dimension. `ScheduledSession.room_id` remains nullable because the shared
   validator also validates materialized sessions after room assignment; H3 runs only when both
   compared sessions have a room.
4. **Draft output is normalized and durable.** Phase 3 introduces
   `schedule_assignments` and `schedule_assignment_reviewers`. Each assignment preserves the
   solved `project_id` as well as its group/timeslot; activation rejects a stale assignment if the
   live Group->Project link changed. Draft detail/edit/compare/delete use those tables. Generated
   DRAFT versions never own sessions; activation materializes them.
5. **Activation is the lifecycle boundary.** Generate inserts a `DRAFT` version plus assignments,
   diagnostics, and scores. Activation serializes on the round, changes exactly one
   `DRAFT -> ACTIVE`, changes any previous `ACTIVE -> DISCARDED`, materializes `PLANNED`
   sessions with `room_id = NULL`, and moves the round `SCHEDULING -> SCHEDULED` atomically.
   Post-publish replacement-version clones are an explicit operational exception: they are created
   directly as `PUBLISHED` with `SCHEDULED` sessions and discard the source atomically.
6. **Publish is also atomic.** `ACTIVE -> PUBLISHED`, `PLANNED -> SCHEDULED`, and
   `rounds.SCHEDULED -> PUBLISHED` commit with notifications/outbox records in one transaction.
7. **Rounds allow room types, not room IDs.** `round_room_types(round_id, room_type)` replaces
   `round_rooms`. This intentionally removes the ability to whitelist one physical room within an
   allowed type.
8. **Room conflicts are global among live schedules.** Room writes take transaction-scoped
   advisory locks using deterministic signed-`int8` keys in sorted room-id order and check
   overlapping sessions across all rounds and all `ACTIVE`/`PUBLISHED` versions. The existing
   per-version GiST exclusion remains a local DB backstop; it is not treated as sufficient for
   cross-version/cross-round safety.
9. **Councils are immutable.** `councils` + `council_members` replace `session_reviewers`, and
   every current `session_reviewers` consumer is migrated. Reviewer-only controlled changes create
   one Council, repoint only the target session, and preserve its PUBLISHED version. Time/room-
   bearing changes retain the replacement-version clone path: source Session/Council rows remain
   untouched, the source version becomes `DISCARDED`, and the replacement is `PUBLISHED`. A mixed
   target receives one new Council while sibling clones reuse their Council IDs.
10. **New actions are manager operations.** `GROUP_ABSENT` and all four Room Assignment routes
    require `ADMIN` or `MANAGER`; unauthenticated, Lecturer, and Student calls are rejected. PUT
    room assignment resolves scope from the target Session; round-scoped room routes additionally
    reject any session/version outside the path Round's current ACTIVE version.

## Phase order

| Phase | File | Requirements / stories | Depends on | Primary risk |
|---|---|---|---|---|
| 1 | [`phase-01-enum-rename.md`](phase-01-enum-rename.md) | FR-05, P2 lifecycle foundation + `GROUP_ABSENT` | none | enum data mapping and literal fan-out |
| 2 | [`phase-02-room-free-solver.md`](phase-02-room-free-solver.md) | FR-01, FR-07, P1 | Phase 1 | solver cardinality/constraint regression |
| 3 | [`phase-03-durable-drafts-and-activation.md`](phase-03-durable-drafts-and-activation.md) | FR-06, P2 | Phases 1–2 | normalized draft persistence and atomic activation |
| 4 | [`phase-04-room-assignment.md`](phase-04-room-assignment.md) | FR-02, FR-03, P1 | Phases 1–3 | global room-conflict concurrency |
| 5 | [`phase-05-immutable-councils.md`](phase-05-immutable-councils.md) | FR-04, P2 | Phases 1–4 | authorization/workload consumers and mixed changes |
| 6 | [`phase-06-makeup-session.md`](phase-06-makeup-session.md) | spec §73 (Postpone / Make-up), P2 | Phase 1 (POSTPONED status), Phase 4 (room helpers) | H-constraint validation for a manually-created Session outside the solver |

The order is mandatory. Room Assignment follows activation materialization because its target is a
real `PLANNED` session. Councils come last because draft reviewer assignments and materialized
session reviewer state must first have distinct ownership. Phase 6 covers a P2 story from the
target spec (§73's `POST /sessions/:sessionId/makeup`) that was never captured in this plan's own
`spec.md` FR list — it was found during a post-hoc plan-vs-spec review, not scoped up front. It
only depends on Phase 1 and Phase 4's already-landed contracts, so it can run any time after Phase
4 lands, independent of Phase 5.

## Implementation progress

- [x] Phase 1: Status Vocabulary and Lifecycle Foundation
- [x] Phase 2: Room-Free Solver
- [x] Phase 3: Durable Drafts and Activation
- [x] Phase 4: Room Assignment
- [x] Phase 5: Immutable Councils
- [x] Phase 6: Postpone Make-up Session

## Session Notes

- 2026-08-19 — Phase 1 implemented: migration `0021_schedule_lifecycle_vocab`, lifecycle literal
  fan-out, `GROUP_ABSENT` action, and result-entry guard. Targeted non-integration tests passed
  (`11 passed`). The PostgreSQL schema check was attempted but is still environment-gated by the
  local database credentials; rerun the migration/integration gates before final plan completion.
- 2026-08-19 — Phase 2 implemented: removed room dimensions from solver candidates, CP-SAT
  variables/scoring/diagnostics, snapshots, scheduler inputs, and readiness checks; made H3
  ignore overlapping unassigned sessions while retaining assigned-room conflicts. Phase 2
  targeted tests, benchmark, non-integration suite, and the room-free static audit passed; hard
  code review passed. PostgreSQL integration/migration gates remain environment-gated by the
  local database credentials and must be rerun before final plan completion.
- 2026-08-19 — Phase 3 implemented: migration `0022_durable_schedule_assignments` adds durable
  assignment and reviewer-snapshot tables, backfills legacy sessions, and supports downgrade
  reconstruction. Generation now persists normalized DRAFT assignments without sessions;
  activation validates provenance under lifecycle/resource locks and materializes PLANNED,
  room-free sessions atomically; draft detail/edit/compare/delete and publish use the durable
  assignment boundary. Phase 3 contract tests and the non-integration suite passed; hard code
  review passed. PostgreSQL integration/migration gates remain blocked by the local database
  password authentication failure and must be rerun before final plan completion.
- 2026-08-19 — Phase 4 implemented: migration `0023_round_room_types` replaces physical room
  whitelists with allowed room types and reversible type expansion on downgrade. Added the four
  manager/admin Room Assignment routes, shared eligibility/conflict validation, deterministic
  least-used suggestions, advisory room locks, atomic/idempotent batch application, and publish
  readiness checks. Phase 4 contract tests and the non-integration suite passed; hard review found
  and cleared transaction, validation, and input-schema issues. PostgreSQL integration/migration
  gates remain blocked by the local database password authentication failure.
- 2026-08-19 — Phase 6 implemented: migration `0024_session_makeup` adds nullable
  `sessions.makeup_of_session_id` plus a partial unique index (one make-up per postponed Session).
  Added `POST /sessions/{id}/makeup` (ADMIN/MANAGER only): validates the target is `POSTPONED`
  with no existing make-up, resolves the requested timeslot, defaults `reviewer_ids` to the
  original Session's Council members, validates H1/H8/H11/H12 via the shared `validate_schedule`,
  checks cross-version reviewer overlap via Phase 5's `validate_council_change`, validates an
  optional room through Phase 4's `allowed_room`/`find_room_conflict`/`lock_room_ids`, and inserts
  the new Session into the original's `schedule_version_id` with a freshly sealed Council (Phase 5
  landed concurrently mid-implementation — the route was rewritten from a `session_reviewers` draft
  to use `create_council`/`load_council_members` once `0025_immutable_councils` dropped that
  table). Phase 6 contract tests and the full non-integration suite passed (auth/role/payload
  negative tests unmarked; the DB-dependent 404 test marked `integration`). PostgreSQL
  integration/migration gates remain blocked by the same pre-existing local database password
  authentication failure documented in every prior phase's notes.
- 2026-08-19 — Phase 5 implemented: migration `0025_immutable_councils` creates sealed,
  immutable `councils`/`council_members`, backfills and requires `sessions.council_id`, and
  removes `session_reviewers`. All application consumers now read Council snapshots; activation,
  result-owner changes, controlled-change branches, and make-up sessions use immutable Council
  replacement/clone semantics with cross-round reviewer locking. Phase 5 contract tests passed
  (`18 passed`), the combined Phase 4/5 contract plus benchmark checks passed (`35 passed`), the
  full non-integration suite, Alembic head, and compile checks passed, and hard code review was
  approved. PostgreSQL integration and migration gates remain blocked by the local database
  password authentication failure (`password authentication failed for user "scheduler"`).
- 2026-08-19 — Checklist alignment follow-up: migration `0026_semester_four_states` restores
  `PLANNING`/`ACTIVE`/`CLOSED`/`ARCHIVED`, extends Semester responses and transitions, blocks
  Round creation outside `ACTIVE`, and makes all semester/round/session/project/result mutations
  reject archived parents through shared write guards. Current API docs were aligned to the same
  four-state contract.
  Legacy create-semester behavior remains backward-compatible (`ACTIVE` by default) while callers
  may explicitly create `PLANNING`; PostgreSQL migration/integration verification remains blocked
  by the local database password authentication failure.

## Migration chain

At plan time `alembic heads` is expected to report `0020_room_type`. Re-check immediately before
each phase and rebase revision/down-revision identifiers if another workstream added migrations.

1. `0021_schedule_lifecycle_vocab`: rebuild both status enums and migrate values.
2. Phase 2: no schema migration.
3. `0022_durable_schedule_assignments`: add normalized draft assignment tables and the one-ACTIVE
   partial unique index; backfill from non-materialized legacy versions before changing routes.
4. `0023_round_room_types`: create/backfill `round_room_types`, then remove `round_rooms`.
5. `0025_immutable_councils` (originally slotted `0024`, rebased after Phase 6 landed first):
   create/backfill immutable councils, add and validate `sessions.council_id`, replace all
   consumers, then remove `session_reviewers`.
6. `0024_session_makeup`: add nullable `sessions.makeup_of_session_id` plus a partial unique index.
   Purely additive, no dependency on Phase 5's schema. Landed before Phase 5; Phase 5's migration
   rebased itself to `0025_immutable_councils` with `down_revision = "0024_session_makeup"`, so the
   chain is `0023_round_room_types -> 0024_session_makeup -> 0025_immutable_councils` with no
   collision.
7. `0026_semester_four_states`: restore the target four-state Semester enum and preserve the
   one-ACTIVE invariant; downgrade maps PLANNING/ARCHIVED to CLOSED.

Each phase file specifies downgrade order and lossy mappings. Do not squash these migrations: the
intermediate states are independently testable and isolate rollback risk.

## Cross-phase verification gates

Run from `apps/api` unless a command explicitly uses Docker:

```powershell
uv run ruff check app tests
uv run pytest -m "not integration" -q
uv run pytest tests/test_benchmark.py -q
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

For every migration phase, also verify a fresh upgrade and one-step downgrade/upgrade round trip.
Do not claim a phase complete from unit tests alone when its acceptance list includes PostgreSQL
constraints, row locks, advisory locks, or concurrent requests.

## Final acceptance

- [ ] The two DB enums expose only the target values; application/test searches contain no
      scheduling uses of `VALID`, `SUPERSEDED`, or session `ONGOING`.
- [ ] Solver-path searches contain no `rooms`/`room_id`; the benchmark remains under 60 seconds
      and the validator reports zero violations.
- [ ] Generate leaves zero `sessions` rows and persists normalized draft assignments; activation
      materializes `PLANNED` sessions once and publish changes them to `SCHEDULED` atomically.
- [ ] The four Room Assignment endpoints filter ACTIVE rooms by allowed type and return structured
      global-conflict errors under concurrent cross-round/cross-version writes.
- [ ] `sessions.council_id` is non-null, Council membership is immutable, and no application query
      still references `session_reviewers`.
- [ ] Reviewer-only controlled change touches one session; mixed changes create one target Council
      while preserving source and sibling Council history.
- [ ] `POST /sessions/{id}/makeup` creates a new Session with `makeup_of_session_id` set on a
      `POSTPONED` target, enforces one make-up per original, and reuses Phase 4's room-conflict
      vocabulary for its optional room.
- [ ] Unit, integration, migration round-trip, concurrency, and benchmark gates pass.

## Explicit non-goals for the whole plan

- Moving academic progression from `groups.status` to Project.
- Literal renaming of every public route to the target document's paths.
- Wholesale error-code vocabulary replacement.
- Cloud deployment, FAP integration, or changes to the legacy top-level `apps/worker/` stub.
- Frontend work or edits outside the backend repository.
