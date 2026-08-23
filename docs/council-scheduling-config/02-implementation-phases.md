# Kế hoạch triển khai theo phase — tuần tự

Đi kèm với [01-full-specification.md](./01-full-specification.md). Nguyên tắc xuyên suốt: **không đụng vào `scheduler.py` hiện tại cho đến Phase 5** — code production (Review 1/2 đang chạy) không được gãy giữa chừng. Mỗi phase có mục tiêu rõ, việc cần làm, file bị ảnh hưởng, và tiêu chí hoàn thành để biết khi nào chuyển phase tiếp theo.

---

## Phase 0 — Chốt quyết định nghiệp vụ (không viết code)

**Mục tiêu:** trả lời 2 câu hỏi thực sự chặn tiến độ trước khi viết migration, vì đổi sau sẽ phải sửa cả schema lẫn dữ liệu đã seed.

**Việc cần làm:**
- Chốt O11: Review 1/2 là 2 hay 3 người
- Chốt O16: ai gán chuyên ngành (project_type) cho đề tài — GVHD lúc đăng ký hay Bộ môn lúc duyệt

**Tiêu chí hoàn thành:** có câu trả lời bằng văn bản (Slack/email/ghi chú) cho 2 câu trên. Không bắt buộc chờ nếu đội ngũ chấp nhận rủi ro đổi sau.

---

## Phase 1 — Schema (an toàn, độc lập, không rủi ro)

**Mục tiêu:** tạo toàn bộ bảng/cột mới, không đụng bảng cũ ngoài việc thêm cột nullable.

**Việc cần làm:**
- Migration mới tạo: `skills`, `lecturer_skills`, `project_types`, `project_type_skill_weights`, `round_type_skill_weights`, `round_lecturer_pair_constraints`
- Thêm cột vào `projects`: `project_type_id`, `research_type`, `source_type`, `source_note`
- Thêm cột vào `rounds`: `uses_council_roles`, `chair_min_level`, `secretary_min_level`, `max_same_supervisor_ratio`, `batch_size`, `alpha_round_weight`, `require_continuity_from_prior_round`, `continuity_min_members`, `continuity_source_round_id`
- Seed dữ liệu mẫu: danh mục skill (FACILITATION, SECRETARY, BA, TECH, ALGO, RESEARCH), vài project_type mẫu (WEB_BUSINESS, AI_ML, DATA_PLATFORM, RESEARCH), ma trận W_round/W_type khởi tạo theo tài liệu gốc mục 2.2

**File bị ảnh hưởng:** `apps/api/migrations/versions/00XX_*.py` (nhiều file mới), không sửa file nào khác.

**Tiêu chí hoàn thành:** `alembic upgrade head` chạy sạch trên DB test; `alembic downgrade -1` rollback được không lỗi; seed script chạy idempotent.

---

## Phase 2 — API CRUD cho dữ liệu nền

**Mục tiêu:** cho Manager/Bộ môn tự quản lý skill, project type, ma trận trọng số qua API — theo đúng pattern `soft_weights` đã có trong `master_data.py`.

**Việc cần làm:**
- `routes/master_data.py`: thêm endpoint CRUD cho `skills`, `project_types`, `project_type_skill_weights`, `round_type_skill_weights`
- Endpoint nhập/sửa `lecturer_skills` — tạm để Bộ môn nhập tay (theo O12 chưa chốt, để mở khả năng GV tự đề xuất sau)
- Response models Pydantic mới trong `response_models.py`
- Endpoint `PATCH /projects/{id}` mở rộng nhận `researchType`, `sourceType`, `sourceNote`, `projectTypeId`

**File bị ảnh hưởng:** `routes/master_data.py`, `response_models.py`, `routes/master_data.py` (project update), test mới `test_skills_api.py`, `test_project_types_api.py`.

**Tiêu chí hoàn thành:** test CRUD pass cho cả 2 domain (skill, project type); không cần round nào bật `uses_council_roles` để test được — độc lập hoàn toàn với scheduler.

**Rủi ro:** không có — hoàn toàn additive, không route cũ nào bị sửa.

---

## Phase 3 — Module lập hội đồng (`council_formation.py`)

**Mục tiêu:** viết xong module ghép hội đồng + tính batch, test độc lập, **chưa nối vào flow chạy lịch thật**.

