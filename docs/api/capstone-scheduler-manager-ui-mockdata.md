# Capstone Scheduler --- Manager UI Specification & Mock Data

> Tài liệu này cụ thể hóa UI cho role **Manager** dựa trên PRD/Business
> Rules đã trao đổi.\
> Mục tiêu: dùng làm tài liệu tham chiếu cho thiết kế UI/UX, frontend
> mockup và seed/mock data.
>
> **Lưu ý nghiệp vụ:** PRD hiện tại được ưu tiên khi có khác biệt với
> Business Rules cũ. Hội đồng dùng **Reviewer ngang hàng**; app chỉ lưu
> kết quả cuối để điều hướng nhóm, không triển khai Gate 0 / 9 tiêu chí
> / phiếu chấm chi tiết.

------------------------------------------------------------------------

## 1. Sidebar đề xuất

``` text
MANAGER

Dashboard

ACADEMIC
├── Semesters
├── Projects
└── Groups

EVALUATION
├── Rounds
├── Invitations
└── Availability

SCHEDULING
├── Schedule Versions
└── Sessions

OPERATIONS
├── Schedule Changes
└── Remediation

RESULTS
├── Group Progress
└── Results

REPORTS
├── Lecturer Workload
├── Attention Groups
└── Reports
```

Các action như `Generate Schedule`, `Publish`, `Set Active`,
`Replace Reviewer`, `Assign Supervisor`, `Mark Failed` nằm trong màn
hình nghiệp vụ tương ứng, không cần trở thành sidebar item.

------------------------------------------------------------------------

# 2. Dashboard

## Mục đích

Cho Manager nhìn nhanh tình trạng học kỳ, round hiện tại, registration,
scheduling và các vấn đề cần xử lý.

## Hiển thị

-   Semester đang chọn.
-   Tổng Project.
-   Tổng Group.
-   Tổng Student.
-   Tổng Lecturer.
-   Round hiện tại và trạng thái.
-   Tỷ lệ Lecturer đã submit availability.
-   Số Group đã/ chưa schedule.
-   Attention items:
    -   Group dưới 4 thành viên.
    -   Group chưa có Leader.
    -   Remediation quá hạn.
    -   Group chưa schedule được.

## Actions

-   View Current Round.
-   View Missing Availability.
-   View Active Schedule.
-   View Attention Groups.

## Mock data

``` json
{
  "semester": "SU26",
  "projects": 74,
  "groups": 74,
  "students": 330,
  "lecturers": 28,
  "currentRound": {
    "id": "ER-D11-SU26",
    "name": "Defense 1.1",
    "status": "OPEN_REGISTRATION"
  },
  "registration": {
    "invited": 26,
    "accepted": 24,
    "availabilitySubmitted": 21
  },
  "scheduling": {
    "scheduledGroups": 70,
    "totalEligibleGroups": 74,
    "unscheduledGroups": 4
  },
  "attention": {
    "noLeader": 2,
    "underFourMembers": 3,
    "remediationOverdue": 1,
    "unscheduled": 4
  }
}
```

------------------------------------------------------------------------

# 3. Academic --- Semesters

## Semester List

Hiển thị:

-   Code.
-   Name.
-   Start date.
-   End date.
-   Status.
-   Số Project / Group.

## Actions

-   Create Semester.
-   View Semester.
-   Edit khi chưa locked.
-   Lock Semester.
-   Chọn Semester làm working context.

> Việc mở khóa dữ liệu `LOCKED` thuộc Admin.

## Mock data

  Code   Name          Start        End          Status     Projects   Groups
  ------ ------------- ------------ ------------ -------- ---------- --------
  SU26   Summer 2026   2026-05-04   2026-09-06   ACTIVE           74       74
  SP26   Spring 2026   2026-01-05   2026-04-26   LOCKED           69       69
  FA25   Fall 2025     2025-09-08   2025-12-28   LOCKED           71       71

## Semester Detail

Tabs:

-   Overview.
-   Projects.
-   Groups.
-   Evaluation Rounds.

------------------------------------------------------------------------

# 4. Academic --- Projects

## Project List

Hiển thị:

-   Project code.
-   Project name.
-   Main Supervisor.
-   Co-Supervisor.
-   Group.
-   Status.

## Actions

-   Create Project.
-   Import Projects.
-   Edit Project.
-   Assign Main Supervisor.
-   Assign Co-Supervisor.
-   Open associated Group.

