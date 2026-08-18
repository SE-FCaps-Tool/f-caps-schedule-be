# PRD — Capstone Defense Scheduler
### Hệ thống Xếp lịch & Quản lý Đánh giá Đồ án Tốt nghiệp — Khoa KTPM, ĐH FPT

**Phiên bản:** 1.0 · **Ngày:** 17/08/2026 · **Chủ sở hữu sản phẩm:** Bộ môn KTPM
**Tài liệu liên quan:** BusinessRules_v1.0.md (cần cập nhật theo mục 2.3 dưới đây)

---

## 1. Tổng quan

### 1.1. Vấn đề

Mỗi học kỳ Bộ môn KTPM phải xếp lịch đánh giá cho ~74 đề tài qua **5 đợt** (Review 1, Review 2, Defense 1.1, Defense 1.2, Defense 2), tương đương **~370 phiên đánh giá/kỳ**. Việc này đang làm thủ công trên Excel, dẫn tới:

| Vấn đề | Biểu hiện trong dữ liệu SU26 |
|---|---|
| Thu lịch rảnh của giảng viên qua email/chat, tổng hợp tay | Không có dấu vết đăng ký trong file lịch |
| Ràng buộc "GVHD không chấm nhóm mình" phải dò tay qua 74 dòng | Đúng 100% nhưng không có gì đảm bảo kỳ sau vẫn đúng |
| Tải giảng viên lệch nặng, không ai kiểm soát | Người nhiều nhất 20 phiên/tuần, người ít nhất 7 |
| Dữ liệu rời rạc, hai sheet dùng hai định danh khác nhau | Sheet1 dùng mã tài khoản, Sheet2 dùng họ tên |
| Đổi người sau công bố không có dấu vết | Không có cột lý do / lịch sử |
| Không biết nhóm nào đủ điều kiện ra đợt tiếp theo | Phải tra lại biên bản giấy |

### 1.2. Sản phẩm là gì

Ứng dụng web quản lý **vòng đời lịch đánh giá Capstone**: từ lúc Bộ môn mở đợt, thu lịch rảnh của giảng viên và nhóm, tự động xếp lịch theo ràng buộc, công bố, xử lý thay đổi, cho tới lúc ghi nhận kết quả để quyết định nhóm nào đi tiếp đợt nào.

### 1.3. Sản phẩm KHÔNG phải là gì

> ⚠️ **Đây là công cụ xếp lịch và công bố lịch, không phải công cụ chấm điểm.**
> Việc đánh giá chi tiết (Gate 0, 9 tiêu chí, phiếu cá nhân, biên bản 07.20a) diễn ra trên công cụ khác. Hệ thống này chỉ **nhận kết quả cuối cùng** vừa đủ để quyết định đợt tiếp theo.

### 1.4. Mục tiêu & chỉ số thành công

| Mục tiêu | Chỉ số | Hiện tại | Mục tiêu |
|---|---|---|---|
| Rút ngắn thời gian xếp lịch | Số giờ công/đợt | ~8–16h thủ công | < 1h |
| Loại bỏ vi phạm ràng buộc | Số ca GVHD chấm nhóm mình | Phụ thuộc người dò | **0**, chặn ở tầng hệ thống |
| Cân bằng tải giảng viên | Độ lệch tải max/min | 20 / 7 ≈ 2.9× | ≤ 1.5× |
| Minh bạch thay đổi | % thay đổi sau công bố có lý do + log | 0% | 100% |
| Thu lịch rảnh đúng hạn | % GV đăng ký trước deadline | Không đo được | ≥ 90% |
| Giảm sai sót truyền đạt | Số khiếu nại nhầm lịch/kỳ | Không đo được | 0 |

---

## 2. Phạm vi

### 2.1. Trong phạm vi (MVP)

1. Quản trị hệ thống, tài khoản, phân quyền, master data (giảng viên, phòng)
2. Quản lý học kỳ, đề tài, nhóm, sinh viên, phân công GVHD
3. Quản lý drop out sinh viên và chỉ định trưởng nhóm
4. Tạo đợt đánh giá + slot, mời giảng viên, thu đăng ký lịch rảnh
5. Thu đăng ký slot của nhóm (chế độ bật/tắt được)
6. **Xếp lịch tự động** theo ràng buộc cứng/mềm + sửa tay có kiểm soát
7. Công bố lịch, thông báo email + in-app
8. Xử lý thay đổi và sự cố sau công bố, có audit log
9. Nhập kết quả cuối (4 mức) và tự động điều hướng nhóm sang đợt tiếp theo
10. Theo dõi gọn hạn khắc phục cho kết luận mức 2
11. Lịch cá nhân, tra cứu, báo cáo, xuất Excel

### 2.2. Ngoài phạm vi

| # | Nội dung | Lý do |
|---|---|---|
| 1 | Số hóa việc chấm: Gate 0, 9 tiêu chí, phiếu cá nhân, hợp nhất 2/3, đánh giá đóng góp cá nhân | Dùng công cụ khác |
| 2 | Sinh Biên bản 07.20a và Bảng yêu cầu chỉnh sửa chi tiết | Dùng công cụ khác |
| 3 | Quản lý hồ sơ nộp (7 report, gói cài đặt, repository, slide) | Ngoài đề tài |
| 4 | Điểm OGA và điểm tổng kết học phần | Do FAP quản lý |
| 5 | Các ngành IS, ES, BLC, ATM | V1 chỉ ngành SE |
| 6 | Ứng dụng mobile native | Web responsive là đủ |

### 2.3. ⚠️ Thay đổi so với BusinessRules v1.0

