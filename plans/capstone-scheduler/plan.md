# Implementation Plan: Capstone Defense Scheduler — Scheduler-only V1

**Spec:** [spec.md](./spec.md)  
**Mode:** `--hard`  
**Risk:** high-risk — authentication/authorization, immutable audit data, relational state transitions, overlap constraints and a CP-SAT scheduling engine all affect user-visible correctness.  
**Testing:** `--tdd`  
**Status:** In progress — Phases 05–07 implemented and verified; Phase 08 pilot/release evidence remains open
**Date:** 2026-08-18

## Outcome

Deliver a production-shaped Scheduler-only web application that manages semester data through admin forms and seed fixtures, collects availability, generates and explains schedule versions, validates manual changes, publishes schedules, records final outcomes and preserves an auditable history. Full Assessment Platform scoring remains out of scope.

## Scope boundary

In scope: FR-01–FR-82, excluding the explicitly out-of-scope Excel import/export, including five round types, H1–H12, H11 waiver, result-owner rules, round/group state transitions, schedule versions, publish/change workflow, in-app notifications, dashboards and F-Caps UI.

Out of scope: detailed assessment criteria, ballots, evidence, Chair/Secretary workflow, FAP integration, OGA/SWP490, native mobile, multi-major, microservices and H13.

## Research synthesis

### Primary approach — modular Python monolith

- React + TypeScript + Vite for the web client.
- FastAPI + Pydantic + SQLAlchemy + Alembic for the API/domain application.
- PostgreSQL as the source of truth.
- A separate scheduler/notification worker process from the same backend codebase, using PostgreSQL jobs/outbox tables; no microservice boundary in V1.
- OR-Tools CP-SAT for schedule generation. The model uses candidate feasibility filtering plus CP-SAT assignment variables, with the same pure validator reused by auto-scheduling and manual edits.

This is the recommended approach because the solver, scheduling logic, form validation and seed tooling can share one Python domain package, while the worker keeps CPU-heavy scheduling away from the HTTP process. FastAPI's own guidance distinguishes small background tasks from heavier work that benefits from a separate worker/queue process. OR-Tools documents employee/job-shop scheduling as appropriate CP-SAT problem shapes. PostgreSQL range/exclusion constraints provide a database-level defense for non-overlapping assignments.

### Alternative considered — TypeScript API plus Python solver service

- React + TypeScript frontend.
- NestJS API with a Redis/BullMQ queue.
- Python OR-Tools solver service communicating over a job protocol.

This gives a strong TypeScript API boundary and easier future horizontal scaling, but introduces a second service contract, deployment topology, queue operations and failure modes before the capstone has demonstrated the core scheduling workflow. It remains a future extraction path: the worker job payload and result schema in this plan must be serializable and versioned so the solver can be moved later.

### Decision

Use the primary approach for V1. Do not add Redis, Kafka, or a separate solver HTTP service unless the performance benchmark proves the PostgreSQL-backed worker inadequate. Revisit that decision only after the target fixture and concurrency tests exist.

## Architecture rules

1. The API, worker and tests share the same domain package for enums, state transitions, constraint codes, snapshot schemas and result contracts.
2. All writes pass through application services; route handlers never mutate ORM entities directly.
3. Every permission check has both system-role and contextual-assignment coverage server-side.
4. Every schedule create/edit/activate/publish path calls the same `ConstraintValidator`.
5. Round transitions and group result transitions are explicit transition tables, not scattered conditionals.
6. A ScheduleVersion is immutable after activation/publish except through a new controlled-change record; old versions and completed session reviewer lists remain queryable.
7. Audit records are append-only to the application role and contain actor, action, entity, before/after, reason and timestamp where required.
8. Time comparisons use half-open `[start, end)` intervals in `Asia/Ho_Chi_Minh` at the domain boundary and normalized UTC timestamps in persistence.
9. H13 and old `max_groups_per_timeslot`, `max_minutes_per_part` and `max_minutes_per_day` fields are not implemented as V1 business rules. H12 is session-count based.
10. The official source precedence is `spec.md` → PRD Scheduler-only → ERD/schema. Existing documents are design inputs to reconcile, not authoritative implementation contracts.

