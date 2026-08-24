# 10. Bóc một feature từ A đến Z: chạy thuật toán xếp lịch

Feature được chọn: **`POST /api/v1/rounds/{round_id}/schedule/run`** — trái tim của cả sản phẩm.

Chọn feature này vì nó chạm vào **mọi layer** có trong repo: route → domain → services → scheduler engine → DB, cộng thêm state machine, transaction, và snapshot.

## 10.1 Feature này làm gì (bằng tiếng Việt đời thường)

> Manager bấm "Chạy xếp lịch" cho đợt Review 1. Hệ thống lấy danh sách nhóm đã đăng ký, khung giờ đã mở, giảng viên đã nhận lời mời và đã khai báo giờ rảnh, rồi tìm một cách xếp sao cho không vi phạm luật nào. Kết quả lưu thành **một phương án nháp** (`ScheduleVersion` trạng thái `DRAFT`). Manager có thể chạy nhiều lần với seed khác nhau, so sánh, rồi mới chọn một phương án để kích hoạt.

Điểm quan trọng: **chạy solver KHÔNG làm thay đổi lịch thật.** Nó chỉ tạo thêm một bản nháp. Chỉ khi `activate` rồi `publish` thì lịch mới có hiệu lực.

## 10.2 Toàn bộ file liên quan, theo thứ tự thực thi

```text
 1. apps/api/app/main.py                       gắn router, middleware
 2. apps/api/app/routes/schedule_operations.py ★ ENTRY POINT (dòng 702)
       ├─ class ScheduleRunPayload            (dòng 70)  schema đầu vào
       ├─ _require()                                     RBAC
       ├─ _validate_scheduler_inputs()        (dòng 128) tiền kiểm tra
       ├─ _round_input()                      (dòng 263) đọc DB → RoundInput
       └─ solve_schedule()                               gọi engine
 3. apps/api/app/services/semester_queries.py  ensure_round_semester_writable()
 4. apps/api/app/domain/transitions.py         transition_round()  state machine
 5. apps/api/app/domain/enums.py               RoundStatus
 6. apps/api/app/scheduler/models.py           RoundInput, Candidate, ScheduledSession
 7. apps/api/app/scheduler/candidates.py       generate_candidates()
 8. apps/api/app/scheduler/validator.py        _eligible(), valid_h11_waiver(), validate_schedule()
 9. apps/api/app/domain/round_types.py         hằng số loại đợt
10. apps/api/app/scheduler/scheduler.py        solve_schedule()  ← CP-SAT ở đây
11. apps/api/app/scheduler/snapshot.py         build_input_snapshot()
12. apps/api/app/response_models.py            ScheduleRunResponse
13. apps/api/migrations/versions/...           schedule_versions, schedule_assignments, scheduler_jobs
```

Và lớp áo cho frontend mới:

```text
14. apps/api/app/routes/target_schedule_contract.py   POST /rounds/{id}/schedules/generate
```

## 10.3 Sơ đồ luồng

