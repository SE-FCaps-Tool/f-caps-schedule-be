# Backend Seed / Mock Data (Current State)

> Tài liệu mô tả mock/seed data hiện có trong backend (`apps/api`), dùng để
> dựng dữ liệu demo/dev cho DB Postgres. Khác với
> [capstone-scheduler-manager-ui-mockdata.md](./capstone-scheduler-manager-ui-mockdata.md)
> (mock data JSON cho FE UI theo màn hình), tài liệu này mô tả dữ liệu thực
> sự được ghi vào database qua các script/endpoint seed.

Có 3 nguồn seed độc lập, dùng cho các mục đích khác nhau:

| Nguồn | Cách chạy | Mục đích |
|---|---|---|
| [`app/domain/seed.py`](../../apps/api/app/domain/seed.py) (`seed_fixture_v1`) | `POST /admin/seed-fixture` (role `ADMIN`) | Bộ dữ liệu lớn, đầy đủ 1 kỳ học để demo/test toàn bộ luồng scheduling |
| [`scripts/seed_accounts.py`](../../apps/api/scripts/seed_accounts.py) | `docker compose exec api python scripts/seed_accounts.py` | 8 tài khoản demo cố định, mỗi role 1-2 account, dùng để đăng nhập thử nhanh |
| [`scripts/seed_student1_full.py`](../../apps/api/scripts/seed_student1_full.py) | `docker compose exec api python scripts/seed_student1_full.py` | Hồ sơ đầy đủ cho `student1@gmail.com`: nhóm, GVHD, reviewer, round đã publish, session đã schedule |

Mật khẩu demo dùng chung 1 hash Argon2 (`DEMO_PASSWORD_HASH` /
`SchedulerDemo2026!` cho `seed_accounts.py`) — không dùng cho production.

---

## 1. `seed_fixture_v1` — bộ fixture chính (`FIXTURE_VERSION = "seed-v1"`)

Endpoint: `POST /admin/seed-fixture` → gọi `load_seed_fixture(db, seed_fixture_v1())`,
upsert (idempotent, `ON CONFLICT DO UPDATE`) toàn bộ bảng liên quan và ghi
`audit_events` với action `SEED_FIXTURE_LOADED`.

### Semester & Major

```json
{
  "semester": {
    "code": "SE-2026-2027",
    "name": "Software Engineering 2026–2027",
    "start_date": "2026-05-11",
    "end_date": "2026-08-23"
  },
  "major": { "code": "SE", "name": "Software Engineering" }
}
```

### Admin / Manager accounts (không có trong loop, hard-coded 4 tài khoản)

| Email | Display name | Role |
|---|---|---|
| admin1@gmail.com | Scheduler Admin 1 | ADMIN |
| admin2@gmail.com | Scheduler Admin 2 | ADMIN |
| manager1@gmail.com | Scheduler Manager 1 | MANAGER |
| manager2@gmail.com | Scheduler Manager 2 | MANAGER |

### Lecturers — 26 giảng viên (`GV01`–`GV26`)

- `lecturer_code`: `GV{i:02d}`
- `email`: `lecturer{i}@gmail.com` cho `i` = 1, 2; còn lại `gv{i:02d}@scheduler.test`
- `display_name`: `Giảng viên {i:02d}`
- Role: `LECTURER`

### Rooms — 4 phòng (`R01`–`R04`)

| code | name | capacity |
|---|---|---|
| R01–R04 | Phòng Defense 01–04 | 12 |

### Students — 296 sinh viên (74 nhóm × 4 thành viên)

- `student_code`: `SV{n:03d}` (n = 1..296)
- `email`: `student{n}@gmail.com` cho n = 1, 2; còn lại `sv{n:03d}@scheduler.test`
- `display_name`: `Sinh viên {n:03d}`
- Role: `STUDENT`

### Groups — 74 nhóm (`G001`–`G074`)

Mỗi nhóm:
- `project_code`: `P{k:03d}`, `title`: `Capstone Project {k:03d}`
- 4 thành viên: member 1 = `LEADER`, member 2–4 = `MEMBER`
- 1 supervisor `MAIN`: xoay vòng qua 26 giảng viên (`GV{((k-1) % 26) + 1}`)

