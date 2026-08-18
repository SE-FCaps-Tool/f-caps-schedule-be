# Scheduler, lịch và vận hành thay đổi

Tất cả route trong file này có prefix `/api/v1`.

## 1. Xem schedule versions

### `GET /rounds/{round_id}/schedule/versions`

- **Role:** tất cả role.
- **Path:** `round_id` integer.
- **Response `200`:** array với các field `id`, `round_id`, `version_no`, `status`, `solver_status`, `total_score`, `soft_scores`, `random_seed`, `created_at`, `activated_at`.
- ADMIN/MANAGER thấy mọi version trong round. LECTURER/STUDENT chỉ thấy version có session thuộc scope của mình.

Ví dụ item: `{ "id": 21, "round_id": 4, "version_no": 1, "status": "VALID", "solver_status": "OPTIMAL", "total_score": 123.4, "soft_scores": { "S1": 4 }, "random_seed": 42, "created_at": "...", "activated_at": "..." }`.

### `GET /schedule/versions/{version_id}`

- **Role:** tất cả role.
- **Response `200`:** schedule version DB fields cộng `sessions`.
- Session row gồm `id`, `group_id`, `group_code`, `project_id`, `timeslot_id`, `room_id`, `start_at`, `end_at`, `status`, `reviewer_ids`, `result_owner_ids`, `reviewer_names`.
- Ví dụ session: `{ "id": 100, "group_id": 1, "group_code": "G001", "project_id": 7, "timeslot_id": 10, "room_id": 3, "start_at": "...", "end_at": "...", "status": "SCHEDULED", "reviewer_ids": [12, 13], "result_owner_ids": [12], "reviewer_names": { "12": "Lecturer A" } }`.
- **`404 VERSION_NOT_FOUND`** nếu version không tồn tại.
- LECTURER/STUDENT không có session thuộc scope sẽ nhận `403`.

## 2. Chạy scheduler

### `POST /rounds/{round_id}/schedule/run`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`ScheduleRunPayload`](schemas.md#schedulerunpayload).
- **Success `201`:** object gồm `version_id`, `status`, `scheduled_count`, `unscheduled`, `soft_scores`.
- Ví dụ: `{ "version_id": 21, "status": "OPTIMAL", "scheduled_count": 12, "unscheduled": [], "soft_scores": { "S1": 4, "S2": 2 } }`.
- `status` là solver status thực tế; `unscheduled` là array object chứa lý do group không được xếp. Một run tạo `ScheduleVersion` mới và chuyển round qua `SCHEDULED` nếu persist thành công.
- **`422 ROUND_INPUTS_INCOMPLETE`:** thiếu group/timeslot/room/Reviewer availability.
- **`422 SCHEDULE_RERUN_FORBIDDEN`:** round đã publish/ongoing/terminal; dùng controlled-change.
- **`422 ROUND_POSTPONED`:** phải reopen round postponed trước.
- **`409 SCHEDULE_PERSIST_FAILED`:** solver có kết quả nhưng không persist được.

### Khi nào FE gọi run

FE nên gọi sau khi resource/availability đầy đủ và round đã ở trạng thái phù hợp. Không cho user double-click tạo nhiều request; disable button khi request đang chạy và reload versions sau khi nhận response.

## 3. Activate và publish

### `POST /schedule/versions/{version_id}/activate`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** none.
- Chỉ version `VALID` được activate; các version `VALID` khác cùng round bị supersede.
- **Success `200`:** `{ "version_id": 21, "status": "VALID" }`.
- **`404 VERSION_NOT_FOUND`** hoặc **`422 VERSION_NOT_VALID`**.

### `POST /rounds/{round_id}/schedule/publish/{version_id}`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** none.
- Version phải thuộc round, đã activate và pass hard-constraint validation.
- Version published cũ bị `SUPERSEDED`; round chuyển `PUBLISHED`.
- **Success `200`:** `{ "round_id": 4, "version_id": 21, "status": "PUBLISHED", "recipient_count": 35 }`.
- **`422 VERSION_NOT_ACTIVE`:** chưa activate version.
- **`422`:** version không publishable hoặc schedule vi phạm hard constraint.
- Publish tạo notification/outbox cho người bị ảnh hưởng.

## 4. H11 waiver và Result Owner

### `POST /rounds/{round_id}/groups/{group_id}/h11-waiver`

- **Role:** `MANAGER`.
- **Body:** `{ "reason": "..." }`.
- **Success `200`:** `{ id, round_id, group_id, active: true }`.
- Group phải được attach vào round.
- Gọi lại sẽ upsert waiver và activate lại waiver.

### `DELETE /rounds/{round_id}/groups/{group_id}/h11-waiver`

- **Role:** `MANAGER`.
- **Body:** none.
- **Success `200`:** `{ id, round_id, group_id, active: false }`.
- **`404`:** waiver/group không tồn tại trong round.

### `POST /schedule/versions/{version_id}/sessions/{session_id}/result-owner`

