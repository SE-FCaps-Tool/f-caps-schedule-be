# 03. Lifecycle của một request

## Luồng chung

```text
Client
  -> ASGI/Uvicorn
  -> CORS + HTTP middleware
  -> FastAPI route matching
  -> path/query/body validation
  -> dependency injection
       -> settings
       -> DB Session
       -> current user
  -> authorization + resource checks
  -> domain/service/raw SQL
  -> transaction + audit event
  -> response serialization
  -> exception handler nếu có lỗi
  -> security/deprecation headers
  -> Client
```

`create_app()` tại `apps/api/app/main.py` tạo FastAPI app, mount Swagger assets, đăng ký
middleware/exception handlers và include các router. `app = create_app()` là object được Uvicorn
import.

## Trace thật: `PATCH /api/v1/rooms/{room_id}`

Endpoint nằm tại `update_room()` trong `apps/api/app/routes/target_room_publish.py`.

### 1. Request vào middleware

Input tiêu biểu:

```json
{
  "code": "P-301",
  "roomType": "NORMAL",
  "capacity": 40,
  "active": true
}
```

Vì đây là `PATCH`, `csrf_guard()` trong `main.py` kiểm tra CSRF nếu request có session cookie.
Nó yêu cầu:

- cookie `scheduler_session`;
- cookie `scheduler_csrf`;
- header `X-CSRF-Token` bằng CSRF cookie;
- hash CSRF trùng giá trị của active session trong DB.

Sai CSRF dừng ngay với 403; handler chưa được gọi.

### 2. FastAPI match route và validate

- `room_id` được parse thành `int`.
- Body được parse thành `RoomUpdateTarget`.
- Pydantic kiểm tra capacity `1..500`, room type hợp lệ và camelCase aliases.
- Sai shape/type tạo `RequestValidationError` trước khi business logic chạy.

### 3. Dependency injection tạo context

```text
Db = Depends(get_db)
  -> get_engine(database_url)
  -> SQLAlchemy Session cho request

User = Depends(get_current_user)
  -> đọc session cookie
  -> hash token
  -> SELECT auth_sessions + accounts + account_roles
  -> kiểm tra active/expire/idle timeout
  -> UPDATE last_seen_at và commit
  -> CurrentUser(role, account_id)
```

`get_engine()` cache engine và bật `pool_pre_ping=True`; `get_db()` yield một Session rồi đóng nó
khi request kết thúc.

### 4. Authorization

`_manager(user)` trong cùng route file chỉ cho `ADMIN` hoặc `MANAGER`. Authentication trả lời
“bạn là ai”; authorization trả lời “bạn có được sửa room này không”. Hai bước không giống nhau.

### 5. Đọc current state

Handler chạy `SELECT` room hiện tại. SQLAlchemy 2 tự mở transaction ở query đầu tiên
(autobegin). Sau read, code gọi `db.rollback()` trước khi vào `with db.begin()`.

Đây là pattern rất quan trọng trong repo:

```text
SELECT trước
  -> implicit transaction đã mở
  -> db.rollback()
  -> with db.begin(): ghi atomically
```

Thiếu rollback có thể gây lỗi khi cố mở explicit transaction trên Session đã ở trong transaction.

### 6. Mutation transaction

Handler chỉ build danh sách cột từ whitelist hard-coded; values vẫn đi qua bound parameters.
Trong một `with db.begin()`:

1. `UPDATE rooms ... RETURNING ...`.
2. `INSERT audit_events` với action `ROOM_UPDATED`.

Nếu một câu lệnh lỗi, cả room update và audit event rollback. Đây là lý do audit insert nằm cùng
transaction thay vì ghi sau khi response thành công.

### 7. Error mapping

- Không có room: 404 với business code.
- Duplicate room code: `IntegrityError` được map thành 409 `ROOM_DUPLICATE`.
- Validation request: 422.
- Không đủ role: 403.

Vì router có tag `target-*`, exception handler trong `main.py` đổi lỗi thành:

```json
{
  "error": {
    "code": "ROOM_DUPLICATE",
    "message": "...",
    "details": {}
  }
}
```

Legacy route vẫn dùng `{"detail": ...}`. Riêng response CSRF được middleware tạo trực tiếp nên
hiện vẫn có shape `{"detail":"CSRF validation failed"}` ngay cả với target endpoint.

### 8. Success response

`success_payload()` đổi keys đệ quy sang camelCase và bọc trong `{"data": ...}`. Middleware thêm
security headers và có thể thêm legacy/deprecation headers trước khi response về client.

## Cách tự trace API khác

1. Tìm decorator `@router.<method>("path")`.
2. Xác định router được include ở đâu trong `main.py` và thứ tự include.
3. Đọc Pydantic input/output models.
4. Liệt kê `Depends`: settings, DB, user hoặc dependency khác.
5. Tìm role guard và resource-level access helper.
6. Theo lời gọi sang domain/service/scheduler.
7. Liệt kê SQL read/write và transaction boundary.
8. Tìm `audit_events`, outbox hoặc notification side effect.
9. Xem `DomainError`, `IntegrityError`, `HTTPException` được map thế nào.
10. Tìm tests có path/function/response code tương ứng.

Đừng chỉ trace “happy path”. Với backend, transaction rollback, authorization và concurrent
request thường là nơi bug nghiêm trọng xuất hiện.
