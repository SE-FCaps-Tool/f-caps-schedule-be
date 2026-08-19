# BUSINESS RULES — Hệ thống Xếp lịch & Quản lý Đánh giá Capstone Project
### Khoa Kỹ thuật Phần mềm, Đại học FPT

**Phiên bản:** 1.0 (chốt) · **Ngày:** 17/08/2026 · **Người soạn:** BA
**Căn cứ:** Syllabus SWP490 (QĐ 1341/QĐ-ĐHFPT), Biểu mẫu FPTU 07.20a, Guideline & StudentGuide Defense 1.1, dữ liệu vận hành SU26
**Trạng thái:** Đã chốt qua 3 vòng phỏng vấn stakeholder. Các điểm còn mở liệt kê ở Phần 10.

---

## 1. Phạm vi

### 1.1. Trong phạm vi

| # | Nội dung |
|---|---|
| 1 | Quản lý học kỳ, đề tài, nhóm, sinh viên, giảng viên của **ngành KTPM (SE)** |
| 2 | Quản lý 5 loại đợt đánh giá: **Review 1, Review 2, Defense 1.1, Defense 1.2, Defense 2** |
| 3 | Mời giảng viên, thu đăng ký lịch rảnh, **tự động xếp lịch** + cho phép sửa tay |
| 4 | Công bố lịch, xử lý thay đổi và sự cố sau công bố |
| 5 | **Số hóa toàn bộ việc chấm Defense**: Gate 0, 9 tiêu chí, hợp nhất phiếu, tự suy kết luận, sinh Biên bản 07.20a và Bảng yêu cầu chỉnh sửa |
| 6 | Theo dõi luồng chuyển tiếp giữa các đợt và trạng thái tốt nghiệp của nhóm |

### 1.2. Ngoài phạm vi

| # | Nội dung | Lý do |
|---|---|---|
| 1 | Quản lý **hồ sơ nộp** (7 report, gói cài đặt, repository, slide, bảng đối chiếu use case) | Stakeholder xác nhận nằm ngoài đề tài |
| 2 | Quản lý và tính **điểm OGA** | Do hệ thống khác (FAP) quản lý; app chỉ nhận giá trị nhập tay khi chấm Gate 0 |
| 3 | Chấm điểm tổng kết học phần SWP490 | Defense 1.1 là buổi **xét điều kiện**, không cho điểm |
| 4 | Các ngành IS, ES, BLC, ATM | V1 chỉ phục vụ ngành SE |

---

## 2. Từ điển thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Đợt đánh giá** (EvaluationRound) | Một chu kỳ đánh giá của 1 học kỳ, thuộc 1 trong 5 loại. Do Moderator tạo. |
| **Slot** | Một khung giờ trống (ngày + giờ bắt đầu + giờ kết thúc) do Moderator tạo trong đợt. |
| **Phiên đánh giá** (Session) | Một lượt đánh giá cụ thể = Slot × Phòng × Nhóm × Hội đồng. Đây là đơn vị của lịch. |
| **Hội đồng** (Council) | Tổ hợp giảng viên đánh giá 1 phiên. Review = 2 GV ngang hàng. Defense = 3 GV: Chủ tịch, Phản biện, Thư ký. |
| **GVHD** (Supervisor) | Giảng viên hướng dẫn đề tài. Mỗi đề tài có 1–2 GVHD, phân vai **chính** và **đồng hướng dẫn**. |
| **Moderator** | Cán bộ Bộ môn điều phối đợt đánh giá. |
| **Gate 0** | Bộ 13 điều kiện tiên quyết (A1–A3, B1–B5, C1–C5) kiểm tra trước khi đánh giá 9 tiêu chí. |
| **Tiêu chí trọng yếu** | TC3 (SRS), TC7 (Hiện thực & demo), TC9 (Hỏi đáp & trách nhiệm cá nhân). |
| **Mức kết luận** | 1 trong 4 mức của Defense 1.1, theo mục 5 Biên bản 07.20a. |
| **Bảng yêu cầu chỉnh sửa** | Phụ lục B — danh mục việc phải sửa kèm hạn và người xác nhận. |

---

## 3. Mô hình miền

```
Semester ── Project ──n:n── Lecturer          (Supervision: role = MAIN | CO)
              │
              └── Group ── GroupMembership ── Student
                            (role: LEADER | MEMBER)
                            (joinedAt, leftAt, status: ACTIVE | DROPPED)

EvaluationRound (type, status, config)
 ├── Slot (date, startTime, endTime, session)
 ├── Room
 ├── RoundInvitation (lecturer, status)
 ├── LecturerAvailability (lecturer, slot, preferredLoadLevel)
 ├── GroupSlotPreference (group, slot)        ← chỉ khi bật groupSelectionMode
 └── ScheduleVersion (score, isActive)
      └── Session (slot, room, group)
           └── Council
                └── CouncilAssignment (lecturer, role, isReplacement, reason)

EvaluationResult (1:1 với Session, chỉ cho loại Defense)
 ├── MemberBallot (lecturer)   ← phiếu cá nhân, độc lập
 │    ├── Gate0Check (code A1..C5, passed, evidence)
 │    ├── CriterionScore (TC1..TC9, level, evidence)
 │    ├── ContributionNote (student, level)
 │    └── proposedConclusion
 ├── mergedCriteria / mergedGate0             ← hệ thống tính
 ├── systemConclusion  ↔  finalConclusion + overrideReason
 ├── crossCheck (ucInSRS, ucDemoed, logicErrors, showStoppers)
 ├── MinutesDocument (07.20a)
 └── RemediationItem (criterion, content, mandatory, dueDate, verifiedBy, verifiedAt)

Master: Lecturer · Room · ConflictDeclaration(lecturer, project, reason) · AuditLog
```

