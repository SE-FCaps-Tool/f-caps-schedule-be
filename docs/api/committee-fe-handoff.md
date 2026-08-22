# FE Handoff — Committee (Hội đồng) Catalog

Committee là danh mục các nhóm giảng viên được tạo trước, dùng để add vào
Round sau này. Committee **chưa** gắn Round/thời gian — vì vậy một lecturer
được phép xuất hiện trong nhiều committee cùng lúc, và việc trùng lịch thật
sự chỉ được kiểm tra sau này khi committee được add vào Round.

Đây **không phải** là bảng `councils` hiện có (hội đồng chấm điểm thật, tự
sinh theo session, không thể sửa/xoá). Committee là bản nháp/catalog, có thể
tạo và xoá tự do.

Tính năng đợt này: **CRUD + bulk-create**. Không có auto-matching — người
dùng tự chọn từng thành viên của từng nhóm; backend chỉ validate và gắn
role/label theo số lượng thành viên.

## 1. Khái niệm

- `code`: mã hội đồng, tối đa 32 ký tự, viết hoa tự động, unique.
- `memberIds`: danh sách lecturer theo đúng thứ tự người dùng chọn — **thứ
  tự quyết định role**.
- Quy tắc gán role theo số lượng thành viên:

| Số thành viên | Role theo vị trí |
|---|---|
| 1–3 | Tất cả `REVIEWER`, label "Reviewer 1", "Reviewer 2", "Reviewer 3" |
| 4–15 | Vị trí 1 = `CHAIR` ("Chủ tịch"), vị trí 2 = `SECRETARY` ("Thư ký"), vị trí 3..N = `MEMBER` ("Thành viên 1", "Thành viên 2", ...) |

```text
memberIds = [A, B, C]           → A: Reviewer 1, B: Reviewer 2, C: Reviewer 3
memberIds = [A, B, C, D, E]     → A: Chủ tịch, B: Thư ký, C: Thành viên 1, D: Thành viên 2, E: Thành viên 3
```

FE **không tự tính role** — luôn hiển thị theo `role`/`roleLabel` trả về từ
API, kể cả ở bước preview.

## 2. Authentication

Base URL local:

```text
http://localhost:8000/api/v1
```

Chỉ role `ADMIN` hoặc `MANAGER` được gọi API. Dùng cookie session:

```ts
credentials: "include"
```

Các request `POST`, `DELETE` phải gửi `X-CSRF-Token` bằng cookie
`scheduler_csrf`. Không dùng Bearer token.

## 3. Danh sách endpoint

| Method | Endpoint | Thành công | Chức năng |
|---|---|---:|---|
| `POST` | `/committees/preview` | `200` | Validate + gán role cho nhiều nhóm cùng lúc, không ghi DB. |
| `POST` | `/committees` | `201` | Tạo hàng loạt — partial success, nhóm lỗi không chặn nhóm hợp lệ. |
| `GET` | `/committees` | `200` | Danh sách committee. |
| `GET` | `/committees?lecturerId={lecturerId}` | `200` | Lọc committee có chứa 1 lecturer cụ thể. |
| `GET` | `/committees/{committeeId}` | `200` | Chi tiết 1 committee kèm danh sách thành viên. |
| `DELETE` | `/committees/{committeeId}` | `200` | Xoá cứng 1 committee (cascade members). |
| `POST` | `/committees/bulk-delete` | `200` | Xoá nhiều committee cùng lúc. |

Không có `PATCH`. Sửa committee = xoá rồi tạo lại.

## 4. TypeScript types

```ts
export type CommitteeGroupInput = {
  code: string;
  memberIds: string[]; // lecturer external id, dạng "lec_123"
};

export type CommitteeBatchRequest = {
  groups: CommitteeGroupInput[];
};

export type CommitteeRole = "REVIEWER" | "CHAIR" | "SECRETARY" | "MEMBER";

export type CommitteeMember = {
  lecturerId: string;
  lecturerCode: string | null;
  displayName: string | null;
  role: CommitteeRole;
  sequenceNumber: number;
  roleLabel: string; // "Reviewer 2", "Chủ tịch", "Thư ký", "Thành viên 1"...
};

export type CommitteePreviewGroupError = {
  code: string;
  message: string;
};

export type CommitteePreviewGroup = {
  code: string;
  memberCount: number;
  ok: boolean;
  members: CommitteeMember[];
  errors: CommitteePreviewGroupError[];
};

export type CommitteePreviewResponse = {
  groups: CommitteePreviewGroup[];
};

export type Committee = {
  id: string; // "cmt_123"
  code: string;
  memberCount: number;
  createdBy: string | null;
  createdAt: string;
  members: CommitteeMember[];
};

export type CommitteeBulkCreateResponse = {
  created: number;
  skipped: number;
  errors: Array<{ index: number; code: string; message: string }>;
  committees: Committee[];
};
```

