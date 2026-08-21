# Accounts-only seed

Script này xoá toàn bộ dữ liệu ứng dụng trong database hiện tại, giữ nguyên
`alembic_version` và schema, sau đó chỉ seed tài khoản.

```powershell
docker compose exec -T api python /app/tools/seed_accounts_only.py
```

Dữ liệu được tạo:

- Admin và Manager.
- 14 Lecturer theo danh sách reviewer demo.
- 198 Student tương ứng với các Lecturer.
- Không tạo semester, project, group, round, timeslot, schedule hoặc session.

Mật khẩu dùng chung: `12345@Abc`.
