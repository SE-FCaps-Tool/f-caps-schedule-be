

## ĐẠI HỌC FPT — BỘ MÔN KỸ THUẬT PHẦN MỀM
## THUẬT TOÁN XẾP LỊCH
## HỘI ĐỒNG CAPSTONE PROJECT
Đặc tả kỹ thuật cho đội phát triển
Phiên bản 1.0
Cơ sở thực nghiệm: học kỳ SU26 — ngành Kỹ thuật phần mềm
Thuật toán xếp lịch Hội đồng Capstone Project  |  1

Mục lục
-  Mục đích và phạm vi
-  Bối cảnh nghiệp vụ
Chuỗi năm vòng · Hình thái từng vòng · Dữ liệu đầu vào · Bài học từ SU26
-  Mô hình dữ liệu
-  Ràng buộc cứng (H1 – H11)
-  Ràng buộc mềm và trọng số
Vì sao khớp Chủ tịch được ưu tiên · Ưu tiên phân bổ tải
-  Thuật toán
Pha 1: thành phần hội đồng · Pha 2: gán nhóm vào ghế · Vòng ghép cặp Review
-  Trần lý thuyết của ràng buộc liên tục
-  Kiểm tra tính khả thi trước khi chạy
-  Bộ kiểm tra kết quả
Kiểm thử công thức và kiểm thử phá hoại
-  Kết quả thực nghiệm đợt SU26
-  Gợi ý cho đội phát triển
Thuật toán xếp lịch Hội đồng Capstone Project  |  2

- Mục đích và phạm vi
Tài liệu mô tả đầy đủ bài toán và thuật toán xếp lịch hội đồng bảo vệ Capstone Project, đủ chi tiết để
đội phát triển hiện thực lại thành phần mềm mà không cần hỏi thêm về nghiệp vụ. Nội dung được
rút ra từ quy trình xếp lịch thủ công và bán tự động đã chạy thực tế trong học kỳ SU26 cho 74 nhóm
ngành Kỹ thuật phần mềm, qua năm vòng đánh giá.
Phạm vi bao gồm: mô hình dữ liệu, tập ràng buộc cứng và mềm, thuật toán hai pha, cách tính trần lý
thuyết, quy trình kiểm tra tính khả thi trước khi chạy và bộ kiểm tra kết quả sau khi chạy. Tài liệu
không quy định ngôn ngữ hay framework hiện thực.
1.1. Thuật ngữ
Thuật ngữÝ nghĩa
Nhóm (group)Một nhóm sinh viên làm một đề tài Capstone. Định danh bằng Mã đề tài (ví dụ
SU26SE094) và Mã nhóm (ví dụ GSU26SE01).
GVHDGiảng viên hướng dẫn của nhóm. Một nhóm có 1 hoặc 2 GVHD.
Vòng (round)Một đợt đánh giá: Review 1, Review 2, Hội đồng 1.1, Hội đồng 1.2, Hội đồng 2.
Hội đồng (council)Một tổ chấm gồm 5 vị trí: Chủ tịch, Thư ký và 3 Thành viên. Hội đồng ngồi cố định
một phòng, chấm nhiều nhóm liên tiếp trong ngày.
Ghế (seat)Một suất chấm = một cặp (hội đồng, khung giờ). Tổng số ghế phải bằng đúng tổng
số nhóm.
Cặp reviewerHai giảng viên chấm một nhóm ở vòng Review 1 và Review 2 (không lập hội đồng).
Tính liên tụcYêu cầu mỗi vòng phải có ít nhất một người đã chấm chính nhóm đó ở vòng liền
trước.
- Bối cảnh nghiệp vụ
2.1. Chuỗi năm vòng
Một học kỳ Capstone đi qua năm vòng theo thứ tự cố định. Mỗi vòng chỉ nhận những nhóm chưa
đạt ở vòng trước, nên số nhóm giảm dần:
Review 1  →  Review 2  →  Hội đồng 1.1  →  Hội đồng 1.2  →  Hội đồng 2
2 người     2 người       5 người          5 người         5 người
(toàn bộ)   (toàn bộ)     (toàn bộ)      (nhóm chưa đạt)  (nhóm chưa đạt)
Hai vòng Review đầu chỉ cần một cặp hai giảng viên đọc và góp ý, không lập hội đồng. Từ Hội đồng
1.1 trở đi mới thành lập hội đồng 5 người và chấm chính thức.
Nguyên tắc cốt lõi: Vòng sau tồn tại là vì vòng trước đánh rớt. Người đã chấm nhóm đó ở vòng trước
hiểu rõ nhóm cần sửa gì, nên phải có mặt ở vòng sau để đánh giá mức độ khắc phục. Đây là ràng buộc H5
và là ràng buộc khó thỏa mãn nhất của toàn bộ bài toán.
2.2. Hình thái từng vòng
VòngQuy mô hội
đồng
Cách xếpRàng buộc liên tục
Review 12 ngườiXếp mới hoàn toàn, cân bằng tảiKhông có (vòng đầu tiên)
Thuật toán xếp lịch Hội đồng Capstone Project  |  3

