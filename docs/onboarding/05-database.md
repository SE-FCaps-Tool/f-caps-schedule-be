# 5. Database

## 5.1 Kết nối được tạo ở đâu?

**File duy nhất:** [apps/api/app/database.py](../../apps/api/app/database.py) — 18 dòng.

```python
@lru_cache(maxsize=4)
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)

def get_db() -> Generator[Session, None, None]:
    with Session(get_engine(get_settings().database_url)) as session:
        yield session
```

```text
DATABASE_URL (biến môi trường)
      │
      ▼
Settings.database_url   ← apps/api/app/config.py
      │
      ▼
create_engine(...)      ← tạo MỘT LẦN cho cả process, nhờ @lru_cache
      │  Engine = pool các kết nối TCP tới Postgres
      ▼
Session(engine)         ← tạo MỚI cho MỖI request, qua Depends(get_db)
      │
      ▼
db.execute(text("SQL"), {tham số})
```

Định dạng URL: `postgresql+psycopg://scheduler:scheduler@postgres:5432/scheduler`
(`+psycopg` chỉ định dùng driver psycopg 3.)

**Ba nơi tự tạo Session ngoài `get_db`** — biết để không hoảng khi gặp:

| Nơi | Vì sao |
|---|---|
| `main.py::_valid_csrf` | Middleware chạy trước hệ thống `Depends`, không xin được `db` theo cách thường |
| `app/worker.py::run` | Worker là process riêng, không có request nào cả |
| `tools/*.py` | Script chạy tay, một số dùng thẳng `psycopg` không qua SQLAlchemy |

## 5.2 Model / Entity nằm ở đâu?

**Không ở đâu cả.** Repo này không có ORM model.

Muốn biết bảng `rounds` có những cột gì, có 3 cách:

```powershell
# 1. Hỏi thẳng DB đang chạy (nhanh nhất)
docker compose exec -T postgres psql -U scheduler -d scheduler -c "\d rounds"

# 2. Tìm trong migration
grep -rn "rounds" apps/api/migrations/versions/

# 3. Đọc ERD nghiệp vụ
docs/project-reference/ERD_CapstoneScheduler_v1.0.md
```

Kết quả truy vấn là dict-like, không phải object:

```python
row = db.execute(text("SELECT id, status FROM rounds WHERE id = :id"), {"id": 1}).mappings().one()
row["status"]      # ✅
row.status         # ❌ AttributeError
```

## 5.3 Query như thế nào?

Không có repository layer. Route và service gọi thẳng `db.execute(text(...))`.

Bảng tra cứu các cách lấy kết quả — bạn sẽ gặp cả năm:

| Cú pháp | Trả về | Dùng khi |
|---|---|---|
| `.mappings().one()` | 1 dict, lỗi nếu ≠ 1 dòng | Chắc chắn phải có đúng một |
| `.mappings().one_or_none()` | 1 dict hoặc `None` | Có thể không tồn tại → thường kèm 404 |
| `.mappings().all()` | list các dict | Danh sách |
| `.scalar_one_or_none()` | giá trị cột đầu hoặc `None` | Chỉ cần 1 giá trị (VD `SELECT id ...`) |
| `.all()` (không `.mappings()`) | list tuple | Lấy theo chỉ số `row[0]` |

Ví dụ mỗi kiểu, đều là code thật:

```python
# apps/api/app/services/semester_queries.py
status = db.execute(text("SELECT status FROM semesters WHERE id = :semester_id FOR UPDATE"),
                    {"semester_id": semester_id}).scalar_one_or_none()

# apps/api/app/services/access.py
rows = db.execute(text("SELECT s.id FROM sessions s WHERE ..."), {...}).all()
return {int(row[0]) for row in rows}

# apps/api/app/routes/auth_routes.py
row = db.execute(text("SELECT a.id, a.password_hash, a.status, ar.role FROM accounts a ..."),
                 {"email": ...}).mappings().one_or_none()
```

**Quy tắc bất di bất dịch:** giá trị luôn đi qua tham số `:ten_tham_so`, **không bao giờ** f-string.

