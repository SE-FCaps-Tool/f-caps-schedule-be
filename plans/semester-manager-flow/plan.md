# Plan: Hoàn thiện Semester API — Fast Track

**Spec:** `plans/semester-manager-flow/spec.md`
**Mode:** fast-track (reuse existing spec and routes; no FE code in this plan)
**Risk:** high-risk — schema migration, audit metadata, lifecycle concurrency, and public API changes.
**Academic year rule:** persist `academic_year` as `start_date.year-start_date.year+1` (for example, dates beginning in 2026 map to `2026-2027`). This matches the existing `SE-2026-2027` seed and avoids ambiguous date-range filtering.

## Approach

Keep the existing route URLs and response compatibility, but centralize semester
query/serialization and lifecycle locking. Additive response fields are returned
by list, detail, create, patch, and set-current. Use PostgreSQL
`pg_advisory_xact_lock` plus deterministic row locks for every operation that can
change the active semester. Counts come from separate grouped subqueries to avoid
join fan-out.

## Fast-track execution rule

Implement one backend slice in this order: migration → response/request models →
shared query/serializer → read endpoints → create/PATCH → lifecycle →
tests/OpenAPI → docs. Do not start FE implementation, project/group changes,
or dashboard work until this contract passes its verification gates. The
optional form `note` is persisted on `semesters` so the artifact's create/edit
form does not silently drop user input.

## Phases

1. **Migration and data contract** — `phase-01-migration-and-contract.md`
   - Add `academic_year`, `created_by`, `updated_by`, `updated_at` to `semesters`.
   - Backfill academic year from existing start dates and `updated_at` from `created_at`.
   - Add/verify semester and round indexes; keep actor columns nullable for imported legacy rows.
   - Add `AuditActorResponse`, count/audit fields to `SemesterResponse`, and request models for filters/set-current.

2. **Shared semester query and list/detail** — `phase-02-list-detail-filters.md`
   - Build one query helper using separate project/group/round aggregates and actor joins.
   - Extend `GET /api/v1/semesters` with `search`, `status`, and `academic_year`.
   - Add `GET /api/v1/semesters/{semester_id}` with typed `SEMESTER_NOT_FOUND`.
   - Validate status and `YYYY-YYYY`; combine filters with AND semantics.

3. **Create/PATCH and audit metadata** — `phase-03-create-update-audit.md`
   - Refactor create and PATCH to use the shared serializer/query.
   - Create defaults `ACTIVE`, sets creator/updater fields, and writes `SEMESTER_CREATED`.
   - PATCH uses a safe whitelist, normalizes code/name, validates duration, sets updater fields, and writes before/after `SEMESTER_UPDATED`.
   - Preserve duplicate-code and active-semester conflict responses.

4. **Close and set-current lifecycle** — `phase-04-lifecycle-concurrency.md`
   - Keep `POST /semesters/{id}/transition` for `ACTIVE → CLOSED`, update audit metadata, and write `SEMESTER_STATUS_CHANGED`.
   - Add `POST /semesters/{id}/set-current`.
   - Acquire one advisory lock for semester lifecycle, lock target/current rows in ID order, close old active before activating target, update metadata, and audit both rows.
   - Make already-active target idempotent and return the complete semester response.

5. **Tests and OpenAPI** — `phase-05-tests-and-verification.md`
   - Add API tests for counts, filters, detail, audit actors, validation, duplicate/active conflicts, close, set-current, idempotency, permissions, and concurrency.
   - Verify response models and query parameter schemas in OpenAPI.
   - Run migration on a disposable database and verify enum/status/unique-active invariants.

6. **Documentation and rollout** — `phase-06-docs-and-rollout.md`
   - Update Manager API, schema, FE flow, lifecycle, and seed documentation.
   - Document `academic_year` derivation, active conflict behavior, and set-current transaction semantics.
   - Verify `docker compose up --build` runs migration and both seed sources without `UPCOMING` rows.

## API Contract Summary

```text
GET  /api/v1/semesters?search=&status=ACTIVE|CLOSED&academic_year=YYYY-YYYY
GET  /api/v1/semesters/{semester_id}
POST /api/v1/semesters
PATCH /api/v1/semesters/{semester_id}
POST /api/v1/semesters/{semester_id}/transition   {target_status: CLOSED, reason}
POST /api/v1/semesters/{semester_id}/set-current
```

List/detail item fields:

```json
{
  "id": 1,
  "code": "SE-2026-2027",
  "name": "Software Engineering 2026–2027",
  "note": "Summer Capstone semester",
  "start_date": "2026-05-11",
  "end_date": "2026-08-23",
  "academic_year": "2026-2027",
  "status": "ACTIVE",
  "project_count": 74,
  "group_count": 74,
  "round_count": 5,
  "created_at": "2026-08-19T00:00:00Z",
  "created_by": {"id": 20, "email": "manager1@gmail.com", "display_name": "Manager"},
  "updated_at": "2026-08-19T00:00:00Z",
  "updated_by": {"id": 20, "email": "manager1@gmail.com", "display_name": "Manager"}
}
```

## Risks and Mitigations

- **Two active rows under concurrency:** advisory transaction lock plus partial unique index.
- **Count multiplication:** independent grouped subqueries/CTEs, not a three-way aggregate join.
- **Legacy actor data missing:** nullable actor IDs and `null` actor objects; do not fabricate ownership.
- **Existing clients:** preserve existing routes and transition response `{id,status}`; new fields are additive.
- **Active create conflict:** return typed `409 ACTIVE_SEMESTER_EXISTS`; do not silently close another semester during create.
- **Form data loss:** persist optional `note`; never accept it and drop it from the response or audit snapshot.

## Exact endpoint contract

```http
GET  /api/v1/semesters?search=&status=ACTIVE|CLOSED&academic_year=YYYY-YYYY
GET  /api/v1/semesters/{semester_id}
POST /api/v1/semesters
PATCH /api/v1/semesters/{semester_id}
POST /api/v1/semesters/{semester_id}/transition
POST /api/v1/semesters/{semester_id}/set-current
```

Create/PATCH request:

```json
{
  "code": "SU26",
  "name": "Summer 2026",
  "note": "Capstone semester",
  "start_date": "2026-05-04",
  "end_date": "2026-08-23"
}
```

Successful item responses contain `id`, `code`, `name`, `note`, dates,
`academic_year`, `status`, the three counts, `created_at`, `created_by`,
`updated_at`, and `updated_by`. Typed errors are:
`SEMESTER_NOT_FOUND`, `SEMESTER_DURATION_INVALID`, `SEMESTER_DATE_INVALID`,
`DATA_DUPLICATE`, `ACTIVE_SEMESTER_EXISTS`, and `SEMESTER_STATUS_INVALID`.

## Definition of done

The API is complete only when all six endpoints exist, migration runs from the
current head, the response shape is visible in OpenAPI, all P1 acceptance tests
pass, and concurrent lifecycle requests leave exactly one `ACTIVE` row. FE is a
follow-up consumer of this stable contract.

## Red-Team Decisions

- Academic year is persisted as `start_year-start_year+1`; this makes a semester
  beginning in 2026 filter as `2026-2027` and avoids deriving a different label
  from an end date.
- `created_by` and `updated_by` are serialized as `{id,email,display_name}`;
  legacy/imported rows return `null` when no reliable actor exists.
- Create never rotates the current semester implicitly. A second `ACTIVE`
  create returns `409 ACTIVE_SEMESTER_EXISTS`; switching is explicit through
  `set-current`.
- Set-current serializes lifecycle changes with a transaction advisory lock and
  deterministic row locks; closing the old active row precedes activating the
  target so the partial unique index is never violated.

## Verification Gates

- `python -m compileall -q apps/api/app`
- `docker compose config --quiet`
- migration + query checks on disposable PostgreSQL
- `pytest -m "not integration" -q` and targeted semester API tests
- OpenAPI inspection for all new fields, filters, and set-current request/response

## Session Notes

Implementation completed on 2026-08-19:

- Alembic head is `0018_semester_audit_backfill`; legacy `UPCOMING` values were
  migrated to `ACTIVE`/`CLOSED` and the one-active partial unique index remains
  enforced.
- List/detail/create/PATCH/transition/set-current routes now expose the planned
  contract, including counts, filters, note, academic year, audit actors and
  timestamps.
- `docker compose exec -T api pytest -q` passes (100 tests), and OpenAPI exposes
  all six routes plus the complete request/response schemas.
- Local database smoke checks confirmed exactly one `ACTIVE` semester after
  switching and idempotent set-current calls.

The remaining rollout action is operational only: commit and push these changes
when the repository owner explicitly requests it. FE implementation is outside
this backend plan.
