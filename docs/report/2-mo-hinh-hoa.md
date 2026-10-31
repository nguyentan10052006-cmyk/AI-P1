## 2. Trò chơi và mô hình hóa bài toán

Chương này mô tả luật chơi mà nhóm cài đặt và cách đưa trò chơi về một bài toán tìm kiếm: trạng thái, hành động, hàm chuyển, kiểm tra đích, chi phí bước và cách tránh lặp trạng thái. Bốn thuật toán (chương 3), giao diện (chương 4) và script thực nghiệm (chương 5) dùng chung mô hình này, cài trong package `Source/bloxorz/`.

### 2.1. Luật chơi

Bloxorz [2] đặt một khối 1×1×2 trên một bàn ô vuông. Khối bắt đầu ở tư thế đứng tại ô xuất phát `S`. Mỗi lượt, người chơi lăn khối theo một trong bốn hướng: lên (U), xuống (D), trái (L), phải (R). Khối có ba tư thế: đứng (chiếm một ô), nằm ngang và nằm dọc (chiếm hai ô kề nhau). Khối thắng khi đứng thẳng trên ô đích `G`. Khối thua khi rơi, tức là khi có một phần khối nằm trên ô trống, trên cầu đang đóng hoặc ra ngoài bàn.

Mỗi loại ô xử lý khối theo một cách riêng (Bảng 2.1).

**Bảng 2.1.** Cách xử lý từng loại ô.

| Loại ô | Ký hiệu trong file màn | Khối đứng | Khối nằm | Khối con (sau khi tách) |
|---|---|---|---|---|
| Trống hoặc ngoài bàn | `.` | rơi | rơi, kể cả khi chỉ một nửa khối ở trên | rơi |
| Sàn | `#` | được | được | được |
| Xuất phát | `S` | như sàn | như sàn | như sàn |
| Đích | `G` | thắng | được, không thắng | được, không thắng |
| Ô dễ vỡ | `F` | ô vỡ, khối rơi | được | được, ô không vỡ |
| Cầu đang đóng | `b` | rơi | rơi | rơi |
| Cầu đang mở | `B` | được | được | được |
| Công tắc mềm | `o` | kích hoạt | kích hoạt | kích hoạt |
| Công tắc nặng | `x` | kích hoạt | không kích hoạt | không kích hoạt |
| Công tắc tách | `@` | tách khối | không có tác dụng | không có tác dụng |

Tọa độ ô viết theo (hàng, cột): hàng tăng xuống dưới, cột tăng sang phải. Dữ liệu 33 màn gốc lấy từ bản port Game Boy Advance của trò chơi gốc [3].

Ở những chỗ đề bài chưa nói rõ, nhóm theo luật của trò chơi gốc và bản port [3]:

- Khối con 1×1×1 không làm vỡ ô dễ vỡ, vì đề chỉ đặt luật này cho khối 1×1×2 đứng.
- Khối con chỉ kích hoạt được công tắc mềm; công tắc nặng và công tắc tách cần khối nguyên đứng trên.
- Công tắc kích hoạt mỗi lần khối lăn tới ô của nó. Khối không cần dừng lại trên công tắc.
- Hai khối con vừa tách ra không kích hoạt công tắc ở ô nơi chúng đáp xuống.
- Công tắc đóng một ô cầu đang nằm dưới khối thì khối rơi.

Các điểm 1, 2, 3 và 5 có test riêng trong `Source/tests/test_spec.py` và `Source/tests/test_rules.py`. Điểm 4 không có test riêng vì không ảnh hưởng tới màn gốc nào: trong 33 màn, khối con chỉ có thể đáp xuống công tắc tách hoặc công tắc nặng, là hai loại khối con vốn không kích hoạt được.

### 2.2. Cầu và công tắc

Cầu là ô có hai trạng thái. Khi mở, cầu đỡ khối như sàn. Khi đóng, cầu giống ô trống. Trong file màn, `B` là cầu mở lúc đầu và `b` là cầu đóng lúc đầu. Trạng thái của cầu thay đổi trong lúc chơi, nên nó là một phần của trạng thái tìm kiếm (mục 2.3).

