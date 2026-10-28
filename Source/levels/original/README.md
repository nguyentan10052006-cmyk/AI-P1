# 33 màn gốc của Bloxorz

`01.json` … `33.json` là 33 màn của Bloxorz (Damien Clarke, 2007), theo đúng thứ tự trong game, dùng làm bộ thực nghiệm cố định (docs/03). Các file này **được sinh tự động**, không sửa tay: muốn đổi thì sửa script rồi chạy lại.

```bash
cd Source
python -m experiments.convert_original_levels --check   # kiểm tra file có khớp với nguồn không (không ghi gì)
python -m experiments.convert_original_levels           # ghi file còn thiếu; không ghi đè file đã có
python -m unittest tests.test_original_levels -v        # kiểm tra tự động
```

## Nguồn

| | |
|---|---|
| Repo | [jacobcoughenour/bloxorz_gba](https://github.com/jacobcoughenour/bloxorz_gba), file `game/levels.json` |
| Commit | `f57ebb6bd57e9d2b42ab478a3d19e53028e62b1d` (13/09/2026, "Add LICENSE file") |
| Ngày lấy | 19/10/2026, tải từ `raw.githubusercontent.com` theo đúng commit trên |
| sha256 | `f30ed31fd4259c336a7ecdd4870ab4f74b13c7c17055e9e6cc8a045eac6406fe` (tính sau khi đổi CRLF thành LF) |
| Bản sao | `Source/experiments/data/bloxorz_gba/levels.json`, kèm `LICENSE` (GPL-3.0) của repo |

Chỉ lấy `levels.json`, `LICENSE` và `README.md` của repo. Không tải code C++, asset hay file nhị phân nào.

**Giấy phép.** Repo bản GBA phát hành theo GPL-3.0; bản sao `levels.json` giữ nguyên và đi kèm toàn văn giấy phép. Thiết kế màn chơi (hình bàn, vị trí công tắc, passcode) là của game gốc, do Damien Clarke giữ bản quyền; giấy phép GPL-3.0 của bản port không trao quyền đối với thiết kế đó. Nhóm dùng dữ liệu trong phạm vi đồ án môn học, trích dẫn cả game gốc lẫn bản port (docs/03 mục 7), và không phân phối như một sản phẩm.

## Chuyển đổi

Theo bảng ở docs/03 mục 6, cài trong `Source/experiments/convert_original_levels.py`:

- Ký tự ô: `' '`→`.`, `b`→`#`, `e`→`G`, `f`→`F`, `s`→`o`, `h`→`x`, `v`→`@`, `l` `r`→`b` (cầu đóng), `k` `q`→`B` (cầu mở). `spawn` = `[x, y]` thành `S` tại hàng y, cột x.
- Khóa công tắc `K` là ô (hàng `K % 10`, cột `K // 10`). Mọi tọa độ của bản GBA là (x, y) = (cột, hàng); file của nhóm dùng (hàng, cột).
- Kiểu liên kết: `onoff`→`toggle`, `on`→`open`, `off`→`close`. Công tắc mà mọi liên kết cùng kiểu ghi `bridges` + `effect`; có nhiều kiểu thì ghi `links`.
- `code` (số nguyên) → `passcode` chuỗi 6 chữ số, giữ số 0 ở đầu (màn 5, 9, 15, 16, 24).
- `group` (G1–G5, docs/03 mục 5) và `par` (bước tối ưu tham khảo, docs/03 mục 4) do nhóm thêm.

## Hiệu chỉnh so với nguồn

| Màn | Thay đổi | Căn cứ |
|---|---|---|
| 3 | Thêm 4 ô sàn tại (6, 11), (7, 12), (7, 13), (7, 14) | Bản GBA thiếu; cả ba nguồn đối chiếu đều có (docs/03 mục 3). Script chỉ áp dụng nếu các ô đó đang trống trong nguồn, và ghi chú vào trường `source` của `03.json` |

Không có hiệu chỉnh nào khác.

## Kiểm tra (`tests/test_original_levels.py`)

- Đủ 33 file `01.json` … `33.json`, JSON hợp lệ, đủ trường và đúng kiểu; lưới 10 × 15; đúng 1 ô `S` và 1 ô `G`.
- Passcode, nhóm, `par`, số ô từng loại (ô không trống, ô dễ vỡ, 3 loại công tắc, ô cầu) và tập kiểu công tắc khớp bảng ở docs/03 mục 4.
- Mọi công tắc nằm trong bàn, trỏ vào ô công tắc; mọi liên kết trỏ vào ô cầu; ô đáp của công tắc tách không trống; mọi ô công tắc đều có cấu hình.
- Đối chiếu từng ô và từng liên kết với `levels.json` thô, đọc độc lập với script.
- Chạy lại script ra đúng nội dung các file đã có.
- Bộ nạp màn (`bloxorz/level.py`) đọc được các màn.

## Việc còn mở

- **Định dạng `links`.** Có 6 màn có công tắc nối nhiều ô cầu với kiểu khác nhau: **17, 23, 25, 29, 30, 31** (tài liệu cũ chỉ nhắc màn 29). Bộ nạp màn hiện chưa đọc `links` nên từ chối 6 màn này với `LevelError`; 27 màn còn lại nạp được. Đây là việc của TV3 (V03, NV2), theo docs/03 mục 6.
- **`par`** lấy từ bộ giải tham khảo khi soạn tài liệu; BFS của nhóm phải kiểm lại (test T24, docs/02 mục 7).
