"""Heuristic cho A* (TV4, docs/01 NV8). Mỗi hàm make_* nhận problem, trả về hàm h(state) -> float.

Mọi heuristic ở đây dựa trên một điều kiện của hàm chi phí: mỗi bước tốn ít nhất 1
(docs/01 NV7 bước 4). Khi đó cận dưới của số bước còn lại cũng là cận dưới của chi phí.

    GridMaze  h_M: Manhattan tới đích. Mỗi bước đi 1 ô nên Manhattan giảm tối đa 1.
              h_P: số bước ít nhất tới đích nếu mọi ô tốn 1, tính trước bằng BFS ngược từ đích.
    Bloxorz   h_M: Φ = khoảng cách Manhattan nhỏ nhất từ một ô của khối (hoặc một khối con) tới đích
                   hoặc tới một công tắc tách bất kỳ; h = max(⌈Φ/2⌉, 1) khi chưa ở đích, 0 khi ở đích.
              h_P: Φ tính bằng khoảng cách trên "lưới điểm": coi mọi ô không trống (kể cả cầu đóng, ô dễ vỡ,
                   công tắc) là đi được, thêm cạnh chi phí 0 từ mỗi công tắc tách tới hai ô đáp của nó, rồi
                   tính trước khoảng cách từ mọi ô tới đích bằng 0-1 BFS ngược từ đích trong prepare().
                   h = max(⌈Φ/2⌉, 1) như h_M; ô không tới được đích cho h = vô cùng (ngõ cụt, A* bỏ luôn).
    Cả hai  zero: h = 0, tức A* chạy như UCS; chỉ dùng làm mốc trong tools/check_heuristics.py.

Vì sao chấp nhận được và nhất quán (chi tiết cho chương 3.4): gọi d là khoảng cách (Manhattan với h_M,
lưới điểm với h_P) và Φ(s) = min d(ô) trên các ô của khối. Hai ô kề nhau có d chênh nhau không quá 1, nên
(i) mỗi lần lăn khối nguyên, mọi ô mới cách một ô cũ không quá 2 bước lưới, Φ giảm tối đa 2; khối con
giảm tối đa 1; ghép khối không đổi ô nào. (ii) Dịch chuyển: khối đứng trên công tắc tách X rồi xuất hiện ở
hai ô đáp A, B; vì d(X) <= min(d(A), d(B)) nên Φ sau dịch chuyển không nhỏ hơn d(X) >= Φ trước - 2.
(iii) Ở đích Φ = 0. (iv) Mỗi bước tốn ít nhất 1. Từ (i), (ii): ⌈Φ/2⌉ giảm tối đa 1 mỗi bước, nên
h(s) <= c(s, a, s') + h(s'); từ (iii), (iv) và vì trạng thái chưa phải đích còn ít nhất một bước,
max với 1 vẫn không ước lượng quá.
"""
from __future__ import annotations

import math
from collections import deque
from typing import Callable, Dict, Tuple

from bloxorz.level import VOID
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

def _from_phi(problem: Problem, distance: Callable[[Cell], float]) -> Heuristic:
    """h = 0 ở đích; vô cùng nếu một ô của khối không tới được đích; còn lại max(⌈Φ/2⌉, 1)."""

    def h(state: State) -> float:
        if problem.is_goal(state):
            return 0
        dists = [distance(cell) for cell in state.cells()]
        # Hai khối con nằm ở hai vùng khác nhau thì không bao giờ ghép lại được: cũng là ngõ cụt
        if math.inf in dists:
            return math.inf
        return max(math.ceil(min(dists) / 2), 1)

    return h


def _split_switches(problem: Problem):
    return [sw for sw in problem.level.switches.values() if sw.kind == "split"]


def bloxorz_manhattan(problem: Problem) -> Heuristic:
    """h_M: d = Manhattan nhỏ nhất tới đích hoặc tới một công tắc tách bất kỳ (docs/01 NV8 bước 3)."""
    targets: Tuple[Cell, ...] = (problem.goal,) + tuple(sw.at for sw in _split_switches(problem))
    return _from_phi(problem, lambda cell: min(manhattan(cell, t) for t in targets))


def bloxorz_pattern(problem: Problem) -> Heuristic:
    """h_P: d = khoảng cách trên lưới điểm tới đích, tính trước bằng 0-1 BFS ngược từ đích."""
    dist = pattern_distances(problem)
    return _from_phi(problem, lambda cell: dist.get(cell, math.inf))


def pattern_distances(problem: Problem) -> Dict[Cell, int]:
    """Khoảng cách từ mọi ô không trống tới đích, trên đồ thị: ô kề nhau tốn 1, công tắc tách -> ô đáp tốn 0.

    Chạy ngược từ đích. Cạnh lưới đi được hai chiều nên giữ nguyên; cạnh 0 của công tắc X tới ô đáp A, B
    chạy ngược thành A -> X và B -> X. Khoảng cách chỉ là số nguyên nên dùng 0-1 BFS (deque) thay cho Dijkstra.
    """
    level = problem.level
    lands_from: Dict[Cell, list] = {}
    for sw in _split_switches(problem):
        for target in sw.targets:
            lands_from.setdefault(target, []).append(sw.at)

    dist: Dict[Cell, int] = {problem.goal: 0}
    queue = deque([problem.goal])
    while queue:
        cell = queue.popleft()
        d = dist[cell]
        for switch_cell in lands_from.get(cell, ()):
            if d < dist.get(switch_cell, math.inf):
                dist[switch_cell] = d
                queue.appendleft(switch_cell)  # cạnh 0: xét trước các ô cùng khoảng cách
        for dr, dc in DELTA.values():
            nxt = (cell[0] + dr, cell[1] + dc)
            if level.tile(nxt) != VOID and d + 1 < dist.get(nxt, math.inf):
                dist[nxt] = d + 1
                queue.append(nxt)
    return dist


def zero(problem) -> Heuristic:
    return lambda state: 0


_TABLE: Dict[Tuple[type, str], Callable[[object], Heuristic]] = {
    (GridMaze, "manhattan"): maze_manhattan,
    (GridMaze, "pattern"): maze_pattern,
    (Problem, "manhattan"): bloxorz_manhattan,
    (Problem, "pattern"): bloxorz_pattern,
    (object, "zero"): zero,
}


def make_heuristic(problem, kind: str) -> Heuristic:
    """Chọn heuristic theo loại bài toán (GridMaze hay Bloxorz) và loại heuristic ('manhattan' | 'pattern' | 'zero')."""
    for (cls, name), factory in _TABLE.items():
        if name == kind and isinstance(problem, cls):
            return factory(problem)
    raise ValueError(f"không có heuristic {kind!r} cho {type(problem).__name__}")
