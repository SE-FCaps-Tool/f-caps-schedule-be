# Spec: Capstone Defense Scheduler — Scheduler-only V1

**Date:** 2026-08-18  
**Status:** Ready

---

## Problem Statement

Bộ môn KTPM đang xếp khoảng 370 phiên Review/Defense mỗi học kỳ bằng quy trình thủ công, khiến việc thu lịch rảnh, tránh xung đột, cân bằng tải, công bố thay đổi và theo dõi nhóm đi tiếp phụ thuộc nhiều vào kiểm tra thủ công. V1 cần một ứng dụng web Scheduler-only quản lý toàn bộ vòng đời lịch và chỉ nhận kết quả cuối để điều hướng nhóm; hệ thống không số hóa quy trình chấm chi tiết.

---

## User Stories

- **[P1]** As an Admin, I want to quản lý tài khoản, giảng viên, phòng và quyền hệ thống so that dữ liệu nền dùng cho mọi đợt là nhất quán.
  Accepted when: chỉ tài khoản đang hoạt động mới đăng nhập được; mỗi người có một định danh duy nhất; thao tác quản trị quan trọng có audit log.

- **[P1]** As a Manager, I want to tạo học kỳ, đề tài, nhóm, thành viên và phân công GVHD so that dữ liệu học thuật đủ tin cậy để kiểm tra ràng buộc lịch.
  Accepted when: một đề tài có 1–2 GVHD và đúng một GVHD chính; một nhóm có đúng một Leader đang hoạt động trước khi được xếp lịch; lịch sử drop out không bị mất.

- **[P1]** As a Manager, I want to tạo một đợt đánh giá, ngày, timeslot, phòng, nhóm tham gia và danh sách giảng viên được mời so that scheduler có đủ đầu vào hợp lệ.
  Accepted when: round không thể chuyển sang bước xếp lịch nếu thiếu nhóm, timeslot, phòng hoặc cấu hình số Reviewer.

- **[P1]** As a Lecturer, I want to chấp nhận/từ chối lời mời, chọn slot rảnh và mức tải mong muốn so that tôi chỉ được xếp vào thời gian có thể tham gia.
  Accepted when: Lecturer hoàn tất lựa chọn 5 ngày × 8 slot trong dưới 2 phút trên điện thoại; quá deadline chỉ Manager mới sửa hộ được.

- **[P1]** As a Project Leader, I want to chọn các slot nhóm có thể tham gia khi Manager bật chế độ cho nhóm chọn lịch so that lịch hạn chế xung đột với cả nhóm.
  Accepted when: chỉ Leader đang hoạt động của đúng nhóm được gửi lựa chọn; khi chế độ tắt, nhóm không được chỉnh availability.

- **[P1]** As a Manager, I want to chạy scheduler và so sánh các phương án so that có thể chọn một lịch hợp lệ, cân bằng và giải thích được.
  Accepted when: mỗi lần chạy tạo một ScheduleVersion độc lập, ghi tham số, điểm từng soft constraint, nhóm chưa xếp và lý do; chỉ một version được active trong một round.

- **[P1]** As a Manager, I want to sửa lịch thủ công và xử lý thay đổi sau công bố so that sự cố được giải quyết mà không phá hard constraint hoặc lịch sử.
  Accepted when: mọi thay đổi được kiểm tra constraint trước khi lưu; thay đổi sau publish bắt buộc có lý do, before/after, actor, timestamp và thông báo tới người bị ảnh hưởng.

- **[P1]** As a Lecturer or Student, I want to xem đúng lịch liên quan đến mình so that không phải dò lịch thủ công và không nhìn thấy dữ liệu không được phép.
  Accepted when: Lecturer thấy các phiên được phân công hoặc nhóm mình hướng dẫn; Student chỉ thấy lịch và kết quả của nhóm mình.

- **[P1]** As a Reviewer, I want to nhập kết quả cuối của phiên so that hệ thống có đủ dữ liệu để cảnh báo hoặc chuyển nhóm sang đợt tiếp theo.
  Accepted when: outcome hợp lệ theo loại round, người nhập là người có quyền ở phiên đó, và thay đổi kết quả đã lưu luôn có audit.

- **[P1]** As a Manager, I want to theo dõi nhóm chưa xếp, tải giảng viên, thay đổi lịch và trạng thái nhóm so that có thể xử lý ngoại lệ trước khi ảnh hưởng đợt đánh giá.
  Accepted when: dashboard hiển thị ít nhất tiến độ availability, số nhóm đã/chưa xếp, vi phạm/cảnh báo, tải giảng viên và yêu cầu đổi lịch đang chờ.

