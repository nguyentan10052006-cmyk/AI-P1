## Phụ lục B. Sử dụng công cụ AI

Đề yêu cầu nêu rõ công cụ AI đã dùng, prompt và kết quả của AI được dùng vào đâu [1, mục 3.6]. Mỗi thành viên tự ghi phần của mình; prompt được trích **nguyên văn** từ lịch sử phiên làm việc lưu trên máy của từng người. Phụ lục gồm bảng công cụ (B.1), việc dùng AI của từng thành viên kèm ví dụ prompt (B.2) và các nguyên tắc nhóm áp dụng (B.3).

### B.1. Công cụ

**Bảng B.1.** Công cụ AI nhóm đã dùng.

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic), tiện ích VS Code, bản 2.1.300–2.1.312, mô hình `claude-opus-5-5` | TV1 (15/10–31/10) | Xem B.2, phần TV1 |
| Claude Code trên web (claude.ai/code, Anthropic) | TV1 (19/10) | Bản cân bằng lại phân công ngày 19/10 (commit `84c5a4e`) |
| Claude Code (Anthropic), tiện ích VS Code, bản 2.1.301–2.1.310, mô hình `claude-opus-5-5` | TV2 (19/10–31/10) | Xem B.2, phần TV2 |
| [TV3 điền: công cụ AI đã dùng, hoặc ghi "không dùng"]{.dien} | TV3 | |
| Claude Code (Anthropic) | TV4 (20/10–26/10) | Xem B.2, phần TV4 |
| Claude Code (Anthropic), giao diện dòng lệnh, bản 2.1.303–2.1.310, mô hình `claude-opus-5-5` | TV5 (19/10–29/10) | Xem B.2, phần TV5 |

### B.2. Việc dùng AI theo từng thành viên

#### Bộ tài liệu nhóm (19/10)

Bộ tài liệu `docs/01`–`06` được soạn với sự hỗ trợ của Claude: phân công PA2, luật chơi chuẩn, đối chiếu dữ liệu 33 màn gốc từ bốn nguồn và cột "Bước tối ưu", cân bằng lại phân công ngày 19/10. Nhóm kiểm tra lại bằng BFS của nhóm: 33/33 màn khớp cột "Bước tối ưu" (test T24).

#### TV1 (Trần Nguyên Tân)

Dùng Claude Code chạy ngay trong repository. Claude đọc tài liệu và code, viết code và test, chạy test, chạy lệnh Git và gọi GitHub API theo từng yêu cầu của TV1. Phần lớn code, test và lời văn của TV1 do Claude viết theo yêu cầu trong prompt và theo tài liệu nhóm.

TV1 làm các việc sau:

- viết prompt, đặt phạm vi cho từng đợt việc;
- quyết định các điểm cần chọn: phương án PA2, theo dõi tiến độ bằng Google Sheets, dùng 33 màn gốc, bộ chỉ số thực nghiệm (prompt ngày 19/10 bên dưới);
- chọn thời điểm gộp và cho phép từng thao tác lên GitHub (push, PR);
- đọc lại kết quả và báo cáo kiểm tra sau mỗi đợt.

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 15–18/10 | Tạo repository; slide cho buổi họp đầu tiên; code luyện tập (engine, giao diện web demo, 18 màn tự thiết kế) | Repository nhóm; bản demo đầu, vào nhánh chính qua PR #1 | Chạy thử demo; toàn bộ test của bản luyện tập |
| 18–19/10 | Soạn bộ tài liệu nhóm `docs/01`–`06` và 7 file CSV cho Google Sheet; đối chiếu dữ liệu 33 màn gốc từ bốn nguồn và tính cột "Bước tối ưu"; cân bằng lại phân công | `docs/`, Google Sheet "AI-P1" | Đối chiếu từng ô với bốn nguồn [3]–[6]; cột "Bước tối ưu" tính bằng BFS |
| 20/10 | BFS (V08): cài đặt, quy ước đếm chỉ số, mã giả | `solvers/bfs.py`, `tests/test_bfs.py`; PR #3 | Đếm `expanded`, `generated`, `max_frontier`, `visited` trên mê cung nhỏ, so với kết quả tính tay |
| 21/10 | Test engine lõi T01–T06 (V02): bảng chuyển 12 trường hợp, rơi, thắng, phát lại lời giải | `tests/test_rules.py`; PR #5 | Toàn bộ test qua |
| 22/10 | Test tách và ghép khối T17–T23 (V06); màn 8, 9, 16 | `tests/test_rules.py`, `tests/test_bfs.py`; PR #6 | Màn 8, 9, 16 ra đúng 10, 24, 28 bước |
| 24/10 | Kiểm tra tiến độ các nhánh trên GitHub | Ghi chú riêng của TV1 | Đối chiếu với GitHub API |
| 25/10 | Test T24: BFS trên đủ 33 màn gốc (V09); khung báo cáo LaTeX; nháp chương 2 và mục 3.1 | `tests/test_bfs.py`; PR #12; bản nháp riêng | BFS khớp số bước tối ưu ở 33/33 màn, lời giải phát lại tới đích |
| 30/10 | Đánh giá bài của nhóm theo thang điểm của đề; cập nhật chương 2 và mục 3.1 theo code mới nhất; viết mục 5.4.1 và phần này; thử cài theo README trong môi trường ảo mới (V37) | `docs/report/2-mo-hinh-hoa.md`, `3.1-bfs.md`, `5.4-nhan-xet-bfs.md`, `phu-luc-b-tv1.md` | Mọi ví dụ và con số được chạy lại bằng engine và script thực nghiệm ở commit `44dc9e3`; trên bản cài mới, 205/206 test qua (test còn lại cần thư mục `.git`) và giao diện import được |
| 31/10 | Ghép báo cáo và xuất PDF. Viết mục 3.3 (UCS và hàm chi phí) và 5.4.3 (nhận xét UCS), là hai phần được giao cho TV3 nhưng chưa có khi ghép; viết chương 1, chương 6, phần Tóm tắt; viết lại mục 5.4.4 và cập nhật Bảng 3.4.1, 3.4.2, mục 5.4.1 theo lần đo chính thức; bỏ ghi chú nháp và tham chiếu tới tài liệu nội bộ | Toàn bộ báo cáo (`docs/report/`, `Report.pdf`) | Mọi con số đối chiếu với `summary.csv` của lần đo `0a35afd`; chạy lại `tools/check_heuristics.py` (0 vi phạm); so lời giải BFS và UCS ở màn 17, 23 bằng engine; đối chiếu mô tả test với code test; chạy lại toàn bộ test (246 test qua) |

