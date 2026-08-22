# FE Handoff — Round Type rename (5 types thay vì 6)

## 1. Cái gì đã đổi

Enum `round_type` rút gọn từ 6 xuống 5 giá trị. **Không đổi hành vi/business
rule nào** — chỉ đổi tên. Mọi rule trước đây gắn với `DEFENSE_1_1` giờ gắn
nguyên vẹn với `REVIEW_3`; mọi rule gắn với `DEFENSE_1_2` giờ gắn nguyên vẹn
với `DEFENSE_1`.

| Cũ | Mới | Số reviewer | Ghi chú |
|---|---|---:|---|
| `REVIEW_1` | `REVIEW_1` | 2 | Không đổi |
| `REVIEW_2` | `REVIEW_2` | 2 | Không đổi |
| `DEFENSE_1_1` | **`REVIEW_3`** | 3 | Đổi tên. Outcome LEVEL_1-4, eligibility/remediation giữ nguyên |
| `DEFENSE_1_2` | **`DEFENSE_1`** | 5 | Đổi tên. Outcome COMPLETED-only, giữ nguyên |
| `DEFENSE_2` | `DEFENSE_2` | 5 | Không đổi |

Enum `REVIEW_3` cũ (thêm ở migration 0012, chưa từng dùng được vì bị domain
validation chặn) đã bị xoá và thay bằng giá trị mới cùng tên này — không
liên quan tới nhau, không có dữ liệu cũ nào bị ảnh hưởng (DB xác nhận 0 round
tồn tại trước khi đổi).

## 2. Những chỗ FE gửi/nhận string này

- Tạo Round: `POST /api/v1/rounds`, `POST /api/v1/semesters/{semesterId}/rounds`
  — field `type` (hoặc `"type"` trong body legacy).
- Mọi response có `round_type`/`roundType`: session detail, result detail,
  lecturer/leader portal, remediation list, results list.
- Bảng số lượng reviewer bắt buộc theo type (dùng để validate form tạo
  Round trước khi gửi):

```text
REVIEW_1  → 2 reviewer
REVIEW_2  → 2 reviewer
REVIEW_3  → 3 reviewer   (trước đây ghi là "Defense 1.1")
DEFENSE_1 → 5 reviewer   (trước đây ghi là "Defense 1.2")
DEFENSE_2 → 5 reviewer
```

- `resultOwnerMode` chỉ được bật cho `REVIEW_3` và `DEFENSE_2` (trước đây
  ghi "DEFENSE_1_1 và DEFENSE_2"). Error message mới:
  `"resultOwnerMode is only available for REVIEW_3 and DEFENSE_2"`.

## 3. Response field rename ở endpoint group-progress

`GET /api/v1/reports/group-progress` (semester-scoped group progress pivot,
dùng bởi `manager_extensions.py`) đổi tên 2 field trong mỗi row:

```diff
- "defense_1_1": "CONDITIONAL",
- "defense_1_2": null,
+ "review_3": "CONDITIONAL",
+ "defense_1": null,
```

`review_1`, `review_2`, `defense_2`, `result_verifier_lecturer_id` không đổi.

## 4. Outcome theo round type (không đổi tập giá trị, chỉ đổi key)

```text
REVIEW_1, REVIEW_2 → PASS | NEEDS_FIX | FAIL
REVIEW_3            → LEVEL_1 | LEVEL_2 | LEVEL_3 | LEVEL_4
DEFENSE_1           → COMPLETED
DEFENSE_2           → PASS | FAIL
```

`REVIEW_3` + `LEVEL_2` vẫn là trigger tạo remediation case (trước đây là
`DEFENSE_1_1` + `LEVEL_2`) — không đổi logic, chỉ đổi type string dùng để
gọi API.

## 5. Checklist FE

- [ ] Đổi mọi string literal `"DEFENSE_1_1"` → `"REVIEW_3"`,
  `"DEFENSE_1_2"` → `"DEFENSE_1"` trong code FE (dropdown tạo Round, filter,
  TS union type nếu có định nghĩa cứng).
- [ ] Đổi label hiển thị UI: "Defense 1.1" → "Review 3", "Defense 1.2" →
  "Defense 1".
- [ ] Form tạo Round: cập nhật bảng validate số reviewer theo bảng ở mục 2.
- [ ] Outcome picker cho `REVIEW_3` vẫn hiện LEVEL_1-4 như trước (chỉ đổi
  tên round type đứng trước nó, không đổi UI outcome).
- [ ] Đổi field đọc từ group-progress report: `defense_1_1`→`review_3`,
  `defense_1_2`→`defense_1` (mục 3).
- [ ] Không cần xử lý migrate dữ liệu cũ — chưa có Round nào tồn tại trong DB
  trước khi đổi, không có round `type` cũ nào cần convert khi hiển thị lại.
