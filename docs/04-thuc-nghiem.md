# Thực nghiệm: đo gì, đo thế nào, trình bày ra sao

Phần thực nghiệm chiếm 20/100 điểm. TV2 chủ trì: viết script, chạy, vẽ biểu đồ. Chủ của 4 thuật toán phải đếm chỉ số đúng quy ước ở mục 3 và viết nhận xét cho thuật toán của mình.

## 1. Thực nghiệm phải trả lời được

1. Thuật toán nào tốn ít công nhất (số nút), nhanh nhất, ít bộ nhớ nhất? Khác biệt thay đổi thế nào theo nhóm màn G1–G5?
2. Chất lượng lời giải: số bước và tổng chi phí so với tối ưu.
3. Công tắc, cầu và tách khối làm không gian trạng thái lớn lên bao nhiêu?
4. Heuristic của A* cắt bớt được bao nhiêu nút so với UCS?

## 2. Các chỉ số

Đề bắt buộc 4 chỉ số: thời gian tìm kiếm, bộ nhớ đỉnh, số nút mở rộng, độ dài lời giải. Nhóm đo thêm 5 chỉ số để giải thích kết quả.

| # | Chỉ số | Cột CSV | Định nghĩa | Đơn vị |
|---|---|---|---|---|
| 1 | Số bước | `steps` | Số lần lăn trong lời giải, gồm cả bước của khối con. Đổi khối không tính | bước |
| 2 | Tổng chi phí | `path_cost` | Tổng chi phí các bước theo hàm chi phí của UCS. Tính cho **cả 4** thuật toán bằng cùng một hàm để so chất lượng lời giải | đơn vị chi phí |
| 3 | Số nút mở rộng | `expanded` | Số trạng thái được lấy ra khỏi frontier rồi sinh con | nút |
| 4 | Số nút sinh ra | `generated` | Số trạng thái con hợp lệ được tạo ra, tính cả trạng thái trùng (đếm trước khi kiểm tra tập đã thăm) | nút |
| 5 | Frontier lớn nhất | `max_frontier` | Số phần tử lớn nhất từng có trong frontier (hàng đợi, ngăn xếp hoặc hàng đợi ưu tiên). Với IDS: lớn nhất qua mọi vòng | phần tử |
| 6 | Số trạng thái đã thăm | `visited` | Kích thước tập đã thăm lúc kết thúc | trạng thái |
| 7 | Bộ nhớ đỉnh | `peak_mem_kb` | Đỉnh bộ nhớ Python cấp phát trong `prepare()` và `search()`, đo bằng `tracemalloc` ở một lần chạy riêng | KB |
| 8 | Thời gian tìm kiếm | `search_ms` | Thời gian chạy `search()`: vòng lặp tìm kiếm và dựng đường đi. Lấy trung vị 5 lần | ms |
| 9 | Tổng thời gian | `total_ms` | Từ lúc bắt đầu đọc file màn tới khi có lời giải: nạp màn, dựng bài toán, `prepare()` (ví dụ dựng bảng heuristic), `search()`. Không gồm bước phát lại kiểm tra và GUI. Lấy trung vị 5 lần | ms |
| 10 | Kết quả | `status` | `solved`, `no_solution`, `timeout` hoặc `invalid` (lời giải phát lại không tới đích) | |

Tổng thời gian trừ thời gian tìm kiếm cho thấy chi phí chuẩn bị. Phần này gần như bằng nhau ở BFS, DFS và UCS; ở A* nó lớn hơn nếu heuristic cần dựng bảng trước.

Chỉ số tùy chọn cho phần nhận xét heuristic: hệ số phân nhánh hiệu dụng b\*, là nghiệm của N + 1 = 1 + b\* + (b\*)² + … + (b\*)^d, với N là số nút sinh ra và d là số bước của lời giải (theo sách của Russell và Norvig).

## 3. Quy ước đếm (bắt buộc giống nhau ở 4 thuật toán)

- `expanded += 1` ngay sau khi lấy một trạng thái ra khỏi frontier và chuẩn bị sinh con của nó. Mục bị bỏ qua thì không tính: ở UCS và A* là mục cũ có g lớn hơn `best_g`; ở DFS là trạng thái đã thăm.
- `generated += 1` cho mỗi trạng thái con hợp lệ (đã loại hành động làm khối rơi), đếm trước khi kiểm tra tập đã thăm.
- `max_frontier = max(max_frontier, len(frontier))` sau mỗi lần thêm vào frontier. UCS và A* dùng lazy deletion nên `len(heap)` tính cả mục cũ; ghi rõ điều này trong báo cáo.
- Thời điểm kiểm tra đích:
  - BFS: khi sinh nút (early goal test).
  - DFS: khi sinh nút.
  - UCS và A*: khi lấy ra khỏi hàng đợi. Bắt buộc, để lời giải tối ưu.

  Ghi rõ trong báo cáo, vì lựa chọn này làm thay đổi số nút mở rộng.
