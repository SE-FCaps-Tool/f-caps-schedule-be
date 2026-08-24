# 13. Lộ trình đọc code

Thiết kế cho 5 ngày đầu. Mỗi bước có: **đọc gì**, **hiểu gì**, và quan trọng không kém — **CHƯA cần quan tâm gì**.

Nguyên tắc xuyên suốt: **chạy được trước, hiểu sau.** Đừng đọc code trong khi hệ thống chưa chạy trên máy bạn.

---

## Ngày 1 — Chạy được và nhìn thấy hệ thống sống

### Bước 1.1 — Dựng stack

```powershell
docker compose up --build
```

Mở:
- http://localhost:8000/health → phải thấy `{"status":"ok","service":"api"}`
- http://localhost:8000/docs → Swagger UI với 174 endpoint

Đăng nhập thử bằng `manager1@gmail.com` / `SchedulerDemo2026!`.

**Hiểu:** hệ thống gồm 3 container; API ở cổng 8000; DB ở cổng 15432 (nhìn từ máy host).
**Chưa cần quan tâm:** Dockerfile viết gì, bootstrap làm gì.

### Bước 1.2 — Nhìn dữ liệu thật

```powershell
docker compose exec -T postgres psql -U scheduler -d scheduler -c "\dt"
docker compose exec -T postgres psql -U scheduler -d scheduler -c "\d rounds"
docker compose exec -T postgres psql -U scheduler -d scheduler -c "SELECT id, code, name, status FROM semesters"
docker compose exec -T postgres psql -U scheduler -d scheduler -c "SELECT id, type, status FROM rounds LIMIT 10"
```

**Hiểu:** 44 bảng, và hình dạng thật của dữ liệu.
**Chưa cần quan tâm:** hiểu hết mọi bảng. Chỉ cần nhớ `semesters`, `rounds`, `groups`, `sessions`, `schedule_versions`.

### Bước 1.3 — Đọc nghiệp vụ

```text
docs/project-reference/PRD_CapstoneScheduler_v1.0.md
docs/project-reference/ERD_CapstoneScheduler_v1.0.md   ← mục "Quyết định thiết kế" đọc kỹ
```

**Hiểu:** bài toán nghiệp vụ. Đợt đánh giá là gì, tại sao Defense 1.2 phải giữ hội đồng cũ.
**Chưa cần quan tâm:** chi tiết từng luật H1–H13.

> Kết thúc ngày 1: bạn phải giải thích được cho người khác *sản phẩm này làm gì* mà không cần mở code.

---

## Ngày 2 — Xương sống của ứng dụng

Bốn file, tổng cộng **296 dòng**. Đọc **từng dòng**, không lướt.

### Bước 2.1 — `apps/api/app/config.py` (29 dòng)

**Hiểu:** cấu hình đến từ đâu; `@lru_cache` nghĩa là singleton; `APP_ENV` điều khiển những gì.
**Chưa cần quan tâm:** ý nghĩa nghiệp vụ của `semester_min_duration_days`.

### Bước 2.2 — `apps/api/app/database.py` (18 dòng)

**Hiểu:** phân biệt Engine (pool, một cho cả process) và Session (một cho mỗi request); `yield` trong dependency dùng để dọn dẹp.
**Chưa cần quan tâm:** tuning pool.

### Bước 2.3 — `apps/api/app/auth.py` (58 dòng)

**Hiểu:** hai nhánh (test và thật); `CurrentUser` chỉ có 3 field; câu SQL kiểm tra 4 điều kiện (chưa thu hồi / chưa hết hạn / chưa quá idle / account ACTIVE).
**Chưa cần quan tâm:** vì sao có `ORDER BY ar.role LIMIT 1` — quay lại sau khi đọc mục 12.1 ⑦.

### Bước 2.4 — `apps/api/app/main.py` (193 dòng)

**Hiểu:**
- `create_app()` lắp ráp toàn bộ ứng dụng.
- Hai middleware và **thứ tự** của chúng.
- Hai exception handler, và `_is_target_route()` quyết định định dạng lỗi bằng cách đọc tag.
- 17 lệnh `include_router`.

