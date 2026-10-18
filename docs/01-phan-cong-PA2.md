# Phân công PA2 và mô tả công việc

Tài liệu chung của nhóm, viết sau buổi họp 18/10. Muốn đổi điều gì ở đây thì báo nhóm chat trước, ghi vào tab **BienBan** của Google Sheet rồi mới sửa file.

## 1. Những gì đã chốt

| Vấn đề | Quyết định |
|---|---|
| Cách chia việc | **PA2**: mỗi người một thuật toán (BFS, DFS, UCS, A*), một người làm GUI. Phần chung (luật chơi, màn chơi, thực nghiệm) được chia thành nhóm việc, mỗi nhóm có một người chủ (mục 3) |
| Theo dõi tiến độ | **Google Sheets**. Cách dựng ở [05-theo-doi-tien-do.md](05-theo-doi-tien-do.md) |
| Màn chơi | **33 màn của game gốc**, dùng cả 33 màn làm bộ thực nghiệm. Xem [03-man-choi.md](03-man-choi.md) |
| Luật chơi | Theo đề và luật của game gốc. Các chỗ đề chưa rõ đã chốt ở [02-luat-choi.md](02-luat-choi.md) |
| Chỉ số thực nghiệm | Số bước, tổng chi phí, số nút mở rộng, số nút sinh ra, frontier lớn nhất, số trạng thái đã thăm, bộ nhớ đỉnh, thời gian tìm kiếm, tổng thời gian. Định nghĩa ở [04-thuc-nghiem.md](04-thuc-nghiem.md) |
| Mốc | M1 thứ Tư 21/10 · M2 Chủ nhật 25/10 (đóng băng tính năng) · M3 thứ Tư 28/10 · nộp thứ Sáu 30/10 (hạn chót 31/10) |

**Còn phải điền:** tên người cho từng vai trò (mục 2), công nghệ GUI 3D, ngôn ngữ và công cụ viết báo cáo, cách dùng Git, người điều phối.

## 2. Ai làm gì

| Vai trò | Họ tên | Thuật toán | Phần chung phụ trách | Chương báo cáo | Đọc chéo cho |
|---|---|---|---|---|---|
| **TV1** | ________ | BFS | NV1 Engine lõi, bộ nạp màn, ghép module | 2. Mô hình hóa · 3.1 BFS | TV2 |
| **TV2** | ________ | DFS (hoặc IDS) | NV4 Màn chơi gốc · NV10 Thực nghiệm | 3.2 DFS · 5. Thực nghiệm | TV5 |
| **TV3** | ________ | UCS | NV2 Ô đặc biệt · hàm chi phí · kiểm thử cài đặt, đóng gói | 3.3 UCS | TV1 |
| **TV4** | ________ | A* | NV3 Tách và ghép khối · heuristic · ghép báo cáo | 3.4 A* · 1. Phân công · 6. Kết luận | TV3 |
| **TV5** | ________ | (không) | NV9 GUI 3D, README · NV12 Video | 4. Cài đặt và giao diện | TV4 |

**Đọc chéo cho** là người mà mình đọc code và chương báo cáo. Vòng đọc chéo: TV1 → TV2 → TV5 → TV4 → TV3 → TV1. Ai cũng đọc phần của một người khác và được một người khác đọc phần của mình.

**Vì sao chia như vậy.** Điểm yếu của PA2 là phần luật chơi làm chung dễ thành nút thắt, bốn người cùng chờ. Để tránh điều đó:

- Engine được chia thành ba khối có chủ riêng: lõi (TV1), ô đặc biệt (TV3), tách khối (TV4). Hợp đồng chung (mục 4) được chốt ngay ngày đầu, nên ai cũng code được mà không chờ người khác.
- Mỗi khối giao cho người cần nó nhất. Hàm chi phí của UCS phụ thuộc loại ô, nên TV3 làm ô đặc biệt. Heuristic của A* phải xử lý trạng thái đã tách, nên TV4 làm tách khối. BFS là thuật toán nhanh xong nhất và cũng là "đáp án" để kiểm tra engine, nên TV1 làm lõi. Thực nghiệm cần bộ màn, nên TV2 làm cả hai.
- Ai cũng có một thuật toán (hoặc GUI), một phần chung, một chương báo cáo và đọc phần của một người khác, đủ để trả lời vấn đáp về cả dự án.

## 3. Các nhóm việc (NV)

