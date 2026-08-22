# FE Handoff — Gán Committee (Hội đồng) vào Round

Tài liệu này **tự chứa**: đủ để tích hợp mà không cần mở thêm file khác. Mọi
response mẫu bên dưới đều là body thật lấy từ backend đang chạy, không phải
ví dụ tự nghĩ.

---

## Phần A — Backend đã làm gì

### A.1. Vấn đề trước đó

`Committee` (Ban Hội Đồng) đã có sẵn dưới dạng **catalog độc lập** — tạo được,
xoá được, nhưng không gắn với Round nào. `Timeframe` thì đã gắn được vào Round
từ trước. Nói cách khác, nửa "gán BHĐ vào round_id" bị thiếu hoàn toàn: không
có cột, không có bảng, không có endpoint nào nối hai thứ lại.

### A.2. Những gì được thêm

| Hạng mục | Nội dung |
|---|---|
| Schema | Bảng nối `round_committees` (many-to-many), migration `0036_round_committees` |
| API | `PUT` / `GET /rounds/{roundId}/committees` |
| Round detail | `GET /rounds/{roundId}` có thêm `committeeCount` |
| Xoá Committee | `DELETE /committees/{id}` trả `409` nếu đang được gán; `bulk-delete` có thêm `inUseIds` |
| Scheduler | Committee được gán là **ràng buộc thật** của thuật toán xếp lịch |
| Readiness | `GET /rounds/{roundId}/scheduling-readiness` có thêm blocker + `unusableCommittees` |

### A.3. Vì sao là many-to-many, không phải `rounds.committee_id`

Committee là catalog **dùng lại được**: một Committee phục vụ nhiều Round khác
nhau qua các kỳ, và một Round cần cả một *pool* Committee để scheduler chọn
chứ không phải đúng một hội đồng. Một cột `committee_id` trên `rounds` sẽ chặn
cả hai chiều đó.

### A.4. Điều quan trọng nhất về scheduler

Khi Round đã gán ít nhất một Committee, scheduler **chỉ xếp lịch bằng nguyên
cả một Committee**. Nó không bao giờ ghép lẻ thành viên của hai Committee khác
nhau thành một hội đồng chấm.

Nghe hiển nhiên, nhưng cách làm ngây thơ sẽ hỏng: nếu chỉ lọc danh sách giảng
viên rồi vẫn để thuật toán tự tổ hợp, thì với Committee A = `(1, 2)`,
Committee B = `(3, 4)` và một khung giờ chỉ có 1 và 3 rảnh, nó sẽ sinh ra hội
đồng `(1, 3)` — một hội đồng không thuộc Committee nào. Backend xử lý bằng
cách kiểm tra nguyên cả member set theo kiểu **all-or-nothing**.

**Ba hệ quả FE phải nắm:**

1. Một thành viên bận ở khung giờ nào thì **cả** Committee đó rớt khỏi khung
   giờ đó — không có chuyện thay người khác vào chỗ trống. Committee vẫn dùng
   được ở các khung giờ mà mọi thành viên đều rảnh.
2. Một Committee chỉ dùng được khi **mọi** thành viên đã `ACCEPTED` lời mời
   của Round (hoặc, với Round chưa có ai accept, đã submit availability).
   Thiếu một người là cả Committee bị loại khỏi lần chạy đó.
3. Nếu Round có Committee được gán nhưng **không** Committee nào đủ điều kiện,
   scheduler trả về không lịch — nó **không** quay về chế độ tự ghép giảng viên
   tự do. Đây là chủ ý: gán Committee không bao giờ được trở thành đường vòng
   lách qua bước mời/xác nhận.

Chính vì hệ quả (2) và (3) mà `scheduling-readiness` phải có blocker riêng —
nếu không, manager chỉ thấy kết quả toàn `UNSCHEDULED` mà không biết lý do.

### A.5. Gán Committee **không** thay thế gán Timeframe

Round resolve **hai** thứ độc lập nhau:

- **Timeframe** — khung giờ, gán qua `PATCH /rounds/{roundId}` với `timeframeId`.
- **Committee** — hội đồng chấm, gán qua `PUT /rounds/{roundId}/committees`.

Hai lời gọi API riêng biệt, không gộp payload. Nhưng dùng **chung một điều
kiện khoá**: cả hai chỉ sửa được khi Round ở `DRAFT` hoặc `OPEN_REGISTRATION`
— nên FE disable cả hai bằng cùng một biến.

---

## Phần B — API Contract

