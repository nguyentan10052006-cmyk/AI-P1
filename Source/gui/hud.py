"""Bảng điều khiển (V21): điều hướng màn, giải bằng 4 thuật toán, So sánh, Hủy, góc nhìn, kết quả, phím tắt.

Chỉ vẽ và gọi lại các hàm do app.py truyền vào; không giữ trạng thái chơi, không gọi solver (docs/07 §5).

Bố cục (GAME_UI_UX_SPECIFICATION §3):
- Thanh điều hướng ở góc phải trên: Chú giải, Màn đầu, < Trước, Chọn màn, Sau >, Chơi lại.
- Cột phải gồm hai thẻ: "TÌM LỜI GIẢI" (lưới 2 × 2 nút BFS, DFS, UCS, A*, nút So sánh và Hủy) và
  "GÓC NHÌN" (nhãn góc hiện tại và 6 nút camera). Nhóm theo việc, việc hay dùng ở trên.
- Khung kết quả ở cột trái; bảng chọn màn, bảng phím tắt (F1) và bảng chú giải các loại ô (G) hiện giữa
  màn hình.
"""
from __future__ import annotations

import math
import textwrap
import time
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from ursina import Button, Circle, Entity, Mesh, Quad, Text, Vec3, camera, color, curve, destroy, window

from gui.block_view import COLORS as BLOCK_COLORS
from gui.board_view import CLOSED_BRIDGE_ALPHA, TILE_SHADE
from gui.board_view import COLORS as TILE_COLORS
from gui.theme import FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD, card, heading, resize_card

# Tên hiện trên nút và trong bảng So sánh, theo khóa của solvers.ALGORITHMS
LABELS = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A*", "astar_m": "A* (h_M)"}
SOLVE_NAMES = ("bfs", "dfs", "ucs", "astar")

COLORS = {
    "button": color.hex("#2f3d4d"),
    "solve": color.hex("#2f6fd6"),
    "cancel": color.hex("#b0413e"),
    "disabled": color.hex("#26313d"),
    "panel": color.hex("#1c2632"),   # sáng hơn nền #0b0f14–#18212b một chút để khung nổi lên
    "ok": color.hex("#7ee787"),
    "warn": color.hex("#f2c94c"),
    "bad": color.hex("#ff7b72"),
    "muted": color.hex("#9aa3ad"),
    "accent": color.hex("#38bdf8"),
    "cam": color.hex("#253241"),
}
HOVER_SCALE = 1.03          # nút phóng nhẹ khi rê chuột (GAME_UI_UX_SPECIFICATION §3.2)
MARGIN = 0.02               # lề với mép màn hình
GAP = 0.008                 # khoảng cách giữa hai nút
NAV_H = 0.044
NAV_BUTTONS = (("legend", "Chú giải", 0.1), ("new", "Màn đầu", 0.1), ("prev", "‹ Trước", 0.092),
               ("pick", "Chọn màn", 0.11), ("next", "Sau ›", 0.085), ("restart", "Chơi lại", 0.1))
COL_W = 0.27                # bề rộng cột thẻ bên phải
CARD_PAD = 0.016
SOLVE_H = 0.052
CAM_H = 0.04
# Khung kết quả là cột dọc bên trái, dưới tên màn và số bước, trên dòng phím tắt; khi khung hiện,
# camera căn bàn vào vùng trống giữa khung và cột thẻ (app.py) nên khung không che bàn
# Khung gọn: rộng PANEL_W khi hiện kết quả một thuật toán, rộng vừa bảng khi So sánh (Hud._fit_panel)
PANEL_TOP, PANEL_BOTTOM, PANEL_W = 0.34, -0.44, 0.38
PAD = 0.016               # lề trong của khung
STATUS_SCALE, DETAILS_SCALE = 0.92, 0.78
LINE_H = 0.0202           # chiều cao một dòng chữ ở DETAILS_SCALE
DETAILS_SPACING = 1.25    # giãn dòng phần chi tiết cho dễ đọc
DETAILS_LINE_H = LINE_H * DETAILS_SPACING
STATUS_WRAP, DETAILS_WRAP = 30, 40   # số ký tự mỗi dòng trước khi xuống hàng, vừa bề rộng PANEL_W
# Dòng trạng thái ngắt theo bề rộng đo bằng font thật (Hud._wrap_status): chừa chỗ cho chữ "H: ẩn" cùng dòng
HINT_GAP = 0.012          # khoảng cách giữa dòng trạng thái và chữ "H: ẩn"
TABLE_Y = -0.054          # đỉnh bảng So sánh và phần chi tiết khi dòng trạng thái chỉ có một dòng
ROW_H = 0.027             # chiều cao một dòng của bảng So sánh
TABLE_SCALE = 0.64
DOT_SIZE = 0.013          # chấm trạng thái trước dòng đầu của khung kết quả
DOT_GAP = 0.022           # dòng trạng thái lùi sang phải chừng này để chừa chỗ cho chấm
# Cột của bảng So sánh: (tiêu đề, các chuỗi dài nhất có thể hiện trong cột). Vị trí cột tính lúc dựng HUD
# theo bề rộng thật của chữ (Hud._table_layout), nên đổi font không làm các cột dính nhau. Chi phí lẻ theo
# hàm chi phí V13, ví dụ DFS màn 23: 1525.37.
TABLE_COLUMNS = (("Thuật toán", ("A* (h_M)",)), ("Kết quả", ("Giải được", "Vô nghiệm", "chạy 59.9s", "Hết giờ")),
                 ("Bước", ("9999",)), ("Chi phí", ("9999.99",)), ("Mở rộng", ("999999",)), ("Giây", ("59.99",)),
                 ("MB", ("999.9",)))
