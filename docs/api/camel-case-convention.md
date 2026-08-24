# API camelCase convention

Target API envelopes expose JSON object field names in `camelCase`. The response converter recursively renames a key only when it is lowercase `snake_case` matching `^[a-z][a-z0-9]*(_[a-z0-9]+)+$`.

All keys that do not match this shape remain unchanged. This protects data identifiers including enum codes such as `OPEN_REGISTRATION`, rule codes such as `S1`, and class or group codes such as `SE1701` and `GRP_02`. JSON values are never modified.

In target envelopes, `beforeJson` and `afterJson` and the objects they contain use the same response-key conversion. Their JSONB representation stored in the database remains unchanged.

The legacy `/api/v1/audit` endpoint is outside the target response converter and continues to expose `before_json` and `after_json`.

## Request input

Requests are accepted under either spelling while the frontend migrates. Every request body field has a camelCase alias, and every query parameter that used to be `snake_case` on the wire is read by a dependency that answers to both names. Only the camelCase name appears in `openapi.json`.

Sending both spellings of the same query parameter with different values is rejected with `422 AMBIGUOUS_PARAM` rather than resolved silently, so a half-migrated caller fails loudly instead of reading the wrong data.

Path parameter names were renamed to camelCase in the route templates. A URL never carries parameter names, so this changes the generated client signatures and nothing else.

## OpenAPI artifacts

Frontend code generation reads the committed files under `apps/api/`. It does not fetch either contract from a runtime endpoint.

- `openapi.json` describes the wire format currently returned by the backend. It is also the contract used by Swagger and regression checks.
- `openapi.camel.json` previews the future camelCase response wire format so frontend types can be generated before the backend response cutover.

Both files contain `info.x-be-commit`, which identifies the backend commit used to generate the artifact. Frontend builds should retain that value with their generated types so a mismatch is visible during rollback or deployment review.

The backend check can regenerate both files and detect drift with:

```powershell
uv run --directory apps/api python ../../tools/check_openapi_spec.py
```