## Mock data

  ---------------------------------------------------------------------------
  Code           Project        Main           Co-Supervisor   Group
                                Supervisor                     
  -------------- -------------- -------------- --------------- --------------
  SU26SE001      Smart Factory  LEC001 -       LEC006 - Trần   G01
                 AI Monitoring  Nguyễn Minh An Quốc Huy        

  SU26SE002      AI Education   LEC002 - Lê    ---             G02
                 Platform       Thanh Bình                     

  SU26SE003      EV Charging    LEC003 - Phạm  LEC008 - Võ     G03
                 Management     Hoàng Nam      Minh Đức        

  SU26SE004      Local AI CRM   LEC004 - Trần  ---             G04
                                Hải Long                       
  ---------------------------------------------------------------------------

## Project Detail

``` text
SU26SE001
Smart Factory AI Monitoring

MAIN SUPERVISOR
LEC001 - Nguyễn Minh An

CO-SUPERVISOR
LEC006 - Trần Quốc Huy

GROUP
G01
```

### Business rules

-   Project có 1--2 Supervisor.
-   Nếu có 2: một `MAIN`, một `CO`.
-   Cả Main và Co Supervisor đều không được làm Reviewer của chính
    Project đó.

------------------------------------------------------------------------

# 5. Academic --- Groups

## Group List

Hiển thị:

-   Group code.
-   Project.
-   Active members.
-   Leader.
-   Supervisor.
-   Current progression state.
-   Warning.

## Mock data

  ----------------------------------------------------------------------------------
  Group       Project            Members Leader      Current State     Warning
  ----------- ----------- -------------- ----------- ----------------- -------------
  G01         SU26SE001                5 ST001 -     D12_CONDITIONAL   Remediation
                                         Nguyễn Văn                    pending
                                         An                            

  G02         SU26SE002                4 ST006 -     ELIGIBLE_D12      ---
                                         Trần Minh                     
                                         Bình                          

  G03         SU26SE003                3 ST010 - Lê  ACTIVE            Under 4
                                         Hoàng Minh                    members

  G04         SU26SE004                4 ---         ACTIVE            No Leader

  G05         SU26SE005                5 ST019 -     PENDING_D2        Waiting
                                         Phạm Gia                      Defense 2
                                         Huy                           
  ----------------------------------------------------------------------------------

## Actions

-   Create Group.
-   Import Groups.
-   Assign Project.
-   Add Student.
-   Mark Student dropout.
-   Assign/Change Leader.
-   View progression.
-   View results.
-   View remediation.

## Group Detail

Tabs:

``` text
Overview
Members
Project & Supervisors
Progress
Results
Remediation
History
```

### Mock members --- G01

  Student ID   Name             Role     Status   Joined       Left
  ------------ ---------------- -------- -------- ------------ ------
  ST001        Nguyễn Văn An    LEADER   ACTIVE   2026-05-04   ---
  ST002        Trần Minh Khoa   MEMBER   ACTIVE   2026-05-04   ---
  ST003        Lê Gia Huy       MEMBER   ACTIVE   2026-05-04   ---
  ST004        Phạm Hoàng Anh   MEMBER   ACTIVE   2026-05-04   ---
  ST005        Võ Thanh Tùng    MEMBER   ACTIVE   2026-05-04   ---

### Dropout rule

Không xóa membership cũ. Lưu:

``` json
{
  "studentId": "ST012",
  "groupId": "G03",
  "joinedAt": "2026-05-04",
  "leftAt": "2026-07-21",
  "status": "DROPPED",
  "reason": "Approved withdrawal"
}
```

Nếu Leader dropout, Group phải được gán Leader mới trước khi scheduling.

------------------------------------------------------------------------

# 6. Evaluation --- Rounds

## Round List

  -----------------------------------------------------------------------------------------
  Round      Type          Status                    Duration      Reviewers Registration
                                                                             Deadline
  ---------- ------------- ------------------- -------------- -------------- --------------
  Review 1 - REVIEW_1      COMPLETED                   45 min              2 2026-06-10
  SU26                                                                       

  Review 2 - REVIEW_2      COMPLETED                   45 min              2 2026-07-08
  SU26                                                                       

  Defense    DEFENSE_1_1   OPEN_REGISTRATION           60 min              3 2026-08-22
  1.1 - SU26                                                                 

  Defense    DEFENSE_1_2   DRAFT                       90 min              5 ---
  1.2 - SU26                                                                 

  Defense    DEFENSE_2     DRAFT                       90 min              5 ---
  2 - SU26                                                                   
  -----------------------------------------------------------------------------------------

## Lifecycle

``` text
DRAFT
  ↓
OPEN_REGISTRATION
  ↓
REGISTRATION_CLOSED
  ↓
SCHEDULING
  ↓
SCHEDULED
  ↓
PUBLISHED
  ↓
ONGOING
  ↓
COMPLETED
  ↓
LOCKED
```