## Cross-cutting definitions

### Authentication and authorization

V1 uses active-account login with Argon2id password hashes and secure httpOnly session cookies. CSRF protection is required for cookie-authenticated mutation requests. A policy layer exposes `can(actor, action, resource)` and supports `ADMIN`, `MANAGER`, `LECTURER`, `STUDENT` plus contextual Supervisor, Reviewer, Result Owner, Remediation Verifier and Project Leader assignments. SSO is explicitly deferred.

### Core persistence model

The implementation must replace the stale schema contract with migrations for at least: accounts/roles, semesters, majors, lecturers, rooms, projects, groups, membership history, rounds/round days/timeslots, invitations, lecturer/group availability, conflicts, schedule versions, sessions, session reviewers, result records, remediation, H11 waivers, change requests, notifications, outbox jobs and audit events.

Session scheduling stores a real interval derived from its timeslot. Room and lecturer assignment tables use `tstzrange`/`EXCLUDE USING GIST` where applicable, while application validation produces stable H-rule codes and friendly explanations. Database constraints are a backstop; the domain validator remains the single user-facing explanation source.

### Scheduler model

1. Build an immutable input snapshot for the selected round.
2. Generate feasible reviewer/session candidates after applying static H1, H8, H10, H11 and availability checks.
3. Create CP-SAT variables for group-timeslot-room placement and reviewer assignment.
4. Enforce H2/H3/H4/H5/H6/H7/H9/H12 in the model; preserve H11 waiver provenance in the snapshot.
5. Optimize in lexicographic order: maximize scheduled groups, then soft score S1–S8 using configurable weights.
6. Persist a new ScheduleVersion with seed, parameters, solver status, objective breakdown, snapshot reference and unscheduled reason codes.
7. Run the pure validator over the materialized sessions before activation or publish.

Partial results are first-class: an unscheduled group is never silently dropped and must receive a reason code such as `NO_REVIEWER_AVAILABILITY`, `H1_CONFLICT`, `H8_CONFLICT`, `H11_CONTINUITY`, `H12_QUOTA`, `NO_ROOM`, or `NO_TIMESLOT`.

## Phase map

| Phase | Outcome | Stories | Requirements |
|---|---|---|---|
| 01 | Repository, architecture spike and runnable test harness | foundation for all P1 | NFR, FR-01–FR-82 traceability |
| 02 | Correct schema, migrations, state machines, policies and audit | Admin, academic data, round setup, operations | FR-01–FR-17, FR-21–FR-25, FR-60–FR-68, FR-75 |
| 03 | Master data and round registration | Academic data, round setup, lecturer/group availability | FR-18–FR-30 |
| 04 | Constraint validator and scheduler engine | Scheduler run, operations | FR-31–FR-52, NFR correctness/performance |
| 05 | Schedule workspace, manual change and publish workflow | Manual changes, scoped schedule, operations | FR-53–FR-60, FR-69–FR-71, FR-74–FR-75 |
| 06 | Results, remediation and group transitions | Result entry, scoped result visibility | FR-61–FR-68, FR-74–FR-75 |
| 07 | UX, reports, notifications and accessibility | Scoped schedule, notifications | FR-69–FR-82 |
| 08 | End-to-end hardening, benchmark, security and release readiness | all P1/P2 | all success criteria and NFRs |

## Phase checklist

- [x] Phase 01: Foundation, architecture spike and test harness
- [x] Phase 02: Domain model, migrations, state machines, policy and audit
- [x] Phase 03: Master data and round registration
- [x] Phase 04: Constraint validator and CP-SAT scheduler
- [x] Phase 05: Schedule workspace, manual change and publish workflow
- [x] Phase 06: Results, remediation and group transitions
- [x] Phase 07: UX, reports and notifications
- [ ] Phase 08: Hardening, benchmark, security and release readiness