TABLE_GAP = 0.014
SHORT_SUMMARY = {"Không có lời giải": "Vô nghiệm"}   # ô của bảng hẹp, khung một thuật toán vẫn ghi đầy đủ
# Không dùng "<" trong chữ: Ursina hiểu "<...>" là thẻ định dạng và bỏ ký tự; dùng ‹ › (font có sẵn)
# Bảng phím tắt (F1): (phím, tác dụng)
SHORTCUTS = (
    ("W A S D / mũi tên", "Lăn khối"), ("Space", "Đổi khối con khi đã tách"), ("R", "Chơi lại màn"),
    ("N / P", "Màn sau / màn trước"), ("Ctrl+K", "Mở lưới chọn màn"), ("Enter", "Nút chính của hộp kết thúc"),
    ("H", "Ẩn / hiện khung kết quả"), ("G", "Chú giải các loại ô"), ("Q / E", "Nghiêng camera trái / phải"),
    ("Z / X", "Hạ thấp / nâng cao góc"),
    ("T", "Nhìn từ đỉnh"), ("F", "Góc mặc định"), ("Chuột phải + kéo", "Chỉnh góc tự do"),
    ("Con lăn chuột", "Thu phóng"), ("Esc", "Đóng hộp, lưới chọn màn"), ("F1", "Bật / tắt bảng này"),
)

# Bảng chú giải (phím G, kịch bản video docs/06 §5 đoạn 2): (mẫu ô, tên, cách hoạt động). Mẫu vẽ cùng màu và ký hiệu
# như trên bàn (board_view.COLORS), nên đổi màu ô trên bàn thì chú giải đổi theo.
LEGEND = (
    ("floor", "Sàn", "Ô thường: khối đứng hay nằm đều được."),
    ("void", "Ô trống", "Không có ô: khối lăn ra ngoài là rơi, thua."),
    ("goal", "Lỗ đích", "Khối phải đứng thẳng trên lỗ mới thắng; nằm ngang qua lỗ thì không."),
    ("fragile", "Ô dễ vỡ (màu cam)", "Chỉ đỡ khối nằm. Khối đứng lên thì ô vỡ và khối rơi."),
    ("block", "Khối 1 × 1 × 2", "Ba tư thế: đứng (chiếm 1 ô), nằm ngang hoặc nằm dọc (chiếm 2 ô)."),
    ("bridge_open", "Cầu đang mở", "Đi được như ô sàn."),
    ("bridge_closed", "Cầu đang đóng", "Như ô trống. Công tắc làm cầu mở, đóng hoặc đổi trạng thái."),
    ("soft", "Công tắc mềm (tròn)", "Kích hoạt khi bất kỳ phần nào của khối chạm vào, kể cả khối con."),
    ("heavy", "Công tắc nặng (chữ X)", "Chỉ kích hoạt khi khối đứng thẳng trên nó."),
    ("split", "Công tắc tách ( )", "Khối đứng lên thì tách đôi; Space đổi khối con, hai khối kề nhau thì ghép lại."),
)
LEGEND_ROWS = 5           # mỗi cột 5 mục: cột trái là ô và khối, cột phải là cầu và công tắc
LEGEND_ROW_H = 0.094
LEGEND_SWATCH = 0.056     # cạnh ô mẫu
LEGEND_WRAP = 44          # số ký tự mỗi dòng giải thích


def outcome_summary(outcome: Mapping) -> tuple[str, color.Color]:
    """Một trong 4 thông báo (docs/07 §6 quy tắc 6) kèm màu: giải được, không có lời giải, hết giờ, lỗi hoặc đã hủy."""
    if outcome.get("ok"):
        if outcome["status"] == "solved":
            return "Giải được", COLORS["ok"]
        return "Không có lời giải", COLORS["warn"]
    if outcome.get("timeout"):
        return "Hết giờ", COLORS["warn"]
    if outcome.get("cancelled"):
        return "Đã hủy", COLORS["muted"]
    return f"Lỗi: {outcome.get('error', '')}", COLORS["bad"]


def _wrap(text: str, width: int) -> str:
    """Ngắt dòng trước khi gán vào Text: wordwrap của Ursina không áp dụng khi đổi .text sau lúc tạo."""
    return "\n".join("\n".join(textwrap.wrap(line, width)) or line for line in text.split("\n"))


def _with_alpha(base: color.Color, alpha: float) -> color.Color:
    return color.Color(base[0], base[1], base[2], alpha)


def _line_count(text: str) -> int:
    return text.count("\n") + 1