## Actions

Tùy trạng thái:

-   Create Round.
-   Edit Configuration.
-   Generate Timeslots.
-   Open Registration.
-   Close Registration.
-   Start Scheduling.
-   Publish Schedule.
-   Complete Round.
-   Lock Round.

Sau `PUBLISHED`, không được rerun scheduler cho toàn Round.

------------------------------------------------------------------------

# 7. Round Detail

Tabs đề xuất:

``` text
Overview
Configuration
Timeslots
Eligible Groups
Invitations
Registration
```

## Configuration mock

``` json
{
  "id": "ER-D11-SU26",
  "type": "DEFENSE_1_1",
  "durationMinutes": 60,
  "reviewerCount": 3,
  "registrationDeadline": "2026-08-22T23:59:59+07:00",
  "startDate": "2026-08-25",
  "endDate": "2026-08-27",
  "morning": {
    "start": "08:00",
    "end": "12:00"
  },
  "afternoon": {
    "start": "13:30",
    "end": "17:30"
  },
  "maxGroupsPerTimeslot": 6,
  "groupSelectionMode": true,
  "resultOwnerMode": true
}
```

------------------------------------------------------------------------

# 8. Round --- Timeslots

## Hiển thị

  Date         Start   End     Enabled     Max Parallel Groups
  ------------ ------- ------- --------- ---------------------
  2026-08-25   08:00   09:00   Yes                           6
  2026-08-25   09:00   10:00   Yes                           6
  2026-08-25   10:00   11:00   Yes                           6
  2026-08-25   11:00   12:00   Yes                           6
  2026-08-25   13:30   14:30   Yes                           6
  2026-08-25   14:30   15:30   Yes                           6

## Actions

-   Generate from Round configuration.
-   Add Timeslot.
-   Disable Timeslot.
-   Edit trước scheduling.

Room là resource được assign vào Session, không cần gắn cố định với
Timeslot.

------------------------------------------------------------------------

# 9. Evaluation --- Invitations

## Invitation List

  --------------------------------------------------------------------------
  Lecturer       Status         Sent At        Response At    Reject Reason
  -------------- -------------- -------------- -------------- --------------
  LEC001 -       ACCEPTED       18/08 09:00    18/08 10:12    ---
  Nguyễn Minh An                                              

  LEC002 - Lê    ACCEPTED       18/08 09:00    18/08 09:45    ---
  Thanh Bình                                                  

  LEC003 - Phạm  PENDING        18/08 09:00    ---            ---
  Hoàng Nam                                                   

  LEC004 - Trần  REJECTED       18/08 09:00    18/08 11:20    Business trip
  Hải Long                                                    
  --------------------------------------------------------------------------

## Actions

-   Select Lecturers.
-   Send Invitation.
-   Resend Invitation.
-   View response.
-   Filter Accepted/Pending/Rejected.

------------------------------------------------------------------------

# 10. Evaluation --- Availability

## Lecturer Availability Summary

  -----------------------------------------------------------------------------------
  Lecturer   Invitation   Submitted     Available Preferred      Semester        Used
                                            Slots Load              Quota 
  ---------- ------------ ----------- ----------- ----------- ----------- -----------
  LEC001     ACCEPTED     Yes                  12 HIGH                 30          14

  LEC002     ACCEPTED     Yes                   8 MEDIUM               20          12

  LEC003     PENDING      No                    0 ---                  25           8

  LEC005     ACCEPTED     Yes                   4 LOW                  16          11
  -----------------------------------------------------------------------------------

## Detail mock

``` json
{
  "lecturerId": "LEC001",
  "roundId": "ER-D11-SU26",
  "preferredLoad": "HIGH",
  "availableTimeslotIds": [
    "TS-2508-0800",
    "TS-2508-0900",
    "TS-2508-1100",
    "TS-2508-1330"
  ]
}
```

### Rule

Lecturer không submit availability = coi như **bận toàn bộ**.

## Manager actions

-   View submission.
-   Enter/Edit availability on behalf of Lecturer.
-   Set semester quota.
-   Find missing submissions.
-   View slot coverage.

------------------------------------------------------------------------

# 11. Group Availability

Chỉ áp dụng khi `groupSelectionMode = true`.

  Group   Submitted     Selected Slots Effective Availability
  ------- ----------- ---------------- ------------------------
  G01     Yes                        6 Selected slots only
  G02     Yes                        4 Selected slots only
  G03     No                         0 All slots
  G04     Yes                        8 Selected slots only

### Rule

Group không submit trước deadline khi mode bật = coi như **available
toàn bộ**.

------------------------------------------------------------------------

# 12. Scheduling --- Schedule Versions

