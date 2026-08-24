# 3. Kiến trúc theo layer

## 3.1 Trước hết: layer nào KHÔNG có ở đây

Nhiều tài liệu backend dạy mô hình 4 tầng "Controller → Service → Repository → Model". Repo này **không** theo mô hình đó. Nói rõ ngay để bạn không đi tìm những file không tồn tại:

| Khái niệm | Có trong repo? | Sự thật |
|---|---|---|
| Controller / Router | ✅ Có | `apps/api/app/routes/*.py` |
| Schema / DTO (dữ liệu vào) | ✅ Có | Class Pydantic khai báo **ngay trong file route** |
| DTO (dữ liệu ra) | ⚠️ Một phần | `apps/api/app/response_models.py`, nhưng dùng `extra="allow"` nên rất lỏng |
| Service layer | ⚠️ Một phần | `services/` chỉ chứa helper dùng chung, **không** phải nơi chứa toàn bộ use case |
| Domain layer | ✅ Có, thật sự thuần | `apps/api/app/domain/*.py` |
| **Repository layer** | ❌ **KHÔNG CÓ** | Không có class/module nào đứng ra bọc truy cập dữ liệu |
| **Model / Entity (ORM)** | ❌ **KHÔNG CÓ** | Không có `declarative_base`. Bảng chỉ tồn tại trong migration |
| Infrastructure | ⚠️ Rải rác | `database.py`, `config.py`, `infra/docker/` |
| Dependency Injection | ✅ Có | Cơ chế `Depends` của FastAPI — xem [09-dependency-injection.md](09-dependency-injection.md) |
| Middleware | ✅ Có | 2 cái, khai báo trong `main.py` |
| Exception handler | ✅ Có | 2 cái, khai báo trong `main.py` |
| Unit of Work | ⚠️ Ngầm | `with db.begin():` chính là unit of work thủ công |

**Đừng đi tìm** `repositories/`, `models/`, `entities/`, `schemas/`, `usecases/`. Chúng không có.

## 3.2 Sơ đồ layer thật của repo này

```text
              ┌───────────────────────────────────────────────────┐
   HTTP  ───► │ Uvicorn (ASGI server)                             │
              └──────────────────────┬────────────────────────────┘
                                     ▼
              ┌───────────────────────────────────────────────────┐
              │ MIDDLEWARE  (apps/api/app/main.py)                │
              │  1. legacy_contract_headers_middleware            │
              │  2. csrf_guard         ← chặn POST thiếu CSRF     │
              │  3. CORSMiddleware                                │
              └──────────────────────┬────────────────────────────┘
                                     ▼
              ┌───────────────────────────────────────────────────┐
              │ DEPENDENCIES  (FastAPI Depends)                   │
              │  get_db()           → app/database.py             │
              │  get_current_user() → app/auth.py                 │
              │  get_settings()     → app/config.py               │
              └──────────────────────┬────────────────────────────┘
                                     ▼
              ┌───────────────────────────────────────────────────┐
              │ SCHEMA VALIDATION  (Pydantic, khai báo trong route)│
              │  VD: class SemesterCreate(BaseModel)              │
              └──────────────────────┬────────────────────────────┘
                                     ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │ ROUTE HANDLER  (apps/api/app/routes/*.py)                       │
    │  ★ Ở repo này handler kiêm luôn Controller + Service + Repository│
    │                                                                  │
    │   _require(user, "ADMIN", "MANAGER")   ← check role             │
    │   with db.begin():                     ← mở transaction         │
    │       db.execute(text("SELECT ..."))   ← truy vấn thẳng         │
    │       validate_xxx(...)                ← gọi domain             │
    │       db.execute(text("INSERT ..."))                            │
    │       db.execute(text("INSERT INTO audit_events ..."))          │
    └───────┬─────────────────┬──────────────────┬────────────────────┘
            │                 │                  │
            ▼                 ▼                  ▼
    ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐
    │ domain/      │  │ services/     │  │ scheduler/       │
    │ rule thuần   │  │ SQL dùng chung│  │ OR-Tools CP-SAT  │
    │ KHÔNG có db  │  │ NHẬN db vào   │  │ tính toán thuần  │
    └──────────────┘  └───────┬───────┘  └──────────────────┘
                              │
                              ▼
                  ┌────────────────────────────┐
                  │ SQLAlchemy Core            │
                  │ Session + Engine (pool)    │
                  └────────────┬───────────────┘
                               ▼
                  ┌────────────────────────────┐
                  │ PostgreSQL 16              │
                  └────────────────────────────┘
```