def _time_and_memory(outcome: Mapping) -> tuple[str, str]:
    return f"{outcome['time_ms'] / 1000:.2f} s", f"{outcome['peak_kb'] / 1024:.1f} MB"


class Hud(Entity):
    """Thanh điều hướng, cột thẻ bên phải, khung kết quả bên trái, bảng chọn màn và bảng phím tắt."""

    def __init__(self, level_ids: Sequence[str], *, on_new_game: Callable[[], None],
                 on_restart: Callable[[], None], on_pick_level: Callable[[int], None],
                 on_solve: Callable[[str], None], on_compare: Callable[[], None],
                 on_cancel: Callable[[], None],
                 on_prev: Optional[Callable[[], None]] = None,
                 on_next: Optional[Callable[[], None]] = None,
                 on_rotate_cam: Optional[Callable[[float], None]] = None,
                 on_tilt_cam: Optional[Callable[[float], None]] = None,
                 on_toggle_top_down: Optional[Callable[[], None]] = None,
                 on_reset_cam: Optional[Callable[[], None]] = None) -> None:
        super().__init__(parent=camera.ui)
        self.on_pick_level = on_pick_level
        self.on_panel_change: Optional[Callable[[bool], None]] = None   # app.py căn lại camera khi khung hiện/ẩn
        self.panel_hidden = False   # người chơi bấm H để ẩn khung kết quả
        self.buttons: Dict[str, Button] = {}
        right = window.right.x - MARGIN

        # ---- thanh điều hướng ----
        nav_actions = {"legend": self.toggle_legend, "new": on_new_game, "prev": on_prev, "pick": self.toggle_picker,
                       "next": on_next, "restart": on_restart}
        x = right - sum(w for _, _, w in NAV_BUTTONS) - GAP * (len(NAV_BUTTONS) - 1)
        nav_y = window.top.y - MARGIN - NAV_H / 2
        for key, label, width in NAV_BUTTONS:
            if nav_actions[key] is not None:
                tint = COLORS["solve"] if key == "pick" else COLORS["button"]
                self._button(key, label, nav_actions[key], (x + width / 2, nav_y), (width, NAV_H), tint, 0.78)
            x += width + GAP

        # ---- thẻ TÌM LỜI GIẢI ----
        self.dock_left = right - COL_W   # mép trái cột thẻ, dùng để tính vùng trống cho bàn
        left = self.dock_left + CARD_PAD
        inner = COL_W - 2 * CARD_PAD
        top = nav_y - NAV_H / 2 - 0.022
        y = top - CARD_PAD
        heading(self, "TÌM LỜI GIẢI", left, y)
        y -= 0.034
        half = (inner - GAP) / 2
        for i, name in enumerate(SOLVE_NAMES):
            r, c = divmod(i, 2)
            self._button(name, LABELS[name], lambda name=name: on_solve(name),
                         (left + half / 2 + c * (half + GAP), y - SOLVE_H / 2 - r * (SOLVE_H + GAP)),
                         (half, SOLVE_H), COLORS["solve"], 1.0, bold=True)
        y -= 2 * (SOLVE_H + GAP)
        self._button("compare", "So sánh cả 5 thuật toán", on_compare, (left + inner / 2, y - SOLVE_H / 2),
                     (inner, SOLVE_H * 0.85), COLORS["button"], 0.8)
        y -= SOLVE_H * 0.85 + GAP
        self._button("cancel", "Hủy", on_cancel, (left + inner / 2, y - SOLVE_H * 0.4),
                     (inner, SOLVE_H * 0.8), COLORS["cancel"], 0.8)
        y -= SOLVE_H * 0.8 + CARD_PAD
        card(self, self.dock_left, top, COL_W, top - y)
        # Khung sáng bao quanh nút của thuật toán đang chạy (§3.2)
        self.indicator = Entity(parent=self, model=Quad(radius=0.2, mode="line", thickness=2),
                                color=COLORS["accent"], enabled=False, z=-0.02)
        self._highlighted: Optional[str] = None

        # ---- thẻ GÓC NHÌN ----
        top = y - 0.018
        y = top - CARD_PAD
        heading(self, "GÓC NHÌN", left, y)
        y -= 0.03
        self.cam_label = Text("CHÍNH DIỆN", parent=self, position=(left, y), origin=(-0.5, 0.5), scale=0.8,
                              color=COLORS["accent"], font=FONT_SEMIBOLD)
        y -= 0.034
        pairs: List[Tuple[Tuple[str, str, Callable[[], None]], Tuple[str, str, Callable[[], None]]]] = []
        if on_rotate_cam is not None:
            pairs.append((("cam_rot_l", "‹ Trái  Q", lambda: on_rotate_cam(-1)),
                          ("cam_rot_r", "Phải  E ›", lambda: on_rotate_cam(1))))
        if on_tilt_cam is not None:
            pairs.append((("cam_tilt_down", "Hạ thấp  Z", lambda: on_tilt_cam(-1)),
                          ("cam_tilt_up", "Nâng cao  X", lambda: on_tilt_cam(1))))
        if on_toggle_top_down is not None and on_reset_cam is not None:
            pairs.append((("cam_top", "Từ đỉnh  T", on_toggle_top_down), ("cam_reset", "Mặc định  F", on_reset_cam)))
        for pair in pairs:
            for c, (key, label, on_click) in enumerate(pair):
                self._button(key, label, on_click, (left + half / 2 + c * (half + GAP), y - CAM_H / 2),
                             (half, CAM_H), COLORS["cam"], 0.72)
            y -= CAM_H + GAP
        card(self, self.dock_left, top, COL_W, top - y - GAP + CARD_PAD)

        # ---- khung kết quả (cột trái) ----
        self.table_x, table_w = self._table_layout()
        self.table_panel_w = max(PANEL_W, table_w + 2 * PAD)   # bề rộng khung khi hiện bảng So sánh
        self.panel_w = PANEL_W
        self.panel = Entity(parent=self, position=(window.left.x + MARGIN, PANEL_TOP), enabled=False)
        self.panel_right = self.panel.x + self.panel_w
        self._panel_h = 0.08
        self.panel_bg = card(self.panel, 0, 0, self.panel_w, self._panel_h)
        self.hide_hint = Text("H: ẩn", parent=self.panel, position=(self.panel_w - PAD, -PAD), origin=(0.5, 0.5),
                              scale=0.64, color=COLORS["muted"])
        # text=" ": Ursina 7 lỗi khi đặt wordwrap cho Text rỗng; lỗi của solver có thể dài nên phải xuống dòng
        self.status = Text(" ", parent=self.panel, position=(PAD + DOT_GAP, -PAD), origin=(-0.5, 0.5),
                           wordwrap=STATUS_WRAP, font=FONT_SEMIBOLD, scale=STATUS_SCALE)
        # Chấm trạng thái: màu theo kết quả, nhấp nháy khi đang giải (§3.4)
        self.dot = Entity(parent=self.panel, model=Circle(resolution=20, radius=0.5), scale=DOT_SIZE,
                          position=(PAD + DOT_SIZE / 2 + 0.002, -PAD - 0.0125, -0.01), color=color.white)
        self._running = False
        self.details = Text(" ", parent=self.panel, position=(PAD, TABLE_Y), origin=(-0.5, 0.5), scale=DETAILS_SCALE,
                            line_height=DETAILS_SPACING, color=COLORS["muted"], wordwrap=DETAILS_WRAP)
        self.table = Entity(parent=self.panel, position=(PAD, TABLE_Y))
        self._content_bottom = -PAD   # đáy nội dung lần _fit_panel() gần nhất, để dời theo dòng trạng thái
        self._char_w: Dict[str, float] = {}   # bề rộng từng ký tự của dòng trạng thái, đo lần đầu gặp
        self._bars_w = self._probe_width("||")
        self._status_line_h = self.status.size * STATUS_SCALE   # Text.height = số dòng × line_height × size
        self.cells: List[List[Text]] = []   # ô của bảng So sánh, dựng lần đầu khi cần

        # ---- bảng chọn màn, bảng phím tắt ----
        self.current_level = 0
        self.picker_buttons: List[Button] = []
        self.solved_marks: List[Entity] = []   # chấm xanh trên nút các màn đã thắng trong lần chạy này
        self.picker = self._build_picker(level_ids)
        self.help = self._build_help()
        self.legend = self._build_legend()
        self.set_current_level(0)
        self.set_running(False)

    def _button(self, key: str, label: str, on_click: Callable[[], None], position: Tuple[float, float],
                size: Tuple[float, float], tint: color.Color, text_size: float, bold: bool = False) -> Button:
        button = Button(text=label, parent=self, position=position, scale=size, color=tint, text_size=text_size,
                        radius=0.22, on_click=on_click)
        button.text_entity.font = FONT_BOLD if bold else FONT_SEMIBOLD
        button.highlight_color = tint.tint(0.15)
        button.pressed_color = tint.tint(-0.12)
        button.highlight_scale = HOVER_SCALE
        button.base_color = tint
        self.buttons[key] = button
        return button

    def _table_layout(self) -> Tuple[List[float], float]:
        """Vị trí x của từng cột và bề rộng cả bảng: mỗi cột rộng bằng chuỗi dài nhất của nó (đo bằng font
        thật) cộng TABLE_GAP."""
        xs, x, last = [], 0.0, 0.0
        for title, samples in TABLE_COLUMNS:
            xs.append(x)
            widths = []
            for text, font in [(title, FONT_SEMIBOLD)] + [(sample, FONT_REGULAR) for sample in samples]:
                probe = Text(text, parent=self, scale=TABLE_SCALE, font=font)
                widths.append(probe.width * TABLE_SCALE)
                destroy(probe)
            last = max(widths)
            x += last + TABLE_GAP
        return xs, xs[-1] + last

    # ---- chọn màn ----

    def _overlay(self, width: float, height: float, on_close: Callable[[], None]) -> Entity:
        """Lớp phủ tối che bàn (bấm ra ngoài thì đóng) và một thẻ ở giữa màn hình."""
        root = Entity(parent=self, z=-0.5, enabled=False)
        backdrop = Button(parent=root, model="quad", color=color.rgba(0, 0, 0, 0.55), scale=(4, 2), z=0.03,
                          on_click=on_close)
        backdrop.highlight_color = backdrop.pressed_color = backdrop.color
        blocker = Button(parent=root, model="quad", color=color.clear, scale=(width, height), z=0.02,
                         highlight_color=color.clear, pressed_color=color.clear)   # chặn click lọt xuống lớp phủ
        blocker.highlight_scale = 1
        card(root, -width / 2, height / 2, width, height, alpha=0.97)
        return root

    def _build_picker(self, level_ids: Sequence[str]) -> Entity:
        """Lưới nút mã màn nằm giữa màn hình; ẩn cho tới khi bấm "Chọn màn"."""
        cols, size = 11, 0.07
        rows = (len(level_ids) + cols - 1) // cols
        width, height = cols * size + 0.06, rows * size + 0.15
        picker = self._overlay(width, height, self.close_picker)
        Text(parent=picker, text="Chọn màn", origin=(0, 0), y=height / 2 - 0.04, z=-0.01, scale=1.25,
             font=FONT_BOLD)
        Text(parent=picker, text="Ctrl+K hoặc Esc để đóng  ·  chấm xanh: màn đã thắng", origin=(0, 0),
             y=-height / 2 + 0.03, z=-0.01, scale=0.7, color=COLORS["muted"])
        self.picker_buttons.clear()
        self.solved_marks.clear()
        for i, level_id in enumerate(level_ids):
            r, c = divmod(i, cols)
            btn = Button(text=level_id, parent=picker, z=-0.01, scale=size * 0.85, color=COLORS["button"],
                         text_size=0.85, radius=0.2, position=((c - (cols - 1) / 2) * size, height / 2 - 0.115 - r * size),
                         highlight_scale=HOVER_SCALE * 1.05, on_click=lambda i=i: self._pick(i))
            btn.text_entity.font = FONT_SEMIBOLD
            self.picker_buttons.append(btn)
            self.solved_marks.append(Entity(parent=btn, model=Circle(resolution=16, radius=0.5),
                                            color=COLORS["ok"], scale=0.16, position=(0.33, 0.33, -0.02),
                                            enabled=False))
        return picker

    def _build_help(self) -> Entity:
        """Bảng phím tắt đầy đủ (F1); dòng phím tắt dưới đáy màn hình chỉ ghi các phím hay dùng."""
        rows = (len(SHORTCUTS) + 1) // 2
        width, height = 1.0, rows * 0.042 + 0.13
        panel = self._overlay(width, height, self.close_help)
        Text(parent=panel, text="Phím tắt", origin=(0, 0), y=height / 2 - 0.04, z=-0.01, scale=1.25, font=FONT_BOLD)
        for i, (key, action) in enumerate(SHORTCUTS):
            col, row = divmod(i, rows)
            x = -width / 2 + 0.04 + col * width / 2
            y = height / 2 - 0.1 - row * 0.042
            Text(parent=panel, text=key, position=(x, y), origin=(-0.5, 0), z=-0.01, scale=0.78,
                 color=COLORS["accent"], font=FONT_SEMIBOLD)
            Text(parent=panel, text=action, position=(x + 0.2, y), origin=(-0.5, 0), z=-0.01, scale=0.78)
        Text(parent=panel, text="F1 hoặc Esc để đóng", origin=(0, 0), y=-height / 2 + 0.028, z=-0.01, scale=0.7,
             color=COLORS["muted"])
        return panel

    def _build_legend(self) -> Entity:
        """Bảng chú giải các loại ô (phím G hoặc nút "Chú giải"): mỗi mục một ô mẫu, tên và cách hoạt động."""
        width, height = 1.16, LEGEND_ROWS * LEGEND_ROW_H + 0.15
        panel = self._overlay(width, height, self.close_legend)
        Text(parent=panel, text="Chú giải các loại ô", origin=(0, 0), y=height / 2 - 0.04, z=-0.01, scale=1.25,
             font=FONT_BOLD)
        for i, (kind, name, rule) in enumerate(LEGEND):
            col, row = divmod(i, LEGEND_ROWS)
            x = -width / 2 + 0.06 + col * width / 2
            y = height / 2 - 0.12 - row * LEGEND_ROW_H
            _tile_swatch(panel, kind, x, y, LEGEND_SWATCH)
            left = x + LEGEND_SWATCH / 2 + 0.024
            Text(parent=panel, text=name, position=(left, y + 0.022), origin=(-0.5, 0.5), z=-0.01, scale=0.8,
                 font=FONT_SEMIBOLD)
            Text(parent=panel, text=_wrap(rule, LEGEND_WRAP), position=(left, y - 0.002), origin=(-0.5, 0.5),
                 z=-0.01, scale=0.66, line_height=1.25, color=COLORS["muted"])
        Text(parent=panel, text="G hoặc Esc để đóng", origin=(0, 0), y=-height / 2 + 0.028, z=-0.01, scale=0.7,
             color=COLORS["muted"])
        return panel

    def set_current_level(self, index: int) -> None:
        """Đổi màu ô màn hiện tại sang màu xanh dương để người chơi nhận biết."""
        self.current_level = index
        for i, btn in enumerate(self.picker_buttons):
            tint = COLORS["solve"] if i == index else COLORS["button"]
            btn.color, btn.highlight_color = tint, tint.tint(0.18)

    def toggle_picker(self) -> None:
        self.help.enabled = self.legend.enabled = False
        self.picker.enabled = not self.picker.enabled
        if self.picker.enabled:
            self.set_current_level(self.current_level)

    def close_picker(self) -> None:
        self.picker.enabled = False

    def toggle_help(self) -> None:
        self.picker.enabled = self.legend.enabled = False
        self.help.enabled = not self.help.enabled

    def close_help(self) -> None:
        self.help.enabled = False

    def toggle_legend(self) -> None:
        self.picker.enabled = self.help.enabled = False
        self.legend.enabled = not self.legend.enabled

    def close_legend(self) -> None:
        self.legend.enabled = False

    @property
    def overlay_open(self) -> bool:
        """Đang mở lưới chọn màn, bảng phím tắt hoặc bảng chú giải."""
        return self.picker.enabled or self.help.enabled or self.legend.enabled

    def mark_solved(self, index: int) -> None:
        """Đánh dấu màn đã thắng (chơi tay hoặc khối tự lăn) bằng chấm xanh trên lưới chọn màn."""
        if 0 <= index < len(self.solved_marks):
            self.solved_marks[index].enabled = True

    def _pick(self, index: int) -> None:
        self.picker.enabled = False
        self.set_current_level(index)
        self.on_pick_level(index)

    def set_camera_view(self, name: str) -> None:
        """Cập nhật nhãn góc camera trên HUD khi người chơi xoay hoặc đổi góc."""
        self.cam_label.text = name

    # ---- trạng thái nút và kết quả ----

    def set_running(self, running: bool) -> None:
        """Đang có solver chạy: tắt các nút giải và So sánh, bật nút Hủy (tắt thì xám, không chỉ mờ).

        Nút Hủy còn bật cả khi khối đang tự lăn: app.py gọi set_cancel_enabled() mỗi khung hình."""
        self._running = running
        if not running:
            self.highlight_solver(None)
            self.dot.alpha = 1.0
        for name in (*SOLVE_NAMES, "compare"):
            self._set_enabled(self.buttons[name], not running)
        self.set_cancel_enabled(running)

    def set_cancel_enabled(self, enabled: bool) -> None:
        """Bật nút Hủy khi đang có solver chạy hoặc khối đang tự lăn theo lời giải."""
        button = self.buttons["cancel"]
        if button.disabled == enabled:
            self._set_enabled(button, enabled)

    @staticmethod
    def _set_enabled(button: Button, enabled: bool) -> None:
        button.disabled = not enabled
        tint = button.base_color if enabled else COLORS["disabled"]
        button.color, button.highlight_color = tint, tint.tint(0.15) if enabled else tint
        button.text_entity.alpha = 1.0 if enabled else 0.4

    def highlight_solver(self, name: Optional[str]) -> None:
        """Khung sáng trượt tới nút của thuật toán đang chạy; A* (h_M) của So sánh dùng chung nút A*; None thì ẩn."""
        button = self.buttons.get("astar" if name == "astar_m" else name) if name else None
        if button is None:
            self.indicator.enabled = False
            self._highlighted = None
            return
        if name == self._highlighted:
            return
        self.indicator.scale = (button.scale_x + 0.008, button.scale_y + 0.008)
        if not self.indicator.enabled:
            self.indicator.position = (button.x, button.y, -0.02)
            self.indicator.enabled = True
        else:
            self.indicator.animate_position((button.x, button.y, -0.02), duration=0.2, curve=curve.out_quad)
        self._highlighted = name

    def update(self) -> None:
        """Mỗi khung hình: chấm trạng thái và khung quanh nút đang chạy nhấp nháy khi đang giải."""
        if self._running:
            pulse = 0.35 + 0.65 * abs(math.sin(time.time() * 4))
            if self.panel.enabled:
                self.dot.alpha = pulse
            if self.indicator.enabled:
                self.indicator.alpha = 0.5 + 0.5 * pulse

    def show_status(self, text: str, tint: Optional[color.Color] = None) -> None:
        """Dòng đầu của khung kết quả; chuỗi rỗng thì ẩn cả khung.

        Dòng trạng thái dài xuống hàng thì bảng So sánh và phần chi tiết dời xuống theo, không bị đè."""
        has_table = any(cell.text for row in self.cells for cell in row)
        text = self._wrap_status(text, self.table_panel_w if has_table else PANEL_W)
        if self.status.text != text:
            self.status.text = text
        self.status.color = tint or color.white
        self.dot.color = _with_alpha(tint or COLORS["accent"], self.dot.alpha)
        delta = TABLE_Y - (_line_count(text) - 1) * self._status_line_h - self.table.y
        if abs(delta) > 1e-6:
            self.table.y += delta
            self.details.y += delta
            self._fit_panel(self._content_bottom + delta)
        if not self.details.text.strip() and not has_table:
            # chỉ có dòng trạng thái (đang tìm, hoặc lỗi dài nhiều dòng)
            self._fit_panel(-PAD - _line_count(text) * LINE_H * 1.4, PANEL_W)
        self._sync_panel()

    def _wrap_status(self, text: str, panel_w: float) -> str:
        """Ngắt dòng trạng thái theo từ để mỗi dòng vừa khung rộng panel_w, không chạm chữ "H: ẩn" ở mép phải.

        Đo bằng font thật vì font tỉ lệ: cùng số ký tự, "Mở rộng" rộng hơn "lời giải" (ngắt theo số ký tự
        như _wrap() thì dòng có nhiều chữ hoa, chữ có dấu vẫn tràn)."""
        room = panel_w - PAD - self.hide_hint.width * self.hide_hint.scale_x - HINT_GAP - (PAD + DOT_GAP)
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split(" "):
                candidate = f"{line} {word}" if line else word
                if line and self._status_width(candidate) > room:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        return "\n".join(lines)

    def _status_width(self, line: str) -> float:
        for char in line:
            if char not in self._char_w:
                # kẹp giữa hai vạch: Text bỏ khoảng trắng ở đầu và cuối nên đo riêng " " sẽ ra 0
                self._char_w[char] = self._probe_width(f"|{char}|") - self._bars_w
        return sum(self._char_w[char] for char in line)

    def _probe_width(self, text: str) -> float:
        probe = Text(text, parent=self, scale=STATUS_SCALE, font=FONT_SEMIBOLD)
        width = probe.width * STATUS_SCALE
        destroy(probe)
        return width

    def toggle_panel(self) -> None:
        """Phím H: ẩn hoặc hiện lại khung kết quả (bàn được căn lại theo)."""
        self.panel_hidden = not self.panel_hidden
        self._sync_panel()

    def _sync_panel(self) -> None:
        visible = bool(self.status.text.strip()) and not self.panel_hidden
        if self.panel.enabled != visible:
            self.panel.enabled = visible
            if self.on_panel_change is not None:
                self.on_panel_change(visible)

    def _fit_panel(self, content_bottom: float, width: Optional[float] = None) -> None:
        """Thẻ nền vừa đủ phủ nội dung (tính từ mép trên của khung), rộng width (None: giữ bề rộng cũ).

        Bề rộng đổi trong lúc khung đang hiện thì báo app.py căn lại bàn theo mép phải mới của khung."""
        width = self.panel_w if width is None else width
        self._content_bottom = content_bottom
        height = min(PANEL_TOP - PANEL_BOTTOM, -content_bottom + PAD)
        if abs(height - self._panel_h) < 1e-4 and abs(width - self.panel_w) < 1e-4:
            return
        width_changed = abs(width - self.panel_w) >= 1e-4
        self._panel_h, self.panel_w = height, width
        resize_card(self.panel_bg, width, height, 0, 0)
        self.hide_hint.x = width - PAD
        self.panel_right = self.panel.x + width
        if width_changed and self.panel.enabled and self.on_panel_change is not None:
            self.on_panel_change(True)

    def clear_results(self) -> None:
        self.panel_hidden = False   # kết quả mới luôn hiện, kể cả khi trước đó đã bấm H
        self.show_status("")
        self.details.text = ""
        for row in self.cells:
            for cell in row:
                cell.text = ""

    def show_result(self, name: str, outcome: Mapping) -> None:
        """Kết quả của một nút Solve."""
        self.clear_results()
        summary, tint = outcome_summary(outcome)
        self.show_status(f"{LABELS[name]}: {summary}", tint)
        self.details.y = self.table.y
        if outcome.get("ok"):
            seconds, memory = _time_and_memory(outcome)
            lines = [f"Số bước {len(outcome['path'])}  ·  chi phí {outcome['path_cost']:g}",
                     f"Mở rộng {outcome['expanded']}  ·  sinh {outcome['generated']}",
                     f"Frontier lớn nhất {outcome['max_frontier']}",
                     f"Đã thăm {outcome['visited']}",
                     f"Thời gian {seconds}  ·  bộ nhớ {memory}"]
            self.details.text = "\n".join(lines)
            self._fit_panel(self.details.y - len(lines) * DETAILS_LINE_H, PANEL_W)

    def show_compare(self, names: Sequence[str], results: Mapping[str, Mapping], running: Optional[str],
                     elapsed: float) -> None:
        """Bảng So sánh: mỗi thuật toán một dòng; dòng đang chạy hiện số giây, dòng chưa chạy ghi "chờ".

        Gọi mỗi khung hình trong lúc So sánh chạy, nên chỉ đổi chữ của các ô đã dựng sẵn.
        """
        rows: List[List[tuple[str, color.Color]]] = [[(title, COLORS["muted"]) for title, _ in TABLE_COLUMNS]]
        errors = []
        for name in names:
            outcome = results.get(name)
            if outcome is None:
                state = (f"chạy {elapsed:.1f}s", COLORS["warn"]) if name == running else ("chờ", COLORS["muted"])
                rows.append([(LABELS[name], color.white), state] + [("", color.white)] * 5)
                continue
            summary, tint = outcome_summary(outcome)
            if summary.startswith("Lỗi"):   # lỗi dài không vừa ô: ô ghi "Lỗi", nội dung ghi ở phần chi tiết
                errors.append(f"{LABELS[name]}: {outcome.get('error', '')}")
                summary = "Lỗi"
            summary = SHORT_SUMMARY.get(summary, summary)
            cells = [(LABELS[name], color.white), (summary, tint)]
            if outcome.get("ok"):
                # bảng hẹp: số không kèm đơn vị, đơn vị ghi ở tiêu đề cột (Giây, MB)
                cells += [(str(len(outcome["path"])), color.white), (f"{outcome['path_cost']:g}", color.white),
                          (str(outcome["expanded"]), color.white), (f"{outcome['time_ms'] / 1000:.2f}", color.white),
                          (f"{outcome['peak_kb'] / 1024:.1f}", color.white)]
            else:
                cells += [("", color.white)] * 5
            rows.append(cells)
        details = _wrap("\n".join(errors), DETAILS_WRAP)
        self.details.y = self.table.y - len(rows) * ROW_H - 0.012
        if self.details.text != details:
            self.details.text = details
        while len(self.cells) < len(rows):
            r = len(self.cells)
            self.cells.append([Text(parent=self.table, position=(cx, -r * ROW_H), origin=(-0.5, 0.5),
                                    scale=TABLE_SCALE, font=FONT_SEMIBOLD if r == 0 else FONT_REGULAR)
                               for cx in self.table_x])
        for cells, row in zip(self.cells, rows):
            for cell, (text, tint) in zip(cells, row):
                if cell.text != text:
                    cell.text = text
                cell.color = tint
        self._fit_panel(self.details.y - _line_count(details) * DETAILS_LINE_H if errors
                        else self.table.y - len(rows) * ROW_H, self.table_panel_w)