- **[P2]** As a user, I want to nhận email/in-app notification và tải lịch iCal so that không bỏ lỡ lịch mới hoặc thay đổi.
  Accepted when: thông báo có trạng thái gửi, retry được, và file iCal mở đúng thời gian trong Google Calendar/Outlook.

- **[P3]** _(out of scope — noted for future)_ Full Assessment Platform gồm Gate 0, 9 tiêu chí, phiếu cá nhân, hợp nhất 2/3, tự suy kết luận, đánh giá đóng góp cá nhân, Biên bản 07.20a và bảng yêu cầu chỉnh sửa chi tiết.

---

## Functional Requirements

### A. Phạm vi và quyền

1. **FR-01 — Product boundary:** V1 là Scheduler-only. Hệ thống quản lý dữ liệu, lịch, công bố/thay đổi lịch, kết quả cuối và trạng thái đủ điều kiện; không thực hiện chấm chi tiết.
2. **FR-02 — System roles:** Có bốn role hệ thống: `ADMIN`, `MANAGER`, `LECTURER`, `STUDENT`.
3. **FR-03 — Contextual roles:** `Supervisor`, `Reviewer`, `Result Owner`, `Remediation Verifier` và `Project Leader` được suy ra từ assignment của từng thực thể, không phải role tài khoản độc lập.
4. **FR-04 — Admin permissions:** Admin quản lý tài khoản, master data giảng viên/phòng, cấu hình hệ thống, xem audit toàn hệ thống và mở khóa dữ liệu đã `LOCKED`.
5. **FR-05 — Manager permissions:** Manager quản lý dữ liệu học kỳ, round, scheduling, publish, thay đổi lịch, yêu cầu đổi lịch, kết quả cuối, waiver được cho phép và báo cáo.
6. **FR-06 — Lecturer permissions:** Lecturer quản lý availability của mình, xem lịch cá nhân, khai báo conflict, xem nhóm mình hướng dẫn/được phân công và nhập kết quả khi có quyền theo phiên.
7. **FR-07 — Student permissions:** Student chỉ xem dữ liệu nhóm mình; Leader đang hoạt động được chọn slot và gửi yêu cầu đổi lịch cho nhóm.
8. **FR-08 — Result Owner:** Result Owner chỉ áp dụng cho phiên Defense có nhập kết quả đánh giá (`DEFENSE_1_1` và `DEFENSE_2`). Khi `resultOwnerMode = true`, Manager phải chỉ định đúng một Reviewer của session làm Result Owner và chỉ người đó hoặc Manager được nhập kết quả. Khi mode tắt, bất kỳ Reviewer nào của session hoặc Manager đều được nhập; hệ thống lưu người nhập thực tế. Defense 1.2 chỉ xác nhận hoàn tất phiên nên không cần Result Owner.
9. **FR-09 — Review result owner:** Review 1/2 không dùng Result Owner; một trong hai Reviewer hoặc Manager được nhập kết quả cuối.
10. **FR-10 — Result correction:** Manager được nhập trực tiếp, sửa hoặc thay thế kết quả cuối; nếu kết quả đã tồn tại thì bắt buộc nhập lý do và ghi before/after trong audit log.

### B. Dữ liệu nền và nhập liệu

11. **FR-11 — Semester:** Semester có bốn trạng thái `PLANNING`, `ACTIVE`, `CLOSED`,
    `ARCHIVED`. Chỉ một học kỳ được `ACTIVE` tại một thời điểm; `PLANNING` dành cho chuẩn bị
    enrollment/group/project và chưa được tạo Round, `CLOSED` kết thúc nghiệp vụ, còn `ARCHIVED`
    là chỉ đọc.
