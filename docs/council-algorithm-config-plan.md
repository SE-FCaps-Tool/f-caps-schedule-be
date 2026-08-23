# Kế hoạch: cấu hình hóa thuật toán xếp lịch hội đồng

**Ngày:** 23/08/2026
**Bối cảnh:** phân tích đối chiếu tài liệu thiết kế "THUẬT TOÁN XẾP LỊCH HỘI ĐỒNG — v1.0" (19/08/2026) với code hiện tại, xác định lỗi/thiếu sót và đề xuất hướng sửa để thuật toán xếp lịch có thể cấu hình được qua API thay vì hardcode.

---

## 1. Tổng quan vấn đề

Thuật toán xếp lịch hiện tại (`apps/api/app/scheduler/`) là một CP-SAT solver "phẳng": sinh candidate (nhóm × khung giờ × tổ hợp reviewer) rồi giải một lần duy nhất. Nhiều tham số nghiệp vụ quan trọng — ngưỡng năng lực để làm Chủ tịch/Thư ký, tỉ lệ GVHD tối đa trong một lô đề tài, trọng số chuyên môn theo loại đợt/loại đề tài — hoặc bị **hardcode trong code**, hoặc **hoàn toàn chưa tồn tại** trong hệ thống.

Mục tiêu của kế hoạch này: bổ sung dữ liệu nền còn thiếu (skill, project type), sửa các lỗi logic đã phát hiện, và đưa mọi tham số nghiệp vụ ra thành **cấu hình per-round qua API**, để Manager/Bộ môn tự chỉnh mà không cần dev deploy lại code.

---

## 2. Danh sách lỗi đã phát hiện

| # | Lỗi | File liên quan | Loại | Mức độ |
|---|---|---|---|---|
| A | Không có bảng lưu năng lực giảng viên (skill điều phối, thư ký, chuyên môn) | *(chưa có bảng)* | Thiếu dữ liệu nền | Chặn toàn bộ Q12/Q14 |
| B | Không có `project_types` + ma trận trọng số → không tính được độ khớp chuyên môn | *(chưa có bảng)* | Thiếu dữ liệu nền | Chặn Q15 |
| C | Không có khái niệm "lô đề tài" (batch) cho 1 hội đồng phụ trách liên tiếp | `scheduler/candidates.py` | Thiếu tính năng | Chặn H15, S3 |
| D | Không ràng buộc đúng 1 Chủ tịch + 1 Thư ký khác nhau trong hội đồng (H16) | `scheduler.py`, `validator.py` | Thiếu ràng buộc | Trung bình |
| E | Không giới hạn tỉ lệ đề tài cùng 1 GVHD trong 1 lô (H15) | `scheduler.py` | Thiếu ràng buộc | Trung bình |
| F | S4 (bonus buổi sáng) và S5 (cờ has-day, luôn đúng) là hardcode không phục vụ mục tiêu nghiệp vụ nào | `scheduler.py` dòng ~245-246 | Rác code | Thấp, nhưng chiếm chỗ mã số cần dùng lại |
| G | Committee catalog: vai CT/TK gán **theo vị trí nhập tay** (`position 1 = CHAIR`), không theo năng lực thật | `domain/committees.py::assign_roles()` | Logic sai | Cao — quyết định sai người |
| H | Vai CT/TK trong Committee catalog **không được lưu vào lịch thật** — mọi thành viên bị ghi cứng `"REVIEWER"` khi tạo hội đồng | `services/councils.py::create_council()`, `routes/schedule_operations.py` (dòng 972, 1042, 1194, 1230, 1477) | Bug rò dữ liệu | Cao — dữ liệu vai bị mất hoàn toàn |
| I | Tham số solver hardcode: `time_limit_seconds=10` mặc định, `random_seed=0` mặc định, `num_search_workers=1` không expose | `scheduler.py` dòng 22-23, 131 | Hardcode | Thấp — có override qua API nhưng thiếu 1 tham số vận hành |

### Chi tiết lỗi G/H (Committee catalog)

Feature "Committee catalog" đã có sẵn và gắn sâu vào solver:

- 4 bảng: `committees`, `committee_members`, `round_committees` (2 migration: `0034_committees.py`, `0036_round_committees.py`)
- Solver coi mỗi committee là **1 khối cố định** (atomic reviewer-set) — nếu round đã gán committee, solver chỉ xét nguyên khối đó, không tự ghép lẻ từng người (`candidates.py::_reviewer_tuples`)
- ~717 dòng code + ~700 dòng test đang chạy ổn định

→ **Không nên xóa**, vì cơ chế atomic reviewer-set đúng tinh thần "hội đồng cố định" của thiết kế mới. Chỉ cần: (1) thay nguồn gán vai từ "tùy tiện theo vị trí" sang "theo skill", (2) vá lỗi rò dữ liệu vai trò khi tạo council.

---

## 3. Đối chiếu tài liệu thiết kế v1.0 với code hiện tại

| Hạng mục trong tài liệu | Trạng thái | Bằng chứng |
|---|---|---|
| Vai CHAIR/SECRETARY/MEMBER/REVIEWER | ⚠️ Có nhưng lệch chỗ | Enum đã có, nhưng gán theo vị trí, không theo skill (lỗi G) |
| Bảng `skills`, `lecturer_skills` (0-3, ROLE/DOMAIN) | ❌ Chưa có | 0 kết quả grep "skill", "FACILITATION" |
| `project_types`, ma trận trọng số W_round/W_type | ❌ Chưa có | `projects` không có FK project_type |
| Cột `rounds`: `uses_council_roles`, `chair_min_level`, `secretary_min_level`, `max_same_supervisor_ratio`, `batch_size`, `alpha_round_weight` | ❌ Chưa có | Không trùng tên với cột hiện có |
| `council_batches` (gom lô đề tài) | ❌ Chưa có | Không có khái niệm batch trong `scheduler/` |
| H14 (skill vai), H15 (tỉ lệ GVHD/lô), H16 (đúng 1 CT+1 TK) | ❌ Chưa có | Solver hiện tại dừng ở H13 |
| S1-S9 mới (S2=CouncilFit, S3=gom ProjectType, S8/S9) | ⚠️ Trùng số, khác nghĩa | Code hiện có S1-S7 nhưng semantics khác (S4=bonus sáng, S5=vô nghĩa) |
| Flow 6 pha (tiền kiểm → batch → lập hội đồng → xếp giờ → sửa tay → gán phòng → công bố) | ❌ Chưa có | Kiến trúc thật: 1 lần `solve_schedule()` duy nhất, phẳng |

**Kết luận:** phần lớn tài liệu vẫn là đề xuất thiết kế, chưa cài đặt. Chỉ có vai CHAIR/SECRETARY tồn tại dạng thô sơ, sai logic, và ngắt kết nối khỏi kết quả xếp lịch thật.

---

## 4. Kế hoạch triển khai — 4 giai đoạn

Nguyên tắc: **không đụng vào `solve_schedule()` hiện tại cho đến giai đoạn cuối**, để scheduler đang chạy production không bị gãy giữa chừng.

### Giai đoạn 1 — Schema (an toàn, làm ngay được)

Migration mới, độc lập với bảng cũ:

- `skills(id, code, name, category ENUM('ROLE','DOMAIN'))`
- `lecturer_skills(lecturer_id, skill_id, level SMALLINT CHECK 0-3)`
- `project_types(id, code, name)`
- `project_type_skill_weights(project_type_id, skill_id, weight)`
- `round_type_skill_weights(round_type, skill_id, weight)`
- Cột `projects.project_type_id` (nullable ban đầu)
- Cột trên `rounds`: `uses_council_roles BOOLEAN DEFAULT FALSE`, `chair_min_level SMALLINT DEFAULT 2`, `secretary_min_level SMALLINT DEFAULT 2`, `max_same_supervisor_ratio NUMERIC DEFAULT 0.5`, `batch_size SMALLINT`, `alpha_round_weight NUMERIC DEFAULT 0.7`

Giá trị mặc định dùng theo khuyến nghị K1-K4 của tài liệu gốc, không chặn tiến độ vì các câu hỏi mở O11-O18 chưa chốt hết — Manager chỉnh lại qua API sau, không cần sửa schema.

