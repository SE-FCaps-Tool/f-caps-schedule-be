# Spec: Align scheduling architecture with docs/capstone-fe-be-implementation-spec.md

**Date:** 2026-08-19
**Status:** Draft

---

## Problem Statement

`docs/capstone-fe-be-implementation-spec.md` describes a target FE+BE design for the Capstone
Defense Scheduler. A full route-by-route, enum-by-enum audit (two parallel Explore agents,
covering PHẦN I–XVI of the spec against the live `apps/api` codebase) found that most surface
differences are cosmetic (path/verb/payload naming) and can be closed incrementally without risk.
But four items are not naming differences — they are opposite architectural decisions already
baked into the schema, the CP-SAT scheduler, and every downstream route/test. Conforming to the
spec on these four requires a deliberate, reviewed migration plan rather than an ad-hoc patch,
because each one changes data that already exists in the running database and behavior that
existing integration tests assert on.

This spec scopes ONLY those four items for `/ck:plan`. Everything else identified in the audit
(pagination/filters, missing enum values that don't conflict with existing data, new read-only
endpoints, error-code aliasing) is being implemented directly, in parallel, outside this plan.

---

## User Stories

- **[P1]** As a Manager, I want Room assignment to happen only after a ScheduleVersion is
  activated (not baked into the CP-SAT solve), so that room availability changes don't force a
  full re-solve and the solver's job stays "Time + Council" as designed.
  Accepted when: `generate_candidates`/`solve_schedule` no longer take `rooms` as an input; H3
  (room conflict) is enforced in a new post-activation Room Assignment phase instead of inside
  the CP-SAT model; existing `test_benchmark.py` still finishes under 60s with zero violations
  using the new two-phase flow.

- **[P1]** As a Manager, I want a dedicated Room Assignment phase (`GET rooms/available`,
  `PUT sessions/:id/room`, `POST rooms/suggest`, `POST rooms/apply-suggestions`) after
  `set-active`, so that I can assign/reassign rooms without re-running the solver.
  Accepted when: those four endpoints exist, enforce `Room.status == ACTIVE` and
  `Room.type ∈ round.roomTypes` (see Council/room-type item below), and reject conflicts with a
  structured error instead of a raw `IntegrityError`.

- **[P2]** As a Manager, I want reviewer replacement to create a new immutable Council instead of
  cloning every Session in the ScheduleVersion, so that a one-reviewer swap doesn't touch
  unrelated sessions' history/audit trail.
  Accepted when: a `councils` table exists, `sessions.council_id` references it, and
  `POST .../controlled-change` on a reviewer field creates one new Council row + repoints only
  the target session, leaving sibling sessions' `council_id`/row untouched.

- **[P2]** As a developer, I want `ScheduleVersion`/`Session` status vocab to match the spec's
  DRAFT→ACTIVE→PUBLISHED→DISCARDED / PLANNED→SCHEDULED→COMPLETED→POSTPONED→GROUP_ABSENT→CANCELLED
  enums, and generate-vs-activate to actually be two distinct lifecycle stages (generate persists
  scores/diagnostics only; activate materializes `PLANNED` Sessions), so DRAFT versions that never
  get activated don't leave orphaned Session rows.
  Accepted when: `schedule_versions.status` and `sessions.status` Postgres enums are renamed/
  extended to the spec vocabulary; `POST schedule/run` no longer inserts `sessions` rows; the
  existing `activate` endpoint does; a `GROUP_ABSENT` session status is settable via a new or
  existing action.

- **[P3]** _(explicitly out of scope for this spec)_ Swapping which of `Group`/`Project` carries
  the academic-progression state machine (spec wants Project; current schema has it on Group via
  `groups.status`). This is flagged in the audit as the single highest-blast-radius item — it
  touches `app/domain/transitions.py`, `app/scheduler/validator.py`'s eligibility map,
  `app/domain/result_workflow.py`, and every route that reads `groups.status`. `/ck:plan` should
  treat this as [NEEDS CLARIFICATION] below and get an explicit user decision before any phase
  touches it — do not fold it into the Room/Council/Session work above.

---

## Functional Requirements

1. FR-01: Remove `rooms` from `apps/api/app/scheduler/candidates.py` candidate generation and
   `apps/api/app/scheduler/scheduler.py`'s CP-SAT model (drop the room-overlap constraint and the
   room dimension of each candidate tuple).
2. FR-02: Add a Room Assignment phase: new routes for available-rooms, single-session room
   assign/reassign, suggest, and apply-suggestions, operating on Sessions belonging to an
   activated (or later) ScheduleVersion.
3. FR-03: Re-derive round→allowed-room-types config (`round_rooms` currently links specific room
   IDs; spec wants a `roomTypes: RoomType[]` list per round) — decide whether to keep
   `round_rooms` as the room pool and add a `RoomType[]` filter on top, or replace it outright.
