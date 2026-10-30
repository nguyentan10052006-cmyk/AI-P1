# Phụ lục B: phần của TV5 (gửi TV4 ghép vào `phu-luc-b-ai.md`)

> TV5 soạn ngày 29/10 theo mẫu phần TV2. Gồm ba phần: đoạn ghép vào B.1 và B.2; các dòng dán vào tab prompt-ai; và nguồn để kiểm lại. Prompt trích **nguyên văn** (giữ cả lỗi gõ) từ lịch sử ba phiên Claude Code lưu trên máy TV5 (file `.jsonl`, 32 prompt từ 19/10 21:17 tới 29/10 20:18; không tính thông báo hệ thống). Giờ ghi theo giờ Việt Nam (+07). Không chép email, token hay thông tin đăng nhập nào.

## Đoạn ghép vào B.1 (bảng công cụ)

| Công cụ | Ai dùng | Dùng cho |
|---|---|---|
| Claude Code (Anthropic), giao diện dòng lệnh, bản 2.1.303–2.1.310, mô hình `claude-opus-5-5` | TV5 (19/10–29/10) | Xem B.2, phần TV5 |

## Đoạn ghép vào B.2

**TV5.** Dùng Claude Code chạy ngay trong thư mục làm việc (repository nhóm và một thư mục tài liệu riêng không đưa lên GitHub). Claude đọc tài liệu và code, sửa file, chạy test, mở cửa sổ giao diện bằng script để chụp màn hình và tự bấm phím, chạy lệnh Git theo từng yêu cầu của TV5. Phần lớn code giao diện trong `gui/` và tài liệu của TV5 do Claude viết theo yêu cầu trong prompt, theo `docs/07` và theo một bản đặc tả giao diện riêng của TV5.

TV5 làm các việc sau:
- viết prompt, đặt phạm vi và ràng buộc cho từng đợt (không push thẳng lên `main`, không push khi chưa đọc lại, commit dưới tên TV5, không ảnh hưởng việc của thành viên khác);
- chạy thử giao diện và nhận xét những chỗ chưa ổn, ví dụ góc xoay camera dễ làm lẫn hướng, bóng đổ, khung kết quả che mất bàn;
- tự sửa một phần code (tô màu ô màn đang mở trong lưới chọn màn) rồi nhờ Claude sửa lỗi phát sinh, giới hạn "chỉ sửa lỗi";
- cho phép từng thao tác lên GitHub (push, soạn nội dung PR) và tự mở, gộp các PR của mình.

Mọi lần chạy test và kiểm tra dưới đây do Claude chạy trong phiên.

