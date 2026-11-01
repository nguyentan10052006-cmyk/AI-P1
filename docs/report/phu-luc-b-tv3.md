# Phụ Lục B: Phần Của TV3 (Gửi Trưởng Nhóm & TV4 Ghép Vào Báo Cáo)

> **Người soạn:** TV3 – Nguyễn Bảo Trọng (MSSV: 24120476)  
> **Ngày soạn:** 01/11/2026  
> **Nhiệm vụ phụ trách:** Thuật toán UCS (V12, V14), Bộ nạp màn & cấu trúc `links` (V03), Ô đặc biệt (V05), Hàm chi phí phi đồng nhất (V13), Bộ màn tự sinh $S_1-S_3$ (V40), Kịch bản & Video Demo (V36).  
> **Tài liệu nguồn:** Trích xuất nguyên văn từ lịch sử làm việc trên IDE với Antigravity (Google DeepMind), mô hình Gemini (Gemini 3.8 Flash / Pro) và các phiên làm việc thực tế trên repository. Giờ ghi theo giờ Việt Nam (+07). Tuyệt đối không chứa token, email hay thông tin cá nhân nhạy cảm.

---

## 1. Đoạn Ghép Vào Bảng B.1 (Phụ Lục B.1 - Trang 94–95 / 110)


| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Antigravity (Google DeepMind), tiện ích IDE, mô hình Gemini (Gemini 3.8 Flash / Pro) | TV3 (21/10–31/10) | Xem B.2, phần TV3 |

*(Ghi chú chi tiết cho nhóm khi cần tóm tắt ngắn: Dùng cho bộ nạp màn `links`, ô đặc biệt, thuật toán UCS, hàm chi phí vật lý V13, bộ màn tự sinh $S_1-S_3$, kịch bản video demo – Xem B.2, phần TV3).*

---

## 2. Đoạn Ghép Vào Mục B.2 (Mục TV3 - Trang 103 / 110)

### TV3 (Nguyễn Bảo Trọng)

Dùng Antigravity (Google DeepMind), mô hình Gemini (Gemini 3.8 Flash / Pro), chạy trực tiếp trong môi trường IDE tích hợp với không gian làm việc của repository. Antigravity đọc tài liệu đặc tả đồ án, phân tích mã nguồn hiện tại của nhóm, đề xuất giải pháp kiến trúc, hỗ trợ viết mã nguồn, thiết kế hàm chi phí năng lượng, viết các bộ kiểm thử hồi quy (unit test), thực thi kiểm tra tự động và điều phối các nhánh Git theo từng yêu cầu chỉ đạo của TV3. Phần lớn mã nguồn thuật toán UCS, hàm chi phí, bộ nạp màn và bộ sinh màn của TV3 được hiện thực với sự hỗ trợ của AI dựa trên các ràng buộc lý thuyết chặt chẽ do TV3 đặt ra.