### Kết quả insert vào DB

`seed_fixture_v1` tương ứng với các bảng: `semesters`, `majors`, `accounts`,
`account_roles`, `lecturers`, `rooms`, `students`, `projects`, `groups`,
`group_memberships`, `project_supervisors`. Không tạo `rounds` / `sessions` /
lịch thi — chỉ dữ liệu academic nền.

Response của endpoint (`counts`): `{version, lecturers: 26, groups: 74, students: 296, rooms: 4}`.

---

## 2. `seed_accounts.py` — 8 tài khoản demo cố định

Password chung: `SchedulerDemo2026!`

| Email | Display name | Role | Code |
|---|---|---|---|
| admin1@gmail.com | Scheduler Admin 1 | ADMIN | — |
| admin2@gmail.com | Scheduler Admin 2 | ADMIN | — |
| manager1@gmail.com | Scheduler Manager 1 | MANAGER | — |
| manager2@gmail.com | Scheduler Manager 2 | MANAGER | — |
| lecturer1@gmail.com | Scheduler Lecturer 1 | LECTURER | GV_DEMO_01 |
| lecturer2@gmail.com | Scheduler Lecturer 2 | LECTURER | GV_DEMO_02 |
| student1@gmail.com | Sinh viên 001 | STUDENT | SV001 |
| student2@gmail.com | Sinh viên 002 | STUDENT | SV002 |

Script này chỉ tạo account + role + (nếu LECTURER/STUDENT) bản ghi
`lecturers`/`students` tương ứng — không tạo project/group/round.

---

## 3. `seed_student1_full.py` — hồ sơ đầy đủ cho `student1@gmail.com`

Password: `12345@Abc`. Dựng toàn bộ chuỗi dữ liệu để demo góc nhìn Student
đã có lịch bảo vệ:

- **Semester**: `SE-2026-2027` (status `ACTIVE`), **Major**: `SE`
- **Lecturers**: `lecturer1@gmail.com` (GV_DEMO1, supervisor) và
  `lecturer2@gmail.com` (GV_DEMO2, reviewer)
- **Student**: `student1@gmail.com`, `student_code = SV_DEMO1`
- **Project/Group**: `P_DEMO1` / `G_DEMO1`, student1 là `LEADER`
- **Room**: `R_DEMO1` (capacity 12)
- **Round**: `DEFENSE_1_1`, status `PUBLISHED`, `session_duration_minutes = 45`,
  `reviewer_count = 1`, `result_owner_mode = TRUE`
- **Round day / timeslot**: ngày = hôm nay + 7 ngày, giờ 09:00–09:45 UTC
- **Invitations & availability**: cả 2 giảng viên đã `ACCEPTED` +
  `AVAILABLE` cho timeslot trên
- **Schedule version**: v1, status `PUBLISHED`
- **Session**: `SCHEDULED`, gắn `G_DEMO1` vào phòng `R_DEMO1`, khung giờ trên
- **Session reviewers**: lecturer1 = `SUPERVISOR` (is_result_owner=True),
  lecturer2 = `REVIEWER`

Toàn bộ insert dùng `ON CONFLICT DO UPDATE`/`DO NOTHING` nên script chạy lại
nhiều lần an toàn (idempotent), không tạo dữ liệu trùng.

---

## Liên quan

- Test bảo đảm `seed_fixture_v1()` là pure/deterministic (không side effect,
  gọi 2 lần cho kết quả giống nhau): [`tests/test_seed_fixture.py`](../../apps/api/tests/test_seed_fixture.py)
- Loader áp dụng fixture vào DB: [`app/services/seed_loader.py`](../../apps/api/app/services/seed_loader.py)
- Route đăng ký seed-fixture: [`app/routes/master_data.py`](../../apps/api/app/routes/master_data.py)
- Mock data JSON theo từng màn hình UI Manager: [`capstone-scheduler-manager-ui-mockdata.md`](./capstone-scheduler-manager-ui-mockdata.md)