12. **FR-12 — Project and supervisor:** Mỗi project thuộc đúng một semester và một major, có mã duy nhất trong semester, 1–2 Supervisor và đúng một `MAIN`.
13. **FR-13 — Group:** Mỗi project gắn đúng một group trong semester; group có mã riêng và có 4–5 Student lúc thành lập.
14. **FR-14 — Membership history:** Membership lưu `joinedAt`, `leftAt`, trạng thái và vai trò. Drop out phải có người yêu cầu, người duyệt, ngày hiệu lực và lý do.
15. **FR-15 — Leader invariant:** Group phải có đúng một Leader đang hoạt động trước khi đăng ký slot hoặc được đưa vào scheduler. Nếu Leader drop out, các thao tác này bị chặn đến khi có Leader mới.
16. **FR-16 — Small group:** Group dưới 4 thành viên do drop out chỉ tạo cảnh báo, không bị chặn xếp lịch.
17. **FR-17 — Lecturer identity:** Lecturer dùng một `lecturerCode` duy nhất cho mọi liên kết; form/API phải phát hiện một người xuất hiện dưới nhiều định danh.
18. **FR-18 — Manual data source:** V1 nhập dữ liệu nền qua form quản trị/API và seed fixture có version; tích hợp Excel và FAP không thuộc V1.
19. **FR-19 — Data validation:** Trước khi lưu, form/API phải phát hiện tối thiểu: trùng mã, thiếu dữ liệu bắt buộc, thiếu/nhầm GVHD chính, Supervisor không tồn tại, group sai sĩ số, Student trùng membership, thiếu Leader và một người có hai định danh.
20. **FR-20 — Atomic data mutation:** Mỗi thao tác tạo/sửa dữ liệu nền nhiều bản ghi phải atomic; hoặc toàn bộ thay đổi hợp lệ được ghi, hoặc không ghi gì. Thao tác phải lưu actor và thời gian trong audit log.

### C. Đợt đánh giá và đăng ký

21. **FR-21 — Round types:** Hỗ trợ `REVIEW_1`, `REVIEW_2`, `DEFENSE_1_1`, `DEFENSE_1_2`, `DEFENSE_2`.
22. **FR-22 — Round lifecycle:** Vòng đời chuẩn là `DRAFT → OPEN_REGISTRATION → REGISTRATION_CLOSED → SCHEDULING → SCHEDULED → PUBLISHED → ONGOING → COMPLETED → LOCKED`. `POSTPONED` là nhánh tạm thời từ `PUBLISHED`/`ONGOING`; `CANCELLED` là nhánh kết thúc có thể đi từ mọi trạng thái trước `LOCKED`.
23. **FR-23 — Round configuration:** Manager cấu hình độ dài session, số Reviewer, deadline, ngày/timeslot, phòng, nhóm, `groupSelectionMode`, `resultOwnerMode`, giới hạn tải và trọng số soft constraint.
24. **FR-24 — Reviewer count:** Review 1/2 có đúng 2 Reviewer; Defense 1.1/1.2/2 có đúng 3 Reviewer ngang hàng về vai trò đánh giá.
25. **FR-25 — Timeslot:** Timeslot có ngày, giờ bắt đầu, giờ kết thúc và buổi; các timeslot trong cùng round không được tạo dữ liệu thời gian mâu thuẫn.
26. **FR-26 — Invitations:** Manager gửi lời mời theo round. Lecturer chấp nhận hoặc từ chối; từ chối bắt buộc có lý do.
27. **FR-27 — Lecturer availability:** Lecturer đã chấp nhận chọn các timeslot rảnh và `LOW/MEDIUM/HIGH`. Không chọn slot nào trước deadline được hiểu là bận toàn bộ.
28. **FR-28 — Manager-entered availability:** Manager được nhập/sửa availability hộ Lecturer, hệ thống phải ghi source và actor.
29. **FR-29 — Group availability:** Khi `groupSelectionMode = true`, Leader chọn các slot của group. Không chọn slot nào trước deadline được hiểu là rảnh toàn bộ. Khi mode tắt, group phải theo lịch được xếp.
30. **FR-30 — Registration dashboard:** Manager xem ai đã/chưa phản hồi, số slot mỗi Lecturer/group chọn và timeslot có nguy cơ thiếu Reviewer.

### D. Scheduler và constraint

