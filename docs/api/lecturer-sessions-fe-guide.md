# FE Guide — Lecturer Sessions

Tài liệu handoff cho màn hình lịch/session của Lecturer.

## 1. Endpoint

```http
GET /api/v1/lecturer/me/sessions
```

Local:

```text
http://localhost:8000/api/v1/lecturer/me/sessions
```

Endpoint chỉ dành cho account có role `LECTURER`. Backend tự xác định lecturer hiện tại từ session đăng nhập, vì vậy FE không truyền `lecturerId`.

## 2. Authentication

Đây là request `GET`, không cần CSRF header. FE vẫn phải gửi cookie session:

```ts
const response = await fetch(`${API_URL}/api/v1/lecturer/me/sessions`, {
  method: "GET",
  credentials: "include",
  headers: {
    Accept: "application/json",
  },
});
```

`API_URL` ở local là `http://localhost:8000`.

FE thật phải login trước bằng `POST /api/v1/auth/login` và dùng `credentials: "include"`. Không dùng `Authorization: Bearer` và không dùng `X-Test-Session` trong môi trường thật.

## 3. Response thành công

HTTP `200`:

```json
{
  "data": [
    {
      "id": 2,
      "roundId": 1,
      "startAt": "2026-08-22T01:00:00Z",
      "endAt": "2026-08-22T02:00:00Z",
      "status": "SCHEDULED",
      "groupId": 2,
      "groupCode": "DEMO-G02",
      "projectCode": "DEMO-P02",
      "roomCode": "N02",
      "roundType": "REVIEW_1"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 1,
    "total": 1
  }
}
```

Không có session thì `data` là mảng rỗng:

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 0,
    "total": 0
  }
}
```

## 4. TypeScript types

```ts
export type LecturerSession = {
  id: number;
  roundId: number;
  startAt: string; // ISO-8601 datetime
  endAt: string; // ISO-8601 datetime
  status: string;
  groupId: number;
  groupCode: string;
  projectCode: string;
  roomCode: string | null;
  roundType: "REVIEW_1" | "REVIEW_2" | "DEFENSE_1_1" | "DEFENSE_1_2" | "DEFENSE_2" | string;
};

export type LecturerSessionsResponse = {
  data: LecturerSession[];
  meta: {
    page: number;
    pageSize: number;
    total: number;
  };
};
```

## 5. Field mapping cho UI

| API field | Dùng trên UI | Lưu ý |
|---|---|---|
| `id` | ID session, key của row/card | Không dùng `groupId` làm key thay thế. |
| `roundId` | Link/filter theo round | Là số nguyên. |
| `startAt` | Ngày và giờ bắt đầu | Chuỗi ISO-8601; parse bằng `new Date()`. |
| `endAt` | Giờ kết thúc | Chuỗi ISO-8601. |
| `status` | Badge trạng thái | Backend trả raw status dạng string. |
| `groupId` | Link tới group | Là số nguyên. |
| `groupCode` | Tên/mã group | Ví dụ `DEMO-G02`. |
| `projectCode` | Mã project | Ví dụ `DEMO-P02`. |
| `roomCode` | Phòng | Có thể `null`; hiển thị `Chưa xếp phòng`. |
| `roundType` | Tên loại kỳ đánh giá | Ví dụ `REVIEW_1`. |

Ví dụ format thời gian:

```ts
const start = new Date(session.startAt);
const end = new Date(session.endAt);

