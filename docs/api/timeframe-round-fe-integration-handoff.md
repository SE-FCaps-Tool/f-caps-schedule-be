# FE Handoff — Timeframe, Round và lịch chính thức

Ngày cập nhật: 2026-08-21

Tài liệu này mô tả phần tích hợp mới giữa Timeframe global, Round và flow chạy
scheduler. Tài liệu CRUD/preview chi tiết vẫn nằm ở
docs/api/timeframe-fe-handoff.md.

## 1. Ý nghĩa thay đổi

Timeframe là cấu hình dùng chung của hệ thống. Khi Manager tạo Round và chọn
timeframeId, Backend sẽ lấy revision ACTIVE hiện tại, ghim revision đó vào Round
và sinh các timeslot thực tế cho từng ngày của Round.

Luồng chính:

    Quản lý Timeframe
    → Preview/chỉnh timeline
    → Lưu Timeframe và revision
    → Tạo Round bằng timeframeId + startDate + endDate
    → Backend ghim timeframeVersionId và sinh round_days/timeslots
    → Đăng ký availability/preference
    → Run scheduler
    → Activate schedule version
    → Gán phòng
    → Publish
    → FE đọc lịch chính thức

Timeframe là template. Round sở hữu timeslot thực tế. ScheduleVersion/session sau
khi publish mới là nguồn của lịch chính thức cho Lecturer và Student.

### 1.1 Các khái niệm cần phân biệt

| Khái niệm | Ý nghĩa | Nơi dùng |
|---|---|---|
| Timeframe | Cấu hình thời gian dùng chung | Cấu hình dùng chung |
| Revision/version | Snapshot của Timeframe tại một thời điểm | Round lưu version đã ghim |
| Block/timeline | Một khung lớn, ví dụ 07:00–09:15 | Preview và timeline editor |
| groupSlot | Khoảng thời gian của một nhóm trong block | Backend chuyển thành Round timeslot |
| Round timeslot | Slot thật gắn với ngày cụ thể | Availability, preference, scheduler |
| groupsPerSlot | Số groupSlot nối tiếp trong một timeline manual | Cấu hình Timeframe |
| maxGroupsPerTimeslot | Số nhóm chạy đồng thời tại một Round timeslot | Tham số scheduler |

groupsPerSlot không thay thế maxGroupsPerTimeslot.

## 2. Authentication và timezone

Base URL local:

~~~text
http://localhost:8000/api/v1
~~~

FE production dùng cookie session:

~~~ts
credentials: "include"
~~~

Các request POST, PUT, PATCH, DELETE phải gửi CSRF token lấy từ cookie
scheduler_csrf:

~~~ts
headers: {
  "Content-Type": "application/json",
  "X-CSRF-Token": csrfToken,
  "Accept": "application/json"
}
~~~

Không dùng Bearer token. X-Test-Session chỉ dành cho test environment.

Giờ trong Timeframe là giờ local dạng HH:mm hoặc HH:mm:ss, không kèm Z hoặc
UTC offset. Khi Backend tạo timeslot, giờ được hiểu theo timezone
Asia/Ho_Chi_Minh. Datetime response là ISO-8601; FE parse bằng new Date().

## 3. API map

### 3.1 Timeframe

| Method | Endpoint | Chức năng |
|---|---|---|
| POST | /timeframes/preview | Preview tạo nhanh, không ghi DB |
| POST | /timeframes/manual/preview | Preview sau khi sửa timeline |
| POST | /timeframes | Tạo Timeframe nhanh |
| POST | /timeframes/manual | Tạo Timeframe manual |
| GET | /timeframes | List Timeframe chưa archive |
| GET | /timeframes?includeArchived=true | List gồm archived |
| GET | /timeframes/{timeframeId} | Detail, blocks và revisions |
| PATCH | /timeframes/{timeframeId} | Full replacement quick |
| PATCH | /timeframes/{timeframeId}/manual | Full replacement manual |
| DELETE | /timeframes/{timeframeId} | Archive mềm |

### 3.2 Round và scheduler

