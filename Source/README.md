# Bloxorz Solver

Đồ án CSC14003 Cơ sở Trí tuệ Nhân tạo, Project 1. Trò chơi Bloxorz có giao diện 3D viết bằng Ursina, chơi trên 33 màn gốc của game, với đủ các ô đặc biệt (ô dễ vỡ, cầu, ba loại công tắc, tách và ghép khối) và bốn thuật toán tìm kiếm: BFS, DFS, UCS, A*.

## Cài đặt

Yêu cầu **Python 3.11** (đã thử với 3.11.9). Ursina chạy trên Panda3D; Panda3D thường ra bản cho Python mới chậm hơn, nên dùng đúng 3.11 để tránh lỗi cài đặt.

```bash
cd Source
python -m venv .venv
.venv\Scripts\activate            # macOS, Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` ghim `ursina==7.0.0`, `panda3d==1.10.16` (giao diện) và `matplotlib==3.10.9` (chỉ để vẽ biểu đồ thực nghiệm). Engine, các thuật toán và test chỉ dùng thư viện chuẩn, nên chạy được cả trên máy chưa cài Ursina.

## Chạy giao diện

```bash
cd Source
python main.py          # mở màn 01
python main.py 17       # mở thẳng màn 17 (mã màn 01 … 33)
```

Trên Windows, chạy bằng `python main.py` chứ không chạy `gui/app.py` trực tiếp từ thư mục khác: các thuật toán chạy ở tiến trình riêng (`multiprocessing`), và `main.py` có sẵn `if __name__ == "__main__":` mà Windows bắt buộc. Cách khác tương đương: `python -m gui.app 17` trong `Source/`.

### Phím điều khiển

| Phím | Tác dụng |
|---|---|
| ← ↑ → ↓ hoặc W A S D | Lăn khối |
| Space | Đổi khối con đang điều khiển (sau khi khối bị tách) |
| R | Chơi lại màn đang mở (cũng dừng khối đang tự lăn) |
| N / P | Sang màn sau / màn trước |
| Q / E | Nghiêng camera sang trái / phải một nấc (chính diện, 20°, 40°) |
| Z / X | Hạ thấp / nâng cao góc nhìn một nấc (52°, 45°, 38°, 30°) |
| T | Bật/tắt góc nhìn thẳng từ đỉnh |
| F | Đặt lại camera về chính diện, 52° |
| Giữ chuột phải và kéo, con lăn chuột | Chỉnh góc nhìn (trong giới hạn trên), thu phóng |
| H | Ẩn/hiện khung kết quả |
| Ctrl+K | Mở/đóng lưới chọn màn (chấm xanh đánh dấu màn đã thắng) |
| Enter | Bấm nút chính của hộp kết thúc màn (Màn tiếp hoặc Chơi lại) |
| G | Bảng chú giải các loại ô (hoặc nút "Chú giải") |
| F1 | Bảng tất cả phím tắt |
| Esc | Đóng hộp kết thúc màn, lưới chọn màn hoặc bảng phím tắt |

Camera luôn nhìn từ trên xuống, từ phía người chơi, và không lệch quá 40° sang hai bên, nên phím ↑ luôn đẩy khối về phía trên màn hình. Góc đã chọn được giữ khi đổi màn. Các nút camera ở cột phải làm được việc như các phím trên.

### Các nút

| Nút | Tác dụng |
|---|---|
| Màn đầu, ‹ Trước, Sau ›, Chơi lại (thanh trên cùng bên phải) | Về màn 01, sang màn trước hoặc sau, chơi lại màn đang mở (như phím P, N, R) |
| Chọn màn (thanh trên cùng) | Mở lưới 33 màn (màn đang mở tô xanh), bấm một màn để chuyển tới |
| BFS / DFS / UCS / A* (thẻ "Tìm lời giải") | Chạy thuật toán ở tiến trình riêng. Giải được thì khối tự lăn theo lời giải, khung kết quả ở cột trái hiện số bước, chi phí, số nút mở rộng và sinh, frontier lớn nhất, số trạng thái đã thăm, thời gian tìm kiếm, bộ nhớ |
| So sánh cả 5 thuật toán | Chạy lần lượt BFS, DFS, UCS, A* (h_P) và A* (h_M) trên màn đang mở, hiện bảng kết quả |
| Hủy | Dừng thuật toán đang chạy hoặc khối đang tự lăn |

