# Manager FE API Flow

Tài liệu này mô tả thứ tự gọi API cho màn hình `MANAGER`, kèm request/response chính.

## 0. Quy ước chung

- Base URL local: `http://localhost:8000`.
- API prefix: `/api/v1`.
- Dùng session cookie, không dùng Bearer token.
- FE phải dùng `credentials: "include"`.
- `POST`, `PATCH`, `DELETE` cần gửi `X-CSRF-Token` bằng giá trị cookie `scheduler_csrf`.
- `401`: chưa đăng nhập/session hết hạn.
- `403`: sai role hoặc không có quyền trên resource.
- `409`: duplicate hoặc conflict cạnh tranh dữ liệu.
- `422`: request/state/business rule không hợp lệ.

## 1. Thứ tự flow tổng thể

```text
POST /auth/login
  ↓
GET /auth/me hoặc GET /me
  ↓
GET /semesters?status=ACTIVE
GET /majors, /lecturers, /rooms
GET /projects?semester_id={semesterId}
GET /groups?semester_id={semesterId}
  ↓
POST /rounds
  ↓
POST /rounds/{id}/days
  ↓
POST /rounds/{id}/resources
  ↓
POST /rounds/{id}/invitations
  ↓
POST /rounds/{id}/transition  (mở registration: OPEN_REGISTRATION)
  ↓
GET /rounds/{id}/registration
GET /rounds/{id}/my-availability
  ↓
POST /rounds/{id}/transition  (REGISTRATION_CLOSED)
  ↓
POST /rounds/{id}/transition  (SCHEDULING)
  ↓
POST /rounds/{id}/schedule/run
  ↓
GET /rounds/{id}/schedule/versions
GET /schedule/versions/{version_id}
  ↓
POST /schedule/versions/{version_id}/activate
  ↓
POST /rounds/{round_id}/schedule/publish/{version_id}
  ↓
GET /dashboard, /reports/*, /my/schedule
  ↓
POST /sessions/{id}/result hoặc xử lý reschedule/remediation
```

FE không được tự suy diễn trạng thái; luôn dùng `status` từ response backend.

## 2. Đăng nhập và hydrate app

### `POST /api/v1/auth/login`

Request:

```json
{
  "email": "manager@example.com",
  "password": "your-password"
}
```

Response `200`:

```json
{
  "role": "MANAGER",
  "expires_at": "2026-08-19T03:00:00+00:00"
}
```

Backend set HttpOnly session cookie và cookie `scheduler_csrf`.

### `GET /api/v1/auth/me`

Response `200`:

```json
{
  "role": "MANAGER",
  "status": "ACTIVE",
  "account_id": 12
}
```

### `GET /api/v1/me`

Response `200`:

```json
{
  "role": "MANAGER",
  "status": "ACTIVE"
}
```

### `POST /api/v1/auth/logout`

Response:

```json
{ "status": "signed_out" }
```

## 3. Chuẩn bị master data

### Semester

#### `GET /api/v1/semesters`

Response:

```json
[
  {
    "id": 1,
    "code": "SP26",
    "name": "Spring 2026",
    "start_date": "2026-05-11",
    "end_date": "2026-08-23",
  "status": "ACTIVE",
    "created_at": "2026-08-18T02:00:00Z"
  }
]
```

#### `GET /api/v1/semesters`

FE khởi tạo Semester Context bằng API này. Có thể truyền `search`, `status` và
`academic_year`; response trả counts và audit actors.

#### `GET /api/v1/semesters/{semester_id}`

Dùng cho màn hình detail/edit; shape giống một item trong list.

#### `POST /api/v1/semesters`

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

Response `201`: semester object như trên, luôn có `status: "ACTIVE"`.
Thời lượng inclusive phải nằm trong cấu hình 105–120 ngày.

#### `PATCH /api/v1/semesters/{semester_id}`

Body gồm một hoặc nhiều field `code`, `name`, `note`, `start_date`, `end_date`.
Không gửi `status` hoặc `academic_year`.

#### `POST /api/v1/semesters/{semester_id}/transition`

Request:

```json
{
  "target_status": "CLOSED",
  "reason": "Semester completed"
}
```