| Method | Endpoint | Chức năng |
|---|---|---|
| POST | /semesters/{semesterId}/rounds | Tạo Round contract camelCase |
| POST | /rounds | Tạo Round legacy, vẫn nhận timeframeId |
| GET | /rounds/{roundId} | Round detail và timeslot đã materialize |
| PATCH | /rounds/{roundId} | Sửa cấu hình Round/Timeframe |
| GET | /rounds/{roundId}/resources | Kiểm tra group/timeslot/room |
| POST | /rounds/{roundId}/invitations | Manager mời Lecturer |
| GET | /lecturer/me/invitations | Lecturer xem invitation |
| POST | /rounds/{roundId}/invitations/me/respond | Lecturer accept/decline |
| GET | /rounds/{roundId}/availability/me | Lecturer đọc availability |
| PUT | /rounds/{roundId}/availability/me | Lecturer gửi availability |
| GET | /rounds/{roundId}/groups/{groupId}/preferences | Leader đọc preference |
| PUT | /rounds/{roundId}/groups/{groupId}/preferences | Leader gửi preference |
| POST | /rounds/{roundId}/schedule/run | Chạy scheduler |
| POST | /schedule/versions/{versionId}/activate | Activate version |
| POST | /rounds/{roundId}/schedules/generate | Chạy scheduler target, trả envelope camelCase |
| POST | /rounds/{roundId}/schedules/{scheduleId}/actions/set-active | Activate target schedule |
| GET | /rounds/{roundId}/schedules | List ScheduleVersion |
| GET | /rounds/{roundId}/schedules/{scheduleId} | Detail ScheduleVersion |
| GET | /rounds/{roundId}/sessions?versionId={scheduleId} | Sessions theo version |
| GET | /rounds/{roundId}/publish-readiness | Kiểm tra publish |
| POST | /rounds/{roundId}/rooms/suggest | Gợi ý phòng |
| POST | /rounds/{roundId}/rooms/apply-suggestions | Áp dụng phòng |
| POST | /rounds/{roundId}/actions/publish | Publish target contract |
| POST | /rounds/{roundId}/schedule/publish/{versionId} | Publish legacy contract |

## 4. TypeScript types

~~~ts
export type TimeframeBreakWindow = {
  name: string;
  startTime: string;
  endTime: string;
};

export type ManualTimeline = {
  startTime: string;
  endTime: string;
  groupsPerSlot: number;
};

export type QuickTimeframeMutationRequest = {
  name: string;
  type: string;
  startTime: string;
  endTime: string;
  blockDurationMinutes: number;
  groupDurationMinutes: number;
  breakBetweenBlocksMinutes?: number;
  breakWindows?: TimeframeBreakWindow[];
  reason?: string | null;
};

export type ManualTimeframeMutationRequest = {
  name: string;
  type: string;
  groupDurationMinutes: number;
  timelines: ManualTimeline[];
  reason?: string | null;
};

export type TimeframeGroupSlot = {
  sequenceNumber: number;
  startTime: string;
  endTime: string;
};

export type TimeframeBlock = {
  sequenceNumber: number;
  startTime: string;
  endTime: string;
  durationMinutes: number;
  groupsPerBlock: number;
  groupDurationMinutes: number;
  groupSlots: TimeframeGroupSlot[];
};

export type TimeframeCalculation = {
  startTime: string;
  endTime: string;
  blockDurationMinutes: number | null;
  groupDurationMinutes: number;
  breakBetweenBlocksMinutes: number | null;
  manualTimelines: ManualTimeline[] | null;
  breakWindows: TimeframeBreakWindow[];
  blocksPerDay: number;
  groupsPerBlock: number | null;
  capacityPerDay: number;
  unusedMinutes: number;
  breakWindowMinutes: number;
  appliedBlockBreakMinutes: number;
  totalBreakMinutes: number;
  blocks: TimeframeBlock[];
};
~~~

## 5. Timeframe request/response

### 5.1 Quick preview

~~~http
POST /api/v1/timeframes/preview
Content-Type: application/json
~~~

Request:

~~~json
{
  "startTime": "07:00:00",
  "endTime": "17:30:00",
  "blockDurationMinutes": 135,
  "groupDurationMinutes": 45,
  "breakBetweenBlocksMinutes": 15,
  "breakWindows": [
    {
      "name": "Nghỉ trưa",
      "startTime": "11:45:00",
      "endTime": "13:00:00"
    }
  ]
}
~~~

Response 200:

~~~json
{
  "data": {
    "startTime": "07:00:00",
    "endTime": "17:30:00",
    "blockDurationMinutes": 135,
    "groupDurationMinutes": 45,
    "breakBetweenBlocksMinutes": 15,
    "manualTimelines": null,
    "breakWindows": [
      {
        "name": "Nghỉ trưa",
        "startTime": "11:45:00",
        "endTime": "13:00:00"
      }
    ],
    "blocksPerDay": 3,
    "groupsPerBlock": 3,
    "capacityPerDay": 9,
    "unusedMinutes": 135,
    "breakWindowMinutes": 75,
    "appliedBlockBreakMinutes": 15,
    "totalBreakMinutes": 90,
    "blocks": [
      {
        "sequenceNumber": 1,
        "startTime": "07:00:00",
        "endTime": "09:15:00",
        "durationMinutes": 135,
        "groupsPerBlock": 3,
        "groupDurationMinutes": 45,
        "groupSlots": [
          {
            "sequenceNumber": 1,
            "startTime": "07:00:00",
            "endTime": "07:45:00"
          },
          {
            "sequenceNumber": 2,
            "startTime": "07:45:00",
            "endTime": "08:30:00"
          },
          {
            "sequenceNumber": 3,
            "startTime": "08:30:00",
            "endTime": "09:15:00"
          }
        ]
      }
    ]
  }
}
~~~