## Mục đích

Mỗi lần chạy scheduler tạo một phương án lịch mới, không overwrite
phương án trước.

## List mock

  Version   Created At      Scheduled   Unscheduled   Score Status
  --------- ------------- ----------- ------------- ------- --------
  V1        23/08 08:15         71/74             3    84.7 DRAFT
  V2        23/08 08:32         74/74             0    88.2 DRAFT
  V3        23/08 09:05         74/74             0    91.5 ACTIVE

## Actions

-   Generate New Schedule.
-   Open Version.
-   Compare Versions.
-   Set Active.
-   Delete unused draft version.

## ScheduleVersion mock

``` json
{
  "id": "SV-D11-003",
  "roundId": "ER-D11-SU26",
  "versionNumber": 3,
  "isActive": true,
  "createdAt": "2026-08-23T09:05:00+07:00",
  "metrics": {
    "scheduledGroups": 74,
    "totalGroups": 74,
    "overallScore": 91.5,
    "balanceScore": 94,
    "reviewerContinuityScore": 90,
    "compactnessScore": 82,
    "roomEfficiencyScore": 88
  }
}
```

------------------------------------------------------------------------

# 13. Schedule Version Detail

Tabs:

``` text
Overview
Schedule
Unscheduled Groups
Constraint Scores
Compare
```

## Example schedule

  Time          Room   Group   Reviewers
  ------------- ------ ------- ------------------------
  25/08 08:00   P201   G01     LEC007, LEC008, LEC009
  25/08 08:00   P202   G02     LEC010, LEC011, LEC012
  25/08 09:00   P201   G03     LEC007, LEC013, LEC014
  25/08 09:00   P202   G04     LEC008, LEC015, LEC016

## Compare mock

  Metric                     V2      V3
  --------------------- ------- -------
  Scheduled Groups        74/74   74/74
  Balance                    88      94
  Reviewer Continuity        95      90
  Compactness                91      82
  Room Efficiency            80      88
  Overall                  88.2    91.5

------------------------------------------------------------------------

# 14. Scheduler Constraints

## Hard constraints

-   **H1:** Main/Co Supervisor không được Reviewer Project mình hướng
    dẫn.
-   **H2:** Lecturer không được ở hai Session trùng giờ.
-   **H3:** Room không được có hai Session trùng giờ.
-   **H4:** Một Group có đúng một Session trong một Round.
-   **H5:** Đủ Reviewer:
    -   Review 1/2 = 2.
    -   Defense 1.1 = 3.
    -   Defense 1.2 = 5.
    -   Defense 2 = 5.
-   **H6:** Lecturer chỉ xuất hiện một lần trong một hội đồng.
-   **H7:** Lecturer chỉ được assign vào slot đã đăng ký rảnh.
-   **H8:** Không assign Lecturer có Conflict of Interest với Project.
-   **H9:** Group phải đủ progression state của Round.
-   **H10:** Nếu Group đã chọn slot thì chỉ schedule trong các slot đã
    chọn.
-   **H11:** Defense 1.2 phải có ít nhất 1 Reviewer từ Defense 1.1 của
    chính Group; Manager có thể override từng Group nhưng phải ghi lý
    do.
-   **H12:** Tải Lecturer tối đa 240 phút/buổi, 480 phút/ngày và không
    vượt semester quota.
-   **H13:** Số Session trong một Timeslot không vượt
    `maxGroupsPerTimeslot`.

## Soft constraints

Theo thứ tự ưu tiên:

1.  Balance workload theo % quota đã dùng và preferred load.
2.  Review 2 ưu tiên giữ cặp Reviewer của Review 1.
3.  Defense 1.2 ưu tiên giữ thêm Reviewer thứ hai từ Defense 1.1.
4.  Gom Session của cùng Lecturer liên tiếp.
5.  Giảm số ngày Lecturer phải có mặt.
6.  Giữ tổ hợp Reviewer ổn định giữa các Session liên tiếp.
7.  Tránh Lecturer chấm quá nhiều Group của cùng Supervisor.
8.  Dùng ít Room nhất có thể.

------------------------------------------------------------------------

# 15. Unscheduled Groups

Nếu không có lời giải đầy đủ, vẫn lưu ScheduleVersion partial.

## Mock

``` json
[
  {
    "groupId": "G17",
    "reasons": [
      "No sufficient eligible reviewers in selected group slots",
      "LEC021 excluded because lecturer is project supervisor",
      "LEC024 excluded because of declared conflict of interest"
    ],
    "suggestions": [
      "Open additional timeslots on 2026-08-27",
      "Invite additional eligible lecturers"
    ]
  },
  {
    "groupId": "G53",
    "reasons": [
      "Defense 1.2 reviewer continuity H11 cannot be satisfied"
    ],
    "suggestions": [
      "Ask previous Defense 1.1 reviewer for additional availability",
      "Manager may override H11 with mandatory reason"
    ]
  }
]
```