**Quy ước mã hóa:** Đề tài `[Kỳ][Ngành][STT]` (VD `SU26SE017`). Nhóm có mã riêng, do Bộ môn cấp, độc lập với mã đề tài.

---

## 4. Business Rules — Dữ liệu nền

| Mã | Quy tắc |
|---|---|
| **BR-SEM-01** | Một học kỳ có nhiều đề tài. Mỗi đề tài thuộc đúng 1 học kỳ. |
| **BR-SEM-02** | Hệ thống chỉ cho phép **một học kỳ ở trạng thái đang hoạt động** tại một thời điểm; các kỳ cũ ở chế độ chỉ đọc. |
| **BR-PRJ-01** | Mỗi đề tài có **1 hoặc 2 GVHD**. Khi có 2, bắt buộc phân vai: đúng **1 GVHD chính** và **1 đồng hướng dẫn**. |
| **BR-PRJ-02** | Một đề tài gắn với **đúng 1 nhóm** trong 1 học kỳ. |
| **BR-PRJ-03** | Đề tài bị fail có thể được cấp lại cho nhóm khác ở kỳ sau; mã đề tài mới được sinh theo kỳ mới, có liên kết tham chiếu về đề tài gốc. |
| **BR-GRP-01** | Mỗi nhóm có mã nhóm duy nhất, gắn với đúng 1 đề tài. |
| **BR-GRP-02** | Nhóm có **4–5 sinh viên** tại thời điểm thành lập. |
| **BR-GRP-03** | Mỗi nhóm có **đúng 1 trưởng nhóm** (LEADER) trong số các thành viên đang hoạt động. Nếu trưởng nhóm drop out, hệ thống bắt buộc chỉ định trưởng nhóm mới trước khi nhóm được xếp lịch. |
| **BR-GRP-04** | Thành viên nhóm được lưu theo **lịch sử thời gian** (`joinedAt`, `leftAt`). Mọi đánh giá cá nhân chỉ áp dụng cho thành viên **đang ACTIVE tại ngày diễn ra phiên**. |
| **BR-STU-01** | Sinh viên có thể **drop out** trong quá trình làm đồ án. Bản ghi drop out phải có: người khởi tạo, người duyệt, ngày hiệu lực, lý do. |
| **BR-STU-02** | Sinh viên đã drop out **không được đánh giá cá nhân** và không xuất hiện trong Biên bản của các phiên sau ngày hiệu lực. |
| **BR-STU-03** | ⭐ Nhóm có **dưới 4 thành viên** do drop out **vẫn được xếp lịch và bảo vệ bình thường**. Hệ thống hiển thị **cảnh báo** sĩ số cho hội đồng, không chặn. Điều kiện Gate 0 mục **C5 được tính theo sĩ số hiện hành**, không theo sĩ số ban đầu. |
| **BR-LEC-01** | Mỗi giảng viên có mã tài khoản duy nhất (VD `TaiNT51`), họ tên đầy đủ và email `@fe.edu.vn`. Mã tài khoản là khóa dùng trong mọi liên kết lịch. |
| **BR-LEC-02** | Giảng viên có thể khai báo **xung đột lợi ích** (`ConflictDeclaration`) với một đề tài cụ thể kèm lý do. Bộ môn cũng có quyền khai báo thay. |

> **Ghi chú BR-STU-03:** Đây là điểm **lệch có chủ ý** so với văn bản Gate 0 mục C5 ("Đủ 4–5 thành viên"). Quy định gốc không lường trước drop out. Cần Bộ môn xác nhận bằng văn bản để hội đồng không tick C5 = Không đạt một cách máy móc. Xem thêm Rủi ro R1.

---

## 5. Business Rules — Đợt đánh giá & Đăng ký

### 5.1. Vòng đời đợt

```
DRAFT ──▶ OPEN_REGISTRATION ──▶ REGISTRATION_CLOSED ──▶ SCHEDULING
                                                            │
                        ┌───────────────────────────────────┘
                        ▼
                    SCHEDULED ──▶ PUBLISHED ──▶ ONGOING ──▶ COMPLETED ──▶ LOCKED
                    (lịch nháp)
```

