# Bloxorz Solver

Đồ án CSC14003 - Project 1. Trò chơi Bloxorz có giao diện 3D, các ô đặc biệt (ô giòn, cầu, ba loại công tắc, tách/ghép khối), và bốn thuật toán tìm kiếm: BFS, DFS (hoặc IDS), UCS, A*.

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
- `http://localhost:8000/?level=08`: mở thẳng một màn

Trình duyệt chạy được trên Windows khi chương trình chạy trong WSL: `localhost` được chuyển tiếp tự động.

## Cấu trúc thư mục

```
Source/
  main.py              điểm vào: khởi động server, mở trình duyệt
  bloxorz/             engine luật chơi (dùng chung cho GUI và solver)
    state.py           State, Action, Orient, Dir
    level.py           đọc và kiểm tra màn chơi JSON
    rules.py           step(): một nước đi -> trạng thái mới + sự kiện
    problem.py         giao diện bài toán cho solver
    serialize.py       chuyển State/Action/Level qua JSON
  solvers/             thuật toán tìm kiếm
    base.py            khung chạy: đo thời gian, bộ nhớ, giới hạn thời gian
    bfs.py dfs.py ucs.py astar.py   mỗi file một solver
  server/              API HTTP (api.py: hàm thuần; app.py: server)
  web/                 giao diện 3D (HTML, CSS, JavaScript + Three.js)
  levels/              10 màn chơi, định dạng JSON
  tests/               unit test và test API
```

## Luật chơi và các giả định

Luật theo đề bài (mục 2). Các điểm đề bài chưa nói rõ, nhóm đã chọn như sau:

- **Khối con (sau khi tách) đứng trên ô giòn** thì ô vỡ và khối rơi, vì khối con không ở tư thế nằm.
- **Khối con chỉ kích hoạt công tắc mềm.** Công tắc nặng và công tắc tách chỉ kích hoạt khi khối đứng nguyên vẹn, theo đúng đề bài.
- **Khối nằm ngang qua ô đích không thắng.** Khối con lăn vào ô đích cũng không thắng: khối phải được ghép lại rồi đứng lên ô đích.
- **Công tắc kích hoạt mỗi lần khối lăn vào ô đó.** Với công tắc mềm, mọi phần của khối đều tính là chạm.
- **Đóng cầu ngay dưới khối** thì khối rơi.
- **Hai khối con kề nhau (chung cạnh)** tự ghép thành khối nằm.

Trạng thái đầy đủ gồm vị trí, tư thế và tập các cầu đang mở. Hai trạng thái cùng vị trí khối nhưng khác cấu hình cầu là hai trạng thái khác nhau.

## Định dạng màn chơi

Mỗi màn là một file JSON trong `levels/`:

```json
{
  "name": "Công tắc nặng",
  "group": "switch",
  "source": "Tự thiết kế cho đồ án",
  "grid": ["S##x", "...b", "...#", "...G"],
  "switches": [
    {"at": [0, 3], "type": "heavy", "effect": "open", "bridges": [[1, 3]]}
  ]
}
```

Ký hiệu trong `grid` (mỗi ký tự là một ô):

| Ký tự | Ý nghĩa |
|---|---|
| `.` | khoảng trống (rơi là thua) |
| `#` | nền |
| `S` | vị trí xuất phát (đứng) |
| `G` | lỗ đích |
| `F` | ô giòn |
| `b` / `B` | cầu đang đóng / đang mở lúc đầu |
| `o` | công tắc mềm |
| `x` | công tắc nặng |
| `@` | công tắc tách |

Cấu hình công tắc trong `switches`:

- Công tắc mềm và nặng: `effect` là `toggle` (đảo trạng thái), `open` hoặc `close` (cố định sau khi kích hoạt), và `bridges` là danh sách ô cầu bị điều khiển.
- Công tắc tách: `targets` là hai ô đích của khối con.

`level.py` kiểm tra file trước khi chạy: đúng một `S`, đúng một `G`, mỗi công tắc có cấu hình, cầu được tham chiếu tồn tại.

## Điều khiển

- Mũi tên hoặc `W A S D`: lăn khối
- `Space`: đổi khối con đang điều khiển (khi đã tách)
- `R`: chơi lại màn · `Z`: hoàn tác một bước
- Chuột: kéo để xoay, cuộn để phóng to
- Nút BFS / DFS / UCS / A*: giải từ vị trí hiện tại và phát lại lời giải. Nút Dừng để ngắt.

## Chạy kiểm thử

```bash
cd Source
python3 -m unittest -v   # Windows: python -m unittest -v
```

Bộ test gồm: bảng chuyển tư thế, rơi, thắng, các loại công tắc, tách và ghép khối, kiểm tra định dạng màn, API và server HTTP.

## Nguồn và thư viện bên ngoài

- **Three.js r160** (`web/vendor/three.module.min.js`), giấy phép MIT, xem `web/vendor/LICENSE-three.txt`. Tải từ `https://cdn.jsdelivr.net/npm/three@0.160.0/`.
- **OrbitControls.js** (`web/vendor/OrbitControls.js`) lấy từ `examples/jsm/controls/` của Three.js r160, giấy phép MIT.
- **10 màn chơi** trong `levels/` do nhóm tự thiết kế, không sao chép từ game nào khác. Mỗi file ghi rõ nguồn trong trường `source`.