------------------------------------------------------------------------

# 16. Scheduling --- Sessions

## Session List

  Session   Group   Round         Date    Time    Room   Status
  --------- ------- ------------- ------- ------- ------ -----------
  SES001    G01     Defense 1.1   25/08   08:00   P201   SCHEDULED
  SES002    G02     Defense 1.1   25/08   08:00   P202   SCHEDULED
  SES003    G03     Defense 1.1   25/08   09:00   P201   SCHEDULED

Filters:

-   Semester.
-   Round.
-   Date.
-   Room.
-   Lecturer.
-   Group.
-   Status.

------------------------------------------------------------------------

# 17. Session Detail

``` json
{
  "id": "SES001",
  "scheduleVersionId": "SV-D11-003",
  "groupId": "G01",
  "roundId": "ER-D11-SU26",
  "timeslotId": "TS-2508-0800",
  "roomId": "ROOM-P201",
  "reviewers": ["LEC007", "LEC008", "LEC009"],
  "resultOwnerId": "LEC007",
  "status": "SCHEDULED"
}
```

Tabs/sections:

-   Group.
-   Project.
-   Date & Time.
-   Room.
-   Reviewers.
-   Result Owner.
-   Result.
-   Change History.

## Manager actions trước Publish

-   Change Timeslot.
-   Change Room.
-   Replace Reviewer.
-   Change Result Owner.

H1/H2/H3 vi phạm phải block. Các override được cho phép theo nghiệp vụ
phải yêu cầu reason và Audit Log.

------------------------------------------------------------------------

# 18. Publish Schedule

## Pre-publish summary

``` text
Defense 1.1 - SU26
Active Version: V3

Groups scheduled: 74/74
Hard violations: 0
Warnings: 2

[Publish Schedule]
```

Sau Publish:

-   Round → `PUBLISHED`.
-   Gửi notification tới Reviewers.
-   Gửi tới Supervisor.
-   Gửi tới Leader.
-   Gửi tới Students.
-   Không cho rerun scheduler toàn Round.
-   Thay đổi tiếp theo phải xử lý ở Session level.

------------------------------------------------------------------------

# 19. Operations --- Schedule Changes

## List

  ------------------------------------------------------------------------------
  Request     Session     Requested   Type               Reason      Status
                          By                                         
  ----------- ----------- ----------- ------------------ ----------- -----------
  CR001       SES001      G01 Leader  POSTPONE           Team        PENDING
                                                         emergency   

  CR002       SES015      LEC014      CHANGE_TIME        Schedule    APPROVED
                                                         conflict    

  CR003       SES021      Manager     REPLACE_REVIEWER   Lecturer    COMPLETED
                                                         absent      
  ------------------------------------------------------------------------------

## Actions

-   View.
-   Approve.
-   Reject.
-   Choose replacement timeslot/room/reviewer.
-   Require reason.
-   Record Audit Log.
-   Notify affected users.

------------------------------------------------------------------------

# 20. Incident --- Reviewer vắng

Có thể triển khai như một subtype của Schedule Change.

## Candidate replacement mock

``` json
{
  "sessionId": "SES001",
  "unavailableReviewerId": "LEC008",
  "candidates": [
    {
      "lecturerId": "LEC017",
      "eligible": true,
      "reasons": []
    },
    {
      "lecturerId": "LEC018",
      "eligible": false,
      "reasons": ["TIME_CONFLICT"]
    },
    {
      "lecturerId": "LEC001",
      "eligible": false,
      "reasons": ["PROJECT_SUPERVISOR"]
    },
    {
      "lecturerId": "LEC020",
      "eligible": false,
      "reasons": ["CONFLICT_OF_INTEREST"]
    }
  ]
}
```

Nếu không có candidate hợp lệ → postpone và xếp make-up slot.

------------------------------------------------------------------------

# 21. Operations --- Remediation

Chỉ phát sinh cho Group nhận `LEVEL_2` ở Defense 1.1.

## List mock

  Group   Defense 1.1 Result   Deadline   Verifier   Status
  ------- -------------------- ---------- ---------- ---------
  G01     LEVEL_2              30/08      LEC008     PENDING
  G07     LEVEL_2              29/08      LEC015     PASSED
  G12     LEVEL_2              27/08      LEC021     OVERDUE

## Detail mock

