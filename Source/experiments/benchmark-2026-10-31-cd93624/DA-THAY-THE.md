# Lần đo này đã được thay thế

Lần đo trên commit `cd93624` dùng `costs.py` khi bước làm khối tách đôi còn tính chi phí 1,0. Lý do: bảng năng lượng thiếu cặp tư thế nằm → tách, nên bước này rơi về `COST_BASE`. PR #23 (commit `0a35afd`) sửa mức này thành 1,62, bằng nằm → đứng.

Số liệu chính thức của chương 5 và Phụ lục A nay lấy từ `../benchmark-2026-10-31-0a35afd/`. Thư mục này được giữ nguyên, không sửa dữ liệu, để đối chiếu. Hai lần đo chỉ khác số đếm và tổng chi phí ở 10 màn G5 (50 cặp); xem `../benchmark-2026-10-31-0a35afd/so-sanh-voi-cd93624.txt` và mục 5.3 của chương 5.

Ở nhóm G5, không dùng `path_cost` hay số liệu UCS và A* của thư mục này.
