## 5. Thực nghiệm

> Nháp của TV2 (V27), 28/10. Trạng thái từng mục:
> - **5.1 Thiết lập, 5.2 Bộ màn:** viết đủ theo code và tài liệu hiện có. Còn trống các ô ghi *(điền từ `run_info.json`)*: lấy từ lần chạy chính thức.
> - **5.3 Kết quả, 5.5 Kết luận:** chỉ có khung. **Chưa có số liệu chính thức**, vì còn chờ:
>   - hàm chi phí của UCS (V13, mục 3.3): TV3 đã cài `bloxorz/costs.py` trên nhánh `feature/trong/V12-ucs`, nhưng chưa vào nhánh chính và chưa được dùng mặc định khi chạy;
>   - bộ nạp màn có `links` (V03), UCS (V12) và $h_P$ (V16) vào nhánh chính;
>   - nhóm chốt các quyết định về định dạng file kết quả.
>
>   Số liệu chạy thử ngày 28/10 chỉ dùng để kiểm tra script, **không** đưa vào chương này.
> - **5.4:** mỗi chủ thuật toán viết một đoạn (5.4.1 BFS, 5.4.2 DFS, 5.4.3 UCS, 5.4.4 A*), file riêng.

### 5.1. Thiết lập thực nghiệm

**Câu hỏi cần trả lời** (04 §1):

1. Thuật toán nào mở rộng ít nút nhất, chạy nhanh nhất, tốn ít bộ nhớ nhất, và khác biệt thay đổi thế nào theo nhóm màn G1–G5?
2. Chất lượng lời giải: số bước và tổng chi phí so với tối ưu.
3. Công tắc và cầu làm không gian trạng thái lớn lên bao nhiêu (nhóm S2)?
4. Mỗi heuristic của A* ($h_M$, $h_P$) bớt được bao nhiêu nút so với UCS?
5. Số nút, thời gian và bộ nhớ tăng thế nào khi bàn lớn dần (S1), và khi màn không có lời giải (S3)?

**Thuật toán.** Năm cấu hình, dùng chung một engine luật, một hàm chi phí và một thứ tự hành động (U, D, L, R; khi đã tách U1 … R1, U2 … R2):

| Khóa | Thuật toán | Kiểm tra đích | Chương |
|---|---|---|---|
| `bfs` | BFS | khi sinh nút | 3.1 |
| `dfs` | DFS dạng tìm kiếm trên đồ thị | khi sinh nút | 3.2 |
| `ucs` | UCS | khi lấy ra khỏi hàng đợi | 3.3 |
| `astar` | A* với $h_P$ (heuristic chính) | khi lấy ra khỏi hàng đợi | 3.4 |
| `astar_m` | A* với $h_M$ (để so sánh) | khi lấy ra khỏi hàng đợi | 3.4 |

Thời điểm kiểm tra đích làm thay đổi số nút mở rộng: BFS và DFS dừng ngay khi sinh ra đích, còn UCS và A* phải chờ tới lúc lấy đích ra để giữ tính tối ưu. Khi đọc bảng, cần nhớ điều này.

**Chỉ số.** Bốn chỉ số đề bắt buộc (thời gian tìm kiếm, bộ nhớ đỉnh, số nút mở rộng, độ dài lời giải), cộng năm chỉ số để giải thích kết quả.

**Bảng 5.1.** Các chỉ số đo (định nghĩa đầy đủ ở 04 §2, quy ước đếm ở 04 §3).

