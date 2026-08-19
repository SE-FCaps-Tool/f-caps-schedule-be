# API contract alignment plan

## Scope challenge

- Exists? The backend already implements most business primitives, but many routes still use legacy paths, response shapes, status values, and error payloads.
- Minimum? Add the target contract as a compatibility layer first, then migrate behavior by bounded domain slices. Do not rewrite the scheduler or remove legacy routes in the first release.
- Complexity? Hard-sized implementation, executed as staged phases.

Mode: fast (the repository and audit evidence are already available; no code is changed by this planning pass)
Risk: high-risk — public API contracts, authorization scopes, historical status data, and database migrations are affected
Test: --tdd recommended for every phase
Tasks: default

## Spec quality check

Verdict: WARN.

`docs/capstone-fe-be-implementation-spec.md` provides a measurable endpoint inventory and screen mapping, but it still contains implementation proposals and unresolved compatibility choices (identifier format, exact envelope migration, and whether legacy aliases remain during frontend rollout). This plan assumes a staged, dual-route migration and records those choices as Phase 0 decisions.

Before freezing a target operation, resolve conflicts in this order: `plans/capstone-scheduler/spec.md`, `docs/project-reference/`, Alembic migrations, implemented API contracts, then the FE implementation spec. Any intentional deviation from that order must be recorded in the Phase 1 compatibility decision log.

## Goal

Bring the runtime API into alignment with the implementation spec and `docs/manager-fe-migration-phases.md`, while preserving existing scheduler invariants and allowing the separated frontend to migrate incrementally.

## Non-goals

- No frontend repository changes.
- No cloud/deployment redesign.
- No replacement of the CP-SAT scheduling algorithm.
- No destructive database reset or blanket rewrite of historical records.
- No removal of legacy endpoints until the frontend cutover and deprecation window are complete.

## Baseline findings

- The spec contains 53 unique method/path declarations after placeholder normalization; only 13 exact shapes currently exist.
- The largest cross-cutting mismatch is the response/error contract: target `{data}` / `{data,meta}` and `{error:{code,message,details}}` versus legacy raw objects/arrays and FastAPI `detail` errors.
- Missing target route families include nested group/project management, round registration/readiness, schedule versions, room/publish actions, lecturer/leader portals, and remediation/progression views.
- Domain values also diverge: group, project, and invitation status enums in code/migrations do not equal the four-state/target values in the migration docs.

## Route backlog mapped to phases

| Phase | Target route families to implement or alias |
| --- | --- |
| 03 | `/semesters/{id}/groups`, `/groups/{id}/members`, `/groups/{id}/actions/change-leader`, `/groups/{id}/members/{member_id}/actions/leave`, `/groups/{id}/project`, `/semesters/{id}/projects`, `/projects/{id}/progression`, `/projects/{id}/results` |
| 04 | `/semesters/{id}/rounds`, `/rounds/{id}/eligible-projects`, `/rounds/{id}/registration-summary`, `/rounds/{id}/scheduling-readiness`, `/rounds/{id}/actions/open-registration`, `/rounds/{id}/actions/close-registration`, `/rounds/{id}/availability/me`, `/rounds/{id}/groups/{group_id}/preferences`, `/rounds/{id}/invitations/me/respond`, `/rounds/{id}/invitations/{invitation_id}/remind` |
| 05 | `/rounds/{id}/schedules`, `/rounds/{id}/schedules/generate`, `/rounds/{id}/schedules/{schedule_id}`, `/rounds/{id}/schedules/{schedule_id}/actions/set-active`, `/rounds/{id}/schedules/{schedule_id}/actions/discard`, `/rounds/{id}/sessions` |
| 06 | `/rooms`, `/rooms/{id}` PATCH, `/rounds/{id}/publish-readiness`, `/rounds/{id}/actions/publish`, plus the target room suggest/apply request shapes |
| 07 | `/sessions/{id}/actions/change-room`, `/sessions/{id}/actions/replace-reviewer`, `/sessions/{id}/actions/postpone` |
| 08 | `/semesters/{id}/remediations`, `/remediations/{id}/verify`, `/remediations/{id}/actions/overdue-fail`, project progression/results and target result payloads |
| 09 | `/lecturer/me/invitations`, `/lecturer/me/availability`, `/lecturer/me/sessions`, `/lecturer/me/supervised-projects`, `/lecturer/me/remediations`, `/leader/me/dashboard`, `/leader/me/sessions` |

