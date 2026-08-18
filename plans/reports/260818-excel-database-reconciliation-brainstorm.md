# Excel ↔ Database Reconciliation Brainstorm

**Ngày:** 2026-08-18  
**Phạm vi:** đọc-only, chưa import và chưa thay đổi database  
**Workbook:** `SE_CapstoneProject_SP26_ReviewDefense_New.xlsx`

## Kết luận ngắn

File Excel và database hiện tại **chưa đồng bộ** và **không thể import thẳng một cách an toàn**.

Excel đang thể hiện một snapshot vận hành có mã đề tài, mã nhóm, mã giảng viên và tên phòng thật. Database hiện tại đang chứa fixture Scheduler-only (`P001…P074`, `G001…G074`, `GV01…GV26`, `R01…R04`) cùng nhiều dữ liệu test lặp. Đây là hai bộ dữ liệu khác nhau, không chỉ khác format.

Theo spec hiện tại, Excel import/export còn nằm ngoài phạm vi V1. Vì vậy, kết quả này chưa phải là lý do để ghi Excel vào database; nó là bằng chứng rằng cần chốt một nguồn dữ liệu và một quy trình mapping riêng trước.

## 1. Excel đang có gì?

| Sheet | Dữ liệu đọc được |
|---|---|
| `Project` | 131 project/group khác nhau; có supervisor, các mã schedule, reviewer, ngày, slot, room, result/state |
| `Review1` | 44 schedule rows; 2026-01-22 đến 2026-01-30; 2 reviewer/row |
| `Review2` | 44 schedule rows; 2026-03-04 đến 2026-03-12; 2 reviewer/row |
| `Review3` | 44 schedule rows; 2026-04-20 đến 2026-04-24; 2 reviewer/row |
| `Defense1` | 20 council rows, 14 council đang có thành viên, 6 council rỗng; 2026-05-07 đến 2026-05-11 |
| `Defense2` | 20 council rows, 16 council đang có thành viên, 4 council rỗng; 2026-06-07 đến 2026-06-11 |
| `Summary` | Bảng tổng hợp workload theo giảng viên |

Các sheet review độc lập có ngày và thứ khớp nhau: không phát hiện date/day mismatch trong 132 schedule rows.

## 2. Database hiện tại đang có gì?

Database đang dùng semester `SE-2026-2027`, trạng thái `DRAFT`:

- 119 projects và 74 groups.
- 26 lecturers, mã `GV01` đến `GV26`.
- 31 rooms, gồm `R01…R04` và các room ID test dạng `R-<hash>`.
- Có 16 round `REVIEW_1` ở trạng thái `DRAFT`.
- Có 121 round `DEFENSE_1_1`: 56 `DRAFT`, 21 `SCHEDULED`, 44 `PUBLISHED`.
- Hiện không có round mục tiêu tương ứng cho `REVIEW_2`, `REVIEW_3`, `DEFENSE_1_2` hoặc `DEFENSE_2` trong kỳ này.
- Trong các round D1.1 hiện có, dữ liệu test đã tạo 25 group references và 85 sessions.

Toàn database có dấu hiệu đã được chạy test nhiều lần: 173 projects, 128 groups, 164 rounds, 117 schedule versions, 112 sessions. Vì vậy database hiện tại không phải một database rỗng sạch để nhận file nghiệp vụ.

## 3. So sánh khóa dữ liệu

| Entity | Excel | Database kỳ `SE-2026-2027` | Đánh giá |
|---|---:|---:|---|
| Project | 131 mã thật như `SP26SE016` | 119 mã, chủ yếu `P001…P074` và mã test | Không trùng mã |
| Group | 131 mã dạng `GSP26SE…` | 74 mã `G001…G074` | Không trùng mã; khác quy ước và khác cardinality |
| Supervisor | 37 mã thật, ví dụ `VanTTN2`, `TaiNT51` | 26 mã `GV01…GV26` | Không có mapping trực tiếp |
| Reviewer | Mã thật, khoảng 29 mã được dùng trong review/council | Cũng chỉ có lecturer fixture `GV01…GV26` | Không có mapping trực tiếp |
| Room | Tên thật như `NVH G.01`, `NVH.301`, `NVH.414` | Code canonical như `R01…R04` và room test | Không có mapping trực tiếp; Excel không cung cấp capacity |

Nói cách khác, không thể dùng `project.code`, `group.code`, `lecturer_code` hoặc `room.code` của Excel làm foreign key vào database hiện tại.

## 4. So sánh nghiệp vụ với Scheduler-only

### Có thể hiểu/mapping về mặt khái niệm

- `Review1` có thể tương ứng với round `REVIEW_1`.
- `Review2` có thể tương ứng với `REVIEW_2` nếu round type này được tạo và đã được chốt trong scope thực thi.
- Hai reviewer trong các sheet review phù hợp với quy tắc Review có 2 reviewer.
- Ngày, slot, room và reviewer có thể trở thành session schedule data sau khi mapping master data.
- `Defense1`/`Defense2` có thể cung cấp ngày, mã hội đồng và danh sách thành viên để dựng schedule sau khi chốt mô hình council.

### Chưa thể mapping trực tiếp

