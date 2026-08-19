# Manager API — Semester-scoped contract (target)

Tài liệu này quy định contract mục tiêu để FE Manager gọi API theo một `semester_id` đã chọn.
Đây là target contract; không phải toàn bộ endpoint bên dưới đã được enforce trong backend hiện tại.
Các mục có nhãn “Đã hỗ trợ” là những route đã có filter; các mục “Cần bổ sung” là phần việc backend tiếp theo.

## 1. Quy tắc chung

- Theo target contract, tất cả API danh sách, dashboard, report và export của Manager phải nằm trong một Semester Context.
- `semester_id` mục tiêu là số nguyên dương và phải tồn tại trong bảng `semesters`.
- Nếu API nhận thêm `round_id`, `project_id`, `group_id`, `session_id` hoặc `version_id`, backend mục tiêu phải kiểm tra resource đó thuộc đúng `semester_id`.
- Resource không thuộc semester trả `404` với mã `RESOURCE_OUTSIDE_SEMESTER` hoặc `404` tương ứng với resource.
- Không được để FE tải dữ liệu toàn bộ các semester rồi tự lọc ở client.
- Các API ghi dữ liệu vẫn phải gửi cookie session và header `X-CSRF-Token`.
- Các endpoint Manager dưới đây dành cho `ADMIN` và `MANAGER`, trừ khi có ghi chú khác. Một số endpoint
  schedule dùng chung còn cho phép `LECTURER` hoặc `STUDENT`; FE không được suy rộng quyền từ tài liệu này.

## 2. Chọn semester

```http
GET /api/v1/semesters
```

Response:

```json
[
  {
    "id": 1,
    "code": "SE-2026-2027",
    "name": "Semester 2026-2027",
    "status": "ACTIVE",
    "start_date": "2026-08-01",
    "end_date": "2026-11-29"
  }
]
```

FE lưu `semester.id` làm `semester_id` cho toàn bộ màn hình Manager.

## 3. API target bắt buộc `semester_id`

Đây là request contract cần áp dụng sau khi backend hoàn tất strict validation. Hiện một số route
vẫn nhận `semester_id` optional hoặc chưa khai báo tham số này; xem mục 8.

### Master data

```http
GET /api/v1/projects?semester_id=1
GET /api/v1/groups?semester_id=1
GET /api/v1/rounds?semester_id=1
```

`GET /projects` trả project, `major_code` và danh sách supervisor. `GET /groups` trả leader,
số thành viên và `ui_status`. `GET /rounds` trả toàn bộ round thuộc semester.

### Dashboard và reports

```http
GET /api/v1/dashboard?semester_id=1
GET /api/v1/reports/lecturer-load?semester_id=1
GET /api/v1/reports/quality?semester_id=1
GET /api/v1/reports/remediation?semester_id=1
GET /api/v1/reports/outcomes?semester_id=1
GET /api/v1/reports/group-progress?semester_id=1
```

Dashboard phải scope theo semester cho totals, availability, selected version, lecturer load,
reschedule requests, changes và attention groups.

### Schedule, session và result

```http
GET /api/v1/sessions?semester_id=1
GET /api/v1/reschedule-requests?semester_id=1
GET /api/v1/results?semester_id=1
GET /api/v1/semesters/1/lecturer-quotas
```

Nếu cần lọc sâu hơn, FE có thể truyền thêm `round_id`, `version_id` hoặc `status_filter`,
nhưng `semester_id` vẫn bắt buộc:

```http
GET /api/v1/sessions?semester_id=1&round_id=12&status_filter=SCHEDULED
```

### Export

```http
GET /api/v1/exports/semester/1/schedule.xlsx
GET /api/v1/exports/semester/1/results.xlsx
```

Export chỉ lấy schedule version đã activate và có trạng thái `VALID` hoặc `PUBLISHED`.

## 4. API tạo/cập nhật phải gắn với semester

### Tạo round

`semester_id` là bắt buộc trong body:

```http
POST /api/v1/rounds
Content-Type: application/json
X-CSRF-Token: <csrf-token>
```