```text
POST /api/v1/rounds/7/schedule/run   {"timeLimitSeconds": 30, "randomSeed": 42}
   │
   ▼
┌─ ROUTE: run_scheduler()  schedule_operations.py:703 ─────────────────────┐
│                                                                          │
│  _require(user, "ADMIN", "MANAGER")                                      │
│                                                                          │
│  with db.begin():                          ← MỘT transaction cho TẤT CẢ  │
│    │                                                                     │
│    ├─1─ ensure_round_semester_writable(db, round_id)   [services]        │
│    │      → SELECT ... FOR UPDATE, chặn nếu học kỳ đã ARCHIVED           │
│    │                                                                     │
│    ├─2─ SELECT status, reviewer_count FROM rounds WHERE id = :id FOR UPDATE│
│    │                                                                     │
│    ├─3─ transition_round(current, SCHEDULING)          [domain]          │
│    │      → 422 nếu chuyển trạng thái không hợp lệ                       │
│    │    _validate_scheduler_inputs(...)                                  │
│    │      → báo lỗi CHÍNH XÁC trước khi tốn công chạy solver             │
│    │    UPDATE rounds SET status = 'SCHEDULING'                          │
│    │                                                                     │
│    ├─4─ _round_input(db, round_id)                                       │
│    │      → hàng chục câu SELECT gom thành RoundInput (dataclass thuần)  │
│    │      → trả về (context, groups, timeslots, reviewers)               │
│    │                                                                     │
│    ├─5─ kiểm tra rỗng → DomainError ROUND_GROUPS_REQUIRED /              │
│    │                    ROUND_TIMESLOTS_REQUIRED /                       │
│    │                    ROUND_REVIEWERS_INSUFFICIENT                     │
│    │                                                                     │
│    ├─6─ solve_schedule(context, groups, timeslots, reviewers, ...)       │
│    │        │                                                            │
│    │        ├── generate_candidates()   candidates.py                    │
│    │        │     lọc cứng trước: eligibility, conflict, supervisor,     │
│    │        │     availability, H11 continuity → sinh mọi tổ hợp hợp lệ  │
│    │        │                                                            │
│    │        ├── dựng model CP-SAT       scheduler.py                     │
│    │        │     biến nhị phân 1 cái/candidate + ràng buộc + hàm mục tiêu│
│    │        │                                                            │
│    │        ├── solver.solve(model)     ← OR-Tools chạy ở đây            │
│    │        │                                                            │
│    │        └── validate_schedule()     validator.py                     │
│    │              kiểm tra lại H1–H13 trên lời giải                      │
│    │              ❌ có vi phạm → DomainError, transaction ROLLBACK       │
│    │                                                                     │
│    ├─7─ build_input_snapshot()          snapshot.py                      │
│    │      → đóng băng toàn bộ input thành JSON                           │
│    │                                                                     │
│    ├─8─ SELECT MAX(version_no)+1 ... ; INSERT INTO schedule_versions     │
│    ├─9─ INSERT INTO schedule_assignments        (mỗi nhóm 1 dòng)        │
│    ├─10─ INSERT INTO schedule_assignment_reviewers (kèm snapshot_name)   │
│    ├─11─ INSERT INTO scheduler_jobs   status = COMPLETED hoặc PARTIAL    │
│    └─12─ INSERT INTO audit_events     'SCHEDULER_RUN'                    │
│                                                                          │
│  ← thoát with = COMMIT                                                   │
│                                                                          │
│  return {"version_id": ..., "status": "DRAFT", "scheduled_count": ...,   │
│          "unscheduled": [...], "soft_scores": {...}}                     │
└──────────────────────────────────────────────────────────────────────────┘
```

## 10.4 Vai trò từng file

### `routes/schedule_operations.py` — nhạc trưởng

Đây là file lớn thứ hai repo (1854 dòng, 19 endpoint). Trong feature này nó đóng **cả bốn vai**: controller, service, repository, và điều phối viên transaction.

Schema đầu vào rất nhỏ:

```python
class ScheduleRunPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    random_seed: int = Field(default=0, alias="randomSeed")
    time_limit_seconds: float = Field(default=10, alias="timeLimitSeconds", gt=0, le=300)
```

- `alias="randomSeed"` — frontend gửi camelCase, Python dùng snake_case. `populate_by_name=True` cho phép nhận **cả hai** dạng.
- `gt=0, le=300` — chặn ngay tại schema: không ai đặt được giới hạn thời gian 1 giờ.
- `random_seed` — cùng seed + cùng dữ liệu = cùng kết quả. Đây là thứ khiến solver **tái lập được**, cực kỳ quan trọng khi debug.

### `domain/transitions.py` — máy trạng thái

```python
next_status = transition_round(current_status, RoundStatus("SCHEDULING"))
```

Hàm thuần: nhận trạng thái hiện tại + trạng thái mong muốn, trả về trạng thái mới hoặc ném `DomainError`. Không có DB, không có HTTP → test trong micro giây.

Đây là ví dụ mẫu mực cho việc **tách luật ra domain**: câu hỏi "đợt đang ở trạng thái PUBLISHED thì có được chạy lại solver không" là luật nghiệp vụ thuần tuý, không liên quan gì tới SQL.

### `_validate_scheduler_inputs()` — tiền kiểm tra

```python
def _validate_scheduler_inputs(db: Session, round_id: int, required_reviewer_count: int) -> None:
    """Raise a precise error before moving a round into scheduler state."""
```

Chạy trước solver để trả **thông báo lỗi cụ thể**. Không có nó, người dùng sẽ nhận "không xếp được lịch" mà không biết vì sao — trong khi lý do thật có thể chỉ là "nhóm G12 chưa có leader".

Chú ý câu SQL của nó dùng một cú pháp Postgres hay:

```sql
COUNT(gm.id) FILTER (WHERE gm.status = 'ACTIVE' AND gm.membership_role = 'LEADER') AS leader_count
```