**Phần AI đề xuất và phần TV1 chọn.**

- **Claude đề xuất,** TV1 đồng ý qua prompt tiếp theo:
  - cấu trúc bộ tài liệu nhóm và cách chia 14 nhóm việc;
  - các lựa chọn khi cài BFS (đánh dấu đã thăm khi đưa vào hàng đợi, kiểm tra đích khi sinh nút);
  - bộ test luật T01–T24;
  - cách tổ chức chương 2 và mục 3.1.
- **TV1 quyết định:**
  - phương án PA2, Google Sheets, 33 màn gốc, các chỉ số thực nghiệm;
  - không giao cho Claude việc nhắn tin, đôn đốc thành viên khác;

Đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn một câu cố định vào báo cáo. TV1 đã tìm và bảo đảm câu đó không có trong các phần của mình.

Mục 3.3 và 5.4.3 do Claude viết trong phiên của TV1 ngày 31/10, dựa trên code của TV3 (`solvers/ucs.py`, `bloxorz/costs.py` cùng phần chú thích giải thích các mức chi phí), test của TV3 và số liệu của lần đo chính thức.

**Ví dụ prompt của TV1 (trích nguyên văn).**

Prompt giao việc soạn tài liệu nhóm, 19/10 00:15:

> bây giờ sau khi họp nhóm tôi quyết định làm PA2, theo dõi tiến độ bằng gg sheet, Thực nghiệm gồm có số bước, số expanded, bộ nhớ, chi phí, các frontieer nếu có, thời gian tìm kiếm, và tổng thời gian,... . Chúng tôi mong muốn lấy lại các màn của game gốc để đánh giá chuẩn nhất. Sử dụng lại các rule chuẩn của game nếu không tìm ra thì thử tìm các mã nguồn của game được public trên github vi dụ nhưu https://github.com/supersaiyanmode/Bloxorz
> https://github.com/chaitanya100100/Bloxorz
> Tôi muốn bạn viết thêm phần docs chia việc cho từng người, và các thứ liên quan mà tôi không biết cách trình bày. Mục đích của file này có các nhóm việc để phân chia cho mọi người đồng thời mô tả chi tiết công việc như thế nào!

Prompt hỏi cách làm phần việc của TV1, 20/10 16:12:

> bạn ơi tôi là thành viên 1. Và hiện tại có rất nhiều nhánh ở github do các người khác làm nên là tôi khá bối rối và không nhóm nào nên tôi muốn bạn cho tôi các phương pháp và cách làm để xong nhiệm vụ của thành viên 1

Prompt nhờ hướng dẫn code, 22/10 20:40:

> vậy bạn cho tôi nội dung code mà tôi cần phải làm hôm nay đồng thời hướng dẫn chi tiết xem nào

Prompt đánh giá bài trước khi nộp, 30/10 15:21:

> bây giờ ở nhánh thu/test-main-m2 là nhánh hiện tại và mới nhăt của chúng tôi và bạn có thể coi như là main. Bây giờ tôi muốn bạn xem xét xem đánh giá điểm cho nhóm tôi theo các tiêu chí mà bạn nghĩ rằng thầy hoặc AI của thầy chấm cho nhóm tôi để còn cải thiện mà nộp bài!

Prompt giao việc ghép và hoàn thiện báo cáo, 31/10 21:35:

> bây giờ tôi muốn bạn tiến hành viết report cho tôi. TÔI MONG BẠN CỐ GẮNG SAO CHO TÔI CÓ THẺ ĐẠT FULL ĐIỂM!

#### TV2 (Bùi Quang Tiến)

Dùng Claude Code chạy ngay trong repository. Claude đọc tài liệu và code, sửa file, chạy test, chạy lệnh Git và gọi GitHub API theo từng yêu cầu của TV2. Phần lớn code và tài liệu của TV2 do Claude viết theo đặc tả trong prompt và trong `docs/01`–`07`.

