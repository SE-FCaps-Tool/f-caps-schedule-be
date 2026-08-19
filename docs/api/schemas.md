# Request schemas và response shapes

Đây là bảng field chính xác cho các body JSON. Field không ghi `optional` là bắt buộc.

## Auth

### `LoginPayload`

```json
{ "email": "manager@example.com", "password": "your-password" }
```

| Field | Type | Rule |
|---|---|---|
| `email` | string | 3–320 ký tự |
| `password` | string | 1–256 ký tự |

## Master data

### `SemesterCreate`

```json
{ "code": "SP26", "name": "Spring 2026", "note": "Capstone semester", "start_date": "2026-05-11", "end_date": "2026-08-23" }
```

`code`: 1–32; `name`: 1–160; `note`: optional, tối đa 1000; `start_date` và `end_date`: ISO `YYYY-MM-DD`.
Semester mới luôn có status `ACTIVE`. Duration inclusive phải nằm trong cấu hình
`SEMESTER_MIN_DURATION_DAYS` (default 105) và `SEMESTER_MAX_DURATION_DAYS` (default 120).

### `SemesterUpdate`

```json
{ "name": "Spring 2026 - Updated", "note": "Updated note" }
```

Tất cả field đều optional trong PATCH: `code`, `name`, `note`, `start_date`,
`end_date`. Không được gửi `status` hoặc `academic_year`.

### `SemesterResponse`

```json
{
  "id": 1,
  "code": "SP26",
  "name": "Spring 2026",
  "note": null,
  "start_date": "2026-05-11",
  "end_date": "2026-08-23",
  "academic_year": "2026-2027",
  "status": "ACTIVE",
  "project_count": 74,
  "group_count": 74,
  "round_count": 5,
  "created_at": "2026-08-18T02:00:00Z",
  "created_by": null,
  "updated_at": "2026-08-18T02:00:00Z",
  "updated_by": null
}
```

`created_by` và `updated_by` là `{ id, email, display_name }` hoặc `null` với
dữ liệu legacy/import không có actor đáng tin cậy.

### `SemesterTransitionPayload`

```json
{ "target_status": "ARCHIVED", "reason": "Semester completed" }
```

Chỉ cho phép transition kế tiếp `PLANNING → ACTIVE → CLOSED → ARCHIVED`; `reason` dài 1–1000 ký tự.

### `AccountCreate`

```json
{ "email": "lecturer@example.com", "display_name": "Nguyen Van A", "password": "at-least-12-chars", "role": "LECTURER" }
```

`email` 3–320; `display_name` 1–160; `password` 12–256; `role`: `ADMIN | MANAGER | LECTURER | STUDENT`.

### `AccountStatusPayload`

```json
{ "status": "INACTIVE", "reason": "Account owner requested deactivation" }
```

`status`: `ACTIVE | INACTIVE`; `reason`: 1–1000.

### `AccountRolePayload`

```json
{ "role": "MANAGER", "reason": "Promoted for the semester" }
```

`role`: `ADMIN | MANAGER | LECTURER | STUDENT`; `reason`: 1–1000.

Role removal dùng query string, không dùng JSON body: `DELETE /accounts/{account_id}/roles/{role}?reason=...`.

### `LecturerCreate`

```json
{ "lecturer_code": "LEC001", "email": "a@example.com", "display_name": "Lecturer A", "password": "at-least-12-chars" }
```

`lecturer_code` 1–32; `email` 3–320; `display_name` 1–160; `password` 12–256.

### `RoomCreate`

```json
{ "code": "A101", "name": "Room A101", "capacity": 30 }
```

`code` 1–32; `name` 1–160; `capacity` > 0 and ≤ 500.

### `ProjectCreate`

```json
{
  "semester_id": 1,
  "major_id": 2,
  "code": "PRJ001",
  "title": "Capstone Scheduler",
  "supervisors": ["LEC001:MAIN", "LEC002:CO"]
}
```

`semester_id`, `major_id` > 0; `code` 1–64; `title` 1–255; `supervisors` có 1–2 phần tử. Mỗi supervisor là chuỗi `LECTURER_CODE:SUPERVISOR_TYPE`; lecturer code phải tồn tại.

### `MemberPayload` và `GroupCreate`

```json
{
  "project_id": 1,
  "code": "G001",
  "members": [
    { "student_code": "SE001", "role": "LEADER" },
    { "student_code": "SE002", "role": "MEMBER" },
    { "student_code": "SE003", "role": "MEMBER" },
    { "student_code": "SE004", "role": "MEMBER" }
  ]
}
```

