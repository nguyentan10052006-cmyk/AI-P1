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

from math import exp
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

from panda3d.core import CullFaceAttrib
from ursina import Entity, Vec3, color, curve, destroy, time
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from bloxorz.state import DELTA, Cell, Dir, Orient, State
from gui.anim import animate_later, stop_animations
from gui.board_view import GOAL_OPENING, cell_to_world
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
# Rơi khỏi mép: khối xoay quanh mép ô tới 90° rồi rời mép, rơi tự do mà vẫn giữ đà quay và đà ngang lúc rời
# (không dừng lại rồi rơi từ vận tốc 0). Quá 90° mà vẫn xoay quanh mép thì khối sẽ quặt vào gầm bàn.
ROLL_OFF_END_SPEED = 1.25   # tốc độ quay lúc rời mép, tính theo tốc độ trung bình của cả lần lăn


def _roll_off_curve(s: float) -> float:
    """Lăn ra khỏi mép: bắt đầu từ vận tốc 0 như lần lăn thường, nhưng không dừng ở 90° mà còn quay với
    ROLL_OFF_END_SPEED lần tốc độ trung bình (in_sine là 1,57 lần: rời mép quá mạnh, khối như bị hút xuống).
    Đa thức bậc ba f(0) = 0, f'(0) = 0, f(1) = 1, f'(1) = ROLL_OFF_END_SPEED."""
    k = ROLL_OFF_END_SPEED
    return (k - 2) * s ** 3 + (3 - k) * s ** 2


TUMBLE_CURVE = _roll_off_curve
ROLL_OFF_STRETCH = 1.4   # lăn ra khỏi mép chậm hơn lần lăn thường chừng này lần: đà rời mép nhẹ, nhìn rõ khối đổ
TIP_SHARE = 0.4      # khối nằm hụt một ô: phần thời gian đổ nghiêng quanh mép trước khi rời mép
GRAVITY = 18.0       # đơn vị/giây² khi rơi tự do (cách điệu cho hợp nhịp hoạt ảnh, không theo tỉ lệ thật)
SPIN_DAMP = 3.0      # tốc độ quay giảm dần theo e^(-k·t) sau khi rời mép, để khối không quay tít
DRIFT_DAMP = 3.5     # đà ngang cũng giảm dần, khối không văng quá xa khỏi bàn (khoảng 2–3 ô)
PUSH = 1.5           # đơn vị/giây đẩy thêm ra phía ngoài lúc rời mép, để khối không cọ vào thành ô
SHADOW_SOFT = 1.55   # bóng rộng hơn đáy khối chừng này lần, mép mờ dần
SHADOW_FADE = 2.5    # khối cao hơn mặt sàn chừng này đơn vị thì bóng mờ hẳn
SINK_TOP = -0.12     # thắng: mặt trên của khối dừng ở độ sâu này, trong lòng lỗ đích (ô dày 0.3)

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


