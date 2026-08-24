# 6. Authentication và Authorization

Hai từ dễ lẫn:

- **Authentication (xác thực)** — "bạn là ai?" Kiểm tra danh tính.
- **Authorization (phân quyền)** — "bạn được làm gì?" Kiểm tra quyền hạn.

Repo này làm cả hai, ở hai chỗ khác nhau.

## 6.1 Cơ chế: session cookie, KHÔNG phải JWT

| | JWT (nhiều project khác dùng) | Session cookie (repo này) |
|---|---|---|
| Token lưu ở đâu | Client giữ, server không lưu | Server lưu hash trong bảng `auth_sessions` |
| Đăng xuất ngay lập tức | Khó (token còn hạn là còn dùng được) | Dễ — `UPDATE ... SET revoked_at = now()` |
| Mỗi request | Chỉ verify chữ ký, không cần DB | **Phải query DB** |
| Chống XSS đánh cắp token | Kém nếu để trong localStorage | Tốt — cookie `httpOnly`, JS không đọc được |
| Cần chống CSRF | Không, nếu dùng header Authorization | **Có** — vì cookie tự động gửi kèm |

Repo chọn session cookie, nên **bắt buộc phải có cơ chế chống CSRF**. Đó là lý do có `csrf_guard`.

> **CSRF là gì?** Trình duyệt tự động gửi cookie của `api.truong.edu` theo **mọi** request tới domain đó — kể cả request do trang `web-doc-hai.com` khởi tạo. Kẻ tấn công dụ bạn mở trang của họ, trang đó ngầm gửi `POST /api/v1/semesters/5/archive`, và cookie của bạn đi kèm. Server tưởng chính bạn bấm.
>
> **Cách chống — double-submit:** server phát thêm cookie `scheduler_csrf` mà JS **đọc được**. Client phải copy giá trị đó vào header `X-CSRF-Token`. Trang độc hại gửi được cookie (tự động) nhưng **không đọc được** giá trị cookie đó (do chính sách same-origin của trình duyệt), nên không đặt được header đúng.

## 6.2 Luồng đăng nhập

**File:** [apps/api/app/routes/auth_routes.py](../../apps/api/app/routes/auth_routes.py) — hàm `login`

```text
POST /api/v1/auth/login   {"email": "...", "password": "..."}
   │
   ├─ 1. _record_login_attempt()  ← CHỐNG BRUTE-FORCE
   │      INSERT INTO auth_login_throttles ... ON CONFLICT DO UPDATE
   │      cửa sổ 15 phút, > 10 lần thử → 429 + header Retry-After
   │
   ├─ 2. SELECT a.id, a.password_hash, a.status, ar.role
   │      FROM accounts a JOIN account_roles ar ON ar.account_id = a.id
   │      WHERE lower(a.email) = lower(:email) ORDER BY ar.role LIMIT 1
   │      ❌ không thấy, hoặc status ≠ ACTIVE → 401 "Invalid credentials"
   │
   ├─ 3. password_hasher.verify(row["password_hash"], payload.password)   ← argon2
   │      ❌ sai → 401 "Invalid credentials"   (thông điệp GIỐNG HỆT bước 2 — cố ý)
   │
   ├─ 4. token      = secrets.token_urlsafe(48)   ← ngẫu nhiên mật mã học
   │      csrf_token = secrets.token_urlsafe(32)
   │
   ├─ 5. INSERT INTO auth_sessions (account_id, token_hash, csrf_token_hash, expires_at)
   │      ★ lưu SHA-256, KHÔNG lưu token gốc
   │
   ├─ 6. INSERT INTO audit_events ... 'LOGIN_SUCCESS'
   │      DELETE FROM auth_login_throttles WHERE identifier = ...   ← reset bộ đếm
   │
   └─ 7. set_cookie("scheduler_session", token, httponly=True,  secure=..., samesite="lax")
         set_cookie("scheduler_csrf",    csrf_token, httponly=False, ...)
         → 200 {"role": "MANAGER", "expires_at": "..."}
```

Bốn chi tiết bảo mật đáng học trong đoạn code này:

**1. Chỉ lưu hash, không lưu token gốc.**
```python
"INSERT INTO auth_sessions (account_id, token_hash, csrf_token_hash, expires_at) ..."
{"token_hash": _hash(token), "csrf_token_hash": _hash(csrf_token), ...}
```
Nếu DB bị lộ, kẻ tấn công có hash nhưng không tạo ngược lại được cookie hợp lệ. Cùng nguyên tắc như lưu mật khẩu.

**2. Thông điệp lỗi giống hệt nhau.**
Email không tồn tại và mật khẩu sai đều trả `401 "Invalid credentials"`. Nếu phân biệt, kẻ tấn công dò được email nào có trong hệ thống.