Mỗi công tắc mềm hoặc nặng nối với một hoặc nhiều ô cầu, và tác động lên mỗi ô cầu theo một trong ba kiểu:

- `toggle`: đảo trạng thái cầu, mở thành đóng và đóng thành mở;
- `open`: luôn mở cầu;
- `close`: luôn đóng cầu.

Đề gọi hai kiểu sau là tác động cố định (permanent). Một công tắc có thể tác động lên các cầu khác nhau theo các kiểu khác nhau. File màn ghi trường hợp này bằng trường `links`, mỗi phần tử gồm một ô cầu và kiểu tác động lên ô đó. Ví dụ, ở màn 29, công tắc mềm tại (0, 2) mở hai cầu (0, 10), (0, 11) và cùng lúc đóng hai cầu (6, 10), (6, 11).

Công tắc tách có trường `targets` gồm hai ô. Khi khối nguyên đứng lên công tắc, khối tách thành hai khối con đặt tại hai ô đó (mục 2.6). Định dạng file màn cho phép công tắc tách nối thêm cầu; khi đó cầu đổi trạng thái trước, rồi khối mới tách. Không màn gốc nào dùng trường hợp này.

**Bảng 2.2.** Số công tắc trong 33 màn gốc, theo loại và kiểu tác động.

| Loại công tắc | `toggle` | `open` | `close` | Nhiều kiểu (`links`) | Tổng |
|---|---|---|---|---|---|
| Mềm | 10 | 5 | 32 | 5 | 52 |
| Nặng | 19 | 15 | 2 | 4 | 40 |
| Tách | | | | | 14 |
| **Tổng** | | | | | **106** |

Sáu màn 17, 23, 25, 29, 30, 31 có công tắc dùng `links`. Bộ nạp màn (`Source/bloxorz/level.py`) kiểm tra file trước khi chạy: mỗi công tắc phải có cấu hình, mỗi ô được nối phải là ô cầu, mỗi công tắc tách phải có đúng hai ô đáp không phải ô trống.

### 2.3. Trạng thái

Trạng thái là lớp `State` (`Source/bloxorz/state.py`) gồm bốn thành phần:

- `orient`: tư thế của khối, một trong bốn giá trị đứng, nằm ngang, nằm dọc, đã tách;
- `pos`: ô neo của khối. Khối đứng có ô neo là ô đang đứng. Khối nằm ngang có ô neo là ô bên trái, khối nằm dọc là ô bên trên. Khi đã tách, `pos` là ô của khối con thứ nhất;
- `pos2`: ô của khối con thứ hai, chỉ có khi đã tách. Hai ô luôn được sắp sao cho `pos < pos2`, nên một cặp ô chỉ có một cách biểu diễn;
- `open_bridges`: tập các ô cầu đang mở.

Thành phần `open_bridges` là bắt buộc. Cùng một vị trí khối nhưng cấu hình cầu khác nhau thì là hai trạng thái khác nhau, vì từ đó khối đi tiếp được theo những cách khác nhau. Nếu tập đã thăm chỉ xét vị trí và tư thế, thuật toán sẽ bỏ qua trạng thái "đã bấm công tắc, quay lại chỗ cũ" và có thể kết luận sai là không có lời giải. Test `test_bridge_state_is_part_of_visited` kiểm tra đúng trường hợp này: lời giải phải đi bấm công tắc rồi quay về qua ô cũ.

Trạng thái không lưu ba thông tin sau, vì chúng không cần thiết:

- *Ô dễ vỡ đã vỡ:* đứng lên ô dễ vỡ thì khối rơi ngay, nên không có trạng thái nào khối còn trên bàn mà ô dễ vỡ đã vỡ.
- *Công tắc đã bấm:* công tắc không có trạng thái riêng. Hệ quả của việc bấm nằm hết ở `open_bridges`.
- *Khối con đang được điều khiển:* hành động đã ghi rõ khối con nào đi (mục 2.4). Nếu lưu thêm thông tin này thì số trạng thái đã tách tăng gấp đôi, và phải có thêm hành động "đổi khối" không lăn. Nếu hành động đó có chi phí nhỏ hơn 1 thì vi phạm điều kiện mọi bước có chi phí ít nhất 1, và heuristic của A* không còn chấp nhận được. Nếu tính nó là một bước thì số bước không còn là số lần lăn như đề định nghĩa.