Response thật trả đầy đủ blocks. FE không tự tính lại summary; chỉ render
response.

### 5.2 Manual preview

~~~http
POST /api/v1/timeframes/manual/preview
Content-Type: application/json
~~~

Request:

~~~json
{
  "groupDurationMinutes": 45,
  "timelines": [
    {
      "startTime": "07:30:00",
      "endTime": "09:00:00",
      "groupsPerSlot": 2
    },
    {
      "startTime": "09:15:00",
      "endTime": "11:30:00",
      "groupsPerSlot": 3
    },
    {
      "startTime": "13:00:00",
      "endTime": "14:30:00",
      "groupsPerSlot": 2
    }
  ]
}
~~~

Response 200:

~~~json
{
  "data": {
    "startTime": "07:30:00",
    "endTime": "14:30:00",
    "blockDurationMinutes": null,
    "groupDurationMinutes": 45,
    "breakBetweenBlocksMinutes": null,
    "manualTimelines": [
      {
        "startTime": "07:30:00",
        "endTime": "09:00:00",
        "groupsPerSlot": 2
      },
      {
        "startTime": "09:15:00",
        "endTime": "11:30:00",
        "groupsPerSlot": 3
      },
      {
        "startTime": "13:00:00",
        "endTime": "14:30:00",
        "groupsPerSlot": 2
      }
    ],
    "breakWindows": [
      {
        "name": "Khoảng nghỉ 1",
        "startTime": "09:00:00",
        "endTime": "09:15:00"
      },
      {
        "name": "Khoảng nghỉ 2",
        "startTime": "11:30:00",
        "endTime": "13:00:00"
      }
    ],
    "blocksPerDay": 3,
    "groupsPerBlock": null,
    "capacityPerDay": 7,
    "unusedMinutes": 0,
    "breakWindowMinutes": 105,
    "appliedBlockBreakMinutes": 0,
    "totalBreakMinutes": 105,
    "blocks": [
      {
        "sequenceNumber": 1,
        "startTime": "07:30:00",
        "endTime": "09:00:00",
        "durationMinutes": 90,
        "groupsPerBlock": 2,
        "groupDurationMinutes": 45,
        "groupSlots": [
          {
            "sequenceNumber": 1,
            "startTime": "07:30:00",
            "endTime": "08:15:00"
          },
          {
            "sequenceNumber": 2,
            "startTime": "08:15:00",
            "endTime": "09:00:00"
          }
        ]
      }
    ]
  }
}
~~~

Trong manual mode, các timeline có thể khác độ dài hoặc số nhóm nên summary chung
có thể là null.

### 5.3 Create quick/manual

Quick:

~~~http
POST /api/v1/timeframes
~~~

~~~json
{
  "name": "Hội đồng chuẩn",
  "type": "COUNCIL",
  "startTime": "07:00:00",
  "endTime": "17:30:00",
  "blockDurationMinutes": 135,
  "groupDurationMinutes": 45,
  "breakBetweenBlocksMinutes": 15,
  "breakWindows": [
    {
      "name": "Nghỉ trưa",
      "startTime": "11:45:00",
      "endTime": "13:00:00"
    }
  ],
  "reason": "Cấu hình chuẩn"
}
~~~

Manual:

~~~http
POST /api/v1/timeframes/manual
~~~

~~~json
{
  "name": "Hội đồng tùy chỉnh",
  "type": "COUNCIL",
  "groupDurationMinutes": 45,
  "timelines": [
    {
      "startTime": "07:30:00",
      "endTime": "09:00:00",
      "groupsPerSlot": 2
    },
    {
      "startTime": "09:15:00",
      "endTime": "11:30:00",
      "groupsPerSlot": 3
    },
    {
      "startTime": "13:00:00",
      "endTime": "14:30:00",
      "groupsPerSlot": 2
    }
  ],
  "reason": "Cấu hình theo timeline thực tế"
}
~~~

Response create 201 và update 200 dùng chung shape:

~~~json
{
  "data": {
    "id": 12,
    "name": "Hội đồng tùy chỉnh",
    "type": "COUNCIL",
    "archivedAt": null,
    "createdAt": "2026-08-21T08:00:00Z",
    "updatedAt": "2026-08-21T08:00:00Z",
    "version": {
      "id": 21,
      "number": 1,
      "status": "ACTIVE",
      "reason": "Cấu hình theo timeline thực tế",
      "createdAt": "2026-08-21T08:00:00Z"
    },
    "revisions": [],
    "startTime": "07:30:00",
    "endTime": "14:30:00",
    "blockDurationMinutes": null,
    "groupDurationMinutes": 45,
    "breakBetweenBlocksMinutes": null,
    "manualTimelines": [
      {
        "startTime": "07:30:00",
        "endTime": "09:00:00",
        "groupsPerSlot": 2
      }
    ],
    "breakWindows": [
      {
        "name": "Khoảng nghỉ 1",
        "startTime": "09:00:00",
        "endTime": "09:15:00"
      }
    ],
    "blocksPerDay": 3,
    "groupsPerBlock": null,
    "capacityPerDay": 7,
    "unusedMinutes": 0,
    "breakWindowMinutes": 105,
    "appliedBlockBreakMinutes": 0,
    "totalBreakMinutes": 105,
    "blocks": []
  }
}
~~~

Response thật trả đầy đủ revisions và blocks. GET list có envelope:

~~~json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 0,
    "total": 0
  }
}
~~~

GET detail trả detail và toàn bộ revisions. PATCH là full replacement:
quick PATCH phải gửi đủ quick fields; manual PATCH phải gửi đủ manual fields.
DELETE chỉ archive mềm, không xóa lịch sử.
+

## 6. Tạo Round bằng Timeframe

### 6.1 Target contract khuyến nghị

~~~http
POST /api/v1/semesters/{semesterId}/rounds
Content-Type: application/json
~~~

Request đầy đủ:

~~~json
{
  "name": "Review 1 - Đợt tháng 9",
  "type": "REVIEW_1",
  "description": "Lịch review lần 1",
  "durationMinutes": 45,
  "reviewerCount": 2,
  "maxGroupsPerTimeslot": 3,
  "registrationDeadline": "2026-08-28T23:59:00+07:00",
  "groupSelectionMode": true,
  "groupPreferenceDeadline": "2026-08-29T23:59:00+07:00",
  "resultOwnerMode": false,
  "roomTypes": ["NORMAL"],
  "timeframeId": 12,
  "startDate": "2026-09-01",
  "endDate": "2026-09-03"
}
~~~

Bắt buộc:

- timeframeId phải tồn tại, chưa archive và có revision dùng được.
- startDate/endDate bắt buộc khi dùng timeframeId.
- durationMinutes phải bằng groupDurationMinutes.
- reviewerCount đúng loại Round: REVIEW_1/2 là 2, DEFENSE_1_1 là 3,
  DEFENSE_1_2/DEFENSE_2 là 5.
- deadline có timezone offset hoặc Z và nằm trong khoảng ngày Round.
- không gửi days cùng timeframeId.
- Semester phải ACTIVE.
- roomTypes chỉ là NORMAL, SEMINAR hoặc LAB.

Response target 201:

~~~json
{
  "data": {
    "id": "85",
    "semesterId": "1",
    "name": "Review 1 - Đợt tháng 9",
    "description": "Lịch review lần 1",
    "type": "REVIEW_1",
    "status": "DRAFT",
    "reviewerCount": 2,
    "resultOwnerMode": false,
    "groupSelectionMode": true,
    "durationMinutes": 45,
    "registrationDeadline": "2026-08-28T16:59:00Z",
    "groupPreferenceDeadline": "2026-08-29T16:59:00Z",
    "maxGroupsPerTimeslot": 3,
    "roomTypes": ["NORMAL"],
    "timeframeId": "12",
    "timeframeVersionId": "21"
  }
}
~~~

Hai field cần lưu để hiển thị/trace là timeframeId và timeframeVersionId. Một
số response target tối giản có thể không trả startDate/endDate; FE lấy lại từ
GET Round Detail nếu cần.

### 6.2 Legacy create

~~~http
POST /api/v1/rounds
Content-Type: application/json
~~~

Request dùng field legacy/snake_case, riêng timeframeId vẫn được chấp nhận:

~~~json
{
  "semester_id": 1,
  "name": "Review 1 - Đợt tháng 9",
  "type": "REVIEW_1",
  "reviewer_count": 2,
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "session_duration_minutes": 45,
  "registration_deadline": "2026-08-28T23:59:00+07:00",
  "group_selection_mode": true,
  "group_preference_deadline": "2026-08-29T23:59:00+07:00",
  "max_groups_per_timeslot": 3,
  "result_owner_mode": false,
  "room_types": ["NORMAL"],
  "timeframeId": 12
}
~~~

