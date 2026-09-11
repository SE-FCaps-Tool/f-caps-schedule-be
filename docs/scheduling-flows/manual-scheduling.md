# Manual Scheduling — luồng xếp lịch thủ công

Phạm vi tài liệu: chỉ route `apps/api/app/routes/manual_scheduling.py` (1758 dòng) — board xếp tay,
tạo/sửa/xóa session thủ công, validate, publish. Không cover thuật toán auto-scheduling (solver
Time+Council ở `schedule_operations.py`), luồng gán phòng post-activation (`room_assignment.py`, xem
`docs/scheduling-flows/room-assignment.md`), hay council flow (`services/councils.py`) — chỉ nêu điểm
gọi vào các module đó, không mô tả lại chi tiết logic bên trong.

## 1. Tổng quan luồng

- **Mục đích:** cho Manager/Admin tự tay xếp lịch hội đồng (nhóm × timeslot × phòng × reviewer) trên
  một **workspace nháp riêng** (`manual_schedule_sessions`), độc lập hoàn toàn với bảng `sessions` /
  `schedule_versions` dùng cho auto-scheduling. Đây không phải "sửa kết quả thuật toán" — manual
  scheduling có bộ bảng, revision, và luồng publish riêng; nó chỉ *đọc* `schedule_versions` khi Manager
  muốn copy một bản thuật toán đã chạy vào làm điểm khởi đầu (`sourceVersionId`,
  `bulk-upsert.sourceVersionId`, dòng 1425-1446), không mutate ngược lại version đó.
- **Khi nào dùng:** bất kỳ lúc nào round đang ở 1 trong 11 status hợp lệ để sửa nháp (mọi status —
  xem `EDITABLE_ROUND_STATUSES` mục 5), kể cả sau khi round đã `PUBLISHED`. Đây là điểm khác biệt lớn
  với auto-scheduling: publish một bản manual mới **không đụng** tới `sessions`/`schedule_versions` cũ
  cho tới khi Manager bấm "Công bố lịch" (`POST .../publish`) — lúc đó mới tạo `schedule_versions` mới
  và archive version cũ (`status='DISCARDED'`).
- **Ai trigger:** chỉ `ADMIN`/`MANAGER` (`_require_manager`, dòng 74-76, 403 `AUTH_FORBIDDEN` cho role
  khác). Không có concept "student/lecturer xem trước" — toàn bộ 9 endpoint đều yêu cầu manager.
- **Khác gì với auto-scheduling:** auto-scheduling chạy solver ghi thẳng `schedule_versions` (nhiều
  version `DRAFT` song song, Manager chọn 1 để `activate`). Manual scheduling không có khái niệm nhiều
  version song song ở tầng nháp — chỉ có **một** draft workspace duy nhất mỗi round
  (`manual_schedule_drafts` PK là `round_id`), tăng dần `revision` sau mỗi lần sửa (optimistic lock).
  Publish thủ công tạo **một** `schedule_versions` mới với `solver_status='MANUAL'` để phân biệt với
  version do solver sinh ra.

## 2. Entry points

Tất cả prefix `/api/v1`, file `apps/api/app/routes/manual_scheduling.py`, wrap `success_payload`.

### 2.1. Xem board / lấy danh sách ứng viên

| Method + Path | Handler | File:line |
|---|---|---|
| `GET /rounds/{roundId}/manual-schedule` | `get_manual_schedule` | :1093-1096 |
| `GET /rounds/{roundId}/manual-schedule/options` | `manual_schedule_options` | :1099-1144 |

### 2.2. Tạo / sửa / xóa session thủ công

| Method + Path | Handler | File:line |
|---|---|---|
| `POST /rounds/{roundId}/manual-schedule/sessions` | `create_manual_session` | :1381-1407 |
| `POST /rounds/{roundId}/manual-schedule/sessions/bulk-upsert` | `bulk_upsert_manual_sessions` | :1410-1469 |
| `PATCH /rounds/{roundId}/manual-schedule/sessions/{sessionId}` | `update_manual_session` | :1472-1500 |
| `DELETE /rounds/{roundId}/manual-schedule/sessions/{sessionId}` | `delete_manual_session` | :1503-1534 |

### 2.3. Validate / publish

| Method + Path | Handler | File:line |
|---|---|---|
| `POST /rounds/{roundId}/manual-schedule/validate` | `validate_manual_schedule` | :1537-1555 |
| `GET /rounds/{roundId}/manual-schedule/publish-readiness` | `manual_publish_readiness` | :1558-1597 |
| `POST /rounds/{roundId}/manual-schedule/publish` | `publish_manual_schedule` | :1600-1758 |

Module dùng chung không phải route, gọi từ nhiều handler ở trên:

- `_board_payload` (:1062-1090) — build response chuẩn cho GET board, dùng lại sau mọi mutation
  (create/update/delete/bulk-upsert đều trả `_board_payload` mới hoặc session vừa upsert lấy từ đó).
- `_validate_manual` (:715-914) + `_validate_against_database` (:917-1005) — engine validate dùng
  chung cho GET board, `/validate`, `/publish-readiness`, `/publish`.
- Gọi ra ngoài phạm vi file này: `create_council` (`app/services/councils.py:57`, chỉ gọi ở bước
  publish để tạo hội đồng chính thức), `_actor_id` (`app/routes/schedule_operations.py:128`, resolve
  account thực hiện hành động), `ensure_round_semester_writable`
  (`app/services/semester_queries.py:35`, khóa học kỳ cha + chặn ghi nếu semester đã archived — gọi ở
  đầu mọi transaction ghi).

## 3. Business logic từng bước

### 3.1. Cơ chế draft workspace + revision (optimistic lock)

