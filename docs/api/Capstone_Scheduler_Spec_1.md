# Capstone Scheduler — Đặc tả nghiệp vụ

*SRS baseline · UI/UX · Rule engine*

44 màn hình chia theo ba vai trò vận hành một học kỳ Capstone: tổ chức đợt đánh giá, xếp lịch bảo vệ, và theo dõi kết quả & remediation từ Review đến Defense 2.

| Chỉ số | Giá trị |
|---|---|
| Màn hình đề xuất | 44 |
| Role vận hành | 3 |
| Ràng buộc cứng | H1–H13 |
| Ràng buộc mềm ưu tiên | 8 |
| Backend entity cốt lõi | 9 |

---

## I · Cấu trúc tổng thể

```
Semester
│
├── Project
│    └── Supervisor MAIN / CO
│
├── Group
│    └── Project Leader
│
└── Evaluation Round
     │
     ├── Review 1 · Review 2
     ├── Defense 1.1 · Defense 1.2 · Defense 2
     │
     ├── Timeslot · Lecturer Invitation · Lecturer Availability
     ├── Group Availability · Rooms
     │
     └── ScheduleVersion
             │
             └── Session
                  ├── Group · Time · Room
                  ├── Reviewers · Result Owner
                  └── Result
```

Ba vai trò vận hành hệ thống:

- **Manager** — Điều phối & vận hành học kỳ (màn hình 01–28)
- **Lecturer** — Giảng viên · Reviewer · Supervisor (màn hình 29–38)
- **Project Leader** — Đại diện nhóm sinh viên (màn hình 39–44)

---

## II–IV · Roles & Screens

## Manager (01–28)

### 01 · Tổng quan

**Fields hiển thị**

Current Semester, Semester Status, Total Projects, Total Groups, Total Lecturers, Total Students, Current Round, Round Status, Registration Deadline, Invited Lecturers, Accepted Lecturers, Rejected Lecturers, Availability Submitted, Availability Missing, Eligible Groups, Scheduled Groups, Unscheduled Groups, Pending Change Requests, Absent Lecturers, Remediation Overdue, Groups Without Leader, Groups Under 4 Members.

**Actions**

Xem đợt hiện tại · Xem lịch đánh giá · Xem nhóm chưa xếp được · Xem Lecturer chưa submit · Xem Change Request · Xem Remediation Overdue

---

### 02 · Học kỳ — Danh sách

**Fields**: Semester Code, Semester Name, Start Date, End Date, Status, Project Count, Group Count, Round Count

**Filters**: Search, Status, Academic Year

**Actions**: + Tạo học kỳ · Xem · Chỉnh sửa · Chọn làm học kỳ hiện tại · Khóa

---

### 03 · Tạo / sửa học kỳ

**Input fields**: Semester Code *, Semester Name *, Start Date *, End Date *, Note

**System fields**: Status, Created At, Created By, Updated At, Updated By

**Validation**: Semester Code unique · Start Date < End Date

---

### 04 · Đề tài — Danh sách

**Fields**: Project Code, Project Name, Main Supervisor, Co-Supervisor, Assigned Group, Current Status

**Filters**: Search Project, Supervisor, Has Group / No Group, Status

**Actions**: + Tạo đề tài · Import Excel · Xem · Chỉnh sửa · Assign Supervisor · Assign Group

---

### 05 · Đề tài chi tiết

**Fields**: Project Code, Vietnamese Name, English Name, Main Supervisor, Co-Supervisor, Assigned Group, Group Leader, Member Count, Current Group Stage, Current Group Status

**Actions**: Chỉnh sửa Project · Đổi Main Supervisor · Đổi Co-Supervisor · Gán / đổi Group

**Rules**

- Project có 1–2 Supervisor
- Nếu có 2: 1 MAIN + 1 CO
- MAIN và CO đều không được làm Reviewer của chính Project mình hướng dẫn

---

### 06 · Nhóm sinh viên

**Fields**: Group Code, Project, Main Supervisor, Leader, Member Count, Current Stage, Current Status, Next Stage, Warning

**Filters**: Search, Supervisor, Current Stage, Current Status, Warning Type

**Actions**: + Tạo nhóm · Import · Xem chi tiết · Assign Leader · Mark Dropout

---

### 07 · Group Detail — Tổng quan