Response:

```json
{ "id": 1, "status": "CLOSED" }
```

Chỉ cho phép `ACTIVE → CLOSED`; chỉ có một semester `ACTIVE`.

#### `POST /api/v1/semesters/{semester_id}/set-current`

Không có request body. Backend đóng semester ACTIVE hiện tại và mở semester
được chọn trong một transaction. Response là semester object đầy đủ; gọi lại
với semester đang ACTIVE là idempotent.

### Lookup data

| API | Response chính |
|---|---|
| `GET /api/v1/majors` | `[{ "id": 2, "code": "SE", "name": "Software Engineering" }]` |
| `GET /api/v1/students` | `[{ "id": 10, "student_code": "SE001" }]` |
| `GET /api/v1/lecturers` | Full lecturer/account/conflicts; xem mẫu bên dưới |
| `GET /api/v1/rooms` | `[{ "id": 3, "code": "R003", "name": "Room 3", "capacity": 30, "active": true }]` |
| `GET /api/v1/projects` | Project kèm `semester_code`, `major_code`, `supervisor_count` |
| `GET /api/v1/groups` | Group kèm `project_code`, `title`, member/leader counts |

`GET /api/v1/lecturers`:

```json
[
  {
    "id": 1,
    "lecturer_code": "LEC001",
    "account_id": 20,
    "email": "lecturer1@gmail.com",
    "display_name": "Lecturer One",
    "account_status": "ACTIVE",
    "conflicts": [
      { "project_id": 12, "reason": "Supervisor conflict" }
    ]
  }
]
```

Manager có thể khai báo conflict thay cho lecturer:

```http
POST /api/v1/lecturers/{lecturer_id}/conflicts
```

```json
{
  "project_id": 12,
  "reason": "Supervisor conflict"
}
```

Response: `{ "id": 8, "lecturer_id": 1, "project_id": 12 }`.

