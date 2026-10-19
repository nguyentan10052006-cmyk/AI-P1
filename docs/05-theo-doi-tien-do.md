# Theo dõi tiến độ bằng Google Sheets

Mục tiêu: một chỗ duy nhất để biết ai đang làm gì, việc nào trễ, % hoàn thành của từng người, nguồn đã dùng và prompt AI. Đề chấm điểm cá nhân theo % hoàn thành, nên bảng này cũng là bằng chứng khi viết chương Phân công.

Sheet của nhóm tên **AI-P1**, link ghim trong nhóm chat. Mỗi tab là một Bảng (**Định dạng → Chuyển đổi thành bảng**). Bảng tính để vùng Việt Nam, nên công thức ngăn tham số bằng dấu chấm phẩy `;`.

## 1. Dựng sheet (đã dựng; giữ lại để dựng lại khi cần)

1. Tạo bảng tính mới.
2. Nhập lần lượt 7 file trong [`docs/sheet/`](sheet/): **Tệp → Nhập → Tải lên**, chọn file, chọn **Chèn trang tính mới**. Ô "Chuyển đổi văn bản thành số, ngày và công thức" bật hay tắt theo bảng dưới. Nhập xong thì đổi tên tab theo cột "Tab" và chuyển vùng dữ liệu thành Bảng.
3. Khi có số liệu thực nghiệm, TV2 tạo thêm hai tab: **thuc-nghiem** (nhập `summary.csv`) và **tong-hop**.
4. Thêm công thức và dropdown theo mục 3.
5. **Chia sẻ**: mời 5 người với quyền Người chỉnh sửa, rồi ghim link trong nhóm chat.

| Thứ tự | File | Tab | Chuyển đổi văn bản thành số/ngày |
|---|---|---|---|
| 1 | `sheet/1-viec.csv` | task | Bật, để cột ngày thành kiểu ngày |
| 2 | `sheet/2-phan-cong.csv` | phan-cong | Bật |
| 3 | `sheet/3-check-in.csv` | checkin | Bật |
| 4 | `sheet/4-man-choi.csv` | stage | **Tắt**, để giữ số 0 đầu của passcode |
| 5 | `sheet/5-nguon-trich-dan.csv` | cite | Tắt |
| 6 | `sheet/6-prompt-ai.csv` | prompt-ai | Bật |
| 7 | `sheet/7-bien-ban.csv` | bien-ban | Bật |

Nhập tab task **trước** tab phan-cong, vì công thức % ở phan-cong đọc dữ liệu từ task.

Khi chuyển tab stage thành Bảng, để cột Passcode ở kiểu văn bản. Kiểu số làm mất số 0 đầu của passcode màn 5, 9, 15, 16, 24 (ví dụ màn 16 là `000241`).

## 2. Các tab

