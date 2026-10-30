"""Khối 1×1×2 và hai khối con: lật quanh cạnh, tách, ghép, rơi, lọt lỗ (V19, V20, V21).

Chỉ vẽ theo State; luật nằm ở bloxorz.rules (docs/07 §5). Kích thước theo docs/07 §4: khối đứng có tâm
y = 1 (cao 2); khối nằm và khối con có tâm y = 0.5.

Cách vẽ:
- Khối nguyên là một hộp vát cạnh 1×2×1 cố định; tư thế thể hiện bằng góc xoay (nằm ngang: quay 90° quanh
  trục z, nằm dọc: quay 90° quanh trục x), không co giãn hình.
- Một lần lăn là một lần lật 90° quanh cạnh đáy theo hướng đi, như game gốc: khối được gắn tạm vào một
  "trục" đặt ở cạnh đó rồi xoay trục. Lật xong (lần gọi kế tiếp) thì đặt lại đúng vị trí và góc theo State,
  nên sai số không dồn qua các bước.
- Hai khối con là hai hộp 1×1×1 riêng, lật theo cùng cách.
- Mỗi khối có viền sáng (vỏ ngoài chỉ vẽ mặt sau) và một bóng mềm dưới đáy để khối "đứng" trên sàn.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from panda3d.core import CullFaceAttrib
from ursina import Entity, Vec3, color, curve, destroy
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from bloxorz.state import DELTA, Cell, Dir, Orient, State
from gui.anim import animate_later, stop_animations
from gui.board_view import cell_to_world
from gui.meshes import beveled_box

SIZE = 0.96          # nhỏ hơn ô một chút để thấy khe giữa khối và sàn
BEVEL = 0.07
OUTLINE = 0.022      # độ dày viền sáng
BLOCK_SHADE = (1.0, 0.9, 0.75)   # mặt trên sáng nhất, mặt dưới tối hơn: khối có khối lượng dù đèn yếu
# Đèn của cảnh hạ còn 62% (GAME_UI_UX_SPECIFICATION §2.2) để sàn không cháy sáng; khối nhân thêm hệ số
# (color scale của Panda3D cho phép > 1) để vẫn trắng như #f0f6fc dưới ánh đèn đó
BLOCK_GAIN = 1.45


def _gain(base: color.Color, gain: float = BLOCK_GAIN) -> color.Color:
    return color.Color(base[0] * gain, base[1] * gain, base[2] * gain, base[3])


COLORS = {
    "block": _gain(color.hex("#f0f6fc")),
    "active": _gain(color.hex("#f0f6fc")),   # khối con đang điều khiển
    "idle": _gain(color.hex("#7d8896")),     # khối con còn lại
    "edge": color.hex("#38bdf8"),     # viền sáng giúp khối nổi trên sàn xám
    "shadow": color.rgba(0, 0, 0, 0.55),
}
EDGE_ALPHA = {"active": 0.9, "idle": 0.25}
ROLL_CURVE = curve.in_out_sine
SHADOW_SOFT = 1.55   # bóng rộng hơn đáy khối chừng này lần, mép mờ dần
SHADOW_FADE = 2.5    # khối cao hơn mặt sàn chừng này đơn vị thì bóng mờ hẳn

# Hướng lăn -> (trục quay của Ursina, góc): rotation_z +90 đưa +y sang +x, rotation_x +90 đưa +y sang +z
ROLL_AXIS = {
    Dir.RIGHT: ("rotation_z", 90), Dir.LEFT: ("rotation_z", -90),
    Dir.UP: ("rotation_x", 90), Dir.DOWN: ("rotation_x", -90),
}


def _world_delta(direction: Dir) -> Tuple[int, int]:
    """(dx, dz) trong không gian 3D của một bước theo direction: x = cột, z = −hàng (docs/07 §4)."""
    dr, dc = DELTA[direction]
    return dc, -dr


def body_transform(state: State) -> Tuple[Vec3, Vec3]:
    """(vị trí tâm, góc xoay) của khối nguyên theo tư thế."""
    r, c = state.pos
    if state.orient is Orient.STANDING:
        return cell_to_world(state.pos, 1.0), Vec3(0, 0, 0)
    if state.orient is Orient.HORIZONTAL:
        return Vec3(c + 0.5, 0.5, -r), Vec3(0, 0, 90)
    return Vec3(c, 0.5, -(r + 0.5)), Vec3(90, 0, 0)


def roll_pivot(cells: Sequence[Cell], direction: Dir) -> Vec3:
    """Cạnh đáy mà khối chiếm cells lật qua khi đi theo direction (mặt sàn y = 0)."""
    points = [cell_to_world(cell) for cell in cells]
    dx, dz = _world_delta(direction)
    x = sum(p.x for p in points) / len(points)
    z = sum(p.z for p in points) / len(points)
    if dx:
        x = (max if dx > 0 else min)(p.x for p in points) + dx * 0.5
    else:
        z = (max if dz > 0 else min)(p.z for p in points) + dz * 0.5
    return Vec3(x, 0, z)


def tip_axis(from_cell: Cell, to_cell: Cell) -> Tuple[str, float]:
    """Trục và chiều quay để khối đổ từ phía from_cell sang phía to_cell (hai ô kề nhau)."""
    (r1, c1), (r2, c2) = from_cell, to_cell
    if c2 != c1:
        return "rotation_z", 90 if c2 > c1 else -90
    return "rotation_x", 90 if r2 < r1 else -90


class BlockView(Entity):
    """Một khối nguyên và hai khối con; chỉ bật những khối đang có trên bàn."""

    def __init__(self, state: State, **kwargs) -> None:
        super().__init__(**kwargs)
        self.body = self._piece((SIZE, 2 * SIZE, SIZE))
        self.cubes = [self._piece((SIZE, SIZE, SIZE)) for _ in range(2)]
        self.shadows = {id(piece): Entity(parent=self, model="quad", texture="radial_gradient",
                                          color=COLORS["shadow"], shader=unlit_shader, rotation_x=90, y=0.012)
                        for piece in self.pieces}
        self._pivot: Optional[Entity] = None
        self._rolled: Optional[Entity] = None    # khối đang gắn vào trục
        self._pending: Optional[Tuple[State, Optional[int]]] = None   # trạng thái cần đặt khi lật xong
        self.show(state)

    @property
    def pieces(self) -> List[Entity]:
        return [self.body, *self.cubes]

    def _piece(self, size: Tuple[float, float, float]) -> Entity:
        piece = Entity(parent=self, model=beveled_box(size, BEVEL, BLOCK_SHADE), color=COLORS["block"],
                       shader=lit_with_shadows_shader)
        outline = Entity(parent=piece, model=beveled_box([s + 2 * OUTLINE for s in size], BEVEL + OUTLINE),
                         color=COLORS["edge"], shader=unlit_shader)
        # Chỉ vẽ mặt trong của lớp vỏ lớn hơn: thấy được một viền sáng quanh khối, không che mặt khối
        outline.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        piece.outline = outline
        return piece

    # ---- đặt khối đứng yên ----

    def show(self, state: State, active_cube: Optional[int] = None, pulse: bool = False) -> None:
        """Đặt khối đúng theo state, dừng mọi hoạt ảnh cũ. pulse: nảy nhẹ (vừa ghép xong)."""
        self._finish_roll(apply_pending=False)
        for piece in self.pieces:
            self._stop(piece)
            self._stop(piece.outline)
        if state.orient is Orient.SPLIT:
            self.body.enabled = False
            order = self._match(state.cells())
            for entity_index, cell in zip(order, state.cells()):
                cube = self.cubes[entity_index]
                cube.enabled = True
                cube.position, cube.rotation, cube.scale = cell_to_world(cell, 0.5), Vec3(0, 0, 0), Vec3(1, 1, 1)
            self._paint(order, active_cube)
        else:
            for cube in self.cubes:
                cube.enabled = False
            self.body.enabled = True
            self.body.position, self.body.rotation = body_transform(state)
            self.body.scale = Vec3(1, 1, 1)
            self.body.color = COLORS["block"]
            self.body.outline.alpha = EDGE_ALPHA["active"]
            if pulse:
                self.body.scale = Vec3(1.06, 1.06, 1.06)
                self.body.animate_scale(Vec3(1, 1, 1), duration=0.18, curve=curve.out_quad)

    def spawn(self, state: State, duration: float, delay: float = 0.0) -> None:
        """Khối rơi nhẹ từ trên xuống chỗ xuất phát (vào màn hoặc chơi lại)."""
        self.show(state)
        for piece in self.pieces:
            if piece.enabled:
                target = piece.y
                piece.y = target + 3
                animate_later(piece, "y", target, duration, delay, curve.out_bounce)

    # ---- một lần lăn ----

    def roll(self, before: State, direction: Dir, moved: State, active_after: Optional[int],
             duration: float, active_before: Optional[int] = None) -> None:
        """Lật khối (hoặc khối con active_before) 90° quanh cạnh đáy theo direction, tới vị trí moved.

        moved là vị trí ngay sau khi lăn, trước khi công tắc hay ghép khối được xử lý (StepResult.moved).
        """
        self.show(before, active_before)
        if before.orient is Orient.SPLIT:
            cell = before.cells()[active_before or 0]
            piece = min(self.cubes, key=lambda cube: (cube.position - cell_to_world(cell, 0.5)).length())
            cells: Sequence[Cell] = (cell,)
        else:
            piece, cells = self.body, before.cells()
        axis, angle = ROLL_AXIS[direction]
        self._pivot = Entity(parent=self, position=roll_pivot(cells, direction))
        piece.world_parent = self._pivot
        self._rolled = piece
        self._pending = (moved, active_after)
        self._pivot.animate(axis, angle, duration=duration, curve=ROLL_CURVE)

    def _finish_roll(self, apply_pending: bool = True) -> None:
        """Gỡ khối khỏi trục quay; apply_pending thì đặt khối đúng vị trí sau lần lăn."""
        if self._pivot is None:
            return
        pending = self._pending
        self._stop(self._pivot)
        self._rolled.world_parent = self
        destroy(self._pivot)
        self._pivot = self._rolled = self._pending = None
        if apply_pending and pending is not None:
            self.show(*pending)

    # ---- tách, rơi, thắng ----

    def split(self, state: State, active_cube: Optional[int], duration: float) -> None:
        """Hai khối con bay theo đường vòng cung từ chỗ khối nguyên tới hai ô đích của công tắc tách."""
        self._finish_roll()
        origin = self.body.position if self.body.enabled else None
        self.show(state, active_cube)
        if origin is None:
            return
        for cube in self.cubes:
            target = cube.position
            cube.position = Vec3(origin.x, origin.y, origin.z)
            cube.animate_x(target.x, duration=duration, curve=curve.linear)
            cube.animate_z(target.z, duration=duration, curve=curve.linear)
            cube.animate_y(target.y + 1.6, duration=duration / 2, curve=curve.out_quad)
            animate_later(cube, "y", target.y, duration / 2, duration / 2, curve.in_quad)

    def fall(self, state: State, unsupported: Iterable[Cell], duration: float) -> None:
        """Khối rơi. Khối nằm hụt đúng một ô thì đổ nghiêng qua mép rồi mới rơi, không xuyên qua sàn;
        đã tách thì chỉ khối con bị hụt rơi; còn lại (đứng trên ô trống, ô dễ vỡ, hụt cả hai ô) rơi thẳng.
        """
        self._finish_roll()
        self.show(state)
        unsupported = list(unsupported)
        if state.orient is Orient.SPLIT:
            falling = [cube for cube in self.cubes if cube.enabled
                       and any((cube.position - cell_to_world(cell, 0.5)).length() < 0.1 for cell in unsupported)]
            for cube in falling or [c for c in self.cubes if c.enabled]:
                self._drop(cube, duration)
            return
        cells = state.cells()
        if len(cells) == 2 and len(unsupported) == 1:
            hanging = unsupported[0]
            resting = cells[0] if cells[1] == hanging else cells[1]
            axis, angle = tip_axis(resting, hanging)
            a, b = cell_to_world(resting), cell_to_world(hanging)
            self._pivot = Entity(parent=self, position=(a + b) / 2)
            self.body.world_parent = self._pivot
            self._rolled, self._pending = self.body, None
            tip = duration * 0.4
            self._pivot.animate(axis, angle, duration=tip, curve=curve.in_quad)
            animate_later(self._pivot, axis, angle * 2.2, duration - tip, tip, curve.linear)
            animate_later(self._pivot, "y", -12, duration - tip, tip, curve.in_quad)
            self._fade(self.body, duration - tip, delay=tip)
            return
        self._drop(self.body, duration)

    def sink(self, duration: float) -> None:
        """Thắng: khối đứng lọt xuống lỗ đích."""
        self._finish_roll()
        self.body.animate_y(self.body.y - 2.2, duration=duration, curve=curve.in_quad)

    @classmethod
    def _drop(cls, piece: Entity, duration: float) -> None:
        piece.animate_y(piece.y - 12, duration=duration, curve=curve.in_quad)
        cls._fade(piece, duration * 0.7, delay=duration * 0.3)

    @staticmethod
    def _fade(piece: Entity, duration: float, delay: float = 0.0) -> None:
        """Mờ dần khi rơi xuống dưới bàn, để khối không lộ ra qua khe giữa các ô (show() trả lại màu).

        Viền tắt trước: thân khối đã trong suốt mà viền (vỏ chỉ vẽ mặt trong) còn thì khối trông như màu viền.
        """
        base = piece.color
        animate_later(piece.outline, "alpha", 0, min(0.08, duration), delay, curve.linear)
        animate_later(piece, "color", color.Color(base[0], base[1], base[2], 0), duration, delay, curve.in_quad)

    # ---- mỗi khung hình: bóng dưới khối ----

    def update(self) -> None:
        for piece in self.pieces:
            shadow = self.shadows[id(piece)]
            shadow.enabled = piece.enabled
            if not piece.enabled:
                continue
            center = piece.world_position
            # nửa bề rộng hình chiếu xuống sàn của hộp đã xoay: cộng |trục| × nửa cạnh theo từng trục
            half = Vec3(SIZE / 2, (2 * SIZE if piece is self.body else SIZE) / 2, SIZE / 2)
            axes = (piece.right, piece.up, piece.forward)
            extent_x = sum(abs(axis.x) * h for axis, h in zip(axes, half))
            extent_z = sum(abs(axis.z) * h for axis, h in zip(axes, half))
            extent_y = sum(abs(axis.y) * h for axis, h in zip(axes, half))
            height = max(0.0, center.y - extent_y)     # khoảng cách từ đáy khối tới mặt sàn
            shadow.x, shadow.z = center.x, center.z
            shadow.scale = Vec3(2 * extent_x * SHADOW_SOFT, 2 * extent_z * SHADOW_SOFT, 1)
            shadow.alpha = COLORS["shadow"].a * max(0.0, 1 - height / SHADOW_FADE) if center.y > -0.2 else 0

    # ---- tiện ích ----

    @staticmethod
    def _stop(piece: Entity) -> None:
        stop_animations(piece)

    def _match(self, cells: Sequence[Cell]) -> List[int]:
        """Gán 2 ô cho 2 khối con sao cho mỗi khối đi quãng ngắn nhất.

        Engine luôn sắp hai khối con để pos < pos2, nên sau một bước chỉ số của khối vừa đi có thể đổi;
        ghép theo khoảng cách để khối không nhảy chéo sang chỗ của khối kia.
        """
        targets = [cell_to_world(cell, 0.5) for cell in cells]
        if not any(cube.enabled for cube in self.cubes):
            return [0, 1]

        def cost(order) -> float:
            return sum((self.cubes[i].position - targets[k]).length() for k, i in enumerate(order))
        return list(min(([0, 1], [1, 0]), key=cost))

    def _paint(self, order: List[int], active_cube: Optional[int]) -> None:
        for k, entity_index in enumerate(order):
            role = "active" if active_cube is None or k == active_cube else "idle"
            cube = self.cubes[entity_index]
            cube.color = COLORS[role]
            cube.outline.alpha = EDGE_ALPHA[role]