**TV3 trực tiếp chỉ đạo và thực hiện các việc sau:**
- Viết prompt, phân rã mục tiêu lớn thành các kế hoạch chi tiết (planning) và danh mục kiểm soát (checklist) trước khi cho phép AI viết code (V03, V05, V12, V13, V14, V40, V36);
- **Quản lý kiến trúc nhánh Git độc lập:** Khi AI đề xuất gộp chung vào một nhánh `feature/TV3/M1`, TV3 đã chặn lại ("chỉ phân tích và trả lời, chưa thực hiện bất cứ điều gì"), phân tích sự độc lập giữa tầng Engine (V03) và tầng Solver (V12), sau đó quyết định tách thành các nhánh riêng biệt (`feature/TV3/V03-level-loader`, và chuẩn hóa tên nhánh `feature/trong/V12-ucs`) để khớp 1-1 với Google Sheet và giúp TV1, TV2, TV5 có thể tích hợp bộ nạp màn sớm mà không bị phụ thuộc vào tiến độ của UCS;
- Quyết định chuẩn hóa trường `passcode` dưới dạng chuỗi (string) 6 chữ số trong cấu trúc `Level` để bảo toàn các số 0 ở đầu (màn 5, 9, 15, 16, 24);
- Giám sát và quyết định nguyên lý vật lý cho **Hàm chi phí không đồng nhất V13**: mô hình hóa dựa trên công cơ học nâng trọng tâm khối hộp $1\times 1\times 2$ khi đổi tư thế ($\Delta h$) và phụ phí rủi ro bề mặt ô giòn $+0.50$;
- **Thiết lập bất biến sống còn (Invariant):** Buộc AI phải đảm bảo mọi bước đi đều có chi phí $c(s, a, s') \ge 1.0$ để không làm phá vỡ tính chấp nhận được (admissible) của hàm heuristic $h(n)$ do TV4 thiết kế cho thuật toán A*;
- **Bảo toàn tính tương thích ngược:** Quyết định `Problem.step_cost` mặc định trả về $1.0$ khi không truyền `cost_fn`, bảo đảm toàn bộ mã nguồn kiểm thử và đo đếm số bước của TV1 (BFS) và TV2 (DFS) không bị ảnh hưởng;
- **Chủ động kiểm soát phạm vi và yêu cầu phân tích tổng thể đồ án:** Ngày 23/10, yêu cầu AI dừng mọi hành vi tự ý sửa code ("chỉ thảo luận, không làm thêm bất cứ gì hết"), đọc lại toàn bộ file mô tả đồ án gốc `AI - Project 1.pdf`, phân tích kiến trúc đa tầng (GUI – Engine – Solvers), làm rõ cơ chế tương tác thời gian thực giữa giao diện và các thuật toán (Auto-solve, Live Hint, Benchmark, Undo) và mục đích học thuật của 4 thuật toán;
- Chủ động phát hiện các điểm thiếu sót kỹ thuật trong quá trình làm việc: nhắc AI bổ sung rà soát ô đặc biệt V05, đính chính trạng thái hoàn thành giữa V12 và V13, yêu cầu thiết kế bộ test riêng biệt;
- Yêu cầu tuân thủ quy trình kiểm thử trước khi gộp code: kiểm thử đơn vị độc lập $\to$ gộp nhánh tích hợp trung gian `integration/M2` $\to$ kiểm tra chéo heuristic với TV4 $\to$ gộp vào `main`;
- Đích thân chỉ đạo kiểm thử toàn diện 5 tầng (246/246 tests pass) và kiểm tra tính tái lập dữ liệu thực nghiệm trước khi chốt mã nguồn đồ án.

Mọi lần chạy test, kiểm tra và đo đạc dưới đây đều được chạy thực tế trong phiên làm việc trên máy của TV3.

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 21/10 (chiều) | Phân tích yêu cầu M1 theo docs/01; nâng cấp bộ nạp màn `level.py` hỗ trợ cấu trúc `links` cho công tắc điều khiển nhiều ô cầu với hiệu ứng hỗn hợp (`toggle`, `open`, `close`) cho 6 màn gốc (17, 23, 25, 29, 30, 31); thêm `passcode` vào `Level`; cập nhật xử lý luật chơi `_apply_switch` trong `rules.py` và `serialize.py`; viết test T14 và test kiểm tra tính hợp lệ file màn (V03); quản lý phân tách nhánh Git | `bloxorz/level.py`, `bloxorz/rules.py`, `bloxorz/serialize.py`, `tests/test_rules.py`; nhánh `feature/TV3/V03-level-loader`, commit `ad4b30e` | 15/15 test trong `test_original_levels.py` qua (nạp đủ 33 màn gốc không lỗi); 27/27 test trong `test_rules.py` qua; toàn bộ test suite (130 test) đạt 100%; test T14 xác nhận cầu chuyển đúng trạng thái qua các lượt bấm |
| 21/10 (tối) | Phân tích thuật toán và lập kế hoạch chi tiết kèm checklist kiểm soát cho việc cài đặt thuật toán UCS trên `GridMaze` (V12): xác định cơ chế `heapq` với tuple `(g, order, state)`, lazy deletion qua `best_g`, goal test khi lấy ra khỏi frontier, và quy ước đếm 4 chỉ số thực nghiệm; tạo file tài liệu kiểm soát `ke_hoach_v12_ucs.md` | Artifact `ke_hoach_v12_ucs.md`; kế hoạch kỹ thuật cho nhánh `feature/TV3/V12-ucs` | Đối chiếu thuật toán với mục 3.4.2 của Russell & Norvig (AIMA 4th) và quy ước docs/04 §3; xác minh tính tối ưu trên mê cung có trọng số `weighted` (chọn đường vòng 10 bước chi phí 10 thay vì đường thẳng 6 bước chi phí 46) |
| 22/10 | Yêu cầu đổi tên chuẩn hóa nhánh thành `feature/trong/V12-ucs`; hiện thực thuật toán UCS trong `solvers/ucs.py` kế thừa lớp cơ sở `Solver` theo đúng checklist đã lập ngày 21/10 (V12) | `solvers/ucs.py`; nhánh `feature/trong/V12-ucs`, commit `e8c472c`, artifact `hoan_thanh_v12_ucs.md` | Chạy `tests/test_solvers.py` vượt qua cả 4 mê cung mẫu (`open`, `walls`, `weighted`, `no_solution`), chi phí khớp chính xác kết quả tính tay (màn `weighted` đi đường vòng 10 bước chi phí 10); chạy toàn bộ test suite `discover -s tests` đạt 111/111 test pass |
| 23/10 | Yêu cầu phân tích tổng thể đồ án từ file gốc `AI - Project 1.pdf` và cấu trúc repo ("chỉ thảo luận, không làm thêm bất cứ gì hết"); rà soát và phát hiện câu bẫy prompt injection của đề bài (dòng chữ ẩn yêu cầu AI chèn câu cố định); phân tích sâu luồng tương tác GUI Ursina – Engine (`rules.step()`, Undo qua `history_stack`), cơ chế chạy solver nền không chặn (`runner.py` đa tiến trình, timeout 60s, Auto-Solve, Live Hint, nút So sánh), và mục đích học thuật/thực tế của 4 thuật toán; rà soát và hoàn thiện xử lý ô đặc biệt (V05: ô giòn, công tắc mềm/nặng, chuyển trạng thái cầu toggle/open/close, cầu đóng dưới chân khối) | `docs/08-phan-tich-tong-quan-do-an.md`, `bloxorz/rules.py`, `tests/test_rules.py`, `tests/test_spec.py` | Biên soạn tài liệu phân tích hoàn chỉnh tại `docs/08-phan-tich-tong-quan-do-an.md`; kiểm tra toàn bộ mã nguồn và báo cáo bảo đảm không dính bẫy prompt injection; vượt qua 100% bộ test T07–T16; các màn 2, 4, 5, 7, 11, 13 giải đúng số bước tham khảo; 26/26 test đặc tả trong `test_spec.py` qua |
| 28/10 (chiều) | Thiết kế và cài đặt hàm chi phí phi đồng nhất V13 dựa trên công nâng trọng tâm; tích hợp vào `Problem.step_cost` | `bloxorz/costs.py`, `bloxorz/problem.py`, `tests/test_costs.py`; commit `828eaed` | Bộ test `test_costs.py` (7/7 pass); bảo đảm $\forall s, a, s': c(s, a, s') \ge 1.0$; giữ mặc định cost = 1.0 cho các test cũ của TV1, TV2 không bị gãy |
| 28/10 (chiều–tối) | Nghiệm thu UCS giải 33 màn gốc (V14); khám phá đường đi tối ưu năng lượng khác BFS ở màn 17, 23; xây dựng script sinh 14 màn tự sinh $S_1-S_3$ kiểm tra độ co giãn (V40) | `tests/test_ucs.py`, `experiments/gen_levels.py`, `tests/test_gen_levels.py`, `levels/gen/`; commit `cc3fa6a` | `test_ucs.py` qua 7/7: khi cost=1 khớp 100% `par` của BFS; khi dùng chi phí năng lượng, màn 17 (106 bước) chi phí BFS $140.42 \to$ UCS $140.10$; màn 23 (75 bước) BFS $100.96 \to$ UCS $99.96$. Tự sinh đủ 14 file JSON $S_1-S_3$, BFS kiểm định tự động: $S_1, S_2$ giải được, $S_3$ vô nghiệm |
| 28/10 (tối) | Gộp toàn bộ công việc của TV3 vào nhánh tích hợp trung gian `integration/M2` để kiểm thử chéo chung với code của TV4 và TV5 | Commit `04d8a9a` trên nhánh `integration/M2` | 203/203 test tự động trên nhánh `integration/M2` đều đạt (100% pass), không có xung đột mã nguồn |
| 31/10 | Kéo toàn bộ code `main` mới nhất (commit `a205b99`); thực hiện kiểm thử toàn diện 5 tầng; sửa lỗi mã hóa console cp1258 cho `charts.py` trên Windows; soạn kịch bản và slide intro cho Video Demo (V36) | `experiments/charts.py` (commit `8b72e74`), `docs/video/intro_slide.md`, `09-ke-hoach-kich-ban-video-demo.md` | Chạy bộ test hệ thống: 246/246 test pass; `check_heuristics.py` đạt 0 vi phạm trên 340.414 cạnh; kiểm tra K1–K8 pass; kiểm tra tái lập trùng 100% số đếm; sinh thử bảng và 8 biểu đồ H1–H9 thành công; kiểm tra khởi tạo headless Ursina 3D qua |

