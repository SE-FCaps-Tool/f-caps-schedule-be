# Room Assignment — luồng gán phòng vật lý cho session

Phạm vi tài liệu: chỉ luồng gán phòng post-activation (`room_assignment.py` + `target_room_publish.py`).
Không cover auto-scheduling algorithm (solver chọn Time+Council), council flow, hay manual-scheduling
draft flow (`manual_schedule_sessions.room_id` là bảng khác, xem doc riêng nếu có).

## 1. Tổng quan luồng

- **Mục đích:** gán `room_id` vật lý cho từng `sessions` sau khi một `schedule_version` đã được activate
  (status `ACTIVE`). Solver ở bước generate/activate chỉ xếp Time + Council, **không** chọn room
  (`docs/api/scheduling.md` §4, §9 xác nhận). `room_id` trên session mới activate luôn là `NULL`.
- **Khi nào chạy:** sau `POST /schedule/versions/{version_id}/activate`, trước khi
  `POST /rounds/{round_id}/actions/publish` (hoặc `POST /rounds/{round_id}/schedule/publish/{version_id}`
  — cùng logic publish, khác route prefix). Publish sẽ chặn nếu còn session chưa có phòng hợp lệ.
- **Ai trigger:** role `ADMIN` hoặc `MANAGER` (mọi endpoint đều gọi `_require`/`_manager` chặn role khác,
  403 `AUTH_FORBIDDEN`/`Insufficient permission`). Manager UI dùng `target_room_publish.py` (route có
  `success_payload` envelope); `room_assignment.py` là route "core" không bọc envelope, được
  `target_room_publish.py` import và tái sử dụng trực tiếp (không proxy HTTP, gọi hàm Python thẳng).

## 2. Entry points

Tất cả prefix `/api/v1`. Cột "File tái export" chỉ áp dụng cho route bị wrap lại ở
`target_room_publish.py` để thêm `success_payload` envelope.

| Method + Path | Handler | File:line | File tái export |
|---|---|---|---|
| `GET /rounds/{roundId}/rooms/available` | `list_available_rooms` | `apps/api/app/routes/room_assignment.py:95` | `target_room_publish.py:52` (`target_available_rooms`) |
| `PUT /sessions/{sessionId}/room` | `assign_session_room` | `apps/api/app/routes/room_assignment.py:135` | `target_room_publish.py:64` (`target_assign_room`) |
| `POST /rounds/{roundId}/rooms/suggest` | `suggest_rooms` | `apps/api/app/routes/room_assignment.py:205` | `target_room_publish.py:69` (`target_suggest_rooms`) |
| `POST /rounds/{roundId}/rooms/apply-suggestions` | `apply_room_suggestions` | `apps/api/app/routes/room_assignment.py:213` | `target_room_publish.py:74` (`target_apply_room_suggestions`) |
| `PATCH /rooms/{roomId}` | `update_room` | `apps/api/app/routes/target_room_publish.py:89` | — (chỉ tồn tại ở target layer) |
| `GET /rounds/{roundId}/publish-readiness` | `publish_readiness` | `apps/api/app/routes/target_room_publish.py:121` | — |
| `POST /rounds/{roundId}/actions/publish` | `publish_target_schedule` | `apps/api/app/routes/target_room_publish.py:142` | gọi thẳng `schedule_operations.publish_schedule` |

Vì `room_assignment.py` không dùng `success_payload`, hai route trùng path (`GET .../rooms/available`,
`PUT .../sessions/{sessionId}/room`, `POST .../rooms/suggest`, `POST .../rooms/apply-suggestions`) tồn
tại 2 lần trong OpenAPI — một bản raw dict, một bản `ApiDataEnvelope`. FastAPI/router nào được include
sau sẽ thắng route conflict; không audit thứ tự include trong `main.py` ở đây (ngoài phạm vi file này).

Service module dùng chung, không phải route: `apps/api/app/services/room_assignment.py`
(`RoomAssignmentError`, `lock_room_ids`, `allowed_room`, `find_room_conflict`,
`allocate_room_assignments`, `validate_assignment_batch`, `build_room_suggestions`,
`validate_publish_room_readiness`).

## 3. Business logic từng bước

