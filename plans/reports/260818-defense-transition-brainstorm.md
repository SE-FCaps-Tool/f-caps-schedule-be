# Brainstorm: Chốt transition Defense 1.2, Defense 2 và quyền quản trị round

**Date:** 2026-08-18

## Ideas Explored

1. Dùng bốn mức kết quả cho mọi Defense. Phương án này bám câu chữ FR-7.2 trong PRD nhưng tạo mapping không có căn cứ cho Defense 1.2/2 và có nguy cơ đưa group quay lại trạng thái cũ.
2. Defense 1.2 chỉ xác nhận hoàn tất phiên; Defense 2 dùng kết quả nhị phân. Phương án này khớp state machine trong PRD và BusinessRules: `DEFENSE_1_2 → COMPLETED`, còn Defense 2 tách rõ Đạt/Không đạt.
3. Giữ một outcome enum chung rồi để Manager tự chọn trạng thái. Phương án này linh hoạt nhưng biến policy thành quyết định thủ công, khó kiểm thử và dễ chuyển sai trạng thái.

## User's Direction

V1 tiếp tục là Scheduler-only. Quyền hủy hoặc hoãn toàn bộ round chỉ dành cho `ADMIN` và `MANAGER`. Transition được tối giản theo mô tả hiện có thay vì mở rộng sang logic Full Assessment.

## Decision

- Defense 1.1 giữ bốn mức và remediation Mức 2 như đã đặc tả.
- Defense 1.2 không nhập bốn mức; session hoàn tất thì group `COMPLETED`.
- Defense 2 là round cuối, chỉ có `PASS/FAIL`; pass thì `COMPLETED`, fail thì `FAILED`.
- Defense 2 không remediation và không có hard continuity Reviewer.
- `ADMIN` hoặc `MANAGER` được hoãn/hủy toàn bộ round; bắt buộc reason, audit và notification.

## Open Questions

Không còn câu hỏi chặn việc lập kế hoạch Scheduler-only.

## Risks

1. PRD FR-7.2 hiện viết chung “Defense nhập một trong bốn mức”, nên PRD/ERD/schema cần được chỉnh theo transition đã chốt.
2. Schema hiện chưa có trạng thái round `POSTPONED`/`CANCELLED` và outcome nhị phân riêng cho Defense 2.
3. Cần phân biệt rõ session bị hoãn/hủy vì vận hành với group `FAILED` vì kết quả đánh giá.
