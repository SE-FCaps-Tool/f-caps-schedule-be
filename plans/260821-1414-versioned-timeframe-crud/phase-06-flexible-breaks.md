# Phase 6 — Flexible Break Configuration

Status: completed.

## Approved contract

- Add `breakBetweenBlocksMinutes`, default `0` for backward compatibility.
- Add ordered `breakWindows[]` with `name`, `startTime`, `endTime`.
- A break window may represent lunch or any other unavailable daily interval.
- Break windows must be inside the Timeframe range and must not overlap.
- Generate blocks independently inside each available segment; no block may
  cross a break window.
- Apply the between-block gap only between consecutive blocks in the same
  available segment.
- Group slots remain contiguous inside a block.
- Persist all break inputs per immutable Timeframe revision.
- Keep Timeframe independent from Round and scheduler in this phase.

## Verification

- Domain coverage includes lunch windows, between-block gaps, sorting,
  overlap rejection and boundary errors.
- CRUD integration confirms break configuration survives create, revision
  update and history reads without changing Round, timeslot or scheduler-job
  counts.
- Migration `0031_timeframe_breaks` supplies backward-compatible defaults of a
  zero-minute gap and an empty break-window list; the Docker database reports
  this migration as the current head.
- FE handoff documents the complete request, response and calculation
  semantics.

## Verification results — 2026-08-21

- `uv run ruff check app/domain/timeframes.py app/routes/target_timeframe_contract.py app/services/timeframe_service.py tests/test_timeframe_generation.py tests/test_timeframe_api.py migrations/versions/0031_timeframe_breaks.py` — passed.
- `uv run pytest tests/test_timeframe_generation.py tests/test_timeframe_api.py -m "not integration" -q` — 18 passed.
- `docker compose exec -T api python -m pytest tests/test_timeframe_api.py::test_global_timeframe_crud_creates_revisions_without_touching_round_slots -q` — 1 passed.
- `uv run pytest -m "not integration" -q` — 246 passed.
- `docker compose exec -T api alembic current` — `0031_timeframe_breaks (head)`.
- `uv run ruff check app tests` — did not pass: 20 findings remain outside
  the focused Phase 6 lint scope in concurrently edited files; no unrelated
  source or test files were changed as part of this phase-plan sync.