31. **FR-31 — Complete and partial solution:** Scheduler cố gắng xếp đúng một session cho mỗi group của round. Nếu không đủ tài nguyên, vẫn trả partial schedule và không tạo session sai hard constraint.
32. **FR-32 — H1:** Supervisor `MAIN` hoặc `CO` không được làm Reviewer của project mình hướng dẫn, áp dụng cho mọi round.
33. **FR-33 — H2:** Một Lecturer không được tham gia hai session có khoảng thời gian giao nhau, kể cả khi hai session dùng hai `timeslotId` khác nhau.
34. **FR-34 — H3:** Một room không được phục vụ hai session có khoảng thời gian giao nhau, kể cả overlap một phần.
35. **FR-35 — H4:** Một group có tối đa một session trong một ScheduleVersion của một round; một lịch đầy đủ phải có đúng một session cho mỗi group tham gia.
36. **FR-36 — H5:** Mỗi session phải đủ số Reviewer theo FR-24.
37. **FR-37 — H6:** Một Lecturer chỉ xuất hiện một lần trong cùng một session/council.
38. **FR-38 — H7:** Lecturer chỉ được xếp vào timeslot đã đăng ký rảnh hoặc được Manager nhập hộ trước khi chạy scheduler.
39. **FR-39 — H8:** Lecturer có conflict declaration với project không được làm Reviewer của project đó.
40. **FR-40 — H9:** Group chỉ được đưa vào round khi trạng thái hiện tại phù hợp với loại round.
41. **FR-41 — H10:** Khi `groupSelectionMode = true` và group đã chọn slot, session của group chỉ được xếp vào các slot đã chọn.
42. **FR-42 — H11:** Defense 1.2 phải có ít nhất một Reviewer đã chấm chính group đó tại Defense 1.1. Ưu tiên người từng được chọn làm Remediation Verifier.
43. **FR-43 — H11 waiver:** Chỉ Manager được miễn H11 cho từng `group + round`, bắt buộc có lý do. Waiver phải là dữ liệu nghiệp vụ có hiệu lực rõ ràng, được scheduler đọc trực tiếp và có audit; không chỉ lưu một dòng log rời.
44. **FR-44 — H12:** Mỗi Lecturer tối đa 4 session trong một buổi, 8 session trong một ngày và không vượt quota số session của semester do Manager cấu hình riêng. H12 tính theo số session, không tự đổi sang phút.
45. **FR-45 — Hard-constraint policy:** H1–H12 đều là hard constraint cho auto-scheduling và manual edit. Chỉ H11 có waiver trong V1; không có waiver cho H1–H10 hoặc H12.
46. **FR-46 — Optional H13:** Manager có thể cấu hình `max_groups_per_timeslot` cho một Round theo mockdata. Khi cấu hình, scheduler và manual edit phải enforce giới hạn này; khi để trống, sức chứa đồng thời được quyết định bởi số room, Reviewer và các hard constraint thực tế.
47. **FR-47 — Soft constraints:** Scheduler chấm điểm theo thứ tự mặc định:
    1. S1 cân bằng phần trăm quota semester đã dùng, có điều chỉnh theo `LOW/MEDIUM/HIGH`.
    2. S2 ưu tiên giữ cặp Reviewer của Review 1 sang Review 2.
    3. S3 ưu tiên giữ thêm Reviewer từ Defense 1.1 sang Defense 1.2 ngoài người bắt buộc bởi H11.
    4. S4 ưu tiên xếp các session của cùng Lecturer liên tiếp trong một buổi.
    5. S5 giảm số ngày Lecturer phải có mặt.
    6. S6 giữ tổ hợp Reviewer ổn định giữa các session liên tiếp.
    7. S7 tránh một Lecturer đánh giá quá nhiều group của cùng một Supervisor.
    8. S8 dùng ít room nhất có thể.
48. **FR-48 — Configurable weights:** Manager được chỉnh trọng số soft constraint trước khi chạy; lịch không được vi phạm hard constraint để cải thiện soft score.
49. **FR-49 — ScheduleVersion:** Mỗi lần chạy tạo version mới gồm input snapshot/reference, algorithm parameters, random seed nếu có, thời gian chạy, người chạy, tổng điểm và điểm từng soft constraint.
50. **FR-50 — Unscheduled explanation:** Mỗi group chưa xếp được phải có reason code và diễn giải dễ hiểu, tối thiểu phân biệt thiếu Reviewer rảnh, H1/H8 conflict, H11 continuity, H12 quota, thiếu room và thiếu timeslot.
51. **FR-51 — Active version:** Một round chỉ có một ScheduleVersion active. Chọn version active trước publish không xóa các version còn lại.
52. **FR-52 — Runtime:** Với fixture 74 group, 26 Lecturer, 40 timeslot và 4 room, scheduler phải trả full hoặc partial result trong dưới 60 giây.

### E. Sửa lịch, công bố và sự cố

