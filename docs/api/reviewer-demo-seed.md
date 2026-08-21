# Reviewer demo seed

Fixture dùng để test 44 group và 44 cặp Reviewer do scheduler sinh tự động.

Chạy lại trên Docker:

```powershell
docker compose exec -T api python /app/tools/seed_reviewer_demo.py
```

Tài khoản dùng chung mật khẩu `12345@Abc`.

- Lecturer: `tript9@gmail.com`, `vulns@gmail.com`, ..., `nguyentt15@gmail.com`.
- Student: dạng `studentnguyentt1501@gmail.com`.
- Group: `REVIEW44-G01` đến `REVIEW44-G44`.
- Round: `REVIEWER-DEMO-44-PAIRS`.

Fixture tạo 8 timeslot, tất cả Lecturer accepted và available ở mọi slot, mỗi
group được phân bổ vào một slot. Scheduler có thể tạo 44 session, mỗi session 2
Reviewer, tổng 88 lượt phân công. Supervisor của group được loại khỏi candidate
Reviewer của chính project đó bởi hard constraint H1.