VòngQuy mô hội
đồng
Cách xếpRàng buộc liên tục
Review 22 ngườiCHÉP NGUYÊN cặp của Review 1; chỉ thay
người khi bị ràng buộc chặn
Giữ tối thiểu 1 người của
## Review 1
Hội đồng 1.15 ngườiLập hội đồng mớiTối thiểu 1 người đã dự
Review 2 của nhóm
Hội đồng 1.25 ngườiLập hội đồng mớiTối thiểu 1 người đã dự Hội
đồng 1.1 của nhóm
Hội đồng 25 ngườiLập hội đồng mớiTối thiểu 1 người đã dự vòng
liền trước; ƯU TIÊN CAO khớp
đúng Chủ tịch
2.3. Dữ liệu đầu vào cần thu thập mỗi đợt
Trước khi chạy thuật toán cho một vòng, phần mềm cần có đủ các nguồn dữ liệu sau. Mọi thứ trong
bảng đều thay đổi theo từng học kỳ, không được tái sử dụng dữ liệu kỳ trước.
Dữ liệuNội dungLưu ý
Danh sách nhóm của
vòng
Mã đề tài, mã nhóm, tên đề tài, GVHDPhải lấy từ danh sách CHÍNH THỨC
của đúng vòng đó — xem mục 2.4
Danh sách giảng viênMã, họ tên, bộ môn, cấp bậc, có thuộc nhóm
thư ký không
Cấp bậc: Senior / Middle / Junior
Lịch bậnMỗi giảng viên bận những buổi nào (sáng /
chiều / tối) của từng ngày
Khảo sát lại mỗi kỳ; xem mục 4,
ràng buộc H11
Kết quả vòng liền
trước
Thành phần hội đồng (hoặc cặp reviewer) của
## TỪNG NHÓM
Là đầu vào bắt buộc của ràng buộc
liên tục H5
Khung hội đồngSố ngày, số hội đồng mỗi ngày, khung giờ, sức
chứa, chủ tịch từng hội đồng
Do điều phối viên chốt trước, thuật
toán không tự sinh
Luật cặpCặp cấm ngồi chung, người bị cấm làm thư ký
cho chủ tịch nào
Mang tính tổ chức, cần xác nhận lại
mỗi kỳ
2.4. Bài học từ SU26: lấy sai danh sách nhóm
Trong đợt SU26, danh sách 50 nhóm cho Hội đồng 2 đã bị lấy nhầm từ một file lịch nháp thay vì từ
danh sách chính thức của vòng. Hậu quả: 17 nhóm đã bảo vệ xong Hội đồng 1.2 vẫn bị xếp lịch lần
nữa, trong khi 17 nhóm thật sự phải bảo vệ lại thì không có tên. Hai danh sách chỉ trùng nhau 33/50
nhóm nhưng số lượng đều bằng 50, nên lỗi không bị phát hiện bằng cách đếm.
Vì vậy phần mềm phải coi việc chốt danh sách nhóm là một bước nghiệp vụ riêng, có kiểm tra chéo
tự động:
•Danh sách vòng N phải là tập con của danh sách vòng N−1.
•Không nhóm nào trong danh sách vòng N được có kết quả "đạt" ở vòng N−1.
•Mọi nhóm trong danh sách vòng N phải có dữ liệu hội đồng của vòng N−1; thiếu là dấu hiệu lấy
nhầm nguồn.
•Đếm số nhóm trùng khớp giữa hai nguồn dữ liệu và cảnh báo nếu tỷ lệ dưới 100%, không chỉ so
tổng số.
Thuật toán xếp lịch Hội đồng Capstone Project  |  4

