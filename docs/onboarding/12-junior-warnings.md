# 12. Những thứ Junior cần đặc biệt chú ý

Mỗi mục dưới đây được gắn nhãn:

- **[Xác nhận từ code]** — tôi đã đọc trực tiếp trong repo, đây là sự thật.
- **[Nhận định]** — suy luận của tôi. Có thể sai. Hỏi team trước khi hành động theo.

---

## 12.1 Bảy chỗ dễ gây bug nhất

### ① SQL thô không có type-safety — **[Xác nhận từ code]**

Không có ORM, nên gõ sai tên cột **không** bị lint bắt, **không** bị type checker bắt. Nó chỉ nổ lúc chạy — và nếu nhánh code đó hiếm khi chạy, nó nổ trên production.

```python
db.execute(text("SELECT statuss FROM rounds WHERE id = :id"), {"id": 1})
#                       ^^ ruff im lặng, mypy im lặng
```

**Phòng thân:**
- Copy tên cột từ migration hoặc từ `\d ten_bang` trong psql, đừng gõ tay.
- Mọi nhánh code có SQL mới đều phải có test đi qua.
- Sửa xong chạy ngay `docker compose exec -T api python -m pytest tests/test_xxx.py -q`.

### ② Bẫy `db.begin()` — **[Xác nhận từ code, có ghi trong CLAUDE.md]**

Một câu `SELECT` chạy trước `with db.begin():` sẽ tự mở transaction ngầm và làm `db.begin()` nổ lỗi `A transaction is already begun`.

```python
# ❌
row = db.execute(text("SELECT ...")).one()
with db.begin():                              # 💥 InvalidRequestError
    ...

# ✅
row = db.execute(text("SELECT ...")).one()
db.rollback()
with db.begin():
    ...
```

Đây là lỗi số một mà người mới dính. Nếu thấy `InvalidRequestError` nói về transaction, tìm ngay câu đọc đứng trước.

### ③ `groups.project_id` được phép NULL — **[Xác nhận từ code, migration 0019]**

Nhóm tồn tại được trước khi có đề tài. Chọn sai kiểu JOIN là mất dữ liệu hoặc lộ dữ liệu:

```sql
-- Liệt kê nhóm → LEFT JOIN, nếu không nhóm chưa có đề tài BIẾN MẤT
FROM groups g LEFT JOIN projects p ON p.id = g.project_id

-- Trong phạm vi round/session → INNER JOIN mới đúng
FROM sessions s JOIN groups g ON g.id = s.group_id
                JOIN projects p ON p.id = g.project_id
```

Bug kiểu này rất khó phát hiện: hệ thống chạy bình thường, chỉ thiếu vài dòng, và không ai để ý cho tới khi có người hỏi "sao nhóm tôi không thấy trong danh sách".

### ④ Route `target_*` gọi lại route cũ — **[Xác nhận từ code]**

```python
# target_schedule_contract.py
from app.routes.schedule_operations import run_scheduler
result = run_scheduler(round_id, payload, db, user)
```

**Sửa hàm gốc → route target đổi theo.** Bạn có thể vô tình phá endpoint mà mình không hề mở file.

**Phòng thân:** trước khi sửa handler, chạy `grep -rn "ten_ham" apps/api/app/routes/` xem có ai gọi lại không.

### ⑤ Quên `_require()` = endpoint mở toang — **[Xác nhận từ code]**

Không có middleware phân quyền, không có decorator. Nếu handler mới của bạn thiếu dòng `_require(...)`, **mọi user đã đăng nhập đều gọi được**, kể cả sinh viên gọi API của Manager.

Không có gì cảnh báo bạn. Không test nào tự động phát hiện. Chỉ có review của con người.

### ⑥ Dịch `IntegrityError` bằng cách dò chuỗi — **[Xác nhận từ code]**

```python
constraint = str(getattr(exc, "orig", exc))
if "uq_active_semester" in constraint:
```

Đổi tên index trong migration mà quên sửa chuỗi này → mã lỗi trả về sai, frontend hiển thị sai thông báo, và **không có test nào bắt được** (vì test cũng chỉ kiểm tra status 409).

Cách chuẩn hơn có trong `committee_service.py`:

