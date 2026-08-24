# FE Handoff - Manual Scheduling

Backend đã thêm luồng xếp lịch thủ công cho Manager/Admin. Luồng thuật toán cũ
vẫn giữ nguyên ở các endpoint schedule hiện tại; màn hình FE mới có thể dùng nhóm
endpoint `manual-schedule` bên dưới và chưa cần gọi generate algorithm.

## 1. Tóm tắt nghiệp vụ

- Một manual session tương ứng một hội đồng/buổi chấm gồm: một ngày, một
  round timeslot, một phòng, một bộ giảng viên chấm và nhiều nhóm.
- Một timeslot có thể có nhiều manual session ở nhiều phòng khác nhau.
- Hai manual session cùng timeslot không được trùng phòng hoặc trùng giảng viên.
- Một nhóm chỉ được nằm trong một manual session của cùng round.
- `maxGroupsPerTimeslot` đang là giới hạn số hội đồng/session trong một
  timeslot theo H13, không phải số nhóm trong một hội đồng.
- `maxGroupsPerTimeslot: null` nghĩa là không áp dụng giới hạn H13. FE không
  được tự fallback thành `1`.
- Số giảng viên của mỗi hội đồng lấy từ `reviewerCount`.

Role theo `reviewerCount`:

| reviewerCount | roles |
|---:|---|
| `2` | `REVIEWER_1`, `REVIEWER_2` |
| `>= 3` | `CHAIR`, `SECRETARY`, `MEMBER_1...MEMBER_N` |

## 2. Auth

Base URL local:

```text
http://localhost:8000/api/v1
```

Chỉ `ADMIN` và `MANAGER` được gọi các endpoint này. FE dùng cookie session:

```ts
credentials: "include"
```

Các request `POST`, `PATCH`, `DELETE` phải gửi `X-CSRF-Token` bằng cookie
`scheduler_csrf`. Không dùng `Authorization: Bearer` và không dùng
`X-Test-Session` ở app thật.

## 3. Endpoint

| Method | Endpoint | Status | Chức năng |
|---|---|---:|---|
| `GET` | `/rounds/{roundId}/manual-schedule` | `200` | Tải board, config, summary, roles và sessions nháp. |
| `GET` | `/rounds/{roundId}/manual-schedule/options` | `200` | Tải lecturer/group/room options theo context đang chọn. |
| `POST` | `/rounds/{roundId}/manual-schedule/sessions` | `201` | Tạo một manual session. |
| `PATCH` | `/rounds/{roundId}/manual-schedule/sessions/{sessionId}` | `200` | Cập nhật một manual session. |
| `DELETE` | `/rounds/{roundId}/manual-schedule/sessions/{sessionId}?clientRevision=...` | `200` | Xóa một manual session. |
| `POST` | `/rounds/{roundId}/manual-schedule/sessions/bulk-upsert` | `200` | Lưu nhiều session và xóa nhiều session trong một request. |
| `POST` | `/rounds/{roundId}/manual-schedule/validate` | `200` | Validate toàn bộ draft. |
| `GET` | `/rounds/{roundId}/manual-schedule/publish-readiness` | `200` | Checklist trước publish. |
| `POST` | `/rounds/{roundId}/manual-schedule/publish` | `200` | Validate lại và publish lịch thủ công. |

Success response luôn bọc trong envelope:

```json
{
  "data": {}
}
```

Riêng options có thêm:

```json
{
  "data": {},
  "meta": {
    "page": 1,
    "pageSize": 50
  }
}
```

## 4. ID convention

Backend trả `session.id` dạng:

```text
manual_session_123
```

Payload/path vẫn nhận cả ID số legacy và ID có prefix:

| Entity | FE có thể gửi |
|---|---|
| manual session | `manual_session_123` hoặc `123` |
| group | `grp_44` hoặc `44` |
| lecturer | `lec_11` hoặc `11` |
| room | `room_3` hoặc `3` |
| timeslot | `ts_1899` hoặc `1899` |

