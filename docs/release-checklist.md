# Scheduler-only V1 release checklist

This checklist separates automated evidence from pilot evidence. A passing automated suite does not replace the real-user measurements required by the PRD.

Detailed run output and browser observations are recorded in [Phase 08 evidence](./phase-08-evidence-2026-08-18.md).

## Automated release gates

| Gate | Evidence command or check | Current state |
|---|---|---|
| Docker startup | `docker compose up --build -d` and `docker compose ps` | Pass: api, worker, web and PostgreSQL healthy/running |
| Migration consistency | `docker compose exec -T api alembic upgrade head` | Pass: current head `0011_auth_rate_limit` |
| API lint | `uv run ruff check app tests` | Pass |
| API unit/domain suite | `uv run pytest -m "not integration" -q` | Pass |
| API integration suite | `docker compose exec -T api pytest -q` | Pass |
| Frontend tests | `npm test -- --run` | Pass |
| Frontend production build | `npm run build` | Pass |
| Scheduler correctness | benchmark test, S1 load-distribution regression and shared validator | Pass: zero H1–H12 violations; repeated local run p50 `0.086s`, p95 `0.117s`; representative availability case is `1.0×` max/min (see [benchmark evidence](./benchmark-2026-08-18.md)) |
| Controlled change history | Phase 05 integration test | Pass: source version remains published and unchanged |
| Concurrency control | Phase 08 concurrent activation test plus transactional result/draft-edit guards | Pass: one active version; stale writes are rejected or revalidated |
| Result transitions | Phase 06 integration/domain tests | Pass |
| Privacy/CSRF | auth, result privacy, login throttle and security-header tests | Pass |
| Backup/restore | logical `pg_dump` into temporary database and row-count verification | Pass: rehearsal recorded in [benchmark evidence](./benchmark-2026-08-18.md) |
| Live operator UI | frontend tests plus local in-app browser smoke | Pass: Manager/Lecturer routes and operator controls render; see [Phase 08 evidence](./phase-08-evidence-2026-08-18.md) |

## Pilot gates still requiring measurement

- Confirm at least 90% of invited Lecturers submit availability before the deadline in a realistic pilot.
- Measure that the mobile Lecturer availability flow completes within two minutes for the agreed five-day/eight-slot scenario.
- Exercise the 74-group fixture on the target demo machine and record wall-clock time, peak memory and unscheduled reason distribution.
- Have an Admin and Manager perform a publish, controlled change, result correction and remediation verification while checking the audit trail.
- Verify notification text and links with a real pilot account; configure a real email adapter only outside local development.
- Review keyboard navigation, focus order, contrast and screen-reader labels on the main dashboard, availability grid, schedule workspace and result form.
- Verify the two latest supported Chrome, Edge and Safari versions when the target environments are available.

Automated UI preview tests and the production build pass. A human browser pass is still required for measured mobile completion time and real screen-reader/contrast verification.

## Release procedure

1. Back up PostgreSQL and record the image/source revision.
2. Run the migration, API, worker and frontend gates above.
3. Load only approved seed/demo data; never ship the demo password to a shared environment.
4. Perform the Admin/Manager pilot workflow and retain the audit/event IDs.
5. Record pilot measurements and unresolved limitations.
6. Approve the release only when all pilot gates have an owner and evidence.
