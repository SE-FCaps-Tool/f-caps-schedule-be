# Phase 3: Durable Draft Assignments and Activation Materialization

**Covers:** FR-06 and the P2 generate-vs-activate lifecycle story.
**Depends on:** Phase 1 target statuses and Phase 2 room-free solver output.
**Risk:** high — this changes the persistence identity returned by draft APIs and moves all session
creation into an activation transaction.

## Target contract

- Generate persists one `schedule_versions(status = DRAFT)` row, normalized assignment/reviewer
  rows, score/diagnostics, and one `scheduler_jobs` row. It inserts **zero** `sessions` and
  `session_reviewers` rows and leaves the round in `SCHEDULING`.
- Draft detail, edit, compare, and delete operate on durable assignment rows. Existing route paths
  may be retained, but a draft item's ID is an assignment ID and must be exposed as
  `assignment_id` (with any temporary `id` compatibility alias documented).
- Activation atomically performs `DRAFT -> ACTIVE`, previous `ACTIVE -> DISCARDED`,
  `round SCHEDULING -> SCHEDULED`, and materializes `PLANNED` sessions with `room_id = NULL` and
  their reviewer rows exactly once.
- Assignments remain after activation as the immutable solver/version record. Generated versions
  acquire sessions only through activation; a post-publish controlled-change replacement is the
  explicit exception and creates a PUBLISHED/SCHEDULED operational clone, never a DRAFT session.
- Publish atomically performs `ACTIVE -> PUBLISHED`, `round SCHEDULED -> PUBLISHED`, and all
  `PLANNED -> SCHEDULED` session transitions before enqueueing notifications/outbox work.

## Current-state evidence

- `run_scheduler` currently inserts `schedule_versions`, `sessions`, `session_reviewers`, and
  `scheduler_jobs` in one transaction and then moves the round to `SCHEDULED`.
- `activate_schedule_version` currently has no materialization work; it updates status/timestamp and
  round only.
- `_session_rows` is the shared representation for version detail, compare, draft edit,
  validation, activation-adjacent operations, and controlled changes.
- `delete_draft_version` counts `sessions`, `session_reviewers`, jobs, and change records as
  blockers, so a generated version cannot normally be deleted even though a delete route exists.
- `scheduler_jobs.schedule_version_id` has a non-cascading FK and a unique constraint.
- Phase 2 guarantees solver outputs have no concrete room and that validator H3 permits NULL.

## Exact files and symbols

- New `apps/api/migrations/versions/0022_durable_schedule_assignments.py` (rebase revision IDs to
  the actual head).
- `apps/api/app/routes/schedule_operations.py`:
  `run_scheduler`, `_session_rows` (split/replace with assignment and materialized loaders),
  `_to_domain_sessions`, `_edited_rows`, `_owner_for_edit`, `schedule_version_detail`,
  `compare_schedule_versions`, `delete_draft_version`, `activate_schedule_version`,
  `edit_draft_session`, `controlled_change`, `replacement_suggestions`, `publish_schedule`.
- New `apps/api/app/services/resource_locks.py`: stable namespace/resource -> signed-int8 advisory
  key derivation plus sorted transaction-lock acquisition, shared later by Room and Council writes.
- `apps/api/app/response_models.py`: `SessionResponse`, `VersionDetailResponse`, `CompareResponse`,
  `ScheduleRunResponse`, `SessionEditResponse` extensions for `assignment_id` and draft shape.
- `apps/api/app/services/access.py` and non-manager version visibility: DRAFT visibility must not
  accidentally expose unactivated schedules; keep DRAFT manager/admin-only. Operational
  supervisor scope/recipient queries for Sessions must use assignment Project provenance.
- `apps/api/app/routes/results.py`, `apps/api/app/routes/operations.py`, and
  `apps/api/app/routes/manager_extensions.py`: every Project lookup derived from a materialized
  Session must join `schedule_assignments` on `(schedule_version_id, group_id)` rather than read the
  mutable `groups.project_id`. Group/master-data listings continue to show the current Group link.
- Tests: `test_phase05_api.py`, `test_phase06_api.py`, `test_phase08_hardening.py`,
  `test_schedule_operations.py`, plus new focused draft-persistence/concurrency integration tests.

## Migration design

Create normalized tables:

