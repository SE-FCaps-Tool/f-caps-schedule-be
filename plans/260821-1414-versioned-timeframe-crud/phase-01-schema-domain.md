# Phase 1 — Schema and Calculation Domain

Status: implemented.

- Add global `timeframes` identity table with soft archive and unique active name.
- Add `timeframe_versions` with one active revision per identity.
- Store only source inputs; derive block layout from them.
- Validate positive durations, ordered daily range, at least one fitting block,
  and exact block/group divisibility.
- Do not add columns or foreign keys to Round/timeslot tables.
