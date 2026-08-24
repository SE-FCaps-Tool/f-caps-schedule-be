# 9. Dependency Injection

## 9.1 Dependency Injection là gì?

**Không** tự tạo thứ mình cần — mà **khai báo** mình cần gì, rồi để framework đưa vào.

```python
# ❌ KHÔNG dùng DI — hàm tự tạo mọi thứ
def create_semester(payload):
    engine = create_engine("postgresql://...")   # tự tạo kết nối
    session = Session(engine)                    # tự tạo session
    user = parse_cookie_somehow()                # tự đọc cookie
    ...
    session.close()                              # tự nhớ đóng
```

```python
# ✅ Dùng DI — chỉ khai báo nhu cầu
def create_semester(payload: SemesterCreate, db: Db, user: User, settings: SettingsDep):
    ...        # db, user, settings đã sẵn sàng; đóng session cũng có người lo
```

Ba cái lợi cụ thể trong repo này:

1. **Không lặp code** — 174 endpoint không phải tự viết đoạn mở/đóng session.
2. **Test dễ** — thay thế được `get_db` bằng bản giả qua `app.dependency_overrides`.
3. **Dọn tài nguyên tự động** — session luôn được đóng, kể cả khi handler ném exception.

## 9.2 Repo này dùng DI của FastAPI, không dùng thư viện ngoài

**[Xác nhận từ code]** Không có `dependency-injector`, `punq`, `wired`, hay bất kỳ IoC container nào trong `pyproject.toml`. Toàn bộ DI là `Depends` sẵn có của FastAPI.

Chỉ có **ba dependency**, tất cả đều dùng ở mọi nơi:

| Dependency | File | Trả về | Vòng đời |
|---|---|---|---|
| `get_db` | `apps/api/app/database.py` | `Session` | Mỗi request một cái, tự đóng |
| `get_current_user` | `apps/api/app/auth.py` | `CurrentUser` | Mỗi request |
| `get_settings` | `apps/api/app/config.py` | `Settings` | **Singleton** cho cả process (`@lru_cache`) |

## 9.3 Cú pháp: alias `Annotated`

Đầu mỗi file route, cùng một ba dòng lặp lại:

```python
# apps/api/app/routes/master_data.py:78-80
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
```

Đọc `Annotated[Session, Depends(get_db)]` như sau: *"kiểu của nó là `Session`; cách lấy nó là gọi `get_db`"*. Phần đầu để type checker và IDE hiểu, phần sau để FastAPI biết phải làm gì.

Dùng:

```python
def create_semester(payload: SemesterCreate, db: Db, user: User, settings: SettingsDep):
```

Không có alias thì phải viết dài dòng ở **mọi** hàm:

```python
def create_semester(payload: SemesterCreate,
                    db: Annotated[Session, Depends(get_db)],
                    user: Annotated[CurrentUser, Depends(get_current_user)]):
```

Ba dòng alias tiết kiệm việc đó cho 40 handler trong một file.

## 9.4 Sơ đồ đồ thị phụ thuộc thật của repo

Sơ đồ "Router → Service → Repository → DB Session" trong tài liệu lý thuyết **không đúng** ở đây. Đồ thị thật:

```text
        ┌──────────────────────────────────────────────────┐
        │  Route handler                                   │
        │  create_semester(payload, db, user, settings)    │
        └───┬──────────┬────────────┬──────────────────────┘
            │          │            │
      cần db│    cần user│    cần settings
            ▼          ▼            ▼
   ┌────────────┐  ┌─────────────────┐  ┌────────────────┐
   │ get_db()   │  │get_current_user()│  │ get_settings() │
   └─────┬──────┘  └───┬────────┬─────┘  └───────┬────────┘
         │             │        │                │
         │      cần db │        │ cần settings   │  @lru_cache
         │             ▼        ▼                ▼
         │        ┌────────┐  ┌───────────────────────┐
         │        │get_db()│  │ Settings()            │
         │        └────┬───┘  │ đọc biến môi trường   │
         │             │      └───────────────────────┘
         ▼             ▼
   ┌────────────────────────────────┐
   │ Session(get_engine(url))       │
   │       │                        │
   │       ▼  @lru_cache(maxsize=4) │
   │  create_engine(url)  ← pool    │
   └────────────────────────────────┘
```

Chú ý điểm thú vị: **`get_current_user` tự nó cũng phụ thuộc `get_db` và `get_settings`**:

```python
# apps/api/app/auth.py
def get_current_user(
    request: Request,
    test_session: Annotated[str | None, Header(alias="X-Test-Session")] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> CurrentUser:
```

FastAPI giải quyết đệ quy: thấy handler cần `user`, nó đi tìm `get_current_user`, thấy hàm đó cần `db` và `settings`, đi tìm tiếp, rồi lắp ngược lên.

**Và đây là điều quan trọng:** trong một request, `get_db` chỉ chạy **một lần**. FastAPI cache kết quả dependency theo phạm vi request. Nên `db` mà `get_current_user` nhận được và `db` mà handler nhận được là **cùng một `Session`**. Đó là lý do câu `db.commit()` trong `get_current_user` ảnh hưởng tới trạng thái transaction mà handler nhìn thấy (xem cạm bẫy ở [04-request-lifecycle.md](04-request-lifecycle.md) mục 4.6).

## 9.5 Dependency dạng generator — dọn dẹp tự động

```python
def get_db() -> Generator[Session, None, None]:
    with Session(get_engine(get_settings().database_url)) as session:
        yield session
```

Từ khoá `yield` (không phải `return`) khiến FastAPI xử lý đặc biệt:

```text
        [phần trước yield]  → tạo Session
                ↓
        yield session       → giao Session cho handler
                ↓
        ... handler chạy, response được sinh ra ...
                ↓
        [phần sau yield]    → thoát khối with → session.close()
```

Phần dọn dẹp chạy **kể cả khi handler ném exception**. Không bao giờ rò rỉ kết nối.

## 9.6 Vì sao service KHÔNG được inject?

Đây là điểm khác biệt lớn nhất so với các project backend "chuẩn mực" (Spring, NestJS, .NET), nơi bạn inject `UserService` vào controller.

Ở đây, service chỉ là **hàm thường**, gọi trực tiếp, và `db` được **truyền tay**:

```python
# apps/api/app/routes/master_data.py
from app.services.semester_queries import semester_or_404, ensure_semester_writable

def create_semester(payload, db, user, settings):
    ...
    return semester_or_404(db, int(row["id"]))     # ← truyền db vào, không inject
```

```python
# apps/api/app/services/semester_queries.py — nhận db làm tham số đầu tiên
def ensure_semester_writable(db: Session, semester_id: int) -> str:
    status = db.execute(text("SELECT status FROM semesters WHERE id = :semester_id FOR UPDATE"),
                        {"semester_id": semester_id}).scalar_one_or_none()
```

**Vì sao thiết kế như vậy? Đây là lý do quan trọng nhất trong cả tài liệu này:**

Nếu service tự xin `Session` riêng qua `Depends`, nó sẽ chạy trên **một kết nối khác**, tức **một transaction khác**. Khi đó:

```text
Route:    with db.begin():                    ← transaction A
              INSERT INTO semesters ...
              some_service.do_something()     ← nếu service dùng Session riêng
                  → transaction B, KHÔNG thấy dữ liệu của A (chưa commit)
                  → A rollback thì B vẫn commit → DỮ LIỆU RÁC
```

Truyền `db` qua tham số đảm bảo **mọi thứ trong một request chạy chung một transaction**, nguyên tử tuyệt đối.

**Quy tắc bất di bất dịch khi bạn viết service mới:**

```python
# ✅ ĐÚNG — luôn nhận db từ bên ngoài
def my_service_function(db: Session, some_id: int) -> dict:
    ...

# ❌ SAI — tự tạo session, phá vỡ transaction của route
def my_service_function(some_id: int) -> dict:
    with Session(get_engine(...)) as db:
        ...
```

## 9.7 Ghi đè dependency trong test

FastAPI cho phép thay thế dependency lúc test:

```python
app.dependency_overrides[get_current_user] = lambda: CurrentUser(role="MANAGER", account_id=1)
```

**[Xác nhận từ code]** Repo **không dùng** cách này. Thay vào đó nó chọn cửa hậu `X-Test-Session` trong chính `auth.py`, và `conftest.py` chỉ có 11 dòng:

```python
import os
os.environ["APP_ENV"] = "test"

import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())
```

**[Nhận định về đánh đổi]**

| | `dependency_overrides` | `X-Test-Session` (repo chọn) |
|---|---|---|
| Code production sạch | ✅ | ❌ có nhánh chỉ dành cho test |
| Viết test đơn giản | ❌ phải setup override từng test | ✅ chỉ thêm 1 header |
| Test được cả middleware CSRF | ❌ | ✅ (đi qua toàn bộ stack thật) |
| Rủi ro bảo mật | không | có, phụ thuộc `APP_ENV` không bao giờ = `test` ở prod |

Với 72 file test, việc chỉ cần thêm một header đúng là tiết kiệm rất nhiều. Nhưng bạn phải hiểu cái giá của nó.

## 9.8 Điều gì KHÔNG được inject

| Thứ | Cách lấy | Ghi chú |
|---|---|---|
| Hàm domain | `import` trực tiếp | Hàm thuần, không trạng thái, không cần inject |
| Hàm service | `import` trực tiếp, truyền `db` | Xem mục 9.6 |
| Scheduler engine | `import solve_schedule` | Hàm thuần |
| Email adapter | Tham số mặc định | Xem bên dưới |

Riêng email adapter có một dạng "DI thủ công" đáng chú ý:

```python
# apps/api/app/services/notification_dispatcher.py
class EmailAdapter(Protocol):
    def send(self, *, recipient: str, event_type: str, payload: dict[str, Any]) -> None: ...

@dataclass(frozen=True)
class NoopEmailAdapter:
    def send(self, *, recipient, event_type, payload) -> None:
        return None

def process_outbox(db: Session, *, limit: int = 50, email_adapter: EmailAdapter | None = None):
    adapter = email_adapter or NoopEmailAdapter()
```

`Protocol` là "interface" của Python — bất kỳ class nào có method `send` đúng chữ ký đều dùng được, không cần kế thừa. Test truyền adapter giả để kiểm tra; production sau này truyền adapter SMTP thật; mặc định là adapter không làm gì.

Đây là **Strategy pattern** làm bằng tay, và nó hoàn toàn hợp lý — không cần framework DI cho một chỗ duy nhất.

## 9.9 Tóm tắt

```text
Repo này có ĐÚNG 3 dependency, tất cả trong 3 file nhỏ:

   get_db()           apps/api/app/database.py   18 dòng
   get_current_user() apps/api/app/auth.py       58 dòng
   get_settings()     apps/api/app/config.py     29 dòng

Không có IoC container. Không inject service. Không inject repository.
`db` luôn được TRUYỀN TAY xuống service để giữ chung một transaction.
```

Nếu bạn từng làm Spring hay NestJS, hãy chủ động quên mô hình "inject mọi thứ" ở đây. Sự đơn giản này là chủ ý, và cái ràng buộc "một request = một transaction" mà nó bảo vệ quan trọng hơn nhiều so với tính thuần khiết của DI.
