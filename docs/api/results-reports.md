# Results, remediation, dashboard, reports và notifications

Tất cả route trong file này có prefix `/api/v1`.

## 1. Kết quả của session

### `GET /sessions/{session_id}/result`

- **Role:** tất cả role đã đăng nhập.
- **Scope:** chỉ đọc được session trong scope actor.
- **Response `200`:** `{ "session_id": 100, "round_type": "DEFENSE_1_1", "group_status": "D11_PASSED", "result": null }`.
- Khi có result, `result` chứa các field lưu trong `session_results`, gồm thường dùng: `id`, `session_id`, `outcome`, `note`, `entered_by`, `entered_at`, `correction_reason`, `remediation_due_at`, `verifier_lecturer_id`, `verify_status`, `before_group_status`, `after_group_status`.
- **`403`:** result nằm ngoài actor scope.
- FE nên dùng `group_status` và `result` từ server để hiển thị state, không tự map outcome nếu chưa có trong response.

### `POST /sessions/{session_id}/result`

- **Role:** `MANAGER`, `LECTURER`.
- **Scope:** Manager có thể nhập/sửa; Lecturer phải là Reviewer được assign. Nếu round bật Result Owner cho D1.1/D2, chỉ Result Owner mới được nhập.
- **Body:** [`ResultPayload`](schemas.md#resultpayload).
- **Success `201`:** `{ "id": 501, "session_id": 100, "outcome": "PASSED", "group_status": "D11_PASSED" }`.
- Result đã tồn tại chỉ Manager được sửa và phải gửi `correction_reason`.
- Result của session đã có remediation completed không được sửa.

### Luật outcome theo workflow hiện tại

- `DEFENSE_1_1` outcome hợp lệ theo domain validator. Khi outcome là `LEVEL_2`, bắt buộc có `remediation_due_at` và `verifier_lecturer_id`; verifier phải là Reviewer hợp lệ.
- Chỉ D1.1 `LEVEL_2` tạo/cập nhật remediation case.
- `DEFENSE_1_2` và `DEFENSE_2` không được gửi remediation fields.
- D1.2 outcome `COMPLETED` sẽ đánh dấu session `COMPLETED`.
- Backend thực hiện group state transition sau khi validate outcome; FE chỉ render `group_status` trả về.

Lỗi quan trọng:

- `403`: không phải assigned Reviewer/Result Owner.
- `422 RESULT_OWNER_REQUIRED`: chưa assign đúng một Result Owner trước khi nhập.
- `422 REMEDIATION_FIELDS_REQUIRED`: D1.1 Level 2 thiếu due date/verifier.
- `422 REMEDIATION_NOT_ALLOWED`: gửi remediation fields cho round không phải D1.1.
- `422 RESULT_CORRECTION_FORBIDDEN`: Lecturer cố sửa result cũ.
- `422 RESULT_AFTER_REMEDIATION`: remediation đã completed.
- `422 RESULT_CONCURRENT_UPDATE`: session/result vừa bị actor khác thay đổi; reload rồi thử lại.

## 2. Remediation

### `GET /remediation`

- **Role:** tất cả role.
- **Scope:** Admin/Manager thấy tất cả; Lecturer chỉ thấy case mà mình là assigned verifier; Student chỉ thấy case thuộc active group của mình.
- **Response `200`:** array item gồm `id`, `group_id`, `group_code`, `status`, `due_at`, `verifier_lecturer_id`, `note`, `round_type`.
- Ví dụ item: `{ "id": 31, "group_id": 1, "group_code": "G001", "status": "OPEN", "due_at": "...", "verifier_lecturer_id": 12, "note": null, "round_type": "DEFENSE_1_1" }`.

### `POST /remediation/{case_id}/decision`

- **Role:** `LECTURER`.
- **Scope:** chỉ assigned Remediation Verifier của case.
- **Body:** `{ "outcome": "PASSED", "note": "..." }`; outcome là `PASSED|FAILED`.
- Case phải ở `OPEN` hoặc `OVERDUE`.
- **Success `200`:** `{ "id": 31, "status": "PASSED" }`.
- **`403 REMEDIATION_VERIFIER_REQUIRED`:** Lecturer không phải verifier.
- **`409 REMEDIATION_ALREADY_DECIDED`:** case đã có quyết định.
- Quyết định đồng thời cập nhật group state và verify status của session result.

### `POST /remediation/{case_id}/overdue-fail`

- **Role:** `MANAGER`.
- **Body:** `{ "reason": "Due date passed..." }`.
- Chỉ fail case `OPEN`/`OVERDUE` sau khi đã quá `due_at`.
- **Success `200`:** `{ "id": 31, "status": "FAILED" }`.
- **`422 REMEDIATION_NOT_OVERDUE`:** chưa qua due date.
- **`409 REMEDIATION_ALREADY_DECIDED`:** case đã xử lý.

## 3. Dashboard và reports cho Manager

### `GET /dashboard?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`.
- `round_id` optional; bỏ trống để lấy aggregate/default selected version.
- **Response `200`:** object gồm `availability`, `groups`, `pending_reschedule_requests`, `changes`, `version`, `lecturer_load`, `attention_groups`.
- `availability`: `{ invited, responded }`; `groups`: `{ total, scheduled, unscheduled }`.
- `lecturer_load` item gồm `id`, `lecturer_code`, `display_name`, `session_count`.
- `attention_groups` item gồm `id`, `code`, `status` và chỉ chứa group cần chú ý như `D12_CONDITIONAL`, `FAILED`, `DROPPED`.

### `GET /reports/lecturer-load?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`.
- `round_id` optional.
- **Response:** `{ round_id, version, rows }`.
- Row gồm `lecturer_id`, `lecturer_code`, `display_name`, `session_count`, `quota`, `quota_percent`.

### `GET /reports/unscheduled?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`.
- **Query bắt buộc:** `round_id`.
- **Response:** `{ round_id, generated_at, versions }`.
- Mỗi version item gồm `version_id`, `version_no`, `status`, `created_at`, `unscheduled`, `provenance`.
- FE dùng route này để render group chưa được xếp và nguyên nhân từ scheduler snapshot.

### `GET /reports/provenance/{version_id}`

- **Role:** tất cả role.
- **Scope:** non-management phải có session visible trong version.
- **Response:** `{ version_id, version_no, status, created_at, round_id, type, semester_code, generated_at }`.
- **`404 VERSION_NOT_FOUND`** hoặc `403` ngoài scope.

### `GET /reports/quality`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `{ version, rows }`.
- Row gồm `id`, `code`, `active_members`, `leaders`; rows là các group dưới minimum active members hoặc không có đúng một leader.

### `GET /reports/remediation?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`.
- `round_id` optional.
- **Response:** `{ round_id, version, rows }`.
- Row gồm `id`, `group_id`, `group_code`, `due_at`, `status`, `verifier_lecturer_id`.

### `GET /reports/outcomes?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`.
- `round_id` optional.
- **Response:** `{ round_id, version, rows }`; mỗi row gồm `type`, `outcome`, `count`.

## 4. Notifications

### `GET /notifications?limit=50`

- **Role:** tất cả role.
- `limit` optional, mặc định 50, clamp 1–100.
- Admin/Manager có scope management; Lecturer/Student chỉ nhận notification có recipient account của mình.
- **Response `200`:** array `{ id, event_type, payload, status, sent_at, created_at }`.
- `payload` là JSON object tùy event, không nên parse theo một schema duy nhất; FE nên switch theo `event_type`.

Các event thường gặp: `REVIEW_INVITATION`, `SCHEDULE_PUBLISHED`, `SCHEDULE_CHANGED`, `SESSION_POSTPONED`, `RESCHEDULE_REQUESTED`, `RESCHEDULE_DECISION`, `RESULT_RECORDED`, `REMEDIATION_CREATED`, `REMEDIATION_DECIDED`, `ROUND_OPERATION`.

### `POST /notifications/{notification_id}/retry`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** none.
- Chỉ retry notification đang `FAILED`.
- **Success `200`:** `{ id, status: "PENDING", dedupe_key }`.
- **`404 NOTIFICATION_NOT_RETRYABLE`:** notification không tồn tại hoặc không ở failed state.

## 5. Calendar export

### `GET /schedule/versions/{version_id}/calendar.ics`

- **Role:** tất cả role.
- **Scope:** Admin/Manager nhận toàn bộ version; Lecturer/Student chỉ nhận session visible.
- **Success `200`:** body text ICS, header `Content-Type: text/calendar; charset=utf-8`.
- Header download: `Content-Disposition: attachment; filename="schedule-{version_id}.ics"`.
- **`404 VERSION_NOT_FOUND`** nếu version không tồn tại; **`403`** nếu ngoài scope.

FE nên dùng `response.blob()`: `const blob = await response.blob(); const url = URL.createObjectURL(blob); window.location.assign(url);`.

## 6. Personal schedule

### `GET /my/schedule?version_id=&from_at=&to_at=`

- **Role:** tất cả role.
- Query optional:
  - `version_id`: lấy đúng version.
  - `from_at`, `to_at`: ISO datetime range; session overlap range mới được trả.
- Nếu không truyền `version_id`, backend chọn version published/valid phù hợp.
- **Response `200`:** `{ version, generated_at, sessions }`.
- Session item gồm `id`, `group_id`, `group_code`, `project_id`, `start_at`, `end_at`, `room_id`, `room_code`, `status`.
- Nếu chưa có version hoặc không có session visible: `version: null` hoặc `sessions: []`.

## 7. Cache invalidation phía FE

Sau khi ghi result, remediation decision, publish, controlled-change, postpone, reschedule decision hoặc round operation, nên invalidate:

- session detail/result;
- group/round detail nếu FE có cache;
- schedule version list/detail;
- `my/schedule`;
- dashboard/reports liên quan;
- notifications.