**Chưa cần quan tâm:** phần custom Swagger UI, chi tiết chuỗi CSP.

**Tài liệu đi kèm:** [03-architecture-layers.md](03-architecture-layers.md)

> Kết thúc ngày 2: vẽ lại được sơ đồ "request đi từ Uvicorn tới handler qua những chặng nào".

---

## Ngày 3 — Trace một request bằng tay

Đây là ngày quan trọng nhất. Đừng bỏ qua.

### Bước 3.1 — Đọc trace mẫu

[04-request-lifecycle.md](04-request-lifecycle.md) — đọc song song với file code thật, mở hai cửa sổ.

Endpoint mẫu: `create_semester` tại [apps/api/app/routes/master_data.py:1020](../../apps/api/app/routes/master_data.py).

### Bước 3.2 — Tự trace một endpoint khác, không xem tài liệu

Chọn `POST /api/v1/groups/{group_id}/leader` — `master_data.py:1000`, khoảng 15 dòng.

Tự trả lời:

```text
[ ] Ai được gọi endpoint này?
[ ] Payload gồm những field nào, validate ra sao?
[ ] Có bao nhiêu câu SQL chạy?
[ ] Vì sao có "FOR UPDATE" trong câu SELECT đầu tiên?
[ ] Nếu student_id không phải thành viên nhóm thì chuyện gì xảy ra?
[ ] Vì sao phải UPDATE hai lần (một để bỏ leader cũ, một để đặt leader mới)?
[ ] audit_events ghi những gì?
[ ] Endpoint target nào bọc nó lại? Nó đổi gì?
```

Câu cuối: đáp án ở `target_group_project.py:258` — nó **đổi mã lỗi** `LEADER_MEMBER_NOT_FOUND` thành `LEADER_NOT_ACTIVE_MEMBER`.

### Bước 3.3 — Đọc một file domain

[apps/api/app/domain/master_data.py](../../apps/api/app/domain/master_data.py) — 48 dòng.

**Hiểu:** vì sao layer này không import gì ngoài `DomainError`; vì sao nó test được không cần Docker.

### Bước 3.4 — Chạy test

```powershell
Push-Location apps/api
uv run pytest -m "not integration" -q
Pop-Location
```

Mở `tests/test_master_data.py` xem test viết thế nào.

> Kết thúc ngày 3: tự trace được bất kỳ endpoint nào mà không cần hỏi ai.

---

## Ngày 4 — Dữ liệu và phân quyền

### Bước 4.1 — `apps/api/app/services/access.py` (161 dòng)

**Hiểu:** phân quyền có **hai tầng** — RBAC (`_require`, trả 403) và row scoping (`access.py`, **lọc bớt** kết quả). Đây là chỗ người mới hay nhầm nhất.

**Chưa cần quan tâm:** chi tiết từng câu JOIN trong `visible_session_ids`.

**Tài liệu đi kèm:** [06-auth.md](06-auth.md)

### Bước 4.2 — `apps/api/app/services/semester_queries.py` (161 dòng)

**Hiểu:** hình dạng của một service điển hình; vì sao có `FOR UPDATE`; advisory lock dùng để làm gì.

### Bước 4.3 — Lướt migration

```powershell
ls apps/api/migrations/versions
```

Đọc **tên** của cả 39 file — chúng kể lại lịch sử tiến hoá sản phẩm. Rồi mở hai file:

- `0002_domain_model.py` — schema nền tảng
- `0019_nullable_group_project.py` — hiểu vì sao `groups.project_id` NULL được

**Chưa cần quan tâm:** đọc hết nội dung mọi migration.

**Tài liệu đi kèm:** [05-database.md](05-database.md)

### Bước 4.4 — `apps/api/app/worker.py` (29 dòng) + đọc lướt `notification_dispatcher.py`

**Hiểu:** pattern outbox; `FOR UPDATE SKIP LOCKED`; vì sao không gửi thông báo ngay trong request.

> Kết thúc ngày 4: giải thích được vì sao hai user gọi cùng một endpoint lại nhận số dòng dữ liệu khác nhau.

---

## Ngày 5 — Feature phức tạp nhất