`project_id` > 0; `code` 1–64; `members` 4–5 phần tử. Member `role`: `MEMBER` (default) hoặc `LEADER`. Business validation yêu cầu group hợp lệ và một leader.

### `DropoutPayload` và `LeaderPayload`

```json
{ "reason": "Student has withdrawn" }
```

`DropoutPayload.reason`: 1–1000.

```json
{ "student_id": 10, "reason": "New group leader approved" }
```

`LeaderPayload.student_id` > 0; `reason` 1–1000.

### `ConflictCreate`

```json
{ "project_id": 1, "reason": "Cannot review this project due to supervision conflict" }
```

`project_id` > 0; `reason` 1–500.

## Round setup

### `RoundCreate`

```json
{
  "semester_id": 1,
  "type": "DEFENSE_1_1",
  "reviewer_count": 3,
  "start_date": "2026-08-25",
  "end_date": "2026-08-27",
  "result_owner_mode": true,
  "group_selection_mode": false,
  "session_duration_minutes": 45,
  "registration_deadline": "2026-08-22T17:00:00+07:00",
  "h12_sessions_per_part": 4,
  "h12_sessions_per_day": 8,
  "h12_semester_quota": 20,
  "max_groups_per_timeslot": 6,
  "max_minutes_per_part": 240,
  "max_minutes_per_day": 480,
  "soft_weights": { "S1": 10, "S2": 5 }
}
```

| Field | Rule |
|---|---|
| `semester_id` | integer > 0 |
| `start_date`, `end_date` | optional ISO dates; `end_date` không trước `start_date` |
| `type` | string, round type theo business rules, ví dụ `DEFENSE_1_1`, `DEFENSE_1_2`, `DEFENSE_2` |
| `reviewer_count` | integer > 0 |
| `result_owner_mode` | boolean, default `false`; dùng cho D1.1/D2 khi cần chỉ định Result Owner |
| `group_selection_mode` | boolean, default `false` |
| `session_duration_minutes` | integer 1–480 |
| `registration_deadline` | ISO datetime hoặc `null` |
| `h12_sessions_per_part` | integer > 0, default 4 |
| `h12_sessions_per_day` | integer > 0, default 8 |
| `h12_semester_quota` | integer > 0 hoặc `null` |
| `max_groups_per_timeslot` | integer > 0 hoặc `null`; áp dụng giới hạn H13 khi cấu hình |
| `max_minutes_per_part`, `max_minutes_per_day` | integer > 0 hoặc `null`; giới hạn H12 theo phút |
| `soft_weights` | object, key chỉ được `S1`…`S9`, value integer không âm |

### `RoundTransitionPayload`

```json
{ "target_status": "OPEN_REGISTRATION", "reason": "Open lecturer registration" }
```

`target_status` 1–32; `reason` optional, tối đa 1000. Transition hợp lệ phụ thuộc state machine của round.

### `RoundResources`

```json
{ "group_ids": [1, 2], "timeslot_ids": [10, 11], "room_ids": [3] }
```

Ba mảng đều bắt buộc và phải có ít nhất một ID.

### `RoundDayCreate`

```json
{
  "day_date": "2026-08-25",
  "slots": [
    { "start_at": "2026-08-25T08:00:00+07:00", "end_at": "2026-08-25T08:45:00+07:00" },
    { "start_at": "2026-08-25T09:00:00+07:00", "end_at": "2026-08-25T09:45:00+07:00" }
  ]
}
```

`day_date` là date; `slots` ít nhất một phần tử; mỗi slot có `start_at`, `end_at` datetime.

### `AvailabilitySubmit`

```json
{ "selected_timeslot_ids": [10, 11], "load_preference": "MEDIUM" }
```

`selected_timeslot_ids` mặc định `[]`; `load_preference`: `LOW | MEDIUM | HIGH` (default `MEDIUM`).

### Invitation schemas

```json
{ "lecturer_ids": [12, 13] }
```

`InvitationCreate.lecturer_ids` là mảng ít nhất một ID.

```json
{ "response": "ACCEPTED", "reason": "Available for this round" }
```

`response`: `ACCEPTED | DECLINED`; `reason` optional.

## Scheduling

### `ScheduleRunPayload`

```json
{ "random_seed": 42, "time_limit_seconds": 30 }
```

`random_seed` integer default `0`; `time_limit_seconds` > 0 và ≤ 300, default `10`.

