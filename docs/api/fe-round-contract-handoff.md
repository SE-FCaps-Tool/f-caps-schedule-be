# FE Handoff — Round Detail và đăng ký tuần tự

Ngày cập nhật: 2026-08-20

Tài liệu này mô tả các thay đổi BE mà FE cần tích hợp. FE không cần tự tính
supervisor/COI hay số reviewer khả dụng trong phạm vi thay đổi này.

## 1. Round Detail

### Endpoint

```http
GET /api/v1/rounds/:roundId
```

Request không có body hoặc query.

### Response mới

BE trả envelope `data`, dùng camelCase và nhóm timeslot theo ngày:

```json
{
  "data": {
    "id": "85",
    "semesterId": "1",
    "name": "Defense 1.1",
    "type": "DEFENSE_1_1",
    "status": "DRAFT",
    "description": null,
    "durationMinutes": 30,
    "reviewerCount": 3,
    "maxGroupsPerTimeslot": 3,
    "registrationDeadline": "2030-01-20T16:59:00Z",
    "groupSelectionMode": true,
    "groupPreferenceDeadline": "2030-01-22T16:59:00Z",
    "resultOwnerMode": true,
    "roomTypes": ["NORMAL"],
    "days": [
      {
        "date": "2030-02-01",
        "slots": [
          {
            "id": "76",
            "startTime": "09:00",
            "endTime": "09:30"
          }
        ]
      }
    ]
  }
}
```

Các slot `active=false` không xuất hiện. Ngày không có slot active vẫn được trả
với `slots: []`. `startTime` và `endTime` dùng múi giờ `Asia/Ho_Chi_Minh`.

FE tiếp tục đọc:

```ts
const response = await apiService.get<{ data: RoundDetail }>(url);
return response.data.data;
```

Không cần adapter snake_case ở FE.

## 2. Hai giai đoạn đăng ký tuần tự

Round vẫn dùng một trạng thái `OPEN_REGISTRATION`. BE suy ra giai đoạn hiện tại
từ hai deadline:

```text
status != OPEN_REGISTRATION
  → INACTIVE

status == OPEN_REGISTRATION && now <= registrationDeadline
  → LECTURER

status == OPEN_REGISTRATION
&& registrationDeadline < now
&& now <= groupPreferenceDeadline
  → GROUP

now > groupPreferenceDeadline
  → CLOSED
```

Giá trị đúng tại biên:

- `now == registrationDeadline`: vẫn là giai đoạn Lecturer.
- `now == groupPreferenceDeadline`: vẫn là giai đoạn Group.

FE có thể dùng `status` và hai deadline từ Round Detail để ẩn/hiện UI, nhưng BE
luôn kiểm tra lại và là nguồn quyết định cuối cùng.

## 3. Tạo Round

### Endpoint

```http
POST /api/v1/semesters/:semesterId/rounds
```

Các field liên quan không đổi tên:

```json
{
  "registrationDeadline": "2030-01-20T23:59:00+07:00",
  "groupSelectionMode": true,
  "groupPreferenceDeadline": "2030-01-22T23:59:00+07:00"
}
```

Validation mới:

- Deadline phải có timezone offset, ví dụ `+07:00` hoặc `Z`.
- Khi `groupSelectionMode=true`, cả hai deadline đều bắt buộc.
- `groupPreferenceDeadline` phải lớn hơn `registrationDeadline`.
- Khi `groupSelectionMode=false`, không có giai đoạn Student chọn preference.

Request sai trả `422 VALIDATION_ERROR` theo error envelope chuẩn.

## 4. Lecturer Availability

### Endpoints

```http
GET /api/v1/rounds/:roundId/availability/me
PUT /api/v1/rounds/:roundId/availability/me
```

Request PUT không đổi:

```json
{
  "preferredLoad": "HIGH",
  "slots": [
    {"timeslotId": "ts_01", "available": true},
    {"timeslotId": "ts_02", "available": false}
  ]
}
```

Điều kiện mới cho Lecturer khi ghi (PUT):

