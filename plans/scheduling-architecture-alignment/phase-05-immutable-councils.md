# Phase 5: Immutable Councils and Targeted Controlled Changes

**Covers:** FR-04 and the P2 immutable-Council story.
**Depends on:** Phase 3's draft/materialized boundary and Phase 4's global room-lock helpers.
**Risk:** high — `session_reviewers` currently drives authorization, visibility, workload,
continuity, result ownership, result writes, notifications, replacement suggestions, and DB overlap
checks. Every consumer must move in one release.

## Target contract

- `councils` is immutable metadata; `council_members` is an immutable reviewer/result-owner set.
- Every materialized session has a non-NULL `council_id`. Drafts continue to use
  `schedule_assignment_reviewers`; activation creates a Council for each materialized assignment.
- Updating Council membership or Result Owner never mutates members. It inserts a new Council and
  members, then repoints only the target session.
- `controlled_change` has three explicit branches:
  - reviewer/result-owner only: create one Council and repoint only the target source session; the
    published version and every sibling row remain untouched;
  - time/room only: retain the version-clone path, create a replacement `PUBLISHED` version whose
    sessions reuse their existing Council IDs, and mark the source version `DISCARDED` atomically;
  - mixed reviewer + time/room: retain the clone path, validate the complete proposed state, create
    exactly one new Council for the target cloned session, and let sibling clones reuse their
    existing Council IDs.
  Every branch requires a reason/audit/change record. Clone branches create SCHEDULED sessions,
  keep the round PUBLISHED, and never expose an intermediate DRAFT/ACTIVE operational version.
- Completed, absent, postponed, or cancelled sessions are immutable for reviewer/time changes;
  allowed operational-state policy is explicit and tested.

## Current-state evidence

- `session_reviewers` stores `session_id`, duplicate `schedule_version_id`, lecturer, assignment,
  Result Owner, snapshot name, duplicated start/end, and a per-version reviewer/time GiST exclusion.
- `_session_rows`, `_owner_for_edit`, generate/activate persistence, draft edit,
  `assign_result_owner`, `controlled_change`, and `replacement_suggestions` all read/write it.
- Additional consumers found by source audit:
  - `services/access.py`: visible sessions and affected recipients;
  - `routes/results.py`: reviewer/owner authorization and notification recipients;
  - `routes/operations.py`: dashboard and lecturer workload/schedule views;
  - `routes/manager_extensions.py`: semester metrics and session list reviewer aggregation;
  - `routes/master_data.py`: conflict-declaration mutation safeguards;
  - `routes/schedule_operations.py`: existing workload, continuity, detail, result owner, edits,
    replacement suggestions, activation, and controlled changes.
- The current `controlled_change` clones every session, reviewer row, result, and remediation case
  into a new version even for one reviewer replacement.
- The current DB reviewer exclusion is scoped to a version and therefore does not prevent an
  overlapping lecturer assignment in a different active round/version.

## Exact files and symbols

- New `apps/api/migrations/versions/0025_immutable_councils.py` (rebased after the existing
  `0024_session_makeup` migration).
- New `apps/api/app/services/councils.py`:
  `lock_reviewer_ids`, `create_council`,
  `load_council_members`, `find_reviewer_conflicts`, `validate_council_change`.
- `apps/api/app/services/resource_locks.py`: reuse the Phase 3 signed-int8 helper and reviewer
  namespace; Council migration must not change lock identity for existing activation code.
- `apps/api/app/routes/schedule_operations.py`:
  `_round_input` workload/continuity queries, materialized row loader, `_owner_for_edit`,
  `activate_schedule_version`, `assign_result_owner`, `controlled_change`,
  `replacement_suggestions`; remove all session-reviewer insert/update/delete SQL.
- `apps/api/app/services/access.py`: `visible_session_ids`,
  `affected_schedule_recipients` and lecturer-session scope queries.
- `apps/api/app/routes/results.py`: `_session_context`, `_can_write`, result/remediation recipients.
- `apps/api/app/routes/operations.py`: lecturer dashboard/workload/session joins.
- `apps/api/app/routes/manager_extensions.py`: reviewer aggregation and workload metrics.
- `apps/api/app/routes/master_data.py`: conflict-declaration dependency checks.
- `apps/api/app/response_models.py`: expose `council_id` and Council member details; change
  `ControlledChangeResponse` to an explicit branch-aware contract: `change_kind`, current
  `schedule_version_id`, nullable `replacement_version_id`, `session_id`, nullable
  `before_council_id`/`after_council_id`, and `status`. Keep deprecated aliases optional only when
  they remain semantically truthful; never report the source version as a newly created version.
