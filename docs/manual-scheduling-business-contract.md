# Manual Scheduling — API, Constraints & Business Rules

> Contract đề xuất cho BE implement luồng **Xếp lịch** bằng tay.
> Nguồn quy tắc: tài liệu thuật toán xếp lịch hội đồng v1.0 ngày 19/08/2026 và UX hiện tại của FE.

## 1. Mục tiêu và mô hình dữ liệu

Manager xếp lịch trên bảng **Timeslot × Ngày**. Một ô timeslot có thể có nhiều hội đồng.

### 1.1. Một phiên/hội đồng

Một session gồm:

    1 round date
    1 round timeslot
    1 room
    1 council/reviewer set
    N groups

Quy tắc:

- Một hội đồng có thể chấm nhiều nhóm trong cùng một timeslot.
- Tất cả nhóm trong cùng hội đồng dùng chung một phòng.
- Không được tách cùng một hội đồng sang hai phòng khác nhau.
- Một timeslot có thể có nhiều hội đồng ở nhiều phòng khác nhau.
- Một nhóm chỉ được thuộc một session trong cùng một round.
- Hai session cùng timeslot không được dùng chung giảng viên hoặc phòng.

### 1.2. Lưu ý tên field H13

Field hiện có là **maxGroupsPerTimeslot** / **max_groups_per_timeslot**, nhưng H13 trong tài liệu thuật toán ghi là:

    Số phiên/hội đồng trong một khung <= max_groups_per_timeslot

Trong contract này, field đó được hiểu là **số hội đồng/phiên tối đa trong một timeslot**, không phải tổng số group nằm trong các hội đồng.

Nếu nghiệp vụ cần giới hạn số nhóm nằm trong một hội đồng, BE nên thêm field riêng:

    batch_size hoặc max_groups_per_council

maxGroupsPerTimeslot = null nghĩa là không áp dụng H13. Nó không có nghĩa là bỏ qua các ràng buộc khác.

## 2. Phân quyền và trạng thái

Tất cả endpoint dành cho MANAGER hoặc ADMIN, dùng cookie session và CSRF theo convention hiện tại.

### 2.1. Round được phép thao tác

Cho phép tạo/sửa/xóa draft khi round ở:

    DRAFT
    OPEN_REGISTRATION
    REGISTRATION_CLOSED
    SCHEDULING

Không cho sửa khi:

    PUBLISHED
    ONGOING
    COMPLETED
    LOCKED
    CANCELLED

Thay đổi sau publish phải đi qua controlled-change/version riêng, không mutate lịch đã công bố.

### 2.2. Trạng thái session

    DRAFT      Có thể thiếu group/phòng/reviewer, chỉ dùng để lưu nháp.
    READY      Đủ dữ liệu và pass các blocker.
    PUBLISHED  Đã nằm trong lịch được công bố.

DRAFT không được tính là lịch hợp lệ để publish.

## 3. API overview

### 3.1. Endpoint bắt buộc

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | /api/v1/rounds/:roundId/manual-schedule | Tải board, config, summary và session |
| GET | /api/v1/rounds/:roundId/manual-schedule/options | Tải group/GV/phòng đã lọc theo timeslot |
| POST | /api/v1/rounds/:roundId/manual-schedule/sessions | Tạo một hội đồng/session |
| PATCH | /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId | Sửa session |
| DELETE | /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId | Xóa session draft |
| POST | /api/v1/rounds/:roundId/manual-schedule/sessions/bulk-upsert | Lưu nhiều session một lần |
| POST | /api/v1/rounds/:roundId/manual-schedule/validate | Validate toàn bộ draft |
| POST | /api/v1/rounds/:roundId/manual-schedule/publish | Validate và công bố lịch |
| GET | /api/v1/rounds/:roundId/manual-schedule/publish-readiness | Checklist trước publish |

### 3.2. API dữ liệu nguồn

Nếu chưa gộp vào manual-schedule/options, BE cần đảm bảo các API sau trả đủ dữ liệu:

| Method | Endpoint | Dữ liệu |
|---|---|---|
| GET | /api/v1/rounds/:roundId | Config round, ngày và timeslot |
| GET | /api/v1/rounds/:roundId/invitations | GV được mời, status, quota |
| GET | /api/v1/rounds/:roundId/availability | Lịch rảnh GV và preference group |
| GET | /api/v1/rounds/:roundId/groups | Group đủ điều kiện, GVHD, project status |
| GET | /api/v1/rooms | Phòng active, loại phòng, sức chứa |

FE chỉ dùng các API nguồn để hiển thị UX. options, validate và publish phải tự kiểm tra lại ở BE.

## 4. GET manual schedule

    GET /api/v1/rounds/:roundId/manual-schedule

Response tối thiểu:

    {
      "data": {
        "roundId": "12",
        "roundStatus": "SCHEDULING",
        "reviewerCount": 3,
        "maxGroupsPerTimeslot": null,
        "roles": [
          { "key": "CHAIR", "label": "Chủ tịch", "order": 1 },
          { "key": "SECRETARY", "label": "Thư kí", "order": 2 },
          { "key": "MEMBER_1", "label": "Thành viên 1", "order": 3 }
        ],
        "config": {
          "roomTypes": ["NORMAL", "SEMINAR"],
          "batchSize": null,
          "chairMinLevel": 2,
          "secretaryMinLevel": 2,
          "maxSameSupervisorRatio": 0.5,
          "eligibleProjectStatuses": ["APPROVED"]
        },
        "summary": {
          "eligibleGroupCount": 45,
          "scheduledGroupCount": 12,
          "unscheduledGroupCount": 33,
          "sessionCount": 6,
          "incompleteSessionCount": 1,
          "blockerCount": 0,
          "warningCount": 2
        },
        "sessions": [
          {
            "id": "manual_session_1",
            "date": "2026-09-04",
            "roundTimeslotId": "slot_0700",
            "startTime": "07:00",
            "endTime": "07:45",
            "status": "DRAFT",
            "groups": [
              {
                "groupId": "grp_44",
                "groupCode": "GRP-SU26SE044",
                "leaderName": "Nguyen Van A",
                "activeMemberCount": 5,
                "supervisorIds": ["17"]
              }
            ],
            "room": {
              "roomId": 3,
              "roomCode": "B1-301",
              "roomName": "B1-301",
              "type": "NORMAL",
              "capacity": 30
            },
            "reviewers": [],
            "blockers": [],
            "warnings": []
          }
        ]
      }
    }

roles, config và summary nên trả trong response để FE không phải tự suy luận rule từ loại round.

## 4.1. Ranh giới trách nhiệm FE và BE

FE không phải nguồn quyết định điều kiện xếp lịch. Các filter đang có ở UI chỉ phục vụ
trải nghiệm chọn nhanh và hiển thị trạng thái tạm thời, ví dụ:

- tìm kiếm theo mã/tên;
- giữ lại item đang được chọn khi edit;
- tránh chọn trùng GV ở hai role trong cùng một draft session;
- ẩn tạm group đã nằm ở session khác trong local draft;
- hiển thị loading, blocked reason và cảnh báo từ API.

FE không được tự kết luận một GV đủ điều kiện làm **Chủ tịch**, **Thư kí** hoặc
**Thành viên** chỉ dựa trên `reviewerCount`, trạng thái invitation, availability hoặc
dữ liệu đã tải từ các API nguồn. Những dữ liệu đó có thể stale và chưa bao gồm toàn bộ
COI, GVHD, lịch round trước, skill, quota và các session khác.

BE là nguồn sự thật cho candidate list và validation:

1. `GET /manual-schedule/options` phải nhận context hiện tại gồm `date`,
   `roundTimeslotId`, `sessionId`, `role`, `reviewerIds`, `groupIds` và `roomId`.
2. API phải trả từng option cùng `available`, `blockedCodes` và `blockedReason`.
   Với lecturer, response nên trả thêm `eligibleRoles` để FE biết GV được xét cho
   role nào ở context đó.
