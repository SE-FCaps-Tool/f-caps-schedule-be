# Plan: Tách Backend thành Repository độc lập

Date: 2026-08-18
Directory: W:\f-caps-schedule-be\plans\260818-backend-repo-extraction
Mode: Hard
Risk: high-risk — copy allowlist, Docker Compose removal, PostgreSQL dump/restore và official database.
Test: default; cook khuyến nghị --hard --tdd nhưng write-capable tests chỉ chạy trên clone disposable.
Spec: spec.md in this directory (spec-driven mode)
Status: Complete

## Phase Status

- [x] Phase 00: Preflight, inventory và source snapshot
- [x] Phase 01: Copy exact backend artifacts
- [x] Phase 02: Minimal Compose target change
- [x] Phase 03: Restore database vào volume riêng
- [x] Phase 04: Read-only database parity
- [x] Phase 05: Target runtime validation
- [x] Phase 06: Final acceptance and rollback evidence
- [x] Phase 07: Cutover: remove old Docker backend and old database

## 1. Scope challenge và source-of-truth

- Source authoritative: W:\Capstone Defense Scheduler.
- Target: W:\f-caps-schedule-be.
- Mục tiêu là exact-copy backend/project artifacts, chỉ loại FE; không refactor, không flatten, không sửa dependency, docs, API, worker, importer, migration hay business behavior.
- Giữ nguyên apps/api layout, apps/worker, tools, docs, plans, specs, root metadata và workbook theo allowlist.
- Chỉ khác source ở: không copy apps/web, không copy FE Dockerfile/FE-only artifacts, xóa service web khỏi target Compose, và database target là logical clone trong volume riêng.
- Các lỗi pre-existing như httpx2/httpx hoặc thiếu openpyxl không được sửa; chỉ ghi nhận nếu validation chạm phải.

## 2. Exact-copy allowlist

Copy nguyên trạng và hash-equivalent:

- apps/api/** gồm app, migrations, tests, alembic.ini, pyproject.toml, uv.lock.
- apps/worker/** gồm cả legacy worker; không đổi Compose command.
- tools/** gồm import_excel_database.py; không chạy trong extraction.
- infra/docker/api.Dockerfile.
- Root docker-compose.yml sau khi chỉ xóa block web và FE-only references bắt buộc bởi block đó.
- Root metadata: .env.example, .dockerignore, .gitignore, schema.sql, README.md và source feature_list.json nếu có.
- Exact source documents: PRD_CapstoneScheduler_v1.0.md, BusinessRules_CapstoneScheduler_v1.0.md, ERD_CapstoneScheduler_v1.0.md, docs/**, plans/capstone-scheduler/**, plans/reports/** và workbook SE_CapstoneProject_SP26_ReviewDefense_New.xlsx.

Không copy apps/web/**, infra/docker/web.Dockerfile, erd-viewer.html và FE-only generated artifacts. Không copy source .git; target giữ Git metadata riêng. Không copy generated caches, virtual environments, secrets hoặc temporary lock files.

FE text references trong docs/plans được giữ nguyên; chỉ runtime Compose/Docker coupling được loại theo scope. Không sanitize hoặc rewrite docs.

Exclude from source hash parity, but do not delete, plan-owned target metadata: plans/backend-repo-extraction/**, plans/260818-backend-repo-extraction/**, plans/reports/260818-backend-repo-extraction-brainstorm.md, plans/.current-brainstorm.md and target feature_list.json.

## 3. Baseline và safety invariants

Alembic head phải là 0012_excel_import_data; source volume là capstonedefensescheduler_postgres_data.

Baseline read-only phải khớp:
projects=131, groups=131, lecturers=44, rooms=11, rounds=5, sessions=132, session_reviewers=264, excel_import_batches=1, excel_sheet_rows=354, excel_projects=131, excel_review_schedule_rows=132, excel_defense_councils=40, excel_council_groups=161, excel_summary_workloads=31.

Round types phải đúng REVIEW_1, REVIEW_2, REVIEW_3, DEFENSE_1_1, DEFENSE_2.

Safety rules:

- Không chạy docker compose down -v trên source trước khi target parity đạt.
- Không chạy importer, seed fixture, full write-test hoặc destructive SQL trên source database.
- Không dùng external true hoặc bind source volume trực tiếp cho target.
- Dump phải được giữ lại trước restore và trước cutover; source repo không được xóa/sửa. Source volume chỉ được xóa ở cutover phase sau khi mọi gate pass.
- Mọi lệnh Docker/pg_dump/pg_restore phải dừng khi container ID rỗng hoặc exit code khác 0.

## 4. TDD/testing strategy

1. Tạo inventory/hash checks trước khi copy.
2. Sau copy, kiểm tra path inventory và hash manifest; expected diff chỉ là FE removal và Compose web removal.
3. Validate target Compose model: đúng postgres, api, worker, không web.
4. Full tests chỉ chạy trên database clone/disposable, không chạy trên official source database.
5. Official source/target databases chỉ nhận read-only health, Alembic head, counts, round types và deterministic keys.
6. Không claim dependency/build issues đã được fix; nếu source parity khiến build fail, ghi evidence là pre-existing và dừng theo scope.

## 5. Phases

Execution files for ck-cook are phase-00 through phase-07 in this directory. The sections below remain the consolidated plan/source of truth.

### Phase 00 — Preflight, inventory và source snapshot

1. Xác nhận source/target paths; target chưa chứa backend copy nhầm.
2. Kiểm tra source Compose, postgres readiness và volume capstonedefensescheduler_postgres_data.
3. Tạo W:\f-caps-schedule-be-artifacts\source-backend-inventory.json và source-backend-hashes.json ngoài target. Inventory phân loại copy, exclude-fe, generated-not-copy.
4. Ghi W:\f-caps-schedule-be-artifacts\source-db-baseline.json bằng read-only queries.
5. Tạo custom dump trong source container, copy ra W:\f-caps-schedule-be-artifacts\db\source-20260818.dump, chạy pg_restore --list để validate, rồi xóa temporary dump trong source container. Mỗi lệnh phải kiểm tra container ID và exit code. Sau docker cp, tính SHA256 dump trên host và so với sha256sum của file trong source container trước khi xóa; mismatch là abort.

Expected: source healthy, exact baseline, readable custom archive, source unchanged.
Abort: health/baseline/hash/dump failure, empty ID hoặc source mutation.

### Phase 01 — Copy exact backend artifacts

Copy all allowlisted files byte-for-byte, preserving paths, including workbook. Không copy source .git, FE paths, generated caches, secrets hoặc local environments.

Verification:
- path inventory target có apps/api, apps/worker, tools, infra/docker/api.Dockerfile, docs, plans, specs, metadata và workbook;
- SHA256 hashes khớp source allowlist;
- FE source/FE Dockerfile không tồn tại;
- docs/plans có thể giữ text FE vì đây không phải runtime coupling.

Abort on any unapproved rewrite, missing artifact, copied FE artifact hoặc workbook bị thiếu.

### Phase 02 — Minimal Compose target change

Chỉ sửa target docker-compose.yml trong phạm vi spec: xóa web service/build context và FE-only configuration. Giữ nguyên postgres, api, worker, commands, Dockerfile path, environment values và backend mounts.

Target Compose project identity là f_caps_schedule_be và actual Docker volume phải là f_caps_schedule_be_postgres_data. Không dùng external true trỏ source volume.

Verification:
- docker compose -p f_caps_schedule_be -f W:\f-caps-schedule-be\docker-compose.yml config --services trả đúng postgres, api, worker;
- config model không có web, Vite, port 5173 hoặc FE build context;
- sau khi start target postgres, docker inspect chứng minh target mount f_caps_schedule_be_postgres_data;
- source mount vẫn là capstonedefensescheduler_postgres_data;
- source và target container IDs khác nhau.
- Khi source stack đang giữ host ports 5432/8000, dùng một Compose override tạm thời nằm ngoài target repo để map target-only host ports, ví dụ 55432/18000; không sửa source hoặc committed target Compose ports.

Abort on any backend Compose change ngoài web removal, source volume resolution, wrong service count hoặc wrong actual mount.

### Phase 03 — Restore database vào volume riêng

1. Start only target postgres and wait readiness.
2. Resolve source/target IDs; abort if empty/equal.
3. Inspect source mount and require capstonedefensescheduler_postgres_data; reject if source ID is empty.
4. Inspect target mount and require f_caps_schedule_be_postgres_data and absence of source volume; reject if target ID equals source ID.
5. Copy validated dump only to target.
6. In the same PowerShell block immediately before pg_restore, re-assert target ID and mount. Run pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges only in target; check exit code; remove target temporary dump.
7. Do not run importer or seed.

Abort before restore if identity/mount check fails or any command touches source container.

### Phase 04 — Read-only database parity

Use read-only source/target queries or a verifier outside runtime. Compare Alembic head, all baseline counts, exact round types, canonical deterministic keys for projects/groups/lecturers/rooms/rounds/sessions/session reviewers, and deterministic keys for every current excel_* table. Check no orphaned Excel links.

Verifier must reject write SQL and fail on mismatch. Recheck source/target IDs and actual volume names before queries. Source health/counts/keys after restore must equal the pre-extraction baseline.

### Phase 05 — Target runtime validation

Start target postgres, api and worker using copied Compose. Validate PostgreSQL readiness, API health, Alembic current, service logs and existing backend test commands only where they do not write official data.

Full write-capable pytest, if run, must use a unique database named scheduler_test_<UTC timestamp> created inside target PostgreSQL. Before creation, query pg_database and abort if that name exists; before pytest, run SELECT current_database(), compare it to the generated name, assert DATABASE_URL contains that name and assert it does not contain /scheduler. Cleanup may target only that generated name and only after evidence is captured. Never point it at official scheduler data. Do not use test output to claim dependency/build repairs; report source-parity failures separately.

Machine-checkable guard sequence:

    $testDb = 'scheduler_test_' + (Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmssfff')
    if ($testDb -notmatch '^scheduler_test_[0-9]{17}$') { throw 'Unsafe test database name' }
    $exists = docker exec $targetPostgres psql -U scheduler -d postgres -At -c "SELECT 1 FROM pg_database WHERE datname='$testDb'"
    if ($LASTEXITCODE -ne 0 -or $exists.Trim() -eq '1') { throw 'Test database already exists or query failed' }
    docker exec $targetPostgres psql -U scheduler -d postgres -c "CREATE DATABASE $testDb OWNER scheduler"
    if ($LASTEXITCODE -ne 0) { throw 'Test database creation failed' }
    $current = docker exec $targetPostgres psql -U scheduler -d $testDb -At -c 'SELECT current_database()'
    if ($LASTEXITCODE -ne 0 -or $current.Trim() -ne $testDb) { throw 'current_database guard failed' }
    $testUrl = "postgresql+psycopg://scheduler:scheduler@postgres:5432/$testDb"
    if ($testUrl -notmatch [regex]::Escape('/' + $testDb) -or $testUrl -match '/scheduler([/?]|$)') { throw 'DATABASE_URL guard failed' }
    # Run pytest with DATABASE_URL=$testUrl only; preserve evidence before dropping $testDb.

If pytest fails, preserve logs and do not run cleanup blindly; any cleanup command must use the same allowlisted $testDb value.

Validate runtime worker command is unchanged from source Compose and apps/worker/main.py remains present and unchanged.

### Phase 06 — Final acceptance and rollback evidence

1. Re-run source hash, source health, counts and keys; prove no source mutation.
2. Re-run target path/hash allowlist; expected source-content diff only allowed FE/Compose removal. Exclude and report plan-owned/generated metadata separately.
3. Re-run service list, actual volume inspect, health, Alembic head and read-only parity.
4. Confirm workbook, importer, worker, docs, plans, specs and root metadata exist at expected paths.
5. Update feature_list.json evidence with captured command outputs; do not mark feature complete until verification passes.

### Phase 07 — Cutover: remove old Docker backend and old database

Run only after Phase 06 passes and the owner has confirmed the destructive cutover. Preserve W:\f-caps-schedule-be-artifacts\db\source-20260818.dump and its checksum first.

1. Stop and remove only the old backend services from the old Compose project: api, worker and postgres. Do not delete source files. The old web container is not part of the new backend and may be stopped separately if it is no longer needed.
2. Verify old containers are absent and target containers use different IDs/volume.
3. Remove the old Docker volume capstonedefensescheduler_postgres_data only after target read-only parity has been captured and the external dump is readable.
4. Start target BE on its canonical host ports if desired; otherwise keep the temporary external override. Validate /health and Alembic current again.
5. Record the cutover evidence and leave the target volume as the only active local scheduler database.

Rollback before deleting the old volume: stop target, restart old Compose backend from the retained source volume. Rollback after deleting the old volume is restore-only from the retained dump into a fresh volume; this is why the dump and checksum are mandatory.

Never delete the source repository. Do not use docker compose down -v on the old project as a shortcut because it can remove unintended volumes.

## 6. File map

- apps/api/**: copy unchanged.
- apps/worker/**: copy unchanged, including legacy worker.
- tools/**: copy unchanged; do not execute importer.
- infra/docker/api.Dockerfile: copy unchanged.
- docker-compose.yml: source copy with only allowed web removal and target volume identity.
- .env.example, .dockerignore, .gitignore, schema.sql: copy unchanged.
- docs/**, plans/**, PRD/BusinessRules/ERD: copy unchanged.
- workbook .xlsx: copy unchanged as external importer input, never database blob.
- W:\f-caps-schedule-be-artifacts\*: generated evidence/dump outside repo.
- source repo: no action/deletion.
- old source Docker containers/volume: remove only in Phase 07 after parity and dump-retention gates.

## 7. Risk register

- Target mounts source volume — Critical: inspect source/target IDs and actual mounts before restore.
- Restore loses Excel data — Critical: validated custom dump, exit-on-error restore, read-only count/key parity.
- Importer/seed/tests change official DB — Critical: never run against source; URL guard.
- Exact-copy scope violated — High: allowlist/hash comparison; only documented FE/Compose diff.
- FE runtime remains — Medium: Compose service/build-context/runtime grep.
- Pre-existing dependency/build failure — Medium: preserve source and report, do not fix.
- Source drift — High: source file hashes and pre-cutover DB baseline; deliberate old-volume deletion is isolated to Phase 07.

## 8. Feature acceptance mapping

- backend-exact-copy: Phases 00,01,02,06; inventory, hashes, path parity, allowed Compose diff.
- frontend-only-removal: Phases 01,02,06; no FE paths, exact three services, no web runtime.
- database-isolated-clone: Phases 00,03,04,06; dump, volume identity, counts, keys, head.
- backend-artifact-preservation: Phases 01,05,06; apps/api, worker, tools, docs, plans, metadata and workbook present/hash-equivalent.
- source-immutability: Phases 00,03,04,06,07; source file hashes remain unchanged, pre-cutover health/counts/keys are captured, and old-volume deletion is explicit and post-parity.

## 9. Red-team adjudication and owner validation

Current plan applies the confirmed exact-copy-except-FE scope and maps directly to the current spec and feature IDs. No source repair or artifact rewrite is included.

Owner must confirm before cook:

1. Exact-copy: giữ nguyên backend artifacts, docs/plans/workbook/dependency metadata; chỉ bỏ FE và web Compose service.
2. Target dùng volume riêng f_caps_schedule_be_postgres_data; source volume giữ nguyên; không external true.
3. Không chạy importer, seed hoặc write-capable tests trên official source database.

After approval:
$ck-cook --hard --tdd plans/backend-repo-extraction/plan.md

## Session Notes
<!-- Updated by cook automatically — do not edit manually -->

Last active: 2026-08-18
Phase in progress: Complete
Status: Cutover passed; standalone backend is running on canonical ports with the isolated target volume, and rollback dump evidence is retained.

### Decisions made this session
- Dump retained at W:\f-caps-schedule-be-artifacts\db\source-20260818.dump.
- Source inventory/hash evidence retained at W:\f-caps-schedule-be-artifacts\source-backend-inventory.json.
- Exact-copy target excludes apps/web, infra/docker/web.Dockerfile and erd-viewer.html; target workbook SHA256 matches source.
- Source Compose remains unchanged and source/target postgres container IDs differ.
- Parity evidence retained at W:\f-caps-schedule-be-artifacts\target-db-parity.json; all parity SQL was read-only.

### Next immediate action
None. Keep W:\f-caps-schedule-be-artifacts\db\source-20260818.dump and its checksum for rollback before any future database reset.