## Dependency graph

`01-contract-baseline → 02-domain-dto-alignment → (03-groups-projects ∥ 04-round-registration) → 05-schedules-drafts → 06-rooms-publish → 07-post-publish-operations → 08-results-remediation → 09-portals → 10-rollout-deprecation`

Parallel work is safe only after Phase 2 publishes shared DTOs, error mapping, authorization helpers, and migration conventions. Phase 8 follows Phase 7 because remediation actions depend on the post-publish session state machine.

## Cross-cutting acceptance gates

Every phase must add or update:

1. OpenAPI route and schema assertions for the target paths.
2. TDD contract tests for success, validation, forbidden, not-found, and conflict cases.
3. The standard response envelope, error envelope, camelCase JSON, string identifiers, and pagination metadata where the spec requires them.
4. Role/scope checks and archived-semester guards, with audit events for mutations.
5. Migration upgrade tests against a disposable database; no test may depend on deleting the shared development volume.
6. Regression coverage for H1–H13, immutable councils, durable drafts, activation, publication, and result/remediation invariants.

## Phase index

| Phase | Focus | Depends on |
| --- | --- | --- |
| 01 | Contract baseline and compatibility policy | — |
| 02 | Status enums, DTOs, envelopes, errors | 01 |
| 03 | Group and project target routes | 02 |
| 04 | Round lifecycle, invitations, availability, preferences | 02 |
| 05 | Schedule versions, draft sessions, activation | 03, 04 |
| 06 | Rooms, publish readiness, publishing | 05 |
| 07 | Post-publish controlled operations | 06 |
| 08 | Results, progression, remediation | 03, 06, 07 |
| 09 | Lecturer and leader portal APIs | 03, 04, 05, 08 |
| 10 | Frontend cutover, deprecation, and cleanup | 01–09 |

## Rollback strategy

Each phase ships behind route-level compatibility switches where practical. Database migrations are additive or use reversible data translations. A phase is releasable only when legacy aliases still pass their regression suite, so a failed target route can be disabled without reverting scheduler data.

## Progress

- [x] Phase 1: Contract baseline and compatibility policy
- [x] Phase 2: Status enums, DTOs, envelopes, errors
- [x] Phase 3: Group and project target routes
- [x] Phase 4: Round lifecycle, invitations, availability, preferences
- [x] Phase 5: Schedule versions, draft sessions, activation
- [x] Phase 6: Rooms, publish readiness, publishing
- [x] Phase 7: Post-publish controlled operations
- [x] Phase 8: Results, progression, remediation
- [x] Phase 9: Lecturer and leader portal APIs
- [x] Phase 10: Frontend cutover, deprecation, and cleanup (backend handoff; external FE sign-off pending)

## Session Notes
<!-- Updated by cook automatically — do not edit manually -->

**Last active:** 2026-08-20 00:35
**Phase in progress:** phase-10-rollout-deprecation
**Status:** Legacy deprecation headers, route usage telemetry, and frontend handoff documentation implemented; external FE cutover evidence remains pending.

### Decisions made this session

- Kept the 53 spec operations separate from the checklist-only semester remediation extension.
- Registry records request schema, success schema/status, roles, pagination, and alias metadata for each operation.
- Historical enum values remain intact; target statuses are exposed through pure mappings and migration views.
- Target group/project handlers delegate existing validation/write paths and return the shared `{data,meta}` envelope.
- Round target handlers preserve legacy transition/availability functions and add nested target aliases with scoped self-service checks.
- Schedule target handlers delegate the existing solver/version state machine; no solver or immutable-council behavior was rewritten.
- Room/publish and controlled-operation aliases delegate existing conflict, readiness, council, and audit services.
- Portal handlers expose only role-scoped session/project/remediation fields; they do not expose solver internals.
- Legacy aliases emit deprecation/sunset/successor headers and usage counters; alias removal is intentionally deferred until frontend telemetry/sign-off.

### Next immediate action

Next: run the full non-integration suite and review the accumulated route aliases before committing; then coordinate the frontend OpenAPI handoff.

## Recommended handoff

Implement with TDD, one phase per change set:

`$ck-cook --fast --tdd plans/api-contract-alignment/plan.md`

Use `--hard` for any phase that changes historical enum values or performs a production data migration.
