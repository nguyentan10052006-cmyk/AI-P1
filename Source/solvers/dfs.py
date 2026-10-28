"""DFS (Depth-First Search) dạng tìm kiếm đồ thị - TV2 (docs/01 NV6).

Các lựa chọn cài đặt (ghi vào báo cáo, chương 3.2):
- Graph search: tập đã thăm `visited` chặn trạng thái lặp, nên luôn dừng trên không gian hữu hạn.
- Ngăn xếp tường minh (list), không đệ quy: lời giải DFS có thể dài hơn giới hạn đệ quy của Python.
- Đánh dấu đã thăm khi ĐƯA VÀO ngăn xếp (như BFS), nên một trạng thái không bao giờ nằm trong
  ngăn xếp hai lần và không có mục nào bị bỏ qua khi lấy ra.
- Kiểm tra đích khi SINH nút (docs/04 mục 3).
- Thứ tự hành động: thứ tự problem.actions() trả về (U, D, L, R; khi đã tách U1 … R2).
  Con được đưa vào ngăn xếp theo thứ tự ngược lại, để con sinh từ hành động U được mở rộng trước.
- DFS không bảo đảm lời giải ngắn nhất hay rẻ nhất.

Đếm chỉ số theo docs/04 mục 3: expanded khi lấy một trạng thái ra để sinh con; generated cho mỗi
con hợp lệ (result() khác None), đếm trước khi xét visited; max_frontier sau mỗi lần thêm vào ngăn xếp;
visited là kích thước tập đã thăm lúc kết thúc (tính cả trạng thái đầu).
"""
from typing import Dict, Hashable, List, Optional, Tuple

from bloxorz.problem import Problem
from bloxorz.state import Action

from .base import NO_SOLUTION, SOLVED, SearchResult, Solver


class DFS(Solver):
    name = "DFS"

    def search(self, problem: Problem) -> SearchResult:
        start = problem.initial_state()
        if problem.is_goal(start):
            return SearchResult(SOLVED, [], 0.0, expanded=0, generated=0, max_frontier=1, visited=1)

        stack: List[Hashable] = [start]
        visited = {start}
        parent: Dict[Hashable, Tuple[Optional[Hashable], Optional[Action]]] = {start: (None, None)}
        expanded = generated = 0
        max_frontier = 1

        while stack:
            state = stack.pop()
            expanded += 1
            children = []
            for action in problem.actions(state):
                child = problem.result(state, action)
                if child is None:          # khối rơi (hoặc đâm tường trong GridMaze): không phải nút
                    continue
                generated += 1
                if child in visited:
                    continue
                visited.add(child)
                parent[child] = (state, action)
                if problem.is_goal(child):
                    path, cost = _build_path(problem, parent, child)
                    return SearchResult(SOLVED, path, cost, expanded, generated, max_frontier, len(visited))
                children.append(child)
            for child in reversed(children):
                stack.append(child)
            max_frontier = max(max_frontier, len(stack))

        return SearchResult(NO_SOLUTION, [], 0.0, expanded, generated, max_frontier, len(visited))


def _build_path(problem, parent, goal) -> Tuple[List[Action], float]:
    """Lần ngược bảng cha từ đích về trạng thái đầu; tính luôn tổng chi phí dọc đường."""
    path: List[Action] = []
    cost = 0.0
    state = goal
    while True:
        prev, action = parent[state]
        if prev is None:
            break
        path.append(action)
        cost += problem.step_cost(prev, action, state)
        state = prev
    path.reverse()
    return path, cost