- Mỗi round có tối đa 1 dòng `manual_schedule_drafts` (PK `round_id`). `_ensure_draft_row` (:230-241)
  dùng `INSERT ... ON CONFLICT (round_id) DO UPDATE SET updated_at = manual_schedule_drafts.updated_at`
  — upsert vô hại (no-op update nếu đã tồn tại) chỉ để đảm bảo dòng tồn tại và lấy `revision` hiện tại.
  Chỉ được gọi trong các handler **ghi** (create/update/delete/bulk-upsert/publish); `GET` board không
  tạo dòng draft — nếu round chưa từng sửa tay, `_load_revision` (:543-549) trả `0` qua `COALESCE`
  dù chưa có dòng nào trong bảng.
- Mọi mutation phải gửi `clientRevision`; `_check_revision` (:244-258) `SELECT ... FOR UPDATE` khóa
  dòng draft rồi so `client_revision` với `revision` hiện tại — lệch thì `409
  STALE_MANUAL_SCHEDULE_REVISION` kèm `currentRevision`. `clientRevision = null` bỏ qua check (ghi đè
  không điều kiện — dùng cho lần ghi đầu tiên khi FE chưa có revision nào).
- `_bump_revision` (:261-271) tăng `revision + 1` sau mỗi create/update/delete/bulk-upsert **thành
  công** (nằm trong cùng transaction, trước khi audit event và trước khi trả response).
  `/validate` **không** bump revision (chỉ đọc, có `db.rollback()` tường minh ở cuối — dòng 1554 — để
  chắc chắn không side-effect dù không ghi gì).

### 3.2. Resolve timeslot & group-selection-mode gate

- `_timeslot_id_for` (:274-315) nhận `roundTimeslotId` ở 2 dạng: id thật (`ts_123`/`123`) hoặc alias
  `slot_HHMM` (regex `slot_(\d{4})`, cần kèm `date` để resolve đúng ngày qua join `round_days`). Luôn
  xác nhận timeslot thuộc đúng round và `timeslots.active = TRUE`; nếu request có `date` thì đối chiếu
  luôn ngày của timeslot khớp `date` gửi lên (`TIMESLOT_NOT_IN_ROUND` nếu lệch).
- `_ensure_registered_timeslot` (:448-495) chỉ chạy khi `rounds.group_selection_mode = TRUE`. Với
  từng `group_id` trong payload, lấy tập timeslot nhóm đó đã `selected = TRUE` trong
  `group_slot_preferences`; nếu timeslot đang gán **không** nằm trong tập đó → `422
  GROUP_SLOT_NOT_SELECTED`. **Edge case:** nhóm hoàn toàn chưa có dòng preference nào (chưa từng chọn
  slot) thì không có trong `selected_by_group` → vòng lặp validate bỏ qua nhóm đó hoàn toàn, không
  chặn (xem thêm mục 7).

### 3.3. Tạo / sửa 1 session — `_upsert_session` (:498-540)

1. Resolve `timeslot_id` (3.2) + gate group-selection-mode.
2. Parse `room_id` qua `_parse_positive_id` (:101-105) — **chỉ parse định dạng id, không query DB**
   kiểm tra phòng có tồn tại/active hay không ở bước này (việc đó dồn qua `/validate` hoặc `/publish`).
3. Nếu tạo mới: `INSERT manual_schedule_sessions` với `status='DRAFT'` cố định.
4. Nếu sửa: `UPDATE ... status='DRAFT'` — **luôn reset về DRAFT** kể cả khi session đang
   `status='PUBLISHED'` (đã từng công bố ở lần publish trước) — sửa tay sau khi publish sẽ "hạ cấp"
   session đó về DRAFT cho tới lần publish kế tiếp. `updated`is `NULL` (id không tồn tại/không thuộc
   round) → `404 SESSION_NOT_FOUND`.
5. `_replace_session_children` (:416-445) — xóa sạch rồi insert lại toàn bộ
   `manual_schedule_session_groups` (dedupe theo `group_id`, giữ thứ tự `position` theo payload) và
   `manual_schedule_session_reviewers` (qua `_normalize_reviewers`).
6. `_normalize_reviewers` (:367-413) — validate **chặn ngay** (không đợi tới `/validate`): role phải
   thuộc `_role_schema(reviewer_count)` của round (`ROLE_STRUCTURE_INVALID` nếu role lạ), 1 lecturer
   không được giữ 2 role (`LECTURER_MULTI_ROLE`), 1 role không được gán 2 lecturer
   (`ROLE_STRUCTURE_INVALID`). Không check double-booking, availability, COI, GVHD ở bước này — dồn
   qua validate/publish (xem 3.10).
7. Handler `create_manual_session`/`update_manual_session` bọc toàn bộ trong 1 transaction: lock round
   `FOR UPDATE` (`_round_or_404(..., for_update=True)`), `_ensure_mutable_round` (chặn nếu status không
   nằm trong `EDITABLE_ROUND_STATUSES` — nhưng set này là **toàn bộ** 11 status nên trên thực tế không
   bao giờ chặn, xem mục 7), ghi `audit_events` (`MANUAL_SESSION_CREATED`/`MANUAL_SESSION_UPDATED`),
   trả `_board_payload` mới rồi tự tìm lại session vừa ghi trong đó để trả riêng (`next(...)` — nếu vì
   lý do nào đó không tìm thấy sẽ raise `StopIteration` không bắt, 500 — xem mục 7).

### 3.4. Bulk upsert — `bulk_upsert_manual_sessions` (:1410-1469)

