# Phase 05 — Schedule workspace, manual change and publish workflow

## Goal

Give Managers a safe scheduling workspace and preserve history through publication and operational changes.

## Stories covered

US-8 manual changes; US-9 personal schedule visibility; US-10 operational monitoring.

## Tasks

1. Build schedule version list/detail/compare screens with hard-violation and soft-score explanations.
2. Build desktop scheduling workspace with filters by day, timeslot, room, Lecturer, group and status.
3. Implement draft session edit for timeslot, room and Reviewer through validator-backed commands.
4. Implement active-version selection and publish guard; publish notification recipients are derived from assignments.
5. Implement controlled post-publish change with reason, before/after, actor, timestamp and affected-user notification.
6. Implement reschedule request workflow for Lecturer/Leader and Manager decision notes.
7. Implement emergency replacement suggestions and postponement when a full council cannot be maintained.
8. Implement whole-round postpone/cancel policy for Admin/Manager with notification and immutable history.
9. Implement personal schedule views and privacy-scoped query endpoints.

## Tests to write first

- Publish rejects inactive/invalid version and sends one event per recipient scope.
- Manual edit rejects every affected H violation and stores no partial mutation.
- Post-publish changes require reason and preserve completed-session reviewer snapshots.
- Student cannot query another group; Lecturer cannot query unrelated private data.
- Emergency replacement never proposes a reviewer violating H1–H12.
- Postponed/cancelled round behavior and reschedule request authorization.
- Idempotent publish/change notification outbox events.

## Exit criteria

- Manager can go from a validated version to published schedule with audit and notifications.
- A controlled change does not rewrite historical completed sessions.
- Schedule pages remain usable at the required desktop/mobile breakpoints.