`roundTimeslotId` trong response hiện trả DB id dạng string, ví dụ `"1899"`.
Khi gửi lên, FE cũng có thể dùng alias `slot_HHMM`, ví dụ `slot_0700`, nhưng
phải gửi kèm `date` để backend resolve đúng ngày.

## 5. GET board

```http
GET /api/v1/rounds/{roundId}/manual-schedule
```

Response chính:

```ts
export type ManualRole =
  | "CHAIR"
  | "SECRETARY"
  | `MEMBER_${number}`
  | "REVIEWER_1"
  | "REVIEWER_2";

export type ManualBlocker = {
  code: string;
  message: string;
  sessionId?: string | null;
  field?: string | null;
  relatedSessionIds?: string[];
  [key: string]: unknown;
};

export type ManualGroup = {
  groupId: string;
  groupCode: string;
  leaderName: string | null;
  activeMemberCount: number;
  supervisorIds: string[];
};

export type ManualRoom = {
  roomId: number;
  roomCode: string;
  roomName: string;
  type: string;
  capacity: number;
};

export type ManualReviewer = {
  lecturerId: string;
  lecturerCode: string;
  lecturerName: string;
  role: ManualRole;
  roleLabel: string;
  order: number;
};

export type ManualSession = {
  id: string;
  date: string; // YYYY-MM-DD
  roundTimeslotId: string;
  startTime: string; // HH:mm, Asia/Ho_Chi_Minh
  endTime: string; // HH:mm, Asia/Ho_Chi_Minh
  status: "DRAFT" | "READY" | "PUBLISHED" | string;
  groups: ManualGroup[];
  room: ManualRoom | null;
  reviewers: ManualReviewer[];
  blockers: ManualBlocker[];
  warnings: ManualBlocker[];
};

export type ManualScheduleBoard = {
  roundId: string;
  roundStatus: string;
  reviewerCount: number;
  maxGroupsPerTimeslot: number | null;
  revision: number;
  roles: Array<{ key: ManualRole; label: string; order: number }>;
  config: {
    roomTypes: string[];
    batchSize: number | null;
    chairMinLevel: number | null;
    secretaryMinLevel: number | null;
    maxSameSupervisorRatio: number | null;
    eligibleProjectStatuses: string[];
  };
  summary: {
    eligibleGroupCount: number;
    scheduledGroupCount: number;
    unscheduledGroupIds: string[];
    incompleteSessionIds: string[];
    sessionCount: number;
    incompleteSessionCount: number;
    blockerCount: number;
    warningCount: number;
  };
  sessions: ManualSession[];
};
```

Ví dụ response rút gọn:

```json
{
  "data": {
    "roundId": "164",
    "roundStatus": "REGISTRATION_CLOSED",
    "reviewerCount": 3,
    "maxGroupsPerTimeslot": null,
    "revision": 0,
    "roles": [
      { "key": "CHAIR", "label": "Chủ tịch", "order": 1 },
      { "key": "SECRETARY", "label": "Thư kí", "order": 2 },
      { "key": "MEMBER_1", "label": "Thành viên 1", "order": 3 }
    ],
    "config": {
      "roomTypes": ["NORMAL"],
      "batchSize": null,
      "chairMinLevel": null,
      "secretaryMinLevel": null,
      "maxSameSupervisorRatio": null,
      "eligibleProjectStatuses": ["ACTIVE"]
    },
    "summary": {
      "eligibleGroupCount": 45,
      "scheduledGroupCount": 0,
      "unscheduledGroupIds": ["grp_1"],
      "incompleteSessionIds": [],
      "sessionCount": 0,
      "incompleteSessionCount": 0,
      "blockerCount": 1,
      "warningCount": 0
    },
    "sessions": []
  }
}
```

## 6. GET options