### B.1. Authentication

Base URL local: `http://localhost:8000/api/v1`

Cookie session (`credentials: "include"`). Request mutating phải gửi header
`X-CSRF-Token` lấy từ cookie `scheduler_csrf`. Không dùng Bearer token.

Chỉ **ADMIN** và **MANAGER** gọi được các endpoint dưới đây; role khác nhận
`403 FORBIDDEN`.

### B.2. ⚠️ Kiểu của id — đọc kỹ chỗ này

Đây là chỗ dễ sai nhất, và nó **không nhất quán** giữa các endpoint:

| Chỗ | Kiểu thực tế | Ví dụ |
|---|---|---|
| `committeeIds` trong request body | `string \| number` — backend nhận **cả hai** | `307` hoặc `"cmt_307"` |
| `Committee.id` trong response | **`number`** | `307` |
| `CommitteeMember.lecturerId` trong response | **`number`** | `1` |
| `missingLecturerIds` trong readiness | **`number[]`** | `[1, 2]` |
| `roundId` trên URL | `number` | `/rounds/163/committees` |
| `id` trong `GET /rounds/{id}` response | **`string`** | `"163"` |
| `id` trong `scheduling-readiness` response | **`number`** | `163` |

> **Lưu ý:** `docs/api/committee-fe-handoff.md` mô tả `Committee.id` là
> `string` dạng `"cmt_123"` và `lecturerId` là `"lec_123"`. Điều đó **không
> đúng với response thật** — backend trả về số nguyên. Nếu FE đang parse theo
> mô tả cũ thì phải sửa. Bảng trên là kết quả dump từ API đang chạy.

Khuyến nghị: **luôn dùng `Number(...)`** khi so sánh id, và gửi id dạng số
nguyên thuần trong request cho đơn giản.

### B.3. `PUT /rounds/{roundId}/committees` — thay toàn bộ

Không có `PATCH`. Muốn sửa thì gửi lại **toàn bộ** tập mong muốn.

```http
PUT /api/v1/rounds/163/committees
Content-Type: application/json
X-CSRF-Token: <giá trị cookie scheduler_csrf>

{ "committeeIds": [307, 309] }
```

Gửi mảng rỗng để gỡ hết Committee khỏi Round:

```json
{ "committeeIds": [] }
```

Giới hạn: tối đa 200 phần tử.

**Response `200`** (giống hệt response của `GET`):

```json
{
  "data": [
    {
      "id": 307,
      "code": "DOC-01",
      "memberCount": 2,
      "createdBy": 2,
      "createdAt": "2026-08-22T08:31:51.771473Z",
      "members": [
        {
          "lecturerId": 1,
          "lecturerCode": "GV-PHUONG-LHK",
          "displayName": "Lâm Hữu Khánh Phương",
          "role": "REVIEWER",
          "sequenceNumber": 1,
          "roleLabel": "Reviewer 1"
        },
        {
          "lecturerId": 2,
          "lecturerCode": "GV-DUC-DNM",
          "displayName": "Đặng Ngọc Minh Đức",
          "role": "REVIEWER",
          "sequenceNumber": 2,
          "roleLabel": "Reviewer 2"
        }
      ]
    }
  ],
  "meta": { "page": 1, "pageSize": 1, "total": 1 }
}
```

### B.4. `GET /rounds/{roundId}/committees`

Không có body. Response giống hệt `PUT` ở trên. Round không có Committee nào
thì `data` là `[]`.

### B.5. Error codes

| HTTP | Code | Khi nào | FE nên làm gì |
|---:|---|---|---|
| 403 | `FORBIDDEN` | Không phải ADMIN/MANAGER | Ẩn UI ngay từ đầu |
| 404 | `ROUND_NOT_FOUND` | `roundId` không tồn tại | Điều hướng về danh sách Round |
| 404 | `COMMITTEE_NOT_FOUND` | Có `committeeId` không tồn tại | Refetch `GET /committees` |
| 409 | `ROUND_CONFIG_LOCKED` | Round đã qua `DRAFT`/`OPEN_REGISTRATION` | Refetch Round, disable UI |
| 409 | `COMMITTEE_IN_USE` | Xoá Committee đang gán vào Round nào đó | Báo "gỡ khỏi Round trước" |
| 422 | `ROUND_COMMITTEE_SIZE_MISMATCH` | `memberCount` ≠ `reviewerCount` | Đáng lẽ FE đã chặn trước |
| 422 | `ROUND_COMMITTEE_DUPLICATE_ID` | Cùng `committeeId` lặp trong một payload | Dedupe phía client |

