# API contract alignment — fast-fix plan

## Scope challenge

- Exists? The target route inventory and most business operations already exist, but the
  implementation still leaks legacy DTOs, integer IDs, raw responses, and FastAPI error shapes.
- Minimum? Add a compatibility boundary for the target API, then fix the highest-value FE flows in
  bounded slices. Preserve the existing route handlers and delegate to their domain/write paths.
- Complexity? Multi-file and high-risk because public request/response contracts, authorization,
  and additive schema changes are involved; suitable for a fast, implementation-oriented pass.

Mode: fast
Risk: high-risk — public API compatibility, identifier translation, error handling, and result/schedule state transitions can affect existing consumers
Test: --tdd recommended for each phase; this plan defines contract tests before implementation
Tasks: default

## Goal

Quickly make the backend consumable by the frontend described in
`docs/capstone-fe-be-implementation-spec.md`, especially camelCase payloads, target envelopes,
string-shaped external IDs, query parameters, and the documented response fields. Keep legacy
routes and database integer primary keys working during the migration.

## Non-goals

- Do not rewrite CP-SAT hard constraints H1–H13 or the immutable-council state machine.
- Do not change frontend code, deployment, authentication strategy, or database primary-key types.
- Do not delete/rename legacy routes or rewrite historical enum/status values.
- Do not add broad CRUD/import/remediation features that are only checklist proposals unless they
  are required to unblock a documented target route.

## Audit baseline

- Target route aliases are present for the main group/project, round, schedule, room/publish,
  result/remediation, and portal families, but several handlers still reuse legacy Pydantic models.
- `POST /semesters/{semesterId}/rounds` now accepts the nested camelCase wizard payload, but its
  neighboring invitation/availability and response contracts still diverge.
- The spec requires `{data}` or `{data,meta}`, `{error:{code,message,details}}`, camelCase fields,
  prefixed string IDs, and the documented query filters. Existing routes commonly return raw
  objects/lists, `detail`, snake_case, and integer IDs.
- The solver has H1–H13 and S1–S3 coverage; S4–S7 and readiness/diagnostic exposure need an
  explicit implementation and regression gate.

## Compatibility policy

1. Target routes accept documented camelCase and, during migration, legacy snake_case aliases.
2. Target responses always use the spec envelope and target field names; legacy routes retain their
   current response shape until deprecation is complete.
3. External IDs use a single codec (`grp_`, `prj_`, `rnd_`, `lec_`, `stu_`, `sv_`, `ses_`, `room_`,
   `ts_`) that accepts both prefixed strings and existing numeric IDs. Database IDs remain integer.
4. Error translation happens at the target boundary and maps validation/domain/permission/not-found
   failures to stable spec error codes. Legacy `detail` responses remain available on legacy routes.
5. Migrations, if needed, are additive and reversible. No phase may require dropping a table,
   changing a primary key, or resetting the development database.

## Dependency graph

`phase-01-shared-contract-boundary → phase-02-groups-projects → phase-03-round-registration`
`phase-01 → phase-04-schedules-sessions → phase-05-rooms-publish-results`
`phase-04 → phase-06-solver-soft-constraints`
`phase-02..06 → phase-07-contract-regression-and-rollout`

Phases 02 and 03 can proceed in parallel after Phase 1. Phase 5 consumes the schedule/session
fields from Phase 4. Phase 6 must not alter hard-constraint semantics while improving scoring.

## Phase index

| Phase | Focus | Depends on | Fast-fix outcome |
| --- | --- | --- | --- |
| 01 | Shared target DTOs, IDs, envelopes, and errors | — | One reusable compatibility boundary |
| 02 | Groups/projects requests, responses, filters | 01 | Manager list/create/detail flows match FE |
| 03 | Round, invitation, availability, preferences | 01 | Registration wizard and lecturer self-service match FE |
| 04 | Schedule generation, versions, sessions | 01, 02, 03 | Calendar/version APIs expose documented fields and paths |
| 05 | Rooms, publish, post-publish, results/remediation | 04 | Operational and result flows match FE |
| 06 | S4–S7 scoring and readiness | 04 | Solver diagnostics and soft objective match spec |
| 07 | Contract tests, OpenAPI, rollout/rollback | 01–06 | Evidence-backed target contract release |

## Cross-cutting acceptance gates

Every phase must include:

- request tests for camelCase plus the documented validation failures;
- success responses validated against target Pydantic models and envelope shape;
- role, scope, archived-semester, not-found, and conflict tests for mutations;
- OpenAPI assertions for method/path, path parameter names, query parameters, request schema, and
  response schema;
- a legacy-route regression test proving the compatibility change did not alter the old contract;
- `git diff --check`, Ruff, and the relevant unit/integration tests before handoff.

## Rollback

Disable target aliases or the new DTO adapter via a route/config flag and restore the previous API
image. Keep additive migrations applied; target reads can fall back to legacy columns/mappings.
Rollback must not delete generated schedule versions, councils, results, or historical statuses.

## Verification commands

```powershell
Push-Location apps/api
uv run ruff check app tests
uv run pytest -m "not integration" -q
uv run pytest tests/test_target_contract.py tests/test_phase03_api.py -q
Pop-Location

docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q

Push-Location apps/api
uv run pytest tests/test_benchmark.py -q
Pop-Location
```

## Progress

- [x] Phase 1: Shared target contract boundary (fast-unverified)
- [x] Phase 2: Groups and projects (fast-unverified)
- [x] Phase 3: Rounds, invitations, availability, preferences (fast-unverified)
- [x] Phase 4: Schedules, versions, sessions (fast-unverified)
- [x] Phase 5: Rooms, publish, post-publish, results/remediation (fast-unverified)
- [x] Phase 6: Solver soft constraints S4–S7/readiness (fast-unverified)
- [x] Phase 7: Contract test matrix and rollout evidence (fast-unverified)

## Handoff

Implement in order with TDD:

`$ck-cook --fast --tdd plans/api-contract-alignment-fast-fix/plan.md`

## Session Notes
<!-- Updated by cook automatically — do not edit manually -->

**Last active:** 2026-08-19
**Phase in progress:** complete
**Status:** Fast implementation completed; all planned adapters are unverified by the fast lane.

### Decisions made this session
- Keep legacy route payloads unchanged where route precedence would otherwise break existing consumers.
- Use additive target DTO adapters and external-ID translation; database primary keys remain integers.

### Next immediate action
Run the full hard review/integration/benchmark lane before production rollout.
