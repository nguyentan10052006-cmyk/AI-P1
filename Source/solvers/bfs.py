"""BFS (Breadth-First Search) - TV1 (docs/01 NV5).

Thuật toán theo Russell và Norvig, Artificial Intelligence: A Modern Approach (4th ed., 2020),
mục 3.4.1 (nguồn #7 ở tab cite).

Các lựa chọn cài đặt (ghi vào báo cáo, chương 3.1):
- Hàng đợi FIFO collections.deque: popleft() và append() đều tốn O(1).
- Graph search: tập đã thăm `visited` chặn trạng thái lặp, nên luôn dừng trên không gian hữu hạn.
- Đánh dấu đã thăm khi ĐƯA VÀO hàng đợi, nên một trạng thái không bao giờ nằm trong hàng đợi hai lần.
- Kiểm tra đích khi SINH nút (early goal test, docs/04 mục 3). Vẫn cho số bước ít nhất, vì hàng
  đợi FIFO sinh mọi nút ở độ sâu d trước mọi nút ở độ sâu d + 1.

Đếm chỉ số theo docs/04 mục 3: expanded khi lấy một trạng thái ra để sinh con; generated cho mỗi
con hợp lệ (result() khác None), đếm trước khi xét visited; max_frontier sau mỗi lần thêm vào hàng
đợi; visited là số trạng thái khác nhau đã gặp (kích thước tập đã thăm, tính cả trạng thái đầu).
"""
from collections import deque
from typing import Deque, Dict, Hashable, List, Optional, Tuple

from bloxorz.problem import Problem
from bloxorz.state import Action

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver

# trạng thái con -> (trạng thái cha, hành động đi từ cha tới con); trạng thái đầu có cha là None
Parent = Dict[Hashable, Tuple[Optional[Hashable], Optional[Action]]]


class BFS(Solver):
    name = "BFS"

    def search(self, problem: Problem) -> SearchResult:
        start = problem.initial_state()
        if problem.is_goal(start):
            return SearchResult(SOLVED, [], 0.0, expanded=0, generated=0, max_frontier=1, visited=1)

        frontier: Deque[Hashable] = deque([start])
        visited = {start}
        parent: Parent = {start: (None, None)}
        expanded = 0
        generated = 0
        max_frontier = 1

        while frontier:
            state = frontier.popleft()
            expanded += 1
            for action in problem.actions(state):
                child = problem.result(state, action)
                if child is None:  # khối rơi (hoặc đâm tường trong GridMaze): không phải nút
                    continue
                generated += 1
                if child in visited:
                    continue
                visited.add(child)
                parent[child] = (state, action)
                if problem.is_goal(child):
                    path, cost = _build_path(problem, parent, child)
                    return SearchResult(SOLVED, path, cost, expanded, generated, max_frontier, len(visited))
                frontier.append(child)
                max_frontier = max(max_frontier, len(frontier))

        return SearchResult(NO_SOLUTION, [], 0.0, expanded, generated, max_frontier, len(visited))


def _build_path(problem: Problem, parent: Parent, goal: Hashable) -> Tuple[List[Action], float]:
    """Lần ngược bảng cha từ đích về trạng thái đầu, rồi đảo lại; cộng step_cost dọc đường."""
    path: List[Action] = []
    cost = 0.0
    state = goal
    prev, action = parent[state]
    while prev is not None:
        path.append(action)
        cost += problem.step_cost(prev, action, state)
        state = prev
        prev, action = parent[state]
    path.reverse()
    return path, cost