### `SessionEditPayload`

```json
{
  "timeslot_id": 10,
  "room_id": 3,
  "reviewer_ids": [12, 13],
  "result_owner_id": 12,
  "reason": "Resolve room maintenance conflict"
}
```

Tất cả field trừ `reason` là optional; `timeslot_id`, `room_id`, `result_owner_id` nếu có phải > 0; `reviewer_ids` là mảng integer; `reason` 1–1000 và luôn bắt buộc.

### Reschedule schemas

```json
{ "reason": "Reviewer unavailable on scheduled date" }
```

`RescheduleRequestPayload.reason`: 1–1000.

```json
{ "decision": "APPROVED", "note": "Moved to next available slot" }
```

`decision`: `APPROVED | REJECTED`; `note`: 1–1000.

### `RoundOperationPayload`

```json
{ "action": "POSTPONED", "reason": "Campus closure" }
```

`action`: `POSTPONED | CANCELLED`; `reason`: 1–1000.

### `H11WaiverPayload` và `ResultOwnerPayload`

```json
{ "reason": "Approved by manager under exceptional capacity constraint" }
```

H11 waiver reason: 1–1000.

```json
{ "lecturer_id": 12 }
```

Result owner lecturer ID: integer > 0; lecturer phải nằm trong Reviewer của session.

## Results và remediation

### `ResultPayload`

```json
{
  "outcome": "PASSED",
  "note": "Meets defense requirements",
  "remediation_due_at": null,
  "verifier_lecturer_id": null,
  "correction_reason": null
}
```

| Field | Rule |
|---|---|
| `outcome` | string 1–32; giá trị hợp lệ còn phụ thuộc loại round/business workflow |
| `note` | optional, tối đa 2000 |
| `remediation_due_at` | optional datetime/null |
| `verifier_lecturer_id` | optional integer > 0 |
| `correction_reason` | optional, tối đa 1000; cần dùng khi sửa result đã tồn tại |

### `RemediationDecisionPayload`

```json
{ "outcome": "PASSED", "note": "Correction verified" }
```

`outcome`: `PASSED | FAILED`; `note` optional, tối đa 2000.

### `OverdueFailPayload`

```json
{ "reason": "Due date passed without remediation submission" }
```

`reason`: 1–1000.

## Response shapes dùng chung

### Round registration

```json
{
  "invited": 8,
  "responded": 6,
  "lecturer_availability": 5,
  "group_availability": 12
}
```

### Schedule run

```json
{
  "version_id": 21,
  "status": "VALID",
  "scheduled_count": 12,
  "unscheduled": [],
  "soft_scores": { "S1": 4, "S2": 2 }
}
```

`unscheduled` là danh sách object reason do solver/snapshot tạo ra; FE nên render nguyên nhân thay vì chỉ hiện số lượng.

### Schedule version

List item thường có: `id`, `round_id`, `version_no`, `status`, `solver_status`, `total_score`, `soft_scores`, `random_seed`, `created_at`, `activated_at`. Status lifecycle là `DRAFT → ACTIVE → PUBLISHED`; các version bị thay thế chuyển thành `DISCARDED`.

Detail có `assignments` và `sessions`. Một generated `DRAFT` chỉ có durable `assignments`/reviewer snapshots và `sessions: []`; assignment có `assignment_id`, `group_id`, `project_id` (provenance snapshot), `timeslot_id`, `start_at`, `end_at`, `room_id: null`, `reviewer_ids`, `result_owner_ids`, `reviewer_names`. Activation materializes đúng một Session cho mỗi assignment với `status: "PLANNED"`, sau đó publish chuyển Session sang `SCHEDULED`. Session đã materialize có thêm `id` và `assignment_id`; downstream reads dùng `assignment_id.project_id` snapshot thay vì mutable `groups.project_id`.

### Personal schedule

```json
{
  "version": { "version_id": 21, "round_id": 4, "status": "PUBLISHED" },
  "generated_at": "2026-08-18T10:00:00Z",
  "sessions": [
    {
      "id": 100,
      "group_id": 1,
      "group_code": "G001",
      "project_id": 7,
      "start_at": "2026-08-25T08:00:00+07:00",
      "end_at": "2026-08-25T08:45:00+07:00",
      "room_id": 3,
      "room_code": "A101",
      "status": "SCHEDULED"
    }
  ]
}
```

Nếu chưa có version nhìn thấy, `version` là `null` hoặc `sessions` là `[]`.
