# 02. Bản đồ repository và các layer

## Cây thư mục rút gọn

```text
f-caps-schedule-be/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── routes/       # HTTP endpoints và orchestration
│   │   │   ├── domain/       # business rules thuần
│   │   │   ├── services/     # DB-backed/shared helpers
│   │   │   ├── scheduler/    # CP-SAT engine và validator
│   │   │   ├── static/       # local Swagger assets
│   │   │   ├── main.py       # app factory, middleware, routers
│   │   │   ├── auth.py       # current-user dependency
│   │   │   ├── config.py     # environment settings
│   │   │   ├── database.py   # engine/session dependency
│   │   │   └── worker.py     # worker runtime thật
│   │   ├── migrations/       # Alembic schema history
│   │   ├── tests/            # unit/contract/integration tests
│   │   ├── pyproject.toml
│   │   └── alembic.ini
│   └── worker/               # legacy stub, không phải Compose worker
├── docs/
│   ├── api/                  # API notes; tuổi tài liệu không đồng đều
│   ├── project-reference/    # PRD, ERD, business rules
│   └── journals/             # engineering journal
├── infra/docker/             # API/worker Docker image
├── plans/                    # implementation plans còn lại
├── tools/                    # bootstrap/import/seed/reconcile utilities
├── docker-compose.yml
└── .env.example
```

## Layer thực tế

```text
Router/handler
   |---> Pydantic request/response model
   |---> domain function (pure rule)
   |---> service function (DB-backed shared behavior)
   |---> scheduler engine
   +---> SQLAlchemy Session -> raw SQL -> PostgreSQL
```

Đây không phải flow bắt buộc `Router -> Service -> Repository -> ORM` cho mọi endpoint. Nhiều
handler gọi SQL trực tiếp. Hãy mô tả kiến trúc theo code hiện tại, không ép tên layer từ project
khác vào repo này.

## Router / Controller

**Khái niệm:** cửa vào HTTP; parse input, gọi các thành phần khác và chọn response/status.

**File thật:** `apps/api/app/routes/*.py`.

- Được `create_app()` trong `apps/api/app/main.py` include.
- Được FastAPI gọi sau middleware và dependency resolution.
- Thường gọi domain, services, scheduler và raw SQL.
- Sửa khi thêm endpoint, đổi public contract hoặc đổi orchestration.

Các file lớn cần biết:

- `master_data.py`: CRUD và setup data nền.
- `manager_extensions.py`: detail/PATCH/import/export/report compatibility.
- `schedule_operations.py`: run, activate, edit, publish và reschedule.
- `results.py`: result/remediation legacy contract.
- `operations.py`: dashboard, notification, personal schedule.
- `target_*.py`: target contract mới, camelCase/envelope mới hoặc adapter lên logic cũ.

## Schema / DTO

**Khái niệm:** hình dạng dữ liệu qua API; không phải database entity.

- Request model thường được khai báo ngay trong route file, ví dụ `ScheduleRunPayload` trong
  `routes/schedule_operations.py` và `RoomUpdateTarget` trong `routes/target_room_publish.py`.
- Response model tập trung một phần tại `app/response_models.py`.
- `api_contract.py` có helpers `success_payload`, `error_payload`, external ID và metadata cho
  target contract.

Base response model đang dùng `extra="allow"` để giữ compatibility. Điều này giảm breakage nhưng
không bảo đảm response hoàn toàn strict.

## Domain

**Khái niệm:** luật nghiệp vụ độc lập với HTTP và database.

**File thật:** `apps/api/app/domain/`.

Ví dụ:

- `transitions.py`: state transition.
- `round_setup.py`, `round_types.py`: cấu hình round/reviewer count.
- `policy.py`, `availability.py`, `results.py`, `waivers.py`: authorization/business guards.
- `errors.py`: `DomainError`, `AuthorizationError` với machine-readable code.

Routes gọi domain. Domain không nên import FastAPI hoặc chạy SQL. Khi thay đổi “điều gì được
phép”, bắt đầu tìm tại đây và tại business rules trước khi sửa handler.

## Service / Use Case helper

**Khái niệm:** logic dùng lại cần database hoặc phối hợp nhiều truy vấn.

**File thật:** `apps/api/app/services/`.

- `access.py`: resource scoping theo role và quan hệ.
- `semester_queries.py`: archived-semester guard và locking.
- `room_assignment.py`: room conflicts và assignment.
- `councils.py`, `committee_service.py`: Council/Committee lifecycle.
- `timeframe_service.py`: versioned timeframe.
- `notification_dispatcher.py`: outbox/reminders/auto-close.
- `resource_locks.py`: PostgreSQL advisory transaction locks.

Một số service mở transaction; một số yêu cầu caller đã mở transaction. Phải đọc docstring và
call site, không đoán theo tên “service”.

## Repository và ORM Model

Repo không có `repositories/` và không có SQLAlchemy declarative entities. Thay vào đó:

```text
route/service
   -> Session.execute(text("SELECT ..."), parameters)
   -> PostgreSQL row/mapping
```

`scheduler/models.py` có Python dataclasses cho input/output thuật toán, nhưng chúng không phải
ORM models và không map tự động tới table.

## Infrastructure

Infrastructure nằm rải rác thay vì một folder `infrastructure/` trong app:

- DB engine/session: `database.py`.
- Settings: `config.py`.
- Docker: `infra/docker/api.Dockerfile`, `docker-compose.yml`.
- Migration: `migrations/`.
- Bootstrap/import: `tools/`.
- Notification adapter: `services/notification_dispatcher.py`.

## Dependency Injection

FastAPI là object factory. Ví dụ handler khai báo:

```text
handler cần Db
   -> Depends(get_db)
      -> Session(get_engine(settings.database_url))

handler cần User
   -> Depends(get_current_user)
      -> Depends(get_settings)
      -> Depends(get_db)
```

Các alias thường có dạng `Annotated[Session, Depends(get_db)]` và
`Annotated[CurrentUser, Depends(get_current_user)]`. Không có DI container riêng.

## Middleware và exception handler

- Middleware trong `main.py`: CORS, CSRF/security headers, legacy contract headers/telemetry.
- Exception handlers trong `main.py`: `HTTPException` và `RequestValidationError`.
- Target route được nhận diện qua tag bắt đầu `target-` và dùng `{"error": ...}`.
- Legacy route giữ `{"detail": ...}`.
- Unexpected exception dùng behavior/logging mặc định của FastAPI/Uvicorn.