- Mô hình dữ liệu
Mô hình tối thiểu để chạy được cả năm vòng. Tên bảng và cột mang tính gợi ý.
Thực thểTrường chínhGhi chú
Termid, code, name, isActiveMột học kỳ, ví dụ SU26
Lecturerid, termId, code, fullName, dept, level,
inSecretaryPool, isChair, active
level   {senior, middle, junior}; code là ∈
mã viết tắt, ví dụ PhuongLHK
BusySlotid, termId, lecturerCode, date, session, notesession   {morning, afternoon, ∈
evening}; chỉ lưu buổi BẬN, mặc định là
rảnh
Projectid, termId, groupCode, topicCode, title,
supervisor1, supervisor2
supervisor lưu bằng mã giảng viên
Roundid, termId, kind, name, panelSize, solvedkind   {review1, review2, defense11, ∈
defense12, defense2}
Councilid, roundId, code, date, room, chairCode, slotsslots là danh sách khung giờ của hội
đồng trong ngày
CouncilSeatid, councilId, roleIndex, lecturerCode, pinnedroleIndex: 0 = Chủ tịch, 1 = Thư ký, 2–4
= Thành viên; pinned = ghế bị ghim tay
Assignmentid, roundId, groupCode, councilCode, date, slot,
room
Kết quả gán nhóm vào ghế
ReviewPairid, roundId, groupCode, reviewer1, reviewer2,
date, slot, room
Dùng cho Review 1 và Review 2
PairRuleid, termId, kind, chairCode, otherCodekind   {forbidden, secretaryBan}∈
SolverWeightid, termId, key, valueTrọng số mềm, cho phép chỉnh mà
không sửa code
Thiết kế quan trọng: Tầng solver phải thuần logic, không phụ thuộc database và không phụ thuộc giao
diện. Nhờ vậy toàn bộ phần khó nhất kiểm thử được bằng unit test với dữ liệu dựng sẵn, không cần mở
ứng dụng.
- Ràng buộc cứng
Ràng buộc cứng là điều kiện không được vi phạm. Trong thuật toán, phương án vi phạm bị loại bỏ
ngay chứ không bị trừ điểm — đây là khác biệt then chốt so với ràng buộc mềm ở mục 5.
MãNội dungKiểm tra như thế nào
H1GVHD không ngồi hội đồng chấm chính nhóm mìnhGiao của tập GVHD nhóm và tập 5 người
trong hội đồng phải rỗng
H2Một người không có mặt ở hai phòng trong cùng
khung giờ
Khóa (người, ngày, khung giờ) phải duy nhất
H3Năm vị trí trong một hội đồng là năm người khác
nhau
Số phần tử của tập 5 người phải bằng 5
H4Hội đồng ngồi xuyên suốt: một thành phần, một
phòng, cả ngày
Thành phần hội đồng không đổi giữa các
khung giờ trong ngày
Thuật toán xếp lịch Hội đồng Capstone Project  |  5

