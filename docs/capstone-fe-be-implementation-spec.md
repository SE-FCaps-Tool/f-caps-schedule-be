# Capstone Defense Scheduler — FE/BE Implementation Specification

> Version: Draft implementation spec  
> Scope: **Manager / Lecturer / Project Leader**, Group, Project, Round, Registration, Scheduling, Room Assignment, Publish, Result, Remediation
>
> Nguyên tắc domain đã chốt:
>
> - `Group` quản lý cấu trúc nhóm và membership.
> - `Project` giữ progression học thuật Review / Defense.
> - `EvaluationRound` giữ lifecycle của một đợt đánh giá.
> - Scheduler chỉ generate **Timeslot + Council**.
> - `Room` **không nằm trong optimizer**.
> - Round chỉ cấu hình **RoomType** (`NORMAL`, `SEMINAR`, `LAB`).
> - Sau khi chọn `ScheduleVersion ACTIVE`, Manager mới gán Room.
> - Session trước publish là `PLANNED`; sau publish là `SCHEDULED`.
> - `Council` là immutable; thay Reviewer tạo Council mới.
> - Postpone không sửa Session cũ thành lịch mới; tạo make-up Session mới.
>
> Ký hiệu:
>
> - **SOURCE RULE**: rule từ domain/spec v2.0 đã chốt trong luồng.
> - **IMPLEMENTATION PROPOSAL**: đề xuất FE/BE để triển khai, có thể tinh chỉnh.

---

# PHẦN I — DOMAIN & ENUMS

## 1. Semester

```ts
enum SemesterStatus {
  PLANNING = "PLANNING",
  ACTIVE = "ACTIVE",
  CLOSED = "CLOSED",
  ARCHIVED = "ARCHIVED"
}
```

```text
PLANNING
→ chuẩn bị enrollment, group, project, supervisor, quota
→ chưa được tạo Evaluation Round

ACTIVE
→ được vận hành Review / Defense

CLOSED
→ kết thúc nghiệp vụ học kỳ

ARCHIVED
→ chỉ đọc / lưu trữ
```

## 2. Group

```ts
enum GroupStatus {
  FORMING = "FORMING",
  FORMED = "FORMED",
  ASSIGNED = "ASSIGNED",
  DISBANDED = "DISBANDED"
}
```

```ts
enum GroupMemberRole {
  LEADER = "LEADER",
  MEMBER = "MEMBER"
}
```

**IMPLEMENTATION PROPOSAL**

```ts
enum GroupMembershipStatus {
  ACTIVE = "ACTIVE",
  LEFT = "LEFT"
}
```

## 3. Project

```ts
enum ProjectStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  ELIGIBLE_D12 = "ELIGIBLE_D12",
  D12_CONDITIONAL = "D12_CONDITIONAL",
  PENDING_D2 = "PENDING_D2",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED"
}
```

```ts
enum SupervisorRole {
  MAIN = "MAIN",
  CO = "CO"
}
```

## 4. Round

```ts
enum RoundType {
  REVIEW_1 = "REVIEW_1",
  REVIEW_2 = "REVIEW_2",
  DEFENSE_1_1 = "DEFENSE_1_1",
  DEFENSE_1_2 = "DEFENSE_1_2",
  DEFENSE_2 = "DEFENSE_2"
}
```

```ts
enum EvaluationRoundStatus {
  DRAFT = "DRAFT",
  OPEN_REGISTRATION = "OPEN_REGISTRATION",
  REGISTRATION_CLOSED = "REGISTRATION_CLOSED",
  SCHEDULING = "SCHEDULING",
  SCHEDULED = "SCHEDULED",
  PUBLISHED = "PUBLISHED",
  ONGOING = "ONGOING",
  COMPLETED = "COMPLETED",
  LOCKED = "LOCKED",
  CANCELLED = "CANCELLED"
}
```

## 5. Invitation / workload

```ts
enum RoundInvitationStatus {
  PENDING = "PENDING",
  ACCEPTED = "ACCEPTED",
  DECLINED = "DECLINED",
  EXPIRED = "EXPIRED",
  WITHDRAWN = "WITHDRAWN"
}
```

**IMPLEMENTATION PROPOSAL**

```ts
enum PreferredLoad {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH"
}
```

## 6. ScheduleVersion

```ts
enum ScheduleVersionStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  PUBLISHED = "PUBLISHED",
  DISCARDED = "DISCARDED"
}
```

## 7. Session

```ts
enum SessionStatus {
  PLANNED = "PLANNED",
  SCHEDULED = "SCHEDULED",
  COMPLETED = "COMPLETED",
  POSTPONED = "POSTPONED",
  GROUP_ABSENT = "GROUP_ABSENT",
  CANCELLED = "CANCELLED"
}
```

## 8. Room

```ts
enum RoomType {
  NORMAL = "NORMAL",
  SEMINAR = "SEMINAR",
  LAB = "LAB"
}

enum RoomStatus {
  ACTIVE = "ACTIVE",
  MAINTENANCE = "MAINTENANCE",
  INACTIVE = "INACTIVE"
}
```

## 9. Results

```ts
enum ReviewResult {
  PASS = "PASS",
  NEEDS_FIX = "NEEDS_FIX",
  FAIL = "FAIL"
}

enum DefenseResult {
  LEVEL_1 = "LEVEL_1",
  LEVEL_2 = "LEVEL_2",
  LEVEL_3 = "LEVEL_3",
  LEVEL_4 = "LEVEL_4"
}
```

---

# PHẦN II — FE GLOBAL DESIGN

