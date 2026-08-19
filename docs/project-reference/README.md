# Capstone Scheduler – Project Reference

Thư mục này lưu các tài liệu nguồn nghiệp vụ và mô hình dữ liệu do nhóm cung cấp. Đây là tài liệu tham chiếu khi đọc code, thiết kế API và kiểm tra thuật toán xếp lịch.

## Tài liệu

| Tài liệu | Nội dung |
| --- | --- |
| [PRD](PRD_CapstoneScheduler_v1.0.md) | Phạm vi sản phẩm, yêu cầu chức năng, vai trò và luồng nghiệp vụ. |
| [ERD](ERD_CapstoneScheduler_v1.0.md) | Mô hình dữ liệu, bảng, quan hệ và các ràng buộc chính. |
| [Business Rules](BusinessRules_CapstoneScheduler_v1.0.md) | Các quy tắc nghiệp vụ dùng để đối chiếu khi triển khai scheduler và workflow. |

## Thứ tự đọc

1. Đọc PRD để xác định phạm vi và hành vi người dùng.
2. Đọc ERD để hiểu dữ liệu được lưu và liên kết như thế nào.
3. Đọc Business Rules để tra các mã quy tắc và điều kiện chi tiết.
4. Đối chiếu với [schema.sql](../../schema.sql), migration và tài liệu API trước khi thay đổi code.

## Lưu ý về nguồn sự thật

Các tài liệu này là nguồn yêu cầu/tham chiếu. Khi có khác biệt với hợp đồng triển khai hiện tại, ưu tiên tài liệu đặc tả trong `plans/`, migration/schema đang chạy và API được kiểm chứng trong test; không tự suy ra hành vi mới chỉ từ một tài liệu cũ.