53. **FR-53 — Draft edit:** Manager được đổi timeslot, room hoặc Reviewer của session nháp; hệ thống validate lại toàn bộ constraint bị ảnh hưởng trước khi lưu.
54. **FR-54 — Publish:** Chỉ version active và không có hard-constraint violation mới được publish. Publish lưu actor/time và gửi thông báo tới Reviewer, Supervisor, Leader và Student của group.
55. **FR-55 — No full rerun after publish:** Sau `PUBLISHED`, không được chạy lại scheduler cho toàn round. Chỉ được thay đổi từng session theo controlled-change workflow.
56. **FR-56 — Controlled change:** Mọi thay đổi sau publish bắt buộc có reason, before/after, actor và timestamp; người bị ảnh hưởng phải nhận notification.
57. **FR-57 — Historical snapshot:** Danh sách Reviewer của session đã `COMPLETED` là bất biến. Thay người cho session chưa diễn ra không được sửa hồi tố người đã chấm session cũ.
58. **FR-58 — Emergency replacement:** Khi Reviewer vắng, hệ thống gợi ý Lecturer đang rảnh và thỏa toàn bộ hard constraint. Nếu không đủ Reviewer, session phải `POSTPONED`; không được diễn ra với hội đồng thiếu người.
59. **FR-59 — Reschedule request:** Lecturer hoặc Leader gửi yêu cầu đổi/hoãn session kèm lý do; Manager duyệt hoặc từ chối và lưu decision note.
60. **FR-60 — Round administration:** Chỉ `ADMIN` hoặc `MANAGER` được hoãn/hủy toàn bộ round. Cả hai thao tác bắt buộc có lý do, audit và notification tới mọi người bị ảnh hưởng. `POSTPONED` giữ nguyên dữ liệu lịch nhưng chặn session diễn ra cho tới khi Manager đặt lịch và publish lại; `CANCELLED` là trạng thái kết thúc, chỉ đọc và không xóa lịch sử. Round `LOCKED` chỉ đọc; chỉ Admin mở khóa được và phải ghi lý do.

### F. Kết quả cuối và trạng thái nhóm

61. **FR-61 — Review outcome:** Review 1/2 chỉ nhận `PASS`, `NEEDS_FIX`, `FAIL` và ghi chú. Kết quả Review tạo cảnh báo nhưng không đổi trạng thái group và không chặn Defense 1.1.
62. **FR-62 — Defense result boundary:** Scheduler-only chỉ lưu kết luận cuối, ghi chú, người nhập và thời gian. Không lưu ballot, Gate 0, criterion score, evidence hay logic hợp nhất.
63. **FR-63 — Defense 1.1 transitions:**
    - Mức 1 → `ELIGIBLE_D12`.
    - Mức 2 → `D12_CONDITIONAL`, bắt buộc có hạn khắc phục và một Reviewer làm Verifier.
    - Mức 3 → `PENDING_D2`.
    - Mức 4 → `FAILED`, không được tham gia Defense 2 trong semester hiện tại.
64. **FR-64 — Remediation:** Verifier phải là một Reviewer của session tạo ra Mức 2. Verifier xác nhận `PASSED` hoặc `FAILED`; reminder gửi trước hạn 2 ngày.
65. **FR-65 — Remediation pass:** Với Mức 2 của Defense 1.1, xác nhận `PASSED` chuyển group từ `D12_CONDITIONAL` sang `ELIGIBLE_D12`.
66. **FR-66 — Remediation overdue:** Quá hạn mà chưa `PASSED` chỉ tạo cảnh báo. Manager chốt chuyển `FAILED` bằng thao tác có lý do; hệ thống không tự động fail.
67. **FR-67 — Defense 1.2 transition:** Defense 1.2 không nhận Mức 1/2/3/4. Khi session được xác nhận `COMPLETED`, group chuyển sang `COMPLETED`. Nếu session `POSTPONED` hoặc `CANCELLED` do sự cố vận hành, trạng thái group không đổi và Manager phải xử lý lịch thay thế; không được tự chuyển group sang `FAILED`.
68. **FR-68 — Defense 2 transition and retake:** Defense 2 là round đánh giá cuối cùng và chỉ nhận `PASS` hoặc `FAIL`. `PASS → COMPLETED`; `FAIL → FAILED`. Defense 2 không có remediation Mức 2 và không áp dụng H11/continuity Reviewer từ các round trước. Group `FAILED` không được xếp vào round còn lại của semester; project/group retake ở kỳ sau có thể liên kết về bản gốc nhưng không sửa lịch sử cũ.

