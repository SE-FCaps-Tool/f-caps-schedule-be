# FE Handoff — Global Timeframe Configuration

Timeframe là cấu hình thời gian dùng chung của toàn hệ thống. Manager quản lý
Timeframe tại màn hình Cấu hình dùng chung; Timeframe không thuộc một Round.

Backend hỗ trợ hai cách tạo:

- Tạo nhanh: nhập công thức, backend sinh timeline nháp.
- Tạo thủ công: FE gửi danh sách timeline cuối cùng sau khi người dùng tự nhập
  hoặc chỉnh kết quả tạo nhanh.

Hai cách đều trả cùng cấu trúc `blocks[].groupSlots[]`. Khi tạo Round, FE có thể
chọn `timeframeId`; backend sẽ ghim version ACTIVE tại thời điểm tạo Round và
sinh timeslot thật cho từng ngày của Round.

## 1. Khái niệm

- `block` hoặc `timeline`: một khung chấm lớn, ví dụ `07:00–09:15`.
- `groupSlot`: thời gian dành cho một nhóm bên trong timeline.
- `groupDurationMinutes`: quy ước thời lượng của một nhóm.
- `groupsPerSlot`: số nhóm được chấm trong một timeline thủ công.

```text
Timeline 07:00–09:15
groupDurationMinutes = 45
groupsPerSlot = 3

→ Nhóm 1: 07:00–07:45
→ Nhóm 2: 07:45–08:30
→ Nhóm 3: 08:30–09:15
```

Khoảng trống giữa hai timeline thủ công được xem là giờ nghỉ. Ví dụ timeline
trước kết thúc `11:45`, timeline sau bắt đầu `13:00` thì giờ nghỉ là
`11:45–13:00`.

## 2. Authentication

Base URL local:

```text
http://localhost:8000/api/v1
```

Chỉ role `ADMIN` hoặc `MANAGER` được gọi API. FE dùng cookie session:

```ts
credentials: "include"
```

Các request `POST`, `PATCH`, `DELETE` phải gửi `X-CSRF-Token` bằng cookie
`scheduler_csrf`. Không dùng Bearer token.

## 3. Danh sách endpoint

| Method | Endpoint | Thành công | Chức năng |
|---|---|---:|---|
| `POST` | `/timeframes/preview` | `200` | Sinh timeline nháp bằng công thức tạo nhanh. |
| `POST` | `/timeframes/manual/preview` | `200` | Tính ngược số liệu sau khi FE chỉnh timelines, không ghi DB. |
| `POST` | `/timeframes` | `201` | Tạo nhanh trực tiếp bằng công thức. |
| `POST` | `/timeframes/manual` | `201` | Tạo từ danh sách timeline cuối cùng. |
| `GET` | `/timeframes` | `200` | Danh sách Timeframe chưa archive. |
| `GET` | `/timeframes?includeArchived=true` | `200` | Gồm cả Timeframe đã archive. |
| `GET` | `/timeframes/{timeframeId}` | `200` | Detail, blocks và lịch sử revision. |
| `PATCH` | `/timeframes/{timeframeId}` | `200` | Full replacement bằng công thức tạo nhanh. |
| `PATCH` | `/timeframes/{timeframeId}/manual` | `200` | Full replacement bằng timelines thủ công. |
| `DELETE` | `/timeframes/{timeframeId}` | `200` | Archive mềm, không xóa lịch sử. |

## 4. TypeScript types

```ts
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

export type QuickTimeframePreviewRequest = {
  startTime: string;
  endTime: string;
  blockDurationMinutes: number;
  groupDurationMinutes: number;
  breakBetweenBlocksMinutes?: number;
  breakWindows?: TimeframeBreakWindow[];
};

export type QuickTimeframeMutationRequest = QuickTimeframePreviewRequest & {
  name: string;
  type: string;
  reason?: string | null;
};

export type ManualTimeframePreviewRequest = {
  groupDurationMinutes: number;
  timelines: ManualTimeline[];
};

export type ManualTimeframeMutationRequest = ManualTimeframePreviewRequest & {
  name: string;
  type: string;
  reason?: string | null;
};
```

Tất cả giờ là `HH:mm` hoặc `HH:mm:ss`, theo giờ local và không kèm `Z`/UTC
offset.

## 5. Tạo nhanh và lấy timeline nháp

```http
POST /api/v1/timeframes/preview
Content-Type: application/json
```

```json
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
```

Backend tính:

```text
groupsPerBlock = blockDurationMinutes / groupDurationMinutes
blocksInSegment = floor(
  (segmentMinutes + breakBetweenBlocksMinutes)
  / (blockDurationMinutes + breakBetweenBlocksMinutes)
)
capacityPerDay = blocksPerDay × groupsPerBlock
```

Response `200` có đầy đủ `blocks`. FE dùng `blocks` làm timelines nháp:

```json
{
  "data": {
    "startTime": "07:00:00",
    "endTime": "17:30:00",
    "blockDurationMinutes": 135,
    "groupDurationMinutes": 45,
    "breakBetweenBlocksMinutes": 15,
    "breakWindows": [
      { "name": "Nghỉ trưa", "startTime": "11:45:00", "endTime": "13:00:00" }
    ],
    "manualTimelines": null,
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
          { "sequenceNumber": 1, "startTime": "07:00:00", "endTime": "07:45:00" },
          { "sequenceNumber": 2, "startTime": "07:45:00", "endTime": "08:30:00" },
          { "sequenceNumber": 3, "startTime": "08:30:00", "endTime": "09:15:00" }
        ]
      }
    ]
  }
}
```

`blocks` trong ví dụ được rút gọn. Response thật trả đủ block.

Nếu không chỉnh timeline, FE có thể tạo nhanh trực tiếp bằng
`POST /api/v1/timeframes` với `QuickTimeframeMutationRequest`.

## 6. Chỉnh timeline trước khi tạo

Sau quick preview, FE chuyển mỗi block thành:

```ts
const timelines: ManualTimeline[] = preview.blocks.map((block) => ({
  startTime: block.startTime,
  endTime: block.endTime,
  groupsPerSlot: block.groupSlots.length,
}));
```

Người dùng được phép thêm/xóa timeline, sửa giờ bắt đầu/kết thúc, sửa số nhóm
và sửa quy ước số phút của một nhóm.

Mỗi lần thay đổi hợp lệ, FE gọi manual preview để backend kiểm tra và tính lại:

```http
POST /api/v1/timeframes/manual/preview
Content-Type: application/json
```

```json
{
  "groupDurationMinutes": 45,
  "timelines": [
    { "startTime": "07:30:00", "endTime": "09:00:00", "groupsPerSlot": 2 },
    { "startTime": "09:15:00", "endTime": "11:30:00", "groupsPerSlot": 3 },
    { "startTime": "13:00:00", "endTime": "14:30:00", "groupsPerSlot": 2 }
  ]
}
```

Response:

```json
{
  "data": {
    "startTime": "07:30:00",
    "endTime": "14:30:00",
    "blockDurationMinutes": null,
    "groupDurationMinutes": 45,
    "breakBetweenBlocksMinutes": null,
    "manualTimelines": [
      { "startTime": "07:30:00", "endTime": "09:00:00", "groupsPerSlot": 2 },
      { "startTime": "09:15:00", "endTime": "11:30:00", "groupsPerSlot": 3 },
      { "startTime": "13:00:00", "endTime": "14:30:00", "groupsPerSlot": 2 }
    ],
    "blocksPerDay": 3,
    "groupsPerBlock": null,
    "capacityPerDay": 7,
    "unusedMinutes": 0,
    "breakWindowMinutes": 105,
    "appliedBlockBreakMinutes": 0,
    "totalBreakMinutes": 105,
    "breakWindows": [
      { "name": "Khoảng nghỉ 1", "startTime": "09:00:00", "endTime": "09:15:00" },
      { "name": "Khoảng nghỉ 2", "startTime": "11:30:00", "endTime": "13:00:00" }
    ],
    "blocks": []
  }
}
```

Response thật trả đầy đủ `blocks` và `groupSlots`.

Các field chung trả `null` nếu timelines không đồng đều:

- `blockDurationMinutes`: `null` nếu block có thời lượng khác nhau.
- `groupsPerBlock`: `null` nếu block có số nhóm khác nhau.
- `breakBetweenBlocksMinutes`: luôn `null` trong manual vì từng khoảng nghỉ có
  thể khác nhau.

## 7. Tạo và cập nhật manual

```http
POST /api/v1/timeframes/manual
PATCH /api/v1/timeframes/{timeframeId}/manual
```

Body dùng chung:

```json
{
  "name": "Hội đồng tùy chỉnh",
  "type": "COUNCIL",
  "groupDurationMinutes": 45,
  "timelines": [
    { "startTime": "07:30:00", "endTime": "09:00:00", "groupsPerSlot": 2 },
    { "startTime": "09:15:00", "endTime": "11:30:00", "groupsPerSlot": 3 },
    { "startTime": "13:00:00", "endTime": "14:30:00", "groupsPerSlot": 2 }
  ],
  "reason": "Điều chỉnh timeline từ kết quả tạo nhanh"
}
```

Backend tự sắp xếp timeline, đánh lại sequence, sinh group slots, tính khung
ngày, capacity và suy ra giờ nghỉ. Snapshot timeline được lưu theo revision.

Mỗi lần PATCH, revision hiện tại chuyển thành `SUPERSEDED`; revision mới là
`ACTIVE`. Có thể chuyển Timeframe nhanh sang manual bằng PATCH manual, hoặc
chuyển manual về công thức bằng PATCH `/timeframes/{id}`.

## 8. Quy tắc validation manual

```text
timelineDurationMinutes = endTime - startTime
requiredMinutes = groupDurationMinutes × groupsPerSlot

timelineDurationMinutes phải bằng requiredMinutes
```

Ví dụ `07:00–09:15 = 135 phút` và `45 × 3 = 135 phút` là hợp lệ.

- Có từ 1 đến 50 timelines.
- `groupDurationMinutes > 0`.
- `groupsPerSlot > 0`.
- Mỗi `endTime` phải sau `startTime`.
- Giờ manual phải khớp tới phút; giây và microsecond phải bằng `0`.
- Timelines không được chồng lấn; chạm biên được phép.
- Backend sắp xếp timelines; FE không gửi `sequenceNumber`.
- Manual mutation không nhận start/end toàn ngày, capacity, blocks/day hoặc
  giờ nghỉ; backend suy ra từ timelines.

## 9. Error codes

```json
{
  "error": {
    "code": "MANUAL_TIMELINE_DURATION_MISMATCH",
    "message": "Timeline duration must equal groupDurationMinutes multiplied by groupsPerSlot.",
    "details": {}
  }
}
```

| HTTP | Code | Ý nghĩa |
|---:|---|---|
| `403` | `FORBIDDEN` | Không phải ADMIN/MANAGER. |
| `404` | `TIMEFRAME_NOT_FOUND` | Timeframe không tồn tại hoặc đã archive khi mutation. |
| `409` | `TIMEFRAME_NAME_DUPLICATE` | Trùng tên Timeframe active. |
| `422` | `MANUAL_TIMELINE_REQUIRED` | Không có timeline. |
| `422` | `MANUAL_TIMELINE_INVALID_RANGE` | Timeline có range không hợp lệ. |
| `422` | `MANUAL_TIMELINE_GROUP_COUNT_INVALID` | Số nhóm không dương. |
| `422` | `MANUAL_TIMELINE_MINUTE_ALIGNMENT_REQUIRED` | Giờ manual không khớp tới phút. |
| `422` | `MANUAL_TIMELINE_DURATION_MISMATCH` | Duration không khớp số nhóm × phút/nhóm. |
| `422` | `MANUAL_TIMELINE_OVERLAP` | Hai timeline chồng lấn. |
| `422` | `TIMEFRAME_TIMEZONE_NOT_ALLOWED` | Giờ chứa `Z` hoặc UTC offset. |
| `422` | `TIMEFRAME_INVALID_RANGE` | Cấu hình nhanh có range không hợp lệ. |
| `422` | `TIMEFRAME_NO_BLOCK_FITS` | Cấu hình nhanh không chứa được block. |
| `422` | `GROUP_DURATION_NOT_DIVISIBLE` | Block nhanh không chia hết cho duration nhóm. |
| `422` | `TIMEFRAME_BREAK_OVERLAP` | Các break nhanh chồng lấn. |

Một số lỗi số lượng/range bị Pydantic chặn tại request và vẫn trả HTTP `422`.

## 10. List, detail và archive

```http
GET /api/v1/timeframes
GET /api/v1/timeframes/{timeframeId}
DELETE /api/v1/timeframes/{timeframeId}
```

Detail luôn trả `blocks[]` đầy đủ. Revision manual có `manualTimelines`; revision
tạo nhanh có giá trị `null`.

List chưa phân trang thật:

```json
{
  "data": [],
  "meta": { "page": 1, "pageSize": 0, "total": 0 }
}
```

Archive body:

```json
{ "reason": "Không còn dùng cấu hình này" }
```