1. Nếu payload có `sourceVersionId`: xác nhận `schedule_versions` đó tồn tại và thuộc đúng round
   (`404 VERSION_NOT_FOUND` / `422 VERSION_ROUND_MISMATCH`), rồi chỉ **ghi lại con trỏ**
   `manual_schedule_drafts.source_schedule_version_id` — **không** tự động copy session từ version đó
   vào `manual_schedule_sessions`; việc "copy" là FE tự đọc version rồi gửi từng session qua field
   `sessions[]` của cùng request.
2. Xóa các `deletedSessionIds` (nếu có).
3. Upsert từng phần tử `sessions[]` qua `_upsert_session` (không điều kiện gì khác 3.3).
4. Bump revision 1 lần cho cả batch, ghi 1 `audit_events` (`MANUAL_SESSION_BULK_UPSERTED`) tổng hợp
   danh sách id đã upsert/xóa.
5. **Không có bước validate blocker nào trước khi ghi** — khác hẳn mô tả trong
   `docs/manual-scheduling-business-contract.md` §7 (xem mục 6). Field `allowDraftIncomplete` được
   khai báo trong `BulkUpsertPayload` (:351) nhưng **không được đọc ở bất kỳ đâu** trong handler — bulk
   upsert luôn ghi mọi session dạng DRAFT bất kể có blocker hay thiếu dữ liệu, tương đương
   `allowDraftIncomplete=true` vĩnh viễn.

### 3.5. Xóa session — `delete_manual_session` (:1503-1534)

Xóa thẳng dòng `manual_schedule_sessions` theo `id` + `round_id` (CASCADE xóa luôn
`manual_schedule_session_groups`/`_reviewers`). Không phân biệt session đang `DRAFT` hay `PUBLISHED` —
xóa được cả session đã từng nằm trong lần publish trước (không đụng `sessions`/`schedule_versions` đã
publish, chỉ xóa bản nháp). `clientRevision` truyền qua query string (`?clientRevision=`), không phải
body.

### 3.6. Options — danh sách ứng viên có `blockedCodes` — `_options_payload` (:1147-1211)

Không filter cứng (loại hẳn item không đủ điều kiện) — trả **toàn bộ** group/lecturer/room khớp
`search`, mỗi item kèm `available` + `blockedCodes[]` + `blockedReason` (tiếng Việt, ghép qua
`_blocked_reason`/`BLOCKED_REASON_LABELS`, :68-71, :43-65) để FE tự quyết định disable hay vẫn cho
chọn. Phân trang (`page`/`pageSize`) cắt **sau khi** đã tính đủ blocked cho toàn bộ danh sách
(:1140-1144) — không phân trang ở tầng SQL.

- `_group_options` (:1214-1268): loại theo `GROUP_DUPLICATED` (đã nằm session khác, trừ session đang
  sửa qua `sessionId`), `GROUP_NOT_ELIGIBLE` (`_eligible_group_status`, theo `round_type` + trạng thái
  nhóm), `GROUP_SLOT_NOT_SELECTED` (chỉ khi `group_selection_mode` bật và có `timeslotId`),
  `SUPERVISOR_REVIEW_CONFLICT` (GVHD trùng `selected_reviewer_ids` đang chọn),
  `LECTURER_CONFLICT_OF_INTEREST` (so `conflict_declarations` với project của nhóm).
- `_lecturer_options` (:1271-1338): `LECTURER_NOT_ACCEPTED` (invitation != ACCEPTED),
  `LECTURER_NOT_AVAILABLE` (không có dòng `lecturer_availabilities` state=AVAILABLE ở timeslot),
  `LECTURER_DOUBLE_BOOKED` (đã ở session khác cùng timeslot), `SUPERVISOR_REVIEW_CONFLICT` (đang là
  GVHD của 1 trong các group đã chọn), `LECTURER_CONFLICT_OF_INTEREST`, `PREVIOUS_REVIEWER_REQUIRED`
  (D1.2 — nhóm cần ít nhất 1 reviewer cũ mà GV này chưa nằm trong tập reviewer cũ),
  `ROLE_STRUCTURE_INVALID` (query có `role` nhưng role đó không thuộc schema round).
- `_room_options` (:1341-1378): `ROOM_NOT_ACTIVE`, `ROOM_TYPE_NOT_ALLOWED` (không thuộc
  `round_room_types`), `ROOM_DOUBLE_BOOKED` (đã dùng ở session khác cùng timeslot, trừ chính
  `roomId` đang giữ).

### 3.7. Validate draft — `_validate_manual` (:715-914)

Chạy trên **toàn bộ** session hiện có trong DB của round (không phải chỉ session client gửi lên) —
`_load_manual_sessions` (:552-663) load lại từ DB mỗi lần gọi. Hai nhóm check:

**Check thuần trong-draft** (không cần query thêm ngoài mấy bảng đã load), tất cả block publish:

- `SESSION_INCOMPLETE`: thiếu group, thiếu room, hoặc số reviewer != `reviewerCount`.
- `ROLE_STRUCTURE_INVALID`: tập role thực tế khác tập role kỳ vọng của round (chỉ check khi
  `role_keys` không rỗng — session thiếu reviewer hoàn toàn không bị gắn lỗi này thêm lần nữa).
- `LECTURER_MULTI_ROLE`: trùng lecturer trong cùng session (double-check, dù `_normalize_reviewers` đã
  chặn lúc ghi — phòng trường hợp dữ liệu cũ).
- `SUPERVISOR_REVIEW_CONFLICT`: GVHD của group nằm trong tập reviewer của session đó.
- `GROUP_DUPLICATED`: 1 group xuất hiện ở > 1 session trong draft.
- `SESSION_LIMIT_EXCEEDED`: số session cùng `timeslot_id` vượt `max_groups_per_timeslot` (bỏ qua nếu
  `null`).