| Nội dung | BR v1.0 | PRD v1.0 | Hệ quả |
|---|---|---|---|
| Số hóa chấm điểm | Đầy đủ, tự suy kết luận | **Bỏ hoàn toàn** | Xóa mục 8 của BR v1.0; xóa BR-BAL-*, BR-GATE-*, BR-MRG-*, BR-CON-01/02, BR-MIN-* |
| Vai hội đồng | Chủ tịch / Phản biện / Thư ký | **3 Reviewer ngang hàng** | Xóa H11 cũ, S2, S6; viết lại quyền theo mục 4 |
| Người chốt kết luận | Chủ tịch override | **1 Reviewer được chỉ định** (mode bật bởi Manager) | Viết lại BR-CON-02 |
| Người xác nhận khắc phục | Giảng viên phản biện | **1 Reviewer được phân công** | Viết lại BR-REM-03 |
| Bảng yêu cầu chỉnh sửa | Chi tiết từng dòng | **Chỉ hạn + trạng thái Đạt/Chưa đạt** | Viết lại BR-REM-01/02 |
| Giữ người ở Defense 1.2 | Giữ Chủ tịch (cứng) | **Giữ ít nhất 1 Reviewer đã chấm 1.1** (cứng) | H11 mới |
| Trần tải giảng viên | Chưa quy định | **4 phiên/buổi, 8 phiên/ngày + hạn mức kỳ theo từng GV** | H12 mới |

Các quy tắc còn lại của BR v1.0 (BR-SEM, BR-PRJ, BR-GRP, BR-STU, BR-LEC, BR-RND, BR-AVL, ràng buộc H/S, BR-SCH, BR-PUB, BR-INC, BR-FLOW) **giữ nguyên hiệu lực**.

---

## 3. Người dùng

### 3.1. Bốn role hệ thống

| Role | Ai | Số lượng/kỳ | Tần suất dùng |
|---|---|---|---|
| **Admin** | Cán bộ IT | 1–2 | Thấp — đầu kỳ và khi có sự cố |
| **Manager** | Trưởng bộ môn / thư ký Bộ môn | 1–3 | Cao — dày đặc trước mỗi đợt |
| **Lecturer** | Giảng viên Khoa KTPM | ~26 | Trung bình — mỗi đợt vài lần |
| **Student** | Sinh viên năm cuối | ~330 (74 nhóm × 4–5) | Thấp — xem lịch, Leader đăng ký slot |

### 3.2. Vai trò theo ngữ cảnh

Role hệ thống là cố định. Ngoài ra một người có các **vai trò theo ngữ cảnh**, suy ra từ dữ liệu chứ không gán cứng trên tài khoản:

| Vai ngữ cảnh | Gắn với | Cách xác định | Quyền phát sinh |
|---|---|---|---|
| **Supervisor** (GVHD) | Đề tài | Manager phân công; 1 chính + tối đa 1 đồng hướng dẫn | Xem tiến độ nhóm mình, chỉ định Leader, khai báo xung đột. **Bị cấm** chấm nhóm mình |
| **Reviewer** | Phiên đánh giá | Thuật toán xếp / Manager gán | Xem thông tin nhóm được phân công, nhập kết quả |
| **Result Owner** | Phiên đánh giá | Manager chỉ định 1 trong các Reviewer của phiên (khi bật mode) | Nhập kết luận cuối cho phiên đó |
| **Remediation Verifier** | Kết quả mức 2 | Chọn 1 trong các Reviewer khi chốt kết quả | Xác nhận nhóm đã khắc phục |
| **Project Leader** | Nhóm | GVHD hoặc Manager chỉ định | Đăng ký slot cho nhóm, xin hoãn/đổi lịch |

> **Nguyên tắc:** một Lecturer hoàn toàn có thể vừa là Supervisor của đề tài A vừa là Reviewer của đề tài B trong cùng một buổi. Điều này đã xảy ra trong dữ liệu SU26 và là hợp lệ. Ràng buộc cấm là theo **đề tài**, không theo **người**.

### 3.3. Personas

**Cô Hương — Manager.** Phải chốt lịch cho 74 nhóm trong 5 ngày, với 26 giảng viên có lịch dạy chồng chéo. Hiện dành 2 buổi tối ghép Excel và vẫn lo sót. Cần: thấy ngay ai chưa đăng ký, bấm một nút ra lịch, và khi có người báo bận thì đổi được mà không vỡ mọi thứ.

**Thầy Tài — Lecturer.** Vừa hướng dẫn 4 nhóm vừa được mời chấm 20 phiên. Không muốn phải mở Excel dò xem hôm nay mình chấm phòng nào. Cần: chọn lịch rảnh trên điện thoại trong 2 phút, và một trang duy nhất hiện lịch của mình.

**Minh — Project Leader.** Nhóm 5 người, 2 bạn đang thực tập ở công ty. Cần: biết sớm lịch bảo vệ, và nếu Bộ môn cho phép thì chọn khung giờ cả nhóm có mặt được.

---

## 4. Ma trận phân quyền