3. `POST/PATCH` session, `bulk-upsert`, `validate` và `publish` đều phải chạy lại
   H1-H16 ở BE. Không được tin kết quả filter hoặc validation trước đó của FE.
4. Nếu options API chưa sẵn sàng, FE có thể dùng filter local làm fallback hiển thị,
   nhưng phải xem kết quả là **unknown/temporary**, không cho publish dựa trên kết quả
   đó và không được thay thế validation ở BE.

### Context tối thiểu khi tải danh sách giảng viên

Ví dụ khi chọn Chủ tịch:

    GET /api/v1/rounds/:roundId/manual-schedule/options
      ?date=2026-09-04
      &roundTimeslotId=slot_0700
      &sessionId=manual_session_1
      &role=CHAIR
      &groupIds=grp_44&groupIds=grp_61
      &reviewerIds=11&reviewerIds=22

BE phải lọc và trả kết quả theo đúng context này, bao gồm invitation, availability,
GVHD conflict, COI, double-booking, load/quota, skill của role và các rule của round.
`reviewerCount` chỉ dùng để derive role schema; nó không chứng minh một lecturer đủ
điều kiện làm role đó.

## 5. GET options

    GET /api/v1/rounds/:roundId/manual-schedule/options

Query hỗ trợ:

    date=2026-09-04
    roundTimeslotId=slot_0700
    sessionId=manual_session_1
    reviewerIds=11&reviewerIds=22
    groupIds=grp_44&groupIds=grp_61
    roomId=3
    search=GV-AN
    page=1
    pageSize=50

sessionId dùng khi edit để option đang chọn không tự loại chính nó.

Mỗi option nên có:

    {
      "available": true,
      "blockedReason": null,
      "blockedCodes": []
    }

Lecturer thêm eligibleRoles. Group thêm supervisorIds và selectedByGroup. Room thêm type và capacity.

Options phải lọc theo:

- Group đúng project status của round.
- Group đã chọn timeslot hoặc được phép xếp tay theo policy round.
- Group chưa nằm trong session khác của round.
- Group không bị loại bởi GVHD đã chọn trong hội đồng.
- Lecturer có invitation ACCEPTED.
- Lecturer đã đăng ký rảnh ở timeslot.
- Lecturer không bị COI với group/project đang chọn.
- Lecturer không nằm trong session khác cùng timeslot.
- Lecturer đạt skill của role nếu round đã cấu hình ngưỡng skill.
- Room active, đúng roomTypes của round, chưa dùng trong session khác cùng timeslot.

Options chỉ là hỗ trợ chọn. BE vẫn phải validate lại khi ghi dữ liệu.

## 6. Create/update/delete session

### Tạo

    POST /api/v1/rounds/:roundId/manual-schedule/sessions

### Sửa

    PATCH /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId

Request cho phép lưu nháp thiếu dữ liệu:

    {
      "date": "2026-09-04",
      "roundTimeslotId": "slot_0700",
      "groupIds": ["grp_44", "grp_61"],
      "roomId": 3,
      "reviewers": [
        { "lecturerId": "11", "role": "CHAIR", "order": 1 },
        { "lecturerId": "22", "role": "SECRETARY", "order": 2 },
        { "lecturerId": "33", "role": "MEMBER_1", "order": 3 }
      ],
      "clientRevision": 4
    }

Ở trạng thái DRAFT, roomId và reviewer có thể null/thiếu. BE tự tính roleLabel, order và snapshot code/name; không tin roleLabel từ FE.

### Xóa

    DELETE /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId

Chỉ xóa session draft hoặc round chưa publish. Xóa phải giải phóng group, room và reviewer khỏi conflict index.

## 7. Bulk upsert

    POST /api/v1/rounds/:roundId/manual-schedule/sessions/bulk-upsert

Request:

    {
      "clientRevision": 4,
      "sessions": [
        {
          "id": null,
          "date": "2026-09-04",
          "roundTimeslotId": "slot_0700",
          "groupIds": ["grp_44", "grp_61"],
          "roomId": 3,
          "reviewers": []
        }
      ],
      "deletedSessionIds": []
    }

