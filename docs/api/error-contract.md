# API error contract

Every JSON error response from the API uses one envelope, on every route and every status:

~~~json
{
  "error": {
    "code": "SEMESTER_NOT_FOUND",
    "message": "Semester does not exist.",
    "details": {}
  }
}
~~~

- `code` — stable machine-readable identifier. Clients branch on this, never on `message`.
- `message` — human-readable sentence. Safe to show to an end user, but prefer a localized
  string keyed by `code` where one exists.
- `details` — endpoint-specific object. `{}` when there is nothing to add.

There is no `detail` key. Responses are camelCase, including keys nested inside `details`.

## Codes produced by the framework

| Situation | Status | `code` |
|---|---|---|
| Request body or query fails validation | 422 | `VALIDATION_ERROR` |
| Mutating request without a valid `X-CSRF-Token` | 403 | `CSRF_INVALID` |
| Handler raised an error without its own code | varies | `HTTP_ERROR` |

Every other code comes from the handler that raised it and is documented with that endpoint.

## Validation errors

`details.errors` lists one entry per invalid field:

~~~json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "errors": [
        { "type": "missing", "loc": ["body", "reviewerCount"], "msg": "Field required" }
      ]
    }
  }
}
~~~

`loc` holds the field name **exactly as the caller sent it**, so a client can map an error back
to the input that produced it. It is not renamed to match any convention.

Entries carry only `type`, `loc`, and `msg`. The submitted value is deliberately absent: echoing
it back would return sign-in fields to the caller on the auth route.

## Diagnostics attached by handlers

A handler may attach extra keys when it raises. Those keys appear inside `details`:

~~~json
{
  "error": {
    "code": "HARD_CONSTRAINT_VIOLATION",
    "message": "HARD_CONSTRAINT_VIOLATION",
    "details": { "violations": [{ "ruleCode": "H1", "groupId": 7 }] }
  }
}
~~~

## OpenAPI

Every operation under `/api/` declares a `default` response referencing `ApiErrorEnvelope`, plus
an explicit `422` where validation applies. `default` is used rather than an enumerated list of
4xx codes because any handler can raise any status, and listing a fixed set would describe
endpoints inaccurately.
