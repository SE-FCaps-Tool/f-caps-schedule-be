## 2026-08-21 — Planned versioned Timeframe CRUD

- Decision / outcome: Plan one active Timeframe per Round with historical revisions, generated block/child slots, edits allowed in every Round status outside archived Semesters, and no multi-Manager optimistic locking.
- Evidence: Current schema already provides `round_days`, durable `timeslots`, `timeslots.active`, actor references by `timeslot_id`, active-slot scheduler loading, and immutable schedule assignment datetimes.
- Follow-up: Implement phases in `plans/260821-1414-versioned-timeframe-crud/plan.md`; verify old manual rounds and published schedules remain unchanged.

## 2026-08-21 — Global Timeframe with flexible breaks

- Decision / outcome: The earlier round-owned design above is superseded. Timeframe is now a global reusable configuration with immutable revisions. A revision supports `breakBetweenBlocksMinutes` and generic named `breakWindows`; blocks are generated independently inside each available segment and remain disconnected from Round/scheduler data.
- Evidence: Migration `0031_timeframe_breaks` upgrade/downgrade preserved Round schedule counts and backfilled old revisions with zero gap; 246 non-integration tests, 4 Docker Timeframe API tests, scoped Ruff, OpenAPI validation and independent review passed.
- Follow-up: A separate future phase must define how a Round selects/pins `timeframeId` and generates concrete dated timeslots.

## 2026-08-21 — Editable manual Timeframe timelines

- Decision / outcome: Quick preview now serves as a draft timeline generator. Manager can edit/add/remove timelines, recalculate through manual preview, then create or revise a Timeframe from the final timeline snapshot. Heterogeneous summaries are nullable while `blocks[].groupSlots[]` remains uniform for consumers.
- Evidence: Migration `0032_manual_timelines` round-tripped; 254 non-integration tests, 8 Docker Timeframe API tests, scoped Ruff and OpenAPI validation passed. Final review found no Critical/High/Medium findings.
- Follow-up: Round integration remains deferred; scheduler must eventually consume the canonical block/group-slot detail rather than formula-only summary fields.

## 2026-08-21 — Round–Timeframe integration

- Decision / outcome: Round creation accepts `timeframeId` on both legacy and
  target contracts. The backend pins the active Timeframe revision in
  `rounds.timeframe_id/timeframe_version_id`, expands every `groupSlot` across
  the Round date range, and leaves scheduler candidate logic unchanged.
- Safety: Global Timeframe edits never mutate existing Round slots. A DRAFT
  Round may change its pinned Timeframe or date range and rebuild slots; rebuild
  is blocked after lecturer availability or group preferences exist. Explicit
  `days[].slots[]` remains backward compatible when no Timeframe is selected.
- Evidence: Migration `0033_round_timeframe_binding` downgrade/upgrade passed;
  10 Docker Timeframe API integration tests, target-contract tests and all
  non-integration tests passed. The complete Docker suite was not a clean
  baseline because the shared database contains pre-existing seed data and
  unrelated legacy failures.
