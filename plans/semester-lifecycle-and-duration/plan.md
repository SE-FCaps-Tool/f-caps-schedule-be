# Plan: Semester lifecycle và thời lượng học kỳ

**Spec:** `plans/semester-lifecycle-and-duration/spec.md`
**Mode:** Auto → Hard (inline fallback; no delegated agents available)
**Risk:** high-risk — enum migration, existing production data, API contract and lifecycle authorization
**Status:** Complete

## Scope challenge

- Exists? → Partial: semester create/list already exist, but dates and lifecycle transition do not.
- Minimum implementation → Add date fields, duration settings/validation, `UPCOMING` enum/default, migration, transition endpoint and tests/docs.
- Complexity → Hard because existing `DRAFT` rows need a safe date backfill and enum migration must be transactional.

## Objective

Extend semester management without changing the existing base path:

```text
POST /api/v1/semesters
GET  /api/v1/semesters
POST /api/v1/semesters/{semester_id}/transition
```

Every newly created semester starts as `UPCOMING`. The only valid lifecycle transitions
are `UPCOMING → ACTIVE → CLOSED`; only one semester may be `ACTIVE`.

## Phases

1. **[x] Preflight and contract** — confirm existing semester date backfill and define request/response/error contract.
2. **[x] Configuration and database migration** — add duration settings, date columns and enum migration from `DRAFT` to `UPCOMING`.
3. **[x] API implementation** — update create/list and add guarded status transition.
4. **[x] Tests and documentation** — cover API, migration, authorization, constraints and OpenAPI/docs.
5. **[x] Verification and rollout** — run migration on current database, verify no data loss and health.

Detailed phase files:

- [phase-01-preflight-and-contract.md](phase-01-preflight-and-contract.md)
- [phase-02-config-and-migration.md](phase-02-config-and-migration.md)
- [phase-03-api-implementation.md](phase-03-api-implementation.md)
- [phase-04-tests-and-docs.md](phase-04-tests-and-docs.md)
- [phase-05-verification-and-rollout.md](phase-05-verification-and-rollout.md)

## Data/API decisions

- `SemesterCreate` receives `code`, `name`, `start_date`, `end_date`; it does not accept caller-selected status.
- Default status is persisted as `UPCOMING`.
- Duration is inclusive: `(end_date - start_date).days + 1`.
- Config defaults are 105 and 120 days, overridable by environment variables.
- Transition request uses `{target_status, reason}`; reason is required for auditability.
- Transition returns `{id, status}` and writes before/after status to audit.
- `GET /api/v1/semesters` and create response include `start_date`, `end_date`, `status` and `created_at`.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Existing semester has no dates | Phase 01 applies the approved deterministic backfill: `SE-2026-2027` → `2026-05-11` to `2026-08-23` (105 inclusive days), before enforcing `NOT NULL`. |
| PostgreSQL enum cannot remove `DRAFT` in place | Phase 02 uses a transactional replacement/rename strategy and maps all legacy rows to `UPCOMING`. |
| Two managers activate semesters concurrently | Keep partial unique active index and lock/check transition in one transaction. |
| FE sends old `status` field | Return validation error for caller-supplied status and update OpenAPI/docs in the same change. |
| Duration defaults differ by environment | Expose settings through `SEMESTER_MIN_DURATION_DAYS` and `SEMESTER_MAX_DURATION_DAYS`; test defaults and overrides. |

## Out of scope

- Excel import changes.
- Automatic date-based status changes.
- Round/schedule status side effects.
- Fixing the separate `{STUDENT}` role serialization issue in `GET /api/v1/accounts`; track separately.

## Verification gates

1. `alembic upgrade head` succeeds on a disposable database and current local schema.
2. Existing semester rows and all foreign-key references remain present.
3. Valid 105–120 day create succeeds; invalid/reversed periods fail with the stable error code.
4. Unauthorized roles receive `403` for create and transition.
5. Lifecycle transition and one-active constraint pass under concurrent transaction tests.
6. `GET /health`, OpenAPI JSON and `/docs` remain available after migration.

## Session Notes

- 2026-08-18: Implemented migration `0013_semester_lifecycle`; current `SE-2026-2027` row was backfilled to `2026-05-11`–`2026-08-23` (105 inclusive days) and status `UPCOMING`.
- 2026-08-18: Added configurable `SEMESTER_MIN_DURATION_DAYS`/`SEMESTER_MAX_DURATION_DAYS` (defaults 105/120), create/list date fields, and guarded lifecycle transition endpoint.
- 2026-08-18: Verification passed in Docker: `pytest -m 'not integration'` (102 passed), `pytest -m integration` (20 passed), focused phase tests (10 passed), DB constraints (2 passed), compileall, OpenAPI path check, and `git diff --check`.
- 2026-08-18: The separate `{STUDENT}` role serialization issue remains out of scope per spec.