1. **`Review3` chưa có trong Scheduler-only hiện tại.** Spec hiện tại có Review 1, Review 2, D1.1, D1.2 và D2; không có Review3. Không được tự ý đổi Review3 thành D1.1 hoặc một round khác.

2. **Mô hình hội đồng không khớp.** Excel có 5 người theo vai trò `Chủ tịch`, `Thư ký`, `Thành viên 1`, `Thành viên 2`, `Thành viên 3`. Scheduler-only hiện mô tả Defense là 3 reviewer ngang hàng, không có Chair/Secretary. Đây là khác biệt domain, không phải khác tên cột.

3. **Không rõ semantics của result/state.** Excel có `Result`, `State`, `Supervisor Result`, `Reviewer Check`, conflict checks và workload summary. Các giá trị này không có mapping một-một đã được chốt vào `session_results`/state machine hiện tại.

4. **Thiếu dữ liệu đầu vào bắt buộc của database.** Excel không cung cấp đầy đủ student records, group memberships, email/account, lecturer availability, room capacity, semester/major metadata và invitation lifecycle. Không thể dựng một kỳ dữ liệu hoàn chỉnh chỉ từ workbook này.

5. **Trộn nhiều term trong cùng workbook.** Mã project có các nhóm `FA25`, `SP26`, `SU25`; trong khi database đang nhắm tới một semester duy nhất `SE-2026-2027`. Cần xác định workbook này thuộc semester nào trước khi import.

## 5. Vấn đề chất lượng trong chính workbook

Các sheet độc lập có thể đọc được, nhưng sheet tổng hợp không đủ sạch để làm source-of-truth mà không validation:

- `Project` có 232 giá trị `#N/A`, gồm các ô tổng hợp Review2 và Defense.
- `Defense1` có 30 giá trị `#REF!` ở các dòng council rỗng.
- `Defense2` có 20 giá trị `#REF!` ở các dòng council rỗng.
- Ví dụ dòng project `FA25SE224`: cột `Review1 Result` đang chứa `7411`, trùng với mã `Review2 Code` của cùng dòng. Điều này cho thấy các cột formula/tổng hợp trên `Project` cần được kiểm tra trước khi dùng làm dữ liệu nhập.
- Các sheet `Review1`, `Review2`, `Review3` không có literal formula error trong các dòng schedule đã đọc.

Do đó, nếu cần lấy lịch, nên ưu tiên parse các sheet schedule độc lập rồi đối chiếu ngược về project/group; không lấy toàn bộ các cột formula trong `Project` làm dữ liệu gốc.

## 6. Đối chiếu với tài liệu dự án

Kết quả này phù hợp với các tài liệu hiện tại:

- `plans/capstone-scheduler/spec.md` nói V1 nhập dữ liệu qua form/API hoặc seed fixture; Excel import/export nằm ngoài scope.
- `docs/operator-guide.md` cũng không mô tả Excel import cho V1.
- `BusinessRules_CapstoneScheduler_v1.0.md` lại dùng canonical lecturer key dạng thật như `TaiNT51` và mô tả council có vai trò Chair/Secretary. Điều này gần với workbook hơn database fixture hiện tại, nhưng lại chưa khớp hoàn toàn với Scheduler-only spec.

Vì vậy hiện có ba lớp cần tách rõ:

1. BusinessRules/workbook nghiệp vụ thật.
2. Scheduler-only spec đã chốt cho sản phẩm V1.
3. Database fixture/test hiện đang chạy local.

## 7. Quyết định đề xuất

**Không import trực tiếp vào database hiện tại.** Đề xuất quy trình an toàn nếu sếp muốn dùng Excel làm input thật:

1. Chụp backup và tạo database/staging sạch, không dùng database đang có test residue.
2. Chốt workbook thuộc semester nào; tách các project ngoài semester đó.
3. Tạo data contract/mapping cho project, group, lecturer và room; có bảng alias từ mã Excel sang canonical ID.
4. Import raw Excel vào staging, chạy validation report và hiển thị các dòng lỗi trước khi commit.
5. Chốt riêng mapping cho Review3, 5-role council, Result/State và các dữ liệu còn thiếu.
6. Chỉ sau khi dry-run đạt yêu cầu mới tạo canonical entities và schedule versions trong database.

Nếu vẫn giữ Scheduler-only như spec hiện tại, workbook chỉ nên được dùng làm tài liệu tham khảo/test fixture sau khi được rút gọn về đúng 5 round và mô hình Defense 3 reviewer.

## 8. Ba điểm cần sếp chốt

1. Workbook này có phải source-of-truth cho một semester thật không? Nếu có, semester code chính xác là gì, và có giữ cả `FA25`, `SP26`, `SU25` trong cùng một lần load không?
2. Có file master để map lecturer/room/student thật sang database không, hay phải thay fixture `GVxx/Rxx` bằng dữ liệu thật từ workbook/FAP?
3. Chọn hướng nào: giữ Scheduler-only và loại `Review3`/Chair/Secretary, hay mở rộng spec để hỗ trợ đúng workbook (Excel import, Review3 và council 5 vai trò)?

**Verdict:** hiện tại **chưa đồng bộ, chưa đủ điều kiện import, và không nên ghi trực tiếp vào database local hiện tại**.