Archive chỉ đặt `archivedAt`; lịch sử revision vẫn đọc được. Chưa có restore.

## 11. Luồng FE đề xuất

```text
Manager chọn Tạo nhanh
→ nhập khung giờ/công thức
→ POST /timeframes/preview
→ FE hiển thị blocks bằng timeline editor
→ Manager thêm/xóa/sửa timeline và số nhóm
→ POST /timeframes/manual/preview
→ FE cập nhật capacity, giờ nghỉ và group slots
→ POST /timeframes/manual để lưu dữ liệu cuối cùng
```

```text
Manager chọn Tạo thủ công
→ nhập groupDurationMinutes và từng timeline
→ POST /timeframes/manual/preview
→ POST /timeframes/manual
```

Không gọi manual preview sau từng ký tự. FE nên debounce hoặc chỉ gọi khi các
input thời gian cơ bản đã đủ.

## 12. Tích hợp với Round và scheduler

Round legacy:

```http
POST /api/v1/rounds
```

Body tối thiểu khi dùng Timeframe:

```json
{
  "semester_id": 1,
  "type": "REVIEW_1",
  "reviewer_count": 2,
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "session_duration_minutes": 45,
  "room_types": ["NORMAL"],
  "timeframeId": 12
}
```

Target Round endpoint cũng nhận `timeframeId`, `startDate`, `endDate`:

```http
POST /api/v1/semesters/{semesterId}/rounds
```

Khi `timeframeId` được gửi:

1. Backend lấy version ACTIVE của Timeframe và lưu vào `rounds.timeframe_id`
   cùng `rounds.timeframe_version_id`.
2. Mỗi `groupSlot` trong timeline trở thành một `timeslot` của Round cho từng
   ngày từ `start_date` đến `end_date`.
3. Khoảng nghỉ giữa các timeline không tạo timeslot.
4. `session_duration_minutes` của Round phải bằng `groupDurationMinutes`.
5. Scheduler không cần thay đổi: nó đọc các `timeslots` đã materialize như
   trước đây.

Ví dụ Timeframe có 3 timeline với tổng 7 `groupSlots`, Round dài 3 ngày sẽ có
21 timeslots. Mỗi timeslot đại diện cho một nhóm nối tiếp; đây không phải là
`maxGroupsPerTimeslot`, vốn là giới hạn số nhóm chạy đồng thời của scheduler.

Response Round trả thêm:

```json
{
  "timeframe_id": 12,
  "timeframe_version_id": 21
}
```

Sửa Timeframe global sau đó không làm thay đổi Round đã tạo. PATCH Round có thể
đổi Timeframe hoặc ngày khi Round còn `DRAFT`; backend sẽ tạo lại slots. Nếu đã
có lecturer availability hoặc group preference, việc tạo lại bị từ chối để
không làm mất dữ liệu đăng ký.

Không gửi đồng thời `timeframeId` và `days[].slots[]`; Round chỉ nhận một nguồn
timeline. Nếu không gửi `timeframeId`, flow cũ với `days[].slots[]` vẫn hoạt động.

## 13. Checklist FE

- [ ] Giữ hai lựa chọn `Tạo nhanh` và `Tạo thủ công`.
- [ ] Sau quick preview, cho chỉnh trực tiếp danh sách `blocks`.
- [ ] Chuyển `block.groupSlots.length` thành `groupsPerSlot` khi mở editor.
- [ ] Cho thêm, xóa, đổi giờ và đổi số nhóm của timeline.
- [ ] Cho đổi `groupDurationMinutes` dùng chung.
- [ ] Gọi manual preview để tính ngược; không tự lưu field tính toán.
- [ ] Hiển thị duration mismatch tại timeline tương ứng.
- [ ] Chấp nhận summary có thể là `null` trong manual không đồng đều.
- [ ] PATCH quick và PATCH manual đều là full replacement.
- [ ] Dùng cookie session và CSRF header đúng quy định.
- [ ] Khi tạo Round bằng Timeframe, gửi `timeframeId`, ngày bắt đầu/kết thúc và
  duration nhóm khớp với Timeframe.
- [ ] Không gửi đồng thời `timeframeId` và `days[].slots[]`.
- [ ] Đọc `timeframe_id` và `timeframe_version_id` từ response Round.
- [ ] Không tự sinh timeslot ở FE; backend đã materialize từng `groupSlot`.
- [ ] Không kỳ vọng sửa Timeframe global làm đổi Round đã tạo.