- `ROOM_DOUBLE_BOOKED` / `LECTURER_DOUBLE_BOOKED`: cùng room/lecturer ở ≥2 session cùng `timeslot_id`.
- `LECTURER_LOAD_EXCEEDED`: tổng phút hoặc tổng số phiên của 1 lecturer trong 1 buổi (AM/PM, chia theo
  giờ bắt đầu < 13h hay không) hoặc 1 ngày, so với `max_minutes_per_part`/`max_minutes_per_day` nếu
  round có set, **fallback** sang đếm số phiên (`h12_sessions_per_part`/`h12_sessions_per_day`) nếu
  round không set minutes limit (chi tiết công thức ở mục 5).
- `UNSCHEDULED_GROUPS`: group thuộc `round_groups` nhưng chưa nằm trong session nào (blocker mức
  round, không gắn `sessionId`).

**Check đối chiếu DB ngoài** — `_validate_against_database` (:917-1005), gọi từ giữa
`_validate_manual` (dòng 849):

- `ROOM_NOT_FOUND` / `ROOM_NOT_ACTIVE` / `ROOM_TYPE_NOT_ALLOWED`.
- `LECTURER_NOT_ACCEPTED` / `LECTURER_NOT_AVAILABLE`.
- `GROUP_NOT_ELIGIBLE`: group không thuộc `round_groups` **hoặc** `project_id IS NULL` — **không**
  check `project.status` (xem mục 6, gap so với field `config.eligibleProjectStatuses`).
- `GROUP_SLOT_NOT_SELECTED`: chỉ chạy khi `group_selection_mode` bật **và** `group_slots` (toàn bộ
  preference đã `selected=TRUE` của round) không rỗng — round bật mode nhưng chưa ai chọn preference gì
  thì check này im lặng bỏ qua toàn bộ (cùng lỗ hổng như 3.2).
- `LECTURER_CONFLICT_OF_INTEREST`: so `conflict_declarations` (bảng global, không filter theo round).
- `PREVIOUS_REVIEWER_REQUIRED`: chỉ áp dụng round type thuộc `DEFENSE_1_2_TYPES`
  (`{"DEFENSE_1_2","DEFENSE_1"}`). `_prior_reviewers_for_groups` (:1012-1042) tìm **bất kỳ**
  council_member nào đã chấm group đó ở round `DEFENSE_1_1_TYPES` (`{"DEFENSE_1_1","REVIEW_3"}`) cùng
  semester, version `ACTIVE`/`PUBLISHED` — chỉ cần **1 người bất kỳ** trong reviewer set cũ xuất hiện
  lại, **không** bắt buộc đúng người giữ vai Chủ tịch như mô tả ở
  `BusinessRules_CapstoneScheduler_v1.0.md` (xem mục 6). Có thể waive theo từng group qua bảng
  `h11_waivers` (`active=TRUE` — cột `reason` tồn tại trong bảng nhưng route quản lý waiver không nằm
  trong file này, không audit ở đây).

Kết quả trả `blockers[]`, `warnings[]` (gồm cả `H14_ROLE_SKILL_NOT_CONFIGURED`/
`H15_SUPERVISOR_RATIO_NOT_CONFIGURED` — cảnh báo cố định vì 2 rule này chưa có dữ liệu nguồn, xem mục
5), `summary` (đếm eligible/scheduled/unscheduled group, session, blocker, warning) và
`sessionBlockers` (map theo `sessionId`, dùng để decorate response board, không trả trực tiếp qua
`/validate` — dòng 1555 loại field này khỏi response).

### 3.8. `_decorate_sessions_with_validation` (:1045-1059)

Gắn `blockers`/`warnings` theo từng session vào response GET board, và tính lại `status` **chỉ trong
bộ nhớ** (không ghi lại DB): session chưa `PUBLISHED` thì `READY` nếu đủ group+room+không blocker,
ngược lại `DRAFT`. Xem mục 7 — DB column `status` trên thực tế chỉ từng nhận `DRAFT`/`PUBLISHED`, giá
trị `READY` chưa bao giờ được `UPDATE` vào bảng dù CHECK constraint cho phép.

### 3.9. Publish — `publish_manual_schedule` (:1600-1758)

Toàn bộ trong 1 transaction, lock round `FOR UPDATE`:

1. `_ensure_publishable_round` — chặn nếu status ngoài `PUBLISHABLE_ROUND_STATUSES` (6 status, mục 5).
2. `_check_revision` — chặn nếu `clientRevision` stale.
3. Load lại toàn bộ session từ DB, chạy `_validate_manual` — còn `blockers[]` thì `422 PUBLISH_BLOCKED`
   kèm danh sách blocker, **không ghi gì**. `payload.confirmWarnings` được nhận nhưng **không đọc ở
   đâu cả** trong hàm này — không có cơ chế thực sự chặn publish vì warning chưa confirm (khớp với ghi
   chú "hiện chưa có warning nào cần confirm" ở `docs/api/manual-scheduling-fe-handoff.md` §14).
4. Tính `version_no` kế tiếp (`MAX(version_no)+1` theo round), `INSERT schedule_versions` mới với
   `status='PUBLISHED'`, `solver_status='MANUAL'`, `algorithm_parameters={"mode":"MANUAL","reason":
   payload.reason}`, `input_snapshot` = toàn bộ session đã publish (qua `_public_sessions`, lược field
   nội bộ `_*`).
5. `UPDATE schedule_versions SET status='DISCARDED' WHERE round_id=... AND status IN ('ACTIVE',
   'PUBLISHED') AND id <> version_id` — archive **mọi** version active/published khác của round (kể cả
   version do solver sinh ra), không chỉ version manual trước đó.