Bulk upsert phải atomic. Nếu có blocker thì không ghi một phần, trừ khi request gửi allowDraftIncomplete=true và tất cả row chỉ là draft.

## 8. Validate toàn bộ draft

    POST /api/v1/rounds/:roundId/manual-schedule/validate

Request gửi toàn bộ sessions hiện tại và clientRevision. Response cần có:

    {
      "data": {
        "valid": false,
        "revision": 5,
        "blockers": [
          {
            "code": "LECTURER_DOUBLE_BOOKED",
            "message": "GV-AN-NDH đã có một phiên khác trong timeslot này.",
            "sessionId": "manual_session_1",
            "field": "reviewers[0].lecturerId",
            "relatedSessionIds": ["manual_session_2"]
          }
        ],
        "warnings": [
          {
            "code": "LOAD_IMBALANCE",
            "message": "Tải của GV-AN-NDH cao hơn trung bình 1.5 lần.",
            "sessionId": "manual_session_1",
            "field": null
          }
        ],
        "summary": {
          "eligibleGroupCount": 45,
          "scheduledGroupCount": 12,
          "unscheduledGroupIds": ["grp_70"],
          "incompleteSessionIds": []
        }
      }
    }

## 9. Publish

    POST /api/v1/rounds/:roundId/manual-schedule/publish

Request:

    {
      "clientRevision": 5,
      "confirmWarnings": ["LOAD_IMBALANCE"],
      "reason": "Đã trao đổi với trưởng bộ môn về phân bổ tải."
    }

Publish phải validate trong cùng transaction, không được tin kết quả validate cũ.

Publish chỉ thành công khi:

- Không còn blocker.
- Không còn session thiếu group, room hoặc reviewer.
- Không còn group bắt buộc bị unscheduled.
- Client revision chưa stale.
- Round vẫn ở trạng thái cho phép publish.
- Tất cả session được chuyển sang version/lịch chính thức trong cùng transaction.

Sau publish trả versionId, publishedAt, publishedBy và summary.

## 10. Quy tắc hội đồng và reviewer

### H5 — role theo reviewer count

| Reviewer count | Roles |
|---:|---|
| 2 | REVIEWER_1, REVIEWER_2 |
| 3 | CHAIR, SECRETARY, MEMBER_1 |
| 5 | CHAIR, SECRETARY, MEMBER_1, MEMBER_2, MEMBER_3 |

Không cho FE tự thay đổi reviewerCount hoặc role structure của round.

Một session READY phải:

- Có số reviewer đúng round.reviewerCount.
- Có role đúng cấu trúc round.
- Một lecturer chỉ có một role.
- Hai role không trỏ tới cùng lecturer.
- Có đúng một roomId.
- Tất cả group dùng chung room và reviewer set.

## 11. Hard constraints — phải chặn

| Code | Rule | Cách validate |
|---|---|---|
| H1_SUPERVISOR_CANNOT_REVIEW | GVHD không chấm group mình hướng dẫn | So sánh toàn bộ supervisor của group với reviewer IDs |
| H2_LECTURER_OVERLAP | GV không ở hai phiên trùng thời gian | Check overlap theo start/end |
| H3_ROOM_OVERLAP | Phòng không ở hai phiên trùng thời gian | Check room + time overlap |
| H4_GROUP_DUPLICATED | Group chỉ có một session trong round | Unique group ID trên toàn draft |
| H5_ROLE_STRUCTURE_INVALID | Role sai cấu trúc round | Server derive role schema |
| H6_LECTURER_MULTI_ROLE | Một GV chỉ một vai trong hội đồng | Unique lecturer ID trong session |
| H7_LECTURER_NOT_AVAILABLE | GV phải rảnh ở slot | Check lecturer availability |
| H8_CONFLICT_OF_INTEREST | Không xếp GV có COI | Check COI với project/group |
| H9_PROJECT_STATUS_INVALID | Project status đúng loại round | Check eligible statuses |
| H10_GROUP_SLOT_NOT_SELECTED | Tôn trọng slot group đã chọn | Check group preference |
| H11_PREVIOUS_REVIEWER_MISSING | D1.2 giữ reviewer của D1.1 cùng group | Check lịch round trước |
| H12_LECTURER_LOAD_EXCEEDED | Không vượt 240 phút/buổi, 480 phút/ngày, quota kỳ | Tính trên toàn lịch của GV |
| H13_SESSION_LIMIT | Số hội đồng/phiên trong slot không vượt max | Count session theo date + timeslot; null thì bỏ qua |
| H14_ROLE_SKILL_MISSING | CT/TK đạt skill threshold | Chair: FACILITATION; Secretary: SECRETARY |
| H15_SUPERVISOR_RATIO_EXCEEDED | Tỉ lệ cùng GVHD trong batch không vượt config | Check từng council batch |
| H16_DEFENSE_ROLE_INVALID | Defense có đúng một CT và một TK khác nhau | Check role set sau khi derive schema |

