# Phase 1: Status Vocabulary and Lifecycle Foundation

**Covers:** FR-05 and the P2 status/lifecycle story, including a settable `GROUP_ABSENT` state.
**Depends on:** nothing.
**Risk:** high — both PostgreSQL enums are rebuilt and scheduling status literals occur in route,
domain, query, response-shaping, in-memory versioning, and integration-test code.

## Target contract

- `schedule_version_status`: `DRAFT`, `ACTIVE`, `PUBLISHED`, `DISCARDED`.
- `session_status`: `PLANNED`, `SCHEDULED`, `COMPLETED`, `POSTPONED`, `GROUP_ABSENT`,
  `CANCELLED`.
- Generate creates `DRAFT`; activate is the only `DRAFT -> ACTIVE` action; publish requires
  `ACTIVE`; replacing an active/published version uses `DISCARDED`.
- Session `ONGOING` has **no target equivalent**. `ONGOING` belongs to `round_status`; existing
  values are mapped by owning-version lifecycle: DRAFT/ACTIVE Sessions become `PLANNED`, while
  PUBLISHED/DISCARDED history becomes `SCHEDULED`. `SCHEDULED` remains the published operational
  state until a terminal/action transition occurs.
- Publish changes every version session from `PLANNED -> SCHEDULED` in its publish transaction.
- Until Phase 5 specializes reviewer-only changes, a post-publish controlled-change clone is
  created directly as `PUBLISHED` with `SCHEDULED` sessions and changes the source version to
  `DISCARDED` in the same transaction; it never creates a DRAFT containing operational sessions.
- `POST /api/v1/sessions/{session_id}/group-absent` changes only `SCHEDULED -> GROUP_ABSENT`,
  requires `ADMIN` or `MANAGER`, a non-empty reason, and a Session in a PUBLISHED version; it
  appends audit/outbox/notification records and rejects unauthenticated/forbidden actors, repeats,
  out-of-scope Sessions, or non-operational states with structured errors.

## Current-state evidence

- `0002_domain_model.py` defines `schedule_version_status` as
  `DRAFT/VALID/PUBLISHED/SUPERSEDED` and `session_status` as
  `SCHEDULED/ONGOING/COMPLETED/POSTPONED/CANCELLED`; `sessions.status` defaults to `SCHEDULED`.
- `run_scheduler` inserts a version as `VALID`, immediately inserts sessions, and moves the round
  to `SCHEDULED`.
- `activate_schedule_version` accepts `VALID` but only sets `activated_at`; therefore one DB value
  currently represents both unactivated and active versions.
- `_version_ui` compensates with `activated_at` and an API-only `ui_status = ACTIVE` alias.
- `publish_schedule`, `ensure_publishable`, dashboard/export queries, and the concurrent activation
  test compare the legacy literals directly.
- `postpone_session` accepts session `ONGOING`, but no route ever sets a session to `ONGOING`.
  The round transition model independently owns `RoundStatus.ONGOING`.

## Exact files and symbols

- New `apps/api/migrations/versions/0021_schedule_lifecycle_vocab.py` (revision/down-revision must
  be rebased to the actual Alembic head at implementation time).
- `apps/api/app/routes/schedule_operations.py`:
  `run_scheduler`, `_version_ui`, `delete_draft_version`, `activate_schedule_version`,
  `edit_draft_session`, `controlled_change`, `postpone_session`, `publish_schedule`, and the new
  `mark_group_absent`; also the workload/continuity queries near `_round_input`.
- `apps/api/app/domain/schedule_operations.py`: `ensure_publishable`.
- `apps/api/app/routes/operations.py`: active/published schedule selection.
- `apps/api/app/routes/manager_extensions.py`: semester metrics, session listing, export, and report
  queries that currently use `VALID`.
- `apps/api/app/scheduler/versions.py`: `VersionStore.activate`; remove `SUPERSEDED` even though this
  is presently an in-memory-only implementation.
- `apps/api/app/routes/results.py`: `record_result` must reject result entry for
  `GROUP_ABSENT`, `POSTPONED`, or `CANCELLED` sessions.
- `apps/api/app/response_models.py`: add a typed response only if `ActionResponse` cannot express
  the group-absent result; extend existing models rather than replacing them.
- Tests: `test_schedule_operations.py`, `test_versioning.py`, `test_phase05_api.py`,
  `test_phase08_hardening.py`, plus any file found by the final literal audit.

## Migration design

Do not use `ALTER TYPE ... ADD VALUE`: it cannot remove `ONGOING` and cannot be cleanly downgraded.
Rebuild both enum types inside one Alembic transaction.

Upgrade order:

1. Drop the two column defaults and cast both status columns to `TEXT`.
2. Classify legacy schedule versions **before** creating the target enum:
   - `VALID` + `activated_at IS NULL` -> `DRAFT`;
   - `VALID` + `activated_at IS NOT NULL` -> `ACTIVE`;
   - `SUPERSEDED` -> `DISCARDED`;
   - existing `DRAFT` and `PUBLISHED` remain unchanged.
   Before accepting this mapping, preflight each Round for more than one `VALID` row with a
   non-NULL `activated_at`. Abort with a diagnostic listing the Round/version IDs rather than
   silently choosing an ACTIVE winner; repair the data before rerunning the migration.
3. Map session states while both columns are TEXT. First preflight that every Session under a
   version now classified as `DRAFT` or `ACTIVE` is only legacy `SCHEDULED`/`ONGOING`; abort on a
   terminal state because silently erasing it would corrupt history. Then map all Sessions under
   both `DRAFT` and `ACTIVE` versions to `PLANNED`, including both legacy `VALID` cases. For
   PUBLISHED/DISCARDED history, map only session `ONGOING -> SCHEDULED`.