**Fields**: Group Code, Project, Main Supervisor, Co-Supervisor, Leader, Initial Member Count, Current Member Count, Current Stage, Current Status, Next Stage, Current Round, Next Evaluation

**Actions**: Edit Group · Change Leader · Open Project · Open Current Round

---

### 08 · Group Detail — Thành viên

**Fields**: Student ID, Full Name, Role (LEADER / MEMBER), Membership Status (ACTIVE / DROPPED), Joined At, Left At, Dropout Reason

**Actions**: Add Member · Set as Leader · Mark Dropout

**Dropout form**: Student *, Effective Date *, Reason *, Approved By, Note

**Rule**

- Không xóa membership cũ — giữ joinedAt / leftAt / status
- Nếu Leader dropout: Group phải có Leader mới trước scheduling

---

### 09 · Group Detail — Tiến độ

**Fields mỗi stage**: Round Type, Round Name, Session Date, Result, Progression State, Next Stage, Remediation Status

**Timeline ví dụ**

- Review 1 · PASS · 12/06
- Review 2 · NEEDS_FIX · 15/07
- Defense 1.1 · LEVEL 2 · 25/08
- Remediation · PENDING · hạn 30/08
- Defense 1.2 · WAITING

---

### 10 · Group Detail — Kết quả

**Fields**: Round, Session, Result, Note, Entered By, Entered At, Last Modified By, Last Modified At, Remediation Deadline, Remediation Verifier, Remediation Status

---

### 11 · Đợt đánh giá — Danh sách

**Fields**: Round Name, Round Type, Status, Start Date, End Date, Duration, Required Reviewers, Eligible Groups, Scheduled Groups, Registration Deadline

**Actions**: + Tạo đợt đánh giá · Xem · Edit nếu còn cho phép

**Lifecycle**

```
DRAFT → OPEN_REGISTRATION → REGISTRATION_CLOSED → SCHEDULING → SCHEDULED
→ PUBLISHED → ONGOING → COMPLETED → LOCKED
```

---

### 12 · Round Detail — Tổng quan

**Fields**: Semester, Round Name, Round Type, Status, Registration Deadline, Evaluation Start Date, Evaluation End Date, Duration Minutes, Required Reviewer Count, Eligible Groups, Participating Groups, Invited Lecturers, Accepted Lecturers, Rejected Lecturers, Availability Submitted, Availability Missing, Timeslot Count, Selected Room Count, Scheduled Groups, Unscheduled Groups

**Actions theo trạng thái**

| Status | Action |
|---|---|
| DRAFT | → Edit / Open Registration |
| OPEN_REGISTRATION | → Close Registration |
| REGISTRATION_CLOSED | → Start Scheduling |
| SCHEDULED | → Publish |
| PUBLISHED | → Manage Sessions |
| ONGOING | → Complete Round |

---

### 13 · Round Detail — Cấu hình

**Fields nhập**: Round Name *, Round Type *, Duration Minutes *, Reviewer Count *, Registration Deadline *, Evaluation Dates *, Morning Start, Morning End, Afternoon Start, Afternoon End, Max Groups / Timeslot *, Group Selection Mode, Result Owner Mode

**Advanced fields**: Max Minutes / Half Day, Max Minutes / Day

**Actions**: Generate Timeslots · Save Configuration

---

### 14 · Round Detail — Timeslots

**Fields**: Date, Start Time, End Time, Enabled, Capacity / Max Parallel Groups

**Actions**: Add Timeslot · Edit Timeslot · Disable Timeslot · Delete Draft Timeslot

---

### 15 · Round Detail — Giảng viên

**Gom**: Invitation · Availability · Workload

**Fields**: Lecturer Code, Lecturer Name, Invitation Status, Sent At, Response At, Reject Reason, Availability Status, Available Slot Count, Preferred Load, Semester Quota, Used Sessions, Used Percentage

**Filters**: Invitation Status, Availability Status, Preferred Load

**Actions**: Invite Lecturer · Resend Invitation · Send Reminder · View Availability · Enter Availability on Behalf

---

### 16 · Lecturer Availability Drawer

**Fields**: Lecturer, Round, Invitation Status, Preferred Load, Semester Quota, Used Quota, Timeslot Grid

**Rule**: Lecturer không submit availability = BUSY ALL

---

### 17 · Round Detail — Nhóm tham gia

