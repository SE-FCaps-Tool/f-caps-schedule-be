# 4. Vòng đời của một request

Đây là phần quan trọng nhất. Đọc xong bạn phải tự trace được API khác.

API được chọn: **`POST /api/v1/semesters`** — tạo một học kỳ mới. Nó đủ nhỏ để đọc hết, nhưng chứa **đầy đủ mọi pattern** của repo: check role, validate Pydantic, validate nghiệp vụ, advisory lock, transaction, ghi audit, bắt lỗi IntegrityError, đọc lại để trả về.

## 4.0 Sơ đồ tổng

```text
Client
  │ POST /api/v1/semesters
  │ Cookie: scheduler_session=...; scheduler_csrf=abc
  │ X-CSRF-Token: abc
  │ {"code":"sp26","name":"Spring 2026","start_date":"2026-01-05","end_date":"2026-04-24"}
  ▼
┌─ Bước 1 ── Uvicorn ─────────────────────────────────────────────┐
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 2 ── Middleware (main.py) ────────────────────────────────┐
│  legacy_contract_headers_middleware → csrf_guard → CORS         │
│  csrf_guard: POST + có cookie phiên → BẮT BUỘC khớp CSRF        │
│  ❌ không khớp → 403, dừng tại đây                              │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 3 ── Routing ─────────────────────────────────────────────┐
│  FastAPI khớp path với create_semester (master_data.py:1020)    │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 4 ── Dependencies (chạy TRƯỚC thân hàm) ──────────────────┐
│  get_db()           → mở Session SQLAlchemy                     │
│  get_current_user() → đọc cookie → SELECT auth_sessions → User  │
│  get_settings()     → object Settings (đã cache)                │
│  ❌ không đăng nhập → 401, dừng tại đây                         │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 5 ── Pydantic validate body ──────────────────────────────┐
│  SemesterCreate: kiểu, độ dài, chuẩn hoá code về CHỮ HOA        │
│  ❌ sai → 422, dừng tại đây (thân hàm chưa từng chạy)           │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 6 ── THÂN HÀM create_semester ────────────────────────────┐
│  6a  _require(user, "ADMIN", "MANAGER")        → 403 nếu sai    │
│  6b  kiểm tra end_date ≥ start_date            → 422            │
│  6c  kiểm tra 105 ≤ số ngày ≤ 120              → 422            │
│  6d  academic_year_for_start()  [services]                      │
│  6e  with db.begin():                          ← BẮT ĐẦU TX     │
│        pg_advisory_xact_lock(...)              ← xếp hàng       │
│        _actor_id()                                              │
│        INSERT INTO semesters ... RETURNING                      │
│        INSERT INTO audit_events ...                             │
│      ← THOÁT with = COMMIT (hoặc ROLLBACK nếu có exception)     │
│  6f  except IntegrityError → 409                                │
│  6g  semester_or_404() → đọc lại bản ghi đầy đủ                 │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 7 ── Serialize response ──────────────────────────────────┐
│  response_model=SemesterResponse → lọc/mô tả field              │
│  status_code=201                                                │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 8 ── Middleware chạy ngược ra ────────────────────────────┐
│  gắn X-Content-Type-Options, X-Frame-Options, CSP...            │
│  record_route_usage("POST", "/api/v1/semesters")                │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─ Bước 9 ── get_db() đóng Session (khối finally của generator) ──┐
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
                       Client nhận 201 + JSON
```

## 4.1 Bước 2 — Middleware CSRF

**File:** [apps/api/app/main.py](../../apps/api/app/main.py)
**Hàm:** `csrf_guard`

```python
@app.middleware("http")
async def csrf_guard(request: Request, call_next):
    mutating = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    cookie_session = request.cookies.get(settings.session_cookie_name)
    exempt = request.url.path in {"/api/v1/auth/login", "/api/v1/auth/logout"}
    if mutating and cookie_session and not exempt:
        csrf_cookie = request.cookies.get("scheduler_csrf")
        csrf_header = request.headers.get("X-CSRF-Token")
        if not _valid_csrf(settings, session_token=cookie_session,
                           cookie_value=csrf_cookie, header_value=csrf_header):
            response = JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})
        else:
            response = await call_next(request)
    else:
        response = await call_next(request)
    # ... gắn security header ...
    return response
```