6. Với từng manual session: `create_council(...)` tạo hội đồng chính thức (`assignment` luôn hardcode
   `"REVIEWER"` cho mọi role kể cả CHAIR/SECRETARY — enum `council_members.assignment` chưa có giá trị
   riêng cho các role đó, xem `docs/api/manual-scheduling-fe-handoff.md` §14; `is_result_owner` luôn
   `False`), rồi `INSERT sessions` (lấy group đầu tiên trong `groups[]` làm `group_id` chính,
   `status='SCHEDULED'`), `INSERT session_groups` cho **mọi** group theo `position`, `INSERT
   schedule_assignments` + `schedule_assignment_reviewers` cho mỗi group (bản snapshot durable song
   song, giống cơ chế `room_assignment.py` dùng khi đổi phòng). Cuối cùng
   `UPDATE manual_schedule_sessions SET status='PUBLISHED', published_session_id=...` cho dòng nháp
   tương ứng.
7. `UPDATE rounds SET status='PUBLISHED'` — set **không điều kiện** cho mọi round publish thủ công
   thành công, bất kể status trước đó là gì trong 6 status cho phép publish.
8. `UPDATE manual_schedule_drafts SET published_schedule_version_id=...`, ghi `audit_events`
   (`MANUAL_SCHEDULE_PUBLISHED`, `entity_type='schedule_version'`).
9. Trả `roundId`, `versionId`, `status='PUBLISHED'`, `publishedAt` (giờ VN, `datetime.now(VN_TZ)`),
   `publishedBy`, `summary` (từ `validation` — **là kết quả `_validate_manual` gọi ở bước 3, trước khi
   dữ liệu round đổi status** — có thể lệch nhẹ với state sau khi round vừa chuyển `PUBLISHED`, nhưng
   không ảnh hưởng số liệu vì `summary` chỉ đếm group/session không phụ thuộc `round.status`).

### 3.10. Write-time vs validate-time enforcement — điểm kiến trúc quan trọng

Ghi (`POST`/`PATCH`/`bulk-upsert`) chỉ chặn các lỗi **cấu trúc** (timeslot hợp lệ, group đã đăng ký
đúng slot nếu bật mode, role hợp lệ, không trùng lecturer/role trong cùng session) — **không** chặn
double-booking phòng/GV, GVHD trùng, COI, thiếu reviewer trước đó (H11), quá tải GV, hay group đã nằm
session khác. Toàn bộ nhóm rule "cross-session"/"cross-DB" đó chỉ được tính lại (không chặn ghi) ở GET
board (hiển thị `blockers`/`status`) và chỉ **thực sự chặn** ở `/validate` (không ghi) và `/publish`
(ghi có điều kiện). Nghĩa là Manager có thể lưu draft ở trạng thái "vi phạm" tùy ý trong lúc thao tác,
UI chỉ cảnh báo qua GET board realtime; chỉ publish mới bị chặn cứng.

### 3.11. Timezone & derived field

Giờ hiển thị (`startTime`/`endTime`, `publishedAt`) convert qua `VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")`
hardcode (:36). Buổi AM/PM để tính `LECTURER_LOAD_EXCEEDED` theo giờ local VN
(`start_at.astimezone(VN_TZ).hour < 13` → AM, dòng 768).

## 4. Data model / bảng liên quan

| Bảng | Cột quan trọng | Ghi chú |
|---|---|---|
| `manual_schedule_drafts` | `round_id` (PK, FK→`rounds`), `revision` (CHECK ≥0), `created_by`/`updated_by`, `source_schedule_version_id` (FK→`schedule_versions`, nullable), `published_schedule_version_id` (FK→`schedule_versions`, nullable) | 1 dòng/round. Migration `0039_manual_scheduling.py`; cột `source_schedule_version_id` thêm sau ở `0043_manual_schedule_source_version.py`. |
| `manual_schedule_sessions` | `id`, `round_id` (FK→`manual_schedule_drafts.round_id` CASCADE), `timeslot_id` (FK→`timeslots`), `room_id` (FK→`rooms`, nullable), `status` (CHECK `DRAFT`\|`READY`\|`PUBLISHED`, **`READY` chưa từng được ghi bởi code hiện tại** — xem mục 7), `published_session_id` (FK→`sessions`, nullable) | Index `(round_id, timeslot_id)`. Đây là "1 hội đồng" trong UI xếp tay. |
| `manual_schedule_session_groups` | `session_id` (FK CASCADE), `group_id` (FK→`groups`), `position` (CHECK >0, UNIQUE theo `session_id`) | Composite PK `(session_id, group_id)` — 1 group không trùng vị trí trong 1 session, nhưng không có UNIQUE ngăn 1 group nằm ở 2 session khác nhau (check đó nằm ở tầng `_validate_manual`, không phải DB constraint). |
| `manual_schedule_session_reviewers` | `session_id` (FK CASCADE), `lecturer_id` (FK→`lecturers`), `role_key`, `role_order` (CHECK >0), `snapshot_name` | Composite PK `(session_id, lecturer_id)` + UNIQUE `(session_id, role_key)` + UNIQUE `(session_id, role_order)` — DB tự chặn trùng role/order trong 1 session, không chặn 1 lecturer giữ 2 session khác nhau. |
| `session_groups` | `session_id` (FK→`sessions` CASCADE), `group_id`, `position` | Tạo cùng migration `0039` — bảng phía **live** (đối xứng với `manual_schedule_session_groups`), cho phép 1 session live chứa nhiều group sau khi publish thủ công. |
| `schedule_versions` (ghi ở publish, không sở hữu bởi file này) | `round_id`, `version_no`, `status`, `solver_status='MANUAL'`, `algorithm_parameters`, `input_snapshot`, `created_by`, `activated_at` | 1 dòng mới mỗi lần publish thủ công thành công. |
| `sessions` / `schedule_assignments` / `schedule_assignment_reviewers` (ghi ở publish) | xem mục 3.9 bước 6 | Bảng live dùng chung với auto-scheduling — không mô tả lại chi tiết ở đây (thuộc phạm vi `schedule_operations.py`). |
| `audit_events` | `actor_id`, `action`, `entity_type`, `entity_id`, `after_json`, `reason` (chỉ publish có `reason`) | Action ghi từ file này: `MANUAL_SESSION_CREATED`, `MANUAL_SESSION_UPDATED`, `MANUAL_SESSION_DELETED`, `MANUAL_SESSION_BULK_UPSERTED`, `MANUAL_SCHEDULE_PUBLISHED`. |

