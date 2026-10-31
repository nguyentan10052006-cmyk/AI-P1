"""Trang chủ khi mở game: tên game, nút Chơi ngay, Chọn màn, Cách chơi, Thoát (chỉ vẽ, docs/07 §5).

Bố cục kiểu màn hình chờ của game: bàn chơi 3D thật của màn đầu nằm phía sau, camera đung đưa chậm (app.py
điều khiển); nửa trái phủ một lớp tối mờ dần sang phải để chữ và nút dễ đọc mà vẫn thấy bàn. Tên game, dòng
giới thiệu và cột nút canh trái; dòng chân trang ghi tên môn học và phím tắt.

Chọn nút bằng chuột hoặc mũi tên lên / xuống (W S) rồi Enter / Space. Trang chủ không giữ trạng thái chơi: mỗi nút chỉ gọi
lại hàm do app.py truyền vào.
"""
from __future__ import annotations

import math
from typing import Callable, List, Optional, Sequence, Tuple

from ursina import Button, Entity, Mesh, Quad, Text, Vec3, camera, color, curve, time, window
from ursina.shaders import unlit_shader

from gui.anim import animate_later, stop_animations
from gui.theme import ACCENT, FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD, MUTED

COLORS = {
    "primary": color.hex("#2f6fd6"),
    "button": color.hex("#2f3d4d"),
    "quit": color.hex("#3a2a30"),
    "shade": color.hex("#0b0f14"),
}
LEFT_PAD = 0.11         # lề trái của khối chữ và nút, tính từ mép trái màn hình
BUTTON_W, BUTTON_H = 0.34, 0.062
BUTTON_GAP = 0.016
SELECT_BAR_W = 0.006    # vạch sáng bên trái nút đang chọn
HOVER_SCALE = 1.03
INTRO_TIME = 0.45       # chữ và nút trượt vào khi trang chủ hiện
INTRO_STAGGER = 0.06    # các nút vào lần lượt cách nhau chừng này giây
PULSE_SPEED = 2.2       # vạch chọn nhấp nháy nhẹ

Item = Tuple[str, str, Callable[[], None]]   # (khóa, nhãn, hàm gọi khi bấm)


