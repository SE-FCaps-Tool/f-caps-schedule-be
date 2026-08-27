# Scheduling Flows — tổng hợp 4 luồng sắp xếp (as-is)

Bộ tài liệu này mô tả **hiện trạng code thật** (không phải thiết kế tương lai) của 4 luồng nghiệp vụ
BE liên quan tới xếp lịch bảo vệ đồ án, tính đến nhánh `dev` ngày 26/08/2026. Viết làm nền cho việc
thiết kế tính năng **config thuật toán sắp xếp** (`feature/scheduling-algorithm-config`). Chỉ phạm vi
BE (thuật toán + service) — không cover FE UI.

Mỗi file do 1 agent đọc code + đối chiếu tài liệu cũ độc lập, có thể có cách trình bày hơi khác nhau
nhưng cùng 1 khung 7 mục: Tổng quan → Entry points → Business logic → Data model → Config/hardcode →
Đối chiếu docs cũ → Giới hạn/edge case.

## Thứ tự đọc theo pipeline thực tế của 1 round

1. **[Auto-Scheduling Algorithm](./auto-scheduling-algorithm.md)** — CP-SAT solver ghép
   group → timeslot → tổ reviewer (H1-H13), tạo `ScheduleVersion` DRAFT, activate.
   File chính: `scheduler/scheduler.py`, `routes/schedule_operations.py`, `routes/target_schedule_contract.py`.
2. **[Council & Lecturer Assignment](./council-lecturer-assignment.md)** — lớp persistence bất biến
   ghi ai chấm phiên nào (`councils`/`council_members`), được gọi từ cả auto-scheduling lẫn manual
   scheduling, không tự quyết định chọn ai.
   File chính: `services/councils.py`.
3. **[Room Assignment](./room-assignment.md)** — gán phòng vật lý sau khi version đã activate (solver
   không chọn room), chặn publish nếu thiếu phòng hợp lệ.
   File chính: `routes/room_assignment.py`, `routes/target_room_publish.py`.
4. **[Manual Scheduling](./manual-scheduling.md)** — workspace nháp riêng cho Manager tự xếp tay
   (nhóm × timeslot × phòng × reviewer), độc lập bảng với auto-scheduling, có thể copy 1 bản solver
   làm điểm khởi đầu.
   File chính: `routes/manual_scheduling.py`.

## Phát hiện đáng chú ý nhất (liên quan trực tiếp tới việc config thuật toán)

- **Không có config surface tập trung**: `app/config.py` hiện **zero** setting cho scheduling — mọi
  trọng số/ràng buộc đều hardcode rải rác trong `scheduler.py`, `manual_scheduling.py`,
  `room_assignment.py`. Đây chính là khoảng trống mà branch `feature/scheduling-algorithm-config` cần lấp.
- **`h12_sessions_per_day` không có constraint CP-SAT thật** — chỉ validate hậu-kỳ (post-hoc), không
  chặn solver sinh candidate vi phạm ngay từ đầu.
- **Soft weights mặc định tắt**, và **objective profile `LEGACY`** (semester-balance) là dead code —
  route không bao giờ truyền `objective_profile="LEGACY"` trong production.
- **`councils.py` không tự chọn người** — mọi logic "nên chọn ai" nằm ở nơi gọi nó (solver hoặc tay
  Manager), không phải trong lớp persistence này. Quan trọng khi thiết kế config: đừng nhầm chỗ đặt
  tham số.
- **Room không nằm trong solver** — bất kỳ config nào về "ưu tiên phòng" phải tác động vào
  `room_assignment.py`, không phải `scheduler.py`.
- **Manual scheduling có bug thật đang tồn tại** (không phải giả định): bulk-upsert không validate
  blocker trước khi ghi (trái với `manual-scheduling-business-contract.md` §7); H11 chỉ yêu cầu *có*
  reviewer cũ bất kỳ chứ không phải đúng Chair cũ (trái BusinessRules doc); nhiều field cấu hình
  (`eligibleProjectStatuses`, `batchSize`, `chairMinLevel`...) là placeholder hardcode, chưa có
  implementation nào phía sau.

## Tài liệu cũ đã xác nhận lỗi thời (không nên dùng làm nguồn tham chiếu nữa)

| Doc | Vấn đề |
|---|---|
| `docs/SchedulingAlgorithm_v1.0 (1).md` | Mô tả thiết kế **tương lai** chưa hề có trong code (skills, CHAIR/SECRETARY role, ràng buộc H14-H16) |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` | Còn schema tiền-immutable-councils (`session_reviewers`, cột `is_active` trên council đã bị bỏ) |

Chi tiết đầy đủ + toàn bộ bảng đối chiếu từng doc khác nằm trong mục 6 của mỗi file luồng tương ứng.

## Chưa cover (ngoài phạm vi lần này)

- FE UI của cả 4 luồng.
- Mockup HTML `docs/council-scheduling-config/mockup/council-schedule-config-flow.html` chỉ được đối
  chiếu gián tiếp qua `council-algorithm-config-plan.md` §7 (file mockup quá lớn để đọc trực tiếp trong
  budget của agent) — cần đọc trực tiếp nếu cần diff sâu hơn với UI đã thiết kế.