| Mã | Quy tắc |
|---|---|
| **BR-RND-01** | Đợt thuộc 1 trong 5 loại: `REVIEW_1`, `REVIEW_2`, `DEFENSE_1_1`, `DEFENSE_1_2`, `DEFENSE_2`. |
| **BR-RND-02** | Chỉ Moderator được tạo đợt và tạo slot. Slot = (ngày, giờ bắt đầu, giờ kết thúc). **Phòng không gắn vào slot** — phòng là tài nguyên được thuật toán gán ở bước xếp lịch. |
| **BR-RND-03** | Đợt có các tham số cấu hình: độ dài slot mặc định, số phiên tối đa/hội đồng/buổi, deadline đăng ký, `groupSelectionMode` (bật/tắt), trọng số ràng buộc mềm. |
| **BR-RND-04** | Chỉ được chuyển `OPEN_REGISTRATION` → `REGISTRATION_CLOSED` do Moderator bấm chủ động, hoặc tự động khi tới deadline. |
| **BR-RND-05** | Từ trạng thái `PUBLISHED` trở đi, mọi thay đổi đều phải qua quy trình sửa có kiểm soát (mục 7) và ghi audit log. |
| **BR-RND-06** | Ở trạng thái `LOCKED`, đợt là chỉ đọc tuyệt đối. Chỉ Admin mới mở khóa được, có ghi log. |

### 5.2. Mời giảng viên & đăng ký lịch rảnh

| Mã | Quy tắc |
|---|---|
| **BR-AVL-01** | Moderator gửi lời mời tham gia đợt tới danh sách giảng viên. GV có quyền **chấp nhận hoặc từ chối** lời mời. |
| **BR-AVL-02** | GV đã chấp nhận sẽ chọn các **slot mình có thể tham gia** trong đợt đó. |
| **BR-AVL-03** | ⭐ Khi đăng ký, GV đồng thời chọn **mức ưu tiên khối lượng** (`preferredLoadLevel`): muốn được xếp **nhiều / trung bình / ít** slot. Đây là đầu vào chính của mục tiêu cân bằng tải. |
| **BR-AVL-04** | ⭐ GV **không đăng ký slot nào** trước deadline ⇒ hệ thống coi là **bận toàn bộ**, không xếp GV đó vào đâu. Hệ thống liệt kê danh sách GV chưa đăng ký để Moderator nhắc hoặc nhập hộ. |
| **BR-AVL-05** | GV được sửa/rút đăng ký **cho tới khi đợt đóng đăng ký**. Sau đó chỉ Moderator sửa được. |
| **BR-AVL-06** | ⭐ Khi Moderator bật `groupSelectionMode`, **trưởng nhóm** đại diện nhóm chọn các slot nhóm có thể tham gia. Khi tắt, nhóm **phải tuân thủ** lịch được xếp, không có quyền chọn. |
| **BR-AVL-07** | Trong chế độ `groupSelectionMode`, nhóm **không chọn slot nào** trước deadline ⇒ coi như **rảnh mọi slot** (ngược với quy tắc của giảng viên tại BR-AVL-04). |

---

## 6. Business Rules — Thuật toán xếp lịch

### 6.1. Ràng buộc CỨNG — vi phạm ⇒ lịch không hợp lệ

| Mã | Ràng buộc | Ghi chú |
|---|---|---|
| **H1** | GVHD (**cả chính và đồng hướng dẫn**) không được là thành viên hội đồng đánh giá đề tài mình hướng dẫn — áp dụng cho **mọi loại đợt** | Đã kiểm chứng: 0/74 vi phạm trong dữ liệu SU26 |
| **H2** | Một giảng viên không được xếp vào 2 phiên trùng giờ | |
| **H3** | Một phòng không được có 2 phiên trùng giờ | |
| **H4** | Một nhóm chỉ có **đúng 1 phiên** trong 1 đợt | |
| **H5** | Hội đồng phải đủ người theo loại đợt: Review = **2 GV**; Defense = **3 GV** đủ 3 vai Chủ tịch / Phản biện / Thư ký | |
| **H6** | Một giảng viên chỉ giữ **1 vai trò** trong 1 phiên | |
| **H7** | Chỉ xếp giảng viên vào slot mà GV **đã đăng ký rảnh** | Theo BR-AVL-04 |
| **H8** | Không xếp giảng viên có `ConflictDeclaration` với đề tài đó | |
| **H9** | Nhóm phải ở trạng thái **đủ điều kiện** của loại đợt (xem mục 9) | |
| **H10** | Khi `groupSelectionMode` bật và nhóm đã chọn slot: chỉ xếp nhóm vào slot nhóm đã chọn | |
| **H11** | ⭐ **Defense 1.2 phải giữ nguyên Chủ tịch** đã chấm Defense 1.1 của chính nhóm đó | Moderator được gỡ ràng buộc này cho từng nhóm, **bắt buộc ghi lý do** |

### 6.2. Ràng buộc MỀM — điểm phạt, xếp theo thứ tự ưu tiên

