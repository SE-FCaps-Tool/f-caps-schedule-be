# Cấu hình hóa thuật toán xếp lịch hội đồng — Đặc tả đầy đủ

**Ngày:** 24/08/2026
**Bối cảnh:** phân tích đối chiếu tài liệu thiết kế "THUẬT TOÁN XẾP LỊCH HỘI ĐỒNG — v1.0" (19/08/2026) với code hiện tại trong repo, xác định lỗi/thiếu sót, và thiết kế đầy đủ để đưa thuật toán xếp lịch từ hardcode sang cấu hình được qua UI/API.
**Mockup UI:** [council-schedule-config-flow.html](./mockup/council-schedule-config-flow.html) — 9 màn hình, xem bằng trình duyệt (không cần mạng, trừ font Google Fonts).
**Thay thế/mở rộng:** `docs/council-algorithm-config-plan.md` (bản đầu tiên, tài liệu này là bản đầy đủ nhất tính đến 24/08/2026).

---

## 1. Tóm tắt vấn đề

Thuật toán xếp lịch hiện tại (`apps/api/app/scheduler/`) là một CP-SAT solver "phẳng": sinh candidate (nhóm × khung giờ × tổ hợp reviewer) rồi giải một lần duy nhất, không phân biệt vai trò trong hội đồng theo năng lực. Nhiều tham số quan trọng bị hardcode hoặc hoàn toàn chưa tồn tại. Mục tiêu tài liệu này: liệt kê đầy đủ mọi lỗi/thiếu sót, thiết kế schema + API + UI hoàn chỉnh để giải quyết, và làm nền cho `02-implementation-phases.md`.

---

## 2. Toàn bộ lỗi & thiếu sót đã phát hiện

| # | Vấn đề | File liên quan | Loại | Mức độ |
|---|---|---|---|---|
| A | Không có bảng lưu năng lực giảng viên (skill điều phối, thư ký, chuyên môn) | *(chưa có bảng)* | Thiếu dữ liệu nền | Chặn toàn bộ vai CT/TK theo năng lực |
| B | Không có `project_types` + ma trận trọng số → không tính được độ khớp chuyên môn | *(chưa có bảng)* | Thiếu dữ liệu nền | Chặn tính điểm CouncilFit |
| C | Không có khái niệm "lô đề tài" (batch) cho 1 hội đồng phụ trách liên tiếp | `scheduler/candidates.py` | Thiếu tính năng | Chặn H15, S3 |
| D | Không ràng buộc đúng 1 Chủ tịch + 1 Thư ký khác nhau trong hội đồng (H16) | `scheduler.py`, `validator.py` | Thiếu ràng buộc | Trung bình |
| E | Không giới hạn tỉ lệ đề tài cùng 1 GVHD trong 1 lô (H15) | `scheduler.py` | Thiếu ràng buộc | Trung bình |
| F | Điểm mềm cũ (bonus buổi sáng, cờ has-day) là hardcode không phục vụ mục tiêu nghiệp vụ nào | `scheduler.py` dòng ~245-246 | Rác code | Thấp, chiếm chỗ mã số cần dùng lại |
| G | Committee catalog: vai CT/TK gán **theo vị trí nhập tay** (`position 1 = CHAIR`), không theo năng lực thật | `domain/committees.py::assign_roles()` | **Bug logic thật** | Cao — quyết định sai người |
| H | Vai CT/TK trong Committee catalog **không được lưu vào lịch thật** — mọi thành viên bị ghi cứng `"REVIEWER"` khi tạo hội đồng | `services/councils.py::create_council()`, `routes/schedule_operations.py` (dòng 972, 1042, 1194, 1230, 1477) | **Bug rò dữ liệu thật** | Cao — dữ liệu vai bị mất hoàn toàn |
| I | Tham số solver hardcode: `time_limit_seconds=10` mặc định, `random_seed=0` mặc định, `num_search_workers=1` không expose | `scheduler.py` dòng 22-23, 131 | Hardcode | Thấp — có override qua API nhưng thiếu 1 tham số vận hành |
| J | H11 (kế thừa đợt trước) suy luận "đợt trước" bằng **tìm theo `round_type`** (`DEFENSE_1_1`/`REVIEW_3`), không có cột lưu round nào là "đợt trước" của round nào | `routes/schedule_operations.py` dòng 377-389 | **Bug logic thật** | Cao — không chọn tay được, dễ nhầm nếu có nhiều round cùng type |
| K | Câu SQL lấy `prior_reviewer_ids` (H11) **không lọc theo `semester_id`** | `routes/schedule_operations.py` dòng 377-389 | **Bug thiết kế** | Trung bình — hiện tại vô hại vì `group_id` thường unique theo kỳ, nhưng mong manh |
| L | Chưa có thuật toán tính số lượng hội đồng cần thiết + phân bổ đề tài vào từng lô dựa trên `batchSize` và tổng số nhóm | *(chưa tồn tại)* | Thiếu tính năng | Cao — không có bước này thì không biết cần bao nhiêu hội đồng |
| M | Không có ràng buộc cặp giảng viên (bắt buộc đi chung / cấm đi chung) | *(chưa tồn tại)* | Thiếu tính năng | Yêu cầu mới bổ sung trong quá trình thiết kế |
| N | Không có bước so sánh nhiều phương án xếp lịch trước khi công bố — hệ thống hiện tại chỉ tạo 1 `ScheduleVersion` mỗi lần chạy | `routes/schedule_operations.py::run_scheduler` | Thiếu tính năng UX | Manager cần so sánh trade-off trước khi chọn |