MãNội dungKiểm tra như thế nào
H5Mỗi nhóm phải có ≥1 người đã chấm chính nhóm đó
ở vòng liền trước
Giao của hội đồng vòng này và hội đồng
vòng trước của nhóm phải khác rỗng
H6Thư ký chỉ lấy từ nhóm được chỉ định, trừ người bị
chủ tịch loại
Kiểm tra secretaryPool và PairRule kind =
secretaryBan
H7Các cặp bị cấm không ngồi chung hội đồngPairRule kind = forbidden
H8Mỗi hội đồng có ít nhất một người cấp MiddleNgoài chủ tịch, trong 4 người còn lại phải có
≥1 người level = middle
H9Tối đa một nhóm cho mỗi GVHD trong cùng một hội
đồng
Đếm số nhóm theo GVHD trong từng hội
đồng
H10Số nhóm mỗi hội đồng đúng bằng sức chứa đã chốtTự thỏa mãn nếu pha 2 dùng hoán vị (xem
mục 6.2)
H11Chỉ xếp người vào hội đồng mà họ rảnh TOÀN BỘ
khung giờ của hội đồng đó
Với mọi khung giờ của hội đồng, người đó
phải rảnh
H11 chặt hơn vẻ ngoài: Vì hội đồng ngồi liên tục cả ngày trong một phòng, một giảng viên bận chỉ một
buổi sáng là bị loại khỏi hội đồng của NGUYÊN NGÀY đó, chứ không phải chỉ khung giờ bị trùng. Đây là
nguyên nhân phổ biến nhất khiến bài toán trở nên vô nghiệm mà người dùng không lường trước.
H1, H9 và H10 chỉ áp dụng cho các vòng có hội đồng. Với Review 1 và Review 2, ràng buộc thu gọn
còn: reviewer không phải GVHD của nhóm, reviewer còn hoạt động, và reviewer rảnh ở khung giờ
đó.
- Ràng buộc mềm và trọng số
Ràng buộc mềm được quy về điểm phạt; thuật toán tìm phương án có tổng điểm phạt nhỏ nhất. Các
giá trị dưới đây đã được hiệu chỉnh qua thực tế đợt SU26 và nên đưa vào cấu hình để điều chỉnh
không cần build lại.
KhóaGiá trịÝ nghĩa
noPreviousMember20 000Không có ai của vòng trước — coi như ràng buộc cứng
mềm hóa
supervisorOnPanel1 000GVHD lọt vào hội đồng chấm nhóm mình (lưới an toàn
cho H1)
matchedByMemberNotC
hair
800Có khớp nhưng không phải qua Chủ tịch
sameSupervisorInCou
ncil
60 × (n−1)²n nhóm cùng một GVHD trong một hội đồng; phạt lũy
tiến để ép dàn đều
changedDate6Lệch ngày so với bản nháp điều phối viên đưa
changedChair2Lệch chủ tịch so với bản nháp
changedSlot1Lệch khung giờ so với bản nháp
5.1. Vì sao khớp Chủ tịch được ưu tiên tuyệt đối
Ở Hội đồng 2, chỉ cần một người của vòng trước là đủ về mặt quy chế (H5). Nhưng trên thực tế,
người nắm rõ nhất nhóm đã bị đánh rớt vì lý do gì chính là Chủ tịch hội đồng vòng trước. Do đó tài
Thuật toán xếp lịch Hội đồng Capstone Project  |  6

liệu quy ước: khớp qua Chủ tịch không bị phạt, khớp qua Thư ký hoặc Thành viên bị phạt 800, không
khớp bị phạt 20 000.
Khoảng cách 800 so với 20 000 là cố ý: thuật toán sẽ hy sinh hàng chục lần "khớp đúng chủ tịch" để
tránh một trường hợp "không khớp ai", đúng thứ tự ưu tiên nghiệp vụ.
5.2. Ưu tiên phân bổ tải
•Nhóm giảng viên ưu tiên (thường là giảng viên cơ hữu của bộ môn chủ quản) được xếp các ghế
cả ngày, tải cao.
•Nhóm còn lại hấp thụ các ghế buổi tối, tải thấp hơn.
•Số lượt làm Thư ký giữa những người trong nhóm thư ký không được lệch nhau quá 1.
•Hạn chế lặp lại cùng một cặp người ngồi chung nhiều hội đồng; phạt 12 điểm cho mỗi lần lặp.
Thuật toán xếp lịch Hội đồng Capstone Project  |  7