TV2 làm các việc sau:
- viết prompt, đặt phạm vi và ràng buộc cho từng đợt (không ghi đè dữ liệu của người khác, không push hoặc merge khi chưa cho phép, không bịa số liệu);
- quyết định các điểm cần chọn, ví dụ chờ PR #10 merge rồi mới làm V23;
- cho phép từng thao tác lên GitHub (push, mở PR);
- đọc các báo cáo nghiệm thu Claude viết sau mỗi đợt.

Mọi lần chạy test và kiểm tra dưới đây do Claude chạy trong phiên. Kết quả ghi trong các báo cáo nghiệm thu của TV2.

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 19–20/10 | Chuyển 33 màn gốc từ bloxorz_gba (NV4, V07), sửa màn 3; DFS dạng tìm kiếm trên đồ thị (NV6, V10, V11); đánh giá chọn DFS hay IDS | `experiments/convert_original_levels.py`, `levels/original/`, `solvers/dfs.py`, `tests/test_original_levels.py`, `tests/test_dfs.py`; PR #10 | Test đối chiếu từng ô với dữ liệu gốc; DFS giải 27 màn nạp được (6 màn `links` chờ V03), phát lại tới đích, số bước không nhỏ hơn tối ưu; sha256 của dữ liệu nguồn |
| 23/10 | Đọc chéo PR #7 (GUI Ursina của TV5); thêm `matplotlib` vào `requirements.txt`; script đo V23 và solver giả để thử | Nhận xét PR #7 (không đăng lên GitHub); `experiments/run.py`, `tests/test_experiments.py`; PR #11 | Chạy test ở head của PR và sau khi gộp; chạy GUI ở chế độ offscreen; thử script với solver giả trả kết quả cố định |
| 28/10 | Sửa 5 lỗi của V23 (F1–F5) kèm test hồi quy | `experiments/run.py`; PR #13 | 10 test hồi quy mới đều thất bại trên code cũ và qua trên code mới; cả bộ test qua trong một worktree sạch |
| 28/10 | Ghép tạm code UCS, $h_P$ và bộ nạp `links` của TV3, TV4 trên một nhánh riêng để chạy thử; viết tạm bộ màn S1–S3; vẽ biểu đồ V25; kiểm tra chéo số liệu | Nhánh `integration/Tien/V24` (chưa push); số liệu chạy thử **không** dùng trong báo cáo | Kiểm tra chéo 04 §6 trên số liệu chạy thử; xem lại từng hình đã vẽ; công cụ `check_heuristics.py` của TV4 cho 0 vi phạm |
| 28/10 | Kiểm tra hồi cứu cách đã khảo sát repository; đối chiếu đề bài với tài liệu nhóm; đọc chéo GUI V20, V21 của TV5 | Các báo cáo trong `docs/nghiem-thu/` (không nộp); ghi chú gửi TV3, TV4, TV5 | Lái GUI ở chế độ offscreen: 13/13 kiểm tra đạt khi có đủ code của TV3, TV4; tái hiện các lỗi tìm được bằng script |
| 28/10 | Nháp chương 3.2, chương 5 (5.1, 5.2, khung 5.3 và 5.5), mục 5.4.2 và phần này | `docs/report/` | Đối chiếu từng câu với code `dfs.py`, `run.py` và test; lệnh tái hiện ví dụ ở Bảng 3.2.1 chạy lại ra đúng số |
| 28/10 (chiều) | Mở PR báo cáo; sửa các công cụ thực nghiệm để từ chối dữ liệu hỏng (5 lỗi tái hiện bằng file cố ý làm hỏng); thêm kiểm tra đủ dòng K8 và `compare_runs.py`; tách các công cụ ra một nhánh sạch từ `main` | PR #14, #16, #17: `check_results.py`, `charts.py`, `tables.py`, `compare_runs.py`, `experiments/README.md` | Test mới thất bại trên code cũ; chạy thử 235 cặp, so hai lần chạy cho số đếm trùng hẳn |
| 31/10 | Rà cách nối hàm chi phí V13 sau PR #18 (đọc code, chạy `check_heuristics` với V13, duyệt mọi cạnh của 33 màn); phát hiện bước làm khối tách đôi có chi phí 1,0 (module của TV3); làm công cụ biết chế độ chi phí | PR #20; tài liệu bàn giao và bản vá đề xuất cho TV3 (không áp vào code của TV3) | 0 vi phạm heuristic; bản vá đề xuất qua 233 test. **Sự cố do Claude gây ra:** lần đo kỹ thuật đầu chạy trong worktree mà Claude đang sửa tạm `costs.py`, nên dữ liệu có thể bị nhiễm. Lần đo đó bị dừng, dữ liệu được đánh dấu loại bỏ, và đo lại trong worktree riêng |
| 31/10 | Đo thực nghiệm trên commit sạch `cd93624` theo 04 §4; kiểm tra K1–K8, tái lập và kiểm tra độc lập; viết mục 5.3, 5.5, 5.4.2 và Phụ lục A | PR #21: chương 5, Phụ lục A, `Source/experiments/benchmark-2026-10-31-cd93624/` | Đo lần hai trùng số đếm 235/235 cặp; phát lại 225 lời giải; tính lại 75 ô trung vị; mỗi con số trong chương đối chiếu với `summary.csv`. Rà lại chương trước khi merge và sửa 3 câu không khớp số liệu |
| 31/10 (trưa, chiều) | Theo cho phép của TV2, đặt chi phí bước làm khối tách đôi bằng 1,62 (bằng nằm → đứng) trong `costs.py`, kèm test hồi quy. Đây là quyết định áp dụng để hoàn thiện phép đo; TV3 chưa review. Đo lại trên commit `0a35afd`; cập nhật chương 5, 5.4.2, Phụ lục A và hình; ghi khác biệt trước và sau khi sửa | PR #23 (`bloxorz/costs.py`, `tests/test_costs_split.py`, `tests/test_ucs.py`); PR #24: chương 5, Phụ lục A, `Source/experiments/benchmark-2026-10-31-0a35afd/` | 3 test mới thất bại trên code cũ, qua trên code mới; cả bộ test qua (246 OK, 1 skip). K1–K8 PASS. So với lần đo `cd93624`: chỉ 50 cặp của 10 màn G5 khác, số bước không đổi. Đo lần hai trùng số đếm 235/235 cặp; kiểm tra độc lập 0 lệch. Rà lại chương và sửa thêm chú thích Hình 5.6 (ghi "thang log" trong khi hình dùng thang tuyến tính) |