```json
{
  "semester_id": 1,
  "type": "DEFENSE_1_1",
  "reviewer_count": 3,
  "start_date": "2026-09-01",
  "end_date": "2026-09-10",
  "session_duration_minutes": 30
}
```

### Tạo project

`semester_id` là bắt buộc trong body:

```json
{
  "semester_id": 1,
  "major_id": 2,
  "code": "PRJ001",
  "title": "Capstone Scheduler",
  "supervisors": ["LEC001:MAIN"]
}
```

### Import Excel

```http
POST /api/v1/projects/import?semester_id=1
POST /api/v1/groups/import?semester_id=1
Content-Type: multipart/form-data
```

Nếu file có cột `semester_code`, giá trị trong file phải khớp với `semester_id` trên request.
Không cho phép import một file vào nhiều semester trong cùng một request.

## 5. API target dùng resource ID nhưng phải kiểm tra semester

Các API detail/action vẫn cần ID riêng của resource; không thay `round_id` hoặc `project_id`
bằng `semester_id`. Theo target contract, request phải truyền thêm `semester_id` để backend kiểm tra phạm vi:

```http
GET   /api/v1/rounds/12?semester_id=1
PATCH /api/v1/rounds/12?semester_id=1
GET   /api/v1/projects/45?semester_id=1
PATCH /api/v1/projects/45?semester_id=1
GET   /api/v1/groups/8?semester_id=1
PATCH /api/v1/groups/8?semester_id=1
GET   /api/v1/rounds/12/invitations?semester_id=1
GET   /api/v1/rounds/12/groups?semester_id=1
GET   /api/v1/schedule/versions/22?semester_id=1
DELETE /api/v1/schedule/versions/22?semester_id=1
```

Nếu resource không thuộc semester `1`, backend không được trả dữ liệu của resource đó.

## 6. Lecturer quota

```http
GET /api/v1/semesters/1/lecturer-quotas
PUT /api/v1/semesters/1/lecturer-quotas/20
Content-Type: application/json
X-CSRF-Token: <csrf-token>
```

```json
{
  "quota": 8
}
```

`lecturer_id` chỉ là lecturer cần cập nhật; quota luôn thuộc semester nằm trên URL.

## 7. API không cần `semester_id`

Các API global hoặc không thuộc dữ liệu học kỳ không cần truyền `semester_id`:

```http
POST /api/v1/auth/login
GET  /api/v1/majors
GET  /api/v1/lecturers
GET  /api/v1/rooms
GET  /api/v1/accounts
GET  /api/v1/audit
```

`GET /lecturers`, `/rooms`, `/accounts` có thể dùng cho màn hình chọn dữ liệu; khi gắn lecturer,
room hoặc account vào một round, backend phải kiểm tra round đó thuộc semester đang thao tác.

## 8. Trạng thái triển khai hiện tại

### Đã hỗ trợ `semester_id` (hiện tại)

Các endpoint sau đã có filter theo học kỳ trong backend:

```text
GET /projects
GET /groups
GET /rounds
GET /dashboard
GET /reports/lecturer-load
GET /reports/quality
GET /reports/remediation
GET /reports/outcomes
GET /reports/group-progress
GET /semesters/{semester_id}/lecturer-quotas
GET /exports/semester/{semester_id}/schedule.xlsx
GET /exports/semester/{semester_id}/results.xlsx
```

Trong code hiện tại, một số query `semester_id` vẫn là optional để giữ tương thích ngược.

### Cần bổ sung để đạt strict contract

Các endpoint sau hiện chưa đạt strict contract; cần được bổ sung `semester_id` bắt buộc hoặc thêm kiểm tra resource thuộc semester:

```text
GET /sessions
GET /reschedule-requests
GET /results
POST /projects/import
POST /groups/import
GET/PATCH /rounds/{round_id}
GET/PATCH /projects/{project_id}
GET/PATCH /groups/{group_id}
GET/PATCH/DELETE /timeslots/{timeslot_id}
GET/DELETE /schedule/versions/{version_id}
GET /rounds/{round_id}/schedule/versions
POST /rounds/{round_id}/schedule/run
POST /rounds/{round_id}/schedule/publish/{version_id}
POST /schedule/versions/{version_id}/activate
POST /schedule/versions/{version_id}/sessions/{session_id}/edit
POST /schedule/versions/{version_id}/sessions/{session_id}/controlled-change
POST /sessions/{session_id}/postpone
POST /sessions/{session_id}/reschedule-requests
POST /reschedule-requests/{request_id}/decision
GET /reports/unscheduled
GET /reports/provenance/{version_id}
GET /notifications
GET /audit
```

Đây là yêu cầu contract cho FE; việc đổi các endpoint trên thành bắt buộc là breaking change,
cần cập nhật FE và test integration cùng lúc.

## 9. Checklist FE

1. Gọi `GET /api/v1/semesters` khi vào Manager portal.
2. Chọn một semester và lưu `semester_id` trong context/store.
3. Gắn `semester_id` vào mọi request list/dashboard/report/session/result/export.
4. Với detail/action, truyền cả resource ID và `semester_id`.
5. Khi đổi semester, hủy request cũ và tải lại toàn bộ dữ liệu theo semester mới.
6. Không dùng dữ liệu của semester trước để hiển thị trong semester hiện tại.

> Khi áp dụng strict contract, backend nên trả `422 SEMESTER_REQUIRED` nếu thiếu `semester_id`,
> và `404 RESOURCE_OUTSIDE_SEMESTER` nếu resource ID không thuộc semester đã chọn.

## 10. Request/response đầy đủ cho FE

### 10.1 Quy ước lỗi dùng chung

```json
{
  "detail": {
    "code": "SEMESTER_REQUIRED",
    "message": "semester_id is required for this Manager endpoint."
  }
}
```

| HTTP | `detail.code` | Ý nghĩa |
|---:|---|---|
| 401 | `AUTH_REQUIRED` | Chưa đăng nhập hoặc session hết hạn |
| 403 | `INSUFFICIENT_PERMISSION` | Không phải Admin/Manager hoặc ngoài quyền |
| 404 | `SEMESTER_NOT_FOUND` | Semester không tồn tại |
| 404 | `RESOURCE_OUTSIDE_SEMESTER` | Resource không thuộc semester đã chọn |
| 409 | `DATA_DUPLICATE` | Trùng code/email hoặc dữ liệu đang bị khóa |
| 422 | `SEMESTER_REQUIRED` | Thiếu `semester_id` |
| 422 | `SEMESTER_INVALID` | `semester_id` không hợp lệ |
| 422 | `VALIDATION_ERROR` | Body/query sai kiểu hoặc sai business rule |

### 10.2 Semester

#### `GET /api/v1/semesters`

Request: không có body.

Response `200`:

```json
[
  {
    "id": 1,
    "code": "SE-2026-2027",
    "name": "Semester 2026-2027",
    "start_date": "2026-08-01",
    "end_date": "2026-11-29",
    "status": "ACTIVE",
    "created_at": "2026-07-25T08:00:00Z"
  }
]
```

#### `POST /api/v1/semesters`

Request:

```json
{
  "code": "SE-2027-2028",
  "name": "Semester 2027-2028",
  "start_date": "2027-08-01",
  "end_date": "2027-11-29"
}
```

Response `201`:

```json
{
  "id": 2,
  "code": "SE-2027-2028",
  "name": "Semester 2027-2028",
  "start_date": "2027-08-01",
  "end_date": "2027-11-29",
  "status": "UPCOMING",
  "created_at": "2027-07-20T08:00:00Z"
}
```

#### `PATCH /api/v1/semesters/{semester_id}`

Request: mọi field đều optional; duration sau khi merge phải nằm trong cấu hình 105–120 ngày.

```json
{
  "name": "Semester 2026-2027 — Updated",
  "start_date": "2026-08-01",
  "end_date": "2026-11-29"
}
```

Response `200`:

```json
{
  "id": 1,
  "code": "SE-2026-2027",
  "name": "Semester 2026-2027 — Updated",
  "start_date": "2026-08-01",
  "end_date": "2026-11-29",
  "status": "ACTIVE",
  "created_at": "2026-07-25T08:00:00Z"
}
```

### 10.3 Projects và groups

#### `GET /api/v1/projects?semester_id=1`

Response `200`:

```json
[
  {
    "id": 45,
    "code": "PRJ001",
    "title": "Capstone Scheduler",
    "status": "ACTIVE",
    "semester_id": 1,
    "semester_code": "SE-2026-2027",
    "major_code": "SE",
    "supervisor_count": 2,
    "supervisors": [
      { "lecturer_code": "LEC001", "display_name": "Lecturer One", "type": "MAIN" },
      { "lecturer_code": "LEC002", "display_name": "Lecturer Two", "type": "CO" }
    ]
  }
]
```

#### `POST /api/v1/projects`

Request:

```json
{
  "semester_id": 1,
  "major_id": 2,
  "code": "PRJ001",
  "title": "Capstone Scheduler",
  "supervisors": ["LEC001:MAIN", "LEC002:CO"]
}
```

Response `201`:

```json
{
  "id": 45,
  "semester_id": 1,
  "major_id": 2,
  "code": "PRJ001",
  "title": "Capstone Scheduler",
  "status": "ACTIVE"
}
```

#### `GET /api/v1/projects/{project_id}?semester_id=1`

Response `200`:

```json
{
  "id": 45,
  "code": "PRJ001",
  "title": "Capstone Scheduler",
  "status": "ACTIVE",
  "semester_id": 1,
  "semester_code": "SE-2026-2027",
  "major_code": "SE",
  "supervisors": [
    { "id": 20, "lecturer_code": "LEC001", "display_name": "Lecturer One", "supervisor_type": "MAIN" }
  ],
  "group": { "id": 8, "code": "G001", "status": "PENDING_D11" }
}
```

#### `PATCH /api/v1/projects/{project_id}?semester_id=1`

Request: mọi field optional.

```json
{
  "code": "PRJ001-UPDATED",
  "title": "Updated Capstone Scheduler",
  "supervisors": ["LEC001:MAIN"]
}
```

Response `200`:

```json
{
  "id": 45,
  "code": "PRJ001-UPDATED",
  "title": "Updated Capstone Scheduler",
  "status": "ACTIVE",
  "semester_id": 1
}
```

#### `GET /api/v1/groups?semester_id=1`

Response `200`:

```json
[
  {
    "id": 8,
    "code": "G001",
    "status": "PENDING_D11",
    "ui_status": "ACTIVE",
    "project_code": "PRJ001",
    "title": "Capstone Scheduler",
    "active_member_count": 4,
    "leader_count": 1,
    "leader_name": "Student One"
  }
]
```

#### `POST /api/v1/groups`

Request:

```json
{
  "project_id": 45,
  "code": "G001",
  "members": [
    { "student_code": "SE001", "role": "LEADER" },
    { "student_code": "SE002", "role": "MEMBER" },
    { "student_code": "SE003", "role": "MEMBER" },
    { "student_code": "SE004", "role": "MEMBER" }
  ]
}
```

Response `201`:

```json
{
  "id": 8,
  "project_id": 45,
  "code": "G001",
  "status": "PENDING_D11"
}
```

#### `GET /api/v1/groups/{group_id}?semester_id=1`

Response `200`:

```json
{
  "id": 8,
  "code": "G001",
  "status": "PENDING_D11",
  "project_id": 45,
  "project_code": "PRJ001",
  "title": "Capstone Scheduler",
  "members": [
    { "student_id": 101, "student_code": "SE001", "display_name": "Student One", "role": "LEADER", "status": "ACTIVE" },
    { "student_id": 102, "student_code": "SE002", "display_name": "Student Two", "role": "MEMBER", "status": "ACTIVE" }
  ]
}
```

### 10.4 Round

#### `GET /api/v1/rounds?semester_id=1`

Response `200`:

```json
[
  {
    "id": 12,
    "semester_id": 1,
    "type": "DEFENSE_1_1",
    "status": "OPEN_REGISTRATION",
    "reviewer_count": 3,
    "result_owner_mode": true,
    "group_selection_mode": false,
    "session_duration_minutes": 45,
    "start_date": "2026-09-01",
    "end_date": "2026-09-10",
    "registration_deadline": "2026-08-28T17:00:00Z",
    "h12_sessions_per_part": 4,
    "h12_sessions_per_day": 8,
    "h12_semester_quota": 20,
    "max_groups_per_timeslot": 6,
    "max_minutes_per_part": 240,
    "max_minutes_per_day": 480,
    "soft_weights": { "S1": 10, "S2": 5 }
  }
]
```

#### `POST /api/v1/rounds`

Request:

```json
{
  "semester_id": 1,
  "type": "DEFENSE_1_1",
  "reviewer_count": 3,
  "result_owner_mode": true,
  "group_selection_mode": false,
  "session_duration_minutes": 45,
  "start_date": "2026-09-01",
  "end_date": "2026-09-10",
  "registration_deadline": "2026-08-28T17:00:00Z",
  "h12_sessions_per_part": 4,
  "h12_sessions_per_day": 8,
  "h12_semester_quota": 20,
  "max_groups_per_timeslot": 6,
  "max_minutes_per_part": 240,
  "max_minutes_per_day": 480,
  "soft_weights": { "S1": 10, "S2": 5 }
}
```

Response `201`: cùng shape với item của `GET /rounds`, kèm `id` được tạo và `status` mặc định `DRAFT`.

#### `GET /api/v1/rounds/{round_id}?semester_id=1`

Response `200`:

```json
{
  "id": 12,
  "semester_id": 1,
  "semester_code": "SE-2026-2027",
  "semester_name": "Semester 2026-2027",
  "type": "DEFENSE_1_1",
  "status": "OPEN_REGISTRATION",
  "reviewer_count": 3,
  "start_date": "2026-09-01",
  "end_date": "2026-09-10",
  "effective_start_date": "2026-09-01",
  "effective_end_date": "2026-09-10",
  "group_count": 25,
  "room_count": 3,
  "active_timeslot_count": 16,
  "days": [
    {
      "id": 30,
      "day_date": "2026-09-01",
      "timeslot_id": 100,
      "start_at": "2026-09-01T08:00:00Z",
      "end_at": "2026-09-01T08:45:00Z",
      "part": "AM",
      "active": true
    }
  ]
}
```

#### `PATCH /api/v1/rounds/{round_id}?semester_id=1`

Request: mọi field optional; chỉ cho sửa khi round là `DRAFT` hoặc `OPEN_REGISTRATION`.

```json
{
  "end_date": "2026-09-12",
  "reviewer_count": 3,
  "max_groups_per_timeslot": 6,
  "max_minutes_per_day": 480
}
```

Response `200`: round detail như `GET /rounds/{round_id}`.

### 10.5 Invitation và lecturer quota

#### `GET /api/v1/rounds/{round_id}/invitations?semester_id=1`

Response `200`:

```json
[
  {
    "round_id": 12,
    "lecturer_id": 20,
    "lecturer_code": "LEC001",
    "display_name": "Lecturer One",
    "email": "lecturer1@example.com",
    "status": "ACCEPTED",
    "response_reason": "Available",
    "responded_at": "2026-08-25T10:00:00Z",
    "available_slot_count": 8,
    "load_preference": "MEDIUM"
  }
]
```

#### `POST /api/v1/rounds/{round_id}/invitations/{lecturer_id}/resend?semester_id=1`

Request: không có body.

Response `200`:

```json
{
  "round_id": 12,
  "lecturer_id": 20,
  "status": "PENDING",
  "resent": true
}
```

#### `GET /api/v1/semesters/{semester_id}/lecturer-quotas`

Response `200`:

```json
[
  {
    "lecturer_id": 20,
    "lecturer_code": "LEC001",
    "display_name": "Lecturer One",
    "quota": 8,
    "used": 3
  }
]
```