| Chức năng | Admin | Manager | Lecturer | Student |
|---|:---:|:---:|:---:|:---:|
| Quản lý tài khoản, phân quyền | ✔ | | | |
| Master data giảng viên, phòng | ✔ | | | |
| Cấu hình hệ thống, mở khóa dữ liệu | ✔ | | | |
| Xem audit log toàn hệ thống | ✔ | | | |
| Tạo/khóa học kỳ | ✔ | ✔ | | |
| Quản lý đề tài, nhóm, sinh viên | | ✔ | | |
| Phân công GVHD | | ✔ | | |
| Duyệt drop out | | ✔ | | |
| Chỉ định Project Leader | | ✔ | ✔ (nhóm mình) | |
| Tạo đợt, tạo slot, cấu hình đợt | | ✔ | | |
| Mời giảng viên vào đợt | | ✔ | | |
| Đăng ký lịch rảnh + mức ưu tiên khối lượng | | | ✔ | |
| Đăng ký slot cho nhóm | | | | ✔ Leader |
| Chạy thuật toán xếp lịch | | ✔ | | |
| Sửa lịch tay | | ✔ | | |
| Công bố lịch | | ✔ | | |
| Thay đổi sau công bố, xử lý sự cố | | ✔ | | |
| Chỉ định Result Owner | | ✔ | | |
| Nhập kết quả phiên | | ✔ | ✔ Result Owner | |
| Xác nhận khắc phục | | | ✔ Verifier | |
| Chốt chuyển mức 2 quá hạn sang Không đạt | | ✔ | | |
| Khai báo xung đột lợi ích | | ✔ | ✔ | |
| Xem lịch cá nhân | ✔ | ✔ | ✔ | ✔ |
| Xem tiến độ & kết quả nhóm mình hướng dẫn | | ✔ | ✔ Supervisor | |
| Xem kết quả nhóm mình | | | | ✔ |
| Xin hoãn / đổi lịch | | | ✔ | ✔ Leader |
| Báo cáo, xuất Excel | | ✔ | | |

---

## 5. Luồng nghiệp vụ chính

```
[Manager]  Tạo đợt ──▶ Tạo slot ──▶ Mời giảng viên
                                          │
[Lecturer] ◀─────────────────────────────┘
   Nhận lời mời ──▶ Chấp nhận/Từ chối ──▶ Chọn slot rảnh + mức ưu tiên khối lượng
                                          │
[Leader]   Chọn slot cho nhóm ────────────┤  (chỉ khi Manager bật groupSelectionMode)
                                          │
[Manager]  Đóng đăng ký ──▶ Chạy thuật toán ──▶ Xem phương án + điểm ràng buộc
                                          │
                              ┌───────────┴───────────┐
                       Chạy lại / đổi trọng số     Sửa tay
                                          │
                              Công bố ──▶ Thông báo (GV, GVHD, Leader, SV)
                                          │
                              Đợt diễn ra ──▶ Sự cố? ──▶ Thay người / hoãn (có lý do + log)
                                          │
[Result Owner] Nhập kết quả (1 trong 4 mức)
                                          │
                              Hệ thống điều hướng nhóm sang đợt tiếp theo
```

---

## 6. Yêu cầu chức năng

> Ký hiệu: **P0** = bắt buộc cho MVP · **P1** = nên có · **P2** = giai đoạn sau

### M1 — Quản trị hệ thống (Admin)

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| **FR-1.1** | Tạo, khóa, phân quyền tài khoản cho 4 role. Hỗ trợ import hàng loạt từ CSV/Excel | P0 |
| **FR-1.2** | Quản lý master data giảng viên: mã tài khoản (khóa chính), họ tên đầy đủ, email `@fe.edu.vn`, bộ môn, trạng thái hoạt động | P0 |
| **FR-1.2b** | Manager ấn định **hạn mức số phiên/kỳ** cho từng giảng viên (định mức giờ chuẩn). Thuật toán cân bằng theo **tỷ lệ %  hạn mức đã dùng**, không theo số tuyệt đối | P0 |
| **FR-1.3** | Quản lý master data phòng: mã phòng, campus, sức chứa, thiết bị | P0 |
| **FR-1.4** | Xem audit log toàn hệ thống, lọc theo người dùng / thực thể / khoảng thời gian | P0 |
| **FR-1.5** | Mở khóa học kỳ hoặc đợt đã ở trạng thái LOCKED, có ghi log bắt buộc | P1 |
| **FR-1.6** | Đăng nhập bằng SSO tài khoản `@fe.edu.vn` (Google hoặc Microsoft) | P1 |

**Tiêu chí chấp nhận FR-1.2:** Import file chứa cả mã tài khoản và họ tên; hệ thống phát hiện và báo lỗi khi cùng một người xuất hiện với hai định danh khác nhau (vấn đề đã có trong dữ liệu SU26).

---

### M2 — Học kỳ, Đề tài, Nhóm (Manager)

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| **FR-2.1** | Tạo học kỳ (mã, tên, ngày bắt đầu/kết thúc). Chỉ một học kỳ ACTIVE tại một thời điểm | P0 |
| **FR-2.2** | Quản lý đề tài: mã theo mẫu `[Kỳ][Ngành][STT]`, tên tiếng Việt, tên tiếng Anh. Nhập tay hoặc import Excel | P0 |
| **FR-2.3** | Phân công GVHD cho đề tài: 1–2 người, bắt buộc phân vai chính / đồng hướng dẫn | P0 |
| **FR-2.4** | Quản lý nhóm: mã nhóm riêng, gắn với đúng 1 đề tài, 4–5 sinh viên | P0 |
| **FR-2.5** | Chỉ định Project Leader. Một nhóm luôn có đúng 1 Leader đang hoạt động | P0 |
| **FR-2.6** | Ghi nhận drop out: người khởi tạo, người duyệt, ngày hiệu lực, lý do. Lưu lịch sử `joinedAt`/`leftAt` | P0 |
| **FR-2.7** | Khi Leader drop out, hệ thống chặn mọi thao tác xếp lịch cho nhóm cho tới khi có Leader mới | P0 |
| **FR-2.8** | Hiển thị cảnh báo sĩ số cho nhóm dưới 4 người, **không chặn** việc xếp lịch | P0 |
| **FR-2.9** | ⭐ **Import Excel theo mẫu** toàn bộ dữ liệu đầu kỳ: đề tài, nhóm, sinh viên, phân công GVHD. Hệ thống cung cấp file mẫu tải xuống | P0 |
| **FR-2.10** | Import có bước **tiền kiểm tra**: hiển thị bảng lỗi/cảnh báo (trùng mã, thiếu GVHD chính, nhóm sai sĩ số, GV không có trong master data, một người hai định danh) và **không ghi dữ liệu** cho tới khi Manager xác nhận | P0 |

