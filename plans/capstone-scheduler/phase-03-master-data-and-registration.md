# Phase 03 — Master data and round registration

## Goal

Allow Admin/Manager to create trusted semester inputs and collect all lecturer/group availability needed by the scheduler.

## Stories covered

Admin/Manager academic data, round setup, lecturer availability and group availability.

## Tasks

1. Implement versioned seed fixtures for semester, project, group, student, membership, lecturer, supervisor and room data.
2. Implement form/API validation, duplicate detection, normalization and user-facing error/warning states.
3. Implement atomic multi-record mutation with actor/timestamp audit; no file import path exists in V1.
4. Implement Admin master-data screens and Manager semester/project/group/member/Leader screens.
5. Implement round creation/configuration, lifecycle gating, group eligibility selection, timeslot/room setup and reviewer invitations.
6. Implement invitation accept/decline with reason and deadline behavior.
7. Implement responsive lecturer availability grid and group Leader availability mode.
8. Implement manager-entered availability with source/actor audit and registration dashboard.
9. Add conflict declarations and validation feedback before scheduler run.

## Tests to write first

- Duplicate/missing/misidentified supervisor, group-size, membership and Leader errors in form/API mutations.
- Atomic rollback when one record in a multi-record mutation is invalid.
- Seed fixture loads deterministically and is idempotent in a clean database.
- Round cannot enter scheduling without required groups/timeslots/rooms/reviewer configuration.
- Invitation deadline and Manager-entered availability audit.
- Lecturer and group availability authorization, including 360px interaction smoke test.
- No-selection fallback semantics: Lecturer busy-all, group available-all.

## Exit criteria

- A Manager can create the target data through the management screens; CI can load the same data from the versioned seed fixture.
- A Lecturer and Leader can complete availability on mobile.
- A round reaches `REGISTRATION_CLOSED` only with valid required inputs and visible warnings.