| Chỉ số | Cột trong `summary.csv` | Định nghĩa |
|---|---|---|
| Số bước | `steps` | Số lần lăn trong lời giải, gồm cả bước của khối con |
| Tổng chi phí | `path_cost` | Tổng chi phí bước dọc lời giải, theo **cùng một** hàm chi phí cho cả 5 cấu hình |
| Số nút mở rộng | `expanded` | Số trạng thái được lấy ra khỏi biên để sinh con. **Chỉ số chính khi so sánh** |
| Số nút sinh | `generated` | Số trạng thái con hợp lệ, đếm trước khi xét tập đã thăm |
| Biên lớn nhất | `max_frontier` | Số phần tử lớn nhất từng có trong biên. UCS và A* tính cả mục cũ còn trong heap (lazy deletion) |
| Trạng thái đã thăm | `visited` | Kích thước tập đã thăm lúc kết thúc |
| Bộ nhớ đỉnh | `peak_mem_kb` | Đỉnh bộ nhớ Python cấp phát trong `prepare()` và `search()`, đo bằng `tracemalloc` |
| Thời gian tìm kiếm | `search_ms` | Thời gian chạy `search()`, trung vị 5 lần |
| Tổng thời gian | `total_ms` | Từ lúc đọc file màn tới khi có lời giải: nạp màn, dựng bài toán, `prepare()`, `search()`; trung vị 5 lần |
| Kết quả | `status` | `solved`, `no_solution`, `timeout`, `invalid` |

**Cách đo.** Script `Source/experiments/run.py` (TV2, việc V23) cài đúng 04 §4:

- **Mỗi lần chạy là một tiến trình con riêng** (`multiprocessing`, kiểu `spawn`), có giới hạn 60 giây. Nhờ vậy, hết giờ thì dừng được tiến trình một cách an toàn, và bộ nhớ của lần chạy trước không dồn sang lần sau.
- **Thời gian:** đo 5 lần bằng `time.perf_counter_ns()`, gọi `gc.collect()` trước mỗi lần, **không** bật `tracemalloc`; lấy trung vị, làm tròn 2 chữ số thập phân. `tracemalloc` làm chương trình chậm đi đáng kể, nên đo thời gian khi đang bật nó thì không tách được chi phí của thuật toán khỏi chi phí của việc đo.
- **Bộ nhớ:** chạy thêm một lần riêng. `tracemalloc.start()` ngay trước `prepare()`, đọc giá trị đỉnh ngay sau `search()`; thời gian của lần này bị bỏ.
- **Kiểm tra lời giải:** sau khi đo, phát lại lời giải bằng engine từ trạng thái đầu và tính lại tổng chi phí. Không tới đích, hoặc tổng chi phí lệch với solver báo, thì ghi `invalid`. Bước phát lại nằm ngoài phần đo thời gian.
- **Nguồn gốc số liệu:** `run_info.json` ghi commit Git, cấu hình máy, các tham số chạy, mã băm sha256 của từng file màn, và đánh dấu `-dirty` nếu mã nguồn hoặc file màn khác với commit.

**Bảng 5.2.** Thiết lập của lần chạy chính thức (T1).

| Hạng mục | Giá trị |
|---|---|
| CPU, RAM | *(điền từ `run_info.json`, khóa `machine`)* |
| Hệ điều hành | *(điền từ `run_info.json`)* |
| Python | *(điền từ `run_info.json`; nhóm dùng Python 3.11, 07 §4)* |
| Commit Git | *(điền từ `run_info.json`; không được có hậu tố `-dirty`)* |
| Số lần đo thời gian | 5, lấy trung vị |
| Số lần đo bộ nhớ | 1, chạy riêng |
| Giới hạn thời gian | 60 giây mỗi lần chạy |
| Hàm chi phí | *(chờ V13, mục 3.3)* |
| Thời gian chạy toàn bộ | *(điền từ `started_utc`, `finished_utc`)* |

**Hàm chi phí.** Cột `path_cost` của cả năm cấu hình tính theo hàm chi phí của UCS (mục 3.3), để so được chất lượng lời giải. Hàm này chưa chốt, nên chương này **chưa** đưa ra kết luận nào về tổng chi phí, về việc UCS chọn đường khác BFS hay không, hay về heuristic theo hàm chi phí cuối cùng.

