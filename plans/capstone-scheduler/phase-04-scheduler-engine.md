# Phase 04 — Constraint validator and CP-SAT scheduler

## Goal

Generate explainable full or partial ScheduleVersions without violating H1–H12.

## Stories covered

US-7 Manager runs and compares schedule versions; US-10 Manager monitors exceptions.

## Tasks

1. Define stable constraint code registry for H1–H12, S1–S8 and unscheduled reason codes. [x]
2. Implement pure interval/eligibility validator with structured violations: rule, objects, severity, explanation and remediation hint. [x]
3. Implement snapshot builder that captures round config, availability, assignments, waivers, prior reviewer continuity and soft weights. [x]
4. Implement candidate generator with static filtering for supervisor/conflict/availability/group-slot/H11 rules. [x]
5. Implement CP-SAT model for assignment, reviewer cardinality/distinctness, time/room/lecturer conflicts, H12 counts and soft objectives. [x]
6. Implement two-level objective: maximize scheduled groups, then optimize S1–S8 in configured order/weights. [x]
7. Implement job lifecycle: queued, running, completed, partial, failed, cancelled; retry without duplicating ScheduleVersion. [x]
8. Persist immutable ScheduleVersion metadata, input snapshot/reference, seed, parameters, solver status, objective breakdown and unscheduled explanations. [x]
9. Implement version comparison and active-version selection transaction. [x]
10. Build deterministic target fixture and benchmark harness for 74 groups, 26 lecturers, 40 timeslots and 4 rooms. [x]

## Tests to write first

- Property tests for half-open overlap: touching intervals do not overlap; partial overlap does.
- One focused test for every H1–H12, including valid H11 waiver and invalid waiver actor/scope.
- Reviewer count/distinctness tests for Review and Defense.
- Partial result always has exactly one reason code per unscheduled group.
- Solver output is rejected if the pure validator finds any hard violation.
- Soft score breakdown is deterministic with a fixed seed.
- Version activation leaves previous versions intact and permits only one active version.
- Target fixture completes within 60 seconds in CI-compatible benchmark mode; record solver status and objective quality.

## Exit criteria

- Auto-generated active candidate has zero H1–H12 violations, except explicitly audited H11 waiver cases.
- Manual edit and publish can reuse the exact validator.
- Target benchmark is repeatable and partial scheduling is explainable.