Mỗi nhóm việc ghi: người chủ, người đọc chéo, cỡ (S nhỏ, M vừa, L lớn), hạn và mã việc tương ứng trong tab **Viec** của Google Sheet. Phần "Cách làm" là các bước nên đi theo thứ tự.

### NV1 · Engine lõi và hợp đồng chung

**Chủ:** TV1 · **Đọc chéo:** TV3 · **Cỡ:** L · **Hạn:** khung code 19/10, lõi 20/10, ghép đủ 24/10 · **Việc:** V01–V04

**Mục tiêu.** Viết phần code luật chơi dùng chung. GUI và cả 4 thuật toán gọi cùng một hàm `result()`; không ai viết lại luật ở chỗ khác.

**Cách làm**
1. Sáng 19/10: tạo khung code theo hợp đồng ở mục 4. Các hàm có đủ chữ ký, thân hàm để `raise NotImplementedError`. Khung có thêm một bài toán mê cung nhỏ (`GridMaze`) cùng giao diện `Problem`, để bốn người thử thuật toán ngay. Đẩy lên nhánh chính rồi báo nhóm.
2. Viết test cho 12 trường hợp của bảng chuyển ([02-luat-choi.md §3](02-luat-choi.md#3-bảng-chuyển-hướng-và-vị-trí)) trước, rồi mới cài. Cài bảng chuyển dưới dạng bảng tra (`dict`), không viết if-else rải rác.
3. Kiểm tra hợp lệ phần lõi: ô khối chiếm nằm ngoài bàn hoặc là ô trống thì hành động bị loại.
4. `is_goal(s)`: khối nguyên, đang đứng, trên ô đích.
5. Viết `result(s, a)` theo đúng thứ tự xử lý một lượt ở [02 §4](02-luat-choi.md#4-một-lượt-đi-được-xử-lý-theo-thứ-tự). Chừa sẵn chỗ gọi `apply_switches`, `apply_split`, `try_merge`; lúc đầu các hàm này không làm gì, TV3 và TV4 sẽ cài sau.
6. Bộ nạp màn (V03): đọc file màn theo định dạng ở [03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm) thành đối tượng `Level` (lưới, ô xuất phát, công tắc, cầu, công tắc tách). Báo lỗi rõ ràng nếu file sai.
7. Từ 22/10 đến 24/10: ghép module của TV3 và TV4, chạy lại toàn bộ test. Sau đó chạy BFS trên 33 màn; màn nào lệch cột "Bước tối ưu" ở [03 §4](03-man-choi.md#4-danh-sách-33-màn) thì báo chủ module liên quan.

**Đầu ra:** thư mục `Source/engine/`, test T01–T06, `GridMaze`.

**Xong khi**
- [ ] Test T01–T06 qua.
- [ ] BFS giải màn 1, 3, 6 đúng 7, 19, 35 bước.
- [ ] TV5 lăn được khối trên GUI bằng engine thật.
- [ ] Sau khi ghép, toàn bộ test T01–T24 qua trên nhánh chính.

**Lỗi hay gặp:** nhầm (x, y) với (hàng, cột); dùng `list` làm trạng thái nên không hash được (phải dùng `tuple`); quên đưa trạng thái cầu vào `State`, khiến hai trạng thái chỉ khác nhau ở cầu bị coi là một.

### NV2 · Ô đặc biệt: ô dễ vỡ, công tắc, cầu

**Chủ:** TV3 · **Đọc chéo:** TV4 · **Cỡ:** L · **Hạn:** 23/10 · **Việc:** V05

**Mục tiêu.** Cài đủ luật mục 2.5 của đề cho ô dễ vỡ, cầu, công tắc mềm và công tắc nặng, với ba kiểu tác động lên cầu: đảo, chỉ mở, chỉ đóng.

**Cách làm**
1. Viết test T07–T16 ([02 §7](02-luat-choi.md#7-bộ-kiểm-thử-luật)) trước, dựng trạng thái bằng tay, không cần chờ engine lõi xong.
2. Ô dễ vỡ: khối nguyên đứng trên ô dễ vỡ thì hành động bị loại (khối rơi). Khối nằm và khối con thì an toàn.
3. Trạng thái cầu: khi nạp màn, đánh số các ô cầu từ 0 đến n−1. Trạng thái cầu là một số nguyên (bitmask), bit i bằng 1 nghĩa là ô cầu i đang mở. Đưa số này vào `State`.
4. Cầu đóng xử lý như ô trống, cầu mở như sàn.
5. Kích hoạt công tắc sau khi khối tới nơi. Công tắc mềm kích hoạt khi bất kỳ phần nào của khối nằm trên nó (kể cả khối con). Công tắc nặng chỉ kích hoạt khi khối nguyên đứng trên nó. Một công tắc có thể nối nhiều ô cầu, mỗi liên kết có kiểu riêng: `toggle` (đảo), `on` (chỉ mở), `off` (chỉ đóng).
6. Sau khi đổi cầu: nếu có phần khối đang nằm trên ô cầu vừa đóng thì hành động bị loại.
7. Đưa cho TV1 ghép, rồi kiểm tra bằng BFS: màn 2, 5, 7, 11 phải ra 17, 33, 44, 47 bước; màn 4, 13 (ô dễ vỡ) phải ra 28, 46 bước.

**Đầu ra:** `Source/engine/tiles.py` và test T07–T16.

**Xong khi**
- [ ] Test T07–T16 qua.
- [ ] Sáu màn ở bước 7 đúng số bước tham khảo.

**Lỗi hay gặp:** lưu "công tắc đã bấm" vào trạng thái (không cần, chỉ cầu có trạng thái); quên trường hợp khối nằm đè hai công tắc cùng lúc; với kiểu "chỉ mở", bấm lại khi cầu đã mở thì không đổi gì.

### NV3 · Tách và ghép khối

**Chủ:** TV4 · **Đọc chéo:** TV5 · **Cỡ:** L · **Hạn:** 23/10 · **Việc:** V06

**Mục tiêu.** Cài công tắc tách: khối tách thành hai khối con 1×1×1, điều khiển từng khối, tự ghép lại khi hai khối kề nhau.

**Cách làm**
1. Viết test T17–T23 trước.
2. Trạng thái đã tách gồm hai ô của hai khối con, lưu thành cặp đã sắp xếp `(a, b)` với `a < b`. Hai khối con giống hệt nhau, nên sắp xếp giúp gộp trạng thái trùng và giảm khoảng một nửa số trạng thái.
3. Hành động khi đã tách: 8 hành động, gồm khối con 1 hoặc 2 nhân với 4 hướng (`U1` … `R2`). `U1` là khối ở ô `a` đi lên. Việc đổi khối đang điều khiển (phím Space trong GUI) không phải hành động tìm kiếm và không tính bước.
4. Khối nguyên đứng trên công tắc tách thì hai khối con xuất hiện tại hai ô ghi trong file màn. Ô đáp không kích hoạt gì.
5. Khối con lăn 1 ô. Ô mới phải nằm trong bàn, không trống, không phải cầu đóng. Khối con không làm vỡ ô dễ vỡ, không thắng ở ô đích, kích hoạt được công tắc mềm, không kích hoạt công tắc nặng hay công tắc tách.
6. Sau mỗi bước của khối con: nếu hai khối con kề cạnh (chung cạnh, kề chéo không tính) thì ghép thành khối nằm. Cùng hàng thì nằm ngang, neo ở ô bên trái; cùng cột thì nằm dọc, neo ở ô bên trên.
7. Khi cầu đóng, kiểm tra cả hai khối con, vì khối kia có thể đang đứng trên cầu.
8. Đưa cho TV1 ghép, rồi kiểm tra bằng BFS: màn 8, 9, 16 phải ra 10, 24, 28 bước.

**Đầu ra:** `Source/engine/split.py` và test T17–T23.

**Xong khi**
- [ ] Test T17–T23 qua.
- [ ] Màn 8, 9, 16 đúng số bước tham khảo.
- [ ] TV5 điều khiển được hai khối con trên GUI.

### NV4 · Màn chơi gốc (33 màn)

**Chủ:** TV2 · **Đọc chéo:** TV1 · **Cỡ:** M · **Hạn:** 20/10 · **Việc:** V07

**Mục tiêu.** Có 33 file màn đúng với game gốc, cùng một định dạng mà engine, GUI và script thực nghiệm đều đọc được.

**Cách làm**
1. Tải `game/levels.json` từ repo [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba) (commit `f57ebb6`, giấy phép GPL-3.0). Ghi nguồn vào tab NguonTrichDan ngay.
2. Cùng TV1 chốt định dạng file màn ([03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm)) trong ngày 19/10.
3. Viết script chuyển đổi theo bảng ánh xạ ở 03 §6. Bản GBA dùng (x, y) = (cột, hàng), khóa công tắc bằng x × 10 + y, và passcode bị mất số 0 ở đầu.
4. Sửa màn 3: thêm 4 ô sàn tại (6, 11), (7, 12), (7, 13), (7, 14) ([03 §3](03-man-choi.md#3-kết-quả-đối-chiếu)).
5. Kiểm tra tự động: mỗi màn có đúng 1 ô xuất phát và 1 ô đích; số ô từng loại khớp bảng ở 03 §4.
6. Đẩy 33 file vào `Source/levels/` và báo TV1, TV5.
7. Khi BFS chạy được: so số bước với cột "Bước tối ưu" ở 03 §4. Màn nào lệch thì kiểm tra file màn trước, rồi mới nghi engine.

**Xong khi**
- [ ] Có 33 file màn, mỗi file có trường `source`.
- [ ] Kiểm tra số ô qua.
- [ ] Tab ManChoi đã đánh dấu "Đã chuyển đổi" và "Đã kiểm tra số ô".

### NV5 · BFS

**Chủ:** TV1 · **Đọc chéo:** TV3 · **Cỡ:** S · **Hạn:** 21/10 (màn cơ bản), 25/10 (33 màn) · **Việc:** V08, V09

**Cách làm**
1. Dùng hàng đợi FIFO `collections.deque`, tập đã thăm `set` và bảng cha `dict` (trạng thái → (trạng thái cha, hành động)) để dựng lại đường đi.
2. Kiểm tra đích ngay khi sinh nút (early goal test). Cách này vẫn cho số bước tối ưu và mở rộng ít nút hơn. Ghi rõ lựa chọn này trong báo cáo.
3. Đánh dấu đã thăm khi đưa vào hàng đợi, không phải khi lấy ra, để không đưa một trạng thái vào hai lần.
4. Đếm chỉ số đúng quy ước ở [04 §3](04-thuc-nghiem.md#3-quy-ước-đếm-bắt-buộc-giống-nhau-ở-4-thuật-toán).
5. Ngày 19–20/10 chạy trên `GridMaze`; từ 21/10 chạy trên engine thật.

**Xong khi**
- [ ] 33/33 màn khớp cột "Bước tối ưu".
- [ ] Mọi lời giải phát lại trên engine đều tới đích.
- [ ] Trả về `SearchResult` đủ trường.

### NV6 · DFS hoặc IDS

**Chủ:** TV2 · **Đọc chéo:** TV1 · **Cỡ:** S · **Hạn:** 21/10, 25/10 · **Việc:** V10, V11

**Cách làm**
1. Chọn DFS dạng tìm kiếm đồ thị (graph search, có tập đã thăm) hoặc IDS. Đề cho phép IDS nhưng phải ghi rõ trong báo cáo. DFS có tập đã thăm là đủ yêu cầu "xử lý trạng thái lặp" và đơn giản hơn.
2. Dùng ngăn xếp tường minh (`list`), không dùng đệ quy, vì Python chỉ cho đệ quy khoảng 1000 tầng.
3. Cố định thứ tự hành động: U, D, L, R; khi đã tách: U1, D1, L1, R1, U2, D2, L2, R2. Kết quả DFS phụ thuộc thứ tự này, nên phải ghi vào báo cáo.
4. Chọn một thời điểm đánh dấu đã thăm (khi đưa vào hoặc khi lấy ra), ghi rõ lựa chọn, và đếm chỉ số theo [04 §3](04-thuc-nghiem.md#3-quy-ước-đếm-bắt-buộc-giống-nhau-ở-4-thuật-toán).
5. Nếu chọn IDS: tăng giới hạn độ sâu từng bậc 1, mỗi vòng chỉ chặn trạng thái lặp trên đường đi hiện tại, và đặt timeout. Màn dài (trên 60 bước) có thể timeout; đó cũng là một kết quả để nhận xét.

**Xong khi**
- [ ] 33 màn giải được, hoặc ghi rõ màn nào timeout.
- [ ] Lời giải phát lại tới đích.
- [ ] Số bước không nhỏ hơn BFS. Nếu nhỏ hơn BFS là có lỗi.

### NV7 · UCS và hàm chi phí

**Chủ:** TV3 · **Đọc chéo:** TV4 · **Cỡ:** M · **Hạn:** mê cung 21/10, hàm chi phí 22/10, 33 màn 25/10 · **Việc:** V12–V14

**Cách làm**
1. Dùng hàng đợi ưu tiên `heapq` với mục `(g, thứ_tự, trạng_thái)`. `thứ_tự` là bộ đếm tăng dần, để Python không phải so sánh hai trạng thái khi `g` bằng nhau.
2. Giữ bảng `best_g`. Khi lấy ra một mục có `g` lớn hơn `best_g` của trạng thái đó thì bỏ qua (lazy deletion).
3. Kiểm tra đích khi **lấy ra** khỏi hàng đợi. Điều này bắt buộc để UCS cho lời giải tối ưu.
4. Thiết kế hàm chi phí không đồng nhất (đề mục 3.4), ví dụ: lăn thường tốn 1, lăn lên ô dễ vỡ tốn thêm vì rủi ro. Quy tắc bắt buộc: **mọi bước có chi phí ≥ 1**, để heuristic của TV4 vẫn chấp nhận được. Thầy cho phép dùng ML đơn giản để học trọng số nếu giải thích rõ trong báo cáo.
5. Chốt hàm chi phí trước 22/10 và gửi TV4, vì A* phải dùng cùng một hàm chi phí. Cài vào `Problem.step_cost`.
6. Kiểm tra cài đặt: đặt mọi chi phí bằng 1 thì số bước của UCS phải bằng BFS ở mọi màn.

**Xong khi**
- [ ] UCS giải 33 màn.
- [ ] Có bảng chi phí và lý do cho từng mức.
- [ ] Tổng chi phí của UCS bằng A* ở mọi màn.

### NV8 · A* và heuristic

**Chủ:** TV4 · **Đọc chéo:** TV5 · **Cỡ:** M · **Hạn:** mê cung 21/10, heuristic 24/10, 33 màn 25/10 · **Việc:** V15–V17

**Cách làm**
1. Cài giống UCS nhưng ưu tiên theo f = g + h. Khi f bằng nhau, ưu tiên h nhỏ hơn; ghi rõ cách phá hòa này trong báo cáo.
2. Thiết kế heuristic theo hàm chi phí của TV3. Vì mọi bước tốn ít nhất 1, một cận dưới của **số bước** còn lại cũng là cận dưới của chi phí. Các ý tưởng từ đề (mục 3.5):
   - Khoảng cách Manhattan từ ô gần đích nhất của khối tới đích là d. Mỗi lần lăn, ô gần nhất tiến lại gần đích tối đa 2 ô, nên ⌈d/2⌉ là cận dưới.
   - Thay Manhattan bằng khoảng cách đường đi trên lưới "điểm": bỏ qua hướng, coi mọi ô không trống (kể cả cầu) là đi được. Tính trước một lần bằng BFS ngược từ ô đích, trong `prepare()`.
   - Phạt hướng phải chứng minh lại. Ví dụ ⌈d/2⌉ + 1 khi khối đang nằm là **không** chấp nhận được: khối nằm sát đích chỉ cần 1 bước để đứng lên đích. Có thể dùng max(⌈d/2⌉, 1) khi khối chưa đứng trên đích.
3. Trạng thái đã tách cần cận dưới riêng (ví dụ dựa trên khối con gần đích hơn), và phải chứng minh vẫn không ước lượng quá.
4. Kiểm tra trên 33 màn: tổng chi phí của A* phải bằng UCS, và số nút mở rộng của A* không lớn hơn UCS. Nếu lệch thì heuristic không chấp nhận được hoặc cài sai.
5. Viết chứng minh heuristic chấp nhận được (h(s) không lớn hơn chi phí thật còn lại) và nhất quán (h(s) ≤ c(s, a, s') + h(s')), theo đúng hàm chi phí đã chốt.

**Xong khi**
- [ ] 33/33 màn cùng tổng chi phí với UCS.
- [ ] Chứng minh nằm trong chương 3.4.
- [ ] (Tùy chọn) so sánh hai heuristic trong phần thực nghiệm.

### NV9 · GUI 3D

**Chủ:** TV5 · **Đọc chéo:** TV2 · **Cỡ:** L · **Hạn:** chơi tay 21/10, đủ tính năng 25/10 · **Việc:** V18–V22

**Cách làm**
1. Chọn công nghệ trước 20/10 và ghi vào biên bản: Ursina (Python) hoặc web Three.js gọi server Python. Thầy cho phép GUI viết bằng ngôn ngữ khác; chỉ thuật toán bắt buộc dùng Python.
2. Vẽ bàn 3D từ file màn. Mỗi loại ô một màu hoặc hình dễ phân biệt: sàn, trống, đích (lỗ), ô dễ vỡ (cam), công tắc mềm (tròn), công tắc nặng (hình X), công tắc tách (hình "( )"), cầu mở, cầu đóng.
3. Chơi tay: phím mũi tên gọi `result()` của engine; phím Space đổi khối con đang điều khiển; rơi thì thua, đứng trên đích thì thắng. **Không viết lại luật trong GUI.**
4. Các nút: New Game (chọn màn 1–33), Restart, Solve BFS, Solve DFS, Solve UCS, Solve A*. Bấm Solve thì gọi solver, khối tự lăn theo lời giải (hoạt ảnh từng bước), và hiện số bước, số nút mở rộng, thời gian.
5. Trước khi có solver thật: nút Solve phát lại lời giải có sẵn của màn 1 là `R D D R R D R`.
6. Hiện số màn, passcode và số bước đã đi.

**Xong khi**
- [ ] Hiện đủ 9 loại ô.
- [ ] Chơi tay có thắng, có thua.
- [ ] Tách và ghép khối hoạt động.
- [ ] 4 nút Solve chạy được trên mọi màn.
- [ ] Người khác cài theo README trên máy của họ và chạy được.

### NV10 · Thực nghiệm

**Chủ:** TV2 · **Đọc chéo:** TV1 · **Cỡ:** M · **Hạn:** script 24/10, chạy thử 25/10, chính thức 27/10 · **Việc:** V23–V25

**Cách làm**
1. Viết script đo theo [04-thuc-nghiem.md](04-thuc-nghiem.md). Mỗi cặp (màn, thuật toán) chạy trong một tiến trình riêng, có timeout. Đo thời gian 5 lần lấy trung vị; đo bộ nhớ 1 lần riêng bằng `tracemalloc`. Ghi ra CSV.
2. Trước khi có solver thật, thử script với solver giả (trả kết quả cố định) để kiểm tra đủ cột CSV.
3. Ngày 25/10 (M2): chạy thử đủ 4 × 33 và làm các kiểm tra chéo ở [04 §6](04-thuc-nghiem.md#6-kiểm-tra-chéo-trước-khi-dùng-số-liệu).
4. Ngày 26–27/10: chạy chính thức trên một máy, ghi cấu hình máy, vẽ biểu đồ, điền bảng. Gửi số liệu cho cả nhóm để sáng 28/10 mọi người viết nhận xét.
5. Nhập `summary.csv` vào tab ThucNghiem.

**Xong khi**
- [ ] CSV có đủ 4 × 33 dòng.
- [ ] Các kiểm tra chéo đều qua.
- [ ] Có bảng T1–T4 và hình H1–H6.
- [ ] Chương Thực nghiệm có số liệu.

### NV11 · Báo cáo

**Chủ:** từng người viết chương của mình (mục 2); TV4 ghép · **Hạn:** chương của từng người 27/10; chương Thực nghiệm và các đoạn nhận xét 28/10; bản ghép 28/10; PDF 30/10 · **Việc:** V26–V35

**Cách làm**
1. Xong code phần nào thì viết nháp chương đó ngay, không đợi tuần cuối. Khung báo cáo, quy ước viết, trích dẫn và phụ lục AI ở [06-bao-cao-video.md](06-bao-cao-video.md).
2. Mỗi người viết thêm một đoạn nhận xét kết quả thuật toán của mình trong mục 5.4 (V31–V34).
3. TV4 ghép bản đầy đủ ngày 28/10, cả nhóm rà soát ngày 29/10, xuất PDF ngày 30/10.

### NV12 · Video demo

**Chủ:** TV5, cả nhóm hỗ trợ · **Hạn:** 29/10 · **Việc:** V36

Làm theo kịch bản ở [06 §5](06-bao-cao-video.md#5-video-10-điểm). Quay ngày 28–29/10, có phụ đề hoặc thuyết minh, đăng YouTube ở chế độ công khai, dán link vào báo cáo.

### NV13 · Tích hợp, kiểm thử cài đặt, đóng gói

**Chủ:** TV1 (tích hợp), TV3 (kiểm thử cài đặt, đóng gói) · **Việc:** V04, V37, V38

- Mỗi mốc: mọi người gộp code vào nhánh chính trước 18h. TV1 chạy toàn bộ test. Họp 15 phút, mỗi người demo phần mình **trên nhánh chính**, không demo bản trên máy riêng.
- Ngày 29/10: TV3 cài theo README trên một máy không phải của TV5 và chạy được GUI cùng 4 nút Solve.
- Ngày 30/10: TV3 đóng gói `MSSV1_MSSV2_….zip` đúng cấu trúc ở mục 4 của đề.

### NV14 · Điều phối

**Người điều phối:** ________ (nên là người tạo Google Sheet)

- Dựng Google Sheet theo [05-theo-doi-tien-do.md](05-theo-doi-tien-do.md), mời cả nhóm, ghim link trong nhóm chat.
- Mỗi tối nhắc check-in. Ai trễ quá 1 ngày thì hỏi thăm và báo nhóm.
- Ghi mọi quyết định vào tab BienBan.

## 4. Hợp đồng chung

TV1 tạo khung code này ngày 19/10. Ai muốn đổi chữ ký hàm thì báo nhóm và ghi BienBan trước.

```python
# Source/engine/state.py  (TV1)
# Trạng thái là tuple bất biến, hash được, dùng làm khóa của dict và set.
#   kind    : 'S' đứng | 'H' nằm ngang | 'V' nằm dọc | 'X' đã tách
#   a       : (hàng, cột). Ô của khối đứng; ô trái (H); ô trên (V); khối con thứ nhất (X)
#   b       : None, hoặc khối con thứ hai khi kind == 'X' (luôn có a < b)
#   bridges : int (bitmask), bit i = 1 nghĩa là ô cầu thứ i đang mở
State = tuple  # (kind, a, b, bridges)

Action = str   # 'U' 'D' 'L' 'R'; khi đã tách: 'U1' ... 'R2' (khối con ở ô a là 1, ô b là 2)

# Source/engine/problem.py  (TV1)
class Problem:
    def __init__(self, level): ...
    def initial_state(self) -> State: ...
    def actions(self, s: State) -> list[Action]: ...     # chỉ hành động hợp lệ (không rơi), thứ tự cố định
    def result(self, s: State, a: Action) -> State: ...
    def is_goal(self, s: State) -> bool: ...             # khối nguyên đứng trên ô đích
    def step_cost(self, s: State, a: Action, s2: State) -> float: ...  # TV3 cài; mặc định 1

# Source/solvers/base.py  (TV1)
@dataclass
class SearchResult:
    status: str          # 'solved' | 'no_solution' | 'timeout'
    path: list[Action]   # dãy hành động từ trạng thái đầu tới đích
    path_cost: float
    expanded: int
    generated: int
    max_frontier: int
    visited: int

class Solver:
    name = "BASE"
    def prepare(self, problem: Problem) -> None: ...     # tiền xử lý (ví dụ bảng heuristic của A*); mặc định không làm gì
    def search(self, problem: Problem) -> SearchResult: ...
```

Ba quy ước đi kèm:
- Tọa độ luôn là **(hàng, cột)**; hàng tăng xuống dưới, cột tăng sang phải.
- Không hàm nào được sửa trạng thái truyền vào; luôn trả về trạng thái mới.
- Thời gian và bộ nhớ do script thực nghiệm đo bên ngoài. Solver chỉ tự đếm `expanded`, `generated`, `max_frontier`, `visited`.

Cấu trúc thư mục đề xuất (theo mẫu nộp bài ở mục 4 của đề):

```
Source/
├── main.py                 # TV5: mở GUI
├── README.md               # TV5: cài đặt và chạy
├── requirements.txt
├── levels/01.json … 33.json            # TV2
├── engine/                 # TV1: state.py, rules.py, level.py, problem.py
│                           # TV3: tiles.py · TV4: split.py
├── solvers/                # base.py (TV1), bfs.py (TV1), dfs.py (TV2),
│                           # ucs.py + costs.py (TV3), astar.py + heuristics.py (TV4)
├── experiments/            # TV2: run.py, charts.py, kết quả CSV
├── gui/                    # TV5
└── tests/                  # mỗi người viết test cho phần mình
```

## 5. Ai phải có gì ở mỗi mốc

| Mốc | TV1 (BFS) | TV2 (DFS) | TV3 (UCS) | TV4 (A*) | TV5 (GUI) |
|---|---|---|---|---|---|
| **M1 · T4 21/10**<br>một màn chạy trọn vòng | Engine lõi và test; bộ nạp màn; BFS giải màn 1, 3, 6 | 33 file màn; DFS giải màn 1, 3, 6 | UCS đúng trên mê cung; đang làm ô đặc biệt | A* đúng trên mê cung; đang làm tách khối | Bàn 3D vẽ từ file; chơi tay màn 1 bằng engine thật |
| **M2 · CN 25/10**<br>đủ tính năng, đóng băng | Ghép xong, toàn bộ test qua; BFS 33/33 khớp bảng | DFS 33 màn; script đo chạy thử 4 × 33 | Ô đặc biệt xong; hàm chi phí đã chốt; UCS 33 màn | Tách khối xong; heuristic; A* 33 màn, cùng chi phí với UCS | Đủ loại ô; tách khối; 4 nút Solve; khối tự lăn |
| **M3 · T4 28/10**<br>đủ số liệu, đủ chương | Chương Mô hình hóa và BFS | Số liệu chính thức và biểu đồ; chương DFS và Thực nghiệm | Chương UCS và hàm chi phí | Chương A* và chứng minh; bắt đầu ghép | README; chương Giao diện; kịch bản video |
| **Nộp · T6 30/10** | Rà soát | Rà soát | Kiểm thử cài đặt (29/10); đóng gói | Báo cáo PDF hoàn chỉnh | Video YouTube công khai |

Từ M2 trở đi chỉ sửa lỗi, không thêm tính năng.

## 6. Ai cần gì từ ai, làm gì trong lúc chờ

| Người | Cần gì | Từ ai | Hạn cần | Trong lúc chờ |
|---|---|---|---|---|
| TV2, TV3, TV4, TV5 | Khung hợp đồng chung và `GridMaze` | TV1 | tối 19/10 | Đọc tài liệu luật và màn; viết test |
| TV1 | Định dạng file màn và 3 màn đầu (1, 3, 6) | TV2 | 20/10 | Gõ tay màn 1 ngay trong test |
| TV3, TV4 | Engine lõi | TV1 | 20/10 | Viết test cho luật của mình, dựng trạng thái bằng tay |
| TV4 | Hàm chi phí | TV3 | 22/10 | Tạm dùng chi phí 1 cho mọi bước |
| TV5 | Engine lõi; BFS | TV1 | 20/10; 21/10 | Vẽ bàn từ file; Solve phát lại `R D D R R D R` |
| TV2 (thực nghiệm) | 4 solver trả về `SearchResult` | TV1, TV2, TV3, TV4 | 24/10 | Chạy script với solver giả |
| TV4 (ghép báo cáo) | Nháp chương của mọi người | Cả nhóm | 27/10 | Dựng khung báo cáo, danh mục tài liệu tham khảo |

## 7. Quy tắc phối hợp

- Mỗi việc có đúng một người chủ. Muốn sửa module của người khác thì nhắn người chủ.
- Đổi hợp đồng chung hoặc định dạng file màn: báo nhóm chat trước, ghi BienBan.
- Check-in mỗi tối trong tab CheckIn: xong gì, mai làm gì, vướng gì.
- Vướng quá 2 giờ thì hỏi ngay; trễ quá 1 ngày thì báo ngay, không đợi đến mốc.
- Đọc chéo trong vòng 24 giờ sau khi người kia gộp code; ghi nhận xét vào pull request hoặc nhóm chat.
- Ghi nguồn (tab NguonTrichDan) và prompt AI (tab PromptAI) ngay khi dùng, không để đến cuối.
- Ngày 28/10 có buổi "dạy chéo" 30 phút: mỗi người giảng 5 phút phần mình. Đây là cách chuẩn bị cho vấn đáp, vì thầy hỏi ngẫu nhiên bất kỳ ai về bất kỳ phần nào.

**Một việc được tính là xong khi:** code đã ở nhánh chính; test của phần đó qua; người đọc chéo đã xem; tab Viec đã cập nhật.

## 8. Cách tính % hoàn thành

Điểm cá nhân = điểm nhóm × % hoàn thành (đề mục 3.6), nên % phải dựa trên bảng việc, không dựa trên cảm giác.

- Mỗi việc trong tab Viec có trọng số theo cỡ: S = 1, M = 2, L = 3.
- % hoàn thành của một người = tổng (trọng số × % xong) chia tổng trọng số, tính trên các việc của người đó. Công thức có sẵn ở [05 §3](05-theo-doi-tien-do.md#3-công-thức-dropdown-và-tô-màu).
- Việc chỉ lên 100% khi người đọc chéo đã xem và test qua.
- Việc chuyển cho người khác (ốm, bận) thì đổi cột Người trong tab Viec và ghi BienBan.
- Ngày 29/10 cả nhóm xem lại bảng, thống nhất % cuối cùng và ghi vào chương Phân công của báo cáo.