```http
GET /api/v1/rounds/{roundId}/manual-schedule/options
  ?date=2026-09-04
  &roundTimeslotId=1899
  &sessionId=manual_session_1
  &role=CHAIR
  &groupIds=grp_44&groupIds=grp_61
  &reviewerIds=lec_11&reviewerIds=lec_22
  &roomId=3
  &search=nguyen
  &page=1
  &pageSize=50
```

Query params:

| Param | Bắt buộc | Ghi chú |
|---|---|---|
| `date` | Không | Cần có nếu dùng `slot_HHMM`. |
| `roundTimeslotId` | Không | Nếu có, options được lọc theo timeslot này. |
| `sessionId` | Không | Khi edit, gửi session hiện tại để item đang chọn không tự block chính nó. |
| `role` | Không | Role đang chọn cho dropdown lecturer. |
| `reviewerIds` | Không | Các lecturer đã chọn trong session hiện tại. |
| `groupIds` | Không | Các group đã chọn trong session hiện tại. |
| `roomId` | Không | Room hiện tại khi edit. |
| `search` | Không | Tìm theo mã/tên. |
| `page`, `pageSize` | Không | Mỗi collection bị cap độc lập; `pageSize` tối đa 200. |

Types:

```ts
export type ManualOptionBase = {
  available: boolean;
  blockedCodes: string[];
  blockedReason: string | null;
};

export type ManualLecturerOption = ManualOptionBase & {
  lecturerId: string;
  lecturerCode: string;
  lecturerName: string;
  eligibleRoles: ManualRole[];
};

export type ManualGroupOption = ManualOptionBase & {
  groupId: string;
  groupCode: string;
  supervisorIds: string[];
  selectedByGroup: boolean;
};

export type ManualRoomOption = ManualOptionBase & ManualRoom;

export type ManualScheduleOptions = {
  lecturers: ManualLecturerOption[];
  groups: ManualGroupOption[];
  rooms: ManualRoomOption[];
};
```

FE nên hiển thị option bị chặn ở trạng thái disabled kèm `blockedReason`, thay vì
tự lọc hết. Backend vẫn validate lại khi tạo/sửa/publish.

## 7. Create, update, delete

Create:

```http
POST /api/v1/rounds/{roundId}/manual-schedule/sessions
```

Update:

```http
PATCH /api/v1/rounds/{roundId}/manual-schedule/sessions/{sessionId}
```

Payload:

```ts
export type ManualSessionMutationRequest = {
  date?: string | null;
  roundTimeslotId: string | number;
  groupIds: Array<string | number>;
  roomId?: string | number | null;
  reviewers: Array<{
    lecturerId: string | number;
    role: ManualRole;
    order?: number | null;
  }>;
  clientRevision?: number | null;
};
```

Ví dụ:

```json
{
  "date": "2026-09-04",
  "roundTimeslotId": "1899",
  "groupIds": ["grp_44", "grp_61"],
  "roomId": "room_3",
  "reviewers": [
    { "lecturerId": "lec_11", "role": "CHAIR", "order": 1 },
    { "lecturerId": "lec_22", "role": "SECRETARY", "order": 2 },
    { "lecturerId": "lec_33", "role": "MEMBER_1", "order": 3 }
  ],
  "clientRevision": 0
}
```

Create response `201` và update response `200`:

```ts
export type ManualSessionMutationResponse = {
  data: {
    revision: number;
    session: ManualSession;
  };
};
```

Delete:

```http
DELETE /api/v1/rounds/{roundId}/manual-schedule/sessions/{sessionId}?clientRevision=0
```

Response:

```json
{
  "data": {
    "id": "manual_session_1",
    "deleted": true,
    "revision": 1
  }
}
```

## 8. Bulk upsert

```http
POST /api/v1/rounds/{roundId}/manual-schedule/sessions/bulk-upsert
```

Payload:

```ts
export type ManualBulkUpsertRequest = {
  clientRevision?: number | null;
  allowDraftIncomplete?: boolean;
  deletedSessionIds?: Array<string | number>;
  sessions: Array<Omit<ManualSessionMutationRequest, "clientRevision"> & {
    id?: string | number | null;
  }>;
};
```