- Thuật toán
Bài toán thuộc lớp tối ưu tổ hợp có ràng buộc. Cách tiếp cận đã kiểm chứng là tìm kiếm cục bộ hai
pha, tách biệt hai quyết định độc lập nhau: ai ngồi với ai, và nhóm nào vào ghế nào.
6.1. Pha 1 — Xác định thành phần hội đồng
Đầu vào: khung hội đồng (ngày, chủ tịch, sức chứa), kế hoạch ghế theo ngày, danh sách giảng viên,
lịch bận, luật cặp. Đầu ra: 4 thành viên cho mỗi hội đồng, sau đó chọn Thư ký.
cho mồ8i NGÀY:
chia những người có mặt trong ngày vào các hội đồng cu@a ngày đó
lặp lại R lần (R = 12), mồ8i lần:
khở@i tạo ngầ8u nhiên một phép chia
lặp I lần (I = 6000):
chọn ngầ8u nhiên 2 hội đồng cùng ngày, đồ@i chồ8 1 thành viên
nêJu điê@m khồng tệ hởn thì giữ, ngược lại hoàn tác
giữ phép chia tồJt nhầJt trong R lần
hàm tính điê@m một ngày:
nêJu vi phạm H3, H6, H7, H8, H11  →  tra@ vê ầm vồ cùng (loại ngay)
trừ điê@m cho mồ8i cặp người lặp lại nhiêu hội đồng
trừ điê@m cho GVHD xuầJt hiện ở@ hội đồng dự kiêJn chầJm nhóm cu@a họ
Chọn Thư ký được làm SAU khi thành phần đã chốt, bằng cách duyệt toàn bộ tổ hợp thư ký hợp lệ
của các hội đồng trong cùng một ngày và lấy tổ hợp cân bằng nhất theo tiêu chí tổng bình phương số
lượt đã làm thư ký. Số hội đồng mỗi ngày nhỏ (≤ 5) nên duyệt vét cạn là khả thi và cho kết quả cân
bằng tốt hơn heuristic tham lam.
6.2. Pha 2 — Gán nhóm vào ghế
Thành phần hội đồng đã cố định. Xây danh sách ghế phẳng, mỗi ghế là một cặp (hội đồng, khung
giờ), tổng số ghế bằng đúng số nhóm. Bài toán trở thành tìm một hoán vị của danh sách nhóm trên
danh sách ghế.
ghêJ  = [(hội đồng, khung giờ) cho mọi hội đồng, mọi khung giờ cu@a nó]
gán  = hoán vị ngầ8u nhiên cu@a danh sách nhóm  (hoặc khở@i tạo từ ba@n nháp)
lặp N lần (N = 120 000 ... 400 000):
chọn ngầ8u nhiên 2 vị trí i, j; đồ@i chồ8 gán[i] và gán[j]
nêJu chi_phí mới ≤ chi_phí cũ thì giữ, ngược lại hoàn tác
hàm chi_phí(gán):
s = 0
cho mồ8i (ghêJ, nhóm):
nêJu GVHD cu@a nhóm nằm trong hội đồng     → s += 10^6      (H1)
nêJu chu@ tịch vòng trước == chu@ tịch hiện tại → s += 0     (tồJt nhầJt)
ngược lại nêJu có người vòng trước trong hội đồng → s += 800
ngược lại                                 → s += 20 000   (H5)
cho mồ8i hội đồng, mồ8i GVHD có n nhóm trong đó:
nêJu n > 1 → s += 60 × (n−1)²                              (H9)
tra@ vê s
Vì sao dùng hoán vị: Biểu diễn bằng hoán vị làm cho H10 (số nhóm mỗi hội đồng đúng sức chứa) luôn
đúng theo cấu trúc, không cần kiểm tra lại và không cần sửa chữa phương án. Đây là lý do nên tách pha 2
khỏi pha 1 thay vì tối ưu đồng thời.
Thuật toán xếp lịch Hội đồng Capstone Project  |  8

