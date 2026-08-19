# API cho Manager — tổng hợp

Tài liệu này gom toàn bộ API mà role `MANAGER` cần, tổ chức theo đúng luồng màn hình Manager
(`app/(manager)/manager/*`) thay vì theo domain như các file gốc. Nội dung request/response ở đây
lấy từ [`master-data.md`](master-data.md), [`scheduling.md`](scheduling.md), [`results-reports.md`](results-reports.md),
[`schemas.md`](schemas.md), [`role-api-matrix.md`](role-api-matrix.md) — coi các file đó là nguồn xác thực
khi có khác biệt. Phần cuối liệt kê **API còn thiếu** mà UI Manager đã build cần nhưng chưa có trong
backend hiện tại.

## Quy ước chung

- Base URL local: `http://localhost:8000`; mọi route nghiệp vụ có prefix `/api/v1`.
- Session qua cookie (`withCredentials: true`), không dùng `Authorization: Bearer`.
- Mọi `POST` / `PATCH` / `DELETE` phải gửi header `X-CSRF-Token` = giá trị cookie `scheduler_csrf`.
- `401` = chưa đăng nhập/session hết hạn. `403` = sai role hoặc ngoài phạm vi dữ liệu (backend luôn là
  nơi quyết định quyền, FE ẩn UI chỉ là UX, không phải kiểm soát bảo mật).
- Lỗi nghiệp vụ trả `422`/`409` kèm `detail.code` (dùng để FE switch message) và `detail.message`.
- Field `reason`/`note` bắt buộc trên các thao tác ghi có ảnh hưởng người khác — luôn ghi `AuditLog`
  (BR-SCH-05, BR-PUB-04).

### Lọc theo học kỳ

Các endpoint danh sách chính đã hỗ trợ `semester_id` để FE giữ một Semester Context nhất quán:
`GET /projects`, `GET /groups`, `GET /rounds`, `GET /dashboard` và các report Manager.
Khi truyền đồng thời `round_id` và `semester_id`, backend áp dụng cả hai điều kiện; không có dữ liệu
ngoài học kỳ được chọn lọt vào dashboard hoặc report.

---

## 1. Học kỳ — `/manager/semesters`

Đã có đầy đủ, dùng chung với Admin.

### `GET /semesters`

- **Role:** `ADMIN`, `MANAGER`.
- **Query:** `search`, `status=ACTIVE|CLOSED`, `academic_year=YYYY-YYYY` (optional, AND semantics).
- **Response `200`:** `[{ id, code, name, note, start_date, end_date, academic_year, status, project_count, group_count, round_count, created_at, created_by, updated_at, updated_by }]`.

### `GET /semesters/{semester_id}`

- **Role:** `ADMIN`, `MANAGER`.
- **Response `200`:** cùng shape đầy đủ với một phần tử list.
- **`404 SEMESTER_NOT_FOUND`** nếu không tồn tại.

### `POST /semesters`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`SemesterCreate`](schemas.md#semestercreate):** `{ code, name, note?, start_date, end_date }`.
- Backend luôn tạo với `status = ACTIVE`; client không chọn được trạng thái khởi tạo.
- Thời lượng `end_date - start_date + 1` phải trong khoảng `SEMESTER_MIN_DURATION_DAYS`–`SEMESTER_MAX_DURATION_DAYS`
  (mặc định 105–120 ngày).
- **`201`:** semester đầy đủ.
- **`409 DATA_DUPLICATE`:** code trùng.
- **`422 SEMESTER_DURATION_INVALID`:** sai khoảng ngày.

### `PATCH /semesters/{id}`

- **Body:** các field tùy chọn `code`, `name`, `note`, `start_date`, `end_date`.
- Không sửa trực tiếp `status` hoặc `academic_year`.
- **`200`:** semester object đầy đủ và metadata `updated_by`/`updated_at`.

### `POST /semesters/{id}/set-current`

- **Role:** `ADMIN`, `MANAGER`.
- Đóng semester ACTIVE hiện tại và mở semester đích trong một transaction.
- Gọi lại với semester đang ACTIVE là idempotent.
- **`200`:** semester object đầy đủ của semester đích.

### `POST /semesters/{id}/transition`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ target_status: "CLOSED", reason }`.
- Chỉ cho phép transition kế tiếp `PLANNING → ACTIVE → CLOSED → ARCHIVED`; `ARCHIVED` chỉ đọc (BR-SEM-02: chỉ 1 semester `ACTIVE` cùng lúc).
- **`200`:** `{ id, status }`.
- **`403`:** không phải ADMIN/MANAGER.
- **`422`:** transition không hợp lệ.

