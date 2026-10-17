"""UCS (Uniform-Cost Search) - SINH VIÊN TỰ CÀI ĐẶT.

Gợi ý:
- Hàng đợi ưu tiên: heapq, với khóa là chi phí tích lũy g(n).
- Chi phí mặc định của mỗi bước là 1 (xem Problem.step_cost). Nếu chỉ dùng chi phí 1 thì UCS = BFS.
  Muốn chi phí khác 1, override step_cost trong problem.py hoặc tự tính trong solver,
  và giải thích thiết kế đó trong báo cáo.
- Chi phí phải luôn dương để UCS đúng.

Trả về SearchResult(actions=[...], expanded=n), hoặc actions=None nếu không có lời giải.
"""
from bloxorz.problem import Problem

from .base import SearchResult


def ucs(problem: Problem) -> SearchResult:
    raise NotImplementedError("Chưa cài đặt (xem solvers/ucs.py)")
