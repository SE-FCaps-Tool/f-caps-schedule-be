# Brainstorm: Reset seed data — new demo accounts + room types

**Date:** 2026-08-19

## Ideas Explored

- **Rewrite `seed_loader.py`/`domain/seed.py` from scratch** (chosen) — replace the fixture entirely with the new minimal dataset, instead of patching values inside the existing fixture or writing a one-time DB-cleanup migration on top of the old fixture.
- **Patch the existing fixture in place** — keep the 74-group/296-student/26-lecturer structure and just add the requested accounts alongside it. Rejected: user explicitly wants old seed data gone, not layered on top.
- **One-time cleanup migration + keep old fixture code** — write an Alembic migration to wipe existing rows in a running DB. Rejected as the primary path since this repo's actual "old seed" source is the Excel bootstrap import (which already TRUNCATEs the DB on every fresh container start), not stale rows sitting in a persistent DB — the real fix is at the seed-source level, not a one-off cleanup script.

## User's Direction

Scout of the codebase surfaced that seed data currently comes from **three independent, overlapping sources**:
1. `app/services/seed_loader.py` + `app/domain/seed.py` (`seed_fixture_v1`, `FIXTURE_VERSION = "seed-v1"`) — used by both `POST /admin/seed-fixture` and the Docker bootstrap.
2. `tools/import_excel_database.py` — runs on every container start via `tools/bootstrap_database.py`, **TRUNCATEs the entire `public` schema** and rebuilds from the bundled Excel workbook (hardcodes the same `admin1/2`, `manager1/2` emails, imports 26 lecturers + 2 students from the workbook, rooms with capacity hardcoded to `999` and no type).
3. Two standalone scripts, `apps/api/scripts/seed_accounts.py` and `apps/api/scripts/seed_student1_full.py`, which create their own overlapping demo accounts/scenario data.

User confirmed the full-reset direction: rewrite the fixture as the **single source of seed truth**, disable the Excel import from bootstrap (or gate it off), and delete the two redundant scripts — so nothing else can reintroduce old accounts on a fresh `docker compose up`.

New dataset, replacing the old 296-student/26-lecturer/74-group structure:
- **Accounts (8 total, single account per non-student role):** `admin@gmail.com` (ADMIN), `manager@gmail.com` (MANAGER), `lecturer@gmail.com` (LECTURER), `student1@gmail.com`…`student5@gmail.com` (STUDENT). All share password `12345@Abc`, hashed with the existing `argon2-cffi` scheme (`accounts.password_hash`).
- **Scope kept minimal:** accounts + rooms only. No semester/major/group/project/round seeding — those get created through the API against the new accounts, not pre-seeded. (Existing groups/projects seeding logic in `seed.py` goes away entirely with the rewrite.)
- **Rooms:** new `room_type` concept (`NORMAL` / `SEMINAR` / `LAB`, from the not-yet-implemented `RoomType` enum already sketched in `docs/capstone-fe-be-implementation-spec.md`) — 2 rooms per type, capacity 12 each, 6 rooms total. This requires a **new Alembic migration** adding a `room_type` column to `rooms` (table currently has no type column or enum at all — confirmed via full grep, this is net-new, not a rename).

## Open Questions

- Should `room_type` be a Postgres native `ENUM` or a `VARCHAR` + `CHECK` constraint? (Repo convention elsewhere uses plain columns + app-level validation more often than native enums — worth checking migration style before deciding in `/ck:plan`.)
- `test_seed_fixture.py` (hard-asserts 26 lecturers/4 rooms/74 groups/296 students/specific emails) and `test_auth_api.py` (logs in as `manager1@gmail.com`) will both need rewriting to match the new fixture shape — not covered by this brainstorm, left for `/ck:plan`.
- Whether any other code path assumes a `lecturers`/`projects` row exists per LECTURER account (e.g. supervisor assignment) — not exercised by the minimal accounts+rooms scope, but worth a grep pass during planning in case something downstream 500s on an empty academic dataset.

## Risks

- **Bootstrap coupling**: `tools/bootstrap_database.py` currently always runs the Excel import step before the fixture; disabling/gating it needs care so a fresh `docker compose up -v` still ends with a fully migrated, minimally-seeded DB and doesn't silently skip seeding.
- **Test breakage**: the fixture rewrite is a hard breaking change for any test hardcoding old emails/counts (`test_seed_fixture.py`, `test_auth_api.py`, possibly others found only at implementation time).
- **Downstream assumptions**: reducing from 26 lecturers/74 groups to 1 lecturer/0 groups may expose code that assumed at least one project/group/round exists (dashboards, reports) — worth a quick smoke test after reseeding, not just unit tests.
