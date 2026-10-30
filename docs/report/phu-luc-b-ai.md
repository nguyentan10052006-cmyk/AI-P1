## Phụ lục B. Sử dụng công cụ AI

> Khung của TV4 (V35), 26/10. Mỗi người tự viết phần mình dựa trên tab prompt-ai (`docs/sheet/6-prompt-ai.csv`), dán prompt gốc vào sheet; TV4 gom lại khi ghép. Đề yêu cầu nêu rõ công cụ, prompt và AI được dùng vào đâu (đề, mục 3.6).

### B.1. Công cụ

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic) | Soạn bộ tài liệu `docs/` (19/10); TV4 (20–26/10) | Xem B.2 |
| *(bổ sung)* | | |

### B.2. Việc dùng AI theo từng thành viên

**Bộ tài liệu nhóm (19/10).** Bộ tài liệu `docs/01`–`06` được soạn với sự hỗ trợ của Claude: phân công PA2, luật chơi chuẩn, đối chiếu dữ liệu 33 màn gốc từ bốn nguồn và cột "Bước tối ưu", cân bằng lại phân công ngày 19/10 (06 §4). Nhóm kiểm tra lại bằng BFS của nhóm: 33/33 màn khớp cột "Bước tối ưu" (test T24).

**TV4.** Dùng Claude Code để viết code và nháp báo cáo cho các việc sau; mọi kết quả đều được kiểm tra bằng test và công cụ đo trước khi gộp:

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 20/10 | Hai biến thể A* (`astar`, `astar_m`); vẽ mê cung mẫu | `solvers/astar.py`, `tools/draw_mazes.py`, `docs/gridmaze/` | Toàn bộ test; xem ảnh SVG |
| 20/10 | A* trên mê cung (V15), module chạy nền không chặn (V39) | `solvers/astar.py`, `solvers/heuristics.py`, `solvers/runner.py` | Test trên mê cung có đáp án; test runner với tiến trình con thật |
| 23/10 | $h_P$ cho Bloxorz (V16), A* trên 33 màn (V17) | `solvers/heuristics.py`, `tools/check_heuristics.py` | 0 vi phạm trên 340 414 cạnh; cùng chi phí với UCS ở 33/33 màn |
| 26/10 | Nháp chương 3.4, mục 5.4 (A*), khung chương 1, 6, tài liệu tham khảo | `docs/report/` | TV4 đọc lại từng bước chứng minh; số liệu lấy từ công cụ đo |

*(TV1, TV2, TV3, TV5 bổ sung phần của mình theo cùng mẫu.)*

### B.3. Nguyên tắc nhóm áp dụng

- Ghi vào tab prompt-ai ngay khi dùng (06 §4).
- Không đưa vào báo cáo kết quả nào của AI mà chưa kiểm tra lại bằng code, test hoặc số liệu đo.
- Đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn một câu cố định vào báo cáo; nhóm đã tìm và bảo đảm câu đó không có trong báo cáo (06 §4).
