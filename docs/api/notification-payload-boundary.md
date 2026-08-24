# Notification payload casing boundary

Status: accepted

Notification and outbox payloads remain snake_case while stored in PostgreSQL and while passed to
`notification_dispatcher.py` email adapters. Event producers and workers therefore share one stable
internal vocabulary.

Camel-case conversion belongs only to the HTTP serialization boundary. API routes must use the
shared `app.api_contract.camelize` path (directly or through `success_payload`) when a notification
payload is exposed under the camelCase contract. They must not rewrite the stored JSON or mutate the
mapping passed to an email adapter.

This keeps retries and non-HTTP consumers independent of presentation casing, while generated HTTP
clients receive the public convention from one conversion point.