Response là full `ManualScheduleBoard` mới nhất:

```ts
export type ManualBulkUpsertResponse = {
  data: ManualScheduleBoard;
};
```

Lưu ý: hiện backend nhận `allowDraftIncomplete` để giữ contract, nhưng publish
vẫn luôn chặn session thiếu group/phòng/reviewer.

## 9. Revision và stale state

`revision` là optimistic lock của draft.

Flow FE nên dùng:

1. Load board, lưu `board.revision`.
2. Mọi `POST`, `PATCH`, `DELETE`, `bulk-upsert`, `validate`, `publish` gửi
   `clientRevision`.
3. Sau mutation thành công, cập nhật revision từ response.
4. Nếu gặp `409 STALE_MANUAL_SCHEDULE_REVISION`, reload board rồi cho user
   quyết định thao tác lại.

Lỗi stale:

```json
{
  "detail": {
    "code": "STALE_MANUAL_SCHEDULE_REVISION",
    "message": "Bản nháp lịch thủ công đã được thay đổi bởi yêu cầu khác.",
    "currentRevision": 3
  }
}
```

Lưu ý: `code` giữ ổn định bằng tiếng Anh để FE xử lý logic; `message`,
`blockedReason`, `blockers[].message` trả tiếng Việt để hiển thị trực tiếp cho
người dùng.

## 10. Validate và publish-readiness

Validate:

```http
POST /api/v1/rounds/{roundId}/manual-schedule/validate
```

Payload:

```json
{
  "clientRevision": 0
}
```

Response:

```ts
export type ManualValidateResponse = {
  data: {
    revision: number;
    valid: boolean;
    blockers: ManualBlocker[];
    warnings: ManualBlocker[];
    summary: ManualScheduleBoard["summary"];
  };
};
```

Publish readiness:

```http
GET /api/v1/rounds/{roundId}/manual-schedule/publish-readiness
```

Response:

```ts
export type ManualPublishReadinessResponse = {
  data: {
    ready: boolean;
    revision: number;
    checks: Array<{
      code:
        | "ALL_GROUPS_SCHEDULED"
        | "ALL_SESSIONS_HAVE_ROOM"
        | "ALL_SESSIONS_HAVE_REVIEWERS"
        | "HARD_CONSTRAINTS"
        | "WARNINGS_CONFIRMED"
        | string;
      passed: boolean;
      count: number;
    }>;
    blockers: ManualBlocker[];
    warnings: ManualBlocker[];
  };
};
```

## 11. Publish

```http
POST /api/v1/rounds/{roundId}/manual-schedule/publish
```

Payload:

```ts
export type ManualPublishRequest = {
  clientRevision?: number | null;
  confirmWarnings?: string[];
  reason?: string | null;
};
```

Ví dụ:

```json
{
  "clientRevision": 4,
  "confirmWarnings": [],
  "reason": "Manager published manual schedule"
}
```

Publish sẽ validate lại trong transaction. Nếu còn blocker, backend trả `422`
với code `PUBLISH_BLOCKED`.

Response thành công:

```ts
export type ManualPublishResponse = {
  data: {
    roundId: string;
    versionId: string;
    status: "PUBLISHED";
    publishedAt: string;
    publishedBy: string | null;
    summary: ManualScheduleBoard["summary"];
  };
};
```

Sau publish, backend tạo dữ liệu official cho luồng cũ:

- `schedule_versions` với `solver_status = "MANUAL"`.
- `sessions`.
- `councils` và `council_members`.
- `schedule_assignments`.
- `schedule_assignment_reviewers`.
- `session_groups` để lưu nhiều group trong cùng một session.

Lưu ý tương thích: `sessions.group_id` vẫn là group đầu tiên của manual session;
FE cần dùng API manual board hoặc bảng `session_groups` nếu muốn hiển thị toàn bộ
group trong một hội đồng sau publish.