- **Input:** object `Request` thô.
- **Xử lý:** POST/PUT/PATCH/DELETE mà có cookie phiên thì bắt buộc `cookie scheduler_csrf == header X-CSRF-Token`, đồng thời hash của header phải khớp `csrf_token_hash` lưu trong bảng `auth_sessions` (`_valid_csrf` tự mở một `Session` riêng để kiểm).
- **Output:** hoặc trả 403 luôn, hoặc gọi `call_next(request)` để đi tiếp.

> **Bẫy cho người mới:** nếu bạn dùng header test `X-Test-Session` mà **không** có cookie, `cookie_session` là `None` nên middleware bỏ qua CSRF. Đó là lý do test không cần lo CSRF.

## 4.2 Bước 3 — Routing

FastAPI khớp `POST /api/v1/semesters` với:

```python
# apps/api/app/routes/master_data.py:1019
@router.post("/semesters", status_code=status.HTTP_201_CREATED, response_model=SemesterResponse)
def create_semester(payload: SemesterCreate, db: Db, user: User, settings: SettingsDep) -> dict[str, object]:
```

Path đầy đủ = `prefix` của router (`/api/v1`) + path của decorator (`/semesters`).

## 4.3 Bước 4 — Dependencies

Ba alias khai báo một lần ở đầu file route, dùng lại cho mọi hàm:

```python
# apps/api/app/routes/master_data.py:78-80
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
```

Nhìn chữ ký `def create_semester(payload, db: Db, user: User, settings: SettingsDep)`, FastAPI hiểu: "trước khi chạy hàm này, hãy gọi `get_db()`, `get_current_user()`, `get_settings()`, rồi truyền kết quả vào".

### `get_db` — [apps/api/app/database.py](../../apps/api/app/database.py)

```python
@lru_cache(maxsize=4)
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)

def get_db() -> Generator[Session, None, None]:
    with Session(get_engine(get_settings().database_url)) as session:
        yield session
```

Hai khái niệm cần phân biệt:

- **Engine** = *pool* các kết nối TCP tới Postgres. Tạo một lần cho cả vòng đời process (`@lru_cache` đảm bảo điều đó). `pool_pre_ping=True` nghĩa là trước khi đưa một kết nối cũ ra dùng, SQLAlchemy ping thử — tránh lỗi "kết nối đã chết" sau khi DB restart.
- **Session** = phiên làm việc cho **một request**. Mượn kết nối từ pool, dùng xong trả lại.

`yield` nằm giữa: mọi thứ trước `yield` chạy trước handler, mọi thứ sau `yield` (ở đây là phần thoát `with`, tức `session.close()`) chạy sau khi response đã sinh xong. Đây là pattern chuẩn của FastAPI để dọn tài nguyên.

### `get_current_user` — [apps/api/app/auth.py](../../apps/api/app/auth.py)

```python
def get_current_user(request, test_session=Header(alias="X-Test-Session"), settings=..., db=...) -> CurrentUser:
    if settings.app_env == "test" and test_session:        # ← lối tắt CHỈ dùng khi APP_ENV=test
        role, _, account = test_session.partition(":")
        if role in test_roles:
            return CurrentUser(role=test_roles[role], account_id=int(account) if account.isdigit() else None)
    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token:
        token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        row = db.execute(text(
            "SELECT s.account_id, a.status, ar.role FROM auth_sessions s "
            "JOIN accounts a ON a.id = s.account_id JOIN account_roles ar ON ar.account_id = a.id "
            "WHERE s.token_hash = :token_hash AND s.revoked_at IS NULL AND s.expires_at > now() "
            "AND s.last_seen_at > now() - (:idle_minutes * interval '1 minute') "
            "ORDER BY ar.role LIMIT 1"
        ), {...}).mappings().one_or_none()
        if row is not None and str(row["status"]) == "ACTIVE":
            db.execute(text("UPDATE auth_sessions SET last_seen_at = now() WHERE token_hash = :token_hash"), {...})
            db.commit()
            return CurrentUser(role=str(row["role"]), status="active", account_id=row["account_id"])
    raise HTTPException(status_code=401, detail="Authentication required")
```