```text
schedule_assignments
  id BIGSERIAL PK
  schedule_version_id FK schedule_versions ON DELETE CASCADE
  group_id FK groups
  project_id FK projects
  timeslot_id FK timeslots
  start_at, end_at, generated time_range
  UNIQUE(schedule_version_id, group_id)
  CHECK(end_at > start_at)

schedule_assignment_reviewers
  assignment_id FK schedule_assignments ON DELETE CASCADE
  lecturer_id FK lecturers
  is_result_owner BOOLEAN
  snapshot_name
  PRIMARY KEY(assignment_id, lecturer_id)
```

Do not add `room_id` to either table. Do not duplicate `schedule_version_id` or time columns in the
reviewer table; those are obtained through the assignment FK.

Also:

- Add `uq_schedule_versions_active_per_round` as a partial unique index on `round_id WHERE
  status = 'ACTIVE'`.
- Replace `scheduler_jobs_schedule_version_id_fkey` with `ON DELETE CASCADE` so deleting a DRAFT
  version removes its job/diagnostics ownership consistently.
- Backfill assignment and assignment-reviewer rows from all existing sessions/session reviewers,
  not only DRAFT versions. This preserves the original solver record for already-active and
  published fixtures.
- Validate backfill counts per `(schedule_version_id, group_id)` and reviewer membership before
  switching application reads.
- Persist/backfill the solved `project_id`, not merely the current Group ID. Activation locks the
  involved Group rows and rejects `DRAFT_ASSIGNMENT_STALE` if any live `groups.project_id` no
  longer equals the assignment snapshot; the Manager must regenerate rather than materialize a
  Council against changed supervisor/COI/progression provenance.
- For legacy rows, the only recoverable source is `sessions.group_id -> groups.project_id` at
  migration time. Abort with the affected Session/Group IDs if that link is NULL; do not invent a
  Project. After backfill, `schedule_assignments.project_id` is the historical source of truth for
  all Session-derived Project, supervisor, COI, eligibility, result, and access queries. A later
  Group reassignment is allowed for future scheduling but cannot reinterpret old Sessions.
- After validation, preflight DRAFT sessions for operational dependents (`session_results`,
  `remediation_cases`, `reschedule_requests`, and `schedule_change_records`). Abort the migration
  with a diagnostic if any exist; otherwise delete `session_reviewers`/`sessions` belonging to
  DRAFT versions so activation cannot collide with `UNIQUE(schedule_version_id, group_id)`.

Downgrade is data-preserving for this phase: insert missing sessions from assignments (status
`PLANNED`, `room_id = NULL`), insert their reviewer rows, restore the scheduler-job FK without
cascade, drop the ACTIVE index, then drop the assignment tables. This intentionally restores the
old "sessions exist for drafts" representation. A downgrade must abort if duplicate/materialized
rows cannot be reconciled rather than silently dropping assignments.

## Transaction and concurrency behavior

Use one lock order everywhere: resolve the owning round, then in the write transaction lock the
`rounds` row, then the target `schedule_versions` row, then assignment/session rows in ID order.

- **Generate:** round lock serializes `version_no = max + 1`, prevents concurrent lifecycle
  movement, and holds through version + assignments + job + audit inserts. It does not update the
  round to `SCHEDULED`.
- **Draft edit:** lock round, version, and target assignment; re-read all assignments, validate the
  proposed time/reviewer set, then replace only the target assignment's reviewer rows. Reject if
  status changed from DRAFT or the prepared values changed.
- **Activation:** after locks, require DRAFT, validate all assignments, discard an existing ACTIVE,
  update target ACTIVE, bulk/materialize sessions and reviewers, set `activated_at`, and transition
  the round in one transaction. The partial index and `(schedule_version_id, group_id)` uniqueness
  are DB backstops. A retry cannot create duplicate sessions.
- **Reviewer conflict serialization:** before materialization, acquire one-argument
  `pg_advisory_xact_lock(bigint)` locks for all assignment Reviewer IDs using deterministic signed
  `int8` keys derived from `"reviewer:<id>"`, in Reviewer-ID order. Re-query overlapping Sessions
  across all ACTIVE/PUBLISHED versions and reject H2 conflicts. Phase 5 reuses this exact protocol
  when Council membership becomes canonical; it must not be deferred until then.
- Apply the same locks and global overlap re-query to the transitional post-publish
  `controlled_change` clone whenever time or reviewer membership can change. Draft edits are not
  live and do not occupy the global schedule, but activation revalidates them under these locks.
