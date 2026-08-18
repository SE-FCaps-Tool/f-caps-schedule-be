# Scheduler-only V1 success-criteria matrix

This matrix is the Phase 08 acceptance index. “Automated” means the repository contains a test or repeatable command for the criterion. “Pilot” means code evidence alone cannot prove the real-world target.

| SC | Criterion | Evidence | Status |
|---:|---|---|---|
| 01 | Manager prepares and schedules a round in under one hour | Live Manager workflow: master data → round → timeslots/resources → invitation → scheduler; browser smoke in [Phase 08 evidence](./phase-08-evidence-2026-08-18.md) | Pilot measurement open |
| 02 | No Supervisor evaluates their own project | `apps/api/tests/test_constraints.py` H3 case; `test_candidates_and_snapshot.py` candidate filtering; shared validator on scheduler output | Automated pass |
| 03 | No Lecturer or room overlap | `apps/api/tests/test_constraints.py` H4/H5/H6/H7 cases; `test_db_constraints.py` exclusion constraint; `test_phase08_hardening.py` concurrency activation | Automated pass |
| 04 | Active/published schedule has no H1–H12 violation except valid H11 waiver | `test_constraints.py` covers H1–H12 and waiver actor/reason; `test_scheduler_engine.py` validates materialized output; publish guard integration test | Automated pass |
| 05 | Every unscheduled group has a reason and explanation | `test_candidates_and_snapshot.py` reason contract; `test_benchmark.py` checks accounting and reason codes; benchmark report records scheduled/unscheduled counts | Automated pass |
| 06 | Every post-publish change has actor/reason/before/after/notification | `test_phase05_api.py::test_controlled_change_creates_a_new_version_without_rewriting_source`; schedule-change audit/outbox assertions | Automated pass |
| 07 | Scheduler finishes the target fixture under 60 seconds | `test_benchmark.py`; repeated 74/26/40/4 run in [benchmark evidence](./benchmark-2026-08-18.md) | Automated pass |
| 08 | At least 90% of invited Lecturers submit availability before deadline | Availability/invitation API and worker reminder tests exist; cohort completion percentage requires a real pilot | Pilot measurement open |
| 09 | Lecturer completes 5 days × 8 slots in under two minutes on mobile | Live grid has 40-slot interaction, `aria-pressed`, responsive CSS and 390px smoke; human timing is still required | Synthetic smoke pass; human measurement open |
| 10 | Load max/min stays within 1.5× when availability permits | H12 session-count limits are enforced by CP-SAT and validator; S1 distribution regression schedules 8 groups as `6/6/6/6` across 4 Reviewers (`1.0×`) | Automated pass; target-machine measurement open |
| 11 | Invalid multi-record input creates no partial data and is audited | `test_phase03_api.py::test_group_mutation_validates_leader_and_rolls_back_atomically`; account lifecycle and audit integration tests | Automated pass |
| 12 | Every result transition is tested per round type | `test_domain_transitions.py`, `test_result_workflow.py`, `test_phase06_api.py`; covers Review, D1.1, D1.2, D2 and remediation | Automated pass |
| 13 | Result and H11 waiver changes are traceable | `test_assignments_and_results.py`, `test_audit.py`, `test_db_constraints.py`; audit query and append-only checks | Automated pass |

## Remaining release evidence

The implementation is locally runnable and automated gates are green. Phase 08 must remain open until SC-01, SC-08, SC-09, the target-machine SC-10 measurement, real Admin/Manager acceptance, accessibility review and the target Chrome/Edge/Safari matrix have owners and recorded observations. See [release checklist](./release-checklist.md).
