# Master data và round setup

Tất cả route trong file này đều có prefix `/api/v1`.

## Semesters

### `GET /semesters`

- **Role:** `ADMIN`, `MANAGER`.
- **Response `200`:** array `{ id, code, name, start_date, end_date, status, created_at }`.

```json
[
  { "id": 1, "code": "SP26", "name": "Spring 2026", "start_date": "2026-05-11", "end_date": "2026-08-23", "status": "UPCOMING", "created_at": "2026-08-18T02:00:00Z" }
]
```

### `POST /semesters`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`SemesterCreate`](schemas.md#semestercreate).
- **Success `201`:** object semester đầy đủ `{ id, code, name, start_date, end_date, status, created_at }`; status luôn là `UPCOMING`.
- **`409 DATA_DUPLICATE`:** code đã tồn tại.
- **`422 SEMESTER_DURATION_INVALID`:** thời lượng không nằm trong cấu hình 105–120 ngày hoặc ngày kết thúc trước ngày bắt đầu.

### `POST /semesters/{semester_id}/transition`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ "target_status": "ACTIVE|CLOSED", "reason": "..." }`.
- **Transitions:** chỉ cho phép `UPCOMING → ACTIVE → CLOSED`.
- **Success `200`:** `{ "id": 1, "status": "ACTIVE" }`.
- **`422 ACTIVE_SEMESTER_EXISTS`:** đã có semester `ACTIVE` khác.
- **`422 SEMESTER_STATUS_INVALID`:** transition không hợp lệ.
- **`404 SEMESTER_NOT_FOUND`:** semester không tồn tại.

## Accounts và audit

### `GET /accounts`

- **Role:** `ADMIN`.
- **Response `200`:** array `{ id, email, display_name, status, created_at, role }`, trong đó `role` là string.

Ví dụ field role: `"role": "STUDENT"`.

### `POST /accounts`

- **Role:** `ADMIN`.
- **Body:** [`AccountCreate`](schemas.md#accountcreate).
- **Success `201`:** `{ id, email, display_name, role, status: "ACTIVE" }`.
- **`409 ACCOUNT_DUPLICATE`:** email đã tồn tại.

### `PATCH /accounts/{account_id}/status`

- **Role:** `ADMIN`.
- **Path:** `account_id` integer.
- **Body:** `AccountStatusPayload`.
- **Success `200`:** `{ id, status }`.
- **`404 ACCOUNT_NOT_FOUND`** nếu account không tồn tại.
- Luôn ghi audit bằng `reason`.

### `POST /accounts/{account_id}/roles`

- **Role:** `ADMIN`.
- **Body:** `AccountRolePayload`.
- **Success `200`:** `{ id, role }`.
- Nếu role đã có, thao tác idempotent ở database nhưng vẫn trả object thành công.

### `DELETE /accounts/{account_id}/roles/{role}?reason=...`

- **Role:** `ADMIN`.
- **Path:** `role` là `ADMIN|MANAGER|LECTURER|STUDENT`.
- **Query bắt buộc:** `reason` không rỗng.
- **Success `200`:** `{ id, role, status: "REMOVED" }`.
- **`422 ACCOUNT_ROLE_INVALID`:** role/lý do không hợp lệ.
- **`422 ACCOUNT_ROLE_LAST`:** không được xóa role cuối cùng của account.
- **`404 ACCOUNT_ROLE_NOT_FOUND`:** account không có role đó.

### `GET /audit?actor_id=&action=&entity_type=&limit=100`

- **Role:** `ADMIN`.
- Query optional: `actor_id` integer, `action` string, `entity_type` string, `limit` mặc định 100 và bị clamp 1–500.
- **Response `200`:** array audit row:

```json
{
  "id": 99,
  "actor_id": 1,
  "action": "ROUND_TRANSITION",
  "entity_type": "round",
  "entity_id": "4",
  "reason": "Open registration",
  "before_json": { "status": "DRAFT" },
  "after_json": { "status": "REGISTRATION" },
  "occurred_at": "2026-08-18T03:00:00Z"
}
```

## Seed và lookup data

### `POST /admin/seed-fixture`

- **Role:** `ADMIN`.
- **Body:** none.
- **Success `201`:** `{ fixture, counts }`.
- Dùng cho local/test fixture; không để nút này trong production UI nếu không có yêu cầu vận hành.

### `GET /majors`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, code, name }`.

### `GET /students`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, student_code }`.

### `GET /lecturers`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, lecturer_code, account_id, email, display_name, account_status, conflicts }`.
- `conflicts` là mảng các object `{ project_id, reason }`; lecturer chưa có conflict sẽ trả về `[]`.

Ví dụ:

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
      {
        "project_id": 12,
        "reason": "Supervisor conflict"
      }
    ]
  }
]
```

### `POST /lecturers`

- **Role:** `ADMIN`.
- **Body:** `LecturerCreate`.
- **Success `201`:** `{ id, lecturer_code, account_id }`.
- **`409 DATA_DUPLICATE`:** email hoặc lecturer code trùng.

### `POST /lecturers/{lecturer_id}/conflicts`

- **Role:** `ADMIN`, `MANAGER`, `LECTURER`.
- **Scope:** Lecturer chỉ khai báo conflict cho chính mình; Admin/Manager có thể khai báo thay.
- **Body:** `ConflictCreate` gồm `project_id` và `reason`.
- **Success `200`:** `{ id, lecturer_id, project_id }`.
- Conflict phải hợp lệ theo project/lecturer và được dùng khi solver loại candidate Reviewer không phù hợp.

### `GET /rooms`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, code, name, capacity, active }`.

