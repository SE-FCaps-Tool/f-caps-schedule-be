# Đối chiếu checklist FE (`be-checklist-open-questions.md`) với codebase BE thật

Ngày kiểm tra: 2026-08-20. Phạm vi: đối chiếu từng mục Phần A/B/C mà FE liệt kê với trạng thái
thực tế của route, không sửa code trong lần kiểm tra này.

## Phát hiện tổng quát quan trọng nhất

**"Chưa có" theo FE ≠ "chưa có" thật.** Nhiều mục ở Phần A thực ra **đã có route** trong code,
chỉ là chúng nằm ở router cũ (`manager_extensions.py`, tag `manager-ui-compatibility`) nên trả
**envelope kiểu cũ** (`{"detail":{code,message}}` khi lỗi, dict phẳng khi thành công — không phải
`{"data":...}`/`{"error":...}`) thay vì envelope target mà FE đang dùng cho các route khác.

Ngoài ra `app/routes/target_portals.py` (toàn bộ cổng self-service Lecturer/Leader) tuy đã dùng
`success_payload()` nhưng **chưa từng được đổi sang camelCase** — vẫn lộ nguyên field snake_case
từ SQL (`round_id`, `group_code`, `response_reason`, ...).

## Phần A — endpoint FE tưởng thiếu