Riêng **số bước và các số đếm của BFS và DFS không phụ thuộc hàm chi phí**, vì hai thuật toán này không dùng chi phí khi chọn nút. Ngược lại, số liệu của UCS và A* sẽ thay đổi khi đổi hàm chi phí.

**Kiểm tra chéo trước khi dùng số liệu** (04 §6). Một dòng sai là dấu hiệu lỗi trong engine hoặc thuật toán; sửa xong mới đưa số liệu vào báo cáo.

- Mọi lời giải phát lại đều tới đích, không có dòng `invalid` hay lỗi.
- Số bước của BFS bằng cột "Bước tối ưu" (03 §4) ở cả 33 màn.
- Số bước của DFS, UCS, A* không nhỏ hơn của BFS.
- Tổng chi phí của UCS bằng A* ở mọi màn, với cả $h_M$ và $h_P$.
- Tổng chi phí của BFS và DFS không nhỏ hơn của UCS.
- Số nút mở rộng của A* không lớn hơn UCS.
- Màn không có lời giải (S3): mọi thuật toán trả `no_solution`.
- Đủ dòng (01 NV10): 33 màn gốc × 5 cấu hình cùng các màn tự sinh, không thiếu cặp nào; mọi dòng của màn gốc là `solved`, vì màn gốc nào cũng có lời giải.

Các mục trên được kiểm tự động bằng `experiments/check_results.py` (K1–K8). Kiểm tra "đặt mọi chi phí bằng 1 thì UCS bằng BFS" nằm ở test của UCS. Kiểm tra "0 vi phạm heuristic" nằm ở `tools/check_heuristics.py`.

*(Ghi kết quả kiểm tra của lần chạy chính thức ở đây: số mục đạt / tổng số mục.)*

**Chạy lại.** Trong `Source/`:

```bash
python -m experiments.run --out experiments/<thư mục>   # 5 cấu hình × các màn trong levels/original; ghi raw.csv, summary.csv, run_info.json
```

*(Bổ sung lệnh chạy cả bộ màn tự sinh, lệnh vẽ hình và lệnh kiểm tra chéo khi các script này đã vào nhánh chính.)*

### 5.2. Bộ màn

Đề yêu cầu một bộ test cố định, chia theo độ khó tăng dần và mô tả rõ trong báo cáo (đề, mục 3.6). Nhóm dùng **33 màn của game gốc** (5 nhóm G1–G5) và **14 màn tự sinh** (3 nhóm S1–S3). Bộ màn cố định cho mọi thuật toán, nên phép so sánh là công bằng.

**33 màn gốc.** 33 màn của Bloxorz [2], theo đúng thứ tự trong game. Dữ liệu chuyển tự động từ file `levels.json` của bản port bloxorz_gba [3] (commit `f57ebb6`, giấy phép GPL-3.0) bằng script `Source/experiments/convert_original_levels.py`. Có một hiệu chỉnh: màn 3 thêm 4 ô sàn mà bản port thiếu, trong khi ba nguồn đối chiếu đều có (03 §3). Test `tests/test_original_levels.py` đối chiếu từng ô và từng liên kết với dữ liệu gốc. Bàn của mọi màn là lưới 10 × 15.

Đề gợi ý bốn nhóm: không có ô đặc biệt, có ô dễ vỡ, có công tắc, và kết hợp. Nhóm tách thêm các màn có công tắc tách thành nhóm riêng (G5), vì khi khối bị tách, trạng thái gồm hai khối con và không gian trạng thái khác hẳn.

**Bảng 5.3.** Năm nhóm màn gốc (T2). "Số bước tối ưu" là lời giải ít bước nhất, lấy từ cột "Bước tối ưu" (03 §4) và được BFS của nhóm kiểm lại (test T24). Trên nhánh chính hiện T24 chạy 27 màn; 6 màn dùng `links` được kiểm khi bộ nạp màn V03 vào nhánh chính. Trên nhánh tích hợp có V03, cả 33 màn đều khớp.

