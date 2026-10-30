"""Dựng bàn 3D từ Level (V18); cầu, công tắc, ô dễ vỡ và ô đích có hoạt ảnh (V20, V21).

Chỉ vẽ, không xử lý luật (docs/07 §5). Tọa độ theo docs/07 §4: ô (r, c) có tâm tại x = c, z = -r;
mặt trên ô sàn ở y = 0.

Mỗi ô có một gốc riêng (`_roots`) chứa tấm ô và ký hiệu trên mặt; hoạt ảnh mở màn nâng từng gốc từ dưới lên.
Tấm ô là hộp vát cạnh có mặt bên tối hơn mặt trên (gui/meshes.py), nên bàn có độ dày mà không cần bóng đổ.
"""
from __future__ import annotations

import math
import time
from typing import Dict, FrozenSet, List, Optional, Tuple

from ursina import Circle, Entity, Mesh, Vec3, color, curve, destroy
from ursina import time as frame_time
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from bloxorz.level import BRIDGE_CHARS, FRAGILE, GOAL, HEAVY, SOFT, SPLIT_SWITCH, VOID, Level
from bloxorz.state import Cell
from gui.anim import animate_later, call_later, stop_animations
from gui.meshes import beveled_box

TILE_SIZE = 0.94      # chừa khe nhỏ giữa các ô để nhìn rõ lưới
TILE_HEIGHT = 0.3
TILE_BEVEL = 0.05
TILE_SHADE = (1.0, 0.68, 0.45)   # mặt trên, mặt bên, mặt dưới
MARK_Y = 0.006        # ký hiệu công tắc nằm sát trên mặt ô

COLORS = {
    "floor": color.hex("#9aa3ad"),
    "floor_alt": color.hex("#929ba5"),   # ô sàn xen kẽ, đậm hơn một chút để dễ đếm ô
    "fragile": color.hex("#e8892c"),
    "bridge": color.hex("#a9784a"),
    "goal_rim": color.hex("#6b737c"),
    "goal_hole": color.hex("#090d12"),
    "goal_glow": color.hex("#f2c94c"),
    "soft": color.hex("#e9eef2"),
    "heavy": color.hex("#c43c3c"),
    "split": color.hex("#2f6fd6"),
}
CLOSED_BRIDGE_ALPHA = 0.18
CLOSED_BRIDGE_DROP = 0.08     # cầu đóng lún xuống một chút so với mặt sàn
BRIDGE_RISE = 0.35            # cầu vừa mở trồi lên từ độ sâu này
GOAL_PULSE = (0.45, 1.0, 2.4)   # hào quang ô đích: alpha thấp nhất, cao nhất, tốc độ nhấp nháy (rad/s)
HUD_SHIFT = 0.06      # phần chiều rộng bàn chừa cho cột nút bên phải (hud.py)
INTRO_DEPTH = 4.0     # mở màn: các ô trồi lên từ độ sâu này
INTRO_STAGGER = 0.018  # giây chênh nhau giữa hai đường chéo ô liền kề
INTRO_TIME = 0.4


def cell_to_world(cell: Cell, y: float = 0.0) -> Vec3:
    r, c = cell
    return Vec3(c, y, -r)


def _with_alpha(base: color.Color, alpha: float) -> color.Color:
    return color.Color(base[0], base[1], base[2], alpha)