- Thứ tự hành động giống nhau ở mọi thuật toán: U, D, L, R; khi đã tách: U1, D1, L1, R1, U2, D2, L2, R2.
- `steps = len(path)`; `path_cost` là tổng `step_cost` dọc đường đi.

## 4. Cách đo

**Điều kiện chung**
- Toàn bộ số liệu chính thức chạy trên **một máy**, trong một lần. Ghi lại CPU, RAM, hệ điều hành, phiên bản Python và mã commit Git.
- Mỗi cặp (màn, thuật toán) chạy trong một tiến trình riêng (`multiprocessing`). Nhờ vậy timeout dừng được an toàn và bộ nhớ không dồn sang lần chạy sau. Timeout là 60 giây mỗi lần chạy.
- Tắt các ứng dụng nặng, cắm sạc máy.

**Thời gian:** dùng `time.perf_counter_ns()`, chạy 5 lần, lấy trung vị. Gọi `gc.collect()` trước mỗi lần. Không bật `tracemalloc` khi đo thời gian, vì nó làm chương trình chậm đi đáng kể.

**Bộ nhớ:** chạy thêm một lần riêng. Gọi `tracemalloc.start()` ngay trước `prepare()`, đọc `tracemalloc.get_traced_memory()[1]` (giá trị đỉnh) ngay sau `search()`.

**Kiểm tra lời giải:** phát lại `path` bằng engine từ trạng thái đầu; phải tới đích, và tính lại `path_cost`. Lời giải sai thì ghi `status = invalid`, báo chủ thuật toán, không đưa vào bảng.

**Lưu ý vì màn gốc nhỏ:** bộ giải tham khảo giải mọi màn dưới 50 ms và gặp nhiều nhất khoảng 5.100 trạng thái. Thời gian chỉ vài mili-giây nên rất dễ nhiễu. Vì vậy:
- Lấy trung vị 5 lần, ghi 2 chữ số thập phân.
- Dùng **số nút mở rộng** làm chỉ số chính khi so sánh; thời gian và bộ nhớ là chỉ số phụ.
- IDS (nếu chọn) có thể timeout ở màn dài. Ghi `timeout`; đó cũng là một kết quả để nhận xét.

**Khung hàm đo một lần chạy** (TV2 phát triển tiếp):

```python
import gc, time, tracemalloc

def run_once(level_path, solver_cls, measure_memory=False):
    gc.collect()
    t0 = time.perf_counter_ns()
    problem = Problem(load_level(level_path))
    solver = solver_cls()
    if measure_memory:
        tracemalloc.start()
    solver.prepare(problem)
    t1 = time.perf_counter_ns()
    result = solver.search(problem)
    t2 = time.perf_counter_ns()
    peak_kb = None
    if measure_memory:
        peak_kb = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()
    return result, (t2 - t1) / 1e6, (t2 - t0) / 1e6, peak_kb   # search_ms, total_ms
```

Lần chạy có `measure_memory=True` chỉ lấy `peak_kb`, bỏ số đo thời gian của lần đó.

## 5. File kết quả

- `Source/experiments/raw.csv`: một dòng cho mỗi lần chạy, để kiểm tra lại khi cần.
- `Source/experiments/summary.csv`: một dòng cho mỗi cặp (màn, thuật toán), đã lấy trung vị. File này được nhập vào tab ThucNghiem của Google Sheet và dùng để vẽ biểu đồ.

Cột của `summary.csv`:

```
level,passcode,group,algorithm,status,steps,path_cost,expanded,generated,max_frontier,visited,peak_mem_kb,search_ms,total_ms,commit
```

## 6. Kiểm tra chéo trước khi dùng số liệu

Làm ở M2 với số liệu nháp và làm lại ở M3. Một dòng sai là dấu hiệu có lỗi trong engine hoặc thuật toán; sửa xong mới đưa số liệu vào báo cáo.