**Tiêu chí chấp nhận FR-2.3:** Hệ thống từ chối lưu nếu gán 2 GVHD mà không chỉ định ai là chính. Dữ liệu cũ dạng chuỗi `"A và B"` phải được tách thành hai bản ghi khi import.

---

### M3 — Đợt đánh giá & Slot (Manager)

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| **FR-3.1** | Tạo đợt thuộc 1 trong 5 loại: `REVIEW_1`, `REVIEW_2`, `DEFENSE_1_1`, `DEFENSE_1_2`, `DEFENSE_2` | P0 |
| **FR-3.2** | Cấu hình đợt: độ dài slot, số phiên tối đa/hội đồng/buổi, **trần phiên/buổi và phiên/ngày cho giảng viên**, deadline đăng ký, `groupSelectionMode`, `resultOwnerMode`, trọng số ràng buộc mềm | P0 |
| **FR-3.3** | Tạo slot hàng loạt: chọn khoảng ngày + khung giờ mẫu (VD sáng 08:00–12:00, chiều 13:30–17:30, mỗi slot 60 phút) → hệ thống sinh toàn bộ slot | P0 |
| **FR-3.4** | Chọn danh sách phòng khả dụng cho đợt. **Phòng không gắn vào slot** — được thuật toán gán khi xếp lịch | P0 |
| **FR-3.5** | Chọn danh sách nhóm tham gia đợt. Hệ thống mặc định chọn các nhóm đủ điều kiện và cảnh báo nhóm không đủ | P0 |
| **FR-3.6** | Vòng đời trạng thái đợt: `DRAFT → OPEN_REGISTRATION → REGISTRATION_CLOSED → SCHEDULING → SCHEDULED → PUBLISHED → ONGOING → COMPLETED → LOCKED` | P0 |
| **FR-3.7** | Sao chép cấu hình từ một đợt cũ để tạo đợt mới | P1 |

---

### M4 — Mời & Đăng ký lịch rảnh

| ID | Yêu cầu | Role | Ưu tiên |
|---|---|---|---|
| **FR-4.1** | Manager gửi lời mời tham gia đợt tới danh sách giảng viên chọn lọc | Manager | P0 |
| **FR-4.2** | Lecturer nhận thông báo, chấp nhận hoặc từ chối lời mời (từ chối phải nêu lý do) | Lecturer | P0 |
| **FR-4.3** | Lecturer chọn các slot mình có thể tham gia trên giao diện dạng lưới ngày × giờ, thao tác được trên điện thoại | Lecturer | P0 |
| **FR-4.4** | Lecturer chọn **mức ưu tiên khối lượng**: muốn được xếp Nhiều / Trung bình / Ít | Lecturer | P0 |
| **FR-4.5** | Lecturer sửa hoặc rút đăng ký cho tới khi đợt đóng đăng ký | Lecturer | P0 |
| **FR-4.6** | Manager xem dashboard tiến độ đăng ký: ai đã đăng ký, ai chưa, số slot mỗi người chọn, cảnh báo khung giờ có quá ít GV rảnh | Manager | P0 |
| **FR-4.7** | Manager nhập hộ lịch rảnh cho giảng viên không tự đăng ký | Manager | P0 |
| **FR-4.8** | Hệ thống nhắc tự động trước deadline 3 ngày và 1 ngày cho GV chưa đăng ký | Hệ thống | P0 |
| **FR-4.9** | Quá deadline mà GV không đăng ký slot nào ⇒ coi như **bận toàn bộ**, không xếp vào đâu; liệt kê cho Manager | Hệ thống | P0 |
| **FR-4.10** | Khi bật `groupSelectionMode`, Leader chọn các slot nhóm có thể tham gia | Student | P0 |
| **FR-4.11** | Nhóm không chọn slot nào trước deadline ⇒ coi như **rảnh mọi slot** (ngược quy tắc của giảng viên) | Hệ thống | P0 |
| **FR-4.12** | Lecturer khai báo xung đột lợi ích với đề tài cụ thể, kèm lý do | Lecturer | P1 |

**Tiêu chí chấp nhận FR-4.3:** Giảng viên hoàn tất việc chọn lịch rảnh cho một đợt 5 ngày × 8 slot trong **dưới 2 phút** trên màn hình điện thoại.

---

