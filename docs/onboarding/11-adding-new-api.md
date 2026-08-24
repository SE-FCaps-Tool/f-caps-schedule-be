# 11. Thêm một API mới

Giả sử bạn được giao:

```text
GET  /api/v1/example          — danh sách, có phân trang
POST /api/v1/example          — tạo mới
```

Dưới đây là workflow **theo đúng convention hiện tại** của repo, không phải theo lý thuyết.

## 11.1 Workflow tổng quan

```text
Bước 0  Quyết định: route CŨ hay route TARGET?        ← quyết định trước tiên
Bước 1  Migration (nếu cần bảng/cột mới)              apps/api/migrations/versions/
Bước 2  Domain rule (nếu có luật nghiệp vụ)           apps/api/app/domain/
Bước 3  Service (nếu SQL sẽ dùng lại ở ≥2 nơi)        apps/api/app/services/
Bước 4  Schema đầu vào (Pydantic)                     ngay trong file route
Bước 5  Response model                                apps/api/app/response_models.py
Bước 6  Route handler                                 apps/api/app/routes/
Bước 7  Gắn router vào app (chỉ khi tạo file mới)     apps/api/app/main.py
Bước 8  Test                                          apps/api/tests/
Bước 9  Tài liệu cho FE (nếu là hợp đồng public)      docs/api/
```

Chú ý thứ tự: **từ trong ra ngoài** (DB → domain → service → route), không phải từ route vào.

## 11.2 Bước 0 — Chọn nhóm route

Đây là quyết định đầu tiên và ảnh hưởng tới mọi bước sau.

| | Route cũ | Route target |
|---|---|---|
| File | `master_data.py`, `manager_extensions.py`, `schedule_operations.py`... | `target_*.py` |
| Tag | `tags=["management"]` | `tags=["target-xxx"]` |
| Body thành công | dict thô | `{"data": ..., "meta": ...}` |
| Body lỗi | `{"detail": {...}}` | `{"error": {"code","message","details"}}` |
| Kiểu id | số nguyên `12` | chuỗi có tiền tố `grp_12` |
| Kiểu tên field | snake_case | camelCase |

**Khuyến nghị:** tính năng mới nên đi theo **target contract** — đó là hướng repo đang chuyển tới. Nhưng hỏi team trước; hãy nhìn xem endpoint gần nhất về mặt nghiệp vụ đang nằm ở nhóm nào.

Nếu chọn target, mẫu chuẩn là: **viết logic thật ở một router thường (hoặc một service), rồi để `target_*.py` bọc lại** — đúng như `target_schedule_contract.py` làm.

## 11.3 Bước 1 — Migration

Chỉ khi cần bảng/cột mới.

```powershell
docker compose exec -T api alembic revision -m "add_example_table"
```

File mới xuất hiện trong `apps/api/migrations/versions/`. Sửa theo phong cách repo (SQL thô):

```python
revision = "0039_add_example_table"
down_revision = "0038_project_bilingual_titles"   # ← PHẢI trỏ đúng revision cuối
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
        CREATE TABLE examples (
            id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            semester_id  BIGINT NOT NULL REFERENCES semesters(id),
            code         VARCHAR(32) NOT NULL,
            name         VARCHAR(160) NOT NULL,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_by   BIGINT REFERENCES accounts(id),
            CONSTRAINT uq_examples_code UNIQUE (code)
        )
    """)

def downgrade() -> None:
    op.execute("DROP TABLE examples")
```

Checklist:

- [ ] `down_revision` trỏ đúng file cuối cùng (`ls apps/api/migrations/versions | tail -3`)
- [ ] Đặt **tên** cho constraint (`uq_examples_code`) — route sẽ dựa vào tên này để dịch lỗi 409
- [ ] Có `created_at`, `created_by` nếu là bảng nghiệp vụ
- [ ] Có `downgrade()` chạy được
- [ ] Chạy `alembic upgrade head` rồi `alembic downgrade -1` rồi `upgrade head` lại để kiểm chứng

```powershell
docker compose exec -T api alembic upgrade head
```

## 11.4 Bước 2 — Domain rule

