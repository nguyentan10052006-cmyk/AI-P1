"""Khối 1×1×2 và hai khối con (V19, hoạt ảnh tách và ghép ở V20). Chỉ vẽ theo State; luật nằm ở bloxorz.rules (docs/07 §5).

Kích thước theo docs/07 §4: khối đứng có tâm y = 1 (cao 2); khối nằm và khối con có tâm y = 0.5.
"""
from __future__ import annotations

from itertools import permutations
from typing import List, Optional, Tuple

from ursina import Entity, Vec3, color, curve
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from bloxorz.state import Orient, State
from gui.board_view import cell_to_world

SIZE = 0.96   # nhỏ hơn ô một chút để thấy viền giữa khối và sàn
COLORS = {
    "block": color.hex("#f0f6fc"),
    "active": color.hex("#f0f6fc"),   # khối con đang điều khiển
    "idle": color.hex("#7d8896"),     # khối con còn lại
    "edge": color.hex("#38bdf8"),     # viền sáng giúp khối nổi trên sàn xám
}
EDGE_ALPHA = {"active": 0.9, "idle": 0.25}

Transform = Tuple[Vec3, Vec3]   # (vị trí tâm, kích thước)


def piece_transforms(state: State) -> List[Transform]:
    """Vị trí và kích thước của từng khối cần vẽ: 1 khối khi chưa tách, 2 khối con khi đã tách."""
    if state.orient is Orient.SPLIT:
        return [(cell_to_world(cell, 0.5), Vec3(SIZE, SIZE, SIZE)) for cell in state.cells()]
    r, c = state.pos
    if state.orient is Orient.STANDING:
        return [(cell_to_world(state.pos, 1.0), Vec3(SIZE, 2 * SIZE, SIZE))]
    if state.orient is Orient.HORIZONTAL:
        return [(Vec3(c + 0.5, 0.5, -r), Vec3(2 * SIZE, SIZE, SIZE))]
    return [(Vec3(c, 0.5, -(r + 0.5)), Vec3(SIZE, SIZE, 2 * SIZE))]


class BlockView(Entity):
    """Luôn giữ 2 entity; khi chưa tách chỉ bật entity đầu."""

    def __init__(self, state: State, **kwargs) -> None:
        super().__init__(**kwargs)
        self.pieces = [Entity(parent=self, model="cube", color=COLORS["block"], shader=lit_with_shadows_shader)
                       for _ in range(2)]
        self.edges = [Entity(parent=piece, model="wireframe_cube", color=COLORS["edge"], shader=unlit_shader,
                             scale=1.004) for piece in self.pieces]
        self.show(state)

    def show(self, state: State, active_cube: Optional[int] = None, duration: float = 0.0) -> None:
        """Đặt khối theo state. duration > 0 thì trượt tới vị trí mới (hoạt ảnh đơn giản)."""
        transforms = piece_transforms(state)
        was_enabled = [piece.enabled for piece in self.pieces]
        origin = next((p.position for p in self.pieces if p.enabled), None)
        if len(transforms) == 2 and not all(was_enabled) and origin is not None:
            for piece in self.pieces:   # vừa tách: cả hai khối con xuất phát từ chỗ khối cũ
                piece.position = origin
        order = self._match(transforms) if len(transforms) == 2 else [0]
        for piece in self.pieces:
            piece.enabled = False
        for index, (position, scale) in zip(order, transforms):
            piece = self.pieces[index]
            piece.enabled = True
            if duration > 0:
                piece.animate_position(position, duration=duration, curve=curve.linear)
                piece.animate_scale(scale, duration=duration, curve=curve.linear)
            else:
                for animation in piece.animations:   # bấm R lúc đang rơi: dừng hoạt ảnh rơi cũ
                    animation.kill()
                piece.animations.clear()
                piece.position, piece.scale = position, scale
        self._paint(state, order, active_cube)

    def drop(self, depth: float, duration: float) -> None:
        """Hoạt ảnh rơi (thua) hoặc lọt xuống lỗ đích (thắng)."""
        for piece in self.pieces:
            if piece.enabled:
                piece.animate_y(piece.y - depth, duration=duration, curve=curve.in_quad)

    def _match(self, transforms: List[Transform]) -> List[int]:
        """Gán 2 khối con cho 2 entity sao cho mỗi entity đi quãng ngắn nhất.

        Engine luôn sắp hai khối con để pos < pos2, nên sau một bước chỉ số của khối vừa đi có thể đổi;
        ghép theo khoảng cách để entity không nhảy chéo sang chỗ của khối kia.
        """
        def cost(order) -> float:
            return sum((self.pieces[i].position - transforms[k][0]).length() for k, i in enumerate(order))
        return list(min(permutations(range(2)), key=cost))

    def _paint(self, state: State, order: List[int], active_cube: Optional[int]) -> None:
        if state.orient is not Orient.SPLIT or active_cube is None:
            self.pieces[order[0]].color = COLORS["block"]
            self.edges[order[0]].alpha = EDGE_ALPHA["active"]
            return
        for k, index in enumerate(order):
            role = "active" if k == active_cube else "idle"
            self.pieces[index].color = COLORS[role]
            self.edges[index].alpha = EDGE_ALPHA[role]
