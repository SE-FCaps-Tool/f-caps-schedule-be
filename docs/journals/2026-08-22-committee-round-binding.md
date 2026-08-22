## 2026-08-22 — Committee (BHĐ) bound to Round, schema + API only

- Decision / outcome: Added the missing half of "gán timeframe với BHĐ vào
  round_id". Timeframe↔Round already existed; Committee was a standalone
  catalog with no Round linkage. Chose a many-to-many `round_committees` join
  table (migration `0036_round_committees`) over a `rounds.committee_id`
  column, because the Committee catalog is explicitly reusable across Rounds
  and a Round needs a pool the scheduler can choose from. `PUT`/`GET
  /rounds/{id}/committees` ship replace-all semantics (no PATCH), matching the
  existing Committee CRUD style. Assignment is gated to
  `DRAFT`/`OPEN_REGISTRATION` — the same window `timeframe_id` already uses, so
  FE disables both with one condition.

  Three guard decisions worth remembering:
  - `committee_id` FK is `ON DELETE RESTRICT`, and the app-level guard turns it
    into `409 COMMITTEE_IN_USE`. The read-then-delete pre-check is only a fast
    path; the `except IntegrityError` around the DELETE is the real protection
    against a Round assignment landing between the two statements.
  - That handler classifies **only**
    `fk_round_committees_committee_id` violations as in-use and re-raises
    everything else, so an unrelated constraint failure can never be reported
    as a friendly `200` partial success.
  - `bulk_delete_committees` deletes per id inside a `SAVEPOINT`, so one
    contended id degrades to `inUseIds` instead of aborting the whole batch.

  Scheduler integration (Phase 3) was deferred at first, then picked up and
  completed the same day — see the second entry below.

- Evidence: `alembic upgrade head` → `0036_round_committees`, verified table
  shape and both FK constraint names via `\d round_committees`; downgrade →
  table absent, re-upgrade → table present. `tests/test_round_committee_api.py`
  14/14 pass. Full-suite failure list diffed against a stashed baseline: the
  only delta is `test_round_detail_contract` going from failing to passing; the
  two `test_phase03_api` semester failures were reproduced identically with the
  changes stashed (DB has no ACTIVE semester — pre-existing state flakiness,
  not a regression). `ruff check` clean on every new file.

- Follow-up:
  - Fixed a pre-existing drift while getting the contract test green:
    `PATCH /rounds/{id}` lacked `response_model_exclude_none=True` while `GET`
    had it, so the two returned different shapes for the same resource.
  - Unexplained: `apps/api/app/services/timeframe_service.py` and two root
    `.xlsx` files were deleted from the working tree mid-session by something
    other than the edits above (the running api/worker containers are the
    likely cause via bootstrap). `timeframe_service.py` was restored from HEAD;
    the two `.xlsx` deletions are still unstaged and unreviewed.

## 2026-08-22 — Assigned Committees now constrain the scheduler

- Decision / outcome: Phase 3 landed, so a Round's assigned Committees are a
  real CP-SAT constraint rather than metadata. The critical design point is
  that the committee branch must **not** reuse
  `combinations(available, expected_reviewer_count)` — with Committees `(1,2)`
  and `(3,4)` and only 1 and 3 available at a slot, `combinations` emits
  `(1,3)`, a council belonging to no Committee. `candidates.py` now routes
  through `_reviewer_tuples`, which for a committee-bound Round tests each
  Committee's whole member set against the same per-slot `available` list the
  legacy path computes (after H1/H8, availability, and `DEFENSE_1` H11
  narrowing) and emits it all-or-nothing.

  Two states must stay distinguishable, hence two fields on `RoundInput`
  instead of one: `has_assigned_committees=False` means the legacy free-pool
  path (byte-for-byte unchanged), while `has_assigned_committees=True` with an
  empty `committee_reviewer_sets` means every assigned Committee was filtered
  out and the Round must produce **zero** candidates. Collapsing those two
  into one empty tuple would silently fall back to free-pool scheduling in
  exactly the case where the Committee constraint matters most.

  `_round_input` only ever **narrows**: a Committee is kept only when its whole
  member set is already a subset of the existing `accepted_reviewer_ids or
  available_reviewer_ids` pool. Nobody is ever added to `reviewers`, so
  assigning a Committee can never let an un-invited lecturer be scheduled, and
  `scheduler.py`'s per-reviewer constraint loop needed no change at all.

  Because a Committee is dropped silently when one member isn't eligible yet,
  `GET /rounds/{id}/scheduling-readiness` now reports
  `COMMITTEE_MEMBERS_NOT_ELIGIBLE` plus an `unusableCommittees` list naming the
  missing lecturers — otherwise "the Committee isn't fully invited" and
  "no feasible schedule exists" both surface as the same all-`UNSCHEDULED`
  result.

- Evidence: `tests/test_committee_candidates.py` 10/10, including a test
  proving the anti-mixing branch is meaningful (same fixture: the legacy path
  would emit `[(2, 4)]`, the committee-bound path emits `[]`).
  `tests/test_round_committee_api.py` 16/16, covering the DB-backed
  `_round_input` filter (one eligible member is still not enough) and the
  readiness blocker clearing once both members are `ACCEPTED`.
  `tests/test_benchmark.py` passes unmodified. Full suite: 28 failures,
  identical to the pre-Phase-3 baseline — all pre-existing seed-fixture and
  integration issues. `ruff check` reports nothing in any changed file.

- Follow-up: assigning a Committee still does not auto-invite its members to
  the Round. That is a product decision, not a technical gap — the readiness
  blocker exists so the manual step is at least visible.