### G. Lịch, dashboard, báo cáo và notification

69. **FR-69 — Personal schedule:** Mọi user xem lịch liên quan dưới dạng danh sách; Lecturer và Manager có thêm lịch tuần. Thời gian hiển thị theo UTC+7.
70. **FR-70 — Manager schedule:** Manager lọc lịch toàn round theo ngày, timeslot, room, Lecturer, group và trạng thái.
71. **FR-71 — Operational dashboard:** Dashboard Manager hiển thị tối thiểu: tiến độ đăng ký availability, số group đã/chưa xếp, số session có thay đổi, yêu cầu đổi lịch đang chờ, tải Lecturer và group cần chú ý.
72. **FR-72 — Reports:** Có báo cáo tải Lecturer theo số session và phần trăm quota, nhóm chưa xếp, group thiếu Leader/dưới 4 thành viên, remediation gần/quá hạn và phân bố kết quả cuối.
73. **FR-73 — Report provenance:** Mọi báo cáo trong ứng dụng phải lấy dữ liệu từ active/published version được chọn và hiển thị rõ semester, round, version, thời điểm tạo.
74. **FR-74 — Notifications:** In-app notification là P1 cho invitation, reminder availability, publish, change, result, remediation deadline và overdue. Email là P2 nhưng phải dùng cùng event source để không sai nội dung.
75. **FR-75 — Audit events:** Tối thiểu phải audit: account/role change, master-data create/update, drop out approval, Leader change, availability nhập hộ, scheduler run/activate, manual edit, H11 waiver, publish, post-publish change, result create/update, overdue decision và unlock.

### H. UX/UI

76. **FR-76 — Visual direction:** Giao diện theo phong cách F-Caps: sáng, gọn, thiên về sản phẩm nội bộ/enterprise; không sao chép logo hoặc tài sản thương hiệu không được cấp quyền.
77. **FR-77 — Color tokens:** Màu chính `#00457C` (FPT Blue), CTA/điểm nhấn `#F36C21` (FPT Orange), hover `#E05E1A`, nền `#F5F7F9`, chữ `#2D3135`, chữ phụ `#8C949D`, border `#E8ECEF`, bề mặt card `#FFFFFF`.
78. **FR-78 — Typography:** Ưu tiên font `Inter` hoặc sans-serif tương đương; body tối thiểu 14px trên desktop và 16px cho input quan trọng trên mobile.
79. **FR-79 — Interaction states:** Mọi form/bảng/lịch phải có loading, empty, error, disabled, success và validation state; không chỉ dùng màu để truyền đạt lỗi hoặc trạng thái.
80. **FR-80 — Scheduling UX:** Hard violation phải hiển thị rule ID, đối tượng xung đột và cách xử lý; soft score phải có giải thích ngắn, không chỉ hiển thị một con số tổng.
81. **FR-81 — Responsive:** Availability grid, personal schedule, notifications và reschedule request dùng được từ viewport 360px; màn hình scheduling chuyên sâu ưu tiên desktop từ 1280px.
82. **FR-82 — Accessibility:** Keyboard navigation cho form và bảng chính, focus visible, label cho input, contrast tối thiểu WCAG AA với text thông thường.

---

## Non-Functional Requirements

- **Performance:** Scheduler hoàn thành trong < 60 giây với 74 group/26 Lecturer/40 timeslot/4 room; trang danh sách và dashboard có p95 < 2 giây ở quy mô một semester.
- **Correctness:** 100% thao tác tạo/sửa/activate/publish lịch phải đi qua cùng một constraint validator; database và application không được dùng hai cách hiểu khác nhau về overlap.
- **Security:** Authorization được kiểm tra server-side theo system role và contextual assignment; Student không truy cập group khác; Lecturer không sửa availability/result ngoài phạm vi được giao.
- **Auditability:** Audit log của các sự kiện FR-75 không được sửa hoặc xóa bằng application role; truy vấn được theo actor, entity, action và khoảng thời gian.
- **Availability:** Mục tiêu 99% trong giờ hành chính; scheduler failure không làm mất input hoặc ScheduleVersion đã có.
- **Backup:** Sao lưu hằng ngày; có khả năng khôi phục theo ngày trong ít nhất 30 ngày gần nhất.
- **Retention:** Dữ liệu học kỳ, lịch, kết quả và audit được giữ tối thiểu 5 học kỳ.
- **Localization:** UI tiếng Việt; tên project hỗ trợ Việt/Anh; timezone nghiệp vụ thống nhất `Asia/Ho_Chi_Minh` (UTC+7).
- **Compatibility:** Web responsive hỗ trợ hai phiên bản ổn định gần nhất của Chrome, Edge và Safari.
- **Maintainability:** Constraint, transition và permission phải có mã ổn định để trace từ spec tới validation, database rule và automated test.
- **Privacy:** Không ghi password, token, nội dung email nhạy cảm hoặc dữ liệu cá nhân không cần thiết vào audit log.