Legacy response là object, không phải target envelope:

~~~json
{
  "id": 85,
  "semester_id": 1,
  "name": "Review 1 - Đợt tháng 9",
  "type": "REVIEW_1",
  "status": "DRAFT",
  "reviewer_count": 2,
  "session_duration_minutes": 45,
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "timeframe_id": 12,
  "timeframe_version_id": 21,
  "room_types": ["NORMAL"]
}
~~~

Chọn một contract, không trộn adapter camelCase và snake_case.

### 6.3 Backend materialize timeslot

Ví dụ Timeframe manual:

~~~text
07:30–09:00: 2 groupSlot
09:15–11:30: 3 groupSlot
13:00–14:30: 2 groupSlot
~~~

Đây là 7 groupSlot/ngày. Round có 3 ngày sẽ có 21 Round timeslot. Khoảng nghỉ
giữa timeline không tạo timeslot. Mỗi timeslot có ngày, startAt, endAt, part và
active=true.

FE không tự POST round_days hoặc timeslots trong flow Timeframe.

## 7. Round Detail và Update

### 7.1 GET detail

~~~http
GET /api/v1/rounds/{roundId}
~~~

Response target:

~~~json
{
  "data": {
    "id": "85",
    "semesterId": "1",
    "name": "Review 1 - Đợt tháng 9",
    "type": "REVIEW_1",
    "status": "DRAFT",
    "description": null,
    "durationMinutes": 45,
    "reviewerCount": 2,
    "maxGroupsPerTimeslot": 3,
    "registrationDeadline": "2026-08-28T16:59:00Z",
    "groupSelectionMode": true,
    "groupPreferenceDeadline": "2026-08-29T16:59:00Z",
    "resultOwnerMode": false,
    "roomTypes": ["NORMAL"],
    "timeframeId": "12",
    "timeframeVersionId": "21",
    "days": [
      {
        "date": "2026-09-01",
        "slots": [
          {
            "id": "1001",
            "startTime": "07:30",
            "endTime": "08:15"
          },
          {
            "id": "1002",
            "startTime": "08:15",
            "endTime": "09:00"
          },
          {
            "id": "1003",
            "startTime": "09:15",
            "endTime": "10:00"
          }
        ]
      },
      {
        "date": "2026-09-02",
        "slots": []
      },
      {
        "date": "2026-09-03",
        "slots": []
      }
    ]
  }
}
~~~

FE dùng days[].slots[] để render calendar/availability của Round. Không dùng
blocks của Timeframe để thay thế các slot đã materialize. Dùng slot.id làm key.

### 7.2 PATCH Round

~~~http
PATCH /api/v1/rounds/{roundId}
Content-Type: application/json
~~~

~~~json
{
  "timeframeId": 15,
  "startDate": "2026-09-02",
  "endDate": "2026-09-04",
  "durationMinutes": 45,
  "maxGroupsPerTimeslot": 3,
  "roomTypes": ["NORMAL", "SEMINAR"]
}
~~~

Rules:

- DRAFT: đổi Timeframe hoặc ngày sẽ xóa/sinh lại slots và ghim version mới.
- OPEN_REGISTRATION: không được regenerate Timeframe slots.
- SCHEDULING/SCHEDULED/PUBLISHED và các trạng thái sau: cấu hình bị khóa.
- Không unbind Timeframe của Round đã có generated slots.
- Nếu đã có lecturer availability hoặc group preference, regenerate bị chặn.
- Response 200 có cùng shape Round Detail target; FE nên dùng response hoặc refetch.

## 8. UI cần có

### 8.1 Cấu hình dùng chung

List card/table nên có:

- name, type, mode Quick/Manual.
- active version.
- start/end.
- blocks/timelines per day.
- capacityPerDay và groupDurationMinutes.
- tổng break và unusedMinutes.
- action Xem, Sửa, Archive.

Form quick:

1. Nhập name/type, start/end, block duration, group duration.
2. Nhập break giữa block và break windows.
3. Gọi quick preview.
4. Render blocks/groupSlots.
5. Cho sửa timeline trước khi lưu.
6. Nếu sửa timeline, chuyển payload sang manual preview/manual create.

Form manual:

- groupDurationMinutes.
- Danh sách startTime, endTime, groupsPerSlot.
- Nút thêm/xóa dòng.
- Hiển thị gap như break.
- Hiển thị duration thực tế và duration bắt buộc.
- Gọi manual preview sau khi input hợp lệ, nên debounce hoặc gọi khi blur.