### 3.1. Liệt kê phòng khả dụng — `list_available_rooms`

`apps/api/app/routes/room_assignment.py:95-132`.

1. Yêu cầu round tồn tại (`_round_or_404`) và có version `ACTIVE` (`_active_version_or_error`) — nếu
   không, `422 ROOM_ASSIGNMENT_STATE_INVALID`.
2. Query base: `rooms.active = TRUE` AND room_type nằm trong `round_room_types` của round đó AND
   (nếu có filter `roomType`/`room_type`) khớp đúng loại.
3. Nếu có `timeslotId`/`timeslot_id`: lookup `timeslots` join `round_days` để xác nhận timeslot thuộc
   round, lấy `start_at`/`end_at`; thêm điều kiện `NOT EXISTS` — loại phòng đang bị chiếm bởi bất kỳ
   session nào có `schedule_version.status IN ('ACTIVE','PUBLISHED')` overlap khung giờ đó. Đây là kiểm
   tra **global** (không giới hạn trong round hiện tại) nên phòng đang dùng ở round khác cũng bị loại.
4. Không filter theo `timeslotId` → trả toàn bộ phòng active + đúng loại, không tính occupancy (FE tự
   diễn giải "available" theo field `available: true` mặc định trên `AvailableRoomResponse`, field này
   **không** được tính lại theo occupancy — chỉ default `True`).

### 3.2. Gán 1 phòng cho 1 session — `assign_session_room` (`PUT /sessions/{sessionId}/room`)

`apps/api/app/routes/room_assignment.py:135-202`.

1. Transaction: đọc session (join `schedule_versions` lấy `round_id`, `version_status`), 404 nếu không
   tồn tại.
2. `ensure_round_semester_writable` — chặn ghi nếu học kỳ cha đã archived/closed
   (`apps/api/app/services/semester_queries.py:35`).
3. Lock thứ tự **Round → ScheduleVersion → Session → Room** (`FOR UPDATE` từng bước, comment ở route
   file dòng 32-33 liệt kê structured failure codes). Re-select session lần 2 sau khi đã lock version.
4. Guard trạng thái: chỉ nhận khi `version_status == 'ACTIVE'` và `session.status == 'PLANNED'`, nếu
   không → `422 ROOM_ASSIGNMENT_STATE_INVALID`.
5. `lock_room_ids([room_id])` — advisory lock `pg_advisory_xact_lock` theo namespace `"room"` (xem 3.5).
6. `validate_assignment_batch(...)` với batch 1 phần tử (chi tiết ở 3.4).
7. Nếu `room_id` mới khác `room_id` cũ: `UPDATE sessions.room_id`, đồng bộ luôn
   `schedule_assignments.room_id` (match theo `schedule_version_id` + `group_id` — đây là bản durable
   snapshot dùng khi tạo version PUBLISHED thay thế qua controlled-change), ghi `audit_events`
   (`action='ROOM_ASSIGNED'`).
8. Idempotent: gán lại đúng phòng cũ → `changed: false`, không ghi audit, không update gì.
9. Bắt `IntegrityError` (từ EXCLUDE constraint DB, xem 4) → `409 ROOM_CONFLICT` (lớp bảo vệ thứ 2 sau
   validate ở bước 6, phòng race condition ngoài phạm vi lock).

### 3.3. Gợi ý phòng hàng loạt — `build_room_suggestions` (`POST /rounds/{roundId}/rooms/suggest`)

Route: `apps/api/app/routes/room_assignment.py:205-210`. Logic: `apps/api/app/services/room_assignment.py:311-363`.

1. Lấy toàn bộ session `PLANNED` thuộc version `ACTIVE` của round (kèm `room_id` hiện tại nếu có).
2. Lấy toàn bộ phòng active + đúng room_type cho phép của round (`round_room_types`).
3. Lấy `live` = mọi session đã có `room_id` thuộc **version ACTIVE/PUBLISHED khác round này** (loại trừ
   chính version đang xử lý) — dùng làm occupancy nền cho thuật toán, đảm bảo suggestion không đề xuất
   phòng đang bận ở round khác.