## Phase files

- [phase-01-foundation.md](./phase-01-foundation.md)
- [phase-02-domain-and-data.md](./phase-02-domain-and-data.md)
- [phase-03-master-data-and-registration.md](./phase-03-master-data-and-registration.md)
- [phase-04-scheduler-engine.md](./phase-04-scheduler-engine.md)
- [phase-05-schedule-operations.md](./phase-05-schedule-operations.md)
- [phase-06-results-and-transitions.md](./phase-06-results-and-transitions.md)
- [phase-07-ux-reports-and-notifications.md](./phase-07-ux-reports-and-notifications.md)
- [phase-08-hardening-and-release.md](./phase-08-hardening-and-release.md)

## Critical dependency order

```text
Foundation
    ↓
Domain/data/state/policy ─────┐
    ↓                         │
Master data + registration    │
    ↓                         │
Constraint validator ────────┘
    ↓
Scheduler engine
    ↓
Schedule operations → Results/transitions
    ↓                         ↓
Reports/notifications/UX ←───┘
    ↓
Benchmark/security/release
```

Do not implement the scheduler against the current `schema.sql` before Phase 02 reconciliation. Do not build UI flows that bypass the API transition/policy services.

## Risks and mitigations

| Risk | Impact | Mitigation / exit condition |
|---|---|---|
| Candidate explosion in reviewer assignment | runtime or memory failure | benchmark candidate counts; pre-filter static conflicts; use CP-SAT time limit and partial result; consider staged assignment only with evidence |
| H-rule drift between solver and manual edit | invalid published schedule | one validator, rule-code contract tests, property tests for overlap and reviewer eligibility |
| Stale ERD/schema conflicts with spec | wrong data model | migration design review before code; remove H13/minute quota fields; trace every table to FR |
| Result transition ambiguity | wrong group eligibility | transition table plus exhaustive round/outcome tests; no implicit transitions from postponed/cancelled sessions |
| Audit tampering or missing reason | compliance/history failure | append-only DB policy/trigger, mutation tests, audit integration tests |
| Invalid multi-record mutation | corrupted semester data | validate-before-write service and transaction rollback tests |
| Missing representative data | weak demo and benchmark evidence | versioned seed fixture created in Phase 01/03 and loaded in CI |
| Heavy solver blocks API | poor UX/timeouts | job table + worker process, polling endpoint, retryable job state and benchmark |
| UI reproduces F-Caps too literally | brand/IP or usability issue | use the project-local F-Caps-derived tokens and patterns, no logo/assets; accessibility review |
| No existing app scaffold | implementation uncertainty | architecture spike and vertical slice in Phase 01 before broad feature work |

## Inline red-team adjudication

- **ACCEPTED:** P2 email and iCal are required user-visible behaviors, so Phase 07 must implement both behind the shared event/calendar contracts; they are not silently dropped because they are lower priority.
- **ACCEPTED:** Excel import/export is removed from V1. Initial data is entered through Manager/Admin forms or versioned seed fixtures; no external template contract is needed.
- **NOTED:** The workspace has no existing application scaffold, so Phase 01 owns the repository bootstrap and local Docker setup.
- **REJECTED:** Extracting the solver into a separate HTTP microservice in V1. The requirement does not need that operational complexity; the worker boundary keeps a future extraction possible after benchmark evidence.

## Definition of done

A phase is complete only when its tests pass, its traceability entries are updated, its API/UI states include loading/empty/error/disabled/success validation, and no phase introduces a direct write path that bypasses policy, transition, validator or audit services.

The V1 release is complete when the Phase 08 checklist demonstrates every measurable success criterion in `spec.md`, including the 74-group benchmark, zero H1–H12 violations, atomic multi-record mutations, result-transition coverage, post-publish auditability and mobile availability usability.

## Confirmed decisions

