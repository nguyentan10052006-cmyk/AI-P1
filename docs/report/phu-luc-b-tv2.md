# Phụ lục B: phần của TV2 (gửi TV4 ghép vào `phu-luc-b-ai.md`)

> TV2 soạn ngày 28/10, bổ sung ngày 31/10. Gồm ba phần: đoạn ghép vào B.1 và B.2 theo mẫu của TV4; các dòng dán vào tab prompt-ai; và nguồn để kiểm lại. Prompt trích **nguyên văn** từ lịch sử phiên Claude Code lưu trên máy TV2 (file `.jsonl` của phiên, 34 prompt từ 19/10 20:32 tới 31/10 14:23; không tính thông báo hệ thống). Giờ ghi theo giờ Việt Nam (+07). Không chép email, token hay thông tin đăng nhập nào.

## Đoạn ghép vào B.1 (bảng công cụ)

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic), tiện ích VS Code, bản 2.1.301–2.1.310, mô hình `claude-opus-5-5` | TV2 (19/10–31/10) | Xem B.2, phần TV2 |

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

## Dòng dán vào tab prompt-ai (`docs/sheet/6-prompt-ai.csv`)

```csv
2026-10-19,TV2,Claude Code (Anthropic),"NV4, NV6: chuyển 33 màn gốc, DFS, đánh giá DFS hay IDS","# ROLE: TV2 — Bloxorz Solver (CSC14003, Project 1) … Đọc tài liệu phân công và đề bài trước khi sửa code. (nguyên văn đầu prompt; đủ ở Phụ lục B)","experiments/convert_original_levels.py, levels/original/, solvers/dfs.py, tests/; PR #10","Test đối chiếu từng ô với dữ liệu gốc; DFS phát lại tới đích, số bước không nhỏ hơn tối ưu"
2026-10-23,TV2,Claude Code (Anthropic),"Đọc chéo PR #7; thêm matplotlib; script đo V23","# Bloxorz Solver — Xử lý PR #7, cập nhật matplotlib và triển khai V23","Nhận xét PR #7; experiments/run.py, tests/test_experiments.py; PR #11","Test ở head PR và sau khi gộp; GUI chạy offscreen; script thử với solver giả"
2026-10-28,TV2,Claude Code (Anthropic),Sửa F1–F5 của V23 kèm test hồi quy,"# AI-P1 — Hoàn thành tối đa công việc TV2 trong hôm nay","experiments/run.py; PR #13","10 test hồi quy thất bại trên code cũ, qua trên code mới; cả bộ test qua trong worktree sạch"
2026-10-28,TV2,Claude Code (Anthropic),"Ghép tạm code TV3, TV4 để chạy thử V24; S1–S3 tạm; biểu đồ V25; kiểm tra chéo","# AI-P1 — Chủ động xử lý dependency của các thành viên để hoàn thành công việc TV2","Nhánh integration/Tien/V24 (chưa push); số liệu chạy thử không dùng trong báo cáo","Kiểm tra chéo 04 §6; xem lại từng hình; check_heuristics.py 0 vi phạm"
2026-10-28,TV2,Claude Code (Anthropic),"Kiểm tra hồi cứu, đối chiếu đề bài, đọc chéo GUI V20/V21 của TV5","Trước khi tiếp tục dự án AI-P1 / Bloxorz Solver, hãy thực hiện kiểm tra hồi cứu việc khảo sát repository Git …","docs/nghiem-thu/ (không nộp); ghi chú cho TV3, TV4, TV5","GUI offscreen 13/13 khi đủ code TV3, TV4; tái hiện lỗi bằng script"
2026-10-28,TV2,Claude Code (Anthropic),"Nháp chương 3.2, 5 (5.1, 5.2), 5.4.2, phụ lục B phần TV2","# AI-P1 / Bloxorz Solver — Hoàn thành toàn bộ công việc thuộc phạm vi TV2","docs/report/3.2-dfs.md, 5-thuc-nghiem.md, 5.4-nhan-xet-dfs.md, phu-luc-b-tv2.md","Đối chiếu với dfs.py, run.py và test; chạy lại lệnh ví dụ ở Bảng 3.2.1"
2026-10-28,TV2,Claude Code (Anthropic),"Kiểm tra nhánh báo cáo, mở PR; rà lại tables.py, charts.py, check_results.py; soạn tin nhắn bàn giao","Tiếp tục công việc TV2 trong repository Bloxorz-Solver dựa trên báo cáo trạng thái gần nhất.","PR nhánh feature/Tien/report; docs/nghiem-thu/ (không nộp)","diff so với main chỉ gồm file báo cáo TV2; git diff --check; cả bộ test"
2026-10-28,TV2,Claude Code (Anthropic),"Công cụ từ chối dữ liệu hỏng, K8, compare_runs.py; tách nhánh công cụ","Tiếp tục công việc TV2 … theo hướng chủ động hoàn thành công việc, không chờ review của TV1 …","PR #16, #17: experiments/check_results.py, charts.py, tables.py, compare_runs.py, README","Test mới thất bại trên code cũ; so hai lần chạy thử: số đếm trùng 235/235"
2026-10-31,TV2,Claude Code (Anthropic),"Rà V13 sau PR #18; công cụ biết chế độ chi phí; tìm lỗi chi phí bước tách (TV3)","# PROMPT CLAUDE CODE — TIẾP TỤC TÍCH HỢP V13 VÀ HOÀN THÀNH THỰC NGHIỆM BLOXORZ SOLVER (TV2)","PR #20; tài liệu bàn giao cho TV3","check_heuristics với V13: 0 vi phạm; lần đo bị nhiễm do Claude sửa tạm code trong cùng worktree đã bị loại và đo lại"
2026-10-31,TV2,Claude Code (Anthropic),"Đo thực nghiệm cd93624; chương 5.3, 5.5, 5.4.2, Phụ lục A","# FINAL PROMPT — HOÀN THIỆN TV2, TÍCH HỢP PR #20/#21, CHẠY BENCHMARK VÀ TỔNG KẾT DỰ ÁN BLOXORZ SOLVER","PR #21: docs/report/, Source/experiments/benchmark-2026-10-31-cd93624/","K1–K8 PASS; lần đo hai trùng số đếm 235/235; kiểm tra độc lập 0 lệch"
2026-10-31,TV2,Claude Code (Anthropic),"Chi phí bước tách 1,62 (quyết định để hoàn thiện phép đo, TV3 chưa review); đo lại 0a35afd; cập nhật chương 5, Phụ lục A","# BỔ SUNG QUYỀN TỰ QUYẾT VÀ HOÀN TẤT TV2","PR #23: bloxorz/costs.py, tests/test_costs_split.py; PR #24: docs/report/, Source/experiments/benchmark-2026-10-31-0a35afd/","Test mới thất bại trên code cũ; cả bộ test qua; K1–K8 PASS; chỉ 50 cặp G5 khác lần đo cd93624; lần đo hai trùng số đếm 235/235"
```

## Nguồn để kiểm lại

Lịch sử phiên nằm trên máy TV2, trong thư mục dự án của Claude Code (`~/.claude/projects/`, một file `.jsonl` cho phiên này). Prompt đầy đủ trích được bằng cách lọc các dòng có `"type": "user"` và nội dung là văn bản. Commit của TV2 ghi tác giả "Quang Tien".