4. Gọi `allocate_room_assignments(sessions, rooms, live)` (thuật toán ở 3.3.1).
5. Trả về suggestion đã enrich `room_code`/`room_type`; **loại bỏ** những session không tìm được phòng
   (`room_id is None` bị filter khỏi kết quả — nghĩa là FE không thấy suggestion cho session đó, không
   có thông báo lỗi tường minh ở tầng suggest).

#### 3.3.1. Thuật toán `allocate_room_assignments` — deterministic greedy theo slot

`apps/api/app/services/room_assignment.py:104-208`. Đây là **thuật toán quyết định — input trực tiếp
cho tính năng config đang thiết kế**.

- Input: `sessions` (đã có `start_at`/`end_at`/`day`/`group_id`, có thể có `room_id` cũ), `rooms`, và
  `occupied` (session đã chiếm phòng từ nơi khác, dùng để seed occupancy — không bị allocator ghi đè).
- Sắp phòng theo `(code, id)` — thứ tự cố định, deterministic.
- Sắp session theo `(start_at, end_at, session_id hoặc group_id)`.
- Xử lý theo **từng cụm session cùng khung giờ** (cùng `start_at`+`end_at` = 1 "slot"). Trong 1 slot,
  duyệt từng session theo thứ tự đã sort:
  - Với mỗi phòng còn trống (không bị session khác trong occupancy hiện tại của phòng đó overlap —
    hàm `_overlaps` so `start_at < other.end_at and other.start_at < left.end_at`), tính rank ưu tiên
    theo tuple (thấp hơn = ưu tiên hơn):
    1. `continuity_rank` = 0 nếu slot trước đó (cùng `day`, `previous_end == start_at` của slot hiện
       tại) đã dùng đúng phòng này, ngược lại 1. → **ưu tiên giữ nguyên phòng liên tục giữa các slot
       kế tiếp nhau trong cùng ngày.**
    2. `current_room_rank` = 0 nếu phòng này chính là `room_id` hiện tại của session (session đã có
       phòng từ trước) → **ưu tiên giữ nguyên phòng đang gán, giảm số lần đổi phòng khi suggest lại.**
    3. `reuse_rank` = 0 nếu phòng đã được allocator này gán cho session khác trước đó trong cùng lần
       chạy → **ưu tiên dùng lại phòng đã "mở" thay vì rải đều ra phòng mới** (giảm số phòng cần dùng).
    4. `len(occupancy[room_id])` — phòng có ít session hơn được ưu tiên hơn (cân bằng tải nhẹ).
    5. `room.code`, `room_id` — tie-break cuối cùng để deterministic tuyệt đối.
  - Chọn `min(choices)` theo tuple trên. Nếu **không có phòng nào trống** cho session → session đó
    được trả về với `room_id: None` (không lỗi, không raise — unassigned âm thầm).
  - Phòng đã chọn trong slot bị loại khỏi ứng viên cho session khác **cùng slot** (`current_room_ids`)
    — đảm bảo 2 session cùng giờ không nhận cùng 1 phòng dù có thể còn "trống" theo occupancy toàn cục
    (occupancy toàn cục chỉ track theo từng phòng riêng, không tự chặn 2 session cùng slot dùng chung
    phòng nếu không có dòng này).
- **Không có khái niệm capacity trong thuật toán này** — phòng được chọn hoàn toàn theo continuity/reuse/
  load, không so `room.capacity` với sĩ số nhóm hay bất kỳ đại lượng nào. `rooms.capacity` được SELECT
  ở một số query khác (vd. `allowed_room`) nhưng giá trị đó không được dùng để so sánh/loại phòng ở bất
  kỳ đâu trong `room_assignment.py` (route lẫn service).
- **Không có khái niệm "loại phòng phù hợp với loại session"** ngoài `round_room_types` (danh sách loại
  phòng round cho phép nói chung) — không phân biệt phòng SEMINAR/LAB có bắt buộc cho loại round nào.

### 3.4. `validate_assignment_batch` — validation dùng chung cho assign đơn lẻ và apply hàng loạt

`apps/api/app/services/room_assignment.py:211-308`. Đây là nơi enforce **mọi ràng buộc hard** trước khi
UPDATE. Không phân biệt caller (single hay batch) — logic giống hệt nhau.

