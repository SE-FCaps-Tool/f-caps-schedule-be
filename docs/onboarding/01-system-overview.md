# 1. Tổng quan hệ thống

## 1.1 Hệ thống này giải quyết bài toán gì?

Đây là backend của **Capstone Defense Scheduler** — hệ thống xếp lịch bảo vệ đồ án tốt nghiệp cho một trường đại học.

Bài toán đời thực nó giải:

> Có ~74 nhóm sinh viên phải bảo vệ, ~26 giảng viên có thể chấm, mỗi giảng viên chỉ rảnh một số khung giờ, có 4 phòng, và hàng chục luật cứng ("giảng viên hướng dẫn không được chấm chính nhóm mình", "một giảng viên không chấm 2 chỗ cùng lúc", "vòng bảo vệ lần 2 phải giữ đúng hội đồng cũ"...). Hãy xếp lịch tự động sao cho không vi phạm luật nào, rồi cho Manager duyệt và công bố.

Vòng đời nghiệp vụ chính:

```text
Học kỳ (Semester)
   └── Đợt đánh giá (Round: Review 1, Review 2, Defense 1.1, Defense 1.2, Defense 2)
         ├── Mời giảng viên → giảng viên đăng ký khung giờ rảnh (availability)
         ├── Đăng ký nhóm tham gia đợt
         ├── Chạy thuật toán → sinh ra nhiều "phương án lịch" (ScheduleVersion, trạng thái DRAFT)
         ├── Manager so sánh, chọn 1 phương án → ACTIVE
         ├── Publish → sinh session thật, bắn thông báo cho sinh viên/giảng viên
         ├── Chấm điểm, ghi kết quả (session_results)
         └── Nhóm rớt → mở case khắc phục (remediation) → xếp lịch bảo vệ lại
```

## 1.2 Ngôn ngữ, framework, hạ tầng

| Thành phần | Công nghệ | File xác nhận |
|---|---|---|
| Ngôn ngữ | Python ≥ 3.11 | [apps/api/pyproject.toml](../../apps/api/pyproject.toml) |
| Web framework | **FastAPI** | [apps/api/app/main.py](../../apps/api/app/main.py) |
| Web server | **Uvicorn** (ASGI) | `docker-compose.yml` → `uvicorn app.main:app` |
| Database | **PostgreSQL 16** | [docker-compose.yml](../../docker-compose.yml) |
| Truy cập DB | **SQLAlchemy 2.x Core** (KHÔNG dùng ORM) | [apps/api/app/database.py](../../apps/api/app/database.py) |
| Driver DB | psycopg 3 | `pyproject.toml` |
| Migration | **Alembic** (39 file version) | [apps/api/migrations/](../../apps/api/migrations/) |
| Validation dữ liệu vào/ra | **Pydantic v2** | có mặt trong mọi route |
| Cấu hình | pydantic-settings | [apps/api/app/config.py](../../apps/api/app/config.py) |
| Thuật toán xếp lịch | **Google OR-Tools CP-SAT** | [apps/api/app/scheduler/scheduler.py](../../apps/api/app/scheduler/scheduler.py) |
| Hash mật khẩu | **argon2-cffi** | [apps/api/app/routes/auth_routes.py](../../apps/api/app/routes/auth_routes.py) |
| Đọc file Excel | openpyxl | `tools/import_excel_database.py` |
| Lint | ruff | `pyproject.toml` |
| Test | pytest + httpx TestClient | [apps/api/tests/conftest.py](../../apps/api/tests/conftest.py) |
| Quản lý package | **uv** (không phải pip/poetry) | có `uv.lock` |

### Giải thích thuật ngữ cho người mới

- **FastAPI**: thư viện Python để viết Web API. Bạn khai báo một hàm Python, gắn decorator `@router.get("/duong-dan")`, FastAPI tự lo phần nhận HTTP request, đọc JSON, kiểm tra kiểu dữ liệu, và trả JSON về.
- **ASGI / Uvicorn**: Python bản thân không biết nói HTTP. Uvicorn là chương trình đứng ở cổng 8000, nhận gói tin HTTP, dịch sang object Python rồi đưa cho FastAPI.
- **ORM (Object-Relational Mapping)**: kỹ thuật ánh xạ bảng DB thành class Python (`class User: ...` rồi gọi `session.query(User).all()`). **Repo này KHÔNG dùng ORM** — xem mục 1.4.
- **Migration**: file mô tả thay đổi cấu trúc DB (thêm bảng, thêm cột). Chạy tuần tự để mọi máy có cùng schema. Ở đây dùng Alembic.
- **CP-SAT**: bộ giải bài toán ràng buộc của Google. Bạn mô tả "có các biến nhị phân này, phải thoả các điều kiện kia, hãy tối ưu điểm số này" — nó tự tìm lời giải.