Chỉ tạo khi có **luật nghiệp vụ thuần** (không cần DB để phán xét).

```python
# apps/api/app/domain/example.py
from app.domain.errors import DomainError

def validate_example_code(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise DomainError("EXAMPLE_CODE_REQUIRED", "An example code is required.")
    if len(normalized) > 32:
        raise DomainError("EXAMPLE_CODE_TOO_LONG", "Code must be at most 32 characters.")
    return normalized
```

Quy tắc:

- **Không** import `fastapi`, **không** import `sqlalchemy`.
- Mã lỗi viết HOA_GẠCH_DƯỚI, ổn định lâu dài (frontend so sánh nó).
- Nếu quy tắc cần đọc DB để phán xét → nó **không** thuộc domain, mà thuộc service hoặc route.

## 11.5 Bước 3 — Service

Chỉ tạo khi SQL sẽ dùng ở **≥ 2 nơi**. Một chỗ dùng thì viết thẳng trong route — repo chấp nhận điều đó.

```python
# apps/api/app/services/example_service.py
"""Persistence helpers for the Example catalog."""

from __future__ import annotations
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


def _error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def example_or_404(db: Session, example_id: int) -> dict[str, Any]:
    row = db.execute(
        text("SELECT id, code, name, created_at FROM examples WHERE id = :id"),
        {"id": example_id},
    ).mappings().one_or_none()
    if row is None:
        raise _error(404, "EXAMPLE_NOT_FOUND", "Example does not exist.")
    return dict(row)
```

**Quy tắc sống còn:** service **nhận** `db: Session` làm tham số, **không bao giờ** tự tạo Session. Lý do đầy đủ ở [09-dependency-injection.md](09-dependency-injection.md) mục 9.6.

Mẫu tham khảo tốt nhất: [apps/api/app/services/committee_service.py](../../apps/api/app/services/committee_service.py).

## 11.6 Bước 4 — Schema đầu vào

Khai báo **ngay trong file route**, đặt cùng khu với các schema khác ở đầu file. Không tạo thư mục `schemas/`.

```python
class ExampleCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)   # ← nếu là target route

    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=160)
    semester_id: int = Field(alias="semesterId", gt=0)

    @field_validator("code")
    @classmethod
    def normalize(cls, value: str) -> str:
        return validate_example_code(value)      # ← tái dùng luật domain
```

Mẹo lấy từ code thật:

- `Field(gt=0)` chặn id âm ngay tại schema, đỡ một lần kiểm tra trong handler.
- `Literal["A", "B"]` cho enum — Pydantic từ chối giá trị khác.
- `@model_validator(mode="after")` cho luật liên quan nhiều field (xem `TargetProjectCreate.supervisors_differ` trong `target_group_project.py`).
- Chuẩn hoá (trim, upper) ở validator, đừng để handler phải làm.

## 11.7 Bước 5 — Response model

```python
# apps/api/app/response_models.py  — thêm vào cuối, KHÔNG sửa model đang có
class ExampleResponse(ResponseModel):
    id: int
    code: str
    name: str
    created_at: datetime | None = None
```

`ResponseModel` là base có sẵn với `extra="allow"`. Kế thừa nó để nhất quán.

Docstring đầu file nói rõ: **mở rộng, đừng thay thế**. Nhiều model đang được dùng chung; sửa một model có thể phá endpoint khác.

## 11.8 Bước 6 — Route handler

Đây là khuôn mẫu. Đọc kỹ từng dòng — mọi handler ghi dữ liệu trong repo đều có hình dạng này.

