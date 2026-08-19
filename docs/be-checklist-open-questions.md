# BE Implementation Checklist — đối chiếu với FE đã build theo `capstone-fe-be-implementation-spec.md`

Ngày lập: 2026-08-19

## BE verification update — 2026-08-19

Semester dùng đúng bốn trạng thái `PLANNING`, `ACTIVE`, `CLOSED`, `ARCHIVED` theo
`capstone-fe-be-implementation-spec.md` và `manager-fe-migration-phases.md`. Migration
`0026_semester_four_states` đã khôi phục enum; Round chỉ được tạo trong Semester `ACTIVE`,
`ARCHIVED` là read-only, và `set-current` không nhận Semester đã archive. Các endpoint FE còn
thiếu hoặc lệch envelope/route/field vẫn được liệt kê bên dưới, chưa được coi là đã hoàn tất.

## Mục đích file này

FE đã build xong toàn bộ Manager / Lecturer / Project Leader theo
`capstone-fe-be-implementation-spec.md`. Với những endpoint spec có JSON mẫu, FE gọi đúng y
như spec — không liệt kê lại ở đây.

Với những chỗ **spec không có JSON mẫu** hoặc **không nhắc tới endpoint**, FE đã tự suy ra một
shape hợp lý để code chạy được ngay, dựa trên: mục "Fields" liệt kê dạng text trong spec, ASCII
mock UI, hoặc pattern của các endpoint khác đã có mẫu trong cùng spec.

**Việc cần làm của BE: build/kiểm tra đúng theo các shape dưới đây.** Nếu BE build khớp, FE
chạy được ngay không cần sửa gì. Nếu BE có lý do để đặt tên khác, báo lại field cụ thể để FE
đổi type — nhưng mặc định là BE build theo đúng những gì liệt kê ở đây.

---

## Phần A — Endpoint FE cần nhưng spec không mô tả

Đây là các nghiệp vụ FE đang có UI sẵn (nút/trang), đang tạm vô hiệu hoá hoặc giữ code cũ, chờ
endpoint tương ứng. Shape đề xuất bên dưới — BE cứ build theo đúng vậy trừ khi có lý do khác.

### A1. Sửa đề tài sau khi tạo
```http
PATCH /api/v1/projects/:projectId
```
```json
{ "nameVi": "string?", "nameEn": "string?", "mainSupervisorId": "string?", "coSupervisorId": "string?" }
```
Response: `{ "data": Project }` (shape giống `GET /projects/:id`).
📁 `app/(manager)/manager/projects/components/projects-page.tsx` (menu "Sửa đề tài" đang tắt)

### A2. Sửa cấu hình Round sau khi tạo (khi còn DRAFT)
```http
PATCH /api/v1/rounds/:roundId
```
Body: cùng field với `POST /semesters/:semesterId/rounds` (spec §49), tất cả optional.
📁 `app/(manager)/manager/rounds/[roundId]/components/round-detail-page.tsx` (menu "Sửa cấu hình" đang tắt)

### A3. Import đề tài hàng loạt
```http
POST /api/v1/semesters/:semesterId/projects/import
```
Đề xuất: multipart file (CSV/Excel), response trả `{ "data": { "created": number, "errors": [{row, message}] } }`.
📁 `app/(manager)/manager/projects/components/projects-page.tsx` (nút "Import" đang tắt)

### A4. CRUD phòng
```http
GET  /api/v1/rooms
POST /api/v1/rooms
PATCH /api/v1/rooms/:roomId
```
```json
{ "code": "SEM-01", "name": "Seminar 1", "type": "SEMINAR", "status": "ACTIVE" }
```
Spec §65-68 chỉ có "Available Rooms" (đọc, cần Round context). Cần thêm route CRUD độc lập
(không phụ thuộc Round) để Manager tự quản lý danh sách phòng.
📁 `app/(manager)/manager/rooms/**` (hiện đang dùng model cũ `code/name/capacity/active`, chưa map `RoomType`)

