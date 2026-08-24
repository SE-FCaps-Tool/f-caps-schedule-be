# 05. Feature scheduling từ A đến Z

Scheduling là feature tốt nhất để hiểu kiến trúc vì nó đi qua HTTP, domain rule, raw SQL,
algorithm, versioning, transaction, room assignment, publish và notification.

## Bức tranh tổng thể

```text
Round setup
  -> registered groups + projects + leaders
  -> timeslots + availability + conflicts
  -> reviewer pool hoặc bound Committees
  -> POST schedule/run
  -> build RoundInput
  -> generate candidates
  -> CP-SAT solve
  -> validate H1-H13
  -> persist DRAFT ScheduleVersion + assignments
  -> activate version -> Sessions + immutable Councils
  -> assign physical rooms
  -> publish readiness
  -> publish + outbox notifications
```

## Các file nên mở theo thứ tự

1. `routes/schedule_operations.py`: orchestration HTTP và persistence.
2. `scheduler/models.py`: input/output dataclasses.
3. `scheduler/candidates.py`: candidate nào được phép tồn tại.
4. `scheduler/scheduler.py`: CP-SAT constraints và objective.
5. `scheduler/validator.py`: kiểm tra độc lập output.
6. `scheduler/snapshot.py`: input snapshot.
7. `domain/round_setup.py`, `domain/round_types.py`, `domain/transitions.py`: setup/state rules.
8. `services/room_assignment.py`, `services/councils.py`: operational materialization.
9. Migrations `0003`, `0004`, `0021`-`0025`, `0034`, `0036`-`0038`.
10. Scheduler/contract/integration tests liên quan.

## Bước 1: API và authorization

`POST /api/v1/rounds/{round_id}/schedule/run` gọi `run_scheduler()` trong
`routes/schedule_operations.py`.

Input `ScheduleRunPayload` có time limit và random seed. `Db` và `User` được inject. Handler chỉ
cho `ADMIN/MANAGER`, rồi mở transaction và gọi `ensure_round_semester_writable()`.

Round bị lock bằng `FOR UPDATE`. Nếu chưa ở trạng thái `SCHEDULING`, `transition_round()` kiểm tra
transition rồi `_validate_scheduler_inputs()` kiểm tra setup trước khi update state.

## Bước 2: Build `RoundInput`

`_round_input()` query và chuẩn hóa:

- group -> project và progression status;
- active group leader;
- timeslot intervals;
- reviewer pool và availability;
- project supervisors;
- reviewer-project conflicts;
- group selected slots;
- previous reviewers/remediation verifier;
- H11 waivers;
- H12 quotas/load/minute caps;
- bound committees;
- H13 slot capacity;
- soft weights.

Output là `RoundInput` cùng lists groups/timeslots/reviewers. Đây là ranh giới giữa dữ liệu DB và
compute core.

## Bước 3: Candidate generation

`generate_candidates()` trong `scheduler/candidates.py` tạo các bộ:

```text
(group, timeslot, reviewer tuple)
```

Candidate bị loại sớm nếu vi phạm eligibility/leader, supervisor conflict, declared conflict,
availability, selected slots hoặc reviewer continuity. Nếu Round bind Committees,
`_reviewer_tuples()` chỉ dùng Committee hoàn chỉnh và hợp lệ; không tự bù reviewer từ free pool.

Thiết kế này giảm kích thước CP-SAT model: solver không cần biểu diễn một lựa chọn vốn đã chắc chắn
không hợp lệ.

## Bước 4: CP-SAT solve

`solve_schedule()` trong `scheduler/scheduler.py`:

1. Gọi `generate_candidates()`.
2. Tạo một Boolean decision variable cho mỗi candidate.
3. Thêm hard constraints còn lại, như at-most-one group, reviewer overlap, quotas và slot cap.
4. Tối ưu ưu tiên số group được xếp, sau đó soft scores/load balance.
5. Dùng một search worker và random seed để kết quả có tính reproducible với cùng input.
6. Chuyển selected candidates thành `ScheduledSession` với `room_id=None`.

Room cố ý chưa được chọn ở bước solve. Room assignment là phase vận hành sau activation.

## Bước 5: Validator H1-H13