---

## 2. Đề tài & Nhóm sinh viên — `/manager/projects`, `/manager/groups`

### `GET /majors`, `GET /students`, `GET /lecturers`, `GET /rooms`

- **Role:** `ADMIN`, `MANAGER`. Dùng làm lookup data cho các form tạo project/group/round.
- `GET /lecturers` → `[{ id, lecturer_code, account_id, email, display_name, account_status, conflicts }]`.
- `GET /rooms` → `[{ id, code, name, capacity, active }]`.

### `POST /lecturers`, `POST /rooms`

- **Role:** `ADMIN`, `MANAGER`.
- Manager có thể tạo lecturer mới (kèm account + role `LECTURER`) và tạo room để dùng làm resource cho round.
- Request/response giữ nguyên contract trong [`admin-api.md`](admin-api.md); mọi thao tác ghi đều có CSRF và audit log.

### `GET /projects`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `[{ id, code, title, status, semester_id, semester_code, major_code, supervisor_count, supervisors }]`.

### `POST /projects`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`ProjectCreate`](schemas.md#projectcreate):**
  ```json
  { "semester_id": 1, "major_id": 2, "code": "PRJ001", "title": "Capstone Scheduler", "supervisors": ["LEC001:MAIN", "LEC002:CO"] }
  ```
  `supervisors` 1–2 phần tử, chuỗi `LECTURER_CODE:SUPERVISOR_TYPE` (BR-PRJ-01: đúng 1 `MAIN`, tối đa 1 `CO`).
- **`201`:** `{ id, code, title }`.
- **`409 DATA_DUPLICATE`:** code trùng trong semester (BR-PRJ-02: 1 đề tài ↔ 1 nhóm/semester).
- **`422 SUPERVISOR_NOT_FOUND` / `DATA_INVALID`.**

### `GET /groups`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `[{ id, code, status, project_code, title, active_member_count, leader_count, leader_name }]`.
- `active_member_count` phản ánh BR-STU-03: nhóm dưới 4 người do drop-out vẫn hợp lệ, chỉ hiển thị cảnh báo, không chặn.

### `POST /groups`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`GroupCreate`](schemas.md#memberpayload-và-groupcreate):**
  ```json
  { "project_id": 1, "code": "G001", "members": [
    { "student_code": "SE001", "role": "LEADER" },
    { "student_code": "SE002", "role": "MEMBER" },
    { "student_code": "SE003", "role": "MEMBER" },
    { "student_code": "SE004", "role": "MEMBER" }
  ] }
  ```
  `members` 4–5 phần tử (BR-GRP-02), đúng 1 `LEADER` (BR-GRP-03).
- **`201`:** `{ id, code, member_count }`.
- **`409 DATA_DUPLICATE` / `422 PROJECT_NOT_FOUND` / `STUDENT_NOT_FOUND`.**

### `POST /groups/{group_id}/members/{student_id}/drop`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ reason }` (1–1000 ký tự).
- **`200`:** `{ group_id, student_id, status: "DROPPED", warning?: "GROUP_BELOW_MINIMUM_MAY_CONTINUE" }`.
- Không tự xóa group khi dưới sĩ số tối thiểu; chỉ cảnh báo (BR-STU-03).
- Sinh viên đã drop không được đánh giá cá nhân từ thời điểm hiệu lực (BR-STU-02).

### `POST /groups/{group_id}/leader`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ student_id, reason }`; `student_id` phải là active member.
- **`200`:** `{ group_id, leader_student_id }`.
- Bắt buộc gán leader mới trước khi nhóm được xếp lịch nếu leader cũ đã drop (BR-GRP-03).

### `POST /lecturers/{lecturer_id}/conflicts`

