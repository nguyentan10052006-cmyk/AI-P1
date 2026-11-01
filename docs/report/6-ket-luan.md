## 6. Kết luận

### 6.1. Kết quả đạt được

- **Mô hình hóa.** Trò chơi Bloxorz được đưa về bài toán tìm kiếm với trạng thái gồm tư thế, vị trí khối (hoặc vị trí hai khối con) và tập cầu đang mở (chương 2). Engine cài đủ luật của đề: ô dễ vỡ, công tắc mềm và công tắc nặng với ba kiểu tác động (đảo, mở, đóng), công tắc tách, điều khiển từng khối con và tự ghép khi hai khối con kề nhau. 33 màn gốc có tổng cộng 70 062 trạng thái tới được.
- **Bốn thuật toán** BFS, DFS, UCS và A* được tự cài bằng Python, chỉ dùng cấu trúc dữ liệu của thư viện chuẩn (`deque`, `list`, `heapq`), và dùng chung một engine luật, một hợp đồng `Problem`/`Solver`. Cả bốn giải đủ 33/33 màn gốc. BFS cho số bước tối ưu ở 33/33 màn; UCS và A* cho tổng chi phí tối ưu ở 33/33 màn; DFS luôn tìm ra lời giải nhưng lời giải dài gấp 1,73 lần tối ưu theo trung vị.
- **Hàm chi phí** dựa trên công nâng trọng tâm khi lật khối, cộng phụ phí rủi ro khi đè lên ô dễ vỡ (mục 3.3). Mọi bước tốn từ 1,10 đến 1,71. Với hàm này, UCS chọn đường rẻ hơn BFS ở 2 màn (17 và 23) với cùng số bước.
- **A*** dùng hai heuristic $h_M$ và $h_P$, cả hai đều tính đường tắt qua công tắc tách. Nhóm chứng minh cả hai chấp nhận được và nhất quán với mọi hàm chi phí có bước tốn ít nhất 1 (mục 3.4.4), và kiểm tra bằng số liệu: 0 vi phạm trên 340 414 cạnh của 33 màn gốc và 2 015 147 cạnh của 14 màn tự sinh. $h_P$ còn phát hiện ngõ cụt và màn không có lời giải.
- **Giao diện 3D** bằng Ursina (chương 4): chơi tay đủ mọi loại ô, giải bằng từng thuật toán trong một tiến trình riêng (giao diện không đơ, có Hủy và giới hạn 60 giây), khối tự lăn theo lời giải, và nút So sánh chạy cả năm cấu hình trên cùng một màn.
- **Thực nghiệm** trên 47 màn (33 màn gốc chia 5 nhóm độ khó, 14 màn tự sinh) × 5 cấu hình (chương 5). Số liệu tái lập được: hai lần đo trên cùng commit cho số đếm trùng nhau ở 235/235 cặp. Các kết luận chính:
  - DFS mở rộng ít nút nhất và nhanh nhất ở 26/33 màn, nhưng lời giải dài và không tối ưu.
  - BFS nhanh nhất trong các thuật toán cho số bước tối ưu (tính trên tổng 33 màn: 898 ms, so với 1 131 ms của A* với $h_P$ và 1 163 ms của UCS).
  - UCS bảo đảm tổng chi phí nhỏ nhất, với giá mở rộng nhiều hơn BFS 5,4 % số nút và chậm hơn khoảng 30 %.
  - A* với $h_P$ cho cùng tổng chi phí với UCS, mở rộng ít hơn UCS 7,3 % số nút, và là cấu hình duy nhất kết luận màn không có lời giải mà không mở rộng nút nào.

### 6.2. Hạn chế

- 33 màn gốc nhỏ (bàn 10 × 15), nên khác biệt về thời gian giữa các thuật toán chỉ vài mili-giây mỗi màn. Thời gian và bộ nhớ đo trên một máy, bộ nhớ đo bằng `tracemalloc` nên chỉ tính phần Python cấp phát.
- Hai heuristic đếm cận dưới của số bước và coi mọi cầu là mở. Khi mỗi bước tốn từ 1,10 trở lên, chúng cách xa chi phí thật: A* chỉ bớt 7,3 % số nút so với UCS trên 33 màn gốc, và gần như không bớt được nút nào trên sân trống lớn.
- Kết quả của DFS phụ thuộc thứ tự hành động U, D, L, R; nhóm chưa đo DFS với các thứ tự khác.
- Bố cục bộ màn S2 có lời giải không đi qua cầu, nên thực nghiệm không đo được mức tăng $2^k$ của không gian trạng thái theo số công tắc.
- Hàm chi phí được xây dựng từ lập luận vật lý, chưa được hiệu chỉnh bằng dữ liệu chơi thật.
- Giao diện chỉ mở được 33 màn gốc, chưa chỉnh được tốc độ khối tự lăn và chưa lưu tiến độ chơi ra file.

### 6.3. Hướng phát triển

- **Heuristic mạnh hơn mà vẫn chấp nhận được:** nhân heuristic với chi phí bước nhỏ nhất 1,10 (vẫn nhất quán, mục 5.4.4); tính trước khoảng cách theo cả ô và tư thế khối trên bàn bỏ qua cầu; hoặc lấy giá trị lớn nhất của nhiều heuristic chấp nhận được.
- **Giảm bộ nhớ trên bàn lớn:** thử IDA* hoặc tìm kiếm hai chiều.
- **Bộ màn khó hơn:** sinh màn có lời giải buộc phải đi qua nhiều cầu và công tắc, để đo đúng ảnh hưởng của cấu hình cầu lên không gian trạng thái.
- **Hiệu chỉnh hàm chi phí bằng dữ liệu:** ghi thời gian người chơi thực hiện từng loại bước, rồi dùng hồi quy tuyến tính đơn giản để ước lượng các mức chi phí, thay cho các mức suy từ công nâng trọng tâm.
- **Giao diện:** mở các màn tự sinh, chỉnh tốc độ tự lăn, lưu tiến độ chơi.