| Ngày | Việc | Kết quả dùng vào đâu | Kiểm tra lại |
|---|---|---|---|
| 19/10 | Soạn tài liệu kiến trúc và tích hợp GUI Ursina từ đặc tả kỹ thuật riêng của TV5 | `docs/07-kien-truc-gui-ursina.md`; nhánh `docs/kien-truc-gui-ursina` | TV5 đọc lại trước khi push; đối chiếu với `docs/01`–`06` |
| 21/10 | Rà các nhánh trên GitHub; sửa biên bản #3; cài Python 3.11 và Ursina, chốt phiên bản; vẽ bàn từ file màn (V18) và chơi tay bằng engine (V19) | `docs/sheet/7-bien-ban.csv`; `requirements.txt`; `gui/app.py`, `board_view.py`, `block_view.py`; PR #7, #8 | Mở được cửa sổ thử; màn 1 thắng đúng 7 bước; lời giải BFS màn 2, 8, 9, 16 thắng đúng 17, 10, 24, 28 bước |
| 23/10 | Check-in; ô đặc biệt, cầu, tách khối (V20); nút Giải, So sánh, Hủy, chọn màn, khối tự lăn (V21); README (V22); nháp chương 4 (V30) | `gui/`; PR #9; nhánh `feature/vo/V22-readme`; `docs/report/4-cai-dat-giao-dien.md` | Ghép thử với nhánh của TV2, TV3, TV4: BFS tự lăn thắng 33/33 màn, So sánh đủ năm dòng ở 33/33 màn; Hủy dừng đúng |
| 25/10 | Giới hạn góc camera (nghiêng tối đa 40°, bốn nấc góc cao, nhìn từ đỉnh); làm lại màu sắc theo đặc tả giao diện; bỏ bóng đổ; dời khung kết quả sang cột trái và căn bàn để không bị che; sửa lỗi sau khi TV5 tự sửa lưới chọn màn | `gui/`; PR #15 | Chụp màn hình ở màn 8, 28 sau mỗi thay đổi; đo góc camera không bị xoay nghiêng; cả bộ test qua |
| 29/10 | Cập nhật README theo phím mới; chụp lại toàn bộ hình chương 4 trên bản ghép thử với `integration/M2`; chạy lại kiểm thử giao diện; phần này | `Source/README.md`; `docs/report/4-cai-dat-giao-dien.md`, `hinh/`; `docs/report/phu-luc-b-tv5.md` | Ghép thử `main` với `integration/M2` không xung đột, cả bộ test qua, 33/33 màn nạp được; script kiểm tra camera qua mọi nấc; BFS tự lăn trên 33 màn |
| 30/10 | Rà các nhánh trên GitHub và trên máy; gộp V22, V30 và nháp báo cáo TV4 vào nhánh tích hợp `thu/test-main-m2`; tạm nối hàm chi phí V13 vào giao diện và script thực nghiệm (thêm `--cost`); nới cột Chi phí của bảng So sánh; cập nhật README | `gui/app.py`, `gui/hud.py`, `experiments/run.py`, `tests/test_experiments.py`, `Source/README.md`, chương 4 | 206 test qua; với chi phí thật, A* cùng chi phí với UCS ở 33/33 màn và `check_heuristics.py` báo 0 vi phạm; mở giao diện thật chạy So sánh ở màn 23 và chụp màn hình để kiểm tra bảng |
| 30/10 | Hoàn thiện đồ họa V21 (`ef1f10c`, `c73bb35`, `44dc9e3`): khối lật quanh cạnh, đổ nghiêng khi rơi, ô vát cạnh, lỗ đích nhìn xuyên, hộp kết thúc màn kéo thả được, font Be Vietnam Pro, thẻ kiểu kính mờ. Rà soát GUI rồi sửa 6 lỗi: Hủy không dừng được khối tự lăn; bấm Giải/So sánh khi đang tự lăn hoặc vừa thắng/rơi; cầu vẽ sai khi bấm R lúc cầu đang đổi; dòng trạng thái đè chữ "H: ẩn" và bảng So sánh; Enter lọt qua bảng F1/Ctrl+K; thu phóng không căn lại bàn | `gui/app.py`, `hud.py`, `board_view.py`, `camera_controller.py`, `popup.py`; `Source/README.md`, chương 4 | Script chạy giao diện thật (cửa sổ offscreen) tái hiện được cả 6 lỗi trước khi sửa, sau khi sửa không còn; kiểm tra hồi quy hộp thắng, hộp rơi, bảng So sánh và chụp màn hình khung kết quả; 206 test qua (1 bỏ qua) |

**Phần AI đề xuất và phần TV5 chọn.**
- **Claude đề xuất,** TV5 đồng ý qua prompt tiếp theo:
  - chạy solver ở tiến trình riêng và hỏi kết quả mỗi khung hình (theo `docs/07`);
  - cách đặt các nấc camera cụ thể (±20°, ±40°; 52°, 45°, 38°, 30°) và cách căn bàn khi khung kết quả hiện;
  - cách tổ chức chương 4.