### A5. Manager nhập hộ lịch rảnh Lecturer / nguyện vọng Group
Nếu vẫn cần tính năng này (BR-AVL-04 cũ), cần 2 endpoint kiểu:
```http
PUT /api/v1/rounds/:roundId/availability/:lecturerId
PUT /api/v1/rounds/:roundId/groups/:groupId/preferences (đã có, nhưng chỉ cho phép current-user=Leader — cần variant cho Manager override)
```
Nếu **không cần nữa** (self-service only), FE giữ nguyên hiện trạng (đã xoá nút "Nhập hộ").
📁 đã xoá khỏi `round-detail-page.tsx`

### A6. Danh sách case khắc phục toàn học kỳ + đánh dấu FAILED do quá hạn (Manager)
```http
GET  /api/v1/semesters/:semesterId/remediations
POST /api/v1/remediations/:remediationId/actions/overdue-fail
```
```json
{ "reason": "string" }
```
Theo bảng Screen→API Mapping (§XVII) hiện chỉ có Lecturer verify remediation từng case qua
Project Detail. Nếu Manager cần xử lý hàng loạt case quá hạn, cần 2 endpoint trên; nếu không,
FE sẽ bỏ hẳn trang `/manager/results` cũ.
📁 `app/(manager)/manager/results/**` (đang giữ nguyên, chạy trên API cũ)

### A7. Tạo buổi bù sau khi Postpone
```http
POST /api/v1/sessions/:sessionId/makeup
```
```json
{ "date": "2026-08-25", "timeslotId": "ts_01", "roomId": "room_sem01" }
```
Response: `{ "data": Session }` với `makeupOfSessionId` trỏ về session gốc (đúng theo spec §73).
📁 chưa có file — FE sẽ build UI "Tạo buổi bù" ngay khi có payload xác nhận

### A8. Kết quả (Project Leader)
```http
GET /api/v1/leader/me/results
```
Đề xuất: mảng `{ roundType, kind, value, date, note }[]` — lịch sử đầy đủ, khác `latestResult`
(chỉ 1 giá trị) đã có ở Dashboard §38.
📁 `app/(student)/student/results/components/student-results-stub.tsx` (đang là trang stub)

### A9. Lịch sử đầy đủ Review/Defense ở Lecturer Supervised Groups
```http
GET /api/v1/lecturer/me/supervised-projects/:projectId/results
```
Đề xuất: cùng shape với A8, dùng chung nếu hợp lý. Hiện §34 chỉ có field số ít `Latest Result`.
📁 `app/(lecturer)/lecturer/supervised-groups/**`

---

## Phần B — Endpoint đã có trong spec, FE tự suy field (BE build khớp theo đây)

### B1. `GET /rounds/:roundId/schedules` (spec §26)
```json
{
  "data": [
    {
      "versionId": "sv_03",
      "versionNumber": 3,
      "status": "DRAFT",
      "scheduledCount": 74,
      "unscheduledCount": 0,
      "overallScore": 91.5,
      "createdAt": "2026-08-19T10:00:00+07:00"
    }
  ]
}
```
📁 `lib/api/services/fetchScheduling.ts`

### B2. `GET /rounds/:roundId/publish-readiness` (spec §69)
```json
{
  "data": {
    "ready": true,
    "checks": {
      "activeVersion": true,
      "allSessionsHaveTimeslot": true,
      "allSessionsHaveCouncil": true,
      "allSessionsHaveRoom": true,
      "roomConflicts": 0
    }
  }
}
```
`roomConflicts` FE đang coi là **số lượng** (0 = hợp lệ), không phải boolean.
📁 `lib/api/services/fetchScheduling.ts`

### B3. `POST /rounds/:roundId/rooms/suggest` (spec §67)
```json
{ "data": [{ "sessionId": "ses_01", "roomId": "room_sem01" }] }
```
FE preview danh sách này trước khi gọi `apply-suggestions` (không kèm tham số, commit y hệt
danh sách vừa suggest). Nếu BE lưu tạm phía server và `apply-suggestions` không cần body, báo
lại để FE bỏ bước preview.
📁 `lib/api/services/fetchRoomAssignment.ts`

