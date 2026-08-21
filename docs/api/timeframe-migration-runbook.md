# Global Timeframe Migration Runbook

Migrations:

- `0030_global_timeframes`: Timeframe global và revision.
- `0031_timeframe_breaks`: khoảng nghỉ giữa block và các break window linh hoạt.
- `0032_manual_timelines`: snapshot JSONB cho timeline được chỉnh thủ công.

Hai migration tạo ba bảng cấu hình độc lập với Round/scheduler:

- `timeframes`: identity của cấu hình dùng chung.
- `timeframe_versions`: lịch sử các lần thay đổi thông số.
- `timeframe_break_windows`: danh sách khoảng nghỉ thuộc từng revision.

Nó không thêm foreign key vào Round, không tạo/đổi `round_days`, `timeslots`,
availability, schedule version hoặc session.

## Upgrade

```powershell
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic current
```

Kiểm tra schema:

```sql
SELECT to_regclass('public.timeframes');
SELECT to_regclass('public.timeframe_versions');
SELECT to_regclass('public.timeframe_break_windows');
SELECT column_name, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'timeframe_versions'
  AND column_name IN ('break_between_blocks_minutes', 'manual_timelines');
SELECT COUNT(*) FROM timeframes;
SELECT COUNT(*) FROM timeframe_versions;
SELECT COUNT(*) FROM timeframe_break_windows;
```

Kiểm tra dữ liệu lịch không đổi bằng cách ghi nhận count trước và sau upgrade:

```sql
SELECT COUNT(*) FROM rounds;
SELECT COUNT(*) FROM round_days;
SELECT COUNT(*) FROM timeslots;
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM schedule_assignments;
```

## Downgrade

Rollback manual timeline về `0031`:

```powershell
docker compose exec -T api alembic downgrade 0031_timeframe_breaks
```

Lệnh này xóa snapshot `manual_timelines`. Trước khi hạ migration trên môi
trường có dữ liệu thật, export các revision có `manual_timelines IS NOT NULL`.

Chỉ rollback cấu hình break linh hoạt của migration `0031`:

```powershell
docker compose exec -T api alembic downgrade 0030_global_timeframes
```

Lệnh này xóa `timeframe_break_windows` và cột
`break_between_blocks_minutes`, nhưng giữ `timeframes` và
`timeframe_versions`. Dữ liệu break của các revision sẽ bị mất.

Rollback toàn bộ tính năng Timeframe:

```powershell
docker compose exec -T api alembic downgrade 0029_manual_registration_phase
```

Downgrade xóa toàn bộ cấu hình và lịch sử Timeframe, nhưng không xóa hay thay đổi
dữ liệu Round/schedule vì hai aggregate hiện chưa liên kết với nhau.

## Rollout gate

1. Alembic lên đúng `0032_manual_timelines`.
2. Revision cũ mặc định `break_between_blocks_minutes = 0` và không có break window.
3. Preview có nghỉ trưa và khoảng nghỉ giữa block không tạo block cắt qua giờ nghỉ.
4. Create → PATCH tạo version 2 → archive hoạt động.
5. `GET /timeframes` ẩn archived; `includeArchived=true` đọc được archived.
6. Count `round_days`, `timeslots`, `sessions`, `schedule_assignments` không đổi.
7. Manual preview → create → PATCH giữ đúng timeline của từng revision.
