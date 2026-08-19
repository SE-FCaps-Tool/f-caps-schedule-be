# FE Migration Phases — sang `capstone-fe-be-implementation-spec.md`

Ngày lập: 2026-08-19
Nguồn: `docs/capstone-fe-be-implementation-spec.md` (spec đích, BE sẽ viết lại theo đây)

FE hiện tại được xây theo `docs/manager-api.md`, `master-data.md`, `scheduling.md`,
`results-reports.md`, `role-api-matrix.md` — các file này **sẽ bị thay thế**. Không sửa
theo spec mới cho tới khi BE xác nhận từng phase đã deploy (xem "Điều kiện bắt đầu"
mỗi phase). Mục tiêu file này: chia nhỏ khối lượng khổng lồ thành phase làm được, theo
đúng thứ tự phụ thuộc của domain, để không phải viết lại một lần toàn bộ ~30 màn hình.

## Thay đổi nền tảng (áp dụng cho MỌI phase, làm ở Phase 0)

| | Hiện tại | Spec mới |
|---|---|---|
| Response envelope | Trả thẳng object/array | `{ "data": ... }`, list có thêm `{ "data": [...], "meta": {page,pageSize,total} }` |
| Lỗi | `{ "detail": { "code", "message" } }` | `{ "error": { "code", "message", "details" } }` |
| Route | Flat + query param: `GET /groups?semester_id=1` | Nested path: `GET /semesters/:semesterId/groups` |
| Naming | snake_case (`student_code`, `start_date`) | camelCase (`studentIds`, `startDate`) |
| Phân trang | Không có | `page`, `pageSize` trong query + `meta.total` |

Không phase nghiệp vụ nào chạy được nếu chưa xử lý bảng này trước — nó nằm trong
`lib/api/core.ts` (unwrap `data`, đọc lỗi từ `error.code/message/details`) và toàn bộ
`lib/api/services/*.ts` (route + field naming).

## Cách đọc từng phase

- **Điều kiện bắt đầu**: BE phải deploy xong nhóm endpoint nào trước khi FE phase đó
  code được (không viết trước vào khoảng không — không test được, dễ sai khi BE đổi ý
  giữa chừng).
- **Thay thế file/màn hình nào**: liệt kê để biết phạm vi đụng tới trong repo hiện tại.
- **Domain mới phải học**: khái niệm hoàn toàn chưa có ở FE hiện tại, cần hiểu trước khi code.
- **Câu hỏi cần chốt với BE**: chỗ spec chưa rõ hoặc mâu thuẫn với tài liệu cũ.

---

## Phase 0 — Nền tảng: envelope, error, Semester (4 trạng thái)

**Điều kiện bắt đầu**: BE xác nhận response envelope mới đã áp dụng cho ít nhất 1 endpoint
thật để verify được (không suy đoán).

**Thay thế**: `lib/api/core.ts`, `lib/api/errorDetail.ts`, toàn bộ `fetchSemesters.ts` +
`hooks/useSemesters.ts` + `components/semesters/*` (vừa viết lại theo doc 2-trạng-thái
ACTIVE/CLOSED tuần trước — **sẽ phải sửa lại lần nữa** sang PLANNING/ACTIVE/CLOSED/ARCHIVED).

**Domain mới**: `SemesterStatus.PLANNING` (chuẩn bị enrollment/group/project, chưa tạo được
Round), `SemesterStatus.ARCHIVED` (chỉ đọc).

**Câu hỏi cần chốt với BE**:
- Spec không liệt kê route CRUD Semester cụ thể (`GET/POST /semesters` không xuất hiện
  trong file) — dùng flat route như tài liệu Semester API tuần trước, hay đổi sang
  `/semesters` vẫn giữ flat vì Semester là gốc (không có parent)?
- `set-current` (chọn ACTIVE) có còn giữ nguyên logic auto-close bên cạnh 2 state mới
  (PLANNING, ARCHIVED) không, hay có transition riêng cho từng cặp trạng thái?

---

## Phase 1 — Group & Project

**Điều kiện bắt đầu**: BE deploy `GroupModule` + `ProjectModule` theo route
`/semesters/:semesterId/groups` và `/semesters/:semesterId/projects`.

**Thay thế**: `fetchGroups.ts`, `fetchProjects.ts`, `hooks/manager/useGroups.ts`,
`useProjects.ts`, toàn bộ `app/(manager)/manager/groups/**`, `app/(manager)/manager/projects/**`.

**Domain mới**:
- `GroupStatus`: `FORMING → FORMED → ASSIGNED → DISBANDED` (khác hẳn field `status: string`
  hiện tại — cần map lại toàn bộ badge/filter).
- `GroupMembershipStatus.LEFT` — không xoá row, chỉ đổi status + `leftAt`.
- `ProjectStatus` 8 giá trị theo academic progression (`DRAFT → ACTIVE → ELIGIBLE_D12 →
  D12_CONDITIONAL → PENDING_D2 → COMPLETED/FAILED/CANCELLED`) — FE **không tự transition**,
  chỉ hiển thị + refetch sau mỗi submit.
- Warning object `{ code, message }` gắn trên từng Group (`memberCount below minimum`,
  `no leader`) thay vì FE tự tính ngưỡng.

**Việc mới hoàn toàn chưa có ở FE hiện tại**:
- Assign Project to Group (`PUT /groups/:id/project`) — dialog riêng.
- Change Leader / Member Left dùng `membershipId` (không phải `student_id` trực tiếp).

**[ĐÃ LÀM — 2026-08-19]** `fetchGroups.ts`, `fetchProjects.ts`, `useGroups.ts`, `useProjects.ts`,
`groups-page.tsx`, `projects-page.tsx` viết lại theo spec §11–18/§41–47 (route nested
`/semesters/:semesterId/groups|projects`, envelope `{data}`/`{data,meta}`, id kiểu `string`).
`labels.ts` thêm `GROUP_STATUS_META` (4 trạng thái tổ chức) và `PROJECT_STATUS_META` (8 trạng
thái academic progression, đổi tên từ `GROUP_PROGRESS_META` cũ vì thực chất là status của
Project chứ không phải Group). `tsc --noEmit` + `eslint` sạch.

**Câu hỏi cần chốt với BE (chưa có trong spec, đã cố tình bỏ qua thay vì đoán)**:
- Không có `PATCH /projects/:projectId` nào trong spec — tính năng "Chỉnh sửa đề tài / Gán lại
  GVHD chính-phụ sau khi tạo" hiện đang bị vô hiệu hoá trên UI (menu item báo "chưa có trong
  spec BE"). Cần hỏi BE có endpoint này không hay đề tài chỉ sửa được lúc còn DRAFT qua cách khác.
- `major_id` không còn xuất hiện ở `POST /semesters/:semesterId/projects` theo spec §17 — Project
  giờ không gắn Major nữa? Form tạo đề tài đã bỏ trường Ngành, cần BE xác nhận.
- Import đề tài hàng loạt (nút "Import" trên `/manager/projects`) chưa có endpoint tương ứng
  trong spec — vẫn để `notImplemented`.

---

## Phase 2 — Round (EvaluationRound) creation & config

**Điều kiện bắt đầu**: BE deploy `RoundModule` với `POST /semesters/:semesterId/rounds`
nhận `days[].slots[]` ngay trong body tạo Round (không tạo Round trước rồi thêm ngày sau
như hiện tại).

