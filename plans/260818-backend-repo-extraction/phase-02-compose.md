# Phase 02 — Minimal Compose target change

Chỉ sửa target docker-compose.yml trong phạm vi spec: xóa web service/build context và FE-only configuration. Giữ nguyên postgres, api, worker, commands, Dockerfile path, environment values và backend mounts.

Target Compose project identity là f_caps_schedule_be và actual Docker volume phải là f_caps_schedule_be_postgres_data. Không dùng external true trỏ source volume.

Verification:
- docker compose -p f_caps_schedule_be -f W:\f-caps-schedule-be\docker-compose.yml config --services trả đúng postgres, api, worker;
- config model không có web, Vite, port 5173 hoặc FE build context;
- sau khi start target postgres, docker inspect chứng minh target mount f_caps_schedule_be_postgres_data;
- source mount vẫn là capstonedefensescheduler_postgres_data;
- source và target container IDs khác nhau.
- Khi source stack đang giữ host ports 5432/8000, dùng một Compose override tạm thời nằm ngoài target repo để map target-only host ports, ví dụ 55432/18000; không sửa source hoặc committed target Compose ports.

Abort on any backend Compose change ngoài web removal, source volume resolution, wrong service count hoặc wrong actual mount.
