# 2. Bản đồ repository

## 2.1 Cây thư mục rút gọn

```text
f-caps-schedule-be/
├── docker-compose.yml          # 3 service: postgres, api, worker
├── CLAUDE.md / AGENTS.md       # quy ước cho AI agent — cũng là tài liệu kiến trúc tốt cho người
├── README.md
│
├── apps/
│   ├── api/                    # ★ TOÀN BỘ backend nằm ở đây
│   │   ├── pyproject.toml      # dependency + cấu hình pytest/ruff
│   │   ├── alembic.ini
│   │   ├── migrations/
│   │   │   └── versions/       # 39 file migration, đánh số 0001 → 0038
│   │   ├── tests/              # 72 file test
│   │   └── app/
│   │       ├── main.py         # ★ điểm khởi đầu: tạo app, gắn middleware, gắn router
│   │       ├── config.py       # ★ đọc biến môi trường → object Settings
│   │       ├── database.py     # ★ tạo engine + dependency get_db()
│   │       ├── auth.py         # ★ dependency get_current_user()
│   │       ├── api_contract.py # helper envelope {data:...} / {error:...} + mã ID công khai
│   │       ├── response_models.py  # model Pydantic mô tả JSON trả về (cho Swagger)
│   │       ├── worker.py       # ★ vòng lặp nền
│   │       ├── jobs.py         # LEGACY, không dùng
│   │       │
│   │       ├── routes/         # ★ 17 router, 174 endpoint
│   │       ├── domain/         # hàm nghiệp vụ thuần, KHÔNG chạm DB
│   │       ├── services/       # helper có chạm DB, dùng chung nhiều route
│   │       ├── scheduler/      # engine OR-Tools CP-SAT
│   │       └── static/swagger/ # asset Swagger UI phục vụ offline
│   │
│   └── worker/                 # ✗ LEGACY, rỗng nghĩa. Đừng đụng.
│
├── tools/                      # script chạy tay / lúc khởi động container
│   ├── bootstrap_database.py   # ★ migrate + seed, chạy trước api và worker
│   ├── seed_versioned_fixture.py
│   ├── import_excel_database.py
│   └── ...
│
├── infra/docker/api.Dockerfile
├── docs/
│   ├── api/                    # tài liệu hợp đồng API cho frontend
│   ├── project-reference/      # ★ PRD, ERD, Business Rules — nguồn nghiệp vụ gốc
│   ├── journals/               # nhật ký kỹ thuật theo ngày
│   └── onboarding/             # ← bạn đang ở đây
└── plans/                      # spec & kế hoạch triển khai
```

`★` = file/thư mục bạn sẽ mở đi mở lại. `✗` = đừng đụng.

## 2.2 Trách nhiệm từng thư mục quan trọng

### `apps/api/app/routes/` — tầng Controller

| Câu hỏi | Trả lời |
|---|---|
| Chịu trách nhiệm gì? | Nhận HTTP request, kiểm tra quyền, validate payload, **mở transaction**, chạy SQL, ghi audit, trả JSON |
| Thuộc layer nào? | Controller — nhưng ở repo này nó *kiêm luôn* Service và Repository |
| Ai gọi nó? | FastAPI, sau khi middleware chạy xong |
| Nó gọi tới đâu? | `domain/` (rule thuần), `services/` (SQL dùng chung), `scheduler/`, và **gọi thẳng DB** |
| Khi nào sửa? | Gần như mọi thay đổi tính năng đều bắt đầu ở đây |

Các file bên trong:

```text
routes/
├── auth_routes.py               login / logout / me
├── master_data.py               2097 dòng — semester, account, project, group, round, room
├── manager_extensions.py        1107 dòng — PATCH + detail + import/export + report
├── schedule_operations.py       1854 dòng — chạy solver, activate, publish, sửa buổi
├── operations.py                dashboard, notification, lịch cá nhân
├── results.py                   nhập kết quả, remediation
├── room_assignment.py           gán phòng
├── committee_contract.py        CRUD danh mục hội đồng
├── round_committee_contract.py  gắn hội đồng vào đợt
└── target_*.py  (9 file)        ← xem giải thích bên dưới
```