### Chi tiết lỗi G/H (Committee catalog) — quyết định: sửa, không xóa

Feature "Committee catalog" đã có sẵn và gắn sâu vào solver:

- 4 bảng: `committees`, `committee_members`, `round_committees` (2 migration: `0034_committees.py`, `0036_round_committees.py`)
- Solver coi mỗi committee là **1 khối cố định** (atomic reviewer-set) — nếu round đã gán committee, solver chỉ xét nguyên khối đó, không tự ghép lẻ từng người (`candidates.py::_reviewer_tuples`, dòng 59-74)
- ~717 dòng code + ~700 dòng test đang chạy ổn định (`test_committee_api.py`, `test_round_committee_api.py`, `test_committee_candidates.py`)

**Quyết định:** không xóa. Cơ chế atomic reviewer-set đúng tinh thần "hội đồng cố định" của thiết kế mới. Chỉ sửa: (1) `assign_roles()` thay logic "theo vị trí" bằng gọi `council_formation.form_council()` (Giai đoạn 3), (2) vá lỗi rò dữ liệu vai trò khi tạo council thật (Giai đoạn 4).

### Chi tiết lỗi J/K (H11 — kế thừa đợt trước)

Code hiện tại (`schedule_operations.py:377-389`):

```sql
SELECT s.group_id, cm.lecturer_id FROM sessions s
JOIN council_members cm ON cm.council_id = s.council_id
JOIN schedule_versions sv ON sv.id = s.schedule_version_id
JOIN rounds previous_round ON previous_round.id = sv.round_id
WHERE s.group_id = ANY(:group_ids)
  AND previous_round.type IN ('DEFENSE_1_1', 'REVIEW_3')
  AND sv.status IN ('ACTIVE', 'PUBLISHED')
```

Vấn đề: (1) không có cách để Manager **chọn tay** đợt nào là "đợt trước" — hoàn toàn suy luận theo `type`; (2) không lọc theo `semester_id`.

**Quyết định thiết kế đã chốt:** Manager chỉ chọn "nguồn kế thừa" trong **cùng kỳ đang mở** (đúng theo cách Manager làm việc theo workspace kỳ) — dropdown chỉ liệt kê các round cùng `semester_id` đã có `schedule_versions.status IN ('ACTIVE','PUBLISHED')`. Nhờ vậy FK mới `continuity_source_round_id` tự động đã đúng kỳ ngay từ lúc chọn, không cần thêm điều kiện lọc `semester_id` riêng ở câu query.

---

## 3. Schema dữ liệu mới

### 3.1. Skill & năng lực giảng viên

