# Phase 6: Postpone Make-up Session

**Covers:** spec PHẦN XIV §73 (`Postpone` / `Make-up`), a P2 controlled-change story that was never
scoped into any FR in `spec.md` and was therefore absent from Phases 1–5.
**Depends on:** Phase 1 (lifecycle vocabulary — `POSTPONED` session status), Phase 4 (room
eligibility/global-conflict helpers this phase reuses for the optional room on the new Session),
and Phase 5 (immutable Councils — landed concurrently; the new Session's reviewer set is sealed as
a fresh Council via `app.services.councils.create_council`, not `session_reviewers`, which Phase 5
dropped).
**Risk:** normal — one additive column/index, one new route, no rewrite of existing behavior.
Postpone itself (`POST /sessions/{id}/postpone`) is unchanged.

## Target contract

- `docs/capstone-fe-be-implementation-spec.md` §73: postponing a Session only flips
  `SCHEDULED -> POSTPONED`; it never rewrites the original Session into a new time. A separate
  action creates a **new** Session carrying `makeupOfSessionId = original.id`.
- `POST /api/v1/sessions/{session_id}/makeup`:
  - `ADMIN`/`MANAGER` only; 401 unauthenticated, 403 Lecturer/Student.
  - Target Session must be `POSTPONED` and must not already have a make-up (one make-up per
    postponed Session; a make-up that itself needs postponing is postponed and given its own
    make-up, chaining `makeup_of_session_id` off the make-up, not the original).
  - Request: `timeslot_id` (required), `room_id` (optional — mirrors Phase 4's post-activation
    model, where a room can be attached later via controlled change instead of at creation),
    `reviewer_ids` (optional; defaults to the original Session's reviewer set for continuity),
    `reason` (required, audited).
  - The new Session is inserted directly into the original's `schedule_version_id` — no new
    `ScheduleVersion` is cloned, matching §73's "postpone doesn't turn the old session into a new
    schedule; it creates a new make-up Session." Only the target Round's version may be
    `PUBLISHED`; `ACTIVE`/`DRAFT` postponed sessions cannot exist under current lifecycle rules, so
    this doubles as a scope guard.
  - New Session starts at `SCHEDULED`, `makeup_of_session_id = original.id`.
  - Hard constraints (H1 supervisor, H8 COI, H11 continuity, H12 quota, group/timeslot conflicts)
    are validated the same way `replacement_suggestions`/`controlled_change` already do: build a
    candidate `ScheduledSession` for the round's `_round_input` context and run it through the
    shared `validate_schedule`. Cross-round/cross-version reviewer overlap is checked with
    `app.services.councils.validate_council_change` (Phase 5's helper — locks reviewers and re-runs
    the cross-version `council_members` overlap query), because `validate_schedule` only sees one
    Round's session set.
  - If `room_id` is supplied, it goes through the Phase 4 helpers (`allowed_room`,
    `find_room_conflict`, `lock_room_ids`) under an advisory lock — the same global-conflict
    protocol as the four Room Assignment routes, not a second implementation.
  - Response includes the new `session_id`, `makeup_of_session_id`, `status`, `start_at`, `end_at`.
  - Emits `audit_events` (`SESSION_MAKEUP_CREATED`) and the same
    `affected_schedule_recipients` notification/outbox fan-out `postpone_session` already uses.

## Current-state evidence

- `apps/api/app/routes/schedule_operations.py:1034` `postpone_session` only updates
  `sessions.status`; nothing in the codebase ever inserts a Session referencing another Session.
- `sessions` (migration `0002_domain_model.py:227`) has no self-referential column; a make-up
  Session cannot be modeled without a new nullable FK.
- No route, test, or response model mentions `makeup` anywhere in `apps/api/`
  (`rg -n "makeup" apps/api` returns nothing before this phase).
- `apps/api/app/routes/schedule_operations.py:999` `replacement_suggestions` is the closest
  existing analog for building an H-constraint-checked candidate Session outside the solver.
- `apps/api/app/services/councils.py` (`create_council`, `load_council_members`,
  `validate_council_change`) is the Phase 5 pattern for sealing a fresh reviewer set and re-checking
  cross-version overlap; this phase reuses it verbatim instead of writing a second raw query.
- `apps/api/app/services/room_assignment.py` (`allowed_room`, `find_room_conflict`,
  `lock_room_ids`) is the Phase 4 global room-conflict protocol this phase must reuse verbatim,
  not reimplement.

## Exact files and symbols

- `apps/api/migrations/versions/0024_session_makeup.py` (revision `0024_session_makeup`,
  `down_revision = "0023_round_room_types"`). Phase 5's migration landed second and rebased itself
  to `0025_immutable_councils` with `down_revision = "0024_session_makeup"`, so the numbering
  collision noted in `plan.md` is already resolved on disk — no further rebase needed.
- `apps/api/app/routes/schedule_operations.py`: new `MakeupSessionPayload` payload model and
  `create_makeup_session` route, placed next to `postpone_session`; reuses `_round_input`,
  `_session_rows`, `_to_domain_sessions`, `validate_schedule`, `affected_schedule_recipients`,
  `require_change_reason`, `_actor_id`, `_json`, plus Phase 5's `create_council`,
  `load_council_members`, `validate_council_change`, `CouncilError`.
- `apps/api/app/services/room_assignment.py`: no changes — imported, not modified.
- `apps/api/app/response_models.py`: extend `ActionResponse` with `makeup_of_session_id`.
- Tests: new `apps/api/tests/test_session_makeup.py` (auth/role/reason negative tests, no DB
  fixture, mirroring `test_phase01_lifecycle.py`'s group-absent tests) plus an
  `@pytest.mark.integration` happy-path test exercising postpone -> makeup -> audit/notification
  rows against Docker PostgreSQL.

## Migration design

Add:

```sql
ALTER TABLE sessions ADD COLUMN makeup_of_session_id BIGINT REFERENCES sessions(id);
CREATE UNIQUE INDEX ux_sessions_makeup_of_session_id
    ON sessions (makeup_of_session_id) WHERE makeup_of_session_id IS NOT NULL;
```

No backfill: the column is new and every existing row is NULL. The partial unique index enforces
"one make-up per postponed Session" without constraining Sessions that are not make-ups.

Downgrade drops the index then the column — fully reversible, no data loss (a make-up Session's
own row is untouched; only the link is dropped, matching the "additive Round Assignment migration"
precedent Phase 4 already established for schema evolution that doesn't rewrite existing data).

## Transaction and concurrency behavior

Single-transaction protocol, matching the Phase 4 lock order (Round -> ScheduleVersion ->
Sessions -> Rooms):

1. `SELECT ... FOR UPDATE` the original Session; confirm `status = 'POSTPONED'` and that no other
   Session already has `makeup_of_session_id` pointing at it (`SELECT 1 FROM sessions WHERE
   makeup_of_session_id = :id FOR UPDATE` — belt-and-suspenders with the unique index, which is the
   actual race-safe backstop).
2. Lock the owning Round and ScheduleVersion (`FOR UPDATE`) in that order, matching every other
   mutating route in this file.
3. Resolve `timeslot_id -> (start_at, end_at, day, part)` from the Round's timeslots; 404
   `TIMESLOT_NOT_FOUND` if it does not belong to the Round.
4. Resolve `reviewer_ids` (payload or original Session's reviewer set) and build one candidate
   `ScheduledSession`; run `validate_schedule` against the Round's existing materialized Sessions
   plus the candidate. Structured `422 HARD_CONSTRAINT_VIOLATION` on failure, same shape
   `edit_draft_session`/`controlled_change` already return.
5. `validate_council_change(db, session_id, round_id, reviewer_ids, start_at, end_at,
   exclude_session_ids=[session_id])` — Phase 5's helper locks reviewers and re-runs the
   cross-version `council_members` overlap query; it raises `CouncilError`, caught at the route
   level and mapped to `409 REVIEWER_OVERLAP` (or whatever code/status the error carries).
6. If `room_id` is present: `lock_room_ids(db, [room_id])`, `allowed_room` (else `404
   ROOM_NOT_FOUND` / `422 ROOM_INACTIVE` / `422 ROOM_TYPE_NOT_ALLOWED`), `find_room_conflict` (else
   `409 ROOM_CONFLICT`) — identical error vocabulary to Phase 4's room routes.
7. Seal a fresh Council via `create_council` (defaults to the original Session's Council members
   when `reviewer_ids` is omitted from the request), insert the Session (`council_id`,
   `makeup_of_session_id` set, `status = 'SCHEDULED'`), insert the `audit_events` row, fan out
   notifications/outbox via `affected_schedule_recipients`, all inside the one transaction from
   step 2 onward.

A residual GiST `IntegrityError` (room/time overlap the pre-check missed under a race) is caught
and mapped to `409 ROOM_CONFLICT`, same as `assign_session_room`/`apply_room_suggestions`.

## Implementation steps

1. Add the migration and its upgrade/downgrade test (assert the partial unique index actually
   rejects a second make-up for the same original Session).
2. Add `MakeupSessionPayload` and the route skeleton with `_require(user, "ADMIN", "MANAGER")` and
   `require_change_reason`; add anonymous/Lecturer/Student negative tests before any mutation
   logic (matching the group-absent test order in `test_phase01_lifecycle.py`).
3. Implement the original-Session lookup/lock and the `POSTPONED` + no-existing-make-up guard;
   structured 404/409 errors.
4. Implement timeslot resolution, candidate construction, and the `validate_schedule` call.
5. Implement the cross-version reviewer-overlap check via `app.services.councils.validate_council_change`,
   reusing Phase 5's helper rather than writing a second query.
6. Implement the optional room branch by calling into `app.services.room_assignment` — no new
   room-conflict logic in this file.
7. Seal a Council via `create_council`, insert the Session/audit/notification rows; return the
   structured response.
8. Add the integration happy-path test: postpone a seeded Session, create its make-up, assert
   `makeup_of_session_id`, the new Session's `SCHEDULED` status, and audit/notification rows.
9. Run the literal audit (`rg -n "makeup" apps/api`) to confirm every new symbol lines up with the
   spec's `makeupOfSessionId` field name in responses (snake_case at the DB/route boundary is
   consistent with this codebase's existing convention; no camelCase leak into JSON).

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest tests/test_session_makeup.py -q
uv run pytest -m "not integration" -q
```

Against Docker PostgreSQL:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/test_session_makeup.py -q
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

## Acceptance checklist

- [ ] `POST /api/v1/sessions/{id}/makeup` returns 401 unauthenticated, 403 for Lecturer/Student,
      422 for a missing/blank reason.
- [ ] The target Session must be `POSTPONED`; a `SCHEDULED`/`COMPLETED`/`CANCELLED`/`GROUP_ABSENT`
      target or a Session that already has a make-up returns a structured 404/409.
- [ ] The new Session persists with `makeup_of_session_id = original.id` and `status = 'SCHEDULED'`
      in the original's `schedule_version_id`; no new `ScheduleVersion` is created.
- [ ] Hard-constraint violations (H1/H8/H11/H12, group/timeslot double-booking) return
      `422 HARD_CONSTRAINT_VIOLATION` with the violation list, not a partial write.
- [ ] Cross-round/cross-version reviewer overlap returns `409 REVIEWER_OVERLAP`.
- [ ] An optional `room_id` is validated through the exact Phase 4 helpers and error vocabulary
      (`ROOM_NOT_FOUND`/`ROOM_INACTIVE`/`ROOM_TYPE_NOT_ALLOWED`/`ROOM_CONFLICT`).
- [ ] A second make-up attempt against the same original Session is rejected structurally (not just
      by the DB unique index leaking a raw `IntegrityError`).
- [ ] Audit and notification/outbox rows are written in the same transaction as the Session insert.
- [ ] Migration upgrade/downgrade/upgrade round-trip passes; unit and integration suites pass.

## Explicit non-goals

- Changing `postpone_session` itself.
- Letting the make-up action retroactively change the original Session's status away from
  `POSTPONED`.
- A dedicated "chain of make-ups" listing endpoint — the FK is enough for spec parity; a listing
  view is a separate, unscoped FR if the product later needs one.
- Council supersession semantics: the make-up's Council is a brand-new sealed Council (like
  activation's), not a `supersedes_council_id` repoint of the original Session's Council — the two
  Sessions are distinct rows with independent Council history.
