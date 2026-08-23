# API camelCase convention

Target API envelopes expose JSON object field names in `camelCase`. The response converter recursively renames a key only when it is lowercase `snake_case` matching `^[a-z][a-z0-9]*(_[a-z0-9]+)+$`.

All keys that do not match this shape remain unchanged. This protects data identifiers including enum codes such as `OPEN_REGISTRATION`, rule codes such as `S1`, and class or group codes such as `SE1701` and `GRP_02`. JSON values are never modified.

In target envelopes, `beforeJson` and `afterJson` and the objects they contain use the same response-key conversion. Their JSONB representation stored in the database remains unchanged.

The legacy `/api/v1/audit` endpoint is outside the target response converter and continues to expose `before_json` and `after_json`.