### M5 — Xếp lịch (Manager)

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| **FR-5.1** | Chạy thuật toán xếp lịch tự động, tuân thủ toàn bộ ràng buộc cứng mục 7.1 | P0 |
| **FR-5.2** | Mỗi lần chạy sinh một `ScheduleVersion` lưu lại, kèm **điểm số từng ràng buộc mềm** để so sánh các phương án | P0 |
| **FR-5.3** | So sánh cạnh nhau nhiều phương án; chọn một phương án làm bản hoạt động | P0 |
| **FR-5.4** | Khi không xếp được đầy đủ, trả kết quả một phần kèm **danh sách nhóm chưa xếp được và lý do cụ thể** cho từng nhóm | P0 |
| **FR-5.5** | Đề xuất phương án gỡ: mở thêm slot ngày nào, mời thêm giảng viên nào, nới ràng buộc mềm nào | P1 |
| **FR-5.6** | Sửa tay: kéo thả phiên sang slot/phòng khác, đổi giảng viên trong hội đồng | P0 |
| **FR-5.7** | Khi sửa tay vi phạm **ràng buộc cứng H1, H2, H3** ⇒ **chặn**, hiện rõ vi phạm nào | P0 |
| **FR-5.8** | Khi sửa tay vi phạm ràng buộc khác ⇒ **cảnh báo** và **bắt nhập lý do** trước khi lưu | P0 |
| **FR-5.9** | Mọi thao tác sửa ghi audit log: ai, lúc nào, từ giá trị nào sang giá trị nào, lý do | P0 |
| **FR-5.10** | Bảng điều khiển trực quan hiển thị tải từng giảng viên: số phiên đã xếp, % hạn mức kỳ đã dùng, so với mức ưu tiên họ chọn | P1 |
| **FR-5.11** | ⭐ Sau khi đợt đã `PUBLISHED`, hệ thống **chặn chạy lại thuật toán cho toàn đợt**. Chỉ cho phép sửa tay từng phiên theo M6 | P0 |

**Tiêu chí chấp nhận FR-5.1:** Với quy mô 74 nhóm / 26 giảng viên / 40 slot / 4 phòng, thuật toán trả kết quả trong **dưới 60 giây**.

---

### M6 — Công bố & Thay đổi (Manager)

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| **FR-6.1** | Công bố lịch. Hệ thống gửi thông báo tới: giảng viên trong hội đồng, GVHD từng nhóm, Leader và toàn bộ sinh viên nhóm | P0 |
| **FR-6.2** | Sau công bố vẫn thay đổi được thành viên hội đồng, giờ, phòng — **bắt buộc nhập lý do** | P0 |
| **FR-6.3** | Người thay thế phải thỏa toàn bộ ràng buộc cứng; hệ thống chặn nếu vi phạm | P0 |
| **FR-6.4** | Mọi thay đổi sau công bố gửi thông báo tới các bên bị ảnh hưởng, nêu rõ thay đổi gì | P0 |
| **FR-6.5** | **Thay người khẩn cấp** ngày diễn ra: gợi ý danh sách giảng viên hợp lệ đang rảnh slot đó, sắp xếp theo mức phù hợp | P0 |
| **FR-6.6** | Hội đồng **luôn phải đủ số người** theo loại đợt — không cho phép chấm thiếu người | P0 |
| **FR-6.7** | Hoãn một phiên và xếp lại vào slot bù | P0 |
| **FR-6.8** | Lecturer hoặc Leader gửi yêu cầu hoãn/đổi lịch; Manager duyệt hoặc từ chối | P1 |
| **FR-6.9** | Cảnh báo khi thay Reviewer muộn hơn N ngày trước phiên (mặc định 3 ngày) — vì Reviewer cần thời gian chuẩn bị | P1 |

---

### M7 — Kết quả & Luồng chuyển tiếp

| ID | Yêu cầu | Role | Ưu tiên |
|---|---|---|---|
| **FR-7.1** | Với đợt Review 1 / Review 2: nhập kết quả dạng Đạt / Cần sửa / Không đạt + ghi chú. Kết quả **chỉ cảnh báo, không chặn** nhóm đi tiếp | Lecturer | P0 |
| **FR-7.2** | Với đợt Defense: nhập **1 trong 4 mức kết luận** + ghi chú | Result Owner | P0 |
| **FR-7.3** | Khi bật `resultOwnerMode`, Manager chỉ định 1 Reviewer của phiên làm Result Owner. Khi tắt, Reviewer nào trong phiên cũng nhập được, hệ thống ghi nhận người nhập | Manager | P0 |
| **FR-7.4** | Khi nhập kết luận mức 2, bắt buộc điền **hạn khắc phục** và chọn **1 Reviewer làm người xác nhận** | Result Owner | P0 |
| **FR-7.5** | Hệ thống tự động chuyển trạng thái nhóm theo kết quả (bảng mục 8.2) | Hệ thống | P0 |
| **FR-7.6** | Người xác nhận đánh dấu nhóm đã khắc phục Đạt / Chưa đạt | Lecturer | P0 |
| **FR-7.7** | Nhắc tự động trước hạn khắc phục 2 ngày cho nhóm, người xác nhận, GVHD | Hệ thống | P0 |
| **FR-7.8** | Quá hạn mà chưa xác nhận Đạt ⇒ hệ thống **cảnh báo**, không tự chuyển. **Manager** là người chốt chuyển sang Không đạt, có ghi lý do | Manager | P0 |
| **FR-7.9** | Quá hạn 3 ngày mà Manager chưa chốt ⇒ leo thang cảnh báo mức cao | Hệ thống | P1 |
| **FR-7.10** | Sửa kết quả đã nhập: cần lý do, ghi audit log, thông báo cho các bên | Manager | P0 |

---

### M8 — Xem lịch, Báo cáo, Xuất dữ liệu