- [ ] Mọi lời giải phát lại đều tới đích.
- [ ] `steps` của BFS bằng cột "Bước tối ưu" ([03 §4](03-man-choi.md#4-danh-sách-33-màn)) ở cả 33 màn.
- [ ] `steps` của DFS, UCS và A* không nhỏ hơn `steps` của BFS.
- [ ] `path_cost` của UCS bằng A* ở mọi màn (chênh lệch nhỏ hơn 1e-9).
- [ ] `path_cost` của BFS và DFS không nhỏ hơn của UCS.
- [ ] `expanded` của A* không lớn hơn UCS. Nếu sai ở vài màn, kiểm tra cách phá hòa trước khi kết luận.
- [ ] Đặt mọi chi phí bằng 1 thì `steps` của UCS bằng BFS.

## 7. Trình bày trong báo cáo

### 7.1 Bảng

| Bảng | Nội dung |
|---|---|
| T1 · Thiết lập | Máy, hệ điều hành, phiên bản Python, số lần lặp, timeout, cách đo thời gian và bộ nhớ |
| T2 · Bộ màn | 5 nhóm G1–G5: mô tả, số màn, các màn (lấy từ [03 §5](03-man-choi.md#5-nhóm-độ-khó)) |
| T3 · Tổng hợp theo nhóm | Hàng là nhóm G1–G5, cột là 4 thuật toán, mỗi ô là trung vị của một chỉ số. Làm 3 bảng nhỏ: số nút mở rộng, thời gian tìm kiếm, bộ nhớ đỉnh |
| T4 · Chất lượng lời giải | Với mỗi thuật toán: số màn giải được, số màn tối ưu về số bước, số màn tối ưu về chi phí, số bước trung bình so với tối ưu (%) |
| Phụ lục A | Bảng đầy đủ 33 màn × 4 thuật toán, mọi chỉ số |

Mẫu bảng T3 (mỗi ô là trung vị số nút mở rộng):

| Nhóm | Số màn | BFS | DFS | UCS | A* |
|---|---|---|---|---|---|
| G1 Cơ bản | 3 | … | … | … | … |
| G2 Ô dễ vỡ | 2 | … | … | … | … |
| G3 Công tắc và cầu | 15 | … | … | … | … |
| G4 Ô dễ vỡ và công tắc | 3 | … | … | … | … |
| G5 Tách khối | 10 | … | … | … | … |

### 7.2 Biểu đồ

Vẽ bằng matplotlib. Mỗi thuật toán giữ **một màu cố định** trong mọi hình.

| Hình | Loại | Trục ngang | Trục dọc | Muốn cho thấy |
|---|---|---|---|---|
| H1 | Cột nhóm | Màn 1–33, xếp theo nhóm G1–G5 | Số nút mở rộng (thang log) | Công tìm kiếm của 4 thuật toán trên từng màn |
| H2 | Cột nhóm | Màn | Thời gian tìm kiếm, ms (thang log) | Thời gian có tăng theo số nút không |
| H3 | Cột nhóm | Màn | Bộ nhớ đỉnh, KB (thang log) | Frontier và tập đã thăm lớn thì bộ nhớ lớn |
| H4 | Cột | Màn | Số bước DFS / số bước tối ưu | DFS dài hơn tối ưu bao nhiêu lần |
| H5 | Cột | Màn | Số nút A* / số nút UCS | Heuristic cắt bớt bao nhiêu |
| H6 | Cột nhóm | Nhóm G1–G5 | Trung vị số nút mở rộng | Loại màn tác động tới độ khó ra sao |
| H7 (tùy chọn) | Điểm | Số nút mở rộng | Thời gian tìm kiếm | Thời gian xử lý một nút của từng thuật toán |

Quy tắc vẽ:
- Dùng thang log khi giá trị lớn nhất gấp hơn 100 lần giá trị nhỏ nhất.
- Trục nào cũng ghi tên và đơn vị.
- Mỗi hình có số thứ tự và một câu chú thích nói kết luận chính. Ví dụ: "Hình 5. A* mở rộng ít hơn UCS ở mọi màn; mức giảm lớn nhất ở nhóm G5".

### 7.3 Nhận xét

Mỗi nhận xét viết theo ba bước:
1. **Quan sát:** nêu số liệu, dẫn đúng bảng hoặc hình.
2. **Giải thích:** vì sao, dựa trên lý thuyết của thuật toán.
3. **Ý nghĩa:** nên dùng thuật toán nào, khi nào.

Câu mẫu: "Trên nhóm G5, A* mở rộng trung vị … nút, bằng …% của UCS (Hình 5). Nguyên nhân là heuristic … loại bớt các trạng thái …. Vì vậy, với màn có tách khối, …"

Câu hỏi gợi ý cho từng chủ thuật toán (mục 5.4 của báo cáo):
- **BFS (TV1):** số bước luôn tối ưu; số nút và bộ nhớ thay đổi thế nào khi màn có nhiều cầu?
- **DFS (TV2):** nhanh hay chậm so với BFS? Lời giải dài gấp bao nhiêu lần? Thứ tự hành động ảnh hưởng ra sao?
- **UCS (TV3):** ở màn nào lời giải của UCS khác BFS (cùng số bước nhưng rẻ hơn, hoặc nhiều bước hơn nhưng rẻ hơn), và vì sao?
- **A\* (TV4):** A* giảm được bao nhiêu nút so với UCS? Thời gian xử lý mỗi nút tăng bao nhiêu do tính heuristic? Có đáng không?