### B4. `GET /lecturer/me/invitations` (spec §31)
```json
{
  "data": [
    {
      "id": "inv_01",
      "round": { "id": "rnd_01", "name": "Defense 1.1", "type": "DEFENSE_1_1", "registrationDeadline": "2026-08-20T23:59:00+07:00" },
      "status": "PENDING",
      "respondedAt": null
    }
  ]
}
```
📁 `lib/api/services/fetchLecturerPortal.ts`

### B5. `GET/PUT /rounds/:roundId/availability/me` (spec §32/§55)
```json
{
  "data": {
    "preferredLoad": "HIGH",
    "slots": [
      { "timeslotId": "ts_01", "date": "2026-08-25", "startTime": "08:00", "endTime": "09:00", "available": true }
    ]
  }
}
```
📁 `lib/api/services/fetchLecturerPortal.ts`

### B6. `GET /lecturer/me/sessions` + `GET /sessions/:sessionId` (spec §33/§35)
```json
{
  "data": {
    "id": "ses_01",
    "round": { "id": "rnd_01", "name": "Defense 1.1", "type": "DEFENSE_1_1" },
    "group": { "id": "grp_01", "code": "G01", "projectTitle": "Smart Factory AI" },
    "date": "2026-08-25",
    "startTime": "08:00",
    "endTime": "09:00",
    "roomCode": "A203",
    "myRole": "REVIEWER",
    "council": [{ "id": "lec_01", "name": "Nguyen Van A" }],
    "status": "SCHEDULED",
    "result": null
  }
}
```
`result` chỉ có ở `GET /sessions/:sessionId`: `{ "type": "REVIEW", "value": "PASS", "note": "string?" }`.
📁 `lib/api/services/fetchLecturerPortal.ts`

### B7. `GET /lecturer/me/supervised-projects` (spec §34)
```json
{
  "data": [
    {
      "id": "prj_01",
      "code": "P001",
      "titleVi": "string",
      "supervisorRole": "MAIN",
      "group": { "id": "grp_01", "code": "G01", "memberCount": 5, "leader": { "id": "stu_01", "name": "string", "code": "SE001" } },
      "projectStatus": "ACTIVE",
      "nextEvaluation": { "roundType": "DEFENSE_1_2", "date": "2026-09-03" },
      "latestResult": { "roundType": "DEFENSE_1_1", "kind": "DEFENSE", "value": "LEVEL_1", "date": "2026-08-20" },
      "remediation": null
    }
  ]
}
```
Xác nhận đây là **single value** (không phải mảng lịch sử — xem A9 nếu cần lịch sử đầy đủ).
📁 `lib/api/services/fetchLecturerPortal.ts`

### B8. `GET /lecturer/me/remediations` (spec §36)
```json
{
  "data": [
    { "id": "rem_01", "group": { "id": "grp_01", "code": "G01", "projectTitle": "string" }, "deadline": "2026-08-30", "status": "PENDING" }
  ]
}
```
FE không có field verifier riêng (giả định verifier = Lecturer đang đăng nhập, theo domain
"Lecturer chỉ thấy case mình được chỉ định làm verifier"). Nếu BE trả kèm `roundType`/`sessionId`
gốc thì càng tốt (FE hiện không dùng nhưng có thể hữu ích để link ngược lại session).
📁 `lib/api/services/fetchLecturerPortal.ts`

### B9. `GET /leader/me/dashboard` (spec §38)
```json
{
  "data": {
    "group": { "id": "grp_01", "code": "G01", "memberCount": 5, "maxMembers": 5 },
    "project": { "id": "prj_01", "code": "P001", "titleVi": "string", "titleEn": "string", "status": "ACTIVE" },
    "mainSupervisor": { "id": "lec_01", "name": "string" },
    "coSupervisor": null,
    "currentRound": { "id": "rnd_01", "name": "Defense 1.1", "type": "DEFENSE_1_1", "status": "OPEN_REGISTRATION" },
    "preferenceStatus": "PENDING",
    "deadline": "2026-08-20T23:59:00+07:00",
    "upcomingSession": { "id": "ses_01", "date": "2026-08-25", "startTime": "08:00", "endTime": "09:00", "room": "A203" },
    "latestResult": { "roundType": "REVIEW_1", "kind": "REVIEW", "value": "PASS", "date": "2026-07-08" },
    "remediation": null
  }
}
```
**`preferenceStatus` là enum FE tự đặt ra** (spec không định nghĩa ở đâu cả):
`"NOT_REQUIRED" | "PENDING" | "SUBMITTED"`. BE build đúng 3 giá trị này (hoặc báo lại tên khác
để FE đổi).
📁 `lib/api/services/fetchLeaderPortal.ts`

