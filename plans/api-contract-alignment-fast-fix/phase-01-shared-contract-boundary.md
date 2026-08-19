# Phase 1 — Shared target contract boundary

## Objective

Make the target API consistently accept camelCase and emit the spec envelope, external string IDs,
and structured errors without changing legacy route behavior.

## Scope

- Add reusable Pydantic request/response DTOs with `populate_by_name` and explicit aliases.
- Add an external-ID codec that accepts `123`, `"123"`, and prefixed values such as `grp_123`, while
  serializing target responses as the documented prefixed string.
- Apply `success_payload`/pagination consistently to target routes and map target exceptions to
  `error_payload` with stable codes.
- Add path/query parsing for target placeholder names (`groupId`, `versionId`, etc.) while retaining
  legacy snake_case route signatures.
- Document one target status/enum mapping per resource; do not mutate historical database values.

## Likely files and ownership

- `apps/api/app/api_contract.py` — envelope, pagination, external-ID and error helpers (shared).
- `apps/api/app/response_models.py` — target DTOs and aliases.
- `apps/api/app/main.py`, `apps/api/app/domain/errors.py` — exception translation boundary.
- `apps/api/app/routes/target_*.py` — adopt target DTOs only.
- `apps/api/tests/test_api_contract.py`, `apps/api/tests/test_target_contract.py` — contract tests.

## Tests to write first

- CamelCase request validates and snake_case alias remains accepted on target routes.
- `grp_123` and integer `123` resolve to the same row; target output is `grp_123`.
- List/single success envelopes and `page/pageSize/total` metadata validate.
- Domain, 404, 403, 409, and 422 errors return `{error:{code,message,details}}`.
- A representative legacy route still returns its old payload.

## Acceptance criteria

- All target routes use the shared envelope/error helpers; no target response is a raw list/object.
- OpenAPI exposes camelCase aliases and target path parameter names for the touched operations.
- ID codec tests cover every target prefix listed in `plan.md` and reject malformed IDs with a stable
  validation code.
- Non-integration suite and target contract tests pass; no legacy route snapshot changes.

## Rollback

Keep the adapter behind target routes only. Revert route dependency wiring or disable target aliases;
leave legacy handlers and additive mappings untouched.

