# Spec: Backend Repository Extraction

**Date:** 2026-08-18  
**Status:** Ready — owner scope confirmed

## Problem statement

Backend hiện nằm chung với FE trong `W:\Capstone Defense Scheduler`. Cần tạo
`W:\f-caps-schedule-be` bằng cách sao chép nguyên trạng toàn bộ backend,
tài liệu, migration, tool, worker legacy, cấu hình và dữ liệu backend hiện có.
Phạm vi duy nhất của extraction là loại bỏ FE; không refactor, không flatten,
không sửa dependency, không sửa API hoặc business behavior.

## Scope rule

Được phép khác source duy nhất ở các điểm sau:

1. Không copy `apps/web/**`.
2. Không copy `infra/docker/web.Dockerfile` và các FE-only artifact như
   `erd-viewer.html`.
3. Xóa service `web` khỏi target `docker-compose.yml`; giữ nguyên định nghĩa
   `postgres`, `api`, `worker` và các giá trị backend còn lại.
4. Database được logical dump/restore sang volume riêng của target để không
   dùng chung hoặc ghi vào source volume. Logical data, schema và migration
   state phải giống source. Chỉ sau khi target parity đạt, container backend
   cũ được gỡ và source volume được xóa theo cutover đã xác nhận; dump vẫn
   được giữ lại bên ngoài repository để rollback.

Mọi file backend còn lại phải được copy nguyên trạng. Không sanitize tài liệu,
không sửa `README`, PRD, BusinessRules, ERD, plans, `.env.example`,
`schema.sql`, Dockerfile, importer, legacy worker hoặc dependency metadata.
Các text reference tới FE trong tài liệu không được xem là active FE runtime
coupling.

Các file do quá trình lập kế hoạch tạo trong target (`plans/backend-repo-extraction/**`,
`plans/260818-backend-repo-extraction/**`, `plans/reports/260818-backend-repo-extraction-brainstorm.md`,
`plans/.current-brainstorm.md` và target `feature_list.json`) là plan-owned/generated
metadata, không thuộc source parity allowlist và không được tính là source drift.

## User stories

- **[P1]** As a backend developer, I want to run the copied backend without the
  FE source or Compose service.
  Accepted when target không có FE source/FE Dockerfile/`web` Compose service,
  và Compose còn đúng `postgres`, `api`, `worker`.

- **[P1]** As a maintainer, I want backend source and project artifacts to stay
  byte-equivalent to the source snapshot.
  Accepted when hashes match for the backend allowlist; only the explicitly
  allowed FE removals and removal of the `web` Compose block differ.

- **[P1]** As a data owner, I want the current Excel-imported database to be
  available to the target backend without mutating it before parity/cutover.
  Accepted when a dump/restore into a new target volume preserves schema head,
  row counts, deterministic business keys and all `excel_*` data.

- **[P2]** As a maintainer, I want the existing backend documentation and
  commands copied without rewriting their content.
  Accepted when backend docs/config/spec files are present and hash-equivalent;
  FE mentions in non-runtime text may remain.

- **[P3]** Replacement FE repository is out of scope.

## Functional requirements

1. **FR-01:** Create `W:\f-caps-schedule-be` without modifying or deleting any
   source file. The old Docker backend containers and old database volume may
   be removed only after target parity, health and cutover gates pass.
2. **FR-02:** Preserve `apps/api/app` as-is. Do not flatten it to root-level
   `app`.
3. **FR-03:** Preserve `apps/api/migrations`, `apps/api/tests`, `alembic.ini`,
   `pyproject.toml` and `uv.lock` as-is.
4. **FR-04:** Preserve `apps/worker/**` as-is, including the legacy worker;
   do not change which worker the existing Compose command runs.
5. **FR-05:** Preserve `tools/import_excel_database.py` as-is. Do not run it as
   part of extraction.
