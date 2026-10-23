"""Dựng bàn 3D từ Level (V18); cầu đóng/mở và ô dễ vỡ có hoạt ảnh (V20). Chỉ vẽ, không xử lý luật (docs/07 §5).

Tọa độ theo docs/07 §4: ô (r, c) có tâm tại x = c, z = -r; mặt trên ô sàn ở y = 0.
"""
from __future__ import annotations

import math
from typing import Dict, FrozenSet, List, Optional

from ursina import Circle, Entity, Mesh, Vec3, camera, color, curve
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from bloxorz.level import FRAGILE, GOAL, HEAVY, SOFT, SPLIT_SWITCH, VOID, BRIDGE_CHARS, Level
from bloxorz.state import Cell

TILE_SIZE = 0.94      # chừa khe nhỏ giữa các ô để nhìn rõ lưới
TILE_HEIGHT = 0.2
MARK_Y = 0.006        # dấu công tắc nằm sát trên mặt ô

COLORS = {
    "floor": color.hex("#9aa3ad"),
    "fragile": color.hex("#e8892c"),
    "bridge": color.hex("#a9784a"),
    "goal_rim": color.hex("#6b737c"),
    "goal_hole": color.hex("#15181c"),
    "soft": color.hex("#e9eef2"),
    "heavy": color.hex("#c43c3c"),
    "split": color.hex("#2f6fd6"),
}
CLOSED_BRIDGE_ALPHA = 0.18
HUD_SHIFT = 0.06      # phần chiều rộng bàn chừa cho cột nút bên phải (hud.py)


def cell_to_world(cell: Cell, y: float = 0.0) -> Vec3:
    r, c = cell
    return Vec3(c, y, -r)


def _with_alpha(base: color.Color, alpha: float) -> color.Color:
    return color.Color(base[0], base[1], base[2], alpha)


