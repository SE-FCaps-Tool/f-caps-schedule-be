# Phase 01 — Contract baseline and compatibility policy

## Objective

Freeze the target API inventory and define how target routes coexist with legacy routes during the frontend migration.

## Scope

- Convert the endpoint list in `docs/capstone-fe-be-implementation-spec.md` into a machine-checkable per-operation registry. Each operation must include method/path, path/query parameters, request body schema, success status/schema, error codes/details, required role/scope, pagination rules, and whether it is a target route or legacy alias.
- Normalize path placeholders, trailing slashes, query parameters, and operation IDs.
- Decide the dual-route policy, deprecation headers, identifier representation, pagination defaults, and envelope migration rules.
- Add shared response/error helpers without changing business handlers yet.

## Likely files/modules

`apps/api/app/main.py`, `apps/api/app/response_models.py`, shared route utilities, OpenAPI/contract tests, and a new contract registry under `apps/api/tests/`.

## Tests to write first

- Registry detects every target path and reports legacy aliases separately, including the complete operation contract rather than path names alone.
- `{data}` and `{data,meta}` serialization tests.
- Error serialization tests for validation, forbidden, not-found, conflict, and domain errors.
- OpenAPI operation IDs and parameter names are stable.

## Acceptance criteria

- The 53 spec declarations are represented in a checked-in registry.
- Every current route is classified as target, alias, or intentionally out of scope.
- The standard success/error envelope and camelCase policy are documented and covered by tests.
- No existing behavior is removed.

## Dependencies and rollback

None. Revert the registry/helpers only; route behavior remains unchanged.
