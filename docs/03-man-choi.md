# Màn chơi: 33 màn của game gốc

## 1. Đã chốt

- Dùng đủ **33 màn của Bloxorz** (Damien Clarke, 2007). Thầy yêu cầu tối thiểu 10 màn; nhóm dùng cả 33 màn làm bộ thực nghiệm cố định.
- Nguồn dữ liệu chính: file `game/levels.json` của bản port Game Boy Advance [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba), commit `f57ebb6`, giấy phép GPL-3.0. README của repo ghi *"Features all 33 levels from the original game"*, và passcode của 33 màn khớp với game gốc.
- Có một lỗi dữ liệu ở màn 3, đã xác định cách sửa (mục 3).

## 2. Các nguồn đã xem

| Nguồn | Có gì | Giấy phép | Dùng làm gì |
|---|---|---|---|
| [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba) (2026) | 33 màn dạng JSON: ô, công tắc với 3 kiểu, trạng thái đầu của cầu, công tắc tách, passcode | GPL-3.0 | **Nguồn chính** |
| [jgordon510/quick_bloxorz](https://github.com/jgordon510/quick_bloxorz) (2021) | 33 màn dạng Tiled JSON | CC BY (theo README) | Đối chiếu |
| [otfried/cs109](https://github.com/otfried/cs109/tree/master/bloxorz/levels), thư mục `bloxorz/levels` (2015, bài tập KAIST) | Màn 1–13 dạng text | Không ghi | Đối chiếu |
| [phamquiluan/BloxorzSolver](https://github.com/phamquiluan/BloxorzSolver) (2018, bài tập HCMUT) | 33 màn dạng ma trận số | Không ghi | Đối chiếu |
| [supersaiyanmode/Bloxorz](https://github.com/supersaiyanmode/Bloxorz) (2012) | 1 màn tự chế, C++/OpenGL | Không ghi | Không dùng: không có màn gốc |
| [chaitanya100100/Bloxorz](https://github.com/chaitanya100100/Bloxorz) (2019) | 2 màn tự chế, C++/OpenGL, không có công tắc tách | Không ghi | Không dùng: không có màn gốc |

Repo không ghi giấy phép thì mặc định không được chép code. Nhóm chỉ dùng các repo đó để đối chiếu dữ liệu và vẫn phải trích dẫn.

## 3. Kết quả đối chiếu

**Cách làm:** so từng màn của nguồn chính với ba nguồn đối chiếu: từng ô, ô xuất phát, liên kết công tắc với cầu, kiểu công tắc, vị trí hai khối con sau khi tách. Hai bản được căn theo ô đích, vì mỗi màn chỉ có một ô đích.

| Màn | Chỗ lệch | Kết luận |
|---|---|---|
| **3** | Bản GBA thiếu 4 ô sàn ở góc dưới phải; cả ba nguồn kia đều có | **Sửa bản GBA:** thêm sàn tại (6, 11), (7, 12), (7, 13), (7, 14) |
| 2, 7, 10, 17, 18 | Quick Bloxorz ghi công tắc kiểu `on`, bản GBA ghi `toggle` | Theo GBA. otfried (màn 2, 7, 10) và phamquiluan (cả 5 màn) cũng ghi `toggle` |
| 4 | Quick Bloxorz lệch hình dạng bàn | Theo GBA, khớp otfried và phamquiluan |
| 11, 15, 23 | Quick Bloxorz lệch trạng thái đầu của cầu hoặc liên kết công tắc | Theo GBA, khớp phamquiluan (màn 11 khớp cả otfried) |
| 30 | Quick Bloxorz lệch 6 ô và một liên kết | Theo GBA, khớp phamquiluan |
| 16 | phamquiluan lệch vị trí đáp của một công tắc tách | Theo GBA, khớp Quick Bloxorz |
| 1 | phamquiluan lệch ô xuất phát | Theo GBA, khớp otfried và Quick Bloxorz |
| 5, 22, 25, 31 | Bản GBA có vài ô cầu luôn mở và không nối công tắc nào; nguồn khác ghi là sàn | Như nhau về luật: cầu luôn mở chính là sàn |

**Kết luận:** sau khi sửa màn 3, mọi chỗ lệch đều nghiêng về bản GBA theo đa số nguồn. Bộ giải tham khảo (mục 4) giải được cả 33 màn theo luật ở [02-luat-choi.md](02-luat-choi.md).

## 4. Danh sách 33 màn

Số liệu tính trên lưới 10 hàng × 15 cột sau khi sửa màn 3. Dấu `·` nghĩa là không có.

| Màn | Passcode | Nhóm | Số ô | Ô dễ vỡ | CT mềm | CT nặng | CT tách | Ô cầu | Kiểu công tắc | Bước tối ưu* |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 780464 | G1 | 35 | · | · | · | · | · | · | 7 |
| 2 | 290299 | G3 | 63 | · | 1 | 1 | · | 4 | đảo | 17 |
| 3 | 918660 | G1 | 48 | · | · | · | · | · | · | 19 |
| 4 | 520967 | G2 | 69 | 31 | · | · | · | · | · | 28 |
| 5 | 028431 | G3 | 73 | · | 4 | · | · | 6 | đảo, chỉ mở, chỉ đóng | 33 |
| 6 | 524383 | G1 | 55 | · | · | · | · | · | · | 35 |
| 7 | 189493 | G3 | 56 | · | · | 1 | · | 1 | đảo | 44 |
| 8 | 499707 | G5 | 54 | · | · | · | 1 | · | · | 10 |
| 9 | 074355 | G5 | 39 | · | · | · | 1 | · | · | 24 |
| 10 | 300590 | G5 | 55 | · | 1 | 1 | 1 | 6 | đảo | 57 |
| 11 | 291709 | G3 | 51 | · | 1 | · | · | 2 | chỉ đóng | 47 |
| 12 | 958640 | G3 | 60 | · | · | 2 | · | 2 | đảo | 65 |
| 13 | 448106 | G2 | 82 | 22 | · | · | · | · | · | 46 |
| 14 | 210362 | G3 | 68 | · | · | 2 | · | 4 | đảo | 67 |
| 15 | 098598 | G5 | 72 | · | 3 | 1 | 1 | 8 | đảo, chỉ đóng | 57 |
| 16 | 000241 | G5 | 42 | · | · | 2 | 5 | 4 | chỉ mở | 28 |
| 17 | 683596 | G3 | 70 | · | 1 | 4 | · | 4 | đảo, chỉ mở, chỉ đóng | 106 |
| 18 | 284933 | G3 | 59 | · | 5 | 1 | · | 7 | đảo, chỉ mở, chỉ đóng | 85 |
| 19 | 119785 | G3 | 66 | · | 3 | · | · | 4 | đảo, chỉ mở, chỉ đóng | 67 |
| 20 | 543019 | G5 | 66 | · | 5 | · | 1 | 6 | đảo, chỉ đóng | 56 |
| 21 | 728724 | G3 | 61 | · | · | 2 | · | 2 | đảo | 71 |
| 22 | 987319 | G3 | 59 | · | 2 | 2 | · | 3 | đảo, chỉ đóng | 65 |
| 23 | 293486 | G5 | 89 | 18 | 3 | 1 | 1 | 8 | đảo, chỉ mở, chỉ đóng | 75 |
| 24 | 088198 | G5 | 59 | · | · | 4 | 1 | 6 | chỉ mở | 57 |
| 25 | 250453 | G3 | 62 | · | 2 | 1 | · | 9 | đảo, chỉ mở, chỉ đóng | 55 |
| 26 | 426329 | G5 | 56 | · | 1 | 1 | 1 | 4 | chỉ mở, chỉ đóng | 104 |
| 27 | 660141 | G4 | 88 | 27 | 2 | 1 | · | 2 | chỉ đóng | 71 |
| 28 | 769721 | G5 | 69 | 7 | 1 | · | 1 | 4 | chỉ đóng | 100 |
| 29 | 691859 | G3 | 65 | · | 3 | 3 | · | 17 | chỉ mở, chỉ đóng | 104 |
| 30 | 280351 | G4 | 87 | 40 | · | 3 | · | 5 | đảo, chỉ mở, chỉ đóng | 114 |
| 31 | 138620 | G4 | 80 | 8 | 2 | 3 | · | 14 | đảo, chỉ mở, chỉ đóng | 91 |
| 32 | 879021 | G3 | 63 | · | · | 3 | · | 8 | đảo | 129 |
| 33 | 614955 | G3 | 99 | · | 12 | 1 | · | 5 | chỉ mở, chỉ đóng | 65 |

**Số ô** là số ô không trống, tính cả ô cầu. **CT** là công tắc.

\* **Bước tối ưu** là số lần lăn ít nhất, mỗi bước chi phí 1. Số này do một bộ giải BFS tham khảo tính ra: Claude (trợ lý AI) viết bộ giải này khi soạn tài liệu, dùng đúng luật ở 02. Bộ giải đó không nằm trong code nộp bài. Bảng chỉ dùng làm đáp án để kiểm tra BFS, và UCS khi đặt chi phí bằng 1. Nếu nhóm dùng bảng này thì ghi vào phụ lục AI.

Các màn gốc khá nhỏ: bộ giải tham khảo giải mỗi màn dưới 50 ms và gặp nhiều nhất khoảng 5.100 trạng thái (màn 26). Ảnh hưởng của điều này tới thực nghiệm được bàn ở [04 §4](04-thuc-nghiem.md#4-cách-đo).

## 5. Nhóm độ khó

Đề gợi ý chia bộ test theo độ khó: không có ô nâng cao, có ô dễ vỡ, có công tắc, và kết hợp. Nhóm tách thêm "tách khối" thành một nhóm riêng, vì khi tách, trạng thái gồm hai khối con và không gian trạng thái khác hẳn.

| Nhóm | Mô tả | Màn | Số màn |
|---|---|---|---|
| G1 | Cơ bản: chỉ sàn, ô trống, đích | 1, 3, 6 | 3 |
| G2 | Ô dễ vỡ | 4, 13 | 2 |
| G3 | Công tắc mềm/nặng và cầu | 2, 5, 7, 11, 12, 14, 17, 18, 19, 21, 22, 25, 29, 32, 33 | 15 |
| G4 | Ô dễ vỡ kết hợp công tắc | 27, 30, 31 | 3 |
| G5 | Có công tắc tách | 8, 9, 10, 15, 16, 20, 23, 24, 26, 28 | 10 |

**Dự phòng khi thiếu thời gian** (nhóm phải quyết trước M2): dùng bộ rút gọn 12 màn, vẫn đủ 5 nhóm: 1, 3, 6 · 4, 13 · 2, 5, 11 · 27, 30 · 8, 9.

**Bộ màn tự sinh.** Ngoài 33 màn, thực nghiệm dùng thêm ba nhóm màn sinh bằng script, S1–S3 ([04 §8](04-thuc-nghiem.md#8-bộ-màn-tự-sinh)): sân trống lớn dần, sân có số cầu tăng dần, và màn không có lời giải. Các màn này nằm riêng trong `Source/levels/gen/`, không tính vào 33 màn và không cần hiện trong danh sách chọn màn của GUI. Riêng màn không lời giải nên mở được trong GUI để demo thông báo.

## 6. Định dạng file màn của nhóm

Đây là đề xuất; TV2, TV1 và TV3 (người viết bộ nạp màn) chốt trong ngày 19/10. Mỗi màn là một file `Source/levels/NN.json`. Ví dụ màn 2:

```json
{
  "id": 2,
  "passcode": "290299",
  "group": "G3",
  "source": "Bloxorz (D. Clarke, 2007), màn 2; dữ liệu: jacobcoughenour/bloxorz_gba (GPL-3.0), commit f57ebb6",
  "grid": [
    "---------------",
    "------oooo--ooo",
    "oooo--ooXo--oGo",
    "oo@o--oooo--ooo",
    "oooo--oooo--ooo",
    "oSoobboooobbooo",
    "oooo--oooo-----",
    "---------------",
    "---------------",
    "---------------"
  ],
  "switches": [
    {"at": [3, 2], "links": [{"cell": [5, 4], "mode": "toggle"}, {"cell": [5, 5], "mode": "toggle"}]},
    {"at": [2, 8], "links": [{"cell": [5, 10], "mode": "toggle"}, {"cell": [5, 11], "mode": "toggle"}]}
  ],
  "splits": []
}
```

- `grid`: 10 hàng × 15 cột, giữ nguyên khung bàn của game gốc. Ký hiệu theo bảng ở [02 §2](02-luat-choi.md#2-bàn-chơi-và-các-loại-ô). Màn tự sinh có kích thước khác, nên bộ nạp phải đọc kích thước từ file, không cố định 10 × 15.
- `switches`: `at` là ô công tắc (hàng, cột). Loại công tắc (mềm `@` hay nặng `X`) đọc từ `grid`. `links` là danh sách ô cầu cùng kiểu tác động.
- `splits`: mỗi phần tử có dạng `{"at": [r, c], "to": [[r1, c1], [r2, c2]]}`, trong đó `at` là ô công tắc tách và `to` là hai ô đáp của hai khối con.

**Bảng chuyển đổi từ bản GBA**

| Bản GBA | Nghĩa | File của nhóm |
|---|---|---|
| `' '` | trống | `-` |
| `'b'` | sàn; ô `spawn` thì thành `S` | `o` |
| `'e'` | đích | `G` |
| `'f'` | ô dễ vỡ | `F` |
| `'s'` | công tắc mềm | `@` |
| `'h'` | công tắc nặng | `X` |
| `'v'` | công tắc tách | `T` |
| `'l'`, `'r'` | ô cầu, đóng lúc đầu (hai nửa của hình cây cầu) | `b` |
| `'k'`, `'q'` | ô cầu, mở lúc đầu | `B` |
| `"spawn": [x, y]` | ô xuất phát | `S` tại hàng y, cột x |
| `"switches": {"K": [[bx, by, mode], …]}` | công tắc tại cột K // 10, hàng K % 10 | `{"at": [K % 10, K // 10], "links": [{"cell": [by, bx], "mode": …}]}` |
| `mode`: `onoff` / `on` / `off` | kiểu tác động | `toggle` / `on` / `off` |
| `"splits": {"K": [x1, y1, x2, y2]}` | công tắc tách tại cột K // 10, hàng K % 10 | `{"at": [K % 10, K // 10], "to": [[y1, x1], [y2, x2]]}` |
| `"code": 28431` | passcode, bị mất số 0 đầu | `"028431"`: chuỗi đủ 6 chữ số |

**Ba bẫy khi chuyển đổi:** bản GBA dùng (x, y) = (cột, hàng); khóa công tắc là x × 10 + y, không phải hàng × 15 + cột; passcode phải giữ số 0 ở đầu.

**Kiểm tra tự động sau khi chuyển:**
- Mỗi màn gốc có lưới 10 × 15 (màn tự sinh thì tùy kích thước), đúng 1 ô `S` và 1 ô `G`.
- Mọi `at` của `switches` trỏ vào ô `@` hoặc `X`. Mọi `cell` trỏ vào ô `b` hoặc `B`. Mọi `at` của `splits` trỏ vào ô `T`. Mọi ô trong `to` không phải ô trống.
- Số ô từng loại khớp bảng ở mục 4.
- Khi BFS chạy được: số bước khớp cột "Bước tối ưu".

## 7. Trích dẫn trong báo cáo

Câu mẫu cho mục "Bộ màn" của chương Thực nghiệm:

> Bộ thực nghiệm gồm 33 màn của game Bloxorz gốc [2]. Dữ liệu màn được chuyển đổi từ bản port Game Boy Advance [3] (giấy phép GPL-3.0), đối chiếu với ba nguồn độc lập [4], [5], [6]; màn 3 được bổ sung 4 ô bị thiếu trong [3].

Danh mục tài liệu tham khảo tương ứng có ở [06 §3](06-bao-cao-video.md#3-tài-liệu-tham-khảo-đã-có).