4. FR-04: Add a `councils` table (immutable set of reviewers + round/session linkage) and
   `sessions.council_id`; update `controlled-change`'s reviewer-replacement path to create one
   Council row instead of cloning the ScheduleVersion's sessions.
5. FR-05: Rename the actual Postgres enum values via migration — `schedule_version_status`
   (`DRAFT, VALID, PUBLISHED, SUPERSEDED` → spec's `DRAFT, ACTIVE, PUBLISHED, DISCARDED`) and
   `session_status` (add `PLANNED`, `GROUP_ABSENT`) — and update every string-matching call site
   in routes/scheduler/tests accordingly. Decided: DB-level rename, not an API-layer remap.
6. FR-06: Split `run_scheduler` (`schedule_operations.py`) into a generate step that persists only
   `schedule_versions` + score/diagnostics rows, and an activate step (already exists) that
   materializes `sessions` rows as `PLANNED`.
7. FR-07: Update `apps/api/app/scheduler/validator.py` to validate H3 (room conflict) against the
   post-activation room assignment instead of at solve time, while keeping H1/H2/H4-H13 unchanged.

---

## Non-Functional Requirements

- Performance: `apps/api/tests/test_benchmark.py` (74 groups / 26 lecturers / 40 timeslots / 4
  rooms) must still complete under 60s with zero validator violations after Room is removed from
  the solver — removing a dimension should only make the CP-SAT model smaller/faster, but must be
  re-verified since candidate count and constraint shape both change.
- Compatibility: all currently-passing tests in `apps/api/tests/` (unit + integration) must be
  updated to the new contract, not left broken — this includes `test_benchmark.py`,
  `test_phase05_api.py`, `test_phase06_api.py`, and any test asserting on `sessions.status`,
  `schedule_versions.status`, or room assignment happening during generate.
- Data safety: this repo has no production data yet (Docker-Compose-only, `docker compose down -v`
  resets everything) — migrations for FR-04/FR-05 do not need a live-data backfill path, but must
  still be reversible (`downgrade()` implemented) per repo Alembic convention.

---

## Success Criteria

- [ ] `apps/api/app/scheduler/candidates.py` and `scheduler.py` have zero references to `rooms`/
      `room_id` in the solver path.
- [ ] Four new Room Assignment endpoints exist and are covered by integration tests.
- [ ] A `councils` table exists; reviewer replacement via `controlled-change` no longer re-inserts
      unrelated sessions in the same ScheduleVersion.
- [ ] `schedule_versions.status`/`sessions.status` support the spec's DRAFT/ACTIVE/PUBLISHED/
      DISCARDED and PLANNED/SCHEDULED/COMPLETED/POSTPONED/GROUP_ABSENT/CANCELLED vocab (exact
      naming choice left to `/ck:plan`'s Step 0 scope challenge).
- [ ] `uv run pytest -m "not integration"` and the full Docker-based integration suite both pass
      with zero regressions after each phase.

---

## Out of Scope

- Group/Project progression-ownership swap (see P3 story above — separate decision, separate spec
  if the user later greenlights it).
- Full REST path/verb/payload rename to match spec literally (e.g. `/rounds/:id/schedules/generate`
  vs actual `/rounds/:id/schedule/run`) — being handled as a lower-risk parallel additive pass, not
  part of this architectural plan.
- Full error-code rename to spec's ~30-code vocabulary — same, handled separately.
- `RoomStatus` MAINTENANCE state, `RoundInvitationStatus` EXPIRED/WITHDRAWN — additive, handled
  separately (see Assumptions).

---

## Assumptions

- The "safe additive" items (missing enum values that don't conflict with existing rows, new
  read-only endpoints like scheduling-readiness/eligible-projects, pagination/filters on existing
  GET list endpoints, RoomStatus/MAINTENANCE, invitation EXPIRED/WITHDRAWN) are being implemented
  directly in the main session concurrently with this plan, not gated on it.
- No production data exists yet, so migrations in this plan can be written as clean forward
  migrations rather than data-preserving backfills.
- The scheduler benchmark (`test_benchmark.py`) is the primary performance regression gate for
  FR-01/FR-06 — no additional profiling infra is assumed to exist or needs to be built.

---

## Resolved Clarifications

- Group/Project progression-ownership swap: confirmed out of scope for this plan (see P3 story
  and Out of Scope above) — it stays a documented, un-scheduled future item, not something this
  plan works toward or commits a date to. Do not open any phase touching `groups.status`'s role
  as the progression state machine.
- FR-05 enum rename: confirmed DB-level — rename the real Postgres enum values via migration, not
  an API-response remap. All string-matching call sites (routes, scheduler, tests) must be
  updated in the same phase as the migration.