## 10. Manager App Shell

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Capstone Scheduler     Học kỳ: [ SU26 ▼ ]        🔔       Manager ▼    │
├────────────────┬─────────────────────────────────────────────────────────┤
│ Tổng quan      │                                                         │
│ HỌC VỤ         │                    PAGE CONTENT                         │
│ Học kỳ         │                                                         │
│ Nhóm sinh viên │                                                         │
│ Đề tài         │                                                         │
│ ĐÁNH GIÁ       │                                                         │
│ Đợt đánh giá   │                                                         │
│ Lịch đánh giá  │                                                         │
│ KẾT QUẢ        │                                                         │
│ Kết quả        │                                                         │
│ Báo cáo        │                                                         │
└────────────────┴─────────────────────────────────────────────────────────┘
```

Shared components:

```text
AppShell
Topbar
Sidebar
SemesterSwitcher
PageHeader
FilterBar
DataTable
Pagination
StatCard
StatusBadge
WarningBadge
AttentionList
DetailDrawer
EntityDetailPage
Tabs
ProgressTimeline
AvailabilityGrid
ScheduleCalendar
RoomResourceGrid
SessionDrawer
ConfirmModal
ReasonModal
ResultForm
```

---

# PHẦN III — FE MANAGER

## 11. Group List

Route:

```text
/manager/groups
```

API:

```text
GET /api/v1/semesters/:semesterId/groups
```

UI:

```text
NHÓM SINH VIÊN — SU26

[🔍 Tìm nhóm...] [Trạng thái ▼] [Đề tài ▼] [Leader ▼] [⚠ Cần chú ý]

                                              [+ Tạo nhóm]

Nhóm    Đề tài            Leader    SL    Trạng thái     Cảnh báo
──────────────────────────────────────────────────────────────────
G01     Smart Factory     SE001     5     ASSIGNED
G02     AI Education      SE012     4     ASSIGNED
G03     —                 SE021     4     FORMED
G04     —                 —         3     FORMING         ⚠ Chưa Leader
```

Display model:

```ts
type GroupListItem = {
  id: string
  code: string
  status: GroupStatus
  leader: {
    id: string
    studentCode: string
    fullName: string
  } | null
  memberCount: number
  project: {
    id: string
    code: string
    name: string
    status: ProjectStatus
  } | null
  warnings: {
    code: string
    message: string
  }[]
}
```

Filters:

```ts
{
  search?: string
  status?: GroupStatus
  hasProject?: boolean
  hasLeader?: boolean
  warning?: string
  page?: number
  pageSize?: number
}
```

FE rules:

```text
Không tính eligibility ở frontend.

Member count dưới minimum:
→ warning cam
→ không block

No Leader:
→ warning đỏ

Project progression:
→ hiển thị riêng
→ không map thành GroupStatus
```

## 12. Create Group

Route:

```text
/manager/groups/new
```

API:

```text
POST /api/v1/semesters/:semesterId/groups
```

Fields:

```ts
{
  code: string
  studentIds: string[]
  leaderId?: string
}
```

UI:

```text
TẠO NHÓM

Học kỳ
Summer 2026
(read-only)

Mã nhóm *
[G01________________]

THÀNH VIÊN
[+ Thêm sinh viên]

SE001   Nguyễn A      [×]
SE002   Trần B        [×]
SE003   Lê C          [×]

Leader
[ Nguyễn A ▼ ]

                  [Hủy] [Tạo nhóm]
```

FE validation:

```text
code required
studentIds.length > 0

leaderId nếu có:
→ phải thuộc studentIds

memberCount < minimum:
→ warning
→ vẫn submit
```

## 13. Group Detail

Route:

```text
/manager/groups/:groupId
```

APIs:

```text
GET /api/v1/groups/:groupId
GET /api/v1/groups/:groupId/members
```

Tabs:

```text
Tổng quan
Thành viên
Đề tài
Lịch sử
```

Overview fields:

```text
Group Code
Group Status
Leader
Current Member Count
Initial Member Count
Assigned Project
Project Status
Main Supervisor
Co-Supervisor
```

## 14. Group Members

API:

```text
GET /api/v1/groups/:groupId/members
```

Actions:

```text
POST /api/v1/groups/:groupId/actions/change-leader
POST /api/v1/groups/:groupId/members/:membershipId/actions/leave
```

UI:

```text
MSSV     Họ tên           Vai trò     Trạng thái
─────────────────────────────────────────────────
SE001    Nguyễn A         Leader      Active
SE002    Trần B           Member      Active
SE003    Lê C             Member      Left
```

FE rules:

```text
Không xóa history row.

Set Leader:
→ chỉ active member.

Mark Left:
→ reason required.
```

## 15. Assign Project to Group

API:

```text
PUT /api/v1/groups/:groupId/project
```

UI:

```text
GẮN ĐỀ TÀI

Group
G01

Project *
[P001 — Smart Factory AI ▼]

GVHD chính
Nguyễn A

Đồng hướng dẫn
Trần B

                [Hủy] [Xác nhận]
```

FE filter Project:

```text
same Semester
not assigned to another Group
not CANCELLED
```

## 16. Project List

Route:

```text
/manager/projects
```

API:

```text
GET /api/v1/semesters/:semesterId/projects
```

UI:

```text
ĐỀ TÀI — SU26

[🔍 Search] [GVHD ▼] [Progress ▼] [Có nhóm ▼]

                                         [+ Tạo đề tài]

