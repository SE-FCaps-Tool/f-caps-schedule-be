# Phase 07 — UX, reports and notifications

## Goal

Complete the operational user experience around the F-Caps visual system and make schedule/report information usable inside the application.

## Stories covered

Scoped schedule; notification/iCal; reports, plus UX acceptance for all P1 stories.

## Tasks

1. Apply project-local F-Caps tokens: blue/orange accents, light enterprise surfaces, typography, spacing, status semantics and no unlicensed brand assets.
2. Implement loading, empty, error, disabled, success and validation states for every form/table/schedule surface.
3. Implement Manager dashboard: availability, scheduled/unscheduled groups, changes, pending requests, load and attention groups.
4. Implement reports for Lecturer load/quota, unscheduled groups, group data quality, remediation and final outcomes.
5. Implement in-app report views with semester/round/version/generated-at provenance; do not add Excel export.
6. Implement in-app notification center and event status/retry; add email adapter as P2 behind the same outbox event source.
7. Implement iCal export as P2 with correct `Asia/Ho_Chi_Minh`/UTC handling; deployment-specific delivery details must not change the schedule semantics.
8. Add keyboard navigation, visible focus, labels, responsive mobile grid and WCAG AA contrast checks.
9. Add visual regression snapshots for critical dashboard, availability, schedule and result screens.

## Tests to write first

- Dashboard counts and filters match active/published data.
- Report provenance matches the selected active/published version.
- Notification event status, retry and idempotency.
- iCal opens with correct timezone/start/end values.
- Accessibility automated checks plus keyboard-only Playwright flows.
- 360px availability, schedule and request flows.
- Role-scoped empty/error states do not disclose unauthorized data.

## Exit criteria

- All required P1 UI flows work at 360px; scheduling workspace is usable from 1280px.
- In-app reports match the selected active/published version and expose provenance.
- Notification failures are visible and retryable without duplicate user-visible events.