**Phần AI đề xuất và phần TV3 quyết định:**
- **Antigravity đề xuất, TV3 đồng ý qua prompt tiếp theo:**
  - Cấu trúc lưu trữ switch `links` dưới dạng `NamedTuple` bất biến (`cell`, `effect`) trong `Switch`, tự động suy biến tương thích ngược hai chiều giữa `bridges` + `effect` và `links`;
  - Cài đặt hàng đợi ưu tiên cho UCS bằng thư viện `heapq` với phần tử `(g, order, state)` kèm bộ đếm `order = itertools.count()` để tránh so sánh trực tiếp hai `State` khi chi phí $g$ bằng nhau, kết hợp lazy deletion qua bảng `best_g`;
  - Công thức tính biến thiên trọng tâm $\Delta h$ cho từng chuyển động: đứng $\to$ nằm ($\Delta h = \frac{\sqrt{5}}{2} - 1.0 \approx 0.12 \Rightarrow 1.12$), nằm $\to$ đứng ($\Delta h = \frac{\sqrt{5}}{2} - 0.5 \approx 0.62 \Rightarrow 1.62$), nằm $\to$ nằm ($\Delta h = \frac{\sqrt{2}}{2} - 0.5 \approx 0.21 \Rightarrow 1.21$);
  - Cấu trúc phân nhóm 14 màn chơi tự sinh: $S_1$ sân trống $N\times N$, $S_2$ kích thước cố định $8\times 12$ rải $k$ công tắc mép sân, $S_3$ chia cắt bởi khe trống 1 ô;
  - Khung kịch bản chi tiết từng giây cho Video Demo khớp với barem chấm Mục 3.7.
