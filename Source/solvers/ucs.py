"""UCS (Uniform-Cost Search) - TV3 cài đặt (docs/01 NV7).

Thuật toán theo Russell và Norvig, Artificial Intelligence: A Modern Approach (4th ed., 2020),
mục 3.4.2 (nguồn #7 ở tab cite).

Các lựa chọn cài đặt (ghi vào báo cáo, chương 3.3):
- Hàng đợi ưu tiên heapq: lưu (g, thứ_tự, trạng_thái); thứ_tự là bộ đếm tăng dần (itertools.count())
  để Python không bao giờ phải so sánh hai trạng thái khi g bằng nhau.
- Graph search với lazy deletion: lưu bảng best_g[state] là chi phí g nhỏ nhất từng đến state.
  Khi pop một mục có g > best_g[state], bỏ qua (lazy deletion).
- Kiểm tra đích khi LẤY RA khỏi hàng đợi (heappop), không kiểm tra khi sinh nút, để đảm bảo
  lời giải tìm được có tổng chi phí nhỏ nhất (tối ưu).
- Chi phí lấy từ problem.step_cost(state, action, child). Mọi bước có chi phí >= 1.
- result() trả None nghĩa là hành động làm khối rơi (hoặc đâm tường trong GridMaze):
  bỏ qua, không tính vào generated.

Đếm chỉ số theo docs/04 mục 3:
- expanded: +1 khi lấy một trạng thái hợp lệ ra khỏi frontier để chuẩn bị sinh con (mục cũ bị lazy deletion bỏ qua thì không tính).
- generated: +1 cho mỗi trạng thái con hợp lệ (result() khác None), đếm trước khi xét best_g.
- max_frontier: len(heap) lớn nhất sau mỗi lần heappush (tính cả mục cũ do lazy deletion).
- visited: số trạng thái khác nhau đã gặp (số khóa của best_g, tính cả trạng thái đầu).
"""
from __future__ import annotations

import heapq
import itertools
import math
from typing import Dict, List, Tuple

from bloxorz.problem import Problem
from bloxorz.state import Action

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver


class UCS(Solver):
    name = "UCS"

    def search(self, problem: Problem) -> SearchResult:
        start = problem.initial_state()
        order = itertools.count()  # bộ đếm tăng dần để heapq không phải so sánh hai trạng thái

        # Mục trong heap: (g, thứ_tự, trạng_thái)
        frontier: List[Tuple[float, int, object]] = [(0.0, next(order), start)]
        best_g: Dict[object, float] = {start: 0.0}
        parent: Dict[object, Tuple[object, Action]] = {}
        expanded = generated = 0
        max_frontier = 1

        while frontier:
            g, _, state = heapq.heappop(frontier)
            if g > best_g[state]:
                continue  # mục cũ (lazy deletion): đã có đường khác đến state với g nhỏ hơn
            if problem.is_goal(state):
                return SearchResult(SOLVED, _path(parent, state), g, expanded, generated,
                                    max_frontier, len(best_g))
            expanded += 1
            for action in problem.actions(state):
                child = problem.result(state, action)
                if child is None:
                    continue  # khối rơi (hoặc đâm tường trong GridMaze): không phải nút con
                generated += 1
                child_g = g + problem.step_cost(state, action, child)
                if child_g >= best_g.get(child, math.inf):
                    continue
                best_g[child] = child_g
                parent[child] = (state, action)
                heapq.heappush(frontier, (child_g, next(order), child))
                max_frontier = max(max_frontier, len(frontier))

        return SearchResult(NO_SOLUTION, expanded=expanded, generated=generated,
                            max_frontier=max_frontier, visited=len(best_g))


def _path(parent: Dict[object, Tuple[object, Action]], state: object) -> List[Action]:
    """Lần ngược bảng cha từ đích về trạng thái đầu."""
    path: List[Action] = []
    while state in parent:
        state, action = parent[state]
        path.append(action)
    path.reverse()
    return path
