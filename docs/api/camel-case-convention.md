# API camelCase convention

This is the final contract for the Phase 9 migration. JSON response keys are
`camelCase`; the rule is enforced by `apps/api/tests/test_wire_is_camel.py` and
the committed `apps/api/openapi.json`.

Every JSON response exposes object field names in `camelCase`. The application's
default JSON response class recursively renames a key only when it is lowercase
`snake_case` matching `^[a-z][a-z0-9]*(_[a-z0-9]+)+$`.

All keys that do not match this shape remain unchanged. This protects data identifiers including enum codes such as `OPEN_REGISTRATION`, rule codes such as `S1`, and class or group codes such as `SE1701` and `GRP_02`. JSON values are never modified.

`beforeJson`, `afterJson`, and the objects they contain use the same
response-key conversion. Their JSONB representation stored in the database
remains unchanged.

## Request input

Requests are accepted under either spelling while the frontend migrates. Every request body field has a camelCase alias, and every query parameter that used to be `snake_case` on the wire is read by a dependency that answers to both names. Only the camelCase name appears in `openapi.json`.

Sending both spellings of the same query parameter with different values is rejected with `422 AMBIGUOUS_PARAM` rather than resolved silently, so a half-migrated caller fails loudly instead of reading the wrong data.

Path parameter names were renamed to camelCase in the route templates. A URL never carries parameter names, so this changes the generated client signatures and nothing else.

## OpenAPI artifact

Frontend code generation reads the single committed `apps/api/openapi.json` artifact. It does not fetch the contract from a runtime endpoint.

- `openapi.json` describes the wire format currently returned by the backend. It is also the contract used by Swagger and regression checks.

The document contains `info.x-be-commit` and `info.x-be-wire-case`. Frontend generated types retain those values so a mismatch is visible during rollback or deployment review.

The backend check can regenerate the artifact and detect drift with:

```powershell
uv run --directory apps/api python ../../tools/check_openapi_spec.py
```

The BE contract workflow runs this drift check as a blocking gate. The FE workflow
also fails when its committed generated artifact differs from BE `main`; regenerate
with `npm run typegen` before merging either repository.

## Exceptions and invariants

- Only JSON object keys are converted. Values are never changed, including enum
  codes, identifiers, exported file contents, and JSON payloads persisted in the
  database. Audit snapshots keep their stored JSONB shape; HTTP responses apply
  the normal response conversion.
- Authentication transport names are protocol constants and stay unchanged:
  `scheduler_session`, `scheduler_csrf`, `X-CSRF-Token`, and `X-Test-Session`.
  The first cookie is HttpOnly; the CSRF cookie is readable by the browser.
- The only accepted error response shape is `{ "error": { "code", "message",
  "details" } }`.
- New endpoints must declare an explicit `response_model`. The OpenAPI coverage
  test and the wire-case test then enforce the contract automatically.

The required CI contract job is green independently of the broader application
baseline. On 2026-08-24 the full suite still contains pre-existing fixture and
database-constraint failures: the codebase is on `seed-v5`/`SU26`, while several
older tests assert `SE-2026-2027`/`seed-v1`, and one constraint test inserts a
session without the now-required council. CI keeps that baseline run
informational until those unrelated tests are reconciled; camelCase or auth
contract regressions remain blocking failures.

## Request compatibility

Request bodies accept the camelCase aliases used by the wire contract while the
backend may continue accepting legacy snake_case during migration. This input
tolerance does not change the response convention.