**Phần AI đề xuất và phần TV2 chọn.**
- **Claude đề xuất,** TV2 đồng ý qua prompt tiếp theo:
  - chọn DFS dạng tìm kiếm trên đồ thị thay vì IDS;
  - cách đo của `run.py`;
  - cách sửa F1–F5;
  - cách tổ chức các chương.
- **TV2 quyết định:**
  - thời điểm và phạm vi mỗi đợt;
  - chờ PR #10 merge rồi mới làm tiếp V23;
  - tên nhánh `feature/Tien/M1`;
  - cho phép push các nhánh `feature/Tien/M1`, `feature/Tien/V23`, `feature/Tien/V23-fixes` và mở PR #10, #11, #13;
  - cho phép push và mở PR #14, #16, #17, #20, #21, #22, #23, #24. #10, #11, #13, #14, #16, #17 do TV1 merge;
  - ngày 31/10, cho phép tự review và tự merge **chỉ** PR #20 và #21, với điều kiện test đạt, không xung đột, không có số liệu giả; Claude thực hiện việc merge qua tài khoản GitHub của TV2;
  - ngày 31/10 (11:34), cho phép tự quyết chi phí bước tách bằng 1,62, chạy lại phần thực nghiệm bị ảnh hưởng, tự review và merge PR #22 và các thay đổi TV2. Kèm điều kiện: không đổi chi phí của các hành động khác; không sửa để số liệu khớp kết quả mong muốn; ghi rõ trong báo cáo rằng đây là quyết định áp dụng để hoàn thiện phép đo, không khẳng định TV3 đã review hay phê duyệt;
  - giữ nguyên các quyết định khác thuộc người khác: bố cục S2 (TV3), định dạng file kết quả Q1–Q7 (nhóm), dòng chi phí bước tách trong Bảng 2.7 (TV1). Báo cáo ghi rõ phần số liệu phụ thuộc các quyết định này;
  - không giao cho Claude các việc thuộc người khác, ngoài mức chi phí bước tách nói trên: phần còn lại của hàm chi phí V13, định dạng file kết quả chung, xác nhận bộ màn S1–S3.

*(TV2 bổ sung trước khi nộp: các lần tự chạy lại test hoặc tự đọc code ngoài phiên Claude Code, nếu có.)*

**Ví dụ prompt của TV2 (trích nguyên văn).**

Prompt đầu tiên, 19/10 20:32 (đoạn mở đầu):

> # ROLE: TV2 — Bloxorz Solver (CSC14003, Project 1)
>
> Bạn là trợ lý lập trình và kỹ sư phần mềm đồng hành với tôi để hoàn thành nhiệm vụ **TV2** trong project Bloxorz Solver của môn CSC14003 – Artificial Intelligence. […] **Không chỉ đưa ra hướng dẫn hoặc kế hoạch. Hãy trực tiếp kiểm tra và thực hiện các thay đổi cần thiết trong workspace.**
>
> 1. Đọc tài liệu phân công và đề bài trước khi sửa code.
> 2. Xác minh mọi nhiệm vụ dựa trên file thực tế; không tự suy đoán tên file, cấu trúc dữ liệu hoặc trạng thái hoàn thành. […]
> 4. Không ghi đè hoặc xóa 18 màn chơi hiện có. […]

Prompt ngắn, 19/10 20:50:

> Cần nghiệm thu và chốt trước hoàn thành M1 đúng hạn, trước hết hãy đánh giá về thuật toán bạn chọn DFS thay vì IDS và trình bày lại tổng quát những gì đã làm.

Prompt giao việc có giới hạn quyền, 28/10 12:28 (đoạn mở đầu):

> # AI-P1 — Hoàn thành tối đa công việc TV2 trong hôm nay
>
> […] Bạn được tự quyết định và triển khai các việc sau mà không cần hỏi tôi trước:
> - Sửa lỗi đã xác định trong V23 và bổ sung regression tests. […]
> - Nếu có nhiều giải pháp, chọn giải pháp ít rủi ro nhất, giải thích ngắn gọn trong báo cáo và tiếp tục thực hiện.

**Danh sách đủ các đợt** (tiêu đề hoặc câu đầu của prompt, nguyên văn):