`FILTER` cho phép đếm có điều kiện ngay trong `GROUP BY` — gọn hơn nhiều so với `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.

### `_round_input()` — biên giới DB → thế giới thuần

```python
def _round_input(db, round_id) -> tuple[RoundInput, list[int], list[tuple[...]], list[int]]:
```

Đây là hàm **quan trọng nhất về mặt kiến trúc** trong feature này. Nó là **ranh giới duy nhất** giữa "thế giới có DB" và "thế giới tính toán thuần".

Nó chạy hàng chục câu SELECT để gom về:

| Dữ liệu | Nguồn |
|---|---|
| Cấu hình đợt (loại, số reviewer, hạn mức H12, trọng số soft) | `rounds` |
| Nhóm tham gia + đề tài + trạng thái | `round_groups`, `groups`, `projects` |
| Khung giờ | `round_days`, `timeslots` |
| Giảng viên nhận lời mời | `round_invitations` |
| Giờ rảnh | `lecturer_availabilities` |
| Xung đột lợi ích | `conflict_declarations` |
| Người hướng dẫn | `project_supervisors` |
| Reviewer lần trước (cho luật H11) | version trước đó |
| Tải hiện tại trong học kỳ | các đợt khác |

...và đóng gói tất cả vào **một dataclass `RoundInput`** (định nghĩa ở `scheduler/models.py`).

**Vì sao thiết kế như thế?** Sau hàm này, **toàn bộ engine xếp lịch không cần chạm DB nữa**. Hệ quả:

1. Test engine bằng `RoundInput` dựng tay, không cần Postgres.
2. Solver chạy 30 giây mà không giữ kết nối DB làm gì.
3. Có thể serialize `RoundInput` ra JSON → tái hiện lại y hệt một lần chạy cũ.

Nếu chỉ học một bài từ toàn bộ tài liệu này, hãy học pattern đó: **đọc hết dữ liệu một lần, đưa vào cấu trúc thuần, rồi tính toán không cần DB.**

### `scheduler/candidates.py` — lọc cứng

```python
def generate_candidates(context, *, groups, timeslots, reviewers) -> list[Candidate]:
    for group_id in sorted(groups):
        if group_id in context.group_leader_valid and not context.group_leader_valid[group_id]:
            continue                                          # nhóm không có leader hợp lệ
        if not _eligible(context.round_type, context.group_status.get(group_id, "")):
            continue                                          # H9: trạng thái nhóm không phù hợp
        allowed_reviewers = [
            r for r in sorted(reviewers)
            if (r, project_id) not in context.conflicts                     # H8: xung đột lợi ích
            and r not in context.project_supervisors.get(project_id, set()) # H1: là GVHD
        ]
        for raw_timeslot in sorted(timeslots, key=lambda v: v[0]):
            ...
            available = [r for r in allowed_reviewers
                         if (r, timeslot_id) in context.lecturer_availability]   # H7: giờ rảnh
            if context.round_type in DEFENSE_1_2_TYPES and not valid_h11_waiver(context, group_id):
                continuity = set(context.prior_reviewer_ids.get(group_id, set()))
                continuity.update(context.remediation_verifier_ids.get(group_id, set()))
                available = [r for r in available if r in continuity]            # H11: giữ hội đồng cũ
            for reviewer_ids in _reviewer_tuples(context, available):
                candidates.append(Candidate(group_id, timeslot_id, start_at, end_at, day, part, reviewer_ids))
```

**Ý tưởng cốt lõi:** thay vì đưa mọi khả năng cho solver rồi bảo nó "đừng vi phạm luật", ta **loại bỏ trước** mọi tổ hợp bất khả thi. Không gian tìm kiếm nhỏ đi rất nhiều → solver chạy nhanh hơn nhiều bậc.

Một `Candidate` = "nhóm G nếu học ở khung giờ T với bộ reviewer R". Solver chỉ việc chọn tập con.

Chú ý mọi vòng lặp đều `sorted(...)`. Kết hợp với `random_seed` cố định, điều này đảm bảo **cùng input luôn cho cùng output**. Không có nó, tập candidate sẽ đổi thứ tự theo tâm trạng của `set` trong Python và kết quả sẽ không tái lập được.

Số reviewer mỗi buổi theo loại đợt: Review 1/2 = 2, Defense 1.1 = 3, Defense 1.2 và Defense 2 = 5. `_reviewer_tuples` dùng `itertools.combinations` để sinh mọi bộ.

### `scheduler/scheduler.py` — CP-SAT

```python
model = cp_model.CpModel()
variables = [model.new_bool_var(f"candidate_{i}") for i in range(len(candidates))]
```

Mỗi candidate ↔ một biến 0/1: "có chọn phương án này không".

Các ràng buộc:

```python
# Mỗi nhóm nhiều nhất một buổi (H4)
for indexes in by_group.values():
    model.add_at_most_one(variables[i] for i in indexes)