- Tests: `test_phase05_api.py`, `test_phase06_api.py`, `test_phase07_api.py`,
  `test_policy.py`, `test_result_workflow.py`, `test_phase08_hardening.py`, plus new Council
  migration/immutability/controlled-change integration cases.

## Migration design

Create:

```text
councils
  id BIGSERIAL PK
  round_id FK rounds ON DELETE RESTRICT
  supersedes_council_id NULL FK councils ON DELETE RESTRICT
  created_by NULL FK accounts
  reason NULL TEXT
  created_at TIMESTAMPTZ
  sealed_at NULL TIMESTAMPTZ

council_members
  council_id FK councils ON DELETE RESTRICT
  lecturer_id FK lecturers
  assignment assignment_role DEFAULT REVIEWER
  is_result_owner BOOLEAN
  snapshot_name VARCHAR(160)
  PRIMARY KEY(council_id, lecturer_id)

sessions.council_id FK councils ON DELETE RESTRICT
```

Upgrade/backfill order:

1. Create Council tables and add nullable `sessions.council_id`.
2. Create one Council per existing session and copy its `session_reviewers` rows to members,
   preserving assignment, owner flag, and snapshot name.
3. Validate: every session has one Council; member counts and owner counts equal the source; each
   Council round matches the session's ScheduleVersion round.
4. Set `sessions.council_id NOT NULL`.
5. Seal every backfilled Council, then add DB triggers with a two-step construction protocol:
   member INSERT is allowed only while `sealed_at IS NULL`; the only allowed Council UPDATE is the
   one-time NULL -> timestamp seal; member UPDATE/DELETE and every mutation after sealing fail.
   A constraint trigger on session insert/`council_id` update rejects attachment to an unsealed
   Council or to a Council whose `round_id` differs from the Session's ScheduleVersion Round.
   Repointing a session to a newly built-and-sealed same-Round Council is the only change path.
6. Drop `session_reviewers` after all application consumers are switched in the same release.

Downgrade first drops immutability triggers, recreates `session_reviewers` including its generated
time range and per-version lecturer exclusion, and backfills it by joining sessions to Council
members and using session start/end/version. Then drop `sessions.council_id` and Council tables.
Unreferenced historical Councils created by replacements cannot be represented in the old schema
and are lost on downgrade; currently referenced membership is preserved exactly. The downgrade
must fail on any exclusion violation rather than silently discard a reviewer row.

Sealed Councils are intentionally undeletable, including through parent cleanup. RESTRICT/NO
ACTION FKs make this explicit instead of promising a cascade that immutability triggers would
reject. Tests and fixtures must use transaction rollback or reset the disposable database rather
than delete a Round containing sealed Council history. An unsealed construction failure rolls back
its whole transaction; no partial Council requires an application cleanup path.

## Transaction and concurrency behavior

- **Activation after this phase:** lock round/version as in Phase 3, acquire reviewer advisory locks
  for all assignment reviewer IDs in sorted order using the same deterministic signed-`int8`
  `"reviewer:<id>"` keys and one-argument PostgreSQL lock overload, validate cross-live-schedule overlaps, then
  create Councils/members and sessions in one transaction. It never writes `session_reviewers`.
- **Controlled change:** follow the mandatory global order: lock the owning Round first, then the
  published Version, then the target/all cloned Session rows in sorted ID order, then relevant
  room IDs (Phase 4 namespace), and finally the union of old/new Reviewer IDs (Council namespace),
  each resource set in sorted order. Re-read
  target/council and validate the complete proposed time/room/reviewer state against all sessions in
  `ACTIVE`/`PUBLISHED` versions across all rounds. Reviewer-only then inserts/repoints one Council.
  Clone branches allocate the next version under the round lock, clone sessions while reusing
  Council IDs, give only the mixed target a new Council, set the new version PUBLISHED, and discard
  the source in the same transaction.
- **Result Owner change:** `assign_result_owner` follows the same Council replacement protocol;
  member rows are never updated in place.