1. Batch rỗng → no-op, trả `[]`.
2. Chuẩn hoá `{session_id, room_id}`; nếu 1 `session_id` xuất hiện > 1 lần trong batch →
   `409 ROOM_SUGGESTION_STALE` ("A session appears more than once in the batch").
3. Lấy version `ACTIVE` hiện tại của round; nếu không có, hoặc khác `active_version_id` truyền vào (so
   sánh optimistic — version đã đổi giữa lúc suggest và lúc apply) → `422 ROOM_ASSIGNMENT_STATE_INVALID`.
4. `SELECT ... FOR UPDATE` toàn bộ session trong batch thuộc đúng version đó. Nếu số dòng trả về khác
   số lượng session yêu cầu (session đã bị xoá/đổi version) → `409 ROOM_SUGGESTION_STALE`.
5. Với từng item:
   - `session.status` phải là `PLANNED`, nếu không → `422 ROOM_ASSIGNMENT_STATE_INVALID`.
   - `allowed_room(db, round_id, room_id)` (room active + room_type nằm trong `round_room_types`):
     - Không tìm thấy row nào phù hợp → phân biệt lỗi cụ thể bằng 1 query bổ sung: room không tồn tại
       → `404 ROOM_NOT_FOUND`; tồn tại nhưng `active=false` → `422 ROOM_INACTIVE`; active nhưng loại
       phòng không nằm trong `round_room_types` → `422 ROOM_TYPE_NOT_ALLOWED`.
6. Sau khi từng item pass check riêng lẻ, so sánh **chéo trong chính batch**: 2 session cùng `room_id`
   và overlap thời gian (`_overlaps`) → `409 ROOM_CONFLICT` với `session_id` của session sau.
7. Với từng item, gọi `find_room_conflict` — kiểm tra **global** (mọi version `ACTIVE`/`PUBLISHED` của
   **mọi round**, không chỉ round hiện tại) có session khác đang chiếm phòng đó overlap thời gian
   không (loại trừ chính session đang xét qua `exclude_session_ids`). Có conflict → `409 ROOM_CONFLICT`
   kèm chi tiết session/round đang chiếm phòng.
8. Trả về danh sách row đã lock (`current_room_id`, `start_at`, `end_at`, `group_id`, ...) cho caller
   dùng tiếp (UPDATE, response payload).

Ghi chú capacity: **không có bước nào trong `validate_assignment_batch` so sánh `room.capacity` với sĩ
số nhóm/hội đồng** — gán phòng 4 chỗ cho hội đồng 6 người vẫn pass validation.

### 3.5. Advisory lock — `lock_room_ids`

`apps/api/app/services/room_assignment.py:31-36`, dùng chung `acquire_resource_locks`
(`apps/api/app/services/resource_locks.py:28-32`).

- Key = SHA-256 của `"scheduler:room:<room_id>"`, cắt 8 byte đầu, ép về signed int8 (range Postgres
  `bigint`) — namespace `"room"` tách biệt với namespace khác (vd `"reviewer"`) để cùng ID số không bao
  giờ đụng lock nhau.
- Lock theo **thứ tự ID đã sort tăng dần** (loại trùng qua `set`) — tránh deadlock khi 2 transaction
  cùng lock nhiều phòng theo thứ tự khác nhau.
- `pg_advisory_xact_lock` — tự giải phóng khi transaction kết thúc (commit/rollback), không cần unlock
  thủ công.
- Được gọi ở: `assign_session_room` (1 phòng), `apply_room_suggestions` (toàn bộ phòng trong batch),
  `validate_publish_room_readiness` (toàn bộ phòng đang được dùng bởi version sắp publish).

### 3.6. Áp dụng suggestion hàng loạt — `apply_room_suggestions` (`POST /rounds/{roundId}/rooms/apply-suggestions`)

`apps/api/app/routes/room_assignment.py:213-269`.