6.3. Vòng ghép cặp Review 1 và Review 2
Review 1 xếp mới từ đầu: chọn cặp hai giảng viên cân bằng tải, không ai là GVHD của nhóm, cả hai
rảnh ở khung giờ đó.
Review 2 KHÔNG xếp lại. Mặc định là chép nguyên cặp của Review 1 sang; chỉ thay từng người khi
người đó bị chặn, và khi thay vẫn phải giữ lại người kia:
cho mồ8i nhóm:
cặp_mới = ba@n sao cu@a cặp Review 1
cho mồ8i người trong cặp:
lý_do = kiê@m tra chặn(người, nhóm, khung giờ)
- là GVHD cu@a chính nhóm này
- khồng còn là gia@ng viên đang hoạt động
- bận ở@ khung giờ này
nêJu bị chặn:
thay bằng người hợp lệ có ta@i thầJp nhầJt,
LOẠI TRỪ ca@ hai người cu@a cặp cũ  → đa@m ba@o giữ ≥1 người gồJc
ghi nhật ký thay đồ@i (nhóm, người bị thay, người thay, lý do)
Nhật ký thay đổi là đầu ra bắt buộc: điều phối viên cần biết chính xác cặp nào đã bị đổi và vì sao,
thay vì nhận một bảng phân công mới không giải thích.
- Trần lý thuyết của ràng buộc liên tục
Không phải lúc nào cũng giữ được 100% "chủ tịch cũ chấm lại". Số lượng tối đa có thể đạt được tính
trước bằng công thức, không cần chạy thuật toán:
với mồ8i chu@ tịch C:
đóng_góp(C) = min( sồJ nhóm C đã làm chu@ tịch ở@ vòng trước ,
sồJ ghêJ chu@ tịch cu@a C ở@ vòng này )
trần = tồ@ng đóng_góp(C) trên toàn bộ chu@ tịch
Ví dụ thực tế, Hội đồng 2 đợt SU26 với 50 nhóm và 13 hội đồng:
Chủ tịchSố nhóm đã chủ trì ở vòng 1.1Sức chứa ở Hội đồng 2Đóng góp vào trần
HuongNTC2111211
DucDNM2131212
TaiNT51131212
PhuongLHK131413
## Tổng505048
Trần là 48/50. Kết quả chạy thực tế đạt đúng 48 nhóm khớp Chủ tịch, 2 nhóm còn lại khớp qua
Thành viên, không nhóm nào mất tính liên tục.
Quy tắc dừng: Khi kết quả đã chạm trần, dừng lại. Tăng số vòng lặp hay đổi trọng số sẽ không cải thiện
được nữa vì giới hạn nằm ở cấu trúc bài toán, không nằm ở thuật toán. Phần mềm nên hiển thị "48/48
(đạt trần)" thay vì "48/50" để người dùng không hiểu nhầm là còn dư địa.
- Kiểm tra tính khả thi trước khi chạy
Nếu bài toán vô nghiệm, tìm kiếm cục bộ sẽ chạy hết số vòng lặp rồi trả về phương án vi phạm, chứ
không tự báo là vô nghiệm. Vì vậy phải chặn trước bằng phép đếm. Với mỗi ngày trong lịch:
•Đếm số người rảnh TOÀN BỘ các khung giờ của ngày đó. Phải ≥ số ghế cần lấp (số hội đồng × 4).
Thuật toán xếp lịch Hội đồng Capstone Project  |  9

