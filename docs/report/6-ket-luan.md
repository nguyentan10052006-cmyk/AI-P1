## 6. Kết luận

> Khung của TV4 (V35), 26/10. Viết xong sau khi có số liệu chính thức (27/10) và các đoạn nhận xét 5.4 (28/10). Các ý dưới đây là gợi ý cần kiểm lại với số liệu cuối cùng; câu nào không còn đúng thì bỏ.

### 6.1. Tóm tắt kết quả

- Mô hình hóa Bloxorz thành bài toán tìm kiếm với trạng thái gồm tư thế, vị trí khối (hoặc hai khối con) và cấu hình cầu; cài đủ luật của đề: ô dễ vỡ, công tắc mềm, nặng, tách, cầu với ba kiểu tác động (chương 2).
- Cài bốn thuật toán BFS, DFS, UCS, A* dùng chung một engine luật và một hợp đồng `Problem`/`Solver`; giải đủ 33 màn của game gốc. *(Kiểm lại: BFS khớp cột "Bước tối ưu" ở 33/33 màn; DFS giải được bao nhiêu màn, có màn nào hết giờ.)*
- Hàm chi phí không đồng nhất của UCS: *(TV3 tóm tắt một câu: chi phí theo gì, ở bao nhiêu màn UCS chọn đường khác BFS.)*
- A* với hai heuristic $h_M$ và $h_P$, cả hai đều tính đường tắt qua công tắc tách; đã chứng minh chấp nhận được và nhất quán với mọi hàm chi phí có bước tốn ít nhất 1, và kiểm tra bằng số liệu không có vi phạm nào trên toàn bộ không gian trạng thái của 33 màn (mục 3.4).
- Giao diện 3D bằng Ursina: chơi tay, bốn nút Giải chạy ở tiến trình riêng (không đơ, có Hủy và hết giờ), nút So sánh (chương 4).
- Thực nghiệm: *(TV2 tóm tắt 2–3 kết luận chính của chương 5, ví dụ thuật toán nào mở rộng ít nút nhất, tốn bộ nhớ nhất, nhanh nhất trên màn lớn.)*

### 6.2. Hạn chế

- Bộ 33 màn gốc nhỏ (bàn 10 × 15, không gian trạng thái tối đa khoảng 23 nghìn trạng thái ở màn 23 khi chi phí bằng 1), nên khác biệt về thời gian giữa các thuật toán chỉ vài mili-giây; nhóm phải dùng thêm bộ màn tự sinh để thấy khác biệt.
- Heuristic dạng $\lceil \Phi/2 \rceil$ chỉ bằng khoảng một nửa chi phí thật và coi mọi cầu là mở, nên A* chỉ bớt được khoảng 10 % số nút so với UCS trên 33 màn gốc (mục 5.4).
- Thời gian và bộ nhớ đo trên một máy, bằng `tracemalloc` của Python; không phản ánh chi phí của một bản cài bằng ngôn ngữ biên dịch.
- *(Bổ sung hạn chế của GUI, DFS, hàm chi phí nếu có.)*

### 6.3. Hướng phát triển

- Heuristic mạnh hơn mà vẫn chấp nhận được: tính khoảng cách theo tư thế khối trên bàn bỏ qua cầu (cơ sở dữ liệu mẫu nhỏ), hoặc lấy max của nhiều heuristic chấp nhận được.
- Thử IDA* hoặc A* hai chiều trên bộ màn lớn để giảm bộ nhớ.
- Sinh màn có lời giải dài hơn (nhiều công tắc, nhiều tầng cầu) để đánh giá thuật toán trên bài khó hơn.
- *(Bổ sung hướng phát triển của GUI và thực nghiệm.)*
