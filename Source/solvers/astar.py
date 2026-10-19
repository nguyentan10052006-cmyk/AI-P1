"""A* Search - TV4 cài đặt (docs/01 NV8).

Gợi ý:
- Cài giống UCS nhưng ưu tiên theo f = g + h; khi f bằng nhau, ưu tiên h nhỏ hơn.
- Bảng heuristic (ví dụ h_P) dựng trong prepare(), không dựng trong search().
- Heuristic phải chấp nhận được và nhất quán theo hàm chi phí đã chốt, và phải tính
  đường tắt qua công tắc tách (docs/01 NV8 bước 3). Chứng minh trong báo cáo.
- Dùng problem.goal để lấy ô đích.
- result() trả None nghĩa là hành động làm khối rơi: bỏ qua, không tính vào generated.
- Đếm expanded, generated, max_frontier, visited theo docs/04 mục 3.
- Thử trước trên bloxorz.maze.GridMaze, rồi mới chạy trên màn Bloxorz.

Trả về SearchResult(SOLVED, path=[...], path_cost=..., ...) hoặc SearchResult(NO_SOLUTION, ...).
"""
from bloxorz.problem import Problem

from .base import SearchResult, Solver


class AStar(Solver):
    name = "A*"

    def prepare(self, problem: Problem) -> None:
        """Dựng bảng heuristic tại đây (nếu cần)."""

    def search(self, problem: Problem) -> SearchResult:
        raise NotImplementedError("A* chưa cài đặt (xem solvers/astar.py)")
