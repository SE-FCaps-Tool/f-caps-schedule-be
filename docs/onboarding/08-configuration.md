# 8. Configuration

> Tài liệu này **không** chứa giá trị bí mật thật. Mọi giá trị dưới đây là mặc định dev đã có sẵn công khai trong repo.

## 8.1 Toàn bộ cấu hình nằm ở một file

[apps/api/app/config.py](../../apps/api/app/config.py) — 29 dòng, đọc hết trong 30 giây:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Capstone Defense Scheduler API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://scheduler:scheduler@localhost:5432/scheduler"
    session_cookie_name: str = "scheduler_session"
    session_idle_minutes: int = 60
    session_absolute_hours: int = 168
    frontend_url: str = "http://localhost:5173"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173"
    )
    semester_min_duration_days: int = 105
    semester_max_duration_days: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## 8.2 Cấu hình được nạp như thế nào

`BaseSettings` của **pydantic-settings** tự động đi tìm giá trị theo thứ tự ưu tiên:

```text
1. Biến môi trường           (ưu tiên CAO NHẤT)
      APP_ENV=production, DATABASE_URL=...
      ↓ nếu không có
2. File cấu hình môi trường  (env_file=".env" trong thư mục làm việc)
      ↓ nếu không có
3. Giá trị mặc định trong class
      app_env: str = "development"
```

**Quy tắc đặt tên:** tên field viết thường có gạch dưới → biến môi trường viết **HOA**.

| Field trong `Settings` | Biến môi trường |
|---|---|
| `app_env` | `APP_ENV` |
| `database_url` | `DATABASE_URL` |
| `session_idle_minutes` | `SESSION_IDLE_MINUTES` |
| `semester_min_duration_days` | `SEMESTER_MIN_DURATION_DAYS` |

`extra="ignore"` nghĩa là biến môi trường lạ không khớp field nào thì bỏ qua, không báo lỗi. Tiện, nhưng cũng nghĩa là **gõ sai tên biến sẽ im lặng không có tác dụng** — hãy kiểm chứng qua `/health` hoặc log khởi động thay vì tin rằng nó đã áp dụng.

Pydantic còn **tự ép kiểu**: biến môi trường luôn là chuỗi, nhưng `session_idle_minutes: int` khiến `"90"` thành `90`. Đặt giá trị không phải số → app **crash ngay lúc khởi động** thay vì lỗi mập mờ về sau. Đây là điểm mạnh của cách làm này.

## 8.3 `@lru_cache` — chi tiết nhỏ nhưng quan trọng

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`lru_cache` khiến `Settings()` chỉ được tạo **đúng một lần** cho cả vòng đời process. Mọi lời gọi `get_settings()` sau đó trả về **cùng một object**.

Ba hệ quả:

1. **Nhanh** — không đọc lại file/môi trường ở mỗi request.
2. **Nhất quán** — mọi nơi trong app thấy cùng một cấu hình.
3. **Đổi biến môi trường lúc runtime không có tác dụng.** Phải restart process.

Điểm 3 giải thích vì sao `apps/api/tests/conftest.py` phải viết như thế này:

```python
import os
os.environ["APP_ENV"] = "test"      # ← PHẢI đặt TRƯỚC

import pytest
from fastapi.testclient import TestClient
from app.main import create_app     # ← import này kích hoạt get_settings()
```

Đảo hai khối này là toàn bộ test auth sẽ hỏng — `APP_ENV` sẽ bị cache thành `"development"` và header `X-Test-Session` không còn tác dụng.

## 8.4 Cấu hình được truyền tới nơi cần bằng cách nào

```text
                    get_settings()   (cache, singleton)
                          │
        ┌─────────────────┼──────────────────┬────────────────────┐
        ▼                 ▼                  ▼                    ▼
   create_app()      get_db()          get_current_user()    route handler
   main.py           database.py       auth.py               qua Depends
   - CORS origins    - database_url    - session_cookie_name  - SettingsDep
   - app_env (HSTS)                    - session_idle_minutes
   - session_cookie_name               - app_env (nhánh test)
```

Trong route, xin cấu hình y như xin `db`:

```python
# apps/api/app/routes/master_data.py
SettingsDep = Annotated[Settings, Depends(get_settings)]

def create_semester(payload: SemesterCreate, db: Db, user: User, settings: SettingsDep):
    if not settings.semester_min_duration_days <= duration_days <= settings.semester_max_duration_days:
        raise HTTPException(422, detail={...})
```

**Không import `get_settings()` rồi gọi trực tiếp trong route.** Đi qua `Depends` để test có thể ghi đè (`app.dependency_overrides`).

## 8.5 Từng biến làm gì

| Biến | Mặc định | Tác dụng |
|---|---|---|
| `APP_ENV` | `development` | **Biến quyền lực nhất.** Xem mục 8.6 |
| `DATABASE_URL` | `postgresql+psycopg://scheduler:scheduler@localhost:5432/scheduler` | Chuỗi kết nối Postgres |
| `SESSION_COOKIE_NAME` | `scheduler_session` | Tên cookie phiên |
| `SESSION_IDLE_MINUTES` | `60` | Không hoạt động bao lâu thì phiên chết |
| `SESSION_ABSOLUTE_HOURS` | `168` (7 ngày) | Hạn tuyệt đối của phiên |
| `CORS_ORIGINS` | 4 origin localhost | Domain frontend được phép gọi API, phân tách bằng dấu phẩy |
| `FRONTEND_URL` | `http://localhost:5173` | URL FE nhận redirect sau Google login |
| `GOOGLE_CLIENT_ID` | trống | OAuth Web client ID từ Google Cloud |
| `GOOGLE_CLIENT_SECRET` | trống | OAuth Web client secret, chỉ đặt trên BE |
| `GOOGLE_REDIRECT_URI` | trống | Callback URI đã đăng ký chính xác trên Google Cloud |
| `SEMESTER_MIN_DURATION_DAYS` | `105` | Luật nghiệp vụ — độ dài học kỳ tối thiểu |
| `SEMESTER_MAX_DURATION_DAYS` | `120` | Độ dài học kỳ tối đa |
| `SEED_FIXTURE` | `true` | *(Đọc bởi `tools/bootstrap_database.py`, không nằm trong `Settings`)* Có nạp dữ liệu mẫu lúc khởi động không |

**Về `CORS_ORIGINS`:** CORS (Cross-Origin Resource Sharing) là cơ chế trình duyệt chặn trang ở domain A gọi API ở domain B, trừ khi B cho phép. Vì frontend nằm ở repo/domain khác, danh sách này phải liệt kê đúng origin của FE. `allow_credentials=True` trong `main.py` cho phép gửi kèm cookie — và đây là lý do **không được** dùng `allow_origins=["*"]` cùng với credentials.

## 8.6 `APP_ENV` — nó điều khiển những gì

Đây là biến bạn phải hiểu rõ nhất, vì nó bật/tắt các hành vi bảo mật:

```python
# apps/api/app/auth.py — mở cửa test
if settings.app_env == "test" and test_session:
    return CurrentUser(role=test_roles[role], ...)

# apps/api/app/routes/auth_routes.py — cookie có bắt buộc HTTPS không
secure = settings.app_env not in {"development", "test"}
response.set_cookie(settings.session_cookie_name, token, httponly=True, secure=secure, samesite="lax")

# apps/api/app/main.py — có ép HTTPS không
if settings.app_env not in {"development", "test"}:
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
```

Bảng so sánh:

| | `development` | `test` | mọi giá trị khác (VD `production`) |
|---|---|---|---|
| Header `X-Test-Session` | ❌ không nhận | ✅ **nhận** | ❌ không nhận |
| Cookie `secure` (chỉ qua HTTPS) | ❌ tắt | ❌ tắt | ✅ **bật** |
| Header `Strict-Transport-Security` | ❌ | ❌ | ✅ **có** |

Lưu ý: mã kiểm tra là `not in {"development", "test"}` — nghĩa là **bất kỳ** giá trị lạ nào (kể cả gõ nhầm `"prod"`, `"produciton"`) cũng được coi là môi trường an toàn và bật hết chế độ chặt. Đây là mặc định **fail-safe** đúng đắn: gõ sai thì chặt hơn, không lỏng hơn.