### B10. `GET /rounds/:roundId/groups/:groupId/preferences` (spec §39)
```json
{
  "data": [
    { "timeslotId": "ts_01", "date": "2026-08-27", "startTime": "08:00", "endTime": "09:30", "selected": true }
  ]
}
```
(Request PUT đã có mẫu ở spec §56 — chỉ GET thiếu mẫu.)
📁 `lib/api/services/fetchLeaderPortal.ts`

### B11. `GET /leader/me/sessions` (spec §40)
```json
{
  "data": [
    {
      "id": "ses_01",
      "round": { "id": "rnd_01", "name": "Defense 1.1", "type": "DEFENSE_1_1" },
      "date": "2026-08-20",
      "startTime": "09:00",
      "endTime": "10:00",
      "roomCode": "A203",
      "council": [{ "name": "Nguyen Van A" }],
      "status": "SCHEDULED"
    }
  ]
}
```
**Bắt buộc**: response này **không được có** field `scheduleVersionLabel`/`softScore`/
`maxGroupsPerTimeslot`/bất kỳ dữ liệu solver nội bộ nào — spec §40 ghi rõ "Không show
ScheduleVersion / Soft Score / Quota / Internal solver data" cho màn này.
Council ở đây FE chỉ cần `name` (không thao tác gì với id) — nếu BE trả thêm `id` thì FE dùng
làm React key tốt hơn, không bắt buộc.
📁 `lib/api/services/fetchLeaderPortal.ts`

---

## Phần C — Logic cần BE xác nhận khớp với hiểu của FE

1. **Semester 4 trạng thái** — Semester dùng flat route `/semesters` (không nested, vì là gốc).
   `POST /semesters/:id/set-current` tự động đóng semester ACTIVE hiện tại khi chuyển sang cái
   khác — FE giữ nguyên logic này từ bản cũ, xác nhận vẫn đúng với 4 trạng thái mới
   (PLANNING/ACTIVE/CLOSED/ARCHIVED).
2. **`maxGroupsPerTimeslot`, `resultOwnerMode`, `groupSelectionMode`** — FE giữ nguyên tên field
   này từ bản cũ, coi như không đổi trong spec mới.
3. **Round tự chuyển trạng thái theo action, không có transition endpoint riêng**: FE hiểu
   `REGISTRATION_CLOSED → SCHEDULING` xảy ra khi gọi `schedules/generate`,
   `SCHEDULED → PUBLISHED` khi gọi `actions/publish`, không có endpoint transition độc lập nào
   khác cho các cặp này. Xác nhận đúng.
4. **Verifier cho remediation LEVEL_2** — FE giới hạn danh sách chọn verifier trong **council
   của chính session đó** (không phải toàn bộ giảng viên hệ thống). BE cần đảm bảo
   `POST /sessions/:sessionId/result` chấp nhận `verifierId` là bất kỳ ai trong council đã chấm
   session đó — nếu domain thật cho phép chọn verifier ngoài council, cần báo lại để FE mở rộng
   danh sách (khi đó cần thêm endpoint liệt kê giảng viên hợp lệ).
5. **Room CRUD thuộc Manager** — FE build route CRUD phòng (A4) dưới quyền Manager, không phải
   Admin. Nếu quyền quản lý phòng thực ra thuộc Admin, báo lại để FE đổi route group.

---

## Ghi chú

- API nào đã có JSON mẫu đầy đủ trong spec (Group/Project/Round list, Scheduling generate,
  Publish, Result submit...) FE đã build khớp 100%, không liệt kê ở đây.
- `docs/manager-fe-migration-phases.md` có log chi tiết quyết định của từng phase nếu cần tra
  lại bối cảnh cụ thể.