| Ngày, giờ | Prompt |
|---|---|
| 19/10 20:32 | `# ROLE: TV2 — Bloxorz Solver (CSC14003, Project 1)` |
| 19/10 20:50 | `Cần nghiệm thu và chốt trước hoàn thành M1 đúng hạn, …` |
| 19/10 21:08 | `Tiếp tục nghiệm thu và chốt M1 cho phần TV2. …` |
| 20/10 08:42 | `Tạo nhánh và push lên github, không cần merg, không cần push file nghiệm thu lên` |
| 20/10 08:49 | `đã sửa gì trong docs/03` |
| 22/10 20:52 | `# Nhiệm vụ: Rà soát sau M1 và lập kế hoạch tiếp theo cho TV2 — Bloxorz Solver` |
| 23/10 14:51 | `Tiếp tục ở trạng thái hiện tại` |
| 23/10 15:08 | `# Tiếp tục Bloxorz Solver sau M1 — Review PR #7 và bổ sung matplotlib` |
| 23/10 15:19 | `# Bloxorz Solver — Xử lý PR #7, cập nhật matplotlib và triển khai V23` |
| 23/10 15:43 | `Tiếp tục project Bloxorz Solver với vai trò TV2. …` |
| 23/10 15:49 | `# Chuẩn bị PR M1 đưa NV4 và DFS vào main` |
| 23/10 16:03 | `# Tiếp tục Bloxorz Solver — Chuẩn bị V23 và bảo toàn PR #10` |
| 23/10 16:10 | `# Theo dõi PR #10 và chuẩn bị V23 — Chưa thao tác Git` |
| 23/10 16:27 | `# Tiếp tục V23 sau khi PR #10 đã merge` |
| 23/10 16:36 | `# Push nhánh V23 và mở Pull Request` |
| 23/10 22:19 | `# Nhiệm vụ: Theo dõi PR #11 và chuẩn bị bước tiếp theo cho V23` |
| 28/10 12:24 | `# Nhiệm vụ: Chuẩn bị hoàn thiện V23 sau khi PR #11 merge` |
| 28/10 12:28 | `# AI-P1 — Hoàn thành tối đa công việc TV2 trong hôm nay` |
| 28/10 12:44 | `# AI-P1 — Chủ động xử lý dependency của các thành viên để hoàn thành công việc TV2` |
| 28/10 13:02 | `Khi nào biết xong?` |
| 28/10 13:13 | `Trước khi tiếp tục dự án AI-P1 / Bloxorz Solver, hãy thực hiện **kiểm tra hồi cứu việc khảo sát repository Git** …` |
| 28/10 13:18 | `# AI-P1 — Phát hành V23 riêng và bảo toàn nhánh tích hợp V24` |
| 28/10 13:24 | `Tiếp tục dự án AI-P1 từ trạng thái hiện tại, nhưng trước khi phát triển thêm V24/V25, hãy hoàn tất kiểm tra repository …` |
| 28/10 13:35 | `# AI-P1 / Bloxorz Solver — Hoàn thành toàn bộ công việc thuộc phạm vi TV2` |
| 28/10 14:12 | `Tiếp tục công việc TV2 trong repository Bloxorz-Solver dựa trên báo cáo trạng thái gần nhất.` |
| 28/10 14:27 | `Tiếp tục công việc TV2 trong repository Bloxorz-Solver theo hướng chủ động hoàn thành công việc, không chờ review của TV1 …` |
| 28/10 20:07 | `Tiếp tục ở trạng thái hiện tại.` |
| 31/10 01:35 | `# TIẾP TỤC HOÀN THÀNH CÔNG VIỆC TV2 — BẢO ĐẢM TÍCH HỢP VÀ BÀN GIAO` |
| 31/10 10:11 | `# PROMPT CLAUDE CODE — TIẾP TỤC TÍCH HỢP V13 VÀ HOÀN THÀNH THỰC NGHIỆM BLOXORZ SOLVER (TV2)` |
| 31/10 10:27 | `thông báo hoàn tất ở đâu?` |
| 31/10 10:35 | `# NHIỆM VỤ: HOÀN TẤT PHẦN VIỆC TV2 – BLOXORZ SOLVER` |
| 31/10 10:50 | `# FINAL PROMPT — HOÀN THIỆN TV2, TÍCH HỢP PR #20/#21, CHẠY BENCHMARK VÀ TỔNG KẾT DỰ ÁN BLOXORZ SOLVER` |
| 31/10 11:34 | `# BỔ SUNG QUYỀN TỰ QUYẾT VÀ HOÀN TẤT TV2` |
| 31/10 14:23 | `Tiếp tục ở trạng thái hiện tại` |

#### TV3 (Nguyễn Bảo Trọng)

[TV3 điền: đã dùng công cụ AI nào cho bộ nạp màn, ô đặc biệt, UCS, hàm chi phí và bộ màn tự sinh; dùng vào đâu; kiểm tra lại thế nào; kèm một vài prompt trích nguyên văn. Nếu không dùng AI thì ghi rõ.]{.dien}

#### TV4 (Trịnh Vỹ Triết)