```python
# apps/api/app/routes/example_routes.py  (hoặc thêm vào file route đã có)

router = APIRouter(prefix="/api/v1", tags=["management"])
Db = Annotated[Session, Depends(get_db)]
User = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/examples", response_model=list[ExampleResponse])
def list_examples(db: Db, user: User, semester_id: int | None = Query(default=None)) -> list[dict]:
    _require(user, "ADMIN", "MANAGER")
    rows = db.execute(
        text(
            "SELECT id, code, name, created_at FROM examples "
            "WHERE (:semester_id IS NULL OR semester_id = :semester_id) "
            "ORDER BY id"
        ),
        {"semester_id": semester_id},
    ).mappings().all()
    return [dict(row) for row in rows]


@router.post("/examples", status_code=status.HTTP_201_CREATED, response_model=ExampleResponse)
def create_example(payload: ExampleCreate, db: Db, user: User) -> dict[str, object]:
    _require(user, "ADMIN", "MANAGER")                        # 1. RBAC — dòng đầu tiên
    try:
        with db.begin():                                       # 2. một transaction
            ensure_semester_writable(db, payload.semester_id)  # 3. tiền điều kiện + khoá
            actor_id = _actor_id(db, user)                     # 4. ai đang thao tác
            row = db.execute(                                  # 5. ghi dữ liệu
                text(
                    "INSERT INTO examples (semester_id, code, name, created_by) "
                    "VALUES (:semester_id, :code, :name, :actor_id) "
                    "RETURNING id, code, name, created_at"
                ),
                {**payload.model_dump(), "actor_id": actor_id},
            ).mappings().one()
            db.execute(                                        # 6. audit — BẮT BUỘC
                text(
                    "INSERT INTO audit_events (actor_id, action, entity_type, entity_id, after_json) "
                    "VALUES (:actor_id, 'EXAMPLE_CREATED', 'example', :entity_id, CAST(:after_json AS JSONB))"
                ),
                {
                    "actor_id": actor_id,
                    "entity_id": str(row["id"]),
                    "after_json": _json(payload.model_dump(mode="json")),
                },
            )
    except DomainError as exc:                                 # 7. dịch lỗi
        raise HTTPException(422, detail={"code": exc.code, "message": str(exc)}) from exc
    except IntegrityError as exc:
        if "uq_examples_code" in str(getattr(exc, "orig", exc)):
            raise HTTPException(409, detail={"code": "EXAMPLE_CODE_DUPLICATE",
                                             "message": "Example code already exists."}) from exc
        raise HTTPException(409, detail={"code": "DATA_DUPLICATE",
                                         "message": "Example conflicts with existing data."}) from exc
    return example_or_404(db, int(row["id"]))                  # 8. đọc lại để trả về
```

Checklist tám điểm — reviewer sẽ soi đúng những thứ này:

| # | Việc | Bỏ sót thì sao |
|---|---|---|
| 1 | `_require(...)` dòng đầu | **Endpoint mở toang** cho mọi user đã đăng nhập |
| 2 | `with db.begin():` bọc mọi thao tác ghi | Ghi một nửa, dữ liệu không nhất quán |
| 3 | Khoá tiền điều kiện (`FOR UPDATE` / `ensure_*_writable`) | Race condition |
| 4 | `_actor_id(db, user)` | Audit không biết ai làm |
| 5 | Tham số `:name`, không f-string | **Lỗ hổng SQL injection** |
| 6 | `INSERT INTO audit_events` | Vi phạm convention, không truy vết được |
| 7 | Dịch `DomainError`/`IntegrityError` | Trả 500 thay vì mã lỗi có nghĩa |
| 8 | Đọc lại qua `*_or_404` | POST và GET trả hình dạng khác nhau |

> **Đừng viết từ số 0.** Mở handler gần nhất trong cùng file route, copy, rồi sửa. Repo cực kỳ nhất quán về pattern này và tính nhất quán ấy có giá trị hơn sự sáng tạo cá nhân.

### Nếu làm target route

```python
# apps/api/app/routes/target_example_contract.py
router = APIRouter(prefix="/api/v1", tags=["target-examples"])    # ← tiền tố "target-" QUAN TRỌNG

@router.get("/examples")
def list_target_examples(db: Db, user: User) -> dict[str, Any]:
    rows = list_examples(db, user)                                 # gọi lại handler thường
    return success_payload(rows, meta={"page": 1, "pageSize": len(rows), "total": len(rows)})

@router.post("/examples", status_code=201)
def create_target_example(payload: ExampleCreate, db: Db, user: User) -> dict[str, Any]:
    result = create_example(payload, db, user)
    return success_payload({"id": external_id(result["id"], "ex"), **result})
```