``` json
{
  "groupId": "G01",
  "sourceSessionId": "SES001",
  "conclusion": "LEVEL_2",
  "deadline": "2026-08-30T23:59:59+07:00",
  "verifierId": "LEC008",
  "status": "PENDING",
  "verifiedAt": null
}
```

## Flow

``` text
LEVEL_2
   ↓
D12_CONDITIONAL
   ↓
Verifier
├── PASS → ELIGIBLE_D12 → Defense 1.2
└── Deadline exceeded
       ↓
     OVERDUE
       ↓
Manager reviews
       ↓
Mark FAILED + mandatory reason
```

Quá hạn không tự động FAILED.

------------------------------------------------------------------------

# 22. Results --- Results

## Result List

  Group   Round         Result      Entered By   Entered At
  ------- ------------- ----------- ------------ -------------
  G01     Review 1      PASS        LEC007       15/06 10:30
  G01     Review 2      NEEDS_FIX   LEC008       15/07 11:05
  G01     Defense 1.1   LEVEL_2     LEC007       25/08 09:15
  G02     Defense 1.1   LEVEL_1     LEC011       25/08 09:20
  G05     Defense 1.1   LEVEL_3     LEC013       25/08 10:12

## Result models

### Review

``` json
{
  "sessionId": "SES-R1-G01",
  "type": "REVIEW",
  "result": "PASS",
  "note": "Requirements are sufficiently defined.",
  "enteredBy": "LEC007"
}
```

Allowed:

``` text
PASS
NEEDS_FIX
FAIL
```

Review result **không block** Group khỏi Defense 1.1.

### Defense 1.1

``` json
{
  "sessionId": "SES001",
  "type": "DEFENSE_1_1",
  "conclusion": "LEVEL_2",
  "note": "Product acceptable; documentation requires remediation.",
  "enteredBy": "LEC007",
  "remediationDeadline": "2026-08-30",
  "remediationVerifierId": "LEC008"
}
```

Allowed:

``` text
LEVEL_1
LEVEL_2
LEVEL_3
LEVEL_4
```

Manager có thể sửa result nhưng phải lưu old/new value, reason và audit.

------------------------------------------------------------------------

# 23. Results --- Group Progress

## Mục đích

Hiển thị Group đang ở đâu trong toàn bộ state machine.

## Mock --- G01

``` text
G01 — Smart Factory AI Monitoring

Review 1
PASS
  ↓
Review 2
NEEDS_FIX
  ↓
Defense 1.1
LEVEL_2
  ↓
D12_CONDITIONAL
  ↓
Remediation
PENDING
  ↓
Defense 1.2
WAITING
```

## Mock --- G05

``` text
G05

Review 1
PASS
  ↓
Review 2
PASS
  ↓
Defense 1.1
LEVEL_3
  ↓
PENDING_D2
  ↓
Defense 2
WAITING
```

## State transition

``` text
ACTIVE
  │
  ├─ Review 1 → result only, non-blocking
  ├─ Review 2 → result only, non-blocking
  │
  ▼
DEFENSE_1_1
  │
  ├─ LEVEL_1 → ELIGIBLE_D12 → DEFENSE_1_2 → COMPLETED
  │
  ├─ LEVEL_2 → D12_CONDITIONAL
  │               ├─ remediation PASS → ELIGIBLE_D12 → DEFENSE_1_2
  │               └─ overdue + Manager closes → FAILED
  │
  ├─ LEVEL_3 → PENDING_D2 → DEFENSE_2
  │                            ├─ PASS → COMPLETED
  │                            └─ FAIL → FAILED
  │
  └─ LEVEL_4 → FAILED
```

`FAILED` không được schedule vào round còn lại của kỳ và được tạo retake
record cho kỳ sau.

------------------------------------------------------------------------

# 24. Reports --- Lecturer Workload

## List mock

  --------------------------------------------------------------------------
  Lecturer       Sessions      Minutes     Semester        Usage Preferred
                                              Quota              Load
  ---------- ------------ ------------ ------------ ------------ -----------
  LEC001               18         1080           30          60% HIGH

  LEC002               19         1140           20          95% MEDIUM

  LEC003               10          600           30          33% HIGH

  LEC004               12          720           16          75% LOW
  --------------------------------------------------------------------------

Filters:

-   Semester.
-   Round.
-   Date.
-   Department.

Có thể hiển thị deviation để Manager phát hiện Lecturer đang quá tải
hoặc under-utilized.

------------------------------------------------------------------------

# 25. Reports --- Attention Groups

## Mock

  Group   Issue                 Severity   Suggested Action
  ------- --------------------- ---------- ---------------------------------
  G04     NO_LEADER             HIGH       Assign a new Leader
  G03     UNDER_4_MEMBERS       MEDIUM     Review approved dropout history
  G12     REMEDIATION_OVERDUE   HIGH       Review and close remediation
  G17     UNSCHEDULED           HIGH       Open scheduling diagnostics

