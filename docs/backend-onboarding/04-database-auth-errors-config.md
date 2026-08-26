# 04. Database, authentication, errors và configuration

## Database connection và Session

`apps/api/app/config.py` đọc `DATABASE_URL`. `apps/api/app/database.py` tạo engine bằng
`create_engine(..., pool_pre_ping=True)` và cache tối đa bốn URL. `get_db()` yield một
SQLAlchemy `Session` cho FastAPI dependency injection.

```text
.env / process environment
   -> Settings.database_url
   -> get_engine(database_url)
   -> connection pool
   -> get_db()
   -> Session/request
```

SQLAlchemy trong repo này không đóng vai trò ORM. Không có class `User`, `Semester` hay `Round`
map tới table. Query thường có dạng:

```python
db.execute(text("SELECT ... WHERE id = :id"), {"id": value}).mappings().one_or_none()
```

Bound parameters tránh việc nối raw user input vào SQL. Với dynamic column list, chỉ dùng tên
cột từ whitelist do code kiểm soát.

## Transaction được quản lý thế nào?

Các pattern chính:

- Read-only endpoint: Session tự mở implicit transaction; đóng Session sẽ trả connection về pool.
- Mutation đơn giản: chạy writes rồi `db.commit()`.
- Mutation nhiều bước: `with db.begin():` để cùng commit/rollback.
- Đã SELECT trước explicit transaction: thường phải `db.rollback()` rồi mới `with db.begin()`.
- Concurrency nhạy cảm: `SELECT ... FOR UPDATE` và/hoặc PostgreSQL advisory transaction lock.

Business write thường đi cùng `INSERT audit_events` trong cùng transaction. Một số thao tác còn
ghi outbox để worker xử lý sau commit.

Không nên mở/commit transaction bên trong một helper mà caller đang kỳ vọng kiểm soát transaction,
trừ khi contract của helper ghi rõ. Hãy đọc call sites của service trước khi thay đổi.

## Migration và schema source of truth

Alembic nằm tại:

- Config: `apps/api/alembic.ini`.
- Runtime environment: `apps/api/migrations/env.py`.
- Revisions: `apps/api/migrations/versions/`.

`target_metadata = None` vì không có ORM metadata để autogenerate schema. Migration viết SQL/
Alembic operations trực tiếp. `DATABASE_URL` từ environment override URL trong Alembic config.

Không dùng root `schema.sql` làm schema runtime. Không sửa migration cũ đã được apply; tạo revision
mới với `down_revision` đúng rồi test `alembic upgrade head`.

## Quan hệ entity quan trọng

```text
Semester
  |--< Project --< ProjectSupervisor >-- Lecturer
  |       |
  |       +-- 0..1 Group --< GroupMembership >-- Student
  |
  +--< Round
         |--< RoundDay --< Timeslot
         |--< registrations / availability / conflicts
         |--< bound Committee(s)
         |--< ScheduleVersion
                  |--< ScheduleAssignment --< assignment reviewers
                  +--< Session
                         |-> Council -> CouncilMember
                         |-> Room
                         +-> SessionResult -> Remediation
```

Các nuance cần nhớ:

- `groups.project_id` nullable: group có thể tồn tại trước project.
- Quan hệ hiện có unique constraint nên effective là project `0..1` group và group `0..1` project.
- `schedule_assignments.project_id` đóng băng provenance lịch sử; không rewrite khi group đổi project.
- Một Round có nhiều ScheduleVersion, nhưng chỉ một version active theo database constraint.
- Committee là reusable planning input; Council là operational snapshot bất biến của Session.
- Nếu Round dùng Timeframe template, nó bind cả Timeframe và đúng TimeframeVersion để đóng băng
  revision được sử dụng. Round cấu hình bằng manual days có thể để cả hai binding là `NULL`.
- DB triggers/constraints bảo vệ audit immutability, Council sealing và nhiều uniqueness/overlap rules.

## Authentication: login đến current user

### Login

Endpoint `POST /api/v1/auth/login` gọi `login()` trong `routes/auth_routes.py`:

```text
email + password
  -> login throttle theo normalized-email + client host
  -> SELECT account + role
  -> Argon2 verify password hash
  -> tạo random session token và CSRF token
  -> chỉ lưu SHA-256 hash vào auth_sessions
  -> ghi LOGIN_SUCCESS audit event
  -> set cookies
```

- `scheduler_session`: `httpOnly`, JavaScript không đọc được.
- `scheduler_csrf`: JavaScript đọc được để gửi lại qua `X-CSRF-Token`.
- Cả hai dùng `SameSite=Lax`; `Secure=True` ngoài development/test.
- Session có absolute expiry và idle timeout.

### Authenticated request

`get_current_user()` trong `app/auth.py`:

1. Trong `APP_ENV=test`, có thể dùng `X-Test-Session: active-<role>[:account_id]`.
2. Môi trường thường đọc cookie session, hash token và query `auth_sessions`.
3. Kiểm tra session chưa revoke/expire/idle-expire và account `ACTIVE`.
4. Update `last_seen_at` **có điều kiện**: chỉ chạy `UPDATE ... WHERE last_seen_at <= now() - SESSION_HEARTBEAT_SECONDS` rồi commit khi `rowcount > 0`; nếu không, rollback (không phải write mỗi request nữa — xem `SESSION_HEARTBEAT_SECONDS` bên dưới). Idle-timeout ở bước 3 vẫn kiểm tra trên mọi request, không bị nới bởi throttle này.
5. Trả `CurrentUser`.
6. Không hợp lệ trả 401.

Test seam tuyệt đối không hoạt động ngoài `APP_ENV=test`.

`SESSION_HEARTBEAT_SECONDS` (default `60`) giới hạn tần suất ghi `last_seen_at`. Phải nhỏ hơn hẳn
`SESSION_IDLE_MINUTES * 60` — `Settings` tự clamp về `idle_minutes * 60 // 2` nếu bị set sai, vì
heartbeat ≥ idle window sẽ khiến mọi session chết ở idle-timeout bất kể có traffic hay không.

### Logout

`logout()` revoke DB session, ghi audit event và xóa hai cookies. Token phía client bị xóa nhưng
điểm bảo vệ quan trọng là `revoked_at` trong DB.

## Authorization

System roles là `ADMIN`, `MANAGER`, `LECTURER`, `STUDENT`. Reviewer, Supervisor, Result Owner,
Remediation Verifier và Project Leader là contextual assignments, không phải system roles.

Authorization hiện phân tán:

- `_require()` hoặc `_manager()` trong route files kiểm tra system role.
- `services/access.py` kiểm tra resource scope, ví dụ `visible_session_ids()`,
  `can_read_session()`, `is_active_group_leader()`.
- Domain policies kiểm tra quyết định nghiệp vụ bằng `PolicyContext`.

Ví dụ Lecturer chỉ thấy session mà họ là reviewer hoặc supervisor; Student chỉ thấy session của
group có active membership; management thấy phạm vi vận hành đầy đủ.

## Error handling

```text
Domain/service/DB phát hiện lỗi
  -> DomainError / IntegrityError / HTTPException
  -> route map thành HTTP status + stable code
  -> main.py exception handler chọn target/legacy envelope
  -> JSON response
```

- `DomainError` trong `domain/errors.py` mang stable machine-readable `code`.
- Route thường map domain rejection thành 409 hoặc 422 tùy contract.
- `IntegrityError` thường thành 409 business conflict.
- `HTTPException` mang status do handler quyết định.
- Request validation mặc định là 422.
- Target routes dùng `{"error":{"code","message","details"}}`.
- Legacy routes dùng `{"detail": ...}`.

Không có global handler riêng cho mọi `DomainError`; route là boundary chuyển domain error sang
HTTP. Unexpected exception đi qua FastAPI/Uvicorn default 500.

## Logging và observability

Đã xác nhận:

- Business audit bền vững nằm trong table `audit_events`.
- `services/route_telemetry.py` dùng in-memory `Counter`, mất khi restart và không aggregate giữa
  nhiều process.
- Không thấy structured application logging/tracing trong core route/auth code.
- Uvicorn/ASGI vẫn log access và unhandled exception theo cấu hình runtime mặc định.

Không được gọi audit table là “application log”: audit mô tả hành động nghiệp vụ; operational log
mô tả runtime/error/performance. Hai mục tiêu khác nhau.

## Configuration và môi trường

`Settings` dùng `pydantic-settings`, đọc environment và file `.env`, bỏ qua keys không biết.
`get_settings()` được cache; thay environment trong process cần restart hoặc clear cache.

Các settings chính:

- `APP_ENV`
- `DATABASE_URL`
- `SESSION_COOKIE_NAME`
- `SESSION_IDLE_MINUTES`, `SESSION_ABSOLUTE_HOURS`
- `CORS_ORIGINS`
- `SEMESTER_MIN_DURATION_DAYS`, `SEMESTER_MAX_DURATION_DAYS`

`SEED_FIXTURE` được bootstrap tool đọc từ environment dù không phải field trong `Settings`.

Repo không có profile hoặc file config riêng cho staging/production. `APP_ENV=test` mở test-session
seam; `development` và `test` tắt `Secure` cookie/HSTS để chạy local. Mọi giá trị khác được xử lý
như môi trường bảo mật hơn: cookie có `Secure` và response có HSTS. Khi deploy staging/production,
platform phải truyền environment variables thật như `APP_ENV`, `DATABASE_URL`, CORS và session
settings; không copy `.env.example` nguyên trạng.

Không commit secret thật. `.env.example` chỉ là template. Cần chú ý hai default lệch nhau:

- `config.py` mặc định session idle/absolute là `60 phút / 168 giờ`.
- `.env.example` đặt `15 phút / 8 giờ`.

Compose DB từ container dùng `postgres:5432`, còn host port là `15432`. `localhost:5432` trong
default config không tự trỏ vào Compose Postgres nếu máy host không map port đó.
