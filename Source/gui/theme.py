"""Font và thành phần giao diện dùng chung cho gui/ (GAME_UI_UX_SPECIFICATION §2).

Font Be Vietnam Pro (SIL Open Font License 1.1, gui/fonts/OFL.txt): thiết kế cho tiếng Việt nên dấu đặt
cân, rõ ở cỡ nhỏ. Ursina nạp font qua loader của Panda3D, nên đường dẫn đổi sang dạng của Panda3D.
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
PANEL_EDGE = color.hex("#2b3a4a")   # viền mảnh quanh thẻ
MUTED = color.hex("#9aa3ad")
ACCENT = color.hex("#38bdf8")


def use_fonts() -> None:
    """Đặt font mặc định cho mọi Text và Button tạo sau lời gọi này."""
    Text.default_font = FONT_REGULAR


def card(parent: Entity, x: float, y: float, width: float, height: float, alpha: float = 0.92,
         tint: Optional[color.Color] = None) -> Entity:
    """Thẻ nền bo góc, góc trên trái tại (x, y); trả về entity nền (z = 0.02 để nằm sau nội dung)."""
    radius = 0.012 / height   # Quad đo bán kính theo chiều cao của mesh trước khi co giãn
    edge = Entity(parent=parent, model=Quad(radius=radius, aspect=width / height), color=PANEL_EDGE,
                  origin=(-0.5, 0.5), position=(x - 0.0015, y + 0.0015, 0.025), scale=(width + 0.003, height + 0.003))
    edge.alpha = alpha
    bg = Entity(parent=parent, model=Quad(radius=radius, aspect=width / height), color=tint or PANEL,
                origin=(-0.5, 0.5), position=(x, y, 0.02), scale=(width, height))
    bg.alpha = alpha
    bg.edge = edge
    return bg


def heading(parent: Entity, text: str, x: float, y: float, scale: float = 0.72) -> Text:
    """Tiêu đề nhỏ viết hoa của một thẻ."""
    return Text(text, parent=parent, position=(x, y), origin=(-0.5, 0.5), scale=scale, color=MUTED,
                font=FONT_SEMIBOLD)