## 1.3 Kiến trúc tổng thể

Đây là **monolith** (một ứng dụng duy nhất, không phải microservices), chạy 3 container:

```text
docker compose up
│
├── postgres   PostgreSQL 16, cổng host 15432 → container 5432
├── api        uvicorn, cổng 8000 — phục vụ toàn bộ REST API
└── worker     python -m app.worker — vòng lặp nền, không mở cổng nào
```

Cả `api` và `worker` dùng **chung một Docker image** và **chung code** ([infra/docker/api.Dockerfile](../../infra/docker/api.Dockerfile)), chỉ khác câu lệnh khởi động. Cả hai đều chạy [tools/bootstrap_database.py](../../tools/bootstrap_database.py) trước — script này lấy một *advisory lock* của PostgreSQL (một loại khoá do ứng dụng tự đặt tên, để hai tiến trình không cùng chạy migration một lúc), chạy `alembic upgrade head`, rồi nạp dữ liệu mẫu.

**Phong cách kiến trúc [Suy luận]:** gần với *Transaction Script* — mỗi endpoint là một kịch bản tuần tự: kiểm tra quyền → mở transaction → chạy vài câu SQL → ghi audit → trả kết quả. Đây **không** phải Clean Architecture / Hexagonal, dù có thư mục tên `domain/` và `services/`.

## 1.4 Vì sao không dùng ORM?

**[Xác nhận từ code]** Không tồn tại một file nào khai báo `declarative_base()` hay class model. Mọi truy vấn đều có dạng:

```python
row = db.execute(
    text("SELECT id, code, name FROM semesters WHERE id = :semester_id"),
    {"semester_id": semester_id},
).mappings().one()
```

**[Suy luận]** Lý do hợp lý: nghiệp vụ này dùng rất nhiều tính năng riêng của PostgreSQL mà ORM diễn đạt vụng về — `jsonb`, native ENUM, *partial unique index*, `SELECT ... FOR UPDATE SKIP LOCKED`, `pg_advisory_xact_lock`, `INSERT ... ON CONFLICT DO UPDATE`. Tài liệu [docs/project-reference/ERD_CapstoneScheduler_v1.0.md](../project-reference/ERD_CapstoneScheduler_v1.0.md) mục E9 xác nhận việc chọn PostgreSQL chính vì các tính năng đó.

**Cái giá phải trả:** không có type-safety cho câu query. Gõ sai tên cột thì chỉ vỡ lúc chạy, không vỡ lúc lint. Đây là nguồn bug số một cho người mới — xem [12-junior-warnings.md](12-junior-warnings.md).

## 1.5 Các module / domain chính

| Module | Router chính | Mô tả |
|---|---|---|
| **Auth** | `routes/auth_routes.py` | Đăng nhập, đăng xuất, phiên làm việc |
| **Master data** | `routes/master_data.py` (2097 dòng, 40 endpoint) | Học kỳ, tài khoản, giảng viên, sinh viên, đề tài, nhóm, đợt đánh giá, phòng, khung giờ |
| **Manager extensions** | `routes/manager_extensions.py` (25 endpoint) | PATCH/chi tiết bổ sung, import/export Excel, báo cáo |
| **Scheduling** | `routes/schedule_operations.py` (1854 dòng, 19 endpoint) | Chạy thuật toán, so sánh phương án, kích hoạt, sửa tay, công bố, dời/bù buổi |
| **Committees** | `routes/committee_contract.py`, `services/committee_service.py` | Danh mục hội đồng dùng lại được |
| **Timeframe** | `routes/target_timeframe_contract.py`, `services/timeframe_service.py` | Mẫu khung giờ toàn cục (chia buổi → block → slot) |
| **Room assignment** | `routes/room_assignment.py`, `services/room_assignment.py` | Gán phòng cho buổi bảo vệ |
| **Results & remediation** | `routes/results.py`, `routes/target_results_remediation.py` | Nhập kết quả, mở case khắc phục |
| **Operations / portals** | `routes/operations.py`, `routes/target_portals.py` | Dashboard, thông báo, lịch cá nhân của giảng viên/sinh viên |