| Nhóm | Mô tả | Màn | Số màn | Số bước tối ưu (nhỏ nhất – lớn nhất) |
|---|---|---|---|---|
| G1 | Cơ bản: chỉ sàn, ô trống, đích | 1, 3, 6 | 3 | 7 – 35 |
| G2 | Có ô dễ vỡ | 4, 13 | 2 | 28 – 46 |
| G3 | Có công tắc mềm hoặc nặng và cầu | 2, 5, 7, 11, 12, 14, 17, 18, 19, 21, 22, 25, 29, 32, 33 | 15 | 17 – 129 |
| G4 | Ô dễ vỡ kết hợp công tắc | 27, 30, 31 | 3 | 71 – 114 |
| G5 | Có công tắc tách | 8, 9, 10, 15, 16, 20, 23, 24, 26, 28 | 10 | 10 – 104 |

Sáu màn 17, 23, 25, 29, 30, 31 có công tắc nối nhiều ô cầu với kiểu tác động khác nhau (mở, đóng, đảo trạng thái); file màn ghi các công tắc này bằng trường `links` (03 §6).

**14 màn tự sinh.** 33 màn gốc nhỏ, thời gian giải chỉ vài mili-giây nên dễ nhiễu, và khó thấy khác biệt giữa các thuật toán. Ba nhóm màn sinh bằng script cho số liệu ở quy mô lớn hơn, mỗi nhóm trả lời một câu hỏi ở mục 5.1 (04 §8).

**Bảng 5.4.** Ba nhóm màn tự sinh.

| Nhóm | Cách dựng | Tham số | Kích thước lưới | Số bước tối ưu | Câu hỏi |
|---|---|---|---|---|---|
| S1 Sân trống | Bàn N × N toàn sàn; xuất phát ở góc trên trái (0, 0), đích ở góc dưới phải (N − 1, N − 1) | N = 10, 25, 50, 100, 150, 200 | N × N | 12, 32, 66, 132, 200, 266 | 5 |
| S2 Cầu | Lưới 8 × 12 cố định. Hàng 0 là mép ngoài: ô trống, trừ k ô cầu đóng ở cột 1 … k. k công tắc mềm ở hàng 1, cột 1 … k; mỗi công tắc đảo ô cầu ngay trên nó. Xuất phát (3, 1), đích (3, 10); đường tới đích không qua cầu | k = 0, 2, 4, 6, 8, 10 | 8 × 12 | 6 với mọi k | 3 |
| S3 Không lời giải | Vùng trái N × N chứa điểm xuất phát (1, 1), một cột ô trống, rồi vùng phải N × 3 chứa đích (1, N + 2). Khối không qua được khe rộng 1 ô, vì lăn về phía khe thì luôn có một phần khối trên ô trống | N = 10, 50 | N × (N + 4) | không có lời giải | 5 |

Ở S2, lời giải không đổi theo k, nhưng mỗi cấu hình cầu là một trạng thái khác nhau, nên số trạng thái có thể tăng tới $2^k$ lần. Đây là cách đo trực tiếp phần không gian trạng thái do cầu tạo ra.

Khi sinh, script `experiments/gen_levels.py` dùng BFS tính số bước tối ưu (`par`) của từng màn; S3 không có lời giải nên `par` = 0. Test `tests/test_gen_levels.py` kiểm đủ 14 file, cấu trúc của từng nhóm, và tính giải được của một màn đại diện mỗi nhóm. Tên file: `s1_010` … `s1_200`, `s2_00` … `s2_10`, `s3_10`, `s3_50`.

> **Nguồn của Bảng 5.4.** Bảng tả bộ màn V40 của TV3 (nhánh `feature/trong/V12-ucs`, commit `cc3fa6a`), lấy trực tiếp từ các file màn. Bộ màn này chưa vào nhánh chính; nếu TV3 đổi trước khi gộp thì sửa bảng theo. Bản tạm trước đó do TV2 viết để chạy thử script đo không còn dùng.