**Fields**: Group Code, Project, Leader, Member Count, Eligibility, Eligibility Reason, Group Availability Status, Selected Slot Count, Effective Availability, Scheduling Status

**Rule**: Nếu groupSelectionMode = ON và Group không submit trước deadline → Effective Availability = ALL TIMESLOTS

---

### 18 · Round Detail — Phòng sử dụng

**Fields**: Room Code, Room Name, Capacity, Location, Equipment, Room Status, Selected For Round

**Actions**: Select Room · Unselect Room

**Rule**: Không cho chọn Room inactive / maintenance

---

### 19 · Round Detail — Xếp lịch

**Readiness fields**: Eligible Groups, Lecturers Accepted, Lecturers With Availability, Selected Rooms, Timeslots, Required Sessions, Estimated Capacity, Blocking Issues

**Action**: Generate Schedule

---

### 20 · ScheduleVersion — Danh sách

**Fields**: Version Number, Created At, Created By, Scheduled Groups, Unscheduled Groups, Overall Score, Balance Score, Continuity Score, Compactness Score, Room Efficiency Score, isActive, Status

**Actions**: Generate New · View · Compare · Set Active · Delete Draft · Open on Calendar

**Rule**: Mỗi lần chạy scheduler → tạo ScheduleVersion mới, không overwrite version trước

---

### 21 · Unscheduled Groups

**Fields**: Group, Project, Failure Reason, Related Constraints, Suggested Resolution

**Ví dụ**

| Group | Failure Reason | Related Constraints | Suggested Resolution |
|---|---|---|---|
| G17 | No sufficient eligible reviewers | H1 · H7 · H8 | Invite additional Lecturer / Open more Timeslots |

**Rule**: Không có full solution → vẫn lưu partial ScheduleVersion, trả danh sách Group chưa xếp được kèm nguyên nhân cụ thể

---

### 22 · Lịch đánh giá

**Header fields**: Current Semester, Selected Round, Current Date Range, View Mode (DAY / WEEK / LIST)

**Filters**: Room, Lecturer, Group, Session Status

**Calendar event fields**: Group Code, Project Short Name, Start Time, End Time, Room, Reviewer Summary, Status

---

### 23 · Session Detail

**Fields**: Session ID, Semester, Round, Group, Project, Date, Start Time, End Time, Room, Reviewers, Result Owner, Status, Published At, Last Updated At

**Optional field**: Previous Defense Reviewers

**Actions trước Publish**: Change Time · Change Room · Replace Reviewer · Change Result Owner

**Actions sau Publish**: Change Time · Change Room · Replace Reviewer · Postpone

**Rule**: Sau Publish: mọi thay đổi phải có reason + audit

---

### 24 · Replace Reviewer Modal

**Fields hiển thị**: Current Reviewer, Candidate Lecturer, Availability, Time Conflict, Supervisor Conflict, Conflict of Interest, Current Workload, Semester Quota, Eligible / Not Eligible

**Input**: New Reviewer *, Reason *

---

### 25 · Change / Postpone Session

**Fields**: Requester, Request Type, Request Reason, Current Date, Current Time, Current Room, New Date, New Timeslot, New Room, Manager Decision, Manager Reason

**Actions**: Approve · Reject · Reschedule

---

### 26 · Kết quả đánh giá

**Fields**: Group, Project, Round, Result, Entered By, Entered At, Remediation Status, Deadline, Verifier, Current Group State, Next Stage

**Tabs**: Tất cả · Waiting Remediation · Overdue · Completed · Failed

**Filters**: Round, Result, Supervisor, Group, Remediation Status

---

### 27 · Result Detail

**Fields**: Group, Project, Round, Session, Result, Note, Entered By, Entered At, Last Modified By, Last Modified At

**Nếu LEVEL 2**: Remediation Deadline, Verifier, Remediation Status, Verified At, Verifier Note

**Actions**: Open Session · View Audit · Edit Result

**Edit Result fields**: Old Result, New Result *, Reason *

---

### 28 · Báo cáo

**Workload fields**: Lecturer, Preferred Load, Session Count, Total Minutes, Semester Quota, Used %

**Result Distribution**: Round, Total Groups, LEVEL 1 Count, LEVEL 2 Count, LEVEL 3 Count, LEVEL 4 Count

**Attention Groups**: Group, Issue Type, Severity, Description, Current Stage, Suggested Action

**Export**: Report Type, Round, Date Range, Format