**Việc cần làm:**
- File mới `apps/api/app/scheduler/council_formation.py`:
  - `plan_batches(groups, batch_size, project_types) -> list[Batch]` (mục 6 của spec)
  - `form_council(batch, round, free_lecturers, pair_constraints) -> Council | Failure` (mục 7 của spec)
  - `_council_fit(candidate, batch, round)` — công thức CouncilFit dùng `max`
- Sửa `domain/committees.py::assign_roles()`: khi hệ thống tự sinh committee theo skill, gọi `council_formation.form_council()` thay vì gán theo vị trí (sửa lỗi G). Committee do Manager tự tạo tay vẫn giữ input tay nhưng validate qua ngưỡng skill.
- Unit test cho `plan_batches` và `form_council` — không phụ thuộc CP-SAT, chạy nhanh, cover: đủ người, thiếu người đủ điều kiện CT/TK (H14), vi phạm tỉ lệ GVHD (H15), vi phạm H16, cặp H17/H18.

**File bị ảnh hưởng:** `scheduler/council_formation.py` (mới), `domain/committees.py`, `tests/test_council_formation.py` (mới).

**Tiêu chí hoàn thành:** coverage đầy đủ các ràng buộc H1 (mở rộng lô), H7, H8, H12, H14, H15, H16, H17, H18 bằng unit test; chạy độc lập không cần DB thật (dùng fixture in-memory).

**Rủi ro:** thấp — module mới, không route nào gọi tới nó ở phase này.

---

## Phase 4 — API cấu hình round + preview + ràng buộc cặp

**Mục tiêu:** expose toàn bộ cấu hình qua 1 endpoint gộp, và endpoint preview dùng module Phase 3 — Manager xem trước kết quả mà chưa cần chạy solver thật.

**Việc cần làm:**
- `PUT /rounds/{round_id}/schedule-config` — nhận toàn bộ payload mục 8.1 của spec, validate `continuitySourceRoundId` cùng `semester_id`
- `GET /rounds/{round_id}/schedule-config/preview-councils` — gọi `plan_batches` + `form_council` cho mọi lô, trả kết quả không lưu DB
- CRUD `round_lecturer_pair_constraints` — gắn theo `round_id`
- Validate ngay lúc lưu: nếu 2 người set MUST_TOGETHER nhưng không có khung giờ rảnh chung nào → cảnh báo sớm (không chặn lưu, chỉ warning)

**File bị ảnh hưởng:** `routes/round_committee_contract.py` hoặc file route mới `routes/round_schedule_config.py`, `services/committee_service.py` (gọi council_formation), test mới.

**Tiêu chí hoàn thành:** Manager gọi API, xem preview đúng với dữ liệu skill/pair constraint đã nhập ở Phase 2; preview không tạo bản ghi DB nào (idempotent, gọi lại nhiều lần không side-effect).

**Rủi ro:** thấp — endpoint mới, `schedule/run` cũ chưa đổi.

---

## Phase 5 — Nối vào scheduler thật (rủi ro cao nhất — làm cẩn thận)

**Mục tiêu:** khi `uses_council_roles = TRUE`, flow xếp lịch thật đi qua council_formation trước, solver chỉ còn xếp giờ.

**Việc cần làm:**
```
routes/schedule_operations.py::run_scheduler:
    if round.uses_council_roles:
        batches = council_formation.plan_batches(...)
        councils = [council_formation.form_council(b, round, ...) for b in batches]
        → đẩy councils vào RoundInput.committee_reviewer_sets (KHÔNG đổi candidates.py atomic logic)
    else:
        giữ nguyên flow cũ (Review 1/2)

    → solve_schedule() chạy variantCount lần (mặc định 3), mỗi lần random_seed khác nhau
    → mỗi lần ra 1 ScheduleVersion DRAFT riêng
```
- Sửa `services/councils.py::create_council()`: đọc đúng vai từ `Council` (sửa lỗi H — đang hardcode `"REVIEWER"`)
- Sửa câu SQL H11 (`schedule_operations.py:377-389`): nếu `continuity_source_round_id` có giá trị, query theo `round_id` cụ thể; nếu không, giữ fallback theo `type` (không phá round cũ chưa cấu hình)
- Xóa S4/S5 hardcode cũ (bonus buổi sáng, cờ has-day vô nghĩa) trong `_candidate_soft_scores()`, thêm S2 (CouncilFit), S3 (gom project_type), S8, S9 theo thứ tự ưu tiên Manager đã chọn (`softWeightsOrder`)

