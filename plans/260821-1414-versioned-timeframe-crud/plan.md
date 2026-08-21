---
title: "Global Versioned Timeframe CRUD"
description: "Manage reusable Timeframe templates independently from Rounds and scheduling."
status: completed
priority: P1
effort: 24h
branch: main
tags: [feature, backend, database, api]
created: 2026-08-21
---

# Global Versioned Timeframe CRUD

## Objective

Add a shared Timeframe configuration catalog for ADMIN/MANAGER. A Timeframe
defines one daily window, block duration and per-group duration. Backend derives
blocks/day, groups/block, capacity/day and trailing unused minutes.

## Locked decisions

- Timeframe is global and has no `round_id`.
- CRUD does not create or mutate Round, round day, timeslot, availability,
  schedule version, session or scheduler input.
- Update is full replacement and creates an immutable revision.
- Delete is soft archive; history remains readable.
- `groupsPerBlock`, `blocksPerDay` and `capacityPerDay` are computed, never input.
- Round selection by `timeframeId` pins the active Timeframe revision and
  materializes its group slots into Round timeslots.

## Phases

| Phase | Name | Status |
|---|---|---|
| 1 | [Schema and calculation domain](./phase-01-schema-domain.md) | Implemented |
| 2 | [Global CRUD API](./phase-02-crud-api.md) | Implemented |
| 3 | [Isolation from Round data](./phase-03-revision-impact.md) | Implemented |
| 4 | [Round integration and scheduler lifecycle](./phase-04-scheduler-lifecycle.md) | Implemented |
| 5 | [Verification and FE handoff](./phase-05-verification-handoff.md) | Completed |
| 6 | [Flexible break configuration](./phase-06-flexible-breaks.md) | Completed |
| 7 | [Editable manual timelines](./phase-07-editable-manual-timelines.md) | Completed |

## Release gates

- Migration is additive and isolated.
- `07:00–17:30 / 135 / 45` returns `4 / 3 / 12 / 90`.
- Create, list, detail, revision update and archive are covered.
- CRUD leaves existing timeslot and schedule counts unchanged.
- OpenAPI and FE handoff contain only global endpoints.
