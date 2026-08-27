# Luồng gán hội đồng / giảng viên (Council & Lecturer Assignment) — hiện trạng code

> Tài liệu mô tả **as-is**, không phải audit. Ngày viết: 26/08/2026, dựa trên nhánh `dev` (be repo) tại thời điểm đọc.
> Phạm vi: `apps/api/app/services/councils.py` + các route gọi vào nó. KHÔNG bao gồm thuật toán auto-scheduling (CP-SAT solver, `scheduler/scheduler.py`, `scheduler/candidates.py` nội bộ) hay luồng manual-scheduling chi tiết — các luồng đó do agent khác phụ trách; ở đây chỉ nhắc tới chúng làm entry point khi chúng gọi `create_council()`.

## 1. Tổng quan luồng

`councils.py` **không tự chọn ai vào hội đồng**. Nó chỉ làm 1 việc: nhận một danh sách `lecturer_id` đã được quyết định sẵn ở nơi khác (solver, thao tác thủ công của Manager, hoặc snapshot từ Committee catalog), rồi ghi thành một bản ghi **bất biến** (immutable) trong bảng `councils` + `council_members`. Đây là lớp persistence cuối cùng của "ai chấm phiên nào", không phải lớp ra quyết định "nên chọn ai".

Council được tạo (trigger) tại các thời điểm:
- Khi Manager **kích hoạt** một phương án lịch nháp (activate schedule version) → tạo 1 council/session từ kết quả solver.
- Khi Manager **publish lịch thủ công** (manual schedule) → tạo council cho từng session thủ công.
- Khi Manager **đổi Result Owner** của 1 phiên → tạo council mới (superseding) chỉ khác cờ `is_result_owner`.
- Khi Manager/Admin thực hiện **controlled-change** trên phiên đã publish (đổi reviewer, đổi giờ/phòng) → tạo council mới (superseding) cho phiên bị sửa.
- Khi Manager/Admin tạo **lịch bù** (makeup session) cho phiên bị hoãn → tạo council mới (kế thừa hoặc đổi reviewer).

Người trigger: luôn là `ADMIN`/`MANAGER` qua các route quản trị lịch (`_require(user, "ADMIN", "MANAGER")` hoặc tương đương); không có endpoint nào cho Lecturer/Student tự tạo council.

## 2. Entry points

Tất cả nằm trong prefix `/api/v1`. File `apps/api/app/routes/schedule_operations.py` import `CouncilError, create_council, load_council_members, lock_reviewer_ids, validate_council_change` từ `app/services/councils.py` (dòng 49-55).

| Method + Path | Handler (file:line) | Council action |
|---|---|---|
| `POST /schedule/versions/{versionId}/activate` | `activate_schedule_version` — `schedule_operations.py:1048` | Với mỗi `schedule_assignment`, tạo 1 council mới từ `schedule_assignment_reviewers` (snapshot của solver). `create_council()` gọi tại dòng 1140. |
| `POST /schedule/versions/{versionId}/sessions/{sessionId}/result-owner` | `assign_result_owner` — `schedule_operations.py:1180` | Đọc council hiện tại (`load_council_members`), validate không đổi thời gian → tạo council mới chỉ đổi `is_result_owner`, `supersedes_council_id` = council cũ. Gọi tại dòng 1210. |
| `POST /schedule/versions/{versionId}/sessions/{sessionId}/controlled-change` (const `CONTROLLED_CHANGE_PATH`) | `controlled_change` — `schedule_operations.py:1295` | 2 nhánh: **reviewer-only** (đổi reviewer, giữ nguyên version) tạo council mới supersede tại dòng 1362; **time/room hoặc mixed** clone toàn version mới, tạo council mới cho phiên bị sửa tại dòng 1398 (các phiên khác trong version giữ nguyên `council_id` cũ). |
| `POST /sessions/{sessionId}/makeup` | `create_makeup_session` — `schedule_operations.py:1533` | Tạo phiên bù cho phiên `POSTPONED`; tạo council mới (giữ nguyên `is_result_owner` từ council gốc trừ khi đổi reviewer) tại dòng 1645. |
| `POST /rounds/{roundId}/manual-schedule/publish` | `publish_manual_schedule` — `manual_scheduling.py:1601` | Với mỗi phiên thủ công, tạo council mới (`assignment="REVIEWER"`, `is_result_owner=False` luôn) tại dòng 1666. Chi tiết luồng manual-schedule không thuộc phạm vi tài liệu này. |