## 8.7 Cấu hình lúc chạy Docker

[docker-compose.yml](../../docker-compose.yml) đặt biến môi trường trực tiếp, không qua file:

```yaml
api:
  environment:
    APP_ENV: development
    DATABASE_URL: postgresql+psycopg://scheduler:scheduler@postgres:5432/scheduler
    SEED_FIXTURE: ${SEED_FIXTURE:-true}
    CORS_ORIGINS: http://localhost:3000,http://localhost:5173,...
```

Hai điểm dễ vấp:

**1. Host name khác nhau trong và ngoài container.**

```text
Từ trong container:  postgres:5432       ← tên service trong compose
Từ máy host:         localhost:15432     ← cổng ánh xạ ra ngoài
```

`ports: "15432:5432"` nghĩa là cổng 15432 của máy bạn nối vào cổng 5432 trong container. Chạy script trên máy host thì `DATABASE_URL` phải là `...@localhost:15432/scheduler`.

**2. `${SEED_FIXTURE:-true}`** là cú pháp shell: lấy biến `SEED_FIXTURE` từ môi trường của bạn, nếu không có thì dùng `true`. Muốn khởi động DB rỗng:

```powershell
$env:SEED_FIXTURE = "false"; docker compose up --build
```

## 8.8 Quản lý bí mật

**Hiện trạng [Xác nhận từ code]:**

- Mật khẩu Postgres là `scheduler/scheduler`, ghi thẳng trong `docker-compose.yml`.
- `.gitignore` loại trừ file cấu hình môi trường thật; repo chỉ có file `.example` làm mẫu.
- **Không có** secret manager (Vault, AWS Secrets Manager, ...).
- **Không có** `SECRET_KEY` để ký gì cả — vì không dùng JWT. Session token là chuỗi ngẫu nhiên lưu DB, không cần khoá ký.

**[Nhận định]** Với môi trường local-only (deploy cloud đang nằm ngoài phạm vi V1 theo `CLAUDE.md`) thì chấp nhận được. Nhưng khi nào lên môi trường thật, đây là danh sách phải xử lý:

1. Mật khẩu DB phải lấy từ nguồn bí mật, không nằm trong compose.
2. `APP_ENV` phải khác `development`/`test` (bắt buộc, nếu không cookie sẽ không có cờ `secure`).
3. `CORS_ORIGINS` phải là domain thật, không phải localhost.
4. Cần một cơ chế xoay vòng bí mật.

**Quy tắc cho bạn ngay bây giờ:** không bao giờ commit giá trị bí mật, không dán chúng vào tài liệu, không viết chúng vào test. Nếu cần một giá trị mới, thêm field vào `Settings` với mặc định vô hại và tài liệu hoá tên biến môi trường.

## 8.9 Thêm một cấu hình mới — 4 bước

Ví dụ: giới hạn thời gian chạy solver.

```python
# 1. Thêm field vào apps/api/app/config.py, LUÔN có giá trị mặc định
class Settings(BaseSettings):
    ...
    scheduler_time_limit_seconds: int = 30
```

```python
# 2. Dùng trong route qua Depends
def run_scheduler(round_id: int, payload: ScheduleRunPayload, db: Db, user: User, settings: SettingsDep):
    limit = payload.time_limit_seconds or settings.scheduler_time_limit_seconds
```

```yaml
# 3. Khai báo trong docker-compose.yml nếu môi trường Docker cần giá trị khác mặc định
api:
  environment:
    SCHEDULER_TIME_LIMIT_SECONDS: 60
```

```text
4. Thêm dòng tương ứng vào file .example ở gốc repo để người sau biết biến này tồn tại.
```

**Luôn có giá trị mặc định hợp lý.** Field không mặc định sẽ khiến app không khởi động được nếu thiếu biến — chỉ làm vậy khi giá trị đó thật sự bắt buộc (như `DATABASE_URL`, mà ngay cả nó cũng có mặc định trỏ localhost).