## 5. Preview — validate trước khi tạo

```http
POST /api/v1/committees/preview
Content-Type: application/json
```

```json
{
  "groups": [
    { "code": "HD-REV-01", "memberIds": ["lec_11", "lec_12", "lec_13"] },
    { "code": "HD-REV-01", "memberIds": ["lec_14", "lec_14"] }
  ]
}
```

Response `200` — trả kết quả cho **từng nhóm theo đúng thứ tự gửi lên**, kể
cả nhóm lỗi:

```json
{
  "data": {
    "groups": [
      {
        "code": "HD-REV-01",
        "memberCount": 3,
        "ok": true,
        "members": [
          { "lecturerId": "lec_11", "lecturerCode": "GV01", "displayName": "Nguyễn Văn A", "role": "REVIEWER", "sequenceNumber": 1, "roleLabel": "Reviewer 1" },
          { "lecturerId": "lec_12", "lecturerCode": "GV02", "displayName": "Trần Thị B", "role": "REVIEWER", "sequenceNumber": 2, "roleLabel": "Reviewer 2" },
          { "lecturerId": "lec_13", "lecturerCode": "GV03", "displayName": "Lê Văn C", "role": "REVIEWER", "sequenceNumber": 3, "roleLabel": "Reviewer 3" }
        ],
        "errors": []
      },
      {
        "code": "HD-REV-01",
        "memberCount": 2,
        "ok": false,
        "members": [
          { "lecturerId": "lec_14", "lecturerCode": "GV04", "displayName": "Phạm Thị D", "role": "REVIEWER", "sequenceNumber": 1, "roleLabel": "Reviewer 1" },
          { "lecturerId": "lec_14", "lecturerCode": "GV04", "displayName": "Phạm Thị D", "role": "REVIEWER", "sequenceNumber": 2, "roleLabel": "Reviewer 2" }
        ],
        "errors": [
          { "code": "COMMITTEE_MEMBER_DUPLICATE", "message": "A lecturer cannot appear twice in one committee." },
          { "code": "COMMITTEE_CODE_DUPLICATE", "message": "This code is used by another group in the same batch." }
        ]
      }
    ]
  }
}
```

Ở ví dụ trên `members` của nhóm lỗi vẫn được trả về (để FE hiển thị label dự
kiến), nhưng `ok: false` — FE phải chặn nút "Tạo" cho tới khi user sửa xong
tất cả nhóm lỗi trong batch, hoặc chỉ gửi lại các nhóm `ok: true` khi tạo.

## 6. Tạo hàng loạt

```http
POST /api/v1/committees
Content-Type: application/json
```

Body **giống hệt** payload preview (client tự build lại, không có draft id):

```json
{
  "groups": [
    { "code": "HD-REV-01", "memberIds": ["lec_11", "lec_12", "lec_13"] },
    { "code": "HD-DEF-01", "memberIds": ["lec_21", "lec_22", "lec_23", "lec_24", "lec_25"] }
  ]
}
```

Response `201` — **partial success**: nhóm hợp lệ được tạo, nhóm lỗi bị bỏ
qua và liệt kê trong `errors[]`, không rollback toàn batch:

```json
{
  "data": {
    "created": 1,
    "skipped": 1,
    "errors": [
      { "index": 1, "code": "COMMITTEE_LECTURER_NOT_FOUND", "message": "Unknown lecturer id(s): 999." }
    ],
    "committees": [
      {
        "id": "cmt_501",
        "code": "HD-REV-01",
        "memberCount": 3,
        "members": [ ... ]
      }
    ]
  }
}
```

`errors[].index` là vị trí (0-based) của nhóm trong mảng `groups` đã gửi —
dùng để highlight đúng nhóm bị lỗi trên UI.

## 7. Quy tắc validate (FE nên chặn trước khi gọi API)

| Điều kiện | Khi nào chặn |
|---|---|
| `code` trống | Ngay khi submit, không gọi preview |
| `code` dài hơn 32 ký tự | Ngay khi nhập |
| Số thành viên ngoài khoảng 1–15 | Ngay khi thêm/bớt thành viên trong 1 nhóm |
| Trùng lecturer trong cùng 1 nhóm | Ngay khi chọn — chặn chọn lại người đã có trong nhóm đó |
| Trùng `code` giữa các nhóm trong cùng batch | Trước khi gọi preview, so sánh các `code` đã nhập |
| Trùng `code` với committee đã tồn tại | Backend trả lỗi ở bước preview/create — FE hiển thị theo `errors[]`, không tự đoán trước |