**Về nhóm `target_*.py`:** đây là **lớp áo mới** cho hợp đồng API dành cho frontend đã tách repo. Chúng **không chứa logic nghiệp vụ** — chúng gọi lại hàm handler của router cũ rồi bọc kết quả vào phong bì `{"data": ..., "meta": ...}` và đổi id số thành id có tiền tố (`grp_12`, `rnd_3`).

Xem ví dụ rõ ràng ở [apps/api/app/routes/target_schedule_contract.py](../../apps/api/app/routes/target_schedule_contract.py):

```python
from app.routes.schedule_operations import run_scheduler   # gọi lại handler cũ

@router.post("/rounds/{round_id}/schedules/generate", status_code=201)
def generate_target_schedule(round_id, payload, db, user):
    result = run_scheduler(round_id, payload, db, user)     # ← logic thật ở đây
    return success_payload({...})                           # ← chỉ đổi hình dạng JSON
```

**Hệ quả bạn phải nhớ:** sửa logic ở router cũ thì route `target_*` cũng đổi theo. Sửa ở `target_*` thì route cũ **không** đổi. Xem [12-junior-warnings.md](12-junior-warnings.md).

### `apps/api/app/domain/` — quy tắc nghiệp vụ thuần

| Câu hỏi | Trả lời |
|---|---|
| Chịu trách nhiệm gì? | Hàm Python thuần: nhận dữ liệu đã đọc sẵn, kiểm tra luật, ném `DomainError` nếu sai |
| Thuộc layer nào? | Domain |
| Ai gọi nó? | `routes/`, `services/`, `scheduler/` |
| Nó gọi tới đâu? | **Không gọi gì hết** — không import SQLAlchemy, không có `db` |
| Khi nào sửa? | Khi luật nghiệp vụ thay đổi (VD: nhóm được phép có 6 thành viên thay vì 5) |

Ví dụ điển hình — [apps/api/app/domain/master_data.py](../../apps/api/app/domain/master_data.py):

```python
def validate_group_members(members):
    if not 4 <= len(members) <= 5:
        raise DomainError("GROUP_SIZE_INVALID", "A new group must have 4 to 5 students.")
    ...
```

Không có `db`, không có HTTP. Vì vậy **test được mà không cần Docker** — đó chính là lý do tồn tại của thư mục này.

File đáng chú ý: `errors.py` (định nghĩa `DomainError`), `enums.py` (các trạng thái hợp lệ), `transitions.py` (trạng thái nào chuyển sang trạng thái nào được), `round_types.py`, `timeframes.py`, `policy.py`.

### `apps/api/app/services/` — helper có chạm DB

| Câu hỏi | Trả lời |
|---|---|
| Chịu trách nhiệm gì? | Đoạn SQL hoặc logic-có-DB được **≥ 2 route dùng chung** |
| Thuộc layer nào? | Nằm giữa Service và Repository, không thuần cái nào |
| Ai gọi nó? | `routes/` |
| Nó gọi tới đâu? | `domain/`, và DB (nhận `db: Session` truyền vào từ route) |
| Khi nào sửa? | Khi bạn thấy mình sắp copy-paste một khối SQL sang route thứ hai |

| File | Vai trò |
|---|---|
| `access.py` | **Rất quan trọng.** Quyết định user được *nhìn thấy* dòng dữ liệu nào (row-level scoping) |
| `semester_queries.py` | Đọc semester, khoá semester, chặn ghi vào kỳ đã đóng |
| `notification_dispatcher.py` | Logic outbox — worker gọi hàm ở đây |
| `committee_service.py` | CRUD hội đồng (route `committee_contract.py` mỏng, logic nằm ở đây) |
| `timeframe_service.py` | 772 dòng — sinh mẫu khung giờ |
| `room_assignment.py` | Thuật toán gán phòng |
| `seed_loader.py` | Nạp dữ liệu mẫu |
| `resource_locks.py` | Sinh khoá advisory lock ổn định từ tên + id |
| `route_telemetry.py` | Đếm số lần gọi route cũ (phục vụ việc khai tử dần) |
| `councils.py`, `ical.py` | Hội đồng bất biến; xuất file lịch `.ics` |

