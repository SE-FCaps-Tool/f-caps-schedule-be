# 7. Error handling và Logging

## 7.1 Bản đồ các loại lỗi

```text
┌─────────────────┬──────────────────────┬────────────┬────────────────────────┐
│ Loại exception  │ Ném từ đâu           │ HTTP status│ Ai bắt                 │
├─────────────────┼──────────────────────┼────────────┼────────────────────────┤
│ DomainError     │ app/domain/*.py      │ 409 hoặc   │ Route, bằng try/except │
│                 │ app/services/*.py    │ 422        │ (KHÔNG có handler chung)│
├─────────────────┼──────────────────────┼────────────┼────────────────────────┤
│ HTTPException   │ route, service       │ tự chỉ định│ handler trong main.py  │
├─────────────────┼──────────────────────┼────────────┼────────────────────────┤
│ IntegrityError  │ SQLAlchemy (từ Postgres)│ 409     │ Route, bằng try/except │
├─────────────────┼──────────────────────┼────────────┼────────────────────────┤
│ RequestValidation-│ FastAPI/Pydantic   │ 422        │ handler trong main.py  │
│ Error           │                      │            │                        │
├─────────────────┼──────────────────────┼────────────┼────────────────────────┤
│ Exception khác  │ bất cứ đâu           │ 500        │ FastAPI mặc định       │
└─────────────────┴──────────────────────┴────────────┴────────────────────────┘
```

## 7.2 `DomainError` — exception nghiệp vụ

**File:** [apps/api/app/domain/errors.py](../../apps/api/app/domain/errors.py) — cả file có 11 dòng:

```python
class DomainError(ValueError):
    """A rejected domain operation with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class AuthorizationError(DomainError):
    pass
```

Điểm mấu chốt là **`code`** — chuỗi ổn định, máy đọc được, như `GROUP_SIZE_INVALID`. Frontend so sánh `code` để hiển thị đúng thông báo tiếng Việt; `message` chỉ dành cho developer và có thể đổi bất cứ lúc nào mà không phá frontend.

Cách ném — [apps/api/app/domain/master_data.py](../../apps/api/app/domain/master_data.py):

```python
def validate_group_members(members):
    if not 4 <= len(members) <= 5:
        raise DomainError("GROUP_SIZE_INVALID", "A new group must have 4 to 5 students.")
    codes = [normalize_code(m.get("student_code", "")) for m in members]
    if len(set(codes)) != len(codes):
        raise DomainError("MEMBERSHIP_DUPLICATE", "A student cannot appear twice in one group.")
    leaders = [m for m in members if m.get("role", "MEMBER").upper() == "LEADER"]
    if len(leaders) != 1:
        raise DomainError("LEADER_REQUIRED", "A group must have exactly one active Leader.")
    return True
```

**Vì sao domain ném `DomainError` chứ không ném thẳng `HTTPException`?**

Vì `app/domain/` **không được biết HTTP tồn tại**. Nếu domain import `fastapi`, ba thứ sau sẽ mất:
1. Không test được luật nghiệp vụ mà không dựng cả web app.
2. Không tái dùng được luật đó trong script CLI ở `tools/` hay trong worker.
3. Câu hỏi "tại sao trả 422 chứ không 409" bị lẫn vào giữa logic nghiệp vụ.

Việc dịch `DomainError` → HTTP status là **quyết định của tầng route**, và ranh giới đó phải giữ.

## 7.3 Route dịch lỗi

Đây là pattern chuẩn, lặp lại khắp repo:

```python
# apps/api/app/routes/master_data.py — create_semester
try:
    with db.begin():
        ...
except DomainError as exc:
    raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
except IntegrityError as exc:
    constraint = str(getattr(exc, "orig", exc))
    if "uq_active_semester" in constraint:
        raise HTTPException(409, detail={"code": "ACTIVE_SEMESTER_EXISTS",
                                         "message": "Only one semester may be ACTIVE."}) from exc
    raise HTTPException(409, detail={"code": "DATA_DUPLICATE",
                                     "message": "Semester code already exists."}) from exc
```

Chú ý `detail` là **dict**, không phải chuỗi:

```python
detail={"code": "SEMESTER_DURATION_INVALID", "message": "..."}
```

Đây là convention xuyên suốt. Body trả về sẽ là:

```json
{ "detail": { "code": "SEMESTER_DURATION_INVALID", "message": "..." } }
```

Có một số chỗ vẫn còn `detail="Insufficient permission"` dạng chuỗi thuần (`_require`) — di sản cũ, không nhất quán.

**`from exc`** cuối câu `raise` giữ nguyên chuỗi nguyên nhân (`__cause__`), nên traceback hiển thị đầy đủ cả lỗi gốc. Luôn viết nó.