| ID | Yêu cầu | Role | Ưu tiên |
|---|---|---|---|
| **FR-8.1** | Trang lịch cá nhân: mọi phiên của tôi, dạng danh sách và dạng lịch tuần, có tải xuống | Tất cả | P0 |
| **FR-8.2** | Trang lịch nhóm cho sinh viên: ngày, giờ, phòng, kết quả các đợt đã qua | Student | P0 |
| **FR-8.3** | Trang tổng quan nhóm cho GVHD: tình trạng qua từng đợt của các nhóm mình hướng dẫn | Lecturer | P0 |
| **FR-8.4** | Bảng lịch toàn đợt: lọc theo ngày, phòng, giảng viên, nhóm, trạng thái | Manager | P0 |
| **FR-8.5** | Báo cáo tải giảng viên theo kỳ: số phiên, so với mức ưu tiên đã chọn, độ lệch | Manager | P0 |
| **FR-8.6** | Báo cáo phân bố kết quả: số nhóm theo từng mức kết luận, theo GVHD | Manager | P1 |
| **FR-8.7** | Báo cáo nhóm cần chú ý: sĩ số dưới 4, chưa có Leader, quá hạn khắc phục, chưa xếp được lịch | Manager | P0 |
| **FR-8.8** | **Xuất Excel đúng định dạng đang dùng** (sheet ngành + sheet điều phối) để bàn giao Phòng Đào tạo / Khảo thí | Manager | P0 |
| **FR-8.9** | Xuất lịch định dạng iCal để giảng viên nhập vào Google/Outlook Calendar | Lecturer | P1 |

**Tiêu chí chấp nhận FR-8.8:** File xuất ra mở được và khớp cấu trúc cột với file `su26_review_1.1_SE.xlsx` hiện hành.

---

### M9 — Thông báo

| ID | Sự kiện | Người nhận | Kênh | Ưu tiên |
|---|---|---|---|---|
| **FR-9.1** | Được mời tham gia đợt | Lecturer | Email + in-app | P0 |
| **FR-9.2** | Nhắc đăng ký lịch rảnh (trước hạn 3 ngày, 1 ngày) | Lecturer chưa đăng ký | Email + in-app | P0 |
| **FR-9.3** | Lịch được công bố | GV trong hội đồng, GVHD, Leader, SV | Email + in-app | P0 |
| **FR-9.4** | Lịch của tôi bị thay đổi | Người bị ảnh hưởng | Email + in-app | P0 |
| **FR-9.5** | Nhắc phiên sắp diễn ra (trước 1 ngày) | GV trong hội đồng, nhóm | Email + in-app | P1 |
| **FR-9.6** | Kết quả đã được nhập | Nhóm, GVHD | Email + in-app | P0 |
| **FR-9.7** | Nhắc hạn khắc phục (trước 2 ngày) | Nhóm, người xác nhận, GVHD | Email + in-app | P0 |
| **FR-9.8** | Quá hạn khắc phục | Nhóm, người xác nhận, GVHD, Manager | Email + in-app | P0 |
| **FR-9.9** | Mở đăng ký slot cho nhóm | Leader | Email + in-app | P0 |

---

## 7. Thuật toán xếp lịch

### 7.1. Ràng buộc CỨNG

| Mã | Ràng buộc |
|---|---|
| **H1** | GVHD (cả chính và đồng hướng dẫn) không được là Reviewer của đề tài mình hướng dẫn — mọi loại đợt |
| **H2** | Một giảng viên không được xếp vào 2 phiên trùng giờ |
| **H3** | Một phòng không được có 2 phiên trùng giờ |
| **H4** | Một nhóm chỉ có đúng 1 phiên trong 1 đợt |
| **H5** | Đủ số Reviewer: Review 1/2 = **2 người**; Defense 1.1/1.2/2 = **3 người**, ngang hàng |
| **H6** | Một giảng viên chỉ xuất hiện 1 lần trong 1 hội đồng |
| **H7** | Chỉ xếp giảng viên vào slot mà GV đã đăng ký rảnh |
| **H8** | Không xếp giảng viên đã khai báo xung đột lợi ích với đề tài đó |
| **H9** | Nhóm phải ở trạng thái đủ điều kiện của loại đợt (mục 8) |
| **H10** | Khi `groupSelectionMode` bật và nhóm đã chọn slot: chỉ xếp nhóm vào slot nhóm đã chọn |
| **H11** | ⭐ Hội đồng **Defense 1.2 phải có ít nhất 1 Reviewer đã chấm Defense 1.1** của chính nhóm đó. Ưu tiên chọn người đã xác nhận khắc phục. Manager gỡ được cho từng nhóm, bắt buộc ghi lý do |
| **H12** | ⭐ **Trần tải giảng viên**: tối đa 4 phiên/buổi và 8 phiên/ngày; đồng thời không vượt **hạn mức số phiên/kỳ** do Manager ấn định riêng cho từng giảng viên |

### 7.2. Ràng buộc MỀM (thứ tự ưu tiên)

| Mã | Ràng buộc | Ưu tiên |
|---|---|---|
| **S1** | **Cân bằng tải** — tối thiểu hóa độ lệch **% hạn mức kỳ đã dùng** giữa các giảng viên, có điều chỉnh theo mức ưu tiên khối lượng GV tự chọn | **1** |
| **S2** | Review 2 giữ nguyên cặp 2 giảng viên đã chấm Review 1 của nhóm đó | 2 |
| **S3** | Defense 1.2 giữ thêm Reviewer thứ 2, thứ 3 từ Defense 1.1 (ngoài người bắt buộc ở H11) | 3 |
| **S4** | Gom các phiên của cùng giảng viên liên tiếp trong một buổi, tránh giờ trống ở giữa | 4 |
| **S5** | Giảm số ngày mỗi giảng viên phải có mặt | 5 |
| **S6** | Giữ tổ hợp hội đồng ổn định giữa các phiên liên tiếp trong cùng buổi | 6 |
| **S7** | Tránh để một giảng viên chấm quá nhiều nhóm của cùng một GVHD | 7 |
| **S8** | Dùng ít phòng nhất có thể | 8 |