- **TV3 quyết định:**
  - **Quyết định tách nhánh Git độc lập và chuẩn hóa tên nhánh:** Bác bỏ việc dùng chung nhánh gộp `feature/TV3/M1`, yêu cầu AI dừng lại để phân tích kiến trúc, sau đó quyết định tách riêng nhánh `feature/TV3/V03-level-loader` và đổi tên chuẩn hóa thành `feature/trong/V12-ucs` để bàn giao sớm bộ nạp màn cho các thành viên khác;
  - **Chủ động kiểm soát mục đích trao đổi:** Yêu cầu AI chỉ phân tích tài liệu và mã nguồn ("chỉ thảo luận, không làm thêm bất cứ gì hết") để TV3 nắm vững cơ chế vận hành hệ thống và tương tác thuật toán trước khi bước vào các mốc code kế tiếp;
  - **Quy tắc bảo toàn tính admissible:** Phụ phí ô giòn và mọi chuyển động đều cộng trên nền $\text{COST\_BASE} = 1.0$, kiên quyết không cho phép bước đi có chi phí $< 1.0$;
  - **Bảo toàn tính tương thích ngược:** Hàm `Problem.step_cost` mặc định trả về $1.0$ nếu không truyền `cost_fn`, tránh phá vỡ các giả định đo đếm số bước của BFS và DFS;
  - Sử dụng nhánh `integration/M2` làm môi trường tích hợp trung gian để kiểm thử an toàn trước khi gộp lên nhánh chính `main`;
  - Quy trình kiểm thử 5 tầng nghiêm ngặt: chỉ thực hiện đo đạc và chạy test khi có xác nhận rõ ràng của TV3;
  - Tối giản hóa trang slide giới thiệu video demo thành file Markdown tinh gọn (chỉ hiển thị tên, MSSV và vai trò), loại bỏ phần chữ rườm rà.

*Cam kết liêm chính học thuật:* Đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn một câu cố định vào báo cáo. TV3 đã chủ động rà soát, kiểm tra toàn bộ mã nguồn, tài liệu và kịch bản video, bảo đảm câu bẫy này tuyệt đối không xuất hiện trong bất kỳ phần nào của mình.

