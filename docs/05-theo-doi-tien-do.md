# Theo dõi tiến độ bằng Google Sheets

Mục tiêu: một chỗ duy nhất để biết ai đang làm gì, việc nào trễ, % hoàn thành của từng người, nguồn đã dùng và prompt AI. Đề chấm điểm cá nhân theo % hoàn thành, nên bảng này cũng là bằng chứng khi viết chương Phân công.

## 1. Dựng sheet (người điều phối, khoảng 15 phút)

1. Tạo bảng tính mới tên **Bloxorz – Tiến độ nhóm**.
2. Nhập lần lượt 7 file trong [`docs/sheet/`](sheet/): **Tệp → Nhập → Tải lên**, chọn file, chọn **Chèn trang tính mới**. Ô "Chuyển đổi văn bản thành số, ngày và công thức" bật hay tắt theo bảng dưới. Nhập xong thì đổi tên tab theo cột "Tab".
3. Tạo thêm hai tab trống: **ThucNghiem** (TV2 nhập `summary.csv` khi có số liệu) và **TongHop**.
4. Thêm công thức, dropdown và tô màu theo mục 3.
5. **Chia sẻ**: mời 5 người với quyền Người chỉnh sửa, rồi ghim link trong nhóm chat.

| Thứ tự | File | Tab | Chuyển đổi văn bản thành số/ngày |
|---|---|---|---|
| 1 | `sheet/1-viec.csv` | Viec | Bật, để cột ngày thành kiểu ngày |
| 2 | `sheet/2-phan-cong.csv` | PhanCong | Bật |
| 3 | `sheet/3-check-in.csv` | CheckIn | Bật |
| 4 | `sheet/4-man-choi.csv` | ManChoi | **Tắt**, để giữ số 0 đầu của passcode |
| 5 | `sheet/5-nguon-trich-dan.csv` | NguonTrichDan | Tắt |
| 6 | `sheet/6-prompt-ai.csv` | PromptAI | Bật |
| 7 | `sheet/7-bien-ban.csv` | BienBan | Bật |

Nhập tab Viec **trước** tab PhanCong, vì công thức % ở PhanCong đọc dữ liệu từ Viec.

## 2. Các tab