| Mã | Ràng buộc mềm | Ưu tiên |
|---|---|---|
| **S1** | ⭐ **Cân bằng tải giảng viên** — tối thiểu hóa độ lệch giữa số slot được xếp và mức ưu tiên khối lượng GV đã chọn (BR-AVL-03) | **1 — cao nhất** |
| **S2** | Defense 1.2: giữ **Phản biện** đã chấm Defense 1.1 của nhóm đó | 2 |
| **S3** | Review 2: giữ nguyên **cặp 2 GV** đã chấm Review 1 của nhóm đó | 3 |
| **S4** | Gom các phiên của cùng 1 GV **liên tiếp** trong 1 buổi, tránh giờ trống ở giữa | 4 |
| **S5** | Giảm số **ngày** mỗi GV phải có mặt | 5 |
| **S6** | Defense 1.2: giữ **Thư ký** đã chấm Defense 1.1 của nhóm đó | 6 |
| **S7** | Giữ **tổ hợp hội đồng ổn định** giữa các phiên liên tiếp trong cùng buổi | 7 |
| **S8** | Tránh để 1 GV chấm quá nhiều nhóm của cùng 1 GVHD | 8 |
| **S9** | Dùng ít phòng nhất có thể | 9 |

> **Lưu ý thiết kế:** S1 (cân bằng tải) và S4/S5 (gom lịch cho GV) **xung đột nhau về bản chất**. Vì stakeholder chọn cân bằng tải là mục tiêu số 1, lịch sinh ra sẽ **rải rác hơn** cách xếp thủ công hiện tại (4 nhóm liên tiếp/buổi). Trọng số phải cấu hình được để Bộ môn tự tinh chỉnh sau vài kỳ chạy thật.

### 6.3. Vận hành thuật toán

| Mã | Quy tắc |
|---|---|
| **BR-SCH-01** | Moderator được **chạy thuật toán nhiều lần**, mỗi lần sinh 1 `ScheduleVersion` kèm điểm số từng ràng buộc mềm để so sánh. Chỉ 1 version được đặt `isActive`. |
| **BR-SCH-02** | Khi không tìm được lời giải đầy đủ, hệ thống **vẫn trả kết quả một phần**, kèm danh sách nhóm chưa xếp được và **lý do cụ thể** cho từng nhóm (thiếu GV rảnh / hết slot / vướng H1 / vướng H11...). |
| **BR-SCH-03** | Kèm theo kết quả một phần, hệ thống **đề xuất phương án gỡ**: mở thêm slot ngày nào, mời thêm GV nào, gỡ ràng buộc mềm nào. |
| **BR-SCH-04** | Moderator được **sửa tay** lịch nháp. Hệ thống **chặn cứng** mọi thao tác vi phạm H1, H2, H3. Các vi phạm còn lại chỉ **cảnh báo** và **bắt ghi lý do**. |
| **BR-SCH-05** | Mọi thao tác sửa tay được ghi `AuditLog`: ai, lúc nào, từ giá trị nào sang giá trị nào, lý do. |

---

## 7. Business Rules — Công bố & Thay đổi sau công bố

| Mã | Quy tắc |
|---|---|
| **BR-PUB-01** | Moderator công bố lịch. Khi công bố, hệ thống gửi thông báo tới: giảng viên trong hội đồng, GVHD của từng nhóm, và trưởng nhóm sinh viên. |
| **BR-PUB-02** | ⭐ Sau công bố, **vẫn được thay đổi thành viên hội đồng** trong lúc đợt đang diễn ra. |
| **BR-PUB-03** | Người thay thế phải thỏa **toàn bộ ràng buộc cứng** H1, H2, H3, H6, H8. Hệ thống chặn nếu vi phạm. |
| **BR-PUB-04** | Mọi thay đổi sau công bố **bắt buộc có lý do** và được ghi audit log kèm thông báo tới các bên liên quan. |
| **BR-PUB-05** | Thay đổi thành viên **không ảnh hưởng** tới kết quả của các phiên đã hoàn thành trước đó — mỗi `EvaluationResult` gắn cứng với danh sách hội đồng **tại thời điểm phiên diễn ra**. |
| **BR-INC-01** | ⭐ **Sự cố ngày bảo vệ** (GV vắng đột xuất): Moderator được thay người ngay tại chỗ. Hệ thống vẫn kiểm tra đầy đủ ràng buộc cứng. **Hội đồng luôn phải đủ 3 người** — không chấp nhận chấm với 2 người. |
| **BR-INC-02** | Nếu không tìm được người thay thế hợp lệ, phiên phải được **hoãn** và xếp lại vào slot bù. Nhóm không bị đánh giá bất lợi vì việc hoãn này. |
| **BR-INC-03** | Nhóm vắng mặt không phép ⇒ ghi nhận vào biên bản, hội đồng đánh giá theo hồ sơ hiện có. Vắng có phép (Bộ môn duyệt) ⇒ hoãn sang slot bù. |

---

## 8. Business Rules — Chấm điểm Defense

### 8.1. Phiếu cá nhân & Gate 0