**Thay thế**: `fetchRounds.ts` (phần create/config), `rounds-page.tsx` (Create dialog
→ đổi thành wizard 4 bước: Thông tin → Ngày & Timeslot → Registration + RoomType → Xác nhận),
`round-detail-page.tsx` tab Cấu hình.

**Domain mới**:
- `EvaluationRoundStatus` thêm `CANCELLED` (spec có, hiện tại không).
- `RoomType[]` chọn ở bước tạo Round (`NORMAL/SEMINAR/LAB`) — Round **không** chọn Room cụ
  thể, chỉ chọn loại phòng cho phép.
- CTA theo trạng thái đổi tên: `open-registration` / `close-registration` là action endpoint
  riêng (không còn `POST /rounds/{id}/transition` chung một chỗ như hiện tại).

**Câu hỏi cần chốt với BE**: `maxGroupsPerTimeslot`, `resultOwnerMode`, `groupSelectionMode`
đã có ở FE hiện tại — xác nhận field name/nghĩa giữ nguyên hay đổi theo camelCase thuần túy.

**[ĐÃ LÀM — 2026-08-19]** `fetchRounds.ts` viết lại phần create/detail/list theo spec
§19–21/§49–52 (route nested `/semesters/:semesterId/rounds`, envelope `{data}`/`{data,meta}`,
id kiểu `string`, `RoundStatus` đổi `POSTPONED`→`CANCELLED`). Thêm route mới
`/manager/rounds/new` với wizard 4 bước (`create-round-wizard.tsx`) — slot tự tính giờ kết
thúc theo `durationMinutes` ở bước 1 để luôn thỏa ràng buộc "slot duration == durationMinutes".
`round-detail-page.tsx` tab Tổng quan/Cấu hình đổi sang field mới; header CTA tách hẳn
`Mở đăng ký`/`Đóng đăng ký` thành 2 nút riêng gọi 2 action endpoint mới; các trạng thái sau
`REGISTRATION_CLOSED` (thuộc Phase 4/6/8) hiển thị nút disabled-ish báo "chưa có trong spec BE".
Phần Giảng viên/Nhóm tham gia/Xếp lịch trong `round-detail-page.tsx` **cố tình chưa đụng** —
vẫn gọi route/shape cũ (`invitations`, `groupRoster`, `myAvailability`, `resendInvitation`,
`useScheduleVersions`...) với id số kiểu cũ, quy đổi qua `Number(roundId)` tại chỗ dùng — sẽ
migrate đúng khi tới Phase 3/4. `tsc --noEmit` + `eslint` sạch.

**Câu hỏi cần chốt với BE (chưa có trong spec)**:
- Không có `PATCH /rounds/:roundId` nào — tính năng "Chỉnh sửa cấu hình" sau khi tạo Round
  hiện bị vô hiệu hoá (báo "chưa có trong spec BE"), giống tình huống Project ở Phase 1.
- Chưa có endpoint transition rõ ràng cho `REGISTRATION_CLOSED → SCHEDULING`,
  `SCHEDULED → PUBLISHED`, `COMPLETED → LOCKED` — spec §57–61/§69–70 mô tả luồng Readiness/
  Generate/Publish riêng chứ không phải một transition endpoint chung; CTA cho các trạng thái
  này đang tạm vô hiệu hoá, sẽ nối đúng khi làm Phase 4/6.

---

## Phase 3 — Invitation / Availability / Group Preference (luồng đăng ký)

**Điều kiện bắt đầu**: BE deploy `InvitationModule`, `AvailabilityModule`, `GroupPreferenceModule`.

**Thay thế**: phần "Mời giảng viên"/"Nhập lịch rảnh hộ" trong `round-detail-page.tsx`,
toàn bộ luồng Lecturer Accept/Decline, Leader chọn slot ưu tiên.

**Domain mới**:
- `RoundInvitationStatus` thêm `EXPIRED`, `WITHDRAWN` (hiện tại chỉ có PENDING/ACCEPTED/REJECTED).
- Rule mới: "ACCEPTED nhưng không nộp availability → coi như BUSY ALL" (BE tự suy ra, FE
  chỉ hiển thị cảnh báo, không tự tính).
- `PreferredLoad` gửi kèm trong availability payload (không phải field riêng như hiện tại).
- Group Preference tách khỏi Availability — Leader chọn `timeslotIds` cho nhóm, khác hẳn
  "Nhập lịch rảnh hộ" hiện tại (đó là của giảng viên).
- Registration Dashboard (`GET /rounds/:id/registration-summary`) và Scheduling Readiness
  (`GET /rounds/:id/scheduling-readiness`) là 2 màn hình mới, chưa có ở FE.

**[ĐÃ LÀM — 2026-08-19]** `fetchRounds.ts` thêm `invitations`/`invite`/`remindInvitation`
(spec §22/§53), `eligibleProjects` (spec §23/§48, thay hẳn `groupRoster` cũ), `registrationSummary`
(spec §24). `round-detail-page.tsx` tab Giảng viên đổi sang `RoundInvitation` mới (bỏ cột "Mức
tải" vì `preferredLoad` giờ nằm trong payload `PUT availability/me`, không còn trả về ở list
invitation); tab Nhóm tham gia đổi sang join `eligible-projects` với danh sách Group đã có từ
Phase 1 (lấy code/leader/memberCount) thay vì gọi route roster riêng. Tab Tổng quan đổi sang
đọc số liệu thẳng từ `registrationSummary` thay vì tự đếm từ mảng invitations. Xoá hẳn nút
"Nhập hộ" + `SubmitAvailabilityDialog` — spec không có endpoint Manager nhập lịch rảnh/slot ưu
tiên hộ người khác, chỉ có 2 endpoint self-service: `PUT /rounds/:id/availability/me` (Lecturer)
và `PUT /rounds/:id/groups/:groupId/preferences` (Leader) — cả hai thuộc luồng Lecturer/Leader
portal (Phase 9), không phải Manager. `INVITATION_STATUS_META` thêm `EXPIRED`/`WITHDRAWN`, đổi
`REJECTED`→`DECLINED`. `tsc --noEmit` + `eslint` sạch.

**Chưa làm trong phase này (cố tình, thuộc phạm vi khác)**:
- Lecturer Respond (`POST /rounds/:id/invitations/me/respond`) — thuộc Lecturer portal (Phase 9).
- Availability/Group Preference self-service form — thuộc Lecturer/Leader portal (Phase 9).
- Scheduling Readiness (`GET /rounds/:id/scheduling-readiness`) — để dành cho Phase 4 vì nó
  trực tiếp gate nút "Generate" (`POST .../schedules/generate`), thuộc luồng Scheduling.

**Câu hỏi cần chốt với BE**: Manager có thật sự không có cách nào nhập lịch rảnh/slot ưu tiên
hộ giảng viên/nhóm quên đăng ký nữa không (BR-AVL-04 cũ), hay endpoint đó sẽ được bổ sung sau?
Đây là tính năng đã có ở FE hiện tại và có thể là gap thật của spec chứ không phải chủ đích.

---

## Phase 4 — Scheduling (CP-SAT) & ScheduleVersion