### Bước 5.1 — Đọc walkthrough

[10-feature-walkthrough.md](10-feature-walkthrough.md)

### Bước 5.2 — Đọc code scheduler theo thứ tự

```text
1. app/scheduler/models.py       (111 dòng)  các dataclass — đọc trước để hiểu từ vựng
2. app/scheduler/candidates.py   (159 dòng)  lọc cứng, sinh tổ hợp
3. app/scheduler/validator.py    (281 dòng)  H1–H13
4. app/scheduler/scheduler.py    (268 dòng)  CP-SAT — khó nhất, đọc cuối
```

**Hiểu:**
- Vì sao lọc **trước** rồi mới đưa cho solver.
- Vì sao **kiểm tra lại** thứ solver vừa đảm bảo.
- Thủ thuật `primary_bonus` để mã hoá ưu tiên từ điển.
- Vì sao `num_search_workers = 1`.

**Chưa cần quan tâm:** hiểu CP-SAT hoạt động bên trong ra sao. Bạn chỉ cần biết cách **mô tả bài toán** cho nó.

### Bước 5.3 — Chạy benchmark

```powershell
Push-Location apps/api
uv run pytest tests/test_benchmark.py -q
Pop-Location
```

74 nhóm / 26 giảng viên / 40 khung giờ / 4 phòng, phải xong dưới 60 giây với 0 vi phạm.

### Bước 5.4 — Đọc cảnh báo

[12-junior-warnings.md](12-junior-warnings.md) — giờ bạn đã đủ ngữ cảnh để hiểu vì sao từng mục là vấn đề.

> Kết thúc ngày 5: nhận task đầu tiên được rồi.

---

## Sau tuần đầu — đọc khi cần

| Khi bạn gặp | Đọc |
|---|---|
| Phải làm việc với route target / hợp đồng API mới | `app/api_contract.py`, `docs/api/api-contract-migration.md` |
| Task về khung giờ | `app/services/timeframe_service.py`, `app/domain/timeframes.py` |
| Task về hội đồng | `app/services/committee_service.py`, `app/domain/committees.py` |
| Task về kết quả / khắc phục | `app/routes/results.py`, `app/domain/result_workflow.py` |
| Task về gán phòng | `app/services/room_assignment.py` |
| Task về nhập Excel | `tools/import_excel_database.py` |
| Muốn biết chuyện gì mới xảy ra gần đây | `docs/journals/` |

---

## Bốn thứ KHÔNG nên đọc trong tuần đầu

| Thứ | Vì sao |
|---|---|
| `apps/worker/` | Code chết |
| `apps/api/app/jobs.py` | Code chết |
| `openapi.tmp.json` | File sinh tự động, 400KB |
| Toàn bộ `master_data.py` từ đầu tới cuối | 2097 dòng. Đọc theo **endpoint bạn đang cần**, không đọc tuần tự |

---

## Bài kiểm tra tự đánh giá

Trả lời được hết là bạn sẵn sàng nhận task:

```text
[ ]  1. Request POST đi qua những chặng nào trước khi tới thân hàm handler?
[ ]  2. Vì sao service phải NHẬN db thay vì tự tạo Session?
[ ]  3. Khác nhau giữa _require() và services/access.py là gì?
[ ]  4. Vì sao domain/ không được import fastapi?
[ ]  5. Chuyện gì xảy ra khi có exception bên trong `with db.begin():`?
[ ]  6. Vì sao cùng một lỗi lại có hai định dạng JSON khác nhau?
[ ]  7. Route target_* khác route thường ở những điểm nào?
[ ]  8. Muốn thêm cột vào bảng rounds thì làm những bước gì?
[ ]  9. Vì sao scheduler kiểm tra lại kết quả mà solver vừa sinh ra?
[ ] 10. Vì sao thông báo không được gửi ngay trong request?
[ ] 11. APP_ENV=test bật thêm những gì?
[ ] 12. Vì sao candidates.py dùng sorted() ở mọi vòng lặp?
```

Đáp án nằm rải trong bộ tài liệu này — nếu bí ở câu nào, quay lại đúng file tương ứng.