•Trong số người rảnh, phải có đủ người thuộc nhóm thư ký cho mọi hội đồng trong ngày, sau khi
trừ những người bị chủ tịch tương ứng loại.
•Trong số người rảnh, phải có ít nhất một người cấp Middle cho mỗi hội đồng trong ngày.
•Tổng sức chứa của tất cả hội đồng phải bằng đúng tổng số nhóm — thừa ghế hoặc thiếu ghế
đều là lỗi cấu hình, không phải việc của thuật toán.
Mỗi điều kiện không thỏa phải sinh ra một thông báo nêu rõ ngày nào, thiếu bao nhiêu người, thiếu
loại nào. Giải pháp luôn nằm ở phía người dùng: bỏ bớt buổi bận, thêm giảng viên, hoặc giảm số hội
đồng trong ngày.
Ngoài ra, nếu thuật toán không tìm được phương án hợp lệ sau tất cả các lần khởi động lại, phải
ném lỗi kèm chẩn đoán (kiểm tra nhóm thư ký, cặp cấm, bảng bận/rảnh) thay vì trả về kết quả sai
hoặc chạy vô hạn.
Thuật toán xếp lịch Hội đồng Capstone Project  |  10

- Bộ kiểm tra kết quả
Chạy trên chính dữ liệu đã xuất ra, không chạy trên biến trong bộ nhớ — đây là cách duy nhất phát
hiện lỗi phát sinh ở khâu ghi file hoặc ghi database.
#Nội dung kiểm traKết quả mong đợi
1Số nhóm bằng đúng danh sách chính thức, không trùng, không
thiếu
Trùng khớp 100%
2Không nhóm nào đã hoàn thành ở vòng trước lọt vào danh sáchRỗng
3Mỗi hội đồng có đúng 5 người khác nhauKhông có lỗi
4Không ai xuất hiện ở hai phòng cùng khung giờRỗng
5Không GVHD nào ngồi chấm nhóm mìnhRỗng
6Thư ký đều thuộc nhóm chỉ định và không vi phạm lệnh cấmKhông có lỗi
7Không có cặp cấm nào ngồi chungRỗng
8Mỗi hội đồng có ≥1 người cấp MiddleKhông có lỗi
9Số nhóm mỗi hội đồng đúng sức chứaKhớp cấu hình
10Thống kê tính liên tục: khớp Chủ tịch / khớp Thành viên / không
khớp
Không khớp = 0; khớp Chủ tịch =
trần
11Số nhóm cùng một GVHD trong một hội đồng≤ 1, hoặc nêu rõ ngoại lệ đã chấp
nhận
12Số lượt làm thư ký giữa các thành viên nhóm thư kýLệch tối đa 1
9.1. Kiểm thử công thức và kiểm thử phá hoại
Nếu sản phẩm xuất file Excel có công thức kiểm tra, phải kiểm chứng rằng công thức thật sự hoạt
động chứ không chỉ hiện chữ "OK". Cách làm: nhân bản file kết quả, cố tình phá dữ liệu theo từng
kiểu lỗi, tính lại và xác nhận công thức bắt đúng loại lỗi tương ứng.
Phá dữ liệu như thế nàoCông thức phải báo
Đặt GVHD của một nhóm trùng với chủ tịch hội đồng của
nhóm đó
## TRÙNG GVHD
Xóa trống ô GVHD của một nhómThiếu GVHD
Đặt một thành viên trùng với chủ tịch trong cùng hội đồngTrùng GV trong HĐ
Bẫy khi xuất Excel bằng thư viện: File tạo bằng thư viện chỉ chứa chuỗi công thức mà không chứa giá trị
đã tính, nên khi mở lên các ô có thể trống. Cần bật cờ buộc tính lại toàn bộ khi mở file, đồng thời chạy file
qua một bộ chuyển đổi (ví dụ LibreOffice ở chế độ headless) để nạp sẵn giá trị mà vẫn giữ nguyên công
thức trong ô.
- Kết quả thực nghiệm đợt SU26
Số liệu dưới đây là của vòng Hội đồng 2, dùng làm mốc đối chiếu khi kiểm thử phần mềm.
Chỉ sốGiá trị
Số nhóm phải bảo vệ50
Thuật toán xếp lịch Hội đồng Capstone Project  |  11

