# Scheduler, lịch và vận hành thay đổi

Tất cả route trong file này có prefix `/api/v1`.

## 1. Xem schedule versions

### `GET /rounds/{round_id}/schedule/versions`

- **Role:** tất cả role.
- **Path:** `round_id` integer.
- **Response `200`:** array với các field `id`, `round_id`, `version_no`, `status`, `solver_status`, `total_score`, `soft_scores`, `random_seed`, `created_at`, `activated_at`.
- ADMIN/MANAGER thấy mọi version trong round. LECTURER/STUDENT chỉ thấy version có session đã materialize thuộc scope của mình; bản `DRAFT` chỉ dành cho ADMIN/MANAGER vì chưa có Session.

Ví dụ item: `{ "id": 21, "round_id": 4, "version_no": 1, "status": "DRAFT", "solver_status": "OPTIMAL", "total_score": 123.4, "soft_scores": { "S1": 4 }, "random_seed": 42, "created_at": "...", "activated_at": null }`.

### `GET /schedule/versions/{version_id}`

- **Role:** tất cả role.
- **Response `200`:** schedule version DB fields cộng `sessions` và `assignments`.
- Với `DRAFT`, `sessions` luôn rỗng; FE đọc các durable solver assignments trong `assignments`. Mỗi assignment gồm `assignment_id`, `group_id`, `group_code`, `project_id` (provenance snapshot), `timeslot_id`, `start_at`, `end_at`, `room_id: null`, `status: "PLANNED"`, `reviewer_ids`, `result_owner_ids`, `reviewer_names`.
- Sau activation, mỗi assignment có đúng một Session materialized; Session row gồm `id`, `assignment_id`, `group_id`, `group_code`, `project_id` (lấy từ assignment snapshot), `timeslot_id`, `room_id`, `start_at`, `end_at`, `status`, `reviewer_ids`, `result_owner_ids`, `reviewer_names`.
- `room_id` có thể là `null` trong version vừa được solver tạo; phòng được gán ở bước Room Assignment trước khi publish.
- Ví dụ session: `{ "id": 100, "group_id": 1, "group_code": "G001", "project_id": 7, "timeslot_id": 10, "room_id": null, "start_at": "...", "end_at": "...", "status": "PLANNED", "reviewer_ids": [12, 13], "result_owner_ids": [12], "reviewer_names": { "12": "Lecturer A" } }`.
- **`404 VERSION_NOT_FOUND`** nếu version không tồn tại.
- LECTURER/STUDENT không có session thuộc scope sẽ nhận `403`.

## 2. Chạy scheduler

### `POST /rounds/{round_id}/schedule/run`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`ScheduleRunPayload`](schemas.md#schedulerunpayload).
- **Success `201`:** object gồm `version_id`, `status`, `scheduled_count`, `unscheduled`, `soft_scores`.
- Ví dụ: `{ "version_id": 21, "status": "OPTIMAL", "scheduled_count": 12, "unscheduled": [], "soft_scores": { "S1": 4, "S2": 2 } }`.
- `status` trong response là solver status thực tế; `unscheduled` là array object chứa lý do group không được xếp. Solver chỉ nhận group, timeslot và reviewer availability, không nhận room và không tối ưu việc chọn room. Một run tạo `ScheduleVersion` mới ở trạng thái `DRAFT`, durable assignments và reviewer snapshots; round vẫn ở `SCHEDULING` cho tới khi một version được activate.
- Generate không tạo `sessions`/`session_reviewers`; `room_id` chỉ được để `null` trên assignment snapshot. Việc này giúp draft có thể sửa/xóa độc lập với operational sessions.
- **`422 ROUND_INPUTS_INCOMPLETE`:** thiếu group/timeslot hoặc Reviewer availability. Không có room inventory vẫn có thể generate schedule.
- **`422 SCHEDULE_RERUN_FORBIDDEN`:** round đã publish/ongoing/terminal; dùng controlled-change.
- **`422 ROUND_POSTPONED`:** phải reopen round postponed trước.
- **`409 SCHEDULE_PERSIST_FAILED`:** solver có kết quả nhưng không persist được.

### Khi nào FE gọi run

FE nên gọi sau khi resource/availability đầy đủ và round đã ở trạng thái phù hợp. Không cho user double-click tạo nhiều request; disable button khi request đang chạy và reload versions sau khi nhận response.

## 3. Activate và publish