Không có endpoint `POST/GET/PATCH /councils` trực tiếp — council chỉ được tạo như tác dụng phụ (side effect) của các thao tác lịch ở trên, không có CRUD catalog riêng cho "council thật" (khác với "Committee catalog" ở mục 3.3).

## 3. Business logic từng bước

### 3.1. `create_council()` — `services/councils.py:57-111`

```
create_council(db, round_id, members, *, created_by=None, reason=None, supersedes_council_id=None) -> council_id
```

1. Chuẩn hoá từng member qua `_member_values()` (dòng 38-54): chấp nhận `Mapping` (dict) hoặc `Sequence` (tuple/list theo thứ tự `lecturer_id, assignment, is_result_owner, snapshot_name`). Mặc định `assignment="REVIEWER"`, `is_result_owner=False`. `snapshot_name` bắt buộc 1-160 ký tự, mặc định = `str(lecturer_id)` nếu không truyền.
2. **Ràng buộc số lượng**: phải có ≥1 member — nếu rỗng raise `COUNCIL_MEMBER_INVALID` (422).
3. **Ràng buộc trùng lặp**: 1 lecturer chỉ được xuất hiện 1 lần trong 1 council — kiểm bằng `len(set(...)) != len(...)`, raise `COUNCIL_MEMBER_INVALID` (422) nếu trùng.
4. INSERT `councils` (round_id, supersedes_council_id, created_by, reason) — `sealed_at` để NULL lúc này.
5. INSERT từng dòng `council_members` (council_id, lecturer_id, assignment, is_result_owner, snapshot_name) — DB trigger chỉ cho phép INSERT khi council cha chưa sealed (xem mục 4).
6. UPDATE `councils SET sealed_at = now()` — seal. Sau bước này DB trigger chặn mọi UPDATE/DELETE tiếp theo trên `councils` lẫn `council_members` (chỉ cho phép chuyển `sealed_at` từ NULL → giá trị, 1 lần duy nhất).

**Không có ràng buộc nào về vai trò (CHAIR/SECRETARY/MEMBER), số lượng tối thiểu theo loại đợt, hay skill/năng lực trong hàm này** — mọi ràng buộc "hội đồng phải đủ 3 người / phải có Chủ tịch" đều được validate ở lớp gọi (route) hoặc ở scheduler, không nằm trong `councils.py`.

### 3.2. Tránh trùng lịch (reviewer overlap) — `find_reviewer_conflicts()` / `validate_council_change()`

- `find_reviewer_conflicts(db, reviewer_ids, start_at, end_at, exclude_session_ids=())` (dòng 132-171): query trực tiếp SQL join `sessions` + `schedule_versions` + `council_members`, tìm session nào có `sv.status IN ('ACTIVE','PUBLISHED')` mà thời gian giao nhau (`s.start_at < end_at AND s.end_at > start_at`) và chứa 1 trong các `reviewer_ids`. Đây là cross-round check — quét MỌI round đang active/published, không giới hạn round hiện tại.
- `validate_council_change(db, session_id, round_id, reviewer_ids, start_at, end_at, exclude_session_ids=())` (dòng 174-202): gọi `lock_reviewer_ids()` trước (advisory lock theo thứ tự id tăng dần, tránh deadlock khi 2 request cùng lock nhiều reviewer), rồi gọi `find_reviewer_conflicts()` loại trừ chính session đang sửa. Nếu có conflict → raise `CouncilError("REVIEWER_OVERLAP", ..., 409)` kèm chi tiết conflict.
- Đây là ràng buộc **duy nhất** về "tránh trùng" mà `councils.py` tự thực thi. Nó **không** kiểm tra advisor conflict (H1 — GVHD không chấm đề tài mình hướng dẫn) hay quota — những check đó nằm ở `domain/schedule_operations.py` / `scheduler/validator.py` (ngoài phạm vi tài liệu), chạy trước khi `create_council()` được gọi (ví dụ `validate_schedule()` ở `activate_schedule_version` dòng 1118, `controlled_change` dòng 1352).