**Action**: Export Excel

---

## Lecturer (29–38)

### 29 · Dashboard

**Fields**: Pending Invitations, Missing Availability, Upcoming Sessions, Supervised Group Count, Pending Result Entries, Pending Remediation Verification

**Upcoming card**: Round, Group, Time, Room, My Role

---

### 30 · Lời mời

**Fields**: Semester, Round, Evaluation Start, Evaluation End, Duration, Registration Deadline, Invitation Status, Sent At, Response At

**Actions**: Accept · Reject (Reason *)

---

### 31 · Đăng ký lịch rảnh

**Fields**: Round, Registration Deadline, Preferred Load, Timeslot Grid, Submission Status, Last Submitted At

**Actions**: Select · Unselect · Select All · Clear · Save · Submit

**Rule**: Không submit = BUSY ALL

---

### 32 · My Schedule

**Fields / Event**: Round, Group, Project, Date, Start Time, End Time, Room, My Role, Session Status

**Filters**: Round, Role, Date

---

### 33 · Nhóm hướng dẫn

**Fields**: Group, Project, Leader, Member Count, Current Stage, Current Status, Latest Result, Next Evaluation, Remediation Status

**Actions**: Open Group · View Progress · View Result · Assign/Change Leader nếu quyền được bật

---

### 34 · Supervised Group Detail

**Tabs**: Tổng quan · Tiến độ · Kết quả

**Tổng quan fields**: Group, Project, Leader, Member Count, Current Stage, Current Status, Next Evaluation

**Tiến độ**: Review 1 Result, Review 2 Result, Defense 1.1 Result, Remediation, Defense 1.2 / Defense 2

---

### 35 · Phiên đánh giá

**Fields**: Session, Round, Group, Project, Supervisor, Date, Time, Room, My Role, Other Reviewers, Result Status

**Actions**: Request Change · Enter Result

---

### 36 · Review Result Form

**Fields**: Group, Round, Result * (PASS / NEEDS_FIX / FAIL), Note

**Rule**: Review result không block Group đi Defense 1.1

---

### 37 · Defense Result Form

**Fields**: Group, Round, Conclusion * (LEVEL 1 / 2 / 3 / 4), Note

**Nếu LEVEL 2**: Remediation Deadline *, Remediation Verifier *

**Rule**

- resultOwnerMode = ON → chỉ Result Owner submit
- resultOwnerMode = OFF → Reviewer trong Session có thể submit theo quyền

---

### 38 · Remediation Verification

**Fields**: Group, Project, Source Round, Source Result, Deadline, Current Remediation Status

**Input**: Verification Result * (PASS / NOT_PASSED), Note

**Action**: Confirm

**Rule**: PASS → D12_CONDITIONAL → ELIGIBLE_D12

---

## Project Leader (39–44)

### 39 · Dashboard

**Fields**: Group Code, Project, Main Supervisor, Co-Supervisor, Member Count, Current Stage, Current Status, Current Round, Availability Status, Registration Deadline, Upcoming Session, Latest Result, Remediation Status, Remediation Deadline

**Không có**: Member List · Member Management · Dropout Management

---

### 40 · Đăng ký lịch nhóm

*Chỉ hiện khi groupSelectionMode = ON*

**Fields**: Round, Registration Deadline, Timeslot Grid, Submission Status, Last Submitted At

**Actions**: Select · Unselect · Select All · Clear · Submit · Edit before deadline

**Rule**: Leader đại diện toàn Group. Không submit trước deadline → Group = AVAILABLE ALL

---

### 41 · Lịch của nhóm

**Fields mỗi event**: Round, Date, Start Time, End Time, Room, Session Status

**Ví dụ**

- ✓ Review 1 · 12/06 · 08:00–08:45 · P201
- ✓ Review 2 · 15/07 · 10:00–10:45 · P203
- ● Defense 1.1 · 25/08 · 08:00–09:00 · P201

---

### 42 · Session Detail

**Fields**: Round, Date, Time, Room, Status, Project

**Không cần show**: ScheduleVersion · Constraint Score · Lecturer Quota · Internal Scheduler Data

**Action**: Request Change

---

### 43 · Change Request

**Fields**: Session, Request Type * (CHANGE_TIME / POSTPONE), Reason *, Request Status, Submitted At, Manager Decision, Manager Note

