# Phase 4 — Round Integration and Scheduler Lifecycle

Status: completed.

Implemented decisions:

- Round accepts `timeframeId` on legacy and target create contracts.
- Round stores both `timeframe_id` and `timeframe_version_id`; the active version
  is pinned at creation time.
- The daily template is expanded across every date from `start_date` to
  `end_date`.
- Each `groupSlot` becomes one concrete Round `timeslot`; timeline gaps remain
  breaks and do not become slots.
- `session_duration_minutes` must equal the Timeframe group duration.
- Scheduler code remains unchanged because it already reads Round timeslots.
- Updating the global Timeframe never mutates existing Round slots.
- A DRAFT Round can change its pinned Timeframe or date range and regenerate
  slots. Regeneration is rejected after lecturer availability or group
  preferences exist.
- The legacy explicit `days[].slots[]` creation path remains available when no
  `timeframeId` is supplied.

None of these behaviors are implied by the global CRUD API.
