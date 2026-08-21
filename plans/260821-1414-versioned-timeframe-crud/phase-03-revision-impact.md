# Phase 3 — Isolation from Round Data

Status: implemented.

Timeframe mutations must not:

- create or retire `round_days`/`timeslots`;
- change Round duration, status or capacity;
- invalidate availability/preferences;
- alter schedule snapshots, sessions or assignments;
- trigger scheduler execution or notifications for Round actors.

Integration tests compare timeslot counts before and after CRUD.
