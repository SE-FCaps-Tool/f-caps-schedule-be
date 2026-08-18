# Brainstorm: Full audit — Capstone Defense Scheduler

**Date:** 2026-08-18  
**Scope:** `PRD_CapstoneScheduler_v1.0.md`, `ERD_CapstoneScheduler_v1.0.md`, `schema.sql`, `erd-viewer.html`

## Kết luận ngắn

Đây là dự án **nhỏ về dữ liệu nhưng không nhỏ về nghiệp vụ**. Quy mô vài trăm phiên mỗi kỳ hoàn toàn phù hợp với một modular monolith dùng PostgreSQL; phần khó nằm ở constraint scheduling, workflow kết quả, quyền theo ngữ cảnh, thay đổi sau công bố và audit.

Bộ tài liệu đã có một backbone tốt và cùng mô tả 31 bảng. Tuy vậy, chưa nên chuyển thẳng sang code vì còn một số mâu thuẫn P0 giữa PRD–ERD–schema. Đặc biệt: cách hiểu “ràng buộc cứng”, Result Owner, luồng kết quả sau Defense 1.2/Defense 2, và các khóa liên bảng đang chưa được chốt.

## Các hướng đã xem xét

### 1. Xây toàn bộ nền tảng trong một lần

Bao phủ import, SSO, email, xếp lịch tối ưu, sửa lịch sau công bố, kết quả, remediation, báo cáo và Excel ngay từ MVP.

- Ưu điểm: đúng tầm nhìn PRD.
- Chi phí: quá nhiều đường đi và trạng thái để kiểm thử cùng lúc; dễ biến capstone thành dự án tích hợp thay vì chứng minh lõi xếp lịch.

### 2. Modular monolith, lấy lõi xếp lịch làm trung tâm

Một backend và PostgreSQL, chia module theo domain: identity, academic data, rounds, availability, scheduling, results, notifications. Thuật toán trả về `ScheduleVersion`; mọi thao tác sau đó đi qua một service kiểm tra constraint và audit.

- Phù hợp nhất với quy mô hiện tại.
- Giữ được khả năng mở rộng mà không phải vận hành microservices.
- Cần làm rõ state machine và các invariant trước khi code.

### 3. Workflow-first, dùng lịch thủ công có validator trước

Ra mắt quản lý dữ liệu, slot, phân quyền, công bố và validator H1–H12; Manager vẫn xếp thủ công. Optimizer được đưa vào sau khi có dữ liệu thực tế.

- Ít rủi ro vận hành và dễ pilot.
- Không đạt ngay mục tiêu quan trọng nhất là giảm thời gian xếp lịch.

### 4. Database-enforced invariants + optimizer

Giữ hướng hiện tại của ERD: dùng unique/check/trigger cho các bất biến quan trọng, còn thuật toán tối ưu ở application layer.

- Ý tưởng `session_reviewers` để cưỡng chế H2 là hợp lý.
- Không được nhầm rằng các comment trong schema đã là trigger thực tế; hiện file mới mô tả những trigger cần viết.

## Hướng người dùng đang theo

Người dùng muốn đánh giá toàn bộ workspace và xác định dự án đã đủ chín để đi tiếp hay chưa. Từ các artifact hiện có, hướng hợp lý là **modular monolith + scheduling core + database invariants**, triển khai theo pha và chạy song song Excel trong một kỳ.

## Những điểm đã làm tốt

1. PRD mô tả đúng pain point và có số đo: thời gian xếp lịch, vi phạm GVHD, cân bằng tải, deadline, audit.
2. Phạm vi “không chấm điểm chi tiết” được giới hạn rõ, tránh biến sản phẩm thành LMS/assessment platform.
3. Mô hình role hệ thống và role theo ngữ cảnh phản ánh đúng nghiệp vụ: một Lecturer có thể vừa là Supervisor vừa là Reviewer.
4. Ý tưởng lưu `ScheduleVersion` và `session_reviewers` giải quyết được hai vấn đề thực tế: so sánh phương án và giữ ảnh chụp người chấm.
5. Schema đã có nhiều bảo vệ tốt ở tầng DDL: một kỳ ACTIVE, một GVHD chính, một Leader active tối đa, H2/H3/H4 ở mức khóa duy nhất, remediation mức 2 và lý do thay đổi hội đồng.
6. `erd-viewer.html` khớp 31 entity với schema và giúp review mô hình dễ hơn.

## Các vấn đề cần xử lý trước khi lập kế hoạch triển khai

### P0 — Mâu thuẫn hoặc thiếu dữ liệu làm thay đổi hành vi hệ thống

