# Bloxorz Solver

Đồ án CSC14003 - Project 1. Trò chơi Bloxorz có giao diện 3D, các ô đặc biệt (ô giòn, cầu, ba loại công tắc, tách/ghép khối), 18 màn chơi theo chương, và bốn thuật toán tìm kiếm: BFS, DFS (hoặc IDS), UCS, A*.

## Cách chạy

Yêu cầu: Python 3.10 trở lên. Không cần cài thêm thư viện, chỉ dùng thư viện chuẩn.

```bash
cd Source
python3 main.py      # Windows: python main.py
```

Chương trình khởi động server cục bộ tại `http://localhost:8000` và tự mở trình duyệt. Tùy chọn:

- `--port 8080`: đổi cổng
- `--timeout 30`: giới hạn thời gian mỗi lần giải (giây, mặc định 60)
- `--no-browser`: không tự mở trình duyệt
- `http://localhost:8000/?level=2-1`: mở thẳng một màn (bỏ qua menu), ví dụ `1-1`, `3-2`, `T1`, `B1`

Trình duyệt chạy được trên Windows khi chương trình chạy trong WSL: `localhost` được chuyển tiếp tự động. Giao diện đã kiểm thử trên Microsoft Edge.

## Cách chơi

Mục tiêu: lăn khối tới lỗ vuông đích và **đứng thẳng** trên lỗ. Rơi khỏi bảng hoặc xuống khoảng trống là thua, nhưng có thể quay lại bước trước.

| Thao tác | Phím | Chuột / cảm ứng |
|---|---|---|
| Lăn khối | ← ↑ → ↓ hoặc W A S D | nút mũi tên trên màn hình, vuốt |
| Đổi khối con (sau khi tách) | Space | nút "Đổi khối" |
| Hoàn tác một bước | Z hoặc Backspace | nút "Hoàn tác" |
| Chơi lại màn | R | nút "Chơi lại" |
| Xoay camera 90° | Q / E | kéo chuột rồi nhả, camera tự về nấc gần nhất |
| Đặt lại camera | C | nút "Camera" |
| Gợi ý nước đi | H | nút "Gợi ý" |
| Tạm dừng | Esc | nút ☰ Menu |
| Tắt/bật tiếng | M | nút 🔊 |
| Điều hướng menu | ← ↑ → ↓, Enter | bấm chuột |

Phím mũi tên đi theo hướng nhìn của camera (có thể tắt trong Cài đặt).

**Sao:** ★★★ nếu số bước ≤ số bước tối ưu (`par`), ★★ nếu ≤ 1,5 × `par`, ★ nếu chỉ hoàn thành. Kỷ lục và sao được lưu trong trình duyệt (localStorage), có nút "Xóa tiến trình" trong Cài đặt.

**Mở khóa:** chương 1–5 và hai màn thử thách mở sẵn. Màn bonus B1 cần 36 sao (tổng 51 sao của 17 màn còn lại). Trong Cài đặt có "Mở khóa tất cả màn" để xem mọi màn.

## Chương và màn chơi

| Màn | Tên | Ý tưởng | `par` | Nhóm |
|---|---|---|---|---|
| 1-1 | Đường thẳng | Lăn khối, đứng thẳng lên lỗ đích | 4 | basic |
| 1-2 | Đổi tư thế | Chuyển giữa đứng và nằm | 8 | basic |
| 1-3 | Mê cung nhỏ | Có đường cụt, phải tính trước | 13 | basic |
| 2-1 | Ô cam | Đứng thẳng lên ô giòn thì vỡ | 8 | fragile |
| 2-2 | Lăn nằm qua dải cam | Phải nằm để đi qua dải ô giòn | 14 | fragile |
| 2-3 | Bãi cam | Nhiều ô giòn, chọn đúng chỗ đứng | 19 | fragile |
| 3-1 | Công tắc mềm | Chạm bằng bất kỳ phần nào, cầu đổi trạng thái | 9 | switch |
| 3-2 | Công tắc nặng | Chỉ kích hoạt khi khối đứng | 16 | switch |
| 3-3 | Bật rồi tắt | Bẫy toggle: chạm hai lần là cầu đóng lại | 19 | switch |
| 4-1 | Tách đôi | Tách, đổi khối con, ghép lại | 12 | switch |
| 4-2 | Hai khối hai việc | Một khối con bật cầu cho khối kia đi | 15 | switch |
| 4-3 | Ghép đúng chỗ | Hướng ghép quyết định đường đi tiếp | 23 | switch |
| 5-1 | Cam và công tắc | Ô giòn kết hợp công tắc nặng | 25 | combined |
| 5-2 | Tách trên ô cam | Tách khối, ô giòn, cầu | 28 | combined |
| 5-3 | Đủ mọi thứ | Mọi cơ chế, có công tắc tách nối cầu | 32 | combined |
| T1 | Mê cung lớn | Không gian trạng thái lớn (thử thách) | 46 | combined |
| T2 | Mạng công tắc | Nhiều cầu toggle chéo nhau (thử thách) | 40 | combined |
| B1 | Đường dài | Màn dài, phần thưởng khi đủ sao (bonus) | 39 | combined |

Mỗi chương giới thiệu một cơ chế: chương 2 là ô giòn, chương 3 là công tắc và cầu, chương 4 là tách khối. Các màn đầu tiên của từng cơ chế (1-1, 2-1, 3-1, 3-2, 4-1) có thêm một thẻ giới thiệu ngắn, mở một lần rồi không hiện lại.

`par` là số bước tối ưu của mỗi màn, tính bằng BFS (xem phần Nguồn). Mỗi màn đã được kiểm chứng: bỏ từng loại công tắc thì đường tối ưu dài hơn hoặc không còn lời giải, và bỏ ô giòn thì đường tối ưu ngắn hơn. Vì vậy không có đường tắt bỏ qua cơ chế của màn.

