# Thực nghiệm (TV2, NV10)

Script đo, kiểm tra, vẽ hình và sinh bảng cho chương 5 của báo cáo. Cách đo và cách trình bày theo `docs/04-thuc-nghiem.md`; file này chỉ ghi lệnh và thứ tự chạy.

| File | Việc | Chủ |
|---|---|---|
| `run.py` | Đo: mỗi lần chạy một tiến trình con, giới hạn 60 giây, thời gian lấy trung vị 5 lần, bộ nhớ đo một lần riêng; ghi `raw.csv`, `summary.csv`, `run_info.json` | TV2 (V23) |
| `check_results.py` | Kiểm tra chéo K1–K8 trên `summary.csv` (04 §6) | TV2 (V24) |
| `charts.py` | Hình H1–H6, H8, H9, mỗi hình kèm một CSV số liệu (04 §7.2); cần `matplotlib` | TV2 (V25) |
| `tables.py` | Bảng T3, T4, T5 và Phụ lục A dạng Markdown (04 §7.1); cần `matplotlib` (dùng chung hàm đọc với `charts.py`) | TV2 (V25) |
| `gen_levels.py` | Sinh bộ màn tự sinh S1–S3 vào `levels/gen/` (04 §8) | TV3 (V40); bản hiện tại do TV2 viết tạm |
| `convert_original_levels.py` | Sinh 33 màn gốc trong `levels/original/` | TV2 (V07) |

Không script nào ghi đè kết quả đã có, trừ khi thêm `--force`.

## Chạy chính thức

### 0. Điều kiện trước khi chạy

Còn thiếu điều kiện nào thì số liệu chỉ là nháp, không đưa vào báo cáo.

- [ ] Hàm chi phí V13 đã chốt và đã cài vào `Problem.step_cost`; `tools/check_heuristics.py` cho 0 vi phạm với hàm chi phí đó.
- [ ] Nhánh chính đã có: bộ nạp màn có `links` (V03), UCS (V12), $h_P$ (V16), các sửa của V23 (PR #13), bộ màn S1–S3 (V40), và các script trong bảng trên.
- [ ] Nhóm đã chốt định dạng file kết quả (Q1–Q7); nếu có đổi thì `docs/04` đã sửa theo, qua PR.
- [ ] Máy chạy: một máy cho toàn bộ, cắm sạc, tắt ứng dụng nặng (04 §4).
- [ ] Working tree sạch. `git status` không có file `.py` chưa commit trong `Source/`, nếu không `run.py` sẽ ghi commit kèm hậu tố `-dirty`.

### 1. Kiểm tra code và dữ liệu

```bash
cd Source
python -m unittest                                   # phải OK; skip chỉ chấp nhận khi biết lý do
python -m experiments.convert_original_levels --check # 33 màn gốc khớp nguồn
python -m experiments.gen_levels --check             # S1–S3 khớp script
python tools/check_heuristics.py                     # 0 vi phạm với hàm chi phí đã chốt
```

### 2. Đo

```bash
python -m experiments.run --levels levels/original levels/gen   # ghi vào experiments/ như 04 §5
```

- **Phạm vi:** 47 màn (33 gốc và 14 tự sinh) × 5 cấu hình = 235 cặp; mỗi cặp 5 lần đo thời gian và 1 lần đo bộ nhớ.
- **Thời gian:** lần chạy thử ngày 28/10 trên máy TV2 mất khoảng 8,5 phút.
- **Kết quả** là `experiments/raw.csv`, `summary.csv`, `run_info.json`. Mở `run_info.json` và kiểm:
  - `commit` không có hậu tố `-dirty`, `dirty_reasons` rỗng;
  - `warnings` rỗng, `memory_failures` rỗng.

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

### 5. Đưa vào báo cáo

- Điền Bảng 5.2 (T1) trong `docs/report/5-thuc-nghiem.md` từ `run_info.json`: máy, Python, commit, thời gian chạy.
- Chép T3, T4, T5 từ `tables.md` vào mục 5.3, và Phụ lục A vào phụ lục. Chèn hình theo bảng "Hình cần có" ở mục 5.3.
- Gửi `summary.csv` cho cả nhóm để viết 5.4. Nhập file vào tab `thuc-nghiem` của Google Sheet (docs/05).
- Viết 5.5 và các chỗ `(…)` ở 5.4.2 **chỉ từ số liệu này**.
- *(Đề xuất, chờ nhóm quyết)* Commit `raw.csv`, `summary.csv`, `run_info.json`, `figures/`, `tables.md` của lần chạy chính thức vào nhánh chính qua PR, để người đọc tái lập được.

## Số liệu chạy thử

Thư mục `trial-*` là các lần chạy thử, chạy trước khi đủ điều kiện ở bước 0. Các thư mục này không được commit và không dùng trong báo cáo.