```sql
CREATE TABLE skills (
  id SERIAL PRIMARY KEY,
  code VARCHAR(32) UNIQUE NOT NULL,        -- FACILITATION, SECRETARY, BA, TECH, ALGO, RESEARCH...
  name VARCHAR(120) NOT NULL,               -- tên hiển thị tiếng Việt
  category VARCHAR(16) NOT NULL CHECK (category IN ('ROLE', 'DOMAIN'))
);

CREATE TABLE lecturer_skills (
  lecturer_id INT NOT NULL REFERENCES lecturers(id),
  skill_id INT NOT NULL REFERENCES skills(id),
  level SMALLINT NOT NULL CHECK (level BETWEEN 0 AND 3),
  PRIMARY KEY (lecturer_id, skill_id)
);
```

Thang 4 bậc: `0` Không có · `1` Cơ bản · `2` Thành thạo · `3` Chuyên sâu.

### 3.2. Loại đề tài — 3 trục độc lập

**Quan trọng — 3 trục phân loại đề tài KHÔNG được gộp làm một:**

| Trục | Giá trị | Dùng để |
|---|---|---|
| **Loại đề tài** | Nghiên cứu / Ứng dụng / Nghiên cứu & Ứng dụng | Mô tả bản chất đề tài |
| **Nguồn đề tài** | Giảng viên đề xuất / Doanh nghiệp / Lab | Ai đề xuất đề tài |
| **Chuyên ngành** (`project_types` — bảng do Bộ môn định nghĩa, vd `WEB_BUSINESS`, `AI_ML`, `DATA_PLATFORM`) | Tự do định nghĩa | Tính điểm khớp chuyên môn khi ghép giảng viên (W_type) |

```sql
CREATE TABLE project_types (
  id SERIAL PRIMARY KEY,
  code VARCHAR(32) UNIQUE NOT NULL,
  name VARCHAR(120) NOT NULL
);

CREATE TABLE project_type_skill_weights (
  project_type_id INT NOT NULL REFERENCES project_types(id),
  skill_id INT NOT NULL REFERENCES skills(id),
  weight NUMERIC NOT NULL,
  PRIMARY KEY (project_type_id, skill_id)
);

CREATE TABLE round_type_skill_weights (
  round_type VARCHAR(32) NOT NULL,          -- REVIEW_1, REVIEW_2, DEFENSE_1_1, DEFENSE_1_2, DEFENSE_2
  skill_id INT NOT NULL REFERENCES skills(id),
  weight NUMERIC NOT NULL,
  PRIMARY KEY (round_type, skill_id)
);

ALTER TABLE projects ADD COLUMN project_type_id INT REFERENCES project_types(id);   -- trục chuyên ngành
ALTER TABLE projects ADD COLUMN research_type VARCHAR(24)                             -- trục Loại đề tài
  CHECK (research_type IN ('RESEARCH', 'APPLICATION', 'BOTH'));
ALTER TABLE projects ADD COLUMN source_type VARCHAR(24)                               -- trục Nguồn đề tài
  CHECK (source_type IN ('LECTURER', 'ENTERPRISE', 'LAB'));
ALTER TABLE projects ADD COLUMN source_note VARCHAR(200);                             -- vd tên doanh nghiệp/lab
```

Công thức trọng số hiệu dụng:

```
w(s) = α_r × W_round[r][s] + (1 − α_r) × W_type[type(p)][s]
```

### 3.3. Cấu hình round

```sql
ALTER TABLE rounds ADD COLUMN uses_council_roles BOOLEAN DEFAULT FALSE;
ALTER TABLE rounds ADD COLUMN chair_min_level SMALLINT DEFAULT 2;
ALTER TABLE rounds ADD COLUMN secretary_min_level SMALLINT DEFAULT 2;
ALTER TABLE rounds ADD COLUMN max_same_supervisor_ratio NUMERIC DEFAULT 0.5;
ALTER TABLE rounds ADD COLUMN batch_size SMALLINT;
ALTER TABLE rounds ADD COLUMN alpha_round_weight NUMERIC DEFAULT 0.7;
ALTER TABLE rounds ADD COLUMN require_continuity_from_prior_round BOOLEAN DEFAULT FALSE;   -- H11 bật/tắt
ALTER TABLE rounds ADD COLUMN continuity_min_members SMALLINT DEFAULT 1;                    -- H11 số người tối thiểu
ALTER TABLE rounds ADD COLUMN continuity_source_round_id INT REFERENCES rounds(id);         -- sửa lỗi J/K
```