#### `PUT /api/v1/semesters/{semester_id}/lecturer-quotas/{lecturer_id}`

Request:

```json
{ "quota": 8 }
```

Response `200`:

```json
{
  "semester_id": 1,
  "lecturer_id": 20,
  "quota": 8,
  "updated_at": "2026-08-29T08:00:00Z"
}
```

### 10.6 Dashboard và reports

#### `GET /api/v1/dashboard?semester_id=1`

Response `200`:

```json
{
  "totals": { "projects": 238, "groups": 205, "students": 296, "lecturers": 70 },
  "availability": { "invited": 40, "responded": 32 },
  "groups": { "total": 205, "scheduled": 180, "unscheduled": 25 },
  "pending_reschedule_requests": 2,
  "changes": 13,
  "version": {
    "version_id": 94,
    "round_id": 12,
    "status": "PUBLISHED",
    "created_at": "2026-08-28T12:00:00Z",
    "type": "DEFENSE_1_1",
    "semester_id": 1,
    "semester_code": "SE-2026-2027",
    "generated_at": "2026-08-29T08:00:00Z"
  },
  "lecturer_load": [
    { "id": 20, "lecturer_code": "LEC001", "display_name": "Lecturer One", "session_count": 6 }
  ],
  "attention_groups": [
    { "id": 8, "code": "G001", "status": "D12_CONDITIONAL" }
  ],
  "attention": { "no_leader": 1, "under_four": 3, "remediation_overdue": 2, "unscheduled": 25 }
}
```

#### `GET /api/v1/reports/lecturer-load?semester_id=1`

Response `200`:

```json
{
  "round_id": null,
  "version": { "version_id": 94, "round_id": 12, "status": "PUBLISHED" },
  "rows": [
    {
      "lecturer_id": 20,
      "lecturer_code": "LEC001",
      "display_name": "Lecturer One",
      "session_count": 6,
      "quota": 8,
      "quota_percent": 75.0
    }
  ]
}
```

#### `GET /api/v1/reports/quality?semester_id=1`

Response `200`:

```json
{
  "version": { "version_id": 94, "round_id": 12, "status": "PUBLISHED" },
  "rows": [
    { "id": 8, "code": "G001", "active_members": 3, "leaders": 1 }
  ]
}
```

#### `GET /api/v1/reports/remediation?semester_id=1`

Response `200`:

```json
{
  "round_id": null,
  "version": { "version_id": 94, "round_id": 12, "status": "PUBLISHED" },
  "rows": [
    {
      "id": 11,
      "group_id": 8,
      "group_code": "G001",
      "due_at": "2026-09-15T17:00:00Z",
      "status": "OPEN",
      "verifier_lecturer_id": 20
    }
  ]
}
```

#### `GET /api/v1/reports/outcomes?semester_id=1`

Response `200`:

```json
{
  "round_id": null,
  "version": { "version_id": 94, "round_id": 12, "status": "PUBLISHED" },
  "rows": [
    { "type": "DEFENSE_1_1", "outcome": "PASSED", "count": 120 },
    { "type": "DEFENSE_1_1", "outcome": "FAILED", "count": 8 }
  ]
}
```

#### `GET /api/v1/reports/group-progress?semester_id=1`

Response `200`:

```json
[
  {
    "group_id": 8,
    "group_code": "G001",
    "project_name": "Capstone Scheduler",
    "group_status": "D12_CONDITIONAL",
    "review_1": "PASSED",
    "review_2": "PASSED",
    "defense_1_1": "CONDITIONAL",
    "defense_1_2": null,
    "defense_2": null,
    "result_verifier_lecturer_id": 20,
    "remediation_status": "OPEN",
    "remediation_due_at": "2026-09-15T17:00:00Z",
    "remediation_verifier_lecturer_id": 20
  }
]
```

### 10.7 Session, reschedule và result

#### `GET /api/v1/sessions?semester_id=1&round_id=12&version_id=94&status_filter=SCHEDULED`

Response `200`:

```json
[
  {
    "id": 500,
    "version_id": 94,
    "round_id": 12,
    "group_id": 8,
    "group_code": "G001",
    "project_code": "PRJ001",
    "timeslot_id": 100,
    "room_id": 3,
    "room_code": "R003",
    "start_at": "2026-09-01T08:00:00Z",
    "end_at": "2026-09-01T08:45:00Z",
    "status": "SCHEDULED",
    "reviewers": [
      { "id": 20, "code": "LEC001", "name": "Lecturer One" }
    ]
  }
]
```

#### `GET /api/v1/reschedule-requests?semester_id=1&status_filter=REQUESTED`

Response `200`:

```json
[
  {
    "id": 77,
    "session_id": 500,
    "requested_by": 20,
    "requester_name": "Lecturer One",
    "reason": "Reviewer unavailable",
    "status": "REQUESTED",
    "reviewed_by": null,
    "created_at": "2026-08-30T08:00:00Z",
    "reviewed_at": null,
    "group_id": 8,
    "group_code": "G001",
    "start_at": "2026-09-01T08:00:00Z",
    "end_at": "2026-09-01T08:45:00Z",
    "room_code": "R003"
  }
]
```

#### `GET /api/v1/results?semester_id=1&round_id=12`

Response `200`:

```json
[
  {
    "id": 900,
    "session_id": 500,
    "group_id": 8,
    "group_code": "G001",
    "round_type": "DEFENSE_1_1",
    "outcome": "PASSED",
    "note": "Good defense",
    "entered_at": "2026-09-01T09:00:00Z",
    "verify_status": "VERIFIED",
    "remediation_due_at": null,
    "verifier_lecturer_id": 20
  }
]
```

### 10.8 Timeslot, import và export

#### `PATCH /api/v1/timeslots/{timeslot_id}?semester_id=1`

Request: mọi field optional; chỉ sửa khi round còn `DRAFT` hoặc `OPEN_REGISTRATION`.

```json
{
  "start_at": "2026-09-01T08:00:00Z",
  "end_at": "2026-09-01T08:45:00Z",
  "part": "AM",
  "active": true
}
```

Response `200`:

```json
{
  "id": 100,
  "round_day_id": 30,
  "start_at": "2026-09-01T08:00:00Z",
  "end_at": "2026-09-01T08:45:00Z",
  "part": "AM",
  "active": true
}
```

#### `POST /api/v1/projects/import?semester_id=1`

Request multipart:

```text
file=<projects.xlsx>
```

Response `201`:

```json
{
  "created": 12,
  "skipped": 2,
  "errors": [
    { "row": 5, "code": "PROJECT_DUPLICATE_OR_INVALID" }
  ]
}
```

#### `POST /api/v1/groups/import?semester_id=1`

Request multipart:

```text
file=<groups.xlsx>
```

Response `201`:

```json
{
  "created": 20,
  "skipped": 1,
  "errors": [
    {
      "group_code": "G021",
      "code": "GROUP_INVALID",
      "message": "Invalid group row; verify project, students and exactly one leader."
    }
  ]
}
```

#### Excel export response

```http
GET /api/v1/exports/semester/1/schedule.xlsx
```

Response `200`:

```http
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="semester-1-schedule.xlsx"
```

Body là binary `.xlsx`, không phải JSON.

### 10.9 Schedule version và scheduling actions

#### `GET /api/v1/rounds/{round_id}/schedule/versions?semester_id=1`

Response `200`:

```json
[
  {
    "id": 94,
    "round_id": 12,
    "version_no": 3,
    "status": "VALID",
    "ui_status": "ACTIVE",
    "is_active": true,
    "solver_status": "OPTIMAL",
    "total_score": 123.4,
    "soft_scores": { "S1": 4, "S2": 2 },
    "random_seed": 42,
    "created_at": "2026-08-28T12:00:00Z",
    "activated_at": "2026-08-28T12:05:00Z"
  }
]
```

#### `POST /api/v1/rounds/{round_id}/schedule/run?semester_id=1`

Request:

```json
{
  "random_seed": 42,
  "time_limit_seconds": 30
}
```

