# Phase 05 — Tests and OpenAPI verification

## Goal

Prove the new contract and concurrency behavior.

## Tests

- list counts and empty-count behavior;
- search/status/academic-year filters and invalid values;
- detail success/404;
- create default status, duplicate code, active conflict, creator metadata;
- PATCH validation, normalization, status immutability, updater metadata;
- note persistence, response serialization, and audit snapshot coverage;
- close transition and audit event;
- set-current closed→active, old-active closure, idempotency, 404;
- concurrent set-current/create invariant;
- ADMIN/MANAGER authorization and CSRF mutation behavior;
- OpenAPI request/query/response schema assertions.

## Verification

- compileall, Compose config validation, disposable PostgreSQL migration,
  targeted semester tests, and non-integration suite.
