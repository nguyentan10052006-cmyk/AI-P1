# Bản nháp báo cáo (TV4 ghép, V35)

Thư mục này chứa nháp từng chương theo khung ở [06 §1](../06-bao-cao-video.md#1-khung-báo-cáo). Tab bien-ban #6 (ngôn ngữ và công cụ viết báo cáo) **chưa chốt**, nên nháp viết bằng Markdown, tiếng Việt, theo bộ thuật ngữ ở 06 §2. Công thức viết kiểu `$...$` (GitHub hiển thị được). Khi nhóm chốt công cụ (LaTeX, Word hoặc Google Docs), TV4 chuyển các file này sang một lần.

Mỗi người viết chương của mình thành một file ở đây (hoặc gửi TV4), đặt tên theo số chương. Hạn: chương của từng người 27/10; chương Thực nghiệm và các đoạn nhận xét 28/10; bản ghép 28/10; rà soát 29/10; PDF 30/10 (01 NV11).

| Phần | File | Người viết | Trạng thái |
|---|---|---|---|
| Bìa | (khi ghép) | TV4 | Chờ tên, MSSV và link video |
| 1. Phân công và tiến độ | [1-phan-cong.md](1-phan-cong.md) | TV4 | Khung; chờ tên và % chốt ngày 29/10 |
| 2. Trò chơi và mô hình hóa | [2-mo-hinh-hoa.md](2-mo-hinh-hoa.md) | TV1 (phần cầu: TV3) | **Đủ mục** (2.1–2.10, kể cả phần cầu và công tắc ở 2.2) |
| 3.1 BFS | [3.1-bfs.md](3.1-bfs.md) | TV1 | **Đủ mục** |
| 3.2 DFS | `3.2-dfs.md` | TV2 | Chưa có |
| 3.3 UCS và hàm chi phí | `3.3-ucs.md` | TV3 | Chưa có |
| 3.4 A* và heuristic | [3.4-astar.md](3.4-astar.md) | TV4 | **Nháp đủ mục**; cập nhật số liệu sau khi chốt hàm chi phí (V13) |
| 4. Cài đặt và giao diện | [4-cai-dat-giao-dien.md](4-cai-dat-giao-dien.md) | TV5 | **Nháp đủ mục**, 11 hình (chụp lại ngày 31/10 trên nhánh chính, hàm chi phí V13; thêm Hình 4.11 bảng chú giải) |
| 5.1–5.3, 5.5 Thực nghiệm | `5-thuc-nghiem.md` | TV2 | Chưa có |
| 5.4 Nhận xét A* | [5.4-nhan-xet-astar.md](5.4-nhan-xet-astar.md) | TV4 | Nháp với số liệu tạm; thay bằng số liệu chính thức của TV2 |
| 5.4.1 Nhận xét BFS | [5.4-nhan-xet-bfs.md](5.4-nhan-xet-bfs.md) | TV1 | **Đủ mục**, số liệu chạy ngày 30/10 (commit 44dc9e3) |
| 5.4 Nhận xét DFS, UCS | | TV2, TV3 | DFS: xem file 5.4-nhan-xet-dfs.md; UCS: chưa có |
| 6. Kết luận | [6-ket-luan.md](6-ket-luan.md) | TV4 | Khung |
| Tài liệu tham khảo | [tai-lieu-tham-khao.md](tai-lieu-tham-khao.md) | TV4 gom | Đủ 8 nguồn ở 06 §3 và tab cite |
| Phụ lục A: bảng kết quả đầy đủ | | TV2 | Chưa có |
| Phụ lục B: dùng AI | [phu-luc-b-ai.md](phu-luc-b-ai.md) | Mọi người viết, TV4 gom | Khung; đã có phần TV1 ([phu-luc-b-tv1.md](phu-luc-b-tv1.md)), TV2, TV5 |

**Trước khi nộp** (06 §4, §6): tìm "con mèo" và "quantum cat" trong toàn bộ báo cáo; đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn câu này. Kiểm tra mọi hình, bảng có số và chú thích; mọi nguồn có trong danh mục.