### `POST /schedule/versions/{version_id}/activate`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** none.
- Chỉ version `DRAFT` được activate; version `DRAFT`/`ACTIVE` khác cùng round bị `DISCARDED`.
- Backend khóa round/version, kiểm tra project provenance của từng group, khóa Reviewer resources và chạy lại toàn bộ hard-constraint validation trước khi materialize.
- Activation materializes đúng một Session `PLANNED` (room `null`) và reviewer snapshot cho mỗi assignment, rồi chuyển round `SCHEDULING` → `SCHEDULED`.
- **Success `200`:** `{ "version_id": 21, "status": "ACTIVE" }`.
- **`404 VERSION_NOT_FOUND`** hoặc **`422 VERSION_NOT_VALID`**.

### `POST /rounds/{round_id}/schedule/publish/{version_id}`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** none.
- Version phải thuộc round, đang ở `ACTIVE` và pass hard-constraint validation. Khi publish, các Session `PLANNED` của version chuyển thành `SCHEDULED` trong cùng transaction.
- Version published cũ bị `DISCARDED`; round chuyển `PUBLISHED`.
- **Success `200`:** `{ "round_id": 4, "version_id": 21, "status": "PUBLISHED", "recipient_count": 35 }`.
- **`422 VERSION_NOT_ACTIVE`:** chưa activate version.
- **`422`:** version không publishable hoặc schedule vi phạm hard constraint.
- Publish tạo notification/outbox cho người bị ảnh hưởng.

## 4. Room Assignment

Room assignment happens after activation. Round configuration stores allowed `room_types`
(`NORMAL`, `SEMINAR`, `LAB`); it no longer persists a physical room whitelist. All four routes
require `ADMIN` or `MANAGER` and operate on the current `ACTIVE` version:

- `GET /rounds/{round_id}/rooms/available?timeslot_id=&room_type=` lists active, allowed rooms
  that are not occupied in any live schedule for the requested interval.
- `PUT /sessions/{session_id}/room` assigns an active allowed room to a `PLANNED` session.
- `POST /rounds/{round_id}/rooms/suggest` returns deterministic least-used room suggestions.
- `POST /rounds/{round_id}/rooms/apply-suggestions` validates the complete batch under room
  advisory locks, applies it atomically, and reports `changed_count`/`unchanged_count`.

Room conflicts are global across all `ACTIVE`/`PUBLISHED` versions. Repeating an identical
assignment is an idempotent no-op. Publish refuses missing, inactive, disallowed, or globally
conflicting rooms.

## 5. Immutable Councils

Migration `0025_immutable_councils` replaces materialized `session_reviewers` rows with immutable
`councils`/`council_members` snapshots. Every materialized Session exposes a non-null `council_id`;
activation creates and seals one Council per Session. Sealed Council metadata and members cannot be
inserted, updated, or deleted directly. A reviewer or Result Owner change creates a new sealed Council
and repoints only the affected Session.

## 6. H11 waiver và Result Owner

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
- Backend không sửa member của Council hiện tại; nó tạo và seal một Council thay thế rồi repoint
  Session. Reviewer cũ và mới đều nằm trong tập recipient của notification/outbox.
- Đây là assignment cho Defense session; Review không dùng Result Owner flow này.

## 7. Sửa schedule

### `POST /schedule/versions/{version_id}/sessions/{session_id}/edit`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `SessionEditPayload`.
- Chỉ sửa version `DRAFT` theo draft-edit workflow. Ở draft, `{session_id}` trên path là `assignment_id` để giữ tương thích route cũ; response trả cả `session_id` (alias) và `assignment_id`.
- Field nào không gửi sẽ giữ giá trị cũ; `reason` luôn bắt buộc.
- Backend chạy lại hard-constraint validation, kiểm tra reviewer và Result Owner.
- **Success `200`:** `{ "session_id": 100, "assignment_id": 100, "version_id": 21, "status": "UPDATED" }`.
- **`422 HARD_CONSTRAINT_VIOLATION`:** response detail có `violations` array.
- **`409 DRAFT_EDIT_CONCURRENT_UPDATE`:** version/session đã đổi trong lúc request xử lý; reload rồi thử lại.