**Rule**: Leader không chọn Reviewer mới · không đổi Room trực tiếp · không tự reschedule

---

### 44 · Kết quả

**Fields**: Round, Result, Note, Current Group State, Next Stage, Remediation Status, Remediation Deadline

**Timeline**

- Review 1 · PASS
- Review 2 · NEEDS_FIX
- Defense 1.1 · LEVEL 2
- Remediation · PENDING
- Defense 1.2 · WAITING

---

## V – VI · Ràng buộc xếp lịch

*Hard & soft constraints.* Vi phạm ràng buộc cứng khiến lịch không hợp lệ; ràng buộc mềm chỉ ảnh hưởng điểm chất lượng của ScheduleVersion.

### Ràng buộc cứng

| Mã | Ràng buộc cứng |
|---|---|
| H1 | GVHD MAIN/CO không được Reviewer Project mình hướng dẫn |
| H2 | Một Lecturer không được ở 2 Session cùng giờ |
| H3 | Một Room không được có 2 Session cùng giờ |
| H4 | Một Group chỉ có đúng 1 Session trong một Round |
| H5 | Đủ số Reviewer theo loại Round |
| H6 | Một Lecturer chỉ xuất hiện một lần trong cùng Council |
| H7 | Chỉ assign Lecturer vào Timeslot họ đăng ký rảnh |
| H8 | Không assign Lecturer có Conflict of Interest với Project |
| H9 | Group phải có progression state hợp lệ với Round |
| H10 | Nếu Group đã chọn availability thì chỉ schedule trong slot đã chọn |
| H11 | Defense 1.2 phải giữ ít nhất 1 Reviewer của Defense 1.1; override phải có reason |
| H12 | Lecturer ≤240 phút/buổi, ≤480 phút/ngày, không vượt semester quota |
| H13 | Số Session trong một Timeslot không vượt maxGroupsPerTimeslot |

### Số reviewer bắt buộc / round

| Round | Số Reviewer |
|---|---|
| Review 1 | 2 |
| Review 2 | 2 |
| Defense 1.1 | 3 |
| Defense 1.2 | 5 |
| Defense 2 | 5 |

### Ràng buộc mềm (theo ưu tiên)

| Ưu tiên | Ràng buộc mềm |
|---|---|
| 1 | Cân bằng workload theo % semester quota used, có xét Preferred Load |
| 2 | Review 2 ưu tiên giữ cặp Reviewer của Review 1 |
| 3 | Defense 1.2 ưu tiên giữ thêm Reviewer thứ 2 của Defense 1.1 |
| 4 | Gom Session của Lecturer liên tiếp |
| 5 | Giảm số ngày Lecturer phải có mặt |
| 6 | Giữ tổ hợp Reviewer ổn định giữa các Session liên tiếp |
| 7 | Tránh Lecturer chấm quá nhiều Group của cùng Supervisor |
| 8 | Dùng ít Room nhất |

---

## VII – XIII · Business logic

*Vòng đời đánh giá & xếp lịch* — từ availability, qua Review không-chặn-tiến-độ, đến rẽ nhánh Defense 1.1, remediation, Defense 2 và vận hành sau Publish.

### VII · Availability

Không khai báo = mặc định bận / rảnh toàn bộ.

- **Lecturer**: không submit → BUSY ALL
- **Group**: groupSelectionMode = ON, Leader không submit trước deadline → AVAILABLE ALL TIMESLOTS

### VIII · Review 1 → Review 2

Kết quả Review không chặn tiến độ nhóm.

```
ACTIVE
  ↓
Review 1 → PASS / NEEDS_FIX / FAIL
  ↓ không block
Review 2 → PASS / NEEDS_FIX / FAIL
  ↓ không block
Defense 1.1
```

### IX · Defense 1.1 — rẽ 4 nhánh

Kết luận Defense 1.1 quyết định hướng đi tiếp theo của nhóm.

- **LEVEL 1** → ELIGIBLE_D12 → Defense 1.2
- **LEVEL 2** → D12_CONDITIONAL → Remediation
- **LEVEL 3** → PENDING_D2 → Defense 2
- **LEVEL 4** → FAILED

**LEVEL 2**: bắt buộc có Deadline + Verifier. PASS → ELIGIBLE_D12 → Defense 1.2.

**Overdue**: → System Warning → Manager Review → Manager chốt FAILED (không auto FAILED)