**3. `db.commit()` trước khi ném 401.**
```python
if row is None or str(row["status"]) != "ACTIVE":
    db.commit()                      # ← giữ lại bản ghi throttle
    raise HTTPException(401, ...)
```
Không có dòng này, exception sẽ rollback và **xoá luôn lần đếm thất bại** — bộ đếm brute-force vô dụng. Rất dễ bỏ sót.

**4. Cookie `secure` phụ thuộc môi trường.**
```python
secure = settings.app_env not in {"development", "test"}
```
`secure=True` bắt cookie chỉ gửi qua HTTPS. Bật ở dev (dùng `http://localhost`) thì không đăng nhập được.

## 6.3 Luồng xác thực mỗi request

**File:** [apps/api/app/auth.py](../../apps/api/app/auth.py) — hàm `get_current_user`

```text
Request tới (cookie scheduler_session tự đính kèm)
   │
   ├─ [nhánh test] APP_ENV=test VÀ có header X-Test-Session
   │      "active-manager"     → CurrentUser(role="MANAGER")
   │      "active-lecturer:42" → CurrentUser(role="LECTURER", account_id=42)
   │      ★ CHỈ hoạt động khi APP_ENV=test — production tuyệt đối không vào nhánh này
   │
   ├─ [nhánh thật] đọc cookie → SHA-256 → tra bảng
   │      SELECT s.account_id, a.status, ar.role
   │      FROM auth_sessions s
   │      JOIN accounts a ON a.id = s.account_id
   │      JOIN account_roles ar ON ar.account_id = a.id
   │      WHERE s.token_hash   = :token_hash
   │        AND s.revoked_at   IS NULL                       ← chưa logout
   │        AND s.expires_at   > now()                       ← chưa hết hạn tuyệt đối (168h)
   │        AND s.last_seen_at > now() - :idle_minutes * interval '1 minute'   ← chưa "ngủ quên" (60p)
   │      ORDER BY ar.role LIMIT 1
   │
   ├─ kiểm tra accounts.status == 'ACTIVE'   ← khoá tài khoản có hiệu lực ngay
   ├─ UPDATE auth_sessions SET last_seen_at = now()   ← gia hạn nhàn rỗi
   ├─ db.commit()
   └─ return CurrentUser(role, status, account_id)

   ❌ mọi trường hợp còn lại → 401 "Authentication required"
```

**Hai loại hạn dùng cùng lúc:**

| Hạn | Cấu hình | Ý nghĩa |
|---|---|---|
| Tuyệt đối | `session_absolute_hours = 168` (7 ngày) | Dù dùng liên tục, sau 7 ngày phải đăng nhập lại |
| Nhàn rỗi | `session_idle_minutes = 60` | Không hoạt động 60 phút → phiên chết |

**Cảnh báo về `ORDER BY ar.role LIMIT 1`:** một tài khoản có thể có **nhiều role**, nhưng `CurrentUser` chỉ giữ **một** chuỗi `role`. Query chọn role đầu tiên theo thứ tự bảng chữ cái của kiểu enum. **[Suy luận]** Với người vừa là MANAGER vừa là LECTURER, kết quả phụ thuộc thứ tự enum trong DB — đây là **điểm mờ ám thật sự** trong thiết kế. Nếu bạn gặp bug "user không thấy dữ liệu đáng lẽ phải thấy", hãy nghi ngờ chỗ này trước.

## 6.4 Phân quyền — hai tầng

Đây là phần dễ hiểu sai nhất. Repo phân quyền ở **hai tầng độc lập**:

```text
┌────────────────────────────────────────────────────────────┐
│ TẦNG 1 — RBAC: "vai trò này được gọi endpoint này không?"  │
│   _require(user, "ADMIN", "MANAGER")                        │
│   → 403 nếu role không nằm trong danh sách                  │
└─────────────────────────┬──────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│ TẦNG 2 — Row scoping: "được nhìn thấy DÒNG DỮ LIỆU nào?"   │
│   apps/api/app/services/access.py                           │
│   → không phải 403, mà là LỌC BỚT kết quả trả về            │
└────────────────────────────────────────────────────────────┘
```

### Tầng 1 — RBAC

Bốn role hệ thống, khai báo trong `app/domain/enums.py`: `ADMIN`, `MANAGER`, `LECTURER`, `STUDENT`.

Cách thực thi — helper 3 dòng, lặp lại trong nhiều file route:

```python
# apps/api/app/routes/master_data.py:120
def _require(user: CurrentUser, *roles: str) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")
```

Dùng ở dòng đầu tiên của handler:

```python
def create_semester(payload, db, user, settings):
    _require(user, "ADMIN", "MANAGER")
    ...
```

**Không có bảng permission, không có decorator, không có middleware phân quyền.** Đây là điểm quan trọng: **quên gọi `_require` = endpoint mở toang cho mọi user đã đăng nhập**, và không có gì cảnh báo bạn. Xem [12-junior-warnings.md](12-junior-warnings.md).