### 3.3. Vai trò CHAIR/SECRETARY/MEMBER — 2 cơ chế song song, KHÔNG liên kết nhau

Có 2 khái niệm "hội đồng" khác nhau trong code, dễ nhầm:

1. **Council thật** (`councils` + `council_members`) — bảng ghi lịch sử bất biến, cột `assignment` dùng enum `AssignmentRole` (`domain/enums.py:23-28`): `SUPERVISOR, REVIEWER, RESULT_OWNER, REMEDIATION_VERIFIER, PROJECT_LEADER`. **Không có giá trị CHAIR/SECRETARY/MEMBER trong enum này.** Mọi lời gọi `create_council()` quan sát được trong 6 entry point ở mục 2 đều truyền `assignment` mặc định `"REVIEWER"` (implicit qua `_member_values`) — không nơi nào gán `SUPERVISOR`/`PROJECT_LEADER`/`REMEDIATION_VERIFIER` khi tạo council cho session chấm. Vai trò "ai là Chủ tịch/Thư ký" **không được lưu vào council thật**.
2. **Committee catalog** (`committees` + `committee_members`, migration `0034_committees.py`) — danh mục **nháp**, độc lập, KHÔNG gắn với session/round nào cho tới khi được bind qua `round_committees` (migration `0036_round_committees.py`, route `round_committee_contract.py`). Bảng này dùng enum riêng `committee_role` (`REVIEWER, CHAIR, SECRETARY, MEMBER`). Vai trò được gán **tự động theo vị trí nhập tay** trong `domain/committees.py::assign_roles()` (dòng 23-40): nếu `count <= 3` → tất cả là `REVIEWER {position}`; nếu `count > 3` → vị trí 1 = `CHAIR`, vị trí 2 = `SECRETARY`, còn lại = `MEMBER`. **Không dựa trên năng lực/skill/thâm niên của giảng viên** — hoàn toàn theo thứ tự người dùng nhập khi tạo Committee.

**Kết nối giữa 2 cơ chế**: khi 1 Round có Committee được gán (`round_committees`), solver (`scheduler/candidates.py::_reviewer_tuples()`, dòng 71-97) chỉ chọn nguyên khối `member_ids` của 1 Committee làm ứng viên reviewer cho 1 (group, timeslot) — không tự trộn lẻ từng người từ nhiều Committee hay từ free-pool. Nhưng khi kết quả solver này được persist qua `create_council()` (tại `activate_schedule_version`), **vai trò CHAIR/SECRETARY của Committee bị mất** — mọi member ghi vào `council_members.assignment` đều là `"REVIEWER"` mặc định (xem `schedule_assignment_reviewers` — bảng trung gian giữa solver output và council không có cột role/CHAIR-SECRETARY nào, chỉ có `is_result_owner`). Việc phục hồi "ai là Chủ tịch" sau đó chỉ làm được ở tầng **export Excel** (`GET /exports/round/{roundId}/council.xlsx`) bằng cách so khớp lại member-set của council với member-set của Committee gốc (best-effort, fallback về thứ tự `lecturer_id` tăng dần nếu không khớp Committee nào) — không phải một trường dữ liệu bền vững.