**Điều kiện bắt đầu**: BE deploy solver mới (không có Room trong constraint) +
`SchedulingModule`.

**Thay thế**: tab "Xếp lịch" trong `round-detail-page.tsx`, `fetchScheduling.ts` phần
generate/versions, `calendar-page.tsx`.

**Domain mới**:
- `ScheduleVersionStatus`: `DRAFT → ACTIVE → PUBLISHED`, hoặc `DISCARDED` — khác hẳn
  `VALID/PUBLISHED/SUPERSEDED` hiện tại.
- Actions riêng: `set-active`, `discard` (hiện tại chỉ có `activate`).
- Response `generate` trả kèm `scores` breakdown (`workload/continuity/compactness`) và
  `unscheduledCount` + lý do (`UnscheduledReason` enum 9 giá trị) — cần UI hiển thị chẩn đoán
  chi tiết hơn hiện tại (hiện chỉ có `unscheduled: [{group_id, reason}]` dạng tự do).
- `roomId = null` khi Session mới materialize — Room gán ở **Phase 5**, không cùng lúc.

**[ĐÃ LÀM — 2026-08-19]** `fetchScheduling.ts` thêm `readiness`/`generate`/`roundScheduleVersions`/
`setActiveVersion`/`discardVersion` (spec §25/§26/§57/§58/§64) — đặt tên khác các hàm cũ
(`run`/`versions`/`activate`) thay vì sửa tại chỗ. `round-detail-page.tsx` tab Xếp lịch đổi
hoàn toàn: gate nút "Chạy xếp lịch" theo `readiness.ready` + hiện `blockingIssues`/`warnings`
thay vì chỉ disable im lặng; bảng phương án đổi cột (Đã xếp/Chưa xếp thay vì chỉ điểm), dropdown
đổi "Kích hoạt"/"Loại bỏ" (set-active/discard) thay vì "Kích hoạt"/"Công bố lịch" cũ — Công bố
dời hẳn sang Phase 6 (đã có nút riêng nhưng disabled từ Phase 2). `ROUND_SCHEDULE_VERSION_STATUS_META`
mới (4 trạng thái) tách khỏi `SCHEDULE_VERSION_STATUS_META` cũ.

**Quyết định phạm vi lại so với kế hoạch ban đầu**: **`calendar-page.tsx` KHÔNG đụng trong phase
này**, dù kế hoạch gốc liệt kê nó ở Phase 4. Lý do: trang đó là grid Session × Room, nhưng Room
chưa tồn tại tới hết Phase 5 (`roomId` luôn `null` sau `set-active` theo spec §64) — sửa nửa vời
rồi phải sửa lại toàn bộ khi làm Room Assignment là lãng phí. Nút "Mở trên Lịch đánh giá" cũng bị
bỏ khỏi tab Xếp lịch vì phương án mới dùng id dạng chuỗi (`sv_03`), không tương thích ngay với
`calendar-page.tsx` đang chọn version bằng id số cũ. `calendar-page.tsx` sẽ gộp chung vào Phase 5.

**Câu hỏi cần chốt với BE**: `GET /rounds/:roundId/schedules` (danh sách phương án) không có
JSON mẫu trong spec — trường `scheduledCount`/`unscheduledCount`/`overallScore`/`createdAt` ở
`RoundScheduleVersionItem` là suy luận từ response của `generate` (§58) + UI mock bảng (§26),
cần BE xác nhận đúng tên field.

---

## Phase 5 — Room Assignment (màn hình hoàn toàn mới)

**Điều kiện bắt đầu**: BE deploy `RoomModule` + `RoomAssignmentModule`. Phụ thuộc Phase 4
xong trước (cần có Session `PLANNED` với `roomId = null`).

