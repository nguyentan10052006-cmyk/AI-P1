# Báo cáo (bản Markdown)

Thư mục này chứa nội dung báo cáo, mỗi phần một file, viết bằng tiếng Việt theo bộ thuật ngữ ở [06 §2](../06-bao-cao-video.md#2-quy-ước-viết). Bản nộp là [Report.pdf](Report.pdf), dựng từ các file này bằng pandoc và XeLaTeX trong thư mục [latex/](latex/) (cách dựng lại ở [latex/README.md](latex/README.md)), theo thứ tự trong bảng dưới; mục 5.4 (bốn file `5.4-nhan-xet-*.md`) được chèn vào giữa mục 5.3 và 5.5 của `5-thuc-nghiem.md`.

| Thứ tự | Phần | File |
|---|---|---|
| 1 | Tóm tắt | [0-tom-tat.md](0-tom-tat.md) |
| 2 | 1. Phân công và tiến độ | [1-phan-cong.md](1-phan-cong.md) |
| 3 | 2. Trò chơi và mô hình hóa | [2-mo-hinh-hoa.md](2-mo-hinh-hoa.md) |
| 4 | 3. Các thuật toán tìm kiếm (mở đầu) | [3-thuat-toan.md](3-thuat-toan.md) |
| 5 | 3.1 BFS, 3.2 DFS, 3.3 UCS và hàm chi phí, 3.4 A* | [3.1-bfs.md](3.1-bfs.md), [3.2-dfs.md](3.2-dfs.md), [3.3-ucs.md](3.3-ucs.md), [3.4-astar.md](3.4-astar.md) |
| 6 | 4. Cài đặt và giao diện | [4-cai-dat-giao-dien.md](4-cai-dat-giao-dien.md) |
| 7 | 5. Thực nghiệm (5.1–5.3, 5.5) | [5-thuc-nghiem.md](5-thuc-nghiem.md) |
| 8 | 5.4.1–5.4.4 Nhận xét BFS, DFS, UCS, A* | [5.4-nhan-xet-bfs.md](5.4-nhan-xet-bfs.md), [5.4-nhan-xet-dfs.md](5.4-nhan-xet-dfs.md), [5.4-nhan-xet-ucs.md](5.4-nhan-xet-ucs.md), [5.4-nhan-xet-astar.md](5.4-nhan-xet-astar.md) |
| 9 | 6. Kết luận | [6-ket-luan.md](6-ket-luan.md) |
| 10 | Tài liệu tham khảo | [tai-lieu-tham-khao.md](tai-lieu-tham-khao.md) |
| 11 | Phụ lục A. Kết quả thực nghiệm đầy đủ | [phu-luc-a-ket-qua.md](phu-luc-a-ket-qua.md) |
| 12 | Phụ lục B. Sử dụng công cụ AI | [phu-luc-b-ai.md](phu-luc-b-ai.md) (đã gộp phần của TV1, TV2, TV4, TV5 từ các file `phu-luc-b-tv*.md`) |

Quy ước khi sửa:

- Mọi số liệu thực nghiệm lấy từ lần đo chính thức `Source/experiments/benchmark-2026-10-31-0a35afd/` (hàm chi phí ở Bảng 3.3.1, bước tách khối 1,62).
- Chú thích bảng viết thành đoạn `**Bảng x.y.** …` ngay trên bảng; chú thích hình viết thành đoạn `*Hình x.y. …*` ngay dưới hình.
- Chỗ còn phải điền viết `[nội dung]{.dien}`; trong PDF hiện chữ đỏ.
- Danh sách phải cách đoạn trước bằng một dòng trống hoặc bắt đầu ngay dòng sau, cả hai đều được.

**Trước khi nộp** (06 §4, §6): tìm "con mèo" và "quantum cat" trong toàn bộ báo cáo; đề bài có một dòng chữ ẩn yêu cầu công cụ AI chèn câu này. Kiểm tra bìa có link video YouTube công khai.