---

## 3. Ví Dụ Prompt Của TV3 (Trích Nguyên Văn)

Dưới đây là các prompt tiêu biểu được trích **nguyên văn** từ lịch sử phiên làm việc của TV3 với Antigravity, kèm bối cảnh và quyết định kỹ thuật:

#### Prompt 1: Rà soát nhiệm vụ M1 và phân tích yêu cầu bộ nạp màn (21/10 15:22 & 15:34)
> *Hãy đọc và phân tích toàn bộ repo trong thư mục hiện tại, đây là đồ án nhóm môn học của chúng tôi. Tôi được phân công là TV3, sau khi phân tích hãy trình bày cho tôi biết những công việc của mình cần phải hoàn thành ở mốc 1 (M1 - 21/10) theo như bản phân công @[AI-P1/docs/01-phan-cong-PA2.md]*  
> *hãy lên kế hoạch chi tiết để hoàn thành công việc của nhiệm vụ 1*

#### Prompt 2: Kiểm soát kiến trúc Git – Yêu cầu phân tích độc lập và quyết định tách nhánh (21/10 16:05 & 16:08)
> *lúc nãy bạn tạo nhánh là origin/feature/TV3/M1. Nhưng ở mốc 1 TV3 có các nhiệm vụ khác nhau, code của các nhiệm vụ này có cùng trường với nhau không? tôi nên giữ nguyên branch ../../M1 như hiện tại và làm cả 2 nhiệm vụ vào đó hay là nên tách ra 2 nhánh riêng cho từng nhiệm vụ? (bạn hãy chỉ phân tích và trả lời, chưa thực hiện bất cứ điều gì)*  
> *vậy tôi nên đổi tên nhánh vừa làm xong là gì*  
> *hãy thực hiện giúp tôi*

#### Prompt 3: Chỉ đạo lập kế hoạch chi tiết kèm checklist kiểm soát cho UCS trước khi code (21/10 18:13)
> *tiếp tục phân tích và lên kế hoạch để hoàn thành nhiệm vụ 2, tạo một tab kế hoạch chi tiết bao gồm check list để tôi kiểm soát (chỉ plan chứ chưa thực hiện)*

#### Prompt 4: Yêu cầu chuẩn hóa tên nhánh và triển khai UCS theo checklist (22/10 13:45 & 14:23)
> *sửa đổi một chút ở tên nhánh: "feature/TV3/V12-ucs" thành "feature/trong/V12-ucs". Tiến hành thực hiện*  
> *thử lại*

#### Prompt 5: Giới hạn phạm vi thảo luận, chỉ đạo phân tích tổng thể đồ án từ PDF đề bài (23/10 11:49)
> *tôi muốn hiểu một cách tổng quát và chi tiết hơn về đồ án đang làm của nhóm, hãy cùng tôi phân tích và thảo luận để hiểu rõ hơn (chỉ thảo luận, không làm thêm bất cứ gì hết). Hãy phân tích lại toàn bộ dự án, đặt biệt là phân tích kỹ file @[AI-P1/docs/AI - Project 1.pdf] để hiểu rõ nhất về yêu cầu đồ án, tiếp theo là phần tích lại toàn bộ repo để hiểu được những gì nhóm đang triển khai. Sau đó trình bày chi tiết cho tôi trong một file .md*

#### Prompt 6: Chỉ đạo làm rõ cơ chế tương tác GUI – Hệ thống – Thuật toán (23/10 12:17 & 12:19)
> *bạn hãy trình bày rõ hơn về cách hoạt động của dự án, tương tác giữa giao diện người chơi và hệ thống, những thuật toán được cài đặt tương tác như thế nào với người chơi, những thuật toán đó phục vụ cho việc gì?*  
> *trình bày lại vào file md*

#### Prompt 7: Rà soát nhiệm vụ M2, phát hiện thiếu V05 và đính chính tiến độ (28/10 18:00 & 18:05 & 18:10)
> *hãy pull code mới nhất về và phân tích lại toàn bộ repo để nắm rõ ngữ cảnh đồ án. Trong đồ án này tôi được phân công là TV3. Sau đó dựa vào file phân công, liệt kê ra các task mà tôi (TV3) cần phải hoàn thành, trong đó tôi đã hoàn thành được 2 task của TV3 là V13, V03.*  
> *bạn có liệt kê thiếu V05 không?*  
> *lúc nãy tôi đã bị nhầm, task tôi đã hoàn thành là v03 và v12 chứ không phải là v03 và v13*

