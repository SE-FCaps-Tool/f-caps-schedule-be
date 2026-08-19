# Phase 5 — Rooms, publish, post-publish, results, and remediation

## Objective

Close the operational contract gaps after scheduling: room assignment, publish readiness, controlled
post-publish changes, result submission, progression, and remediation verification.

## Scope

- Normalize available-room query params (`timeslotId`, `type`), room `type/status` aliases, room
  assignment body `roomId`, suggestion preview/apply, and atomic validation.
- Align publish readiness checks including numeric `roomConflicts`, and publish response/status.
- Align change-room, replace-reviewer, postpone, and makeup request fields and reason validation;
  preserve immutable historical councils and create replacement councils.
- Align result payload `{result,note,remediation:{deadline,verifierId}}`, result-owner permission,
  progression values, remediation verify, semester remediation list, and overdue-fail codes.

## Likely files and ownership

- `apps/api/app/routes/target_room_publish.py`, `room_assignment.py`, `target_operations.py`.
- `apps/api/app/routes/results.py`, `target_results_remediation.py`, `schedule_operations.py`.
- `apps/api/app/services/room_assignment.py`, `app/domain/result_workflow.py`, `response_models.py`.
- `apps/api/tests/test_phase04_room_assignment_contract.py`, `test_results_contract.py`,
  `test_publish_contract.py`, `test_phase05_immutable_council.py`.

## Tests to write first

- Room availability/type/status filters, assignment conflict, suggest/apply preview, and atomicity.
- Publish readiness shape and publish transition/notification behavior.
- Post-publish room/reviewer/postpone/makeup validation and council immutability.
- Review and defense result bodies, LEVEL_2 remediation requirements, verifier-in-council rule,
  progression, verify, and overdue fail.

## Acceptance criteria

- FE samples in spec §§65–76 pass target contract tests with exact envelopes and field casing.
- No target operation returns `room_id`, `old_lecturer_id`, `outcome`, or other legacy names unless
  explicitly marked as an accepted input alias.
- Publish/readiness and result/remediation errors use stable spec codes and preserve audit events.
- Immutable council and post-publish regression suites remain green.

## Rollback

Disable target operational aliases and use legacy room/result routes. Do not reverse migrations or
remove published sessions/results; response mapping is additive and reversible.