- **Input:** cookie `scheduler_session`.
- **Xử lý:** hash cookie bằng SHA-256, tìm trong `auth_sessions`; kiểm tra chưa thu hồi, chưa hết hạn tuyệt đối, chưa quá hạn nhàn rỗi; cập nhật `last_seen_at`.
- **Output:** dataclass `CurrentUser(role, status, account_id)` — chỉ 3 field.

> **Điểm rất quan trọng để trace đúng:** hàm này gọi `db.commit()`. Nghĩa là khi thân hàm route bắt đầu chạy, `Session` **đã có một transaction vừa được commit**. Chi tiết hệ quả ở mục 4.6.

## 4.4 Bước 5 — Pydantic validate

```python
# apps/api/app/routes/master_data.py:134
class SemesterCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=160)
    note: str | None = Field(default=None, max_length=1000)
    start_date: date
    end_date: date
    status: Literal["PLANNING", "ACTIVE"] = "ACTIVE"

    @field_validator("code")
    @classmethod
    def normalize_semester_code(cls, value: str) -> str:
        return normalize_code(value)      # ← gọi sang domain/master_data.py
```

- **Input:** JSON body.
- **Xử lý:** ép kiểu (chuỗi `"2026-01-05"` → object `date`), kiểm độ dài, chặn `status` ngoài 2 giá trị cho phép, rồi **chuẩn hoá**: `code` viết hoa và trim, `name` trim, `note` rỗng → `None`.
- **Output:** object `SemesterCreate` đã sạch, truyền vào tham số `payload`.
- **Nếu sai:** FastAPI ném `RequestValidationError` → handler ở `main.py` trả 422. Thân hàm chưa từng chạy.

Chú ý `normalize_semester_code` gọi `normalize_code()` từ [apps/api/app/domain/master_data.py](../../apps/api/app/domain/master_data.py). Đây là ví dụ đẹp: **layer schema tái dùng luật của layer domain**.

## 4.5 Bước 6a–6d — Kiểm tra quyền và nghiệp vụ

```python
_require(user, "ADMIN", "MANAGER")
```

`_require` là helper 3 dòng ở `master_data.py:120`:

```python
def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")
```

Đây là toàn bộ cơ chế **RBAC** (Role-Based Access Control) của repo — không có decorator, không có bảng permission. Mỗi handler tự gọi `_require` ở dòng đầu tiên.

Tiếp theo là hai luật nghiệp vụ, viết **thẳng trong route** chứ không tách ra domain:

```python
if payload.end_date < payload.start_date:
    raise HTTPException(422, detail={"code": "SEMESTER_DATE_INVALID", "message": "..."})

duration_days = (payload.end_date - payload.start_date).days + 1
if not settings.semester_min_duration_days <= duration_days <= settings.semester_max_duration_days:
    raise HTTPException(422, detail={"code": "SEMESTER_DURATION_INVALID", "message": "..."})
```

Ngưỡng 105–120 ngày lấy từ `Settings` chứ không hardcode — nghĩa là đổi được bằng biến môi trường.

Rồi tính năm học:

```python
academic_year = academic_year_for_start(payload.start_date)   # services/semester_queries.py
# start_date năm 2026 → "2026-2027"
```

## 4.6 Bước 6e — Transaction

Đây là pattern **lặp lại ở gần như mọi endpoint ghi dữ liệu** trong repo. Học thuộc nó.

```python
try:
    with db.begin():
        db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"),
                   {"lock_key": SEMESTER_LIFECYCLE_LOCK_KEY})
        actor_id = _actor_id(db, user)
        row = db.execute(text("""
            INSERT INTO semesters (code, name, note, start_date, end_date, academic_year,
                                   status, created_by, updated_by, updated_at)
            VALUES (:code, :name, :note, :start_date, :end_date, :academic_year,
                    :status, :actor_id, :actor_id, now())
            RETURNING id, code, name, note, start_date, end_date, academic_year, status,
                      created_at, updated_at, created_by, updated_by
        """), {**payload.model_dump(), "academic_year": academic_year,
               "status": payload.status, "actor_id": actor_id}).mappings().one()
        db.execute(text("""
            INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json)
            VALUES (:actor_id, 'SEMESTER_CREATED', 'semester', :entity_id, CAST(:after_json AS JSONB))
        """), {...})
except DomainError as exc:
    raise HTTPException(422, detail={"code": exc.code, "message": str(exc)}) from exc
except IntegrityError as exc:
    ...
```

