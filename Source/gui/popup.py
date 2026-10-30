"""Hộp thông báo khi kết thúc màn: thắng hoặc rơi (chỉ vẽ, không giữ trạng thái chơi; docs/07 §5).

Hiện giữa vùng bàn chơi (không che khung kết quả bên trái và cột nút bên phải), có tiêu đề, vài dòng chi tiết
và các nút hành động tiếp theo. Không chặn phần còn lại của giao diện: các nút Giải, phím R, N, P vẫn dùng
được; chơi lại hoặc đổi màn thì app.py ẩn hộp.

Kéo thả: giữ chuột trái ở chỗ bất kỳ trên hộp (trừ các nút) rồi kéo; hộp không ra khỏi màn hình. Vị trí người
chơi đã kéo tới được giữ cho các lần hiện sau trong lần chạy này.
"""
from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

from ursina import Button, Circle, Entity, Quad, Text, Vec3, camera, color, curve, mouse, window

from gui.anim import stop_animations
from gui.theme import FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD, MUTED, card

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
        card(self.box, -WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT)
        # Vùng nắm để kéo: phủ cả hộp, nằm dưới chữ và các nút (nút có collider riêng nên vẫn bấm được)
        self.handle = Button(parent=self.box, model="quad", color=color.clear, highlight_color=color.clear,
                             pressed_color=color.clear, scale=(WIDTH, HEIGHT), z=0.01)
        self.handle.highlight_scale = 1
        for i in range(3):   # dấu tay nắm ở giữa mép trên
            for row in range(2):
                Entity(parent=self.box, model=Circle(resolution=8, radius=0.5), color=MUTED, alpha=0.55,
                       scale=0.0055, position=((i - 1) * 0.011, HEIGHT / 2 - 0.011 - row * 0.009, -0.005))
        self._drag: Optional[Vec3] = None      # khoảng lệch giữa hộp và chuột khi đang kéo
        self.user_position: Optional[Vec3] = None   # vị trí người chơi đã kéo tới
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
        stop_animations(self)   # move_to() còn dở sẽ kéo hộp khỏi vị trí vừa đặt
        self._drag = None
        if self.user_position is not None:
            self.position = self._clamp(self.user_position)
        else:
            self.position = (x, 0, self.z)
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
        """Bàn được căn lại (khung kết quả hiện hoặc ẩn): hộp đi theo tâm vùng bàn, trừ khi người chơi đã kéo."""
        if self.user_position is None:
            self.animate_x(x, duration=0.2, curve=curve.out_quad)

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        if key == "left mouse down" and mouse.hovered_entity is self.handle:
            stop_animations(self)
            self._drag = self.position - Vec3(mouse.x, mouse.y, self.z)
        elif key == "left mouse up":
            self._drag = None

    def update(self) -> None:
        if self._drag is None:
            return
        if not mouse.left:   # nhả chuột ngoài cửa sổ thì không nhận được "left mouse up"
            self._drag = None
            return
        self.position = self._clamp(Vec3(mouse.x, mouse.y, self.z) + self._drag)
        self.user_position = Vec3(self.position)

    def _clamp(self, position: Vec3) -> Vec3:
        """Giữ cả hộp trong màn hình."""
        half_w, half_h = WIDTH / 2 + 0.01, HEIGHT / 2 + 0.01
        x = min(max(position.x, window.left.x + half_w), window.right.x - half_w)
        y = min(max(position.y, window.bottom.y + half_h), window.top.y - half_h)
        return Vec3(x, y, self.z)

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
