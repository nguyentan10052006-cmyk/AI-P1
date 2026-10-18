# Luật chơi chuẩn

Luật dùng chung cho engine, 4 thuật toán, GUI và bộ test. Ai thấy chỗ nào sai hoặc thiếu thì báo TV1 (chủ engine), không tự sửa trong code của mình.

## 1. Nguồn luật và thứ tự ưu tiên

1. **Đề bài**, mục 2 (`docs/AI - Project 1.pdf`). Đây là luật được chấm điểm.
2. **Bảng hỏi đáp của thầy.**
3. **Hướng dẫn chính thức của game gốc** trên Coolmath Games (tác giả Damien Clarke, 2007): <https://www.coolmathgames.com/0-bloxorz>. Hai câu then chốt: *"If your block stands up vertically on an orange tile, the tile will give way"* và *"small blocks cannot go through the exit hole -- only a complete block can finish the stage"*.
4. **Bản port Game Boy Advance của game gốc**, [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba) (GPL-3.0, file `game/src/level_scene.cpp`). Dùng để biết game gốc xử lý những chỗ hướng dẫn không nói rõ. Chỉ đọc để đối chiếu, không chép code.

Hai repo được gợi ý trong buổi họp, [supersaiyanmode/Bloxorz](https://github.com/supersaiyanmode/Bloxorz) và [chaitanya100100/Bloxorz](https://github.com/chaitanya100100/Bloxorz), đã được xem nhưng không dùng. Lý do: chỉ có 1–2 màn tự chế, không có công tắc tách, và không có giấy phép.

## 2. Bàn chơi và các loại ô

Tọa độ là **(hàng, cột)**, viết (r, c). Hàng tăng xuống dưới, cột tăng sang phải. Các hướng: U lên (r − 1), D xuống (r + 1), L trái (c − 1), R phải (c + 1).

Khối 1×1×2 bắt đầu ở tư thế **đứng** trên ô xuất phát.

| Loại ô | Ký hiệu trong file màn | Khối nguyên đứng | Khối nguyên nằm | Khối con 1×1×1 |
|---|---|---|---|---|
| Trống hoặc ngoài bàn | `-` | rơi | rơi, kể cả khi chỉ một nửa khối ở trên | rơi |
| Sàn | `o` | được | được | được |
| Xuất phát | `S` | như sàn | như sàn | như sàn |
| Đích | `G` | **thắng** | được, không thắng | được, không thắng, không rơi |
| Ô dễ vỡ (màu cam) | `F` | **vỡ, khối rơi** | được | được, không vỡ |
| Cầu đang đóng | `b` (đóng lúc đầu) | rơi | rơi | rơi |
| Cầu đang mở | `B` (mở lúc đầu) | được | được | được |
| Công tắc mềm (tròn) | `@` | kích hoạt | kích hoạt | kích hoạt |
| Công tắc nặng (hình X) | `X` | kích hoạt | không kích hoạt | không kích hoạt |
| Công tắc tách (hình "( )") | `T` | tách khối | không có tác dụng | không có tác dụng |

Mọi loại công tắc và ô đích đều đỡ được khối như sàn. Cầu có hai trạng thái, đổi được trong lúc chơi; `b` và `B` trong file màn chỉ là trạng thái lúc đầu.

**Ba kiểu tác động của công tắc lên cầu.** Mỗi liên kết công tắc → ô cầu có một kiểu:
- `toggle` (đảo): mỗi lần kích hoạt thì đổi mở ↔ đóng.
- `on` (chỉ mở): sau khi kích hoạt, cầu mở; bấm lại không đổi gì.
- `off` (chỉ đóng): sau khi kích hoạt, cầu đóng; bấm lại không đổi gì.

Đề gọi `on` và `off` chung là "permanent". Một công tắc có thể nối nhiều ô cầu với các kiểu khác nhau (ví dụ màn 29).

## 3. Bảng chuyển hướng và vị trí

Ba tư thế của khối nguyên, xác định bằng ô neo (r, c):
- `S` đứng: chiếm (r, c).
- `H` nằm ngang: chiếm (r, c) và (r, c + 1); ô neo là ô bên trái.
- `V` nằm dọc: chiếm (r, c) và (r + 1, c); ô neo là ô bên trên.

| Tư thế hiện tại | U | D | L | R |
|---|---|---|---|---|
| `S` tại (r, c) | `V` tại (r − 2, c) | `V` tại (r + 1, c) | `H` tại (r, c − 2) | `H` tại (r, c + 1) |
| `H` tại (r, c) | `H` tại (r − 1, c) | `H` tại (r + 1, c) | `S` tại (r, c − 1) | `S` tại (r, c + 2) |
| `V` tại (r, c) | `S` tại (r − 1, c) | `S` tại (r + 2, c) | `V` tại (r, c − 1) | `V` tại (r, c + 1) |

Đọc bảng: khối đứng tại (5, 5) lăn U thì thành nằm dọc tại (3, 5), tức chiếm (3, 5) và (4, 5).

Khối con tại (r, c) mỗi bước chỉ đi đúng 1 ô theo hướng đã chọn.

## 4. Một lượt đi được xử lý theo thứ tự

**Khối nguyên lăn một bước:**
1. Tính tư thế và ô neo mới theo bảng ở mục 3.
2. Mọi ô khối mới chiếm phải nằm trong bàn, không phải ô trống, không phải cầu đang đóng. Sai thì hành động bị loại; trên GUI là khối rơi và thua.
3. Khối đứng trên ô dễ vỡ: hành động bị loại.
4. Khối đứng trên ô đích: **thắng**. Đây là trạng thái đích.
5. Kích hoạt công tắc tại các ô khối vừa tới. Công tắc mềm: mọi ô khối chiếm. Công tắc nặng: chỉ khi khối đứng. Cập nhật cầu theo kiểu của từng liên kết.
6. Nếu có ô khối đang chiếm là cầu vừa bị đóng ở bước 5: hành động bị loại.
7. Khối đứng trên công tắc tách: khối thành hai khối con tại hai ô ghi trong file màn.

**Một khối con đi một bước (khi đã tách):**
1. Khối con được chọn đi 1 ô theo hướng.
2. Ô mới phải nằm trong bàn, không trống, không phải cầu đang đóng. Ô dễ vỡ, ô đích, các loại công tắc đều được.
3. Ô mới là công tắc mềm thì kích hoạt và cập nhật cầu.
4. Nếu một trong hai khối con đang đứng trên cầu vừa bị đóng: hành động bị loại.
5. Hai khối con kề cạnh nhau thì ghép thành khối nằm. Cùng hàng: `H` neo ở ô bên trái. Cùng cột: `V` neo ở ô bên trên.

**Số bước** của lời giải là số lần lăn, gồm cả các bước của khối con. Rơi không phải là một bước: thuật toán không bao giờ chọn hành động bị loại.

## 5. Các điểm đề chưa rõ đã được chốt

Bảy dòng đầu là bảy câu hỏi ở slide 12 của buổi họp. Nhóm đã chọn "dùng luật chuẩn của game gốc", nên mỗi dòng ghi căn cứ từ đề hoặc từ game gốc.

| # | Tình huống | Chốt | Căn cứ |
|---|---|---|---|
| 1 | Khối con đứng trên ô dễ vỡ | Không vỡ | Đề 2.5 chỉ nói khối 1×1×2 đứng thì làm vỡ ô; bản GBA cũng chỉ xét khối nguyên đứng |
| 2 | Khối con đi vào ô đích | Như sàn: không thắng, không rơi | Đề 2.5 nói khối con không hoàn thành được màn; hướng dẫn gốc nói chỉ khối nguyên mới qua được lỗ |
| 3 | Công tắc tách có điều khiển cầu không | Không | Không màn gốc nào có công tắc tách nối với cầu (đã kiểm tra dữ liệu 33 màn) |
| 4 | Cầu đóng khi khối đang ở trên | Khối rơi, hành động bị loại | Đề 2.5: cầu đóng như ô trống. Đề 2.1: một phần khối ở trên ô trống thì rơi. Bản GBA không xét trường hợp này; bộ giải tham khảo cho thấy số bước tối ưu của cả 33 màn giống nhau theo cả hai cách |
| 5 | Hai khối con kề nhau | Tự ghép thành khối nằm; kề chéo thì không ghép | Đề 2.5 và hướng dẫn gốc ("rejoin into a normal block when both are placed next to each other") |
| 6 | Công tắc kích hoạt khi nào | Mỗi lần khối hoặc khối con lăn tới ô công tắc; không cần đứng lại trên đó | Hướng dẫn gốc; bản GBA kích hoạt sau mỗi bước lăn tới |
| 7 | Đổi khối con đang điều khiển có tính bước không | Không tính; trong tìm kiếm, đây không phải một hành động | Game gốc chỉ đếm số lần lăn; đề định nghĩa độ dài lời giải là số lần lăn |
| 8 | Khối nằm đè lên hai công tắc | Kích hoạt cả hai; ô trên hoặc ô trái trước | Bản GBA |
| 9 | Bấm `on` khi cầu đã mở, hoặc `off` khi cầu đã đóng | Không đổi gì | Đề 2.5 (permanent) |
| 10 | Khối con vừa tách ra đáp xuống ô công tắc | Không kích hoạt | Bản GBA. Trong 33 màn, chỉ xảy ra với công tắc tách và công tắc nặng, vốn khối con không kích hoạt được |

Ví dụ thật cho dòng 4: ở màn 20, công tắc mềm tại (6, 12) đảo ô cầu kề nó tại (6, 11). Khối nằm ngang đè lên cả hai ô sẽ tự đóng cầu dưới mình và rơi.

## 6. Trạng thái tìm kiếm phải chứa gì

**Phải có:**
- Tư thế: đứng, nằm ngang, nằm dọc, hoặc đã tách.
- Vị trí: ô neo của khối nguyên; khi đã tách là cặp hai ô, sắp xếp tăng dần.
- Trạng thái mở hoặc đóng của **mọi** ô cầu. Đề mục 3.1 nhấn mạnh: cùng vị trí khối nhưng khác trạng thái cầu là hai trạng thái khác nhau.

**Không cần:**
- "Ô dễ vỡ đã vỡ": đứng lên là rơi ngay, nên không có trạng thái ô đã vỡ mà khối vẫn còn trên bàn.
- "Công tắc đã bấm": công tắc không có trạng thái riêng, chỉ cầu có.
- "Khối con nào đang được điều khiển": thuật toán chọn thẳng khối con trong hành động (`U1` … `R2`).

## 7. Bộ kiểm thử luật

Mỗi luật có ít nhất một test. Chủ module viết test của module mình, trước khi cài.

| Mã | Kiểm tra | Chủ |
|---|---|---|
| T01 | Đủ 12 trường hợp của bảng chuyển ở mục 3 | TV1 |
| T02 | Lăn ra ngoài bàn thì hành động bị loại | TV1 |
| T03 | Khối nằm, một nửa trên ô trống: bị loại | TV1 |
| T04 | Đứng trên ô đích: thắng | TV1 |
| T05 | Nằm đè lên ô đích: không thắng | TV1 |
| T06 | Phát lại `R D D R R D R` trên màn 1: thắng đúng ở bước 7 | TV1 |
| T07 | Đứng trên ô dễ vỡ: bị loại | TV3 |
| T08 | Nằm trên ô dễ vỡ: được | TV3 |
| T09 | Cầu đóng như ô trống, cầu mở như sàn | TV3 |
| T10 | Công tắc mềm kích hoạt khi khối đứng và khi khối nằm | TV3 |
| T11 | Công tắc nặng: đứng thì kích hoạt, nằm thì không | TV3 |
| T12 | Kiểu `toggle`: bấm hai lần thì cầu trở về như cũ | TV3 |
| T13 | Kiểu `on` và `off`: bấm lại không đổi gì | TV3 |
| T14 | Một công tắc nối nhiều ô cầu với kiểu khác nhau | TV3 |
| T15 | Cầu đóng ngay dưới khối: bị loại | TV3 |
| T16 | Hai trạng thái cùng vị trí khối, khác trạng thái cầu: khác nhau khi so sánh và hash | TV3 |
| T17 | Chỉ tách khi khối nguyên đứng trên công tắc tách | TV4 |
| T18 | Sau khi tách: hai khối con ở đúng hai ô ghi trong file màn | TV4 |
| T19 | Khối con kích hoạt công tắc mềm, không kích hoạt công tắc nặng | TV4 |
| T20 | Khối con trên ô dễ vỡ không vỡ; trên ô đích không thắng | TV4 |
| T21 | Hai khối con kề cạnh: ghép đúng tư thế và ô neo, theo cả chiều ngang và chiều dọc | TV4 |
| T22 | Hai khối con kề chéo: không ghép | TV4 |
| T23 | Khối con này bấm công tắc đóng cầu dưới khối con kia: bị loại | TV4 |
| T24 | BFS trên 33 màn ra đúng cột "Bước tối ưu" ở [03-man-choi.md](03-man-choi.md#4-danh-sách-33-màn) | TV1, chạy sau khi ghép |