---

## Success Criteria

- [ ] Thời gian chuẩn bị và xếp một round giảm từ 8–16 giờ xuống dưới 1 giờ thao tác của Manager.
- [ ] 0 session có Supervisor chấm project mình hướng dẫn.
- [ ] 0 Lecturer hoặc room bị xếp vào hai session overlap.
- [ ] 0 lịch active/published vi phạm H1–H12 nếu không có H11 waiver hợp lệ.
- [ ] 100% group chưa xếp được có reason code và diễn giải.
- [ ] 100% thay đổi sau publish có actor, reason, before/after và notification tới người bị ảnh hưởng.
- [ ] Scheduler trả kết quả trong < 60 giây ở fixture mục tiêu.
- [ ] Ít nhất 90% Lecturer hoàn tất availability trước deadline trong kỳ pilot.
- [ ] Lecturer hoàn tất chọn 5 ngày × 8 slot trong < 2 phút trên mobile.
- [ ] Độ lệch tải max/min theo phần trăm quota không vượt 1.5× khi dữ liệu availability cho phép.
- [ ] Thao tác nhập liệu nhiều bản ghi lỗi không tạo partial data và có audit actor/time.
- [ ] 100% result transition đã được test riêng theo từng round type trước khi module result được phát hành.
- [ ] 100% thay đổi result và H11 waiver truy ngược được người thực hiện, thời gian và lý do.

---

## Out of Scope

- Gate 0, 9 tiêu chí, phiếu Reviewer độc lập, minh chứng, hợp nhất 2/3 và tự suy kết luận.
- Vai Chair/Reviewer/Secretary và quyền override của Chair trong Full Assessment.
- Đánh giá mức đóng góp từng Student.
- Sinh Biên bản FPTU 07.20a hoặc bảng yêu cầu chỉnh sửa chi tiết từng tiêu chí.
- Quản lý 7 report, source repository, gói cài đặt, slide và hồ sơ nộp.
- Điểm OGA, điểm học phần SWP490 hoặc đồng bộ điểm với FAP.
- Tích hợp FAP làm nguồn master data trong V1.
- Excel import/export và mọi template vận hành bên ngoài.
- Multi-major ngoài SE, native mobile app và microservices.
- H13/`max_groups_per_timeslot` như một business hard constraint.

---

## Assumptions

- Quyết định sản phẩm đã chốt: V1 là Scheduler-only; Full Assessment là phase sau và có thể mở rộng từ dữ liệu session/result hiện tại bằng module mới.
- Thứ tự nguồn khi có mâu thuẫn cho V1: spec này → PRD Scheduler-only → ERD/schema. BusinessRules v1.0 hiện tại chỉ còn hiệu lực với các quy tắc dữ liệu/lịch không mâu thuẫn; toàn bộ phần chấm chi tiết là tài liệu tham khảo cho phase Full Assessment.
- Form quản trị/API và seed fixture có version là nguồn dữ liệu đầu kỳ trong V1; Excel/FAP integration là tương lai.
- Hội đồng Defense trong V1 gồm 3 Reviewer ngang hàng, không có Chair/Secretary.
- H2 và H3 so sánh khoảng thời gian thực tế `[start, end)`, không chỉ so sánh cùng `timeslotId`.
- H12 dùng số session theo PRD: mặc định 4/buổi, 8/ngày và quota/semester; các cột phút trong ERD/schema cũ phải được điều chỉnh khi lập kế hoạch dữ liệu.
- H11 là hard constraint duy nhất được waiver trong V1.
- Defense 1.2 chỉ đánh dấu hoàn tất phiên; Defense 2 là round cuối với kết quả nhị phân `PASS/FAIL`.
- In-app notification thuộc lõi V1; email, SSO và iCal có thể phát hành sau mà không thay đổi invariant scheduling.