- **Publish:** lock round then ACTIVE version; verify materialization is complete, transition
  sessions/version/round, and enqueue notifications in the same transaction. Phase 4 adds the room
  completeness gate; until then this phase verifies time/council completeness only.
- **Delete:** only DRAFT is deletable. One version delete cascades assignments and its scheduler job;
  audit events remain append-only and are not FK-owned by the version.

## Implementation steps

1. Add the migration, backfill assertions, safe legacy-DRAFT cleanup, downgrade reconstruction,
   duplicate-ACTIVE preflight/index creation, and migration tests.
2. Add the shared signed-int8 resource-lock helper; its derivation must be deterministic across
   processes and Python versions, and hash collisions may only over-serialize, never skip a lock.
3. Introduce `_assignment_rows` and a version-aware detail serializer: DRAFT reads assignments;
   ACTIVE/PUBLISHED/DISCARDED reads materialized sessions for operational fields while retaining
   assignment provenance.
4. Change `run_scheduler` to persist assignments/reviewers only, return status `DRAFT`, retain the
   round in `SCHEDULING`, and keep partial-solution diagnostics in snapshot/job data.
5. Move all session and session-reviewer inserts into `activate_schedule_version`; set status
   explicitly to `PLANNED` and room explicitly to NULL. Lock/recheck the assignment Project
   snapshots and all Reviewer conflicts before inserting.
6. Refactor draft edit/compare to assignment tables. Compare group, project, timeslot, and reviewer set;
   room is not a solver-version difference.
7. Make every controlled-change replacement version copy assignment/project provenance; update
   only the target assignment fields represented by the change. Use the shared Reviewer lock and
   cross-live-schedule re-query before writing a live clone.
8. Make draft delete a real cascade operation and return a structured conflict for any non-DRAFT.
9. Make activation and publish use the standardized lock order and lifecycle transitions.
10. Update all Session-derived Project joins, visibility/response models, and integration tests that assumed sessions exist after
   generation.

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest tests/test_schedule_operations.py -q
uv run pytest -m "not integration" -q
```

PostgreSQL/integration:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/test_phase05_api.py tests/test_phase06_api.py tests/test_phase08_hardening.py -q
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

Add explicit concurrent tests for two activations, activation racing a draft edit, and two Rounds
attempting to activate overlapping assignments for the same Reviewer. Include a lock-key unit test
with a Reviewer ID above `2_147_483_647`. Add the equivalent cross-Round race for a
post-publish controlled change before Phase 5 changes reviewer persistence.

## Acceptance checklist

- [ ] Generate creates DRAFT assignments/reviewers/job and zero session/session-reviewer rows.
- [ ] Draft detail returns the scheduled count, diagnostics, timeslots, and reviewer sets from the
      normalized tables; draft edit and compare no longer query sessions.
- [ ] Deleting a DRAFT removes its assignments and job; deleting ACTIVE/PUBLISHED/DISCARDED fails.
- [ ] Activation creates one PLANNED session per assignment with NULL room and the exact reviewer
      set, changes statuses/round atomically, and is safe under concurrency/retry.
- [ ] Assignment `project_id` provenance is preserved and a changed Group->Project link blocks
      activation with `DRAFT_ASSIGNMENT_STALE`.
- [ ] After activation, every Session-derived Project/supervisor/COI/result/access query uses the
      retained assignment snapshot; later Group reassignment does not rewrite history.
- [ ] Concurrent cross-round activation cannot assign one Reviewer to overlapping live Sessions;
      signed-int8 advisory keys work for BIGSERIAL IDs above the int4 range.
- [ ] The transitional controlled-change clone uses the same Reviewer lock/re-query protocol and
      cannot race another Round into a global H2 violation.
- [ ] Publish changes version/round/session states atomically; a forced failure rolls all three back.
- [ ] Migration backfill and downgrade reconstruction preserve counts and reviewer membership.
- [ ] A migrated legacy DRAFT has assignments but zero sessions and activates without uniqueness
      conflicts; migration aborts rather than deleting a DRAFT with operational dependents.
- [ ] Unit and full integration suites pass.

## Explicit non-goals

- Room type configuration, room suggestions, or publish room-readiness (Phase 4).
- Replacing `session_reviewers` with Councils (Phase 5).
- Exposing DRAFT schedules to lecturers/students.
- Changing the external route family solely to match the reference document.