**File bị ảnh hưởng:** `routes/schedule_operations.py`, `services/councils.py`, `scheduler/scheduler.py`, `scheduler/candidates.py` (chỉ thêm, không đổi cấu trúc atomic reviewer-set).

**Tiêu chí hoàn thành:**
- Round có `uses_council_roles = FALSE` (Review 1/2) — hành vi **y hệt trước khi sửa**, chạy full test suite cũ, không regression
- Round có `uses_council_roles = TRUE` — tạo đúng 3 `ScheduleVersion`, mỗi version có vai CT/TK/TV đúng theo council đã lập, `council_members.assignment` lưu đúng vai (không còn cứng `"REVIEWER"`)
- H11 dùng `continuity_source_round_id` khi có, fallback khi không có

**Rủi ro:** cao — đây là điểm chạm vào code production. Bắt buộc: chạy song song A/B trên môi trường staging trước khi bật `uses_council_roles = TRUE` cho round thật đầu tiên; có thể tắt cờ để rollback ngay lập tức nếu phát hiện lỗi.

---

## Phase 6 — API so sánh phương án + gán phòng

**Mục tiêu:** Manager xem 3 phương án, chọn 1, gán phòng, rồi công bố — đúng luồng UI đã thiết kế.

**Việc cần làm:**
- `GET /rounds/{round_id}/schedule/versions` (đã có) — FE dùng để hiển thị 3 phương án song song
- `POST /schedule/versions/{version_id}/select` — đánh dấu phương án đang xử lý tiếp (mới, nhẹ — chỉ set 1 cờ trên `schedule_versions`)
- Gán phòng: dùng lại cơ chế `room_id` hiện có trên `schedule_assignments`, không cần API mới, chỉ cần FE
- Publish: giữ nguyên guard đã có — không cho công bố khi còn phiên thiếu phòng

**File bị ảnh hưởng:** `routes/schedule_operations.py` (thêm 1 endpoint nhỏ), không đổi gì ở `schedule_assignments`/`room` logic đã có.

**Tiêu chí hoàn thành:** FE gọi được 3 API (list versions, select version, existing room-assignment) đúng theo luồng 6 bước trong mockup.

**Rủi ro:** thấp — chủ yếu là FE work, BE chỉ thêm 1 endpoint nhỏ.

---

## Phase 7 — Frontend

**Mục tiêu:** dựng UI thật theo mockup [council-schedule-config-flow.html](./mockup/council-schedule-config-flow.html).

**Việc cần làm:**
- 6 màn luồng chính (Cấu hình → Ràng buộc cặp → Xem trước → So sánh phương án → Gán phòng → Công bố)
- 2 màn quản lý dữ liệu (Giảng viên, Đề tài)
- Toàn bộ label tiếng Việt tự nhiên, không hiện tên biến kỹ thuật; danh sách ưu tiên dùng kéo-thả; trọng số α dùng lựa chọn rời rạc — đúng theo mockup đã duyệt

**File bị ảnh hưởng:** nằm ngoài phạm vi repo backend này (`apps/web` hoặc repo FE riêng).

**Tiêu chí hoàn thành:** golden path test tay: setup skill → nhập năng lực → cấu hình round → xem preview → chạy xếp lịch → so sánh phương án → gán phòng → công bố, không lỗi ở bước nào.

---

## Bảng tổng hợp phụ thuộc giữa các phase

```
Phase 0 (quyết định)
   │
   ▼
Phase 1 (schema) ──────────────┐
   │                           │
   ▼                           ▼
Phase 2 (API dữ liệu nền)   Phase 3 (council_formation.py, test độc lập)
   │                           │
   └───────────┬───────────────┘
               ▼
        Phase 4 (API cấu hình round + preview)
               │
               ▼
        Phase 5 (nối vào scheduler thật — rủi ro cao)
               │
               ▼
        Phase 6 (API so sánh phương án + gán phòng)
               │
               ▼
        Phase 7 (Frontend)
```

Phase 2 và Phase 3 làm **song song được** — không phụ thuộc lẫn nhau, chỉ cùng phụ thuộc Phase 1. Phase 5 là nút thắt duy nhất bắt buộc phải xong Phase 3+4 trước, và là phase duy nhất bắt buộc review kỹ + rollback plan trước khi merge.