```python
cause = getattr(exc, "orig", None)
if not isinstance(cause, ForeignKeyViolation):
    return False
diag = getattr(cause, "diag", None)
return (getattr(diag, "constraint_name", None) or "") == ROUND_COMMITTEE_FK
```

### ⑦ Một tài khoản nhiều role → `CurrentUser` chỉ giữ một — **[Xác nhận từ code, hệ quả là Nhận định]**

```sql
JOIN account_roles ar ON ar.account_id = a.id
...
ORDER BY ar.role LIMIT 1
```

`CurrentUser` chỉ có **một** chuỗi `role`. Với tài khoản vừa là MANAGER vừa là LECTURER, role nào thắng phụ thuộc thứ tự của kiểu enum trong Postgres.

**[Nhận định]** Đây là điểm mờ ám thật sự trong thiết kế. Nếu gặp bug "user không thấy dữ liệu đáng lẽ phải thấy" hoặc "user bị 403 dù có quyền", nghi ngờ chỗ này trước tiên.

---

## 12.2 Convention team đang dùng

Tất cả đều **[Xác nhận từ code]** — quan sát được qua nhiều file.

| # | Convention | Ví dụ |
|---|---|---|
| 1 | `_require(user, ...)` là dòng đầu tiên của handler ghi dữ liệu | mọi route |
| 2 | Ghi dữ liệu luôn bọc trong `with db.begin():` | mọi route |
| 3 | Mọi ghi dữ liệu kèm `INSERT INTO audit_events` cùng transaction | mọi route |
| 4 | `detail` là dict `{"code", "message"}`, không phải chuỗi | phần lớn route |
| 5 | Mã lỗi VIẾT_HOA_GẠCH_DƯỚI, ổn định lâu dài | `domain/errors.py` |
| 6 | SQL luôn dùng tham số `:name`, tuyệt đối không f-string | mọi nơi |
| 7 | Sau khi ghi, đọc lại qua `*_or_404()` rồi mới return | `create_semester` |
| 8 | Service **nhận** `db`, không tự tạo Session | mọi service |
| 9 | Domain thuần: không import fastapi/sqlalchemy | `domain/*.py` |
| 10 | Alias `Db`, `User`, `SettingsDep` khai báo đầu file route | mọi route |
| 11 | Độ dài dòng tối đa 100, kiểm bằng ruff, target `py311` | `pyproject.toml` |
| 12 | Comment giải thích **WHY**, không phải WHAT | xem `resource_locks.py` |
| 13 | Migration đặt **tên** cho constraint | `uq_active_semester` |
| 14 | `sorted()` ở mọi vòng lặp trong scheduler (tính tái lập) | `candidates.py` |
| 15 | Khoá advisory lấy theo thứ tự đã sắp xếp (tránh deadlock) | `resource_locks.py` |

Về comment, đây là ví dụ đúng chuẩn repo — nói **vì sao**, không nói **cái gì**:

```python
# apps/api/app/services/resource_locks.py
def resource_lock_key(namespace: str, resource_id: int) -> int:
    """Return a deterministic signed PostgreSQL int8 key.

    The namespace is part of the key so a reviewer and room with the same id
    never accidentally share a lock.  Truncation may collide (and therefore
    only over-serialize), but can never produce an out-of-range int8 value.
    """
```

---

## 12.3 Pattern lặp lại nhiều nhất

Nhận ra 5 pattern này là bạn đọc được 80% repo:

**1. Khuôn handler ghi dữ liệu** *(xuất hiện hàng chục lần)*

```python
_require(...) → try → with db.begin() → khoá → SQL → audit
             → except DomainError/IntegrityError → đọc lại → return
```

**2. Khoá trước khi đọc-rồi-ghi**

```python
"SELECT status FROM semesters WHERE id = :id FOR UPDATE"
"SELECT pg_advisory_xact_lock(:key)"
```

**3. Đọc-hết-một-lần rồi tính thuần** — `_round_input()` trong scheduler. Pattern mạnh nhất repo, nên bắt chước.

**4. Bọc-và-chuyển-tiếp** — mọi file `target_*.py`.

**5. Transactional outbox** — ghi `outbox_jobs` trong transaction, worker gửi sau.

---

## 12.4 File quan trọng nhất

