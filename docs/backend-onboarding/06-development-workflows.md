# 06. Workflow sửa feature và thêm API

## Khi được giao sửa một feature

Đi theo chiều từ contract vào trong, rồi quay ra bằng tests:

```text
API path / behavior mong muốn
  -> route handler + request/response schemas
  -> role/resource checks
  -> domain rules
  -> services/raw SQL
  -> migrations/constraints
  -> tests hiện có
  -> thay đổi nhỏ nhất
  -> lint + unit + integration phù hợp
  -> docs/API contract update
```

Trước khi sửa, trả lời được bảy câu:

1. Đây là target contract hay legacy contract?
2. Ai được gọi endpoint và resource scope là gì?
3. Business invariant nằm trong domain, DB hay cả hai?
4. Transaction bắt đầu/kết thúc ở đâu?
5. Có cần audit/outbox không?
6. Concurrent requests được serialize/bảo vệ thế nào?
7. Test nào chứng minh behavior hiện tại?

## Ví dụ thêm `GET /example`

Nếu là read-only và không cần schema mới:

1. Chọn route file theo functional slice trong `apps/api/app/routes/`; không tạo file “misc”.
2. Khai báo response model trong `response_models.py` hoặc gần route theo convention của slice.
3. Thêm decorator và handler.
4. Inject `Db`/`User` nếu cần.
5. Kiểm tra system role và resource-level scope.
6. Query bằng `text()` + bound parameters.
7. Trả target `success_payload()` hoặc legacy shape đúng contract của router.
8. Thêm unit/contract test; integration test nếu behavior phụ thuộc PostgreSQL semantics.
9. Kiểm tra OpenAPI không có duplicate method/path.
10. Cập nhật docs API liên quan.

Không tạo Repository/ORM class cho đúng “mẫu sách giáo khoa” nếu chỉ một endpoint dùng. Đây sẽ là
architecture migration, không còn là thay đổi nhỏ.

## Ví dụ thêm `POST /example`

Mutation thường cần thêm:

1. Pydantic request schema với types/range/aliases rõ ràng.
2. Domain validation cho rule thuần.
3. Nếu cần schema: tạo Alembic revision mới, không sửa revision cũ.
4. Xác định transaction owner.
5. Nếu đã đọc bằng Session trước `with db.begin()`, kết thúc implicit transaction đúng cách.
6. Lock row/advisory resource nếu có race condition.
7. Thực hiện writes và `audit_events` cùng transaction.
8. Enqueue outbox trong cùng transaction nếu cần notification sau commit.
9. Map `DomainError`, `IntegrityError` sang stable business code/status.
10. Test success, invalid input, unauthorized, conflict và rollback/atomicity.

## Chọn file nào để sửa

| Loại thay đổi | Bắt đầu ở đâu |
|---|---|
| HTTP path/body/response | `app/routes/`, `response_models.py`, `api_contract.py` |
| Business state/eligibility | `app/domain/` và business rules docs |
| Shared DB logic | `app/services/` |
| Database constraint/table | migration revision mới |
| Solver rule | candidates + scheduler + validator + tests |
| Session/room/publish | schedule routes + room/council services |
| Authentication/session | `auth_routes.py`, `auth.py`, `main.py` CSRF |
| Background reminder/outbox | `services/notification_dispatcher.py`, `app/worker.py` |
| Seed/import | `tools/`, tách khỏi production request flow |

## Convention cần giữ

- SQL values luôn bind parameters.
- Archived semester read-only; dùng guard hiện có.
- Business mutations có audit event.
- Contextual assignment không được biến thành system role.
- Historical schedule dùng frozen `schedule_assignments.project_id`.
- Committee và Council không được dùng thay thế nhau.
- Council sealed không mutate trực tiếp.
- Migration đã ship là lịch sử; thêm revision mới.
- Target/legacy error envelope phải nhất quán với router tag và contract.
- Response field mới nên mở rộng typed model thay vì bỏ model đang có.

## Testing strategy

### Nhanh trên host

```powershell
Push-Location apps/api
uv run ruff check app tests
uv run pytest -m "not integration" -q
Pop-Location
```

### Integration với Docker PostgreSQL

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

### Scheduler benchmark

```powershell
Push-Location apps/api
uv run pytest tests/test_benchmark.py -q
Pop-Location
```

Tests dùng `create_app()` với `APP_ENV=test`. `X-Test-Session` là test seam thay cho real login,
không phải public auth mechanism.

Chọn mức test theo rủi ro:

- Pure rule/state: unit test domain.
- Serialization/error envelope: contract/TestClient test.
- Constraint, locks, PostgreSQL enum/trigger/raw SQL: integration test.
- Scheduler: candidate/validator unit + engine cases + benchmark.
- Multi-write mutation: test atomic rollback, không chỉ status 200.

## Checklist review một endpoint mutation

- [ ] Authenticated và authorized đúng role/resource.
- [ ] Pydantic validation đủ chặt.
- [ ] Domain rule không bị duplicate/lệch giữa layers.
- [ ] Parameterized SQL; dynamic identifiers từ whitelist.
- [ ] Transaction boundary rõ.
- [ ] Read-before-begin xử lý autobegin đúng.
- [ ] Lock/constraint bảo vệ race condition.
- [ ] Audit/outbox trong cùng transaction khi cần.
- [ ] Stable error code và đúng target/legacy envelope.
- [ ] Tests gồm failure/rollback/concurrency-relevant path.
- [ ] OpenAPI không bị duplicate path precedence.

