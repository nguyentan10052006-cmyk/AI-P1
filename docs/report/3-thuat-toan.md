## 3. Các thuật toán tìm kiếm

Bốn thuật toán được cài trong `Source/solvers/`. Mỗi thuật toán là một lớp con của `Solver`, có hàm `search(problem)` nhận một `Problem` (chương 2) và trả về một `SearchResult` gồm kết quả (`solved`, `no_solution`), đường đi, tổng chi phí và bốn số đếm: nút mở rộng, nút sinh, biên lớn nhất, trạng thái đã thăm. Nhờ hợp đồng chung này, giao diện (chương 4) và script thực nghiệm (chương 5) gọi bốn thuật toán theo cùng một cách.

Cả bốn thuật toán được nhóm tự viết, chỉ dùng cấu trúc dữ liệu của thư viện chuẩn Python (`collections.deque`, `list`, `heapq`), không dùng thư viện tìm kiếm có sẵn. Cả bốn đều là tìm kiếm trên đồ thị (mục 2.9) và duyệt hành động theo cùng một thứ tự cố định (mục 2.4). Bảng 3.1 tóm tắt điểm giống và khác nhau; mỗi mục 3.1 đến 3.4 trình bày ý tưởng, mã giả, tính đầy đủ, tính tối ưu, độ phức tạp và các điểm riêng khi cài đặt.

**Bảng 3.1.** Tóm tắt bốn thuật toán.

| Thuật toán | Biên | Kiểm tra đích | Tránh lặp | Đầy đủ | Tối ưu | Mục |
|---|---|---|---|---|---|---|
| BFS | hàng đợi FIFO (`deque`) | khi sinh nút | tập đã thăm | có | theo số bước | 3.1 |
| DFS | ngăn xếp (`list`) | khi sinh nút | tập đã thăm | có (không gian hữu hạn) | không | 3.2 |
| UCS | hàng đợi ưu tiên theo $g$ (`heapq`) | khi lấy ra | bảng `best_g` | có | theo tổng chi phí | 3.3 |
| A* | hàng đợi ưu tiên theo $f = g + h$ (`heapq`) | khi lấy ra | bảng `best_g` | có | theo tổng chi phí ($h$ chấp nhận được) | 3.4 |