Mã      Tên                  GVHD       Nhóm     Progress
────────────────────────────────────────────────────────
P001    Smart Factory        Nguyễn A   G01      ACTIVE
P002    AI Education         Trần B     G02      ELIGIBLE_D12
P003    EV Charging          Lê C       —        DRAFT
```

## 17. Create Project

API:

```text
POST /api/v1/semesters/:semesterId/projects
```

Fields:

```ts
{
  code: string
  nameVi: string
  nameEn?: string
  mainSupervisorId: string
  coSupervisorId?: string
}
```

Validation:

```text
code required
nameVi required
mainSupervisor required
mainSupervisor != coSupervisor
```

## 18. Project Detail

Route:

```text
/manager/projects/:projectId
```

APIs:

```text
GET /api/v1/projects/:projectId
GET /api/v1/projects/:projectId/progression
GET /api/v1/projects/:projectId/results
```

Tabs:

```text
Tổng quan
Nhóm
Tiến độ
Kết quả
Lịch sử
```

UI progression:

```text
● ACTIVE
│ Review 1 → PASS
│ Review 2 → NEEDS FIX
● Defense 1.1 → LEVEL 2
● D12_CONDITIONAL
│ Remediation · Deadline 30/08
○ ELIGIBLE_D12
○ Defense 1.2
```

FE rule:

```text
Không tự transition ProjectStatus.
Sau submit result:
→ refetch.
```

## 19. Round List

Route:

```text
/manager/rounds
```

API:

```text
GET /api/v1/semesters/:semesterId/rounds
```

FE rule:

```text
semester.status != ACTIVE
→ disable Create Round
```

## 20. Create Round Wizard

Route:

```text
/manager/rounds/new
```

Final API:

```text
POST /api/v1/semesters/:semesterId/rounds
```

Steps:

```text
1. Thông tin
2. Ngày & Timeslot
3. Registration + Room Type
4. Xác nhận
```

### Step 1

Fields:

```ts
{
  name: string
  type: RoundType
  description?: string
  durationMinutes: number
  reviewerCount: number
  maxGroupsPerTimeslot: number
}
```

Defaults:

```text
REVIEW_1      → 2 reviewers
REVIEW_2      → 2 reviewers
DEFENSE_1_1   → 3 reviewers
DEFENSE_1_2   → 5 reviewers
DEFENSE_2     → 5 reviewers
```

Validation:

```text
name required
durationMinutes > 0
reviewerCount > 0
maxGroupsPerTimeslot > 0
```

### Step 2

Model:

```ts
type RoundDayInput = {
  date: string
  slots: {
    startTime: string
    endTime: string
  }[]
}
```

Validation:

```text
days.length >= 1
startTime < endTime
same-day slots do not overlap
slot duration == durationMinutes
```

### Step 3

Fields:

```ts
{
  registrationDeadline: string
  groupSelectionMode: boolean
  groupPreferenceDeadline?: string
  resultOwnerMode: boolean
  roomTypes: RoomType[]
}
```

Validation:

```text
registrationDeadline required
roomTypes.length >= 1

groupSelectionMode == true
→ groupPreferenceDeadline required
```

Room UI:

```text
☑ Phòng thường
☑ Seminar
☐ Lab
```

### Step 4

Review-only summary and submit.

## 21. Round Detail

Route:

```text
/manager/rounds/:roundId
```

API:

```text
GET /api/v1/rounds/:roundId
```

Tabs:

```text
Tổng quan
Cấu hình
Giảng viên
Nhóm tham gia
Xếp lịch
```

CTA:

```text
DRAFT → Mở đăng ký
OPEN_REGISTRATION → Đóng đăng ký
REGISTRATION_CLOSED → Bắt đầu xếp lịch
SCHEDULING → Generate / Versions
SCHEDULED → Gán phòng / Publish
PUBLISHED → Operational Calendar
ONGOING → Result / Incident
```

## 22. Lecturer Tab — Manager

APIs:

```text
GET  /api/v1/rounds/:roundId/invitations
POST /api/v1/rounds/:roundId/invitations
POST /api/v1/rounds/:roundId/invitations/:invitationId/remind
```

UI:

```text
Lecturer      Invitation       Availability      Workload
──────────────────────────────────────────────────────────
Nguyễn A      ACCEPTED         12 slots          12/30
Trần B        PENDING          —                 8/25
Lê C          DECLINED         —                 10/30
```

## 23. Group / Project Participation

API:

```text
GET /api/v1/rounds/:roundId/eligible-projects
```

UI:

```text
Group Project           GroupStatus ProjectStatus    Leader SL  Eligibility
───────────────────────────────────────────────────────────────────────────
G01   Smart Factory     ASSIGNED    ACTIVE           SE001  5   ✓
G02   AI Education      ASSIGNED    ACTIVE           SE012  4   ✓
G03   EV Charging       ASSIGNED    ELIGIBLE_D12     SE021  3   ✕
G04   Local CRM         FORMED      —                —      4   ✕
```

FE rule:

```text
blocking reason → red
warning → orange
eligible → green

Không derive eligibility client-side.
```

## 24. Registration Dashboard

API:

```text
GET /api/v1/rounds/:roundId/registration-summary
```

UI:

```text
GIẢNG VIÊN
24 invited
21 accepted
18 availability submitted
3 missing

NHÓM
74 eligible
68 preference submitted
6 missing
```

## 25. Scheduling Readiness

API:

```text
GET /api/v1/rounds/:roundId/scheduling-readiness
```

FE behavior:

```text
ready=false
→ disable Generate
→ show blockingIssues

ready=true
→ enable Generate
```

## 26. Schedule Versions

APIs:

```text
POST /api/v1/rounds/:roundId/schedules/generate
GET  /api/v1/rounds/:roundId/schedules
GET  /api/v1/rounds/:roundId/schedules/:versionId
POST /api/v1/rounds/:roundId/schedules/:versionId/actions/set-active
POST /api/v1/rounds/:roundId/schedules/:versionId/actions/discard
```

UI:

```text
Version   Scheduled   Missing    Score    Status
────────────────────────────────────────────────
V1        71/74       3          84.7     DRAFT
V2        74/74       0          88.2     DRAFT
V3        74/74       0          91.5     ACTIVE
```

## 27. Draft Calendar

API:

```text
GET /api/v1/rounds/:roundId/sessions?versionId=:versionId
```

Design:

```text
DEFENSE 1.1 — V3 ACTIVE

           08:00       09:00       10:00
