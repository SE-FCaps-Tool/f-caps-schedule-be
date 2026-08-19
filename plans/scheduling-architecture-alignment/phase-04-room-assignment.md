# Phase 4: Round Room Types and Post-Activation Room Assignment

**Covers:** FR-02, FR-03, and both P1 Room Assignment stories.
**Depends on:** Phase 2 room-free solver and Phase 3 activation-created PLANNED sessions.
**Risk:** high — correctness depends on serializing conflicts across versions and rounds, which the
current per-version exclusion constraint cannot do alone.

## Target contract

- A round stores one or more allowed `room_type` values, never selected room IDs.
- Four endpoints are added:
  - `GET /api/v1/rounds/{round_id}/rooms/available?timeslot_id=&room_type=`;
  - `PUT /api/v1/sessions/{session_id}/room` with `{ "room_id": ... }`;
  - `POST /api/v1/rounds/{round_id}/rooms/suggest`;
  - `POST /api/v1/rounds/{round_id}/rooms/apply-suggestions` with an explicit list of
    `{session_id, room_id}` pairs returned by suggest.
- Initial assignment endpoints mutate only `PLANNED` sessions in the round's `ACTIVE` version.
  Post-publish room changes continue through the reason/audit-controlled change path; the PUT route
  must not become an audit bypass for `SCHEDULED` sessions.
- All four routes require `ADMIN` or `MANAGER`. Anonymous calls return 401 and
  Lecturer/Student calls return 403. The PUT route derives Round/version scope from its target
  Session; suggest/apply/list reject data outside the path Round's current ACTIVE version.
- Eligible rooms satisfy `rooms.active = TRUE` and `rooms.room_type IN round_room_types`.
- Active-state compatibility is resolved once at phase start: if the concurrent RoomStatus
  migration has landed, `rooms.status = 'ACTIVE'` is the sole domain predicate and the Boolean is
  only a deprecated compatibility field; otherwise this phase uses `rooms.active = TRUE` through
  one shared helper. No query may require both columns or invent divergent truth sources.
- A conflict means the same room has an overlapping time range in any session belonging to any
  `ACTIVE` or `PUBLISHED` ScheduleVersion, regardless of round or version.
- Publish readiness requires every ACTIVE-version session to have a still-active, allowed room and
  zero global room conflicts.

## Current-state evidence

- `round_rooms(round_id, room_id)` selects physical rooms; `RoundResources.room_ids` is required and
  `set_round_resources` validates/inserts those IDs.
- `0020_room_type.py` already defines `room_type` and adds `rooms.room_type`; rooms still represent
  active state with a Boolean `active`, not a `RoomStatus` enum.
- `spec.md` says the additive RoomStatus work may land concurrently. Re-check Alembic head and the
  actual `rooms` columns before writing migration/routes, then lock the shared active-room
  predicate described above for the whole phase.
- `sessions.room_id` is nullable, but its GiST exclusion is scoped by `schedule_version_id`.
  Therefore it catches two overlaps inside one version but allows the same room/time in another
  active version or another round.
- `manager_extensions.get_round_detail` derives `room_count` from `round_rooms`.
- Existing integration setup sends `room_ids` before generation and edits a draft session to
  confirm a room. Both flows conflict with post-activation assignment.

## Exact files and symbols

- New `apps/api/migrations/versions/0023_round_room_types.py` (rebase IDs to actual head).
- New `apps/api/app/routes/room_assignment.py`:
  `list_available_rooms`, `assign_session_room`, `suggest_rooms`,
  `apply_room_suggestions` and payload models.
- New `apps/api/app/services/room_assignment.py` (or equivalently scoped helper module):
  `lock_room_ids`, `allowed_room`,
  `find_room_conflict`, `build_room_suggestions`, `validate_assignment_batch`.
- `apps/api/app/services/resource_locks.py`: reuse Phase 3's stable signed-int8 key/lock helper;
  do not introduce a second lock-key algorithm.
- `apps/api/app/main.py`: include the new router.
- `apps/api/app/routes/master_data.py`: `RoundCreate`, `RoundResources`,
  `set_round_resources`, round readiness counts.
- `apps/api/app/routes/manager_extensions.py`: `RoundUpdate`, `get_round_detail`.
- `apps/api/app/routes/schedule_operations.py`: `publish_schedule` room readiness and any
  post-publish room branch in `controlled_change`.
- `apps/api/app/response_models.py`: round `room_types`, available-room, suggestion, assignment,
  and structured readiness fields.
- Seed/bootstrap fixture code if it creates round resources; populate allowed types, not room IDs.
- Tests: update `test_phase05_api.py`, `test_phase06_api.py`; add
  `tests/test_room_assignment_api.py` and global concurrency cases in
  `test_phase08_hardening.py` or a dedicated integration file.

## Migration design

Create:

```text
round_room_types
  round_id FK rounds ON DELETE CASCADE
  room_type room_type NOT NULL
  PRIMARY KEY(round_id, room_type)
```

Upgrade/backfill order:

1. Create the table.
2. Insert each distinct `(round_id, rooms.room_type)` represented by existing `round_rooms`.
3. Assert every round that previously had physical rooms has at least one type.
4. Drop `round_rooms` only after application queries and fixtures are ready in the same release.

