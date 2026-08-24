# 07. Lộ trình đọc code và các vùng rủi ro

## Lộ trình đọc tối ưu

### Bước 1: Chạy hệ thống và xem contract

Đọc `docker-compose.yml`, mở `/health` và `/docs`.

Hiểu: API, worker, PostgreSQL chạy thế nào; container/host port khác nhau ra sao.

Chưa cần: toàn bộ migration history hoặc scheduler objective.

### Bước 2: Đọc app entry point

Đọc `apps/api/app/main.py`.

Hiểu: app factory, middleware order, router registration, target/legacy exception envelopes.

Chưa cần: nội dung từng route lớn.

### Bước 3: Đọc config, DB và auth

Đọc theo thứ tự:

1. `config.py`
2. `database.py`
3. `auth.py`
4. `routes/auth_routes.py`
5. `services/access.py`

Hiểu: Settings, Session/request, cookie session, CSRF, role và resource scope.

### Bước 4: Trace một CRUD mutation nhỏ

Đọc `update_room()` trong `routes/target_room_publish.py` và test tương ứng.

Hiểu: Pydantic, DI, role guard, autobegin/rollback, transaction, audit, error mapping.

Chưa cần: CP-SAT.

### Bước 5: Đọc một domain rule

Chọn `domain/transitions.py`, `domain/round_setup.py` hoặc `domain/policy.py` cùng unit tests.

Hiểu: vì sao business rule nên là hàm thuần và được routes map sang HTTP.

### Bước 6: Đọc schema theo feature

Đọc `docs/project-reference/ERD_CapstoneScheduler_v1.0.md`, migration
`apps/api/migrations/versions/0002_domain_model.py`, rồi chỉ các migration sau liên quan feature.
Không cần thuộc toàn bộ revision theo thứ tự ngay lần đầu.

Hiểu: table, FK, unique/exclusion/partial indexes, triggers và lifecycle vocabulary hiện tại.

### Bước 7: Trace scheduling

Theo thứ tự trong chương 05: route -> models -> candidates -> solver -> validator -> persistence ->
activate -> room -> publish.

Hiểu: candidate filtering khác CP constraint; ScheduleVersion khác Session; room là phase sau.

### Bước 8: Đọc worker và outbox

Đọc `app/worker.py` và `services/notification_dispatcher.py`.

Hiểu: PostgreSQL queue, `SKIP LOCKED`, noop email adapter, reminder lifecycle.

Không đọc `apps/worker` trước vì đó là legacy stub.

### Bước 9: Học qua tests

Đọc `tests/conftest.py`, một domain test, một contract test và một integration workflow test.

Hiểu: test session seam, markers và đâu là behavior cần DB thật.

### Bước 10: Chỉ sau đó mới đọc tools/imports

`tools/` có utility nguy hiểm như truncate/import/reconcile. Chỉ đọc tool đúng nhiệm vụ và luôn
phân biệt validate-only với `--apply`.

## File rất quan trọng

- `app/main.py`: mọi request đi qua.
- `app/auth.py`, `routes/auth_routes.py`: identity/session/CSRF context.
- `app/database.py`: Session lifecycle.
- `app/routes/schedule_operations.py`: orchestration scheduling lớn nhất.
- `app/scheduler/candidates.py`, `scheduler.py`, `validator.py`: hard rules.
- `app/services/access.py`: privacy/resource scope.
- `app/services/resource_locks.py`: concurrency contract.
- `app/services/councils.py`, `room_assignment.py`: operational invariants.
- Alembic revisions: schema truth.
- `tests/conftest.py`: cách tests tạo app/auth context.

## File không nên sửa khi chưa hiểu rõ

- Migration cũ, đặc biệt `0002`, `0021`, `0022`, `0025`.
- `scheduler/validator.py` mà không sửa/kiểm tra candidates, solver và publish flow tương ứng.
- `domain/round_types.py` mà chưa hiểu legacy aliases từ migrations `0035/0037`.
- Council sealing triggers/services.
- `schedule_assignments.project_id` và provenance semantics.
- Import/reset tools có truncate hoặc `--apply`.
- Root `schema.sql`: legacy snapshot, không phải nơi sửa schema.