Không cho save khi timeline overlap hoặc duration mismatch. Các summary như
capacity và break do Backend trả về.

### 8.2 Tạo Round

1. GET /timeframes.
2. Dropdown chỉ cho chọn Timeframe chưa archive.
3. Hiển thị preview read-only blocks/groupSlots/capacity.
4. Nhập startDate/endDate.
5. Tự điền durationMinutes bằng groupDurationMinutes, nên disable.
6. Nhập reviewerCount, deadlines, roomTypes, maxGroupsPerTimeslot.
7. Submit timeframeId + startDate + endDate.
8. Sau success gọi GET Round detail để hiển thị slots.

Khi chọn Timeframe, không render form days[].slots[] trong cùng payload. Nếu
dùng flow explicit days cũ thì bỏ timeframeId.

### 8.3 Round Detail/calendar

Header nên có:

~~~text
Timeframe: Hội đồng tùy chỉnh
Version: v3
Round duration: 45 phút
Timeslots: 21
~~~

Calendar lấy days[].slots[]:

- group theo ngày;
- hiển thị slot start/end;
- gap giữa 11:45 và 13:00 là break;
- không tự sinh slot;
- key là slot.id.

### 8.4 Registration và scheduler

Lecturer:

~~~text
PENDING invitation
→ Accept
→ availability form
→ PUT availability
~~~

Leader:

~~~text
OPEN_REGISTRATION
→ chọn các Round timeslot
→ PUT toàn bộ timeslotIds
~~~

Manager:

~~~text
resources/readiness
→ run scheduler
→ hiển thị unscheduled
→ activate version
→ suggest/apply room
→ publish-readiness
→ publish
~~~

Lịch preview Timeframe không phải lịch chính thức.
+

## 9. Scheduler, room và publish request/response

### 9.1 Run scheduler

~~~http
POST /api/v1/rounds/{roundId}/schedule/run
Content-Type: application/json
~~~

~~~json
{
  "randomSeed": 0,
  "timeLimitSeconds": 10
}
~~~

Response legacy 201:

~~~json
{
  "version_id": 31,
  "status": "FEASIBLE",
  "scheduled_count": 21,
  "unscheduled": [],
  "soft_scores": {
    "total": 87,
    "S1": 20
  }
}
~~~

version_id là ScheduleVersion draft mới. Nếu unscheduled không rỗng, UI phải
hiển thị từng lý do thay vì báo thành công hoàn toàn.

Nếu FE dùng target schedule contract, endpoint tương ứng là:

~~~http
POST /api/v1/rounds/{roundId}/schedules/generate
Content-Type: application/json
~~~

Response target:

~~~json
{
  "data": {
    "versionId": "sv_31",
    "versionNumber": 1,
    "status": "FEASIBLE",
    "scheduledCount": 21,
    "unscheduledCount": 0,
    "overallScore": 87,
    "scores": { "S1": 20 },
    "unscheduled": []
  }
}
~~~

Target versionId có thể là external ID dạng sv_31; dùng đúng ID mà response trả
ở các request target tiếp theo.

Scheduler đọc các group đã attach, active Round timeslots do Timeframe tạo,
reviewer availability, group preference nếu bật, councils và hard constraints.

### 9.2 Activate

~~~http
POST /api/v1/schedule/versions/{versionId}/activate
~~~

Response action đại diện:

~~~json
{
  "id": 31,
  "status": "ACTIVE"
}
~~~

### 9.3 Suggest/apply room

Suggest:

~~~http
POST /api/v1/rounds/{roundId}/rooms/suggest
~~~

Apply:

~~~http
POST /api/v1/rounds/{roundId}/rooms/apply-suggestions
Content-Type: application/json
~~~

~~~json
{
  "assignments": [
    { "sessionId": 301, "roomId": 7 },
    { "sessionId": 302, "roomId": 8 }
  ]
}
~~~

Response đại diện:

~~~json
{
  "data": {
    "roundId": 85,
    "changedCount": 2,
    "unchangedCount": 0,
    "assignments": [
      { "sessionId": 301, "roomId": 7 },
      { "sessionId": 302, "roomId": 8 }
    ]
  }
}
~~~

### 9.4 Publish readiness

~~~http
GET /api/v1/rounds/{roundId}/publish-readiness
~~~

Ready:

~~~json
{
  "data": {
    "ready": true,
    "versionId": 31,
    "blockers": []
  }
}
~~~

Not ready:

~~~json
{
  "data": {
    "ready": false,
    "versionId": 31,
    "blockers": [
      {
        "code": "ROOM_ASSIGNMENT_MISSING",
        "message": "Every scheduled session must have a room."
      }
    ]
  }
}
~~~