Chỉ sốGiá trị
Số hội đồng13 (4 ngày)
Cấu trúc ngàyNgày 1: 4 hội đồng × 8 nhóm — Ngày 2 và 3: 4 hội đồng × 2 nhóm —
Ngày 4: 1 hội đồng × 2 nhóm
Khung giờ ngày 18 khung, từ 07:30 đến 20:00
Khung giờ buổi tối2 khung: 17:30–19:00 và 19:00–20:30
Số giảng viên tham gia23 (4 chủ tịch, 19 thành viên)
Khớp Chủ tịch vòng trước48/50 — đạt trần lý thuyết
Khớp qua Thành viên2/50
Mất tính liên tục0
GVHD chấm nhóm mình0
Trùng lịch trong cùng khung giờ0
Hội đồng có 2 nhóm cùng GVHD1 (ngoại lệ được chấp nhận, xem mục 10.1)
10.1. Đánh đổi đã ghi nhận
Siết tuyệt đối H9 (mỗi GVHD tối đa một nhóm trong một hội đồng) làm số nhóm khớp Chủ tịch tụt từ
48 xuống 46. Quyết định nghiệp vụ: giữ 48 và chấp nhận một hội đồng có hai nhóm cùng GVHD, vì
tính liên tục qua Chủ tịch được ưu tiên cao hơn việc dàn đều GVHD.
Phần mềm nên cho phép người dùng chọn giữa hai chế độ này và hiển thị rõ cái giá của mỗi lựa
chọn, thay vì cứng hóa một phương án trong code.
- Gợi ý cho đội phát triển
11.1. Thứ tự hiện thực
•Tầng mô hình và bộ kiểm tra (mục 3, 4, 9) — làm trước, vì đây là thứ định nghĩa "đúng".
•Hàm tính trần lý thuyết và hàm kiểm tra khả thi (mục 7, 8) — rẻ, chạy nhanh, chặn phần lớn lỗi
dữ liệu.
•Pha 2 trước pha 1: với thành phần hội đồng dựng tay, pha 2 đã cho ra kết quả dùng được ngay.
•Pha 1 sau cùng, khi bộ kiểm tra đã đủ mạnh để phát hiện phương án sai.
•Giao diện và nhập/xuất Excel làm sau khi lõi đã có unit test xanh.
11.2. Những điểm dễ làm sai
•Kiểm tra rảnh theo từng khung giờ thay vì theo toàn bộ ngày (vi phạm H11 một cách âm thầm).
•Đếm số nhóm để xác nhận danh sách đúng, thay vì so khớp từng mã đề tài.
•Phạt điểm ràng buộc cứng thay vì loại bỏ phương án, khiến kết quả cuối vẫn vi phạm.
•Xếp lại Review 2 từ đầu thay vì chép từ Review 1.
•Tăng vòng lặp khi đã chạm trần lý thuyết.
•So khớp giảng viên bằng tên tiếng Việt có dấu; luôn dùng mã viết tắt làm khóa.
11.3. Danh mục cần xác nhận lại mỗi học kỳ
Không tái sử dụng dữ liệu kỳ trước cho các mục sau:
Thuật toán xếp lịch Hội đồng Capstone Project  |  12

Hạng mụcVì sao thay đổi
Danh sách giảng viên và cấp bậcNhân sự vào/ra, thăng cấp
Lịch bận theo buổi của từng giảng viênThay đổi hoàn toàn theo thời khóa biểu từng kỳ
Nhóm thư ký và lệnh cấm thư kýPhụ thuộc phân công của bộ môn
Cặp cấm ngồi chungPhụ thuộc quan hệ hướng dẫn và tổ chức trong kỳ
Khung hội đồng: số ngày, số hội đồng,
khung giờ, phòng
Do phòng đào tạo bố trí
Danh sách nhóm của từng vòngPhụ thuộc kết quả vòng trước
Trọng số mềmCó thể chỉnh theo ưu tiên của điều phối viên từng kỳ
Hết tài liệu. Mọi số liệu thực nghiệm trong tài liệu lấy từ vòng Hội đồng 2 học kỳ SU26, ngành Kỹ thuật phần mềm.
Thuật toán xếp lịch Hội đồng Capstone Project  |  13