Validate khi set `continuity_source_round_id`: round nguồn phải cùng `semester_id`.

### 3.4. Ràng buộc cặp giảng viên (H17/H18)

```sql
CREATE TABLE round_lecturer_pair_constraints (
  id SERIAL PRIMARY KEY,
  round_id INT NOT NULL REFERENCES rounds(id),
  lecturer_id_a INT NOT NULL REFERENCES lecturers(id),
  lecturer_id_b INT NOT NULL REFERENCES lecturers(id),
  constraint_type VARCHAR(20) NOT NULL CHECK (constraint_type IN ('MUST_TOGETHER', 'MUST_NOT_TOGETHER')),
  reason TEXT,
  created_by INT REFERENCES accounts(id),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Gắn theo `round_id` (không phải bảng global) — đúng theo cách Manager làm việc theo từng đợt cụ thể.

---

## 4. Ràng buộc cứng — danh sách đầy đủ H1-H18

| Mã | Ràng buộc | Trạng thái | Cấu hình ở đâu |
|---|---|---|---|
| H1 | GVHD không chấm đề tài mình hướng dẫn — mở rộng cho **cả lô** khi hội đồng phụ trách nhiều đề tài | Đã có | Luôn bật |
| H2 | 1 giảng viên không ở 2 phiên trùng giờ | Đã có | Luôn bật |
| H3 | 1 phòng không có 2 phiên trùng giờ | Validate tay ở bước Gán phòng | Tự động khi chọn phòng |
| H4 | 1 nhóm đúng 1 phiên trong 1 đợt | Đã có | Luôn bật |
| H5 | Cấu trúc hội đồng theo loại đợt (Review 2 người ngang hàng; Defense 1.1 = 3 người CT+TK+TV; Defense 1.2/2 = 5 người CT+TK+3TV) | Đã có | "Một hội đồng cần bao nhiêu người?" |
| H6 | 1 giảng viên chỉ giữ 1 vai trong 1 hội đồng | Đã có | Luôn bật |
| H7 | Chỉ xếp GV vào khung đã đăng ký rảnh | Đã có | Theo dữ liệu đăng ký |
| H8 | Không xếp GV đã khai xung đột lợi ích | Đã có | Theo khai báo xung đột |
| H9 | Nhóm phải đúng trạng thái phù hợp loại đợt | Đã có | Theo trạng thái nhóm |
| H10 | Tôn trọng khung giờ nhóm đã chọn | Đã có | Theo đăng ký nhóm |
| H11 | Giữ lại người đã chấm đợt trước (số lượng tối thiểu + chọn tay nguồn kế thừa cùng kỳ) | **Cần sửa** (lỗi J/K) | "Có cần giữ người cũ từ đợt trước không?" |
| H12 | Trần phút/buổi, phút/ngày, hạn mức kỳ | Đã có | Cấu hình chung kỳ |
| H13 | Số phiên tối đa/khung giờ | Đã có | Cấu hình chung round |
| H14 | Chủ tịch/Thư ký phải đủ năng lực tối thiểu | **Cần xây** | "Ai đủ điều kiện làm Chủ tịch/Thư ký?" |
| H15 | Giới hạn tỉ lệ đề tài cùng 1 GVHD trong 1 lô | **Cần xây** | "Mỗi hội đồng chấm liên tiếp mấy đề tài?" |
| H16 | Hội đồng Defense có đúng 1 CT + 1 TK, 2 người khác nhau | **Cần xây** | Tự động khi bật phân vai |
| H17 | Cặp giảng viên bắt buộc đi chung (MUST_TOGETHER) | **Cần xây (mới)** | Bước "Ràng buộc cặp giảng viên" |
| H18 | Cặp giảng viên cấm chung 1 hội đồng (MUST_NOT_TOGETHER) | **Cần xây (mới)** | Bước "Ràng buộc cặp giảng viên" |

---

## 5. Ràng buộc mềm — danh sách đầy đủ S1-S9

| Mã | Tiêu chí | Trạng thái | Ghi chú |
|---|---|---|---|
| S1 | Cân bằng tải giữa các giảng viên (theo % hạn mức kỳ, điều chỉnh theo mức ưu tiên GV tự chọn) | Đã có | |
| S2 | Khớp đúng chuyên môn (CouncilFit — dùng `max` trong hội đồng, không dùng trung bình, để hội đồng "phủ" đủ mặt chuyên môn thay vì chọn toàn người đều đều) | **Cần xây** | |
| S3 | Gom đề tài cùng loại (project_type) gần nhau — cùng hội đồng hoặc ít nhất cùng buổi | **Cần xây** | |
| S4 | Giữ nguyên cặp GV đã chấm Review 1 | **Cần xây** | Chỉ áp dụng đợt Review 2 |
| S5 | Giữ thêm người thứ 2 từ hội đồng Defense 1.1 (bổ sung mềm cho H11) | **Cần xây** | Chỉ áp dụng đợt Defense 1.2 |
| S6 | Gom lịch liên tiếp trong 1 buổi | Đã có | |
| S7 | Giảm số ngày phải có mặt | Đã có | |
| S8 | Đa dạng GVHD trong 1 lô (thưởng thêm, vượt trên mức H15 đã ép cứng) | **Cần xây** | |
| S9 | Giữ ổn định tổ hợp hội đồng giữa các phiên liên tiếp | **Cần xây** | |

**Công thức điểm khớp:**

```
fit(l, p, r) = Σ_s w(s) × level(l, s)  /  (3 × Σ_s w(s))                    ∈ [0, 1]

