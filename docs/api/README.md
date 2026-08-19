# Capstone Defense Scheduler — FE API Guide

Tài liệu này là hợp đồng tích hợp cho frontend với backend hiện tại. Nội dung được đối chiếu với OpenAPI runtime tại `http://localhost:8000/openapi.json` và source route trong commit ngày 2026-08-18.

## 1. Kết nối

| Môi trường | Base URL |
|---|---|
| Docker local | `http://localhost:8000` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| Swagger UI | `http://localhost:8000/docs` |

Mọi route nghiệp vụ bắt đầu bằng `/api/v1`. Ví dụ: `GET http://localhost:8000/api/v1/me`.

### Cross-origin khi FE chạy repo riêng

Backend đã bật `CORSMiddleware`. Danh sách origin lấy từ biến môi trường
`CORS_ORIGINS` (mặc định `http://localhost:3000`); khi FE chạy ở origin khác, thêm origin
đó vào biến này. Vì API dùng cookie session nên không dùng
`Access-Control-Allow-Origin: *`; `allow_credentials=true` phải đi cùng origin cụ thể.

Backend là cookie-session API, không dùng `Authorization: Bearer`. Frontend phải gửi cookie cross-request:

```ts
fetch(`${API_URL}/api/v1/me`, {
  credentials: "include",
  headers: { Accept: "application/json" },
});
```

## 2. Luồng đăng nhập bắt buộc

1. `POST /api/v1/auth/login` với email/password.
2. Browser tự lưu HttpOnly session cookie. Response cũng đặt cookie `scheduler_csrf` để frontend đọc được.
3. Với mọi `POST`, `PATCH`, `DELETE` sau đăng nhập, gửi `X-CSRF-Token` bằng đúng giá trị cookie `scheduler_csrf`.
4. Gọi `GET /api/v1/auth/me` để hydrate user và role.
5. Khi logout, gọi `POST /api/v1/auth/logout`.

```ts
function csrfToken() {
  return document.cookie
    .split("; ")
    .map((part) => part.trim())
    .find((part) => part.startsWith("scheduler_csrf="))
    ?.split("=")[1];
}

async function api(path: string, init: RequestInit = {}) {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (["POST", "PATCH", "DELETE"].includes(method)) {
    const token = csrfToken();
    if (token) headers.set("X-CSRF-Token", token);
  }
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) throw { status: response.status, data, response };
  return data;
}
```

`API_URL` nên là `http://localhost:8000` ở local. Không nối thêm `/api/v1` nếu helper đã nhận path đầy đủ.

`X-Test-Session` có trong OpenAPI để phục vụ test/fixture compatibility. FE thật không dùng header này; luôn login và dùng cookie session.

## 3. Role

| Role | Ý nghĩa |
|---|---|
| `ADMIN` | Quản trị tài khoản, fixture, audit, master data nhạy cảm và mọi chức năng quản lý. |
| `MANAGER` | Quản lý round, dữ liệu nghiệp vụ, chạy/xuất bản lịch, kết quả và vận hành. |
| `LECTURER` | Đăng ký lời mời, khai báo availability, xem lịch được phân công, nhập kết quả khi được phân công. |
| `STUDENT` | Khai báo availability của group và xem lịch/kết quả trong phạm vi group. |

Một số route yêu cầu nhiều role. Nếu role không nằm trong danh sách, backend trả `403`.

## 4. Quy ước request/response

- `Content-Type: application/json` cho request body JSON.
- Datetime nên gửi ISO-8601 có timezone, ví dụ `2026-08-20T08:00:00+07:00`.
- Date dùng `YYYY-MM-DD`.
- ID là số nguyên dương.
- Các mã code được backend normalize thành uppercase/trim khi cần.
- Trường không bắt buộc thường được đánh dấu `optional` hoặc có giá trị mặc định trong [schemas.md](schemas.md).
- Response thành công thường là JSON object/array. Các status code tạo resource gồm `201`.
- Calendar trả file `text/calendar`, không phải JSON.

## 5. Lỗi và cách xử lý

### Lỗi nghiệp vụ

Phần lớn lỗi có dạng:

```json
{
  "detail": {
    "code": "VERSION_NOT_VALID",
    "message": "Only a valid version can become active."
  }
}
```

Các status code chính:

| Status | Khi nào |
|---:|---|
| `401` | Chưa đăng nhập, session hết hạn, hoặc credentials sai. Xóa state user và đưa về login. |
| `403` | Đã đăng nhập nhưng role hoặc phạm vi dữ liệu không được phép. |
| `404` | Resource không tồn tại hoặc không thuộc scope của thao tác. |
| `409` | Trùng dữ liệu hoặc concurrent update. Hiển thị thông báo và reload resource. |
| `422` | Body sai validation hoặc vi phạm business rule/hard constraint. |
| `429` | Login bị throttle; đọc header `Retry-After`. |

### Lỗi validation FastAPI

```json
{
  "detail": [
    {
      "loc": ["body", "session_duration_minutes"],
      "msg": "Input should be greater than 0",
      "type": "greater_than",
      "input": 0
    }
  ]
}
```

### CSRF

Thiếu hoặc sai `X-CSRF-Token` sẽ bị từ chối trước khi route nghiệp vụ chạy. Không hard-code token; lấy từ cookie sau login.

## 6. Danh mục đầy đủ route