6. **FR-06:** Copy all intentional backend docs, plans, specs, `.env.example`,
   `.dockerignore`, `.gitignore`, `schema.sql`, `tools/**`,
   `infra/docker/api.Dockerfile` and root project metadata as-is. The target
   root `feature_list.json` is plan-owned extraction metadata, not runtime
   backend source.
7. **FR-07:** Remove only FE source/artifacts and the `web` service from the
   target Compose file. Do not rewrite API Dockerfile paths or dependencies.
8. **FR-08:** Restore the current database into a new target volume named
   `f_caps_schedule_be_postgres_data`; never bind the source volume directly.
9. **FR-09:** Preserve Alembic head `0012_excel_import_data`, current round
   types, canonical tables, session reviewer data and every `excel_*` table.
10. **FR-10:** Preserve API routes, JSON contracts, auth/session, CSRF,
    scheduler, result workflow, notification and worker behavior by source-file
    parity. This extraction does not repair pre-existing backend issues.
11. **FR-11:** Preserve all existing environment/config values as source files;
    do not introduce a new env contract in this extraction.
12. **FR-12:** Do not run importer, seed fixture, write tests or destructive
    commands against the official source database.

## Non-functional requirements

- **Source parity:** backend allowlist hashes match source, excluding only the
  documented Compose/FE removals and the plan-owned/generated metadata listed above.
- **Runtime isolation:** target Compose has no FE service, FE build context or
  FE container dependency.
- **Database isolation:** source and target use different PostgreSQL containers
  and volumes.
- **Data integrity:** target counts and deterministic key sets match source.
- **Recovery:** source files remain untouched; a verified dump is retained
  before target restore and before removing the old database volume.

## Success criteria

- [ ] Target contains the complete backend allowlist and no `apps/web`, FE
      Dockerfile or FE-only artifact.
- [ ] `docker compose config --services` in target returns exactly
      `postgres`, `api`, `worker`.
- [ ] Resolved target volume is exactly `f_caps_schedule_be_postgres_data` and
      is different from `capstonedefensescheduler_postgres_data`.
- [ ] Hash comparison passes for all copied backend files; the only expected
      source-content diff is removal of the Compose `web` block. Plan-owned/
      generated metadata is reported separately and excluded from source parity.
- [ ] Before cutover, source database health/counts/keys match the baseline; after
      cutover, old backend containers are removed, old volume is no longer used,
      and the verified dump remains outside the repository.
- [ ] Target database has Alembic head `0012_excel_import_data`, 131 projects,
      131 groups, 44 lecturers, 11 rooms, 5 rounds, 132 sessions and 264
      `session_reviewers`.
- [ ] Counts and deterministic key sets match for all current `excel_*` tables.
- [ ] No importer, seed fixture or write-test is executed against the source
      database.
- [ ] No claim is made that pre-existing Docker dependency/build issues are
      fixed; any such issue is reported separately because source parity is the
      requirement.

## Out of scope

- Writing or migrating the replacement FE.
- Flattening `apps/api` or refactoring the backend.
- Changing `pyproject.toml`, `uv.lock`, Dockerfile, importer, worker, docs,
  migrations, API contracts or business rules.
- Fixing the existing `httpx2`/`httpx` or `openpyxl` dependency issues.
- Running importer/seed/full write-test on the official database.
- Cloud deployment, CI/CD or production infrastructure.
- Deleting the source repository.

## Assumptions

- The source snapshot and current imported PostgreSQL database are authoritative.
- Target has its own Git metadata; source `.git` is not copied.
- Workbook may be copied as the unchanged importer input, but is never stored
  inside the database as a binary/blob.
- Generated caches, virtual environments, secrets and temporary lock files are
  not project artifacts and are not copied.
- Alembic migrations remain the operational schema source of truth.

## [NEEDS CLARIFICATION]

<!-- Owner confirmed the exact-copy-except-FE scope on 2026-08-18. -->


