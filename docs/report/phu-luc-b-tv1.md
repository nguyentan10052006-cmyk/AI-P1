# Phụ lục B: phần của TV1 (ghép vào `phu-luc-b-ai.md`)

Phần này gồm đoạn ghép vào B.1 và B.2 theo mẫu của TV4, cùng các ví dụ prompt. Prompt được trích **nguyên văn** từ lịch sử 24 phiên Claude Code lưu trên máy TV1 (file `.jsonl`, 120 prompt từ 15/10 tới 30/10; không tính thông báo hệ thống). Giờ ghi theo giờ Việt Nam (+07).

## Đoạn ghép vào B.1 (bảng công cụ)

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic), tiện ích VS Code, bản 2.1.300–2.1.312, mô hình `claude-opus-5-5` | TV1 (15/10–30/10) | Xem B.2, phần TV1 |
| Claude Code trên web (claude.ai/code, Anthropic) | TV1 (19/10) | Bản cân bằng lại phân công ngày 19/10 (commit `84c5a4e`) |

## Đoạn ghép vào B.2

**TV1.** Dùng Claude Code chạy ngay trong repository. Claude đọc tài liệu và code, viết code và test, chạy test, chạy lệnh Git và gọi GitHub API theo từng yêu cầu của TV1. Phần lớn code, test và lời văn của TV1 do Claude viết theo yêu cầu trong prompt và theo tài liệu nhóm.

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

**Phần AI đề xuất và phần TV1 chọn.**

- **Claude đề xuất,** TV1 đồng ý qua prompt tiếp theo:
  - cấu trúc bộ tài liệu nhóm và cách chia 14 nhóm việc;
  - các lựa chọn khi cài BFS (đánh dấu đã thăm khi đưa vào hàng đợi, kiểm tra đích khi sinh nút);
  - bộ test luật T01–T24;
  - cách tổ chức chương 2 và mục 3.1.
- **TV1 quyết định:**
  - phương án PA2, Google Sheets, 33 màn gốc, các chỉ số thực nghiệm;
  - không giao cho Claude việc nhắn tin, đôn đốc thành viên khác;
  - nhánh chính của nhóm để ghép báo cáo (`thu/test-main-m2`).

Đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn một câu cố định vào báo cáo. TV1 đã tìm và bảo đảm câu đó không có trong các phần của mình.

## Ví dụ prompt (trích nguyên văn)

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
