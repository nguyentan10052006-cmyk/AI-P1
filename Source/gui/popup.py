"""Hộp thông báo khi kết thúc màn: thắng hoặc rơi (chỉ vẽ, không giữ trạng thái chơi; docs/07 §5).

Hiện giữa vùng bàn chơi (không che khung kết quả bên trái và cột nút bên phải), có tiêu đề, vài dòng chi tiết
và các nút hành động tiếp theo. Không chặn phần còn lại của giao diện: các nút Giải, phím R, N, P vẫn dùng
được; chơi lại hoặc đổi màn thì app.py ẩn hộp.
"""
from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

from ursina import Button, Entity, Quad, Text, camera, color, curve

from gui.anim import stop_animations
from gui.theme import FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD, MUTED, PANEL, PANEL_EDGE

WIDTH, HEIGHT = 0.6, 0.3
PAD = 0.03
BUTTON_H = 0.052
COLORS = {
    "win": color.hex("#7ee787"),
    "fall": color.hex("#ff7b72"),
    "primary": color.hex("#2f6fd6"),
    "secondary": color.hex("#2f3d4d"),
    "good": color.hex("#7ee787"),
    "warn": color.hex("#f2c94c"),
}

Action = Tuple[str, Callable[[], None], bool]   # (nhãn, hàm gọi khi bấm, là nút chính)


class ResultPopup(Entity):
    """Một hộp dùng lại cho mọi lần kết thúc màn; show() thay nội dung, hide() ẩn."""

    def __init__(self) -> None:
        super().__init__(parent=camera.ui, z=-0.3, enabled=False)
        self.box = Entity(parent=self)
        radius = 0.016 / HEIGHT
        Entity(parent=self.box, model=Quad(radius=radius, aspect=WIDTH / HEIGHT), color=PANEL_EDGE,
               scale=(WIDTH + 0.004, HEIGHT + 0.004), z=0.03)
        Entity(parent=self.box, model=Quad(radius=radius, aspect=WIDTH / HEIGHT), color=PANEL,
               scale=(WIDTH, HEIGHT), z=0.02)
        self.stripe = Entity(parent=self.box, model=Quad(radius=0.5, aspect=0.18 / 0.006), scale=(0.18, 0.006),
                             y=HEIGHT / 2 - 0.018, z=0.01)
        left = -WIDTH / 2 + PAD
        self.title = Text("", parent=self.box, position=(left, HEIGHT / 2 - 0.04), origin=(-0.5, 0.5), scale=1.7,
                          font=FONT_BOLD)
        self.lines: List[Text] = [
            Text("", parent=self.box, position=(left, HEIGHT / 2 - 0.105 - i * 0.034), origin=(-0.5, 0.5),
                 scale=0.95 if i == 0 else 0.85, font=FONT_SEMIBOLD if i == 0 else FONT_REGULAR)
            for i in range(2)]
        self.hint = Text("", parent=self.box, position=(left, -HEIGHT / 2 + 0.03), origin=(-0.5, 0), scale=0.7,
                         color=MUTED)
        self.buttons: List[Button] = []
        self.primary: Optional[Callable[[], None]] = None

    @property
    def visible(self) -> bool:
        return self.enabled

    def show(self, kind: str, title: str, lines: Sequence[Tuple[str, color.Color]], actions: Sequence[Action],
             hint: str, x: float = 0.0) -> None:
        """kind: "win" hoặc "fall" (màu dải trên cùng và tiêu đề). lines: tối đa 2 dòng (chữ, màu)."""
        stop_animations(self.box)
        self.x = x
        self.stripe.color = COLORS[kind]
        self.stripe.x = -WIDTH / 2 + PAD + 0.09
        self.title.text, self.title.color = title, COLORS[kind]
        for text, (line, tint) in zip(self.lines, list(lines) + [("", color.white)] * 2):
            text.text, text.color = line, tint
        self.hint.text = hint
        for button in self.buttons:
            button.enabled = False   # Button bị destroy() trong lúc đang được bấm sẽ lỗi; giữ lại, chỉ ẩn
        self.primary = None
        width = 0.17
        right = WIDTH / 2 - PAD
        for i, (label, on_click, primary) in enumerate(reversed(actions)):
            button = self._button(i)
            button.text = label
            button.on_click = self._wrap(on_click)
            tint = COLORS["primary"] if primary else COLORS["secondary"]
            button.color, button.highlight_color, button.pressed_color = tint, tint.tint(0.15), tint.tint(-0.12)
            button.position = (right - width / 2 - i * (width + 0.012), -HEIGHT / 2 + 0.035 + BUTTON_H / 2 + 0.012)
            button.enabled = True
            if primary:
                self.primary = on_click
        self.enabled = True
        self.box.scale = 0.9
        self.box.animate_scale(1, duration=0.22, curve=curve.out_back)

    def hide(self) -> None:
        self.enabled = False

    def move_to(self, x: float) -> None:
        """Bàn được căn lại (khung kết quả hiện hoặc ẩn): hộp đi theo tâm vùng bàn."""
        self.animate_x(x, duration=0.2, curve=curve.out_quad)

    def press_primary(self) -> bool:
        """Phím Enter: bấm nút chính nếu hộp đang hiện."""
        if self.enabled and self.primary is not None:
            self.primary()
            return True
        return False

    def _button(self, index: int) -> Button:
        while len(self.buttons) <= index:
            button = Button(text=" ", parent=self.box, scale=(0.17, BUTTON_H), radius=0.25, text_size=0.85,
                            z=-0.01)
            button.text_entity.font = FONT_SEMIBOLD
            button.highlight_scale = 1.03
            self.buttons.append(button)
        return self.buttons[index]

    def _wrap(self, on_click: Callable[[], None]) -> Callable[[], None]:
        def click() -> None:
            self.hide()
            on_click()
        return click
