"""Luật chơi: một lần lăn cho ra trạng thái mới, kèm sự kiện để GUI vẽ hiệu ứng."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .level import BRIDGE_CHARS, FRAGILE, VOID, Level, Switch
from .state import Action, Cell, DELTA, Dir, Orient, State, split_state

OK = "ok"      # đi tiếp bình thường
FELL = "fell"  # khối rơi: lệnh bị coi là thua
WON = "won"    # khối đứng trên lỗ đích

# (tư thế cũ, hướng lăn) -> (tư thế mới, độ lệch của ô neo mới so với ô neo cũ)
# Ví dụ: khối đứng tại (r, c) lăn lên thì nằm dọc với ô neo mới (r-2, c).
BLOCK_MOVES: Dict[Tuple[Orient, Dir], Tuple[Orient, Cell]] = {
    (Orient.STANDING, Dir.UP): (Orient.VERTICAL, (-2, 0)),
    (Orient.STANDING, Dir.DOWN): (Orient.VERTICAL, (1, 0)),
    (Orient.STANDING, Dir.LEFT): (Orient.HORIZONTAL, (0, -2)),
    (Orient.STANDING, Dir.RIGHT): (Orient.HORIZONTAL, (0, 1)),
    (Orient.HORIZONTAL, Dir.UP): (Orient.HORIZONTAL, (-1, 0)),
    (Orient.HORIZONTAL, Dir.DOWN): (Orient.HORIZONTAL, (1, 0)),
    (Orient.HORIZONTAL, Dir.LEFT): (Orient.STANDING, (0, -1)),
    (Orient.HORIZONTAL, Dir.RIGHT): (Orient.STANDING, (0, 2)),
    (Orient.VERTICAL, Dir.UP): (Orient.STANDING, (-1, 0)),
    (Orient.VERTICAL, Dir.DOWN): (Orient.STANDING, (2, 0)),
    (Orient.VERTICAL, Dir.LEFT): (Orient.VERTICAL, (0, -1)),
    (Orient.VERTICAL, Dir.RIGHT): (Orient.VERTICAL, (0, 1)),
}


@dataclass(frozen=True)
class StepResult:
    state: State          # trạng thái cuối cùng sau khi xử lý xong
    status: str           # OK | FELL | WON
    events: List[dict]    # sự kiện để GUI hiển thị (công tắc, vỡ ô, tách, ghép, rơi, thắng)
    moved: State          # vị trí ngay sau khi lăn, trước khi kích hoạt công tắc hoặc ghép


def step(level: Level, state: State, action: Action) -> StepResult:
    """Áp dụng một lệnh lăn. Không thay đổi state đầu vào."""
    if state.orient is Orient.SPLIT:
        if action.cube not in (0, 1):
            raise ValueError("khi đã tách, lệnh phải chỉ rõ khối con: cube = 0 hoặc 1")
        cells = list(state.cells())
        dr, dc = DELTA[action.dir]
        r, c = cells[action.cube]
        cells[action.cube] = (r + dr, c + dc)
        moved = split_state(cells[0], cells[1], state.open_bridges)
        pressed: Tuple[Cell, ...] = (cells[action.cube],)
    else:
        if action.cube is not None:
            raise ValueError("khối chưa tách không có khối con để chọn")
        orient, (dr, dc) = BLOCK_MOVES[(state.orient, action.dir)]
        r, c = state.pos
        moved = State(orient, (r + dr, c + dc), None, state.open_bridges)
        pressed = moved.cells()
    return _settle(level, moved, pressed)


def _settle(level: Level, moved: State, pressed: Tuple[Cell, ...]) -> StepResult:
    """Xử lý phần sau khi lăn: rơi, công tắc, ghép khối, thắng."""
    events: List[dict] = []
    state = moved

    reason = _fall_reason(level, state)
    if reason is None:
        state = _activate(level, state, pressed, events)
        reason = _fall_reason(level, state)
    if reason is not None:
        kind, cell = reason
        if kind == "fragile":
            events.append({"type": "fragile_broken", "at": cell})
        events.append({"type": "fell", "reason": kind, "at": cell})
        return StepResult(state, FELL, events, moved)

    if state.orient is Orient.SPLIT:
        state = _merge(state, events)

    if state.orient is Orient.STANDING and state.pos == level.goal:
        events.append({"type": "won"})
        return StepResult(state, WON, events, moved)
    return StepResult(state, OK, events, moved)


def _fall_reason(level: Level, state: State) -> Optional[Tuple[str, Cell]]:
    """Lý do khối rơi, hoặc None nếu khối được đỡ đầy đủ."""
    for cell in state.cells():
        problem = _support_problem(level, state.open_bridges, cell)
        if problem is not None:
            return problem, cell
    # Luật ô giòn của đề chỉ áp dụng cho khối 1×1×2 ("the block"): khối đứng thì ô vỡ và khối rơi.
    # Khối con 1×1×1 không bị áp dụng luật này (xem README, mục "Luật chơi và các giả định").
    if state.orient is Orient.STANDING and level.tile(state.pos) == FRAGILE:
        return "fragile", state.pos
    return None


def _support_problem(level: Level, open_bridges, cell: Cell) -> Optional[str]:
    r, c = cell
    if not (0 <= r < level.rows and 0 <= c < level.cols):
        return "off_board"
    ch = level.grid[r][c]
    if ch == VOID:
        return "void"
    if ch in BRIDGE_CHARS and cell not in open_bridges:
        return "bridge_closed"
    return None


def _activate(level: Level, state: State, pressed: Tuple[Cell, ...], events: List[dict]) -> State:
    for cell in pressed:
        switch = level.switches.get(cell)
        if switch is None:
            continue
        standing_here = state.orient is Orient.STANDING and state.pos == cell
        # Công tắc mềm: mọi tư thế, kể cả khối con. Hai loại còn lại: chỉ khi khối đứng.
        if switch.kind != "soft" and not standing_here:
            continue
        if switch.kind == "split":
            # Công tắc tách có thể nối cầu (tùy chọn): cầu đổi trước, rồi khối mới được dịch chuyển.
            if switch.bridges:
                state = _apply_switch(state, switch, events)
            a, b = switch.targets
            state = split_state(a, b, state.open_bridges)
            events.append({"type": "split", "from": cell, "targets": [a, b]})
        else:
            state = _apply_switch(state, switch, events)
    return state


def _apply_switch(state: State, switch: Switch, events: List[dict]) -> State:
    new_open = set(state.open_bridges)
    if switch.links:
        for link in switch.links:
            if link.effect == "toggle":
                new_open.symmetric_difference_update({link.cell})
            elif link.effect == "open":
                new_open.add(link.cell)
            elif link.effect == "close":
                new_open.discard(link.cell)
    else:
        targets = set(switch.bridges)
        if switch.effect == "toggle":
            new_open ^= targets
        elif switch.effect == "open":
            new_open |= targets
        elif switch.effect == "close":
            new_open -= targets
    events.append({"type": "switch", "at": switch.at, "kind": switch.kind, "effect": switch.effect})
    return State(state.orient, state.pos, state.pos2, frozenset(new_open))


def _merge(state: State, events: List[dict]) -> State:
    """Hai khối con kề nhau (chung cạnh) thì ghép lại thành khối nằm."""
    (r1, c1), (r2, c2) = state.pos, state.pos2
    if abs(r1 - r2) + abs(c1 - c2) != 1:
        return state
    events.append({"type": "merge"})
    if r1 == r2:
        return State(Orient.HORIZONTAL, (r1, min(c1, c2)), None, state.open_bridges)
    return State(Orient.VERTICAL, (min(r1, r2), c1), None, state.open_bridges)