**Thay thế**: `calendar-page.tsx` (dời từ Phase 4 sang đây — xem ghi chú "Quyết định phạm vi
lại" ở Phase 4) + màn Room Assignment mới hoàn toàn, FE hiện tại chưa có khái niệm Room/RoomType
ở đâu cả.

**Việc cần làm từ đầu**:
- `RoomModule` CRUD (`RoomType`, `RoomStatus: ACTIVE/MAINTENANCE/INACTIVE`) — màn hình quản
  lý phòng (khác `components/rooms/` hiện tại, vốn không có `type`/nghiệp vụ maintenance).
- Grid gán phòng theo timeslot × room (giống UI mẫu trong spec §28), có khu "Chưa gán".
- Suggest Rooms + Apply Suggestions (gợi ý tự động, không ảnh hưởng điểm solver).

**[ĐÃ LÀM — 2026-08-19]** `fetchRoomAssignment.ts` (file mới) + `useRoomAssignment.ts`: `sessions`
(spec §27, nguồn cho grid), `availableRooms`/`assignRoom`/`suggestRooms`/`applySuggestions`
(spec §28/§65-68). Route mới `/manager/rounds/:roundId/room-assignment` — chọn ngày, hiển thị
grid Room × Timeslot lấy từ `round.days` (đã có sẵn từ Phase 2, không cần gọi thêm), khu
"Chưa gán" liệt kê session `roomId=null` trong ngày, click vào để mở dialog chọn phòng còn
trống theo timeslot đó. Nút "Gợi ý gán phòng" tính trước (preview số lượng), "Áp dụng gợi ý"
mới commit thật. Menu "Gán phòng" trong tab Xếp lịch của `round-detail-page.tsx` giờ link thẳng
sang trang này (trước đó là `notImplemented`), chỉ bật khi phương án đang `ACTIVE`.
`ROUND_SESSION_STATUS_META` mới (6 trạng thái theo spec §7) tách khỏi `SESSION_STATUS_META` cũ.
`tsc --noEmit` + `eslint` sạch.

**Cố tình chưa làm (thu hẹp phạm vi so với kế hoạch gốc)**:
- **`RoomModule` CRUD không đụng tới** — spec hoàn toàn không có route Create/List Room nào
  (chỉ có "Available Rooms" để *đọc*, không có POST tạo phòng hay PATCH đổi `status`). Trang
  `/manager/rooms` hiện tại (`fetchRooms.ts`, model `code/name/capacity/active`, không có
  `type`) giữ nguyên, không map sang `RoomType`/`RoomStatus` mới vì chưa có cơ sở.
- **`calendar-page.tsx` vẫn chưa đụng**, dù kế hoạch đã dời nó vào phase này. Lý do thực tế:
  Draft Calendar (spec §27, xem toàn bộ session mọi phòng cùng lúc, có postpone/edit) và Room
  Assignment (spec §28, chỉ gán phòng cho session chưa có phòng) là hai màn hình tách biệt trong
  spec — đã làm xong màn Room Assignment như một trang riêng thay vì vá vào trang Calendar cũ
  vốn đang gánh cả session-edit/publish/drag-drop (Phase 6/7). `calendar-page.tsx` dời tiếp
  sang khi làm Phase 7 (Post-publish ops), vì đó là lúc các thao tác edit-session của nó thật
  sự cần dùng tới.

**Câu hỏi cần chốt với BE**:
- Room CRUD (tạo/sửa/đổi status phòng) thật sự không có trong scope BE, hay chỉ chưa liệt kê
  trong tài liệu này? Nếu Manager cần tự thêm phòng mới, cần endpoint.
- `POST .../rooms/suggest` trả về danh sách gợi ý hay tự lưu tạm rồi `apply-suggestions` chỉ
  cần gọi suông không kèm id? Đã giả định trả `RoomSuggestion[]` để preview số lượng trước khi
  áp dụng — cần BE xác nhận request/response thật.

---

## Phase 6 — Publish

**Điều kiện bắt đầu**: Phase 4 + 5 xong (`publish-readiness` cần `allSessionsHaveRoom`).

**Thay thế**: nút "Công bố lịch" trong `round-detail-page.tsx`/`fetchScheduling.ts`.

**Domain mới**: Publish Readiness check riêng (`activeVersion`, `allSessionsHaveTimeslot`,
`allSessionsHaveCouncil`, `allSessionsHaveRoom`, `roomConflicts == 0`) hiển thị danh sách
lỗi cụ thể trước khi cho bấm Publish — hiện tại chỉ disable nút không có, không giải thích.

**[ĐÃ LÀM — 2026-08-19]** `fetchScheduling.ts` thêm `publishReadiness`/`publishRound` (spec
§29/§69/§70). Nút "Công bố lịch" ở header `round-detail-page.tsx` (trước đây disabled từ
Phase 2/4) giờ mở `PublishDialog` — liệt kê từng điều kiện (`activeVersion`,
`allSessionsHaveTimeslot`, `allSessionsHaveCouncil`, `allSessionsHaveRoom`, `roomConflicts`)
kèm dấu Đạt/Chưa đạt theo màu, nút "Xác nhận công bố" chỉ bật khi `ready === true`. Sau publish:
Round `SCHEDULED→PUBLISHED`, Version `ACTIVE→PUBLISHED`, Session `PLANNED→SCHEDULED` (BE tự làm,
FE chỉ refetch). `tsc --noEmit` + `eslint` sạch.

**Câu hỏi cần chốt với BE**: response `GET /rounds/:roundId/publish-readiness` không có JSON
mẫu trong spec — cấu trúc `{ ready, checks: {...} }` là suy luận từ danh sách "Checks" trong
§69, cần xác nhận đúng tên field (đặc biệt `roomConflicts` là số hay boolean).

---

## Phase 7 — Post-publish operations

**Điều kiện bắt đầu**: Phase 6 xong.

**Thay thế**: `session-drawer.tsx` (Thay reviewer, đổi phòng), `useEditSession`/
`useControlledChangeSession`/`usePostponeSession` trong `useScheduling.ts` — **toàn bộ
logic "sửa session" hiện tại dựa trên generic `editSession`/`controlledChangeSession` sẽ
bị thay bằng 3 action endpoint tách riêng**: `change-room`, `replace-reviewer`, `postpone`.

**Domain mới quan trọng**: `Council` là **immutable** — đổi reviewer không sửa Council cũ,
mà tạo Council mới rồi gán `session.councilId` trỏ sang. Postpone không sửa Session cũ
thành giờ mới — tạo Session `makeup` mới với `makeupOfSessionId` trỏ về bản gốc, Session gốc
chuyển `POSTPONED` và **giữ nguyên** (không xoá, không update giờ).

**[ĐÃ LÀM — 2026-08-19]** `fetchScheduling.ts` thêm `changeSessionRoom`/`replaceSessionReviewer`/
`postponeRoundSession`/`createMakeupSession` (spec §71-73), tên riêng để không đụng các hàm cũ
(`editSession`/`controlledChangeSession`/`publish` — giờ không còn nơi nào gọi tới, xem mục dọn
dẹp bên dưới). `calendar-page.tsx` viết lại hoàn toàn để lấy dữ liệu từ chuỗi hook Phase 4/5 đã
migrate (`useRounds`, `useRoundDetail`, `useRoundScheduleVersions`, `useRoundSessions`,
`useAvailableRooms`) thay vì `useScheduleVersions`/`useScheduleVersion` cũ. **Bỏ hẳn tính năng
kéo-thả đổi timeslot** — spec không có action nào cho phép đổi giờ một session sau khi đã có
lịch (chỉ đổi phòng/đổi reviewer/hoãn), nên kéo-thả giờ chỉ còn tác dụng đổi phòng (kéo giữa các
cột phòng cùng hàng giờ) → mở `ReasonDialog` xác nhận → gọi `change-room`. `session-drawer.tsx`
viết lại 3 action riêng: Đổi phòng (chọn phòng khác + lý do), Thay reviewer (chọn reviewer cũ
trong council + reviewer mới + lý do — UI note rõ council cũ được giữ nguyên), Hoãn buổi (chỉ
lý do, không chọn giờ mới — đúng rule "giữ nguyên buổi gốc"). Nút "Công bố lịch" trên trang
Calendar bị **bỏ hẳn** (trùng với luồng Publish chuẩn đã làm ở Phase 6 trên `round-detail-page.tsx`,
giữ 2 nơi publish dễ lệch trạng thái). `ROUND_SESSION_STATUS_META` (Phase 5) được tái dùng ở đây.
`tsc --noEmit` + `eslint` sạch.

**Dọn dẹp còn nợ (không làm trong phase này, để tránh rủi ro ngoài phạm vi)**: `useEditSession`,
`useControlledChangeSession`, `usePublishVersion` (hooks) và các hàm `fetchScheduling.editSession`/
`controlledChangeSession`/`publish`/`activate`/`versions`/`versionDetail`/`run` (service) giờ
**không còn nơi nào trong FE gọi tới** — an toàn để xoá hẳn, nhưng để dành cho đợt dọn dẹp cuối
cùng (cùng lúc dọn `core.ts`) theo đúng nguyên tắc đã thống nhất từ đầu phiên làm việc, thay vì
xoá rải rác từng phase.

**Câu hỏi cần chốt với BE**: `POST /sessions/:sessionId/makeup` hoàn toàn không có JSON mẫu
trong spec. Đã giả định payload `{date, timeslotId, roomId?}` (Session bù cần một lịch mới) và
**chưa nối UI cho hành động này** — sau khi Hoãn buổi, FE hiện chưa có nút "Tạo buổi bù" vì
không đủ cơ sở để thiết kế form đúng cho tới khi BE xác nhận payload thật.

---

## Phase 8 — Result & Progression

**Điều kiện bắt đầu**: BE deploy `ResultModule` + `ProgressionModule` + `RemediationModule`.

**Thay thế**: `useResults.ts`, `fetchResults.ts`, `results-page.tsx` (Manager),
`lecturer-results.tsx` (Lecturer).

**Domain mới**:
- Payload Result tách theo loại: Review (`{result: PASS/NEEDS_FIX/FAIL, note}`) vs Defense
  (`{result: LEVEL_1..4, note, remediation?: {deadline, verifierId}}`) — khác `outcome` phẳng
  hiện tại.
- Progression tự động theo bảng cố định (`D1.1 LEVEL_1 → ELIGIBLE_D12`, `LEVEL_2 →
  D12_CONDITIONAL + Remediation`, ...) — **BE tính, FE chỉ hiển thị + refetch**.
- Remediation Verify (`POST /remediations/:id/verify`) — action mới, PASS thì
  `D12_CONDITIONAL → ELIGIBLE_D12`.

**[ĐÃ LÀM — 2026-08-19]** `fetchResults.ts` thêm `submitSessionResult` (payload tách Review/Defense
theo spec §74, tên riêng khác `submitResult`/`ResultPayload` cũ vì không nơi nào trong FE đang
gọi hàm cũ — xem mục dọn dẹp) và `verifyRemediation` (spec §76). `fetchProjects.ts` thêm
`getById`/`progression`/`results` (spec §18). **Route mới `/manager/projects/:projectId`** —
trang chi tiết đề tài hoàn toàn chưa có ở FE trước đây, với 4 tab: Tổng quan, Nhóm, Tiến độ
(timeline Review/Defense + block Remediation nếu đang khắc phục), Kết quả (danh sách kết quả
từng buổi). Danh sách đề tài (`/manager/projects`) giờ link mã đề tài sang trang này.
`tsc --noEmit` + `eslint` sạch.

**Phát hiện quan trọng — mismatch giữa `/manager/results` hiện tại và spec mới**: Spec **không
có bất kỳ endpoint Manager nào cho danh sách case khắc phục hàng loạt** (`GET /remediation`) hay
"đánh dấu FAILED do quá hạn" (`overdue-fail`) — theo bảng Screen → API Mapping (§XVII), "Verify
Remediation" chỉ thuộc **Lecturer** (`POST /remediations/:id/verify`), và Manager chỉ thấy kết
quả/tiến độ qua Project Detail (§18) — đúng như đã build ở trên. Trang `/manager/results` hiện
tại (danh sách case khắc phục toàn học kỳ + nút "Đánh dấu FAILED") **không có chỗ đứng tương ứng
trong spec mới** — cố tình **giữ nguyên, không sửa/xoá**, vì:
1. Không đủ cơ sở để đoán Manager có thật sự mất hẳn quyền này hay spec chỉ chưa liệt kê.
2. Xoá một trang đang chạy được (dù chưa migrate) khi không chắc BE có ý định thay thế nó bằng
   gì là rủi ro hơn giữ nguyên.

**Câu hỏi cần chốt với BE (quan trọng)**: `/manager/results` (danh sách case khắc phục quá hạn
+ "Đánh dấu FAILED") có tương đương trong kiến trúc mới không? Nếu không, Manager làm sao xử lý
hàng loạt case khắc phục quá hạn — duyệt qua từng Project Detail một cách thủ công, hay cần bổ
sung endpoint `GET /remediations?semesterId=` mới cho Manager?

**Dọn dẹp còn nợ (không làm trong phase này)**: `fetchResults.submitResult`/`ResultPayload`/
`SessionResultResponse` (hooks `useSubmitResult`/`useSessionResult`) hiện **không còn nơi nào
trong FE gọi tới** (đã kiểm tra trước khi viết `submitSessionResult` mới) — gộp vào đợt dọn dẹp
cuối cùng cùng với các hàm chết từ Phase 7.

---

## Phase 9 — Lecturer & Leader (Student) portal

**Điều kiện bắt đầu**: các phase Manager tương ứng (3, 4, 7, 8) đã xong phần API mà
Lecturer/Leader tiêu thụ chung.

**Thay thế**: toàn bộ `app/(lecturer)/**`, và role hiện tại tên "Student" cần đối chiếu với
"Project Leader" trong spec — **[ĐÃ CHỐT]** `lib/types/roles.ts` đã tự trả lời câu hỏi này
trước cả khi hỏi: hệ thống chỉ có 4 role tài khoản (`ADMIN/MANAGER/LECTURER/STUDENT`), và
`CONTEXT_ROLE_PROJECT_LEADER` được định nghĩa rõ là **role theo ngữ cảnh** (suy ra từ dữ liệu —
Student nào đang là Leader active của nhóm — không gán cứng trên tài khoản). Vậy "Project
Leader" trong spec = role `STUDENT` hiện tại, route group `app/(student)/**` chính là Leader
portal của spec §37-40, không phải role thứ 5.

**Domain mới đáng chú ý**: Leader dashboard **không** được thấy `ScheduleVersion`, `Soft
Score`, `Quota`, dữ liệu nội bộ solver — cần rà lại xem FE Student hiện tại có lỡ hiển thị
gì thuộc nhóm này không (rounds-page/calendar hiện tại đang expose cho Manager, cần đảm bảo
không leak sang Student).

**Khác biệt quan trọng so với Phase 0-8**: toàn bộ `app/(lecturer)/**` và `app/(student)/**`
hiện tại chạy 100% trên `mock-data.ts` tĩnh (đã tự đánh dấu TODO "thay bằng dữ liệu thật khi
backend sẵn sàng") — không phải code đã nối API cần đổi shape như Manager. Sidebar theo spec
§30 (Lời mời, Đăng ký lịch rảnh, Nhóm hướng dẫn, Phiên đánh giá, Khắc phục) cũng khác cấu trúc
nav cũ (dashboard/results/schedule/supervised-groups). Đã hỏi ý kiến user và thống nhất: làm
theo từng lát nhỏ, không làm hết Phase 9 trong một lần.

**[ĐÃ LÀM — sub-phase 9a, 2026-08-19] Lecturer Invitations + Availability (spec §31/§32/§54/§55)**
- `fetchLecturerPortal.ts` (file mới): `invitations`, `respondInvitation`, `availability`,
  `submitAvailability`.
- `hooks/lecturer/useLecturerPortal.ts` (thư mục hook mới cho Lecturer, song song `hooks/manager/`).
- `app/(lecturer)/lecturer/_shared/{status-dot,labels}.ts` — bản local cho Lecturer, không
  import chéo sang `(manager)/manager/_shared` (hai route group nên tách biệt).
- Route mới `/lecturer/invitations` — danh sách lời mời, Nhận lời / Từ chối (bắt buộc lý do).
- Route mới `/lecturer/availability` (danh sách đợt đã ACCEPTED) → `/lecturer/availability/:roundId`
  (grid ngày × giờ chọn timeslot rảnh + Mức tải mong muốn, submit `PUT availability/me`).
- `app/(lecturer)/lecturer/dashboard` nối thật số lời mời đang chờ thay vì text tĩnh "chưa có dữ liệu".
- Thêm 2 mục nav "Lời mời"/"Đăng ký lịch rảnh" vào sidebar Lecturer trong `app-shell.tsx`.
- `tsc --noEmit` + `eslint` sạch.

**Chưa làm (để dành sub-phase sau)**: Lecturer Schedule (`/lecturer/schedule`, spec §33 — vẫn
mock), Supervised Groups (§34 — vẫn mock), Session Result (§35), Remediation (§36), toàn bộ
Leader/Student portal (§37-40).

**Câu hỏi cần chốt với BE**: response JSON của `GET /lecturer/me/invitations` và
`GET/PUT /rounds/:roundId/availability/me` không có mẫu trong spec — các field đã dùng
(`round.name/type/registrationDeadline`, `slots[].date/startTime/endTime/available`) là suy
luận hợp lý từ UI mock (§30-32), cần BE xác nhận tên field thật.

**[ĐÃ LÀM — sub-phase 9b, 2026-08-19] Lecturer Schedule + Session Result (spec §33/§35/§74)**
- `fetchLecturerPortal.ts` — thêm `mySessions(params)` (GET `/lecturer/me/sessions`, params
  `roundId/dateFrom/dateTo/role/status`) và `sessionDetail(sessionId)` (GET `/sessions/:sessionId`).
  Type `LecturerScheduleSession`/`LecturerSessionDetail` tự suy ra field (xem câu hỏi BE bên dưới).
  Submit kết quả tái dùng `fetchResults.submitSessionResult` đã có sẵn từ Phase 8 (cùng route
  `POST /sessions/:sessionId/result`, không cần thêm hàm mới).
- `hooks/lecturer/useLecturerPortal.ts` — thêm `useLecturerSessions`, `useLecturerSessionDetail`,
  `useSubmitLecturerSessionResult` (wrap lại hook Manager Phase 8 nhưng invalidate cache theo
  key `["lecturer", ...]` thay vì `["manager", ...]`).
- `app/(lecturer)/lecturer/schedule/components/` — xoá `mock-data.ts`, thay bằng `types.ts`
  (giữ nguyên shape `LecturerSession` cũ để không phải sửa lại `session-row/time-grid/
  schedule-list-view/build-ics`, chỉ đổi nguồn dữ liệu qua hàm `toLecturerSession()` map từ
  DTO API). Bỏ khái niệm `isOnline` (không có trong domain model — Room chỉ có
  `type: NORMAL/SEMINAR/LAB`, không có "online"). `SessionStatus` đổi theo đúng enum domain
  spec §7 (`SCHEDULED/COMPLETED/POSTPONED/GROUP_ABSENT/CANCELLED`, bỏ `ONGOING` không có trong
  spec, thêm `GROUP_ABSENT`).
- `lecturer-schedule.tsx` — nối `useLecturerSessions()` thay vì mảng mock tĩnh, thêm trạng thái
  loading/error.
- Route Session Result: **không tạo trang riêng** — spec sidebar §30 có mục "Phiên đánh giá"
  tách biệt nhưng để tránh nhân đôi logic fetch-sessions trong 1 lát nhỏ, đã gắn hành động
  "Nhập kết quả" ngay trong `SessionRow` (mở rộng row) khi `myRole === RESULT_OWNER` và status
  cho phép nhập (`SCHEDULED`/`COMPLETED`) → mở `SessionResultDialog` mới, tự fetch
  `sessionDetail` khi mở. Form tách 2 nhánh theo `roundKind`: Review (PASS/NEEDS_FIX/FAIL) và
  Defense (LEVEL_1-4, LEVEL_2 bắt buộc `remediation.deadline` + `remediation.verifierId` theo
  spec §35/§74). Route `/lecturer/results` (nav "Nhập kết quả", mock cũ) **giữ nguyên chưa đụng**
  — đó là UI cho §36 Remediation, chưa nằm trong lát này.
- Label mới: `REVIEW_RESULT_META`/`DEFENSE_RESULT_META` thêm vào `app/(lecturer)/lecturer/_shared/labels.ts`.
- `tsc --noEmit` + `eslint` sạch. **Chưa test qua browser thật** (không có dev server chạy sẵn
  trong phiên này) — chỉ verify qua type-check/lint, nên coi phần UI runtime là "chưa xác nhận
  bằng mắt", cần user tự chạy `npm run dev` kiểm tra lại giao diện trước khi merge.

**Quyết định suy luận cần BE xác nhận (chưa có trong spec, đã tự chọn hướng)**:
1. `GET /lecturer/me/sessions` và `GET /sessions/:sessionId` không có JSON mẫu — field đặt theo
   pattern `DisplaySession` đã dùng ở Manager Calendar (Phase 7): `round{id,name,type}`,
   `group{id,code,projectTitle}`, `date/startTime/endTime` tách riêng, `roomCode`, `myRole`,
   `council[]`, `status`.
2. **Người xác nhận (verifier) cho remediation LEVEL_2**: spec chỉ nói `verifierId required`,
   không nói verifier lấy từ đâu. Đã chọn suy luận: verifier là một thành viên trong chính
   `council` của session đó (hội đồng đã chấm), không phải danh sách toàn bộ giảng viên hệ
   thống — vì `fetchLecturers.list()` hiện có là API cũ (ADMIN/MANAGER only, ID số, không rõ
   Lecturer có quyền gọi hay không). Nếu BE có endpoint riêng cho verifier (có thể không giới
   hạn trong hội đồng), cần đổi lại `DefenseForm` trong `session-result-dialog.tsx`.

**[ĐÃ LÀM — sub-phase 9c, 2026-08-19] Lecturer Supervised Groups (spec §34)**
- `fetchLecturerPortal.ts` — thêm `supervisedProjects()` (GET `/lecturer/me/supervised-projects`)
  và type `SupervisedProject` theo đúng field list trong spec §34 (Group/Project/Leader/Member
  Count/Project Status/Next Evaluation/Latest Result/Remediation) + `supervisorRole` (MAIN/CO,
  suy luận thêm từ enum `SupervisorRole` §3 để phân biệt GVHD chính/đồng hướng dẫn trên UI).
- `hooks/lecturer/useLecturerPortal.ts` — thêm `useSupervisedProjects()`.
- **Thay đổi hành vi quan trọng so với UI mock cũ**: spec ghi rõ màn này "Không có membership
  management" — đã **bỏ hẳn** tính năng "Chỉ định trưởng nhóm" (`AssignLeaderPopover`) từng có
  trong mock. Đổi Leader vẫn chỉ làm được ở Manager (`POST /groups/:id/actions/change-leader`,
  đã có từ Phase 1), Lecturer chỉ xem, không sửa.
- **Đơn giản hoá UI so với mock cũ**: mock cũ hiển thị ma trận đầy đủ Review 1/Review 2/Defense
  1.1 theo từng cột (`rounds[]` mảng). Spec §34 chỉ liệt kê field đơn `Next Evaluation` và
  `Latest Result` (số ít, không phải mảng lịch sử) — không có API progression riêng cho màn
  Lecturer như Manager Project Detail (`GET /projects/:id/progression`, Phase 8). Đã đổi UI
  theo đúng field list spec thay vì cố giữ ma trận cũ; nếu BE có ý định cho xem lại lịch sử đầy
  đủ ở màn Lecturer thì cần bổ sung field/endpoint, không suy diễn thêm.
- Xoá `mock-data.ts`, `round-progress.tsx`, `assign-leader-popover.tsx` (không còn dùng); viết
  lại `tone.ts` dùng chung `StatusTone` từ `_shared/status-dot.tsx`.
- Thêm `PROJECT_STATUS_META`, `REMEDIATION_STATUS_META` vào `_shared/labels.ts`.
- `tsc --noEmit` + `eslint` sạch. Chưa test qua browser (lý do như sub-phase 9b).

**Câu hỏi cần chốt với BE**: `GET /lecturer/me/supervised-projects` không có JSON mẫu trong
spec — toàn bộ field trong `SupervisedProject` (kể cả cấu trúc lồng `group.leader`,
`nextEvaluation`, `latestResult`, `remediation`) là suy luận từ mục "Fields" liệt kê trong §34,
cần BE xác nhận tên field thật và có đúng là dữ liệu single-value (không phải mảng lịch sử) hay
không.

**[ĐÃ LÀM — sub-phase 9d, 2026-08-19] Remediation (spec §36) — hoàn tất Phase 9 phần Lecturer**
- `fetchLecturerPortal.ts` — thêm `remediations()` (GET `/lecturer/me/remediations`) và type
  `LecturerRemediation`. Verify tái dùng `fetchResults.verifyRemediation` đã có từ Phase 8
  (cùng route `POST /remediations/:remediationId/verify`, không cần hàm mới).
- `hooks/lecturer/useLecturerPortal.ts` — thêm `useLecturerRemediations()`,
  `useVerifyLecturerRemediation()` (wrap hook Manager Phase 8, invalidate cache
  `["lecturer","remediations"]` + `["lecturer","supervised-projects"]`).
- **Gộp lại route `/lecturer/results`**: mock cũ trộn 2 việc trong 1 trang — "Phiên cần nhập
  kết quả" (trùng với §35, đã làm ở sub-phase 9b dưới dạng dialog ngay trong Lịch của tôi) và
  "Xác nhận khắc phục" (§36). Vì sidebar theo spec §30 không có mục "Nhập kết quả" riêng, chỉ
  có "Phiên đánh giá" (đã map vào §35) và "Khắc phục" (§36) — đã **bỏ hẳn phần nhập kết quả
  trùng lặp**, đổi route `/lecturer/results` thành thuần màn Khắc phục, đổi tiêu đề trang +
  nhãn nav trong `app-shell.tsx` từ "Nhập kết quả" → "Khắc phục" cho khớp spec. Xoá
  `mock-data.ts`, `result-entry-row.tsx`, `segmented-picker.tsx`, `tone.ts` (không còn dùng).
- Thêm `toneBadgeClass` (badge màu theo `StatusTone`) vào `_shared/status-dot.tsx` để dùng
  chung, tránh định nghĩa lại ở từng route con.
- `tsc --noEmit` + `eslint` sạch. Chưa test qua browser (lý do như các sub-phase trước).

**Câu hỏi cần chốt với BE**: `GET /lecturer/me/remediations` không có JSON mẫu — field suy
luận đơn giản (mỗi case gắn 1 Group, deadline, status) vì domain nói verifier chính là
Lecturer hiện tại (được chỉ định lúc submit result Defense 1.1 LEVEL_2, §74), nên không cần
field verifier riêng như bên Manager remediation list. Cần BE xác nhận field thật, đặc biệt có
trả kèm `roundType`/`sessionId` gốc hay không (hiện FE không cần nhưng có thể hữu ích để link
ngược lại session).

**Phase 9 — Lecturer coverage hiện tại**: §31 Invitations ✅, §32 Availability ✅, §33 My
Schedule ✅, §34 Supervised Groups ✅, §35 Session Result ✅ (dialog trong Lịch của tôi), §36
Remediation ✅.

**[ĐÃ LÀM — sub-phase 9e, 2026-08-19] Project Leader — Dashboard + Group Preference (spec §37/§38/§39)**
- Trước đó (turn trước) đã sửa 2 chỗ lộ ScheduleVersion/Quota trong `student/schedule/
  components/session-detail-panel.tsx` (patch nhỏ, chưa nối API — xem sub-phase note cũ).
- `lib/api/services/fetchLeaderPortal.ts` (file mới): `dashboard()` (GET `/leader/me/dashboard`,
  spec §38), `groupPreferences()`/`submitGroupPreferences()` (GET/PUT
  `/rounds/:roundId/groups/:groupId/preferences`, spec §39/§56), `mySessions()` (GET
  `/leader/me/sessions`, spec §40 — **khai báo type nhưng chưa dùng ở UI, để dành sub-phase
  sau** vì `student/schedule` hiện vẫn còn nguyên UI/mock cũ theo đúng yêu cầu "UI giữ nguyên"
  của user, chỉ patch 2 dòng lộ dữ liệu, chưa migrate toàn bộ sang API thật).
- `hooks/student/useLeaderPortal.ts` (thư mục hook mới cho Student/Leader, song song
  `hooks/lecturer/`): `useLeaderDashboard`, `useGroupPreferences`, `useSubmitGroupPreferences`,
  `useLeaderSessions` (khai báo sẵn, chưa dùng).
- `app/(student)/student/_shared/{status-dot,labels}.ts` — bản local cho Student, không import
  chéo sang `(lecturer)/lecturer/_shared` dù nội dung tương tự (đúng convention đã theo suốt
  từ Phase 9a).
- **Dashboard (`/student/dashboard`) viết lại hoàn toàn** theo đúng field list §38 (Group Code,
  Project, Main/Co-Supervisor, Member Count, Project Status, Current Round, Preference Status,
  Deadline, Upcoming Session, Latest Result, Remediation Status) — **bỏ hẳn** UI cũ
  (`HorizontalTimeline`/`RoundTimeline`/`GroupMembers` roster đầy đủ) vì đó là dữ liệu
  progression **không nằm trong field list §38** và không có API progression riêng cho Leader
  (khác Manager Project Detail §18 có `GET /projects/:id/progression`). Cùng lý do đã áp dụng
  cho Lecturer Supervised Groups (sub-phase 9c) — bám đúng field spec thay vì giữ UI cũ rồi tự
  suy diễn thêm cột. Đã xoá `mock-data.ts`, `group-members.tsx`, `horizontal-timeline.tsx`,
  `round-timeline.tsx`, `round-entry.tsx`, `status-line.tsx`, `remediation-status.tsx`, `tone.ts`
  cũ; giữ lại `copy-group-code-button.tsx`, thêm `detail-row.tsx` + `remediation-banner.tsx` mới.
- **Route mới `/student/preferences`** (spec §39, trước đây hoàn toàn không tồn tại — gap lớn
  nhất đã nêu) — landing page dựa trên `currentRound`/`preferenceStatus` của Dashboard (spec
  không có endpoint "list rounds cần preference" riêng cho Leader nên dùng lại field đã có ở
  §38) → `/student/preferences/:roundId` — grid ngày × giờ chọn timeslot, submit
  `PUT preferences`. Cùng pattern grid đã dùng cho Lecturer Availability (sub-phase 9a).
- **Sidebar Student** trong `app-shell.tsx` đổi từ 2 mục (Tổng quan, Lịch nhóm) thành đủ 4 mục
  theo spec §37: Tổng quan, **Đăng ký lịch** (mới), Lịch của nhóm, **Kết quả** (mới, xem note
  dưới).
- **Route mới `/student/results`** — spec §37 liệt kê "Kết quả" trong sidebar nhưng **không có
  mục §38-40 nào mô tả API/field riêng cho màn này** (khác hẳn Manager/Lecturer, cả hai đều có
  endpoint result rõ ràng). Không suy đoán field — dựng trang stub giải thích rõ lý do, trỏ
  người dùng tạm về Tổng quan (đã có field "Latest Result" từ §38). Đây là gap cần BE xác nhận,
  không phải lỗi FE.
- `tsc --noEmit` + `eslint` sạch. Chưa test qua browser (lý do như các sub-phase trước — không
  có dev server chạy sẵn trong phiên).

**Chưa làm (để dành sub-phase sau)**: `/student/schedule` (§40) vẫn còn dùng UI/mock cũ, chưa
nối `GET /leader/me/sessions` — cần đánh giá lại cấu trúc dữ liệu vì mock cũ trộn cả Session
chính thức lẫn các "khung ưu tiên/còn chỗ/không chọn" (thuộc domain Group Preference, đã tách
riêng ra `/student/preferences` ở sub-phase này) trong cùng 1 view theo round; API thật §40 chỉ
trả Session (danh sách phẳng), không có khái niệm round-config đầy đủ — sẽ cần quyết định lại
cấu trúc UI trước khi migrate, không chỉ đổi nguồn dữ liệu như các sub-phase trước.

**Câu hỏi cần chốt với BE**:
1. `GET /leader/me/dashboard` không có JSON mẫu — field đặt đúng theo list §38 nhưng cấu trúc
   lồng (`project`, `mainSupervisor`, `currentRound`, `upcomingSession`, `latestResult`,
   `remediation`) là suy luận, cần xác nhận. Riêng `preferenceStatus` (`NOT_REQUIRED | PENDING |
   SUBMITTED`) spec hoàn toàn không định nghĩa enum này — tự đặt 3 giá trị hợp lý, có thể sai
   tên.
2. `GET/PUT /rounds/:roundId/groups/:groupId/preferences` không có JSON mẫu cho response GET
   (chỉ có request PUT `{timeslotIds}` ở §56) — field `GroupPreference[]` (`timeslotId, date,
   startTime, endTime, selected`) tự suy theo pattern Lecturer Availability.
3. Màn "Kết quả" (§37 sidebar) không có API — cần BE xác nhận có đúng là chưa thiết kế, hay bị
   sót trong spec.

**[ĐÃ LÀM — sub-phase 9f, 2026-08-19] Group Schedule (spec §40) — hoàn tất Phần V, đóng Phase 9**
- Nối `/student/schedule` với `GET /leader/me/sessions` (`fetchLeaderPortal.mySessions`, đã khai
  báo sẵn từ sub-phase 9e). **Yêu cầu của user: giữ nguyên UI/UX hiện có** (calendar theo tuần,
  round rail bên trái, mini calendar, popover chi tiết session, agenda mobile) — không thiết kế
  lại, chỉ đổi tầng dữ liệu.
- `app/(student)/student/schedule/components/types.ts` (file mới, thay `mock-data.ts`): mapper
  `toStudentScheduleData()` gom `LeaderSession[]` (phẳng) thành lại đúng shape
  `ScheduleRound → ScheduleDay → ScheduleSlot` mà `schedule-calendar.tsx`/`session-detail-panel.tsx`
  cần, để **không phải viết lại 2 file component đó** — chỉ đổi import path
  `./mock-data` → `./types` và sửa vài chỗ nhỏ ăn theo type mới (xem dưới).
- **Đơn giản hoá bắt buộc so với mock cũ** (không phải lựa chọn thiết kế, mà vì API thật không
  có dữ liệu tương ứng):
  - `ScheduleSlot.kind` giờ chỉ còn 1 giá trị `"official"` — bỏ hẳn `preferred/available/
    not-selected/empty` vì `GET /leader/me/sessions` chỉ trả Session thật đã publish, không trả
    khung ưu tiên/còn chỗ (dữ liệu đó thuộc Group Preference, đã tách sang `/student/preferences`
    ở sub-phase 9e). Icon/màu trong `schedule-calendar.tsx` và `session-detail-panel.tsx` rút
    gọn theo đúng 1 kind này; nút hành động trong `SessionDetailPanel` chỉ còn nhánh "Xin đổi
    lịch"/"Copy giờ" (bỏ nhánh "Cập nhật lựa chọn" vì không còn slot dạng chọn ở màn này nữa).
  - `ScheduleRound.status` đổi từ `EvaluationRoundStatus` (8 giá trị DRAFT..LOCKED — Leader
    không có API lấy trạng thái round lịch sử) sang `LeaderSessionStatus` (5 giá trị, suy luận
    tổng hợp từ trạng thái các Session thật thuộc round đó — có ưu tiên POSTPONED >
    GROUP_ABSENT > SCHEDULED > CANCELLED > COMPLETED). Đây là dữ liệu thật (SessionStatus theo
    spec §7), không phải suy đoán tùy tiện.
  - Bỏ hẳn field `scheduleVersionLabel`/`maxGroupsPerTimeslot`/`groupSelectionMode`/
    `registrationDeadline`/`emptyState` khỏi type (đã xác nhận không nơi nào trong 2 file UI
    dùng tới, hoặc là field lộ dữ liệu cấm theo §40 "Không show ScheduleVersion/Quota" đã patch
    ở lượt trước).
  - Reviewer trong council chỉ còn `{id, name}` (API council chỉ trả `{name}[]`) — bỏ
    `reviewer.code`/`isResultOwner`/`isCarriedFromPrevious` khỏi UI vì không có nguồn dữ liệu.
  - Badge học kỳ (`data.semester.code`) ở header bị bỏ — không có endpoint semester nào lộ ra
    cho Leader (endpoint semester hiện có là `ADMIN`-only qua `hooks/useSemesters.ts`).
- `tsc --noEmit` + `eslint` sạch. Chưa test qua browser (lý do như các sub-phase trước).

**Phase 9 — hoàn tất toàn bộ**: Lecturer §31-36 ✅, Project Leader §37-40 ✅. Còn lại việc dọn
dẹp code cũ (`fetchScheduling`/`fetchResults` hàm cũ chưa dùng, `core.ts` envelope) để dành 1
lần cuối cùng khi không còn phase nào động vào các file đó nữa.

---

## Bảng tổng hợp thứ tự phụ thuộc

```text
Phase 0 (envelope/error/Semester)
   ↓
Phase 1 (Group/Project) ──┐
   ↓                       │
Phase 2 (Round config)     │
   ↓                       │
Phase 3 (Invitation/Availability/Preference) ← phụ thuộc Phase 1 (Group) + Phase 2 (Round)
   ↓
Phase 4 (Scheduling/CP-SAT)
   ↓
Phase 5 (Room Assignment)
   ↓
Phase 6 (Publish)
   ↓
Phase 7 (Post-publish: change room / replace reviewer / postpone)
   ↓
Phase 8 (Result & Progression)
   ↓
Phase 9 (Lecturer/Leader portal — cắt lát theo phase tương ứng ở trên, làm song song
         khi phase Manager liên quan đã xong, không cần đợi tới cuối)
```

## Cách vận hành từng phase khi tới lượt

1. Xác nhận với BE: endpoint của phase đã deploy ở môi trường nào (local/staging), trả đúng
   response envelope mới chưa (`{data}`/`{data,meta}`/`{error}`).
2. Đọc kỹ phần spec tương ứng trong `capstone-fe-be-implementation-spec.md` (mục số thứ tự
   ghi trong bảng trên).
3. Viết lại `fetchX.ts` theo route + field mới, giữ nguyên tên hook/component bên ngoài nếu
   có thể để giảm chỗ phải sửa ở page.
4. Cập nhật UI theo enum/status mới (đổi label map trong `_shared/labels.ts` tương ứng).
5. `tsc --noEmit` + `eslint` sạch trước khi coi phase xong.
6. Không bắt đầu phase kế tiếp nếu phase trước còn endpoint tạm (giữ code cũ tại chỗ đó,
   đừng half-migrate — dễ vỡ giữa 2 convention trong cùng một trang).