Body lỗi theo envelope chuẩn:

```json
{
  "error": {
    "code": "ROUND_COMMITTEE_DUPLICATE_ID",
    "message": "The same committee cannot be assigned twice to one round.",
    "details": {}
  }
}
```

### B.6. Quy tắc validate — FE nên chặn trước khi gọi API

**1. Số thành viên phải khớp `reviewerCount` của Round:**

| Round type | `reviewerCount` | Committee cần |
|---|---:|---:|
| `REVIEW_1`, `REVIEW_2` | 2 | 2 người |
| `REVIEW_3` | 3 | 3 người |
| `DEFENSE_1`, `DEFENSE_2` | 5 | 5 người |

FE nên lọc sẵn danh sách Committee theo `reviewerCount` của Round đang mở, để
user không chọn được cái sai size ngay từ đầu.

**2. Round phải đang ở `DRAFT` hoặc `OPEN_REGISTRATION`.**

**3. Không lặp `committeeId` trong cùng một payload.**

### B.7. Endpoint sẵn có bị thay đổi

#### `GET /rounds/{roundId}` — thêm `committeeCount`

```json
{
  "data": {
    "id": "163",
    "semesterId": "1",
    "name": "Doc Dump Round",
    "type": "REVIEW_1",
    "status": "DRAFT",
    "durationMinutes": 60,
    "reviewerCount": 2,
    "groupSelectionMode": false,
    "resultOwnerMode": false,
    "roomTypes": [],
    "committeeCount": 1,
    "days": [],
    "registrationPhase": "INACTIVE"
  }
}
```

Dùng để hiển thị nhanh trạng thái mà không phải gọi thêm endpoint danh sách.
Round chưa gán gì thì `committeeCount: 0`.

> Các field `null` bị loại khỏi response (`exclude_none`), nên `timeframeId`
> chỉ xuất hiện khi Round thực sự có Timeframe. FE phải coi mọi field optional
> là có thể vắng mặt, không chỉ là `null`.

#### `DELETE /committees/{committeeId}` — có thể trả `409`

```json
{
  "error": {
    "code": "COMMITTEE_IN_USE",
    "message": "Committee is assigned to a Round and cannot be deleted.",
    "details": {}
  }
}
```

Gỡ khỏi Round trước rồi mới xoá được.

#### `POST /committees/bulk-delete` — thêm `inUseIds`

Không fail cả batch nữa. Nó xoá những cái xoá được và báo lại phần bị chặn:

```json
{
  "data": {
    "deleted": 0,
    "deletedIds": [],
    "inUseIds": [307]
  }
}
```