### H13 clarification

Một session có thể có nhiều groupIds, nhưng H13 chỉ đếm số session/hội đồng trong ô timeslot. Nếu muốn giới hạn số group trong một hội đồng, dùng batchSize riêng.

## 12. Soft constraints — cảnh báo/điểm

| Code | Rule |
|---|---|
| S1_LOAD_BALANCE | Cân bằng tải theo quota kỳ và preference load |
| S2_SKILL_FIT | Tối đa hóa CouncilFit theo project type và skill matrix |
| S3_PROJECT_TYPE_GROUPING | Ưu tiên group cùng ProjectType trong cùng hội đồng/buổi |
| S4_REVIEW2_PAIR_REUSE | Review 2 ưu tiên giữ cặp GV Review 1 |
| S5_PREVIOUS_REVIEWER_REUSE | D1.2 ưu tiên thêm reviewer từ D1.1 |
| S6_CONSECUTIVE_LECTURER_SESSIONS | Ưu tiên phiên liên tiếp trong cùng buổi |
| S7_FEWER_LECTURER_DAYS | Giảm số ngày GV phải đến trường |
| S8_SUPERVISOR_DIVERSITY | Đa dạng GVHD vượt mức H15 |
| S9_COUNCIL_STABILITY | Giữ tổ hợp hội đồng ổn định giữa các phiên liên tiếp |

S1 và S2 có thể xung đột. Validate nên trả cả load score và skill-fit score để Manager thấy lý do cảnh báo.

## 13. Quy tắc riêng cho xếp tay

### Group không hiển thị đề tài

FE không cần hiển thị project/topic. BE vẫn phải dùng quan hệ:

    group -> project -> supervisor(s)
    group -> project.status
    group -> previous round sessions/reviewers

Nếu reviewer là GVHD của bất kỳ group nào trong session, group đó không được chọn vào session.

### Nhiều group trong một hội đồng

- Có thể chọn hàng loạt group vào cùng một session.
- Tất cả group dùng chung room và reviewer set.
- Nếu có batchSize, không cho vượt batch size; trả BATCH_SIZE_EXCEEDED.
- Nếu không có batchSize, không tự đặt fallback là 1.
- maxGroupsPerTimeslot = null chỉ bỏ H13, không bỏ H1–H12 và H14–H16.

### Nhiều hội đồng trong một timeslot

- Được phép nếu H13 không bị vi phạm hoặc H13 là null.
- Mỗi hội đồng phải có một room riêng.
- Không dùng chung room trong hai session overlap.
- Không dùng chung lecturer trong hai session overlap.

### Phòng

- Room phải active và đúng loại round cho phép.
- roomId là singular trong một session.
- Nếu capacity là hard rule, thêm blocker ROOM_CAPACITY_INSUFFICIENT.
- Nếu chưa chốt capacity là hard rule, chỉ trả warning ROOM_CAPACITY_LOW.

### Draft incomplete

- Draft thiếu dữ liệu hiển thị blocker tương ứng.
- Không publish draft thiếu dữ liệu.
- Không nên giữ draft rỗng vô thời hạn; có thể cleanup theo TTL hoặc endpoint cleanup riêng.

