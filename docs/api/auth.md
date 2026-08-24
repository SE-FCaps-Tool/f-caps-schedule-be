# Auth và current user

## `GET /health`

- **Auth:** public.
- **Response `200`:**

```json
{ "status": "ok", "service": "api" }
```

Dùng cho health check của FE/dev tooling, không dùng để xác định user đã đăng nhập.

## `POST /api/v1/auth/login`

Đăng nhập bằng account đang `ACTIVE`.

- **Auth:** public; không cần CSRF.
- **Body:** [`LoginPayload`](schemas.md#loginpayload).
- **Success `200`:**

```json
{ "role": "MANAGER", "expiresAt": "2026-08-19T03:00:00+00:00", "requiresRoleSelection": false, "availableRoles": ["MANAGER"] }
```

Nếu account có nhiều role, BE chưa tạo session mà trả:

```json
{ "role": null, "expiresAt": null, "requiresRoleSelection": true, "availableRoles": ["ADMIN", "MANAGER", "LECTURER"] }
```

FE chuyển người dùng tới màn hình chọn role. Challenge được giữ trong HttpOnly cookie
`scheduler_login_challenge` và hết hạn sau 10 phút.

- **Set-Cookie:** session cookie HttpOnly và `scheduler_csrf` readable by JavaScript. Tên session cookie có thể cấu hình, vì vậy FE chỉ nên dùng `credentials: "include"`.
- **`401`:** `Invalid credentials` nếu email/password sai hoặc account không active.
- **`429`:** quá 10 lần thử trong cửa sổ throttle; đọc `Retry-After` để hiển thị thời gian chờ.
- **Lưu ý:** email được xử lý không phân biệt hoa thường; không lưu password ở frontend state/localStorage.

Ví dụ:

```ts
await fetch(`${API_URL}/api/v1/auth/login`, {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json", Accept: "application/json" },
  body: JSON.stringify({ email, password }),
});
```

## `POST /api/v1/auth/logout`

- **Auth:** public về mặt route; nếu có session thì session bị revoke.
- **CSRF:** không yêu cầu.
- **Response `200`:**

```json
{ "status": "signed_out" }
```

Backend xóa session cookie, `scheduler_csrf` và login challenge nếu còn. FE nên reset toàn bộ cached user/query sau khi gọi.

## Google OAuth

Google login dùng server-side OAuth Authorization Code + PKCE. Google chỉ được liên kết với
account đã tồn tại trong `accounts` và đang `ACTIVE`; email chưa được admin tạo trước sẽ bị từ
chối. Role vẫn lấy từ `account_roles`, không lấy từ Google.

### `GET /api/v1/auth/google/start`

- **Auth:** public.
- Redirect người dùng sang Google với `state`, `nonce` và PKCE cookies ngắn hạn.
- Cần cấu hình `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` và `GOOGLE_REDIRECT_URI`.

### `GET /api/v1/auth/google/callback`

- Google redirect về endpoint này với authorization code.
- BE xác minh code, ID token, issuer, audience, nonce và `email_verified`, sau đó tạo cùng loại
  session/CSRF cookie như login mật khẩu.
- Thành công redirect về FE `/auth/callback`; thất bại redirect về `/login?oauth_error=...`.
- Account có nhiều role sẽ được redirect về `/auth/callback`, sau đó FE gọi `GET /api/v1/auth/pending`
  và hiển thị màn hình chọn role. Google callback URL và các scope hiện tại không thay đổi.

## Chọn role sau đăng nhập

### `GET /api/v1/auth/pending`

Đọc challenge HttpOnly của lần đăng nhập vừa xác thực.

```json
{ "availableRoles": ["ADMIN", "MANAGER", "LECTURER"] }
```

### `POST /api/v1/auth/select-role`

- **Auth:** dùng challenge cookie, chưa cần session đầy đủ.
- **Body:** `{ "role": "MANAGER" }`.
- **Success:** tạo session gắn với role đã chọn và trả cùng shape `LoginResponse` với `role` đã chọn.
- **403 `ROLE_NOT_ASSIGNED`:** role không thuộc account.
- **401 `ROLE_SELECTION_EXPIRED`:** challenge đã dùng hoặc hết hạn; yêu cầu đăng nhập lại.

Mọi request sau đó, bao gồm `GET /api/v1/auth/me`, dùng role đã gắn trong session. Không suy ra
role bằng cách lấy role đầu tiên từ `account_roles` nữa.

## `GET /api/v1/auth/me`

Trả identity của session hiện tại.

- **Auth:** tất cả role đã đăng nhập.
- **Response `200`:**

```json
{ "role": "LECTURER", "status": "ACTIVE", "account_id": 17 }
```

- **`401`:** chưa có session, session hết hạn hoặc session đã revoke.

Đây là endpoint nên gọi khi app khởi động, refresh trang và sau khi nhận `401` ở API khác.

## `GET /api/v1/me`

Alias ngắn cho current user dùng ở UI guard.

- **Auth:** tất cả role đã đăng nhập.
- **Response `200`:**

```json
{ "role": "MANAGER", "status": "ACTIVE" }
```

- **`401`:** chưa đăng nhập.

## Quy tắc session cho FE

- Không tự copy HttpOnly session token.
- Luôn bật `credentials: "include"`.
- Lấy CSRF token từ cookie `scheduler_csrf` cho `POST/PATCH/DELETE`.
- Không retry vô hạn khi `401`; chỉ thử hydrate lại một lần, sau đó chuyển về login.
- `403` là lỗi permission/scope, không phải lỗi session hết hạn.

### Thời hạn session hiện tại

- Idle timeout: `60 phút` không có request hợp lệ.
- Absolute timeout: `168 giờ` (7 ngày) kể từ lúc login.
- Backend không dùng refresh token và không có endpoint `/auth/refresh`.
- Khi session hết hạn, API trả `401`; FE cần xóa auth state và chuyển user về màn hình login.

Có thể override bằng biến môi trường:

```env
SESSION_IDLE_MINUTES=60
SESSION_ABSOLUTE_HOURS=168
```