FE nên hiển thị `inUseIds` như **cảnh báo** ("các hội đồng này đang được dùng,
chưa xoá được"), không coi cả request là thất bại — HTTP status vẫn là `200`.

#### `GET /rounds/{roundId}/scheduling-readiness` — thêm blocker

```json
{
  "data": {
    "ready": false,
    "blockers": ["NO_GROUPS", "NO_TIMESLOTS", "COMMITTEE_MEMBERS_NOT_ELIGIBLE"],
    "unusableCommittees": [
      { "committeeId": 307, "code": "DOC-01", "missingLecturerIds": [1, 2] }
    ],
    "id": 163,
    "status": "DRAFT",
    "groups": 0,
    "timeslots": 0,
    "acceptedInvitations": 0
  }
}
```

`blockers` là mảng, có thể chứa nhiều mã cùng lúc. `unusableCommittees` là `[]`
khi không có vấn đề gì.

---

## Phần C — Hướng dẫn tích hợp

### C.1. TypeScript types (copy nguyên vào FE)

```ts
// ---- Committee ----

export type CommitteeRole = "REVIEWER" | "CHAIR" | "SECRETARY" | "MEMBER";

export type CommitteeMember = {
  lecturerId: number;
  lecturerCode: string | null;
  displayName: string | null;
  role: CommitteeRole;
  sequenceNumber: number;
  /** "Reviewer 1" | "Chủ tịch" | "Thư ký" | "Thành viên 1"... — luôn hiển thị
   *  giá trị này, không tự suy ra role ở FE. */
  roleLabel: string;
};

export type Committee = {
  id: number;
  code: string;
  memberCount: number;
  createdBy: number | null;
  createdAt: string;
  members: CommitteeMember[];
};

// ---- Round ↔ Committee ----

export type RoundCommitteeReplaceRequest = {
  committeeIds: number[];
};

export type ApiListEnvelope<T> = {
  data: T[];
  meta: { page: number; pageSize: number; total: number };
};

export type RoundCommitteeListResponse = ApiListEnvelope<Committee>;

// ---- Readiness ----

export type UnusableCommittee = {
  committeeId: number;
  code: string;
  missingLecturerIds: number[];
};

export type SchedulingReadiness = {
  ready: boolean;
  blockers: string[];
  unusableCommittees: UnusableCommittee[];
  id: number;
  status: string;
  groups: number;
  timeslots: number;
  acceptedInvitations: number;
};

// ---- Error ----

export type ApiError = {
  error: { code: string; message: string; details: Record<string, unknown> };
};
```

### C.2. API client

```ts
const BASE = "/api/v1";

function csrfToken(): string {
  return (
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("scheduler_csrf="))
      ?.split("=")[1] ?? ""
  );
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.method && init.method !== "GET"
        ? { "X-CSRF-Token": csrfToken() }
        : {}),
      ...init?.headers,
    },
  });

  const body = await response.json();
  if (!response.ok) {
    throw Object.assign(new Error(body?.error?.message ?? "Request failed"), {
      code: body?.error?.code as string | undefined,
      status: response.status,
    });
  }
  return body as T;
}

export const roundCommitteeApi = {
  list: (roundId: number) =>
    request<RoundCommitteeListResponse>(`/rounds/${roundId}/committees`),

  replace: (roundId: number, committeeIds: number[]) =>
    request<RoundCommitteeListResponse>(`/rounds/${roundId}/committees`, {
      method: "PUT",
      body: JSON.stringify({ committeeIds }),
    }),

  readiness: (roundId: number) =>
    request<{ data: SchedulingReadiness }>(
      `/rounds/${roundId}/scheduling-readiness`,
    ),
};
```

### C.3. Điều kiện khoá UI — dùng chung với Timeframe

```ts
const ROUND_CONFIG_EDITABLE = new Set(["DRAFT", "OPEN_REGISTRATION"]);

export function canEditRoundConfig(round: { status: string }): boolean {
  return ROUND_CONFIG_EDITABLE.has(round.status);
}
```

Dùng đúng một hàm này để disable **cả** picker Timeframe **và** picker
Committee. Nếu chỉ disable một cái, user sẽ gặp `409 ROUND_CONFIG_LOCKED` giữa
chừng.

### C.4. Lọc Committee theo size

```ts
export function selectableCommittees(
  all: Committee[],
  round: { reviewerCount: number },
): Committee[] {
  return all.filter((c) => c.memberCount === round.reviewerCount);
}
```

Nếu kết quả rỗng, hiển thị empty state có hành động rõ ràng — ví dụ
"Chưa có hội đồng nào đủ {reviewerCount} thành viên. Tạo hội đồng mới" — thay
vì một dropdown trống không giải thích gì.

### C.5. Hook React Query mẫu

```ts
export function useRoundCommittees(roundId: number) {
  return useQuery({
    queryKey: ["round-committees", roundId],
    queryFn: () => roundCommitteeApi.list(roundId),
    select: (response) => response.data,
  });
}

export function useReplaceRoundCommittees(roundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (committeeIds: number[]) => {
      // Backend trả 422 nếu trùng; dedupe trước cho gọn.
      const unique = [...new Set(committeeIds)];
      return roundCommitteeApi.replace(roundId, unique);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["round-committees", roundId] });
      // committeeCount nằm trong round detail nên phải invalidate luôn.
      queryClient.invalidateQueries({ queryKey: ["round", roundId] });
      queryClient.invalidateQueries({
        queryKey: ["scheduling-readiness", roundId],
      });
    },
  });
}
```

### C.6. Xử lý lỗi

```ts
const MESSAGES: Record<string, string> = {
  ROUND_CONFIG_LOCKED:
    "Round đã qua giai đoạn cấu hình, không thay đổi hội đồng được nữa.",
  COMMITTEE_NOT_FOUND:
    "Một hội đồng đã bị xoá bởi người khác. Vui lòng tải lại danh sách.",
  ROUND_COMMITTEE_SIZE_MISMATCH:
    "Số thành viên hội đồng không khớp với số reviewer của Round.",
  ROUND_COMMITTEE_DUPLICATE_ID: "Một hội đồng bị chọn trùng hai lần.",
  COMMITTEE_IN_USE:
    "Hội đồng đang được gán vào Round. Gỡ khỏi Round trước khi xoá.",
};
```

Với `ROUND_CONFIG_LOCKED` và `COMMITTEE_NOT_FOUND`, **refetch rồi mới hiện
thông báo** — cả hai đều nghĩa là state trên màn hình đã cũ.

### C.7. Chặn trước khi chạy scheduler

```tsx
function RunSchedulerButton({ roundId }: { roundId: number }) {
  const { data: readiness } = useQuery({
    queryKey: ["scheduling-readiness", roundId],
    queryFn: () => roundCommitteeApi.readiness(roundId),
    select: (response) => response.data,
  });

  if (!readiness) return null;

  const committeeIssue = readiness.blockers.includes(
    "COMMITTEE_MEMBERS_NOT_ELIGIBLE",
  );

  return (
    <>
      {committeeIssue && (
        <Alert severity="warning">
          <p>Các hội đồng sau chưa dùng được vì còn thành viên chưa nhận lời mời:</p>
          <ul>
            {readiness.unusableCommittees.map((item) => (
              <li key={item.committeeId}>
                {item.code} — còn {item.missingLecturerIds.length} thành viên
              </li>
            ))}
          </ul>
        </Alert>
      )}
      <Button disabled={!readiness.ready} onClick={runScheduler}>
        Chạy scheduler
      </Button>
    </>
  );
}
```

Không bỏ qua bước này. Nếu bỏ, manager chạy scheduler xong nhận về một danh
sách toàn `UNSCHEDULED` mà không có bất kỳ manh mối nào về lý do — trong khi
lý do thật chỉ là "hội đồng chưa được mời đủ".

### C.8. Luồng màn hình đề xuất

```
Màn hình cấu hình Round
├─ GET /rounds/{id}                    → reviewerCount, status, committeeCount
├─ GET /committees                     → lọc theo memberCount === reviewerCount
├─ GET /rounds/{id}/committees         → tick sẵn cái đã gán
│
├─ [user chọn / bỏ chọn]
│  └─ PUT /rounds/{id}/committees      → gửi TOÀN BỘ tập mới, không gửi diff
│     └─ invalidate: round detail + round committees + readiness
│
└─ [trước khi bấm chạy scheduler]
   └─ GET /rounds/{id}/scheduling-readiness
      └─ nếu có COMMITTEE_MEMBERS_NOT_ELIGIBLE → cảnh báo, disable nút
```

### C.9. Checklist

- [ ] Đổi `Committee.id` và `lecturerId` sang `number` (nếu FE đang để `string`).
- [ ] Lọc Committee theo `reviewerCount` của Round trước khi cho chọn.
- [ ] Disable UI gán Committee khi Round không ở `DRAFT`/`OPEN_REGISTRATION`,
      dùng **chung** điều kiện với Timeframe.
- [ ] Gửi `PUT` với toàn bộ tập, không gửi diff.
- [ ] Dedupe `committeeId` phía client.
- [ ] Invalidate cả round detail (vì `committeeCount`) sau khi `PUT` thành công.
- [ ] Xử lý `409 COMMITTEE_IN_USE` ở màn hình quản lý Committee.
- [ ] Đọc `inUseIds` trong bulk-delete và hiển thị dạng cảnh báo, không phải lỗi.
- [ ] Hiển thị `committeeCount` trong Round detail.
- [ ] Gọi `scheduling-readiness` trước khi chạy scheduler, hiển thị
      `unusableCommittees`.
- [ ] Giải thích cho user rằng gán Committee **không** tự mời thành viên vào
      Round — đó vẫn là thao tác riêng.

---

## Phần D — Điểm cần biết trước khi hỏi thêm

**Gán Committee không tự động mời thành viên vào Round.** Manager vẫn phải mời
lecturer và chờ họ `ACCEPTED` như bình thường. Backend cố tình không tự mời:
làm vậy sẽ biến việc gán Committee thành đường vòng lách qua bước xác nhận của
giảng viên. Đây là quyết định sản phẩm, không phải thiếu sót kỹ thuật — nếu
muốn đổi thì phải bàn lại.

**Một Committee bị "rớt" là im lặng ở phía scheduler.** Không có event, không
có notification. `scheduling-readiness` là **kênh duy nhất** để biết chuyện đó
sắp xảy ra.

**Không có endpoint "thêm/bớt một Committee".** Chỉ có replace-all. Nếu UI cần
thao tác từng cái thì FE tự đọc tập hiện tại, sửa trong state, rồi gửi lại
toàn bộ.
