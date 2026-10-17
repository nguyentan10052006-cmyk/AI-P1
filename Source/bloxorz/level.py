"""Đọc và kiểm tra màn chơi từ file JSON."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

from .state import Cell, Orient, State, to_cell

# Mỗi ký tự trong lưới là một ô.
VOID = "."           # khoảng trống: không có ô, rơi xuống là thua
FLOOR = "#"          # ô nền thường
START = "S"          # vị trí xuất phát (khối đứng)
GOAL = "G"           # lỗ đích
FRAGILE = "F"        # ô giòn: chỉ đỡ khối nằm, khối đứng làm vỡ ô
BRIDGE_CLOSED = "b"  # cầu đang đóng lúc đầu
BRIDGE_OPEN = "B"    # cầu đang mở lúc đầu
SOFT = "o"           # công tắc mềm: bất kỳ phần nào của khối chạm vào đều kích hoạt
HEAVY = "x"          # công tắc nặng: chỉ kích hoạt khi khối đứng trên
SPLIT_SWITCH = "@"   # công tắc tách: khi khối đứng trên, dịch chuyển và tách thành 2 khối con

BRIDGE_CHARS = (BRIDGE_CLOSED, BRIDGE_OPEN)
SWITCH_KIND = {SOFT: "soft", HEAVY: "heavy", SPLIT_SWITCH: "split"}
TILE_CHARS = {FLOOR, START, GOAL, FRAGILE, BRIDGE_CLOSED, BRIDGE_OPEN, *SWITCH_KIND}
EFFECTS = ("toggle", "open", "close")
KINDS = ("main", "challenge", "bonus")


class LevelError(ValueError):
    """Màn chơi sai định dạng."""


@dataclass(frozen=True)
class Switch:
    at: Cell
    kind: str                       # "soft" | "heavy" | "split"
    effect: str = ""                # soft/heavy: "toggle" | "open" | "close"
    bridges: Tuple[Cell, ...] = ()  # soft/heavy: các cầu bị điều khiển
    targets: Tuple[Cell, ...] = ()  # split: hai ô đích của khối con


@dataclass(frozen=True)
class Level:
    id: str
    name: str
    group: str
    source: str
    grid: Tuple[str, ...]
    start: Cell
    goal: Cell
    switches: Dict[Cell, Switch]
    initial_open: FrozenSet[Cell]
    chapter: int = 1
    order: int = 1
    kind: str = "main"        # "main" | "challenge" | "bonus"
    par: int = 0              # số bước tối ưu, 0 nghĩa là chưa biết
    intro: Optional[str] = None
    unlock_stars: int = 0

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0])

    def tile(self, cell: Cell) -> str:
        """Ký tự của ô, hoặc VOID nếu ô nằm ngoài bảng."""
        r, c = cell
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return VOID

    def initial_state(self) -> State:
        return State(Orient.STANDING, self.start, None, self.initial_open)


def load_level(path: Path, level_id: str) -> Level:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LevelError(f"{path.name}: {exc}") from exc
    return parse_level(data, level_id, where=path.name)


def load_levels(directory: Path) -> Dict[str, Level]:
    """Đọc mọi file *.json trong thư mục, theo thứ tự tên file."""
    levels: Dict[str, Level] = {}
    for path in sorted(directory.glob("*.json")):
        level = load_level(path, path.stem)
        levels[level.id] = level
    if not levels:
        raise LevelError(f"Không có màn chơi nào trong {directory}")
    return levels


def parse_level(data: Any, level_id: str, where: str = "") -> Level:
    where = where or level_id
    if not isinstance(data, dict):
        raise LevelError(f"{where}: nội dung phải là một object JSON")

    grid = data.get("grid")
    if not isinstance(grid, list) or not grid or not all(isinstance(row, str) for row in grid):
        raise LevelError(f"{where}: 'grid' phải là danh sách chuỗi, không rỗng")
    grid = tuple(grid)
    if not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise LevelError(f"{where}: mọi hàng của 'grid' phải có cùng độ dài")
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch != VOID and ch not in TILE_CHARS:
                raise LevelError(f"{where}: ký tự lạ {ch!r} tại ô {(r, c)}")

    starts = _cells_of(grid, START)
    goals = _cells_of(grid, GOAL)
    if len(starts) != 1 or len(goals) != 1:
        raise LevelError(f"{where}: cần đúng 1 ô 'S' và đúng 1 ô 'G'")
    bridge_set = set(_cells_of(grid, BRIDGE_CLOSED)) | set(_cells_of(grid, BRIDGE_OPEN))

    switches: Dict[Cell, Switch] = {}
    for raw in data.get("switches", []):
        at, declared_kind, effect, bridges, targets = _read_switch(raw, where)
        if at in switches:
            raise LevelError(f"{where}: công tắc {at} được khai báo hai lần")
        if _char(grid, at) not in SWITCH_KIND:
            raise LevelError(f"{where}: ô {at} không phải ô công tắc trong 'grid'")
        kind = SWITCH_KIND[_char(grid, at)]
        if declared_kind not in (None, kind):
            raise LevelError(f"{where}: ô {at} là công tắc '{kind}' nhưng khai báo '{declared_kind}'")

        if kind == "split":
            if len(targets) != 2 or targets[0] == targets[1]:
                raise LevelError(f"{where}: công tắc tách {at} cần đúng 2 ô đích khác nhau")
            if any(_char(grid, t) == VOID for t in targets):
                raise LevelError(f"{where}: ô đích của công tắc tách {at} không được là khoảng trống")
        else:
            if targets:
                raise LevelError(f"{where}: chỉ công tắc tách mới có 'targets' (ô {at})")
            if not bridges:
                raise LevelError(f"{where}: công tắc {at} phải điều khiển ít nhất một cầu")
        # Công tắc tách có thể nối cầu (tùy chọn), nên effect chỉ bắt buộc khi có cầu.
        if bridges and effect not in EFFECTS:
            raise LevelError(f"{where}: công tắc {at} có effect phải là một trong {EFFECTS}")
        if effect and not bridges:
            raise LevelError(f"{where}: công tắc {at} có effect nhưng không có cầu nào")
        unknown = [b for b in bridges if b not in bridge_set]
        if unknown:
            raise LevelError(f"{where}: công tắc {at} trỏ tới ô không phải cầu: {unknown}")
        switches[at] = Switch(at, kind, effect, bridges, targets)

    for cell, ch in _iter_cells(grid):
        if ch in SWITCH_KIND and cell not in switches:
            raise LevelError(f"{where}: thiếu cấu hình cho công tắc tại {cell}")

    level_kind = str(data.get("kind", "main"))
    if level_kind not in KINDS:
        raise LevelError(f"{where}: 'kind' phải là một trong {KINDS}")
    intro = data.get("intro")
    if intro is not None and not isinstance(intro, str):
        raise LevelError(f"{where}: 'intro' phải là chuỗi hoặc null")

    return Level(
        id=level_id,
        name=str(data.get("name", level_id)),
        group=str(data.get("group", "khác")),
        source=str(data.get("source", "")),
        grid=grid,
        start=starts[0],
        goal=goals[0],
        switches=switches,
        initial_open=frozenset(_cells_of(grid, BRIDGE_OPEN)),
        chapter=_int_field(data, "chapter", 1, where, minimum=1),
        order=_int_field(data, "order", 1, where, minimum=1),
        kind=level_kind,
        par=_int_field(data, "par", 0, where, minimum=0),
        intro=intro,
        unlock_stars=_int_field(data, "unlock_stars", 0, where, minimum=0),
    )


def _int_field(data: Dict[str, Any], key: str, default: int, where: str, minimum: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise LevelError(f"{where}: '{key}' phải là số nguyên >= {minimum}")
    return value


def _read_switch(raw: Any, where: str):
    if not isinstance(raw, dict):
        raise LevelError(f"{where}: mỗi công tắc phải là một object JSON")
    try:
        at = to_cell(raw["at"])
        bridges = tuple(to_cell(x) for x in raw.get("bridges", []))
        targets = tuple(to_cell(x) for x in raw.get("targets", []))
    except (KeyError, ValueError) as exc:
        raise LevelError(f"{where}: cấu hình công tắc không hợp lệ ({exc})") from exc
    return at, raw.get("type"), str(raw.get("effect", "")), bridges, targets


def _char(grid: Tuple[str, ...], cell: Cell) -> str:
    r, c = cell
    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
        return grid[r][c]
    return VOID


def _iter_cells(grid: Tuple[str, ...]):
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            yield (r, c), ch


def _cells_of(grid: Tuple[str, ...], ch: str) -> List[Cell]:
    return [cell for cell, value in _iter_cells(grid) if value == ch]
