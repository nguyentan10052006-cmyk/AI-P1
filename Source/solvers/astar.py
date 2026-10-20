"""A* Search - TV4 cài đặt (docs/01 NV8).

- Ưu tiên theo f = g + h; khi f bằng nhau, ưu tiên h nhỏ hơn (gần đích hơn), rồi tới thứ tự đưa vào.
- Hàng đợi ưu tiên heapq, giữ best_g; mục lấy ra có g lớn hơn best_g thì bỏ qua (lazy deletion).
- Kiểm tra đích khi LẤY RA khỏi hàng đợi, để lời giải tối ưu khi h chấp nhận được.
- Heuristic dựng trong prepare() (solvers/heuristics.py), không dựng trong search().
- Hai biến thể dùng chung code, chỉ khác self.heuristic (docs/07 §9, điểm mở #2):
    'astar'   -> AStar,  heuristic = "pattern"   (h_P, heuristic chính)
    'astar_m' -> AStarM, heuristic = "manhattan" (h_M, để so sánh)
- Đếm theo docs/04 mục 3:
    expanded     +1 khi lấy một trạng thái ra để sinh con (mục cũ bị bỏ qua thì không tính)
    generated    +1 cho mỗi trạng thái con hợp lệ (result() khác None), trước khi so với best_g
    max_frontier len(heap) lớn nhất sau mỗi lần đưa vào; tính cả mục cũ do lazy deletion
    visited      số trạng thái khác nhau đã gặp (số khóa của best_g)
- Trạng thái có h = vô cùng (không tới được đích) thì không đưa vào hàng đợi.
"""
from __future__ import annotations

import heapq
import itertools
import math
from typing import Dict, List, Optional, Tuple

from bloxorz.problem import Problem
from bloxorz.state import Action

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver
from .heuristics import Heuristic, make_heuristic


class AStar(Solver):
    name = "A* (h_P)"
    heuristic = "pattern"  # h_P: khoảng cách trên lưới điểm, dựng bảng trong prepare()

    def __init__(self) -> None:
        self.h: Optional[Heuristic] = None

    def prepare(self, problem: Problem) -> None:
        self.h = make_heuristic(problem, self.heuristic)

    def search(self, problem: Problem) -> SearchResult:
        h = self.h if self.h is not None else make_heuristic(problem, self.heuristic)
        start = problem.initial_state()
        h0 = h(start)
        if h0 == math.inf:
            return SearchResult(NO_SOLUTION, expanded=0, generated=0, max_frontier=0, visited=1)

        order = itertools.count()  # phá hòa cuối cùng, để heapq không phải so sánh hai trạng thái
        # Mục: (f, h, thứ_tự, g, trạng_thái)
        frontier: List[Tuple[float, float, int, float, object]] = [(h0, h0, next(order), 0, start)]
        best_g: Dict[object, float] = {start: 0}
        parent: Dict[object, Tuple[object, Action]] = {}
        expanded = generated = 0
        max_frontier = 1

        while frontier:
            _, _, _, g, state = heapq.heappop(frontier)
            if g > best_g[state]:
                continue  # mục cũ: trạng thái này đã được đưa vào lại với g nhỏ hơn
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
                child_h = h(child)
                best_g[child] = child_g
                if child_h == math.inf:
                    continue  # ngõ cụt: đã ghi nhận là đã gặp, nhưng không cần mở rộng
                parent[child] = (state, action)
                heapq.heappush(frontier, (child_g + child_h, child_h, next(order), child_g, child))
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


class AStarM(AStar):
    """A* với h_M (Manhattan có tính đường tắt qua công tắc tách). Phải là lớp ở mức module
    để tiến trình con (multiprocessing kiểu spawn) import lại được."""

    name = "A* (h_M)"
    heuristic = "manhattan"