### `POST /rooms`

- **Role:** `ADMIN`.
- **Body:** `RoomCreate`.
- **Success `201`:** `{ id, code, name, capacity, active }`.
- **`409 DATA_DUPLICATE`:** room code trùng.

## Projects và groups

### `GET /projects`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, code, title, status, semester_id, semester_code, major_code, supervisor_count }`.

### `POST /projects`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`ProjectCreate`](schemas.md#projectcreate).
- **Success `201`:** `{ id, code, title }`.
- **`422 SUPERVISOR_NOT_FOUND`/`DATA_INVALID`:** supervisor code/type không hợp lệ.
- **`409 DATA_DUPLICATE`:** project code trùng trong semester.

### `GET /groups`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array `{ id, code, status, project_code, title, active_member_count, leader_count }`.

### `POST /groups`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`GroupCreate`](schemas.md#memberpayload-và-groupcreate).
- **Success `201`:** `{ id, code, member_count }`.
- **`422 PROJECT_NOT_FOUND`/`STUDENT_NOT_FOUND`:** reference không tồn tại.
- **`409 DATA_DUPLICATE`:** group hoặc membership trùng.

### `POST /groups/{group_id}/members/{student_id}/drop`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `DropoutPayload`.
- **Success `200`:**

```json
{ "group_id": 1, "student_id": 10, "status": "DROPPED", "warning": "GROUP_BELOW_MINIMUM_MAY_CONTINUE" }
```

Nếu group xuống dưới minimum, backend vẫn trả warning để FE hiện cảnh báo. Không tự xóa group.

### `POST /groups/{group_id}/leader`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `LeaderPayload`.
- **Success `200`:** `{ group_id, leader_student_id }`.
- Request phải kèm reason và student phải là active member phù hợp.

## Rounds

### `GET /rounds`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** array gồm `id`, `semester_id`, `type`, `status`, `reviewer_count`, `result_owner_mode`, `group_selection_mode`, `session_duration_minutes`, `registration_deadline`, `h12_sessions_per_part`, `h12_sessions_per_day`, `h12_semester_quota`, `soft_weights`.

### `POST /rounds`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** [`RoundCreate`](schemas.md#roundcreate).
- **Success `201`:** round object như `GET /rounds`, thường status ban đầu là `DRAFT`.
- **`422`:** type/configuration/semester không hợp lệ.

### `POST /rounds/{round_id}/transition`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RoundTransitionPayload`.
- **Success `200`:** `{ round_id, status }`.
- Transition tới scheduling sẽ kiểm tra có group, timeslot, room và đủ Reviewer availability.
- **`422 ROUND_INPUTS_INCOMPLETE`/`ROUND_STATUS_INVALID`:** chưa đủ input hoặc state transition không hợp lệ.

### `POST /rounds/{round_id}/unlock`