If a concurrent RoomStatus migration is present, rebase on it and use its `status = ACTIVE`
contract. If it is absent, do not add the enum in this phase; keep all active checks behind the
shared helper so the later additive migration has one atomic switch point.

Downgrade recreates `round_rooms` and expands each allowed type to all rooms of that type, then
drops `round_room_types`. This is schema-reversible but cannot recover an old per-room whitelist;
the forward migration intentionally collapsed that information to types. Document and test this
capability-expanding downgrade.

No new DB room-overlap constraint is added. A partial exclusion cannot reference
`schedule_versions.status`, and a global exclusion on all sessions would let DISCARDED historical
sessions block legitimate rooms. Global live-schedule correctness is therefore enforced by the
transaction/advisory-lock protocol below, with the existing per-version exclusion retained as a
local backstop.

## Transaction and concurrency behavior

All room mutations use this protocol:

1. Lock the owning round, ACTIVE version, and target session rows in stable ID order.
2. Validate session/version state and requested rooms.
3. Derive a deterministic signed `int8` key from `"room:<room_id>"` and acquire the one-argument
   `pg_advisory_xact_lock(bigint)` overload for every requested room in sorted room-id order. The
   stable hash may cause harmless extra serialization on collision but must never truncate the
   BIGSERIAL ID to int4.
4. Re-read room active/type state and query conflicts by overlap against sessions joined to
   versions where status is `ACTIVE` or `PUBLISHED`, excluding the target session(s).
5. Validate conflicts within the submitted batch before any UPDATE.
6. Apply all updates and write audit rows in the same transaction.

The single-session route maps known failures to structured responses:

- `ROOM_NOT_FOUND` (404), `ROOM_INACTIVE` (422), `ROOM_TYPE_NOT_ALLOWED` (422),
  `ROOM_ASSIGNMENT_STATE_INVALID` (409), and `ROOM_CONFLICT` (409) with `room_id`, conflicting
  session/round/version IDs, and interval details.
- A residual GiST `IntegrityError` is caught and mapped to `ROOM_CONFLICT`; raw SQL/constraint text
  is never exposed.

Suggest is read-only and may become stale. Apply must rerun every validation under locks and return
`ROOM_SUGGESTION_STALE`/`ROOM_CONFLICT` atomically; it must never partially apply a batch. The
deterministic heuristic sorts sessions by `(start_at, id)` and chooses the least-used eligible room,
then room code/id as tie-breakers.

Repeated identical PUT assignment is a 200 idempotent no-op: it emits no second audit,
notification, or outbox record. Apply-suggestions reports changed/unchanged counts, skips identical
pairs without side effects, and is likewise safe to retry after a client timeout.

## Implementation steps

1. Add/backfill the migration and its downgrade test.
2. Replace `room_ids` with `room_types` in round create/update/resource contracts and round detail.
   Require at least one allowed type as round configuration, but never require a concrete room ID
   for solver input.
3. Implement shared eligibility, conflict query, advisory-lock, and batch-validation helpers.
   Centralize the stable namespace-to-signed-int8 key function and test IDs above the int4 range.
4. Implement available-room filtering; when a timeslot is provided, use its actual `[start,end)`
   overlap rather than equality on `timeslot_id`.
5. Implement single assignment, deterministic suggest, and validate-all/apply-all endpoints.
   Put `_require(user, "ADMIN", "MANAGER")` and path/object scope checks at every route boundary;
   add anonymous/Lecturer/Student negative tests before mutation tests.
6. Add publish readiness checks and make `publish_schedule` refuse missing/inactive/disallowed/
   conflicting rooms before any lifecycle update.
7. Update the integration flow to generate -> activate -> assign/apply suggestions -> publish.
8. Add cross-round and cross-version concurrent assignment tests with one winner and one structured
   409 response.

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest -m "not integration" -q
```

PostgreSQL/integration:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/test_room_assignment_api.py tests/test_phase05_api.py tests/test_phase08_hardening.py -q
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

Also rerun `uv run pytest tests/test_benchmark.py -q` to prove Room Assignment did not leak back
into the solver.

## Acceptance checklist

- [ ] Round APIs persist/expose allowed room types and no longer write `round_rooms`.
- [ ] Available rooms are active, allowed, and truly unoccupied for the requested interval.
- [ ] PUT assignment accepts only ACTIVE-version PLANNED sessions and returns structured failures.
- [ ] All four endpoints enforce ADMIN/MANAGER plus Round/Session scope; anonymous and
      Lecturer/Student requests cannot read suggestions or mutate rooms.
- [ ] Suggest is deterministic; apply validates all first and commits all-or-none.
- [ ] Retrying an identical PUT or apply batch is a no-op without duplicate side effects.
- [ ] Concurrent overlapping writes across two versions or two rounds cannot both succeed.
- [ ] Publish fails on any missing/inactive/disallowed/conflicting room and otherwise atomically
      transitions version/round/sessions.
- [ ] Migration downgrade/upgrade and all unit/integration/benchmark gates pass.

## Explicit non-goals

- Room capacity/equipment optimization or putting Room back into CP-SAT.
- Selecting individual physical rooms during round creation.
- Creating a new `RoomStatus` enum inside this phase. An already-landed enum is honored as the sole
  predicate; otherwise the existing Boolean is encapsulated for a later atomic migration.
- Council persistence or reviewer replacement (Phase 5).