class HomeScreen(Entity):
    """Trang chủ; show() hiện và chạy hoạt ảnh vào, hide() ẩn. is_blocked(): đang có bảng phủ (chọn màn,
    chú giải) mở phía trên thì không nhận phím."""

    def __init__(self, items: Sequence[Item], is_blocked: Callable[[], bool] = lambda: False,
                 subtitle: str = "") -> None:
        super().__init__(parent=camera.ui, z=-0.4, enabled=False)
        self.is_blocked = is_blocked
        left = window.left.x + LEFT_PAD

        # Lớp tối: đục ở mép trái, trong dần tới khoảng giữa màn hình; vạch mờ ở đáy cho dòng chân trang
        shade = COLORS["shade"]
        solid, clear = color.Color(shade[0], shade[1], shade[2], 0.9), color.Color(shade[0], shade[1], shade[2], 0)
        x0, x1, x2 = window.left.x - 0.05, window.left.x + 0.62, window.left.x + 1.15
        y0, y1 = window.bottom.y - 0.05, window.top.y + 0.05
        Entity(parent=self, z=0.05, shader=unlit_shader, model=Mesh(
            vertices=[(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0), (x2, y0, 0), (x2, y1, 0)],
            triangles=[(0, 1, 2), (0, 2, 3), (1, 4, 5), (1, 5, 2)],
            colors=[solid, solid, solid, solid, clear, clear]))

        # ---- tên game ----
        self.header = Entity(parent=self)
        Entity(parent=self.header, model=Quad(radius=0.5, aspect=0.07 / 0.006), color=ACCENT,
               scale=(0.07, 0.006), position=(left + 0.035, 0.305))
        Text("ĐỒ ÁN TRÍ TUỆ NHÂN TẠO", parent=self.header, position=(left + 0.085, 0.305), origin=(-0.5, 0),
             scale=0.78, color=ACCENT, font=FONT_SEMIBOLD)
        Text("BLOXORZ", parent=self.header, position=(left - 0.006, 0.27), origin=(-0.5, 0.5), scale=5.2,
             font=FONT_BOLD)
        Text("S O L V E R", parent=self.header, position=(left, 0.14), origin=(-0.5, 0.5), scale=1.5,
             color=ACCENT, font=FONT_SEMIBOLD)
        Text("Lăn khối 1 × 1 × 2 vào lỗ đích, hoặc để AI\ntìm đường bằng BFS, DFS, UCS và A*.",
             parent=self.header, position=(left, 0.07), origin=(-0.5, 0.5), scale=0.9, line_height=1.3,
             color=MUTED, font=FONT_REGULAR)

        # ---- cột nút ----
        self.buttons: List[Button] = []
        self.actions: List[Callable[[], None]] = []
        self.tints: List[color.Color] = []
        top = -0.05
        for i, (key, label, action) in enumerate(items):
            tint = COLORS["primary"] if i == 0 else COLORS["quit"] if key == "quit" else COLORS["button"]
            button = Button(text=label, parent=self, scale=(BUTTON_W, BUTTON_H), color=tint, radius=0.22,
                            text_size=1.05 if i == 0 else 0.9,
                            position=(left + BUTTON_W / 2, top - BUTTON_H / 2 - i * (BUTTON_H + BUTTON_GAP)),
                            on_click=lambda i=i: self._activate(i))
            button.text_entity.font = FONT_BOLD if i == 0 else FONT_SEMIBOLD
            button.highlight_color = tint.tint(0.15)
            button.pressed_color = tint.tint(-0.12)
            button.highlight_scale = HOVER_SCALE
            button.home_x = button.x
            self.buttons.append(button)
            self.actions.append(action)
            self.tints.append(tint)
        # quad thường: Quad bo góc của Ursina vẽ sai khi khung hẹp hơn chiều cao (aspect < 1)
        self.select_bar = Entity(parent=self, model="quad", color=ACCENT, scale=(SELECT_BAR_W, BUTTON_H * 0.6),
                                 z=-0.01)
        self.selected = 0
        self._last_hover: Optional[int] = None

        # ---- chân trang ----
        self.footer = Entity(parent=self)
        Text(subtitle, parent=self.footer, position=(left, window.bottom.y + 0.045), origin=(-0.5, 0), scale=0.72,
             color=MUTED)
        Text("W / S hoặc mũi tên: chọn   ·   Enter: bắt đầu   ·   F1: phím tắt", parent=self.footer,
             position=(window.right.x - 0.03, window.bottom.y + 0.045), origin=(0.5, 0), scale=0.72, color=MUTED)
        self._select(0)

    # ---- hiện, ẩn ----

    def show(self) -> None:
        self.enabled = True
        self._select(0)
        self._last_hover = None
        # Tên game trượt từ trên xuống, các nút trượt từ trái sang lần lượt, chân trang hiện sau cùng
        stop_animations(self.header)
        self.header.y = 0.04
        self.header.animate_y(0, duration=INTRO_TIME, curve=curve.out_quad)
        for i, button in enumerate(self.buttons):
            stop_animations(button)
            button.x = button.home_x - 0.12
            animate_later(button, "x", button.home_x, INTRO_TIME, 0.12 + i * INTRO_STAGGER, curve.out_back)
        self._place_bar()

    def hide(self) -> None:
        self.enabled = False

    @property
    def visible(self) -> bool:
        return self.enabled

    # ---- chọn, bấm ----

    def _select(self, index: int) -> None:
        self.selected = index % len(self.buttons)
        for i, button in enumerate(self.buttons):
            tint = self.tints[i]
            button.color = tint.tint(0.12) if i == self.selected else tint
        self._place_bar()

    def _place_bar(self) -> None:
        button = self.buttons[self.selected]
        self.select_bar.position = (button.x - BUTTON_W / 2 - 0.014, button.y, -0.01)

    def _activate(self, index: int) -> None:
        if not self.enabled or self.is_blocked():
            return
        self._select(index)
        self.actions[index]()

    def input(self, key: str) -> None:
        if not self.enabled or self.is_blocked():
            return
        if key in ("down arrow", "s", "down arrow hold", "s hold"):
            self._select(self.selected + 1)
        elif key in ("up arrow", "w", "up arrow hold", "w hold"):
            self._select(self.selected - 1)
        elif key in ("enter", "space"):
            self._activate(self.selected)

    def update(self) -> None:
        # rê chuột lên nút nào thì nút đó thành nút đang chọn (bàn phím và chuột dùng chung một vạch chọn)
        hovered = next((i for i, button in enumerate(self.buttons) if button.hovered), None)
        if hovered is not None and hovered != self._last_hover:
            self._select(hovered)
        self._last_hover = hovered
        self._place_bar()   # nút đang trượt vào thì vạch đi theo
        self.select_bar.alpha = 0.7 + 0.3 * math.sin(time.time() * PULSE_SPEED * math.pi)