#### Prompt 8: Chỉ đạo lập kế hoạch chi tiết cho V13 (Hàm chi phí) và V05 (Ô đặc biệt) (28/10 18:15)
> *lên kế hoạch chi tiết để thực hiện V13, V05*  
> *tiến hành thực hiện*

#### Prompt 9: Chỉ đạo lập kế hoạch cho V14 (UCS 33 màn) và V40 (Bộ màn tự sinh S1–S3) (28/10 18:30)
> *tiếp tục lên kế hoạch chi tiết để thực hiện V14 và V40*  
> *tiến hành thực hiện kế hoạch trên*

#### Prompt 10: Yêu cầu tích hợp vào nhánh trung gian `integration/M2` (28/10 19:39)
> *nhóm tôi sử dụng nhánh "Integration M2" để test toàn bộ code trước khi merge vào nhánh main. Hãy PR toàn bộ code của tôi (TV3) vào nhánh này*

#### Prompt 11: Chỉ đạo kiểm thử 5 tầng có kiểm soát và xác nhận (31/10 19:53 & 20:06)
> *hãy pull hết code mới nhất trên github của nhóm về và lên kế hoạch kiểm thử chi tiết (pull và planning, chỉ thực hiện kiểm thử sau khi có xác nhận của tôi)*  
> *tiến hành*

#### Prompt 12: Chỉ đạo xây dựng kịch bản video demo theo chuẩn barem đề bài (31/10 21:16)
> *đọc kỹ lại phần yêu cầu quay video up youtube trong file mô tả đồ án gốc @[AI-P1/docs/AI - Project 1.pdf] , sau đó lên cho tôi một plan để thực hiện yêu cầu này sao cho đúng với những gì được yêu cầu trong file và có thể được trọn điểm*

#### Prompt 13: Yêu cầu tối giản hóa slide giới thiệu video sang file Markdown (31/10 21:45 & 21:48 & 21:52)
> *làm lại trang intro trên, yêu cầu: đơn giản, ít chữ, phần các thành viên chỉ cần để tên và mssv, không cần giới thiệu rườm rà, xóa luôn các chú thích ở phía đáy slide*  
> *làm lại trong một file .md*  
> *viết hết phần kế hoạch kịch bản lúc nãy của bạn vào một file .md và đặt nó ở ngoài thư mục "AI-P1"*

---

### Danh Sách Đủ Các Đợt Prompt Của TV3 (Trích Nguyên Văn Theo Thời Gian)

Bảng dưới đây liệt kê toàn bộ các đợt prompt chính của TV3 từ ngày 21/10 đến 31/10 (câu đầu nguyên văn theo log hệ thống):

