"""Font và thành phần giao diện dùng chung cho gui/ (GAME_UI_UX_SPECIFICATION §2).

Font Be Vietnam Pro (SIL Open Font License 1.1, gui/fonts/OFL.txt): thiết kế cho tiếng Việt nên dấu đặt
cân, rõ ở cỡ nhỏ. Ursina nạp font qua loader của Panda3D, nên đường dẫn đổi sang dạng của Panda3D.

Thẻ (card) kiểu kính mờ: nền hơi trong để vẫn thấy bàn phía sau, một lớp sáng rất nhẹ ở nửa trên, viền
mảnh và bóng mềm phía dưới để thẻ tách khỏi nền. Không có vệt phản chiếu, nên không trông như mặt gương.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from panda3d.core import Filename
from ursina import Entity, Quad, Text, color

FONTS_DIR = Path(__file__).resolve().parent / "fonts"


def _font(name: str) -> str:
    return Filename.fromOsSpecific(str(FONTS_DIR / name)).getFullpath()


FONT_REGULAR = _font("BeVietnamPro-Regular.ttf")
FONT_SEMIBOLD = _font("BeVietnamPro-SemiBold.ttf")
FONT_BOLD = _font("BeVietnamPro-Bold.ttf")

PANEL = color.hex("#1c2632")        # nền thẻ (ui_panel)
PANEL_EDGE = color.hex("#3a4b5e")   # viền mảnh quanh thẻ
MUTED = color.hex("#9aa3ad")
ACCENT = color.hex("#38bdf8")
CARD_ALPHA = 0.84      # độ đục của nền thẻ: đủ đọc chữ, vẫn thấy lờ mờ bàn phía sau
SHINE_ALPHA = 0.08     # lớp sáng ở mép trên, mờ dần xuống: rất nhẹ, chỉ để thẻ có chiều sâu
SHADOW_ALPHA = 0.35
CORNER = 0.012         # bán kính bo góc (đơn vị camera.ui)


def use_fonts() -> None:
    """Đặt font mặc định cho mọi Text và Button tạo sau lời gọi này."""
    Text.default_font = FONT_REGULAR


def _rounded(width: float, height: float) -> Quad:
    return Quad(radius=CORNER / height, aspect=width / height)   # Quad đo bán kính theo chiều cao của mesh


def card(parent: Entity, x: float, y: float, width: float, height: float, alpha: float = CARD_ALPHA,
         tint: Optional[color.Color] = None) -> Entity:
    """Thẻ nền bo góc, góc trên trái tại (x, y); trả về entity nền (nội dung đặt ở z < 0 để nằm trên)."""
    shadow = Entity(parent=parent, color=color.rgba(0, 0, 0, SHADOW_ALPHA), origin=(-0.5, 0.5))
    edge = Entity(parent=parent, color=PANEL_EDGE, origin=(-0.5, 0.5))
    bg = Entity(parent=parent, color=tint or PANEL, origin=(-0.5, 0.5))
    # vertical_gradient của Ursina đục ở dưới, trong ở trên: lật dọc để sáng ở mép trên rồi mờ dần, không có mép cắt
    shine = Entity(parent=parent, color=color.rgba(1, 1, 1, SHINE_ALPHA), origin=(-0.5, 0.5))
    bg.shadow, bg.edge, bg.shine, bg.card_alpha = shadow, edge, shine, alpha
    resize_card(bg, width, height, x, y)
    return bg


def resize_card(bg: Entity, width: float, height: float, x: Optional[float] = None,
                y: Optional[float] = None) -> None:
    """Đổi cỡ (và vị trí góc trên trái nếu có) của thẻ; dựng lại mesh bo góc để góc không bị kéo méo."""
    x = bg.x if x is None else x
    y = bg.y if y is None else y
    layers = ((bg.shadow, 0.006, (0.0, -0.006), 0.03, SHADOW_ALPHA),     # bóng: rộng hơn, lệch xuống dưới
              (bg.edge, 0.003, (-0.0015, 0.0015), 0.025, bg.card_alpha),
              (bg, 0.0, (0.0, 0.0), 0.02, bg.card_alpha),
              (bg.shine, 0.0, (0.0, 0.0), 0.015, SHINE_ALPHA))  # lớp sáng: phần trên, mờ dần xuống
    for entity, grow, (dx, dy), z, alpha in layers:
        if entity is bg.shine:
            # quad thường (có UV chuẩn cho dải chuyển màu; Quad bo góc của Ursina không có), phủ hết bề ngang
            # nhưng bắt đầu ngay dưới phần bo góc nên không lòi ra ở góc
            w, h = width, max(0.01, min(height * 0.6, 0.12))
            dy = -CORNER
            entity.model = "quad"
            entity.texture = "vertical_gradient"   # đổi model thì Ursina bỏ texture cũ: gắn lại
            entity.texture_scale = (1, -1)
        else:
            w, h = width + grow, height + grow
            entity.model = _rounded(w, h)
        entity.origin = (-0.5, 0.5)   # đổi model thì Ursina bỏ origin cũ
        entity.position = (x + dx, y + dy, z)
        entity.scale = (w, h)
        entity.alpha = alpha


def heading(parent: Entity, text: str, x: float, y: float, scale: float = 0.72) -> Text:
    """Tiêu đề nhỏ viết hoa của một thẻ."""
    return Text(text, parent=parent, position=(x, y), origin=(-0.5, 0.5), scale=scale, color=MUTED,
                font=FONT_SEMIBOLD)