# Giới hạn số nhóm mỗi khung giờ (H13)
model.add(sum(variables[i] for i in indexes) <= context.max_groups_per_timeslot)

# Một giảng viên không ở hai chỗ chồng giờ (H2)
_add_resource_overlap_constraints(model, variables, candidates, "reviewer", reviewer_id)

# Hạn mức tải (H12): số buổi mỗi buổi sáng/chiều, mỗi ngày, mỗi học kỳ
model.add(sum(variables[i] for i in indexes) <= limit)
model.add(sum(variables[i] for i in indexes)
          <= max(0, context.h12_semester_quota - context.existing_semester_load.get(reviewer_id, 0)))
```

Hàm mục tiêu có một thủ thuật đáng học:

```python
primary_bonus = secondary_bound + balance_bound + 1
model.maximize(
    sum((primary_bonus + weighted_scores[i]) * variables[i] for i in range(len(candidates)))
    + balance_expression
)
```

`primary_bonus` **lớn hơn tổng mọi điểm mềm cộng lại**. Nghĩa là: xếp thêm được **một** nhóm luôn có giá trị cao hơn mọi cải thiện chất lượng gộp lại. Đây là cách mã hoá **ưu tiên từ điển** (lexicographic priority) trong một hàm mục tiêu duy nhất:

> Ưu tiên 1: xếp được nhiều nhóm nhất. Ưu tiên 2 (chỉ khi hoà): tối ưu điểm mềm và cân bằng tải.

`balance_expression = balance_weight * (minimum_load - maximum_load)` — tối đa hoá (min − max) chính là **thu hẹp khoảng cách** giữa giảng viên bận nhất và rảnh nhất. Cân bằng tải.

```python
solver.parameters.max_time_in_seconds = time_limit_seconds
solver.parameters.random_seed = random_seed
solver.parameters.num_search_workers = 1          # ← 1 luồng để KẾT QUẢ TÁI LẬP ĐƯỢC
```

`num_search_workers = 1` là đánh đổi có chủ ý: chậm hơn, nhưng cùng input luôn cho cùng output. Với hệ thống mà Manager phải giải thích "vì sao nhóm này bị xếp vào thứ Sáu", tính tái lập quan trọng hơn tốc độ.

### `scheduler/validator.py` — lưới an toàn

Sau khi solver trả lời, code **kiểm tra lại từ đầu**:

```python
def validate_schedule(sessions, context) -> ValidationResult:
```

13 luật cứng:

| Luật | Nội dung |
|---|---|
| H1 | Người hướng dẫn không được chấm chính đề tài mình hướng dẫn |
| H2 | Một giảng viên không ở hai buổi chồng giờ |
| H3 | Một phòng không có hai buổi chồng giờ |
| H4 | Một nhóm chỉ một buổi trong một phương án |
| H5 | Đúng số lượng reviewer theo loại đợt |
| H6 | Không có giảng viên trùng lặp trong cùng một buổi |
| H7 | Reviewer phải rảnh ở khung giờ được xếp |
| H8 | Reviewer không có xung đột lợi ích với đề tài |
| H9 | Trạng thái nhóm phù hợp với loại đợt |
| H10 | Buổi nằm trong khung giờ nhóm đã chọn |
| H11 | Defense 1.2 giữ đúng hội đồng cũ (trừ khi Manager miễn trừ có lý do) |
| H12 | Không vượt hạn mức tải (buổi/ngày/học kỳ) |
| H13 | Không vượt số nhóm tối đa mỗi khung giờ |

**Vì sao kiểm tra lại thứ mà solver vừa đảm bảo?** Ba lý do rất thực tế:

1. Ràng buộc trong `scheduler.py` là code người viết — có thể sai.
2. Bộ lọc trong `candidates.py` là code người viết — có thể sót.
3. Đây là hệ thống mà một buổi bảo vệ xếp sai làm hỏng cả ngày của 5 người thật.

Nếu validator phát hiện vi phạm, `DomainError` được ném **bên trong `with db.begin():`** → toàn bộ transaction rollback → không có phương án rác nào lọt vào DB. Thà không có kết quả còn hơn có kết quả sai.

Đây là pattern **defence in depth** và bạn nên giữ nó: nếu thêm ràng buộc mới vào solver, hãy thêm luôn phép kiểm tra tương ứng vào validator.

### `scheduler/snapshot.py` — đóng băng input

```python
snapshot = build_input_snapshot(round_id=round_id, context=context, groups=groups,
                                timeslots=[row[0] for row in timeslots],
                                reviewer_assignments={...}, soft_weights=context.soft_weights)