- **Role:** `ADMIN`.
- **Body:** `{ "reason": "..." }` theo `UnlockPayload`.
- Chỉ unlock round đang `LOCKED`.
- **Success `200`:** `{ round_id, status: "COMPLETED" }`.
- **`409 ROUND_NOT_LOCKED`:** round không ở trạng thái `LOCKED`.

### `POST /rounds/{round_id}/resources`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RoundResources` gồm `group_ids`, `timeslot_ids`, `room_ids`.
- **Success `200`:** `{ round_id, groups, timeslots, rooms }`; đây là số ID unique được nhận từ request.
- Group được attach idempotently; room phải active; timeslot phải thuộc round.

### `POST /rounds/{round_id}/days`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `RoundDayCreate`.
- **Success `201`:** `{ round_id, day_id, timeslot_ids }`.
- `end_at` phải sau `start_at`; duplicate day/timeslot trả `409 TIMESLOT_DUPLICATE`.

## Availability và invitation

### `POST /rounds/{round_id}/lecturers/{lecturer_id}/availability`

- **Role:** `ADMIN`, `MANAGER`, `LECTURER`.
- **Scope:** Lecturer chỉ sửa chính mình và chỉ sau khi accept invitation; Manager/Admin có thể nhập thay.
- **Body:** `AvailabilitySubmit`.
- **Success `200`:**

```json
{ "round_id": 4, "lecturer_id": 12, "selected_count": 8, "total_slots": 12, "source": "FORM" }
```

`source` là `FORM` khi lecturer nhập, `MANAGER` khi manager/admin nhập. Chọn `[]` nghĩa là không có slot available cho lecturer.

### `POST /rounds/{round_id}/groups/{group_id}/availability`

- **Role:** `ADMIN`, `MANAGER`, `STUDENT`.
- **Scope:** Student chỉ được sửa khi là active group leader.
- Chỉ dùng được khi round có `group_selection_mode=true`.
- **Body:** `AvailabilitySubmit`.
- **Success `200`:** `{ round_id, group_id, selected_count, total_slots, source }`.
- Nếu selected list rỗng, backend coi toàn bộ round slots là effective selection cho group.
- **`409 GROUP_SELECTION_DISABLED`** nếu round tắt group selection.

### `POST /rounds/{round_id}/invitations`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ "lecturer_ids": [12, 13] }`.
- **Success `200`:** `{ round_id, invited_count }`.
- Gửi invitation notification/outbox cho lecturer có account.

### `POST /rounds/{round_id}/invitations/{lecturer_id}/response`

- **Role:** `ADMIN`, `MANAGER`, `LECTURER`.
- Lecturer chỉ response invitation của chính mình.
- **Body:** `{ "response": "ACCEPTED", "reason": "..." }`.
- **Success `200`:** `{ round_id, lecturer_id, response }`.
- Deadline và state của invitation được kiểm tra bởi backend.

### `GET /rounds/{round_id}/registration`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `{ invited, responded, lecturer_availability, group_availability }`.

### `GET /rounds/{round_id}/my-availability`

- **Role:** tất cả role đã đăng nhập.
- Base response:

```json
{
  "round": { "id": 4, "type": "DEFENSE_1_1", "group_selection_mode": false, "registration_deadline": "2026-08-22T10:00:00Z" },
  "timeslots": [ { "id": 10, "start_at": "...", "end_at": "...", "day_date": "2026-08-25" } ]
}
```

- Lecturer được thêm `lecturer_id` và `selected_timeslot_ids`.
- Student được thêm `groups: [{ id, code }]` và `selected_by_group: { "1": [10, 11] }`.
- Admin/Manager được thêm `selected_by_lecturer` và `selected_by_group` dạng audit view.
- Không thuộc scope thì trả `403 AUTH_RESOURCE_SCOPE`.

### `GET /my/rounds`

- **Role:** tất cả role.
- **Response:** array `{ id, semester_id, semester_code, type, status, group_selection_mode, registration_deadline }`.
- Kết quả được scope theo role: manager/admin rộng; lecturer theo invitation accepted hoặc assignment; student theo active group membership.

### `GET /my/invitations`

- **Role:** `LECTURER`.
- **Response:** array `{ round_id, lecturer_id, status, response_reason, responded_at, type, registration_deadline, semester_code }`.