Chi tiết request/response theo nhóm:

- [API architecture và luồng nghiệp vụ](api-reorganization.md)
- [ADMIN-only API](admin-api.md)
- [Auth và current user](auth.md)
- [Master data và round setup](master-data.md)
- [Manager FE API flow — request/response theo thứ tự](manager-fe-flow.md)
- [Manager API tổng hợp và mockdata alignment](manager-api.md)
- [Scheduler, lịch và vận hành thay đổi](scheduling.md)
- [Kết quả, remediation, dashboard, reports, notification](results-reports.md)
- [Request schemas, enum và response shapes dùng chung](schemas.md)

### Auth/system

`GET /health`, `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`, `GET /api/v1/me`

### Master data và round setup

`GET/POST /api/v1/semesters`, `POST /api/v1/semesters/{semester_id}/transition`, `GET/POST /api/v1/accounts`, `PATCH /api/v1/accounts/{account_id}/status`, `POST /api/v1/accounts/{account_id}/roles`, `DELETE /api/v1/accounts/{account_id}/roles/{role}`, `POST /api/v1/admin/seed-fixture`, `GET /api/v1/audit`, `GET /api/v1/majors`, `GET /api/v1/students`, `GET/POST /api/v1/projects`, `GET/POST /api/v1/lecturers`, `POST /api/v1/lecturers/{lecturer_id}/conflicts`, `GET/POST /api/v1/rooms`, `GET/POST /api/v1/groups`, `POST /api/v1/groups/{group_id}/members/{student_id}/drop`, `POST /api/v1/groups/{group_id}/leader`, `GET/POST /api/v1/rounds`, `POST /api/v1/rounds/{round_id}/transition`, `POST /api/v1/rounds/{round_id}/unlock`, `POST /api/v1/rounds/{round_id}/resources`, `POST /api/v1/rounds/{round_id}/days`, `POST /api/v1/rounds/{round_id}/lecturers/{lecturer_id}/availability`, `POST /api/v1/rounds/{round_id}/groups/{group_id}/availability`, `POST /api/v1/rounds/{round_id}/invitations`, `POST /api/v1/rounds/{round_id}/invitations/{lecturer_id}/response`, `GET /api/v1/rounds/{round_id}/registration`, `GET /api/v1/rounds/{round_id}/my-availability`, `GET /api/v1/my/rounds`, `GET /api/v1/my/invitations`

### Schedule operations

`GET /api/v1/rounds/{round_id}/schedule/versions`, `GET /api/v1/schedule/versions/{version_id}`, `POST /api/v1/rounds/{round_id}/schedule/run`, `POST /api/v1/schedule/versions/{version_id}/activate`, `POST /api/v1/rounds/{round_id}/schedule/publish/{version_id}`, `POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/result-owner`, `POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/edit`, `POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/controlled-change`, `GET /api/v1/sessions/{session_id}/replacement-suggestions`, `POST /api/v1/sessions/{session_id}/postpone`, `POST /api/v1/sessions/{session_id}/reschedule-requests`, `POST /api/v1/reschedule-requests/{request_id}/decision`, `POST /api/v1/rounds/{round_id}/operation`, `POST/DELETE /api/v1/rounds/{round_id}/groups/{group_id}/h11-waiver`

### Results/reports/operations

`GET/POST /api/v1/sessions/{session_id}/result`, `GET /api/v1/remediation`, `POST /api/v1/remediation/{case_id}/decision`, `POST /api/v1/remediation/{case_id}/overdue-fail`, `GET /api/v1/dashboard`, `GET /api/v1/reports/lecturer-load`, `GET /api/v1/reports/unscheduled`, `GET /api/v1/reports/provenance/{version_id}`, `GET /api/v1/reports/quality`, `GET /api/v1/reports/remediation`, `GET /api/v1/reports/outcomes`, `GET /api/v1/notifications`, `POST /api/v1/notifications/{notification_id}/retry`, `GET /api/v1/schedule/versions/{version_id}/calendar.ics`, `GET /api/v1/my/schedule`

## 7. FE flow đề xuất

### Manager tạo và publish một round

`GET semesters` → `POST rounds` → `POST rounds/{id}/resources` → `POST rounds/{id}/days` → `POST invitations` → theo dõi `GET registration` → `POST schedule/run` → `POST versions/{id}/activate` → `POST rounds/{id}/schedule/publish/{version_id}` → `GET dashboard`/`GET my/schedule`.

### Lecturer

`GET my/rounds` → `GET my/invitations` → `POST invitations/{lecturer_id}/response` → `POST rounds/{id}/lecturers/{lecturer_id}/availability` → `GET my/schedule` → `GET sessions/{id}/result` → `POST sessions/{id}/result` nếu lecturer là Reviewer/Result Owner hợp lệ.

### Student

`GET my/rounds` → `GET rounds/{id}/my-availability` → `POST rounds/{id}/groups/{group_id}/availability` khi là active group leader → `GET my/schedule`.

## 8. Scope dữ liệu

ADMIN/MANAGER xem dữ liệu quản lý rộng hơn. LECTURER chỉ xem invitation đã nhận, session được phân công và các report/session thuộc scope. STUDENT chỉ xem group/session của mình. FE không nên giả định chỉ cần ẩn button là đủ; backend vẫn là nguồn quyết định quyền và scope.