snapshot["unscheduled"] = [reason.__dict__ for reason in result.unscheduled]
```

Lưu vào cột `jsonb` của `schedule_versions.input_snapshot`.

Vì sao? Ba tháng sau ai đó hỏi "vì sao phương án #3 không xếp được nhóm G45". Không có snapshot, bạn không trả lời được — dữ liệu đã đổi rồi. Có snapshot, bạn biết chính xác lúc đó ai rảnh, ai bận, nhóm nào đăng ký gì.

`result.unscheduled` chứa **lý do** cho từng nhóm không xếp được — không chỉ nói "thất bại" mà nói "vì sao thất bại".

### Lưu xuống DB

Ba bảng, một transaction:

```python
INSERT INTO schedule_versions (round_id, version_no, status='DRAFT', input_snapshot,
                               algorithm_parameters, random_seed, solver_status,
                               total_score, soft_scores, created_by) RETURNING id
   ↓
INSERT INTO schedule_assignments (schedule_version_id, group_id, project_id,
                                  timeslot_id, start_at, end_at) RETURNING id
   ↓
INSERT INTO schedule_assignment_reviewers (assignment_id, lecturer_id,
                                           is_result_owner, snapshot_name)
   ↓
INSERT INTO scheduler_jobs (..., status='COMPLETED' hoặc 'PARTIAL')
INSERT INTO audit_events   (action='SCHEDULER_RUN')
```

`version_no` tính bằng `SELECT COALESCE(MAX(version_no), 0) + 1 FROM schedule_versions WHERE round_id = :round_id` — an toàn vì đang nằm trong transaction đã khoá dòng `rounds`.

`snapshot_name` lưu tên giảng viên tại thời điểm đó (xem [05-database.md](05-database.md) mục 5.6).

`status = "PARTIAL" if result.unscheduled else "COMPLETED"` — xếp được một phần vẫn là kết quả có ích, không phải thất bại.

## 10.5 Lớp áo cho frontend mới

```python
# apps/api/app/routes/target_schedule_contract.py
@router.post("/rounds/{round_id}/schedules/generate", status_code=201)
def generate_target_schedule(round_id: int, payload: ScheduleRunPayload, db: Db, user: User):
    result = run_scheduler(round_id, payload, db, user)     # ← gọi lại y nguyên
    return success_payload({
        "versionId": external_id(result["version_id"], "sv") if result.get("version_id") else None,
        "versionNumber": result.get("version_number", result.get("version_id")),
        "status": result.get("status", "DRAFT"),
        "scheduledCount": result.get("scheduled_count", 0),
        "unscheduledCount": len(result.get("unscheduled", [])),
        ...
    })
```

Chỉ làm ba việc: đổi id số → chuỗi có tiền tố (`12` → `sv_12`), đổi snake_case → camelCase, bọc vào `{"data": ...}`. **Không có logic nghiệp vụ nào ở đây.**

## 10.6 "Ngày mai tôi được giao sửa feature này thì bắt đầu từ đâu?"

Tuỳ loại việc:

| Yêu cầu | Đọc file này trước |
|---|---|
| "Thêm luật cứng H14" | `scheduler/validator.py` → `scheduler/candidates.py` → `scheduler/scheduler.py` (đủ cả 3) |
| "Đổi số reviewer cho Defense 2" | `domain/round_types.py` → `scheduler/candidates.py::_reviewer_tuples` |
| "Solver chạy chậm quá" | `scheduler/candidates.py` (số candidate sinh ra là bao nhiêu?) → `tests/test_benchmark.py` |
| "Kết quả bị lệch giữa 2 lần chạy" | tìm chỗ thiếu `sorted()`, kiểm tra `num_search_workers` và `random_seed` |
| "Cần thêm field vào response" | `routes/schedule_operations.py` câu `return` → `response_models.py` → `target_schedule_contract.py` |
| "Muốn thêm điều kiện lọc nhóm" | `_round_input()` (query) → `candidates.py` (bộ lọc) |
| "Báo lỗi khó hiểu quá" | `_validate_scheduler_inputs()` |

## 10.7 Chạy thử ngay

```powershell
# Benchmark chính thức: 74 nhóm / 26 giảng viên / 40 khung giờ / 4 phòng
# Yêu cầu: xong dưới 60 giây, không vi phạm luật nào
Push-Location apps/api
uv run pytest tests/test_benchmark.py -q
Pop-Location

# Test engine (không cần Docker)
uv run pytest tests/test_constraints.py tests/test_candidates_and_snapshot.py -q

# Test API đầy đủ (cần Postgres đang chạy)
docker compose exec -T api python -m pytest tests/test_schedule_operations.py -q
```