1. **Ràng buộc cứng không nhất quán.** PRD định nghĩa H1–H12 là hard constraints, nhưng FR-5.7 chỉ chặn H1–H3 và FR-5.8 cho phép cảnh báo + lý do với “ràng buộc khác”. Như vậy H4–H12 có thể bị vi phạm bằng sửa tay, trái với mục 7.1. Cần quy định rõ: tất cả H đều chặn, ngoại lệ nào được waiver, và waiver lưu ở đâu.

2. **Result Owner chưa có trong schema.** PRD yêu cầu Manager chỉ định một Reviewer làm Result Owner khi `resultOwnerMode` bật, nhưng không có bảng/cột assignment. `session_results.recorded_by_lecturer_id` chỉ ghi người nhập sau sự kiện, không ghi người được chỉ định trước đó và cũng không thể biểu diễn Manager nhập kết quả.

3. **Luồng kết quả sau Defense 1.2 và Defense 2 chưa đầy đủ.** PRD nêu 4 outcome cho Defense nhưng sơ đồ chỉ mô tả rõ Defense 1.1 và một phần Defense 2. Phụ lục schema dùng các mapping L1→ELIGIBLE_D12, L2→D12_CONDITIONAL... một cách chung chung; nếu áp dụng cho D1.2 sẽ tạo loop hoặc trạng thái sai. Cần state-transition matrix theo từng `round_type`.

4. **H12 đổi đơn vị nhưng PRD chưa đổi theo.** PRD nói tối đa 4 phiên/buổi, 8 phiên/ngày; ERD/schema dùng `max_minutes_per_part/day`. Với phiên 45 phút, mặc định 240 phút cho phép 5 phiên; với phiên 90 phút, chỉ cho 2 phiên. Cần chốt đây là giới hạn theo số phiên, theo phút, hay cả hai.

5. **H13 xuất hiện trong ERD/schema nhưng không có trong PRD.** `max_groups_per_timeslot` và giới hạn tổng phiên trong một timeslot có thể là yêu cầu hợp lý, nhưng chưa có định nghĩa nghiệp vụ, ưu tiên và cách tương tác với số phòng/hội đồng.

6. **H11 waiver chưa có mô hình dữ liệu rõ.** PRD cho Manager gỡ H11 theo từng nhóm, bắt buộc ghi lý do; schema không có cờ/record waiver. Audit log generic không đủ tốt để truy vấn “nhóm nào đang được miễn H11” khi chạy thuật toán lại hoặc báo cáo.

### P1 — Schema chưa bảo vệ đúng các invariant đã tuyên bố

1. Các khóa phi chuẩn hóa chưa có khóa liên bảng để bảo đảm cùng round: `timeslots.round_id` vs `round_day_id`, `sessions.round_id` vs `schedule_version_id/timeslot_id`, availability vs timeslot, session reviewer vs session.
2. `sessions.room_id` không bắt buộc phải thuộc `round_rooms`; `sessions.group_id` không bắt buộc phải thuộc `round_groups`; `sessions.council_id` không bắt buộc thuộc cùng round.
3. `session_reviewers.schedule_version_id` và `timeslot_id` không có FK, nên có thể lệch khỏi `session_id`. Cơ chế “trigger đồng bộ” mới nằm trong comment, chưa tồn tại trong `schema.sql`.
4. Unique theo `timeslot_id` chỉ chặn trùng cùng ID, không chặn hai timeslot bị overlap về thời gian. H2/H3 thực tế cần exclusion constraint trên khoảng thời gian hoặc trigger chống overlap.
5. `council_members` được mô tả là bất biến nhưng DDL chưa cấm UPDATE/DELETE. `audit_logs` được mô tả là không xóa được nhưng DDL cũng chưa cấm UPDATE/DELETE.
6. Schema chỉ đảm bảo **tối đa** một Leader active, không đảm bảo **ít nhất** một Leader; nhóm 4–5 thành viên, tối đa 2 Supervisor và trạng thái drop-out đã được duyệt cũng chưa được cưỡng chế đầy đủ.
7. `group_slot_preferences.selected_by` chỉ FK tới Student, chưa kiểm tra người đó là Leader active của đúng group. Nhiều bảng có `round_id` và ID con nhưng chưa có consistency constraint.
8. `session_results` chưa kiểm soát đầy đủ các cặp trạng thái remediation: verifier/verify status/verified_at/overdue close có thể tồn tại sai ở outcome không phải L2.

### P2 — Tài liệu và bằng chứng

