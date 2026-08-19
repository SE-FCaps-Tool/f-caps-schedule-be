# Audit: `capstone-fe-be-implementation-spec.md` vs actual implementation

Full request/response/status/error-code comparison of PHẦN VII–XVI of
`docs/capstone-fe-be-implementation-spec.md` (sections 41–76, the BE API
contract) against the `target_*.py` route files that are meant to implement
it. **8/8 audited section groups have at least one HIGH-severity divergence.**
This is not a spot-check list — treat it as the current ground truth of where
the target contract is incomplete.

Files audited: `apps/api/app/routes/target_group_project.py`,
`target_round_contract.py`, `target_schedule_contract.py`,
`target_room_publish.py`, `target_operations.py`, `target_results_remediation.py`,
plus the legacy handlers they wrap (`master_data.py`, `manager_extensions.py`,
`schedule_operations.py`, `room_assignment.py`, `results.py`).

---

## Systemic issues (apply across most/all endpoints — fix these first)

### S1. Error envelope is never `{"error": {...}}` (HIGH, 100% of error responses)

Spec (PHẦN VI) requires every error response to be:

```json
{ "error": { "code": "...", "message": "...", "details": {} } }
```

`app/api_contract.py:205-223` defines `error_payload()` / `ApiErrorEnvelope`
that produce exactly this shape — but **they are never called anywhere in the
codebase** (confirmed by repo-wide grep, zero call sites outside their own
definition). Every route still raises `HTTPException(status_code=..., detail={"code":...,"message":...})`,
and FastAPI's default handler wraps that as `{"detail": {"code":...,"message":...}}`.
No exception handler in `app/main.py` translates `detail` → `error`. Every
single error response from the API — not just the audited sections — currently
violates PHẦN VI.

**Fix shape:** register a FastAPI exception handler for `HTTPException` (and
`DomainError`) in `app/main.py` that emits `error_payload(...)` instead of the
default `{"detail": ...}` body, repo-wide, once.

### S2. Error code vocabulary doesn't match spec's PHẦN XVI list (HIGH)

Of the 26 canonical codes in the spec, only **5 are ever raised anywhere** in
the codebase: `SEMESTER_NOT_ACTIVE`, `GROUP_CODE_DUPLICATE`,
`PROJECT_ALREADY_ASSIGNED`, `ROOM_TYPE_NOT_ALLOWED`, `ROOM_CONFLICT`.

The other 21 are dead — the implementation raises a parallel, differently-named
vocabulary for the same business rules:

| Spec code (PHẦN XVI) | Actual code raised | Location |
|---|---|---|
| `ROUND_INVALID_STATE` | `ROUND_TRANSITION_NOT_ALLOWED` | `app/domain/transitions.py:34` |
| `ROUND_INVALID_TIMESLOT` | never raised | — |
| `ROUND_ROOM_TYPE_REQUIRED` | never raised | — |
| `INVITATION_NOT_PENDING` / `INVITATION_NOT_ACCEPTED` | `INVITATION_RESPONSE_INVALID`, `INVITATION_REASON_REQUIRED`, `INVITATION_DEADLINE_PASSED` | `app/domain/availability.py:38-52` |
| `SCHEDULER_NOT_READY` | `ROUND_INPUTS_INCOMPLETE`, `SCHEDULE_RERUN_FORBIDDEN`, `ROUND_POSTPONED` | `schedule_operations.py` (`run_scheduler`) |
| `ROOM_NOT_ACTIVE` | `ROOM_INACTIVE` | `services/room_assignment.py:171,289` |
| `SESSION_INVALID_STATE` | `ROOM_ASSIGNMENT_STATE_INVALID` (room ops), `SESSION_NOT_POSTPONABLE` (postpone) | `services/room_assignment.py:137,162`; `schedule_operations.py:1235` |
| `REVIEWER_NOT_AVAILABLE` / `REVIEWER_IS_SUPERVISOR` / `REVIEWER_COI` / `REVIEWER_TIME_CONFLICT` / `REVIEWER_QUOTA_EXCEEDED` | generic `REVIEWER_OVERLAP` only; the 5 specific codes are never raised because Replace Reviewer's request shape doesn't match the spec flow (see §72 below) | `schedule_operations.py:848` |
| `RESULT_PERMISSION_DENIED` | plain `HTTPException(403, detail="...")` — no `code` field at all | `results.py:37,193` |
| `RESULT_TYPE_INVALID` | `OUTCOME_NOT_ALLOWED` | `app/domain/result_workflow.py:14` |
| `REMEDIATION_REQUIRED_FIELDS_MISSING` | `REMEDIATION_FIELDS_REQUIRED` | `results.py:212` |
| `STUDENT_NOT_ENROLLED` / `STUDENT_ALREADY_IN_GROUP` / `LEADER_NOT_ACTIVE_MEMBER` | never raised (validation not implemented — see §42) | — |
| `PROJECT_HAS_NO_MAIN_SUPERVISOR` | never raised (validation not implemented — see §45) | — |
| `GROUP_NOT_ELIGIBLE` / `USER_NOT_GROUP_LEADER` | never raised (eligibility checks not implemented — see §48) | — |