Tag bắt đầu bằng `target-` là thứ khiến exception handler ở `main.py` chọn định dạng lỗi `{"error": {...}}`. **Quên tiền tố này = lỗi trả sai định dạng và frontend vỡ.**

## 11.9 Bước 7 — Gắn router

Chỉ khi bạn tạo **file router mới**:

```python
# apps/api/app/main.py
from .routes.example_routes import router as example_router
...
app.include_router(example_router)
```

**Thứ tự `include_router` có ý nghĩa.** FastAPI khớp route theo thứ tự đăng ký. Nếu hai router có path đụng nhau, cái đăng ký trước thắng. Nhìn thứ tự hiện tại trong `main.py`: `master_data` trước, rồi `manager_extensions`, rồi các `target_*`, và `auth_router` cuối cùng.

## 11.10 Bước 8 — Test

```python
# apps/api/tests/test_example_api.py
import pytest

@pytest.mark.integration                      # bỏ marker nếu không cần DB
def test_create_example_requires_manager(client):
    response = client.post("/api/v1/examples",
                           json={"code": "ex1", "name": "Example"},
                           headers={"X-Test-Session": "active-student"})
    assert response.status_code == 403


@pytest.mark.integration
def test_create_example_rejects_duplicate_code(client):
    headers = {"X-Test-Session": "active-admin"}
    client.post("/api/v1/admin/seed-fixture", headers=headers)

    payload = {"code": "ex1", "name": "Example", "semesterId": 1}
    assert client.post("/api/v1/examples", json=payload, headers=headers).status_code == 201

    second = client.post("/api/v1/examples", json=payload, headers=headers)
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "EXAMPLE_CODE_DUPLICATE"
```

Tối thiểu phải có:

- [ ] Đường đi thành công (201 + hình dạng response đúng)
- [ ] Sai role → 403
- [ ] Vi phạm luật nghiệp vụ → 422 với **đúng `code`**
- [ ] Trùng dữ liệu → 409 với đúng `code`
- [ ] Không đăng nhập → 401
- [ ] Nếu logic có nhiều bước ghi: kiểm tra **rollback nguyên tử** khi bước sau thất bại

Mẫu tốt: `tests/test_phase03_api.py::test_group_mutation_validates_leader_and_rolls_back_atomically`.

Chạy:

```powershell
# Test thuần, không cần Docker
Push-Location apps/api
uv run ruff check app tests
uv run pytest -m "not integration" -q
Pop-Location

# Test có DB
docker compose exec -T api python -m pytest tests/test_example_api.py -q
```

## 11.11 Bước 9 — Tài liệu

Nếu endpoint là hợp đồng công khai với frontend, thêm một file vào [docs/api/](../api/) theo mẫu các file có sẵn (`manager-api.md`, `master-data.md`, ...): path, role được phép, ví dụ request/response, và **danh sách mã lỗi**.

Frontend cần biết mọi `code` có thể xuất hiện để hiển thị thông báo tiếng Việt tương ứng. Thiếu tài liệu này họ sẽ phải đoán.

## 11.12 Checklist rút gọn — dán lên màn hình

```text
[ ] 0. Chọn nhóm route (cũ / target) — hỏi team nếu không chắc
[ ] 1. Migration: down_revision đúng, constraint có tên, downgrade chạy được
[ ] 2. Domain: không import fastapi/sqlalchemy, mã lỗi ổn định
[ ] 3. Service: NHẬN db, không tự tạo Session
[ ] 4. Schema: khai báo trong file route, chuẩn hoá ở validator
[ ] 5. Response model: THÊM vào response_models.py, không sửa cái cũ
[ ] 6. Route: _require → with db.begin() → khoá → SQL tham số hoá → audit_events
[ ]        → except DomainError/IntegrityError → đọc lại rồi return
[ ] 7. include_router trong main.py (chỉ khi tạo file mới)
[ ] 8. Test: 201 / 403 / 422 / 409 / 401 + rollback
[ ] 9. ruff check + pytest xanh
[ ] 10. docs/api/ nếu là hợp đồng công khai
```