CouncilFit(C, B, r) = Σ_s w̄(s) × max_{l ∈ C} level(l, s)  /  (3 × Σ_s w̄(s))
                        với w̄(s) = trung bình w(s) trên các đề tài trong lô
```

**Xung đột cần biết trước:** S1 (cân bằng tải) và S2 (khớp chuyên môn) kéo ngược nhau — nếu chỉ có vài giảng viên giỏi 1 kỹ năng hiếm mà có rất nhiều đề tài cần kỹ năng đó, tối ưu S2 sẽ dồn hết phiên lên vài người đó. Do đó UI cần cho Manager tự sắp xếp độ ưu tiên (không phải chỉ số trừu tượng).

---

## 6. Thuật toán lập kế hoạch lô (`plan_batches`) — mục L

Bài toán: từ tổng số nhóm trong round + `batchSize` đã chọn, tính ra cần bao nhiêu hội đồng và nhóm nào thuộc lô nào.

```
số_hội_đồng = ceil(tổng_số_nhóm / batchSize)

1. Sắp nhóm theo project_type
2. Trong mỗi loại, RẢI VÒNG theo GVHD (round-robin) để không dồn liền nhau
   → tránh vi phạm H15 ngay từ lúc chia
3. Cắt thành lô kích thước batchSize
4. Lô lẻ cuối của mỗi loại → ghép với loại GẦN NHẤT
   (đo bằng cosine similarity giữa 2 vector W_type)