Undocumented codes also raised outside the spec list (mostly acceptable
infra-level 404/403 codes, but some look like they should have been the spec
codes above under a different name): `AUTH_FORBIDDEN`, `GROUP_NOT_FOUND`,
`MAJOR_NOT_FOUND`, `PROJECT_NOT_FOUND`, `SESSION_NOT_FOUND`,
`AUTH_RESOURCE_SCOPE`, `ROOM_NOT_FOUND`, `ROOM_DUPLICATE`, `VERSION_NOT_ACTIVE`,
`ROUND_NOT_FOUND`, `INVITATION_RESOURCE_INVALID`, `VERSION_NOT_FOUND`,
`DATA_DUPLICATE`, `ROUND_DATE_INVALID`, `MEMBERSHIP_NOT_FOUND`,
`LEADER_MEMBER_NOT_FOUND`, `VERIFIER_NOT_REVIEWER`,
`REMEDIATION_VERIFIER_REQUIRED`, `REMEDIATION_ALREADY_DECIDED`,
`REMEDIATION_NOT_FOUND`, `ACCOUNT_DUPLICATE`, `ACCOUNT_ROLE_INVALID`,
`SEMESTER_DURATION_INVALID`, `ACTIVE_SEMESTER_EXISTS`, `ROUND_NOT_LOCKED`,
`GROUP_SELECTION_DISABLED`, `GROUP_NOT_IN_ROUND`, `AVAILABILITY_DEADLINE_PASSED`,
`CONFLICT_RESOURCE_INVALID`, `MAKEUP_ALREADY_EXISTS`, `SESSION_OUT_OF_SCOPE`,
`SESSION_NOT_POSTPONED`.

**Decision needed before fixing:** either (a) rename the 21 dead spec codes to
match what's actually implemented and update the spec doc, or (b) rename the
actual codes to match the spec. Given FE is presumably building against the
spec's codes, (b) is the safer default — flag for confirmation before a bulk
rename.

### S3. Response bodies leak snake_case instead of camelCase (HIGH, most routes)

Request bodies in `target_*.py` correctly alias camelCase → snake_case via
Pydantic (`Field(alias=...)`). Responses do the opposite of what's needed:
most routes just pass the legacy handler's raw dict straight into
`success_payload()` with no field renaming, so responses leak the DB/legacy
naming instead of the camelCase spec expects.

