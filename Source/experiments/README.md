# Thực nghiệm (TV2, NV10)

Script đo, kiểm tra, vẽ hình và sinh bảng cho chương 5 của báo cáo. Cách đo và cách trình bày theo `docs/04-thuc-nghiem.md`; file này chỉ ghi lệnh và thứ tự chạy.

## Cài đặt

Python 3.11 (docs/07 §4). Trong `Source/`:

```bash
python -m pip install -r requirements.txt   # gồm matplotlib==3.10.9 cho charts.py và tables.py
python -c "import matplotlib; print(matplotlib.__version__)"   # kiểm tra: phải in 3.10.9
```

- `run.py`, `check_results.py`, `compare_runs.py` chỉ dùng thư viện chuẩn.
- `charts.py` và `tables.py` cần `matplotlib`. Thiếu matplotlib thì hai script này báo `ModuleNotFoundError`, và test của chúng tự bỏ qua.

Vẽ hình và sinh bảng nhanh từ một `summary.csv` có sẵn:

```bash
python -m experiments.charts --summary <summary.csv> --out <thư mục hình>   # 8 hình H1–H6, H8, H9, mỗi hình kèm CSV
python -m experiments.tables --summary <summary.csv> --out <file .md>       # T3, T4, T5, Phụ lục A
python -m experiments.check_results <summary.csv>                           # K1–K8
```

| File | Việc | Chủ |
|---|---|---|
| `run.py` | Đo: mỗi lần chạy một tiến trình con, giới hạn 60 giây, thời gian lấy trung vị 5 lần, bộ nhớ đo một lần riêng; ghi `raw.csv`, `summary.csv`, `run_info.json` | TV2 (V23) |
| `check_results.py` | Kiểm tra chéo K1–K8 trên `summary.csv` (04 §6) | TV2 (V24) |
| `charts.py` | Hình H1–H6, H8, H9, mỗi hình kèm một CSV số liệu (04 §7.2); cần `matplotlib` | TV2 (V25) |
| `compare_runs.py` | So hai lần chạy để kiểm tra tái lập: số đếm phải trùng hẳn, thời gian và bộ nhớ chỉ báo tỉ lệ | TV2 (V24) |
| `tables.py` | Bảng T3, T4, T5 và Phụ lục A dạng Markdown (04 §7.1); cần `matplotlib` (dùng chung hàm đọc với `charts.py`) | TV2 (V25) |
| `gen_levels.py` | Sinh bộ màn tự sinh S1–S3 vào `levels/gen/` (04 §8) | TV3 (V40). Tên file `s1_010`, `s2_04`, `s3_10`; `charts.py` đọc cả tên này lẫn dạng `S1-010`, `S2-k04` |
| `convert_original_levels.py` | Sinh 33 màn gốc trong `levels/original/` | TV2 (V07) |

Không script nào ghi đè kết quả đã có, trừ khi thêm `--force`.

`check_results.py`, `charts.py`, `tables.py` và `compare_runs.py` từ chối file hỏng, báo kèm số dòng:
- thiếu cột;
- ô số không đọc được;
- trùng cặp (màn, thuật toán);
- dòng `solved` thiếu `steps`, `path_cost` hoặc `expanded`.

`charts.py` liệt kê các cặp không `solved`, vì các cặp này không có trên hình.

Các công cụ đọc chế độ chi phí (`cost`: `energy` là V13, `unit` là 1 mỗi bước) từ `run_info.json` cạnh `summary.csv`:
- `check_results.py` và `charts.py` in ra chế độ này;
- `tables.py` ghi nó ở đầu file bảng;
- `charts.py` ghi nó vào chú thích góc dưới phải mỗi hình;
- `compare_runs.py` từ chối so hai lần chạy khác chế độ.

Khi không xác định được chế độ, công cụ nêu lý do (thiếu file, file hỏng, thiếu khóa `cost`, giá trị lạ) và không đoán.

## Chạy chính thức

### 0. Điều kiện trước khi chạy

Còn thiếu điều kiện nào thì số liệu chỉ là nháp, không đưa vào báo cáo.