### X · Defense 2

```
PENDING_D2
  ↓
Defense 2
PASS → COMPLETED
FAIL → FAILED
```

### XI · Scheduling pipeline

```
Tạo Round → Timeslot → Rooms
  ↓
Mời Lecturer → Accept/Reject → Availability
  ↓
Group Availability (nếu bật)
  ↓
Close Registration → Scheduler
  ↓
Check H1–H13 → ScheduleVersion V1…Vn
  ↓
Compare Soft Scores → Set Active → Publish
```

### XII · Sau Publish

Không rerun toàn Round — chỉ chỉnh từng Session.

```
Session → Change Time/Room/Reviewer
  ↓
Check Constraints → Reason → Save
  ↓
Audit → Notify
```

Không tìm được Reviewer thay → Postpone → Make-up Session

### XIII · ScheduleVersion

Mỗi lần chạy scheduler tạo version mới, không ghi đè bản trước.

- V1, V2, V3… — chỉ một version `isActive` tại một thời điểm
- **Partial result**: ví dụ Scheduled 70/74, Unscheduled 4 — vẫn lưu kèm lý do cụ thể

---

## XIV · Phân quyền cuối cùng

Ma trận quyền theo vai trò

| Nghiệp vụ | Manager | Lecturer | Project Leader |
|---|---|---|---|
| Quản lý Semester | ✓ | — | — |
| Quản lý Project | ✓ | — | — |
| Quản lý Group membership | ✓ | — | — |
| Phân Supervisor | ✓ | — | — |
| Chỉ định Leader | ✓ | Supervisor theo quyền | — |
| Tạo Round | ✓ | — | — |
| Cấu hình Round | ✓ | — | — |
| Chọn Room | ✓ | — | — |
| Mời Lecturer | ✓ | — | — |
| Accept/Reject Invitation | — | ✓ | — |
| Lecturer Availability | theo dõi / nhập hộ | ✓ | — |
| Preferred Load | xem | ✓ | — |
| Group Availability | theo dõi | — | ✓ |
| Run Scheduler | ✓ | — | — |
| ScheduleVersion | ✓ | — | — |
| Publish | ✓ | — | — |
| Xem lịch | ✓ | ✓ cá nhân | ✓ nhóm |
| Sửa Session | ✓ | — | — |
| Change Request | xử lý | gửi | gửi |
| Review Result | quản trị | Reviewer | — |
| Defense Result | quản trị | Result Owner / Reviewer | — |
| Verify Remediation | theo dõi | Verifier | — |
| Chốt overdue FAILED | ✓ | — | — |
| Group Progress | ✓ | Supervisor | ✓ nhóm |
| Reports | ✓ | — | — |

---

## XV · UI Navigation đề xuất

Menu chính theo vai trò

**Manager**: Tổng quan · Học kỳ · Đề tài · Nhóm sinh viên · Đợt đánh giá · Lịch đánh giá · Kết quả đánh giá · Báo cáo

**Lecturer**: Tổng quan · Lời mời · Đăng ký lịch rảnh · Lịch của tôi · Nhóm hướng dẫn · Phiên đánh giá · Khắc phục

**Project Leader**: Tổng quan · Đăng ký lịch · Lịch của nhóm · Kết quả

---

## XVI · Core backend fields

Entity đề xuất

### Semester
- id
- code
- name
- startDate
- endDate
- status

### Project
- id
- code
- nameVi
- nameEn
- semesterId

### Group
- id
- code
- projectId
- leaderId
- memberCount
- progressState

### EvaluationRound
- id
- semesterId
- type
- name
- status
- durationMinutes
- reviewerCount
- registrationDeadline
- groupSelectionMode
- resultOwnerMode

### ScheduleVersion
- id
- roundId
- versionNumber
- isActive
- overallScore
- createdAt

### Session
- id
- scheduleVersionId
- roundId
- groupId
- timeslotId
- roomId
- resultOwnerId
- status

### SessionReviewer
- sessionId
- lecturerId

### Result
- id
- sessionId
- result
- note
- enteredBy
- enteredAt

### Remediation
- id
- groupId
- sourceSessionId
- deadline
- verifierId
- status
- verifiedAt

---

*Capstone Scheduler — Roles, Screens, Fields, Constraints & Business Logic*
*Baseline cho SRS · UI/UX · Rule engine*