### Giai đoạn 2 — API CRUD (theo đúng pattern `soft_weights` đã có)

- Endpoint quản lý `skills`, `project_types`, 2 bảng weight — copy style từ endpoint quota/soft_weights hiện có trong `routes/master_data.py`
- Endpoint nhập/sửa `lecturer_skills`
- Response models Pydantic tương ứng trong `response_models.py`

Không ảnh hưởng scheduler, deploy độc lập, an toàn.

### Giai đoạn 3 — Module lập hội đồng (file mới, tách khỏi solver cũ)

`apps/api/app/scheduler/council_formation.py`:

```
form_council(batch, round_config, free_lecturers) -> Council
  1. Lọc free_lecturers:
       - loại GVHD của MỌI đề tài trong batch (H1 mở rộng)
       - loại người khai xung đột (H8)
       - loại người quá quota (H12)
  2. Nếu round_config.uses_council_roles:
       a. CHAIR: lọc level(FACILITATION) ≥ chair_min_level,
          chọn điểm CouncilFit cao nhất trong số đó
       b. SECRETARY: lọc level(SECRETARY) ≥ secretary_min_level, tương tự
  3. MEMBER còn lại: lấp lỗ hổng skill
       (chọn skill mà batch cần nhất nhưng council chưa có ai mạnh)
  4. Kiểm H15: đếm đề tài/GVHD trong batch, loại bớt ứng viên nếu vượt ratio
  5. Kiểm H16: đúng 1 CHAIR, đúng 1 SECRETARY, khác người
  → trả về Council (list of (lecturer_id, role))
```

Viết unit test độc lập cho module này trước khi nối vào flow chính — dễ test vì không phụ thuộc CP-SAT.

Sửa các file cũ để nối vào:

- `domain/committees.py::assign_roles()` — bỏ logic "vị trí 1 = CHAIR" (lỗi G), gọi `council_formation.form_council()` khi hệ thống tự sinh committee theo skill
- `services/councils.py::create_council()` — sửa lỗi H (đang hardcode `"REVIEWER"` cho mọi người), đọc đúng vai từ `Council` trả về

### Giai đoạn 4 — Nối vào scheduler hiện tại (rủi ro cao nhất, làm sau cùng)

```
Manager bấm "Xếp lịch"
        │
        ▼
round.uses_council_roles?
   │                     │
  FALSE                 TRUE
   │                     │
   ▼                     ▼
(giữ nguyên flow      council_formation.form_council()
 hiện tại: Review 1/2)  cho từng batch/nhóm
                          │
                          ▼
                    Council (CHAIR/SECRETARY/MEMBER đúng người)
                          │
                          ▼
                    đẩy vào RoundInput.committee_reviewer_sets
                    (KHÔNG đổi — atomic reviewer-set cũ, đã test kỹ)
                          │
                          ▼
                    scheduler.py solve_schedule()
                    (chỉ xếp GIỜ, không tự chọn ai nữa)
                          │
                          ▼
                    services/councils.py::create_council()
                    lưu đúng vai (sửa lỗi H) thay vì cứng "REVIEWER"
```

Nhờ cờ `uses_council_roles`, Review 1/2 hiện tại không bị ảnh hưởng — chỉ đợt Defense mới đi qua nhánh mới. Tắt cờ là quay về hành vi cũ (rollback dễ).

Cuối cùng sửa `_candidate_soft_scores()`: xóa S4/S5 vô nghĩa (lỗi F), thêm CouncilFit (S2) và group-by-ProjectType (S3) — chỉ áp dụng khi có đủ dữ liệu skill/project_type thật.

---

## 5. Thiết kế API cấu hình

Nguyên tắc phân loại tham số:

- **Đổi theo từng đợt/kỳ học**, Manager cần tự chỉnh không cần dev → cột trên `rounds` + API, giống hệt `soft_weights` đã làm
- **Đổi theo hạ tầng/vận hành** (deploy mới đổi, ví dụ số CPU server) → `app/config.py` (`pydantic-settings`, đọc `.env`)
- **Không bao giờ** nằm cứng trong `scheduler.py` dưới dạng số hardcode