## 3.3 Giải thích từng khái niệm + file thật

### Router (Controller)

**Là gì:** file khai báo "URL nào ứng với hàm Python nào".

**Ở đâu:** mỗi file trong `apps/api/app/routes/` tạo một `APIRouter`, rồi `main.py` gắn tất cả vào app.

```python
# apps/api/app/routes/master_data.py, dòng 77
router = APIRouter(prefix="/api/v1", tags=["management"])
```

```python
# apps/api/app/main.py — gắn router
app.include_router(master_data_router)
app.include_router(manager_extensions_router)
...
```

`prefix="/api/v1"` nghĩa là mọi path khai báo trong file đó tự động có tiền tố `/api/v1`. `tags` dùng để nhóm trong Swagger — **và ở repo này tag còn có tác dụng thật**: exception handler kiểm tra tag có bắt đầu bằng `target-` không để quyết định định dạng lỗi (xem [07-errors-logging.md](07-errors-logging.md)).

### Schema / DTO

**Là gì:** class mô tả hình dạng dữ liệu, để framework tự kiểm tra hộ. "Field `email` phải là chuỗi dài 3–320 ký tự" — nếu client gửi sai, FastAPI trả 422 trước khi hàm của bạn chạy.

**Ở đâu — schema đầu vào:** khai báo **ngay trong file route**, không có thư mục riêng.

```python
# apps/api/app/routes/auth_routes.py
class LoginPayload(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)
```

Có cả validator phức tạp hơn, ví dụ trong `routes/target_group_project.py`:

```python
@model_validator(mode="after")
def supervisors_differ(self):
    if self.co_supervisor_id is not None and str(self.co_supervisor_id) == str(self.main_supervisor_id):
        raise ValueError("mainSupervisorId and coSupervisorId must differ")
    return self
```

**Ở đâu — schema đầu ra:** [apps/api/app/response_models.py](../../apps/api/app/response_models.py), 1028 dòng.

Đọc docstring đầu file — nó tự thú nhận rất thẳng thắn:

> "The application historically returned raw SQL mapping dictionaries. That is fine at runtime, but `list[dict[str, object]]` gives FastAPI no field information and Swagger renders `additionalProp1`. These models describe the public response contract while keeping `extra='allow'` during the transition."

Nghĩa là: model response được **thêm vào sau**, để Swagger đẹp. Vì `extra="allow"`, nếu SQL trả thêm cột lạ thì Pydantic vẫn cho qua. **Đây vừa tiện vừa nguy hiểm** — nó không chặn được việc rò rỉ cột nhạy cảm ra API. Xem [12-junior-warnings.md](12-junior-warnings.md).

### Service / Use Case

**Là gì (lý thuyết):** nơi chứa một thao tác nghiệp vụ hoàn chỉnh, độc lập với HTTP.

**Ở repo này:** phần lớn use case nằm **trong chính hàm route**. Thư mục `services/` chỉ chứa những đoạn dùng lại nhiều nơi.

Có ngoại lệ đáng học: `committee_service.py` và `timeframe_service.py` gần với service layer đúng nghĩa. So sánh:

```python
# routes/committee_contract.py — router mỏng, chỉ ủy quyền
# services/committee_service.py — 414 dòng, chứa CRUD + xử lý lỗi FK
```

vs.

```python
# routes/master_data.py — 2097 dòng, tự làm hết
```

**[Suy luận]** Hai file service kia là code viết sau, theo hướng team đang muốn đi. Nếu bạn viết tính năng mới, hãy noi theo `committee_service.py` chứ đừng noi theo `master_data.py`.

### Domain

**Là gì:** quy tắc nghiệp vụ tinh khiết. Không biết HTTP là gì, không biết DB là gì.

**Ở đâu:** `apps/api/app/domain/`. Kiểm chứng nhanh: mở [apps/api/app/domain/master_data.py](../../apps/api/app/domain/master_data.py) — file chỉ import đúng một thứ là `DomainError`.

Layer này tồn tại vì hai lý do:
1. Test cực nhanh, không cần Docker.
2. Luật nghiệp vụ nằm một chỗ, không rải khắp SQL.

