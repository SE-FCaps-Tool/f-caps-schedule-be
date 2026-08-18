# API theo role — Capstone Defense Scheduler

Tài liệu này tổng hợp các API trong thư mục `docs/api` theo quyền của từng role để frontend dễ xây route guard và menu.

## Quy ước chung

- Base URL local: `http://localhost:8000`.
- Tất cả API nghiệp vụ có prefix `/api/v1`.
- API health là ngoại lệ: `GET /health`.
- Backend dùng cookie session, không dùng `Authorization: Bearer`.
- Frontend phải gửi `credentials: "include"`.
- Mọi `POST`, `PATCH`, `DELETE` sau khi đăng nhập phải gửi header `X-CSRF-Token` bằng giá trị cookie `scheduler_csrf`.
- `401` nghĩa là chưa đăng nhập/session hết hạn; `403` nghĩa là sai role hoặc ngoài phạm vi dữ liệu.

## 1. Student — danh sách đầy đủ

Student có thể gọi các API sau.

### Auth và thông tin cá nhân

| Method | Endpoint | Mục đích |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Đăng nhập bằng email/password. |
| `POST` | `/api/v1/auth/logout` | Đăng xuất và revoke session nếu có. |
| `GET` | `/api/v1/auth/me` | Lấy role, trạng thái account và `account_id`. |
| `GET` | `/api/v1/me` | Alias ngắn để kiểm tra current user. |

`GET /health` là public để kiểm tra server, không phải API nghiệp vụ của Student.

### Round và khai báo availability

| Method | Endpoint | Mục đích và điều kiện |
|---|---|---|
| `GET` | `/api/v1/my/rounds` | Xem các round liên quan đến group đang active của Student. |
| `GET` | `/api/v1/rounds/{round_id}/my-availability` | Xem timeslot của round, các group của Student và availability hiện tại của từng group. |
| `POST` | `/api/v1/rounds/{round_id}/groups/{group_id}/availability` | Gửi availability cho group. Chỉ **active group leader** được gọi; round phải bật `group_selection_mode=true`. |

Body của availability:

```json
{
  "selected_timeslot_ids": [10, 11],
  "load_preference": "MEDIUM"
}
```

Nếu `selected_timeslot_ids` là `[]`, backend coi toàn bộ timeslot của round là effective selection cho group.

### Xem lịch

| Method | Endpoint | Mục đích và phạm vi |
|---|---|---|
| `GET` | `/api/v1/rounds/{round_id}/schedule/versions` | Xem các schedule version có session thuộc group của Student. |
| `GET` | `/api/v1/schedule/versions/{version_id}` | Xem chi tiết version, nhưng chỉ các session Student được phép thấy. Không có session thuộc scope sẽ trả `403`. |
| `GET` | `/api/v1/my/schedule` | Xem lịch cá nhân/group. Có thể lọc bằng `version_id`, `from_at`, `to_at`. |
| `GET` | `/api/v1/schedule/versions/{version_id}/calendar.ics` | Tải lịch dạng iCalendar; chỉ chứa session thuộc group của Student. |

### Xem kết quả và remediation

| Method | Endpoint | Mục đích và phạm vi |
|---|---|---|
| `GET` | `/api/v1/sessions/{session_id}/result` | Xem kết quả của session thuộc group mình. |
| `GET` | `/api/v1/remediation` | Xem remediation case thuộc active group của mình. |
| `GET` | `/api/v1/reports/provenance/{version_id}` | Xem nguồn gốc/provenance của version nếu version có session Student được phép thấy. |

Student chỉ đọc kết quả. Student không được nhập, sửa hoặc quyết định remediation.

### Reschedule và thông báo

| Method | Endpoint | Mục đích và điều kiện |
|---|---|---|
| `POST` | `/api/v1/sessions/{session_id}/reschedule-requests` | Gửi yêu cầu đổi lịch. Chỉ **active group leader** được request cho session của group mình. Request sẽ gửi notification cho Manager. |
| `GET` | `/api/v1/notifications` | Xem notification có `recipient account` là Student hiện tại. |

Body gửi reschedule:

```json
{
  "reason": "Reviewer unavailable on scheduled date"
}
```

## 2. API dùng chung cho mọi role đã đăng nhập

Các endpoint dưới đây đều cho `ADMIN`, `MANAGER`, `LECTURER`, `STUDENT`, nhưng dữ liệu trả về vẫn bị giới hạn theo scope:

| Method | Endpoint | Ghi chú scope |
|---|---|---|
| `GET` | `/api/v1/auth/me` | Identity của session. |
| `GET` | `/api/v1/me` | Alias của current user. |
| `GET` | `/api/v1/rounds/{round_id}/my-availability` | Mỗi role nhận phần dữ liệu phù hợp. |
| `GET` | `/api/v1/my/rounds` | Manager/Admin thấy rộng; Lecturer theo invitation/assignment; Student theo group. |
| `GET` | `/api/v1/rounds/{round_id}/schedule/versions` | Lecturer/Student chỉ thấy version có session thuộc scope. |
| `GET` | `/api/v1/schedule/versions/{version_id}` | Non-management chỉ xem được session visible. |
| `GET` | `/api/v1/sessions/{session_id}/result` | Chỉ đọc result trong actor scope. |
| `GET` | `/api/v1/remediation` | Manager/Admin thấy tất cả; Lecturer theo verifier; Student theo group. |
| `GET` | `/api/v1/reports/provenance/{version_id}` | Non-management phải có session visible trong version. |
| `GET` | `/api/v1/notifications` | Manager/Admin theo management scope; Lecturer/Student chỉ notification của mình. |
| `GET` | `/api/v1/schedule/versions/{version_id}/calendar.ics` | Manager/Admin nhận toàn bộ; Lecturer/Student nhận session visible. |
| `GET` | `/api/v1/my/schedule` | Lịch cá nhân theo role và scope. |

## 3. Lecturer

Ngoài các API dùng chung, Lecturer có các API sau:

| Method | Endpoint | Mục đích và điều kiện |
|---|---|---|
| `GET` | `/api/v1/my/invitations` | Xem các invitation của chính Lecturer. |
| `POST` | `/api/v1/rounds/{round_id}/invitations/{lecturer_id}/response` | Accept/decline invitation; chỉ được response cho chính mình. |
| `POST` | `/api/v1/rounds/{round_id}/lecturers/{lecturer_id}/availability` | Gửi availability của chính mình; chỉ sau khi accept invitation. |
| `POST` | `/api/v1/lecturers/{lecturer_id}/conflicts` | Khai báo conflict cho chính mình. |
| `POST` | `/api/v1/sessions/{session_id}/reschedule-requests` | Request đổi lịch cho session được assign. |
| `POST` | `/api/v1/sessions/{session_id}/result` | Nhập result nếu là Reviewer được assign; nếu bật Result Owner thì phải là Result Owner. |
| `POST` | `/api/v1/remediation/{case_id}/decision` | Quyết định remediation nếu là assigned verifier của case. |

## 4. Manager

Manager có các API quản lý round, dữ liệu và vận hành sau:

### Master data và round setup

| Method | Endpoint |
|---|---|
| `GET`, `POST` | `/api/v1/semesters` |
| `GET` | `/api/v1/majors` |
| `GET` | `/api/v1/students` |
| `GET` | `/api/v1/lecturers` |
| `GET` | `/api/v1/rooms` |
| `GET`, `POST` | `/api/v1/projects` |
| `GET`, `POST` | `/api/v1/groups` |
| `POST` | `/api/v1/groups/{group_id}/members/{student_id}/drop` |
| `POST` | `/api/v1/groups/{group_id}/leader` |
| `GET`, `POST` | `/api/v1/rounds` |
| `POST` | `/api/v1/rounds/{round_id}/transition` |
| `POST` | `/api/v1/rounds/{round_id}/resources` |
| `POST` | `/api/v1/rounds/{round_id}/days` |
| `POST` | `/api/v1/rounds/{round_id}/lecturers/{lecturer_id}/availability` |
| `POST` | `/api/v1/rounds/{round_id}/groups/{group_id}/availability` |
| `POST` | `/api/v1/rounds/{round_id}/invitations` |
| `POST` | `/api/v1/rounds/{round_id}/invitations/{lecturer_id}/response` |
| `GET` | `/api/v1/rounds/{round_id}/registration` |
| `POST` | `/api/v1/lecturers/{lecturer_id}/conflicts` |

### Scheduler và vận hành lịch