Response `201`:

```json
{
  "version_id": 94,
  "status": "OPTIMAL",
  "scheduled_count": 25,
  "unscheduled": [],
  "soft_scores": { "S1": 4, "S2": 2 }
}
```

#### `GET /api/v1/schedule/versions/{version_id}?semester_id=1`

Response `200`:

```json
{
  "id": 94,
  "round_id": 12,
  "version_no": 3,
  "status": "VALID",
  "solver_status": "OPTIMAL",
  "total_score": 123.4,
  "soft_scores": { "S1": 4, "S2": 2 },
  "created_at": "2026-08-28T12:00:00Z",
  "activated_at": "2026-08-28T12:05:00Z",
  "sessions": [
    {
      "id": 500,
      "group_id": 8,
      "group_code": "G001",
      "project_id": 45,
      "timeslot_id": 100,
      "room_id": 3,
      "start_at": "2026-09-01T08:00:00Z",
      "end_at": "2026-09-01T08:45:00Z",
      "status": "SCHEDULED",
      "reviewer_ids": [20, 21, 22],
      "result_owner_ids": [20],
      "reviewer_names": { "20": "Lecturer One", "21": "Lecturer Two", "22": "Lecturer Three" }
    }
  ]
}
```

#### Activate/publish

```http
POST /api/v1/schedule/versions/94/activate?semester_id=1
POST /api/v1/rounds/12/schedule/publish/94?semester_id=1
```

Request body: không có.

Response activate `200`:

```json
{ "version_id": 94, "status": "VALID" }
```

Response publish `200`:

```json
{ "round_id": 12, "version_id": 94, "status": "PUBLISHED", "recipient_count": 35 }
```

#### `POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/edit?semester_id=1`

Request:

```json
{
  "timeslot_id": 101,
  "room_id": 4,
  "reviewer_ids": [20, 21, 22],
  "result_owner_id": 20,
  "reason": "Resolve room maintenance conflict"
}
```

Response `200`:

```json
{ "session_id": 500, "version_id": 94, "status": "UPDATED" }
```

#### Controlled change sau publish

```http
POST /api/v1/schedule/versions/94/sessions/500/controlled-change?semester_id=1
```

Request body: giống `SessionEditPayload` ở trên.

Response `200`:

```json
{ "version_id": 95, "source_version_id": 94, "session_id": 500, "status": "VALID" }
```

#### `DELETE /api/v1/schedule/versions/{version_id}?semester_id=1`

Request body: không có.

Response `200`:

```json
{ "version_id": 94, "deleted": true }
```

Nếu version đã có session, change record hoặc đã publish, trả `409 VERSION_DELETE_HAS_DEPENDENCIES`.

### 10.10 H11, postpone và reschedule

#### H11 waiver

```http
POST /api/v1/rounds/12/groups/8/h11-waiver?semester_id=1
```

Request:

```json
{ "reason": "Approved exception for this group" }
```

Response `200`:

```json
{ "id": 10, "round_id": 12, "group_id": 8, "active": true }
```

#### Postpone session

```http
POST /api/v1/sessions/500/postpone?semester_id=1
```

Request:

```json
{ "reason": "Reviewer unavailable on scheduled date" }
```

Response `200`:

```json
{ "id": 500, "status": "POSTPONED" }
```

#### Tạo reschedule request

```http
POST /api/v1/sessions/500/reschedule-requests?semester_id=1
```

Request:

```json
{ "reason": "Reviewer unavailable" }
```

Response `201`:

```json
{ "id": 77, "status": "REQUESTED" }
```

#### Quyết định reschedule request

```http
POST /api/v1/reschedule-requests/77/decision?semester_id=1
```

Request:

```json
{ "decision": "APPROVED", "note": "Moved to next available slot" }
```

Response `200`:

```json
{ "id": 77, "status": "APPROVED", "decision_note": "Moved to next available slot" }
```

Decision chỉ đổi trạng thái request; việc đổi lịch thực tế dùng `edit` hoặc `controlled-change`.