Mỗi lần giải có bốn kết quả: giải được, không có lời giải, hết giờ (quá 60 giây thì tiến trình bị dừng), lỗi hoặc đã hủy. Trong lúc thuật toán chạy, cửa sổ vẫn phản hồi và nút Hủy dùng được. Khi khung kết quả hiện, bàn tự thu vào phần màn hình còn trống nên không bị che; bấm H để ẩn khung. Thời gian và bộ nhớ hiện trên giao diện chỉ để tham khảo; số liệu trong báo cáo lấy từ script thực nghiệm.

Khi thắng hoặc rơi, một hộp thông báo (kéo thả được bằng chuột) hiện giữa vùng bàn: số bước so với tối ưu (hoặc lý do rơi) và các nút Màn tiếp, Chơi lại, Chọn màn. Các nút camera nằm trong thẻ "Góc nhìn".

## Cách chơi

Mục tiêu: lăn khối 1×1×2 tới lỗ vuông đích và **đứng thẳng** trên lỗ. Khối chạm ô trống hoặc ra ngoài bàn thì rơi, thua.

| Ô | Hình trên giao diện | Luật |
|---|---|---|
| Sàn | ô xám | Đi bình thường |
| Đích | lỗ vuông tối, viền vàng nhấp nháy | Khối đứng thẳng trên ô này thì thắng |
| Ô dễ vỡ | ô cam | Khối đứng thẳng lên thì ô vỡ, khối rơi |
| Công tắc mềm | đĩa tròn trắng | Bất kỳ phần nào của khối chạm vào đều kích hoạt |
| Công tắc nặng | hình X đỏ | Chỉ kích hoạt khi khối đứng thẳng trên nó |
| Công tắc tách | hình "( )" xanh | Khối đứng lên thì tách thành hai khối con 1×1×1 ở hai ô định sẵn |
| Cầu mở | ô gỗ nâu | Đi như sàn |
| Cầu đóng | ô sẫm | Như ô trống: đi vào là rơi |

Khối lật quanh cạnh đáy như game gốc; khối nằm mà một đầu hụt khỏi sàn thì đổ nghiêng qua mép rồi rơi. Khi công tắc tác động, khối tách hay ghép, giao diện hiện một dòng thông báo ngắn dưới dòng thắng thua. Góc trái dưới có bộ đếm FPS.

## Luật chơi và các giả định

Luật theo đề bài (mục 2). Các điểm đề bài chưa nói rõ, nhóm đã chọn như sau:

- **Khối con 1×1×1 không làm vỡ ô giòn.** Đề chỉ đặt luật này cho "the block" (khối 1×1×2), nên khối con đi qua ô giòn như nền thường. Mỗi câu luật có test trong `tests/test_spec.py`.
- **Khối con chỉ kích hoạt công tắc mềm.** Công tắc nặng và công tắc tách chỉ kích hoạt khi khối đứng nguyên vẹn, theo đúng đề bài.
- **Khối nằm ngang qua ô đích không thắng.** Khối con lăn vào ô đích cũng không thắng: khối phải được ghép lại rồi đứng lên ô đích.
- **Công tắc kích hoạt mỗi lần khối lăn vào ô đó.** Với công tắc mềm, mọi phần của khối đều tính là chạm.
- **Công tắc tách có thể nối cầu** (đề: "Each switch is linked to one or more bridge tiles"). Khi đó hiệu ứng toggle/open/close áp dụng cho cầu, rồi khối mới được tách.
- **Đóng cầu ngay dưới khối** thì khối rơi.
- **Hai khối con kề nhau (chung cạnh)** tự ghép thành khối nằm.

