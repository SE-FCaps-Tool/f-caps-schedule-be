# Phase 01 — Foundation, architecture spike and test harness

## Goal

Turn the documentation-only workspace into a reproducible modular-monolith workspace with a frontend, API, worker entry point, database migrations and automated checks.

## Stories covered

All P1 stories as infrastructure; directly enables US-1 through US-10.

## Tasks

1. Create repository layout: `apps/web`, `apps/api`, `packages/contracts`, `packages/ui-tokens`, `tests/fixtures`, `infra`.
2. Scaffold React/TypeScript/Vite web app and FastAPI/Python backend with pinned toolchain versions.
3. Add PostgreSQL Docker Compose for local development, health checks, seed command and environment validation.
4. Add API, worker and web commands; worker must be a separate process using the same backend package.
5. Add OpenAPI generation and a typed frontend client; reject hand-written request/response drift in CI.
6. Add lint, format, type-check, unit, integration and Playwright test commands.
7. Copy the project-local F-Caps tokens into the UI package and create an accessible shell with authenticated/unauthenticated states.
8. Add a traceability file mapping FR/SC → module → test file, initially marked `not_started`.
9. Run a vertical slice: health check, login placeholder, database migration, one protected API route and one rendered dashboard shell.

## Tests to write first

- Toolchain smoke test and API health test.
- Database connection/migration up-down test.
- Protected route rejects unauthenticated request and accepts an active test account.
- Worker can claim and complete a no-op job idempotently.
- Frontend shell renders loading, error and empty states at 360px and desktop widths.

## Exit criteria

- Fresh checkout starts with documented commands.
- CI/test command fails on type, lint, migration or contract errors.
- No feature code depends on the stale root `schema.sql`.
- Stack/auth/deployment assumptions are recorded as ADRs.

