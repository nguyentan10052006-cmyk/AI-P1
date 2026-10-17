"""A* Search - SINH VIÊN TỰ CÀI ĐẶT.

Gợi ý:
- Hàm đánh giá f(n) = g(n) + h(n), với g là chi phí thật từ đầu, h là heuristic.
- Heuristic gợi ý: khoảng cách Manhattan từ khối tới goal chia 2 (một lần lăn đi tối đa 2 ô),
  hoặc cộng thêm phạt nếu khối chưa đứng (cần thêm một lần lăn để đứng lên goal).
- Heuristic phải chấp nhận được (không ước lượng quá chi phí thật) theo chi phí bạn đã chọn.
  Hãy chứng minh điều này trong báo cáo.
- Dùng problem.goal để lấy ô đích.

Trả về SearchResult(actions=[...], expanded=n), hoặc actions=None nếu không có lời giải.
"""
from bloxorz.problem import Problem

from .base import SearchResult


def astar(problem: Problem) -> SearchResult:
    raise NotImplementedError("A* chưa được cài đặt (solvers/astar.py)")