```

Ví dụ minh họa: 24 nhóm, `batchSize=4` → cần 6 hội đồng; WEB_BUSINESS (10 nhóm) → 2 lô đủ + 1 lô lẻ (2 nhóm); AI_ML (8 nhóm) → 2 lô đủ; DATA_PLATFORM (6 nhóm) → 1 lô đủ + 1 lô lẻ (2 nhóm); 2 lô lẻ ghép lại thành 1 lô hỗn hợp.

Nếu `số_hội_đồng` tính ra vượt quá trần nhân lực thực tế (xem mục "Tiền kiểm tra năng lực" trong `02-implementation-phases.md`), hệ thống phải báo ngay, không được chạy solver rồi mới fail giữa chừng.

---

## 7. Thuật toán lập hội đồng (`form_council`)

```
function formCouncil(batch, round, freeLecturers, pairConstraints):

    P = freeLecturers
    P = P \ supervisorsOf(batch)                    # H1 mở rộng cho CẢ LÔ
    P = P \ conflictDeclaredWith(batch)             # H8
    P = P ∩ availableAtAll(batch.timeslots)         # H7
    P = P \ overQuota(round)                        # H12

    council = []

    if round.uses_council_roles:
        Cands = { l ∈ P : level(l, FACILITATION) ≥ round.chair_min_level }    # H14
        if Cands = ∅ : return FAIL("không còn GV đủ điều kiện Chủ tịch")
        chair = argmax_{l ∈ Cands} score(l, batch, round)
        council += (chair, CHAIR);  P −= chair

        Cands = { l ∈ P : level(l, SECRETARY) ≥ round.secretary_min_level }   # H14
        if Cands = ∅ : return FAIL("không còn GV đủ điều kiện Thư ký")
        sec = argmax_{l ∈ Cands} score(l, batch, round)
        council += (sec, SECRETARY);  P −= sec

    while |council| < round.council_size:
        if P = ∅ : return FAIL("không đủ giảng viên")
        candidates = { l ∈ P : không MUST_NOT_TOGETHER (H18) với bất kỳ ai trong council }
        gap = argmax_s  w̄(s) × (3 − coverage(council, s))
        m   = argmax_{l ∈ candidates} [ β₁ × level(l, gap)/3
                             + β₂ × fit(l, batch, round)
                             + β₃ × loadHeadroom(l)
                             − β₄ × supervisorOverlap(l, batch) ]
        council += (m, MEMBER)
        forced_partner = mustTogetherPartnerOf(m)                              # H17
        if forced_partner ∈ P and forced_partner ∉ council:
            council += (forced_partner, MEMBER)
        P −= m, forced_partner

    validateH15(council, batch, round)   # tỉ lệ GVHD trong lô
    validateH16(council, round)          # đúng 1 CT + 1 TK khác nhau
    return council
