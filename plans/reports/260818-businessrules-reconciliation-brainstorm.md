# Brainstorm: Reconcile PRD, BusinessRules, ERD và schema

**Date:** 2026-08-18  
**Scope:** toàn bộ artifact domain trong workspace: PRD, BusinessRules, ERD, `schema.sql`, ERD viewer và spec audit trước đó.

## Kết luận ngắn

Việc bổ sung `BusinessRules_CapstoneScheduler_v1.0.md` chưa làm project rõ hơn theo nghĩa “một source of truth”. Ngược lại, nó xác nhận rằng workspace đang chứa **hai sản phẩm khác nhau**:

1. **Scheduler-only** theo PRD, ERD và schema: thu lịch rảnh, xếp lịch, công bố, thay đổi, nhận kết quả cuối.
2. **Full assessment platform** theo BusinessRules: Gate 0, 9 tiêu chí, phiếu độc lập, hợp nhất 2/3, tự suy kết luận, Biên bản 07.20a và bảng yêu cầu chỉnh sửa.

Hai hướng này không thể cùng là MVP. PRD mục 2.3 đã nói phải bỏ toàn bộ phần chấm chi tiết trong BusinessRules, nhưng file BusinessRules hiện tại vẫn giữ nguyên các phần đó và tự ghi là “v1.0 (chốt)”.

## Bằng chứng đối chiếu

| Chủ đề | PRD / ERD / schema | BusinessRules mới | Kết luận |
|---|---|---|---|
| Phạm vi chấm | PRD loại Gate 0, 9 tiêu chí, phiếu, biên bản ra khỏi MVP | BusinessRules đưa toàn bộ vào phạm vi | Mâu thuẫn P0 |
| Vai hội đồng | 3 Reviewer ngang hàng | Chủ tịch / Phản biện / Thư ký | Mâu thuẫn P0 |
| Người chốt kết luận | Result Owner do Manager chỉ định | Chủ tịch override | Mâu thuẫn P0 |
| Người chốt mức 2 quá hạn | Manager | Chủ tịch hội đồng | Mâu thuẫn P0 |
| H11 | D1.2 giữ ít nhất 1 Reviewer cũ | D1.2 giữ nguyên Chủ tịch cũ | Mâu thuẫn P0 |
| Soft constraints | S2 Review 2; S3 D1.2; S4–S8 theo PRD | S2 D1.2; S3 Review 2; thêm vai trò cũ | Mâu thuẫn P1 |
| H12 | 4 phiên/buổi, 8 phiên/ngày + quota kỳ | BusinessRules chưa định nghĩa | Chưa chốt |
| H13 | Không có trong PRD | Không có | ERD/schema tự thêm |
| Kết quả | Nhận kết quả cuối cho Review và Defense | Có full ballot và systemConclusion | Hai mô hình dữ liệu khác nhau |
| Actor | Manager | Moderator, Chair, Secretary | Từ điển role không thống nhất |

## Những điểm BusinessRules đã làm rõ

BusinessRules bổ sung một số thông tin hữu ích:

- Review 1/2 không chặn nhóm đi tiếp.
- Mức 1/2/3/4 của Defense 1.1 và đường đi tới D1.2/D2.
- Mức 2 có remediation và người xác nhận.
- H11 có waiver theo từng nhóm.
- Sự cố vắng Reviewer phải hoãn phiên nếu không tìm được người thay.
- Dữ liệu drop out được tính theo ngày hiệu lực.
- Có câu hỏi mở O1–O8.

Tuy nhiên các điểm này vẫn đang mang quy tắc của full-assessment model, không phải bản cập nhật của scheduler-only PRD.

## Hai hướng cần chọn

### Hướng A — Scheduler-only (phù hợp với PRD và schema hiện tại)

Giữ sản phẩm là công cụ xếp lịch và nhận kết quả cuối.

- Ưu điểm: phạm vi capstone kiểm soát được; schema hiện tại đã có nền tảng tương ứng.
- Chi phí: phải viết lại BusinessRules để bỏ Section 8 và các BR-BAL/BR-GATE/BR-MRG/BR-CON/BR-MIN.
- Cần giữ lại: kết quả cuối, remediation tối giản, Result Owner, Verifier, flow D1.1/D1.2/D2.

### Hướng B — Full assessment platform

Giữ BusinessRules hiện tại làm chuẩn và mở rộng PRD, ERD, schema.

- Ưu điểm: bao phủ toàn bộ quy trình đánh giá.
- Chi phí: scope tăng rất mạnh; cần thêm ballot, Gate0, criteria, merge, override, minutes, secretary/chair workflow và nhiều bảng dữ liệu.
- Không còn phù hợp với câu “sản phẩm không phải công cụ chấm điểm” trong PRD.

### Đánh giá

Hướng A phù hợp hơn với mục tiêu và tên sản phẩm hiện tại. ERD/schema cũng đã đi theo Hướng A, nên Hướng B sẽ là một dự án khác chứ không phải mở rộng nhỏ.

## Các blocker còn lại nếu chọn Hướng A

1. Viết lại BusinessRules thành bản scheduler-only, không chỉ để PRD ghi “xóa” các rule cũ.
2. Chốt state transition cho D1.2 và D2; BusinessRules hiện chỉ nói D1.2 → Completed và D2 không đạt → Failed, nhưng chưa định nghĩa 4 outcome cho từng round.
3. Chốt H12 là số phiên, số phút hay cả hai.
4. Quyết định H13 có phải hard constraint không.
5. Chốt H11 theo PRD là “ít nhất một Reviewer cũ”, không phải “giữ Chủ tịch”.
6. Chốt Defense 2 có continuity rule hay ghép tự do; BusinessRules O1 vẫn mở, ERD đang ngầm tắt reuse cho D2.
7. Chốt Result Owner/Manager: schema hiện chỉ có `result_owner_mode` và `recorded_by_lecturer_id`, chưa lưu assignment đầy đủ.
8. Chốt xử lý round cancellation và nguồn dữ liệu MVP.

## Open Questions

- **[NEEDS CLARIFICATION: Product scope]** Chọn Scheduler-only hay Full assessment platform làm sản phẩm chính thức của V1?
- **[NEEDS CLARIFICATION: Canonical rules]** Nếu chọn Scheduler-only, BusinessRules mới có được coi là legacy cần rewrite theo PRD không?
- **[NEEDS CLARIFICATION: State and scheduling]** Bảng transition D1.2/D2, H12/H13 và Defense 2 continuity rule sẽ được chốt theo phương án nào?

## Risks

1. Nếu code theo BusinessRules hiện tại, nhóm sẽ xây nhầm full assessment platform dù PRD loại nó khỏi MVP.
2. Nếu code theo PRD nhưng không rewrite BusinessRules, mọi quyết định về role, H11 và kết quả sẽ tiếp tục bị hiểu hai cách.
3. ERD/schema hiện có các trường và comment tự thêm như H13, phút H12 nhưng chưa có source nghiệp vụ tương ứng; chúng có thể trở thành “quy định ngầm” khó sửa.

