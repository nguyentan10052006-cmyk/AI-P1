# Phân công PA2 và mô tả công việc

Tài liệu chung của nhóm, viết sau buổi họp 18/10, cân bằng lại việc ngày 19/10 (mục 2). Muốn đổi điều gì ở đây thì báo nhóm chat trước, ghi vào tab **bien-ban** của Google Sheet rồi mới sửa file.

## 1. Những gì đã chốt

| Vấn đề | Quyết định |
|---|---|
| Cách chia việc | **PA2**: mỗi người một thuật toán (BFS, DFS, UCS, A*), một người làm GUI. Phần chung (luật chơi, màn chơi, thực nghiệm) được chia thành nhóm việc, mỗi nhóm có một người chủ; vài việc lẻ trong nhóm do người khác làm và được ghi rõ ở mục 3 |
| Theo dõi tiến độ | **Google Sheets**. Cách dựng ở [05-theo-doi-tien-do.md](05-theo-doi-tien-do.md) |
| Màn chơi | **33 màn của game gốc**, dùng cả 33 màn làm bộ thực nghiệm. Xem [03-man-choi.md](03-man-choi.md) |
| Luật chơi | Theo đề và luật của game gốc. Các chỗ đề chưa rõ đã chốt ở [02-luat-choi.md](02-luat-choi.md) |
| Chỉ số thực nghiệm | Số bước, tổng chi phí, số nút mở rộng, số nút sinh ra, frontier lớn nhất, số trạng thái đã thăm, bộ nhớ đỉnh, thời gian tìm kiếm, tổng thời gian. Định nghĩa ở [04-thuc-nghiem.md](04-thuc-nghiem.md) |
| Mốc | M1 thứ Tư 21/10 · M2 Chủ nhật 25/10 (đóng băng tính năng) · M3 thứ Tư 28/10 · nộp thứ Sáu 30/10 (hạn chót 31/10) |

**Còn phải điền:** tên người cho từng vai trò (mục 2), công nghệ GUI 3D, ngôn ngữ và công cụ viết báo cáo, cách dùng Git, người điều phối.

## 2. Ai làm gì

| Vai trò | Họ tên | Thuật toán | Phần chung phụ trách | Chương báo cáo | Đọc chéo cho |
|---|---|---|---|---|---|
| **TV1** | ________ | BFS | NV1 Engine lõi, ghép module · NV3 Tách và ghép khối · NV13 Kiểm thử cài đặt, đóng gói | 2. Mô hình hóa · 3.1 BFS | TV2 |
| **TV2** | ________ | DFS (hoặc IDS) | NV4 Màn chơi gốc · NV10 Thực nghiệm (trừ bộ màn tự sinh) | 3.2 DFS · 5. Thực nghiệm | TV5 |
| **TV3** | ________ | UCS | NV2 Ô đặc biệt · hàm chi phí · bộ nạp màn (V03) · bộ màn tự sinh (V40) · NV12 Video | 3.3 UCS | TV1 |
| **TV4** | ________ | A* | Heuristic · module chạy solver nền và So sánh cho GUI (V39) · NV11 Ghép báo cáo | 3.4 A* · 1. Phân công · 6. Kết luận | TV3 |
| **TV5** | ________ | (không) | NV9 GUI 3D (trừ V39), README | 4. Cài đặt và giao diện | TV4 |

**Đọc chéo cho** là người mà mình đọc code và chương báo cáo. Vòng đọc chéo: TV1 → TV2 → TV5 → TV4 → TV3 → TV1. Ai cũng đọc phần của một người khác và được một người khác đọc phần của mình.

**Vì sao chia như vậy.** Điểm yếu của PA2 là phần luật chơi làm chung dễ thành nút thắt, bốn người cùng chờ. Để tránh điều đó:

- Engine được chia thành hai khối có chủ riêng: lõi cùng tách và ghép khối (TV1), ô đặc biệt (TV3). Hợp đồng chung (mục 4) được chốt ngay ngày đầu, nên ai cũng code được mà không chờ người khác.
- Mỗi khối giao cho người cần nó nhất. Hàm chi phí của UCS phụ thuộc loại ô, nên TV3 làm ô đặc biệt. BFS là thuật toán nhanh xong nhất và cũng là "đáp án" để kiểm tra engine, nên TV1 giữ toàn bộ phần di chuyển của khối (lõi, tách và ghép khối) và ghép module. Thực nghiệm cần bộ màn, nên TV2 làm cả hai.
- Ai cũng có một thuật toán (hoặc GUI), một phần chung, một chương báo cáo và đọc phần của một người khác, đủ để trả lời vấn đáp về cả dự án.