**HTTP status dùng ở đâu:**

| Status | Khi nào |
|---|---|
| 400 | Payload sai về mặt cấu trúc |
| 401 | Chưa đăng nhập |
| 403 | Đã đăng nhập nhưng sai role, hoặc CSRF sai |
| 404 | Không tìm thấy tài nguyên |
| 409 | Xung đột với trạng thái hiện tại (trùng, đã ACTIVE, đang được dùng) |
| 422 | Vi phạm luật nghiệp vụ hoặc validate Pydantic |
| 429 | Bị chặn vì thử đăng nhập quá nhiều |

## 7.4 Global exception handler — và chuyện hai định dạng lỗi

**File:** [apps/api/app/main.py](../../apps/api/app/main.py)

Repo đang trong quá trình chuyển hợp đồng API, nên **tồn tại song song hai định dạng lỗi**. Hàm quyết định dùng cái nào:

```python
def _is_target_route(request: Request) -> bool:
    """True when the matched route belongs to a ``target_*`` contract router."""
    route = request.scope.get("route")
    tags = getattr(route, "tags", None) or []
    return any(str(tag).startswith("target-") for tag in tags)
```

Nó đọc **tag** của route. Router `target_*` khai báo `tags=["target-schedules"]`, router cũ khai báo `tags=["management"]`.

```python
@app.exception_handler(HTTPException)
async def _target_http_exception_handler(request, exc) -> JSONResponse:
    if not _is_target_route(request):
        return JSONResponse(status_code=exc.status_code,
                            content={"detail": exc.detail}, headers=exc.headers)
    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code", "HTTP_ERROR"))
        message = str(detail.get("message", code))
        raw_details = detail.get("details")
        details = raw_details if isinstance(raw_details, dict) else {}
    else:
        code, message, details = "HTTP_ERROR", str(detail), {}
    return JSONResponse(status_code=exc.status_code,
                        content=error_payload(code, message, details=details),
                        headers=exc.headers)
```

Kết quả — **cùng một lỗi, hai hình dạng JSON**:

```json
// Route CŨ  (tags=["management"])
{ "detail": { "code": "SEMESTER_NOT_FOUND", "message": "Semester does not exist." } }

// Route TARGET  (tags=["target-rounds"])
{ "error": { "code": "SEMESTER_NOT_FOUND", "message": "Semester does not exist.", "details": {} } }
```

Phong bì `error` do `error_payload()` trong [apps/api/app/api_contract.py](../../apps/api/app/api_contract.py) sinh ra:

```python
def error_payload(code, message, *, details=None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": dict(details or {})}}
```

Tương tự với lỗi validate:

```python
@app.exception_handler(RequestValidationError)
async def _target_validation_exception_handler(request, exc):
    if not _is_target_route(request):
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})
    return JSONResponse(status_code=422, content=error_payload(
        "VALIDATION_ERROR", "Request validation failed.",
        details={"errors": jsonable_encoder(exc.errors())}))
```

**Vì sao lại làm thế này?** Vì đổi định dạng lỗi là **breaking change** với frontend. Không thể đổi hết trong một đêm. Cách này cho phép migrate từng route một: khi một endpoint được "nâng cấp" sang router `target_*`, frontend chuyển sang gọi endpoint mới và nhận định dạng mới; endpoint cũ vẫn sống cho tới khi không còn ai gọi.

Có cả cơ chế **đếm xem route cũ còn ai gọi không**:

```python
# main.py
record_route_usage(request.method, request.url.path)      # services/route_telemetry.py
for key, value in legacy_contract_headers(request.url.path).items():
    response.headers.setdefault(key, value)               # gắn header Deprecation
```

**[Nhận định]** Đây là chiến lược migration đúng bài. Nhưng nó cũng có nghĩa là **bạn phải luôn biết mình đang làm việc với nhóm route nào**. Đọc `tags=` ở dòng `APIRouter(...)` đầu file trước khi viết bất cứ thứ gì.

## 7.5 Trace một lỗi thật từ đầu tới cuối

Kịch bản: Manager tạo học kỳ nhưng mã học kỳ đã tồn tại.