1. `ensure_round_semester_writable`, lock Round `FOR UPDATE`.
2. Lock version `ACTIVE` hiện tại `FOR UPDATE`; không có → `422 ROOM_ASSIGNMENT_STATE_INVALID`.
3. `lock_room_ids` cho **toàn bộ** `room_id` xuất hiện trong payload (kể cả trùng lặp, đã dedupe).
4. `validate_assignment_batch` cho toàn bộ batch, `active_version_id` = version vừa lock (chặn
   TOCTOU giữa lúc FE gọi suggest và lúc gọi apply — nếu version đã đổi, toàn batch bị từ chối).
5. Với từng row đã validate: nếu `current_room_id == room_id` mới → tính là `unchanged`, **skip UPDATE
   và skip audit** (không ghi log cho no-op). Khác → UPDATE `sessions.room_id` +
   `schedule_assignments.room_id` (match theo version+group), tăng `changed`, ghi 1 `audit_events` row
   riêng cho từng session đổi (`action='ROOM_ASSIGNED'`, `after_json` có `batch: true`).
6. Response: `changed_count`, `unchanged_count`, danh sách `{session_id, room_id}` đã validate (bao gồm
   cả phần unchanged).
7. Toàn bộ nằm trong **1 transaction duy nhất** — không có concept "apply từng phần"; 1 session lỗi
   (vd conflict) làm rollback toàn bộ batch, không có phòng nào được gán.

### 3.7. Publish readiness check — `validate_publish_room_readiness`

`apps/api/app/services/room_assignment.py:366-412`. Gọi từ 2 nơi:
- `GET /rounds/{roundId}/publish-readiness` (`target_room_publish.py:121-134`) — **dry-run**, luôn
  `db.rollback()` sau khi kiểm tra (kể cả khi raise), không giữ lock, chỉ để FE hiển thị blocker trước
  khi bấm publish thật.
- `publish_schedule` (`apps/api/app/routes/schedule_operations.py:1791`) — chạy **trong** transaction
  publish thật, lock giữ tới khi commit.

Các bước:
1. Lấy toàn bộ session của version (bất kể status), `LEFT JOIN rooms`, kèm cờ `allowed` (room_type có
   nằm trong `round_room_types` của round không). `FOR UPDATE OF s`.