```python
# ❌ TUYỆT ĐỐI KHÔNG — mở cửa cho SQL injection
db.execute(text(f"SELECT * FROM accounts WHERE email = '{email}'"))

# ✅
db.execute(text("SELECT * FROM accounts WHERE email = :email"), {"email": email})
```

## 5.4 Transaction được quản lý ở đâu?

Ở **tầng route**, bằng `with db.begin():`. Không có decorator `@transactional`, không có Unit of Work tự động.

```python
with db.begin():
    ...  # nhiều câu SQL
# thoát khối êm đẹp → COMMIT
# có exception    → ROLLBACK, exception bay tiếp lên trên
```

Ba kỹ thuật đồng thời (concurrency) mà repo dùng — bạn sẽ gặp liên tục:

### 1. `SELECT ... FOR UPDATE` — khoá dòng

```python
# apps/api/app/services/semester_queries.py
status = db.execute(
    text("SELECT status FROM semesters WHERE id = :semester_id FOR UPDATE"),
    {"semester_id": semester_id},
).scalar_one_or_none()
```

Khoá đúng dòng đó cho tới hết transaction. Transaction khác muốn `FOR UPDATE` cùng dòng phải xếp hàng chờ. Dùng cho mẫu "đọc → quyết định → ghi" trên một bản ghi.

### 2. `pg_advisory_xact_lock` — khoá do ứng dụng đặt tên

```python
db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"),
           {"lock_key": SEMESTER_LIFECYCLE_LOCK_KEY})   # = 918273645
```

Khoá không gắn với dòng nào, chỉ là một con số hai bên cùng quy ước. Dùng khi phải bảo vệ **một bất biến trải trên nhiều dòng** ("chỉ được một học kỳ ACTIVE").

Khoá cho tài nguyên động (phòng, giảng viên) được sinh từ tên + id để không đụng nhau — [apps/api/app/services/resource_locks.py](../../apps/api/app/services/resource_locks.py):

```python
def resource_lock_key(namespace: str, resource_id: int) -> int:
    digest = hashlib.sha256(f"scheduler:{namespace}:{int(resource_id)}".encode()).digest()
    ...
def acquire_resource_locks(db, namespace, resource_ids):
    keys = sorted({resource_lock_key(namespace, rid) for rid in resource_ids})
    for key in keys:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
```

Chú ý `sorted(...)`: luôn lấy khoá theo cùng thứ tự → **không bao giờ deadlock**. Đây là chi tiết tinh tế đáng học.

### 3. `FOR UPDATE SKIP LOCKED` — hàng đợi

```python
# apps/api/app/services/notification_dispatcher.py
claimed = db.execute(text(
    "SELECT id, topic, payload, dedupe_key FROM outbox_jobs "
    "WHERE status = 'PENDING' AND available_at <= now() "
    "ORDER BY id FOR UPDATE SKIP LOCKED LIMIT :limit"
), {"limit": ...}).mappings().all()
```

`SKIP LOCKED` = "dòng nào đang bị khoá thì bỏ qua, đừng chờ". Nhờ vậy nhiều worker chạy song song, mỗi worker nhận một lô job khác nhau. Đây là cách biến bảng SQL thành hàng đợi mà không cần Redis.

## 5.5 Migration

Công cụ: **Alembic**. Thư mục: [apps/api/migrations/versions/](../../apps/api/migrations/versions/) — 39 file, `0001` → `0038`.

Mỗi file có `revision` và `down_revision` tạo thành chuỗi tuyến tính:

```text
0001_bootstrap → 0002_domain_model → ... → 0038_project_bilingual_titles
```

Trong repo này, migration đa số viết **SQL thô** qua `op.execute("CREATE TABLE ...")` chứ không dùng API `op.create_table` của Alembic — nhất quán với triết lý "SQL thật, không trừu tượng hoá".

Khi nào chạy? Tự động, mỗi lần container khởi động, qua [tools/bootstrap_database.py](../../tools/bootstrap_database.py):

