# Phase 08 evidence — 2026-08-18

This document records the reproducible local evidence for Scheduler-only V1. It intentionally separates automated checks from pilot gates that require human operators or additional browser environments.

The criterion-by-criterion index is [success-criteria-matrix.md](./success-criteria-matrix.md).

## Automated checks

Run from the repository root:

```powershell
docker compose up -d --build api worker web
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q

Push-Location apps/api
uv run ruff check app tests
python -m compileall -q app
Pop-Location

Push-Location apps/web
npm run lint
npm test -- --run
npm run build
Pop-Location
```

Observed on this date:

- Docker Compose: `api`, `worker`, `web` running; PostgreSQL healthy.
- API migration: current head `0011_auth_rate_limit`.
- API suite: full Docker suite passed, including Phase 08 concurrent activation, authorization/IDOR, CSRF, append-only audit, result transitions and controlled changes.
- Frontend: 2 test files, 8 tests passed; lint and production build passed.
- Health checks: `GET http://localhost:8000/health` returned HTTP 200 and `GET http://localhost:5173/` returned HTTP 200.
- Scheduler benchmark and backup/restore rehearsal: [benchmark evidence](./benchmark-2026-08-18.md).
- S1 reviewer-load regression: 8 fully available groups across 4 Reviewers produced `6/6/6/6` sessions (`1.0×` max/min) and passed the shared validator.
- Dashboard, round-list and lecturer-load API latency: 30-request local samples stayed below 32 ms p95; details are in the benchmark evidence.

## Live browser smoke

Using the local in-app browser against `http://localhost:5173`:

- Manager desktop flow rendered Dashboard, Master data, Rounds, Availability, Schedule, Results, Reports and Notifications.
- Round operations rendered create-round, timeslot generation, invitation, resource attachment and postpone/cancel controls.
- Schedule rendered scheduler run, version history, H11 waiver and session inspector areas; empty-version state correctly disabled session-only actions.
- Lecturer flow rendered scoped navigation, pending invitations, Accept/Decline controls and availability preference/grid.
- Accepting an invitation called the scoped endpoint `/api/v1/rounds/{round_id}/invitations/{lecturer_id}/response` and returned visible success feedback.
- A 390px viewport smoke retained readable navigation and usable invitation/availability controls.
- After the last Docker rebuild, the Round snapshot contained `GV có slot` and no `undefined GV` output.
- Accessibility smoke on Availability, Schedule and Results found zero unlabeled form controls and zero unnamed buttons/links; `:focus-visible` was present and the AA-safe muted text token measured 4.92:1 against white.

This is a browser smoke check, not a substitute for a real operator pilot or cross-browser certification.

## Pilot and release gates still open

- Measure at least 90% Lecturer availability completion in a realistic invited cohort.
- Measure the agreed five-day/eight-slot Lecturer mobile task at under two minutes with a human participant.
- Run the 74-group fixture on the target demo machine and record wall-clock time, peak memory and unscheduled-reason distribution.
- Have Admin and Manager execute publish, controlled change, result correction and remediation verification while checking audit entries.
- Verify notification copy and links with a real pilot account.
- Perform keyboard, focus-order, contrast and screen-reader review on the dashboard, availability grid, schedule workspace and result form.
- Verify the two latest supported Chrome, Edge and Safari versions when those target environments are available.

Until these items have owners and evidence, Phase 08 remains release-ready for local/demo use but not formally pilot-complete.