Trạng thái đầy đủ gồm vị trí, tư thế và tập các cầu đang mở. Hai trạng thái cùng vị trí khối nhưng khác cấu hình cầu là hai trạng thái khác nhau.

## Hàm chi phí

UCS và A* dùng hàm chi phí không đồng nhất trong `bloxorz/costs.py` (công nâng trọng tâm khi lật khối, cộng phụ phí khi đi lên ô dễ vỡ). Mọi bước tốn ít nhất 1, nên heuristic đếm bước của A* vẫn chấp nhận được.

| Bước | Chi phí |
|---|---|
| Đứng → nằm | 1.12 |
| Nằm → đứng | 1.62 |
| Nằm → nằm (lăn quanh trục dài) | 1.21 |
| Khối con 1×1×1 lăn | 1.10 |
| Thêm khi có phần khối nằm trên ô dễ vỡ | +0.50 |

Đây là hàm chi phí chính thức của nhóm. Nút Giải, nút So sánh, script thực nghiệm, công cụ kiểm tra heuristic và bản demo web đều dùng hàm này (`COST_FN` trong `gui/app.py`, `--cost` trong `experiments/run.py` và `tools/check_heuristics.py`, `cost_fn` trong `server/api.py`; `--cost unit` để đối chiếu với chi phí 1 mỗi bước), nên cột chi phí của BFS và DFS cũng tính theo cùng hàm để so chất lượng lời giải (docs/04 §2). BFS cho số bước ít nhất, UCS và A* cho tổng chi phí nhỏ nhất; trên 33 màn gốc, hai tiêu chí này cho đường khác nhau ở màn 17 và 23.

## Màn chơi

`levels/original/01.json` … `33.json` là 33 màn của Bloxorz gốc theo đúng thứ tự trong game, chuyển tự động từ dữ liệu của bloxorz_gba (cách sinh lại và kiểm tra: `levels/original/README.md`). Mỗi file có `name`, `passcode`, `group` (nhóm độ khó), `source`, `par` (số bước tối ưu tham khảo), `grid` và `switches`:

```json
{
  "name": "Màn 2", "passcode": "290299", "group": "G3", "par": 17,
  "grid": ["####..##x#..#G#", "##o#..####..###", "#S##bb####bb###"],
  "switches": [
    {"at": [1, 2], "bridges": [[2, 4], [2, 5]], "effect": "toggle"},
    {"at": [0, 8], "bridges": [[2, 10], [2, 11]], "effect": "toggle"}
  ]
}
```

(ví dụ rút gọn; file thật có lưới 10 × 15)

Ký hiệu trong `grid`: `.` ô trống, `#` sàn, `S` vị trí xuất phát (khối đứng), `G` đích, `F` ô dễ vỡ, `b` / `B` cầu đóng / mở lúc đầu, `o` công tắc mềm, `x` công tắc nặng, `@` công tắc tách. Công tắc mềm và nặng có `effect` (`toggle`, `open`, `close`) và `bridges`; công tắc tách có `targets` là hai ô đích của khối con. Công tắc nối nhiều cầu với hiệu ứng khác nhau dùng `links`: `[{"cell": [r, c], "effect": "open"}, …]`. `bloxorz/level.py` kiểm tra file trước khi chạy và báo lỗi rõ ràng nếu file sai.

`levels/gen/` là bộ màn tự sinh cho thực nghiệm (`python -m experiments.gen_levels`, docs/04 §8): S1 sân trống N × N (N từ 10 tới 200), S2 có k công tắc mềm (k từ 0 tới 10), S3 không có lời giải.

Các file `levels/*.json` ngay trong `levels/` (1-1 … 5-3, T1, T2, B1) là 18 màn tự thiết kế của bản demo đầu, giao diện Ursina chưa dùng (đang chờ nhóm chốt giữ làm màn hướng dẫn hay bỏ).

