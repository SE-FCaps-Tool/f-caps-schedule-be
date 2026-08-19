# Brainstorm: Hoàn thiện flow quản lý học kỳ cho Manager

**Date:** 2026-08-19

## Ideas Explored

1. **Bổ sung ngay trên endpoint list hiện tại** — thêm filter và các count vào
   `GET /api/v1/semesters`; ít thay đổi route nhưng vẫn cần endpoint detail và
   action chuyển kỳ hiện tại.
2. **Tách endpoint detail/action riêng** — giữ list nhẹ, thêm
   `GET /semesters/{id}` và `POST /semesters/{id}/set-current`; dễ phân quyền,
   audit và dùng lại cho màn detail.
3. **Dùng một cột `is_current` riêng** — linh hoạt cho UI nhưng tạo hai nguồn
   sự thật với `status`; không chọn vì nghiệp vụ đã thống nhất `ACTIVE` là kỳ
   hiện tại.
4. **Cho phép chuyển kỳ `CLOSED` thành `ACTIVE`** — khi chọn kỳ hiện tại,
   transaction khóa các row semester, đóng kỳ active cũ và mở kỳ được chọn.
   Đây là hướng người dùng đã chọn.

## User's Direction

- Làm đầy đủ flow Manager: danh sách có counts, search/status/academic-year,
  detail, create/edit, khóa và chọn kỳ hiện tại.
- Semester chỉ có `ACTIVE` và `CLOSED`.
- Semester mới mặc định `ACTIVE`.
- Cho phép chuyển kỳ `CLOSED` thành `ACTIVE`; kỳ `ACTIVE` cũ tự chuyển thành
  `CLOSED` trong cùng transaction.
- Bổ sung các system fields `created_by`, `created_at`, `updated_by`,
  `updated_at`.

## Open Questions

- Không còn câu hỏi chặn triển khai. `academic_year` được coi là chuỗi filter
  tùy chọn (ví dụ `2026-2027`), lấy từ năm của khoảng ngày hoặc mã kỳ khi
  client truyền vào.

## Risks

- Chuyển kỳ hiện tại phải khóa row để tránh hai request đồng thời tạo hai kỳ
  `ACTIVE`.
- Dữ liệu cũ chưa có actor/timestamp update cần được backfill an toàn, để null
  cho actor không thể suy ra từ audit history.
- Tạo semester mặc định `ACTIVE` sẽ trả conflict nếu đã có kỳ active; FE phải
  hiển thị lỗi và dùng action “Chọn làm hiện tại” sau khi tạo theo flow phù hợp.