25/08     G01         G02         G03
26/08     G04         G05         G06
```

Session Drawer:

```text
Group
Project
Date
Time
Council
Room: Chưa gán
Status: PLANNED
```

## 28. Room Assignment

APIs:

```text
GET  /api/v1/rounds/:roundId/rooms/available
PUT  /api/v1/sessions/:sessionId/room
POST /api/v1/rounds/:roundId/rooms/suggest
POST /api/v1/rounds/:roundId/rooms/apply-suggestions
```

UI:

```text
Allowed Room Types:
SEMINAR · LAB

             08:00      09:00       10:00
SEM-01       G01        G07         G12
SEM-02       G02        G08         G13
LAB-01       G03                    G14

CHƯA GÁN
G17 · 09:00
G21 · 10:00
```

FE validation:

```text
Only show:
Room.status == ACTIVE
Room.type ∈ round.roomTypes

Conflict:
→ show BE error
→ rollback optimistic UI
```

## 29. Publish Readiness

API:

```text
GET /api/v1/rounds/:roundId/publish-readiness
```

Publish:

```text
POST /api/v1/rounds/:roundId/actions/publish
```

FE:

```text
ready=false → disabled
ready=true → confirmation modal
```

---

# PHẦN IV — FE LECTURER

## 30. Sidebar

```text
Tổng quan
Lời mời
Đăng ký lịch rảnh
Lịch của tôi
Nhóm hướng dẫn
Phiên đánh giá
Khắc phục
```

Contextual menu không có dữ liệu → ẩn.

## 31. Invitations

APIs:

```text
GET  /api/v1/lecturer/me/invitations
POST /api/v1/rounds/:roundId/invitations/me/respond
```

Decline:

```text
reason required
```

## 32. Availability

APIs:

```text
GET /api/v1/rounds/:roundId/availability/me
PUT /api/v1/rounds/:roundId/availability/me
```

UI:

```text
Preferred Load
LOW / MEDIUM / HIGH

             08:00 09:00 10:00
25/08         ✓     ✓     —
26/08         ✓     —     ✓
```

FE validation:

```text
Round OPEN_REGISTRATION
Invitation ACCEPTED
```

## 33. My Schedule

API:

```text
GET /api/v1/lecturer/me/sessions
```

Params:

```text
roundId?
dateFrom?
dateTo?
role?
status?
```

## 34. Supervised Groups

API:

```text
GET /api/v1/lecturer/me/supervised-projects
```

Fields:

```text
Group
Project
Leader
Member Count
Project Status
Next Evaluation
Latest Result
Remediation
```

Không có membership management.

## 35. Session Detail / Result

APIs:

```text
GET  /api/v1/sessions/:sessionId
POST /api/v1/sessions/:sessionId/result
```

LEVEL_2 validation:

```text
remediationDeadline required
verifierId required
```

## 36. Remediation

APIs:

```text
GET  /api/v1/lecturer/me/remediations
POST /api/v1/remediations/:remediationId/verify
```

---

# PHẦN V — FE PROJECT LEADER

## 37. Sidebar

```text
Tổng quan
Đăng ký lịch
Lịch của nhóm
Kết quả
```

## 38. Dashboard

API:

```text
GET /api/v1/leader/me/dashboard
```

Fields:

```text
Group Code
Project
Main Supervisor
Co-Supervisor
Member Count
Project Status
Current Round
Preference Status
Deadline
Upcoming Session
Latest Result
Remediation Status
```

Không có member management.

## 39. Group Preference

APIs:

```text
GET /api/v1/rounds/:roundId/groups/:groupId/preferences
PUT /api/v1/rounds/:roundId/groups/:groupId/preferences
```

Validate:

```text
Current user = active Leader
groupSelectionMode == true
Round == OPEN_REGISTRATION
```

## 40. Group Schedule

API:

```text
GET /api/v1/leader/me/sessions
```

Timeline UI.

Không show:

```text
ScheduleVersion
Soft Score
Quota
Internal solver data
```

---

# PHẦN VI — API CONVENTION

Base:

```text
/api/v1
```

Success:

```json
{
  "data": {}
}
```

Paginated:

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 74
  }
}
```

Error:

```json
{
  "error": {
    "code": "ROUND_INVALID_STATE",
    "message": "Round must be REGISTRATION_CLOSED.",
    "details": {}
  }
}
```

---

# PHẦN VII — BE GROUP APIs

## 41. GET Groups

```http
GET /api/v1/semesters/:semesterId/groups
```

Params:

```text
search?
status?
hasProject?
hasLeader?
warning?
page?
pageSize?
```

Response:

```json
{
  "data": [
    {
      "id": "grp_01",
      "code": "G01",
      "status": "ASSIGNED",
      "memberCount": 5,
      "leader": {
        "id": "stu_01",
        "code": "SE001",
        "fullName": "Nguyen Van A"
      },
      "project": {
        "id": "prj_01",
        "code": "P001",
        "name": "Smart Factory AI",
        "status": "ACTIVE"
      },
      "warnings": []
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 74
  }
}
```

## 42. POST Group

```http
POST /api/v1/semesters/:semesterId/groups
```

Request:

```json
{
  "code": "G01",
  "studentIds": ["stu_01", "stu_02", "stu_03"],
  "leaderId": "stu_01"
}
```

Response:

```json
{
  "data": {
    "id": "grp_01",
    "code": "G01",
    "status": "FORMED"
  }
}
```

Validation:

```text
Semester exists
Student enrolled in Semester
Student not active in another Group same Semester
Leader belongs to active members
Group code unique
```

## 43. Change Leader

```http
POST /api/v1/groups/:groupId/actions/change-leader
```

Request:

```json
{
  "leaderId": "stu_02",
  "reason": "Current leader changed."
}
```

## 44. Member Left

```http
POST /api/v1/groups/:groupId/members/:membershipId/actions/leave
```

Request:

```json
{
  "effectiveDate": "2026-08-19",
  "reason": "Approved withdrawal."
}
```

Logic:

```text
Do not delete membership
status = LEFT
leftAt = effectiveDate
recalculate memberCount

If Leader left:
leaderId = null
```

## 45. Assign Project

```http
PUT /api/v1/groups/:groupId/project
```

Request:

```json
{
  "projectId": "prj_01"
}
```

Validation:

```text
same Semester
Group != DISBANDED
Project not assigned elsewhere
Project != CANCELLED
```

State:

```text
Group FORMED → ASSIGNED

If Main Supervisor exists:
Project DRAFT → ACTIVE
```

---

# PHẦN VIII — BE PROJECT APIs

## 46. GET Projects

```http
GET /api/v1/semesters/:semesterId/projects
```

Params:

```text
search?
status?
supervisorId?
hasGroup?
page?
pageSize?
```

## 47. POST Project

```http
POST /api/v1/semesters/:semesterId/projects
```

Request:

```json
{
  "code": "P001",
  "nameVi": "He thong nha may thong minh",
  "nameEn": "Smart Factory AI",
  "mainSupervisorId": "lec_01",
  "coSupervisorId": "lec_02"
}
```

Validation:

```text
code unique
mainSupervisor required
mainSupervisor != coSupervisor
Lecturer valid
```

Initial status:

```text
DRAFT
```

## 48. Eligibility

```http
GET /api/v1/rounds/:roundId/eligible-projects
```

Response:

```json
{
  "data": [
    {
      "projectId": "prj_01",
      "groupId": "grp_01",
      "eligible": true,
      "checks": {
        "hasGroup": true,
        "hasActiveLeader": true,
        "hasMainSupervisor": true,
        "progressionAllowed": true
      },
      "blockingReasons": [],
      "warnings": [
        {
          "code": "MEMBER_COUNT_BELOW_MIN",
          "message": "Group has fewer than recommended members."
        }
      ]
    }
  ]
}
```

Block:

```text
No Group
No Active Leader
No Main Supervisor
Progression incompatible
```

Warning only:

```text
Member count below minimum
```

---

# PHẦN IX — BE ROUND APIs

## 49. Create Round

```http
POST /api/v1/semesters/:semesterId/rounds
```

Request:

```json
{
  "name": "Defense 1.1",
  "type": "DEFENSE_1_1",
  "description": "",
  "durationMinutes": 60,
  "reviewerCount": 3,
  "maxGroupsPerTimeslot": 3,
  "registrationDeadline": "2026-08-20T23:59:00+07:00",
  "groupSelectionMode": true,
  "groupPreferenceDeadline": "2026-08-22T23:59:00+07:00",
  "resultOwnerMode": true,
  "roomTypes": ["SEMINAR", "LAB"],
  "days": [
    {
      "date": "2026-08-25",
      "slots": [
        {"startTime": "08:00", "endTime": "09:00"},
        {"startTime": "09:00", "endTime": "10:00"}
      ]
    }
  ]
}
```

Validation:

```text
Semester.status == ACTIVE
name non-empty
type valid
durationMinutes > 0
reviewerCount valid
maxGroupsPerTimeslot > 0
days >= 1
no slot overlap
roomTypes >= 1
if groupSelectionMode → groupPreferenceDeadline required
```

Transaction:

```text
create EvaluationRound
create RoundDays
create Timeslots
create RoundRoomTypes
```

## 50. Round Detail

```http
GET /api/v1/rounds/:roundId
```

## 51. Open Registration

```http
POST /api/v1/rounds/:roundId/actions/open-registration
```

Validation:

```text
Round DRAFT
has Timeslot
valid config
RoomType configured
```

Transition:

```text
DRAFT → OPEN_REGISTRATION
```

## 52. Close Registration

```http
POST /api/v1/rounds/:roundId/actions/close-registration
```

Transition:

```text
OPEN_REGISTRATION → REGISTRATION_CLOSED
```

---

# PHẦN X — BE INVITATION / AVAILABILITY

## 53. Invite Lecturers

```http
POST /api/v1/rounds/:roundId/invitations
```

Request:

```json
{
  "lecturerIds": ["lec_01", "lec_02", "lec_03"]
}
```

Initial:

```text
PENDING
```

## 54. Lecturer Respond

```http
POST /api/v1/rounds/:roundId/invitations/me/respond
```

Accept:

```json
{"decision":"ACCEPTED"}
```

Decline:

```json
{
  "decision":"DECLINED",
  "reason":"Unavailable."
}
```

## 55. Availability

```http
PUT /api/v1/rounds/:roundId/availability/me
```

Request:

```json
{
  "preferredLoad": "HIGH",
  "slots": [
    {"timeslotId":"ts_01","available":true},
    {"timeslotId":"ts_02","available":false}
  ]
}
```

Rule:

```text
ACCEPTED + no availability submitted
→ BUSY ALL
```

## 56. Group Preference

```http
PUT /api/v1/rounds/:roundId/groups/:groupId/preferences
```

Request:

```json
{
  "timeslotIds": ["ts_01","ts_02","ts_05"]
}
```

Validation:

```text
current user active Leader
groupSelectionMode true
Round OPEN_REGISTRATION
Group eligible
slots belong to Round
```

---

# PHẦN XI — SCHEDULING ALGORITHM

## 57. Readiness