| # | Endpoint | Kết luận |
|---|---|---|
| A1 | `PATCH /projects/:projectId` | **Đã có** — [`manager_extensions.py:300`](../../apps/api/app/routes/manager_extensions.py#L300). Tag `manager-ui-compatibility`, lỗi trả `{"detail":{code,message}}` chứ không phải `{"error":...}`. Field response: `id,code,title,status,semester_id` — thiếu `nameVi/nameEn` FE đề xuất (repo hiện chỉ có 1 field `title`, không tách vi/en). |
| A2 | `PATCH /rounds/:roundId` | **Đã có** — [`manager_extensions.py:258`](../../apps/api/app/routes/manager_extensions.py#L258). Cùng vấn đề envelope cũ như A1. Field khớp khá tốt với `POST /rounds` (start_date, end_date, reviewer_count, room_types...). |
| A3 | `POST /semesters/:semesterId/projects/import` | **Đã có** — `POST /projects/import` tại [`manager_extensions.py:673`](../../apps/api/app/routes/manager_extensions.py#L673), envelope cũ tương tự. |
| A4 | `GET/POST/PATCH /rooms` | **Đã có nhưng rải 2 nơi**: `GET/POST /rooms` ở [`master_data.py:557`](../../apps/api/app/routes/master_data.py#L557) (envelope cũ), còn `PATCH /rooms/:id` lại ở [`target_room_publish.py:79`](../../apps/api/app/routes/target_room_publish.py#L79) (envelope target, đúng chuẩn). Không đồng bộ giữa GET/POST và PATCH. |
| A5 | Manager nhập hộ availability/preference | Route cũ vẫn còn (`POST /rounds/:id/lecturers/:id/availability` với `source=MANAGER`, thấy trong `tests/test_phase03_api.py:179`). FE nói có thể không cần nữa — không cần động vào. |
| A6 | remediations overdue-fail | **Đã có**, đúng target envelope: [`target_results_remediation.py:66,71`](../../apps/api/app/routes/target_results_remediation.py#L66). |
| A7 | `POST /sessions/:id/makeup` | **Đã có** — [`schedule_operations.py:1245`](../../apps/api/app/routes/schedule_operations.py#L1245), response có `makeup_of_session_id` (snake_case, không phải `makeupOfSessionId` như FE mong đợi). |
| A8 | `GET /leader/me/results` | **Chưa có** — không tìm thấy route nào. Cần build thật. |
| A9 | `GET /lecturer/me/supervised-projects/:projectId/results` | **Chưa có** dạng lịch sử đầy đủ. Chỉ có [`target_group_project.py:416 GET /projects/:id/results`](../../apps/api/app/routes/target_group_project.py#L416) (theo project, chưa rõ có đúng scope lecturer hay không) và `lecturer/me/supervised-projects` (list, không có lịch sử result). Cần xác nhận lại thiết kế. |
| A10 | `GET .../invitations/:id/availability-grid` | **Chưa có** — chỉ có `GET /rounds/:id/my-availability` cũ ở [`master_data.py:1607`](../../apps/api/app/routes/master_data.py#L1607), đúng như FE mô tả (route tạm, sai convention). Cần build route target thật. |

## Phần B — shape cần xác nhận

| # | Endpoint | Kết luận |
|---|---|---|
| B1 | `GET /rounds/:id/schedules` (§26) | **Field sai hoàn toàn.** `list_schedule_versions` ([`schedule_operations.py:478`](../../apps/api/app/routes/schedule_operations.py#L478)) trả `id, round_id, version_no, status, solver_status, total_score, soft_scores, random_seed, created_at, activated_at, is_active` — không phải `versionId,versionNumber,status,scheduledCount,unscheduledCount,overallScore,createdAt` như FE kỳ vọng. Lỗi đã nêu trong audit gốc (§58) hoá ra ảnh hưởng cả §26 — chưa sửa (thuộc Phase 3+, chưa làm). |
| B2 | `GET /rounds/:id/publish-readiness` (§69) | **Shape khác hẳn.** Response thực tế ([`target_room_publish.py:107`](../../apps/api/app/routes/target_room_publish.py#L107)): `{ready, versionId, blockers:[{code,message}]}` — **không có field `roomConflicts`** dạng số lượng như FE mong đợi. Cần thống nhất: hoặc FE đổi sang đọc `blockers`, hoặc BE thêm field `roomConflicts`. |
| B3 | `POST /rounds/:id/rooms/suggest` (§67) | Khớp — không cần tham số, `apply-suggestions` nhận payload riêng. Route target đúng đã thắng route legacy trùng path (`room_assignment.py`) nhờ thứ tự đăng ký router trong `main.py`. |
| B4 | `GET /lecturer/me/invitations` (§31) | Có, đúng router target nhưng **snake_case**: `round_id, response_reason, responded_at, round_status, semester_code` thay vì camelCase. ([`target_portals.py:39`](../../apps/api/app/routes/target_portals.py#L39)) |
| B5 | `GET/PUT /rounds/:id/availability/me` (§32/55) | Có ở [`target_round_contract.py:310-324`](../../apps/api/app/routes/target_round_contract.py#L310), dùng Pydantic model riêng — có vẻ đã camelCase, ổn hơn B4. |
| B6 | `GET /lecturer/me/sessions` + `GET /sessions/:id` (§33/35) | List có nhưng **snake_case** (`round_id, group_id, group_code, project_code, room_code, round_type`). Detail (`GET /sessions/:id`) nằm ở [`manager_extensions.py:571`](../../apps/api/app/routes/manager_extensions.py#L571), tag `manager-ui-compatibility` — không phải target, chưa rõ có field `result` đúng chỗ hay không, cần soi thêm nếu FE cần dùng route này cho vai Lecturer. |
| B7 | `GET /lecturer/me/supervised-projects` (§34) | Có nhưng **thiếu hẳn field `latestResult`** — hiện chỉ trả `id,code,title,status,semester_id,semester_code,supervisor_type`, toàn snake_case. ([`target_portals.py:74`](../../apps/api/app/routes/target_portals.py#L74)) |
| B8 | `GET /lecturer/me/remediations` (§36) | Có, **snake_case** tương tự (`group_id, group_code, due_at, verifier_lecturer_id, round_type`). ([`target_portals.py:90`](../../apps/api/app/routes/target_portals.py#L90)) |
| B9 | `GET /leader/me/dashboard` (§38) | **Thiếu hẳn field `preferenceStatus`** — response hiện tại chỉ có `{groups:[...], groupCount}`, không có enum FE tự đặt. ([`target_portals.py:111`](../../apps/api/app/routes/target_portals.py#L111)) |
| B10 | `GET /rounds/:id/groups/:id/preferences` (§39) | Có ở [`target_round_contract.py:357`](../../apps/api/app/routes/target_round_contract.py#L357) nhưng **snake_case** (`timeslot_id, start_at, end_at`) và `roundId/groupId` trả về là **số nguyên trần, không có prefix** (`rnd_`/`grp_`) — không nhất quán với PUT cùng endpoint (nhận `timeslot_ids` dạng chuỗi có prefix `ts_`). |
| B11 | `GET /leader/me/sessions` (§40) | **Đạt yêu cầu "không rò rỉ dữ liệu solver"** — không có `scheduleVersionLabel/softScore/maxGroupsPerTimeslot`. Nhưng vẫn snake_case (`round_id, group_code, project_code, room_code, round_type`). ([`target_portals.py:122`](../../apps/api/app/routes/target_portals.py#L122)) |

## Phần C — logic

- **C1** (4 trạng thái semester PLANNING/ACTIVE/CLOSED/ARCHIVED): **Đúng** — migration
  `0026_semester_four_states.py` đã áp dụng đúng 4 giá trị này ở DB thật. Lưu ý: dòng ghi chú
  "chỉ ACTIVE/CLOSED" trong `CLAUDE.md` đã lỗi thời (có từ trước migration 0026) — nên cập nhật
  lại file đó.
- **C2** (`maxGroupsPerTimeslot`, `resultOwnerMode`, `groupSelectionMode` giữ tên cũ): xác nhận
  đúng — các field này thấy nguyên tên trong [`manager_extensions.py:266`](../../apps/api/app/routes/manager_extensions.py#L266)
  (cột `max_groups_per_timeslot`, `result_owner_mode`, `group_selection_mode` — FE map sang
  camelCase là đúng hướng).
- **C3** (round tự chuyển trạng thái theo action): **Đúng** — `run_scheduler` set
  `rounds.status='SCHEDULING'` rồi `'SCHEDULED'`; `publish_schedule` set `'PUBLISHED'`. Khớp với
  FE mô tả, không cần endpoint transition riêng.
- **C4** (verifier LEVEL_2 giới hạn trong council của session): **chưa xác nhận được** — chỉ thấy
  cột `verifier_lecturer_id` được ghi ở `results.py:263,308`, chưa đọc kỹ logic chọn verifier có
  giới hạn theo council hay không. Cần soi sâu hơn nếu quan trọng.
- **C5** (Room CRUD thuộc Manager không phải Admin): route `target_room_publish.py` check
  `_manager()` cho phép cả `ADMIN` và `MANAGER` — không giới hạn chỉ Manager như FE giả định,
  nhưng Manager chắc chắn có quyền nên không sai, chỉ rộng hơn giả định của FE.
- **C6 (quan trọng nhất)**:
  - Group list (§41), Project list (§46): **đã có `meta:{page,pageSize,total}` đúng chuẩn** — do
    Phase 2 của kế hoạch alignment vừa sửa xong.
  - **Round list (§19): vẫn HOÀN TOÀN chưa có envelope** — `GET /rounds` ở
    [`master_data.py:1048`](../../apps/api/app/routes/master_data.py#L1048) trả thẳng
    `list[dict]`, không có cả `{"data":...}` chứ đừng nói `meta`. Đây là mục nặng nhất còn sót
    trong C6, chưa được đụng tới ở Phase 2.

## Đề xuất thứ tự xử lý (chưa thực hiện, chờ xác nhận)

1. `GET /rounds` (§19) — bọc envelope `{data, meta}` giống Group/Project list đã làm ở Phase 2.
2. camelCase hoá toàn bộ `target_portals.py` (B4, B6, B7, B8, B9, B11) — cùng một khuôn mẫu, sửa
   một lượt.
3. B1/B2 — thống nhất lại field với FE trước khi sửa (đổi field name có thể phá vỡ hợp đồng đang
   dùng), vì đây là quyết định thiết kế chứ không chỉ đổi tên.
4. A8/A9/A10 — endpoint mới hoàn toàn, cần thiết kế trước khi build.
5. A1/A2/A3/A4 (GET/POST rooms) — chuyển sang tag target + envelope chuẩn (đổi router hoặc thêm
   route target mới, tuỳ mức độ rủi ro phá vỡ FE đang gọi route cũ).