| Method | Endpoint |
|---|---|
| `POST` | `/api/v1/rounds/{round_id}/schedule/run` |
| `POST` | `/api/v1/schedule/versions/{version_id}/activate` |
| `POST` | `/api/v1/rounds/{round_id}/schedule/publish/{version_id}` |
| `POST` | `/api/v1/schedule/versions/{version_id}/sessions/{session_id}/edit` |
| `POST` | `/api/v1/schedule/versions/{version_id}/sessions/{session_id}/controlled-change` |
| `GET` | `/api/v1/sessions/{session_id}/replacement-suggestions` |
| `POST` | `/api/v1/sessions/{session_id}/postpone` |
| `POST` | `/api/v1/sessions/{session_id}/reschedule-requests` |
| `POST` | `/api/v1/reschedule-requests/{request_id}/decision` |
| `POST` | `/api/v1/rounds/{round_id}/operation` |
| `POST`, `DELETE` | `/api/v1/rounds/{round_id}/groups/{group_id}/h11-waiver` |
| `POST` | `/api/v1/schedule/versions/{version_id}/sessions/{session_id}/result-owner` |

Theo tài liệu hiện tại, H11 waiver và Result Owner ghi rõ role `MANAGER`.

### Results, reports và notification operations

| Method | Endpoint |
|---|---|
| `POST` | `/api/v1/sessions/{session_id}/result` |
| `POST` | `/api/v1/remediation/{case_id}/overdue-fail` |
| `GET` | `/api/v1/dashboard` |
| `GET` | `/api/v1/reports/lecturer-load` |
| `GET` | `/api/v1/reports/unscheduled` |
| `GET` | `/api/v1/reports/quality` |
| `GET` | `/api/v1/reports/remediation` |
| `GET` | `/api/v1/reports/outcomes` |
| `POST` | `/api/v1/notifications/{notification_id}/retry` |

## 5. Admin

Admin có các API được tài liệu ghi `ADMIN` hoặc `ADMIN, MANAGER`, cộng các API quản trị riêng:

### Quản trị account và audit — Admin only

| Method | Endpoint |
|---|---|
| `GET` | `/api/v1/accounts` |
| `POST` | `/api/v1/accounts` |
| `PATCH` | `/api/v1/accounts/{account_id}/status` |
| `POST` | `/api/v1/accounts/{account_id}/roles` |
| `DELETE` | `/api/v1/accounts/{account_id}/roles/{role}?reason=...` |
| `GET` | `/api/v1/audit` |
| `POST` | `/api/v1/admin/seed-fixture` |
| `POST` | `/api/v1/lecturers` |
| `POST` | `/api/v1/rooms` |
| `POST` | `/api/v1/rounds/{round_id}/unlock` |

### Các API Admin dùng cùng Manager

Admin cũng được gọi các nhóm sau:

- Quản lý semester, project, group, round, resources, days, availability và invitations.
- Chạy scheduler, activate/publish version, edit/controlled-change schedule.
- Postpone session, xử lý reschedule request và round operation.
- Xem dashboard và các report quản lý.
- Retry notification failed.

Theo phân quyền được ghi trong tài liệu hiện tại, Admin **không mặc định** được gọi các endpoint chỉ ghi role `MANAGER`: H11 waiver, Result Owner, nhập/sửa result và overdue-fail remediation.

## 6. API không dành cho Student

Student không được gọi các nhóm sau:

- Quản lý semester, account, audit, fixture, lecturer, room, project và group.
- Tạo/chuyển trạng thái round, attach resource, tạo ngày/timeslot, gửi invitation.
- Chạy scheduler, activate, publish, edit hoặc controlled-change schedule.
- Gán Result Owner, tạo H11 waiver, postpone session, approve/reject reschedule request.
- Nhập hoặc sửa result.
- Ra quyết định remediation hoặc overdue-fail remediation.
- Xem dashboard và management reports: lecturer load, unscheduled, quality, remediation report, outcomes.
- Retry notification failed.

Nếu Student gọi các route này, backend phải trả `403`; frontend chỉ ẩn menu/button là chưa đủ, backend vẫn là nơi quyết định quyền.

## 7. Luồng API chuẩn cho Student

```text
POST /api/v1/auth/login
  -> GET /api/v1/auth/me
  -> GET /api/v1/my/rounds
  -> GET /api/v1/rounds/{round_id}/my-availability
  -> POST /api/v1/rounds/{round_id}/groups/{group_id}/availability
       (chỉ khi là active group leader và group_selection_mode=true)
  -> GET /api/v1/my/schedule
  -> GET /api/v1/sessions/{session_id}/result
  -> GET /api/v1/remediation
  -> GET /api/v1/notifications
```

Khi cần đổi lịch, Student active group leader gọi thêm:

```text
POST /api/v1/sessions/{session_id}/reschedule-requests
```

Tham khảo chi tiết request/response tại:

- [`auth.md`](auth.md)
- [`master-data.md`](master-data.md)
- [`scheduling.md`](scheduling.md)
- [`results-reports.md`](results-reports.md)
- [`schemas.md`](schemas.md)