```

Thứ tự CT → TK → Member **không phải quy ước hành chính mà là chiến lược tìm kiếm** — chọn tài nguyên khan hiếm nhất trước (most-constrained-first), vì chỉ khoảng một nửa giảng viên đủ điều kiện làm Chủ tịch.

---

## 8. Thiết kế API

### 8.1. Cấu hình round (gộp 1 endpoint theo yêu cầu UX)

```
PUT /api/v1/rounds/{round_id}/schedule-config
```
```json
{
  "councilSize": 3,
  "usesCouncilRoles": true,
  "chairMinLevel": 2,
  "secretaryMinLevel": 2,
  "maxSameSupervisorRatio": 0.5,
  "batchSize": 4,
  "alphaRoundWeight": 0.35,
  "requireContinuityFromPriorRound": true,
  "continuityMinMembers": 1,
  "continuitySourceRoundId": 41,
  "softWeightsOrder": ["S1", "S2", "S3", "S6", "S7", "S8", "S9"],
  "pairConstraints": [
    { "lecturerIdA": 12, "lecturerIdB": 20, "type": "MUST_TOGETHER", "reason": "..." },
    { "lecturerIdA": 15, "lecturerIdB": 30, "type": "MUST_NOT_TOGETHER", "reason": "..." }
  ]
}
```

`continuitySourceRoundId` chỉ chấp nhận round có cùng `semester_id`; validate lỗi `CONTINUITY_SOURCE_DIFFERENT_SEMESTER` nếu vi phạm. `softWeightsOrder` là **thứ tự ưu tiên** (mảng có thứ tự), không phải object số như thiết kế v1 — khớp với UI kéo-thả đã chốt.

```
GET /api/v1/rounds/{round_id}/schedule-config/preview-councils
```
Chạy riêng `form_council()` cho mọi lô, **không** chạy CP-SAT xếp giờ — trả về danh sách hội đồng dự kiến để Manager xem trước.

### 8.2. Danh mục skill / project types

```
GET/POST/PATCH  /api/v1/skills
GET/PUT         /api/v1/lecturers/{id}/skills
GET/POST/PATCH  /api/v1/project-types
GET/PUT         /api/v1/project-types/{id}/skill-weights     # W_type
GET/PUT         /api/v1/round-types/{type}/skill-weights     # W_round
```

### 8.3. Chạy xếp lịch — tạo nhiều phương án

```
POST /api/v1/rounds/{round_id}/schedule/run
{ "variantCount": 3, "timeLimitSeconds": 60 }
```
Chạy solver `variantCount` lần với `random_seed` khác nhau, mỗi lần ra 1 `ScheduleVersion` DRAFT — API `GET /rounds/{round_id}/schedule/versions` (đã có sẵn) trả về mảng, FE hiển thị dạng so sánh 3 phương án (điểm mềm, số nhóm xếp được, vi phạm ràng buộc cặp).

```
POST /api/v1/schedule/versions/{version_id}/select
```
Đánh dấu 1 version là phương án đang xử lý tiếp (khác với activate/publish — chỉ là bước trung gian trước khi gán phòng).

### 8.4. Gán phòng (đã có endpoint, không đổi)

Dùng lại cơ chế `room_id` trên `schedule_assignments` đã có, chỉ cần UI mới ở FE — không cần API mới.

---

## 9. Thiết kế UI/UX

Xem mockup đầy đủ tại [council-schedule-config-flow.html](./mockup/council-schedule-config-flow.html) — 3 trang trên canvas:

**Trang "Luồng thao tác"** — 6 bước tuần tự:
1. Cấu hình xếp lịch — mọi field bằng câu hỏi tiếng Việt tự nhiên, không hiện tên biến kỹ thuật (đã bỏ hết `batchSize`, `chairMinLevel`...); tiêu chí ưu tiên xếp hạng bằng danh sách kéo-thả (không dùng ô nhập số hay mã S1-S9); trọng số α dùng 5 ô lựa chọn rời rạc thay vì thanh trượt liên tục; có banner "Tiền kiểm tra năng lực" cập nhật real-time
2. Ràng buộc cặp giảng viên — form thêm + bảng danh sách MUST_TOGETHER/MUST_NOT_TOGETHER
3. Xem trước hội đồng — card từng hội đồng dự kiến, không tốn thời gian giải CP-SAT
4. So sánh phương án — 3 phương án A/B/C song song, breakdown điểm theo tiêu chí, cảnh báo trade-off riêng từng phương án
5. Gán phòng — bảng chọn phòng từng phiên, chặn tiếp tục nếu còn thiếu
6. Công bố lịch — bảng lịch theo khung giờ, xem lại lần cuối trước khi công bố

**Trang "Quản lý dữ liệu"**:
- Quản lý giảng viên — ngoài mã/họ tên/email: bộ môn, học hàm-học vị, năng lực điều phối/thư ký (trực quan), vai đủ điều kiện (tính sẵn), tải công việc kỳ hiện tại, mức ưu tiên tự chọn, trạng thái đăng ký đợt, ràng buộc cặp liên quan — panel chi tiết khi chọn 1 giảng viên
- Quản lý đề tài — 3 trục lọc/hiển thị độc lập: Loại đề tài, Nguồn đề tài, Chuyên ngành (xem mục 3.2)

**Trang "Tham chiếu ràng buộc"** — bảng đầy đủ H1-H18 và S1-S9, mỗi dòng có trạng thái (đã có/cần sửa/cần xây) và chỉ rõ cấu hình ở đâu trong luồng chính — dùng để đối chiếu, không phải màn thao tác.

---

## 10. Ví dụ minh họa đầy đủ

**Bối cảnh:** đợt Defense 1.1, kỳ SP26, 6 giảng viên liên quan, cần hội đồng 3 người (1 CT + 1 TK + 1 TV) cho đề tài AI/ML.

### Bước 1 — Setup danh mục skill (làm 1 lần, dùng lại mãi)

```
POST /api/v1/skills
{"code": "FACILITATION", "name": "Điều phối cuộc họp", "category": "ROLE"}

POST /api/v1/skills
{"code": "SECRETARY", "name": "Kinh nghiệm thư ký", "category": "ROLE"}

POST /api/v1/skills
{"code": "ALGO", "name": "Thuật toán", "category": "DOMAIN"}
```
*(BA, TECH, RESEARCH tương tự)*

### Bước 2 — Nhập năng lực từng giảng viên (Bộ môn, đầu kỳ)

```
PUT /api/v1/lecturers/12/skills
{"FACILITATION": 3, "SECRETARY": 1, "BA": 1, "TECH": 2, "ALGO": 3, "RESEARCH": 1}
```
→ GV #12: rất mạnh điều phối + mạnh ALGO, yếu thư ký.

```
PUT /api/v1/lecturers/15/skills
{"FACILITATION": 1, "SECRETARY": 3, "BA": 2, "TECH": 1, "ALGO": 1, "RESEARCH": 1}
```
→ GV #15: rất mạnh thư ký, yếu điều phối và yếu ALGO.

### Bước 3 — Setup loại đề tài + trọng số

```
POST /api/v1/project-types
{"code": "AI_ML", "name": "Trí tuệ nhân tạo"}