- **Role:** `MANAGER`.
- **Body:** `{ "lecturer_id": 12 }`.
- **Success `200`:** `{ version_id, session_id, result_owner_id }`.
- Chỉ dùng khi round bật `result_owner_mode` và type là `DEFENSE_1_1` hoặc `DEFENSE_2`.
- Lecturer được chọn phải là một Reviewer của session.
- Session đã `COMPLETED` immutable.
- Đây là assignment cho Defense session; Review không dùng Result Owner flow này.

## 5. Sửa schedule

### `POST /schedule/versions/{version_id}/sessions/{session_id}/edit`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `SessionEditPayload`.
- Chỉ sửa version `VALID` hiện tại theo draft-edit workflow.
- Field nào không gửi sẽ giữ giá trị cũ; `reason` luôn bắt buộc.
- Backend chạy lại hard-constraint validation, kiểm tra reviewer và Result Owner.
- **Success `200`:** `{ "session_id": 100, "version_id": 21, "status": "UPDATED" }`.
- **`422 HARD_CONSTRAINT_VIOLATION`:** response detail có `violations` array.
- **`409 DRAFT_EDIT_CONCURRENT_UPDATE`:** version/session đã đổi trong lúc request xử lý; reload rồi thử lại.

### `POST /schedule/versions/{version_id}/sessions/{session_id}/controlled-change`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `SessionEditPayload`.
- Chỉ dùng cho version `PUBLISHED`.
- Không mutate version published; tạo version mới `VALID`, copy các session/result liên quan và ghi change record.
- **Success `200`:** `{ "version_id": 22, "source_version_id": 21, "session_id": 101, "status": "VALID" }`.
- FE phải hiển thị version mới và yêu cầu manager activate/publish theo quy trình nếu cần công bố thay đổi.
- **`422 CONTROLLED_CHANGE_REQUIRES_PUBLISHED`**.
- **`422 COMPLETED_SESSION_IMMUTABLE`**.
- **`422 HARD_CONSTRAINT_VIOLATION`**.
- **`409 CONTROLLED_CHANGE_CONCURRENT_UPDATE`**.

### `GET /sessions/{session_id}/replacement-suggestions`

- **Role:** `ADMIN`, `MANAGER`.
- **Response `200`:** tối đa 50 suggestion, mỗi item gồm `timeslot_id`, `room_id`, `reviewer_ids`, `replaces`.
- Ví dụ: `{ "timeslot_id": 11, "room_id": 4, "reviewer_ids": [13, 14], "replaces": [12] }`.
- Suggestions đã được filter qua schedule validator; FE có thể dùng để prefill `SessionEditPayload` nhưng vẫn phải gửi `reason` và backend sẽ validate lại.

## 6. Hoãn, reschedule và round operation

### `POST /sessions/{session_id}/postpone`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RescheduleRequestPayload` (`reason` bắt buộc).
- Session đang `SCHEDULED` hoặc `ONGOING` mới postpone được.
- **Success `200`:** `{ "id": 100, "status": "POSTPONED" }`.
- Tạo notification cho các recipient bị ảnh hưởng.

### `POST /sessions/{session_id}/reschedule-requests`

- **Role:** `MANAGER`, `LECTURER`, `STUDENT`.
- **Scope:** manager có thể request mọi session; lecturer phải được assign; student phải là active group leader của group.
- **Body:** `{ "reason": "..." }`.
- **Success `201`:** `{ "id": 55, "status": "REQUESTED" }`.
- Gửi notification cho Manager.

### `POST /reschedule-requests/{request_id}/decision`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ "decision": "APPROVED", "note": "..." }`.
- **Success `200`:** `{ "id": 55, "status": "APPROVED", "decision_note": "..." }`.
- Chỉ request đang `REQUESTED` mới decision được.
- **`404 RESCHEDULE_REQUEST_NOT_FOUND`:** request không tồn tại hoặc đã xử lý.

Decision chỉ cập nhật trạng thái request; việc sắp lịch lại thực tế vẫn dùng edit/controlled-change workflow.

### `POST /rounds/{round_id}/operation`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ "action": "POSTPONED", "reason": "..." }`.
- `action`: `POSTPONED` hoặc `CANCELLED`.
- **Success `200`:** `{ "round_id": 4, "status": "POSTPONED" }` hoặc `CANCELLED`.
- State transition được backend kiểm tra; mọi operation ghi audit/change record và notification.

## 7. Status và UI guidance

FE nên lấy status từ response, không tự suy diễn. Các status thường gặp:

- Schedule version: `VALID`, `PUBLISHED`, `SUPERSEDED`.
- Session: `SCHEDULED`, `ONGOING`, `COMPLETED`, `POSTPONED`.
- Round: `DRAFT`, `REGISTRATION`, `SCHEDULING`, `SCHEDULED`, `PUBLISHED`, `ONGOING`, `COMPLETED`, `LOCKED`, `POSTPONED`, `CANCELLED`.

Mỗi thao tác làm thay đổi schedule nên invalidate các query: round detail, versions, version detail, dashboard, personal schedule, notifications.