1. `BusinessRules_v1.0.md` được PRD và ERD dẫn chiếu nhưng không có trong workspace. Vì vậy chưa thể xác minh phần “các quy tắc còn lại giữ nguyên hiệu lực”.
2. ERD nói còn “8 câu mở” và nhắc A8, trong khi PRD hiện có A1–A5, B1–B4, C1–C4, D1–D4 và không có A8. Đây là dấu hiệu ERD còn sót từ phiên bản trước.
3. ERD/HTML tuyên bố “16/16 ca kiểm thử” đã chạy trên PostgreSQL 16, nhưng workspace không có file test, fixture hoặc log chạy; máy hiện tại cũng không có `psql`. Claim này chưa thể tái kiểm chứng từ artifact.
4. PRD yêu cầu xuất Excel đúng file `su26_review_1.1_SE.xlsx`, nhưng file mẫu không có trong workspace. Chưa thể kiểm tra FR-8.8.

## Đánh giá theo khía cạnh

| Khía cạnh | Đánh giá | Nhận xét |
|---|---|---|
| Giá trị nghiệp vụ | Tốt | Pain point cụ thể, có người dùng và chỉ số thành công rõ |
| Phạm vi sản phẩm | Khá | Có ranh giới không chấm điểm, nhưng MVP vẫn nhiều P0 |
| Mô hình dữ liệu | Khá tốt | 31 bảng có cấu trúc hợp lý; còn thiếu nhiều consistency constraint |
| Lõi thuật toán | Chưa chốt | Có hard/soft constraints nhưng semantics H12–H13 và waiver chưa ổn định |
| Workflow kết quả | Chưa đủ | D1.2/D2 và Result Owner cần đặc tả lại |
| Audit và vận hành | Có nền tảng | Có bảng log, nhưng tính bất biến và lifecycle chưa được DB bảo vệ |
| Khả năng triển khai | Có thể làm | Phù hợp modular monolith; không cần microservices ở quy mô này |
| Mức sẵn sàng viết code | Chưa sẵn sàng | Cần đóng các P0 trước khi tạo plan triển khai |

## Đề xuất cắt MVP thực tế

### P1 — phải chứng minh được trong capstone

- Import và quản lý semester/project/group/student/supervisor.
- Tạo round, timeslot, room, invitation và availability.
- Feasibility scheduler tuân thủ toàn bộ hard constraints đã chốt.
- Lưu nhiều `ScheduleVersion`, chọn active, giải thích nhóm chưa xếp được.
- Công bố lịch, sửa từng phiên sau công bố, audit đầy đủ.
- Lịch cá nhân và bảng lịch Manager.
- Kết quả Defense 1.1 với state transition được đặc tả rõ.

### P2 — chỉ giữ nếu còn thời gian và đã có dữ liệu thật

- Group slot selection.
- H11 preference/waiver nâng cao.
- Email delivery hoàn chỉnh, retry và template.
- So sánh nhiều phương án với scoring chi tiết.
- Excel compatibility và iCal.
- Remediation escalation nâng cao.

### Nên tạm hoãn

- Mở đa ngành, mobile native, SSO hai nhà cung cấp cùng lúc, các báo cáo không phục vụ quyết định vận hành.

## Hành động tiếp theo trước `ck-plan`

1. Chọn một source of truth: hợp nhất BusinessRules vào PRD hoặc bổ sung file BusinessRules còn thiếu.
2. Viết ma trận traceability: `FR/H/S/BR → table/trigger/service/test`.
3. Viết state-transition matrix riêng cho Review 1, Review 2, Defense 1.1, Defense 1.2 và Defense 2.
4. Chốt ba nhóm clarification ở dưới; sau đó mới khóa ERD/schema.
5. Tạo fixture nhỏ 3–5 nhóm và fixture gần thật 74 nhóm/26 GV để kiểm thử feasibility, overlap, H1, H11, H12 và rerun.

## Open Questions

- **[NEEDS CLARIFICATION: Kết quả]** Result Owner có áp dụng cho Review không? Manager có được nhập kết quả trực tiếp không? D1.2/D2 map 4 outcome sang trạng thái nào?
- **[NEEDS CLARIFICATION: Constraint]** H12 tính theo số phiên hay số phút? H13 có phải hard constraint không? Sửa tay được waiver những H nào, và H11 waiver lưu ra sao?
- **[NEEDS CLARIFICATION: Source of truth]** BusinessRules và file Excel mẫu nào là bản chính thức; các quyết định chưa trả lời trong PRD mục 12 có được khóa cho MVP không?

## Risks

1. Thuật toán không vô nghiệm chỉ vì availability thiếu hoặc quota không được seed; cần fallback và lý do không xếp được.
2. Workflow kết quả sai có thể đưa nhóm vào nhầm Defense 1.2/Defense 2, rủi ro nghiệp vụ cao hơn lỗi UI.
3. Dữ liệu denormalized không đồng bộ sẽ làm mất ý nghĩa của H2/H3 dù schema nhìn có vẻ đã bảo vệ được.