PUT /api/v1/project-types/AI_ML/skill-weights
{"BA": 15, "TECH": 25, "ALGO": 35, "RESEARCH": 25}

PATCH /api/v1/projects/307
{"projectTypeId": "AI_ML", "researchType": "RESEARCH", "sourceType": "LAB", "sourceNote": "Lab AI"}
```

### Bước 4 — Cấu hình thuật toán cho round

```
PUT /api/v1/rounds/41/schedule-config
{
  "councilSize": 3,
  "usesCouncilRoles": true,
  "chairMinLevel": 2,
  "secretaryMinLevel": 2,
  "maxSameSupervisorRatio": 0.5,
  "batchSize": 3,
  "alphaRoundWeight": 0.35,
  "softWeightsOrder": ["S1", "S2", "S3", "S6", "S7", "S8", "S9"]
}
```

### Bước 5 — Xem trước rồi chạy xếp lịch

```
GET  /api/v1/rounds/41/schedule-config/preview-councils
POST /api/v1/rounds/41/schedule/run
{"variantCount": 3, "timeLimitSeconds": 60}
```

### Hệ thống xử lý ra sao (theo config vừa nhập)

1. Đề tài #307 (AI_ML) cần người giỏi ALGO; `alphaRoundWeight=0.35` (Defense nghiêng theo chuyên ngành) → `w(ALGO)` được tính cao
2. Lọc **Chủ tịch**: `FACILITATION ≥ 2` → GV #12 đạt (level 3), GV #15 không đạt (level 1) → loại #15 khỏi vai CT
3. Lọc **Thư ký**: `SECRETARY ≥ 2` → GV #15 đạt (level 3), GV #12 không đạt (level 1) → loại #12 khỏi vai TK
4. Kết quả: GV #12 → CHAIR, GV #15 → SECRETARY, người thứ 3 chọn theo skill còn thiếu
5. `softWeightsOrder` đặt S2 (khớp chuyên môn) lên trên S1 (cân bằng tải) → chấp nhận vài GV giỏi ALGO phải chấm nhiều hơn người khác, miễn khớp chuyên môn tốt

### So sánh khi đổi config — không cần sửa code

| Tham số đổi | Kết quả khác đi |
|---|---|
| `chairMinLevel: 2 → 1` | GV #15 (FACILITATION=1) giờ cũng đủ điều kiện làm CT — nhiều lựa chọn hơn, chất lượng điều phối có thể thấp hơn |
| `alphaRoundWeight: 0.35 → 0.7` | Đề tài AI_ML không còn ưu tiên tìm người giỏi ALGO nữa, mà theo yêu cầu chung của đợt Defense |
| Đưa S1 (cân bằng tải) lên đầu `softWeightsOrder` | Ưu tiên chia đều tải giữa GV hơn, chấp nhận ghép kém khớp chuyên môn hơn để tránh 1 người bị xếp quá nhiều |

Mọi thay đổi trên chỉ cần gọi lại API tương ứng rồi chạy `schedule/run` lại — không sửa code, không deploy.

---

## 11. Câu hỏi mở còn chặn tiến độ thật (theo O11-O18 của tài liệu gốc)

Chỉ 2 câu thực sự chặn (đổi cấu trúc bảng nếu trả lời sau khi đã migration):

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| O11 | Review 1/2 là 2 hay 3 người? | Đổi ràng buộc trần đầu người |
| O16 | Ai gán chuyên ngành (project_type) cho đề tài — GVHD lúc đăng ký hay Bộ môn lúc duyệt? | Đổi chỗ đặt FK và quyền ghi |

Các câu còn lại dùng default an toàn, chỉnh qua API sau, không chặn code.