Không gian trạng thái thực tế nhỏ hơn nhiều so với số tổ hợp có thể có. Duyệt hết các trạng thái tới được từ trạng thái đầu (không đi tiếp từ trạng thái đích), 33 màn gốc có tổng cộng 70 062 trạng thái (Bảng 2.3).

**Bảng 2.3.** Số trạng thái tới được ở một số màn.

| Màn | Nhóm | Số ô cầu | Trạng thái tới được | Trong đó đã tách | Cấu hình cầu tới được |
|---|---|---|---|---|---|
| 1 | G1 | 0 | 89 | 0 | 1 |
| 2 | G3 | 4 | 380 | 0 | 4 |
| 8 | G5 | 0 | 710 | 573 | 1 |
| 20 | G5 | 6 | 10 856 | 9 814 | 8 |
| 23 | G5 | 8 | 22 847 | 21 712 | 16 |
| 29 | G3 | 17 | 1 817 | 0 | 21 |
| 32 | G3 | 8 | 840 | 0 | 8 |

Bảng 2.3 cho thấy hai điều. Thứ nhất, trạng thái đã tách chiếm phần lớn không gian ở các màn có công tắc tách: 95 % ở màn 23 và 90 % ở màn 20, vì hai khối con đặt ở hai ô bất kỳ tạo ra nhiều tổ hợp hơn một khối nguyên. Thứ hai, số cấu hình cầu thực tế rất nhỏ: màn 29 có 17 ô cầu, tức tối đa $2^{17} = 131\,072$ cấu hình, nhưng chỉ 21 cấu hình tới được, vì mỗi công tắc chỉ đổi một nhóm cầu cố định.

*Chạy lại trong `Source/`:* duyệt BFS từ `level.initial_state()` với `Problem.actions()` và `Problem.result()`, không mở rộng trạng thái đích, rồi đếm kích thước tập đã thăm. Công cụ `tools/check_heuristics.py` in cùng tổng 70 062.

### 2.4. Hành động

Khi khối nguyên, có bốn hành động U, D, L, R. Khi đã tách, có tám hành động theo thứ tự cố định U1, D1, L1, R1, U2, D2, L2, R2, trong đó chỉ số 1 và 2 là khối con ở `pos` và ở `pos2`. Trong code, hành động là `Action(dir, cube)` với `cube` bằng `None` khi khối nguyên, bằng 0 hoặc 1 khi đã tách.

Thứ tự này cố định và giống nhau ở cả bốn thuật toán, để kết quả tái lập được và so sánh được. Khi có nhiều lời giải cùng độ dài, thứ tự hành động quyết định lời giải nào được trả về.

Hàm `Problem.actions(state)` trả về mọi hành động, kể cả hành động làm khối rơi. Hàm `Problem.result(state, action)` trả về trạng thái kế tiếp, hoặc `None` nếu hành động làm khối rơi. Thuật toán bỏ qua kết quả `None` và không đếm nó vào số nút được sinh.

### 2.5. Hàm chuyển

Hàm chuyển của khối nguyên cho bởi Bảng 2.4: với mỗi tư thế và mỗi hướng lăn là tư thế mới và vị trí ô neo mới.

**Bảng 2.4.** Bảng chuyển của khối nguyên, với ô neo hiện tại là (r, c).

| Tư thế hiện tại | U | D | L | R |
|---|---|---|---|---|
| Đứng | nằm dọc tại (r − 2, c) | nằm dọc tại (r + 1, c) | nằm ngang tại (r, c − 2) | nằm ngang tại (r, c + 1) |
| Nằm ngang | nằm ngang tại (r − 1, c) | nằm ngang tại (r + 1, c) | đứng tại (r, c − 1) | đứng tại (r, c + 2) |
| Nằm dọc | đứng tại (r − 1, c) | đứng tại (r + 2, c) | nằm dọc tại (r, c − 1) | nằm dọc tại (r, c + 1) |

Bảng này là hằng `BLOCK_MOVES` trong `Source/bloxorz/rules.py`, và cả 12 trường hợp đều có test. Một bước được xử lý theo thứ tự sau (hàm `step()` và `_settle()`):

