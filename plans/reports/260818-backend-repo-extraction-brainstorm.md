# Brainstorm: Tách toàn bộ Backend thành repo độc lập

**Date:** 2026-08-18

## Challenge

Tách toàn bộ backend của Capstone Defense Scheduler khỏi repo hiện tại `W:\Capstone Defense Scheduler` sang repo mới `W:\f-caps-schedule-be`, không đưa FE sang repo mới và không làm thay đổi source hoặc database hiện tại.

## Ideas Explored

### 1. Giữ monorepo và chỉ bỏ qua FE

Giữ `apps/api` trong repo cũ, chỉ cấu hình Docker không chạy web. Cách này ít di chuyển nhất nhưng không đạt mục tiêu có một backend repo độc lập.

### 2. Copy-and-verify sang repo backend mới — hướng được chọn

Copy toàn bộ backend và các migration/test/tool cần thiết sang repo mới, giữ repo cũ nguyên trạng. Sau khi build, migrate, test và kiểm tra database thành công mới coi repo mới là backend chính.

### 3. Dùng git subtree/submodule

Có thể giữ lịch sử hoặc liên kết hai repo, nhưng tạo coupling lâu dài giữa repo FE cũ và backend mới. Không phù hợp với mục tiêu FE sẽ được viết lại ở repo khác.

### 4. Viết lại backend trong repo mới

Không cần thiết và có rủi ro làm thay đổi behavior của scheduler, auth, migrations và dữ liệu Excel đã import.

## User's Direction

Người dùng chốt:

- Repo mới chứa **full backend**.
- FE hoàn toàn nằm ngoài phạm vi.
- Giữ lại toàn bộ dữ liệu Excel đã import vào database.
- Không thay đổi repo cũ và không thay đổi dữ liệu hiện tại trong quá trình tách.

## Findings From Current Repository

- Backend thực tế nằm ở `apps/api`: FastAPI routes, domain, OR-Tools scheduler, worker, services, migrations và tests.
- Worker đang được Compose chạy từ `apps/api/app/worker.py`. `apps/worker/main.py` là module cũ/không được Compose sử dụng.
- Excel importer nằm ở `tools/import_excel_database.py` và phải được đưa theo backend repo.
- `docker-compose.yml` hiện trộn ba service backend (`postgres`, `api`, `worker`) với service FE (`web`). Repo mới phải loại bỏ service `web`, `VITE_API_PROXY` và `infra/docker/web.Dockerfile`.
- `infra/docker/api.Dockerfile` đang build theo root context rồi copy `apps/api`; khi repo mới có `app`, `migrations` và `tests` ở root, Dockerfile phải đổi đường dẫn build nhưng behavior API không đổi.
- `alembic.ini`, `pyproject.toml`, `uv.lock`, `migrations` và `tests` có thể trở thành root-level backend files.
- Alembic migration head hiện tại là `0012_excel_import_data`; migration này phải được giữ nguyên để database mới hiểu dữ liệu Excel đã import.
- Database hiện nằm trong volume Docker `capstonedefensescheduler_postgres_data`. Repo mới không tự dùng volume này nếu Compose project name thay đổi. Việc giữ dữ liệu phải thực hiện bằng volume mapping rõ ràng hoặc dump/restore có kiểm chứng.

## Proposed Backend Repository

```text
W:\f-caps-schedule-be\
├─ app\
│  ├─ domain\
│  ├─ routes\
│  ├─ scheduler\
│  └─ services\
├─ migrations\
│  └─ versions\
├─ tests\
├─ tools\
│  └─ import_excel_database.py
├─ docs\
├─ pyproject.toml
├─ uv.lock
├─ alembic.ini
├─ Dockerfile
├─ docker-compose.yml
└─ .env.example
```

`docker-compose.yml` của repo mới chỉ có `postgres`, `api` và `worker`. Database data không commit vào Git; data hiện tại được chuyển bằng backup/restore hoặc dùng đúng volume đã xác nhận.

## Data Preservation Strategy

1. Không sửa hoặc xoá repo cũ.
2. Không chạy `down -v` trên stack cũ.
3. Tạo logical dump từ database hiện tại sau khi Excel import đã hoàn tất.
4. Khởi tạo PostgreSQL của repo mới và restore dump.
5. So sánh table counts, project/group codes, round types, session counts và các bảng `excel_*` giữa source và target.
6. Chỉ đổi `DATABASE_URL`/Compose volume khi parity đã được xác nhận.

Copy code và chuyển data là hai bước riêng. Repo mới không được dùng một database rỗng rồi chạy seed fixture, vì như vậy sẽ làm mất bộ dữ liệu Excel hiện tại.

## Open Questions

Không còn câu hỏi chặn hướng chính. Các giả định cần giữ trong plan:

- File `.xlsx` là input bên ngoài cho importer, không bắt buộc commit vào repo backend.
- `schema.sql` cũ có thể được giữ như tài liệu legacy nhưng Alembic vẫn là source of truth.
- Repo mới dùng Git history riêng; repo cũ giữ nguyên history và working tree.

## Risks

1. **Mất dữ liệu do Docker volume:** Compose project name mới có thể tạo volume mới. Phải kiểm tra parity sau restore trước khi chuyển sử dụng.
2. **Sai đường dẫn build/runtime:** Dockerfile, Alembic và `PYTHONPATH` hiện phụ thuộc `apps/api`; copy sang root phải thay đổi path nhưng không đổi import contract.
3. **FE coupling bị sót:** README/docs/Compose có thể còn nhắc `apps/web`, port 5173 hoặc Vite. Cần grep toàn repo backend trước khi chốt.

## Recommendation

Thực hiện `copy-and-verify`: tạo backend repo độc lập từ backend hiện tại, giữ nguyên behavior và migration/data, loại toàn bộ FE coupling, rồi xác minh bằng Docker startup, Alembic head, API health, backend tests và database parity.