`validate_schedule()` kiểm tra lại output độc lập với solver:

| Rule | Ý nghĩa đơn giản |
|---|---|
| H1 | Supervisor không review project của mình |
| H2 | Lecturer không ở hai session trùng thời gian |
| H3 | Một room không chứa hai session trùng thời gian |
| H4 | Một group tối đa một lần trong một version |
| H5 | Đủ đúng số reviewer theo round type |
| H6 | Không lặp reviewer trong cùng session |
| H7 | Reviewer phải AVAILABLE |
| H8 | Không vi phạm declared reviewer-project conflict |
| H9 | Group status đủ điều kiện cho round type |
| H10 | Nếu bật group selection, dùng slot group đã chọn |
| H11 | Defense 1.2 giữ continuity hoặc có waiver hợp lệ |
| H12 | Không vượt workload/session/minute quotas |
| H13 | Không vượt số group tối đa trong timeslot |

Còn một invariant `GROUP_LEADER`: group cần đúng một active project leader khi context cung cấp
leader validation.

Reviewer count hiện tại: Review 1.1/2.1 = 2; Defense 1.1 = 3; Defense 1.2/2 = 5. Domain vẫn có
alias cho legacy round names do lịch sử migration; không tự ý “dọn enum” mà chưa kiểm tra data và
client compatibility.

## Bước 6: Snapshot và persistence

`build_input_snapshot()` tạo JSON snapshot phục vụ audit/replay. `run_scheduler()` sau đó tạo
`schedule_versions`, durable `schedule_assignments`, reviewer assignments và các bản ghi liên quan
trong transaction.

`scheduler/jobs.py` và `scheduler/versions.py` là in-memory seams, không phải persistence runtime.
Production truth là các tables/mutations trong routes và migrations.

Nếu không xếp được tất cả group, result có thể `PARTIAL` và lưu structured unscheduled reasons;
đây không nhất thiết là crash.

## Bước 7: Activate

`POST /api/v1/schedule/versions/{version_id}/activate` gọi `activate_schedule_version()`.

Activation chuyển một version thành phương án vận hành, materialize Sessions và sealed Councils,
đồng thời xử lý active-version lifecycle. Council là snapshot reviewer bất biến. Nếu cần thay
reviewer sau đó, flow controlled replacement tạo Council/supersession mới thay vì sửa member cũ.

## Bước 8: Room assignment

Solver để `room_id=None`. `services/room_assignment.py` gán room sau activation dựa trên room types
được Round cho phép. Service dùng row/advisory locks và kiểm tra conflict xuyên các ACTIVE/PUBLISHED
versions.

H3 vì vậy là operational/post-room constraint. Không thêm room vào solver chỉ vì thấy
`room_id=None`; đó là thay đổi kiến trúc và blast radius lớn.

## Bước 9: Publish

Publish readiness yêu cầu mọi Session có active room đúng type và không overlap. Publish endpoint
đổi lifecycle state, ghi audit và enqueue recipients/outbox. Worker sau đó xử lý notifications.

## Bước 10: Controlled operations và results

Sau publish, thay đổi không nên mutate lịch sử im lặng. Các endpoints edit/change/postpone/makeup/
reschedule ghi reason, change records, Council supersession và audit. Results/remediation được gắn
với operational Session.

## Rủi ro đã xác nhận trong scheduling

- `scheduler/registry.py` liệt kê H1-H12 nhưng validator có H13; registry cũng thiếu S9.
- Solver chưa encode rõ daily session-count branch của H12 trong khi validator kiểm tra sau solve;
  một output có thể bị validator reject thay vì solver tránh từ đầu.
- Snapshot hiện có dấu hiệu chưa chứa mọi field của `RoundInput`; cần kiểm tra cả
  `algorithm_parameters` trước khi cam kết “replay hoàn toàn”.
- `reason_for_unscheduled()` có thể đưa lý do gần đúng, không phải proof tối thiểu duy nhất.
- `public_session_projection()` hiện trả row nguyên trạng; privacy đang phụ thuộc query scoping.

Các mục trên là điểm review/technical debt, không phải giấy phép sửa riêng lẻ. Mọi thay đổi cần
đối chiếu candidate generator, solver, validator, persistence, publish và tests cùng lúc.