- **Role:** `ADMIN`, `MANAGER`, `LECTURER` (Lecturer chỉ khai cho chính mình; Manager khai thay được).
- **Body [`ConflictCreate`](schemas.md#conflictcreate):** `{ project_id, reason }`.
- **`200`:** `{ id, lecturer_id, project_id }`.
- Conflict dùng để loại candidate Reviewer khi chạy scheduler (ràng buộc **H8**).

---

## 3. Đợt đánh giá & Cấu hình — `/manager/rounds`, `/manager/rounds/[roundId]`

### 3.1. Danh sách & tạo round

### `GET /rounds`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `[{ id, semester_id, type, status, reviewer_count, result_owner_mode, group_selection_mode, session_duration_minutes, registration_deadline, h12_sessions_per_part, h12_sessions_per_day, h12_semester_quota, soft_weights }]`.
- `type`: `REVIEW_1 | REVIEW_2 | DEFENSE_1_1 | DEFENSE_1_2 | DEFENSE_2` (BR-RND-01).

### `POST /rounds`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`RoundCreate`](schemas.md#roundcreate):**
  ```json
  {
     "semester_id": 1, "type": "DEFENSE_1_1", "reviewer_count": 3,
    "result_owner_mode": true, "group_selection_mode": false,
    "session_duration_minutes": 45, "registration_deadline": "2026-08-22T17:00:00+07:00",
    "h12_sessions_per_part": 4, "h12_sessions_per_day": 8, "h12_semester_quota": 20,
    "soft_weights": { "S1": 10, "S2": 5 }
  }
  ```
  `soft_weights` key chỉ nhận `S1`…`S9` (mục 6.2 Business Rules — cân bằng tải GV là **S1**, ưu tiên cao nhất).
- **`201`:** round object như `GET /rounds`, status khởi tạo `DRAFT`.
- **`422`:** type/config/semester không hợp lệ.

### `POST /rounds/{round_id}/transition`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`RoundTransitionPayload`](schemas.md):** `{ target_status, reason? }`.
- Vòng đời (BR-RND §5.1): `DRAFT → OPEN_REGISTRATION → REGISTRATION_CLOSED → SCHEDULING → SCHEDULED → PUBLISHED → ONGOING → COMPLETED → LOCKED`.
- Transition sang `SCHEDULING` sẽ kiểm tra đã có group/timeslot và đủ reviewer availability; room inventory không còn là điều kiện để bắt đầu scheduler.
- Từ `PUBLISHED` trở đi mọi sửa lịch phải qua controlled-change (BR-RND-05); `LOCKED` chỉ đọc, chỉ Admin unlock được (BR-RND-06).
- **`200`:** `{ round_id, status }`.
- **`422 ROUND_INPUTS_INCOMPLETE` / `ROUND_STATUS_INVALID`.**

### 3.2. Cấu hình round — ngày, slot, tài nguyên

### `POST /rounds/{round_id}/days`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`RoundDayCreate`](schemas.md#rounddaycreate):**
  ```json
  { "day_date": "2026-08-25", "slots": [
    { "start_at": "2026-08-25T08:00:00+07:00", "end_at": "2026-08-25T08:45:00+07:00" }
  ] }
  ```
- Phòng **không** gắn vào slot ở bước này — phòng do thuật toán gán khi xếp lịch (BR-RND-02).
- **`201`:** `{ round_id, day_id, timeslot_ids }`.
- **`409 TIMESLOT_DUPLICATE`.**

### `POST /rounds/{round_id}/resources`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`RoundResources`](schemas.md#roundresources):** `{ group_ids: number[], room_ids: number[], timeslot_ids: number[] }` — cả 3 mảng bắt buộc, mỗi mảng ≥1 phần tử.
- Attach group idempotent; room phải `active`; timeslot phải thuộc round.
- **`200`:** `{ round_id, groups, timeslots, rooms }` (số ID unique đã nhận).

### 3.3. Mời giảng viên & lịch rảnh

### `POST /rounds/{round_id}/invitations`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ lecturer_ids: number[] }` (≥1 phần tử).
- **`200`:** `{ round_id, invited_count }`. Tạo notification/outbox cho lecturer.

### `POST /rounds/{round_id}/invitations/{lecturer_id}/response`

- Lecturer và Manager đều có thể ghi response; Manager dùng endpoint này để xử lý thay. Roster chi tiết dùng `GET /rounds/{round_id}/invitations`.

### `POST /rounds/{round_id}/lecturers/{lecturer_id}/availability`

- **Role:** `ADMIN`, `MANAGER`, `LECTURER`.
- **Scope:** Manager/Admin nhập hộ lecturer (khi lecturer quên đăng ký — BR-AVL-04: không đăng ký = hệ thống coi là bận toàn bộ).
- **Body [`AvailabilitySubmit`](schemas.md#availabilitysubmit):** `{ selected_timeslot_ids: number[], load_preference?: "LOW"|"MEDIUM"|"HIGH" }`.
- `load_preference` là đầu vào chính cho ràng buộc mềm **S1** (cân bằng tải).
- **`200`:** `{ round_id, lecturer_id, selected_count, total_slots, source: "FORM"|"MANAGER" }`.

### `POST /rounds/{round_id}/groups/{group_id}/availability`

- **Role:** `ADMIN`, `MANAGER`, `STUDENT` (student chỉ khi là active leader).
- Chỉ dùng được khi round bật `group_selection_mode=true` (BR-AVL-06). Rỗng ⇒ coi như rảnh mọi slot (BR-AVL-07, ngược với luật của lecturer).
- **`200`:** `{ round_id, group_id, selected_count, total_slots, source }`.
- **`409 GROUP_SELECTION_DISABLED`.**

### `GET /rounds/{round_id}/registration`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `{ invited, responded, lecturer_availability, group_availability }` — số đếm tổng; dùng thêm `GET /rounds/{round_id}/invitations` và `GET /rounds/{round_id}/groups` cho bảng chi tiết.

### `GET /rounds/{round_id}/my-availability`

- **Role:** tất cả role đăng nhập; Admin/Manager nhận thêm `selected_by_lecturer`, `selected_by_group` (audit view).
- **Response cơ sở:**
  ```json
  {
    "round": { "id": 4, "type": "DEFENSE_1_1", "group_selection_mode": false, "registration_deadline": "..." },
    "timeslots": [ { "id": 10, "start_at": "...", "end_at": "...", "day_date": "2026-08-25" } ]
  }
  ```
- **Đây là nguồn timeslot cho màn hình Lịch đánh giá (Calendar)** — dùng `timeslots` để dựng cột giờ, dùng `selected_by_lecturer`/`selected_by_group` để biết ai đã đăng ký slot nào trước khi chạy scheduler.

---

## 4. Xếp lịch — `/manager/rounds/[roundId]` tab "Xếp lịch"

### `POST /rounds/{round_id}/schedule/run`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`ScheduleRunPayload`](schemas.md#schedulerunpayload):** `{ random_seed?: number, time_limit_seconds?: number }` (mặc định `0` và `10`, tối đa `300`).
- Solver áp toàn bộ ràng buộc cứng **H1–H13 khi được cấu hình** (mục 6.1 Business Rules) và tối ưu **S1–S9** theo `soft_weights` của round.
- Có thể chạy **nhiều lần**, mỗi lần tạo 1 `ScheduleVersion` mới kèm điểm số để so sánh (BR-SCH-01). Không cho double-click; disable nút khi đang chạy.
- Khi không tìm được lời giải đầy đủ vẫn trả kết quả một phần kèm lý do cụ thể từng nhóm chưa xếp được (BR-SCH-02) và đề xuất phương án gỡ (BR-SCH-03).
- **`201`:** `{ version_id, status, scheduled_count, unscheduled: [...], soft_scores: { "S1": 4, ... } }`.
- **`422 ROUND_INPUTS_INCOMPLETE`** (thiếu group/timeslot hoặc reviewer availability; room inventory không bắt buộc để chạy solver).
- **`422 SCHEDULE_RERUN_FORBIDDEN`** (round đã publish/ongoing/terminal — dùng controlled-change thay vì run lại).
- **`422 ROUND_POSTPONED`** (phải reopen round trước).
- **`409 SCHEDULE_PERSIST_FAILED`.**

### `GET /rounds/{round_id}/schedule/versions`

- **Role:** tất cả role (Manager thấy mọi version).
- **Response:** `[{ id, round_id, version_no, status, solver_status, total_score, soft_scores, random_seed, created_at, activated_at }]`.
- `status`: `VALID | PUBLISHED | SUPERSEDED`.

### `GET /schedule/versions/{version_id}`

- **Role:** tất cả role (Manager xem mọi session).
- **Response:** version fields + `sessions: [{ id, group_id, group_code, project_id, timeslot_id, room_id, start_at, end_at, status, reviewer_ids, result_owner_ids, reviewer_names }]`.
- **Đây là nguồn dữ liệu chính cho Calendar** (phòng, giờ, reviewer thật) — kết hợp với `GET /rounds/{round_id}/my-availability` cho danh sách timeslot/phòng khả dụng.
- Session `status`: `SCHEDULED | ONGOING | COMPLETED | POSTPONED`.

### `POST /schedule/versions/{version_id}/activate`

- **Role:** `ADMIN`, `MANAGER`.
- Chỉ version `VALID` activate được; các version `VALID` khác cùng round bị supersede.
- **`200`:** `{ version_id, status }`.
- **`404 VERSION_NOT_FOUND` / `422 VERSION_NOT_VALID`.**

### `POST /rounds/{round_id}/schedule/publish/{version_id}`

- **Role:** `ADMIN`, `MANAGER`.
- Version phải đã activate và pass hard-constraint validation. Publish tạo notification cho hội đồng, GVHD, trưởng nhóm (BR-PUB-01). Version published cũ bị `SUPERSEDED`; round chuyển `PUBLISHED`.
- **`200`:** `{ round_id, version_id, status: "PUBLISHED", recipient_count }`.
- **`422 VERSION_NOT_ACTIVE`.**

### `GET /sessions/{session_id}/replacement-suggestions`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** tối đa 50 item `{ timeslot_id, room_id, reviewer_ids, replaces }` — đã lọc qua validator, có thể prefill `SessionEditPayload` (vẫn phải gửi `reason`, backend validate lại).

### `POST /schedule/versions/{version_id}/sessions/{session_id}/result-owner`

- **Role:** `MANAGER` (chỉ Manager, không phải Admin).
- **Body [`ResultOwnerPayload`](schemas.md):** `{ lecturer_id }` — phải là 1 trong các Reviewer của session.
- Chỉ dùng khi round bật `result_owner_mode` và type là `DEFENSE_1_1`/`DEFENSE_2`. Session đã `COMPLETED` thì immutable.
- **`200`:** `{ version_id, session_id, result_owner_id }`.

### `POST /rounds/{round_id}/groups/{group_id}/h11-waiver` · `DELETE .../h11-waiver`

- **Role:** `MANAGER` (chỉ Manager).
- **H11** (BR mục 6.1): Defense 1.2 mặc định phải giữ ít nhất một Reviewer đã chấm Defense 1.1 của nhóm đó — waiver là cách Manager gỡ ràng buộc này **theo từng nhóm**, bắt buộc ghi lý do.
- POST **`200`:** `{ id, round_id, group_id, active: true }` (gọi lại sẽ upsert/activate lại).
- DELETE **`200`:** `{ id, round_id, group_id, active: false }`.
- **`404`** nếu waiver/group không tồn tại trong round.

---

## 5. Vận hành sau công bố — sửa lịch, hoãn, đổi lịch

### `POST /schedule/versions/{version_id}/sessions/{session_id}/edit`

- **Role:** `ADMIN`, `MANAGER`.
- Chỉ sửa version `VALID` hiện tại (draft-edit, trước khi publish).
- **Body [`SessionEditPayload`](schemas.md#sessioneditpayload):** `{ timeslot_id?, room_id?, reviewer_ids?, result_owner_id?, reason }` — field nào không gửi giữ nguyên giá trị cũ; `reason` luôn bắt buộc.
- Backend chạy lại **H1, H2, H3** (chặn cứng) và kiểm tra reviewer/Result Owner; các vi phạm ràng buộc mềm khác chỉ cảnh báo (BR-SCH-04).
- **`200`:** `{ session_id, version_id, status: "UPDATED" }`.
- **`422 HARD_CONSTRAINT_VIOLATION`** (`detail.violations: []`).
- **`409 DRAFT_EDIT_CONCURRENT_UPDATE`** — reload rồi thử lại.

### `POST /schedule/versions/{version_id}/sessions/{session_id}/controlled-change`

- **Role:** `ADMIN`, `MANAGER`.
- Chỉ dùng cho version đã `PUBLISHED` (BR-PUB-02: sau công bố vẫn được đổi thành viên hội đồng trong lúc đợt diễn ra). Không mutate version published — tạo version mới `VALID`, copy session/result liên quan, ghi change record.
- **Body:** cùng `SessionEditPayload`.
- Người thay thế phải thỏa toàn bộ **H1, H2, H3, H6, H8** (BR-PUB-03). Thay đổi không ảnh hưởng kết quả các phiên đã hoàn thành trước đó (BR-PUB-05 — result gắn cứng với hội đồng tại thời điểm phiên diễn ra).
- **`200`:** `{ version_id, source_version_id, session_id, status: "VALID" }`.
- **`422 CONTROLLED_CHANGE_REQUIRES_PUBLISHED` / `COMPLETED_SESSION_IMMUTABLE` / `HARD_CONSTRAINT_VIOLATION`.**
- **`409 CONTROLLED_CHANGE_CONCURRENT_UPDATE`.**

### `POST /sessions/{session_id}/postpone`

- **Role:** `ADMIN`, `MANAGER`.
- Chỉ postpone session đang `SCHEDULED`/`ONGOING`. Nếu không tìm được người thay thế hợp lệ khi có sự cố (BR-INC-01: GV vắng đột xuất — hội đồng luôn phải đủ 3 người, không chấp nhận 2 người), phiên phải hoãn và xếp lại vào slot bù, nhóm không bị đánh giá bất lợi (BR-INC-02).
- **Body [`RescheduleRequestPayload`](schemas.md):** `{ reason }`.
- **`200`:** `{ id, status: "POSTPONED" }`. Tạo notification cho recipient bị ảnh hưởng.

### `POST /reschedule-requests/{request_id}/decision`

- **Role:** `ADMIN`, `MANAGER`.
- **Body:** `{ decision: "APPROVED"|"REJECTED", note }`.
- Chỉ request đang `REQUESTED` mới quyết định được. Quyết định chỉ đổi trạng thái request — việc sắp lại lịch thực tế vẫn dùng `edit`/`controlled-change`.
- **`200`:** `{ id, status, decision_note }`.
- **`404 RESCHEDULE_REQUEST_NOT_FOUND`.**

### `POST /rounds/{round_id}/operation`

- **Role:** `ADMIN`, `MANAGER`.
- **Body [`RoundOperationPayload`](schemas.md):** `{ action: "POSTPONED"|"CANCELLED", reason }`.
- **`200`:** `{ round_id, status }`. Mọi operation ghi audit + notification.

---

## 6. Kết quả & Khắc phục — `/manager/results`

### `POST /sessions/{session_id}/result`

- **Role:** `MANAGER`, `LECTURER`.
- **Scope:** Manager nhập/sửa bất kỳ lúc nào; Lecturer phải là Reviewer được assign (Result Owner nếu round bật `result_owner_mode` cho D1.1/D2).
- **Body [`ResultPayload`](schemas.md#resultpayload):**
  ```json
  { "outcome": "PASSED", "note": "...", "remediation_due_at": null, "verifier_lecturer_id": null, "correction_reason": null }
  ```
- **Luật outcome (mục 8.3 Business Rules — decision table Mức 1–4):**
  - `DEFENSE_1_1` outcome `LEVEL_2` **bắt buộc** có `remediation_due_at` + `verifier_lecturer_id` hợp lệ (Reviewer của session) — chỉ D1.1 Level 2 tạo remediation case.
  - `DEFENSE_1_2`/`DEFENSE_2` **không** được gửi remediation field.
  - D1.2 outcome `COMPLETED` đánh dấu session `COMPLETED`.
  - Sửa result đã tồn tại: chỉ Manager được sửa, bắt buộc `correction_reason`; không sửa được nếu remediation đã completed.
- **`201`:** `{ id, session_id, outcome, group_status }` — `group_status` theo máy trạng thái nhóm (mục 9: `ACTIVE → D12_CONDITIONAL/ELIGIBLE_D12/PENDING_D2/FAILED → ...`).
- **`422 RESULT_OWNER_REQUIRED` / `REMEDIATION_FIELDS_REQUIRED` / `REMEDIATION_NOT_ALLOWED` / `RESULT_CORRECTION_FORBIDDEN` / `RESULT_AFTER_REMEDIATION`.**
- **`409 RESULT_CONCURRENT_UPDATE`.**

### `GET /remediation`

- **Role:** tất cả role; Manager thấy tất cả case.
- **Response:** `[{ id, group_id, group_code, status, due_at, verifier_lecturer_id, note, round_type }]` — `status`: `OPEN | OVERDUE | PASSED | FAILED`.
- Đây là nguồn dữ liệu chính cho cột "Khắc phục" của bảng Kết quả & khắc phục.

### `POST /remediation/{case_id}/overdue-fail`

- **Role:** `MANAGER` (chỉ Manager, không phải Lecturer/Admin).
- **Body [`OverdueFailPayload`](schemas.md):** `{ reason }`.
- Chỉ fail case `OPEN`/`OVERDUE` **sau khi đã quá `due_at`**. Việc chuyển Mức 2 quá hạn ⇒ Không đạt là **bán tự động**: hệ thống chỉ cảnh báo, Manager phải bấm xác nhận.
- **`200`:** `{ id, status: "FAILED" }`.
- **`422 REMEDIATION_NOT_OVERDUE`.**
- **`409 REMEDIATION_ALREADY_DECIDED`.**

> Quyết định `PASSED`/`FAILED` bình thường (không overdue) do **Lecturer** (Reviewer phản biện, verifier) gọi
> `POST /remediation/{case_id}/decision`, Manager không gọi trực tiếp nhưng cần thấy kết quả qua `GET /remediation`.

---

## 7. Tổng quan & Báo cáo — `/manager/dashboard`, `/manager/progress`, `/manager/reports`

### `GET /dashboard?round_id={round_id}&semester_id={semester_id}`

- **Role:** `ADMIN`, `MANAGER`.
- `round_id` optional — bỏ trống lấy aggregate/default version.
- **Response:** `{ totals: { projects, groups, students, lecturers }, availability: { invited, responded }, groups: { total, scheduled, unscheduled }, pending_reschedule_requests, changes, version, lecturer_load: [{ id, lecturer_code, display_name, session_count }], attention_groups: [{ id, code, status }], attention: { no_leader, under_four, remediation_overdue, unscheduled } }`.
- `attention_groups` chỉ chứa nhóm cần chú ý: `D12_CONDITIONAL`, `FAILED`, `DROPPED`.
- `semester_id` scopes totals, availability, selected version, lecturer load, requests, changes và attention groups.

### `GET /reports/lecturer-load?round_id={round_id}&semester_id={semester_id}`

- **Role:** `ADMIN`, `MANAGER`. `round_id` optional.
- **Response:** `{ round_id, version, rows: [{ lecturer_id, lecturer_code, display_name, session_count, quota, quota_percent }] }`.
- Nguồn cho mục "Tải giảng viên" của trang Báo cáo.

### `GET /reports/unscheduled?round_id={round_id}`

- **Role:** `ADMIN`, `MANAGER`. **`round_id` bắt buộc.**
- **Response:** `{ round_id, generated_at, versions: [{ version_id, version_no, status, created_at, unscheduled, provenance }] }`.

### `GET /reports/quality?semester_id={semester_id}`

- **Role:** `ADMIN`, `MANAGER`.
- **Response:** `{ version, rows: [{ id, code, active_members, leaders }] }` — nhóm dưới sĩ số tối thiểu hoặc không đúng 1 leader.

### `GET /reports/remediation?round_id={round_id}&semester_id={semester_id}`

- **Role:** `ADMIN`, `MANAGER`. `round_id` optional.
- **Response:** `{ round_id, version, rows: [{ id, group_id, group_code, due_at, status, verifier_lecturer_id }] }`.

### `GET /reports/outcomes?round_id={round_id}&semester_id={semester_id}`

- **Role:** `ADMIN`, `MANAGER`. `round_id` optional.
- **Response:** `{ round_id, version, rows: [{ type, outcome, count }] }` — nguồn cho biểu đồ phân bố kết luận (Mức 1–4) trong trang Báo cáo.

### `GET /reports/provenance/{version_id}`

- **Role:** tất cả role (Manager luôn trong scope).
- **Response:** `{ version_id, version_no, status, created_at, round_id, type, semester_code, generated_at }`.

### Mockdata alignment endpoints (migration `0014_manager_mock_alignment`)

Các màn hình mockdata hiện có API tương ứng:

- `PATCH /semesters/{id}`: sửa code/name/ngày, giữ nguyên lifecycle `ACTIVE | CLOSED`.
- `GET/PATCH /projects/{id}`, `GET/PATCH /groups/{id}` và `POST /projects/import`, `POST /groups/import`.
- `GET/PATCH /rounds/{id}`, `GET /rounds/{id}/invitations`, `POST /rounds/{id}/invitations/{lecturer_id}/resend`, `GET /rounds/{id}/groups`.
- `PATCH/DELETE /timeslots/{id}` để sửa hoặc disable slot.
- `GET/PUT /semesters/{id}/lecturer-quotas/{lecturer_id}` và danh sách quota của kỳ.
- `GET /sessions`, `GET /sessions/{id}`, `GET /reschedule-requests`, `GET /results`, `GET /reports/group-progress`.
- `GET /schedule/versions/compare/{version_a}/{version_b}` và `DELETE /schedule/versions/{version_id}` cho Compare/Delete draft.
- `GET /exports/round/{id}.xlsx`, `GET /exports/semester/{id}/schedule.xlsx`, `GET /exports/semester/{id}/results.xlsx`.

Các API này vẫn dùng ID số của backend; FE có thể hiển thị code dạng `LEC001`, `G01`, `SV-D11-003` từ các field code tương ứng.

### Trang "Tiến độ nhóm" (`/manager/progress`)

`GET /reports/group-progress?semester_id=` trả một dòng cho mỗi nhóm, gồm Review 1/2, Defense 1.1/1.2/2,
trạng thái remediation, hạn xử lý và verifier; FE không cần ghép nhiều report aggregate.

---

## 8. API còn thiếu — cần bổ sung cho Manager UI

Các endpoint từng được liệt kê ở mục 8.2–8.6 đã được bổ sung trong migrations `0014_manager_mock_alignment`
và `0015_round_minute_limits`; phần dưới chỉ còn các nhu cầu nâng cao chưa có trong contract hiện tại.

Các mục dưới đây là **đề xuất mới**, dựa trên đối chiếu trực tiếp với các trang Manager đã build
(`app/(manager)/manager/**`). Method/path/response là gợi ý, backend team quyết định hình dạng cuối cùng.

### 8.1. Lọc theo `semester_id` (đã có)

Đã triển khai cho `GET /projects`, `GET /groups`, `GET /rounds`, `GET /dashboard` và các report
`lecturer-load`, `quality`, `remediation`, `outcomes`. FE nên truyền `semester_id` ở mọi màn hình có
Semester Context.

### 8.2. `GET /rounds/{round_id}` — chi tiết 1 round (đã có)

Round Detail hiện dùng `GET /rounds/{round_id}`; cấu hình có ngày, minute quota, H13 capacity và danh sách day/timeslot.

### 8.3. `GET /rounds/{round_id}/invitations` — roster mời giảng viên (đã có)

Tab "Giảng viên" của Round Detail cần danh sách từng giảng viên kèm: trạng thái mời (`PENDING/ACCEPTED/REJECTED`),
số slot đã đăng ký rảnh, `load_preference`, quota kỳ, số slot đã dùng. `GET /rounds/{round_id}/registration`
hiện chỉ trả tổng số đếm (`invited`, `responded`, ...), không đủ để render bảng theo từng dòng giảng viên.
Response thực tế: `[{ round_id, lecturer_id, lecturer_code, display_name, email, status, response_reason,
responded_at, available_slot_count, load_preference }]`; `DECLINED` của DB được map thành `REJECTED` cho UI.

### 8.4. `GET /rounds/{round_id}/groups` — roster nhóm tham gia round (đã có)

Tab "Nhóm tham gia" dùng response thực tế: `[{ group_id, group_code, status, ui_status, project_code,
title, active_member_count, leader_name, selected_slot_count }]`.

### 8.5. Field tên GVHD / Leader trên list endpoint (đã có)

`GET /projects` đã trả thêm `supervisors`; `GET /groups` trả `leader_name` và `ui_status`. Chi tiết đầy đủ
của từng project/group dùng `GET /projects/{id}` và `GET /groups/{id}`.

### 8.6. Tổng hợp tiến độ nhóm theo nhiều round (đã có)

`GET /reports/group-progress?semester_id=` trả `group_id`, `group_code`, `project_name`, outcome của
Review 1/2 và Defense 1.1/1.2/2, cùng các field remediation (`status`, `due_at`, `verifier_lecturer_id`).

### 8.7. "Giảng viên báo vắng" trên Dashboard

`GET /dashboard` hiện không có field đếm số giảng viên báo vắng đột xuất (BR-INC-01) đang cần Manager xử
lý. Nếu nghiệp vụ này được model bằng chính flow `postpone` + `controlled-change`, đề xuất thêm
`pending_replacements: number` vào response `GET /dashboard`, đếm session có sự cố chưa xử lý xong.

---

## Tham chiếu

- [`master-data.md`](master-data.md) — semester, account, project, group, round setup, availability, invitation.
- [`scheduling.md`](scheduling.md) — chạy scheduler, activate/publish, sửa lịch, hoãn, reschedule.
- [`results-reports.md`](results-reports.md) — result, remediation, dashboard, reports, notification, calendar export.
- [`schemas.md`](schemas.md) — schema chính xác cho mọi request body.
- [`role-api-matrix.md`](role-api-matrix.md) — bảng endpoint theo role (nguồn cho phần phân quyền ở trên).
- [`project-reference/BusinessRules_CapstoneScheduler_v1.0.md`](../project-reference/BusinessRules_CapstoneScheduler_v1.0.md) — mã `BR-*`/`H*`/`S*` được trích dẫn trong tài liệu này.