Bóc từng mảnh:

**`with db.begin():`** — mở transaction. Thoát khối bình thường → `COMMIT`. Có exception bay ra → `ROLLBACK` rồi exception tiếp tục bay lên. Bạn **không bao giờ** phải gọi `commit()` hay `rollback()` bằng tay bên trong khối này.

**`pg_advisory_xact_lock(:lock_key)`** — *advisory lock* là khoá do ứng dụng tự định nghĩa, không gắn với bảng nào. Ở đây `SEMESTER_LIFECYCLE_LOCK_KEY = 918273645` (hằng số trong `services/semester_queries.py`). Mọi thao tác đụng vòng đời học kỳ đều lấy cùng con số này, nên chúng **xếp hàng tuần tự**. Hậu tố `xact` nghĩa là khoá tự nhả khi transaction kết thúc — không thể quên nhả.

Vì sao cần? Vì có ràng buộc "chỉ một học kỳ được ACTIVE". Nếu hai request tạo học kỳ ACTIVE chạy song song, cả hai đều kiểm tra "chưa có ai ACTIVE" cùng lúc rồi cả hai cùng insert. Khoá này chặn tình huống đó. (Có thêm partial unique index `uq_active_semester` làm lưới an toàn cuối cùng ở tầng DB.)

**Tham số `:code`, `:name`** — SQLAlchemy gửi câu lệnh và giá trị **tách rời** xuống Postgres. Chuỗi độc hại không bao giờ được ghép vào SQL → miễn nhiễm SQL injection. **Tuyệt đối không** dùng f-string để nhét giá trị vào câu SQL.

**`RETURNING ...`** — tính năng của Postgres: INSERT xong trả luôn dòng vừa tạo, khỏi phải SELECT lần nữa.

**`.mappings().one()`** — `.mappings()` biến kết quả thành dict-like (truy cập `row["id"]`); `.one()` khẳng định đúng 1 dòng, sai số lượng thì ném exception. Họ hàng: `.one_or_none()` (0 hoặc 1), `.all()` (danh sách), `.scalar_one_or_none()` (lấy đúng 1 giá trị của cột đầu).

**`INSERT INTO audit_events`** — mọi thao tác ghi đều để lại vết, **cùng transaction** với dữ liệu. Rollback thì audit cũng biến mất → nhật ký không bao giờ ghi việc chưa xảy ra.

### Cạm bẫy `db.begin()` phải biết

**[Xác nhận từ code]** — `CLAUDE.md` cảnh báo và code chứng minh: một câu `db.execute(SELECT ...)` chạy *bên ngoài* `with db.begin():` sẽ **tự động mở** một transaction ngầm. Khi đó `with db.begin():` phía sau sẽ nổ lỗi `A transaction is already begun`.

```python
# ❌ SAI
row = db.execute(text("SELECT ...")).one()   # tự mở transaction ngầm
with db.begin():                              # 💥 InvalidRequestError
    ...

# ✅ ĐÚNG — cách 1: đọc luôn bên trong
with db.begin():
    row = db.execute(text("SELECT ...")).one()
    db.execute(text("UPDATE ..."))

# ✅ ĐÚNG — cách 2: đóng transaction ngầm trước
row = db.execute(text("SELECT ...")).one()
db.rollback()
with db.begin():
    ...
```

Nhắc lại mục 4.3: `get_current_user` đã gọi `db.commit()` rồi, nên khi vào handler, session ở trạng thái "sạch". Nhưng chỉ cần bạn thêm một câu đọc trước `with db.begin():` là dính bẫy ngay.

## 4.7 Bước 6f — Dịch lỗi DB sang HTTP

