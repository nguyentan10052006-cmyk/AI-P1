"""Heuristic cho A* (TV4, docs/01 NV8). Mỗi hàm make_* nhận problem, trả về hàm h(state) -> float.

Mọi heuristic ở đây dựa trên một điều kiện của hàm chi phí: mỗi bước tốn ít nhất 1
(docs/01 NV7 bước 4). Khi đó cận dưới của số bước còn lại cũng là cận dưới của chi phí.

    GridMaze  h_M: Manhattan tới đích. Mỗi bước đi 1 ô nên Manhattan giảm tối đa 1.
              h_P: số bước ít nhất tới đích nếu mọi ô tốn 1, tính trước bằng BFS ngược từ đích.
    Bloxorz   h_M: Φ = khoảng cách Manhattan nhỏ nhất từ một ô của khối (hoặc một khối con) tới đích
                   hoặc tới một công tắc tách bất kỳ; h = max(⌈Φ/2⌉, 1) khi chưa ở đích, 0 khi ở đích.
              h_P: chưa cài (V16, hạn 24/10).
"""
from __future__ import annotations

import math
from collections import deque
from typing import Callable, Dict, Tuple

from bloxorz.maze import GridMaze
from bloxorz.problem import Problem
from bloxorz.state import DELTA, Cell, State

Heuristic = Callable[[object], float]


def manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------------------------------------------------------------- GridMaze

def maze_manhattan(problem: GridMaze) -> Heuristic:
    goal = problem.goal
    return lambda cell: manhattan(cell, goal)


def maze_pattern(problem: GridMaze) -> Heuristic:
    """Khoảng cách theo số bước (bỏ qua chi phí ô) từ mọi ô tới đích; ô không tới được đích là vô cùng."""
    dist: Dict[Cell, int] = {problem.goal: 0}
    queue = deque([problem.goal])
    while queue:
        cell = queue.popleft()
        for dr, dc in DELTA.values():
            nxt = (cell[0] + dr, cell[1] + dc)
            # Đi được hai chiều như nhau nên BFS từ đích cho đúng khoảng cách tới đích
            if nxt not in dist and _maze_open(problem, nxt):
                dist[nxt] = dist[cell] + 1
                queue.append(nxt)
    return lambda cell: dist.get(cell, math.inf)


def _maze_open(problem: GridMaze, cell: Cell) -> bool:
    r, c = cell
    return 0 <= r < problem.rows and 0 <= c < problem.cols and problem.grid[r][c] != "#"


# ---------------------------------------------------------------- Bloxorz

def bloxorz_manhattan(problem: Problem) -> Heuristic:
    """h_M có tính đường tắt qua công tắc tách (docs/01 NV8 bước 3).

    Chấp nhận được: mỗi lần lăn, khối nguyên làm Φ giảm tối đa 2, khối con tối đa 1; dịch chuyển
    tới ô đáp chỉ xảy ra khi khối đứng trên công tắc tách, lúc đó Φ = 0. Ở mọi trạng thái chưa
    phải đích, còn ít nhất một bước tốn ít nhất 1, nên lấy max với 1 vẫn không ước lượng quá.
    """
    targets: Tuple[Cell, ...] = (problem.goal,) + tuple(
        sw.at for sw in problem.level.switches.values() if sw.kind == "split")

    def h(state: State) -> float:
        if problem.is_goal(state):
            return 0
        phi = min(manhattan(cell, t) for cell in state.cells() for t in targets)
        return max(math.ceil(phi / 2), 1)

    return h


def bloxorz_pattern(problem: Problem) -> Heuristic:
    raise NotImplementedError("h_P cho Bloxorz chưa cài (V16, hạn 24/10); tạm dùng 'astar_m' (h_M)")


_TABLE: Dict[Tuple[type, str], Callable[[object], Heuristic]] = {
    (GridMaze, "manhattan"): maze_manhattan,
    (GridMaze, "pattern"): maze_pattern,
    (Problem, "manhattan"): bloxorz_manhattan,
    (Problem, "pattern"): bloxorz_pattern,
}


def make_heuristic(problem, kind: str) -> Heuristic:
    """Chọn heuristic theo loại bài toán (GridMaze hay Bloxorz) và loại heuristic ('manhattan' | 'pattern')."""
    for (cls, name), factory in _TABLE.items():
        if name == kind and isinstance(problem, cls):
            return factory(problem)
    raise ValueError(f"không có heuristic {kind!r} cho {type(problem).__name__}")
