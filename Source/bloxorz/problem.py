"""Giao diện bài toán tìm kiếm mà các solver (BFS, DFS, UCS, A*) dùng."""
from __future__ import annotations

from typing import List, Optional

from .level import Level
from .rules import FELL, step
from .state import Action, Cell, Dir, Orient, State


class Problem:
    def __init__(self, level: Level, start: Optional[State] = None) -> None:
        self.level = level
        self._start = start if start is not None else level.initial_state()

    @property
    def goal(self) -> Cell:
        return self.level.goal

    def initial_state(self) -> State:
        return self._start

    def actions(self, state: State) -> List[Action]:
        """Mọi lệnh có thể thử ở state. Lệnh có thể làm khối rơi, result() sẽ trả None."""
        if state.orient is Orient.SPLIT:
            return [Action(d, cube) for cube in (0, 1) for d in Dir]
        return [Action(d) for d in Dir]

    def result(self, state: State, action: Action) -> Optional[State]:
        """Trạng thái kế tiếp, hoặc None nếu lệnh làm khối rơi."""
        outcome = step(self.level, state, action)
        return None if outcome.status == FELL else outcome.state

    def is_goal(self, state: State) -> bool:
        return state.orient is Orient.STANDING and state.pos == self.level.goal

    def step_cost(self, state: State, action: Action, next_state: State) -> float:
        """Chi phí của một bước. Mặc định là 1 (đếm số nước đi)."""
        return 1