class _Tumble:
    """Một lần rơi khỏi mép: xoay quanh trục ở mép ô (pivot) rồi bay tự do (flight). Thời gian tính từng khung."""

    def __init__(self, piece: Entity, axis: str, angle: float, pivot_time: float,
                 curve_fn: Callable[[float], float], flight_time: float, outward: Vec3) -> None:
        self.piece, self.axis, self.angle = piece, axis, angle
        self.pivot_time, self.curve, self.flight_time = pivot_time, curve_fn, flight_time
        self.outward = outward
        self.t = 0.0
        self.released = False
        # điền lúc rời mép
        self.origin = Vec3(0, 0, 0)    # tâm khối lúc rời mép (hệ tọa độ của BlockView)
        self.spin = 0.0                # độ/giây lúc rời mép
        self.drift = Vec3(0, 0, 0)     # vận tốc ngang lúc rời mép
        self.fall_speed = 0.0          # vận tốc đứng lúc rời mép (âm: đi xuống)


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
        self._tumble: Optional[_Tumble] = None   # đang rơi khỏi mép (do update() điều khiển từng khung)
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
             duration: float, active_before: Optional[int] = None,
             hanging: Iterable[Cell] = (), fall_time: float = 0.0) -> bool:
        """Lật khối (hoặc khối con active_before) 90° quanh cạnh đáy theo direction, tới vị trí moved.

        moved là vị trí ngay sau khi lăn, trước khi công tắc hay ghép khối được xử lý (StepResult.moved).
        hanging: các ô của moved không có sàn đỡ (khối sẽ rơi). Nếu mọi ô khối vừa lăn tới đều hụt thì khối
        lăn thẳng ra khỏi mép rồi rơi luôn, liền một chuyển động, xong sau duration + fall_time giây (như lăn
        thường rồi fall()); khi đó trả về True và
        không cần gọi fall() nữa. Còn lại trả về False (lăn thường; rơi, nếu có, do fall() vẽ sau).
        """
        self.show(before, active_before)
        if before.orient is Orient.SPLIT:
            cell = before.cells()[active_before or 0]
            piece = min(self.cubes, key=lambda cube: (cube.position - cell_to_world(cell, 0.5)).length())
            cells: Sequence[Cell] = (cell,)
        else:
            piece, cells = self.body, before.cells()
        axis, angle = ROLL_AXIS[direction]
        hanging = set(hanging)
        dr, dc = DELTA[direction]
        landing = [(r + dr, c + dc) for r, c in cells] if before.orient is Orient.SPLIT else list(moved.cells())
        if hanging and all(cell in hanging for cell in landing):
            dx, dz = _world_delta(direction)
            # lăn chậm hơn nhưng cú rơi vẫn kết thúc đúng lúc cũ (duration + fall_time), app hẹn giờ theo mốc đó
            pivot_time = min(duration * ROLL_OFF_STRETCH, duration + fall_time * 0.5)
            self._start_tumble(piece, roll_pivot(cells, direction), axis, angle, pivot_time, TUMBLE_CURVE,
                               duration + fall_time - pivot_time, Vec3(dx, 0, dz))
            return True
        self._pivot = Entity(parent=self, position=roll_pivot(cells, direction))
        piece.world_parent = self._pivot
        self._rolled = piece
        self._pending = (moved, active_after)
        self._pivot.animate(axis, angle, duration=duration, curve=ROLL_CURVE)
        return False

    def _finish_roll(self, apply_pending: bool = True) -> None:
        """Gỡ khối khỏi trục quay; apply_pending thì đặt khối đúng vị trí sau lần lăn."""
        if self._pivot is None:
            return
        pending = self._pending
        self._stop(self._pivot)
        self._rolled.world_parent = self
        destroy(self._pivot)
        self._pivot = self._rolled = self._pending = self._tumble = None
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
        """Khối rơi sau khi đã lăn xong. Khối nằm hụt đúng một ô thì đổ nghiêng qua mép (nhanh dần từ thế cân
        bằng) rồi rời mép, rơi tiếp mà vẫn giữ đà quay; đã tách thì chỉ khối con bị hụt rơi; còn lại (ô dễ vỡ,
        cầu đóng ngay dưới khối sau khi bấm công tắc) rơi thẳng. Lăn ra khỏi mép thì roll() đã vẽ cả cú rơi.
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
            tip = duration * TIP_SHARE
            self._start_tumble(self.body, (a + b) / 2, axis, angle, tip, curve.in_quad, duration - tip,
                               (b - a).normalized())
            return
        self._drop(self.body, duration)

    # ---- rơi khỏi mép ----

    def _start_tumble(self, piece: Entity, pivot: Vec3, axis: str, angle: float, pivot_time: float,
                      curve_fn: Callable[[float], float], flight_time: float, outward: Vec3) -> None:
        """Gắn piece vào trục ở mép ô; update() xoay trục angle độ trong pivot_time giây theo curve_fn, rồi
        cho khối rời mép và rơi tự do flight_time giây. outward: hướng ngang từ sàn ra khoảng trống."""
        self._pivot = Entity(parent=self, position=pivot)
        piece.world_parent = self._pivot
        self._rolled, self._pending = piece, None
        self._tumble = _Tumble(piece, axis, angle, max(pivot_time, 1e-3), curve_fn, flight_time, outward)

    def _advance_tumble(self, dt: float) -> None:
        tumble = self._tumble
        if tumble is None or self._pivot is None:
            return
        tumble.t += dt
        if not tumble.released:
            s = min(tumble.t / tumble.pivot_time, 1.0)
            setattr(self._pivot, tumble.axis, tumble.angle * tumble.curve(s))
            if s < 1.0:
                return
            self._release(tumble)
        # Rơi tự do theo công thức đóng (không cộng dồn theo dt nên không tích sai số): quay quanh tâm khối với
        # tốc độ giảm dần, trôi ngang chậm dần, rơi đứng nhanh dần đều.
        tau = min(tumble.t - tumble.pivot_time, tumble.flight_time)
        spun = (1 - exp(-SPIN_DAMP * tau)) / SPIN_DAMP
        drifted = (1 - exp(-DRIFT_DAMP * tau)) / DRIFT_DAMP
        setattr(self._pivot, tumble.axis, tumble.spin * spun)
        self._pivot.position = (tumble.origin + tumble.drift * drifted
                                + Vec3(0, tumble.fall_speed * tau - GRAVITY * tau * tau / 2, 0))

    def _release(self, tumble: _Tumble) -> None:
        """Khối rời mép: chuyển trục quay về tâm khối, giữ nguyên tốc độ quay và vận tốc tâm khối lúc đó."""
        piece, pivot = tumble.piece, self._pivot
        h = 1e-3
        spin = tumble.angle * (tumble.curve(1.0) - tumble.curve(1.0 - h)) / h / tumble.pivot_time   # độ/giây
        # Vận tốc tâm khối: lùi trục lại đúng góc đã quay trong 1 ms rồi đo, khỏi phụ thuộc quy ước chiều quay
        setattr(pivot, tumble.axis, tumble.angle - spin * h)
        before = Vec3(*piece.getPos(self))
        setattr(pivot, tumble.axis, tumble.angle)
        center = Vec3(*piece.getPos(self))
        velocity = (center - before) / h

        flight = Entity(parent=self, position=center)
        piece.world_parent = flight
        destroy(pivot)
        self._pivot = flight
        tumble.released = True
        tumble.origin, tumble.spin = center, spin
        tumble.drift = Vec3(velocity.x, 0, velocity.z) + tumble.outward * PUSH
        tumble.fall_speed = velocity.y
        self._fade(piece, tumble.flight_time * 0.7, delay=tumble.flight_time * 0.3)

    def sink(self, duration: float) -> None:
        """Thắng: khối đứng thu vừa miệng lỗ đích rồi lọt xuống, dừng lại khi mặt trên nằm trong lòng lỗ
        (dưới mặt sàn SINK_TOP) để vẫn nhìn thấy khối qua miệng lỗ."""
        self._finish_roll()
        narrow = 0.1
        fit = GOAL_OPENING * 0.97 / SIZE
        self.body.outline.animate("alpha", 0, duration=narrow, curve=curve.linear)
        self.body.animate_scale(Vec3(fit, 1, fit), duration=narrow, curve=curve.out_quad)
        animate_later(self.body, "y", SINK_TOP - SIZE, duration - narrow, narrow, curve.in_quad)

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
        self._advance_tumble(time.dt)
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
            bottom = center.y - extent_y     # độ cao của đáy khối so với mặt sàn
            shadow.x, shadow.z = center.x, center.z
            shadow.scale = Vec3(2 * extent_x * SHADOW_SOFT, 2 * extent_z * SHADOW_SOFT, 1)
            # đáy đã xuống dưới mặt sàn (rơi, lọt lỗ đích): bỏ bóng, nếu không bóng phủ tối miệng lỗ
            shadow.alpha = COLORS["shadow"].a * max(0.0, 1 - bottom / SHADOW_FADE) if bottom > -0.05 else 0

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