Lưu ý: **1 lecturer được phép nằm trong nhiều nhóm khác nhau của cùng 1
batch, và trong nhiều committee khác nhau** — đây không phải lỗi, không cần
cảnh báo.

## 8. Error codes

```json
{
  "error": {
    "code": "COMMITTEE_NOT_FOUND",
    "message": "Committee not found.",
    "details": {}
  }
}
```

| HTTP | Code | Ý nghĩa |
|---:|---|---|
| `403` | `FORBIDDEN` | Không phải ADMIN/MANAGER. |
| `404` | `COMMITTEE_NOT_FOUND` | Get/Delete committee không tồn tại. |
| `422` | `COMMITTEE_CODE_REQUIRED` | `code` trống hoặc quá dài. |
| `422` | `COMMITTEE_MEMBER_COUNT_INVALID` | Số thành viên ngoài khoảng 1–15. |
| `422` | `COMMITTEE_MEMBER_DUPLICATE` | Trùng lecturer trong 1 nhóm. |
| `422` | `COMMITTEE_LECTURER_NOT_FOUND` | `lecturerId` không tồn tại. |
| — | `COMMITTEE_CODE_DUPLICATE` | Trùng `code` (trong batch hoặc với DB) — xuất hiện trong `errors[]` của preview/create, không phải lỗi HTTP toàn request vì batch dùng partial success. |

Ở `/committees/preview`, lỗi nằm **trong từng nhóm** (`groups[].errors[]`),
HTTP response luôn là `200` nếu request hợp lệ về mặt shape — chỉ 422 khi
Pydantic chặn (vd `memberIds` rỗng, vượt quá 15 phần tử, thiếu `code`).

Ở `/committees`, tương tự: HTTP `201` ngay cả khi có nhóm bị `skipped`, lỗi
từng nhóm nằm trong `data.errors[]`.

## 9. List, detail, xoá

```http
GET /api/v1/committees
GET /api/v1/committees?lecturerId=lec_11
GET /api/v1/committees/{committeeId}
DELETE /api/v1/committees/{committeeId}
POST /api/v1/committees/bulk-delete
```

List trả `meta.total`, chưa phân trang thật:

```json
{
  "data": [],
  "meta": { "page": 1, "pageSize": 0, "total": 0 }
}
```

Bulk delete:

```http
POST /api/v1/committees/bulk-delete
```

```json
{ "committeeIds": ["cmt_501", "cmt_502"] }
```

```json
{ "data": { "deleted": 2, "deletedIds": [501, 502] } }
```

## 10. Luồng FE đề xuất

```text
Manager nhập nhiều nhóm (code + chọn thành viên theo đúng thứ tự)
→ POST /committees/preview
→ FE hiển thị role/label từng người theo response, không tự tính
→ Nhóm nào ok:false → highlight lỗi tại đúng nhóm đó theo errors[]
→ Manager sửa cho tới khi tất cả nhóm hợp lệ (hoặc chấp nhận bỏ nhóm lỗi)
→ POST /committees với đúng payload đã sửa
→ FE đọc data.created/data.skipped/data.errors[] để báo kết quả
→ Nhóm tạo thành công hiện trong data.committees[]
```

## 11. Checklist FE

- [ ] Không tự tính `role`/`roleLabel` ở FE — luôn lấy từ response.
- [ ] Thứ tự `memberIds` quyết định role — cho phép kéo-thả/sắp xếp lại thứ
  tự trước khi submit, không chỉ cho chọn tự do.
- [ ] Cho phép 1 lecturer lặp lại ở nhiều nhóm/nhiều committee khác nhau —
  không cảnh báo, không chặn.
- [ ] Chặn chọn trùng lecturer trong cùng 1 nhóm ngay trên UI.
- [ ] Preview trả `200` với nhóm lỗi nằm trong `groups[].errors[]` — không
  coi cả request là lỗi khi có 1 nhóm sai.
- [ ] Create là partial success (`201` dù có `skipped > 0`) — hiển thị rõ
  nhóm nào tạo được, nhóm nào bị bỏ qua và lý do (`errors[].index`).
- [ ] Không có PATCH — sửa committee nghĩa là xoá rồi tạo lại.
- [ ] Dùng cookie session và CSRF header đúng quy định.
- [ ] `committeeId`/`lecturerId` đều là external id dạng `cmt_123`/`lec_123`.