2. Bất kỳ session nào `room_id IS NULL` → `422 ROOM_INACTIVE` ("Every session must have an active room
   before publishing") — **dùng chung code `ROOM_INACTIVE` cho cả trường hợp "chưa gán phòng" lẫn
   "phòng đã bị inactive"**, không có code riêng kiểu `ROOM_MISSING`.
3. Với từng session đã có `room_id`: `room.active` phải true (nếu room bị xoá/JOIN NULL thì `active` là
   NULL → falsy → cùng lỗi `ROOM_INACTIVE`); `allowed` phải true, nếu không →
   `422 ROOM_TYPE_NOT_ALLOWED`.
4. `lock_room_ids` toàn bộ phòng đang dùng trong version.
5. So sánh chéo trong version: 2 session cùng phòng, overlap giờ → `409 ROOM_CONFLICT`.
6. `find_room_conflict` cho từng session — kiểm tra **global**, loại trừ toàn bộ session thuộc chính
   version đang xét (`exclude_session_ids`) và tuỳ chọn loại trừ `exclude_round_id` (dùng khi replace
   version publish cũ của cùng round, tránh tự đụng chính mình — publish thường không truyền
   `exclude_round_id`, chỉ `readiness` cũng không truyền → mặc định `None`, nghĩa là **không** tự động
   loại trừ version PUBLISHED cũ của cùng round; nếu round có version PUBLISHED cũ đang dùng phòng
   trùng giờ, đây có thể tự conflict với chính lịch cũ của mình cho tới khi version cũ bị `DISCARDED` —
   xem 7).
7. Trả `list[dict]` các row đã kiểm tra; `publish_schedule` gọi hàm này **trước** khi
   `UPDATE schedule_versions SET status='DISCARDED' WHERE ... status='PUBLISHED' AND id <> version_id`
   — tức là lúc readiness-check chạy, version PUBLISHED cũ (nếu có) **vẫn còn** `PUBLISHED` và vẫn nằm
   trong tập global bị `find_room_conflict` xét (không exclude), nên nếu version mới dùng đúng phòng+
   giờ với chính version cũ của cùng round, hàm này **sẽ báo `ROOM_CONFLICT`** — đây là edge case cần
   để ý khi thiết kế lại (xem mục 7).

Sau `validate_publish_room_readiness`, `publish_schedule` còn chạy `validate_schedule` (hard-constraint
solver-side, ngoài phạm vi tài liệu này) trước khi thật sự UPDATE version → `PUBLISHED`.

## 4. Data model / bảng liên quan

| Bảng | Cột liên quan tới room | Ghi chú |
|---|---|---|
| `rooms` | `id`, `code` (UNIQUE), `name`, `capacity` (CHECK `>0`), `active` (bool), `room_type` (enum `NORMAL`\|`SEMINAR`\|`LAB`, thêm ở migration `0020_room_type`) | Định nghĩa gốc: `apps/api/migrations/versions/0002_domain_model.py:89-95`. Không có cột `is_online` trong code hiện tại (khác ERD cũ, xem mục 6). |
| `round_room_types` | `round_id`, `room_type` (composite PK) | Thay thế `round_rooms` (whitelist phòng vật lý) từ migration `0023_round_room_types`. Round chỉ khai báo **loại phòng cho phép**, không khai báo phòng cụ thể. |
| `sessions` | `room_id` (nullable FK → `rooms.id`), `schedule_version_id`, `group_id`, `start_at`, `end_at`, `status`, cột generated `time_range` (`TSTZRANGE`) | Có `EXCLUDE USING gist (schedule_version_id WITH =, room_id WITH =, time_range WITH &&)` — DB tự chặn 2 session **cùng version** dùng cùng phòng overlap giờ. Constraint không đặt tên tường minh trong migration (Postgres tự sinh tên), **không phải** `uq_session_room` như ERD cũ ghi (xem mục 6). Ràng buộc DB này chỉ theo scope `schedule_version_id` — conflict **giữa các version khác nhau** (vd ACTIVE vs PUBLISHED) hoàn toàn dựa vào `find_room_conflict` ở tầng ứng dụng, DB không tự chặn. |
| `schedule_assignments` | `room_id` (nullable FK → `rooms.id`, thêm ở migration `0042_schedule_assignment_rooms`) | Bản snapshot durable song song với `sessions`; mọi UPDATE room ở `sessions` đều UPDATE kèm dòng tương ứng ở đây (match theo `schedule_version_id` + `group_id`). Dùng khi tạo version thay thế qua controlled-change (clone). |
| `schedule_versions` | `status` (`DRAFT`/`ACTIVE`/`PUBLISHED`/`DISCARDED`/...) | Room assignment chỉ thao tác trên version `ACTIVE` (assign/suggest/apply) hoặc version đang publish (readiness). |
| `audit_events` | `action='ROOM_ASSIGNED'` / `'ROOM_UPDATED'`, `entity_type='session'`/`'room'`, `after_json` | Ghi khi đổi phòng thật sự (không ghi cho no-op) và khi PATCH `/rooms/{roomId}`. |

Quan hệ: `rounds (1) —— (N) round_room_types`, `rooms (1) —— (N) sessions`, `schedule_versions (1) ——
(N) sessions`, `sessions (1) —— (1) schedule_assignments` (theo `version_id + group_id`).

## 5. Config / hằng số hiện tại (input cho thiết kế tính năng config thuật toán)

| Tên | Giá trị mặc định / hành vi | Nơi định nghĩa | Configurable qua API/settings? |
|---|---|---|---|
| Danh sách loại phòng cho phép/round | Không có default cứng — set rỗng nếu round chưa khai `round_room_types` (khi đó mọi phòng bị coi là "không allowed", `list_available_rooms` trả rỗng, `validate_assignment_batch` luôn `ROOM_TYPE_NOT_ALLOWED`) | `round_room_types` table, `apps/api/migrations/versions/0023_round_room_types.py` | Có — qua route quản lý round (ngoài phạm vi file này), lưu ở DB, không hardcode trong `room_assignment.py` |
| Room active flag | `rooms.active DEFAULT TRUE` | `apps/api/migrations/versions/0002_domain_model.py:94` | Có — `PATCH /rooms/{roomId}` (`target_room_publish.py:89-113`) |
| Room capacity | `CHECK (capacity > 0)`, không có upper/lower bound nghiệp vụ, **không được đối chiếu với sĩ số nhóm/hội đồng ở bất kỳ đâu trong luồng này** | `apps/api/migrations/versions/0002_domain_model.py:93`; `RoomUpdateTarget.capacity` giới hạn `gt=0, le=500` chỉ ở tầng validate PATCH request (`target_room_publish.py:42`) | `capacity` field có thể sửa qua `PATCH /rooms/{roomId}`, nhưng **không có config nào bật/tắt việc enforce capacity khi assign/suggest/publish** — hardcode "không check" |
| Thứ tự ưu tiên chọn phòng trong `allocate_room_assignments` (continuity → giữ phòng hiện tại → reuse phòng đã mở → ít session nhất → code/id) | Cố định, không có tham số nào thay đổi được thứ tự hay bật/tắt từng tiêu chí | `apps/api/app/services/room_assignment.py:161-192` (tuple rank hardcode trong vòng lặp) | Không — hardcode hoàn toàn trong logic, không đọc từ `rounds.soft_weights` hay bảng config nào |
| Phạm vi "conflict toàn cục" khi tìm phòng đụng độ (`find_room_conflict`) — tính theo mọi `schedule_versions.status IN ('ACTIVE','PUBLISHED')` của **mọi round**, không giới hạn cùng loại round | Cố định `('ACTIVE', 'PUBLISHED')` | `apps/api/app/services/room_assignment.py:81` (literal trong SQL) | Không — hardcode trong câu SQL, không phải tham số |
| Danh sách room_type hợp lệ (enum) | `NORMAL`, `SEMINAR`, `LAB` | DB enum `room_type`, tạo ở `apps/api/migrations/versions/0020_room_type.py:12`; lặp lại dạng `Literal[...]` ở route (`room_assignment.py:101-103`, `target_room_publish.py:44,58`) | Không — cố định enum DB, đổi phải chạy migration mới (thêm giá trị enum) |
| Advisory-lock namespace `"room"` | Chuỗi literal `"room"` | `apps/api/app/services/room_assignment.py:36` (`lock_room_ids`) gọi `acquire_resource_locks(db, "room", ...)` | Không — hardcode |
| `RoomUpdateTarget.code` max_length | 32 | `target_room_publish.py:40` | Không (Pydantic field constraint, không phải setting) |
| `RoomUpdateTarget.name` max_length | 160 | `target_room_publish.py:41` | Không |
| Không có setting nào trong `apps/api/app/config.py` liên quan tới room/capacity/room_type — đã grep xác nhận không có biến nào khớp `room`/`capacity` trong file này. | — | `apps/api/app/config.py` | N/A |

**Tổng kết cho việc thiết kế config:** toàn bộ "thuật toán" gán phòng hiện nay là 1 hàm greedy
deterministic không tham số hoá (`allocate_room_assignments`), không đọc bất kỳ config nào từ
`rounds` (kể cả `soft_weights` JSONB đã có sẵn cho soft constraint của solver Time+Council — room
assignment **không** dùng field này) hay bảng settings riêng. Capacity tồn tại trong schema nhưng
hoàn toàn không được dùng trong logic gán/validate/publish của luồng này.

## 6. Đối chiếu tài liệu cũ

| Doc | Trạng thái | Ghi chú cụ thể |
|---|---|---|
| `docs/api/scheduling.md` §4 "Room Assignment" | Đúng | Mô tả đúng 4 route, đúng hành vi "conflict toàn cục", đúng việc round chỉ lưu `room_types` (không lưu whitelist phòng vật lý). Không đề cập `PATCH /rooms/{roomId}` hay `publish-readiness`/`actions/publish` (2 route đó nằm ở `target_room_publish.py`, không cùng file/section — không phải lỗi, chỉ là chưa gộp). |
| `docs/api/scheduling.md` §9 "Room và H3 trong giai đoạn draft" | Đúng | Khớp code: session chưa có `room_id` không vi phạm H3; H3 chỉ áp dụng khi cả 2 session cùng gán 1 room cụ thể. |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` — bảng `rooms` "Có `is_online` cho buổi trên MS Teams" | Lỗi thời | Cột `is_online` **không tồn tại** trong `rooms` (migration 0002 chỉ có `id, code, name, capacity, active`, + `room_type` thêm sau ở 0020). Không có logic online/offline nào trong `room_assignment.py`. |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` §3.3 bảng `round_rooms` "Phòng khả dụng cho đợt" | Lỗi thời | Bảng `round_rooms` đã bị **drop** ở migration `0023_round_room_types`, thay bằng `round_room_types` (round chỉ chọn loại phòng, không chọn phòng cụ thể). Doc ERD chưa cập nhật theo migration này. |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` — sơ đồ phân cấp "Session (slot, room, group)" | Một phần đúng | Đúng ở mức khái niệm (session có room), nhưng gợi ý room được gán cùng lúc với slot lúc solver chạy — thực tế room luôn `NULL` lúc materialize, gán riêng ở bước sau (đúng như `scheduling.md` §9 đã nói, ERD không nói rõ điều này). |
| `docs/project-reference/BusinessRules_CapstoneScheduler_v1.0.md` §5 "H3 — phòng không trùng khung giờ" → cơ chế `uq_session_room` | Một phần đúng | H3 đúng là được enforce ở tầng DB, nhưng tên constraint thực tế không phải `uq_session_room` — đó là 1 `EXCLUDE USING gist` không đặt tên tường minh trong migration 0002 (dòng 239-243), Postgres tự sinh tên. Constraint cũng chỉ scope trong 1 `schedule_version_id`, không phải global; phần global dựa vào `find_room_conflict` ở app layer — doc không nhắc phần app-layer này. |
| `docs/be-checklist-open-questions.md` (mục A4, phòng/room CRUD FE-BE alias `type`/`status` ↔ `room_type`/`active`) | Đúng | Khớp code: comment trong `response_models.py:298-299` trích dẫn đúng file/mục này; `RoomResponse._fill_fe_contract_aliases` implement đúng như checklist mô tả. |
| Không tìm thấy doc nào khác mô tả riêng luồng room-assignment post-activation (các doc khác match từ khoá "room" đều thuộc phạm vi manual-scheduling, admin room CRUD FE handoff, hoặc round config — không chồng lấn nội dung tài liệu này). | Không đề cập | — |

## 7. Giới hạn / edge case quan sát được trong code hiện tại

- **Không enforce capacity**: gán phòng sức chứa nhỏ hơn số lượng người/nhóm cần chứa vẫn hợp lệ ở mọi
  bước (suggest, validate, publish-readiness).
- **Publish có thể tự conflict với version PUBLISHED cũ của cùng round**: `validate_publish_room_readiness`
  không tự động `exclude_round_id` khi gọi từ `publish_schedule`, và version cũ vẫn `PUBLISHED` (chưa bị
  `DISCARDED`) tại thời điểm check — xem mục 3.7 bước 7.
- **`build_room_suggestions` âm thầm bỏ qua session không tìm được phòng** (`room_id: None` bị filter
  khỏi response) — không có cách nào từ response biết được session nào bị thiếu phòng do hết phòng
  trống trong slot đó; phải tự so sánh số session PLANNED với số suggestion trả về.
- **`list_available_rooms` không filter theo `timeslotId` thì không loại phòng đang bận** — field
  `available` trên response luôn `true` mặc định, không phản ánh occupancy thật khi không truyền
  `timeslotId`.
- **2 bản route trùng path** giữa `room_assignment.py` và `target_room_publish.py` (route tái export) —
  tồn tại đồng thời trong router, hành vi phụ thuộc thứ tự include ở `main.py` (không audit trong tài
  liệu này).
- **Round chưa khai `round_room_types`** → mọi request assign/suggest/apply cho round đó luôn thất bại
  (`ROOM_TYPE_NOT_ALLOWED` hoặc suggest trả rỗng) — không có thông báo riêng "round chưa cấu hình loại
  phòng", lỗi trông giống như phòng cụ thể sai loại.
- **`ROOM_INACTIVE` dùng chung cho 2 tình huống khác nhau** ở publish-readiness: "chưa gán phòng" và
  "phòng đã bị inactive" — FE phải tự phân biệt qua có/không có `room_id` trong `details`.