**Lưu ý [Xác nhận từ code]:** service **không tự tạo** `Session`. Nó luôn nhận `db: Session` làm tham số. Nhờ vậy nó chạy chung transaction với route — đây là quyết định thiết kế đúng và bạn phải giữ nguyên khi viết service mới.

### `apps/api/app/scheduler/` — engine xếp lịch

| Câu hỏi | Trả lời |
|---|---|
| Chịu trách nhiệm gì? | Biến dữ liệu đợt đánh giá thành bài toán CP-SAT, giải, kiểm tra lại kết quả, lưu xuống DB |
| Thuộc layer nào? | Một domain riêng, khá độc lập |
| Ai gọi nó? | Chỉ `routes/schedule_operations.py` |
| Nó gọi tới đâu? | `domain/round_types.py`, `domain/errors.py`, thư viện `ortools` |
| Khi nào sửa? | Khi luật xếp lịch H1–H13 đổi, hoặc muốn đổi tiêu chí tối ưu |

Luồng bên trong:

```text
candidates.py   sinh mọi tổ hợp hợp lệ (nhóm, khung giờ, bộ reviewer)
      ↓
scheduler.py    dựng model CP-SAT, thêm ràng buộc, gọi solver
      ↓
validator.py    kiểm tra lại lời giải theo H1–H13 (mạng lưới an toàn — nếu solver sai thì bắt được)
      ↓
snapshot.py     đóng băng input để về sau còn tái hiện được
versions.py     ghi ScheduleVersion + Session xuống DB
```

`models.py` chứa các dataclass thuần (`RoundInput`, `Candidate`, `ScheduledSession`, `Violation`) — không phải ORM model, đừng nhầm tên.

### `apps/api/migrations/` — nguồn sự thật của schema

**Đây là nơi duy nhất định nghĩa cấu trúc DB.** Không có file model nào mô tả bảng. Muốn biết bảng `rounds` có cột gì, bạn phải hoặc đọc migration, hoặc `\d rounds` trong psql.

`schema.sql` ở gốc repo (nếu còn) là **ảnh chụp cũ, không được áp dụng lúc chạy** — `CLAUDE.md` nói rõ điều này.

### `apps/api/tests/` — 72 file

Chia hai loại qua marker pytest:

```text
không marker              → chạy được trên máy, không cần Docker (test domain thuần)
@pytest.mark.integration  → cần Postgres thật đang chạy
```

`conftest.py` chỉ có 11 dòng: set `APP_ENV=test` rồi tạo `TestClient(create_app())`. Nhờ `APP_ENV=test`, test được phép dùng header `X-Test-Session: active-admin` thay cho đăng nhập thật.

### `tools/` — script vận hành

Không phải một phần của app đang chạy, nhưng `bootstrap_database.py` **được gọi bởi container lúc khởi động** nên nó rất quan trọng. Còn lại là script nạp/xuất dữ liệu chạy tay.

### `docs/project-reference/` — nghiệp vụ gốc

Khi không hiểu *vì sao* một luật tồn tại, đọc ở đây trước khi hỏi:

- `PRD_CapstoneScheduler_v1.0.md` — yêu cầu sản phẩm
- `ERD_CapstoneScheduler_v1.0.md` — sơ đồ quan hệ + **lý do** cho từng quyết định thiết kế DB (mục "Quyết định thiết kế" rất đáng đọc)
- `BusinessRules_CapstoneScheduler_v1.0.md` — luật H1–H13 và các luật khác

## 2.3 Thư mục KHÔNG cần quan tâm

| Đường dẫn | Lý do |
|---|---|
| `apps/worker/` | **Stub chết** còn sót lại từ repo cũ. Worker thật là `apps/api/app/worker.py` |
| `apps/api/app/jobs.py` | `JobStore` in-memory, chỉ dùng ở giai đoạn Phase 01 |
| `openapi.tmp.json` | File sinh tự động, 400KB |
| `.ruff_cache/`, `__pycache__/` | cache |
| `apps/api/app/static/swagger/` | asset tĩnh của Swagger UI |
| `defenserflowdb/`, `docs/db/*.sql.gz` | dữ liệu dump |