1. Stack: React/Vite + TypeScript, FastAPI/Python, PostgreSQL, same-codebase worker and OR-Tools CP-SAT.
2. Authentication: local active-account login with secure session cookies; SSO is out of scope.
3. Data entry: Excel import/export is removed from V1; Admin/Manager forms and versioned seed fixtures are the supported sources.
4. Deployment: Docker local only for V1; no cloud deployment pipeline is planned.

## Handoff

Implementation starts with:

```text
$ck-cook --hard --tdd plans/capstone-scheduler/plan.md
```

## Session Notes
<!-- Updated by cook automatically — do not edit manually -->

**Last active:** 2026-08-18  
**Phase in progress:** phase-08-hardening-and-release  
**Status:** Phase 05 schedule operations, Phase 06 results/remediation, Phase 07 operations reports/notifications/iCal and the F-Caps web shell are implemented. Phase 08 automated hardening evidence is passing; human pilot and cross-browser release gates remain open. Auth uses Argon2id sessions, CSRF double-submit protection, security headers and server-side resource scope.  

**Verification:** Docker migration is at `0011_auth_rate_limit (head)`; full Docker API/integration suite passes, including concurrent activation, controlled post-publish change, auth/CSRF/rate-limit, result privacy, scoped invitation/project/remediation endpoints, dashboard/report surfaces and account lifecycle. Local Ruff and compileall pass. Frontend has 8 Vitest tests across 2 files; lint and the TypeScript/Vite production build pass; authenticated screens now load round, availability, schedule, result, report and notification data from the API. Target fixture is 74 groups/26 lecturers/40 timeslots/4 rooms and passes the under-60-second benchmark with the shared validator; repeated local evidence is recorded in `docs/benchmark-2026-08-18.md`. Docker health and web/API smoke checks return HTTP 200, and a PostgreSQL backup/restore rehearsal was verified in a temporary database. Local in-app browser smoke covers Manager and Lecturer flows, including 390px availability; detailed evidence is in `docs/phase-08-evidence-2026-08-18.md`.  

### Decisions made this session

- Excel import/export is removed from V1; data entry uses Admin/Manager forms and versioned seed fixtures.
- Local Docker is the only V1 deployment target.
- Phase 02 keeps system roles to ADMIN, MANAGER, LECTURER and STUDENT; Result Owner, Reviewer, Supervisor and Remediation Verifier remain contextual assignments.
- H12 is represented by session-count fields (`h12_sessions_per_part`, `h12_sessions_per_day`, optional semester quota); H13 and legacy H12 minute quota fields are absent.
- Review sessions cannot have a Result Owner; enabled Result Owner mode requires exactly one owner on Defense sessions.
- Excel/import-batch entities are intentionally absent; remediation, waiver, reschedule, notification, outbox and audit entities are persisted in PostgreSQL.
- Phase 03 seed fixture is versioned as `seed-v1`, deterministic, atomic and idempotent: 26 lecturers, 74 groups and 296 students across 4 rooms.
- Lecturer no-selection fallback is busy-all; group no-selection fallback is available-all. Manager-entered availability records `source = MANAGER`.
- Round types are `REVIEW_1`, `REVIEW_2`, `DEFENSE_1_1`, `DEFENSE_1_2` and `DEFENSE_2`; Review requires 2 Reviewers and Defense requires 3.
- H11 waiver is valid only for the current group/round with a `MANAGER` actor and non-empty reason; invalid waiver metadata remains a hard H11 violation.
- Scheduler jobs use queued/running/completed/partial/failed/cancelled transitions; retry reuses the same job and cannot bind a second ScheduleVersion.
- The CP-SAT objective is lexicographic: maximize scheduled groups first, then apply configured soft weights; materialized output is rechecked by the shared validator.

### Next immediate action

Run the remaining pilot gates in [docs/release-checklist.md](../../docs/release-checklist.md): real Lecturer availability completion/time, cross-browser/accessibility checks and final Admin/Manager acceptance. Repeated benchmark p50/p95 and backup/restore evidence are attached in `docs/benchmark-2026-08-18.md`; automated/browser evidence is in `docs/phase-08-evidence-2026-08-18.md`.
