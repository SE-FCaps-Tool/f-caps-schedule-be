# Phase 7 — Editable Manual Timelines

Status: completed.

## Approved behavior

- Keep `POST /timeframes/preview` as the quick calculator that produces draft
  `blocks` for FE editing.
- Add `POST /timeframes/manual` to create a Timeframe from the final edited
  timeline list.
- Add `PATCH /timeframes/{timeframeId}/manual` as full replacement and create
  an immutable revision.
- A manual request supplies one shared `groupDurationMinutes` and, per timeline,
  `startTime`, `endTime`, and `groupsPerSlot`.
- Require each timeline duration to equal
  `groupDurationMinutes * groupsPerSlot`; timelines must not overlap.
- Derive daily start/end, capacity, breaks, blocks and group slots from the
  final timeline list.
- Preserve quick create/update behavior and existing records.
- Keep manual timeline snapshots on each Timeframe revision; do not integrate
  Timeframes with Rounds or scheduler inputs in this phase.

## Implementation

- [x] Add an additive migration for immutable manual timeline snapshots.
- [x] Add pure-domain manual timeline normalization, validation and metrics.
- [x] Add manual preview/create/update service operations and read assembly.
- [x] Add typed request/response contracts and routes.
- [x] Add domain and PostgreSQL API coverage, including revision history.
- [x] Update the FE handoff with complete requests, responses and UI flow.

## Success criteria

- Preview output can be converted to the manual mutation payload without
  losing block boundaries.
- FE can add, remove or change timelines before saving.
- Manual detail/list reads reconstruct the exact saved timeline snapshot.
- Capacity equals the sum of `groupsPerSlot`; gap metrics come from spaces
  between timelines.
- Existing formula-based Timeframes remain readable and mutable.

## Verification — 2026-08-21

- `uv run pytest -m "not integration" -q` — 254 passed.
- Docker PostgreSQL `tests/test_timeframe_api.py` — 8 passed.
- Alembic downgrade to `0031_timeframe_breaks` and upgrade to head passed.
- Database head is `0032_manual_timelines`.
- Scoped Ruff checks passed; `response_models.py` passed with only the
  repository's pre-existing `UP037` findings ignored.
- OpenAPI exposes manual preview/create/update and nullable heterogeneous
  summary fields.
- Final sequential code review found no Critical, High or Medium findings.
