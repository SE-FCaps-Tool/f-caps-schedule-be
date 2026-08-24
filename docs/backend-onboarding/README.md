# Backend Onboarding Handbook

Tài liệu này giúp một Backend Developer mới xây dựng mental model về Capstone Defense
Scheduler trước khi sửa code. Nội dung được đối chiếu với repository ngày 2026-08-22;
không xem các file generated, database dump, workbook và Swagger bundle là source code cần học.

## Hiểu hệ thống trong hai phút

Đây là một **modular monolith**: một ứng dụng FastAPI chứa nhiều module nghiệp vụ nhưng cùng
chạy trong một process API và dùng chung PostgreSQL. Một worker riêng cũng dùng cùng codebase và
database để xử lý reminder/outbox.

```text
Frontend hoặc API client
          |
          v
FastAPI middleware: CORS, CSRF, security headers
          |
          v
Router + Pydantic request validation
          |
          v
Authentication + authorization
          |
          v
Domain rule / DB-backed service / raw SQL
          |
          v
PostgreSQL + audit/outbox
          |
          +----> polling worker ----> notification adapter
```

Điểm quan trọng nhất: project **không có ORM Entity và Repository layer truyền thống**.
SQLAlchemy tạo engine/session, còn routes và services thực thi SQL bằng `text()`. Vì vậy đừng
tìm `models/` hoặc `repositories/` rồi kết luận code bị thiếu.

## Thứ tự đọc handbook

1. [Tổng quan hệ thống](01-system-overview.md)
2. [Bản đồ repository và các layer](02-repository-map-and-layers.md)
3. [Lifecycle của một request](03-request-lifecycle.md)
4. [Database, auth, error và config](04-database-auth-errors-config.md)
5. [Feature scheduling từ A đến Z](05-scheduling-feature-a-to-z.md)
6. [Workflow sửa feature và thêm API](06-development-workflows.md)
7. [Lộ trình đọc code và các vùng rủi ro](07-junior-reading-roadmap-and-risks.md)

Nếu chỉ có 30 phút, hãy đọc file này, chương 03 và phần “đừng nhầm” trong chương 07.

## Bốn nhóm code cần phân biệt

| Nhóm | Nơi chính | Mental model |
|---|---|---|
| HTTP/API | `apps/api/app/routes/` | Nhận request, điều phối, map lỗi và trả response |
| Business rules | `apps/api/app/domain/` | Hàm thuần, state transition, policy; không truy cập DB |
| DB-backed helpers | `apps/api/app/services/` | Logic dùng lại có đọc/ghi PostgreSQL |
| Scheduling engine | `apps/api/app/scheduler/` | Tạo candidate, chạy CP-SAT, kiểm tra H1-H13 |

## Source of truth

Khi tài liệu mâu thuẫn với code, ưu tiên theo thứ tự:

1. `docs/project-reference/`: PRD, ERD và Business Rules cho ý nghĩa nghiệp vụ.
2. `apps/api/migrations/versions/`: schema và database constraints đang được áp dụng.
3. `apps/api/app/routes/`, domain/services/scheduler: hành vi runtime thực tế.
4. OpenAPI tại `/docs` và tests: contract được công bố/kiểm chứng.
5. Các tài liệu API cũ và root `README.md`: chỉ dùng làm lịch sử, phải đối chiếu lại.

`AGENTS.md` có nhắc `plans/capstone-scheduler/spec.md` và
`plans/backend-repo-extraction/spec.md`, nhưng tại thời điểm đối chiếu hai đường dẫn này không
tồn tại. Không được viện dẫn nội dung chưa có trên disk như một sự thật hiện tại.

## Thuật ngữ tối thiểu

- **Router**: nơi FastAPI ghép HTTP method/path với một Python function.
- **DTO/schema**: Pydantic model mô tả dữ liệu request/response, không phải database table.
- **Domain rule**: quy tắc nghiệp vụ có thể kiểm tra mà không cần biết HTTP.
- **Service**: helper dùng lại, trong repo này thường có DB access.
- **Dependency injection (DI)**: FastAPI tạo và truyền settings, DB session, current user vào
  handler thông qua `Depends`.
- **Transaction**: nhóm thao tác DB cùng thành công hoặc cùng rollback.
- **Migration**: lịch sử thay đổi schema chạy bởi Alembic.
- **Outbox**: bảng DB ghi “việc cần gửi”; worker claim rồi xử lý sau.
- **ScheduleVersion**: một phương án lịch có version; chưa đồng nghĩa với lịch đang hoạt động.
- **Committee**: nhóm giảng viên tái sử dụng khi lập kế hoạch.
- **Council**: snapshot hội đồng đã chốt cho một session; được bảo vệ bất biến.

## Lệnh bắt đầu

```powershell
docker compose up --build
# API/OpenAPI: http://localhost:8000/docs

Push-Location apps/api
uv run ruff check app tests
uv run pytest -m "not integration" -q
Pop-Location
```

PostgreSQL trong container dùng `postgres:5432`; từ host, Compose publish ra
`localhost:15432`. Hãy override `DATABASE_URL` khi chạy integration tool từ host thay vì tin
mặc định `localhost:5432` trong `.env.example`.