const timeLabel = `${start.toLocaleString("vi-VN")} - ${end.toLocaleTimeString("vi-VN", {
  hour: "2-digit",
  minute: "2-digit",
})}`;
```

## 6. Scope dữ liệu

Backend chỉ trả các session mà lecturer hiện tại là thành viên của council/session đó. FE không cần tự lọc theo lecturer.

Kết quả được sắp xếp tăng dần theo `startAt`, sau đó theo `id`.

Nếu một session chưa có phòng, session vẫn được trả về nhưng `roomCode` là `null`.

## 7. Xử lý trạng thái request

```ts
async function getLecturerSessions(): Promise<LecturerSessionsResponse> {
  const response = await fetch(`${API_URL}/api/v1/lecturer/me/sessions`, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (response.status === 401) {
    throw new Error("SESSION_EXPIRED");
  }

  if (response.status === 403) {
    throw new Error("LECTURER_SCOPE_REQUIRED");
  }

  if (!response.ok) {
    throw new Error(`LECTURER_SESSIONS_REQUEST_FAILED_${response.status}`);
  }

  return response.json() as Promise<LecturerSessionsResponse>;
}
```

UI nên có các state:

- `loading`: đang tải danh sách.
- `success + data.length > 0`: hiển thị danh sách/calendar.
- `success + data.length === 0`: hiển thị empty state, ví dụ `Chưa có session được phân công`.
- `401`: xóa auth state và chuyển về màn hình login; backend hiện không có refresh token.
- `403`: hiển thị `Tài khoản không có quyền Lecturer`.
- network/`5xx`: hiển thị lỗi tải dữ liệu và nút retry.

## 8. Giới hạn hiện tại của API

`meta` có format phân trang nhưng endpoint hiện chưa hỗ trợ phân trang thật:

- Không nhận query `page` hoặc `pageSize`.
- Không có `LIMIT/OFFSET` trong query.
- Luôn trả toàn bộ session thuộc scope của lecturer.
- `meta.page` luôn là `1`.
- `meta.pageSize` bằng số item thực tế trả về.
- `meta.total` bằng số item thực tế trả về.

Vì vậy FE hiện không cần dựng pagination control cho endpoint này. Nếu số lượng session tăng lớn, backend cần bổ sung pagination trước khi FE dùng `meta` để chia trang.

Ngoài ra, response hiện không trả reviewer/council member details. FE chỉ có thông tin session, group, project, phòng, thời gian và round type.

## 9. Checklist tích hợp FE

- [ ] Gọi API sau khi hydrate current user và xác nhận role là `LECTURER`.
- [ ] Dùng `credentials: "include"`.
- [ ] Không truyền `lecturerId` trên URL.
- [ ] Hiển thị `roomCode ?? "Chưa xếp phòng"`.
- [ ] Parse `startAt`/`endAt` theo timezone thay vì cắt chuỗi thủ công.
- [ ] Có loading, empty, `401`, `403`, network error và retry state.
- [ ] Không thêm pagination UI dựa trên `meta` ở phiên bản API hiện tại.

## 10. Flow trước khi có Lecturer Session

Session chỉ xuất hiện sau khi round được chạy scheduler. Flow chuẩn của màn hình
Lecturer là:

```text
Manager gửi invitation
→ Lecturer xem invitation
→ Lecturer accept invitation
→ Lecturer chọn availability
→ Group Leader chọn timeslot cho group
→ Manager chạy scheduler
→ Lecturer xem session tại GET /lecturer/me/sessions
```

Lecturer phải accept invitation trước khi submit availability. Nếu chưa accept,
backend từ chối request chọn availability.

### 10.1 Xem invitation

```http
GET /api/v1/lecturer/me/invitations
```

Backend tự lấy Lecturer từ session hiện tại. FE không truyền `lecturerId`.

### 10.2 Accept hoặc decline invitation

```http
POST /api/v1/rounds/{roundId}/invitations/me/respond
Content-Type: application/json
```

Accept:

```json
{
  "decision": "ACCEPTED"
}
```

Decline:

```json
{
  "decision": "DECLINED",
  "reason": "Không thể tham gia round này"
}
```

Chỉ sau response `ACCEPTED` FE mới nên mở form availability.

### 10.3 Lecturer chọn availability

```http
PUT /api/v1/rounds/{roundId}/availability/me
Content-Type: application/json
```

```json
{
  "preferredLoad": "MEDIUM",
  "slots": [
    { "timeslotId": 101, "available": true },
    { "timeslotId": 102, "available": false }
  ]
}
```

Request này chỉ dành cho role `LECTURER` và chỉ hợp lệ sau khi invitation đã ở
trạng thái `ACCEPTED`.

### 10.4 Student/Group Leader chọn slot cho group

Đây không phải availability cá nhân của Student. Active Group Leader chọn slot
phù hợp cho toàn group:

```http
PUT /api/v1/rounds/{roundId}/groups/{groupId}/preferences
Content-Type: application/json
```

```json
{
  "timeslotIds": [101, 103]
}
```

Chỉ active Group Leader được sửa preference của group. Khi
`groupSelectionMode = true`, scheduler chỉ chọn slot nằm trong preference của
group đó.

### 10.5 Scheduler dùng dữ liệu của hai phía

Một candidate chỉ hợp lệ khi đồng thời thỏa:

```text
group selected slot
∩
accepted Lecturer availability
```

Sau khi scheduler tạo và publish schedule, Lecturer mới đọc lịch chính thức từ
`GET /api/v1/lecturer/me/sessions`.

FE nên xử lý các trạng thái chính:

- `PENDING`: hiển thị nút Accept/Decline, chưa hiển thị form availability.
- `ACCEPTED`: hiển thị form availability.
- `DECLINED` hoặc `EXPIRED`: khóa form availability.
- Availability submit trước khi accept: hiển thị lỗi và yêu cầu accept invitation.
