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

`requirements.txt` ghim `ursina==7.0.0` và `panda3d==1.10.16`. Engine, các thuật toán và test chỉ dùng thư viện chuẩn, nên chạy được cả trên máy chưa cài Ursina; chỉ giao diện cần hai thư viện này.

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

### Các nút

| Nút | Tác dụng |
|---|---|
| Màn mới (màn 01) | Bắt đầu lại từ màn 01 |
| Chơi lại | Như phím R |
| Chọn màn… | Mở lưới 33 màn, bấm một màn để chuyển tới |
| Giải bằng BFS / DFS / UCS / A* | Chạy thuật toán ở tiến trình riêng. Giải được thì khối tự lăn theo lời giải, khung góc trái dưới hiện số bước, chi phí, số nút mở rộng và sinh, frontier lớn nhất, số trạng thái đã thăm, thời gian tìm kiếm, bộ nhớ |
| So sánh | Chạy lần lượt BFS, DFS, UCS, A* (h_P) và A* (h_M) trên màn đang mở, hiện bảng kết quả |
| Hủy | Dừng thuật toán đang chạy hoặc khối đang tự lăn |

Mỗi lần giải có bốn kết quả: giải được, không có lời giải, hết giờ (quá 60 giây thì tiến trình bị dừng), lỗi hoặc đã hủy. Trong lúc thuật toán chạy, cửa sổ vẫn phản hồi và nút Hủy dùng được. Thời gian và bộ nhớ hiện trên giao diện chỉ để tham khảo; số liệu trong báo cáo lấy từ script thực nghiệm.

## Cách chơi

Mục tiêu: lăn khối 1×1×2 tới lỗ vuông đích và **đứng thẳng** trên lỗ. Khối chạm ô trống hoặc ra ngoài bàn thì rơi, thua.

| Ô | Hình trên giao diện | Luật |
|---|---|---|
| Sàn | ô xám | Đi bình thường |
| Đích | lỗ vuông tối có viền | Khối đứng thẳng trên ô này thì thắng |
| Ô dễ vỡ | ô cam | Khối đứng thẳng lên thì ô vỡ, khối rơi |
| Công tắc mềm | đĩa tròn trắng | Bất kỳ phần nào của khối chạm vào đều kích hoạt |
| Công tắc nặng | hình X đỏ | Chỉ kích hoạt khi khối đứng thẳng trên nó |
| Công tắc tách | hình "( )" xanh | Khối đứng lên thì tách thành hai khối con 1×1×1 ở hai ô định sẵn |
| Cầu mở | ô gỗ nâu | Đi như sàn |
| Cầu đóng | ô sẫm | Như ô trống: đi vào là rơi |

Khi công tắc tác động, khối tách hay ghép, giao diện hiện một dòng thông báo ngắn dưới dòng thắng thua.

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

Các file `levels/*.json` ngoài thư mục `original/` (1-1 … 5-3, T1, T2, B1) là 18 màn tự thiết kế của bản demo đầu, giao diện Ursina chưa dùng (đang chờ nhóm chốt giữ làm màn hướng dẫn hay bỏ).

## Chạy kiểm thử

```bash
cd Source
python -m unittest discover -v
```

Bộ test gồm bảng chuyển tư thế, rơi, thắng, các loại công tắc, tách và ghép khối (`test_rules.py`, `test_spec.py` với mỗi câu luật trích từ đề), bộ nạp màn, các solver trên mê cung mẫu `GridMaze` (`test_solvers.py`, `test_bfs.py`) và module chạy solver ở tiến trình riêng (`test_runner.py`). Test không cần Ursina.

## Thực nghiệm

_(TV2 bổ sung khi có script đo V23: lệnh chạy, file CSV kết quả, lệnh vẽ biểu đồ.)_

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
    maze.py            GridMaze: mê cung nhỏ cùng giao diện Problem, để thử solver
  solvers/             thuật toán tìm kiếm, mỗi file một lớp con của Solver (base.py)
    bfs.py dfs.py ucs.py astar.py heuristics.py
    runner.py          chạy solver ở tiến trình riêng: hết giờ, Hủy, So sánh; start_solver()/poll() cho giao diện
  gui/                 giao diện 3D Ursina
    app.py             cửa sổ, vòng update(), phím; gọi rules.step() khi chơi tay và runner khi bấm Solve
    board_view.py      dựng bàn từ Level: các loại ô, cầu mở/đóng, ô dễ vỡ vỡ
    block_view.py      khối và hai khối con; hoạt ảnh lăn, tách, ghép, rơi
    hud.py             các nút, lưới chọn màn, khung kết quả, bảng So sánh
  levels/original/     33 màn gốc (JSON)
  tools/draw_mazes.py  vẽ các mê cung mẫu của GridMaze ra docs/gridmaze/
  tests/               unit test (unittest)
  server/, web/        bản demo đầu (giao diện web Three.js qua server HTTP), không còn dùng; chờ nhóm đồng ý thì bỏ
```

Quy tắc phụ thuộc: `bloxorz/` không import package nào khác của dự án; `solvers/` chỉ import `bloxorz`; `gui/` chỉ dùng `ALGORITHMS` và `runner` của `solvers`, không gọi thẳng thuật toán. Nhờ vậy engine, solver và test chạy được không cần Ursina (chi tiết: `docs/07-kien-truc-gui-ursina.md`).

## Nguồn và thư viện bên ngoài

- **Bloxorz** (D. Clarke, 2007): luật chơi và thiết kế 33 màn gốc.
- **bloxorz_gba** (J. Coughenour, commit f57ebb6), giấy phép **GPL-3.0**: dữ liệu 33 màn trong `levels/original/` được chuyển từ `game/levels.json` của repo này. https://github.com/jacobcoughenour/bloxorz_gba
- **Ursina 7.0.0** (giấy phép MIT) và **Panda3D 1.10.16** (giấy phép Modified BSD): giao diện 3D. https://www.ursinaengine.org, https://www.panda3d.org
- Bản demo trong `web/` dùng **Three.js r160**, **OrbitControls.js**, **RoundedBoxGeometry.js** (giấy phép MIT, `web/vendor/LICENSE-three.txt`) và phông **Baloo 2**, **Nunito** (SIL Open Font License 1.1, `web/vendor/fonts/OFL-*.txt`).

Danh mục nguồn đầy đủ (kể cả các nguồn chỉ dùng để đối chiếu) nằm ở `docs/06-bao-cao-video.md` mục 3.