| Tab | Mỗi dòng là | Cột chính | Ai cập nhật |
|---|---|---|---|
| **Viec** | một việc (V01–V38, khớp mục 3 của [01](01-phan-cong-PA2.md)) | ID, nhóm việc, việc, người, đọc chéo, cỡ, trọng số, bắt đầu, hạn, mốc, trạng thái, % xong, xong khi, link, ghi chú | Người làm việc đó |
| **PhanCong** | một thành viên | Mã TV, vai trò, họ tên, MSSV, thuật toán, phần chung, chương báo cáo, đọc chéo cho, **% hoàn thành** (công thức) | Người điều phối |
| **CheckIn** | một lần check-in mỗi tối | Ngày, người, xong gì, mai làm gì, vướng gì, cần ai giúp | Mọi người, mỗi tối |
| **ManChoi** | một màn (1–33) | Passcode, nhóm, đặc điểm, bước tối ưu, các ô đánh dấu: đã chuyển đổi, đã kiểm tra số ô, BFS, DFS, UCS, A*, GUI hiển thị đúng | TV2, TV5 và chủ 4 thuật toán |
| **ThucNghiem** | một cặp (màn, thuật toán) | Các cột của `summary.csv` ([04 §5](04-thuc-nghiem.md#5-file-kết-quả)) | TV2 |
| **TongHop** | bảng tổng hợp | Pivot theo nhóm màn và thuật toán | TV2 |
| **NguonTrichDan** | một nguồn đã dùng | Nguồn, tác giả, năm, link, commit, giấy phép, dùng vào đâu, người thêm, đã vào báo cáo | Người dùng nguồn đó, ngay khi dùng |
| **PromptAI** | một lần dùng AI đáng kể | Ngày, người, công cụ, mục đích, prompt, dùng vào đâu, đã kiểm tra lại thế nào | Người dùng AI, ngay khi dùng |
| **BienBan** | một quyết định | Ngày, vấn đề, quyết định, lý do, người chốt, ghi chú | Người điều phối |

Tab ManChoi giúp nhìn nhanh tiến độ "33 màn × 4 thuật toán": chèn hộp kiểm vào các cột từ F đến L (**Chèn → Hộp kiểm**). Mỗi khi thuật toán của mình giải đúng một màn, chủ thuật toán tick vào ô tương ứng.

## 3. Công thức, dropdown và tô màu

Nếu bảng tính dùng định dạng vùng Việt Nam, Google Sheets ngăn tham số bằng dấu chấm phẩy `;` thay cho dấu phẩy `,`. Mỗi công thức dưới đây có cả hai cách viết.

**% hoàn thành** (tab PhanCong, ô I2, kéo xuống I6, định dạng phần trăm). Trọng số nằm ở cột G của Viec, % xong ở cột L (từ 0 đến 100):

```
=IFERROR(SUMPRODUCT((Viec!$D$2:$D$100=$A2)*Viec!$G$2:$G$100*Viec!$L$2:$L$100)/SUMIF(Viec!$D$2:$D$100,$A2,Viec!$G$2:$G$100)/100,0)
=IFERROR(SUMPRODUCT((Viec!$D$2:$D$100=$A2)*Viec!$G$2:$G$100*Viec!$L$2:$L$100)/SUMIF(Viec!$D$2:$D$100;$A2;Viec!$G$2:$G$100)/100;0)
```

**Trọng số tự tính theo cỡ** (tab Viec, cột G, nếu muốn thay số có sẵn):

```
=SWITCH(F2,"S",1,"M",2,"L",3)
=SWITCH(F2;"S";1;"M";2;"L";3)
```

**Dropdown** (**Dữ liệu → Xác thực dữ liệu → Thả xuống**):
- Viec cột K (Trạng thái): `Chưa bắt đầu`, `Đang làm`, `Chờ đọc chéo`, `Xong`, `Tạm dừng`.
- Viec cột F (Cỡ): `S`, `M`, `L`.
- Viec cột D và E (Người, Đọc chéo): `TV1` … `TV5`.

**Tô màu** (chọn vùng `A2:O100` của Viec → **Định dạng → Định dạng có điều kiện → Công thức tùy chỉnh**):
- Việc trễ, tô đỏ: `=AND($K2<>"Xong",$I2<>"",$I2<TODAY())`. Nếu dùng chấm phẩy: `=AND($K2<>"Xong";$I2<>"";$I2<TODAY())`.
- Việc xong, tô xanh: `=$K2="Xong"`.

**Tab TongHop:** chọn dữ liệu của tab ThucNghiem → **Chèn → Bảng tổng hợp**. Hàng: `group`. Cột: `algorithm`. Giá trị: `expanded`, tóm tắt theo **MEDIAN**. Làm tương tự cho `search_ms` và `peak_mem_kb`. Số liệu này dùng để điền bảng T3 của báo cáo.

## 4. Quy ước cột "% xong"

Chỉ dùng 5 mức để tránh đoán:

| % | Nghĩa |
|---|---|
| 0 | Chưa bắt đầu |
| 25 | Đã bắt đầu, chưa chạy được |
| 50 | Phần chính đã chạy được |
| 75 | Code xong, đang test hoặc chờ đọc chéo |
| 100 | Người đọc chéo đã xem, test qua, đã ở nhánh chính |

## 5. Nhịp cập nhật

| Khi nào | Ai | Làm gì |
|---|---|---|
| Mỗi tối, trước 22h | Mọi người | Thêm một dòng CheckIn; cập nhật trạng thái và % các việc của mình |
| Khi gộp code | Người làm | Dán link pull request hoặc commit vào cột Link; chuyển sang "Chờ đọc chéo" |
| Trong 24 giờ sau đó | Người đọc chéo | Xem; đạt thì chuyển "Xong" và 100% |
| Trước mỗi mốc | Người điều phối | Lọc các việc tô đỏ; nhắc trong nhóm chat |
| Khi có quyết định mới | Người điều phối | Thêm một dòng BienBan |
| 29/10 | Cả nhóm | Thống nhất % hoàn thành cuối cùng cho báo cáo |