Confirmed snake_case leaks: round create/detail (`semester_id`, `reviewer_count`,
`result_owner_mode`, `session_duration_minutes`, `start_date`, `end_date`,
`max_groups_per_timeslot`, `group_preference_deadline`), invitation respond
(`round_id`, `lecturer_id`, `response`), availability submit (`round_id`,
`lecturer_id`, `selected_count`, `total_slots`, `source`), group preference
(`round_id`, `group_id`, `selected_count`, `total_slots`, `source`), room
assign (`session_id`, `room_id`, `changed`, `start_at`, `end_at`), suggest/apply
rooms, set-active schedule (`version_id`, `status`), result submit
(`session_id`, `outcome`, `group_status`), and the entire GET Groups listing
(§41, see below).

Also DB integer primary keys are returned raw instead of the external
prefixed-id format (`rnd_…`, `sv_…`, `grp_…`) used consistently elsewhere in
the same target-contract layer — inconsistent within the same file in several
cases (e.g. `target_round_contract.py`'s create-round response vs its
invitation response).

**Fix shape:** a single camelCase-conversion helper applied at the
`success_payload()` boundary (or a dict → alias-model round-trip) would fix
most of these in one pass, rather than patching each handler's SQL/dict
individually.

---

## Section-by-section findings

### PHẦN VII — Group APIs (§41–45), `target_group_project.py`

- **§41 GET Groups — HIGH.** Response is raw SQL columns
  (`active_member_count`, `leader_count`, `project_code`, `title`), not the
  spec's `memberCount`, nested `leader:{id,code,fullName}`,
  `project:{id,code,name,status}`, `warnings:[]`. `warning` query param
  accepted but unused. `page`/`pageSize` accepted but no `LIMIT`/`OFFSET`
  applied — `meta.total` is just the post-filter array length, not a true
  independent total. `target_group_project.py:85-119`, `_target_row` helper at
  `:70-77` only prefixes id fields, never restructures.
- **§42 POST Group — HIGH.** Envelope/aliasing correct, but "semester exists",
  "student enrolled in semester", "student not already active in another
  group this semester" are never checked. Group-code uniqueness only scopes
  `WHERE project_id IS NULL`, not per-semester. `STUDENT_NOT_ENROLLED`,
  `STUDENT_ALREADY_IN_GROUP`, `LEADER_NOT_ACTIVE_MEMBER` never raised.
  `target_group_project.py:122-137`.
- **§43 Change Leader — HIGH.** Reuses legacy `LeaderPayload{student_id, reason}`
  with no camelCase alias and no external-id parsing — spec body
  `{"leaderId":"stu_02","reason":...}` will fail Pydantic validation outright.
  Response also unwrapped snake_case with raw ints.
  `target_group_project.py:159-161`, `master_data.py:287-289,735-751`.
- **§44 Member Left — HIGH.** `DropoutPayload` has no `effectiveDate` field
  (spec requires it); `left_at` hardcoded to `now()` regardless. Separately,
  `target_leave_group` passes the URL's `membership_id` into
  `approve_dropout`'s `student_id` parameter — an id-space bug since the
  spec's path uses a membership id, not a student id.
  `target_group_project.py:164-166`, `master_data.py:283-284,717-732`.
- **§45 Assign Project — HIGH.** `projectId` aliasing correct, but "Group !=
  DISBANDED" / "Project != CANCELLED" checks and the Group/Project status
  state machine (FORMED→ASSIGNED, DRAFT→ACTIVE) are entirely unimplemented —
  only `code`/`project_id` columns are written. Response bypasses `_target_row`
  (raw ints/snake_case), inconsistent with sibling endpoints.
  `target_group_project.py:169-171`, `manager_extensions.py:88-92,357-405`.

### PHẦN VIII — Project APIs (§46–48)

- **§46 GET Projects — HIGH, route missing.** No target-shaped route exists
  anywhere. `api_contract.py:120` declares the operation but it's
  unimplemented; only the legacy `master_data.py:447-451` handler exists
  (bare array, no envelope, no `search/status/supervisorId/hasGroup/page/pageSize`
  filtering).