### Repository — KHÔNG TỒN TẠI

**Là gì (lý thuyết):** class như `SemesterRepository` với các method `find_by_id`, `save`, để route không phải biết SQL.

**Thực tế ở đây:** route viết SQL trực tiếp.

```python
# apps/api/app/routes/master_data.py — không qua lớp trung gian nào
row = db.execute(
    text("INSERT INTO semesters (code, name, ...) VALUES (:code, :name, ...) RETURNING id, code, ..."),
    {**payload.model_dump(), "academic_year": academic_year, "actor_id": actor_id},
).mappings().one()
```

Thứ **gần nhất** với repository là vài hàm trong `services/semester_queries.py` (`semester_or_404`, `semester_rows`) — nhưng chúng là hàm rời, không phải class, và không phủ hết mọi bảng.

**Hệ quả thực dụng:** muốn tìm mọi chỗ đụng vào bảng `rounds`, bạn không mở `RoundRepository` — bạn `grep -rn "FROM rounds" apps/api/app/`.

### Model / Entity — KHÔNG TỒN TẠI

Không có class Python nào đại diện cho một dòng dữ liệu. Kết quả truy vấn là `dict`-like:

```python
row = db.execute(text("SELECT id, status FROM rounds WHERE id = :id"), {...}).mappings().one()
row["status"]   # đúng
row.status      # SAI — sẽ lỗi
```

`.mappings()` biến kết quả thành dạng dict truy cập bằng tên cột. Không có `.mappings()` thì kết quả là tuple, truy cập bằng chỉ số: `row[0]`.

Các dataclass trong `app/scheduler/models.py` (`RoundInput`, `Candidate`) là **cấu trúc dữ liệu để tính toán**, không ánh xạ xuống bảng.

### Infrastructure

Rải rác, không gom một chỗ:

| Việc | File |
|---|---|
| Tạo engine (pool kết nối) | `apps/api/app/database.py` |
| Đọc cấu hình | `apps/api/app/config.py` |
| Đóng gói container | `infra/docker/api.Dockerfile`, `docker-compose.yml` |
| Migration | `apps/api/migrations/` |
| Bootstrap DB lúc khởi động | `tools/bootstrap_database.py` |

### Middleware

**Là gì:** hàm chạy *bao quanh* mọi request, trước và sau handler. Dùng cho việc chung: bảo mật, log, header.

**Ở đâu:** `apps/api/app/main.py`, hai cái tự viết + một cái của FastAPI.

```python
@app.middleware("http")
async def csrf_guard(request, call_next):
    mutating = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    ...  # nếu thiếu/sai X-CSRF-Token → 403, không cho vào handler
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    ...
```

```python
@app.middleware("http")
async def legacy_contract_headers_middleware(request, call_next):
    response = await call_next(request)
    record_route_usage(request.method, request.url.path)   # đếm route cũ còn ai gọi
    for key, value in legacy_contract_headers(request.url.path).items():
        response.headers.setdefault(key, value)            # gắn header Deprecation
    return response
```

**Thứ tự chạy quan trọng:** FastAPI chạy middleware theo **thứ tự ngược** với thứ tự khai báo. Khai báo CORS → csrf_guard → legacy_headers, nên request đi vào theo chiều: legacy_headers → csrf_guard → CORS → handler.

### Exception Handler

Xem chi tiết ở [07-errors-logging.md](07-errors-logging.md). Tóm tắt: hai handler trong `main.py` bắt `HTTPException` và `RequestValidationError`, rồi chọn định dạng JSON tuỳ theo route thuộc nhóm cũ hay nhóm `target-`.

## 3.4 Vậy nên tóm lại luồng đúng là gì?

Sơ đồ "chuẩn sách vở" **không đúng** với repo này:

```text
❌ Router → Service → Repository → ORM → Database
```

Sơ đồ đúng:

```text
✅ Middleware → Depends → Pydantic → Route handler ─┬─► domain/    (rule thuần)
                                                     ├─► services/  (SQL dùng chung)
                                                     ├─► scheduler/ (thuật toán)
                                                     └─► text(SQL) ─► PostgreSQL
```

Khi ai đó hỏi "logic nằm ở đâu", câu trả lời trung thực là: **trong hàm route**, trừ phần luật thuần đã tách ra `domain/` và phần dùng chung đã tách ra `services/`.
