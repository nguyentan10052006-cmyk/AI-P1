# Dựng Report.pdf

`docs/report/Report.pdf` được dựng từ các file Markdown trong `docs/report/` (thứ tự ở [../README.md](../README.md)): pandoc chuyển từng file sang LaTeX vào `chapters/`, rồi XeLaTeX biên dịch `Report.tex` theo khung báo cáo (bìa, mục lục, đầu trang, chân trang).

| File | Vai trò |
|---|---|
| `info.tex` | Thông tin bìa còn thiếu: lớp học phần, giảng viên, **link video YouTube**. Sửa file này rồi chạy `python3 build.py --tex-only` |
| `build.py` | Ghép các phần theo thứ tự, gọi pandoc và XeLaTeX, chép PDF ra `docs/report/Report.pdf` |
| `filter.lua` | Bộ lọc pandoc: gắn chú thích "Bảng x.y" vào bảng, "Hình x.y" vào hình; tính độ rộng cột; `[chữ]{.dien}` thành chữ đỏ (chỗ còn phải điền) |
| `preamble.tex`, `cover.tex`, `logo-hcmus.png` | Giao diện chung và trang bìa |
| `Report.tex`, `chapters/*.tex` | Do `build.py` sinh ra từ Markdown; không sửa tay |

## Lệnh

Chạy trong thư mục này:

```bash
python3 build.py              # sửa Markdown xong: pandoc + XeLaTeX 3 lượt
python3 build.py --tex-only   # chỉ sửa info.tex: XeLaTeX 3 lượt, không cần pandoc
```

Cần pandoc 3.x (`pip install pypandoc_binary` cũng được) và XeLaTeX (MiKTeX hoặc TeX Live). Trên WSL, script tự tìm `xelatex.exe` của MiKTeX bên Windows. Không cài được thì tải cả thư mục `docs/report` lên Overleaf, chọn Compiler = XeLaTeX, Main document = `latex/Report.tex` (các file `chapters/*.tex` đã có sẵn).

Sau khi dựng, tìm câu bẫy của đề trong PDF (docs/06 §4) và kiểm tra bìa có link video.
