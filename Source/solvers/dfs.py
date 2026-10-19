"""DFS (Depth-First Search) hoặc IDS - TV2 cài đặt (docs/01 NV6).

Gợi ý:
- DFS dạng graph search: cần tập đã thăm (visited) để không lặp vô hạn trong chu trình.
- Dùng ngăn xếp tường minh (list), không dùng đệ quy.
- Có thể cài IDS (Iterative Deepening) thay cho DFS thuần. Nếu chọn IDS thì ghi rõ trong báo cáo.
- Thứ tự hành động là thứ tự problem.actions() trả về (U, D, L, R).
- result() trả None nghĩa là hành động làm khối rơi: bỏ qua, không tính vào generated.
- Đếm expanded, generated, max_frontier, visited theo docs/04 mục 3.
- Thử trước trên bloxorz.maze.GridMaze, rồi mới chạy trên màn Bloxorz.

Trả về SearchResult(SOLVED, path=[...], ...) hoặc SearchResult(NO_SOLUTION, ...).
"""
from bloxorz.problem import Problem

from .base import SearchResult, Solver


class DFS(Solver):
    name = "DFS"

    def search(self, problem: Problem) -> SearchResult:
        raise NotImplementedError("DFS chưa cài đặt (xem solvers/dfs.py)")