- [ ] Hàm chi phí V13 được dùng khi chạy. Trên nhánh chính từ PR #18: `bloxorz/costs.py` (`compute_step_cost`, TV3) được truyền vào ở từng chỗ gọi: `run.py --cost energy` (mặc định của dòng lệnh), GUI, `server/api.py`, `tools/check_heuristics.py` (mặc định `energy`). `Problem` tự nó vẫn mặc định chi phí 1 (`DEFAULT_COST_FN = None`), nên **luôn kiểm `"cost": "energy"` trong `run_info.json`**. Lệnh `check_results`, `charts`, `tables`, `compare_runs` in chế độ chi phí đọc từ file này.
- [ ] `tools/check_heuristics.py` cho 0 vi phạm với hàm chi phí V13 (mặc định `--cost energy`), trên cả `levels/original` và `levels/gen`.
- [ ] Nhánh chính đã có: bộ nạp màn có `links` (V03), UCS (V12), $h_P$ (V16), bộ màn S1–S3 (V40), các script trong bảng trên (PR #17), sửa V23 (PR #13), GUI V21 (PR #15, #18).
- [ ] Nhóm đã chốt định dạng file kết quả (Q1–Q7); nếu có đổi thì `docs/04` đã sửa theo, qua PR.
- [ ] Máy chạy: một máy cho toàn bộ, cắm sạc, tắt ứng dụng nặng (04 §4).
- [ ] Working tree sạch. `git status` không có file `.py` chưa commit trong `Source/`, nếu không `run.py` sẽ ghi commit kèm hậu tố `-dirty`.

### 1. Kiểm tra code và dữ liệu

```bash
cd Source
python -m unittest                                   # phải OK; skip chỉ chấp nhận khi biết lý do
python -m experiments.convert_original_levels --check # 33 màn gốc khớp nguồn
python -m unittest tests.test_gen_levels           # S1–S3 (test của TV3; gen_levels.py không có --check)
python tools/check_heuristics.py                     # 33 màn gốc, 0 vi phạm, chi phí V13 (--cost energy)
python tools/check_heuristics.py levels/gen          # 14 màn tự sinh
```

### 2. Đo

```bash
python -m experiments.run --levels levels/original levels/gen --cost energy   # ghi vào experiments/ như 04 §5; --cost ghi rõ dù đã là mặc định
```

- **Phạm vi:** 47 màn (33 gốc và 14 tự sinh) × 5 cấu hình = 235 cặp; mỗi cặp 5 lần đo thời gian và 1 lần đo bộ nhớ.
- **Thời gian:** lần chạy thử ngày 28/10 trên máy TV2 mất khoảng 8,5 phút.
- **Kết quả** là `experiments/raw.csv`, `summary.csv`, `run_info.json`. Mở `run_info.json` và kiểm:
  - `commit` không có hậu tố `-dirty`, `dirty_reasons` rỗng;
  - `warnings` rỗng, `memory_failures` rỗng;
  - `cost` là `energy`.

### 3. Kiểm tra chéo

```bash
python -m experiments.check_results experiments/summary.csv
```

Phải ra **K1–K8 đều PASS** (exit 0).
- **K8** kiểm đủ dòng: đủ 33 màn gốc × 5 cấu hình, và mọi dòng màn gốc đều `solved`.
- **Có FAIL:** không dùng số liệu. Báo chủ thuật toán, sửa xong thì chạy lại từ bước 1.
- **NOT RUN:** nghĩa là thiếu dữ liệu để kiểm. Lần chạy chính thức không được có NOT RUN.

Các kiểm tra ở 04 §6 cần đổi hàm chi phí hoặc heuristic thì không nằm ở đây:
- "đặt mọi chi phí bằng 1 thì UCS bằng BFS": test của UCS;
- "0 vi phạm": `tools/check_heuristics.py`;
- "có màn UCS chọn đường khác BFS": đọc bảng T4, so cột tối ưu về số bước với tối ưu về chi phí.

### 4. Hình và bảng

```bash
python -m experiments.charts    # đọc experiments/summary.csv, ghi experiments/figures/
python -m experiments.tables    # đọc experiments/summary.csv, ghi experiments/tables.md
```

- **Hình:** mỗi hình là một file PNG kèm một file CSV chứa đúng số liệu đã vẽ. Mở từng hình để kiểm nhãn, chú giải và thang log.
- **Bảng:** `tables.md` ghi commit nguồn ở đầu file. Nếu file có dòng **Cảnh báo** (số liệu từ nhiều commit, hoặc commit `-dirty`), không dùng.

### 5. Kiểm tra tái lập

Clone sạch repo ở đúng commit của lần chạy chính thức (trên cùng máy, hoặc một máy khác), rồi chạy lại bước 2 vào một thư mục khác. Sau đó so hai lần chạy:

```bash
git clone <repo> tai-lap && cd tai-lap && git checkout <commit trong run_info.json>
cd Source
python -m experiments.run --levels levels/original levels/gen --cost energy --out experiments/tai-lap
python -m experiments.compare_runs <Source/experiments/summary.csv của lần chính thức> experiments/tai-lap/summary.csv
```

- **Phải ra `TRÙNG`** (exit 0): status, số bước, chi phí và các số đếm tất định, nên cùng commit phải ra cùng số.
- **Thời gian và bộ nhớ:** chỉ có tỉ lệ B / A để ghi vào báo cáo như độ dao động giữa các lần đo.
- **Kiểm thử kỹ thuật ngày 28/10:** chạy lại toàn bộ 235 cặp sau khi đã sửa các công cụ (code solver và file màn không đổi), rồi so với lần chạy thử. Số đếm trùng hẳn ở cả 235 cặp; bộ nhớ đỉnh trùng; thời gian tìm kiếm có trung vị B / A = 1,05.

### 6. Đưa vào báo cáo

- Điền Bảng 5.2 (T1) trong `docs/report/5-thuc-nghiem.md` từ `run_info.json`: máy, Python, commit, thời gian chạy.
- Chép T3, T4, T5 từ `tables.md` vào mục 5.3, và Phụ lục A vào phụ lục. Chèn hình theo bảng "Hình cần có" ở mục 5.3.
- Gửi `summary.csv` cho cả nhóm để viết 5.4. Nhập file vào tab `thuc-nghiem` của Google Sheet (docs/05).
- Viết 5.5 và các chỗ `(…)` ở 5.4.2 **chỉ từ số liệu này**.
- *(Đề xuất, chờ nhóm quyết)* Commit `raw.csv`, `summary.csv`, `run_info.json`, `figures/`, `tables.md` của lần chạy chính thức vào nhánh chính qua PR, để người đọc tái lập được.

## Số liệu chạy thử

Thư mục `trial-*` là các lần chạy thử, chạy trước khi đủ điều kiện ở bước 0. Các thư mục này không được commit và không dùng trong báo cáo.
