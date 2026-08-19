# Phase 6 — Solver soft constraints S4–S7 and readiness

## Objective

Implement measurable S4–S7 soft scoring and expose diagnostics while preserving every hard
constraint, partial-solution behavior, and room-free solver boundary.

## Scope

- S4 compact schedule: reward assignments with fewer idle gaps/compact occupied slots.
- S5 minimum attendance days: reward schedules meeting the minimum attendance-day objective.
- S6 council stability: reward continuity with prior councils where valid; never override H1–H10 or
  immutable council records.
- S7 supervisor diversity: reward balanced supervisor/council distribution without introducing COI.
- Make weights/configuration explicit and server-configurable; expose score components as `scores`.
- Ensure readiness counts, warnings, and blocking issues explain missing availability, reviewers,
  eligible projects, timeslots, quota, and continuity inputs.

## Likely files and ownership

- `apps/api/app/scheduler/scheduler.py`, `candidates.py`, `models.py` — scoring/input model only.
- `apps/api/app/domain/schedule_operations.py` — readiness/diagnostic mapping.
- `apps/api/app/routes/target_round_contract.py`, `target_schedule_contract.py` — response fields.
- `apps/api/tests/test_scheduler_soft_constraints.py`, `test_benchmark.py`, readiness contract tests.

## Tests to write first

- Unit fixtures where each S4–S7 score changes predictably while H1–H13 remain valid.
- Weight configuration produces deterministic score breakdowns and does not affect scheduled-count
  priority.
- Prior-council continuity is a bonus only and never mutates immutable council rows.
- Zero/partial availability produces target readiness diagnostics and a persisted partial draft.
- Benchmark completes under the repository's 60-second budget with zero validator violations.

## Acceptance criteria

- `scores` contains named, bounded S4–S7 components and `overallScore` is reproducible for a fixed
  fixture/configuration.
- Objective still maximizes scheduled group count before soft score.
- Existing H1–H13, no-room-input, partial-solution, benchmark, and council tests pass unchanged.
- Readiness response matches spec §57 and blocks generation only for true hard blockers.

## Rollback

Feature-flag S4–S7 weights to zero and retain S1–S3 scoring. Restore the previous scheduler image;
persisted versions remain readable because score components are additive metadata.