class BoardView(Entity):
    """Gốc chung của mọi entity trong một màn. Đổi màn thì destroy() đối tượng này (docs/07 §7)."""

    def __init__(self, level: Level, open_bridges: Optional[FrozenSet[Cell]] = None) -> None:
        super().__init__()
        self.level = level
        self._roots: Dict[Cell, Entity] = {}
        self._bridges: Dict[Cell, Entity] = {}
        self._fragile: Dict[Cell, Entity] = {}
        self._caps: Dict[Cell, Entity] = {}     # ký hiệu công tắc, lún xuống khi bị nhấn
        self._open: Optional[FrozenSet[Cell]] = None
        self._glow: List[Entity] = []
        self._glow_boost = 0.0                  # > 0 trong lúc ô đích lóe sáng khi thắng
        self._extent_cache = self._compute_extent()
        for r in range(level.rows):
            for c in range(level.cols):
                char = level.tile((r, c))
                if char != VOID:
                    self._roots[(r, c)] = Entity(parent=self, position=cell_to_world((r, c)))
                    self._build_tile((r, c), char)
        self.set_open_bridges(level.initial_open if open_bridges is None else open_bridges)

    # ---- trạng thái màn ----

    def reset(self, open_bridges: FrozenSet[Cell]) -> None:
        """Restart: dựng lại ô dễ vỡ đã vỡ và đặt cầu về trạng thái đầu, không hoạt ảnh."""
        for slab in self._fragile.values():
            self._stop(slab)
            slab.y, slab.color = -TILE_HEIGHT / 2, COLORS["fragile"]
        for cap in self._caps.values():
            self._stop(cap)
            cap.y = 0
        self._open = None
        self.set_open_bridges(open_bridges)

    def supports(self, cell: Cell, open_bridges: FrozenSet[Cell]) -> bool:
        """Ô có tấm đỡ (để chọn hoạt ảnh rơi). Luật rơi thật do rules.step() quyết định, đây chỉ là hình."""
        char = self.level.tile(cell)
        return char != VOID and (char not in BRIDGE_CHARS or cell in open_bridges)

    def set_open_bridges(self, open_bridges: FrozenSet[Cell], duration: float = 0.0) -> None:
        """Cầu mở vẽ như sàn gỗ; cầu đóng chỉ còn bóng mờ, lún nhẹ, để người chơi biết chỗ có cầu.

        duration > 0 thì cầu vừa mở trồi lên và hiện dần, cầu vừa đóng mờ đi và lún xuống (sau khi bấm công tắc).
        """
        base_y = -TILE_HEIGHT / 2
        for cell, slab in self._bridges.items():
            opened = cell in open_bridges
            target_color = COLORS["bridge"] if opened else _with_alpha(COLORS["bridge"], CLOSED_BRIDGE_ALPHA)
            target_y = base_y if opened else base_y - CLOSED_BRIDGE_DROP
            changed = self._open is not None and opened != (cell in self._open)
            if duration > 0 and changed:
                self._stop(slab)
                if opened:
                    slab.y = base_y - BRIDGE_RISE
                slab.animate_color(target_color, duration=duration, curve=curve.out_quad)
                slab.animate_y(target_y, duration=duration * 1.4, curve=curve.out_back if opened else curve.in_quad)
            else:
                slab.color, slab.y = target_color, target_y
        self._open = open_bridges

    # ---- hoạt ảnh ----

    def play_intro(self) -> float:
        """Mở màn: các ô trồi lên lần lượt theo đường chéo. Trả về số giây tới khi ô cuối cùng vào chỗ."""
        (r0, _), (c0, _) = self._extent_cache
        last = 0.0
        for (r, c), root in self._roots.items():
            delay = ((r - r0) + (c - c0)) * INTRO_STAGGER
            root.y = -INTRO_DEPTH
            animate_later(root, "y", 0, INTRO_TIME, delay, curve.out_back)
            last = max(last, delay + INTRO_TIME)
        return last

    def break_tile(self, cell: Cell, duration: float) -> None:
        """Ô dễ vỡ bị khối đứng lên: ô rơi xuống cùng khối và mờ dần."""
        slab = self._fragile.get(cell)
        if slab is not None:
            slab.animate_y(slab.y - 12, duration=duration, curve=curve.in_quad)
            slab.animate_color(_with_alpha(COLORS["fragile"], 0), duration=duration)

    def press_switch(self, cell: Cell) -> None:
        """Công tắc vừa tác động: ký hiệu lún xuống rồi nảy lên."""
        cap = self._caps.get(cell)
        if cap is not None:
            self._stop(cap)
            cap.y = 0
            cap.animate_y(-0.035, duration=0.07, curve=curve.out_quad)
            animate_later(cap, "y", 0, 0.25, 0.07, curve.out_back)

    def celebrate_goal(self) -> None:
        """Thắng: viền ô đích lóe sáng và một vòng sáng lan ra."""
        self._glow_boost = 1.0
        ring = Entity(parent=self, model=Circle(resolution=48, radius=0.5, mode="line", thickness=4),
                      color=COLORS["goal_glow"], shader=unlit_shader, rotation_x=90,
                      position=cell_to_world(self.level.goal, MARK_Y + 0.02))
        ring.animate_scale(4.5, duration=0.8, curve=curve.out_quad)
        ring.animate_color(_with_alpha(COLORS["goal_glow"], 0), duration=0.8, curve=curve.in_quad)
        # bàn có thể đã bị hủy (đổi màn) trước lúc này, khi đó vòng sáng cũng đã bị hủy theo
        call_later(ring, lambda: destroy(ring), 0.85)

    def update(self) -> None:
        """Ursina gọi mỗi frame: hào quang ô đích sáng tối nhịp nhàng để người chơi thấy đích ngay."""
        low, high, speed = GOAL_PULSE
        alpha = low + (high - low) * (0.5 + 0.5 * math.sin(time.time() * speed))
        if self._glow_boost > 0:
            self._glow_boost = max(0.0, self._glow_boost - 1.2 * frame_time.dt)
            alpha = max(alpha, high * min(1.0, self._glow_boost * 2))
        for strip in self._glow:
            strip.alpha = alpha

    # ---- camera ----

    @property
    def center(self) -> Vec3:
        """Tâm của phần bàn có ô (lưới màn gốc luôn 10 × 15 nhưng nhiều hàng, cột để trống)."""
        rows, cols = self._extent_cache
        return Vec3((cols[0] + cols[1]) / 2, 0, -(rows[0] + rows[1]) / 2)

    def fit_camera(self, camera_controller) -> None:
        """Căn camera theo kích thước bàn, nhìn từ phía z âm để phím ↑ đẩy khối ra xa (docs/07 §4)."""
        rows, cols = self._extent_cache
        size = max((rows[1] - rows[0] + 1) * 1.6, cols[1] - cols[0] + 1) + 3   # 1.6: tỉ lệ khung hình; +3: lề
        # camera xoay quanh tâm bàn; độ lệch chừa cột nút tính theo chiều ngang màn hình
        camera_controller.setup(self.center, size, screen_shift=size * HUD_SHIFT)

    def _compute_extent(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        cells = [(r, c) for r in range(self.level.rows) for c in range(self.level.cols)
                 if self.level.tile((r, c)) != VOID]
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]
        return (min(rs), max(rs)), (min(cs), max(cs))

    # ---- dựng ô ----

    @staticmethod
    def _stop(entity: Entity) -> None:
        stop_animations(entity)

    def _slab(self, cell: Cell, tint: color.Color, scale_xz: float = TILE_SIZE, height: float = TILE_HEIGHT,
              top: float = 0.0, offset: Vec3 = Vec3(0, 0, 0), size_z: Optional[float] = None) -> Entity:
        size = (scale_xz, height, scale_xz if size_z is None else size_z)
        return Entity(parent=self._roots[cell], model=beveled_box(size, TILE_BEVEL, TILE_SHADE), color=tint,
                      shader=lit_with_shadows_shader, position=offset + Vec3(0, top - height / 2, 0))

    def _cap(self, cell: Cell) -> Entity:
        cap = Entity(parent=self._roots[cell])
        self._caps[cell] = cap
        return cap

    def _build_tile(self, cell: Cell, char: str) -> None:
        if char == GOAL:
            self._build_goal(cell)
        elif char == FRAGILE:
            self._fragile[cell] = self._slab(cell, COLORS["fragile"])
        elif char in BRIDGE_CHARS:
            self._bridges[cell] = self._slab(cell, COLORS["bridge"])
        else:
            r, c = cell
            self._slab(cell, COLORS["floor"] if (r + c) % 2 == 0 else COLORS["floor_alt"])   # sàn, ô xuất phát
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
        for dx, dz, sx, sz in ((-half, 0, rim, TILE_SIZE), (half, 0, rim, TILE_SIZE),
                               (0, -half, TILE_SIZE - 2 * rim, rim), (0, half, TILE_SIZE - 2 * rim, rim)):
            self._slab(cell, COLORS["goal_rim"], scale_xz=sx, size_z=sz, offset=Vec3(dx, 0, dz))
        self._slab(cell, COLORS["goal_hole"], scale_xz=TILE_SIZE - 2 * rim, height=0.05, top=-0.22)
        # Viền sáng unlit nằm sát mép trong của lỗ, không phụ thuộc hướng đèn
        glow, inner = 0.045, TILE_SIZE / 2 - rim + 0.045 / 2
        for dx, dz, sx, sz in ((-inner, 0, glow, 2 * inner + glow), (inner, 0, glow, 2 * inner + glow),
                               (0, -inner, 2 * inner - glow, glow), (0, inner, 2 * inner - glow, glow)):
            self._glow.append(Entity(parent=self._roots[cell], model="quad", color=COLORS["goal_glow"],
                                     shader=unlit_shader, position=Vec3(dx, MARK_Y, dz), rotation_x=90,
                                     scale=(sx, sz)))

    def _mark_soft(self, cell: Cell) -> None:
        """Công tắc mềm: đĩa tròn."""
        Entity(parent=self._cap(cell), model=Circle(resolution=32, radius=0.32), color=COLORS["soft"],
               shader=unlit_shader, y=MARK_Y, rotation_x=90)

    def _mark_heavy(self, cell: Cell) -> None:
        """Công tắc nặng: hình X."""
        cap = self._cap(cell)
        for angle in (45, -45):
            Entity(parent=cap, model="cube", color=COLORS["heavy"], y=MARK_Y + 0.01, rotation_y=angle,
                   scale=(0.72, 0.02, 0.13))

    def _mark_split(self, cell: Cell) -> None:
        """Công tắc tách: hình "( )", vẽ bằng hai cung tròn."""
        cap = self._cap(cell)
        for start in (120, -60):
            points: List[Vec3] = []
            for i in range(13):
                a = math.radians(start + i * 10)
                points.append(Vec3(0.3 * math.cos(a), 0, 0.3 * math.sin(a)))
            Entity(parent=cap, model=Mesh(vertices=points, mode="line", thickness=5), color=COLORS["split"],
                   shader=unlit_shader, y=MARK_Y + 0.01)