**Cân bằng lại ngày 19/10** (tab bien-ban, #12). Bản chia đầu tiên bị lệch: TV5 (GUI 3D và video) và TV2 (màn chơi và thực nghiệm) nhiều việc nhất, TV3 ít việc nhất, còn TV4 vừa làm phần luật khó nhất (tách khối) vừa làm heuristic, chứng minh và ghép báo cáo. Các việc đã chuyển:

| Việc | Từ | Sang |
|---|---|---|
| V06 Tách và ghép khối (NV3) | TV4 | TV1 |
| V03 Bộ nạp màn | TV1 | TV3 |
| V37, V38 Kiểm thử cài đặt, đóng gói (NV13) | TV3 | TV1 |
| V40 Bộ màn tự sinh S1–S3 (tách từ NV10) | TV2 | TV3 |
| V36 Video (NV12) | TV5 | TV3 |
| V39 Module chạy solver nền và So sánh (tách từ V21) | TV5 | TV4 |

Người đọc chéo của mỗi việc đi theo người làm mới, theo vòng đọc chéo ở trên.

## 3. Các nhóm việc (NV)

Mỗi nhóm việc ghi: người chủ, người đọc chéo, hạn và mã việc tương ứng trong tab **task** của Google Sheet. Việc nào trong nhóm do người khác làm thì dòng Chủ ghi rõ. Phần "Cách làm" là các bước nên đi theo thứ tự.

### NV1 · Engine lõi và hợp đồng chung

**Chủ:** TV1; riêng bộ nạp màn (V03) là TV3 · **Đọc chéo:** TV3 (V03: TV4) · **Hạn:** khung code 19/10, lõi 20/10, bộ nạp màn 21/10, ghép đủ 24/10 · **Việc:** V01–V04

**Mục tiêu.** Viết phần code luật chơi dùng chung. GUI và cả 4 thuật toán gọi cùng một hàm `result()`; không ai viết lại luật ở chỗ khác.

**Cách làm**
1. Sáng 19/10: tạo khung code theo hợp đồng ở mục 4. Các hàm có đủ chữ ký, thân hàm để `raise NotImplementedError`. Khung có thêm một bài toán mê cung nhỏ (`GridMaze`) cùng giao diện `Problem`, để bốn người thử thuật toán ngay. Đẩy lên nhánh chính rồi báo nhóm.
2. Viết test cho 12 trường hợp của bảng chuyển ([02-luat-choi.md §3](02-luat-choi.md#3-bảng-chuyển-hướng-và-vị-trí)) trước, rồi mới cài. Cài bảng chuyển dưới dạng bảng tra (`dict`), không viết if-else rải rác.
3. Kiểm tra hợp lệ phần lõi: ô khối chiếm nằm ngoài bàn hoặc là ô trống thì hành động bị loại.
4. `is_goal(s)`: khối nguyên, đang đứng, trên ô đích.
5. Viết `result(s, a)` theo đúng thứ tự xử lý một lượt ở [02 §4](02-luat-choi.md#4-một-lượt-đi-được-xử-lý-theo-thứ-tự). Phần ô đặc biệt (TV3, NV2) và tách khối (TV1, NV3) đã nằm sẵn trong `rules.py`; mục 4 ghi rõ hàm nào thuộc phần nào.
6. Bộ nạp màn (V03, **TV3 làm**): đọc file màn theo định dạng ở [03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm) thành đối tượng `Level` (lưới, ô xuất phát, công tắc, cầu, công tắc tách) theo chữ ký ở mục 4. Báo lỗi rõ ràng nếu file sai. Trong lúc chờ, TV1 gõ tay màn 1 ngay trong test.
7. Từ 22/10 đến 24/10: ghép module ô đặc biệt của TV3 với lõi và phần tách khối, chạy lại toàn bộ test. Sau đó chạy BFS trên 33 màn; màn nào lệch cột "Bước tối ưu" ở [03 §4](03-man-choi.md#4-danh-sách-33-màn) thì báo chủ module liên quan.

**Đầu ra:** thư mục `Source/bloxorz/` (phần lõi của `rules.py`, `state.py`, `problem.py`), test T01–T06, `GridMaze` (đã có ở `bloxorz/maze.py`).

**Xong khi**
- [ ] Test T01–T06 qua.
- [ ] Bộ nạp màn của TV3 nạp đủ 33 màn không lỗi.
- [ ] BFS giải màn 1, 3, 6 đúng 7, 19, 35 bước.
- [ ] TV5 lăn được khối trên GUI bằng engine thật.
- [ ] Sau khi ghép, toàn bộ test T01–T24 qua trên nhánh chính.

**Lỗi hay gặp:** nhầm (x, y) với (hàng, cột); dùng `list` làm trạng thái nên không hash được (phải dùng `tuple`); quên đưa trạng thái cầu vào `State`, khiến hai trạng thái chỉ khác nhau ở cầu bị coi là một.

### NV2 · Ô đặc biệt: ô dễ vỡ, công tắc, cầu

**Chủ:** TV3 · **Đọc chéo:** TV4 · **Hạn:** 23/10 · **Việc:** V05

**Mục tiêu.** Cài đủ luật mục 2.5 của đề cho ô dễ vỡ, cầu, công tắc mềm và công tắc nặng, với ba kiểu tác động lên cầu: đảo, chỉ mở, chỉ đóng.

**Cách làm**
1. Viết test T07–T16 ([02 §7](02-luat-choi.md#7-bộ-kiểm-thử-luật)) trước, dựng trạng thái bằng tay, không cần chờ engine lõi xong.
2. Ô dễ vỡ: khối nguyên đứng trên ô dễ vỡ thì hành động bị loại (khối rơi). Khối nằm và khối con thì an toàn.
3. Trạng thái cầu là tập các ô cầu đang mở (`State.open_bridges`, kiểu `frozenset`), đã có trong `State` (mục 4.1).
4. Cầu đóng xử lý như ô trống, cầu mở như sàn.
5. Kích hoạt công tắc sau khi khối tới nơi. Công tắc mềm kích hoạt khi bất kỳ phần nào của khối nằm trên nó (kể cả khối con). Công tắc nặng chỉ kích hoạt khi khối nguyên đứng trên nó. Một công tắc có thể nối nhiều ô cầu, mỗi liên kết có kiểu riêng: `toggle` (đảo), `open` (chỉ mở), `close` (chỉ đóng). Code hiện chỉ cho một kiểu chung cho cả công tắc; phải mở rộng theo định dạng `links` ở [03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm) vì màn 29 cần. Khối con cũng đi qua cùng `_activate()`, nên phần này dùng chung cho cả trạng thái đã tách.
6. Sau khi đổi cầu: nếu có phần khối đang nằm trên ô cầu vừa đóng thì hành động bị loại. Khi đã tách, kiểm tra cả hai khối con.
7. Đưa cho TV1 ghép, rồi kiểm tra bằng BFS: màn 2, 5, 7, 11 phải ra 17, 33, 44, 47 bước; màn 4, 13 (ô dễ vỡ) phải ra 28, 46 bước.

**Đầu ra:** phần ô đặc biệt trong `Source/bloxorz/rules.py` (mục 4), `links` trong bộ nạp màn, và test T07–T16.

**Xong khi**
- [ ] Test T07–T16 qua.
- [ ] Sáu màn ở bước 7 đúng số bước tham khảo.

**Lỗi hay gặp:** lưu "công tắc đã bấm" vào trạng thái (không cần, chỉ cầu có trạng thái); quên trường hợp khối nằm đè hai công tắc cùng lúc; với kiểu "chỉ mở", bấm lại khi cầu đã mở thì không đổi gì.

### NV3 · Tách và ghép khối

**Chủ:** TV1 · **Đọc chéo:** TV3 · **Hạn:** 23/10 · **Việc:** V06

**Mục tiêu.** Cài công tắc tách: khối tách thành hai khối con 1×1×1, điều khiển từng khối, tự ghép lại khi hai khối kề nhau.

**Cách làm**
1. Viết test T17–T23 trước.
2. Trạng thái đã tách gồm hai ô của hai khối con, lưu thành cặp đã sắp xếp `(a, b)` với `a < b`. Hai khối con giống hệt nhau, nên sắp xếp giúp gộp trạng thái trùng và giảm khoảng một nửa số trạng thái.
3. Hành động khi đã tách: 8 hành động, gồm khối con 1 hoặc 2 nhân với 4 hướng (`U1` … `R2`). `U1` là khối ở ô `a` đi lên. Việc đổi khối đang điều khiển (phím Space trong GUI) không phải hành động tìm kiếm và không tính bước.
4. Khối nguyên đứng trên công tắc tách thì hai khối con xuất hiện tại hai ô ghi trong file màn. Ô đáp không kích hoạt gì.
5. Khối con lăn 1 ô. Ô mới phải nằm trong bàn, không trống, không phải cầu đóng. Khối con không làm vỡ ô dễ vỡ, không thắng ở ô đích, kích hoạt được công tắc mềm, không kích hoạt công tắc nặng hay công tắc tách.
6. Sau mỗi bước của khối con: nếu hai khối con kề cạnh (chung cạnh, kề chéo không tính) thì ghép thành khối nằm. Cùng hàng thì nằm ngang, neo ở ô bên trái; cùng cột thì nằm dọc, neo ở ô bên trên.
7. Khối con bấm công tắc và kiểm tra cầu đóng bằng chính phần công tắc của TV3 trong `rules.py`; không viết lại luật công tắc. Khi cầu đóng, phải kiểm tra cả hai khối con, vì khối kia có thể đang đứng trên cầu. Trước khi TV3 xong (23/10), tạm cho khối con không kích hoạt gì.
8. Ghép vào `result()` cùng lúc với module của TV3 (NV1 bước 7), rồi kiểm tra bằng BFS: màn 8, 9, 16 phải ra 10, 24, 28 bước.

**Đầu ra:** phần tách khối trong `Source/bloxorz/rules.py` (mục 4) và test T17–T23.

**Xong khi**
- [ ] Test T17–T23 qua.
- [ ] Màn 8, 9, 16 đúng số bước tham khảo.
- [ ] TV5 điều khiển được hai khối con trên GUI.

### NV4 · Màn chơi gốc (33 màn)

**Chủ:** TV2 · **Đọc chéo:** TV1 · **Hạn:** 20/10 · **Việc:** V07

**Mục tiêu.** Có 33 file màn đúng với game gốc, cùng một định dạng mà engine, GUI và script thực nghiệm đều đọc được.

**Cách làm**
1. Tải `game/levels.json` từ repo [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba) (commit `f57ebb6`, giấy phép GPL-3.0). Ghi nguồn vào tab cite ngay.
2. Cùng TV1 và TV3 (người viết bộ nạp màn) chốt định dạng file màn ([03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm)) trong ngày 19/10.
3. Viết script chuyển đổi theo bảng ánh xạ ở 03 §6. Bản GBA dùng (x, y) = (cột, hàng), khóa công tắc bằng x × 10 + y, và passcode bị mất số 0 ở đầu.
4. Sửa màn 3: thêm 4 ô sàn tại (6, 11), (7, 12), (7, 13), (7, 14) ([03 §3](03-man-choi.md#3-kết-quả-đối-chiếu)).
5. Kiểm tra tự động: mỗi màn có đúng 1 ô xuất phát và 1 ô đích; số ô từng loại khớp bảng ở 03 §4.
6. Đẩy 33 file vào `Source/levels/original/` (ký hiệu ô theo 02 §2) và báo TV1, TV3, TV5.
7. Khi BFS chạy được: so số bước với cột "Bước tối ưu" ở 03 §4. Màn nào lệch thì kiểm tra file màn trước, rồi mới nghi engine.

**Xong khi**
- [ ] Có 33 file màn, mỗi file có trường `source`.
- [ ] Kiểm tra số ô qua.
- [ ] Tab stage đã đánh dấu "Đã chuyển đổi" và "Đã kiểm tra số ô".

### NV5 · BFS

**Chủ:** TV1 · **Đọc chéo:** TV3 · **Hạn:** 21/10 (màn cơ bản), 25/10 (33 màn) · **Việc:** V08, V09

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

**Chủ:** TV2 · **Đọc chéo:** TV1 · **Hạn:** 21/10, 25/10 · **Việc:** V10, V11

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

**Lỗi hay gặp:** IDS dùng bảng nhớ toàn cục (nhớ mọi trạng thái đã duyệt qua các vòng) thì mất ưu điểm bộ nhớ của IDS: ở repo khóa trước ([06 §3](06-bao-cao-video.md#3-tài-liệu-tham-khảo-đã-có) mục 8), IDS tốn 30,7 MB trong khi BFS chỉ 5,6 MB. Dùng đệ quy rồi nâng `sys.setrecursionlimit` thì dễ tràn ngăn xếp, chương trình tắt mà không báo lỗi. Ở màn không có lời giải, IDS chỉ chặn lặp trên đường đi thì không tự dừng được; khi đó `timeout` là kết quả đúng.

### NV7 · UCS và hàm chi phí

**Chủ:** TV3 · **Đọc chéo:** TV4 · **Hạn:** mê cung 21/10, hàm chi phí 22/10, 33 màn 25/10 · **Việc:** V12–V14

**Cách làm**
1. Dùng hàng đợi ưu tiên `heapq` với mục `(g, thứ_tự, trạng_thái)`. `thứ_tự` là bộ đếm tăng dần, để Python không phải so sánh hai trạng thái khi `g` bằng nhau.
2. Giữ bảng `best_g`. Khi lấy ra một mục có `g` lớn hơn `best_g` của trạng thái đó thì bỏ qua (lazy deletion).
3. Kiểm tra đích khi **lấy ra** khỏi hàng đợi. Điều này bắt buộc để UCS cho lời giải tối ưu.
4. Thiết kế hàm chi phí không đồng nhất (đề mục 3.4). Quy tắc bắt buộc: **mọi bước có chi phí ≥ 1**, để heuristic của TV4 vẫn chấp nhận được. Hàm chi phí phải tạo ra lựa chọn thật: nếu không màn nào UCS chọn đường khác BFS thì chương UCS không có gì để phân tích. Repo khóa trước ([06 §3](06-bao-cao-video.md#3-tài-liệu-tham-khảo-đã-có) mục 8) chỉ cộng thêm rất ít (ô dễ vỡ +1, công tắc +0,25), và UCS ra y hệt BFS ở 9/10 màn. Hai hướng có lý do rõ:
   - **Theo năng lượng:** chi phí = 1 (một lần lăn) + công nâng trọng tâm khi lật, đơn vị là cạnh khối × trọng lượng khối nguyên. Đứng → nằm: 1 + (√5/2 − 1) ≈ 1,12. Nằm → đứng: 1 + (√5/2 − 1/2) ≈ 1,62. Nằm → nằm (lăn quanh cạnh dài): 1 + (√2/2 − 1/2) ≈ 1,21. Khối con nặng bằng nửa khối: 1 + (√2/2 − 1/2)/2 ≈ 1,10. UCS sẽ tránh dựng khối lên khi không cần. Mỗi con số tính lại được bằng hình học, nên dễ bảo vệ khi vấn đáp.
   - **Theo rủi ro:** ví dụ lăn lên ô dễ vỡ tốn thêm. Thầy cho phép dùng ML đơn giản để học trọng số nếu giải thích rõ trong báo cáo.
5. Chốt hàm chi phí trước 22/10 và gửi TV4, vì A* phải dùng cùng một hàm chi phí. Cài vào `Problem.step_cost`.
6. Kiểm tra cài đặt: đặt mọi chi phí bằng 1 thì số bước của UCS phải bằng BFS ở mọi màn.

**Xong khi**
- [ ] UCS giải 33 màn.
- [ ] Có bảng chi phí và lý do cho từng mức.
- [ ] Tổng chi phí của UCS bằng A* ở mọi màn.
- [ ] Liệt kê các màn mà UCS chọn đường khác BFS, kèm giải thích. Không có màn nào thì xem lại hàm chi phí.

### NV8 · A* và heuristic

**Chủ:** TV4 · **Đọc chéo:** TV5 · **Hạn:** mê cung 21/10, heuristic 24/10, 33 màn 25/10 · **Việc:** V15–V17

**Cách làm**
1. Cài giống UCS nhưng ưu tiên theo f = g + h. Khi f bằng nhau, ưu tiên h nhỏ hơn; ghi rõ cách phá hòa này trong báo cáo.
2. Thiết kế heuristic theo hàm chi phí của TV3. Vì mọi bước tốn ít nhất 1, một cận dưới của **số bước** còn lại cũng là cận dưới của chi phí. Gọi Φ(s) là khoảng cách nhỏ nhất từ một ô của khối (khi đã tách: một trong hai khối con) tới đích. Mỗi lần lăn, khối nguyên tiến lại gần đích tối đa 2 ô, khối con tối đa 1 ô, nên ⌈Φ/2⌉ là cận dưới, **với điều kiện Φ tính cả đường tắt qua công tắc tách** (bước 3).
3. **Bẫy: công tắc tách dịch chuyển hai khối con đi xa**, nên Manhattan thuần có thể ước lượng quá. Ví dụ: khối đứng ở (5, 0), công tắc tách ở (5, 3), hai ô đáp (1, 10) và (1, 12), đích (1, 13). Lời giải thật chỉ 4 bước (R, R, R1 rồi tự ghép, R), nhưng ⌈17/2⌉ = 9. Repo khóa trước ([06 §3](06-bao-cao-video.md#3-tài-liệu-tham-khảo-đã-có) mục 8) mắc đúng lỗi này. Cài **hai** heuristic, cả hai đều tính đường tắt:
   - **h_M (Manhattan):** Φ là khoảng cách Manhattan nhỏ nhất tới đích hoặc tới một công tắc tách bất kỳ. Ở màn không có công tắc tách, đây là Manhattan thường.
   - **h_P (lưới điểm):** coi mọi ô không trống (kể cả cầu và ô dễ vỡ) là đi được, thêm cạnh chi phí 0 từ mỗi công tắc tách tới hai ô đáp của nó. Tính trước khoảng cách từ mọi ô tới đích bằng 0-1 BFS ngược từ đích, trong `prepare()`. Ô không tới được đích cho h = ∞: trạng thái đó là ngõ cụt, bỏ luôn.

   h_P là heuristic chính; h_M dùng để so sánh trong thực nghiệm.
4. Phạt hướng phải chứng minh lại. Ví dụ ⌈Φ/2⌉ + 1 khi khối đang nằm là **không** chấp nhận được: khối nằm sát đích chỉ cần 1 bước để đứng lên đích. Có thể dùng max(⌈Φ/2⌉, 1) khi khối chưa đứng trên đích.
5. Viết chứng minh heuristic chấp nhận được (h(s) không lớn hơn chi phí thật còn lại) và nhất quán (h(s) ≤ c(s, a, s') + h(s')), theo đúng hàm chi phí đã chốt. Khung chứng minh: (i) mỗi bước, Φ giảm tối đa 2 (khối nguyên) hoặc 1 (khối con); (ii) dịch chuyển không làm Φ giảm thêm, vì khoảng cách tại công tắc tách không lớn hơn khoảng cách tại các ô đáp của nó; (iii) ở đích Φ = 0; (iv) mỗi bước tốn ít nhất 1.
6. Kiểm tra bằng số liệu, bổ sung cho chứng minh: dọc lời giải tối ưu của UCS, mọi trạng thái có h(s) ≤ chi phí còn lại; trên mọi cạnh A* đã duyệt, h(s) ≤ c + h(s'). Đếm số vi phạm; phải bằng 0 ở cả 33 màn.
7. Kiểm tra trên 33 màn: tổng chi phí của A* phải bằng UCS, và số nút mở rộng của A* không lớn hơn UCS. Nếu lệch thì heuristic không chấp nhận được hoặc cài sai.

**Xong khi**
- [ ] 33/33 màn cùng tổng chi phí với UCS, với cả h_M và h_P.
- [ ] Kiểm tra bằng số liệu ở bước 6: 0 vi phạm.
- [ ] Chứng minh nằm trong chương 3.4.
- [ ] Có số liệu so sánh h_M với h_P (bảng T5 và hình H5 ở [04 §7](04-thuc-nghiem.md#7-trình-bày-trong-báo-cáo)).

**Lỗi hay gặp:** quên đường tắt qua công tắc tách; chọn heuristic quá yếu. Repo khóa trước dùng ⌈d/2⌉ Manhattan và chỉ bớt được 0,6–22 % số nút so với UCS, nên phần so sánh A* với UCS gần như không có gì để viết.

### NV9 · GUI 3D

**Chủ:** TV5; riêng module chạy solver nền (V39, bước 7 và 9) là TV4 · **Đọc chéo:** TV2 (V39: TV5) · **Hạn:** chơi tay 21/10, module chạy nền 23/10, đủ tính năng 25/10 · **Việc:** V18–V22, V39

**Cách làm**
1. Chọn công nghệ trước 20/10 và ghi vào biên bản: Ursina (Python) hoặc web Three.js gọi server Python. Thầy cho phép GUI viết bằng ngôn ngữ khác; chỉ thuật toán bắt buộc dùng Python. Repo khóa trước ([06 §3](06-bao-cao-video.md#3-tài-liệu-tham-khảo-đã-có) mục 8) cho thấy Ursina đủ làm bàn 3D có hoạt ảnh lật và rơi qua mép, và gọi thẳng engine Python. Three.js đẹp hơn nhưng phải viết thêm server và API giữa GUI với engine.
2. Vẽ bàn 3D từ file màn. Mỗi loại ô một màu hoặc hình dễ phân biệt: sàn, trống, đích (lỗ), ô dễ vỡ (cam), công tắc mềm (tròn), công tắc nặng (hình X), công tắc tách (hình "( )"), cầu mở, cầu đóng.
3. Chơi tay: phím mũi tên gọi `result()` của engine; phím Space đổi khối con đang điều khiển; rơi thì thua, đứng trên đích thì thắng. **Không viết lại luật trong GUI.**
4. Các nút: New Game (chọn màn 1–33), Restart, Solve BFS, Solve DFS, Solve UCS, Solve A*. Bấm Solve thì gọi solver, khối tự lăn theo lời giải (hoạt ảnh từng bước), và hiện số bước, số nút mở rộng, thời gian tìm kiếm (không tính thời gian hoạt ảnh).
5. Trước khi có solver thật: nút Solve phát lại lời giải có sẵn của màn 1 là `R D D R R D R`.
6. Hiện số màn, passcode và số bước đã đi.
7. **Module chạy nền** (V39, `Source/solvers/runner.py`, chữ ký ở mục 4) đã có bản chạy được: server gọi `run_solver`, GUI gọi server. TV4 giữ và mở rộng module này (hiện đủ chỉ số mới, So sánh trên 33 màn). Solver chạy trong **tiến trình riêng** (`multiprocessing`), không chạy trong luồng giao diện. Trong lúc chờ, GUI hiện "Đang tìm…" và nút Hủy; quá 60 giây thì module dừng và GUI báo hết giờ. Repo khóa trước gọi solver ngay trong luồng giao diện, nên cửa sổ đơ suốt lúc tìm. Dùng tiến trình chứ không dùng luồng (thread), vì Python không dừng ngang được một luồng. Trên Windows, `main.py` phải có `if __name__ == "__main__":`.
8. Thông báo riêng cho 4 kết quả: thắng, rơi (thua), không có lời giải, hết giờ. Thử bằng màn không lời giải S3 ở [04 §8](04-thuc-nghiem.md#8-bộ-màn-tự-sinh).
9. Nút **So sánh**: module của TV4 chạy cả 4 thuật toán trên màn đang mở; GUI hiện kết quả thành một bảng gồm số bước, tổng chi phí, số nút mở rộng, thời gian. Ý tưởng lấy từ danh sách việc dự định trong README của repo khóa trước, nên ghi nguồn khi dùng.
10. Camera tự căn theo kích thước bàn; chỉnh được tốc độ phát lại lời giải và tạm dừng. Có màn hướng dẫn: chú giải 9 loại ô và các phím.

**Xong khi**
- [ ] Hiện đủ 9 loại ô.
- [ ] Chơi tay có thắng, có thua.
- [ ] Tách và ghép khối hoạt động.
- [ ] 4 nút Solve chạy được trên mọi màn.
- [ ] Solver chạy lâu không làm đơ GUI; Hủy và hết giờ hoạt động (thử DFS trên màn khó nhất và trên màn không lời giải).
- [ ] Nút So sánh hiện đủ bảng 4 thuật toán.
- [ ] Người khác cài theo README trên máy của họ và chạy được.

**Lỗi hay gặp (nếu dùng Ursina; rút từ README của repo khóa trước):** đối tượng không gắn vào một gốc chung của màn chơi thì không bị hủy khi đổi màn, nên bàn cũ còn sót; tạo nút trong vòng lặp bằng `lambda: chon(i)` thì mọi nút đều nhận giá trị cuối, phải viết `lambda i=i: chon(i)`; texture `.webp` không đọc được, phải chuyển hẳn sang PNG hoặc JPG (đổi đuôi file không đủ).

### NV10 · Thực nghiệm

**Chủ:** TV2; riêng bộ màn tự sinh (V40, bước 3) là TV3 · **Đọc chéo:** TV1 (V40: TV4) · **Hạn:** script 24/10, bộ màn tự sinh 24/10, chạy thử 25/10, chính thức 27/10 · **Việc:** V23–V25, V40

**Cách làm**
1. Viết script đo theo [04-thuc-nghiem.md](04-thuc-nghiem.md). Mỗi cặp (màn, thuật toán) chạy trong một tiến trình riêng, có timeout. Đo thời gian 5 lần lấy trung vị; đo bộ nhớ 1 lần riêng bằng `tracemalloc`. Ghi ra CSV.
2. Trước khi có solver thật, thử script với solver giả (trả kết quả cố định) để kiểm tra đủ cột CSV.
3. TV3 viết `experiments/gen_levels.py` sinh bộ màn tự sinh S1–S3 ([04 §8](04-thuc-nghiem.md#8-bộ-màn-tự-sinh)) và dùng BFS kiểm tra: S1, S2 giải được, S3 không có lời giải. S1 và S3 chỉ cần sàn nên làm trước; S2 cần cầu nên làm sau khi engine đã ghép (24/10). 33 màn gốc quá nhỏ, thời gian chỉ vài mili-giây, nên cần màn lớn hơn để thấy khác biệt giữa các thuật toán.
4. Ngày 25/10 (M2): chạy thử đủ 4 × 33, thêm A* với h_M và bộ màn tự sinh, rồi làm các kiểm tra chéo ở [04 §6](04-thuc-nghiem.md#6-kiểm-tra-chéo-trước-khi-dùng-số-liệu).
5. Ngày 26–27/10: chạy chính thức trên một máy, ghi cấu hình máy, vẽ biểu đồ, điền bảng. Gửi số liệu cho cả nhóm để sáng 28/10 mọi người viết nhận xét.
6. Tạo tab thuc-nghiem trong Google Sheet và nhập `summary.csv` vào đó.

**Xong khi**
- [ ] CSV có đủ 4 × 33 dòng chính, 33 dòng A* với h_M và các dòng của bộ màn tự sinh.
- [ ] Các kiểm tra chéo đều qua.
- [ ] Có bảng T1–T5 và hình H1–H6, H8, H9.
- [ ] Chương Thực nghiệm có số liệu.

### NV11 · Báo cáo

**Chủ:** từng người viết chương của mình (mục 2); TV4 ghép · **Hạn:** chương của từng người 27/10; chương Thực nghiệm và các đoạn nhận xét 28/10; bản ghép 28/10; PDF 30/10 · **Việc:** V26–V35

**Cách làm**
1. Xong code phần nào thì viết nháp chương đó ngay, không đợi tuần cuối. Khung báo cáo, quy ước viết, trích dẫn và phụ lục AI ở [06-bao-cao-video.md](06-bao-cao-video.md).
2. Mỗi người viết thêm một đoạn nhận xét kết quả thuật toán của mình trong mục 5.4 (V31–V34).
3. TV4 ghép bản đầy đủ ngày 28/10, cả nhóm rà soát ngày 29/10, xuất PDF ngày 30/10.

### NV12 · Video demo

**Chủ:** TV3; TV5 hỗ trợ chạy GUI, cả nhóm hỗ trợ · **Đọc chéo:** TV4 · **Hạn:** 29/10 · **Việc:** V36

Viết kịch bản theo [06 §5](06-bao-cao-video.md#5-video-10-điểm) từ 25/10, khi GUI đã đủ tính năng; cả nhóm duyệt ở M3. Quay ngày 28–29/10, có phụ đề hoặc thuyết minh, đăng YouTube ở chế độ công khai, dán link vào báo cáo.

### NV13 · Tích hợp, kiểm thử cài đặt, đóng gói

**Chủ:** TV1 · **Đọc chéo:** TV3 · **Việc:** V04, V37, V38

- Mỗi mốc: mọi người gộp code vào nhánh chính trước 18h. TV1 chạy toàn bộ test. Họp 15 phút, mỗi người demo phần mình **trên nhánh chính**, không demo bản trên máy riêng.
- Ngày 29/10: TV1 cài theo README trên một máy không phải của TV5 và chạy được GUI cùng 4 nút Solve.
- Ngày 30/10: TV1 đóng gói `MSSV1_MSSV2_….zip` đúng cấu trúc ở mục 4 của đề.

### NV14 · Điều phối

**Người điều phối:** ________ (nên là người tạo Google Sheet)

- Dựng Google Sheet theo [05-theo-doi-tien-do.md](05-theo-doi-tien-do.md), mời cả nhóm, ghim link trong nhóm chat.
- Mỗi tối nhắc check-in. Ai trễ quá 1 ngày thì hỏi thăm và báo nhóm.
- Ghi mọi quyết định vào tab bien-ban.

## 4. Hợp đồng chung

Khung code đã có sẵn (nhánh `test`, ghép vào `feature/triet/structure` ngày 19/10). Hợp đồng dưới đây mô tả **đúng code hiện có**. Bản đề xuất ban đầu (tuple `(kind, a, b, bridges)`, thư mục `engine/`, các file `tiles.py` và `split.py`) đã được thay bằng bản này ngày 19/10 (tab bien-ban, #14; lý do ở mục 4.1). Ai muốn đổi chữ ký hàm thì báo nhóm và ghi vào tab bien-ban trước.

```python
# Source/bloxorz/state.py  (TV1)
class Orient(str, Enum): STANDING, HORIZONTAL, VERTICAL, SPLIT    # đứng | nằm ngang | nằm dọc | đã tách
class Dir(str, Enum):    UP, DOWN, LEFT, RIGHT                     # thứ tự này là thứ tự hành động

@dataclass(frozen=True)
class State:                       # bất biến, hash được, dùng làm khóa của dict và set
    orient: Orient
    pos: Cell                      # (hàng, cột). Ô đứng; ô trái (HORIZONTAL); ô trên (VERTICAL); khối con thứ nhất (SPLIT)
    pos2: Cell | None              # khối con thứ hai khi SPLIT, luôn có pos < pos2; còn lại là None
    open_bridges: frozenset[Cell]  # tập các ô cầu đang mở
    def cells(self) -> tuple[Cell, ...]: ...   # các ô khối đang chiếm

@dataclass(frozen=True)
class Action:
    dir: Dir
    cube: int | None = None        # None khi chưa tách; 0 hoặc 1 khi đã tách (khối con ở pos là 0, ở pos2 là 1)
#   Cách viết tắt trong tài liệu: U = Action(Dir.UP); U1 = Action(Dir.UP, 0); U2 = Action(Dir.UP, 1)

# Source/bloxorz/problem.py  (TV1)
class Problem:
    def __init__(self, level: Level, start: State | None = None): ...
    goal: Cell                                            # ô đích (thuộc tính)
    def initial_state(self) -> State: ...
    def actions(self, s: State) -> list[Action]: ...      # MỌI hành động, thứ tự cố định: U, D, L, R; khi đã tách U1, D1, L1, R1, U2, D2, L2, R2
    def result(self, s: State, a: Action) -> State | None: ...   # None nếu hành động làm khối rơi
    def is_goal(self, s: State) -> bool: ...              # khối nguyên đứng trên ô đích
    def step_cost(self, s: State, a: Action, s2: State) -> float: ...  # TV3 cài hàm chi phí; mặc định 1

# Source/bloxorz/maze.py  (TV1): bài toán thử, cùng giao diện Problem
class GridMaze: ...                # trạng thái là (hàng, cột); ô chữ số 1..9 tốn đúng số đó
MAZES: dict[str, MazeCase]         # mê cung mẫu kèm đáp án (số bước ít nhất, chi phí nhỏ nhất)

# Source/bloxorz/level.py  (TV3: bộ nạp màn, V03)
@dataclass(frozen=True)
class Switch:
    at: Cell
    kind: str                      # 'soft' | 'heavy' | 'split'
    effect: str                    # 'toggle' | 'open' | 'close', áp dụng cho mọi cầu của công tắc
    bridges: tuple[Cell, ...]      # các ô cầu bị điều khiển
    targets: tuple[Cell, ...]      # chỉ công tắc tách: hai ô đáp

@dataclass(frozen=True)
class Level:
    id: str; name: str; group: str; source: str
    grid: tuple[str, ...]          # ký hiệu ô ở 02 §2; kích thước đọc từ file
    start: Cell; goal: Cell
    switches: dict[Cell, Switch]
    initial_open: frozenset[Cell]  # các ô cầu mở lúc đầu (ký tự B)
    # cùng vài trường cho GUI: chapter, order, kind, par, intro, unlock_stars
    def tile(self, cell) -> str: ...

def load_level(path: Path, level_id: str) -> Level: ...      # file sai thì raise LevelError, nói rõ file và ô
def load_levels(directory: Path) -> dict[str, Level]: ...

# Source/bloxorz/rules.py: luật một lượt đi. GUI, server và Problem.result() đều gọi step()
def step(level, s: State, a: Action) -> StepResult: ...      # StepResult(state, status 'ok' | 'fell' | 'won', events, moved)
#   Phần của TV1 (lõi, NV1):         BLOCK_MOVES (bảng chuyển), step(), _settle(), _support_problem()
#   Phần của TV3 (ô đặc biệt, NV2):  _fall_reason() (ô dễ vỡ, cầu đóng), _activate() với công tắc mềm/nặng, _apply_switch()
#   Phần của TV1 (tách khối, NV3):   nhánh SPLIT của step(), nhánh công tắc tách trong _activate(), _merge()

# Source/solvers/base.py  (TV1)
@dataclass
class SearchResult:
    status: str          # 'solved' | 'no_solution'  ('timeout' do khung chạy gán, solver không tự trả về)
    path: list[Action]   # dãy hành động từ trạng thái đầu tới đích; rỗng khi không có lời giải
    path_cost: float
    expanded: int
    generated: int
    max_frontier: int
    visited: int

class Solver:
    name = "BASE"
    def prepare(self, problem) -> None: ...     # tiền xử lý (ví dụ bảng heuristic của A*); mặc định không làm gì
    def search(self, problem) -> SearchResult: ...
#   Đăng ký trong solvers/__init__.py: ALGORITHMS = {'bfs': BFS, 'dfs': DFS, 'ucs': UCS, 'astar': AStar, 'astar_m': AStarM}
#   'astar' là A* với h_P (heuristic chính), 'astar_m' là A* với h_M; AStarM là lớp con của AStar (07 §9, #2)

# Source/solvers/runner.py  (TV4, V39): chạy solver ở tiến trình riêng cho GUI (đã có bản chạy được)
class SolveJob:
    def cancel(self) -> None: ...               # dừng tiến trình con ngay
def run_solver(solver_cls, problem, timeout_s=60.0, job: SolveJob | None = None) -> dict: ...
#   Gọi prepare() rồi search() trong tiến trình con. Trả về các trường của SearchResult
#   cùng prepare_ms, time_ms (chỉ search), peak_kb; hoặc {'ok': False, 'error', 'timeout' | 'cancelled'}
```

Bốn quy ước đi kèm:
- Tọa độ luôn là **(hàng, cột)**; hàng tăng xuống dưới, cột tăng sang phải.
- Không hàm nào được sửa trạng thái truyền vào; luôn trả về trạng thái mới.
- `actions()` trả về mọi hành động, kể cả hành động làm khối rơi. Solver gọi `result()`; kết quả `None` thì **bỏ qua và không tính vào `generated`** ([04 §3](04-thuc-nghiem.md#3-quy-ước-đếm-bắt-buộc-giống-nhau-ở-4-thuật-toán)). `GridMaze` làm giống hệt: hướng đâm vào tường cho `None`.
- Thời gian và bộ nhớ do script thực nghiệm đo bên ngoài. Solver chỉ tự đếm `expanded`, `generated`, `max_frontier`, `visited`.

Kiểm tra nhanh trên mê cung: `python -m unittest tests.test_solvers -v` (chạy trong `Source/`) chạy cả 4 solver trên các mê cung mẫu; solver nào chưa cài thì được bỏ qua.

### 4.1. Đối chiếu bản đề xuất với code (chốt 19/10)

| Đầu mục | Bản đề xuất | Chốt | Lý do |
|---|---|---|---|
| Thư mục engine | `Source/engine/` | **Giữ code**: `Source/bloxorz/` | Đổi tên chỉ tốn công sửa import ở server, solver, test |
| `tiles.py`, `split.py` riêng | Hai file, hàm `is_open`, `fragile_breaks`, `apply_switches`, `apply_split`, `try_merge` | **Giữ code**: luật nằm chung trong `rules.py`, chia phần sở hữu như ghi chú ở trên | Luật đã viết xong và có test; TV3 và TV1 nhận phần tương ứng, đọc lại và viết test T07–T23 |
| `State` | tuple `(kind, a, b, bridges)`, cầu là bitmask | **Giữ code**: dataclass, `Orient`, `frozenset` ô cầu mở | Hash được như nhau, dễ đọc, dễ giải thích khi vấn đáp; đổi thì phải sửa engine, server, GUI |
| `Action` | chuỗi `'U'`, `'U1'` … `'R2'` | **Giữ code**: `Action(dir, cube)`, `cube` 0 hoặc 1 | Như trên. `U1`/`U2` trong tài liệu ứng với `cube` 0/1 |
| `actions()` | chỉ hành động hợp lệ | **Giữ code**: mọi hành động, `result()` trả `None` khi rơi | Lọc trước thì mỗi hành động phải tính luật hai lần. Đổi lại phải theo quy ước đếm ở trên |
| `Level` | trường `bridges`, `bridges_open` (bitmask), `splits` riêng | **Giữ code**: `Switch` gộp cả công tắc tách, `initial_open` | Bộ nạp xử lý đồng nhất; cho phép công tắc tách nối cầu |
| Kiểu tác động theo từng liên kết | `links: [{cell, mode}]` | **Cần mở rộng code** (TV3, V03 và NV2) | Màn 29 có một công tắc nối nhiều cầu với kiểu khác nhau. Định dạng ở [03 §6](03-man-choi.md#6-định-dạng-file-màn-của-nhóm) |
| Ký hiệu ô | `-` `o` `@` `X` `T` | **Giữ code**: `.` `#` `o` `x` `@` | Code, GUI, test và 18 màn đã dùng. Hai bộ xung đột (`o`, `@` mang nghĩa khác nhau) nên chỉ được dùng một bộ. Bảng ở [02 §2](02-luat-choi.md#2-bàn-chơi-và-các-loại-ô) |
| `SearchResult` | đủ 7 trường | **Theo tài liệu**: đã sửa code | Thực nghiệm cần đủ chỉ số |
| `Solver` có `prepare()` | lớp `Solver` | **Theo tài liệu**: đã sửa code, 4 file solver là lớp con | Tổng thời gian và bộ nhớ đo cả `prepare()` ([04 §2](04-thuc-nghiem.md)) |
| `GridMaze` | có | **Theo tài liệu**: đã thêm `bloxorz/maze.py` và test | Để TV2, TV3, TV4 thử thuật toán ngay |
| Module chạy nền | `SolverRunner` có `start`, `poll`, `cancel` | **Giữ code**: `run_solver` và `SolveJob` trong `solvers/runner.py` | GUI web gọi qua server HTTP nên không cần `poll`; đã có hủy và hết giờ. V39 còn lại: nút So sánh hiện đủ chỉ số mới, kiểm thử trên 33 màn |
| Bộ màn | `levels/01.json … 33.json` | 33 màn gốc ở `Source/levels/original/NN.json`; màn tự sinh ở `levels/gen/`; 18 màn tự thiết kế giữ ở `levels/` cho GUI | Script thực nghiệm chỉ đọc `original/` và `gen/`, không lẫn với màn hướng dẫn. GUI nạp thêm `original/` là việc của TV5 |

Cấu trúc thư mục:

```
Source/
├── main.py                 # TV5: mở GUI (server + trình duyệt)
├── README.md               # TV5: cài đặt và chạy
├── requirements.txt
├── levels/                 # 18 màn tự thiết kế cho GUI
│   ├── original/01.json … 33.json   # TV2: 33 màn gốc
│   └── gen/                # TV3: màn tự sinh
├── bloxorz/                # TV1: state.py, rules.py (phần lõi, tách khối), problem.py, maze.py, serialize.py
│                           # TV3: level.py (bộ nạp màn), rules.py (phần ô đặc biệt)
├── solvers/                # base.py (TV1), bfs.py (TV1), dfs.py (TV2),
│                           # ucs.py + costs.py (TV3), astar.py + heuristics.py + runner.py (TV4)
├── server/                 # TV5: API HTTP cho GUI
├── experiments/            # TV2: run.py, charts.py, kết quả CSV · TV3: gen_levels.py
├── web/                    # TV5: GUI 3D (Three.js)
└── tests/                  # mỗi người viết test cho phần mình
```

## 5. Ai phải có gì ở mỗi mốc

| Mốc | TV1 (BFS) | TV2 (DFS) | TV3 (UCS) | TV4 (A*) | TV5 (GUI) |
|---|---|---|---|---|---|
| **M1 · T4 21/10**<br>một màn chạy trọn vòng | Engine lõi và test; BFS giải màn 1, 3, 6; đang làm tách khối | 33 file màn; DFS giải màn 1, 3, 6 | Bộ nạp màn; UCS đúng trên mê cung; đang làm ô đặc biệt | A* đúng trên mê cung; đang làm module chạy solver nền | Bàn 3D vẽ từ file; chơi tay màn 1 bằng engine thật |
| **M2 · CN 25/10**<br>đủ tính năng, đóng băng | Tách khối xong; ghép xong, toàn bộ test qua; BFS 33/33 khớp bảng | DFS 33 màn; script đo chạy thử 4 × 33 và bộ màn tự sinh | Ô đặc biệt xong; hàm chi phí đã chốt; UCS 33 màn; bộ màn tự sinh | Module chạy solver nền (23/10); h_M và h_P; A* 33 màn, cùng chi phí với UCS, 0 vi phạm | Đủ loại ô; tách khối; 4 nút Solve chạy nền; khối tự lăn; nút So sánh |
| **M3 · T4 28/10**<br>đủ số liệu, đủ chương | Chương Mô hình hóa và BFS | Số liệu chính thức và biểu đồ; chương DFS và Thực nghiệm | Chương UCS và hàm chi phí; kịch bản video | Chương A* và chứng minh; bắt đầu ghép | README; chương Giao diện |
| **Nộp · T6 30/10** | Kiểm thử cài đặt (29/10); đóng gói | Rà soát | Video YouTube công khai | Báo cáo PDF hoàn chỉnh | Rà soát; chạy GUI cho buổi quay video |

Từ M2 trở đi chỉ sửa lỗi, không thêm tính năng.

## 6. Ai cần gì từ ai, làm gì trong lúc chờ

| Người | Cần gì | Từ ai | Hạn cần | Trong lúc chờ |
|---|---|---|---|---|
| TV2, TV3, TV4, TV5 | Khung hợp đồng chung và `GridMaze` | TV1 | tối 19/10 | Đọc tài liệu luật và màn; viết test |
| TV1, TV3 | Định dạng file màn và 3 màn đầu (1, 3, 6) | TV2 | 20/10 | TV1 gõ tay màn 1 ngay trong test; TV3 viết bộ nạp màn theo bản đề xuất ở 03 §6 |
| TV1, TV5 | Bộ nạp màn | TV3 | 21/10 | TV1 gõ tay màn 1 trong test; TV5 đọc thẳng file JSON để vẽ bàn |
| TV3 | Engine lõi | TV1 | 20/10 | Viết test cho luật của mình, dựng trạng thái bằng tay |
| TV1 (tách khối) | Phần công tắc trong `rules.py` đã rà xong cho khối con | TV3 | 23/10 | Viết test T19, T23 trước; phần này đã chạy sẵn trong code |
| TV4 | Hàm chi phí | TV3 | 22/10 | Tạm dùng chi phí 1 cho mọi bước |
| TV5 | Engine lõi; BFS | TV1 | 20/10; 21/10 | Vẽ bàn từ file; Solve phát lại `R D D R R D R` |
| TV5 | Module chạy solver nền (V39) | TV4 | 23/10 | Gọi solver trực tiếp để thử nút Solve (GUI tạm đơ lúc tìm) |
| TV3 (bộ màn tự sinh) | BFS; engine đã ghép cầu | TV1 | 21/10; 24/10 | Sinh S1 và S3 trước, chỉ cần sàn |
| TV2 (thực nghiệm) | 4 solver trả về `SearchResult` | TV1, TV2, TV3, TV4 | 24/10 | Chạy script với solver giả |
| TV2 (thực nghiệm) | Bộ màn tự sinh | TV3 | 24/10 | Chạy thử trên 33 màn gốc trước |
| TV3 (video) | GUI đủ tính năng | TV5 | 25/10 | Viết kịch bản theo 06 §5 |
| TV4 (ghép báo cáo) | Nháp chương của mọi người | Cả nhóm | 27/10 | Dựng khung báo cáo, danh mục tài liệu tham khảo |

## 7. Quy tắc phối hợp

- Mỗi việc có đúng một người chủ. Muốn sửa module của người khác thì nhắn người chủ.
- Đổi hợp đồng chung hoặc định dạng file màn: báo nhóm chat trước, ghi vào tab bien-ban.
- Check-in mỗi tối trong tab checkin: xong gì, mai làm gì, vướng gì.
- Vướng quá 2 giờ thì hỏi ngay; trễ quá 1 ngày thì báo ngay, không đợi đến mốc.
- Đọc chéo trong vòng 24 giờ sau khi người kia gộp code; ghi nhận xét vào pull request hoặc nhóm chat.
- Ghi nguồn (tab cite) và prompt AI (tab prompt-ai) ngay khi dùng, không để đến cuối.
- Ngày 28/10 có buổi "dạy chéo" 30 phút: mỗi người giảng 5 phút phần mình. Đây là cách chuẩn bị cho vấn đáp, vì thầy hỏi ngẫu nhiên bất kỳ ai về bất kỳ phần nào.

**Một việc được tính là xong khi:** code đã ở nhánh chính; test của phần đó qua; người đọc chéo đã xem. Khi đó mới chọn "Hoàn thành" ở cột Trạng thái của tab task.

## 8. Cách tính % hoàn thành

Điểm cá nhân = điểm nhóm × % hoàn thành (đề mục 3.6), nên % phải dựa trên bảng việc, không dựa trên cảm giác. Nhóm không dùng cỡ hay trọng số; mỗi việc tính ngang nhau.

- Mỗi việc trong tab task được tính theo cột Trạng thái: Chưa bắt đầu 0%, Đã bắt đầu 50%, Hoàn thành 100%. Bảng mức này nằm ở tab phan-cong, ô K1:L4.
- % hoàn thành của một người = trung bình mức của các việc mà người đó làm (cột Người). Tab phan-cong cột I tự tính; công thức ở [05 §3](05-theo-doi-tien-do.md#3-công-thức-dropdown-và-tô-màu).
- Chỉ chọn Hoàn thành khi người đọc chéo đã xem và test qua (mục 7).
- Việc chuyển cho người khác (ốm, bận) thì đổi cột Người trong tab task và ghi vào tab bien-ban.
- Ngày 29/10 cả nhóm xem lại bảng, thống nhất % cuối cùng và ghi vào chương Phân công của báo cáo.
