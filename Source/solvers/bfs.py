"""BFS (Breadth-First Search) - TV1 cài đặt (docs/01 NV5).

Gợi ý:
- Hàng đợi: collections.deque, lấy ra bằng popleft().
- Tập đã thăm: set các State (State là hashable, đã có sẵn). Đánh dấu khi đưa vào hàng đợi.
- Truy vết lời giải: lưu parent[state] = (state_cha, action), rồi lần ngược từ đích.
- Kiểm tra đích khi sinh nút (early goal test).
- result() trả None nghĩa là hành động làm khối rơi: bỏ qua, không tính vào generated.
- Đếm expanded, generated, max_frontier, visited theo docs/04 mục 3.
- Thử trước trên bloxorz.maze.GridMaze, rồi mới chạy trên màn Bloxorz.

Trả về SearchResult(SOLVED, path=[...], ...) hoặc SearchResult(NO_SOLUTION, ...).
"""
from bloxorz.problem import Problem

from .base import SearchResult, Solver


class BFS(Solver):
    name = "BFS"

    def search(self, problem: Problem) -> SearchResult:
        # raise NotImplementedError("Chưa cài đặt (xem solvers/bfs.py)")
        state = problem.initial_state()
        deque = [state]
        visited = {state}
        parent = {state: (None, None)}
        expanded = 0
        # while deque:
        raise NotImplementedError("BFS chưa cài đặt (xem solvers/bfs.py)")