### 9.5 Publish

Target:

~~~http
POST /api/v1/rounds/{roundId}/actions/publish
Content-Type: application/json
~~~

~~~json
{
  "versionId": 31
}
~~~

Response:

~~~json
{
  "data": {
    "roundId": 85,
    "versionId": 31,
    "status": "PUBLISHED",
    "recipientCount": 48
  }
}
~~~

Legacy publish:

~~~http
POST /api/v1/rounds/{roundId}/schedule/publish/{versionId}
~~~

Sau publish, refetch Round Detail và gọi endpoint schedule/session của từng actor.
Không dùng preview hoặc scheduler draft làm lịch cuối cho Student/Lecturer.

## 10. Registration request/response

### 10.1 Lecturer invitation

~~~http
GET /api/v1/lecturer/me/invitations
~~~

~~~json
{
  "data": [
    {
      "id": "inv_85_12",
      "round": {
        "id": "85",
        "name": "Review 1 - Đợt tháng 9",
        "type": "REVIEW_1",
        "registrationDeadline": "2026-08-28T16:59:00Z"
      },
      "status": "PENDING",
      "respondedAt": null
    }
  ]
}
~~~

Respond:

~~~http
POST /api/v1/rounds/{roundId}/invitations/me/respond
~~~

Accept:

~~~json
{ "decision": "ACCEPTED" }
~~~

Decline:

~~~json
{
  "decision": "DECLINED",
  "reason": "Không thể tham gia round này"
}
~~~

Chỉ sau ACCEPTED mới mở availability.

Response invitation hiện tại có thể không có respondedAt trong target portal; FE
không nên bắt buộc field đó phải tồn tại. Trạng thái cần hỗ trợ là PENDING,
ACCEPTED, DECLINED và EXPIRED.

### 10.2 Lecturer availability

~~~http
PUT /api/v1/rounds/{roundId}/availability/me
~~~

~~~json
{
  "preferredLoad": "MEDIUM",
  "slots": [
    { "timeslotId": "ts_1001", "available": true },
    { "timeslotId": "ts_1002", "available": false }
  ]
}
~~~

Success:

~~~json
{
  "data": {
    "roundId": 85,
    "lecturerId": 12,
    "selectedCount": 1,
    "totalSlots": 21,
    "source": "FORM"
  }
}
~~~

### 10.3 Group Leader preference

~~~http
PUT /api/v1/rounds/{roundId}/groups/{groupId}/preferences
~~~

~~~json
{
  "timeslotIds": ["ts_1001", "ts_1005", "ts_1010"]
}
~~~

Success:

~~~json
{
  "data": {
    "roundId": 85,
    "groupId": 7,
    "selectedCount": 3,
    "totalSlots": 21,
    "source": "FORM"
  }
}
~~~

timeslotIds là replacement toàn bộ, không phải append. Gửi mảng rỗng để xóa
toàn bộ preference.

## 11. Error contract

~~~json
{
  "error": {
    "code": "TIMEFRAME_SESSION_DURATION_MISMATCH",
    "message": "Round duration must equal the Timeframe group duration.",
    "details": {}
  }
}
~~~

| HTTP | Code | UI xử lý |
|---:|---|---|
| 401 | UNAUTHENTICATED/SESSION_EXPIRED | Về login |
| 403 | FORBIDDEN/AUTH_RESOURCE_SCOPE | Không có quyền |
| 404 | TIMEFRAME_NOT_FOUND | Reload list, bỏ lựa chọn cũ |
| 409 | TIMEFRAME_NAME_DUPLICATE | Báo trùng tên |
| 409 | ROUND_TIMEFRAME_UNBIND_NOT_ALLOWED | Không cho unbind |
| 409 | ROUND_TIMEFRAME_LOCKED | Khóa sửa Timeframe |
| 409 | ROUND_TIMEFRAME_REGENERATION_BLOCKED | Đã có đăng ký, không rebuild |
| 409 | ROUND_CONFIG_LOCKED | Round đã vào scheduler |
| 409 | REGISTRATION_PHASE_INVALID | Refetch Round Detail, khóa form |
| 409 | GROUP_SELECTION_DISABLED | Ẩn preference |
| 422 | TIMEFRAME_SESSION_DURATION_MISMATCH | Khớp duration với Timeframe |
| 422 | ROUND_TIMEFRAME_DAYS_CONFLICT | Không gửi days cùng timeframeId |
| 422 | TIMEFRAME_INVALID_RANGE | Sửa khoảng giờ |
| 422 | TIMEFRAME_NO_BLOCK_FITS | Giảm block hoặc tăng khung ngày |
| 422 | GROUP_DURATION_NOT_DIVISIBLE | Chọn duration chia hết block |
| 422 | MANUAL_TIMELINE_DURATION_MISMATCH | Sửa timeline duration |
| 422 | MANUAL_TIMELINE_OVERLAP | Sửa timeline chồng nhau |
| 422 | ROUND_GROUPS_REQUIRED | Gắn group vào Round |
| 422 | ROUND_TIMESLOTS_REQUIRED | Kiểm tra materialization |
| 422 | ROUND_REVIEWERS_INSUFFICIENT | Kiểm tra reviewer/availability |
| 422 | ROUND_INPUTS_INCOMPLETE | Hiển thị readiness checklist |
| 422 | ROOM_ASSIGNMENT_MISSING | Gán phòng |
| 422 | ROOM_CONFLICT | Đổi phòng |
| 422 | VERSION_NOT_ACTIVE | Activate version |
| 422 | MATERIALIZATION_INCOMPLETE | Kiểm tra session/assignment |