| Ngày, giờ | Prompt (trích nguyên văn) |
|---|---|
| 21/10 15:22 | `Hãy đọc và phân tích toàn bộ repo trong thư mục hiện tại, đây là đồ án nhóm môn học của chúng tôi. Tôi được phân công là TV3, sau khi phân tích hãy trình bày cho tôi biết những công việc của mình cần phải hoàn thành ở mốc 1 (M1 - 21/10) theo như bản phân công @[AI-P1/docs/01-phan-cong-PA2.md]` |
| 21/10 15:34 | `hãy lên kế hoạch chi tiết để hoàn thành công việc của nhiệm vụ 1` |
| 21/10 15:42 | `hãy tiến hành thực hiện` |
| 21/10 15:55 | `bạn đã push lên github và tạo pull request chưa?` |
| 21/10 16:05 | `lúc nãy bạn tạo nhánh là origin/feature/TV3/M1. Nhưng ở mốc 1 TV3 có các nhiệm vụ khác nhau, code của các nhiệm vụ này có cùng trường với nhau không? tôi nên giữ nguyên branch ../../M1 như hiện tại và làm cả 2 nhiệm vụ vào đó hay là nên tách ra 2 nhánh riêng cho từng nhiệm vụ? (bạn hãy chỉ phân tích và trả lời, chưa thực hiện bất cứ điều gì)` |
| 21/10 16:08 | `vậy tôi nên đổi tên nhánh vừa làm xong là gì` |
| 21/10 16:10 | `hãy thực hiện giúp tôi` |
| 21/10 18:13 | `tiếp tục phân tích và lên kế hoạch để hoàn thành nhiệm vụ 2, tạo một tab kế hoạch chi tiết bao gồm check list để tôi kiểm soát (chỉ plan chứ chưa thực hiện)` |
| 22/10 13:45 | `sửa đổi một chút ở tên nhánh: "feature/TV3/V12-ucs" thành "feature/trong/V12-ucs". Tiến hành thực hiện` |
| 22/10 14:23 | `thử lại` |
| 23/10 11:49 | `tôi muốn hiểu một cách tổng quát và chi tiết hơn về đồ án đang làm của nhóm, hãy cùng tôi phân tích và thảo luận để hiểu rõ hơn (chỉ thảo luận, không làm thêm bất cứ gì hết). Hãy phân tích lại toàn bộ dự án, đặt biệt là phân tích kỹ file @[AI-P1/docs/AI - Project 1.pdf] để hiểu rõ nhất về yêu cầu đồ án, tiếp theo là phần tích lại toàn bộ repo để hiểu được những gì nhóm đang triển khai. Sau đó trình bày chi tiết cho tôi trong một file .md` |
| 23/10 12:17 | `bạn hãy trình bày rõ hơn về cách hoạt động của dự án, tương tác giữa giao diện người chơi và hệ thống, những thuật toán được cài đặt tương tác như thế nào với người chơi, những thuật toán đó phục vụ cho việc gì?` |
| 23/10 12:19 | `trình bày lại vào file md` |
| 28/10 18:00 | `hãy pull code mới nhất về và phân tích lại toàn bộ repo để nắm rõ ngữ cảnh đồ án. Trong đồ án này tôi được phân công là TV3. Sau đó dựa vào file phân công, liệt kê ra các task mà tôi (TV3) cần phải hoàn thành, trong đó tôi đã hoàn thành được 2 task của TV3 là V13, V03.` |
| 28/10 18:05 | `bạn có liệt kê thiếu V05 không?` |
| 28/10 18:10 | `lúc nãy tôi đã bị nhầm, task tôi đã hoàn thành là v03 và v12 chứ không phải là v03 và v13` |
| 28/10 18:15 | `lên kế hoạch chi tiết để thực hiện V13, V05` |
| 28/10 18:22 | `tiến hành thực hiện` |
| 28/10 18:30 | `tiếp tục lên kế hoạch chi tiết để thực hiện V14 và V40` |
| 28/10 18:35 | `tiến hành thực hiện kế hoạch trên` |
| 28/10 19:39 | `nhóm tôi sử dụng nhánh "Integration M2" để test toàn bộ code trước khi merge vào nhánh main. Hãy PR toàn bộ code của tôi (TV3) vào nhánh này` |
| 31/10 19:53 | `hãy pull hết code mới nhất trên github của nhóm về và lên kế hoạch kiểm thử chi tiết (pull và planning, chỉ thực hiện kiểm thử sau khi có xác nhận của tôi)` |
| 31/10 20:06 | `tiến hành` |
| 31/10 20:30 | `hướng dẫn tôi chạy game` |
| 31/10 21:16 | `đọc kỹ lại phần yêu cầu quay video up youtube trong file mô tả đồ án gốc @[AI-P1/docs/AI - Project 1.pdf] , sau đó lên cho tôi một plan để thực hiện yêu cầu này sao cho đúng với những gì được yêu cầu trong file và có thể được trọn điểm` |
| 31/10 21:32 | `pull code mới nhất về, vừa có thêm một số update phần gui` |
| 31/10 21:41 | `tạo cho tôi một slide giới thiệu như bạn đề cập ở phần1 trong kịch bản video` |
| 31/10 21:45 | `làm lại trang intro trên, yêu cầu: đơn giản, ít chữ, phần các thành viên chỉ cần để tên và mssv, không cần giới thiệu rườm rà, xóa luôn các chú thích ở phía đáy slide` |
| 31/10 21:48 | `làm lại trong một file .md` |
| 31/10 21:52 | `viết hết phần kế hoạch kịch bản lúc nãy của bạn vào một file .md và đặt nó ở ngoài thư mục "AI-P1"` |