## Chạy kiểm thử

```bash
cd Source
python -m unittest discover -v
```

Bộ test (khoảng 200 test, chạy chừng 30 giây) gồm:

- luật chơi: bảng chuyển tư thế, rơi, thắng, các loại công tắc, tách và ghép khối (`test_rules.py`, `test_spec.py` với mỗi câu luật trích từ đề);
- màn chơi: bộ nạp màn, 33 màn gốc, bộ màn tự sinh (`test_levels.py`, `test_original_levels.py`, `test_gen_levels.py`);
- thuật toán: mê cung mẫu `GridMaze`, BFS đúng số bước tối ưu trên 33 màn, UCS và A* cùng chi phí, hàm chi phí (`test_solvers.py`, `test_bfs.py`, `test_dfs.py`, `test_ucs.py`, `test_astar.py`, `test_costs.py`);
- module chạy solver ở tiến trình riêng và script thực nghiệm (`test_runner.py`, `test_experiments.py`).

Test không cần Ursina.

## Thực nghiệm

```bash
cd Source
python -m experiments.run                          # 5 thuật toán × 33 màn gốc, ghi vào experiments/
python -m experiments.run --levels levels/gen --out experiments/gen   # bộ màn tự sinh
python -m experiments.run --cost unit --out experiments/unit           # chi phí 1 mỗi bước, để đối chiếu
python tools/check_heuristics.py                   # kiểm tra h_M, h_P chấp nhận được và nhất quán (chi phí V13)
```

Mỗi lần đo chạy trong một tiến trình riêng, có giới hạn thời gian (mặc định 60 giây). Thời gian là trung vị của 5 lần chạy không bật `tracemalloc`; bộ nhớ đo ở một lần chạy riêng. Kết quả gồm `raw.csv` (mỗi lần chạy một dòng), `summary.csv` (mỗi cặp màn, thuật toán một dòng, cột theo docs/04 §5) và `run_info.json` (cấu hình máy, commit, hàm chi phí). Mặc định không ghi đè kết quả cũ; thêm `--force` nếu chắc chắn.

Kiểm tra chéo, vẽ hình và sinh bảng cho chương 5 (cần `matplotlib`; thứ tự chạy chính thức: `experiments/README.md`):

```bash
python -m experiments.check_results experiments/summary.csv   # K1–K8 (docs/04 §6)
python -m experiments.charts       # đọc experiments/summary.csv, ghi experiments/figures/ (H1–H6, H8, H9)
python -m experiments.tables       # đọc experiments/summary.csv, ghi experiments/tables.md (T3–T5, Phụ lục A)
python -m experiments.compare_runs <summary.csv lần 1> <summary.csv lần 2>   # kiểm tra tái lập
```

## Cấu trúc thư mục