def _shade(base: color.Color, factor: float) -> color.Color:
    return color.Color(base[0] * factor, base[1] * factor, base[2] * factor, base[3])


def _tile_swatch(parent: Entity, kind: str, x: float, y: float, size: float) -> None:
    """Ô mẫu của bảng chú giải, tâm tại (x, y): mặt trên và một dải mặt bên tối hơn (như hộp vát cạnh trên bàn,
    TILE_SHADE), rồi ký hiệu công tắc hoặc lỗ đích vẽ phẳng bằng đúng màu của board_view."""
    def slab(tint: color.Color, alpha: float = 1.0) -> None:
        side = Entity(parent=parent, model=Quad(radius=0.12), color=_shade(tint, TILE_SHADE[1]),
                      scale=size, position=(x, y - size * 0.16, -0.008))
        top = Entity(parent=parent, model=Quad(radius=0.12), color=tint, scale=size, position=(x, y, -0.01))
        side.alpha, top.alpha = alpha, alpha

    def mark(**kwargs) -> Entity:
        return Entity(parent=parent, position=(x, y, -0.012), **kwargs)

    if kind == "void":
        Entity(parent=parent, model=Quad(radius=0.12, mode="line", thickness=1.5), color=COLORS["muted"],
               scale=size, position=(x, y, -0.01), alpha=0.55)
    elif kind == "goal":
        slab(TILE_COLORS["goal_rim"])
        mark(model="quad", color=TILE_COLORS["goal_shaft"], scale=size * 0.8)
        mark(model=Quad(mode="line", thickness=2), color=TILE_COLORS["goal_glow"], scale=size * 0.84)
    elif kind == "fragile":
        slab(TILE_COLORS["fragile"])
    elif kind == "bridge_open":
        slab(TILE_COLORS["bridge"])
    elif kind == "bridge_closed":
        slab(TILE_COLORS["bridge"], CLOSED_BRIDGE_ALPHA * 2)   # trên nền tối của bảng, alpha gốc gần như không thấy
    elif kind == "block":
        body = mark(model=Quad(radius=0.15), color=BLOCK_COLORS["block"], scale=(size * 0.55, size * 1.1))
        Entity(parent=body, model=Quad(radius=0.15, mode="line", thickness=2), color=BLOCK_COLORS["edge"],
               z=-0.001)
    else:
        slab(TILE_COLORS["floor"])
        if kind == "soft":
            mark(model=Circle(resolution=32, radius=0.32), color=TILE_COLORS["soft"], scale=size)
        elif kind == "heavy":
            for angle in (45, -45):
                mark(model="quad", color=TILE_COLORS["heavy"], rotation_z=angle, scale=(size * 0.72, size * 0.13))
        elif kind == "split":
            for start in (120, -60):   # hai cung tròn thành hình "( )" như board_view._mark_split
                points = [Vec3(0.3 * size * math.cos(math.radians(start + i * 10)),
                               0.3 * size * math.sin(math.radians(start + i * 10)), 0) for i in range(13)]
                mark(model=Mesh(vertices=points, mode="line", thickness=4), color=TILE_COLORS["split"])