## Cấu trúc thư mục

```
Source/
  main.py              điểm vào: khởi động server, mở trình duyệt
  bloxorz/             engine luật chơi (dùng chung cho GUI và solver)
    state.py           State, Action, Orient, Dir
    level.py           đọc và kiểm tra màn chơi JSON
    rules.py           step(): một nước đi -> trạng thái mới + sự kiện
    problem.py         giao diện bài toán cho solver
    maze.py            GridMaze: mê cung nhỏ cùng giao diện Problem, để thử solver
    serialize.py       chuyển State/Action/Level qua JSON
  solvers/             thuật toán tìm kiếm
    base.py            hợp đồng chung: SearchResult và lớp cơ sở Solver
    runner.py          khung chạy cho GUI: tiến trình riêng, đo thời gian, bộ nhớ, giới hạn thời gian, hủy
    bfs.py dfs.py ucs.py astar.py   mỗi file một lớp con của Solver (astar.py có AStar với h_P, AStarM với h_M)
    heuristics.py      heuristic cho A*: h_M, h_P trên GridMaze và Bloxorz
  server/              API HTTP (api.py: hàm thuần; app.py: server)
  levels/              18 màn chơi, định dạng JSON (mỗi file một màn)
  web/                 giao diện 3D
    index.html style.css
    js/                game.js (điều khiển), screens.js (màn hình phủ),
                       board.js block.js tiles.js (bảng và khối 3D),
                       camera.js input.js ai-panel.js audio.js storage.js strings.js ...
    vendor/            Three.js r160, OrbitControls, RoundedBoxGeometry, phông chữ
  tools/
    draw_mazes.py      vẽ các mê cung mẫu của GridMaze ra docs/gridmaze/ (chạy lại khi sửa MAZES)
  tests/               unit test: luật, đặc tả, màn chơi, API và server, GridMaze,
                       4 solver trên mê cung mẫu (test_solvers.py; solver chưa cài thì bỏ qua)
```

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

## Định dạng màn chơi

Mỗi màn là một file JSON trong `levels/`, tên file là mã màn (ví dụ `2-1.json`):

```json
{
  "name": "Công tắc nặng",
  "chapter": 3, "order": 2,
  "kind": "main",
  "group": "switch",
  "par": 16,
  "intro": "Công tắc nặng chỉ kích hoạt khi khối đứng thẳng trên nó.",
  "unlock_stars": 0,
  "source": "Tự thiết kế cho đồ án",
  "grid": ["S##x", "...b", "...#", "...G"],
  "switches": [
    {"at": [0, 3], "type": "heavy", "effect": "open", "bridges": [[1, 3]]}
  ]
}
```

Trường mới: `chapter`, `order` (thứ tự trong chương), `kind` (`main`, `challenge`, `bonus`), `par` (số bước tối ưu, 0 nghĩa là chưa biết), `intro` (thẻ giới thiệu, có thể `null`), `unlock_stars` (số sao cần để mở).

Ký hiệu trong `grid` (mỗi ký tự là một ô, hiển thị giống hệt trong chú thích của game):

| Ký tự | Ý nghĩa |
|---|---|
| `.` | khoảng trống (rơi là thua) |
| `#` | nền |
| `S` | vị trí xuất phát (đứng) |
| `G` | lỗ vuông đích |
| `F` | ô giòn |
| `b` / `B` | cầu đang đóng / đang mở lúc đầu (cầu đóng trông như khoảng trống) |
| `o` | công tắc mềm |
| `x` | công tắc nặng |
| `@` | công tắc tách |

Cấu hình công tắc trong `switches`:

- Công tắc mềm và nặng: `effect` là `toggle` (đảo trạng thái), `open` hoặc `close` (cố định sau khi kích hoạt), và `bridges` là danh sách ô cầu bị điều khiển.
- Công tắc tách: `targets` là hai ô đích của khối con. Có thể thêm `effect` và `bridges` nếu công tắc tách cũng nối cầu.

`level.py` kiểm tra file trước khi chạy: đúng một `S`, đúng một `G`, mỗi công tắc có cấu hình, cầu được tham chiếu tồn tại, `kind` hợp lệ.

## Chạy kiểm thử

```bash
cd Source
python3 -m unittest -v   # Windows: python -m unittest -v
```

Bộ test gồm: bảng chuyển tư thế, rơi, thắng, các loại công tắc, tách và ghép khối (`test_rules.py`, `test_spec.py` với mỗi câu luật trích từ đề), kiểm tra 18 màn (số lượng, chương, độ khó tăng dần, thứ tự giới thiệu cơ chế) và API/server HTTP.

## Nguồn và thư viện bên ngoài

- **Three.js r160** (`web/vendor/three.module.min.js`), giấy phép MIT, xem `web/vendor/LICENSE-three.txt`. Tải từ `https://cdn.jsdelivr.net/npm/three@0.160.0/`.
- **OrbitControls.js** và **RoundedBoxGeometry.js** lấy từ `examples/jsm/` của Three.js r160, giấy phép MIT.
- **Phông chữ Baloo 2** (700) và **Nunito** (400, 800), giấy phép SIL Open Font License 1.1, lấy từ gói `@fontsource` 5.3.0. Bản Latin và bản tiếng Việt, giấy phép trong `web/vendor/fonts/OFL-*.txt`.
- **Nhạc nền và âm thanh** tự tạo bằng Web Audio API trong `web/js/audio.js`, không dùng file ngoài.
- **18 màn chơi** do nhóm tự thiết kế, không sao chép từ game nào khác. Mỗi file ghi nguồn trong trường `source`. Giá trị `par` được tính bằng một script BFS riêng đặt ngoài repo.