```http
GET /api/v1/rounds/:roundId/scheduling-readiness
```

Response:

```json
{
  "data": {
    "ready": true,
    "counts": {
      "eligibleProjects": 74,
      "availableLecturers": 21,
      "timeslots": 24
    },
    "blockingIssues": [],
    "warnings": [
      {
        "code": "LECTURER_AVAILABILITY_MISSING",
        "count": 3
      }
    ]
  }
}
```

## 58. Generate

```http
POST /api/v1/rounds/:roundId/schedules/generate
```

Recommended request:

```json
{}
```

Response:

```json
{
  "data": {
    "versionId": "sv_03",
    "versionNumber": 3,
    "status": "DRAFT",
    "scheduledCount": 74,
    "unscheduledCount": 0,
    "overallScore": 91.5,
    "scores": {
      "workload": 94,
      "continuity": 90,
      "compactness": 89
    }
  }
}
```

## 59. Solver input

```text
Round
Enabled Timeslots
Eligible Projects
Groups
Accepted Lecturers
Effective Availability
Project Supervisors
COI
Group Preferences
Semester Quotas
Current Workload
Previous Councils
```

Không có Room.

## 60. Pre-filter

```text
For each Project:
- remove MAIN Supervisor
- remove CO Supervisor
- remove COI Lecturer

For each Timeslot:
- remove unavailable Lecturer
```

Candidate:

```ts
type SessionCandidate = {
  groupId: string
  projectId: string
  timeslotId: string
  groupAllowed: boolean
  reviewerCandidates: string[]
}
```

Invalid if:

```text
Group preference blocks slot
OR
reviewerCandidates < reviewerCount
```

## 61. Solver

Recommended:

```text
Google OR-Tools CP-SAT
```

Variables:

```text
X[g,t] ∈ {0,1}
→ Group g scheduled at Timeslot t

Y[g,t,l] ∈ {0,1}
→ Lecturer l reviews Group g at Timeslot t

S[g] ∈ {0,1}
→ Group g scheduled
```

### Hard constraints

**H1 Supervisor exclusion**

```text
Y[g,t,l] = 0
if l is MAIN/CO supervisor
```

**H2 Lecturer conflict**

```text
∀ l,t:
Σ_g Y[g,t,l] <= 1
```

**H3 Room conflict**

```text
NOT in optimizer.
Validated during Room Assignment.
```

**H4 One Session per Group**

```text
Σ_t X[g,t] = S[g]
```

**H5 Reviewer count**

```text
Σ_l Y[g,t,l]
=
reviewerCount * X[g,t]
```

**H6 Unique Reviewer**

Binary reviewer assignment ensures unique council membership.

**H7 Availability**

```text
Y[g,t,l] = 0
if lecturer unavailable
```

**H8 COI**

```text
Y[g,t,l] = 0
if COI(l, project(g))
```

**H9 Progression eligibility**

Only eligible Projects enter solver.

**H10 Group preference**

```text
X[g,t] = 0
if t not in effective Group preference
```

**H11 D1.2 continuity**

```text
intersection(D11Council, D12Council).size >= 1
```

**H12 Workload / quota**

```text
halfDayMinutes <= 240
dayMinutes <= 480
semesterUsage <= quota
```

**H13 Timeslot capacity**

```text
∀ t:
Σ_g X[g,t] <= maxGroupsPerTimeslot
```

### Soft constraints

```text
S1 Workload Balance
S2 Review continuity
S3 Defense continuity bonus
S4 Compact schedule
S5 Min attendance days
S6 Council stability
S7 Supervisor diversity
```

No Room objective.

### Objective

Priority:

```text
1. maximize scheduled Group count
2. maximize soft score
```

Implementation:

```text
objective =
scheduledCount * HUGE_WEIGHT
+ softScore
```

Example:

```text
HUGE_WEIGHT = 1_000_000
```

**IMPLEMENTATION PROPOSAL soft weights**

```text
0.40 WorkloadBalance
0.25 Continuity
0.20 Compactness
0.10 AttendanceDays
0.05 CouncilStability
```

Weights server-configurable.

## 62. Partial Solution

Do not fail whole generation.

Example:

```text
71/74 scheduled
3 unscheduled
```

Still save `ScheduleVersion DRAFT`.

Unscheduled reasons:

```ts
enum UnscheduledReason {
  NO_VALID_TIMESLOT,
  NO_ENOUGH_ELIGIBLE_REVIEWERS,
  SUPERVISOR_CONFLICT,
  COI_CONFLICT,
  LECTURER_AVAILABILITY_TOO_LOW,
  GROUP_PREFERENCE_TOO_NARROW,
  QUOTA_EXCEEDED,
  TIMESLOT_CAPACITY_REACHED,
  CONTINUITY_CONSTRAINT_FAILED
}
```

## 63. Save ScheduleVersion

Recommended:

```text
DRAFT version
→ save assignments + score + diagnostics

ACTIVE version
→ materialize PLANNED Sessions
```

Avoid duplicate Session rows for every draft version.

## 64. Set Active

```http
POST /api/v1/rounds/:roundId/schedules/:versionId/actions/set-active
```

Transaction:

```text
new Version → ACTIVE
Round → SCHEDULED
materialize Session(status=PLANNED)
roomId = null
```

---

# PHẦN XII — ROOM ASSIGNMENT

## 65. Available Rooms

```http
GET /api/v1/rounds/:roundId/rooms/available
```

Params:

```text
timeslotId?
type?
```

Filter:

```text
Room ACTIVE
Room.type ∈ Round.roomTypes
if timeslotId: not occupied
```

## 66. Assign Room

```http
PUT /api/v1/sessions/:sessionId/room
```

Request:

```json
{
  "roomId": "room_sem01"
}
```