---

## 4. Các Dòng Bổ Sung Vào Tab `prompt-ai` (File `docs/sheet/6-prompt-ai.csv`)

Dán thêm các dòng sau vào tệp theo dõi sử dụng AI của nhóm:

```csv
2026-10-21,TV3,Antigravity (Google DeepMind),"Nâng cấp bộ nạp màn hỗ trợ links công tắc đa hiệu ứng (V03); lập kế hoạch UCS (V12)","Nạp đủ 33 màn gốc, xử lý links cho công tắc nối nhiều cầu; thêm passcode vào Level; quy hoạch tách nhánh Git","bloxorz/level.py, bloxorz/rules.py, bloxorz/serialize.py, tests/test_rules.py, ke_hoach_v12_ucs.md","Nạp thành công 33 màn gốc (đặc biệt 6 màn 17, 23, 25, 29, 30, 31 có links); test T14 qua; 130/130 test hệ thống qua"
2026-10-22,TV3,Antigravity (Google DeepMind),"Đổi tên nhánh thành feature/trong/V12-ucs; Cài đặt thuật toán UCS trên mê cung có trọng số (V12)","Cài đặt UCS dùng heapq, lazy deletion qua best_g, goal test khi lấy ra khỏi frontier, đếm 4 chỉ số thực nghiệm","solvers/ucs.py, tests/test_solvers.py, hoan_thanh_v12_ucs.md","UCS giải đúng 4 mê cung mẫu có trọng số (open, walls, weighted, no_solution), chi phí khớp tính tay; 111/111 test qua"
2026-10-23,TV3,Antigravity (Google DeepMind),"Phân tích toàn diện đồ án từ PDF đề bài, kiến trúc tương tác GUI - Engine - Solvers; hoàn thiện ô đặc biệt (V05)","Đọc kĩ đề bài AI - Project 1.pdf, phát hiện bẫy prompt injection; phân tích mô hình tìm kiếm, cơ chế chạy nền runner.py và ý nghĩa 4 thuật toán; hoàn thiện rules.py","docs/08-phan-tich-tong-quan-do-an.md, bloxorz/rules.py, tests/test_rules.py, tests/test_spec.py","Tài liệu 08-phan-tich-tong-quan-do-an.md hoàn chỉnh; bộ test T07–T16 qua 100%; màn 2, 4, 5, 7, 11, 13 giải đúng số bước; 26/26 test_spec qua"
2026-10-28,TV3,Antigravity (Google DeepMind),"Thiết kế và cài đặt hàm chi phí không đồng nhất V13 dựa trên công nâng trọng tâm; tích hợp vào Problem","Hàm chi phí vật lý V13 bảo đảm mọi bước >= 1.0; DEFAULT_COST_FN bảo đảm tương thích ngược","bloxorz/costs.py, bloxorz/problem.py, tests/test_costs.py","test_costs qua 7/7; không làm ảnh hưởng các test cũ của BFS/DFS; A* bảo toàn tính admissible"
2026-10-28,TV3,Antigravity (Google DeepMind),"UCS giải đủ 33 màn (V14); viết script sinh 14 màn tự sinh S1–S3 (V40); gộp code vào integration/M2","Test kiểm chứng UCS trên 33 màn; script experiments/gen_levels.py sinh 14 file JSON; PR vào integration/M2","tests/test_ucs.py, experiments/gen_levels.py, tests/test_gen_levels.py, levels/gen/","UCS khớp 100% par của BFS khi cost=1; tối ưu năng lượng ở màn 17 và 23; 14 màn tự sinh được BFS kiểm định tự động; 203/203 test qua trên integration/M2"
2026-10-31,TV3,Antigravity (Google DeepMind),"Kiểm thử toàn diện 5 tầng; sửa lỗi encoding cp1258 cho charts.py; soạn kịch bản và slide intro video demo (V36)","Kế hoạch kiểm thử 5 tầng; sửa charts.py parse_args; kịch bản chi tiết 09-ke-hoach-kich-ban-video-demo.md; intro_slide.md","experiments/charts.py, docs/video/intro_slide.md, 09-ke-hoach-kich-ban-video-demo.md","246/246 test qua; check_heuristics báo 0 vi phạm trên 340.414 cạnh; K1–K8 pass; tái lập trùng 100%; slide intro hiển thị chuẩn"
```