## Những bẫy đã xác nhận từ code/repository

### Runtime và docs bị lệch

- Root README vẫn nhắc frontend/apps/web dù repo backend-only.
- README mô tả Excel bootstrap nhưng bootstrap hiện chạy migration + versioned fixture.
- Compose publish PostgreSQL host `15432`; README/`.env.example`/một số tool default dùng `5432`.
- `AGENTS.md` viện dẫn hai spec hiện không có trên disk.

### Legacy code dễ bị dùng nhầm

- Worker thật: `apps/api/app/worker.py`.
- `apps/worker/main.py` chỉ enqueue `noop`.
- `apps/api/app/jobs.py` và một số scheduler stores là in-memory seams.

### Contract đang trong giai đoạn migration

- Target routes dùng camelCase/data/error envelope; legacy routes dùng shape cũ.
- Error format phụ thuộc route tags.
- Một số target routes chưa có strict response model.
- Một số room paths trùng giữa target và legacy routers; OpenAPI/route precedence cần test kỹ.
- CSRF middleware trả legacy-like `detail` envelope trực tiếp.

### Dependency/build drift

- Dockerfile không dùng `uv.lock`.
- Dockerfile cài `httpx2>=0.1.0`, trong khi `pyproject.toml`/lock dùng `httpx`.
- Image chứa pytest/tools/workbook; chưa tách dev/runtime image.

### Scheduler drift

- Registry thiếu H13 và S9 so với validator/solver.
- H12 daily-count có dấu hiệu chỉ được validator bắt sau solve.
- Snapshot có dấu hiệu chưa chứa mọi input cần cho full replay.
- Room không nằm trong solver là quyết định kiến trúc hiện tại, không phải field bị quên.

### Observability/worker gaps

- Route telemetry là in-memory Counter.
- Không có structured app logging/tracing rõ ràng trong code core.
- Outbox `FAILED` không được worker tự claim lại; retry hiện thiên về thao tác thủ công.
- Direct tests cho production `process_outbox`/remediation worker còn mỏng.

## Nhận định, chưa được coi là fact

- Route modules lớn và trộn SQL/orchestration có thể tăng chi phí bảo trì; nhưng tách Repository/
  Use Case toàn repo là refactor lớn, không nên làm kèm một feature nhỏ.
- Việc update `last_seen_at` và commit trên mọi authenticated request có thể gây DB write contention;
  chưa có benchmark production chứng minh đây là bottleneck.
- Integration tests có thể nhạy với database state vì chưa thấy fixture reset chung; cần chạy suite
  nhiều lần/isolated DB trước khi kết luận flakiness.
- PostgreSQL outbox có thể đủ cho V1; chưa có evidence cần Redis/broker.

## Convention/pattern xuất hiện nhiều

- Role guard ở route, resource access ở helper/query.
- Pure domain validation kết hợp DB constraints.
- Raw parameterized SQL và mapping rows thành dict.
- Read -> rollback implicit transaction -> explicit `db.begin()` cho write.
- Mutation + audit event atomically.
- PostgreSQL row/advisory locks cho resource cạnh tranh.
- State transition thay vì update status tùy ý.
- Version/snapshot/provenance thay vì overwrite lịch sử.
- Compatibility adapters trong `target_*.py` khi public API đang migration.

## Khi bị lạc, dùng câu hỏi này

```text
Tôi đang thay đổi public contract, business rule,
database invariant hay background side effect?
```

- Public contract -> routes/schemas/OpenAPI/tests.
- Business rule -> domain + business rules docs.
- Database invariant -> service/SQL + migration/constraints.
- Background side effect -> outbox/dispatcher/worker.

Nếu một thay đổi chạm cả bốn, hãy dừng và lập plan trước khi code.