- Build recipient sets as the union of before/after affected accounts so removed reviewers are also
  notified. Insert schedule-change, audit, notification, and outbox records before commit.
- DB immutability triggers turn late member INSERT as well as UPDATE/DELETE into transaction
  failures. `create_council` inserts an unsealed row, inserts the complete member set, seals it, and
  only then attaches/repoints the session in the same transaction.
  Advisory locks plus conflict re-query replace the old insufficient per-version reviewer
  exclusion and cover cross-round/cross-version races.

## Implementation steps

1. Add migration/backfill/downgrade tests and direct SQL tests proving late member INSERT and all
   Council/member UPDATE/DELETE operations are rejected after sealing.
2. Implement Council creation/load/conflict helpers and stable reviewer lock namespace.
   Add a concurrency test that races controlled change with publish/room work and proves every
   path acquires Round -> Version -> Session -> room advisory -> Reviewer advisory locks.
3. Change Phase 3 activation materialization to create Council/member rows from draft assignment
   reviewers and set each new session's `council_id`.
4. Replace the materialized session loader's reviewer aggregation with Council joins.
5. Rewrite every consumer listed above; use one shared Council query shape where practical to
   avoid inconsistent owner/authorization semantics.
6. Refactor `assign_result_owner` to create/repoint a Council.
7. Split `controlled_change` into the three explicit branches. Remove cloning only for
   reviewer/result-owner-only changes; retain a coherent PUBLISHED-to-PUBLISHED clone transaction
   for topology-only and mixed changes.
   Reviewer-only returns `change_kind=COUNCIL_REPLACED`, the unchanged current
   `schedule_version_id`, `replacement_version_id=null`, and before/after Council IDs. Clone
   branches return `change_kind=VERSION_REPLACED` or `MIXED_REPLACEMENT` plus the real replacement
   version ID. Cover all three response shapes with compatibility tests.
8. In clone branches reuse sibling Council IDs and copy result/remediation data exactly as the
   existing workflow does; in a mixed branch create one target Council. Record before/after version
   and Council IDs in audit/change JSON.
9. Update replacement suggestions to be room-free and Council-backed, then run a final search for
   application `session_reviewers` references.

## Tests and commands

From `apps/api`:

```powershell
uv run ruff check app tests
uv run pytest tests/test_policy.py tests/test_result_workflow.py tests/test_schedule_operations.py -q
uv run pytest -m "not integration" -q
```

PostgreSQL/integration:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/test_phase05_api.py tests/test_phase06_api.py tests/test_phase07_api.py tests/test_phase08_hardening.py -q
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

Static consumer audit:

```powershell
rg -n "session_reviewers" app
```

This must return zero application hits after the migration; references in historical migration
files and the new downgrade are expected.

## Acceptance checklist

- [ ] Every session has a non-NULL Council with the exact migrated reviewer/owner membership.
- [ ] Attaching an unsealed Council fails; after sealing, member INSERT and all Council/member
      UPDATE/DELETE operations fail; application changes only build, seal, and repoint.
- [ ] Direct SQL cannot attach a sealed Council from another Round; parent deletion of sealed
      history is explicitly RESTRICTED rather than partially cascading.
- [ ] All access, result, workload, continuity, visibility, notification, and suggestion consumers
      use Councils; application search has zero `session_reviewers` hits.
- [ ] Reviewer-only controlled change inserts one Council and updates one session; sibling session
      rows/Council IDs and the source version are unchanged.
- [ ] Reviewer-only response has no fake replacement version; all three controlled-change branches
      return their documented discriminator and Council/version identities.
- [ ] Time/room-only creates a replacement PUBLISHED version while reusing all Council IDs; mixed
      change does the same but creates exactly one Council for the target clone.
- [ ] Removed and added reviewers are notified; before/after Council IDs are audited.
- [ ] Concurrent cross-round reviewer changes cannot both assign one lecturer to overlapping live
      sessions.
- [ ] Migration downgrade/upgrade and all unit/integration/benchmark gates pass.

## Explicit non-goals

- Reusing/deduplicating Councils by membership hash; one change may intentionally create a new
  historical Council even if its set matches an older one.
- Mutating completed/absent/postponed/cancelled session history.
- Redesigning the existing clone semantics for time/room-bearing controlled changes beyond making
  their lifecycle status and Council handling coherent.
- Moving progression state from Group to Project or changing result/remediation rules.