Tổng cộng **174 endpoint** trên 17 router.

## 1.6 Auth hoạt động ra sao (bản tóm tắt)

Không dùng JWT. Dùng **cookie session** lưu trong DB + **CSRF double-submit**:

```text
POST /api/v1/auth/login
   → kiểm tra mật khẩu bằng argon2
   → sinh 2 chuỗi ngẫu nhiên: session token + csrf token
   → lưu SHA-256 của cả hai vào bảng auth_sessions
   → set 2 cookie: scheduler_session (httpOnly) + scheduler_csrf (đọc được bằng JS)

Mọi request sau:
   → cookie scheduler_session tự gửi kèm
   → nếu là POST/PUT/PATCH/DELETE, client phải copy giá trị cookie scheduler_csrf
     vào header X-CSRF-Token
```

Chi tiết đầy đủ ở [06-auth.md](06-auth.md).

## 1.7 Có Redis, Queue, Background Job, WebSocket không?

| Thứ | Có? | Ghi chú |
|---|---|---|
| Redis | **Không** | Không có trong dependency lẫn compose |
| Message broker (RabbitMQ/Kafka) | **Không** | |
| Celery | **Không** | |
| Background job | **Có, tự viết** | Bảng `outbox_jobs` trong Postgres + vòng lặp `while True: ... sleep(2)` ở [apps/api/app/worker.py](../../apps/api/app/worker.py) |
| Scheduler kiểu cron | **Không** | Việc theo lịch (nhắc hạn, tự đóng đợt) được kiểm tra mỗi 2 giây trong chính vòng lặp worker |
| WebSocket | **Không** | Frontend phải tự poll |
| Gửi email thật | **Không** | `NoopEmailAdapter` trong [apps/api/app/services/notification_dispatcher.py](../../apps/api/app/services/notification_dispatcher.py) — có interface sẵn nhưng không gửi gì |
| External service | **Không** | Duy nhất có nạp dữ liệu từ file Excel một lần lúc khởi tạo |

**Pattern quan trọng — Transactional Outbox:** thay vì gửi thông báo ngay trong request (rủi ro: transaction rollback nhưng email đã bay đi), route chỉ `INSERT INTO outbox_jobs` cùng transaction với dữ liệu nghiệp vụ. Worker đọc bảng đó sau và mới thực sự "gửi". Nếu transaction rollback thì job cũng biến mất — không bao giờ gửi nhầm.

Worker lấy job bằng `SELECT ... FOR UPDATE SKIP LOCKED` — cú pháp Postgres cho phép nhiều worker chạy song song mà không giành nhau cùng một dòng.

## 1.8 Dependency quan trọng nhất và vai trò

Đọc từ [apps/api/pyproject.toml](../../apps/api/pyproject.toml):

```text
fastapi          → định tuyến HTTP, validate, sinh tài liệu OpenAPI tự động
uvicorn          → chạy app, cổng 8000
sqlalchemy       → kết nối DB, quản lý transaction, bind tham số an toàn (chống SQL injection)
psycopg[binary]  → driver PostgreSQL
alembic          → migration schema
pydantic-settings→ đọc biến môi trường thành object Settings có kiểu
argon2-cffi      → hash & verify mật khẩu
ortools          → CP-SAT solver, trái tim của việc xếp lịch
openpyxl         → đọc file Excel khi bootstrap dữ liệu
python-multipart → nhận file upload
```

Dev only: `pytest`, `pytest-cov`, `httpx` (TestClient gọi API trong bộ nhớ, không cần chạy server), `ruff`.

## 1.9 Câu hỏi tự kiểm tra

Trước khi sang phần 2, bạn nên trả lời được:

1. Khi tôi `POST /api/v1/auth/login`, server lưu gì vào DB?
2. Nếu tôi thêm một cột mới vào bảng `rounds`, tôi phải sửa ở đâu để mọi người cùng có cột đó?
3. Vì sao route không gọi thẳng hàm gửi email?