Dùng Claude Code để viết code và nháp báo cáo cho các việc sau; mọi kết quả đều được kiểm tra bằng test và công cụ đo trước khi gộp:

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 20/10 | Hai biến thể A* (`astar`, `astar_m`); vẽ mê cung mẫu | `solvers/astar.py`, `tools/draw_mazes.py`, `docs/gridmaze/` | Toàn bộ test; xem ảnh SVG |
| 20/10 | A* trên mê cung (V15), module chạy nền không chặn (V39) | `solvers/astar.py`, `solvers/heuristics.py`, `solvers/runner.py` | Test trên mê cung có đáp án; test runner với tiến trình con thật |
| 23/10 | $h_P$ cho Bloxorz (V16), A* trên 33 màn (V17) | `solvers/heuristics.py`, `tools/check_heuristics.py` | 0 vi phạm trên 340 414 cạnh; cùng chi phí với UCS ở 33/33 màn |
| 26/10 | Nháp chương 3.4, mục 5.4 (A*), khung chương 1, 6, tài liệu tham khảo | `docs/report/` | TV4 đọc lại từng bước chứng minh; số liệu lấy từ công cụ đo |

#### TV5 (Võ Quốc Trung)

Dùng Claude Code chạy ngay trong thư mục làm việc (repository nhóm và một thư mục tài liệu riêng không đưa lên GitHub). Claude đọc tài liệu và code, sửa file, chạy test, mở cửa sổ giao diện bằng script để chụp màn hình và tự bấm phím, chạy lệnh Git theo từng yêu cầu của TV5. Phần lớn code giao diện trong `gui/` và tài liệu của TV5 do Claude viết theo yêu cầu trong prompt, theo `docs/07` và theo một bản đặc tả giao diện riêng của TV5.

TV5 làm các việc sau:
- viết prompt, đặt phạm vi và ràng buộc cho từng đợt (không push thẳng lên `main`, không push khi chưa đọc lại, commit dưới tên TV5, không ảnh hưởng việc của thành viên khác);
- chạy thử giao diện và nhận xét những chỗ chưa ổn, ví dụ góc xoay camera dễ làm lẫn hướng, bóng đổ, khung kết quả che mất bàn;
- tự sửa một phần code (tô màu ô màn đang mở trong lưới chọn màn) rồi nhờ Claude sửa lỗi phát sinh, giới hạn "chỉ sửa lỗi";
- cho phép từng thao tác lên GitHub (push, soạn nội dung PR) và tự mở, gộp các PR của mình.

Mọi lần chạy test và kiểm tra dưới đây do Claude chạy trong phiên.

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 19/10 | Soạn tài liệu kiến trúc và tích hợp GUI Ursina từ đặc tả kỹ thuật riêng của TV5 | `docs/07-kien-truc-gui-ursina.md`; nhánh `docs/kien-truc-gui-ursina` | TV5 đọc lại trước khi push; đối chiếu với `docs/01`–`06` |
| 21/10 | Rà các nhánh trên GitHub; sửa biên bản #3; cài Python 3.11 và Ursina, chốt phiên bản; vẽ bàn từ file màn (V18) và chơi tay bằng engine (V19) | `docs/sheet/7-bien-ban.csv`; `requirements.txt`; `gui/app.py`, `board_view.py`, `block_view.py`; PR #7, #8 | Mở được cửa sổ thử; màn 1 thắng đúng 7 bước; lời giải BFS màn 2, 8, 9, 16 thắng đúng 17, 10, 24, 28 bước |
| 23/10 | Check-in; ô đặc biệt, cầu, tách khối (V20); nút Giải, So sánh, Hủy, chọn màn, khối tự lăn (V21); README (V22); nháp chương 4 (V30) | `gui/`; PR #9; nhánh `feature/vo/V22-readme`; `docs/report/4-cai-dat-giao-dien.md` | Ghép thử với nhánh của TV2, TV3, TV4: BFS tự lăn thắng 33/33 màn, So sánh đủ năm dòng ở 33/33 màn; Hủy dừng đúng |
| 25/10 | Giới hạn góc camera (nghiêng tối đa 40°, bốn nấc góc cao, nhìn từ đỉnh); làm lại màu sắc theo đặc tả giao diện; bỏ bóng đổ; dời khung kết quả sang cột trái và căn bàn để không bị che; sửa lỗi sau khi TV5 tự sửa lưới chọn màn | `gui/`; PR #15 | Chụp màn hình ở màn 8, 28 sau mỗi thay đổi; đo góc camera không bị xoay nghiêng; cả bộ test qua |
| 29/10 | Cập nhật README theo phím mới; chụp lại toàn bộ hình chương 4 trên bản ghép thử với `integration/M2`; chạy lại kiểm thử giao diện; phần này | `Source/README.md`; `docs/report/4-cai-dat-giao-dien.md`, `hinh/`; `docs/report/phu-luc-b-tv5.md` | Ghép thử `main` với `integration/M2` không xung đột, cả bộ test qua, 33/33 màn nạp được; script kiểm tra camera qua mọi nấc; BFS tự lăn trên 33 màn |
| 30/10 | Rà các nhánh trên GitHub và trên máy; gộp V22, V30 và nháp báo cáo TV4 vào nhánh tích hợp `thu/test-main-m2`; tạm nối hàm chi phí V13 vào giao diện và script thực nghiệm (thêm `--cost`); nới cột Chi phí của bảng So sánh; cập nhật README | `gui/app.py`, `gui/hud.py`, `experiments/run.py`, `tests/test_experiments.py`, `Source/README.md`, chương 4 | 206 test qua; với chi phí thật, A* cùng chi phí với UCS ở 33/33 màn và `check_heuristics.py` báo 0 vi phạm; mở giao diện thật chạy So sánh ở màn 23 và chụp màn hình để kiểm tra bảng |
| 30/10 | Hoàn thiện đồ họa V21 (`ef1f10c`, `c73bb35`, `44dc9e3`): khối lật quanh cạnh, đổ nghiêng khi rơi, ô vát cạnh, lỗ đích nhìn xuyên, hộp kết thúc màn kéo thả được, font Be Vietnam Pro, thẻ kiểu kính mờ. Rà soát GUI rồi sửa 6 lỗi: Hủy không dừng được khối tự lăn; bấm Giải/So sánh khi đang tự lăn hoặc vừa thắng/rơi; cầu vẽ sai khi bấm R lúc cầu đang đổi; dòng trạng thái đè chữ "H: ẩn" và bảng So sánh; Enter lọt qua bảng F1/Ctrl+K; thu phóng không căn lại bàn | `gui/app.py`, `hud.py`, `board_view.py`, `camera_controller.py`, `popup.py`; `Source/README.md`, chương 4 | Script chạy giao diện thật (cửa sổ offscreen) tái hiện được cả 6 lỗi trước khi sửa, sau khi sửa không còn; kiểm tra hồi quy hộp thắng, hộp rơi, bảng So sánh và chụp màn hình khung kết quả; 206 test qua (1 bỏ qua) |
| 31/10 | Bảng chú giải các loại ô (phím G, nút "Chú giải") cho kịch bản video; chụp lại 10 hình chương 4 trên nhánh chính và thêm Hình 4.11; sửa test chạy được khi giải nén file nộp không có `.git`; README có lệnh vẽ hình và bảng | `gui/hud.py`, `gui/app.py`, `tests/test_experiments.py`, `Source/README.md`, chương 4, `hinh/` | Script mở giao diện thật bấm G, Esc, F1, Enter, phím lăn khi bảng mở; script chụp hình đi theo lời giải BFS và `rules.step()`, xem lại từng hình; số liệu trong hình khớp chữ của chương 4 (BFS 75 bước, chi phí 100,96; UCS, A* 99,96; DFS 1187 bước); bộ test qua cả trong thư mục không có `.git` |
| 31/10 | Cập nhật chương 4 và README theo PR #23 (bước làm khối tách đôi tính 1,62): số liệu màn 23, dòng mới trong bảng chi phí; chụp lại Hình 4.6–4.8 | chương 4, `hinh/`, `Source/README.md`, `gui/hud.py` (ghi chú) | Tính lại 5 thuật toán trên 33 màn: màn 23 BFS 101,58, UCS và A* 100,58, DFS 1525,37; BFS vẫn đắt hơn UCS đúng ở màn 17, 23; số trong hình khớp chữ của chương |

