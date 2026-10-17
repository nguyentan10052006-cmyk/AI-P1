"""Biểu diễn trạng thái: vị trí khối, tư thế và cấu hình cầu."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, FrozenSet, Optional, Tuple

Cell = Tuple[int, int]  # (hàng, cột)


class Orient(str, Enum):
    """Tư thế của khối 1×1×2, hoặc trạng thái đã tách thành hai khối 1×1×1."""

    STANDING = "standing"      # đứng thẳng, chiếm 1 ô
    HORIZONTAL = "horizontal"  # nằm ngang, chiếm (r, c) và (r, c+1)
    VERTICAL = "vertical"      # nằm dọc, chiếm (r, c) và (r+1, c)
    SPLIT = "split"            # đã tách: hai khối con, mỗi khối chiếm 1 ô


class Dir(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


DELTA = {
    Dir.UP: (-1, 0),
    Dir.DOWN: (1, 0),
    Dir.LEFT: (0, -1),
    Dir.RIGHT: (0, 1),
}


@dataclass(frozen=True)
class State:
    """Trạng thái đầy đủ. Hashable nên dùng được làm khóa của tập đã thăm.

    pos: ô neo của khối. Với khối đứng là ô đứng, với khối nằm là ô trái/trên,
         khi đã tách là ô của khối con 0.
    pos2: ô của khối con 1 (chỉ khi SPLIT). Luôn được chuẩn hóa để pos < pos2.
    open_bridges: tập các ô cầu đang mở. Cùng vị trí khối nhưng khác cấu hình
         cầu thì là hai trạng thái khác nhau.
    """

    orient: Orient
    pos: Cell
    pos2: Optional[Cell] = None
    open_bridges: FrozenSet[Cell] = frozenset()

    def cells(self) -> Tuple[Cell, ...]:
        """Các ô mà khối đang chiếm."""
        r, c = self.pos
        if self.orient is Orient.STANDING:
            return (self.pos,)
        if self.orient is Orient.HORIZONTAL:
            return (self.pos, (r, c + 1))
        if self.orient is Orient.VERTICAL:
            return (self.pos, (r + 1, c))
        return (self.pos, self.pos2)


@dataclass(frozen=True)
class Action:
    """Một lệnh lăn. cube chỉ dùng khi đã tách: 0 hoặc 1 là khối con nào."""

    dir: Dir
    cube: Optional[int] = None


def split_state(a: Cell, b: Cell, open_bridges: FrozenSet[Cell]) -> State:
    """Tạo trạng thái đã tách, chuẩn hóa thứ tự hai khối con."""
    lo, hi = sorted((a, b))
    return State(Orient.SPLIT, lo, hi, open_bridges)


def to_cell(value: Any) -> Cell:
    """Đổi [r, c] từ JSON thành tuple (r, c) và kiểm tra kiểu."""
    if (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(x, int) and not isinstance(x, bool) for x in value)
    ):
        return (value[0], value[1])
    raise ValueError(f"ô không hợp lệ: {value!r}")