| Mã | Quy tắc |
|---|---|
| **BR-BAL-01** | ⭐ **Mỗi thành viên hội đồng nhập phiếu độc lập** (Phụ lục A): 13 mục Gate 0 + 9 tiêu chí + mức đóng góp từng sinh viên + đề xuất kết luận. |
| **BR-BAL-02** | Phiếu của thành viên khác **bị ẩn** cho tới khi cả 3 phiếu được nộp — nhằm giữ nguyên tắc "đánh giá độc lập trước, hợp nhất sau" (Guideline 1.2, nguyên tắc 3). |
| **BR-BAL-03** | Mỗi mức đánh giá phải kèm **minh chứng** dạng text. Hệ thống cảnh báo nếu để trống ở các mục Không đạt. |
| **BR-BAL-04** | Bắt buộc nhập **3 con số kiểm tra chéo**: số use case khai trong SRS, số use case demo được, số lỗi logic / show-stopper. |
| **BR-GATE-01** | Gate 0 gồm 13 mục: **A1–A3** (dẫn tới làm lại đồ án), **B1–B5** (dẫn tới bảo vệ lần 2), **C1–C5** (điều kiện hồ sơ). |
| **BR-GATE-02** | ⭐ **Điểm OGA nằm ngoài app.** Hội đồng nhập tay giá trị OGA khi chấm mục A3 (`OGA ≥ 2/10` cho mọi đầu điểm) và B5 (`OGA ≥ 5/10`). |
| **BR-GATE-03** | ⭐ Nếu GVHD **chưa gửi OGA**, hội đồng tick "chưa có OGA" ⇒ hệ thống tự đặt **A3 = Đạt và B5 = Đạt** (theo Guideline 3.1, 3.2). |
| **BR-GATE-04** | Mục **C5** được tính theo sĩ số hiện hành sau drop out — xem BR-STU-03. |

### 8.2. Hợp nhất phiếu

| Mã | Quy tắc |
|---|---|
| **BR-MRG-01** | Mức của nhóm ở mỗi tiêu chí = mức được **ít nhất 2 trong 3** thành viên chọn. |
| **BR-MRG-02** | Nếu **cả 3 thành viên chọn 3 mức khác nhau**, hệ thống cảnh báo để Chủ tịch yêu cầu trao đổi lại. Nếu vẫn không thống nhất, hệ thống lấy **mức thấp hơn trong hai mức được nêu nhiều nhất** (Guideline 5.1). |
| **BR-MRG-03** | Với Gate 0 (nhị phân Đạt/Không), mục được coi là **vi phạm** nếu **≥ 2/3** thành viên tick Không đạt. |
| **BR-MRG-04** | Mức đóng góp cá nhân của sinh viên = mức được ≥2/3 thành viên chọn; nếu phân tán thì lấy mức thấp hơn trong 2 mức nhiều nhất. |
| **BR-MRG-05** | Sinh viên bị đánh giá **"Rất hạn chế"** ⇒ hệ thống **bắt buộc hội đồng kiểm tra lại điều kiện A1** (liêm chính học thuật) trước khi chốt (Guideline 5.2). |

### 8.3. Suy ra kết luận — Decision table

Hệ thống tính `systemConclusion` theo thuật toán sau. **Nguyên tắc bao trùm: luôn lấy mức thấp nhất (số lớn nhất) trong các mức mà nhóm rơi vào.**

```
Ký hiệu:
  TRỌNG_YẾU = {TC3, TC7, TC9}
  TÀI_LIỆU_TRÌNH_BÀY = {TC1, TC2, TC5, TC6, TC8}
  n_KĐ  = số tiêu chí ở mức Không đạt
  n_CS  = số tiêu chí ở mức Cần sửa

── MỨC 4 (Không đạt — làm lại khóa luận) nếu BẤT KỲ điều nào đúng:
   • vi phạm bất kỳ mục nhóm A (A1, A2, A3)
   • một trong TRỌNG_YẾU ở mức Không đạt
   • n_KĐ ≥ 3
   • nhóm đã ở mức 3 tại lần bảo vệ thử trước mà chưa khắc phục

── MỨC 3 (Sửa lại để bảo vệ lần 2) nếu BẤT KỲ điều nào đúng:
   • vi phạm bất kỳ mục nhóm B (B1..B5)
   • một trong TRỌNG_YẾU ở mức Cần sửa
   • n_KĐ ∈ {1, 2}
   • n_CS ≥ 4

── MỨC 2 (Được bảo vệ lần 1 — chỉnh sửa gửi lại trong N ngày) nếu ĐỒNG THỜI:
   • qua toàn bộ Gate 0 nhóm A và nhóm B
   • cả TC3, TC7, TC9 đều Đạt
   • n_KĐ = 0
   • n_CS ∈ {2, 3} VÀ tất cả tiêu chí Cần sửa đều ∈ TÀI_LIỆU_TRÌNH_BÀY
   HOẶC: chỉ vi phạm nhóm C (trần kết luận là mức 2)

── MỨC 1 (Được bảo vệ lần 1) nếu ĐỒNG THỜI:
   • qua toàn bộ Gate 0 (A, B và C)
   • cả TC3, TC7, TC9 đều Đạt
   • n_KĐ = 0
   • n_CS ≤ 1
```