4. Drop and recreate `schedule_version_status` and `session_status` with exactly the target labels,
   cast the columns back, then set defaults to `DRAFT` and `PLANNED` respectively.
5. Assert with SQL that no NULL or unmapped text values remain before the final casts.

Downgrade reverses the type rebuild:

- `ACTIVE -> VALID`, `DISCARDED -> SUPERSEDED`; `DRAFT` and `PUBLISHED` remain available in the
  legacy type.
- `PLANNED -> SCHEDULED` and `GROUP_ABSENT -> CANCELLED`; the other values remain unchanged, and
  the legacy `ONGOING` label is recreated unused.
- Restore defaults `schedule_versions.status = DRAFT` and `sessions.status = SCHEDULED`.

The session downgrade is schema-reversible but semantically lossy because the old vocabulary has
no `GROUP_ABSENT` or `PLANNED`. The migration must document this explicitly and test the mapping.

## Transaction and concurrency behavior

- Alembic performs the enum conversion atomically; a failed cast rolls back the entire migration.
- `activate_schedule_version` locks the target version and then the owning round. Inside the same
  transaction it changes other `ACTIVE` rows for that round to `DISCARDED`, changes the target
  `DRAFT -> ACTIVE`, sets `activated_at`, and changes the round only when it is `SCHEDULING`.
- `run_scheduler` must stop performing its current `rounds -> SCHEDULED` update in this phase.
  Generate leaves the Round `SCHEDULING`; activation is already the sole owner of that transition
  before Phase 3 later moves Session materialization.
- Concurrent activation tests must prove one winner. Phase 3 adds the partial unique-index DB
  backstop when the durable-assignment migration lands; until then the round row lock is mandatory.
- `publish_schedule` locks version then round, verifies `ACTIVE`, updates version/round and
  `PLANNED` sessions together, then enqueues notifications before commit.
- `mark_group_absent` locks the session, updates with a status predicate (`status = SCHEDULED`),
  and writes audit/outbox rows in the same transaction. A racing result write must re-read status
  and fail rather than create a result for an absent group.

## Implementation steps

1. Add migration tests for all legacy values, especially the two `VALID` cases distinguished by
   `activated_at`, their resulting Session status (`PLANNED` in both cases), the terminal-state
   preflight abort, and the documented downgrade mappings.
2. Apply the enum rewrite and verify exact values through `pg_enum`.
3. Replace every scheduling use of `VALID`/`SUPERSEDED`; do not replace unrelated words such as
   `VERSION_NOT_VALID` unless contract naming is intentionally changed (error-code rename is out of
   scope).
4. Make generate insert `DRAFT` and leave the Round `SCHEDULING`; activation require and update
   `DRAFT -> ACTIVE` and own `SCHEDULING -> SCHEDULED`; draft edit require `DRAFT`; publish require
   `ACTIVE` and update sessions to `SCHEDULED`. Make the existing controlled-change clone a direct
   PUBLISHED replacement that discards its PUBLISHED source.
5. Remove `_version_ui`'s vocabulary alias; derive `is_active` from the real status (and retain
   `activated_at` only as history).
6. Update `VersionStore` and tests to use `DISCARDED`.
7. Add `mark_group_absent`, an explicit `_require(user, "ADMIN", "MANAGER")` boundary, PUBLISHED
   version/session scope validation, its reason/audit/notification behavior, and the result-entry
   guard. Test anonymous, Lecturer, and Student denial before the happy path.
8. Run literal searches and inspect every remaining hit in context.

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest tests/test_schedule_operations.py tests/test_versioning.py -q
uv run pytest -m "not integration" -q
```

Against Docker PostgreSQL:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/test_phase05_api.py tests/test_phase08_hardening.py -q
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

Literal audit:

```powershell
rg -n "VALID|SUPERSEDED|session.*ONGOING|ONGOING.*session" app tests
```

## Acceptance checklist

- [ ] Upgrade maps unactivated `VALID` to `DRAFT` and activated `VALID` to `ACTIVE`.
- [ ] Sessions owned by either migrated DRAFT or ACTIVE versions are PLANNED; a terminal Session
      in either lifecycle state aborts migration instead of being overwritten.
- [ ] Both rebuilt enums contain exactly the target values; downgrade and re-upgrade succeed.
- [ ] Generate returns/persists `DRAFT`; activate atomically returns/persists `ACTIVE`; publish
      returns/persists `PUBLISHED` and moves `PLANNED` sessions to `SCHEDULED`.
- [ ] Concurrent activation leaves at most one `ACTIVE` version for the round.
- [ ] No application/test scheduling comparison still uses `VALID`, `SUPERSEDED`, or session
      `ONGOING`; remaining error-code text is reviewed and intentional.
- [ ] `GROUP_ABSENT` is reachable only from `SCHEDULED`, is audited/notified, and blocks results.
- [ ] `GROUP_ABSENT` returns 401 without authentication and 403 for Lecturer/Student actors; only
      ADMIN/MANAGER can mutate a PUBLISHED in-scope Session.
- [ ] Unit and PostgreSQL integration suites pass.

## Explicit non-goals

- Moving session materialization out of generate (Phase 3).
- Removing room data from the solver (Phase 2).
- Renaming public route paths or legacy error codes solely for cosmetic alignment.
- Changing Round `ONGOING` or Group/Project progression semantics.
