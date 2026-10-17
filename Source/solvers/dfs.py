"""DFS (Depth-First Search) hoặc IDS - SINH VIÊN TỰ CÀI ĐẶT.

Gợi ý:
- DFS cần tập đã thăm (visited) để không lặp vô hạn trong chu trình.
- Có thể cài IDS (Iterative Deepening) thay cho DFS thuần. Nếu chọn IDS thì ghi rõ trong báo cáo.
- Dùng problem.actions(), problem.result(), problem.is_goal().

Trả về SearchResult(actions=[...], expanded=n), hoặc actions=None nếu không có lời giải.
"""
from bloxorz.problem import Problem

from .base import SearchResult


def dfs(problem: Problem) -> SearchResult:
    raise NotImplementedError("Chưa cài đặt (xem solvers/dfs.py)")