| Mã | Quy tắc |
|---|---|
| **BR-CON-01** | Hệ thống tính `systemConclusion` theo decision table trên và hiển thị **đường dẫn suy luận** (điều kiện nào đã kích hoạt mức nào). |
| **BR-CON-02** | ⭐ **Chủ tịch được override** kết luận hệ thống suy ra. Khi override, hệ thống **bắt buộc nhập lý do** và ghi rõ trong biên bản rằng "đây là quyết định của Chủ tịch" (Guideline 5.1). |
| **BR-CON-03** | Khi chọn mức 2, **bắt buộc điền số ngày cụ thể** cho hạn chỉnh sửa (khuyến nghị 5–7 ngày). |
| **BR-CON-04** | Với mọi kết luận **khác mức 1**, hệ thống **bắt buộc lập Bảng yêu cầu chỉnh sửa** (Phụ lục B) — không cho chốt biên bản nếu bảng trống. |
| **BR-CON-05** | Biên bản chỉ được chốt khi cả 3 phiếu cá nhân đã nộp và Chủ tịch đã ký duyệt. |

### 8.4. Biên bản & khắc phục

| Mã | Quy tắc |
|---|---|
| **BR-MIN-01** | Hệ thống sinh **Biên bản FPTU 07.20a** tự động từ dữ liệu đã nhập, đủ các mục 3, 4.1–4.4, 5, 6. |
| **BR-MIN-02** | Mục 4.3 của biên bản **bắt buộc chứa 3 con số kiểm tra chéo** (BR-BAL-04). |
| **BR-MIN-03** | **SLA:** Thư ký hoàn thiện biên bản trong **24 giờ**; Bảng yêu cầu chỉnh sửa gửi tới nhóm và GVHD trong **48 giờ**. Hệ thống nhắc tự động khi sắp quá hạn. |
| **BR-REM-01** | Mỗi dòng Bảng yêu cầu chỉnh sửa gồm: tiêu chí liên quan, nội dung phải sửa, mức độ (**Bắt buộc** / Khuyến nghị), hạn hoàn thành, người xác nhận. |
| **BR-REM-02** | Chỉ các mục **Bắt buộc** mới là điều kiện để ra bảo vệ chính thức. |
| **BR-REM-03** | **Giảng viên phản biện** là người xác nhận nhóm đã khắc phục xong. |
| **BR-REM-04** | ⭐ Khi kết luận mức 2 **quá hạn** mà phản biện chưa xác nhận đạt, hệ thống **cảnh báo** tới Chủ tịch, Phản biện, Moderator, GVHD và nhóm — nhưng **không tự động chuyển kết luận**. Việc chuyển sang Không đạt phải do **Chủ tịch hội đồng bấm xác nhận**, có ghi lý do. |
| **BR-REM-05** | Hệ thống nhắc trước hạn **2 ngày** cho nhóm và phản biện. |

> **Cảnh báo tuân thủ (BR-REM-04):** Guideline mục 1.4 và StudentGuide mục VIII ghi rõ *"Quá hạn hoặc sửa chưa đạt thì kết quả **tự động** chuyển thành Không đạt"*. Hệ thống đang thiết kế theo hướng **bán tự động** (cảnh báo + người chốt). Đây là lệch có chủ ý so với văn bản — xem Rủi ro R2.

---

## 9. Business Rules — Luồng chuyển tiếp giữa các đợt

### 9.1. Máy trạng thái của nhóm

```
                 ┌──────────────────────────────────────────────┐
                 │                  ACTIVE                       │
                 └───┬──────────────────────────────────────────┘
                     │ Review 1 (2 GV) ──▶ kết quả: cảnh báo, KHÔNG chặn
                     │ Review 2 (2 GV) ──▶ kết quả: cảnh báo, KHÔNG chặn
                     ▼
              ┌─────────────────┐
              │  DEFENSE_1_1    │  (3 GV: CT, PB, TK)
              └────┬────────────┘
        ┌──────────┼──────────┬─────────────────┐
     Mức 1      Mức 2       Mức 3            Mức 4
        │          │           │                │
        │          ▼           ▼                ▼
        │   ELIGIBLE_D12   PENDING_D2       FAILED
        │   _CONDITIONAL       │          (làm lại kỳ sau,
        │          │           │           KHÔNG có Defense 2)
        │   PB xác nhận đạt    │
        │     ──▶ đủ ĐK        ▼
        │   Quá hạn + CT chốt  DEFENSE_2
        │     ──▶ FAILED       │
        ▼                  ┌───┴───┐
   ELIGIBLE_D12         Đạt      Không đạt
        │                 │          │
        ▼                 ▼          ▼
   DEFENSE_1_2       COMPLETED    FAILED
        │
        ▼
   COMPLETED
```