```python
LOCK_KEY = 617283945

def main():
    connection = _connect(database_url)          # lấy pg_advisory_lock(617283945)
    try:
        commands = [["alembic", "upgrade", "head"]]
        if _seed_fixture_enabled():
            commands.append(["python", "/app/tools/seed_versioned_fixture.py"])
        for command in commands:
            subprocess.run(command, cwd=API_ROOT, check=True)
    finally:
        connection.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
```

Advisory lock ở đây giải quyết đúng một vấn đề: container `api` và `worker` khởi động **cùng lúc**, cả hai đều muốn chạy migration. Khoá khiến một cái chờ cái kia xong.

Tên migration đọc như nhật ký tiến hoá sản phẩm — đáng lướt qua để hiểu hệ thống đã đi qua những gì:

```text
0006 auth_sessions              → thêm đăng nhập
0012 excel_import_data          → nạp dữ liệu từ Excel
0016 semester_active_closed     → BỎ trạng thái UPCOMING
0019 nullable_group_project     → nhóm được tồn tại trước khi có đề tài
0025 immutable_councils         → hội đồng thành bất biến
0026 semester_four_states       → lại đổi tập trạng thái học kỳ
0030 global_timeframe_templates → mẫu khung giờ dùng chung
0034 committees                 → danh mục hội đồng
0037 canonical_defense_round_types
```

### Thêm migration mới

```powershell
docker compose exec -T api alembic revision -m "mo_ta_ngan"
# sửa file vừa sinh trong apps/api/migrations/versions/
docker compose exec -T api alembic upgrade head
```

Quy tắc: **không bao giờ sửa migration đã merge**. Người khác đã chạy nó rồi; sửa xong máy bạn và máy họ sẽ lệch schema. Luôn thêm file mới.

## 5.6 Các bảng chính và quan hệ

44 bảng. Nhóm theo chức năng:

```text
IDENTITY & AUTH
  accounts, account_roles, auth_sessions, auth_login_throttles

DANH MỤC / MASTER DATA
  majors, semesters, rooms, lecturers, students,
  projects, project_supervisors, groups, group_memberships,
  conflict_declarations, semester_lecturer_quotas

TỔ CHỨC ĐỢT ĐÁNH GIÁ
  rounds, round_days, timeslots, round_groups, round_rooms,
  round_room_types, round_invitations,
  lecturer_availabilities, group_slot_preferences

HỘI ĐỒNG
  councils, council_members     (bất biến — đổi người ⇒ tạo council mới)

XẾP LỊCH
  scheduler_jobs, schedule_versions, sessions, session_reviewers,
  schedule_change_records, reschedule_requests, round_operation_records

KẾT QUẢ
  session_results, remediation_cases

HẠ TẦNG
  audit_events, notifications, outbox_jobs

NHẬP LIỆU EXCEL (chỉ dùng lúc bootstrap)
  excel_import_batches, excel_sheet_rows, excel_projects,
  excel_defense_councils, excel_council_groups,
  excel_review_schedule_rows, excel_summary_workloads
```

### Quan hệ quan trọng nhất

```text
accounts  (đăng nhập — 1 dòng cho mọi loại người)
 ├── has many → account_roles       (ADMIN / MANAGER / LECTURER / STUDENT)
 ├── has one  → lecturers           (hồ sơ giảng viên, 1-1)
 ├── has one  → students            (hồ sơ sinh viên, 1-1)
 └── has many → auth_sessions       (mỗi lần login 1 dòng)

semesters
 ├── has many → projects
 ├── has many → rounds
 └── has many → semester_lecturer_quotas

projects
 ├── belongs to → semesters, majors
 ├── has many   → project_supervisors → lecturers   (1 MAIN + tối đa 1 CO)
 └── has one    → groups                            (quan hệ 1-1)

groups
 ├── belongs to → projects           ⚠️ NULLABLE (migration 0019)
 └── has many   → group_memberships → students      (4–5 người, đúng 1 LEADER)

rounds
 ├── belongs to → semesters
 ├── has many   → round_days → timeslots            (khung giờ cụ thể)
 ├── has many   → round_groups   → groups           (nhóm nào tham gia đợt này)
 ├── has many   → round_rooms    → rooms
 ├── has many   → round_invitations → lecturers     (mời chấm)
 └── has many   → schedule_versions

lecturers
 ├── has many → lecturer_availabilities → timeslots (đăng ký rảnh)
 ├── has many → conflict_declarations → projects    (khai báo xung đột lợi ích)
 └── has many → council_members

schedule_versions   (một "phương án lịch", chạy solver nhiều lần → nhiều version)
 ├── belongs to → rounds
 ├── has many   → sessions
 ├── has many   → schedule_assignments (bản nháp bền vững)
 └── status: DRAFT → ACTIVE → PUBLISHED

sessions            (một buổi bảo vệ cụ thể)
 ├── belongs to → schedule_versions, groups, timeslots, rooms, councils
 ├── has many   → session_reviewers    (ẢNH CHỤP người chấm tại thời điểm đó)
 └── has one    → session_results
                    └── has one → remediation_cases  (nếu rớt)
```