## 14. Error codes

Dùng error envelope chuẩn của project:

    {
      "error": {
        "code": "GROUP_DUPLICATED",
        "message": "Group đã được xếp trong một session khác.",
        "details": {
          "groupId": "grp_44",
          "relatedSessionId": "manual_session_2"
        },
        "requestId": "req_abc123"
      }
    }

Codes tối thiểu:

    ROUND_NOT_FOUND
    ROUND_SCHEDULING_LOCKED
    ROUND_STATUS_INVALID
    STALE_MANUAL_SCHEDULE_REVISION
    TIMESLOT_NOT_IN_ROUND
    GROUP_NOT_ELIGIBLE
    GROUP_SLOT_NOT_SELECTED
    GROUP_DUPLICATED
    SUPERVISOR_REVIEW_CONFLICT
    LECTURER_NOT_ACCEPTED
    LECTURER_NOT_AVAILABLE
    LECTURER_DOUBLE_BOOKED
    LECTURER_CONFLICT_OF_INTEREST
    LECTURER_LOAD_EXCEEDED
    ROLE_STRUCTURE_INVALID
    LECTURER_MULTI_ROLE
    REVIEWER_SKILL_INSUFFICIENT
    PREVIOUS_REVIEWER_REQUIRED
    ROOM_NOT_FOUND
    ROOM_NOT_ACTIVE
    ROOM_TYPE_NOT_ALLOWED
    ROOM_DOUBLE_BOOKED
    ROOM_CAPACITY_INSUFFICIENT
    SESSION_LIMIT_EXCEEDED
    BATCH_SIZE_EXCEEDED
    UNSCHEDULED_GROUPS
    SESSION_INCOMPLETE
    PUBLISH_BLOCKED

## 15. Concurrency, audit và transaction

- Mỗi draft round có revision tăng sau create/update/delete/bulk-upsert.
- FE gửi clientRevision; mismatch trả 409 STALE_MANUAL_SCHEDULE_REVISION.
- Publish lock round/draft revision và validate lại trong cùng transaction.
- Lưu createdBy, updatedBy, createdAt, updatedAt cho session.
- Audit tối thiểu: tạo, sửa group, sửa room, thêm/xóa reviewer, xóa session, validate, publish.
- Không mutate lịch đã publish; thay đổi sau publish tạo controlled-change/version mới.

## 16. Publish readiness

    GET /api/v1/rounds/:roundId/manual-schedule/publish-readiness

Response:

    {
      "data": {
        "ready": false,
        "checks": [
          { "code": "ALL_GROUPS_SCHEDULED", "passed": false, "count": 33 },
          { "code": "ALL_SESSIONS_HAVE_ROOM", "passed": true, "count": 6 },
          { "code": "ALL_SESSIONS_HAVE_REVIEWERS", "passed": false, "count": 1 },
          { "code": "HARD_CONSTRAINTS", "passed": true, "count": 0 },
          { "code": "WARNINGS_CONFIRMED", "passed": true, "count": 0 }
        ],
        "blockers": [],
        "warnings": []
      }
    }

Endpoint này chỉ để hiển thị. POST publish vẫn phải validate độc lập.

## 17. FE handoff checklist

- [ ] Một session chứa nhiều group.
- [ ] Một session chỉ có một room.
- [ ] Một group không xuất hiện ở hai session.
- [ ] Một timeslot có thể có nhiều hội đồng/phòng.
- [ ] Options lọc theo timeslot, availability và supervisor conflict.
- [ ] Hỗ trợ chọn hàng loạt group.
- [ ] Hiển thị blocker/warning tại đúng field.
- [ ] Gửi clientRevision khi bật optimistic locking.
- [ ] Trả maxGroupsPerTimeslot = null nếu không giới hạn H13.
- [ ] Không fallback max null về 1.
- [ ] Validate lại H1–H16 tại create/update/validate/publish.
- [ ] Phân biệt blocker và warning; soft constraint không tự chặn nếu Manager đã confirm.
