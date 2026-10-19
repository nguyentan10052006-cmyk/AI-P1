"""UCS (Uniform-Cost Search) - TV3 cài đặt (docs/01 NV7).

Gợi ý:
- Hàng đợi ưu tiên: heapq, mục (g, thứ_tự, trạng_thái); thứ_tự là bộ đếm tăng dần.
- Giữ best_g; lấy ra mục có g lớn hơn best_g thì bỏ qua (lazy deletion).
- Kiểm tra đích khi LẤY RA khỏi hàng đợi, để lời giải tối ưu.
- Chi phí lấy từ problem.step_cost(s, a, s2). Hàm chi phí riêng của nhóm cài trong Problem.step_cost;
  mọi bước phải có chi phí >= 1.
- result() trả None nghĩa là hành động làm khối rơi: bỏ qua, không tính vào generated.
- Đếm expanded, generated, max_frontier, visited theo docs/04 mục 3.
- Thử trước trên bloxorz.maze.GridMaze (có ô chi phí khác 1), rồi mới chạy trên màn Bloxorz.

Trả về SearchResult(SOLVED, path=[...], path_cost=..., ...) hoặc SearchResult(NO_SOLUTION, ...).
"""
from bloxorz.problem import Problem

from .base import SearchResult, Solver


class UCS(Solver):
    name = "UCS"

    def search(self, problem: Problem) -> SearchResult:
        raise NotImplementedError("UCS chưa cài đặt (xem solvers/ucs.py)")
