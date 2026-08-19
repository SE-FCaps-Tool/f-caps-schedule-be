# Cập nhật Semester Lifecycle và Duration

## Tổng quan

Semester đã được mở rộng để lưu thời gian bắt đầu/kết thúc và quản lý vòng đời rõ ràng.

Trạng thái hợp lệ:

```text
ACTIVE → CLOSED
```

Semester mới luôn được tạo với trạng thái `ACTIVE`.

## API

### Tạo semester

```http
POST /api/v1/semesters
```

Request:

```json
{
  "code": "SP26",
  "name": "Spring 2026",
  "note": "Capstone semester",
  "start_date": "2026-05-11",
  "end_date": "2026-08-23"
}
```

Response `201`:

```json
{
  "id": 1,
  "code": "SP26",
  "name": "Spring 2026",
  "note": "Capstone semester",
  "start_date": "2026-05-11",
  "end_date": "2026-08-23",
  "status": "ACTIVE",
  "created_at": "2026-08-18T02:00:00Z"
}
```

Client không thể chọn trạng thái khi tạo; backend luôn lưu `ACTIVE`.

### Danh sách semester

```http
GET /api/v1/semesters
```

Mỗi phần tử trả về `id`, `code`, `name`, `note`, `start_date`, `end_date`,
`academic_year`, `status`, `project_count`, `group_count`, `round_count`,
`created_at`, `created_by`, `updated_at`, `updated_by`.

Có thể lọc bằng:

```http
GET /api/v1/semesters?search=summer&status=CLOSED&academic_year=2026-2027
```

### Chi tiết, chỉnh sửa và chọn kỳ hiện tại

```http
GET   /api/v1/semesters/{semester_id}
PATCH /api/v1/semesters/{semester_id}
POST  /api/v1/semesters/{semester_id}/set-current
```

PATCH nhận `code`, `name`, `note`, `start_date`, `end_date`; không nhận status.
`set-current` đóng kỳ ACTIVE cũ và mở kỳ đích nguyên tử, đồng thời ghi audit.

### Chuyển trạng thái

```http
POST /api/v1/semesters/{semester_id}/transition
```

Request:

```json
{
  "target_status": "CLOSED",
  "reason": "Semester completed"
}
```

Response:

```json
{
  "id": 1,
  "status": "CLOSED"
}
```

Chỉ `ADMIN` và `MANAGER` được thực hiện thao tác này. Hệ thống chỉ cho phép:

- `ACTIVE` → `CLOSED`

Không cho phép chuyển ngược hoặc bỏ qua trạng thái. Chỉ một semester được `ACTIVE` tại một thời điểm.

## Kiểm tra thời lượng

Thời lượng được tính inclusive:

```text
duration_days = (end_date - start_date).days + 1
```

Mặc định semester phải dài từ 105 đến 120 ngày.

Nếu ngày không hợp lệ hoặc thời lượng nằm ngoài khoảng cho phép, API trả:

```json
{
  "detail": {
    "code": "SEMESTER_DURATION_INVALID",
    "message": "..."
  }
}
```

HTTP status: `422`.

## Cấu hình

Có thể ghi đè trong `.env`:

```env
SEMESTER_MIN_DURATION_DAYS=105
SEMESTER_MAX_DURATION_DAYS=120
```

## Database migration

Migrations:

```text
apps/api/migrations/versions/0013_semester_lifecycle.py
apps/api/migrations/versions/0016_semester_active_closed.py
```

Migration thực hiện:

- Thêm `start_date DATE` và `end_date DATE` vào bảng `semesters`.
- Backfill dữ liệu semester cũ.
- Thêm constraint `end_date >= start_date`.
- Đổi enum cũ `UPCOMING, ACTIVE, CLOSED` thành `ACTIVE, CLOSED`.
- Chuyển các row legacy về `ACTIVE` hoặc `CLOSED`, giữ tối đa một row `ACTIVE`.
- Giữ unique index đảm bảo chỉ có một semester `ACTIVE`.

## Dữ liệu hiện tại

Semester Excel hiện tại:

```text
Code:       SE-2026-2027
Start date: 2026-05-11
End date:   2026-08-23
Status:     ACTIVE
```

## Seed và import

Các nguồn seed/import đã được cập nhật để luôn cung cấp ngày semester và dùng trạng thái `ACTIVE`:

- `apps/api/app/domain/seed.py`
- `apps/api/app/services/seed_loader.py`
- `tools/import_excel_database.py`
- `apps/api/scripts/seed_student1_full.py`

## Kiểm thử và vận hành

Đã kiểm tra:

- Migration từ database rỗng đến `0013_semester_lifecycle`.
- Tạo semester hợp lệ và không hợp lệ.
- Chuyển trạng thái `ACTIVE → CLOSED`.
- Constraint database và duplicate code.
- `/health` trả HTTP `200`.
- `/docs` trả HTTP `200`.

Commit triển khai:

```text
ca17a6a feat(api): add semester lifecycle and duration management
```