> **Đánh đổi cần Bộ môn biết trước:** S1 xung đột trực tiếp với S4 và S5. Vì cân bằng tải là ưu tiên số 1, lịch sinh ra sẽ **rải rác hơn** cách xếp thủ công hiện tại (vốn gom 4 nhóm liên tiếp/buổi). Trọng số phải cấu hình được để tinh chỉnh sau vài kỳ chạy thật.

---

## 8. Máy trạng thái

### 8.1. Trạng thái nhóm trong học kỳ

```
                            ACTIVE
                              │
          Review 1 ──▶ kết quả ghi nhận, KHÔNG chặn
          Review 2 ──▶ kết quả ghi nhận, KHÔNG chặn
                              │
                        DEFENSE_1_1
        ┌────────────┬─────────┴────────┬──────────────┐
     Mức 1        Mức 2              Mức 3          Mức 4
        │            │                  │              │
        │   D12_CONDITIONAL         PENDING_D2       FAILED
        │      │        │                │        (làm lại kỳ sau,
        │  Xác nhận  Quá hạn +           │       KHÔNG có Defense 2)
        │   Đạt      Manager chốt        ▼
        │      │        │            DEFENSE_2
        ▼      ▼        ▼            ┌────┴────┐
   ELIGIBLE_D12      FAILED       Đạt      Không đạt
        │                           │            │
        ▼                           ▼            ▼
   DEFENSE_1_2 ────────────▶  COMPLETED      FAILED
```

### 8.2. Bảng điều hướng sau Defense 1.1

| Kết luận | Ý nghĩa | Trạng thái nhóm | Đợt tiếp theo |
|---|---|---|---|
| **Mức 1** — Được bảo vệ lần 1 | Đủ điều kiện, không vướng gì | `ELIGIBLE_D12` | Defense 1.2 |
| **Mức 2** — Được bảo vệ lần 1 (chỉnh sửa trong N ngày) | Sản phẩm đạt, hồ sơ/trình bày còn thiếu | `D12_CONDITIONAL` | Defense 1.2, **có điều kiện** |
| **Mức 3** — Sửa lại để bảo vệ lần 2 | Chưa đủ điều kiện đợt này | `PENDING_D2` | Defense 2 |
| **Mức 4** — Không đạt | Vi phạm nghiêm trọng hoặc không khắc phục kịp | `FAILED` | **Không có**, làm lại kỳ sau |

| Quy tắc | Nội dung |
|---|---|
| **FLOW-1** | Kết quả Review 1 và Review 2 **không chặn** nhóm đi tiếp. Mọi nhóm đều được xếp Defense 1.1 |
| **FLOW-2** | Mức 2 quá hạn khắc phục ⇒ hệ thống cảnh báo; **Manager chốt** chuyển sang `FAILED` và hủy suất Defense 1.2 |
| **FLOW-3** | Mức 4 **không được xếp Defense 2** — khác với mức 3 |
| **FLOW-4** | Defense 2 không đạt ⇒ `FAILED` |
| **FLOW-5** | Nhóm `FAILED` được tạo bản ghi retake cho kỳ sau, giữ liên kết về nhóm và đề tài gốc |
| **FLOW-6** | Nhóm `FAILED` không được xếp vào bất kỳ đợt nào còn lại của kỳ hiện tại |

---

## 9. Yêu cầu phi chức năng

| Loại | Yêu cầu |
|---|---|
| **Nền tảng** | Web responsive. Giao diện đăng ký lịch rảnh và xem lịch phải dùng tốt trên màn hình điện thoại |
| **Hiệu năng** | Thuật toán xếp lịch: < 60 giây với 74 nhóm / 26 GV / 40 slot / 4 phòng. Trang danh sách: < 2 giây |
| **Quy mô** | 1 ngành, ~80 đề tài, ~400 sinh viên, ~30 giảng viên, ~400 phiên mỗi kỳ. Thiết kế chịu được ×5 khi mở rộng đa ngành |
| **Ngôn ngữ** | Giao diện tiếng Việt. Dữ liệu hỗ trợ tên đề tài song ngữ Việt–Anh |
| **Múi giờ** | Asia/Bangkok (UTC+7) |
| **Bảo mật** | Phân quyền theo mục 4. Sinh viên chỉ xem được dữ liệu nhóm mình. Giảng viên chỉ xem chi tiết nhóm mình được phân công hoặc hướng dẫn |
| **Audit** | Ghi log mọi thao tác thay đổi lịch, thay đổi kết quả, duyệt drop out, gỡ ràng buộc. Log không xóa được |
| **Lưu trữ** | Giữ dữ liệu tối thiểu 5 học kỳ, tra cứu ngược được |
| **Sao lưu** | Sao lưu hàng ngày, khôi phục được về từng ngày trong 30 ngày gần nhất |
| **Khả dụng** | 99% trong giờ hành chính. Giai đoạn đăng ký và ngày diễn ra đợt là cao điểm |

---

## 10. Kế hoạch phát hành

| Giai đoạn | Nội dung | Mốc |
|---|---|---|
| **R1 — Nền tảng** | M1, M2: tài khoản, master data, học kỳ, đề tài, nhóm, GVHD, drop out | Trước kỳ FA26 6 tuần |
| **R2 — Xếp lịch** | M3, M4, M5: đợt, slot, mời, đăng ký, thuật toán, sửa tay | Trước kỳ FA26 3 tuần |
| **R3 — Vận hành** | M6, M7, M9: công bố, thay đổi, sự cố, kết quả, thông báo | Trước Defense 1.1 của FA26 |
| **R4 — Báo cáo** | M8: lịch cá nhân, báo cáo, xuất Excel, iCal | Trong kỳ FA26 |