Đọc kỹ 8 file này là hiểu được xương sống hệ thống:

| File | Dòng | Vì sao |
|---|---|---|
| `apps/api/app/main.py` | 193 | Toàn bộ cách app được lắp ráp |
| `apps/api/app/auth.py` | 58 | Mọi request đều đi qua |
| `apps/api/app/database.py` | 18 | Nguồn của mọi kết nối DB |
| `apps/api/app/config.py` | 29 | Mọi cấu hình |
| `apps/api/app/domain/errors.py` | 11 | Nền tảng xử lý lỗi |
| `apps/api/app/services/access.py` | 161 | Quyết định ai thấy dữ liệu gì |
| `apps/api/app/api_contract.py` | 298 | Hợp đồng API mới |
| `apps/api/app/scheduler/validator.py` | 281 | Luật cứng H1–H13 |

---

## 12.5 File KHÔNG nên sửa khi chưa hiểu rõ

| File | Vì sao nguy hiểm |
|---|---|
| `app/main.py` | Sai thứ tự middleware/router → hỏng CSRF hoặc routing toàn hệ thống |
| `app/auth.py` | Sửa sai → hoặc thủng bảo mật, hoặc không ai đăng nhập được |
| `app/scheduler/validator.py` | Nới lỏng một luật = lịch sai được đưa vào production |
| `app/scheduler/scheduler.py` | Đổi hàm mục tiêu ảnh hưởng mọi lần chạy; dễ khiến solver chậm hàng chục lần |
| `migrations/versions/*` **đã merge** | **Tuyệt đối không sửa.** Người khác đã chạy rồi. Luôn thêm file mới |
| `app/response_models.py` | Model dùng chung nhiều endpoint. Chỉ **thêm**, đừng **sửa** |
| `app/api_contract.py` | `parse_external_id` / `success_payload` được dùng khắp nơi |
| `tools/bootstrap_database.py` | Sai là container không khởi động được |

---

## 12.6 Technical debt và code smell

### Rõ ràng, xác nhận được từ code

**① Route file khổng lồ**

```text
master_data.py         2097 dòng, 40 endpoint
schedule_operations.py 1854 dòng, 19 endpoint
manager_extensions.py  1107 dòng, 25 endpoint
```

Chiếm 34% tổng số dòng của `app/`. Merge conflict thường xuyên khi nhiều người cùng làm.

**② `_require()` bị copy ở 6 file khác nhau**

```text
master_data.py:120    manager_extensions.py:67   operations.py:31
results.py:36         schedule_operations.py:65  room_assignment.py:51
```

Cùng một hàm 3 dòng, 6 bản sao. Muốn đổi cách phân quyền (VD: thêm log) phải sửa 6 chỗ. Vi phạm DRY một cách hiển nhiên.

`room_assignment.py:51` thậm chí có chữ ký **khác** (`_require(user)` không nhận `*roles`) — dễ gây nhầm khi copy code giữa các file.

**③ Không có logging** — **[Xác nhận từ code]**

`grep -rn "import logging|getLogger|logger\." apps/api/app/` → **không kết quả nào**. Xem [07-errors-logging.md](07-errors-logging.md) mục 7.6.

**④ Hai định dạng API song song**

Route cũ `{"detail": ...}` vs route target `{"error": {...}}`; id số vs id có tiền tố; snake_case vs camelCase. Nhân đôi bề mặt API cần bảo trì và test.

**⑤ `response_models.py` dùng `extra="allow"` toàn cục**

Model **mô tả** response chứ chưa **kiểm soát** nó. Một câu `SELECT *` vô ý sẽ đẩy thêm cột ra API mà không có gì chặn — kể cả cột nhạy cảm.

**⑥ Code chết còn trong repo**

```text
apps/worker/            stub "noop", không ai dùng
apps/api/app/jobs.py    JobStore in-memory từ Phase 01
```

**⑦ Dò chuỗi để nhận diện constraint** — mục 12.1 ⑥.

**⑧ Từ vựng trạng thái phải dịch qua lại**

`app/domain/status_compat.py` tồn tại để ánh xạ giữa hai bộ từ vựng trạng thái: DB dùng `PENDING_D11 → ELIGIBLE_D12 → ...`, spec API mới dùng `FORMED/ASSIGNED/DISBANDED`. Docstring giải thích lý do là để **không phải migrate schema**. Hợp lý, nhưng là một lớp dịch thuật phải nuôi mãi.