FE nên map theo error.code, dùng error.message làm fallback, không render thẳng
object detail.

## 12. QA checklist trên UI

### Timeframe

- [ ] Quick preview hiển thị blocks, groupSlots, capacity và break.
- [ ] Tạo manual với timeline 07:00–09:15, group 45 phút, 3 nhóm là hợp lệ.
- [ ] Timeline 07:00–09:00, group 45 phút, 3 nhóm bị mismatch.
- [ ] Timeline overlap bị từ chối; chạm biên được phép.
- [ ] Có thể sửa/thêm/xóa timeline sau quick preview.
- [ ] PATCH gửi full payload và không làm mất break/timeline.
- [ ] Archive vẫn giữ detail/revision history.

### Round

- [ ] Dropdown chỉ có Timeframe active.
- [ ] Chọn Timeframe hiển thị group duration và capacity.
- [ ] Submit có timeframeId/startDate/endDate và không có days.
- [ ] Response có timeframeId/timeframeVersionId.
- [ ] GET Round detail hiển thị đúng version và slots.
- [ ] Số slot đúng bằng groupSlot mỗi ngày nhân số ngày.
- [ ] Khoảng nghỉ không xuất hiện thành slot.

### Snapshot/update

- [ ] Sửa Timeframe global sau khi Round đã tạo không đổi Round cũ.
- [ ] Round mới dùng version mới.
- [ ] DRAFT đổi Timeframe/date thì slots rebuild.
- [ ] Đã có availability/preference thì rebuild bị chặn.
- [ ] Round sau DRAFT không cho regenerate.

### Scheduler/publish

- [ ] Gắn group và có project/active leader.
- [ ] Đủ reviewer đúng loại Round.
- [ ] Lecturer accept invitation trước availability.
- [ ] Leader gửi preference replacement.
- [ ] Run scheduler hiển thị scheduled và unscheduled.
- [ ] Activate version trước publish.
- [ ] Gán phòng đủ và không conflict.
- [ ] publish-readiness hiển thị blocker.
- [ ] Chỉ publish khi ready=true.
- [ ] Sau publish lịch chính thức xuất hiện.

### Auth/error

- [ ] GET dùng cookie session.
- [ ] Mutation có CSRF.
- [ ] 401 về login.
- [ ] 403 hiển thị thiếu quyền.
- [ ] 409/422 hiển thị lỗi nghiệp vụ và retry/refetch phù hợp.

## 13. Những việc FE không làm

- Không tự sinh round_days/timeslots khi dùng Timeframe.
- Không gửi timeframeId cùng explicit days[].slots[].
- Không tự ghi capacity/blocksPerDay vào Round.
- Không sửa timeframeVersionId bằng tay.
- Không kỳ vọng sửa Timeframe global làm đổi Round cũ.
- Không dùng groupsPerSlot thay maxGroupsPerTimeslot.
- Không dùng preview làm lịch chính thức.
- Không dùng index làm key cho slot; dùng slot.id sau khi Backend materialize.
- Không dùng Bearer token hoặc truyền lecturerId trong personal endpoints.

## 14. Hàm gọi API mẫu

~~~ts
async function requestJson<T>(
  url: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(API_URL + url, {
    credentials: "include",
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(init.headers ?? {}),
    },
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = body?.error ?? body?.detail ?? {};
    const code = error.code ?? ("HTTP_" + response.status);
    throw Object.assign(new Error(error.message ?? code), {
      status: response.status,
      code,
      details: error.details ?? {},
    });
  }
  return body as T;
}
~~~

Wrapper thật cần thêm X-CSRF-Token cho mutation.
