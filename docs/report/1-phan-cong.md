## 1. Phân công và tiến độ

> Khung của TV4 (V35), 26/10. Bảng việc sinh từ tab task (`docs/sheet/1-viec.csv`). Ngày 29/10 cả nhóm chốt cột Trạng thái và % hoàn thành trên Google Sheet (01 §8); khi đó điền họ tên, MSSV, cột % và cột Trạng thái ở đây.

### 1.1. Cách chia việc

Nhóm chia việc theo phương án PA2 (bien-ban #1): mỗi thành viên phụ trách một thuật toán (BFS, DFS, UCS, A*), một thành viên làm giao diện 3D. Phần dùng chung (luật chơi, màn chơi, thực nghiệm, báo cáo) chia thành 14 nhóm việc, mỗi nhóm có một người chủ và một người đọc chéo. Ngày 19/10 nhóm cân bằng lại khối lượng giữa các thành viên (bien-ban #12). Tiến độ theo dõi trên Google Sheets (bien-ban #8): mỗi tối thành viên check-in; mỗi mốc (M1 21/10, M2 25/10, M3 28/10) mọi người gộp code vào nhánh chính và demo trên nhánh chính.

**Bảng 1.1.** Vai trò của từng thành viên.

| Mã | Họ tên | MSSV | Thuật toán | Phần chung phụ trách | Chương báo cáo | Đọc chéo cho | % hoàn thành |
|---|---|---|---|---|---|---|---|
| TV1 | … | … | BFS | NV1: hợp đồng chung, engine lõi, ghép module; NV3: tách và ghép khối; NV13: kiểm thử cài đặt, đóng gói | 2. Mô hình hóa; 3.1 BFS | TV2 | … |
| TV2 | … | … | DFS hoặc IDS | NV4: 33 màn gốc; NV10: thực nghiệm (trừ bộ màn tự sinh) | 3.2 DFS; 5. Thực nghiệm | TV5 | … |
| TV3 | … | … | UCS | NV2: ô dễ vỡ, công tắc, cầu; hàm chi phí; bộ nạp màn (V03); bộ màn tự sinh (V40); NV12: video | 3.3 UCS | TV1 | … |
| TV4 | … | … | A* | Heuristic; module chạy solver nền và So sánh cho GUI (V39); NV11: ghép báo cáo | 3.4 A*; 1. Phân công; 6. Kết luận | TV3 | … |
| TV5 | … | … | (không) | NV9: GUI 3D (trừ module chạy solver nền), README | 4. Cài đặt và giao diện | TV4 | … |

### 1.2. Cách tính % hoàn thành

Điểm cá nhân bằng điểm nhóm nhân % hoàn thành (đề, mục 3.6), nên % tính từ bảng việc, không theo cảm giác (bien-ban #13). Mỗi việc nhận mức theo trạng thái: Chưa bắt đầu 0 %, Đã bắt đầu 50 %, Hoàn thành 100 %. % của một thành viên là trung bình mức của các việc người đó làm. Một việc chỉ được chọn Hoàn thành khi code đã ở nhánh chính, test của phần đó qua và người đọc chéo đã xem (01 §7).

### 1.3. Bảng việc

**Bảng 1.2.** Việc của TV1 (10 việc).

| ID | Việc | Mốc | Hạn | Đọc chéo | Trạng thái |
|---|---|---|---|---|---|
| V01 | Chốt hợp đồng chung (State, Problem, Solver, SearchResult) và GridMaze; đẩy khung code lên nhánh chính | M1 | 2026-10-19 | TV3 | Chưa bắt đầu |
| V02 | Engine lõi: bảng chuyển 12 trường hợp, rơi, thắng | M1 | 2026-10-20 | TV3 | Chưa bắt đầu |
| V04 | Ghép ô đặc biệt và tách khối vào result(); chạy lại toàn bộ test | M2 | 2026-10-24 | TV3 | Chưa bắt đầu |
| V06 | Công tắc tách, điều khiển 2 khối con, ghép khi kề | M2 | 2026-10-23 | TV3 | Chưa bắt đầu |
| V08 | BFS và đếm chỉ số theo docs/04 | M1 | 2026-10-21 | TV3 | Chưa bắt đầu |
| V09 | BFS giải đủ 33 màn | M2 | 2026-10-25 | TV3 | Chưa bắt đầu |
| V26 | Chương 2 Mô hình hóa bài toán và 3.1 BFS | M3 | 2026-10-27 | TV3 | Chưa bắt đầu |
| V31 | Nhận xét kết quả BFS (mục 5.4) | M3 | 2026-10-28 | TV3 | Chưa bắt đầu |
| V37 | Kiểm thử cài đặt theo README trên máy khác | Nộp | 2026-10-29 | TV3 | Chưa bắt đầu |
| V38 | Đóng gói file nộp MSSV1_MSSV2_….zip | Nộp | 2026-10-30 | TV3 | Chưa bắt đầu |

**Bảng 1.3.** Việc của TV2 (8 việc).

| ID | Việc | Mốc | Hạn | Đọc chéo | Trạng thái |
|---|---|---|---|---|---|
| V07 | Định dạng file màn và script chuyển 33 màn gốc (sửa màn 3) | M1 | 2026-10-20 | TV1 | Chưa bắt đầu |
| V10 | DFS (hoặc IDS) có tập đã thăm, thứ tự hành động cố định | M1 | 2026-10-21 | TV1 | Chưa bắt đầu |
| V11 | DFS giải đủ 33 màn | M2 | 2026-10-25 | TV1 | Chưa bắt đầu |
| V23 | Script đo: thời gian, bộ nhớ, timeout, xuất CSV | M2 | 2026-10-24 | TV1 | Chưa bắt đầu |
| V24 | Chạy thử 4 thuật toán × 33 màn, thêm A* với h_M và bộ màn tự sinh (số liệu nháp) | M2 | 2026-10-25 | TV1 | Chưa bắt đầu |
| V25 | Chạy chính thức; bảng và biểu đồ | M3 | 2026-10-27 | TV1 | Chưa bắt đầu |
| V27 | Chương 3.2 DFS và chương 5 Thực nghiệm (5.1–5.3, 5.5) | M3 | 2026-10-28 | TV1 | Chưa bắt đầu |
| V32 | Nhận xét kết quả DFS (mục 5.4) | M3 | 2026-10-28 | TV1 | Chưa bắt đầu |

**Bảng 1.4.** Việc của TV3 (9 việc).

| ID | Việc | Mốc | Hạn | Đọc chéo | Trạng thái |
|---|---|---|---|---|---|
| V03 | Bộ nạp màn và kiểm tra hợp lệ file màn | M1 | 2026-10-21 | TV4 | Chưa bắt đầu |
| V05 | Ô dễ vỡ, cầu, công tắc mềm và nặng (toggle, on, off), trạng thái cầu | M2 | 2026-10-23 | TV4 | Chưa bắt đầu |
| V12 | UCS (heapq) đúng trên mê cung có trọng số | M1 | 2026-10-21 | TV4 | Chưa bắt đầu |
| V13 | Hàm chi phí không đồng nhất và lý do; gửi TV4 | M2 | 2026-10-22 | TV4 | Chưa bắt đầu |
| V14 | UCS giải đủ 33 màn | M2 | 2026-10-25 | TV4 | Chưa bắt đầu |
| V28 | Chương 3.3 UCS và hàm chi phí | M3 | 2026-10-27 | TV4 | Chưa bắt đầu |
| V33 | Nhận xét kết quả UCS (mục 5.4) | M3 | 2026-10-28 | TV4 | Chưa bắt đầu |
| V36 | Kịch bản, quay, phụ đề, đăng YouTube công khai | Nộp | 2026-10-29 | TV4 | Chưa bắt đầu |
| V40 | Bộ màn tự sinh S1–S3 (gen_levels.py), dùng BFS kiểm tra | M2 | 2026-10-24 | TV4 | Chưa bắt đầu |

**Bảng 1.5.** Việc của TV4 (7 việc).

| ID | Việc | Mốc | Hạn | Đọc chéo | Trạng thái |
|---|---|---|---|---|---|
| V15 | A* đúng trên mê cung (h = Manhattan) | M1 | 2026-10-21 | TV5 | Chưa bắt đầu |
| V16 | Heuristic h_M và h_P chấp nhận được với hàm chi phí của TV3 (cả trạng thái đã tách) | M2 | 2026-10-24 | TV5 | Chưa bắt đầu |
| V17 | A* giải đủ 33 màn | M2 | 2026-10-25 | TV5 | Chưa bắt đầu |
| V29 | Chương 3.4 A*, heuristic và chứng minh | M3 | 2026-10-27 | TV5 | Chưa bắt đầu |
| V34 | Nhận xét kết quả A* (mục 5.4) | M3 | 2026-10-28 | TV5 | Chưa bắt đầu |
| V35 | Ghép báo cáo; chương 1 Phân công; chương 6; tài liệu tham khảo; phụ lục AI; xuất PDF | Nộp | 2026-10-30 | TV5 | Chưa bắt đầu |
| V39 | Module chạy solver ở tiến trình riêng cho GUI: Hủy, hết giờ 60 giây, chạy So sánh 4 thuật toán | M2 | 2026-10-23 | TV5 | Chưa bắt đầu |

**Bảng 1.6.** Việc của TV5 (6 việc).

| ID | Việc | Mốc | Hạn | Đọc chéo | Trạng thái |
|---|---|---|---|---|---|
| V18 | Chọn công nghệ 3D; vẽ bàn từ file màn | M1 | 2026-10-21 | TV2 | Chưa bắt đầu |
| V19 | Chơi tay bằng engine thật (lăn, rơi, thắng) | M1 | 2026-10-21 | TV2 | Chưa bắt đầu |
| V20 | Hiển thị ô đặc biệt, cầu, tách khối; Space đổi khối | M2 | 2026-10-24 | TV2 | Chưa bắt đầu |
| V21 | New Game, Restart, chọn 33 màn, 4 nút Solve, nút So sánh và nút Hủy (gọi module V39), khối tự lăn, thông báo 4 kết quả | M2 | 2026-10-25 | TV2 | Chưa bắt đầu |
| V22 | main.py, README, requirements.txt | M3 | 2026-10-27 | TV2 | Chưa bắt đầu |
| V30 | Chương 4 Cài đặt và giao diện | M3 | 2026-10-27 | TV2 | Chưa bắt đầu |