**Role ngữ cảnh ≠ role hệ thống.** `Reviewer`, `Supervisor`, `Result Owner`, `Remediation Verifier`, `Project Leader` **không phải** role hệ thống — chúng là quan hệ dữ liệu. Một `LECTURER` trở thành `Reviewer` của buổi X vì có dòng trong `session_reviewers`, chứ không vì role của họ. Kiểm tra loại này thuộc tầng 2.

### Tầng 2 — Row-level scoping

**File:** [apps/api/app/services/access.py](../../apps/api/app/services/access.py)

Cùng một endpoint `GET /sessions`, nhưng mỗi người thấy tập dữ liệu khác nhau:

```python
def visible_session_ids(db, user, *, version_id=None) -> set[int]:
    if is_management_user(user):        # ADMIN hoặc MANAGER
        # → thấy TẤT CẢ
    if user.account_id is None:
        return set()                    # ← không xác định được danh tính ⇒ không thấy gì
    if user.role == "LECTURER":
        # → chỉ buổi mà mình là Reviewer (qua council_members)
        #   hoặc là Supervisor của đề tài nhóm đó (qua project_supervisors)
    if user.role == "STUDENT":
        # → chỉ buổi của nhóm mình đang là thành viên ACTIVE
    return set()
```

Docstring của hàm nói rõ triết lý:

> "Missing account identity deliberately yields no private records."

Tức là **fail-closed**: không chắc bạn là ai thì không cho thấy gì. Đây là mặc định an toàn đúng đắn.

Ngoài ra `access.py` còn có:

| Hàm | Dùng để |
|---|---|
| `is_management_user(user)` | Kiểm tra ADMIN/MANAGER |
| `lecturer_id_for_account(db, account_id)` | Đổi `account_id` → `lecturer_id` |
| `student_id_for_account(db, account_id)` | Đổi `account_id` → `student_id` |
| `is_active_group_leader(...)` | Sinh viên này có phải leader đang hoạt động không |
| `can_read_session(db, user, session_id)` | Kiểm tra một buổi cụ thể |

Vì sao cần đổi id? Vì `CurrentUser` chỉ có `account_id`, còn nghiệp vụ tham chiếu tới `lecturers.id` / `students.id` — ba bảng khác nhau. Xem mẫu ở [apps/api/app/routes/target_portals.py](../../apps/api/app/routes/target_portals.py):

```python
def _lecturer_id(db: Session, user: CurrentUser) -> int:
    if user.role != "LECTURER":
        raise HTTPException(403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer portal access is required."})
    lecturer_id = lecturer_id_for_account(db, user.account_id)
    if lecturer_id is None:
        raise HTTPException(403, detail={"code": "AUTH_RESOURCE_SCOPE", "message": "Lecturer profile is not linked."})
    return int(lecturer_id)
```

## 6.5 Seam dành cho test

```python
# apps/api/app/auth.py
if settings.app_env == "test" and test_session:
    role, _, account = test_session.partition(":")
```

Mọi test trong `apps/api/tests/` dùng cửa này thay vì đăng nhập thật:

```python
client.post("/api/v1/semesters",
            json={...},
            headers={"X-Test-Session": "active-admin"})

# muốn gắn account cụ thể:
headers={"X-Test-Session": "active-lecturer:42"}
```

Hai lớp bảo vệ khiến nó không thành lỗ hổng production:
1. Điều kiện `settings.app_env == "test"` — dev/prod không vào nhánh này.
2. `conftest.py` set `os.environ["APP_ENV"] = "test"` **trước khi** import `app.main`, vì `get_settings()` có `@lru_cache` nên chỉ đọc môi trường đúng một lần.

**[Nhận định]** Đây là đánh đổi hợp lý cho project quy mô này, nhưng nó phụ thuộc hoàn toàn vào việc `APP_ENV` không bao giờ bị đặt thành `test` ngoài môi trường test. Nếu sau này triển khai lên cloud, đây là thứ cần rà lại đầu tiên.

## 6.6 Tài khoản demo local

Mật khẩu chung: `SchedulerDemo2026!`

```text
admin1@gmail.com      ADMIN
manager1@gmail.com    MANAGER
lecturer1@gmail.com   LECTURER
student1@gmail.com    STUDENT  ← là leader của một nhóm
student2@gmail.com    STUDENT  ← thành viên cùng nhóm đó
```

Còn có biến thể `*2@gmail.com`. Nguồn: `CLAUDE.md`.

## 6.7 Thử bằng tay

```powershell
# 1. Đăng nhập, lưu cookie vào file
curl.exe -i -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"manager1@gmail.com\",\"password\":\"SchedulerDemo2026!\"}'

# 2. GET không cần CSRF
curl.exe -b cookies.txt http://localhost:8000/api/v1/auth/me

# 3. POST thì phải lấy giá trị scheduler_csrf trong cookies.txt
#    và gắn vào header X-CSRF-Token, nếu không sẽ nhận 403.
```
