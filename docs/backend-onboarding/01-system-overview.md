# 01. Tổng quan hệ thống

## Project giải quyết bài toán gì?

Capstone Defense Scheduler hỗ trợ tổ chức các vòng review/defense của đồ án: quản lý học kỳ,
project, nhóm sinh viên, giảng viên, availability, hội đồng, chạy thuật toán xếp lịch, kích hoạt
và publish lịch, ghi kết quả, remediation và controlled changes.

V1 tập trung vào scheduler. Frontend đã tách sang repository khác; `apps/web` không tồn tại ở
đây dù root `README.md` vẫn còn một số hướng dẫn frontend cũ.

## Công nghệ chính

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Ngôn ngữ | Python 3.11 | Toàn bộ API, domain, worker và scheduler |
| HTTP framework | FastAPI + Uvicorn | Route, middleware, validation, OpenAPI, ASGI server |
| Validation | Pydantic | Parse và kiểm tra request/response/config |
| Database | PostgreSQL 16 | Dữ liệu nghiệp vụ, constraints, audit, outbox |
| DB toolkit | SQLAlchemy 2 + psycopg | Engine, Session và raw parameterized SQL |
| Migration | Alembic | Lịch sử schema, index, enum, trigger, constraint |
| Password | Argon2 | Hash và verify password |
| Scheduler | Google OR-Tools CP-SAT | Tối ưu assignment group/timeslot/reviewer |
| Excel | openpyxl | Import/bootstrap utilities, không phải request core |
| Tests/lint | pytest, httpx, Ruff | Unit, contract, integration và static checks |

`apps/api/pyproject.toml` và `apps/api/uv.lock` là dependency source trên host. Dockerfile hiện
cài dependencies thủ công thay vì dùng lockfile; xem cảnh báo tại chương 07.

## Kiến trúc tổng thể

```text
                         +-----------------------+
                         | PostgreSQL 16         |
                         | data/audit/outbox      |
                         +----^-------------^----+
                              |             |
                   raw SQL    |             | claim/commit
                              |             |
+-------------+      +--------+------+   +--+----------------+
| API client  +----->| FastAPI API   |   | app.worker        |
+-------------+ HTTP +---------------+   | poll mỗi 2 giây   |
                     | routes        |   +-------------------+
                     | domain        |
                     | services      |
                     | scheduler     |
                     +---------------+
```

Gọi là modular monolith vì:

- Một deployable API chứa tất cả domain.
- Các module được tách bằng folder và trách nhiệm, không phải network service.
- Tất cả cùng một database và transaction boundary.
- Worker là process riêng nhưng dùng chung package `app` và PostgreSQL.

Đây không phải microservices. Không có API gateway, service-to-service call hoặc database riêng
cho từng domain.

## Các domain/module chính

- **Master data**: semester, account, lecturer, student, project, group, room, round.
- **Round setup**: timeframe, registration, availability, invitation, conflict, committee.
- **Scheduling**: input snapshot, candidates, CP-SAT solve, validator, schedule versions.
- **Operations**: activate/publish, Council, room assignment, changes, notifications.
- **Results**: result owner, evaluation result, completion, remediation.
- **Portals/reporting**: schedule cá nhân, dashboard, notifications, exports.
- **Authentication/access**: cookie sessions, CSRF, system roles và resource scoping.

## Runtime services

`docker-compose.yml` chạy ba service:

1. `postgres`: PostgreSQL 16, host port `15432`.
2. `api`: bootstrap DB rồi chạy `uvicorn app.main:app` ở port `8000`.
3. `worker`: bootstrap DB rồi chạy `python -m app.worker`.

Cả API và worker chạy `tools/bootstrap_database.py` dưới PostgreSQL advisory lock. Code hiện tại
chạy `alembic upgrade head` và seed versioned fixture khi bật `SEED_FIXTURE`; nó không tự import
workbook Excel như một số đoạn README cũ mô tả.

## Queue, background job và external service

Đã xác nhận:

- Không Redis, Celery, RabbitMQ, Kafka hoặc queue broker.
- Không WebSocket/realtime push.
- Queue/outbox nằm trong PostgreSQL và được claim với `FOR UPDATE SKIP LOCKED`.
- Worker thật là `apps/api/app/worker.py`.
- Email adapter mặc định là `NoopEmailAdapter`, nên local không gửi email thật.
- `apps/worker/main.py` và `apps/api/app/jobs.py` là legacy/in-memory seams, không phải runtime
  production mà Compose đang dùng.

Worker gọi tuần tự:

```text
process_round_auto_close
  -> process_remediation_reminders
  -> process_availability_reminders
  -> process_outbox
  -> sleep(2 giây)
```

## Điều đã xác nhận và điều chỉ là nhận định

### Xác nhận từ code

- Routes và services dùng raw `sqlalchemy.text()`; không có declarative ORM model.
- Domain folder chủ yếu là hàm thuần và exception/state/policy.
- Business mutations thường ghi `audit_events` cùng transaction.
- Scheduler tạo reviewer/timeslot assignments; room được gán ở bước sau.

### Nhận định kiến trúc

- Modular monolith phù hợp V1 vì transaction giữa scheduling, audit và publish quan trọng hơn
  khả năng scale từng service độc lập.
- Đưa raw SQL vào nhiều route giúp delivery nhanh nhưng làm handler lớn, lặp transaction/error
  mapping và tăng chi phí onboarding.
- PostgreSQL outbox đủ đơn giản cho tải hiện tại; nếu cần retry/backoff/throughput lớn, team mới
  nên đánh giá broker chuyên dụng. Repo chưa cho thấy nhu cầu đó.