### Ba quyết định thiết kế cần hiểu

**1. `groups.project_id` được phép NULL** (migration `0019`)

Nhóm sinh viên có thể lập trước khi chọn đề tài. Hệ quả trực tiếp lên cách viết query — và đây là chỗ **rất dễ sinh bug**:

```sql
-- Liệt kê nhóm → phải LEFT JOIN, nếu không nhóm chưa có đề tài sẽ biến mất
SELECT ... FROM groups g LEFT JOIN projects p ON p.id = g.project_id

-- Trong phạm vi một round/session → INNER JOIN là đúng,
-- vì nhóm không có đề tài thì không thể tham gia đợt đánh giá
SELECT ... FROM sessions s JOIN groups g ON g.id = s.group_id
                           JOIN projects p ON p.id = g.project_id
```

**2. `session_reviewers` là ảnh chụp (snapshot), không phải tham chiếu sống**

Bảng lưu cả `snapshot_name` — tên giảng viên tại thời điểm xếp lịch:

```python
# apps/api/app/routes/schedule_operations.py
"INSERT INTO schedule_assignment_reviewers (assignment_id, lecturer_id, is_result_owner, snapshot_name) ..."
```

Vì sao? Câu hỏi "ai đã chấm nhóm X hồi tháng 3" phải luôn cho cùng một đáp án, kể cả khi giảng viên đó đã đổi tên hoặc nghỉ việc.

**3. `council_members` bất biến**

Muốn đổi thành viên hội đồng → tạo `councils` mới, trỏ `derived_from_council_id` về cái cũ. Lý do giống trên: bảo toàn tính truy vết. Migration `0025_immutable_councils` và ERD mục E6 xác nhận.

## 5.7 `audit_events` — bảng bạn phải nhớ

Mọi thao tác ghi đều chèn một dòng vào đây, **cùng transaction**:

```python
db.execute(text("""
    INSERT INTO audit_events (actor_id, action, entity_type, entity_id, reason, before_json, after_json)
    VALUES (:actor_id, 'LEADER_CHANGED', 'group', :entity_id, :reason,
            CAST(:before_json AS JSONB), CAST(:after_json AS JSONB))
"""), {...})
```

`before_json` / `after_json` là kiểu `jsonb` của Postgres — lưu JSON có thể truy vấn được, không phải chuỗi thường.

> **Khi bạn viết endpoint ghi mới, việc chèn `audit_events` là bắt buộc theo convention.** Reviewer sẽ hỏi nếu thiếu. Copy y hệt từ handler gần nhất trong cùng file.

## 5.8 Lệnh hay dùng

```powershell
# Vào psql
docker compose exec -T postgres psql -U scheduler -d scheduler

# Xem cấu trúc một bảng
docker compose exec -T postgres psql -U scheduler -d scheduler -c "\d rounds"

# Liệt kê mọi bảng
docker compose exec -T postgres psql -U scheduler -d scheduler -c "\dt"

# Đang ở migration nào
docker compose exec -T api alembic current

# Nâng lên mới nhất
docker compose exec -T api alembic upgrade head

# Đập đi làm lại từ đầu (DB local là dữ liệu test, cứ thoải mái)
docker compose down -v && docker compose up --build
```