```
Source/
  main.py              điểm vào: mở giao diện Ursina (chỉ import gui bên trong main())
  requirements.txt     ursina, panda3d (ghim phiên bản)
  bloxorz/             engine luật chơi, dùng chung cho giao diện và solver; chỉ dùng thư viện chuẩn
    state.py           State, Action, Orient, Dir
    level.py           đọc và kiểm tra file màn JSON
    rules.py           step(): một nước đi -> trạng thái mới + sự kiện (công tắc, tách, ghép, rơi, thắng)
    problem.py         giao diện bài toán tìm kiếm cho solver
    costs.py           hàm chi phí không đồng nhất (V13)
    maze.py            GridMaze: mê cung nhỏ cùng giao diện Problem, để thử solver
    serialize.py       chuyển State, Action, Level qua JSON (dùng cho bản demo web)
  solvers/             thuật toán tìm kiếm, mỗi file một lớp con của Solver (base.py)
    bfs.py dfs.py ucs.py astar.py heuristics.py
    runner.py          chạy solver ở tiến trình riêng: hết giờ, Hủy, So sánh; start_solver()/poll() cho giao diện
  gui/                 giao diện 3D Ursina
    app.py             cửa sổ, vòng update(), phím; gọi rules.step() khi chơi tay và runner khi bấm Solve
    board_view.py      dựng bàn từ Level: các loại ô, cầu mở/đóng, ô dễ vỡ vỡ
    block_view.py      khối và hai khối con; hoạt ảnh lăn, tách, ghép, rơi
    hud.py             các nút, lưới chọn màn, khung kết quả, bảng So sánh
    camera_controller.py  góc nhìn: các nấc nghiêng, nhìn từ đỉnh, thu phóng, căn bàn khi khung kết quả hiện
    popup.py           hộp kết thúc màn (thắng, rơi), kéo thả được
    theme.py           font Be Vietnam Pro, thẻ kiểu kính mờ dùng chung
    meshes.py          mesh hộp vát cạnh cho ô và khối
    anim.py            hoạt ảnh hẹn giờ dừng được (tránh lỗi của Ursina khi đổi màn)
    fonts/             font Be Vietnam Pro và giấy phép OFL
  levels/original/     33 màn gốc (JSON)
  levels/gen/          bộ màn tự sinh S1–S3 cho thực nghiệm
  experiments/         run.py: script đo (CSV); gen_levels.py: sinh levels/gen/;
                       convert_original_levels.py: chuyển 33 màn từ dữ liệu bloxorz_gba;
                       check_results.py: kiểm tra chéo K1–K8; charts.py: vẽ hình; tables.py: sinh bảng;
                       compare_runs.py: so hai lần chạy (kiểm tra tái lập); README.md: lệnh và thứ tự chạy
  tools/
    check_heuristics.py  kiểm tra h_M, h_P bằng số liệu trên 33 màn: chấp nhận được, nhất quán, cùng chi phí với UCS
    draw_mazes.py      vẽ các mê cung mẫu của GridMaze ra docs/gridmaze/
  tests/               unit test (unittest)
  server/, web/        bản demo đầu (giao diện web Three.js qua server HTTP), không còn dùng; chờ nhóm đồng ý thì bỏ
```

Quy tắc phụ thuộc: `bloxorz/` không import package nào khác của dự án; `solvers/` chỉ import `bloxorz`; `gui/` chỉ dùng `ALGORITHMS` và `runner` của `solvers`, không gọi thẳng thuật toán. Nhờ vậy engine, solver và test chạy được không cần Ursina (chi tiết: `docs/07-kien-truc-gui-ursina.md`).

## Nguồn và thư viện bên ngoài

- **Bloxorz** (D. Clarke, 2007): luật chơi và thiết kế 33 màn gốc.
- **bloxorz_gba** (J. Coughenour, commit f57ebb6), giấy phép **GPL-3.0**: dữ liệu 33 màn trong `levels/original/` được chuyển từ `game/levels.json` của repo này. https://github.com/jacobcoughenour/bloxorz_gba
- **Ursina 7.0.0** (giấy phép MIT) và **Panda3D 1.10.16** (giấy phép Modified BSD): giao diện 3D. https://www.ursinaengine.org, https://www.panda3d.org
- **Be Vietnam Pro** (The Be Vietnam Pro Project Authors, giấy phép SIL Open Font License 1.1, `gui/fonts/OFL.txt`): font chữ của giao diện. https://github.com/bettergui/BeVietnamPro
- **Matplotlib 3.10.9**: biểu đồ thực nghiệm.
- Bản demo trong `web/` dùng **Three.js r160**, **OrbitControls.js**, **RoundedBoxGeometry.js** (giấy phép MIT, `web/vendor/LICENSE-three.txt`) và phông **Baloo 2**, **Nunito** (SIL Open Font License 1.1, `web/vendor/fonts/OFL-*.txt`).

Danh mục nguồn đầy đủ (kể cả các nguồn chỉ dùng để đối chiếu) nằm ở `docs/06-bao-cao-video.md` mục 3 và `docs/report/tai-lieu-tham-khao.md`.
