# Spec: Reset seed data — new demo accounts + room types

**Date:** 2026-08-19
**Status:** Draft

---

## Problem Statement

The current seed data (296 students, 26 lecturers, 74 groups, 4 admin/manager accounts, rooms with no type) is oversized noise for day-to-day dev/demo work and is spread across three conflicting sources (fixture, Excel import, two ad-hoc scripts) that fight each other on every bootstrap. We need one small, predictable demo dataset — 8 named accounts and 6 typed rooms — seeded from a single source so a fresh environment is fast to reason about and matches what manual testing actually needs.

---

## User Stories

- **[P1]** As a developer resetting a local/Docker environment, I want `docker compose up --build` (or `POST /admin/seed-fixture`) to produce exactly the 8 demo accounts and 6 rooms below, with no leftover 26-lecturer/296-student data, so that I can log in and test without wading through unrelated fixture noise.
  Accepted when: after a clean `docker compose down -v && docker compose up --build`, querying `accounts` returns exactly the 8 seeded rows and `rooms` returns exactly 6 rows across the 3 types — nothing else.

- **[P1]** As any role (admin/manager/lecturer/student), I want to log in with my role's fixed email and the shared password `12345@Abc`, so that manual testing across roles is fast and consistent.
  Accepted when: `POST /auth/login` succeeds for `admin@gmail.com`, `manager@gmail.com`, `lecturer@gmail.com`, `student1@gmail.com`…`student5@gmail.com`, all with password `12345@Abc`.

- **[P1]** As a developer working on room/round scheduling, I want rooms to carry a `room_type` of `NORMAL`, `SEMINAR`, or `LAB`, so that future round/scheduler work (per `docs/capstone-fe-be-implementation-spec.md`) has real typed room data to build against.
  Accepted when: `rooms` table has a `room_type` column populated with exactly 2 `NORMAL`, 2 `SEMINAR`, 2 `LAB` rows, capacity 12 each; the column is enforced (enum or CHECK) so invalid values are rejected.

- **[P2]** As a maintainer, I want only one seed source in the repo, so that future changes don't need to be made in three places.
  Accepted when: `tools/import_excel_database.py` no longer runs as part of `tools/bootstrap_database.py` (or is otherwise neutralized), and `apps/api/scripts/seed_accounts.py` / `apps/api/scripts/seed_student1_full.py` are removed.

- **[P3]** _(out of scope — future)_ Seeding a demo semester/major/group/project/round around the new accounts, once the minimal account+room reset is validated.

---

## Functional Requirements

1. FR-01: `app/domain/seed.py` (`seed_fixture_v1` or equivalent) is rewritten to produce exactly 8 accounts: `admin@gmail.com` (ADMIN), `manager@gmail.com` (MANAGER), `lecturer@gmail.com` (LECTURER), `student1@gmail.com`..`student5@gmail.com` (STUDENT) — no `admin2`/`manager2`/`lecturer2`/paired accounts.
2. FR-02: All 8 accounts share the same password `12345@Abc`, stored as an argon2id hash consistent with `auth_routes.py`'s `PasswordHasher().verify(...)` check.
3. FR-03: The fixture no longer creates majors, semesters, groups, projects, or rounds — accounts and rooms only.
4. FR-04: A new Alembic migration adds a `room_type` column to `rooms` (values `NORMAL`/`SEMINAR`/`LAB`), enforced via native Postgres enum or `VARCHAR` + `CHECK` constraint (decide during planning based on this repo's existing migration conventions).
5. FR-05: The fixture seeds exactly 6 rooms: 2 each of `NORMAL`, `SEMINAR`, `LAB`, capacity 12.
6. FR-06: `tools/bootstrap_database.py` is updated so the Excel import step (`tools/import_excel_database.py`) no longer runs on container start — the new fixture becomes the sole seed path for a fresh DB.
7. FR-07: `apps/api/scripts/seed_accounts.py` and `apps/api/scripts/seed_student1_full.py` are deleted.
8. FR-08: `POST /admin/seed-fixture` continues to work against the rewritten fixture (idempotent upsert behavior preserved) — no route signature changes required.
9. FR-09: Tests that hardcode the old fixture shape (`apps/api/tests/test_seed_fixture.py`, `apps/api/tests/test_auth_api.py`, and any others surfaced by running the suite) are updated to assert the new 8-account/6-room shape.

---

## Non-Functional Requirements

- Performance: fixture load completes in well under 1s (trivial compared to today's 74-group/296-student load) — not a concern, just shouldn't regress.
- Security: password hash for the shared demo password must use the same argon2id parameters/verification path as production login (`app/routes/auth_routes.py`) — no plaintext storage, no weakened hash params for "just seed data."
- Consistency: exactly one code path in the repo may create seed accounts/rooms after this change (the rewritten fixture) — no duplicate/competing seed logic.

---

## Success Criteria

- [ ] Fresh `docker compose down -v && docker compose up --build` leaves exactly 8 rows in `accounts` and exactly 6 rows in `rooms` (2 per `room_type`).
- [ ] `POST /auth/login` succeeds for all 8 seeded emails with password `12345@Abc`.
- [ ] `POST /api/v1/admin/seed-fixture` re-run against an already-seeded DB is idempotent (no duplicate rows, no errors).
- [ ] `uv run pytest -m "not integration" -q` and the full Docker-backed suite (`docker compose exec -T api pytest -q`) pass with the updated fixture-shape tests.
- [ ] `ruff check app tests` passes after removing the two deleted scripts and any now-dead imports.

---

## Out of Scope

- Seeding any semester/major/group/project/round data (deferred to P3 above).
- Changing the scheduler (`app/scheduler/*`) to filter candidate rooms by `room_type` — this spec only adds the column/enum and seed values, not the scheduling logic consuming it (tracked in `docs/capstone-fe-be-implementation-spec.md` separately).
- Renaming or restructuring the Excel import tool itself — it is only removed from the bootstrap invocation, not deleted, in case it's still wanted for a future one-time real-data import.

---

## Assumptions

- No other code path (dashboards, reports, notification dispatcher) hard-requires at least one existing group/project/round to function without erroring — if wrong, this spec's "accounts + rooms only" minimal scope needs revisiting to add a smoke-test pass in `/ck:plan`.
- The existing `argon2-cffi` verify path in `auth_routes.py` accepts any valid argon2id hash regardless of which params generated it, so the new fixture can compute its own hash for `12345@Abc` rather than reusing the old `DEMO_PASSWORD_HASH` constant.
- `tools/import_excel_database.py` is safe to stop invoking from bootstrap without deleting the file or its bundled workbook reference, since no other automated path depends on it.

---

## [NEEDS CLARIFICATION]

- [ ] Native Postgres `ENUM` type vs. `VARCHAR` + `CHECK` constraint for `room_type` — check existing migration conventions in `apps/api/migrations/versions/` during `/ck:plan` before deciding.
- [ ] Whether any downstream endpoint (dashboard/report/notification) 500s or degrades ungracefully when there are zero groups/projects/rounds in the DB — needs a quick grep/smoke pass during planning since this spec seeds none.
