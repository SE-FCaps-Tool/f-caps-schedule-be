# Semester API — Tổng hợp thay đổi

**Ngày cập nhật:** 2026-08-19  
**Phạm vi:** Backend API, database migration và contract cho FE Manager

Tài liệu này mô tả toàn bộ thay đổi đã triển khai cho vòng đời học kỳ. API sử
dụng bốn trạng thái `PLANNING`, `ACTIVE`, `CLOSED`, `ARCHIVED`; trạng thái cũ
`UPCOMING` không còn được sử dụng.

## 1. Trạng thái và nguyên tắc

Semester có bốn trạng thái:

| Status | Ý nghĩa |
|---|---|
| `ACTIVE` | Học kỳ hiện tại đang được sử dụng |
| `CLOSED` | Học kỳ đã khóa/kết thúc |
| `PLANNING` | Chuẩn bị dữ liệu, chưa mở Round đánh giá |
| `ARCHIVED` | Lưu trữ, toàn bộ dữ liệu chỉ đọc |

Các nguyên tắc:

- Database chỉ cho phép tối đa một semester `ACTIVE`.
- Tạo semester mới mặc định `ACTIVE` để tương thích client cũ; client mới có thể gửi `status: PLANNING`.
- Tạo semester mới khi đã có semester `ACTIVE` trả `409 ACTIVE_SEMESTER_EXISTS`.
- Transition hợp lệ là `PLANNING → ACTIVE → CLOSED → ARCHIVED`.
- Chỉ Round thuộc semester `ACTIVE` mới được tạo; semester `ARCHIVED` không cho phép mutation.
- Chọn semester `PLANNING` hoặc `CLOSED` làm hiện tại sẽ tự động đóng semester `ACTIVE` cũ.
- `set-current` dùng một transaction và PostgreSQL advisory lock để tránh race condition.
- Khoảng thời gian semester tính theo số ngày inclusive, mặc định từ 105 đến 120 ngày.

## 2. Database và migration

Các migration liên quan:

- `0016_semester_active_closed`: đổi enum thành `ACTIVE | CLOSED`, chuyển dữ liệu
  legacy và tạo unique partial index cho trạng thái `ACTIVE`.
- `0017_semester_manager_metadata`: thêm metadata và index.
- `0018_semester_audit_backfill`: backfill timestamp/academic year cho dữ liệu cũ.
- `0026_semester_four_states`: mở rộng enum thành `PLANNING | ACTIVE | CLOSED | ARCHIVED`, giữ unique index cho `ACTIVE`.

Các field mới trong bảng `semesters`:

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `note` | `TEXT NULL` | Ghi chú semester |
| `academic_year` | `VARCHAR(9)` | Ví dụ `2026-2027` |
| `created_by` | `BIGINT NULL` | Account tạo semester |
| `updated_by` | `BIGINT NULL` | Account cập nhật gần nhất |
| `updated_at` | `TIMESTAMPTZ` | Thời điểm cập nhật gần nhất |

`academic_year` được suy ra từ năm của `start_date`:

```text
start_date = 2026-05-04 → academic_year = "2026-2027"
```

Các row legacy/import Excel không xác định được actor sẽ trả `created_by: null`
và/hoặc `updated_by: null`.

## 3. Response chuẩn

Tất cả list/detail/create/PATCH/set-current trả cùng shape `SemesterResponse`:

```json
{
  "id": 1,
  "code": "SU26",
  "name": "Summer 2026",
  "note": "Capstone semester",
  "start_date": "2026-05-04",
  "end_date": "2026-08-23",
  "academic_year": "2026-2027",
  "status": "ACTIVE",
  "project_count": 74,
  "group_count": 74,
  "round_count": 3,
  "created_at": "2026-08-19T08:00:00Z",
  "created_by": {
    "id": 3,
    "email": "manager1@gmail.com",
    "display_name": "Scheduler Manager 1"
  },
  "updated_at": "2026-08-19T08:30:00Z",
  "updated_by": {
    "id": 3,
    "email": "manager1@gmail.com",
    "display_name": "Scheduler Manager 1"
  }
}
```

Các count được tính độc lập theo `semester_id`:

- `project_count`: số project thuộc semester.
- `group_count`: số group của các project thuộc semester.
- `round_count`: số round thuộc semester.

## 4. API endpoints

### 4.1. Danh sách semester

```http
GET /api/v1/semesters
```

Role: `ADMIN`, `MANAGER`.

Query parameters:

| Parameter | Kiểu | Bắt buộc | Mô tả |
|---|---|---:|---|
| `search` | string | Không | Tìm không phân biệt hoa thường theo `code` hoặc `name` |
| `status` | `PLANNING \| ACTIVE \| CLOSED \| ARCHIVED` | Không | Lọc theo trạng thái |
| `academic_year` | `YYYY-YYYY` | Không | Lọc theo academic year |

Ví dụ:

```http
GET /api/v1/semesters?search=summer&status=ACTIVE&academic_year=2026-2027
```

Response `200`:

```json
[
  {
    "id": 1,
    "code": "SU26",
    "name": "Summer 2026",
    "note": null,
    "start_date": "2026-05-04",
    "end_date": "2026-08-23",
    "academic_year": "2026-2027",
    "status": "ACTIVE",
    "project_count": 74,
    "group_count": 74,
    "round_count": 3,
    "created_at": "2026-08-19T08:00:00Z",
    "created_by": null,
    "updated_at": "2026-08-19T08:00:00Z",
    "updated_by": null
  }
]
```

### 4.2. Chi tiết semester

```http
GET /api/v1/semesters/{semester_id}
```

Response `200`: cùng shape với một item trong danh sách.  
Không tồn tại trả `404`:

```json
{
  "detail": {
    "code": "SEMESTER_NOT_FOUND",
    "message": "Semester does not exist."
  }
}
```

### 4.3. Tạo semester

```http
POST /api/v1/semesters
Content-Type: application/json
```

Request:

```json
{
  "code": "SU26",
  "name": "Summer 2026",
  "note": "Capstone semester",
  "start_date": "2026-05-04",
  "end_date": "2026-08-23"
}
```

`note` là optional. `status` và `academic_year` không truyền trong request:

- `status` mặc định `ACTIVE`; có thể truyền `PLANNING`.
- `academic_year` tự suy ra từ `start_date`.
- `created_by`, `updated_by`, `created_at`, `updated_at` được backend lưu.

Response `201`: `SemesterResponse` đầy đủ.

### 4.4. Chỉnh sửa semester

```http
PATCH /api/v1/semesters/{semester_id}
Content-Type: application/json
```

Request có thể truyền một hoặc nhiều field:

```json
{
  "code": "SU26",
  "name": "Summer Capstone 2026",
  "note": "Updated note",
  "start_date": "2026-05-04",
  "end_date": "2026-08-23"
}
```

Không được sửa `status` trực tiếp. Khi sửa ngày, backend tính lại
`academic_year` và kiểm tra duration. Response `200` là `SemesterResponse` đầy đủ.

### 4.5. Khóa semester

```http
POST /api/v1/semesters/{semester_id}/transition
Content-Type: application/json
```

Request transition:

```json
{
  "target_status": "ARCHIVED",
  "reason": "Semester completed"
}
```

Chỉ transition kế tiếp theo thứ tự `PLANNING → ACTIVE → CLOSED → ARCHIVED` hợp lệ. Response giữ contract tương thích:

```json
{
  "id": 1,
  "status": "ARCHIVED"
}
```

### 4.6. Chọn semester hiện tại

```http
POST /api/v1/semesters/{semester_id}/set-current
```

Không cần request body.

Nếu target đang `PLANNING` hoặc `CLOSED`:

1. Lock lifecycle bằng advisory lock.
2. Lock semester ACTIVE hiện tại và target theo thứ tự ID.
3. Chuyển semester ACTIVE cũ thành `CLOSED`.
4. Chuyển target thành `ACTIVE`.
5. Ghi audit cho cả hai row.

Nếu target đã `ACTIVE`, API idempotent và chỉ trả lại resource hiện tại.
Response `200` là `SemesterResponse` đầy đủ.

## 5. Error contract

| Status | Code | Khi xảy ra |
|---:|---|---|
| `401` | `Authentication required` | Chưa đăng nhập hoặc session hết hạn |
| `403` | `Insufficient permission` | Không phải `ADMIN`/`MANAGER` |
| `404` | `SEMESTER_NOT_FOUND` | Không tìm thấy semester |
| `409` | `DATA_DUPLICATE` | Trùng semester code |
| `409` | `ACTIVE_SEMESTER_EXISTS` | Tạo ACTIVE khi đã có ACTIVE khác |
| `422` | `SEMESTER_DURATION_INVALID` | Duration ngoài 105–120 ngày |
| `422` | `SEMESTER_DATE_INVALID` | Ngày thiếu hoặc `end_date < start_date` |
| `422` | `SEMESTER_STATUS_INVALID` | Transition không hợp lệ |
| `422` | `ACADEMIC_YEAR_INVALID` | Filter không đúng `YYYY-YYYY` |

## 6. Flow FE Manager

```text
POST /api/v1/auth/login
        ↓
GET /api/v1/auth/me
        ↓
GET /api/v1/semesters?status=ACTIVE
        ↓
GET /api/v1/semesters/{id}
        ↓
Manager tạo/sửa form
        ├── POST /api/v1/semesters
        └── PATCH /api/v1/semesters/{id}
        ↓
Các action
        ├── POST /api/v1/semesters/{id}/transition
        └── POST /api/v1/semesters/{id}/set-current
```

FE phải dùng cookie session:

```ts
fetch(`${API_URL}/api/v1/semesters`, {
  credentials: "include",
});
```

Mutation (`POST`, `PATCH`) phải gửi thêm `X-CSRF-Token` bằng giá trị cookie
`scheduler_csrf`.

## 7. Seed và Docker

Stack hiện không còn service `db-init`. Khi `docker compose up`:

- API và worker cùng gọi `tools/bootstrap_database.py`.
- Script dùng advisory lock để chỉ một tiến trình bootstrap database tại một thời điểm.
- Chạy Alembic migration.
- Import Excel nếu database chưa có dữ liệu.
- Load fixture `seed-v1` theo cơ chế idempotent.

Restart không xóa dữ liệu hiện tại. Muốn xóa database phải chủ động dùng
`docker compose down -v`.

## 8. Verification

Đã kiểm tra:

- OpenAPI hiển thị đủ request/response fields.
- Migration head `0026_semester_four_states`.
- Có đúng tối đa một semester `ACTIVE`.
- CORS preflight cho local FE trả `200` với credentials.
- Login/session flow trả `200`.
- Full test suite: **100 tests passed**.

## 9. Files liên quan

- `apps/api/app/routes/master_data.py`
- `apps/api/app/routes/manager_extensions.py`
- `apps/api/app/services/semester_queries.py`
- `apps/api/app/response_models.py`
- `apps/api/migrations/versions/0016_semester_active_closed.py`
- `apps/api/migrations/versions/0017_semester_manager_metadata.py`
- `apps/api/migrations/versions/0018_semester_audit_backfill.py`
- `apps/api/migrations/versions/0026_semester_four_states.py`
- `plans/semester-manager-flow/spec.md`
- `plans/semester-manager-flow/plan.md`