```text
Client
  │ POST /api/v1/semesters   {"code": "SP26", ...}
  ▼
route create_semester  (master_data.py:1020)
  │ với db.begin():
  │     INSERT INTO semesters (code, ...) VALUES ('SP26', ...)
  ▼
PostgreSQL
  │ ❌ vi phạm UNIQUE constraint trên cột code
  │ ERROR: duplicate key value violates unique constraint "semesters_code_key"
  ▼
psycopg  → ném UniqueViolation
  ▼
SQLAlchemy → bọc lại thành IntegrityError
  ▼
`with db.begin():` thấy exception → ROLLBACK
  │  ★ dòng audit_events cũng bị rollback — không ghi việc chưa xảy ra
  ▼
except IntegrityError as exc:              (master_data.py:1092)
  │ constraint = str(exc.orig)
  │ "uq_active_semester" không có trong chuỗi
  │ → raise HTTPException(409, detail={"code": "DATA_DUPLICATE",
  │                                    "message": "Semester code already exists."})
  ▼
_target_http_exception_handler             (main.py)
  │ _is_target_route(request)?  tag là "management" → KHÔNG phải target
  │ → JSONResponse(409, {"detail": {"code": "DATA_DUPLICATE", "message": "..."}})
  ▼
middleware csrf_guard (chiều ra) → gắn X-Content-Type-Options, X-Frame-Options, CSP...
  ▼
Client nhận:
  HTTP/1.1 409 Conflict
  { "detail": { "code": "DATA_DUPLICATE", "message": "Semester code already exists." } }
```

Bốn bài học rút ra:

1. **Rollback là tự động.** Không cần `try/except` để gọi `db.rollback()` — `with db.begin():` lo hết.
2. **Audit không bao giờ nói dối.** Vì nằm cùng transaction.
3. **Lỗi được dịch tại đúng biên giới.** Postgres nói tiếng của Postgres, HTTP nói tiếng của HTTP, route là phiên dịch viên.
4. **Định dạng response phụ thuộc tag của route**, không phụ thuộc loại lỗi.

## 7.6 Logging — sự thật khó chịu

**[Xác nhận từ code]** Chạy lệnh này trên toàn bộ `apps/api/app/`:

```powershell
grep -rn "import logging|getLogger|logger\." apps/api/app/
```

**Kết quả: không có kết quả nào.**

Nghĩa là:

- **Không có** cấu hình logging.
- **Không có** logger nào trong bất cứ layer nào.
- **Không có** correlation/request id để nối các dòng log của cùng một request.
- **Không có** structured logging (JSON log).
- Thứ duy nhất bạn có là **access log mặc định của Uvicorn** (`INFO: 127.0.0.1 - "POST /api/v1/semesters HTTP/1.1" 409`) và **traceback in ra stderr** khi có lỗi 500.

**Vậy thay thế bằng gì?** Repo dùng **bảng `audit_events`** làm nhật ký nghiệp vụ. Nó tốt hơn log ở chỗ: có transaction, truy vấn được bằng SQL, không bao giờ ghi việc bị rollback. Nhưng nó **không thay thế được** log kỹ thuật — nó không ghi lại độ trễ, lỗi 500, hay câu SQL nào chậm.

**[Nhận định — technical debt rõ ràng]** Với một hệ thống đã có 174 endpoint và một CP-SAT solver chạy hàng chục giây, việc không có logging là khoảng trống thật sự. Khi có sự cố production, công cụ điều tra duy nhất là `audit_events` và access log của Uvicorn.

**Điều này ảnh hưởng gì tới bạn ngay hôm nay?**

- Debug bằng cách chạy **test**, không phải bằng cách đọc log.
- `docker compose logs -f api` chỉ cho bạn access log và traceback.
- Nếu bạn muốn thêm `print()` để debug — được, nhưng **xoá trước khi commit**.
- Nếu bạn định thêm logging thật, đó là một thay đổi kiến trúc: hãy bàn với team, đừng tự ý rắc `logging.info` rải rác.

## 7.7 Anti-pattern cần tránh

```python
# ❌ Domain biết tới HTTP — phá vỡ ranh giới layer
# trong app/domain/xxx.py
from fastapi import HTTPException
raise HTTPException(422, ...)

# ❌ Nuốt lỗi
try:
    ...
except Exception:
    pass

# ❌ detail là chuỗi trần, frontend không có code để so
raise HTTPException(422, detail="Sai rồi")

# ❌ Mất chuỗi nguyên nhân
raise HTTPException(409, detail={...})          # thiếu "from exc"

# ✅ Đúng
raise HTTPException(409, detail={"code": "XXX_INVALID", "message": "..."}) from exc
```

Có đúng **một** chỗ được phép bắt `Exception` trần — worker, vì một job hỏng không được làm chết cả vòng lặp:

```python
# apps/api/app/services/notification_dispatcher.py
except Exception:  # noqa: BLE001 - a failed delivery must be persisted and retried.
    db.execute(text("UPDATE outbox_jobs SET status = 'FAILED' WHERE id = :id"), {"id": job["id"]})
```

Chú ý: nó **ghi trạng thái thất bại xuống DB** rồi mới đi tiếp — không im lặng nuốt lỗi.