1. Tính vị trí mới. Khối nguyên đi theo Bảng 2.4; khối con đi một ô theo hướng đã chọn.
2. Kiểm tra rơi. Nếu một ô khối chiếm nằm ngoài bàn, là ô trống hoặc là cầu đang đóng thì khối rơi. Khối nguyên đứng trên ô dễ vỡ cũng rơi.
3. Nếu khối không rơi, kích hoạt công tắc ở các ô khối vừa tới: công tắc mềm kích hoạt ở mọi tư thế; công tắc nặng và công tắc tách chỉ kích hoạt khi khối nguyên đứng trên.
4. Kiểm tra rơi lần hai: nếu một ô khối đang chiếm là cầu vừa bị đóng ở bước 3 thì khối rơi.
5. Nếu đã tách và hai khối con kề cạnh nhau thì ghép lại (mục 2.6).
6. Nếu khối nguyên đứng trên ô đích thì thắng.

Ngoài trạng thái mới, `step()` trả về danh sách sự kiện theo thứ tự xảy ra (công tắc, ô vỡ, tách, ghép, rơi, thắng). Giao diện chỉ đọc các sự kiện này để vẽ hiệu ứng, không tự tính lại luật (chương 4). Hàm `Problem.result()` của bài toán tìm kiếm gọi đúng hàm `step()` này.

**Bảng 2.5.** Lời giải BFS của màn 1: `R D D R R D R`, 7 bước.

| Bước | Lệnh | Tư thế | Ô khối chiếm |
|---|---|---|---|
| 0 | | đứng | (3, 3) |
| 1 | R | nằm ngang | (3, 4), (3, 5) |
| 2 | D | nằm ngang | (4, 4), (4, 5) |
| 3 | D | nằm ngang | (5, 4), (5, 5) |
| 4 | R | đứng | (5, 6) |
| 5 | R | nằm ngang | (5, 7), (5, 8) |
| 6 | D | nằm ngang | (6, 7), (6, 8) |
| 7 | R | đứng trên đích | (6, 9) |

### 2.6. Tách và ghép khối

Chỉ khối nguyên đứng trên công tắc tách mới bị tách. Khi đó khối thành hai khối con 1×1×1, đặt tại hai ô ghi trong trường `targets` của công tắc. Các khối con vừa đáp xuống không kích hoạt công tắc ở ô đáp.

Sau khi tách, mỗi bước chỉ một khối con đi một ô. Khối con không làm vỡ ô dễ vỡ; đi vào ô đích cũng không thắng. Khi hai khối con kề cạnh nhau (chung một cạnh), chúng tự ghép thành khối nằm. Nếu cùng hàng thì thành khối nằm ngang với ô neo bên trái; nếu cùng cột thì thành khối nằm dọc với ô neo bên trên. Hai khối con kề chéo thì không ghép.

**Bảng 2.6.** Lời giải BFS của màn 8, có tách và ghép, 10 bước. Công tắc tách ở (4, 4), hai ô đáp là (1, 10) và (7, 10).

| Bước | Lệnh | Tư thế | Ô khối chiếm | Sự kiện |
|---|---|---|---|---|
| 0 | | đứng | (4, 1) | |
| 1 | R | nằm ngang | (4, 2), (4, 3) | |
| 2 | R | đã tách | (1, 10), (7, 10) | khối đứng lên công tắc tách tại (4, 4) và tách |
| 3–6 | D1 (bốn lần) | đã tách | khối con 1 đi từ (1, 10) xuống (5, 10); khối con 2 ở yên (7, 10) | |
| 7 | U2 | nằm dọc | (5, 10), (6, 10) | hai khối con kề cạnh, ghép thành khối nằm dọc |
| 8 | U | đứng | (4, 10) | |
| 9 | R | nằm ngang | (4, 11), (4, 12) | |
| 10 | R | đứng trên đích | (4, 13) | thắng |

"Khối con 1" là khối ở `pos`, tức ô nhỏ hơn theo thứ tự (hàng, cột); hàm `split_state()` luôn sắp xếp hai ô như vậy. Sau bước 6, khối con 1 ở (5, 10) đứng trước khối con 2 ở (7, 10), nên lệnh U2 đưa khối con ở (7, 10) lên (6, 10).