Validation:

```text
Session PLANNED / allowed operational state
Room ACTIVE
Room type allowed
No same timeslot + room conflict
```

## 67. Suggest Rooms

**IMPLEMENTATION PROPOSAL**

```http
POST /api/v1/rounds/:roundId/rooms/suggest
```

Logic:

```text
sort Sessions by Timeslot

for each Session:
  filter ACTIVE Rooms
  filter allowed RoomType
  remove occupied
  choose first / least-used room
```

No scheduler score impact.

## 68. Apply Suggestions

```http
POST /api/v1/rounds/:roundId/rooms/apply-suggestions
```

Validate all first, then atomic commit.

---

# PHẦN XIII — PUBLISH

## 69. Publish Readiness

```http
GET /api/v1/rounds/:roundId/publish-readiness
```

Checks:

```text
activeVersion
allSessionsHaveTimeslot
allSessionsHaveCouncil
allSessionsHaveRoom
roomConflicts == 0
```

## 70. Publish

```http
POST /api/v1/rounds/:roundId/actions/publish
```

Transaction:

```text
Round:
SCHEDULED → PUBLISHED

Active Version:
ACTIVE → PUBLISHED

Sessions:
PLANNED → SCHEDULED

Create notifications
```

---

# PHẦN XIV — POST-PUBLISH

## 71. Change Room

```http
POST /api/v1/sessions/:sessionId/actions/change-room
```

Request:

```json
{
  "roomId": "room_lab01",
  "reason": "Seminar room unavailable."
}
```

Validate:

```text
Room ACTIVE
Allowed type
No conflict
Reason required
```

## 72. Replace Reviewer

```http
POST /api/v1/sessions/:sessionId/actions/replace-reviewer
```

Request:

```json
{
  "oldLecturerId": "lec_01",
  "newLecturerId": "lec_04",
  "reason": "Lecturer is absent."
}
```

Validate:

```text
Available
Not Supervisor
No COI
No time conflict
Within quota
Continuity valid
```

Logic:

```text
Old Council immutable
Create new Council
session.councilId = newCouncil.id
Session status unchanged
```

## 73. Postpone

```http
POST /api/v1/sessions/:sessionId/actions/postpone
```

Request:

```json
{
  "reason": "Lecturer unavailable."
}
```

Effect:

```text
Original Session:
SCHEDULED → POSTPONED
```

Make-up:

```http
POST /api/v1/sessions/:sessionId/makeup
```

Create new Session with:

```text
makeupOfSessionId = original.id
```

---

# PHẦN XV — RESULT & PROGRESSION

## 74. Submit Result

```http
POST /api/v1/sessions/:sessionId/result
```

Review:

```json
{
  "result": "PASS",
  "note": "Meets requirements."
}
```

Defense:

```json
{
  "result": "LEVEL_2",
  "note": "Requires remediation.",
  "remediation": {
    "deadline": "2026-08-30",
    "verifierId": "lec_02"
  }
}
```

Validation:

```text
permission
resultOwnerMode
result enum matches RoundType

LEVEL_2:
deadline required
verifier required
```

## 75. Project Progression

```text
D1.1 LEVEL_1 → ELIGIBLE_D12
D1.1 LEVEL_2 → D12_CONDITIONAL + Remediation
D1.1 LEVEL_3 → PENDING_D2
D1.1 LEVEL_4 → FAILED
```

Review 1 / 2:

```text
result does not block D1.1
```

## 76. Remediation Verify

```http
POST /api/v1/remediations/:remediationId/verify
```

PASS:

```text
D12_CONDITIONAL → ELIGIBLE_D12
```

---

# PHẦN XVI — ERROR CODES

```text
SEMESTER_NOT_ACTIVE

GROUP_CODE_DUPLICATE
STUDENT_NOT_ENROLLED
STUDENT_ALREADY_IN_GROUP
LEADER_NOT_ACTIVE_MEMBER

PROJECT_ALREADY_ASSIGNED
PROJECT_HAS_NO_MAIN_SUPERVISOR

ROUND_INVALID_STATE
ROUND_INVALID_TIMESLOT
ROUND_ROOM_TYPE_REQUIRED

INVITATION_NOT_PENDING
INVITATION_NOT_ACCEPTED

GROUP_NOT_ELIGIBLE
USER_NOT_GROUP_LEADER

SCHEDULER_NOT_READY

ROOM_TYPE_NOT_ALLOWED
ROOM_NOT_ACTIVE
ROOM_CONFLICT

SESSION_INVALID_STATE
REVIEWER_NOT_AVAILABLE
REVIEWER_IS_SUPERVISOR
REVIEWER_COI
REVIEWER_TIME_CONFLICT
REVIEWER_QUOTA_EXCEEDED

RESULT_PERMISSION_DENIED
RESULT_TYPE_INVALID
REMEDIATION_REQUIRED_FIELDS_MISSING
```

---

# PHẦN XVII — SCREEN → API MAPPING