Click từng row → đi thẳng tới màn hình xử lý tương ứng.

------------------------------------------------------------------------

# 26. Reports --- Reports

## Result Distribution mock

``` json
{
  "round": "DEFENSE_1_1",
  "total": 74,
  "distribution": {
    "LEVEL_1": 42,
    "LEVEL_2": 19,
    "LEVEL_3": 9,
    "LEVEL_4": 4
  }
}
```

Có thể breakdown theo Supervisor.

## Export Excel

Manager có action:

``` text
Export Current Round
Export Semester Schedule
Export Result Summary
```

File export cần khớp cấu trúc Excel nghiệp vụ hiện hành theo PRD.

------------------------------------------------------------------------

# 27. Notification Mock Data

  Event                              Recipients
  ---------------------------------- -----------------------------------------
  Lecturer invited                   Lecturer
  Availability deadline reminder     Lecturer chưa submit
  Schedule published                 Reviewers, Supervisor, Leader, Students
  Session changed                    Affected users
  Session upcoming                   Reviewers, Group
  Result entered                     Group, Supervisor
  Remediation deadline approaching   Group, Verifier, Supervisor
  Remediation overdue                Group, Verifier, Supervisor, Manager
  Group slot selection opened        Leader

Example:

``` json
{
  "id": "NOTI001",
  "type": "SCHEDULE_PUBLISHED",
  "title": "Defense 1.1 schedule published",
  "message": "Your Defense 1.1 session is scheduled for 25/08/2026 at 08:00 in room P201.",
  "recipientId": "ST001",
  "read": false
}
```

------------------------------------------------------------------------

# 28. Audit Log Mock Data

``` json
[
  {
    "id": "AUD001",
    "actorId": "MGR001",
    "action": "SESSION_ROOM_CHANGED",
    "entityType": "SESSION",
    "entityId": "SES001",
    "oldValue": {"roomId": "ROOM-P201"},
    "newValue": {"roomId": "ROOM-P202"},
    "reason": "P201 unavailable due to maintenance",
    "createdAt": "2026-08-24T15:30:00+07:00"
  },
  {
    "id": "AUD002",
    "actorId": "MGR001",
    "action": "REVIEWER_REPLACED",
    "entityType": "SESSION",
    "entityId": "SES001",
    "oldValue": {"lecturerId": "LEC008"},
    "newValue": {"lecturerId": "LEC017"},
    "reason": "Original reviewer reported emergency absence",
    "createdAt": "2026-08-25T07:15:00+07:00"
  }
]
```

------------------------------------------------------------------------

# 29. Core Mock Entities

## Lecturers

``` json
[
  {
    "id": "LEC001",
    "name": "Nguyễn Minh An",
    "email": "an.nm@fe.edu.vn",
    "department": "Software Engineering",
    "active": true
  },
  {
    "id": "LEC002",
    "name": "Lê Thanh Bình",
    "email": "binh.lt@fe.edu.vn",
    "department": "Software Engineering",
    "active": true
  },
  {
    "id": "LEC007",
    "name": "Vũ Quốc Khánh",
    "email": "khanh.vq@fe.edu.vn",
    "department": "Software Engineering",
    "active": true
  },
  {
    "id": "LEC008",
    "name": "Võ Minh Đức",
    "email": "duc.vm@fe.edu.vn",
    "department": "Software Engineering",
    "active": true
  }
]
```

## Rooms

``` json
[
  {
    "id": "ROOM-P201",
    "name": "P201",
    "campus": "HCM",
    "capacity": 30,
    "equipment": ["PROJECTOR", "TV"],
    "active": true
  },
  {
    "id": "ROOM-P202",
    "name": "P202",
    "campus": "HCM",
    "capacity": 30,
    "equipment": ["PROJECTOR"],
    "active": true
  },
  {
    "id": "ROOM-P203",
    "name": "P203",
    "campus": "HCM",
    "capacity": 40,
    "equipment": ["PROJECTOR", "TV", "SPEAKER"],
    "active": true
  }
]
```

## Conflict of Interest

``` json
[
  {
    "id": "COI001",
    "lecturerId": "LEC020",
    "projectId": "SU26SE001",
    "reason": "Declared research conflict"
  }
]
```

------------------------------------------------------------------------

# 30. Manager End-to-End Flow

