# Phase 05 — Verification và rollout

## Goal

Verify the migration and running Docker stack without destroying the current database.

## Tasks

1. Run migration against a disposable PostgreSQL database first.
2. Run the full API test suite and schema/OpenAPI checks.
3. Back up the current database before applying the new migration locally.
4. Run `docker compose up` with the existing volume; verify `db-init` does not truncate data.
5. Check `/health`, `/openapi.json`, `/docs` and create/list/transition smoke requests.
6. Compare semester count, IDs, codes and round foreign-key counts before/after.

## Acceptance

- No existing data is deleted or re-keyed.
- API and worker containers remain healthy.
- `db-init` completes successfully and reports expected populated-database behavior.
- Rollback procedure is documented before production migration.

