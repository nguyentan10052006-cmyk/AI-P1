# Kiến trúc code và GUI Ursina

Bản đề xuất ngày 19/10, TV5 soạn. Cần TV1 (chủ hợp đồng chung, V01) và TV4 (module chạy nền, V39) duyệt; duyệt xong thì ghi vào tab bien-ban và sửa các file ở mục 9.

File này **bổ sung** cho [01 §4](01-phan-cong-PA2.md#4-hợp-đồng-chung), không thay thế. Hợp đồng giữa engine và solver (`State`, `Action`, `Problem`, `Level`, `step()`, `SearchResult`, `Solver`) giữ nguyên như đã chốt ở bien-ban #14. Những gì mới ở đây: cấu trúc thư mục khi GUI chuyển sang Ursina, quy tắc phụ thuộc giữa các package, môi trường, hợp đồng giữa GUI và engine, module chạy nền dạng không chặn cho Ursina, và quy trình Git.

## 1. Những gì đổi khi chọn Ursina

`Source/` hiện tại là bản demo dựng nhanh cho buổi họp đầu: GUI web (Three.js) gọi engine qua server HTTP. Nhóm đã chọn **Ursina** (Python, chạy trên Panda3D) cho GUI 3D (bien-ban #3).

| Phần | Bản demo | Khi dùng Ursina |
|---|---|---|
| `bloxorz/` (engine, bộ nạp màn, `GridMaze`) | có | **Giữ hợp đồng** ở 01 §4. Chủ module viết lại hoặc sửa tiếp trên code demo, nhưng không đổi chữ ký hàm |
| `solvers/` (`base.py`, 4 thuật toán, `runner.py`) | có | **Giữ hợp đồng**. `runner.py` thêm hàm không chặn cho GUI (mục 6) |
| `levels/original/`, `levels/gen/` | chưa có | Như 03 §6 và 04 §8, không đổi |
| 18 màn tự thiết kế trong `levels/` | có | TV5 quyết giữ làm màn hướng dẫn hay bỏ (mục 8) |
| `web/`, `server/`, `tests/test_server.py` | có | **Bỏ**, thay bằng `gui/` |
| `bloxorz/serialize.py` | chỉ dùng cho HTTP | Bỏ, trừ khi thực nghiệm cần ghi `path` ra CSV |
| `main.py`, `README.md`, `requirements.txt` | mở server và trình duyệt; không cần thư viện ngoài | Mở cửa sổ Ursina; ghim phiên bản `ursina` |

## 2. Kiến trúc và quy tắc phụ thuộc

```
 levels/**/*.json ──> bloxorz.level.load_level ──> Level
                                                     │
                             bloxorz.rules.step()  (luật một lượt, thuần Python)
                               ▲                  ▲
           step() khi chơi tay │                  │ Problem.actions / result / step_cost
                               │                  │
                        gui/ (Ursina)      solvers/ (BFS, DFS, UCS, A*)
                               │                  ▲
                               └─> solvers.runner ┘
                         (tiến trình riêng, Hủy, hết giờ 60 giây, So sánh)
```

| Package | Được import | Không được import |
|---|---|---|
| `bloxorz/` | thư viện chuẩn | `solvers`, `gui`, `experiments`, `ursina` |
| `solvers/` (kể cả `runner.py`) | `bloxorz` | `gui`, `experiments`, `ursina` |
| `gui/` | `bloxorz`, `solvers` (chỉ `ALGORITHMS` và `runner`), `ursina` | không gọi thẳng `Solver.search()` |
| `experiments/` | `bloxorz`, `solvers`, `matplotlib` | `gui`, `ursina` |
| `tests/` | mọi package trừ `gui` | `ursina` |

Lý do: thuật toán, thực nghiệm và test phải chạy được trên máy chưa cài Ursina; module chạy nền phải thử được không cần GUI (điều kiện "Xong khi" của V39).

**`main.py` chỉ import `gui` bên trong hàm `main()`.** Module chạy nền dùng `multiprocessing` kiểu `spawn`; tiến trình con nạp lại `main.py` (dưới tên `__mp_main__`) và chạy mọi lệnh import ở cấp ngoài cùng. Nếu `import ursina` nằm ở đầu file, mỗi lần bấm Solve sẽ nạp Ursina thêm một lần trong tiến trình con, chậm thêm khoảng một giây.

```python
# Source/main.py
def main() -> int:
    from gui.app import run      # import ở đây, không đặt ở đầu file
    return run()

if __name__ == "__main__":       # bắt buộc trên Windows khi dùng multiprocessing
    raise SystemExit(main())
```

## 3. Cấu trúc thư mục

Thay cho cây thư mục ở 01 §4.1; phần khác giữ nguyên.

```
Source/
├── main.py                 # TV5: mở GUI Ursina
├── README.md               # TV5: cài đặt, chạy, phím điều khiển, ghi công nguồn
├── requirements.txt        # ursina==…, matplotlib==… (ghim phiên bản, mục 4)
├── levels/
│   ├── original/01.json … 33.json   # TV2: 33 màn gốc
│   └── gen/                # TV3: màn tự sinh S1–S3
├── bloxorz/                # TV1: state.py, rules.py (lõi, tách khối), problem.py, maze.py
│                           # TV3: level.py (bộ nạp màn), rules.py (ô đặc biệt), hàm chi phí (mục 8)
├── solvers/                # base.py, bfs.py (TV1) · dfs.py (TV2) · ucs.py (TV3)
│                           # astar.py, heuristics.py, runner.py (TV4)
├── gui/                    # TV5
│   ├── app.py              # khởi tạo Ursina, vòng update(), nhận phím
│   ├── board_view.py       # dựng bàn từ Level, vẽ 9 loại ô, cầu đóng/mở
│   ├── block_view.py       # khối và hai khối con; hoạt ảnh lăn, rơi, tách, ghép
│   └── hud.py              # menu chọn màn, nút New Game, Restart, 4 nút Solve, So sánh, Hủy; thông báo
├── experiments/            # TV2: run.py, charts.py, raw.csv, summary.csv · TV3: gen_levels.py
└── tests/                  # mỗi người viết test cho phần mình (unittest)
```

## 4. Môi trường và quy ước code

**Môi trường**
- Cả nhóm dùng **Python 3.11**. Ursina chạy trên Panda3D, mà Panda3D thường ra bản cho Python mới chậm hơn. Dùng chung một phiên bản để tránh lỗi chỉ xảy ra trên một máy.
- `requirements.txt` ghim phiên bản cụ thể (06 §6): `ursina==7.0.0`, `panda3d==1.10.16`. TV5 đã cài thử với Python 3.11.9 trên Windows 11 và mở được cửa sổ (21/10). Cài bằng `python -m pip install -r requirements.txt` trong `Source/`.
- Bộ nhớ đo bằng `tracemalloc` của thư viện chuẩn (04 §4), không cần `psutil`.
- Test chạy bằng `unittest` như code hiện có: `python -m unittest discover -v` trong `Source/`.

**Tọa độ trong Ursina** (chỉ dùng trong `gui/`). Mọi chỗ khác vẫn là (hàng, cột) như 02 §2.
- Ô (r, c) có tâm tại `x = c`, `z = -r`; trục `y` hướng lên; mặt trên ô sàn ở `y = 0`. Cạnh ô dài 1.
- Khối đứng: tâm `y = 1` (cao 2). Khối nằm: tâm `y = 0.5`, nằm giữa hai ô nó chiếm. Khối con: tâm `y = 0.5`.
- Vì `z = -r`, hàng tăng thì `z` giảm. Đặt camera nhìn từ phía `z` âm lên để phím ↑ (U, hàng giảm) làm khối đi ra xa người xem.

**Phím:** ← ↑ → ↓ (và W A S D) đổi thành `Dir`. Space đổi khối con đang điều khiển. Space **không phải hành động** của bài toán (02 §5 dòng 7), chỉ đổi giá trị `cube` mà GUI điền vào `Action` ở lần lăn tiếp theo.

**Phong cách code**
1. Có type hint cho tham số và giá trị trả về.
2. `snake_case` cho hàm và biến, `PascalCase` cho lớp, `UPPER_CASE` cho hằng số.
3. `State`, `Action`, `Level`, `Problem` và `SearchResult` phải **pickle được**, vì được gửi sang tiến trình con. Không gắn lambda hay đối tượng Ursina vào chúng.
4. Code đã gộp vào nhánh chính trong `bloxorz/` và `solvers/` không dùng `print` để gỡ lỗi.

## 5. Hợp đồng giữa GUI và engine

GUI chỉ dùng các hàm dưới đây và **không viết lại luật** (01 NV9 bước 3).

| Việc | Gọi |
|---|---|
| Danh sách màn cho menu | `load_levels(Path("levels/original"))`; thêm màn hướng dẫn nếu giữ (mục 8) và màn S3 để demo thông báo không có lời giải (03 §5) |
| New Game, Restart | `level.initial_state()` |
| Chơi tay | `rules.step(level, state, Action(dir, cube))`, rồi đọc `status`, `events`, `moved` của `StepResult` để vẽ |
| Vẽ ô | `level.tile(cell)` trả ký hiệu ở 02 §2 |
| Cầu đang mở hay đóng | `cell in state.open_bridges` |
| Số màn, passcode, bước tối ưu | `level.name`, `passcode` (TV3 thêm vào `Level`, 03 §6), `level.par` |
| 4 nút Solve | `runner.start_solver(ALGORITHMS[name], Problem(level))`, rồi gọi `poll()` mỗi khung hình (mục 6) |
| Nút So sánh | `runner.start_compare(Problem(level))`, rồi `poll()` |
| Nút Hủy | `job.cancel()` |
| Khối tự lăn theo lời giải | gọi `rules.step()` lần lượt với từng `Action` trong `path`, có độ trễ giữa các bước |

**`StepResult`** (`bloxorz/rules.py`):
- `status`: `'ok'`, `'fell'` hoặc `'won'`. Khi `'fell'`, `state` là trạng thái lúc rơi; GUI vẽ cảnh rơi rồi báo thua, không lấy `state` này để chơi tiếp.
- `moved`: vị trí ngay sau khi lăn, trước khi công tắc kích hoạt hoặc hai khối con ghép lại. Dùng cho hoạt ảnh lăn.
- `events`: danh sách `dict` theo thứ tự xảy ra, dùng cho hiệu ứng: `switch` (`at`, `kind`, `effect`), `split` (`from`, `targets`), `merge`, `fragile_broken` (`at`), `fell` (`reason`, `at`), `won`. Ai thêm loại sự kiện mới thì báo TV5.

**Khối con đang điều khiển do GUI tự giữ**, vì `State` không lưu thông tin này (02 §6). GUI giữ `active_cube` (0 hoặc 1). Engine luôn sắp hai khối con để `pos < pos2`, nên sau một bước, khối vừa đi có thể đổi từ chỉ số 0 sang 1. Sau mỗi bước, GUI tìm lại khối vừa đi theo ô mới của nó trong `state.cells()`, rồi cập nhật `active_cube`. Khi phát lại lời giải thì không cần làm vậy, vì `Action.cube` trong `path` đã tính theo thứ tự của trạng thái lúc đó; GUI chỉ cần tô sáng khối con có chỉ số `action.cube`.

## 6. Module chạy nền cho Ursina (V39, TV4)

`run_solver()` ở 01 §4 chạy solver trong tiến trình con nhưng **chặn** tiến trình gọi cho tới khi có kết quả. Bản demo dùng được như vậy vì server HTTP chờ trong một luồng riêng. Ursina vẽ mọi thứ trong một vòng `update()` duy nhất, nên nếu gọi hàm chặn ở đó thì cửa sổ đơ. Module cần thêm các hàm không chặn sau, đặt trong `solvers/runner.py`, không import `ursina`:

```python
def run_solver(solver_cls, problem, timeout_s=60.0, job=None) -> dict: ...   # giữ nguyên, cho test và dòng lệnh

def start_solver(solver_cls: type[Solver], problem: Problem, timeout_s: float = 60.0) -> SolveJob:
    """Mở tiến trình con rồi trả về ngay."""

class SolveJob:
    elapsed: float                      # số giây đã chạy, để GUI hiện "Đang tìm… 12 s"
    def poll(self) -> dict | None: ...  # None khi chưa xong; không chặn. Quá timeout_s thì tự dừng tiến trình và trả kết quả hết giờ
    def cancel(self) -> None: ...       # dừng tiến trình con ngay; lần poll() sau trả kết quả đã hủy

def start_compare(problem: Problem, names: Sequence[str] = ("bfs", "dfs", "ucs", "astar", "astar_m"),
                  timeout_s: float = 60.0) -> CompareJob:
    """Chạy lần lượt từng thuật toán, mỗi thuật toán một tiến trình."""

class CompareJob:
    done: bool
    def poll(self) -> dict[str, dict]: ...   # kết quả của các thuật toán đã xong tới lúc gọi
    def cancel(self) -> None: ...
```

`dict` kết quả giữ đúng dạng `run_solver()` đang trả: khi thành công có các trường của `SearchResult` cùng `prepare_ms`, `time_ms`, `peak_kb`; khi không thành công là `{'ok': False, 'error': …}` kèm `'timeout': True` hoặc `'cancelled': True`.

**Quy tắc**
1. Dùng `multiprocessing` kiểu `spawn` trên mọi hệ điều hành, để hành vi trên Windows và các máy khác giống nhau.
2. GUI **không** nhận callback từ tiến trình con hay luồng khác, vì Ursina không an toàn khi đối tượng được sửa ngoài luồng chính. GUI giữ `SolveJob` hoặc `CompareJob` và gọi `poll()` trong `update()` mỗi khung hình.
3. Hết 60 giây thì tiến trình con bị dừng. Solver không cần tự kiểm tra thời gian.
4. So sánh mặc định chạy 5 solver: 4 thuật toán và thêm A* với h_M (`astar_m`), để GUI so được h_P với h_M ngay trên màn đang mở. So sánh chạy **lần lượt**, không song song, để thời gian và bộ nhớ của các thuật toán không ảnh hưởng lẫn nhau.
5. Thời gian và bộ nhớ hiện trên GUI chỉ để tham khảo. Số liệu cho báo cáo lấy từ script thực nghiệm (04 §4), vì GUI đo khi đang bật `tracemalloc`.
6. GUI phân biệt bốn thông báo (01 NV9 bước 8): thắng hoặc giải được (`status == 'solved'`), không có lời giải (`'no_solution'`), hết giờ (`'timeout'`), lỗi hoặc đã hủy. Rơi chỉ xảy ra khi chơi tay.

## 7. Lưu ý khi viết GUI bằng Ursina

Ngoài các lỗi hay gặp ở 01 NV9:
- Mọi entity của một màn gắn vào **một entity gốc**; đổi màn hoặc Restart thì `destroy()` entity gốc đó.
- Trong lúc hoạt ảnh lăn đang chạy, bỏ qua phím mới hoặc đưa vào hàng đợi. Nếu không, `state` của GUI sẽ đi trước hình đang vẽ.
- Bàn 10 × 15 của màn gốc và bàn tới 200 × 200 của màn tự sinh dùng cùng một hàm căn camera theo `level.rows` và `level.cols`.
- Màu và hình của 9 loại ô theo 01 NV9 bước 2, dùng chung cho màn hướng dẫn và cho ảnh chụp trong báo cáo (06 §1, chương 4).

## 8. Quy trình Git

Tab bien-ban #7 chưa chốt. Đề xuất theo cách nhóm đang làm trên repo:

1. Không commit thẳng lên `main`. Mỗi việc một nhánh `feature/<tên>/<việc>` (ví dụ `feature/triet/structure`), rồi mở pull request vào `main`.
2. Người duyệt pull request là người đọc chéo ở 01 §2:

| Tác giả | Người duyệt |
|---|---|
| TV1 | TV3 |
| TV2 | TV1 |
| TV3 | TV4 |
| TV4 | TV5 |
| TV5 | TV2 |

3. Trước khi mở pull request: chạy toàn bộ test, và kiểm tra không vi phạm bảng phụ thuộc ở mục 2. Mẹo kiểm tra nhanh: gỡ Ursina trong một môi trường ảo rồi chạy test; test vẫn phải qua.
4. Ở mỗi mốc, mọi người gộp vào `main` trước 18h (01 NV13). Chỉ chọn "Hoàn thành" trong tab task khi người đọc chéo đã xem và test qua (01 §7).

## 9. Điểm còn mở và các file cần sửa sau khi duyệt

**Cần chốt**

| # | Vấn đề | Đề xuất | Ai chốt |
|---|---|---|---|
| 1 | Hàm chi phí đặt ở đâu. 01 §4.1 để `costs.py` trong `solvers/`, nhưng `Problem.step_cost()` nằm ở `bloxorz/`, nên `bloxorz` phải import `solvers`, trái bảng ở mục 2 | Đặt ở `bloxorz/costs.py`, vì hàm chi phí chỉ phụ thuộc `State` và `Level` | TV1, TV3 |
| 2 | Chọn h_M hay h_P khi chạy A*. `ALGORITHMS` chỉ có một khóa `'astar'` | **Đã chốt 20/10 (TV4, bien-ban #15):** thêm khóa `'astar_m'` (lớp `AStarM`, con của `AStar`) cho h_M; `'astar'` là h_P. Nút Solve A* dùng `'astar'`; nút So sánh chạy cả `'astar'` và `'astar_m'` để so h_P với h_M. Đã có trong code và `tests/test_solvers.py` | TV4 |
| 3 | Giữ hay bỏ 18 màn tự thiết kế trong `levels/` | Giữ 2–3 màn ngắn làm màn hướng dẫn, chuyển vào `levels/tutorial/`; bỏ phần còn lại | TV5 |
| 4 | Phiên bản Python và Ursina | **Đã chốt 21/10 (TV5, bien-ban #16):** Python 3.11, `ursina==7.0.0`, `panda3d==1.10.16`, đã ghim trong `requirements.txt` | TV5 |

**Sau khi duyệt, sửa các chỗ sau cho khớp:**
- Tab bien-ban: điền #3 (GUI dùng Ursina) và #7 (Git); thêm một dòng cho các điểm ở bảng trên.
- 01 §1 dòng "Còn phải điền": bỏ "công nghệ GUI 3D".
- 01 §4: thêm `start_solver`, `SolveJob.poll`, `start_compare` vào khối chữ ký của `runner.py`.
- 01 §4.1: dòng "Module chạy nền" (bỏ câu "GUI web gọi qua server HTTP nên không cần `poll`"), và cây thư mục (thay `server/`, `web/` bằng `gui/`; trỏ sang mục 3 của file này).
- 01 NV9: bước 1 (đã chọn Ursina) và bước 7 (gọi `start_solver` rồi `poll()` thay vì gọi qua server).
- `Source/README.md`, `Source/requirements.txt`, `Source/main.py`: viết lại cho Ursina (V22).
