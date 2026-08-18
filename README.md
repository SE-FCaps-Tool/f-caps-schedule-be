# Capstone Defense Scheduler

Scheduler-only V1 for managing assessment rounds, availability, schedule versions, controlled changes, published schedules, results and remediation. Full Assessment Platform scoring, Excel/FAP integration and cloud deployment are out of scope.

## Stack

- React + TypeScript + Vite
- FastAPI + Pydantic + SQLAlchemy + Alembic
- PostgreSQL 16
- OR-Tools CP-SAT scheduler
- Same-codebase worker for scheduler jobs and notification outbox delivery
- Docker Compose for local development

## Run locally

From the repository root:

```powershell
docker compose up --build
```

Services:

- Web UI: http://localhost:5173
- API/OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- PostgreSQL: localhost:5432, database `scheduler`

API and worker containers run `alembic upgrade head` on startup. Do not edit the old `schema.sql` as an operational migration; Alembic migrations are the database source of truth.

The seed fixture is loaded through the Admin endpoint when needed:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/admin/seed-fixture `
  -H "X-Test-Session: active-admin"
```

Local demo accounts use the password `SchedulerDemo2026!`:

- `admin@capstone.local`
- `manager@capstone.local`
- seeded students use `<student-code lower>@scheduler.test`

These credentials are for local development only and must be replaced before any shared deployment.

## Verify

API checks on the host:

```powershell
Push-Location apps/api
uv run ruff check app tests
uv run pytest -m "not integration" -q
Pop-Location
```

Full API and integration suite in Docker:

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

Frontend checks:

```powershell
Push-Location apps/web
npm install
npm test -- --run
npm run build
Pop-Location
```

Scheduler benchmark:

```powershell
Push-Location apps/api
uv run pytest tests/test_benchmark.py -q
Pop-Location
```

The target fixture contains 74 groups, 26 lecturers, 40 timeslots and 4 rooms. The test asserts completion under 60 seconds, complete scheduled/unscheduled accounting and zero validator violations.

## Product boundary and source precedence

This repository implements the Scheduler-only scope in `plans/capstone-scheduler/spec.md`. The authoritative order is:

1. `plans/capstone-scheduler/spec.md`
2. the Scheduler-only PRD/business rules
3. Alembic migrations and the implemented API contracts

Excel import/export has been removed from V1. Initial data is entered through Admin/Manager forms or the versioned seed fixture. H12 is session-count based; H13 is not implemented. Result Owner applies only to Defense 1.1 and Defense 2. The system roles are `ADMIN`, `MANAGER`, `LECTURER` and `STUDENT`; Reviewer, Supervisor, Result Owner, Remediation Verifier and Project Leader are contextual assignments.

## Operating workflow

See [the operator guide](docs/operator-guide.md) for the end-to-end local workflow, [the FE API guide](docs/api/README.md) for the complete route/request/response contract, and [the release checklist](docs/release-checklist.md) for evidence and pilot measurements still required before a real rollout.