### 5.1. Cấu hình theo round

```
PATCH /api/v1/rounds/{round_id}/algorithm-config
```
```json
{
  "usesCouncilRoles": true,
  "chairMinLevel": 2,
  "secretaryMinLevel": 2,
  "maxSameSupervisorRatio": 0.5,
  "batchSize": 4,
  "alphaRoundWeight": 0.7,
  "softWeights": {
    "S1": 1, "S2": 3, "S3": 2, "S6": 1, "S7": 1, "S8": 1, "S9": 1
  }
}
```

### 5.2. Danh mục skill

```
GET/POST/PATCH  /api/v1/skills
GET/PUT         /api/v1/lecturers/{id}/skills
```

### 5.3. Danh mục ProjectType + ma trận trọng số

```
GET/POST/PATCH  /api/v1/project-types
GET/PUT         /api/v1/project-types/{id}/skill-weights     # W_type
GET/PUT         /api/v1/round-types/{type}/skill-weights     # W_round
```

Bảng trọng số ví dụ trong tài liệu gốc chỉ là **giá trị seed mặc định** — Bộ môn sửa qua API này bất cứ lúc nào, không cần migration lại.

### 5.4. Chạy xếp lịch — không đổi payload hiện có

```
POST /api/v1/rounds/{round_id}/schedule/run
{
  "randomSeed": 0,
  "timeLimitSeconds": 60
}
```

Solver tự đọc `usesCouncilRoles`, `chairMinLevel`... từ round đã cấu hình ở 5.1; payload run chỉ chứa tham số kỹ thuật.

### 5.5. Tham số hạ tầng — KHÔNG qua API

```
# app/config.py — chỉ ops/dev đổi khi deploy, .env
SCHEDULER_NUM_SEARCH_WORKERS=1
SCHEDULER_DEFAULT_TIME_LIMIT_SECONDS=10
```

---

## 6. Ý nghĩa & công dụng từng tham số

| Tham số | Ý nghĩa | Công dụng | Ví dụ |
|---|---|---|---|
| `chairMinLevel` / `secretaryMinLevel` | Ngưỡng năng lực tối thiểu để làm CT/TK | Ngăn xếp người chưa từng điều phối/làm thư ký lên vai đó chỉ vì đang rảnh | `chairMinLevel=2` → GV level 0-1 tự động bị loại khỏi vai CT dù rảnh giờ đó |
| `maxSameSupervisorRatio` | Tỉ lệ tối đa đề tài cùng 1 GVHD trong 1 lô | Tránh hội đồng chấm quá nhiều đề tài của cùng 1 thầy — mất khách quan | Lô 4 đề tài, ratio=0.5 → tối đa 2/4 đề tài cùng 1 GVHD, dư ra bị tách lô khác |
| `batchSize` | Số đề tài tối đa 1 hội đồng phụ trách liên tiếp 1 buổi | Cân bằng lợi ích gom đề tài cùng loại vs. rủi ro khó tìm đủ người khi lô lớn (theo mô phỏng gốc: batch 8 chỉ thành công 45%, batch 3 thành công 73%) | Kỳ ít GV → giảm `batchSize` xuống 2 để tăng khả năng xếp lịch thành công |
| `alphaRoundWeight` (α_r) | Tỉ trọng giữa "chuyên môn cần cho loại đợt" và "chuyên môn cần cho loại đề tài" | Review chỉ xem 1 khía cạnh cụ thể nên nghiêng theo loại đợt (α cao); Defense đánh giá tổng thể nên nghiêng theo loại đề tài (α thấp) | Review 1, α=0.7 → 70% điểm khớp lấy theo "Review 1 cần BA giỏi", 30% theo loại đề tài |
| `softWeights` (S1-S9) | Mức thưởng điểm cho từng tiêu chí mềm khi so sánh phương án | Điều chỉnh ưu tiên giữa các mục tiêu xung đột nhau (S1 cân bằng tải vs. S2 khớp chuyên môn) | `{"S1":3,"S2":1}` ưu tiên chia đều tải; `{"S1":1,"S2":3}` ưu tiên đúng chuyên môn |
| Bảng `skills` / `lecturer_skills` | Lưu năng lực từng giảng viên | Dữ liệu nền cho mọi tính toán ở trên — không có bảng này thì mọi ngưỡng đều vô nghĩa | GV A: `FACILITATION=3, SECRETARY=1, ALGO=3` → đủ làm CT, không đủ làm TK, hợp đề tài ALGO |
| `project_types` + ma trận trọng số | Phân loại đề tài và quy định mỗi loại cần chuyên môn gì | Để hệ thống biết đề tài AI/ML nên ưu tiên người giỏi ALGO hơn BA | `AI_ML → {BA:15, TECH:25, ALGO:35, RESEARCH:25}` |

