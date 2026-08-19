# Phase 06 — Documentation and rollout

## Changes

- Update `docs/api/manager-api.md`, `master-data.md`, `schemas.md`,
  `manager-fe-flow.md`, `semester-lifecycle-update.md`, and seed documentation.
- Document response counts, actor objects, filters, academic-year derivation,
  active-create conflict, close, and set-current behavior.
- Build the image and run `db-init` so migration and both Excel/seed-v1 sources
  complete without `UPCOMING` data.

## Acceptance

- FE can implement the list/detail/create/edit/action flow using only the
  documented endpoints.
- Docker bootstrap exits successfully and database status enum is verified.