class BoardView(Entity):
    """Gốc chung của mọi entity trong một màn. Đổi màn hoặc Restart thì destroy() đối tượng này (docs/07 §7)."""

    def __init__(self, level: Level, open_bridges: Optional[FrozenSet[Cell]] = None) -> None:
        super().__init__()
        self.level = level
        self._bridges: Dict[Cell, Entity] = {}
        self._fragile: Dict[Cell, Entity] = {}
        self._open: Optional[FrozenSet[Cell]] = None
        for r in range(level.rows):
            for c in range(level.cols):
                char = level.tile((r, c))
                if char != VOID:
                    self._build_tile((r, c), char)
        self.set_open_bridges(level.initial_open if open_bridges is None else open_bridges)

    def reset(self, open_bridges: FrozenSet[Cell]) -> None:
        """Restart: dựng lại ô dễ vỡ đã vỡ và đặt cầu về trạng thái đầu, không hoạt ảnh."""
        for slab in self._fragile.values():
            for animation in slab.animations:   # dừng hoạt ảnh vỡ nếu bấm R lúc ô đang rơi
                animation.kill()
            slab.animations.clear()
            slab.y, slab.color = -TILE_HEIGHT / 2, COLORS["fragile"]
        self._open = None
        self.set_open_bridges(open_bridges)

    def break_tile(self, cell: Cell, duration: float) -> None:
        """Ô dễ vỡ bị khối đứng lên: ô rơi xuống cùng khối và mờ dần."""
        slab = self._fragile.get(cell)
        if slab is not None:
            slab.animate_y(slab.y - 12, duration=duration, curve=curve.in_quad)
            slab.animate_color(_with_alpha(COLORS["fragile"], 0), duration=duration)

    @property
    def center(self) -> Vec3:
        """Tâm của phần bàn có ô (lưới màn gốc luôn 10 × 15 nhưng nhiều hàng, cột để trống)."""
        rows, cols = self._extent()
        return Vec3((cols[0] + cols[1]) / 2, 0, -(rows[0] + rows[1]) / 2)

    def _extent(self) -> tuple[tuple[int, int], tuple[int, int]]:
        cells = [(r, c) for r in range(self.level.rows) for c in range(self.level.cols)
                 if self.level.tile((r, c)) != VOID]
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]
        return (min(rs), max(rs)), (min(cs), max(cs))

    def set_open_bridges(self, open_bridges: FrozenSet[Cell], duration: float = 0.0) -> None:
        """Cầu mở vẽ như sàn gỗ; cầu đóng chỉ còn bóng mờ để người chơi biết chỗ có cầu.

        duration > 0 thì các ô cầu vừa đổi trạng thái hiện hoặc mờ dần (sau khi bấm công tắc).
        """
        for cell, slab in self._bridges.items():
            opened = cell in open_bridges
            target = COLORS["bridge"] if opened else _with_alpha(COLORS["bridge"], CLOSED_BRIDGE_ALPHA)
            changed = self._open is not None and opened != (cell in self._open)
            if duration > 0 and changed:
                slab.animate_color(target, duration=duration)
            else:
                slab.color = target
        self._open = open_bridges

    def fit_camera(self) -> None:
        """Căn camera theo kích thước bàn, nhìn từ phía z âm để phím ↑ đẩy khối ra xa (docs/07 §4)."""
        rows, cols = self._extent()
        size = max((rows[1] - rows[0] + 1) * 1.6, cols[1] - cols[0] + 1) + 3   # 1.6: tỉ lệ khung hình; +3: lề quanh bàn
        target = self.center + Vec3(size * HUD_SHIFT, 0, 0)   # nhìn lệch sang phải: bàn dời sang trái, chừa cột nút
        camera.position = target + Vec3(size * 0.1, size * 1.05, -size * 0.95)
        camera.look_at(target)

    def _slab(self, cell: Cell, tint: color.Color, scale_xz: float = TILE_SIZE, height: float = TILE_HEIGHT,
              top: float = 0.0) -> Entity:
        return Entity(
            parent=self, model="cube", color=tint, shader=lit_with_shadows_shader,
            position=cell_to_world(cell, top - height / 2), scale=(scale_xz, height, scale_xz),
        )

    def _build_tile(self, cell: Cell, char: str) -> None:
        if char == GOAL:
            self._build_goal(cell)
        elif char == FRAGILE:
            self._fragile[cell] = self._slab(cell, COLORS["fragile"])
        elif char in BRIDGE_CHARS:
            self._bridges[cell] = self._slab(cell, COLORS["bridge"])
        else:
            self._slab(cell, COLORS["floor"])  # sàn, ô xuất phát và nền của công tắc
            if char == SOFT:
                self._mark_soft(cell)
            elif char == HEAVY:
                self._mark_heavy(cell)
            elif char == SPLIT_SWITCH:
                self._mark_split(cell)

    def _build_goal(self, cell: Cell) -> None:
        """Lỗ vuông: viền 4 cạnh ngang mặt sàn, đáy tối lún xuống."""
        rim = 0.12
        half = TILE_SIZE / 2 - rim / 2
        center = cell_to_world(cell, -TILE_HEIGHT / 2)
        for dx, dz, sx, sz in ((-half, 0, rim, TILE_SIZE), (half, 0, rim, TILE_SIZE),
                               (0, -half, TILE_SIZE, rim), (0, half, TILE_SIZE, rim)):
            Entity(parent=self, model="cube", color=COLORS["goal_rim"], shader=lit_with_shadows_shader,
                   position=center + Vec3(dx, 0, dz), scale=(sx, TILE_HEIGHT, sz))
        self._slab(cell, COLORS["goal_hole"], scale_xz=TILE_SIZE - 2 * rim, height=0.05, top=-0.15)

    def _mark_soft(self, cell: Cell) -> None:
        """Công tắc mềm: đĩa tròn."""
        Entity(parent=self, model=Circle(resolution=32, radius=0.32), color=COLORS["soft"], shader=unlit_shader,
               position=cell_to_world(cell, MARK_Y), rotation_x=90)

    def _mark_heavy(self, cell: Cell) -> None:
        """Công tắc nặng: hình X."""
        for angle in (45, -45):
            Entity(parent=self, model="cube", color=COLORS["heavy"],
                   position=cell_to_world(cell, MARK_Y + 0.01), rotation_y=angle, scale=(0.72, 0.02, 0.13))

    def _mark_split(self, cell: Cell) -> None:
        """Công tắc tách: hình "( )", vẽ bằng hai cung tròn."""
        for start in (120, -60):
            points: List[Vec3] = []
            for i in range(13):
                a = math.radians(start + i * 10)
                points.append(Vec3(0.3 * math.cos(a), 0, 0.3 * math.sin(a)))
            Entity(parent=self, model=Mesh(vertices=points, mode="line", thickness=5), color=COLORS["split"],
                   position=cell_to_world(cell, MARK_Y + 0.01))