### 3.4. Tránh trùng GVHD (advisor conflict) và các ràng buộc chọn người khác

**Không thuộc `councils.py`** — nằm ở tầng scheduler (`scheduler/candidates.py` dòng 31-36: lọc `reviewer_id not in context.project_supervisors.get(project_id, set())` và loại theo `context.conflicts` khai báo trước) hoặc ở `validate_schedule()` cho manual/controlled-change path. `councils.py` chỉ nhận đầu vào đã qua các lọc đó; bản thân nó không biết ai là GVHD của đề tài nào.

### 3.5. Council dẫn xuất (superseding) — cơ chế "đổi người"

Vì `council_members` bất biến (immutable), muốn đổi 1 người trong hội đồng phải: tạo council **mới** với danh sách member đầy đủ (copy từ council cũ + áp thay đổi), gọi `create_council(..., supersedes_council_id=<council cũ>)`, rồi UPDATE `sessions.council_id` trỏ sang council mới. Council cũ vẫn tồn tại nguyên vẹn trong DB (audit trail) — không bị xoá, không bị sửa. Thấy rõ ở `assign_result_owner` (dòng 1210), nhánh reviewer-only của `controlled_change` (dòng 1362), và `create_makeup_session` khi đổi reviewer (dòng 1645, dù makeup không truyền `supersedes_council_id` — nó là council "gốc mới" cho phiên bù, không kế thừa lineage).

## 4. Data model / bảng liên quan

Nguồn: migration `0025_immutable_councils.py`, `0034_committees.py`, `0036_round_committees.py`.

| Bảng | Cột quan trọng | Ghi chú |
|---|---|---|
| `councils` | `id`, `round_id` (FK `rounds`, RESTRICT), `supersedes_council_id` (self-FK, RESTRICT), `created_by` (FK `accounts`), `reason`, `created_at`, `sealed_at` | `sealed_at IS NULL` = đang trong "cửa sổ dựng" (construction window); chỉ ứng dụng ghi trong transaction của `create_council()` mới thấy state này. Sau khi `sealed_at` được set, **immutable hoàn toàn**. |
| `council_members` | PK composite `(council_id, lecturer_id)`, `assignment` (enum `assignment_role`), `is_result_owner`, `snapshot_name` | `snapshot_name` là tên hiển thị tại thời điểm tạo (không tự cập nhật nếu GV đổi tên sau này — đúng tinh thần "snapshot"). |
| `sessions.council_id` | FK → `councils.id`, RESTRICT, NOT NULL | Mỗi session luôn có đúng 1 council tại 1 thời điểm; đổi hội đồng = đổi con trỏ này sang council mới, không sửa council cũ. |
| `committees` | `id`, `code` (unique), `member_count` (CHECK 1-15), `created_by`, `created_at` | Danh mục nháp, KHÔNG gắn round/thời gian trực tiếp. |
| `committee_members` | PK `(committee_id, lecturer_id)`, `role` (enum `committee_role`: REVIEWER/CHAIR/SECRETARY/MEMBER), `sequence_number` (unique trong committee) | Vai trò gán theo `assign_roles()` khi tạo (mục 3.3). |
| `round_committees` | PK `(round_id, committee_id)`, FK `round_id` → `rounds` (CASCADE), FK `committee_id` → `committees` (RESTRICT) | Many-to-many: 1 round có thể gán nhiều committee (pool), 1 committee dùng lại được ở nhiều round. Ràng buộc `committee.member_count == rounds.reviewer_count` được enforce ở `domain/committees.py::validate_round_committee_sizes()` (không phải DB constraint). |