### 9.2. Quy tắc chuyển tiếp

| Mã | Quy tắc |
|---|---|
| **BR-FLOW-01** | ⭐ Kết quả **Review 1 và Review 2 không chặn** nhóm đi tiếp. Mọi nhóm đều được xếp Defense 1.1. Kết quả review chỉ mang tính **cảnh báo sớm** cho nhóm, GVHD và hội đồng Defense. |
| **BR-FLOW-02** | Review 1 đánh giá **Requirement**. Review 2 đánh giá **thiết kế ERD, cơ sở dữ liệu và công nghệ sử dụng**. Cả hai do **2 giảng viên không phải GVHD** thực hiện. |
| **BR-FLOW-03** | **Mức 1** ⇒ nhóm đủ điều kiện, được xếp **Defense 1.2** ngay. |
| **BR-FLOW-04** | **Mức 2** ⇒ nhóm được xếp Defense 1.2 nhưng ở trạng thái **có điều kiện**. Suất Defense 1.2 chỉ có hiệu lực khi phản biện xác nhận đã khắc phục xong các mục Bắt buộc **trước hạn**. |
| **BR-FLOW-05** | **Mức 2 quá hạn** ⇒ hệ thống cảnh báo; Chủ tịch chốt chuyển thành **Không đạt (mức 4)** ⇒ nhóm FAILED, hủy suất Defense 1.2 đã xếp (theo BR-REM-04). |
| **BR-FLOW-06** | **Mức 3** ⇒ nhóm **không ra bảo vệ đợt này**, chuyển sang trạng thái chờ **Defense 2**. Bảng yêu cầu chỉnh sửa là căn cứ đánh giá lại. |
| **BR-FLOW-07** | ⭐ **Mức 4** ⇒ nhóm **FAILED ngay**, phải làm lại đồ án ở kỳ sau. **Không được xếp Defense 2.** |
| **BR-FLOW-08** | **Defense 2 không đạt** ⇒ nhóm FAILED, làm lại đồ án ở kỳ sau. |
| **BR-FLOW-09** | Nhóm FAILED được tạo bản ghi **retake** cho kỳ sau, giữ liên kết tham chiếu tới đề tài và nhóm gốc. |
| **BR-FLOW-10** | Ràng buộc H9: nhóm chỉ được xếp vào đợt nếu đang ở trạng thái tương ứng. Nhóm FAILED không được xếp vào bất kỳ đợt nào của kỳ hiện tại. |

---

## 10. Phân quyền

| Actor | Quyền chính |
|---|---|
| **Admin** | Cấu hình học kỳ, master data giảng viên/phòng, mở khóa đợt đã LOCKED |
| **Moderator (Bộ môn)** | Tạo đợt, tạo slot, mời GV, đóng đăng ký, chạy thuật toán, sửa lịch, công bố, xử lý sự cố, thay người |
| **Giảng viên** | Nhận lời mời, đăng ký slot rảnh + mức ưu tiên khối lượng, xem lịch cá nhân |
| **GVHD** | + Xem tiến độ và kết quả mọi đợt của nhóm mình hướng dẫn; khai báo xung đột lợi ích |
| **Thành viên hội đồng** | + Nhập phiếu cá nhân cho phiên được phân công |
| **Giảng viên phản biện** | + Xác nhận nhóm đã khắc phục các mục Bắt buộc |
| **Chủ tịch hội đồng** | + Chốt kết luận, override kết luận kèm lý do, ký biên bản, chốt chuyển mức 2 quá hạn sang Không đạt |
| **Thư ký hội đồng** | + Lập biên bản 07.20a và Bảng yêu cầu chỉnh sửa |
| **Trưởng nhóm SV** | Chọn slot cho nhóm (khi bật `groupSelectionMode`), xem lịch và kết quả |
| **Sinh viên** | Xem lịch, kết quả nhóm, mức đóng góp cá nhân của chính mình, bảng yêu cầu chỉnh sửa |

| Mã | Quy tắc |
|---|---|
| **BR-SEC-01** | Giảng viên chỉ xem được phiếu của thành viên khác **sau khi cả 3 phiếu đã nộp**. |
| **BR-SEC-02** | Sinh viên chỉ xem được **mức đóng góp của chính mình**, không xem được của bạn cùng nhóm. |
| **BR-SEC-03** | GVHD không được xem phiếu cá nhân chi tiết của hội đồng chấm nhóm mình trước khi biên bản được chốt. |

---

## 11. Rủi ro & Điểm còn mở

### 11.1. Rủi ro cần xử lý