**Phần AI đề xuất và phần TV5 chọn.**
- **Claude đề xuất,** TV5 đồng ý qua prompt tiếp theo:
  - chạy solver ở tiến trình riêng và hỏi kết quả mỗi khung hình (theo `docs/07`);
  - cách đặt các nấc camera cụ thể (±20°, ±40°; 52°, 45°, 38°, 30°) và cách căn bàn khi khung kết quả hiện;
  - cách tổ chức chương 4.
- **TV5 quyết định:**
  - dùng Ursina (cùng nhóm, bien-ban #3);
  - camera chỉ nhìn từ trên xuống, không xoay 360°; thêm một nấc nghiêng mỗi bên và các nấc hạ thấp góc nhìn;
  - bỏ bóng đổ; màn đang mở phải có màu khác trong lưới chọn màn;
  - tên nhánh, thời điểm push, commit dưới tên TV5; không giao cho Claude việc của thành viên khác (bộ nạp màn, solver, runner).

*(TV5 bổ sung trước khi nộp: các lần tự chạy lại hoặc tự sửa code ngoài phiên Claude Code, nếu có.)*

**Ví dụ prompt của TV5 (trích nguyên văn).**

Prompt giao việc có giới hạn, 23/10 15:31:

> làm V22 và V30 trước đi trên tiền đề phải không ảnh hưởng đến các công việc của các thành viên khác

Prompt nhận xét sau khi chạy thử, 25/10 16:56:

> Bạn xem lại hững thay đổi gần đây đi, nhưng toi thấy phần xoay camera mó không ổn lắm, góc xoay thì phải luôn  nhìn từ trên uống hay có việc nhìn góc nghiên thì cũng từ trên xuống, với nếu đưuọc phép  xoay 3060 độ thì sẽ dễ khiến người chơi bị lẫn lộn hướng trái phải trên dưới lắm nên phải đặt các góc sao cho ít bị lẫn lộn, bạn giúp tôi tối ưu lại với

Prompt giới hạn phạm vi sửa, 25/10 18:00:

> Tôi vừa sửa khi bấm nút chọn màng thì nó không hiện màng hiện tại, kiểu như tất cả các màng đều cùng màu và tôi sửa thành đang ở màng nào thì ô màng đó có màu khác mà sửa xong thì nó lỗi, bạn giúp tôi chỉnh nó vfa tuyệt đối chỉ sửa lỗi không đưuọc phép tực hiện các thao tác phái sinh khác

**Danh sách đủ các đợt** (nguyên văn, prompt dài chỉ ghi câu đầu):

| Ngày, giờ | Prompt |
|---|---|
| 19/10 21:17 | `Thư mục docs_private là thư mục tôi dùng tạm để làm các việc cá nhân cho đồ án mà chưa public cho nhóm, … bạn giúp tôi pull về vô Project đi` |
| 19/10 21:22 | `Tạm thời cái Source chỉ là do nhóm trưởng vibe code để demo họp buổi đầu thôi, nhóm đang quyết dùng Ursina Engine. …` |
| 19/10 21:33 | `giúp tôi push lên đi, tài liệu ổn rồi, nhớ tạo nhánh riêng nha, đừng có push thảng lên main hay dev` |
| 21/10 13:42 | `Giờ bạn lên github kiểm tra xem có những gì thay đổi không? …` |
| 21/10 13:58 | `Sửa 7-bien-ban.csv #3, và nêu các công việc tôi cần làm trong hôm nay` |
| 21/10 14:01 | `push bien-ban lên đi và tạo danh sách công việc bằng markdown vào trong docs_private và thực hiện 1. …` |
| 21/10 14:08 | `ở 1 còn 1 việc chuwwa làm, bạn thực hiện luôn đi, pull các màng từ feature/Tien/M1 cũng được và thực hiện công việc số 2` |
| 21/10 14:16 | `ủa tôi chạy thử để test bằng cách nào` |
| 21/10 14:31 | `Làm luôn phần 3 đi (V19)` |
| 21/10 14:38 | `Từ từ tôi hỏi tí, thao tác lăn là sửa ở V mấy hay M mấy tôi nhìn không ưng lắm` |
| 21/10 20:21 | `Bạn quét github xem các nhánh khác sao rồi, tôi có thể hoàn thành toàn bộ công việc cho hôm nay chưa …` |
| 21/10 20:23 | `commit rồi ush lên giùm tôi đi` |
| 23/10 14:11 | `đọc tài liệu AGENTS.md để nắm bắt khái quát lại đồ án, …` |
| 23/10 14:25 | `bạn giúp tôi viết check-in tôi tự copy lên google sheet và giúp tôi bắt đầu V20 sau khi xong checkin đi` |
| 23/10 14:28 | `làm tiếp đi, tôi lỡi tay bấm dừng thôi` |
| 23/10 14:47 | `bạn kiểm tra lại trên github sao rồi, tôi đãcho PR rồi` |
| 23/10 14:51 | `bạn giúp tôi cho lệnh terminal để tuự động giải màn 33 với, chỉ cần cho code không cần chạy` |
| 23/10 14:56 | `tự động tạo script tự động chạy toàn bộ  33 màn  (không cần lưu script hoặc` |
| 23/10 14:57 | `lưu script đó vào doc_private đi` |
| 23/10 14:59 | `ý là script khi chạy sẽ mở luôn GUI cho chạy tự động và tôi có thể thể nhìn luôn á` |
| 23/10 15:02 | `commit và push lên github đi, nhớ là dưới danh nghiax tôi chứ không phải claude code` |
| 23/10 15:05 | `Trước làm tiếp V21 thì kiểm tra các màn còn lại của trọng đã push nhánh lên chưa rồi thì pull về máy tôi hết đi, …` |
| 23/10 15:20 | `commit và push và soạn nội dung PR. …` |
| 23/10 15:25 | `ủa sao python main.py mà cái DFS vẫn hiện là chưa nạp vậy, tôi tưởng bạn pull về rồi` |
| 23/10 15:29 | `quay lại nhánh hồi nãy lam đi và giúp tôi commit và push lên nếu chưa làm với, …` |
| 23/10 15:31 | `làm V22 và V30 trước đi trên tiền đề phải không ảnh hưởng đến các công việc của các thành viên khác` |
| 25/10 16:56 | `Bạn xem lại hững thay đổi gần đây đi, nhưng toi thấy phần xoay camera mó không ổn lắm, …` |
| 25/10 17:05 | `Từ từ, bạn xem GAME_UI_UX_SPECIFICATION.md coi có thiết kế giao diện gì không kiểu như là theme gì đó, …` |
| 25/10 17:17 | `Bỏ cái bón đổ đi, sửa lại cái tài liệu GAME_UI_UX_SPECIFICATION.md cho nó hợp lý` |
| 25/10 17:24 | `có mấy bảng thông số hiện lên khi chọn giải bằng thuật toán nó cho mất cái bàn rồi, bạn giúp  tôi tối ưu chỉnh lại đi` |
| 25/10 18:00 | `Tôi vừa sửa khi bấm nút chọn màng thì nó không hiện màng hiện tại, …` |
| 29/10 20:18 | `Giúp tôi hoàn thiện các phần còn lại của đồ án đi` |

### B.3. Nguyên tắc nhóm áp dụng

- Ghi lại việc dùng AI vào bảng theo dõi của nhóm ngay khi dùng.
- Không đưa vào báo cáo kết quả nào của AI mà chưa kiểm tra lại bằng code, test hoặc số liệu đo.
- Đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn một câu cố định vào báo cáo; nhóm đã tìm và bảo đảm câu đó không có trong báo cáo.
