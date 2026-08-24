# Onboarding — Capstone Defense Scheduler (Backend)

Bộ tài liệu này dành cho người **mới làm Backend** vừa được giao repo này. Mục tiêu không phải liệt kê file, mà giúp bạn dựng được **mental model**: hệ thống làm gì, request chạy qua đâu, và khi sửa/thêm tính năng thì mở file nào.

> Mọi đường dẫn file trong bộ tài liệu này là đường dẫn thật, tính từ gốc repo.

## Đọc theo thứ tự

| # | File | Nội dung |
|---|------|----------|
| 1 | [01-system-overview.md](01-system-overview.md) | Ngôn ngữ, framework, bài toán nghiệp vụ, module chính, dependency quan trọng |
| 2 | [02-repository-map.md](02-repository-map.md) | Cây thư mục rút gọn + trách nhiệm từng folder |
| 3 | [03-architecture-layers.md](03-architecture-layers.md) | Layer nào thật sự tồn tại — và layer nào **không** tồn tại |
| 4 | [04-request-lifecycle.md](04-request-lifecycle.md) | Trace một request thật từ đầu đến cuối — **phần quan trọng nhất** |
| 5 | [05-database.md](05-database.md) | Kết nối, session, transaction, migration, quan hệ giữa các bảng |
| 6 | [06-auth.md](06-auth.md) | Login → cookie session → CSRF → phân quyền theo role và theo scope |
| 7 | [07-errors-logging.md](07-errors-logging.md) | DomainError, exception handler, hai định dạng lỗi song song, chuyện logging |
| 8 | [08-configuration.md](08-configuration.md) | Biến môi trường, `Settings`, môi trường dev/test/prod |
| 9 | [09-dependency-injection.md](09-dependency-injection.md) | FastAPI `Depends` hoạt động thế nào trong repo này |
| 10 | [10-feature-walkthrough.md](10-feature-walkthrough.md) | Bóc một feature hoàn chỉnh A–Z: **chạy thuật toán xếp lịch** |
| 11 | [11-adding-new-api.md](11-adding-new-api.md) | Checklist thêm một API mới đúng convention hiện tại |
| 12 | [12-junior-warnings.md](12-junior-warnings.md) | Bẫy dễ dính, technical debt, file không nên đụng khi chưa hiểu |
| 13 | [13-reading-path.md](13-reading-path.md) | Lộ trình đọc code 5 ngày đầu |

## Bức tranh 30 giây

```text
                    ┌──────────────────────────────────┐
  Frontend          │  FastAPI app (apps/api)          │
  (repo riêng,      │                                  │
   không nằm ở đây) │  middleware: CSRF + security hdr │
        │           │            │                     │
        │   HTTP    │            ▼                     │
        └──────────►│  routes/*.py                     │
                    │      ├── domain/*.py  (rule thuần)│
                    │      ├── services/*.py (SQL chung)│
                    │      └── scheduler/*.py (OR-Tools)│
                    │            │                     │
                    │            ▼                     │
                    │  SQLAlchemy Core — text("SQL")   │
                    └────────────┬─────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────────────┐
                    │  PostgreSQL 16                   │
                    │  (kiêm luôn hàng đợi:            │
                    │   bảng outbox_jobs)              │
                    └────────────┬─────────────────────┘
                                 │ poll mỗi 2 giây
                                 ▼
                    ┌──────────────────────────────────┐
                    │  worker — apps/api/app/worker.py │
                    │  gửi thông báo, nhắc hạn         │
                    └──────────────────────────────────┘
```

Ba câu cần nhớ trước khi đọc tiếp:

1. **Không có ORM model.** Mọi truy vấn là SQL thô viết tay bọc trong `text("...")`.
2. **Không có Redis / Celery / RabbitMQ.** Hàng đợi chính là một bảng PostgreSQL.
3. **File route rất to và làm nhiều việc.** Đó là kiểu tổ chức chủ ý của repo, không phải bạn đọc nhầm.

## Cách tài liệu này phân biệt sự thật và suy luận

- **[Xác nhận từ code]** — tôi đã đọc trực tiếp file đó.
- **[Suy luận]** — nhận định của tôi dựa trên dấu hiệu trong code, có thể sai; hãy hỏi lại team trước khi hành động theo.
