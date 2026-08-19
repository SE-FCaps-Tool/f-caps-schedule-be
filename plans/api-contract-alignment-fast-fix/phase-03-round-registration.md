# Phase 3 — Round, invitation, availability, and preference DTOs

## Objective

Finish the round wizard and lecturer/leader registration contract around the partially fixed nested
round-create endpoint.

## Scope

- Confirm `POST /semesters/{semesterId}/rounds` accepts the full camelCase wizard body and creates
  days, slots, room types, and metadata atomically.
- Add/align round list/detail query fields and target status mapping.
- Normalize invitation creation (`lecturerIds`), lecturer response (`decision`, optional `reason`),
  invitation list/remind response, and `PENDING/ACCEPTED/DECLINED` status.
- Normalize availability (`preferredLoad`, `slots[{timeslotId,available}]`) and group preferences
  (`timeslotIds`) with self-service role/scope checks.
- Preserve the domain rule that `REVIEW_1` has two reviewers and does not require result owner,
  while `DEFENSE_1_1` has three and may require it.

## Likely files and ownership

- `apps/api/app/routes/target_round_contract.py` — target request models and handlers.
- `apps/api/app/routes/master_data.py`, `app/domain/round_setup.py`, `app/domain/availability.py`.
- `apps/api/app/response_models.py` — round/invitation/availability DTOs.
- `apps/api/tests/test_phase03_api.py`, new `test_round_registration_contract.py`.

## Tests to write first

- Round wizard success and atomic rollback for overlapping slots/invalid room types.
- `groupSelectionMode` deadline requirement and round-type reviewer/result-owner validation.
- Invitation accept/decline and non-pending/remind conflicts.
- Availability round-trip, missing availability → busy-all behavior, and lecturer scope denial.
- Leader-only preference write, round state, slot ownership, and response envelope.

## Acceptance criteria

- FE sample bodies in spec §§49 and 53–56 are accepted with no snake_case conversion in FE.
- Target responses contain only target field names and documented status values.
- All round/invitation/availability/pref routes advertise request/query/response schemas in OpenAPI.
- Existing round lifecycle and archived-semester guards remain green.

## Rollback

Route DTOs can be reverted independently; keep the existing round metadata migration and legacy
handlers. Disable only target registration aliases if a production consumer reports a regression.