**DB triggers bất biến** (định nghĩa trong `0025_immutable_councils.py`):
- `councils_immutable` (BEFORE UPDATE/DELETE on `councils`): chặn DELETE tuyệt đối; chỉ cho phép 1 UPDATE hợp lệ duy nhất — chuyển `sealed_at` từ NULL sang NOT NULL, mọi cột khác phải giữ nguyên.
- `council_members_immutable` (BEFORE INSERT/UPDATE/DELETE): cho INSERT chỉ khi council cha chưa sealed; chặn UPDATE/DELETE tuyệt đối.
- `sessions_council_valid` (CONSTRAINT TRIGGER, DEFERRABLE INITIALLY IMMEDIATE, AFTER INSERT/UPDATE OF `council_id` on `sessions`): council phải tồn tại + đã sealed + cùng `round_id` với `schedule_version.round_id` của session — nếu không raise exception ngay ở tầng DB, kể cả khi thao tác không qua application code.

Các trigger này áp dụng ở **mọi đường ghi DB**, không chỉ qua `councils.py` — nên `councils.py` thực chất chỉ là 1 client thuận tiện tuân theo giao thức "insert-then-seal" mà DB đã ép buộc.

## 5. Config / hằng số hiện đang hardcode

**`app/config.py` (`Settings`, pydantic-settings) hoàn toàn không có setting nào liên quan council/committee/scheduler** — đã đọc toàn bộ file (49 dòng): chỉ có app_name, database_url, session/cookie, Google OAuth, CORS, semester duration. Không có `chair_min_level`, không có council size, không có timeout thuật toán.

Các tham số nghiệp vụ liên quan hiện có, toàn bộ đều hardcode trong code (không qua `.env`, không qua API):

| Tên/giá trị | Ý nghĩa | Nơi định nghĩa (file:line) | Có expose qua API không |
|---|---|---|---|
| `MIN_MEMBERS = 1`, `MAX_MEMBERS = 15` | Số thành viên tối thiểu/tối đa của 1 Committee | `domain/committees.py:8-9` | Không — hardcode Python constant, đồng thời trùng lặp bằng DB `CHECK (member_count BETWEEN 1 AND 15)` ở migration `0034` |
| `REVIEWER_ONLY_MAX = 3` | Ngưỡng phân biệt "chỉ có REVIEWER" (≤3 người) vs "có CHAIR/SECRETARY/MEMBER" (>3 người) trong `assign_roles()` | `domain/committees.py:10` | Không |
| Vị trí 1 = CHAIR, vị trí 2 = SECRETARY | Quy tắc gán vai trong Committee | `domain/committees.py::assign_roles()` dòng 32-38 | Không — logic if/elif cứng theo `position`, không đọc năng lực GV nào |
| `expected_reviewers` map: REVIEW_1_1/REVIEW_1/REVIEW_2_1/REVIEW_2 = 2, DEFENSE_1_1/REVIEW_3 = 3, DEFENSE_1_2/DEFENSE_1/DEFENSE_2 = 5 | Số reviewer bắt buộc theo loại đợt — validate khi Manager tạo Round | `routes/target_round_contract.py:173-186` | Gián tiếp — Manager không sửa được số này qua API, chỉ có thể set `reviewerCount` khớp đúng giá trị bảng này khi tạo Round, sai thì bị reject `ValueError` |
| `result_owner_mode` chỉ cho phép với `{DEFENSE_1_1, REVIEW_3, DEFENSE_2}` | Loại đợt nào được bật Result Owner | `routes/target_round_contract.py:188-189`, lặp lại check ở `schedule_operations.py:1203` | Không — set cứng trong code, Manager chỉ bật/tắt cờ boolean `resultOwnerMode` cho các loại đợt đã cho phép |
| `snapshot_name` giới hạn 1-160 ký tự | Validate input council member | `services/councils.py:52-53` | N/A (input validation, không phải business config) |
| `FREE_POOL_REVIEWER_TUPLE_CAP` (không đọc trực tiếp trong scope tài liệu này) | Giới hạn số tổ hợp reviewer sinh ra khi round KHÔNG gán Committee | `scheduler/candidates.py` (ngoài phạm vi chi tiết) | Không — thuộc solver, xem tài liệu solver riêng |