Bảng chỉ **đọc** (nguồn dữ liệu cho options/validate, không sở hữu bởi manual scheduling):
`rounds` (config, mục 5), `round_groups` (group đủ điều kiện của round), `group_slot_preferences`
(preference slot của nhóm khi `group_selection_mode` bật), `round_invitations` (trạng thái mời GV),
`lecturer_availabilities` (GV rảnh giờ nào), `conflict_declarations` (COI GV↔project, bảng global),
`h11_waivers` (miễn H11 theo group), `project_supervisors` (GVHD theo project), `timeslots` +
`round_days` (lịch ngày/giờ round), `rooms` + `round_room_types` (phòng & loại phòng cho phép),
`groups` + `group_memberships` (leader/member để hiển thị).

Quan hệ chính: `rounds (1) —— (1) manual_schedule_drafts` —— `(N) manual_schedule_sessions` ——
`(N) manual_schedule_session_groups` / `(N) manual_schedule_session_reviewers`. Publish tạo nhánh song
song `schedule_versions (1) —— (N) sessions —— (N) session_groups`.

## 5. Config / hằng số hiện đang hardcode hoặc configurable

| Tên | Giá trị mặc định / hành vi | Nơi định nghĩa | Configurable qua API/settings? |
|---|---|---|---|
| `reviewer_count` (số reviewer/hội đồng) | Cột round, `DEFAULT 2`, dùng derive role schema (2→REVIEWER_1/2, ≥3→CHAIR/SECRETARY/MEMBER_n) | `apps/api/migrations/versions/0002_domain_model.py:140`; schema hardcode ở `manual_scheduling.py:108-122` | Có — round-level column, sửa qua route quản lý round (ngoài phạm vi file này). Schema role (2 vs ≥3) thì **hardcode cứng** trong `_role_schema`, không đọc config nào khác. |
| `max_groups_per_timeslot` (H13) | Cột round, nullable, **không có default** — `null` = không giới hạn | `apps/api/migrations/versions/0014_manager_mock_alignment.py:16-17` | Có, round-level. |
| `max_minutes_per_part` / `max_minutes_per_day` (giới hạn phút GV/buổi, /ngày) | Cột round, nullable, **không có default** | `apps/api/migrations/versions/0015_round_minute_limits.py:14-19` | Có, round-level. Khi `null` thì fallback sang đếm số phiên (2 dòng dưới). |
| `h12_sessions_per_part` / `h12_sessions_per_day` (giới hạn số phiên GV/buổi, /ngày — fallback khi không set phút) | `DEFAULT 4` / `DEFAULT 8` | `apps/api/migrations/versions/0002_domain_model.py:143-144` | Có, round-level. Logic fallback (chỉ dùng session-count khi minutes-limit là `null`) hardcode ở `manual_scheduling.py:851-860`. |
| `h12_semester_quota` | Cột round, nullable, **không có default**, **được SELECT nhưng không hề dùng trong bất kỳ check nào của file này** | `apps/api/migrations/versions/0002_domain_model.py:145`; select ở `manual_scheduling.py:201` | Có cột, nhưng **không enforce** ở manual scheduling (xem mục 7). |
| `group_selection_mode` | Cột round, `DEFAULT FALSE` | `apps/api/migrations/versions/0009_round_selection_mode.py:13` | Có, round-level. Bật/tắt toàn bộ nhóm check `GROUP_SLOT_NOT_SELECTED` (3.2, 3.7). |
| `round_room_types` (loại phòng cho phép) | Không default cứng — round chưa khai thì set rỗng (`room_types = []`) → mọi phòng bị coi allowed (điều kiện `if room_types and ...` chỉ chặn khi set không rỗng, khác với `room_assignment.py` — xem mục 7) | Bảng `round_room_types`, `0023_round_room_types.py` | Có, round-level. |
| `PUBLISHABLE_ROUND_STATUSES` (6 status cho phép publish) | `EDITABLE_ROUND_STATUSES - {ONGOING, POSTPONED, COMPLETED, LOCKED, CANCELLED}` = `{DRAFT, OPEN_REGISTRATION, REGISTRATION_CLOSED, SCHEDULING, SCHEDULED, PUBLISHED}` | Literal set, `manual_scheduling.py:37-41` | Không — hardcode Python set, đổi phải sửa code. |
| `EDITABLE_ROUND_STATUSES` (status cho phép sửa nháp) | = toàn bộ 11 giá trị enum `RoundStatus` (mọi status đều sửa được nháp) | `manual_scheduling.py:37-38` | Không — hardcode; trên thực tế `_ensure_mutable_round` không bao giờ raise vì set này luôn full. |
| `MANUAL_SESSION_PREFIX` | `"manual_session_"` | `manual_scheduling.py:42` | Không — literal string cho external id. |
| `VN_TZ` | `"Asia/Ho_Chi_Minh"` | `manual_scheduling.py:36` | Không — hardcode, không đọc từ settings/config nào. |
| `BLOCKED_REASON_LABELS` (message tiếng Việt cho từng blocker code) | Dict 20 entry cố định | `manual_scheduling.py:43-65` | Không — hardcode string, không i18n table. |
| `_role_schema` label tiếng Việt (`"Chủ tịch"`, `"Thư kí"`, `"Thành viên N"`, `"Review N"`) | Cố định | `manual_scheduling.py:108-122`, `_role_label` :666-675 | Không. |
| `_eligible_group_status` — map `round_type` → tập `group.status` hợp lệ | Dict hardcode trong hàm (vd `DEFENSE_2`→`{PENDING_D2}`, `DEFENSE_1_2_TYPES`→`{ELIGIBLE_D12, D12_CONDITIONAL}`...) | `manual_scheduling.py:178-185` | Không — hardcode, không đọc bảng config nào. |
| `config.batchSize` / `chairMinLevel` / `secretaryMinLevel` / `maxSameSupervisorRatio` trong response board | **Luôn `null`** | `manual_scheduling.py:1081-1084` | Không — literal `None`; **grep toàn repo xác nhận không có cột/bảng nào tên tương ứng ở bất kỳ đâu**, kể cả phía auto-scheduling. Đây là field đặt chỗ cho tương lai, hiện chưa có input nào phía sau. |
| `config.eligibleProjectStatuses` trong response board | Luôn literal `["ACTIVE"]` | `manual_scheduling.py:1085` | Không — hardcode, và **không khớp với check thực tế**: `_validate_against_database` chỉ check `project_id IS NOT NULL`, không hề so `project.status` với `"ACTIVE"` hay giá trị nào khác (xem mục 6). |
| `_constraint_statuses` — H14 (skill CT/TK)/H15 (tỉ lệ GVHD) | Luôn trả `status="notConfigured"`, chỉ sinh warning không chặn publish | `manual_scheduling.py:136-161` | Không — 2 rule này chưa có nguồn dữ liệu (bảng skill, bảng batch/tỉ lệ GVHD chưa tồn tại), hardcode "chưa cấu hình". |
| Advisory/session limit của `/manual-schedule/options` — `pageSize` | `default=50`, `le=200`; `page default=1` | `manual_scheduling.py:1113-1114` | Là query param FE tự set trong giới hạn 1-200, không phải setting hệ thống. |

