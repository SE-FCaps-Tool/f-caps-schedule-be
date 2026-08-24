# Manual scheduling API contract

Mục tiêu FE: xếp lịch bằng tay theo `Timeslot x Ngày`; mỗi hội đồng có thể chấm nhiều nhóm nhưng luôn dùng một phòng duy nhất. Một timeslot có thể có nhiều hội đồng ở nhiều phòng khác nhau.
Luồng thuật toán / xem lịch sau thuật toán / gán phòng hàng loạt đang tạm ẩn khỏi UI.

## Reviewer roles

- Nếu `round.reviewerCount = 2`: dùng `REVIEWER_1` / `REVIEWER_2`, label `Review 1` / `Review 2`.
- Nếu `round.reviewerCount >= 3`: dùng `CHAIR`, `SECRETARY`, rồi `MEMBER_1...MEMBER_N`.

## Required endpoints

### `GET /api/v1/rounds/:roundId/manual-schedule`

Trả lịch nháp/đã publish hiện tại.

```json
{
  "data": {
    "roundId": "12",
    "reviewerCount": 3,
    "maxGroupsPerTimeslot": 2,
    "sessions": [
      {
        "id": "manual_session_1",
        "date": "2026-09-04",
        "roundTimeslotId": "slot_0700",
        "startTime": "07:00",
        "endTime": "07:45",
        "groups": [
          {
            "groupId": "grp_44",
            "groupCode": "GRP-SU26SE044",
            "leaderName": "Nguyen Van A",
            "activeMemberCount": 5,
            "supervisorIds": ["17"]
          },
          {
            "groupId": "grp_61",
            "groupCode": "GRP-SU26SE061",
            "leaderName": "Tran Van B",
            "activeMemberCount": 4,
            "supervisorIds": ["24"]
          }
        ],
        "room": {
          "roomId": 3,
          "roomCode": "B1-301",
          "roomName": "B1-301",
          "type": "NORMAL",
          "capacity": 30
        },
        "reviewers": [
          { "lecturerId": "11", "lecturerCode": "GV-AN-NDH", "lecturerName": "Nguyen Duc Huy", "role": "CHAIR", "roleLabel": "Chủ tịch", "order": 1 }
        ],
        "status": "DRAFT",
        "warnings": []
      }
    ]
  }
}
```

### `GET /api/v1/rounds/:roundId/manual-schedule/options`

Query:

```txt
date=2026-09-04
roundTimeslotId=slot_0700
reviewerIds=11&reviewerIds=22
groupIds=grp_44&groupIds=grp_61
```

BE nên trả options đã lọc theo timeslot:

- `lecturers`: chỉ giảng viên đã nhận lời và rảnh ở timeslot này, không trùng buổi khác.
- `groups`: chỉ nhóm đã chọn/đăng ký timeslot này, chưa được xếp buổi khác.
- Nếu `reviewerIds` có GVHD của nhóm thì không trả nhóm đó.
- Nếu `groupIds` đã chọn thì không trả lecturer là GVHD của bất kỳ nhóm nào trong hội đồng đó.
- `rooms`: phòng đúng loại `round.roomTypes`, đang active, chưa dùng ở cùng date/timeslot.

### `POST /api/v1/rounds/:roundId/manual-schedule/sessions`

Tạo một buổi chấm.

```json
{
  "date": "2026-09-04",
  "roundTimeslotId": "slot_0700",
  "groupIds": ["grp_44", "grp_61"],
  "roomId": 3,
  "reviewers": [
    { "lecturerId": "11", "role": "CHAIR", "roleLabel": "Chủ tịch", "order": 1 },
    { "lecturerId": "22", "role": "SECRETARY", "roleLabel": "Thư kí", "order": 2 },
    { "lecturerId": "33", "role": "MEMBER_1", "roleLabel": "Thành viên 1", "order": 3 }
  ]
}
```

### `PATCH /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId`

Update cùng payload với create.

### `DELETE /api/v1/rounds/:roundId/manual-schedule/sessions/:sessionId`

Xóa một buổi chấm khỏi lịch nháp.

### `POST /api/v1/rounds/:roundId/manual-schedule/validate`

Validate toàn lịch trước publish.

Ràng buộc BE cần chặn:

- Một group chỉ có một session/hội đồng trong round.
- Nếu `round.maxGroupsPerTimeslot` khác `null`, số hội đồng/phiên trong một date/timeslot không được vượt giá trị đó (theo H13).
- Nếu `round.maxGroupsPerTimeslot = null`, không áp dụng giới hạn số hội đồng trong một date/timeslot.
- GV không trùng hai session cùng date/timeslot.
- Room không trùng hai session cùng date/timeslot.
- Số reviewer đúng `round.reviewerCount`.
- Role đúng rule theo reviewer count.
- Group có GVHD nằm trong hội đồng thì invalid.
- Group/lecturer phải đăng ký/rảnh đúng timeslot nếu round yêu cầu chọn lịch.

### `POST /api/v1/rounds/:roundId/manual-schedule/publish`

Publish lịch thủ công sau khi validate pass. Sau publish, lịch đi theo luồng session hiện tại cho student/lecturer.