``` text
1. Select/Create Semester
          ↓
2. Import/Create Projects
          ↓
3. Create Groups + Students
          ↓
4. Assign Main/Co Supervisors
          ↓
5. Assign Leaders / process dropout
          ↓
6. Create Evaluation Round
          ↓
7. Configure dates, duration, reviewer count, modes
          ↓
8. Generate Timeslots
          ↓
9. Invite Lecturers
          ↓
10. Collect Lecturer Availability
          ↓
11. Collect Group Availability (optional)
          ↓
12. Close Registration
          ↓
13. Run Scheduler
          ↓
14. Generate Schedule Versions V1/V2/V3...
          ↓
15. Compare + Set Active
          ↓
16. Manually adjust Sessions if necessary
          ↓
17. Publish
          ↓
18. Handle change requests / incidents
          ↓
19. Reviewer / Result Owner enters result
          ↓
20. Manager monitors Group Progress
          ↓
21. Handle remediation / overdue cases
          ↓
22. Defense 1.2 / Defense 2
          ↓
23. COMPLETED / FAILED
          ↓
24. Reports + Excel Export
```

------------------------------------------------------------------------

# 31. Suggested Frontend Route Structure

``` text
/manager
/manager/dashboard

/manager/semesters
/manager/semesters/:semesterId

/manager/projects
/manager/projects/:projectId

/manager/groups
/manager/groups/:groupId

/manager/rounds
/manager/rounds/:roundId
/manager/rounds/:roundId/timeslots
/manager/rounds/:roundId/invitations
/manager/rounds/:roundId/availability

/manager/schedules
/manager/schedules/:versionId
/manager/schedules/compare

/manager/sessions
/manager/sessions/:sessionId

/manager/operations/changes
/manager/operations/remediation

/manager/results/progress
/manager/results

/manager/reports/workload
/manager/reports/attention
/manager/reports
```

------------------------------------------------------------------------

# 32. Suggested Status Enums

``` ts
type RoundStatus =
  | "DRAFT"
  | "OPEN_REGISTRATION"
  | "REGISTRATION_CLOSED"
  | "SCHEDULING"
  | "SCHEDULED"
  | "PUBLISHED"
  | "ONGOING"
  | "COMPLETED"
  | "LOCKED";

type GroupProgressState =
  | "ACTIVE"
  | "D12_CONDITIONAL"
  | "ELIGIBLE_D12"
  | "PENDING_D2"
  | "COMPLETED"
  | "FAILED";

type ReviewResult =
  | "PASS"
  | "NEEDS_FIX"
  | "FAIL";

type DefenseConclusion =
  | "LEVEL_1"
  | "LEVEL_2"
  | "LEVEL_3"
  | "LEVEL_4";

type RemediationStatus =
  | "PENDING"
  | "PASSED"
  | "OVERDUE"
  | "FAILED";

type InvitationStatus =
  | "PENDING"
  | "ACCEPTED"
  | "REJECTED";
```

------------------------------------------------------------------------

# 33. Phân biệt các entity quan trọng

``` text
Semester
= một học kỳ.

Project
= đề tài Capstone.

Group
= nhóm sinh viên thực hiện Project.

EvaluationRound
= một đợt Review/Defense.

Timeslot
= khung thời gian có thể tổ chức Session.

ScheduleVersion
= một phương án xếp lịch toàn bộ Round.

Session
= một Group cụ thể + Timeslot + Room + Reviewers.

ReviewerAssignment
= Lecturer được phân vào Session.

ResultOwner
= Reviewer chịu trách nhiệm nhập kết quả cuối khi mode bật.

Remediation
= trạng thái khắc phục của Group nhận Level 2.

GroupProgress
= trạng thái quyết định Group được đi Round nào tiếp theo.
```

------------------------------------------------------------------------

# 34. Tóm tắt quyền Manager

Manager là người vận hành nghiệp vụ Capstone:

-   Quản lý Semester.
-   Quản lý Project/Group/Student.
-   Phân công Supervisor.
-   Quản lý Leader và dropout.
-   Tạo/configure Evaluation Round.
-   Mời Lecturer.
-   Theo dõi availability.
-   Quản lý semester workload quota.
-   Chạy scheduler.
-   Quản lý ScheduleVersion.
-   Chọn active version.
-   Sửa Session.
-   Publish Schedule.
-   Xử lý change request.
-   Xử lý incident và thay Reviewer.
-   Quản lý Result Owner.
-   Xem/sửa result có audit.
-   Theo dõi Group Progress.
-   Xử lý remediation quá hạn.
-   Xem workload/attention/result reports.
-   Export dữ liệu nghiệp vụ.

Admin vẫn giữ các quyền quản trị nền tảng như account/role, master
Lecturer/Room, audit toàn hệ thống và unlock dữ liệu đã LOCKED.