- Round phải là `OPEN_REGISTRATION`.
- Giai đoạn hiện tại phải là `LECTURER`.
- Invitation phải là `ACCEPTED`.
- Lecturer chỉ sửa availability của chính mình.

Success response PUT giữ nguyên shape:

```json
{
  "data": {
    "roundId": 85,
    "lecturerId": 12,
    "selectedCount": 1,
    "totalSlots": 10,
    "source": "FORM"
  }
}
```

Manager/Admin vẫn có thể nhập thay ngoài cửa sổ Lecturer bằng endpoint quản lý
hiện có.

GET là thao tác đọc lịch sử: Lecturer đã được mời và chấp nhận vẫn xem được
availability của mình sau khi phase chuyển sang `GROUP` hoặc đã đóng; chỉ PUT
mới bị chặn bởi phase.

## 5. Leader Dashboard

### Endpoint

```http
GET /api/v1/leader/me/dashboard
```

Request không có body hoặc query. Endpoint dùng cookie session và không cần
CSRF vì là request GET.

### Response

```json
{
  "data": {
    "group": {
      "id": "7",
      "code": "G01",
      "memberCount": 4,
      "maxMembers": 5
    },
    "project": {
      "id": "12",
      "code": "PRJ01",
      "titleVi": "Capstone Defense Scheduler",
      "titleEn": null,
      "status": "ACTIVE"
    },
    "mainSupervisor": {"id": "21", "name": "Nguyen Van A"},
    "coSupervisor": null,
    "currentRound": {
      "id": "85",
      "name": "Defense 1.1",
      "type": "DEFENSE_1_1",
      "status": "OPEN_REGISTRATION"
    },
    "preferenceStatus": "PENDING",
    "deadline": "2030-01-22T16:59:00Z",
    "upcomingSession": {
      "id": "301",
      "date": "2030-02-01",
      "startTime": "09:00",
      "endTime": "09:30",
      "room": "P-201"
    },
    "latestResult": {
      "roundType": "REVIEW_2",
      "kind": "REVIEW",
      "value": "LEVEL_1",
      "date": "2030-01-10"
    },
    "remediation": {
      "deadline": "2030-01-15T16:59:00Z",
      "status": "PENDING"
    }
  }
}
```

Các object trên đều có thể là `null` theo type FE. Nếu Student không phải active
Leader của nhóm nào, BE trả đủ các key nhưng toàn bộ giá trị là `null`.

Các ID lồng trong `group`, `project`, `mainSupervisor`, `coSupervisor`,
`currentRound` và `upcomingSession` là numeric string, ví dụ `"85"`, không có
prefix. `memberCount` và `maxMembers` là number; `maxMembers` hiện là `5`.

Quy tắc chọn dữ liệu:

- Chỉ xét membership `LEADER` đang `ACTIVE`. Nếu có nhiều nhóm, BE ưu tiên nhóm
  có Project thuộc Semester `ACTIVE`, sau đó sắp theo mã nhóm và ID.
- `currentRound` chỉ là Round gắn với nhóm và đang `OPEN_REGISTRATION`; nếu có
  nhiều Round phù hợp, BE lấy Round có ID lớn nhất. Round ở trạng thái khác không
  được trả trong field này.
- `deadline` là `groupPreferenceDeadline` của `currentRound`, hoặc `null` khi
  không có `currentRound`.
- `preferenceStatus = NOT_REQUIRED` khi không có Round đang mở hoặc Round không
  bật `groupSelectionMode`; bằng `SUBMITTED` khi đã tồn tại ít nhất một preference
  `selected=true`; còn lại là `PENDING`.
- `upcomingSession` chỉ lấy session tương lai gần nhất có trạng thái `SCHEDULED`
  thuộc Schedule Version `PUBLISHED`. `date`, `startTime`, `endTime` dùng múi giờ
  `Asia/Ho_Chi_Minh`.
- `latestResult.kind` là `REVIEW` với Round type bắt đầu bằng `REVIEW_`, các loại
  còn lại là `DEFENSE`.