---

## 7. Ví dụ đầy đủ một luồng thật

**Bối cảnh:** đợt Defense 1.1, 6 giảng viên, cần hội đồng 3 người (1 CT + 1 TK + 1 MEMBER) cho đề tài AI/ML.

### Bước 1 — Setup danh mục skill (1 lần, dùng lại mãi)

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
{"projectTypeId": "AI_ML"}
```

### Bước 4 — Cấu hình thuật toán cho round

```
PATCH /api/v1/rounds/41/algorithm-config
{
  "usesCouncilRoles": true,
  "chairMinLevel": 2,
  "secretaryMinLevel": 2,
  "maxSameSupervisorRatio": 0.5,
  "batchSize": 3,
  "alphaRoundWeight": 0.35,
  "softWeights": {"S1": 1, "S2": 3, "S3": 2}
}
```

### Bước 5 — Chạy xếp lịch

```
POST /api/v1/rounds/41/schedule/run
{"timeLimitSeconds": 60}
```

### Hệ thống xử lý ra sao (theo config vừa nhập)

1. Đề tài #307 (AI_ML) cần người giỏi ALGO; `alphaRoundWeight=0.35` (Defense nghiêng theo loại đề tài) → `w(ALGO)` được tính cao
2. Lọc **Chủ tịch**: `FACILITATION ≥ 2` → GV #12 đạt (level 3), GV #15 không đạt (level 1) → loại #15 khỏi vai CT
3. Lọc **Thư ký**: `SECRETARY ≥ 2` → GV #15 đạt (level 3), GV #12 không đạt (level 1) → loại #12 khỏi vai TK
4. Kết quả: GV #12 → CHAIR, GV #15 → SECRETARY, người thứ 3 chọn theo skill còn thiếu
5. `softWeights.S2=3` cao hơn `S1=1` → chấp nhận vài GV giỏi ALGO phải chấm nhiều hơn người khác, miễn khớp chuyên môn tốt

### So sánh khi đổi config — không cần sửa code

| Config đổi | Kết quả khác đi |
|---|---|
| `chairMinLevel: 2 → 1` | GV #15 (FACILITATION=1) giờ cũng đủ điều kiện làm CT — nhiều lựa chọn hơn, chất lượng điều phối có thể thấp hơn |
| `alphaRoundWeight: 0.35 → 0.7` | Đề tài AI_ML không còn ưu tiên tìm người giỏi ALGO nữa, mà theo yêu cầu chung của loại đợt Defense |
| `softWeights.S1: 1 → 5` | Ưu tiên chia đều tải giữa GV hơn, chấp nhận ghép kém khớp chuyên môn hơn để tránh 1 người bị xếp quá nhiều |

Mọi thay đổi trên chỉ cần gọi lại API tương ứng rồi chạy `schedule/run` lại — không sửa code, không deploy.

---

## 8. Câu hỏi mở cần chốt trước khi triển khai Giai đoạn 1

Chỉ 2 câu sau **thực sự chặn tiến độ** (đổi cấu trúc bảng nếu trả lời sau khi đã migration):

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| O11 | Review 1/2 là 2 hay 3 người? | Đổi ràng buộc trần đầu người |
| O16 | Ai gán `project_type` cho đề tài — GVHD lúc đăng ký hay Bộ môn lúc duyệt? | Đổi chỗ đặt FK và quyền ghi |

Các câu còn lại (O12-O15, O17-O18 trong tài liệu gốc) đều dùng được default an toàn và chỉnh qua API sau, không cần chặn code.