**Tổng kết cho việc thiết kế config thuật toán:** phần "constraint cứng" (H1-H13, trừ H11 chi tiết) đã
đọc từ cột round có sẵn (`reviewer_count`, `max_groups_per_timeslot`, `max_minutes_per_part/day`,
`h12_sessions_per_part/day`, `group_selection_mode`, `round_room_types`). Phần "constraint mềm/soft"
(S1-S9 trong tài liệu thuật toán cũ) **hoàn toàn không xuất hiện** trong file này — manual scheduling
không tính điểm load-balance hay skill-fit, chỉ có hard blocker nhị phân. `batchSize`,
`chairMinLevel`, `secretaryMinLevel`, `maxSameSupervisorRatio` là 4 field lộ ra ngoài API nhưng chưa
có bất kỳ cơ chế lưu/đọc nào — là ứng viên rõ nhất cần thiết kế bảng config mới nếu muốn hiện thực hóa.

## 6. Đối chiếu tài liệu cũ

| Doc | Trạng thái | Ghi chú cụ thể |
|---|---|---|
| `docs/manual-scheduling-api.md` | Lỗi thời | Thiếu hẳn `bulk-upsert` và `publish-readiness` (2 trong 9 endpoint hiện có). Không có `clientRevision`/optimistic lock. Đây là bản đề xuất ban đầu, đã bị thay thế bởi 2 doc chi tiết hơn (business-contract, fe-handoff). |
| `docs/manual-scheduling-business-contract.md` §1-§6, §10-§16 | Một phần đúng | Đúng ở mức khái niệm (1 session nhiều group 1 phòng, phân quyền, endpoint list, error code, revision/audit). Sai/thiếu cụ thể: (1) §7 "Bulk upsert phải atomic... trừ khi `allowDraftIncomplete=true`" — **không đúng**, code không hề validate blocker trước khi ghi bulk-upsert, field `allowDraftIncomplete` không được đọc (mục 3.4); (2) §11 bảng H1-H16 liệt kê `H14_ROLE_SKILL_MISSING`, `H15_SUPERVISOR_RATIO_EXCEEDED`, `H16_DEFENSE_ROLE_INVALID`, `ROOM_CAPACITY_INSUFFICIENT`, `BATCH_SIZE_EXCEEDED`, `REVIEWER_SKILL_INSUFFICIENT` như đã enforce — thực tế H14/H15 chỉ là warning "notConfigured" (không chặn), H16/capacity/batch-size/skill **chưa hề implement**, không xuất hiện ở đâu trong code; (3) §11 mô tả H12 số cụ thể "240 phút/buổi, 480 phút/ngày" — thực tế đây là cột round configurable (`max_minutes_per_part/day`, không default cứng, fallback qua session-count), không phải số hardcode 240/480. |
| `docs/manual-scheduling-business-contract.md` §9 "Publish phải validate ... không được tin kết quả validate cũ" | Đúng | Khớp code — `/publish` tự load lại session và chạy `_validate_manual` trong transaction, không dùng kết quả `/validate` trước đó. |
| `docs/journals/260825-1554-manual-schedule-persistence.md` | Đúng | Khớp code hiện tại: DB là source of truth (không còn localStorage), mỗi mutation tăng revision, sửa sau publish đi vào draft không đụng bản công khai, publish tạo controlled-change/version mới. |
| `docs/api/manual-scheduling-fe-handoff.md` §3, §4, §5, §12, §14, §15 | Đúng | Endpoint list, ID convention (`manual_session_N`/`grp_N`/`lec_N`/`room_N`/`ts_N`/`slot_HHMM`), blocker code list, và đặc biệt §14 "Giới hạn hiện tại của BE" (batchSize/chairMinLevel/secretaryMinLevel null, `confirmWarnings` chưa dùng, `council_members.assignment` luôn `REVIEWER`) **khớp chính xác** với code đọc được — đây là doc cross-check chính xác nhất trong số các doc cũ. |
| `docs/api/capstone-scheduler-manager-ui-mockdata.md` | Không đề cập | Grep toàn file không có dòng nào nhắc `manual-schedule`/`manual_schedule` — tài liệu mock UI chung, không phủ luồng này. |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` | Không đề cập | Grep không có bảng `manual_schedule_*` — ERD v1.0 được viết trước migration `0039_manual_scheduling`, chưa cập nhật theo tính năng này. |
| `docs/project-reference/BusinessRules_CapstoneScheduler_v1.0.md` H11 "Defense 1.2 phải giữ nguyên Chủ tịch đã chấm Defense 1.1" | Một phần đúng | Business rule gốc yêu cầu giữ đúng **người giữ vai Chủ tịch** ở D1.1. Code (`_prior_reviewers_for_groups`, :1012-1042) chỉ yêu cầu **bất kỳ 1 người nào** trong toàn bộ council cũ (không phân biệt role) xuất hiện lại ở D1.2 — lỏng hơn rule gốc mô tả. Cơ chế waiver theo group (`h11_waivers`) khớp mô tả "Moderator gỡ ràng buộc từng nhóm". |

## 7. Giới hạn/edge case quan sát được trong code hiện tại

- **`EDITABLE_ROUND_STATUSES` = toàn bộ enum status** → `_ensure_mutable_round` trên thực tế **không
  bao giờ chặn** gì (mọi round ở mọi status đều sửa được nháp) — code có logic guard nhưng điều kiện
  luôn true, khác biệt duy nhất còn tác dụng thật là `_ensure_publishable_round` (6/11 status).
- **DB column `manual_schedule_sessions.status` không bao giờ nhận giá trị `READY`** dù CHECK
  constraint cho phép 3 giá trị — `READY` chỉ tồn tại tạm thời trong response JSON
  (`_decorate_sessions_with_validation`), không bao giờ được `UPDATE` vào bảng.
- **Nhóm chưa từng gửi `group_slot_preferences`** (0 dòng preference) thì bypass hoàn toàn check
  `GROUP_SLOT_NOT_SELECTED` ở cả write-time (`_ensure_registered_timeslot`) lẫn validate-time
  (`_validate_against_database`) — kể cả khi `group_selection_mode` đang bật. Chỉ nhóm **có** preference
  nhưng chọn sai timeslot mới bị chặn.
- **`bulk-upsert` không validate blocker trước khi ghi** — luôn ghi mọi session dạng DRAFT, khác hẳn
  hành vi atomic/chặn mô tả trong business-contract cũ (mục 6).
- **`round_room_types` rỗng (round chưa khai loại phòng)** → `room_types` trả `set()` rỗng →
  `_validate_against_database` dùng điều kiện `elif room_types and room["room_type"] not in
  room_types` — set rỗng làm điều kiện `room_types` false nên **check bị bỏ qua hoàn toàn**, nghĩa là
  round chưa cấu hình loại phòng thì **mọi phòng đều được coi hợp lệ** (ngược với hành vi ở
  `room_assignment.py`, nơi round chưa khai `round_room_types` làm mọi phòng bị coi "không allowed" —
  2 luồng xử lý set rỗng theo 2 hướng ngược nhau, xem `docs/scheduling-flows/room-assignment.md` §5).
- **`create_manual_session`/`update_manual_session` dùng `next(...)` không bắt exception** (dòng 1406,
  1499) để tìm lại session vừa ghi trong `_board_payload` — nếu vì lý do nào đó session không xuất
  hiện trong board mới build (race condition lý thuyết, hoặc bug ở `_board_payload`) sẽ raise
  `StopIteration` không được catch → lỗi 500 không có error code rõ ràng.
- **`h12_semester_quota`** được load từ round nhưng không hề dùng trong bất kỳ phép tính load nào của
  file này — quota theo kỳ không được enforce ở luồng manual scheduling (có thể enforce ở nơi khác,
  không xác nhận trong phạm vi file này).
- **`PublishPayload.confirm_warnings`** và **`BulkUpsertPayload.allow_draft_incomplete`** là 2 field
  request được khai báo (giữ đúng contract JSON) nhưng không được đọc ở bất kỳ đâu trong logic xử lý —
  dead field, gửi gì cũng không đổi hành vi.
- **`council_members.assignment` luôn ghi `"REVIEWER"`** khi publish thủ công, kể cả cho reviewer giữ
  role `CHAIR`/`SECRETARY` — vai trò chi tiết chỉ còn lưu được ở `manual_schedule_session_reviewers`
  (bản nháp), không có ở bảng council chính thức sau publish.
- **`_round_or_404` không tồn tại route riêng để tạo/xóa `h11_waivers`** trong file này — waiver được
  đọc (`active=TRUE`) nhưng route ghi waiver nằm ngoài phạm vi `manual_scheduling.py`, không xác nhận
  được ở đây.