- **§47 POST Project — HIGH.** Request aliasing and main/co-supervisor
  distinctness check are correct, but "code unique" / "lecturer valid" aren't
  checked in application code — violations surface as an unhandled raw
  `IntegrityError`, not the documented error envelope. Also silently defaults
  `major_id` via `SELECT id FROM majors ORDER BY id LIMIT 1` — an undocumented
  behavior that mis-tags projects whenever more than one major exists.
  `target_group_project.py:174-193`.
- **§48 Eligibility — HIGH.** Route path matches (`target_round_contract.py:205-218`)
  but response is a raw project list — none of `projectId`, `groupId`,
  `eligible`, `checks{...}`, `blockingReasons`, `warnings` exist. None of the
  four blocking conditions or the member-count warning are evaluated.

### PHẦN IX — Round APIs (§49–52), `target_round_contract.py`

- **§49 Create Round — HIGH.** Request fields all correctly aliased and
  validated. Response is the raw snake_case dict from `create_round_with_days`
  — violates camelCase convention (see S3). LOW: undocumented `le=480` cap on
  `durationMinutes` not in spec. `target_round_contract.py:198-202`, request
  model `:91-150`.
- **§50 Round Detail — HIGH, route missing.** `GET /rounds/{roundId}` doesn't
  exist in any `target_*.py` file (confirmed by repo-wide grep).
- **§51/§52 Open/Close Registration — HIGH.** Wrong-state transitions raise
  `ROUND_TRANSITION_NOT_ALLOWED`, not spec's `ROUND_INVALID_STATE` (see S2).
  MEDIUM: the "has Timeslot / valid config / RoomType configured" completeness
  checks only run on transition into `SCHEDULING`, not on
  `OPEN_REGISTRATION` as the spec's validation list implies.
  `target_round_contract.py:256-263`.

### PHẦN X — Invitation / Availability (§53–56)

- **§53 Invite Lecturers — LOW.** Request/status correct. Invalid-lecturer
  error uses `INVITATION_RESOURCE_INVALID`, not in the spec's code list.
- **§54 Lecturer Respond — HIGH.** Request matches spec exactly. Response is
  snake_case (S3). MEDIUM: actual failure codes are
  `INVITATION_RESPONSE_INVALID` / `INVITATION_REASON_REQUIRED` /
  `INVITATION_DEADLINE_PASSED`, none on the approved list.
- **§55 Availability — MEDIUM/HIGH.** Request matches spec exactly
  (`preferredLoad`, `slots[]`). MEDIUM: route hard-rejects STUDENT (403), but
  `api_contract.py:131` declares this operation's allowed roles as
  `(LECTURER, STUDENT)` — internal contract inconsistency. LOW: spec's
  "ACCEPTED + no availability submitted → BUSY ALL" default has no
  implementation anywhere. HIGH: response is snake_case (S3).
- **§56 Group Preference — HIGH.** Request matches spec exactly. MEDIUM: spec
  requires "Round OPEN_REGISTRATION" as a gate; `submit_group_availability`
  never checks round status. HIGH: response is snake_case (S3).

### PHẦN XI — Scheduling Algorithm (§57–64), `target_schedule_contract.py`

(§59–61 Solver input/Pre-filter/Solver are internal mechanics, no HTTP
surface — not applicable to this audit.)

