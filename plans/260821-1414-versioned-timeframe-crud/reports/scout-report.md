# Scout Report — Versioned Timeframe CRUD

> Historical discovery only. The round-owned proposal below was superseded by
> the approved global Timeframe architecture in `../plan.md`.

## Existing Reusable Behavior

- `round_days` and `timeslots` already model concrete scheduling intervals.
- `timeslots.active` already supports retirement without deletion.
- Lecturer availability and group preferences reference `timeslot_id` directly.
- Scheduler loads active slots and builds Candidates from concrete start/end times.
- H13 currently applies one round-wide `max_groups_per_timeslot`.
- ScheduleAssignments persist timeslot, start/end, project, and reviewers; published history can survive slot retirement.
- ScheduleVersion input snapshots already store groups, slot IDs, availability, and hard-rule settings.

## Main Integration Files

- `apps/api/app/routes/target_round_contract.py`: target Round request and explicit-slot validation.
- `apps/api/app/routes/master_data.py`: Round persistence, actor choices, readiness.
- `apps/api/app/routes/manager_extensions.py`: Round PATCH/detail and slot retirement.
- `apps/api/app/routes/schedule_operations.py`: active-slot loading, RoundInput, lifecycle.
- `apps/api/app/scheduler/{models,candidates,scheduler,validator,snapshot}.py`: solver pipeline.
- Migrations `0002`, `0014`, and `0022`: schema foundations.

## Risks Found

- Some readiness/detail queries count inactive slots or return retired selections.
- Existing `max_groups_per_timeslot` means concurrent capacity, not sequential groups inside a block.
- Existing target Round creation requires explicit slots and owns `durationMinutes`; Timeframe flow needs a backward-compatible ownership rule.
- Reusing or deleting old slot IDs would corrupt actor choices and schedule provenance.
- A draft becomes semantically stale after a Timeframe revision unless activation/publish verifies snapshot provenance.

## Scope Decisions

- One active Timeframe per Round in V1.
- One Manager; no optimistic concurrency contract.
- No external research needed; implementation uses existing FastAPI/PostgreSQL/CP-SAT patterns.
- Untracked `tools/generated/` is unrelated user data and must remain untouched.