```python
except IntegrityError as exc:
    constraint = str(getattr(exc, "orig", exc))
    if "uq_active_semester" in constraint:
        raise HTTPException(409, detail={"code": "ACTIVE_SEMESTER_EXISTS",
                                         "message": "Only one semester may be ACTIVE."}) from exc
    raise HTTPException(409, detail={"code": "DATA_DUPLICATE",
                                     "message": "Semester code already exists."}) from exc
```

`IntegrityError` là lỗi SQLAlchemy khi Postgres từ chối vì vi phạm ràng buộc (unique, foreign key, check). Route **đọc tên constraint trong thông điệp lỗi** để đoán chuyện gì xảy ra và trả mã lỗi phù hợp.

**[Suy luận]** Cách này mong manh: đổi tên index trong migration mà quên sửa chuỗi ở route thì lỗi 409 sẽ trả sai mã. `services/committee_service.py` làm chuẩn hơn — nó kiểm tra `diag.constraint_name` từ psycopg thay vì dò chuỗi:

```python
cause = getattr(exc, "orig", None)
if not isinstance(cause, ForeignKeyViolation):
    return False
diag = getattr(cause, "diag", None)
return (getattr(diag, "constraint_name", None) or "") == ROUND_COMMITTEE_FK
```

Hãy theo cách của `committee_service.py`.

## 4.8 Bước 6g–7 — Đọc lại và serialize

```python
return semester_or_404(db, int(row["id"]))
```

Handler **không** trả `row` vừa `RETURNING`, mà gọi `semester_or_404()` để đọc lại bản ghi qua đúng query dùng cho endpoint GET.

Vì sao? Để `POST /semesters` và `GET /semesters/{id}` trả **cùng một hình dạng JSON** — bao gồm cả các field tính toán như thông tin người tạo (`semester_rows` có join sang `accounts` để lấy email/display_name). Một chỗ định nghĩa hình dạng, không lệch nhau.

Sau đó FastAPI dùng `response_model=SemesterResponse` (trong `response_models.py`) để mô tả kiểu cho Swagger. Vì model đặt `extra="allow"`, field lạ không bị chặn — nó **mô tả** chứ chưa thực sự **kiểm soát** đầu ra.

## 4.9 So sánh nhanh: cùng nghiệp vụ, khác vỏ

Nếu frontend gọi route "target" thay vì route cũ, thêm đúng một lớp:

```text
POST /api/v1/rounds/{id}/schedules/generate     ← target route
   │
   ├─ target_schedule_contract.generate_target_schedule()
   │     └─ gọi thẳng schedule_operations.run_scheduler(round_id, payload, db, user)
   │           └─ ...toàn bộ logic thật...
   │     └─ success_payload({...})   → bọc thành {"data": {...}}
   │
   └─ nếu lỗi: exception handler thấy tag "target-schedules"
         → trả {"error": {"code": ..., "message": ..., "details": {}}}
           thay vì {"detail": ...}
```

## 4.10 Công thức trace bất kỳ API nào

1. **Tìm handler:** `grep -rn '"/duong-dan"' apps/api/app/routes/`
2. **Xem nó cần gì:** đọc chữ ký hàm — `db`, `user`, `payload`, `settings`?
3. **Tìm schema đầu vào:** class Pydantic đó khai báo ngay trong cùng file, cuộn lên trên.
4. **Đọc dòng `_require(...)`:** biết ngay ai được gọi.
5. **Tìm `with db.begin():`:** mọi thứ trong đó là một transaction nguyên tử.
6. **Nhìn các `import` đầu file:** `from app.domain...` là luật nghiệp vụ, `from app.services...` là SQL dùng chung — mở tiếp nếu cần.
7. **Xem câu `return`:** trả dict thô, hay gọi hàm `*_or_404` để đọc lại?
8. **Nếu là route `target_*`:** tìm hàm gốc nó gọi lại và trace tiếp ở đó.

Thử ngay với: `POST /api/v1/groups/{group_id}/leader` (`master_data.py:1000`) — ngắn, đủ pattern, và có một chi tiết thú vị: route `target_group_project.py` bọc nó lại và **đổi mã lỗi** `LEADER_MEMBER_NOT_FOUND` thành `LEADER_NOT_ACTIVE_MEMBER`.
