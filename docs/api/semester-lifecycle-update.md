# Cập nhật Semester Lifecycle và Duration

## Tổng quan

Semester đã được mở rộng để lưu thời gian bắt đầu/kết thúc và quản lý vòng đời rõ ràng.

Trạng thái hợp lệ:

```text
UPCOMING → ACTIVE → CLOSED
```

Semester mới luôn được tạo với trạng thái `UPCOMING`.

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
  "start_date": "2026-05-11",
  "end_date": "2026-08-23",
  "status": "UPCOMING",
  "created_at": "2026-08-18T02:00:00Z"
}
```

Client không thể chọn trạng thái khi tạo; backend luôn lưu `UPCOMING`.

### Danh sách semester

```http
GET /api/v1/semesters
```

Mỗi phần tử trả về `id`, `code`, `name`, `start_date`, `end_date`, `status` và `created_at`.

### Chuyển trạng thái

```http
POST /api/v1/semesters/{semester_id}/transition
```

Request:

```json
{
  "target_status": "ACTIVE",
  "reason": "Open semester"
}
```

Response:

```json
{
  "id": 1,
  "status": "ACTIVE"
}
```

Chỉ `ADMIN` và `MANAGER` được thực hiện thao tác này. Hệ thống chỉ cho phép:

- `UPCOMING` → `ACTIVE`
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

Migration:

```text
apps/api/migrations/versions/0013_semester_lifecycle.py
```

Migration thực hiện:

- Thêm `start_date DATE` và `end_date DATE` vào bảng `semesters`.
- Backfill dữ liệu semester cũ.
- Thêm constraint `end_date >= start_date`.
- Đổi enum cũ `DRAFT, ACTIVE, CLOSED` thành `UPCOMING, ACTIVE, CLOSED`.
- Chuyển các row `DRAFT` thành `UPCOMING`.
- Giữ unique index đảm bảo chỉ có một semester `ACTIVE`.

## Dữ liệu hiện tại

Semester Excel hiện tại:

```text
Code:       SE-2026-2027
Start date: 2026-05-11
End date:   2026-08-23
Status:     UPCOMING
```

## Seed và import

Các nguồn seed/import đã được cập nhật để luôn cung cấp ngày semester và dùng trạng thái `UPCOMING`:

- `apps/api/app/domain/seed.py`
- `apps/api/app/services/seed_loader.py`
- `tools/import_excel_database.py`
- `apps/api/scripts/seed_student1_full.py`

## Kiểm thử và vận hành

Đã kiểm tra:

- Migration từ database rỗng đến `0013_semester_lifecycle`.
- Tạo semester hợp lệ và không hợp lệ.
- Chuyển trạng thái `UPCOMING → ACTIVE → CLOSED`.
- Constraint database và duplicate code.
- `/health` trả HTTP `200`.
- `/docs` trả HTTP `200`.

Commit triển khai:

```text
ca17a6a feat(api): add semester lifecycle and duration management
```