### `POST /schedule/versions/{version_id}/sessions/{session_id}/controlled-change`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `SessionEditPayload`.
- Chỉ dùng cho version `PUBLISHED`.
- Có ba nhánh, tất cả đều yêu cầu `reason`, hard-constraint validation và ghi audit/change record:
  - chỉ đổi Reviewer/Result Owner: tạo một Council thay thế, repoint đúng Session mục tiêu, giữ nguyên
    version hiện tại;
  - chỉ đổi time/room: tạo version thay thế `PUBLISHED`, clone các Session thành `SCHEDULED`, tái sử
    dụng Council ID của sibling, rồi đánh dấu version nguồn `DISCARDED`;
  - đổi Reviewer/Result Owner cùng time/room: giống clone branch nhưng chỉ tạo một Council mới cho
    Session mục tiêu; sibling clone vẫn tái sử dụng Council ID cũ.
- Clone branch copy cả result/remediation liên quan và không expose version trung gian `DRAFT`/`ACTIVE`.
- **Success `200` reviewer-only:** `{ "change_kind": "COUNCIL_REPLACED", "schedule_version_id": 21, "replacement_version_id": null, "session_id": 100, "status": "PUBLISHED", "before_council_id": 12, "after_council_id": 14 }`.
- **Success `200` time/room:** `change_kind` là `VERSION_REPLACED`; **mixed:** `MIXED_REPLACEMENT`.
  Hai nhánh clone trả `replacement_version_id` là ID version mới; `session_id` luôn là Session nguồn
  được yêu cầu thay đổi. Các alias `version_id`/`source_version_id` còn được trả để tương thích client cũ.
- FE hiển thị version replacement đã publish khi `replacement_version_id` khác `null`.
- **`422 CONTROLLED_CHANGE_REQUIRES_PUBLISHED`**.
- **`422 COMPLETED_SESSION_IMMUTABLE`**.
- **`422 HARD_CONSTRAINT_VIOLATION`**.
- **`409 CONTROLLED_CHANGE_CONCURRENT_UPDATE`**.

### `GET /sessions/{session_id}/replacement-suggestions`

- **Role:** `ADMIN`, `MANAGER`.
- **Response `200`:** tối đa 50 suggestion, mỗi item gồm `timeslot_id`, `room_id`, `reviewer_ids`, `replaces`. Solver không đề xuất room nên `room_id` là `null` ở bước này.
- Ví dụ: `{ "timeslot_id": 11, "room_id": null, "reviewer_ids": [13, 14], "replaces": [12] }`.
- Suggestions đã được filter qua schedule validator; FE có thể dùng để prefill controlled-change payload nhưng vẫn phải gửi `reason` và backend sẽ validate lại.

## 8. Hoãn, reschedule và round operation

### `POST /sessions/{session_id}/postpone`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RescheduleRequestPayload` (`reason` bắt buộc).
- Chỉ Session đang `SCHEDULED` mới postpone được.
- **Success `200`:** `{ "id": 100, "status": "POSTPONED" }`.
- Tạo notification cho các recipient bị ảnh hưởng.

### `POST /sessions/{session_id}/group-absent`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RescheduleRequestPayload` (`reason` bắt buộc, không được rỗng).
- Chỉ Session `SCHEDULED` thuộc version `PUBLISHED` mới chuyển được sang `GROUP_ABSENT`.
- **Success `200`:** `{ "id": 100, "status": "GROUP_ABSENT" }`.
- Ghi audit event và tạo notification/outbox cho các recipient bị ảnh hưởng trong cùng transaction.
- **`401`:** chưa xác thực; **`403`:** Lecturer/Student hoặc Session ngoài phạm vi version published; **`422`:** reason rỗng, Session đã ở trạng thái khác, hoặc request lặp.

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

## 9. Status và UI guidance

FE nên lấy status từ response, không tự suy diễn. Các status thường gặp:

- Schedule version: `DRAFT`, `ACTIVE`, `PUBLISHED`, `DISCARDED`.
- Session: `PLANNED`, `SCHEDULED`, `COMPLETED`, `POSTPONED`, `GROUP_ABSENT`, `CANCELLED`.
- Round: `DRAFT`, `REGISTRATION`, `SCHEDULING`, `SCHEDULED`, `PUBLISHED`, `ONGOING`, `COMPLETED`, `LOCKED`, `POSTPONED`, `CANCELLED`.

Mỗi thao tác làm thay đổi schedule nên invalidate các query: round detail, versions, version detail, dashboard, personal schedule, notifications.

### Room và H3 trong giai đoạn draft

Solver chỉ xếp `Time + Council`. Hai session chồng giờ nhưng đều chưa có `room_id` không vi phạm H3; H3 chỉ được kiểm tra khi cả hai session đã được gán cùng một room cụ thể. Việc gán room và kiểm tra xung đột room thuộc Room Assignment workflow.