| Mã | Rủi ro | Mức độ | Đề xuất |
|---|---|---|---|
| **R1** | **BR-STU-03 lệch quy định C5.** Văn bản Gate 0 yêu cầu "đủ 4–5 thành viên"; hệ thống cho nhóm 3 người vẫn bảo vệ. Nếu hội đồng tick C5 = Không đạt theo đúng chữ nghĩa, nhóm bị trần kết luận mức 2 một cách oan | Cao | Xin Bộ môn ra văn bản diễn giải C5 theo sĩ số hiện hành. Trong app, hiển thị ngay tại mục C5 dòng chú thích "Nhóm có N/5 SV, M SV đã drop out có duyệt ngày dd/mm" |
| **R2** | **BR-REM-04 lệch quy định.** Guideline ghi "tự động chuyển thành Không đạt"; hệ thống chọn bán tự động. Nếu không ai bấm chốt, nhóm quá hạn vẫn giữ suất Defense 1.2 — trái quy định | Cao | Bổ sung leo thang: quá hạn 3 ngày mà Chủ tịch chưa chốt thì hệ thống báo lên Trưởng bộ môn |
| **R3** | **Ràng buộc thời gian của Phản biện.** Phản biện phải đọc 7 report và **tự cài đặt phần mềm** trước buổi — cần vài ngày. Nhưng BR-PUB-02 cho phép đổi người trong lúc đợt đang diễn ra, và BR-INC-01 cho thay người ngay tại chỗ | Cao | Hệ thống cảnh báo khi thay Phản biện muộn hơn N ngày trước phiên. Cân nhắc phân công Phản biện **sớm hơn** phần còn lại của lịch |
| **R4** | **S1 xung đột S4/S5.** Cân bằng tải làm lịch rải rác, GV phải đến trường nhiều ngày hơn cách làm thủ công hiện tại — có thể gây phản ứng từ giảng viên | Trung bình | Cho Bộ môn cấu hình trọng số; chạy song song với cách thủ công 1 kỳ để so sánh |
| **R5** | **BR-AVL-04 (không đăng ký = bận) có thể làm thuật toán vô nghiệm** nếu nhiều GV quên đăng ký | Trung bình | Nhắc tự động trước deadline; dashboard tỷ lệ đăng ký cho Moderator theo dõi |
| **R6** | **H11 (giữ Chủ tịch ở Defense 1.2)** làm giảm mạnh không gian lời giải, đặc biệt khi Chủ tịch đó bận | Trung bình | Đã có cơ chế Moderator gỡ ràng buộc theo từng nhóm kèm lý do |

### 11.2. Điểm còn mở — cần quyết định trước khi thiết kế chi tiết

| # | Câu hỏi |
|---|---|
| **O1** | Hội đồng **Defense 2** có ràng buộc giữ người giống H11/S2 không, hay ghép tự do hoàn toàn? |
| **O2** | Nhóm đạt **Defense 2** thì kết thúc luôn, hay vẫn phải qua một buổi bảo vệ chính thức nữa? (Guideline không nói rõ; hiện đang mô hình hóa Defense 2 là **đợt cuối cùng**) |
| **O3** | Tiêu chuẩn để một giảng viên được làm **Chủ tịch hội đồng** (học hàm/học vị/thâm niên)? Hiện hệ thống chưa ràng buộc. |
| **O4** | Định mức **trần cứng** số phiên/ngày và số phiên/kỳ cho mỗi giảng viên — hay chỉ dựa hoàn toàn vào mức ưu tiên GV tự chọn? |
| **O5** | Có cần thu **availability của nhóm** ở cả Review 1/2 hay chỉ ở các đợt Defense? |
| **O6** | Buổi đánh giá **online (MS Teams)** có được coi là một loại "phòng" với giới hạn số phiên song song không? |
| **O7** | Có yêu cầu **xuất Excel đúng định dạng hiện tại** (2 sheet) để bàn giao Phòng Đào tạo / Khảo thí không? |
| **O8** | **Tích hợp** nào bắt buộc ở v1: SSO `@fe.edu.vn`, đẩy lịch sang Google/Outlook Calendar, email tự động? |

---

## 12. Phụ lục — Tham số cấu hình

| Tham số | Giá trị mặc định (theo SU26) | Cấu hình theo |
|---|---|---|
| Độ dài slot | 60 phút | Đợt |
| Khung giờ buổi sáng | 08:00–12:00 (4 slot) | Đợt |
| Khung giờ buổi chiều | 13:30–17:30 (4 slot) | Đợt |
| Số phiên tối đa / hội đồng / buổi | 4 | Đợt |
| Số GV hội đồng — Review | 2 | Loại đợt |
| Số GV hội đồng — Defense | 3 | Loại đợt |
| Hạn chỉnh sửa mức 2 | 5–7 ngày | Từng nhóm |
| Nhắc trước hạn khắc phục | 2 ngày | Hệ thống |
| SLA biên bản | 24 giờ | Hệ thống |
| SLA bảng yêu cầu chỉnh sửa | 48 giờ | Hệ thống |
| `groupSelectionMode` | Tắt | Đợt |
| Trọng số ràng buộc mềm S1–S9 | Theo thứ tự ưu tiên mục 6.2 | Đợt |

---

*Tài liệu này là đầu vào cho SRS. Mọi quy tắc có mã `BR-*`, `H*`, `S*` để trace ngược từ code và test case về quy định gốc.*
