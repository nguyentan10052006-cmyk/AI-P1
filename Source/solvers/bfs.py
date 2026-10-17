"""BFS (Breadth-First Search) - SINH VIÊN TỰ CÀI ĐẶT.

Gợi ý:
- Hàng đợi: collections.deque, lấy ra bằng popleft().
- Tập đã thăm: set các State (State là hashable, đã có sẵn).
- Truy vết lời giải: lưu parent[state] = (state_cha, action), rồi lần ngược từ đích.
- expanded: số state được lấy ra khỏi hàng đợi để mở rộng.
- Dùng problem.actions(), problem.result(), problem.is_goal().

Trả về SearchResult(actions=[...], expanded=n), hoặc actions=None nếu không có lời giải.
"""
from bloxorz.problem import Problem

from .base import SearchResult


def bfs(problem: Problem) -> SearchResult:
    raise NotImplementedError("BFS chưa được cài đặt (solvers/bfs.py)")