### [Nhận định] — góc nhìn của tôi, hãy tự đánh giá

**Về việc route file to:** đây **có vẻ** là hệ quả của việc phát triển theo phase nhanh (tên test `test_phase01` → `test_phase10` cho thấy điều đó), không phải quyết định kiến trúc. Xu hướng gần đây (`committee_service.py`, `timeframe_service.py`) cho thấy team đang tách dần ra. **Nếu bạn viết tính năng mới, hãy noi theo hai file service đó.**

**Về việc không có ORM:** với domain nặng SQL này, tôi cho là **lựa chọn đúng**. Cái giá phải trả (không type-safe) được bù bằng 72 file test. Đừng đề xuất thêm ORM — sẽ phải viết lại toàn bộ.

**Về việc không có logging:** đây là khoảng trống **thật sự**, không phải chuyện thẩm mỹ. Với 174 endpoint và một solver chạy hàng chục giây, khi có sự cố bạn gần như mù. **[Nhận định]** Nếu được hỏi "nên cải thiện gì trước", tôi chọn cái này.

**Về hai định dạng API:** chiến lược migration **đúng bài** (có tag phân biệt, có header deprecation, có đếm lượt gọi route cũ). Rủi ro là nó **kẹt lại nửa đường mãi mãi** — hãy hỏi team xem có timeline gỡ bỏ route cũ không.

---

## 12.7 Có gì bất thường trong kiến trúc không?

**Bất thường nhưng CÓ LÝ DO chính đáng:**

| Điều bất thường | Lý do hợp lý |
|---|---|
| Không có ORM | Domain phụ thuộc nặng vào tính năng riêng của Postgres |
| Không có repository layer | Với SQL thô, thêm một lớp bọc chỉ tăng chi phí, không thêm giá trị |
| Hàng đợi bằng bảng SQL | Đúng mức độ phức tạp cần thiết; thêm Redis là over-engineering ở quy mô này |
| `X-Test-Session` | Đánh đổi có ý thức, được bảo vệ bởi điều kiện `APP_ENV=test` |
| Validator kiểm tra lại thứ solver đã đảm bảo | Defence in depth cho hệ thống ảnh hưởng tới người thật |
| `num_search_workers = 1` | Đổi tốc độ lấy tính tái lập — đúng ưu tiên cho bài toán này |
| Council bất biến | Bảo toàn tính truy vết lịch sử |

**Bất thường và ĐÁNG NGỜ [Nhận định]:**

| Điều | Vì sao đáng ngờ |
|---|---|
| `CurrentUser` chỉ có một role | Multi-role bị xử lý bằng `ORDER BY ... LIMIT 1` — không tường minh |
| `_valid_csrf` tự mở Session riêng | Một query DB thêm cho **mọi** request ghi. Có thể dùng cache được |
| `get_current_user` gọi `db.commit()` | Dependency mà gây tác dụng phụ lên transaction là điều bất ngờ, dễ gây bug |
| Không có phân trang thật ở nhiều endpoint list | `meta={"page": 1, "pageSize": len(rows), "total": len(rows)}` là phân trang giả |
| `openapi.tmp.json` 400KB trong repo | File sinh tự động, không nên commit |

---

## 12.8 Bảy quy tắc sinh tồn cho tuần đầu

1. **Copy handler gần nhất trong cùng file**, đừng viết từ số 0. Tính nhất quán > sáng tạo.
2. **Chạy test trước và sau mỗi thay đổi.** `uv run pytest -m "not integration" -q` chỉ mất vài giây.
3. **Trước khi sửa hàm, grep xem ai gọi nó.** Route `target_*` gọi lại route cũ.
4. **Đọc migration trước khi viết SQL.** Đừng đoán tên cột.
5. **Không bao giờ sửa migration đã merge.** Luôn thêm file mới.
6. **Hỏi khi thấy hai cách làm khác nhau cho cùng một việc.** Repo đang giữa quá trình migration; một trong hai là cách cũ.
7. **DB local là dữ liệu test** — cứ `docker compose down -v` thoải mái khi cần làm lại từ đầu.