- **§57 Readiness — HIGH.** Not in `target_schedule_contract.py` at all —
  implemented in `target_round_contract.py:227-247` instead, and its shape is
  wrong: returns `{ready, blockers:[...], id, status, groups, timeslots,
  accepted_invitations}` instead of spec's `{ready, counts:{eligibleProjects,
  availableLecturers, timeslots}, blockingIssues:[...], warnings:[...]}`. No
  `counts` object, no `warnings` field at all.
- **§58 Generate — HIGH.** `run_scheduler`'s return dict has no
  `version_number` or `overall_score` keys. `versionNumber` falls back to the
  raw DB PK (wrong value vs spec's sequential per-round number).
  `overallScore` falls back to `soft_scores.get("overall", 0)` but soft-score
  keys are `S1`..`S9`, never `"overall"` — **always 0** even though the real
  solver objective is computed and just never returned. `scores` returns raw
  `{S1..S9}` instead of spec's `{workload, continuity, compactness}` — wrong
  keys entirely. `unscheduled[].code` uses a different reason-code vocabulary
  (`NO_REVIEWER_AVAILABILITY`, `H1_CONFLICT`, etc.) than spec's
  `UnscheduledReason` enum (`NO_VALID_TIMESLOT`,
  `NO_ENOUGH_ELIGIBLE_REVIEWERS`, etc.). `target_schedule_contract.py:34-46`.
- **§62/§63 Partial Solution / Save ScheduleVersion — OK** behaviorally
  (DRAFT saves without materializing Sessions, matches spec) — only the
  reason-code vocabulary issue above applies.
- **§64 Set Active — MEDIUM.** Transaction semantics correct. Response is the
  raw legacy `{"version_id": int, "status": "ACTIVE"}` — snake_case, raw PK
  instead of `sv_`-prefixed id used elsewhere in this same file.
  `target_schedule_contract.py:59-61`.
- **Error codes — HIGH.** `SCHEDULER_NOT_READY` and `ROUND_INVALID_STATE` are
  never raised anywhere; actual codes are `ROUND_INPUTS_INCOMPLETE`,
  `SCHEDULE_RERUN_FORBIDDEN`, `ROUND_POSTPONED`.

### PHẦN XII — Room Assignment (§65–68), `target_room_publish.py`

- **§65 Available Rooms — mostly OK.** Path/params correct. LOW: response
  rows leak `room_type` instead of `roomType`.
- **§66 Assign Room — MEDIUM.** Request `roomId` aliases correctly. Response
  is raw snake_case (`session_id`, `room_id`, `changed`, `start_at`, `end_at`).
- **§67/§68 Suggest/Apply Suggestions — MEDIUM.** Paths correct; response
  bodies (`suggestions`, `assignments`) are snake_case internally.

### PHẦN XIII — Publish (§69–70)

- **§69 Publish Readiness — HIGH.** Only checks room/type/conflict. Spec also
  requires `allSessionsHaveTimeslot` and `allSessionsHaveCouncil` — these
  checks exist but only run inside `publish_schedule` itself
  (`schedule_operations.py:1486-1501`, `MATERIALIZATION_INCOMPLETE`), never
  surfaced via the readiness endpoint. FE can see `ready: true` and still hit
  a publish failure. `target_room_publish.py:107-121`.
- **§70 Publish — MEDIUM/HIGH.** Requires body `{"versionId": ...}`
  (`PublishTargetPayload`), but spec shows no request body — publish is
  expected to act implicitly on the round's current active version (consistent
  with §69's readiness auto-resolving the ACTIVE version). Extra required
  field not in spec. `target_room_publish.py:124-126`.
- **Error codes — MEDIUM.** `ROOM_INACTIVE` used instead of spec's
  `ROOM_NOT_ACTIVE`; `ROOM_ASSIGNMENT_STATE_INVALID` used instead of spec's
  `SESSION_INVALID_STATE`.

### PHẦN XIV — Post-publish (§71–73), `target_operations.py` (not `target_room_publish.py`)

- **§71 Change Room — HIGH.** `ChangeRoomPayload` declares `room_id: int` with
  **no alias / no `populate_by_name`** — spec's `{"roomId": ..., "reason": ...}`
  body will 422 with a missing-field error. Response (`change_kind`,
  `schedule_version_id`, `replacement_version_id`, `before_council_id`,
  `after_council_id`, …) bears no resemblance to any spec-described shape.
  `target_operations.py:27-29,46-50`.
- **§72 Replace Reviewer — HIGH.** Spec body is a single swap
  `{"oldLecturerId", "newLecturerId", "reason"}`. Actual
  `ReplaceReviewerPayload` is `{"reviewer_ids": [...], "result_owner_id": ...,
  "reason": ...}` — a full council-replacement list, no old/new fields, no
  alias for the snake_case names either. Because the shape doesn't match, none
  of the five spec-mandated reviewer-conflict codes (`REVIEWER_NOT_AVAILABLE`,
  `REVIEWER_IS_SUPERVISOR`, `REVIEWER_COI`, `REVIEWER_TIME_CONFLICT`,
  `REVIEWER_QUOTA_EXCEEDED`) are ever raised — only a generic
  `REVIEWER_OVERLAP`. `target_operations.py:32-35,53-57`.
- **§73 Postpone — MEDIUM.** Path/request correct
  (`POST /sessions/{id}/actions/postpone` → legacy `postpone_session`). Failure
  code is `SESSION_NOT_POSTPONABLE`, not spec's `SESSION_INVALID_STATE`.
  `target_operations.py:60-62`.
- **Make-up session (`POST /sessions/{id}/makeup`) — MEDIUM.** Declared in
  `api_contract.py:155` but only implemented as the legacy route directly
  (`schedule_operations.py:1245`, path matches spec, functionally reachable)
  with no camelCase adaptation layer and outside both `target_room_publish.py`
  and `target_operations.py`. Errors used (`MAKEUP_ALREADY_EXISTS`,
  `SESSION_OUT_OF_SCOPE`, `SESSION_NOT_POSTPONED`) aren't in the spec list.

### PHẦN XV — Result & Progression (§74–76), `target_results_remediation.py`

- **§74 Submit Result — HIGH (error codes only).** Request fields
  (`result`, `note`, `remediation.deadline`, `remediation.verifierId`) match
  spec exactly. But permission failures raise a plain
  `HTTPException(403, detail="...")` with **no `code` field at all** (spec
  wants `RESULT_PERMISSION_DENIED`); invalid-outcome failures raise
  `OUTCOME_NOT_ALLOWED` (spec wants `RESULT_TYPE_INVALID`); missing
  LEVEL_2 fields raise `REMEDIATION_FIELDS_REQUIRED` (spec wants
  `REMEDIATION_REQUIRED_FIELDS_MISSING`). `results.py:37,193,212`,
  `app/domain/result_workflow.py:14,20`.
- **§75 Project Progression — OK.** Not a standalone route; transition logic
  (`transition_group`, `results.py:287-289`) invoked from result-submit. No
  divergence found.
- **§76 Remediation Verify — MEDIUM.** Route exists
  (`target_results_remediation.py:43-45`). Spec text only describes the
  PASSED outcome; the implementation also supports FAILED
  (`decision` pattern `^(PASSED|FAILED)$`) — undocumented but not wrong. Uses
  `REMEDIATION_VERIFIER_REQUIRED`, `REMEDIATION_ALREADY_DECIDED`,
  `REMEDIATION_NOT_FOUND` — none are in the canonical spec list.

---

## Suggested fix order

1. **S1 (error envelope)** — one exception handler in `app/main.py`, fixes
   every error response app-wide in one change.
2. **S2 (error codes)** — needs a decision first (rename code vs rename spec);
   once decided, it's a mechanical find/replace per the table above.
3. **S3 (camelCase responses)** — a shared response-shaping helper at the
   `success_payload()` boundary, then apply per route.
4. **Missing routes**: §46 `GET /projects` (target-shaped), §50
   `GET /rounds/{roundId}`.
5. **Broken request shapes**: §71 Change Room (`room_id` alias), §72 Replace
   Reviewer (needs a genuine design decision — single swap vs council list;
   flag to product/FE before implementing either way).
6. **Missing business validations**: §42, §45, §48 group/project eligibility
   checks — currently silent no-ops.
7. **§58 Generate response values** (`versionNumber`, `overallScore`,
   `scores`) — wrong data reaching FE today, not just wrong shape.
8. Remaining MEDIUM/LOW items (readiness `counts`/`warnings` shape, publish
   request body, minor snake_case leaks in room routes) as capacity allows.