**Tổng cộng:** 47 màn (33 gốc + 14 tự sinh) × 5 cấu hình = 235 cặp (màn, cấu hình); mỗi cặp 5 lần đo thời gian và 1 lần đo bộ nhớ.

### 5.3. Kết quả

> **Chưa có số liệu chính thức.** Các bảng và hình dưới đây là danh sách cần điền (04 §7), kèm câu chú thích mẫu. Mỗi hình có một file CSV đi kèm chứa đúng số liệu đã vẽ, để kiểm tra lại. Không điền số từ lần chạy thử.

**Bảng cần có**

| Số | Nội dung (04 §7.1) | Trạng thái |
|---|---|---|
| Bảng 5.5 (T3a) | Trung vị số nút mở rộng theo nhóm G1–G5 × 5 cấu hình | Chờ số liệu |
| Bảng 5.6 (T3b) | Trung vị thời gian tìm kiếm theo nhóm | Chờ số liệu |
| Bảng 5.7 (T3c) | Trung vị bộ nhớ đỉnh theo nhóm | Chờ số liệu |
| Bảng 5.8 (T4) | Chất lượng lời giải: số màn giải được, số màn tối ưu về số bước, về chi phí, số bước trung bình so với tối ưu | Chờ số liệu và V13 |
| Bảng 5.9 (T5) | Heuristic: trung vị số nút mở rộng của UCS, A* $h_M$, A* $h_P$ theo nhóm; hệ số phân nhánh hiệu dụng $b^*$ | Chờ số liệu và V13 |
| Phụ lục A | Bảng đầy đủ 47 màn × 5 cấu hình, mọi chỉ số | Chờ số liệu |

**Hình cần có** (vẽ bằng matplotlib; mỗi thuật toán giữ một màu, một kiểu ký hiệu và một kiểu nét cố định trong mọi hình)

| Số | Nội dung (04 §7.2) | Thang | Câu chú thích cần có |
|---|---|---|---|
| Hình 5.1 (H1) | Số nút mở rộng trên từng màn gốc, xếp theo nhóm | log | Thuật toán nào mở rộng ít nút nhất, ở nhóm nào |
| Hình 5.2 (H2) | Thời gian tìm kiếm trên từng màn gốc | log | Thời gian có tăng theo số nút không |
| Hình 5.3 (H3) | Bộ nhớ đỉnh trên từng màn gốc | log | Biên và tập đã thăm lớn thì bộ nhớ lớn |
| Hình 5.4 (H4) | Số bước DFS / số bước tối ưu | tuyến tính | DFS dài hơn tối ưu bao nhiêu lần |
| Hình 5.5 (H5) | Số nút A* / số nút UCS, một cột cho $h_M$, một cột cho $h_P$ | tuyến tính | Mỗi heuristic bớt được bao nhiêu |
| Hình 5.6 (H6) | Trung vị số nút mở rộng theo nhóm G1–G5 | log | Loại màn tác động tới độ khó ra sao |
| Hình 5.7 (H8) | Số nút mở rộng theo kích thước sân N (S1) | log | Công tìm kiếm tăng theo kích thước bàn ra sao |
| Hình 5.8 (H9) | Số trạng thái đã thăm theo số công tắc k (S2), kèm đường $2^k$ | log | Trạng thái cầu làm số trạng thái tăng nhanh cỡ nào |

Hình H7 (thời gian theo số nút) là tùy chọn ở 04 §7.2; nhóm không vẽ.

### 5.5. Kết luận thực nghiệm

> **Chờ số liệu chính thức và các đoạn 5.4.** Mục này trả lời lần lượt năm câu hỏi ở mục 5.1, mỗi câu theo ba bước (04 §7.3): **quan sát** (dẫn đúng bảng hoặc hình), **giải thích** (theo lý thuyết của thuật toán), **ý nghĩa** (nên dùng thuật toán nào, khi nào). Không viết kết luận nào khi chưa có bảng hoặc hình làm căn cứ.