| Role | Screen | API |
|---|---|---|
| Manager | Group List | `GET /semesters/:id/groups` |
| Manager | Create Group | `POST /semesters/:id/groups` |
| Manager | Group Detail | `GET /groups/:id` |
| Manager | Group Members | `GET /groups/:id/members` |
| Manager | Change Leader | `POST /groups/:id/actions/change-leader` |
| Manager | Member Left | `POST /groups/:id/members/:membershipId/actions/leave` |
| Manager | Assign Project | `PUT /groups/:id/project` |
| Manager | Project List | `GET /semesters/:id/projects` |
| Manager | Create Project | `POST /semesters/:id/projects` |
| Manager | Project Detail | `GET /projects/:id` |
| Manager | Round List | `GET /semesters/:id/rounds` |
| Manager | Create Round | `POST /semesters/:id/rounds` |
| Manager | Round Detail | `GET /rounds/:id` |
| Manager | Lecturer Tab | `GET /rounds/:id/invitations` |
| Manager | Invite Lecturer | `POST /rounds/:id/invitations` |
| Manager | Group Participation | `GET /rounds/:id/eligible-projects` |
| Manager | Open Registration | `POST /rounds/:id/actions/open-registration` |
| Manager | Registration Dashboard | `GET /rounds/:id/registration-summary` |
| Manager | Close Registration | `POST /rounds/:id/actions/close-registration` |
| Manager | Scheduling Readiness | `GET /rounds/:id/scheduling-readiness` |
| Manager | Generate | `POST /rounds/:id/schedules/generate` |
| Manager | Versions | `GET /rounds/:id/schedules` |
| Manager | Set Active | `POST /rounds/:id/schedules/:versionId/actions/set-active` |
| Manager | Draft Calendar | `GET /rounds/:id/sessions?versionId=` |
| Manager | Available Rooms | `GET /rounds/:id/rooms/available` |
| Manager | Assign Room | `PUT /sessions/:id/room` |
| Manager | Suggest Rooms | `POST /rounds/:id/rooms/suggest` |
| Manager | Publish Readiness | `GET /rounds/:id/publish-readiness` |
| Manager | Publish | `POST /rounds/:id/actions/publish` |
| Manager | Change Room | `POST /sessions/:id/actions/change-room` |
| Manager | Replace Reviewer | `POST /sessions/:id/actions/replace-reviewer` |
| Manager | Postpone | `POST /sessions/:id/actions/postpone` |
| Lecturer | Invitations | `GET /lecturer/me/invitations` |
| Lecturer | Respond Invitation | `POST /rounds/:id/invitations/me/respond` |
| Lecturer | Availability | `GET/PUT /rounds/:id/availability/me` |
| Lecturer | My Schedule | `GET /lecturer/me/sessions` |
| Lecturer | Supervised Projects | `GET /lecturer/me/supervised-projects` |
| Lecturer | Session Detail | `GET /sessions/:id` |
| Lecturer | Enter Result | `POST /sessions/:id/result` |
| Lecturer | Remediations | `GET /lecturer/me/remediations` |
| Lecturer | Verify Remediation | `POST /remediations/:id/verify` |
| Leader | Dashboard | `GET /leader/me/dashboard` |
| Leader | Preference | `GET/PUT /rounds/:id/groups/:groupId/preferences` |
| Leader | Group Schedule | `GET /leader/me/sessions` |

---

# PHẦN XVIII — BACKEND MODULES

```text
SemesterModule
StudentModule
EnrollmentModule

GroupModule
ProjectModule

RoundModule

InvitationModule
AvailabilityModule
GroupPreferenceModule

EligibilityModule

SchedulingModule
├── CandidateBuilder
├── ConstraintBuilder
├── CpSatSolver
├── ScoreService
├── DiagnosisService
└── ScheduleVersionService

CouncilModule
SessionModule

RoomModule
RoomAssignmentModule

ResultModule
ProgressionModule
RemediationModule

AuditModule
NotificationModule
```

Boundary:

```text
SchedulingModule
= Time + Council

RoomAssignmentModule
= physical Room

ProgressionModule
= Project state transition

SessionModule
= operational lifecycle
```

---

# PHẦN XIX — END-TO-END FLOW

```text
SEMESTER ACTIVE
       ↓
CREATE GROUP
       ↓
FORMED
       ↓
CREATE PROJECT
       ↓
DRAFT
       ↓
ASSIGN PROJECT TO GROUP
       ↓
Group = ASSIGNED
Project = ACTIVE
       ↓
CREATE ROUND
       ↓
DRAFT
       ↓
CONFIGURE
├── Round Info
├── Days
├── Timeslots
├── Registration
└── Room Types
       ↓
INVITE LECTURERS
       ↓
OPEN_REGISTRATION
├── Lecturer Accept / Decline
├── Lecturer Availability
└── Leader Group Preference
       ↓
REGISTRATION_CLOSED
       ↓
SCHEDULING READINESS
       ↓
GENERATE
       ↓
CP-SAT
├── maximize scheduled groups
├── enforce hard constraints
└── optimize soft constraints
       ↓
ScheduleVersion V1 / V2 / V3
       ↓
SET ACTIVE
       ↓
Round = SCHEDULED
Sessions = PLANNED
       ↓
ROOM ASSIGNMENT
├── Room ACTIVE
├── type ∈ Round.roomTypes
└── no timeslot-room conflict
       ↓
PUBLISH READINESS
       ↓
PUBLISH
       ↓
Round = PUBLISHED
Version = PUBLISHED
Sessions = SCHEDULED
       ↓
ONGOING
├── Result
├── Replace Reviewer
├── Change Room
├── Postpone
└── Group Absent
       ↓
PROJECT PROGRESSION
       ↓
COMPLETED
       ↓
LOCKED
```

---

# PHẦN XX — IMPLEMENTATION NOTES

## FE

```text
FE validate:
required
format
conditional fields
local consistency

BE always re-validates domain rules.
```

## BE

```text
Do not let FE PATCH raw status.

All state transitions use action endpoints:
open-registration
close-registration
set-active
publish
postpone
...
```

## Scheduler

```text
No Room in CP-SAT.

Do not fail entire generation
when some Groups cannot be scheduled.

Always return:
ScheduleVersion
+
Unscheduled diagnostics
```

## Room

```text
Round selects RoomType only.

No individual Room selection during Create Round.

Room Assignment starts after Active ScheduleVersion.
```

## Project vs Group

```text
GroupStatus
= organizational lifecycle

ProjectStatus
= academic progression
```
