# Phụ lục B: phần của TV2 (gửi TV4 ghép vào `phu-luc-b-ai.md`)

> TV2 soạn ngày 28/10. Gồm ba phần: đoạn ghép vào B.1 và B.2 theo mẫu của TV4; các dòng dán vào tab prompt-ai; và nguồn để kiểm lại. Prompt trích **nguyên văn** từ lịch sử phiên Claude Code lưu trên máy TV2 (file `.jsonl` của phiên, 25 tin nhắn, 19/10–28/10). Giờ ghi theo giờ Việt Nam (+07). Không chép email, token hay thông tin đăng nhập nào.

## Đoạn ghép vào B.1 (bảng công cụ)

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic), tiện ích VS Code, bản 2.1.301–2.1.310, mô hình `claude-opus-5-5` | TV2 (19/10–28/10) | Xem B.2, phần TV2 |

## Đoạn ghép vào B.2

**TV2.** Dùng Claude Code chạy ngay trong repository. Claude đọc tài liệu và code, sửa file, chạy test, chạy lệnh Git và gọi GitHub API theo từng yêu cầu của TV2. Phần lớn code và tài liệu của TV2 do Claude viết theo đặc tả trong prompt và trong `docs/01`–`07`.

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
  - không giao cho Claude các việc thuộc người khác: hàm chi phí V13, định dạng file kết quả chung, xác nhận bộ màn S1–S3.

*(TV2 bổ sung trước khi nộp: các lần tự chạy lại test hoặc tự đọc code ngoài phiên Claude Code, nếu có.)*

## Ví dụ prompt (trích nguyên văn)

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

## Dòng dán vào tab prompt-ai (`docs/sheet/6-prompt-ai.csv`)

```csv
2026-10-19,TV2,Claude Code (Anthropic),"NV4, NV6: chuyển 33 màn gốc, DFS, đánh giá DFS hay IDS","# ROLE: TV2 — Bloxorz Solver (CSC14003, Project 1) … Đọc tài liệu phân công và đề bài trước khi sửa code. (nguyên văn đầu prompt; đủ ở Phụ lục B)","experiments/convert_original_levels.py, levels/original/, solvers/dfs.py, tests/; PR #10","Test đối chiếu từng ô với dữ liệu gốc; DFS phát lại tới đích, số bước không nhỏ hơn tối ưu"
2026-10-23,TV2,Claude Code (Anthropic),"Đọc chéo PR #7; thêm matplotlib; script đo V23","# Bloxorz Solver — Xử lý PR #7, cập nhật matplotlib và triển khai V23","Nhận xét PR #7; experiments/run.py, tests/test_experiments.py; PR #11","Test ở head PR và sau khi gộp; GUI chạy offscreen; script thử với solver giả"
2026-10-28,TV2,Claude Code (Anthropic),Sửa F1–F5 của V23 kèm test hồi quy,"# AI-P1 — Hoàn thành tối đa công việc TV2 trong hôm nay","experiments/run.py; PR #13","10 test hồi quy thất bại trên code cũ, qua trên code mới; cả bộ test qua trong worktree sạch"
2026-10-28,TV2,Claude Code (Anthropic),"Ghép tạm code TV3, TV4 để chạy thử V24; S1–S3 tạm; biểu đồ V25; kiểm tra chéo","# AI-P1 — Chủ động xử lý dependency của các thành viên để hoàn thành công việc TV2","Nhánh integration/Tien/V24 (chưa push); số liệu chạy thử không dùng trong báo cáo","Kiểm tra chéo 04 §6; xem lại từng hình; check_heuristics.py 0 vi phạm"
2026-10-28,TV2,Claude Code (Anthropic),"Kiểm tra hồi cứu, đối chiếu đề bài, đọc chéo GUI V20/V21 của TV5","Trước khi tiếp tục dự án AI-P1 / Bloxorz Solver, hãy thực hiện kiểm tra hồi cứu việc khảo sát repository Git …","docs/nghiem-thu/ (không nộp); ghi chú cho TV3, TV4, TV5","GUI offscreen 13/13 khi đủ code TV3, TV4; tái hiện lỗi bằng script"
2026-10-28,TV2,Claude Code (Anthropic),"Nháp chương 3.2, 5 (5.1, 5.2), 5.4.2, phụ lục B phần TV2","# AI-P1 / Bloxorz Solver — Hoàn thành toàn bộ công việc thuộc phạm vi TV2","docs/report/3.2-dfs.md, 5-thuc-nghiem.md, 5.4-nhan-xet-dfs.md, phu-luc-b-tv2.md","Đối chiếu với dfs.py, run.py và test; chạy lại lệnh ví dụ ở Bảng 3.2.1"
```

## Nguồn để kiểm lại

Lịch sử phiên nằm trên máy TV2, trong thư mục dự án của Claude Code (`~/.claude/projects/`, một file `.jsonl` cho phiên này). Prompt đầy đủ trích được bằng cách lọc các dòng có `"type": "user"` và nội dung là văn bản. Commit của TV2 ghi tác giả "Quang Tien".