**Kết luận cho thiết kế config mới**: điểm cần cấu hình hóa rõ nhất nằm ở `domain/committees.py::assign_roles()` (gán CHAIR/SECRETARY theo skill thay vì theo vị trí nhập) và ở việc vai trò Committee **không được truyền tiếp** vào `council_members.assignment` khi `create_council()` chạy (mọi nơi gọi đều hardcode `"REVIEWER"`) — muốn có `chairMinLevel`/`secretaryMinLevel` v.v. thì phải sửa cả 2 điểm này, không chỉ thêm cột config trên `rounds`.

## 6. Đối chiếu tài liệu cũ

| Doc | Trạng thái | Ghi chú cụ thể |
|---|---|---|
| `docs/council-algorithm-config-plan.md` | **Đúng** (khớp code hiện tại tại thời điểm đọc) | Đây là tài liệu phân tích code do 1 phiên trước viết (23/08/2026), các trích dẫn file:line (`councils.py:57`, `domain/committees.py::assign_roles()`, các dòng gọi `create_council` trong `schedule_operations.py`) đều khớp với code đọc trực tiếp ở tài liệu này. Riêng dòng "970, 1042, 1194, 1230, 1477" (mục lỗi H) là số dòng tại thời điểm viết tài liệu đó — tại thời điểm đọc hiện tại các lời gọi tương ứng nằm ở dòng 1140, 1210, 1362, 1398, 1666 (đã dịch chuyển do code thay đổi giữa 2 lần đọc, không phải sai nội dung). Bảng `skills`/`lecturer_skills`/`project_types`/cột `uses_council_roles` v.v. mà doc này đề xuất — xác nhận **chưa tồn tại** trong migrations hiện có. |
| `docs/council-scheduling-config/mockup/council-schedule-config-flow.html` | **Không đối chiếu được trực tiếp** | File là 1 Claude-Design canvas export (~476K token, nội dung UI nằm trong JSON escape của script block `appifact-doc`), không phải HTML đọc tuyến tính được trong ngân sách hợp lý. Nội dung nghiệp vụ minh hoạ của nó trùng với ví dụ luồng đầy đủ ở mục 7 của `council-algorithm-config-plan.md` (đã đọc) — không phát hiện mâu thuẫn qua phần đọc được (CSS design tokens, phần đầu file). Khuyến nghị: nếu cần đối chiếu sâu, mở trực tiếp bằng trình duyệt thay vì đọc file. |
| `plans/260822-1110-committee-round-binding/plan.md` | **Đúng, đã hoàn thành** | Trạng thái `status: completed`, 4 phase đều "Completed". Đối chiếu với code: migration `0034`/`0036` tồn tại đúng như mô tả, route `round_committee_contract.py` tồn tại đúng path `PUT/GET /rounds/{roundId}/committees`, `validate_round_committee_sizes()` tồn tại đúng ở `domain/committees.py:43-55`. Điểm "No change to Council semantics" trong plan này được xác nhận đúng — `council_members.assignment` vẫn độc lập với Committee role, và điều này **chính là gốc của "lỗi H"** mà `council-algorithm-config-plan.md` nêu (2 tài liệu không mâu thuẫn, chỉ khác góc nhìn: 1 tài liệu coi đó là thiết kế đã chốt, tài liệu kia coi đó là mất dữ liệu cần vá). |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` | **Một phần đúng — lệch thuật ngữ so với schema thật** | Doc mô tả `rounds.council_reuse_mode` (dòng 16) và cột `derived_from_council_id` trên `councils` (dòng 71, 144) — **schema thật dùng tên cột `supersedes_council_id`** (migration `0025`, xác nhận trực tiếp), không có cột `council_reuse_mode` nào trên `rounds` (đã không grep thấy trong migrations liên quan councils). Doc cũng còn mô tả bảng `session_reviewers` như nguồn "ảnh chụp người chấm" (dòng 167, 182-198) — bảng này **đã bị DROP** ở migration `0025` (`bind.exec_driver_sql("DROP TABLE session_reviewers")`), thay bằng `council_members` (bất biến) + `schedule_assignment_reviewers` (bảng nháp trước khi activate). Đây là tài liệu thiết kế v1.0 (tiền-implementation), không phải tài liệu đồng bộ theo code. |
| `docs/project-reference/BusinessRules_CapstoneScheduler_v1.0.md` | **Một phần đúng — mô tả nghiệp vụ đúng tinh thần, sai chi tiết vai trò** | H1 (GVHD không chấm đề tài mình hướng dẫn), H5 (đủ người theo loại đợt), BR-PUB-02 (đổi hội đồng sau publish), BR-INC-01 (đổi người tại chỗ) — tất cả đều khớp hành vi code quan sát được (mục 3.2, 3.5). Riêng dòng 41 "Defense = 3 GV: Chủ tịch, Phản biện, Thư ký" và dòng 359-360 (quyền hạn riêng của "Chủ tịch hội đồng"/"Thư ký hội đồng") **không có cơ sở dữ liệu tương ứng** ở tầng council thật — như đã nêu ở mục 3.3, vai trò này chỉ tồn tại (thô sơ, không theo năng lực) ở Committee catalog, và bị mất khi ghi vào `council_members`. Câu hỏi mở O3 của chính tài liệu này ("Tiêu chuẩn để 1 GV được làm Chủ tịch — hệ thống chưa ràng buộc") tự xác nhận đây là khoảng trống đã biết. |

## 7. Giới hạn / edge case quan sát được

- **Council không tự validate số lượng theo loại đợt** — `create_council()` chỉ yêu cầu ≥1 member. Ràng buộc "Review=2, Defense=3/5" chỉ được enforce ở tầng gọi (`validate_schedule()`, `target_round_contract.py`), không phải invariant của bảng `councils`. Một lời gọi `create_council()` trực tiếp (vd. từ script/test) với 1 member vẫn thành công.
- **`makeup` session không kế thừa `supersedes_council_id`** (dòng 1645-1651: không truyền tham số này) — khác với 4 entry point còn lại. Council của phiên bù là 1 "gốc" mới về mặt lineage, dù nội dung member có thể trùng hệt council gốc.
- **Vai trò CHAIR/SECRETARY hoàn toàn không truy vấn lại được** từ dữ liệu council thật sau khi lịch được activate — chỉ suy luận lại (best-effort) ở export Excel bằng cách so khớp member-set với Committee catalog gốc; nếu Manager không gán Committee cho round (free-pool scheduling), không có cách nào biết ai từng là Chủ tịch.
- **`find_reviewer_conflicts()` quét toàn bộ round ACTIVE/PUBLISHED trong hệ thống**, không giới hạn theo semester hay round hiện tại — có thể là chủ đích (đúng nghiệp vụ "1 GV không được trùng giờ giữa các đợt khác nhau") nhưng cũng nghĩa là chi phí query tăng theo tổng số session toàn hệ thống, không có index hint hay giới hạn phạm vi thời gian ngoài `start_at`/`end_at` filter.
- **`_member_values()` chấp nhận cả dict lẫn tuple/list** cho input member — 2 hình dạng dữ liệu khác nhau cùng được hỗ trợ tại 1 hàm, dễ gây nhầm lẫn khi thêm caller mới (không rõ interface "chính thức" là gì).
- **Council catalog không có endpoint đọc trực tiếp** (`GET /councils/{id}`) — muốn xem council phải qua `load_council_members()` nội bộ (dùng bởi các route khác) hoặc qua `sessions`/export; không có REST resource độc lập cho council.