| Tab | Mỗi dòng là | Cột chính | Ai cập nhật |
|---|---|---|---|
| **task** | một việc (V01–V40, khớp mục 3 của [01](01-phan-cong-PA2.md)) | ID, nhóm việc, việc, người, đọc chéo, bắt đầu, hạn, mốc, trạng thái, xong khi, link, ghi chú | Người làm việc đó |
| **phan-cong** | một thành viên | Mã TV, vai trò, họ tên, MSSV, thuật toán, phần chung, chương báo cáo, đọc chéo cho, **% hoàn thành** (công thức); bảng mức % theo trạng thái ở K1:L4 | Người điều phối |
| **checkin** | một lần check-in mỗi tối | Ngày, người, xong gì, mai làm gì, vướng gì, cần ai giúp | Mọi người, mỗi tối |
| **stage** | một màn (1–33) | Passcode, nhóm, đặc điểm, bước tối ưu, các ô đánh dấu: đã chuyển đổi, đã kiểm tra số ô, BFS, DFS, UCS, A*, GUI hiển thị đúng | TV2, TV5 và chủ 4 thuật toán |
| **thuc-nghiem** (tạo khi có số liệu) | một cặp (màn, thuật toán) | Các cột của `summary.csv` ([04 §5](04-thuc-nghiem.md#5-file-kết-quả)) | TV2 |
| **tong-hop** (tạo khi có số liệu) | bảng tổng hợp | Pivot theo nhóm màn và thuật toán | TV2 |
| **cite** | một nguồn đã dùng | Nguồn, tác giả, năm, link, commit, giấy phép, dùng vào đâu, người thêm, đã vào báo cáo | Người dùng nguồn đó, ngay khi dùng |
| **prompt-ai** | một lần dùng AI đáng kể | Ngày, người, công cụ, mục đích, prompt, dùng vào đâu, đã kiểm tra lại thế nào | Người dùng AI, ngay khi dùng |
| **bien-ban** | một quyết định | Ngày, vấn đề, quyết định, lý do, người chốt, ghi chú | Người điều phối |

Tab stage giúp nhìn nhanh tiến độ "33 màn × 4 thuật toán": chèn hộp kiểm vào các cột từ F đến L (**Chèn → Hộp kiểm**). Mỗi khi thuật toán của mình giải đúng một màn, chủ thuật toán tick vào ô tương ứng.

## 3. Công thức, dropdown và tô màu

Công thức dưới đây viết cho vùng Việt Nam (ngăn tham số bằng `;`). Nếu dựng lại sheet ở vùng dùng dấu phẩy, ví dụ Hoa Kỳ, thay mọi `;` bằng `,`.

**Mức tính % theo trạng thái** (tab phan-cong, K1:L4):

| Trạng thái | Mức tính vào % |
|---|---|
| Chưa bắt đầu | 0% |
| Đã bắt đầu | 50% |
| Hoàn thành | 100% |

**% hoàn thành** (tab phan-cong, ô I2, kéo xuống I6, định dạng phần trăm). Lấy trung bình mức của các việc có cột Người (task, cột D) là thành viên đó; cột Trạng thái là cột I của task:

```
=IF(COUNTIF(task!$D$2:$D;$A2)=0;0;SUMPRODUCT(COUNTIFS(task!$D$2:$D;$A2;task!$I$2:$I;$K$2:$K$4);$L$2:$L$4)/COUNTIF(task!$D$2:$D;$A2))
```

Ví dụ: TV5 có 6 việc, 2 việc Hoàn thành, 1 việc Đã bắt đầu, còn lại Chưa bắt đầu: (2 × 100% + 1 × 50%) / 6 ≈ 42%.

Đổi tên hay thêm một trạng thái thì sửa cả dropdown cột Trạng thái của tab task lẫn bảng mức K1:L4, nếu không % sẽ tính sai.

**Dropdown** (kiểu cột Thả xuống của Bảng):
- task, cột Trạng thái: `Chưa bắt đầu`, `Đã bắt đầu`, `Hoàn thành`.
- task, cột Người và Đọc chéo: `TV1` … `TV5`.
- task, cột Mốc: `M1`, `M2`, `M3`, `Nộp`.

**Tô màu** (tùy chọn; chọn vùng `A2:L` của task → **Định dạng → Định dạng có điều kiện → Công thức tùy chỉnh**):
- Việc trễ, tô đỏ: `=AND($I2<>"Hoàn thành";$G2<>"";$G2<TODAY())`.
- Việc xong, tô xanh: `=$I2="Hoàn thành"`.

**Tab tong-hop:** chọn dữ liệu của tab thuc-nghiem → **Chèn → Bảng tổng hợp**. Hàng: `group`. Cột: `algorithm`. Giá trị: `expanded`, tóm tắt theo **MEDIAN**. Làm tương tự cho `search_ms` và `peak_mem_kb`. Số liệu này dùng để điền bảng T3 của báo cáo.

## 4. Khi nào đổi Trạng thái

| Trạng thái | Khi nào chọn |
|---|---|
| Chưa bắt đầu | Chưa làm gì |
| Đã bắt đầu | Đã bắt tay làm, kể cả khi code đã xong và đang chờ đọc chéo |
| Hoàn thành | Code ở nhánh chính, test của phần đó qua, người đọc chéo đã xem ([01 mục 7](01-phan-cong-PA2.md#7-quy-tắc-phối-hợp)) |

## 5. Nhịp cập nhật

| Khi nào | Ai | Làm gì |
|---|---|---|
| Mỗi tối, trước 22h | Mọi người | Thêm một dòng checkin; cập nhật Trạng thái các việc của mình |
| Khi gộp code | Người làm | Dán link pull request hoặc commit vào cột Link; nhắn người đọc chéo |
| Trong 24 giờ sau đó | Người đọc chéo | Xem; đạt thì chuyển Trạng thái sang "Hoàn thành" |
| Trước mỗi mốc | Người điều phối | Lọc các việc chưa Hoàn thành mà đã quá hạn; nhắc trong nhóm chat |
| Khi có quyết định mới | Người điều phối | Thêm một dòng bien-ban |
| 29/10 | Cả nhóm | Thống nhất % hoàn thành cuối cùng cho báo cáo |