## 12. Blocker codes FE nên handle

Các code đang có thể trả về trong `blockers`, `blockedCodes`, hoặc lỗi publish:

```text
SESSION_INCOMPLETE
ROLE_STRUCTURE_INVALID
LECTURER_MULTI_ROLE
GROUP_NOT_ELIGIBLE
SUPERVISOR_REVIEW_CONFLICT
GROUP_DUPLICATED
SESSION_LIMIT_EXCEEDED
ROOM_DOUBLE_BOOKED
LECTURER_DOUBLE_BOOKED
ROOM_NOT_FOUND
ROOM_NOT_ACTIVE
ROOM_TYPE_NOT_ALLOWED
LECTURER_NOT_ACCEPTED
LECTURER_NOT_AVAILABLE
GROUP_SLOT_NOT_SELECTED
LECTURER_CONFLICT_OF_INTEREST
PREVIOUS_REVIEWER_REQUIRED
LECTURER_LOAD_EXCEEDED
UNSCHEDULED_GROUPS
PUBLISH_BLOCKED
STALE_MANUAL_SCHEDULE_REVISION
ROUND_STATUS_INVALID
TIMESLOT_NOT_IN_ROUND
SESSION_NOT_FOUND
```

Gợi ý UI:

- Blocker có `sessionId`: highlight đúng manual session.
- Blocker có `field`: highlight control tương ứng như `groupIds`, `roomId`,
  `reviewers`.
- `UNSCHEDULED_GROUPS`: hiển thị ở summary/global banner.
- `SESSION_LIMIT_EXCEEDED`: highlight timeslot/cell vì quá số session trong cùng
  timeslot.
- `STALE_MANUAL_SCHEDULE_REVISION`: reload board, không retry âm thầm.

## 13. Flow tích hợp FE đề xuất

1. Khi vào màn hình, gọi `GET /manual-schedule`.
2. Render board theo `date`, `roundTimeslotId`, `sessions`.
3. Khi user mở form tạo/sửa session, gọi `GET /manual-schedule/options` với
   context hiện tại.
4. Khi user đổi groups/reviewers/room, gọi lại options nếu cần để cập nhật disabled
   states.
5. Lưu draft bằng `POST`, `PATCH` hoặc `bulk-upsert`, luôn gửi `clientRevision`.
6. Sau mỗi mutation, lấy revision mới từ response.
7. Trước publish, gọi `validate` hoặc `publish-readiness`.
8. Publish bằng `POST /manual-schedule/publish`.

## 14. Giới hạn hiện tại của BE

- H14 về level/skill của `CHAIR` và `SECRETARY` chưa hard-enforce vì schema/config
  nguồn chưa có field rõ ràng. Vì vậy `chairMinLevel`, `secretaryMinLevel`,
  `maxSameSupervisorRatio` đang trả `null`.
- Batch size cho số nhóm trong một hội đồng chưa có config riêng, nên
  `config.batchSize` đang là `null`.
- `confirmWarnings` đã có trong payload publish để giữ contract, nhưng hiện chưa có
  warning nào cần confirm.
- Trong bảng official `council_members`, assignment vẫn lưu `REVIEWER` vì enum cũ
  chưa có `CHAIR`/`SECRETARY`. Role chi tiết của manual schedule nằm ở manual API
  và bảng manual reviewer.

## 15. BE đã verify

- Đã thêm migration `0039_manual_scheduling`.
- Đã chạy migration trong Docker DB bằng `alembic upgrade head`.
- Đã chạy test contract:

```text
pytest tests/test_manual_scheduling_contract.py -q
4 passed
```

- Đã chạy regression subset:

```text
pytest tests/test_manual_scheduling_contract.py tests/test_schedule_operations.py tests/test_health.py -q
8 passed
```

- Smoke test round local hiện tại:

```text
GET /api/v1/rounds/164/manual-schedule -> 200
revision = 0
sessions = []
reviewerCount = 3
maxGroupsPerTimeslot = null
```