### Tạo project

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
{ "id": 12, "code": "PRJ001", "title": "Capstone Scheduler" }
```

### Tạo group

#### `POST /api/v1/groups`

Request:

```json
{
  "project_id": 12,
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
{ "id": 5, "code": "G001", "member_count": 4 }
```

#### `POST /api/v1/groups/{group_id}/members/{student_id}/drop`

Request:

```json
{ "reason": "Student has withdrawn" }
```

Response:

```json
{
  "group_id": 5,
  "student_id": 10,
  "status": "DROPPED",
  "warning": "GROUP_BELOW_MINIMUM_MAY_CONTINUE"
}
```

#### `POST /api/v1/groups/{group_id}/leader`

Request:

```json
{ "student_id": 10, "reason": "New group leader approved" }
```

Response:

```json
{ "group_id": 5, "leader_student_id": 10 }
```

## 4. Tạo và cấu hình round

### `GET /api/v1/rounds`

Response item:

```json
{
  "id": 4,
  "semester_id": 1,
  "type": "DEFENSE_1_1",
  "status": "DRAFT",
  "reviewer_count": 3,
  "result_owner_mode": true,
  "group_selection_mode": false,
  "session_duration_minutes": 45,
  "registration_deadline": "2026-08-22T17:00:00+07:00",
  "h12_sessions_per_part": 4,
  "h12_sessions_per_day": 8,
  "h12_semester_quota": 20,
  "soft_weights": { "S1": 10, "S2": 5 }
}
```

### `POST /api/v1/rounds`

Request:

```json
{
  "semester_id": 1,
  "type": "DEFENSE_1_1",
  "reviewer_count": 3,
  "result_owner_mode": true,
  "group_selection_mode": false,
  "session_duration_minutes": 45,
  "registration_deadline": "2026-08-22T17:00:00+07:00",
  "h12_sessions_per_part": 4,
  "h12_sessions_per_day": 8,
  "h12_semester_quota": 20,
  "soft_weights": { "S1": 10, "S2": 5 }
}
```

Response `201`: round object như `GET /rounds`, thường `status: "DRAFT"`.

### `POST /api/v1/rounds/{round_id}/days`

Request:

```json
{
  "day_date": "2026-08-25",
  "slots": [
    {
      "start_at": "2026-08-25T08:00:00+07:00",
      "end_at": "2026-08-25T08:45:00+07:00"
    }
  ]
}
```

Response `201`:

```json
{ "round_id": 4, "day_id": 8, "timeslot_ids": [10] }
```

### `POST /api/v1/rounds/{round_id}/resources`

Request:

```json
{
  "group_ids": [5, 6],
  "timeslot_ids": [10, 11],
  "room_ids": [3, 4]
}
```

Response:

```json
{ "round_id": 4, "groups": 2, "timeslots": 2, "rooms": 2 }
```

### `POST /api/v1/rounds/{round_id}/invitations`

Request:

```json
{ "lecturer_ids": [1, 2, 3] }
```

Response:

```json
{ "round_id": 4, "invited_count": 3 }
```

### `POST /api/v1/rounds/{round_id}/transition`

Request:

```json
{ "target_status": "OPEN_REGISTRATION", "reason": "Open lecturer registration" }
```

Response:

```json
{ "round_id": 4, "status": "OPEN_REGISTRATION" }
```

Round transition tới `SCHEDULING` chỉ thành công khi đã có group, timeslot, room và availability hợp lệ.

### `GET /api/v1/rounds/{round_id}/registration`

Response:

```json
{
  "invited": 3,
  "responded": 2,
  "lecturer_availability": 2,
  "group_availability": 0
}
```

### Nhập availability thay cho lecturer/group

#### `POST /api/v1/rounds/{round_id}/lecturers/{lecturer_id}/availability`

Request:

```json
{
  "selected_timeslot_ids": [10, 11],
  "load_preference": "MEDIUM"
}
```

Response:

```json
{
  "round_id": 4,
  "lecturer_id": 1,
  "selected_count": 2,
  "total_slots": 12,
  "source": "MANAGER"
}
```

#### `POST /api/v1/rounds/{round_id}/groups/{group_id}/availability`

Request có cùng format `selected_timeslot_ids` và `load_preference`.

Response:

```json
{
  "round_id": 4,
  "group_id": 5,
  "selected_count": 2,
  "total_slots": 12,
  "source": "MANAGER"
}
```

### Ghi nhận phản hồi invitation thay lecturer

`POST /api/v1/rounds/{round_id}/invitations/{lecturer_id}/response`

```json
{
  "response": "ACCEPTED",
  "reason": "Available for this round"
}
```

Response: `{ "round_id": 4, "lecturer_id": 1, "response": "ACCEPTED" }`.

### `GET /api/v1/rounds/{round_id}/my-availability`

Manager nhận view audit:

```json
{
  "round": {
    "id": 4,
    "type": "DEFENSE_1_1",
    "group_selection_mode": false,
    "registration_deadline": "2026-08-22T10:00:00Z"
  },
  "timeslots": [
    { "id": 10, "start_at": "...", "end_at": "...", "day_date": "2026-08-25" }
  ],
  "selected_by_lecturer": [
    { "lecturer_id": 1, "timeslot_id": 10, "state": "AVAILABLE" }
  ],
  "selected_by_group": {}
}
```

### `GET /api/v1/my/rounds`

Manager nhận các round mình có quyền quản lý:

```json
[
  {
    "id": 4,
    "semester_id": 1,
    "semester_code": "SP26",
    "type": "DEFENSE_1_1",
    "status": "OPEN_REGISTRATION",
    "group_selection_mode": false,
    "registration_deadline": "2026-08-22T17:00:00Z"
  }
]
```

## 5. Chạy scheduler và công bố lịch

### `POST /api/v1/rounds/{round_id}/schedule/run`

Request:

```json
{ "random_seed": 42, "time_limit_seconds": 30 }
```

Response `201`:

```json
{
  "version_id": 21,
  "status": "OPTIMAL",
  "scheduled_count": 12,
  "unscheduled": [],
  "soft_scores": { "S1": 4, "S2": 2 }
}
```

### `GET /api/v1/rounds/{round_id}/schedule/versions`

Response:

```json
[
  {
    "id": 21,
    "round_id": 4,
    "version_no": 1,
    "status": "VALID",
    "solver_status": "OPTIMAL",
    "total_score": 123.4,
    "soft_scores": { "S1": 4 },
    "random_seed": 42,
    "created_at": "...",
    "activated_at": null
  }
]
```

### `GET /api/v1/schedule/versions/{version_id}`

Response gồm version fields và `sessions`:

```json
{
  "id": 21,
  "round_id": 4,
  "version_no": 1,
  "status": "VALID",
  "sessions": [
    {
      "id": 100,
      "group_id": 5,
      "group_code": "G001",
      "project_id": 12,
      "timeslot_id": 10,
      "room_id": 3,
      "start_at": "...",
      "end_at": "...",
      "status": "SCHEDULED",
      "reviewer_ids": [1, 2, 3],
      "result_owner_ids": [1],
      "reviewer_names": { "1": "Lecturer One" }
    }
  ]
}
```

### Activate và publish

```http
POST /api/v1/schedule/versions/{version_id}/activate
```

Response:

```json
{ "version_id": 21, "status": "VALID" }
```

```http
POST /api/v1/rounds/{round_id}/schedule/publish/{version_id}
```

Response:

```json
{
  "round_id": 4,
  "version_id": 21,
  "status": "PUBLISHED",
  "recipient_count": 35
}
```

## 6. Vận hành sau khi publish

### Sửa schedule version trước publish

#### `POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/edit`

Request:

```json
{
  "timeslot_id": 11,
  "room_id": 4,
  "reviewer_ids": [1, 2, 3],
  "result_owner_id": 1,
  "reason": "Resolve room maintenance conflict"
}
```

Response:

```json
{ "session_id": 100, "version_id": 21, "status": "UPDATED" }
```

### Controlled change cho version published

`POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/controlled-change`

Response:

```json
{ "version_id": 22, "source_version_id": 21, "session_id": 101, "status": "VALID" }
```

FE phải reload version mới, sau đó activate và publish nếu muốn công bố thay đổi.

### Gợi ý thay reviewer/slot/phòng

`GET /api/v1/sessions/{session_id}/replacement-suggestions`

Response:

```json
[
  { "timeslot_id": 11, "room_id": 4, "reviewer_ids": [2, 3], "replaces": [1] }
]
```

### Hoãn và reschedule

`POST /api/v1/sessions/{session_id}/postpone`

```json
{ "reason": "Campus closure" }
```

Response: `{ "id": 100, "status": "POSTPONED" }`.

`POST /api/v1/sessions/{session_id}/reschedule-requests`

```json
{ "reason": "Reviewer unavailable on scheduled date" }
```

Response `201`: `{ "id": 55, "status": "REQUESTED" }`.

`POST /api/v1/reschedule-requests/{request_id}/decision`

```json
{ "decision": "APPROVED", "note": "Moved to next available slot" }
```

Response: `{ "id": 55, "status": "APPROVED", "decision_note": "..." }`.

Decision chỉ đổi trạng thái request; việc sắp lịch thực tế dùng edit/controlled-change.

### Round operation

`POST /api/v1/rounds/{round_id}/operation`

Request:

```json
{
  "action": "POSTPONED",
  "reason": "Campus closure"
}
```

`action` là `POSTPONED` hoặc `CANCELLED`.

Response:

```json
{ "round_id": 4, "status": "POSTPONED" }
```

Operation ghi audit/change record và tạo notification cho người bị ảnh hưởng.

### H11 waiver

`POST /api/v1/rounds/{round_id}/groups/{group_id}/h11-waiver`

```json
{ "reason": "Approved exception by Manager" }
```

Response: `{ "id": 7, "round_id": 4, "group_id": 5, "active": true }`.

Xóa waiver:

```http
DELETE /api/v1/rounds/{round_id}/groups/{group_id}/h11-waiver
```

Response: `{ "id": 7, "round_id": 4, "group_id": 5, "active": false }`.

### Result Owner

`POST /api/v1/schedule/versions/{version_id}/sessions/{session_id}/result-owner`

```json
{ "lecturer_id": 1 }
```

Response: `{ "version_id": 21, "session_id": 100, "result_owner_id": 1 }`.

Chỉ dùng khi `result_owner_mode=true` cho `DEFENSE_1_1` hoặc `DEFENSE_2`.

## 7. Result, remediation và reports

### Nhập result

`POST /api/v1/sessions/{session_id}/result`

Body cơ bản:

```json
{
  "outcome": "LEVEL_2",
  "note": "Needs remediation",
  "remediation_due_at": "2026-09-01T17:00:00+07:00",
  "verifier_lecturer_id": 2
}
```

Response `201`:

```json
{ "id": 501, "session_id": 100, "outcome": "LEVEL_2", "group_status": "D12_CONDITIONAL" }
```

### `GET /api/v1/sessions/{session_id}/result`

Response:

```json
{
  "session_id": 100,
  "round_type": "DEFENSE_1_1",
  "group_status": "D12_CONDITIONAL",
  "result": { "id": 501, "outcome": "LEVEL_2", "verify_status": "PENDING" }
}
```

### `GET /api/v1/remediation`

Response item:

```json
{
  "id": 31,
  "group_id": 5,
  "group_code": "G001",
  "status": "OPEN",
  "due_at": "2026-09-01T17:00:00Z",
  "verifier_lecturer_id": 2,
  "note": null,
  "round_type": "DEFENSE_1_1"
}
```

### `POST /api/v1/remediation/{case_id}/overdue-fail`

Request: `{ "reason": "Due date passed" }`.

Response: `{ "id": 31, "status": "FAILED" }`.

### Dashboard/reports

| API | Response chính |
|---|---|
| `GET /api/v1/dashboard?round_id=4` | `availability`, `groups`, `pending_reschedule_requests`, `changes`, `version`, `lecturer_load`, `attention_groups` |
| `GET /api/v1/reports/lecturer-load?round_id=4` | `{ round_id, version, rows }`; row có lecturer/session/quota |
| `GET /api/v1/reports/unscheduled?round_id=4` | `{ round_id, generated_at, versions }` |
| `GET /api/v1/reports/provenance/{version_id}` | Metadata nguồn version: round, type, semester, created time |
| `GET /api/v1/reports/quality` | `{ version, rows }` về group thiếu member/leader |
| `GET /api/v1/reports/remediation?round_id=4` | `{ round_id, version, rows }` |
| `GET /api/v1/reports/outcomes?round_id=4` | `{ round_id, version, rows }` |

## 8. Notifications và lịch

### `GET /api/v1/notifications?limit=50`

Response:

```json
[
  {
    "id": 90,
    "event_type": "SCHEDULE_PUBLISHED",
    "payload": { "round_id": 4, "version_id": 21 },
    "status": "SENT",
    "sent_at": "...",
    "created_at": "..."
  }
]
```

### `POST /api/v1/notifications/{notification_id}/retry`

Không có body. Chỉ retry notification `FAILED`.

Response:

```json
{ "id": 90, "status": "PENDING", "dedupe_key": "..." }
```

### `GET /api/v1/my/schedule?version_id=&from_at=&to_at=`

Response:

```json
{
  "version": { "id": 21, "version_no": 1, "status": "PUBLISHED" },
  "generated_at": "...",
  "sessions": [
    {
      "id": 100,
      "group_id": 5,
      "group_code": "G001",
      "project_id": 12,
      "start_at": "...",
      "end_at": "...",
      "room_id": 3,
      "room_code": "R003",
      "status": "SCHEDULED"
    }
  ]
}
```

### `GET /api/v1/schedule/versions/{version_id}/calendar.ics`

Trả file `text/calendar`; FE dùng `response.blob()` để tải lịch.

## 9. Cache invalidation cho FE

Sau các thao tác sau, FE nên reload/invalidate:

- transition round/semester;
- tạo resources/days/invitations/availability;
- scheduler run;
- activate/publish;
- edit/controlled-change/postpone;
- result/remediation/reschedule decision.

Các query cần invalidate:

```text
round detail
registration
availability
schedule versions
version detail
my schedule
dashboard/reports
notifications
```

Chi tiết schema đầy đủ xem thêm:

- [master-data.md](master-data.md)
- [scheduling.md](scheduling.md)
- [results-reports.md](results-reports.md)
- [schemas.md](schemas.md)
- [auth.md](auth.md)
