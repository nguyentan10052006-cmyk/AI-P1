"""GridMaze: mê cung lưới nhỏ, cùng giao diện với Problem, để thử thuật toán trước khi chạy Bloxorz.

Một ô đi lên, xuống, trái, phải; không lật khối, không cầu, không tách khối.
Trạng thái là tuple (hàng, cột). Hành động là Action(Dir) như Bloxorz, cùng thứ tự U, D, L, R.

Ký hiệu trong lưới:
    #      tường
    .      ô trống, đi vào tốn 1
    S, G   xuất phát, đích (đi vào tốn 1)
    1..9   ô trống, đi vào tốn đúng chữ số đó (để UCS và A* có chi phí khác nhau)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .state import DELTA, Action, Cell, Dir

WALL = "#"
START = "S"
GOAL = "G"
_OPEN = {".", START, GOAL, *"123456789"}


class GridMaze:
    def __init__(self, grid: List[str]) -> None:
        if not grid or any(len(row) != len(grid[0]) for row in grid):
            raise ValueError("mọi hàng của mê cung phải có cùng độ dài")
        self.grid: Tuple[str, ...] = tuple(grid)
        starts, goals = [], []
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                if ch != WALL and ch not in _OPEN:
                    raise ValueError(f"ký tự lạ {ch!r} tại ô {(r, c)}")
                if ch == START:
                    starts.append((r, c))
                elif ch == GOAL:
                    goals.append((r, c))
        if len(starts) != 1 or len(goals) != 1:
            raise ValueError("mê cung cần đúng 1 ô 'S' và đúng 1 ô 'G'")
        self._start: Cell = starts[0]
        self._goal: Cell = goals[0]

    @property
    def goal(self) -> Cell:
        return self._goal

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    def initial_state(self) -> Cell:
        return self._start

    def actions(self, state: Cell) -> List[Action]:
        """Mọi hướng có thể thử, giống Problem: hướng đâm vào tường thì result() trả None."""
        return [Action(d) for d in Dir]

    def result(self, state: Cell, action: Action) -> Optional[Cell]:
        dr, dc = DELTA[action.dir]
        r, c = state[0] + dr, state[1] + dc
        if not (0 <= r < self.rows and 0 <= c < self.cols) or self.grid[r][c] == WALL:
            return None
        return (r, c)

    def is_goal(self, state: Cell) -> bool:
        return state == self._goal

    def step_cost(self, state: Cell, action: Action, next_state: Cell) -> float:
        ch = self.grid[next_state[0]][next_state[1]]
        return int(ch) if ch.isdigit() else 1


@dataclass(frozen=True)
class MazeCase:
    """Một mê cung mẫu kèm đáp án đúng, để tự kiểm tra solver."""

    grid: Tuple[str, ...]
    steps: Optional[int]   # số bước ít nhất (BFS phải ra đúng số này); None nếu không có lời giải
    cost: Optional[float]  # tổng chi phí nhỏ nhất (UCS, A* phải ra đúng số này)
    note: str

    def problem(self) -> GridMaze:
        return GridMaze(list(self.grid))


MAZES: Dict[str, MazeCase] = {
    "open": MazeCase(
        ("S....",
         ".....",
         ".....",
         "....G"),
        steps=7, cost=7,
        note="Sân trống: mọi đường ngắn nhất đều dài 7.",
    ),
    "walls": MazeCase(
        ("S...#.....",
         ".##.#.###.",
         ".#..#...#.",
         ".#.####.#.",
         ".#......#G",
         ".########.",
         ".........."),
        steps=17, cost=17,
        note="Mê cung có nhiều nhánh và ngõ cụt: DFS có thể ra đường dài hơn BFS.",
    ),
    "weighted": MazeCase(
        ("S99999G",
         ".#####.",
         "......."),
        steps=6, cost=10,
        note="Đường ngắn nhất (6 bước) đi qua năm ô 9, tốn 46; đường vòng 10 bước tốn 10. UCS phải chọn đường vòng.",
    ),
    "no_solution": MazeCase(
        ("S..#...",
         "...#.G.",
         "...#..."),
        steps=None, cost=None,
        note="Tường chắn kín: phải trả về NO_SOLUTION.",
    ),
}