- **TV5 quyết định:**
  - dùng Ursina (cùng nhóm, bien-ban #3);
  - camera chỉ nhìn từ trên xuống, không xoay 360°; thêm một nấc nghiêng mỗi bên và các nấc hạ thấp góc nhìn;
  - bỏ bóng đổ; màn đang mở phải có màu khác trong lưới chọn màn;
  - tên nhánh, thời điểm push, commit dưới tên TV5; không giao cho Claude việc của thành viên khác (bộ nạp màn, solver, runner).

*(TV5 bổ sung trước khi nộp: các lần tự chạy lại hoặc tự sửa code ngoài phiên Claude Code, nếu có.)*

## Ví dụ prompt (trích nguyên văn)

Prompt giao việc có giới hạn, 23/10 15:31:

> làm V22 và V30 trước đi trên tiền đề phải không ảnh hưởng đến các công việc của các thành viên khác

Prompt nhận xét sau khi chạy thử, 25/10 16:56:

> Bạn xem lại hững thay đổi gần đây đi, nhưng toi thấy phần xoay camera mó không ổn lắm, góc xoay thì phải luôn  nhìn từ trên uống hay có việc nhìn góc nghiên thì cũng từ trên xuống, với nếu đưuọc phép  xoay 3060 độ thì sẽ dễ khiến người chơi bị lẫn lộn hướng trái phải trên dưới lắm nên phải đặt các góc sao cho ít bị lẫn lộn, bạn giúp tôi tối ưu lại với

Prompt giới hạn phạm vi sửa, 25/10 18:00:

> Tôi vừa sửa khi bấm nút chọn màng thì nó không hiện màng hiện tại, kiểu như tất cả các màng đều cùng màu và tôi sửa thành đang ở màng nào thì ô màng đó có màu khác mà sửa xong thì nó lỗi, bạn giúp tôi chỉnh nó vfa tuyệt đối chỉ sửa lỗi không đưuọc phép tực hiện các thao tác phái sinh khác

**Danh sách đủ các đợt** (nguyên văn, prompt dài chỉ ghi câu đầu):

| Ngày, giờ | Prompt |
|---|---|
| 19/10 21:17 | `Thư mục docs_private là thư mục tôi dùng tạm để làm các việc cá nhân cho đồ án mà chưa public cho nhóm, … bạn giúp tôi pull về vô Project đi` |
| 19/10 21:22 | `Tạm thời cái Source chỉ là do nhóm trưởng vibe code để demo họp buổi đầu thôi, nhóm đang quyết dùng Ursina Engine. …` |
| 19/10 21:33 | `giúp tôi push lên đi, tài liệu ổn rồi, nhớ tạo nhánh riêng nha, đừng có push thảng lên main hay dev` |
| 21/10 13:42 | `Giờ bạn lên github kiểm tra xem có những gì thay đổi không? …` |
| 21/10 13:58 | `Sửa 7-bien-ban.csv #3, và nêu các công việc tôi cần làm trong hôm nay` |
| 21/10 14:01 | `push bien-ban lên đi và tạo danh sách công việc bằng markdown vào trong docs_private và thực hiện 1. …` |
| 21/10 14:08 | `ở 1 còn 1 việc chuwwa làm, bạn thực hiện luôn đi, pull các màng từ feature/Tien/M1 cũng được và thực hiện công việc số 2` |
| 21/10 14:16 | `ủa tôi chạy thử để test bằng cách nào` |
| 21/10 14:31 | `Làm luôn phần 3 đi (V19)` |
| 21/10 14:38 | `Từ từ tôi hỏi tí, thao tác lăn là sửa ở V mấy hay M mấy tôi nhìn không ưng lắm` |
| 21/10 20:21 | `Bạn quét github xem các nhánh khác sao rồi, tôi có thể hoàn thành toàn bộ công việc cho hôm nay chưa …` |
| 21/10 20:23 | `commit rồi ush lên giùm tôi đi` |
| 23/10 14:11 | `đọc tài liệu AGENTS.md để nắm bắt khái quát lại đồ án, …` |
| 23/10 14:25 | `bạn giúp tôi viết check-in tôi tự copy lên google sheet và giúp tôi bắt đầu V20 sau khi xong checkin đi` |
| 23/10 14:28 | `làm tiếp đi, tôi lỡi tay bấm dừng thôi` |
| 23/10 14:47 | `bạn kiểm tra lại trên github sao rồi, tôi đãcho PR rồi` |
| 23/10 14:51 | `bạn giúp tôi cho lệnh terminal để tuự động giải màn 33 với, chỉ cần cho code không cần chạy` |
| 23/10 14:56 | `tự động tạo script tự động chạy toàn bộ  33 màn  (không cần lưu script hoặc` |
| 23/10 14:57 | `lưu script đó vào doc_private đi` |
| 23/10 14:59 | `ý là script khi chạy sẽ mở luôn GUI cho chạy tự động và tôi có thể thể nhìn luôn á` |
| 23/10 15:02 | `commit và push lên github đi, nhớ là dưới danh nghiax tôi chứ không phải claude code` |
| 23/10 15:05 | `Trước làm tiếp V21 thì kiểm tra các màn còn lại của trọng đã push nhánh lên chưa rồi thì pull về máy tôi hết đi, …` |
| 23/10 15:20 | `commit và push và soạn nội dung PR. …` |
| 23/10 15:25 | `ủa sao python main.py mà cái DFS vẫn hiện là chưa nạp vậy, tôi tưởng bạn pull về rồi` |
| 23/10 15:29 | `quay lại nhánh hồi nãy lam đi và giúp tôi commit và push lên nếu chưa làm với, …` |
| 23/10 15:31 | `làm V22 và V30 trước đi trên tiền đề phải không ảnh hưởng đến các công việc của các thành viên khác` |
| 25/10 16:56 | `Bạn xem lại hững thay đổi gần đây đi, nhưng toi thấy phần xoay camera mó không ổn lắm, …` |
| 25/10 17:05 | `Từ từ, bạn xem GAME_UI_UX_SPECIFICATION.md coi có thiết kế giao diện gì không kiểu như là theme gì đó, …` |
| 25/10 17:17 | `Bỏ cái bón đổ đi, sửa lại cái tài liệu GAME_UI_UX_SPECIFICATION.md cho nó hợp lý` |
| 25/10 17:24 | `có mấy bảng thông số hiện lên khi chọn giải bằng thuật toán nó cho mất cái bàn rồi, bạn giúp  tôi tối ưu chỉnh lại đi` |
| 25/10 18:00 | `Tôi vừa sửa khi bấm nút chọn màng thì nó không hiện màng hiện tại, …` |
| 29/10 20:18 | `Giúp tôi hoàn thiện các phần còn lại của đồ án đi` |

## Dòng dán vào tab prompt-ai (`docs/sheet/6-prompt-ai.csv`)

```csv
2026-10-19,TV5,Claude Code (Anthropic),Soạn tài liệu kiến trúc và tích hợp GUI Ursina,"Tạm thời cái Source chỉ là do nhóm trưởng vibe code để demo họp buổi đầu thôi, nhóm đang quyết dùng Ursina Engine. …","docs/07-kien-truc-gui-ursina.md","TV5 đọc lại trước khi push; đối chiếu docs/01–06"
2026-10-21,TV5,Claude Code (Anthropic),"Cài môi trường, chốt phiên bản; V18 vẽ bàn, V19 chơi tay; sửa biên bản #3","push bien-ban lên đi và tạo danh sách công việc bằng markdown vào trong docs_private và thực hiện 1. …","requirements.txt, gui/; PR #7, #8","Màn 1 thắng đúng 7 bước; lời giải BFS màn 2, 8, 9, 16 thắng đúng số bước"
2026-10-23,TV5,Claude Code (Anthropic),"V20 ô đặc biệt; V21 nút Giải, So sánh, Hủy, chọn màn; nháp V22, V30","bạn giúp tôi viết check-in tôi tự copy lên google sheet và giúp tôi bắt đầu V20 sau khi xong checkin đi","gui/; PR #9; README; chương 4","Ghép thử với nhánh TV2–TV4: BFS tự lăn thắng 33/33 màn; So sánh đủ năm dòng 33/33 màn"
2026-10-25,TV5,Claude Code (Anthropic),"Giới hạn góc camera, màu sắc, bỏ bóng đổ, khung kết quả không che bàn; sửa lỗi lưới chọn màn","Bạn xem lại hững thay đổi gần đây đi, nhưng toi thấy phần xoay camera mó không ổn lắm, …","gui/; PR #15","Chụp màn hình màn 8, 28; đo góc camera; cả bộ test qua"
2026-10-29,TV5,Claude Code (Anthropic),"Cập nhật README; chụp lại hình và kiểm thử chương 4; phụ lục B phần TV5","Giúp tôi hoàn thiện các phần còn lại của đồ án đi","Source/README.md; docs/report/4-cai-dat-giao-dien.md, hinh/, phu-luc-b-tv5.md","Ghép thử main với integration/M2: test qua, 33/33 màn nạp được; kiểm tra camera mọi nấc; BFS tự lăn 33 màn"
```

## Nguồn để kiểm lại

Lịch sử phiên nằm trên máy TV5, trong thư mục dự án của Claude Code (`~/.claude/projects/`, ba file `.jsonl`). Prompt đầy đủ trích được bằng cách lọc các dòng có `"type": "user"` và nội dung là văn bản. Commit của TV5 ghi tác giả "artyVo" (email sinh viên 24120478).