Mapping `project.status` từ dữ liệu BE sang `ProjectStatus` của FE:

- Project `ARCHIVED` → `CANCELLED`.
- Project còn active và Group đã tiến triển → một trong `ELIGIBLE_D12`,
  `D12_CONDITIONAL`, `PENDING_D2`, `COMPLETED`, `FAILED` theo trạng thái Group.
- Các trường hợp active còn lại, bao gồm Group `PENDING_D11` → `ACTIVE`.

`project.titleEn` hiện luôn là `null`. BE hiện không tạo giá trị `DRAFT` từ
endpoint Dashboard.

Mapping `remediation.status`:

- Trạng thái DB `OPEN` → `PENDING` cho FE.
- `PASSED`, `OVERDUE`, `FAILED` được giữ nguyên.
- `remediation = null` khi nhóm chưa có remediation case.

## 6. Student Group Preference

### Endpoints

```http
GET /api/v1/rounds/:roundId/groups/:groupId/preferences
PUT /api/v1/rounds/:roundId/groups/:groupId/preferences
```

Request PUT không đổi:

```json
{
  "timeslotIds": ["ts_01", "ts_02", "ts_05"]
}
```

Điều kiện mới khi ghi (PUT):

- Round phải là `OPEN_REGISTRATION`.
- Giai đoạn hiện tại phải là `GROUP`.
- `groupSelectionMode=true`.
- Current Student phải là active Leader của nhóm.
- Nhóm phải được gắn vào Round.
- Lecturer và member thường không được đọc hoặc sửa preference của nhóm.

Success response GET giữ nguyên shape:

```json
{
  "data": {
    "roundId": 85,
    "groupId": 7,
    "timeslots": [
      {
        "timeslotId": 76,
        "startAt": "2030-02-01T02:00:00Z",
        "endAt": "2030-02-01T02:30:00Z",
        "selected": true,
        "source": "FORM"
      }
    ]
  }
}
```

GET chỉ trả timeslot đang `active=true`. Với timeslot chưa được nhóm chọn hoặc
chưa từng lưu, `selected` và `source` có thể là `null`; FE chuẩn hóa
`selected === true` thành boolean khi render. Với lựa chọn do Leader lưu,
`source` là `FORM`.

Success response PUT giữ nguyên shape:

```json
{
  "data": {
    "roundId": 85,
    "groupId": 7,
    "selectedCount": 3,
    "totalSlots": 10,
    "source": "FORM"
  }
}
```

PUT dùng replacement semantics: `timeslotIds` là toàn bộ danh sách lựa chọn mới,
không phải danh sách bổ sung. Các lựa chọn cũ không còn trong request bị xóa;
gửi `{"timeslotIds": []}` sẽ xóa toàn bộ lựa chọn. Chỉ ID của timeslot đang
`active=true` và thuộc Round được chấp nhận; gửi ID ngoài tập này trả
`422 AVAILABILITY_SLOT_INVALID` và không lưu một phần request.

Khi đọc preference với tư cách Student, GET vẫn cho xem các lựa chọn đã lưu sau
khi phase chuyển sang `CLOSED`; chỉ PUT mới yêu cầu phase `GROUP`. GET chỉ trả
timeslot active thuộc Round và không expose availability của giảng viên cho
Student. Manager/Admin vẫn có thể xem toàn bộ availability để quản trị.

## 7. Lecturer Invitations

Các endpoint này dùng cookie session hiện tại của hệ thống, không dùng Bearer
JWT. Request thay đổi dữ liệu phải gửi thêm CSRF token theo cơ chế cookie +
`X-CSRF-Token`; request GET không cần CSRF.

### Danh sách lời mời của Lecturer

```http
GET /api/v1/lecturer/me/invitations
```

Request không có body hoặc query. Response:

```json
{
  "data": [
    {
      "id": "inv_85_7",
      "round": {
        "id": "85",
        "name": "Defense 1.1",
        "type": "DEFENSE_1_1",
        "registrationDeadline": "2026-08-20T23:59:00+07:00"
      },
      "status": "PENDING",
      "respondedAt": null
    }
  ]
}
```

