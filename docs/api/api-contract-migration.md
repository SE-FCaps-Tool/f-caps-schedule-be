# API contract migration handoff

This backend now exposes the target nested route families alongside the legacy
paths. The machine-readable operation inventory lives in
`apps/api/app/api_contract.py`; the phase plan is
`plans/api-contract-alignment/plan.md`.

## Consumer migration rules

- Prefer target routes and the `{data}` / `{data,meta}` success envelope.
- Treat `error.code`, `error.message`, and `error.details` as the stable error contract.
- Use string-safe IDs in frontend state and preserve pagination metadata.
- Keep legacy routes during the deprecation window. They return `Deprecation: true`,
  a `Sunset` date, and a `Link` successor header where a direct successor is known.
- Route usage counters are available through the in-process telemetry helper for
  deployment-level export or replacement with the platform metrics sink.

## External handoff evidence required before cleanup

The frontend repository must attach a versioned OpenAPI export, a screen-to-endpoint
migration matrix, and consumer sign-off. Legacy aliases may be removed only after
route telemetry shows zero usage for the agreed observation window and rollback has
been rehearsed with additive migrations.