**Khuyến nghị vận hành song song:** kỳ FA26 chạy hệ thống **song song với Excel** để đối chiếu, đặc biệt để đo xem lịch do thuật toán sinh (ưu tiên cân bằng tải) có được giảng viên chấp nhận không.

---

## 11. Rủi ro

| Mã | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| **R1** | Cân bằng tải làm lịch rải rác, giảng viên phải đến trường nhiều ngày hơn ⇒ phản ứng tiêu cực | Cao | Trọng số cấu hình được; chạy song song 1 kỳ; cho GV chọn mức ưu tiên khối lượng để tự điều tiết |
| **R2** | Quy tắc "không đăng ký = bận" khiến thuật toán vô nghiệm nếu nhiều GV quên | Cao | Nhắc tự động 2 lần; dashboard tiến độ; Manager nhập hộ (FR-4.7) |
| **R3** | Mức 2 quá hạn không tự chuyển ⇒ nhóm vi phạm vẫn giữ suất Defense 1.2, trái Guideline | Cao | Leo thang cảnh báo sau 3 ngày (FR-7.9); báo cáo nhóm cần chú ý (FR-8.7) |
| **R4** | Thay Reviewer sát ngày ⇒ người mới không kịp chuẩn bị, chất lượng đánh giá giảm | Trung bình | Cảnh báo khi thay muộn hơn 3 ngày (FR-6.9) |
| **R5** | Nhóm dưới 4 người vẫn bảo vệ — lệch điều kiện C5 trong quy định gốc | Trung bình | Xin Bộ môn văn bản diễn giải; hiển thị rõ tình trạng sĩ số cho hội đồng |
| **R6** | H11 (giữ ít nhất 1 Reviewer cũ ở D1.2) thu hẹp không gian lời giải | Trung bình | Manager gỡ được theo từng nhóm, có ghi lý do |
| **R7** | Kết quả nhập tay bởi 1 người ⇒ sai sót không ai đối chiếu | Trung bình | Thông báo kết quả tới nhóm và GVHD ngay (FR-9.6) để phát hiện sai sớm; sửa được có log |
| **R8** | Dữ liệu cũ lệch chuẩn (2 định danh cho 1 người, 2 GVHD trong 1 ô) | Thấp | Trình import có bước kiểm tra và báo lỗi trước khi ghi (FR-1.2, FR-2.3) |

---

## 12. Câu hỏi mở — cần trả lời cho vòng tiếp theo

### Nhóm A — Ràng buộc còn thiếu

**A1.** Có **trần cứng** số phiên/ngày và số phiên/kỳ cho mỗi giảng viên không, hay hoàn toàn dựa vào mức ưu tiên GV tự chọn? Nếu một GV chọn "Nhiều" thì trần là bao nhiêu?

**A2.** Hội đồng **Defense 2** có ràng buộc giữ người giống H11 không, hay ghép tự do?

**A3.** Nhóm đạt **Defense 2** thì kết thúc luôn, hay vẫn phải qua một buổi bảo vệ chính thức nữa? *(Hiện đang mô hình hóa Defense 2 là đợt cuối cùng.)*

**A4.** Có cần ràng buộc **nghỉ giữa các phiên** cho giảng viên không (VD sau 4 phiên liên tiếp phải nghỉ 1 slot)?

**A5.** Buổi đánh giá **online** có được coi là một loại "phòng" với giới hạn số phiên song song không?

### Nhóm B — Quy trình

**B1.** Ai được **hủy hoặc hoãn cả một đợt** đã công bố (VD trùng lịch thi toàn trường)? Manager tự quyết hay cần cấp trên?

**B2.** Khi Manager **chạy lại thuật toán sau khi đã công bố**, hệ thống nên xử lý thế nào — chặn hoàn toàn, hay cho chạy nhưng phải công bố lại và thông báo cho mọi người?

**B3.** Sinh viên hoặc giảng viên **xin đổi lịch** (FR-6.8) — có giới hạn số lần xin không? Có deadline không (VD chỉ được xin trước 3 ngày)?

**B4.** Một đề tài có thể **đổi GVHD giữa kỳ** không? Nếu có, các phiên đã xếp mà GVHD mới đang ngồi hội đồng thì xử lý ra sao (vi phạm H1 hồi tố)?

### Nhóm C — Dữ liệu & tích hợp

**C1.** Danh sách sinh viên, đề tài, nhóm đầu kỳ đến từ đâu — nhập tay, import Excel, hay tích hợp FAP? Nếu import, ai là người chuẩn bị file?

**C2.** **SSO** `@fe.edu.vn` là bắt buộc ở MVP hay có thể dùng tài khoản riêng trước?

**C3.** Email thông báo gửi qua hệ thống mail nào của trường? Có giới hạn số lượng gửi/ngày không?

**C4.** Sinh viên đăng nhập bằng email `@fpt.edu.vn` — hệ thống có sẵn danh sách này không, hay Bộ môn phải tạo tay?

### Nhóm D — Chi tiết chưa rõ

**D1.** Ghi chú kết quả (FR-7.2) có cần cấu trúc gì không, hay chỉ là một ô text tự do?

**D2.** Nhóm bị `FAILED` ở kỳ này, sang kỳ sau: **giữ nguyên đề tài hay bắt buộc đổi**? Các thành viên có được tách sang nhóm khác không?

**D3.** Sinh viên drop out rồi quay lại kỳ sau — hệ thống có cần nối lịch sử của họ không?

**D4.** Có cần trang **dashboard tổng quan** cho Manager ở màn hình đầu tiên không? Nếu có, 3 số liệu quan trọng nhất cần thấy ngay là gì?

---

*PRD này là đầu vào cho thiết kế chi tiết (use case specification, ERD, wireframe).*