`round.id` là numeric string có chủ đích, ví dụ `"85"`, để FE dùng trực tiếp
trong path của endpoint phản hồi bên dưới. Không thêm prefix `rnd_`.

Các trạng thái BE có thể trả:

- `PENDING`: chưa phản hồi và chưa quá hạn đăng ký.
- `ACCEPTED`: Lecturer đã nhận lời.
- `DECLINED`: Lecturer đã từ chối.
- `EXPIRED`: invitation còn `PENDING` nhưng đã quá `registrationDeadline`.

`WITHDRAWN` có trong enum phía FE nhưng BE hiện chưa có transition tạo ra trạng
thái này. `respondedAt` là ISO datetime hoặc `null` khi chưa phản hồi.

### Lecturer phản hồi lời mời

```http
POST /api/v1/rounds/:roundId/invitations/me/respond
Content-Type: application/json
X-CSRF-Token: <giá trị cookie scheduler_csrf>
```

Nhận lời:

```json
{"decision": "ACCEPTED"}
```

Từ chối; `reason` là bắt buộc:

```json
{"decision": "DECLINED", "reason": "Lý do từ chối"}
```

FE chỉ cần kiểm tra HTTP status 2xx khi thành công, không cần đọc success body.

## 8. Error handling FE cần hỗ trợ

Target endpoints trả lỗi theo dạng:

```json
{
  "error": {
    "code": "REGISTRATION_PHASE_INVALID",
    "message": "This action requires the GROUP registration phase; current phase is LECTURER.",
    "details": {}
  }
}
```

Các mã liên quan:

| HTTP | Code | Ý nghĩa FE |
|---|---|---|
| 409 | `REGISTRATION_PHASE_INVALID` | Chưa tới hoặc đã hết giai đoạn cho actor hiện tại |
| 409 | `GROUP_SELECTION_DISABLED` | Round không bật chức năng nhóm chọn slot |
| 403 | `AUTH_RESOURCE_SCOPE` | Không phải Lecturer/active Leader của resource |
| 403 | `GROUP_NOT_IN_ROUND` | Leader đang truy cập nhóm không thuộc Round |
| 422 | `GROUP_NOT_IN_ROUND` | Manager truy cập nhóm không thuộc Round |
| 409 | `GROUP_ALREADY_REVIEWED` | Nhóm đã thuộc một Round `REVIEW_1` chưa bị hủy |
| 422 | `VALIDATION_ERROR` | Request tạo Round hoặc deadline không hợp lệ |
| 422 | `AVAILABILITY_SLOT_INVALID` | Preference chứa timeslot không active hoặc không thuộc Round |

FE nên refetch Round Detail khi nhận `REGISTRATION_PHASE_INVALID`, vì deadline
hoặc trạng thái Round có thể vừa chuyển trong lúc màn hình đang mở.

## 9. Checklist tích hợp FE

- Round Detail đọc `response.data.data`.
- Không map snake_case cho Round Detail.
- Form Lecturer chỉ enable trong phase `LECTURER`.
- Form Leader chỉ enable trong phase `GROUP`.
- Đồng hồ FE chỉ phục vụ UX; không thay thế validation từ BE.
- Khi nhận `409 REGISTRATION_PHASE_INVALID`, khóa form và refetch Round Detail.
- Không hiển thị UI Group Preference khi `groupSelectionMode=false`.
- Dashboard chỉ dùng `currentRound` do BE trả; không suy ra Round đang mở từ
  lịch sử Round khác.
- PUT Group Preference gửi toàn bộ selection hiện tại; gửi mảng rỗng để bỏ chọn
  tất cả.
- Không gửi deadline thiếu timezone offset.
- Đọc invitation từ `response.data.data` và dùng `invitation.round.id` trực
  tiếp cho endpoint phản hồi.
- Không gửi Bearer token; dùng cookie session và gửi CSRF header cho POST phản
  hồi invitation.