### 2.7. Kiểm tra đích

Trạng thái đích là trạng thái khối nguyên đứng có ô neo trùng ô đích (`Problem.is_goal()`). Khối nằm vắt qua ô đích không thắng. Khối con đi vào ô đích cũng không thắng: hai khối con phải ghép lại rồi khối nguyên đứng lên ô đích.

### 2.8. Chi phí bước

Chi phí của một bước do `Problem.step_cost(s, a, s')` trả về. Khi không truyền hàm chi phí, mỗi bước tốn 1. Giao diện và script thực nghiệm dùng hàm chi phí không đồng nhất trong `Source/bloxorz/costs.py` (Bảng 2.7), xây dựng từ công nâng trọng tâm khi lật khối và rủi ro khi đi lên ô dễ vỡ. Lý do của từng mức được trình bày ở mục 3.3.

**Bảng 2.7.** Chi phí một bước.

| Bước | Chi phí |
|---|---|
| Đứng → nằm | 1,12 |
| Nằm → đứng | 1,62 |
| Nằm → nằm (lăn quanh trục dài) | 1,21 |
| Khối con 1×1×1 lăn một ô | 1,10 |
| Thêm khi có phần khối nằm trên ô dễ vỡ | + 0,50 |

Mọi bước có chi phí ít nhất 1. Điều kiện này giữ cho heuristic của A*, vốn đếm cận dưới của số bước, vẫn chấp nhận được (mục 3.4). BFS và DFS không dùng chi phí khi chọn nút. Tuy vậy, tổng chi phí lời giải của cả bốn thuật toán đều tính theo cùng một hàm chi phí, để so sánh được chất lượng lời giải ở chương 5.

### 2.9. Tránh lặp trạng thái

Bốn thuật toán đều là tìm kiếm trên đồ thị (graph search): ghi nhớ các trạng thái đã gặp và không xét lại một trạng thái đã có.

- BFS và DFS giữ tập đã thăm `visited` và đánh dấu một trạng thái ngay khi đưa nó vào biên, nên mỗi trạng thái vào biên nhiều nhất một lần.
- UCS và A* giữ bảng `best_g`, chi phí nhỏ nhất đã biết để tới mỗi trạng thái. Một trạng thái chỉ được đưa lại vào biên khi tìm được đường rẻ hơn. Mục cũ còn trong hàng đợi ưu tiên bị bỏ qua lúc lấy ra (lazy deletion).

`State` là dataclass bất biến (`frozen=True`) và `open_bridges` có kiểu `frozenset`, nên trạng thái băm được (hashable) và dùng trực tiếp làm khóa của tập đã thăm, bảng cha và bảng `best_g`. Số trạng thái tới được của một màn là hữu hạn (Bảng 2.3), nên với cơ chế trên, cả bốn thuật toán đều dừng: hoặc tìm ra lời giải, hoặc duyệt hết rồi báo không có lời giải.

### 2.10. Tóm tắt mô hình

**Bảng 2.8.** Mô hình bài toán tìm kiếm và nơi cài đặt.

| Thành phần | Định nghĩa | Cài đặt trong `Source/` |
|---|---|---|
| Trạng thái | (tư thế, ô neo, ô khối con thứ hai, tập cầu đang mở) | `bloxorz/state.py`, lớp `State` |
| Trạng thái đầu | khối đứng tại `S`; cầu mở là các ô `B` | `Level.initial_state()` |
| Hành động | U, D, L, R; khi đã tách U1 … R1, U2 … R2 | `Problem.actions()` |
| Hàm chuyển | Bảng 2.4 và thứ tự xử lý ở mục 2.5; `None` khi khối rơi | `rules.step()`, `Problem.result()` |
| Kiểm tra đích | khối nguyên đứng trên ô đích | `Problem.is_goal()` |
| Chi phí bước | Bảng 2.7, mọi bước ≥ 1 | `Problem.step_cost()`, `bloxorz/costs.py` |
| Heuristic | $h_M$ và $h_P$ (mục 3.4) | `solvers/heuristics.py` |
| Tránh lặp | tập đã thăm (BFS, DFS); bảng `best_g` (UCS, A*) | `solvers/*.py` |
