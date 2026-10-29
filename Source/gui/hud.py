"""Bảng điều khiển (V21): New Game, Restart, chọn màn, 4 nút Solve, So sánh, Hủy và bảng kết quả.

Chỉ vẽ và gọi lại các hàm do app.py truyền vào; không giữ trạng thái chơi, không gọi solver (docs/07 §5).
"""
from __future__ import annotations

import textwrap
from typing import Callable, Dict, List, Mapping, Optional, Sequence

from ursina import Button, Entity, Text, Vec3, camera, color, window

# Tên hiện trên nút và trong bảng So sánh, theo khóa của solvers.ALGORITHMS
LABELS = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A*", "astar_m": "A* (h_M)"}
SOLVE_NAMES = ("bfs", "dfs", "ucs", "astar")

COLORS = {
    "button": color.hex("#2f3d4d"),
    "solve": color.hex("#2f6fd6"),
    "cancel": color.hex("#b0413e"),
    "panel": color.hex("#1c2632"),   # sáng hơn nền #0b0f14–#18212b một chút để khung nổi lên
    "ok": color.hex("#7ee787"),
    "warn": color.hex("#f2c94c"),
    "bad": color.hex("#ff7b72"),
    "muted": color.hex("#9aa3ad"),
    "accent": color.hex("#38bdf8"),
    "cam": color.hex("#253241"),
}
HOVER_SCALE = 1.03          # nút phóng nhẹ khi rê chuột (GAME_UI_UX_SPECIFICATION §3.2)
BUTTON_W, BUTTON_H, GAP = 0.2, 0.045, 0.008
# Khung kết quả là cột dọc bên trái, dưới dòng STAGE/MOVES và trên dòng phím tắt; khi khung hiện,
# camera căn bàn vào vùng trống giữa khung và cột nút (app.py) nên khung không che bàn
PANEL_TOP, PANEL_BOTTOM, PANEL_W = 0.36, -0.44, 0.53
PAD = 0.015               # lề trong của khung
LINE_H = 0.022            # chiều cao một dòng chữ scale 0.85
STATUS_WRAP, DETAILS_WRAP = 38, 46   # số ký tự mỗi dòng trước khi xuống hàng, vừa bề rộng khung
ROW_H = 0.03              # chiều cao một dòng của bảng So sánh
TABLE_SCALE = 0.72
# vị trí cột đo theo bề rộng thật của chữ ở TABLE_SCALE, cách nhau 0.012
TABLE_COLUMNS = (("Thuật toán", 0.0), ("Kết quả", 0.103), ("Bước", 0.195), ("Chi phí", 0.25),
                 ("Mở rộng", 0.317), ("Giây", 0.401), ("MB", 0.46))


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


def _line_count(text: str) -> int:
    return text.count("\n") + 1


def _time_and_memory(outcome: Mapping) -> tuple[str, str]:
    return f"{outcome['time_ms'] / 1000:.2f} s", f"{outcome['peak_kb'] / 1024:.1f} MB"


class Hud(Entity):
    """Cột nút bên phải, bảng chọn màn ở giữa, khung kết quả ở góc trái dưới."""

    def __init__(self, level_ids: Sequence[str], *, on_new_game: Callable[[], None],
                 on_restart: Callable[[], None], on_pick_level: Callable[[int], None],
                 on_solve: Callable[[str], None], on_compare: Callable[[], None],
                 on_cancel: Callable[[], None],
                 on_rotate_cam: Optional[Callable[[float], None]] = None,
                 on_tilt_cam: Optional[Callable[[float], None]] = None,
                 on_toggle_top_down: Optional[Callable[[], None]] = None,
                 on_reset_cam: Optional[Callable[[], None]] = None) -> None:
        super().__init__(parent=camera.ui)
        self.on_pick_level = on_pick_level
        self.on_panel_change: Optional[Callable[[bool], None]] = None   # app.py căn lại camera khi khung hiện/ẩn
        self.panel_hidden = False   # người chơi bấm H để ẩn khung kết quả
        x = window.right.x - BUTTON_W / 2 - 0.02
        self.dock_left = x - BUTTON_W / 2   # mép trái cột nút, dùng để tính vùng trống cho bàn
        y = 0.45
        self.buttons: Dict[str, Button] = {}

        def add(key: str, text: str, on_click: Callable[[], None], tint: color.Color) -> None:
            nonlocal y
            btn = Button(text=text, parent=self, position=(x, y), scale=(BUTTON_W, BUTTON_H),
                         color=tint, text_size=0.8, radius=0.2, on_click=on_click)
            btn.highlight_color = tint.tint(0.18)
            btn.pressed_color = tint.tint(-0.15)
            btn.highlight_scale = HOVER_SCALE
            self.buttons[key] = btn
            y -= BUTTON_H + GAP

        add("new", "Màn mới (màn 01)", on_new_game, COLORS["button"])
        add("restart", "Chơi lại", on_restart, COLORS["button"])
        add("pick", "Chọn màn…", self.toggle_picker, COLORS["button"])
        y -= GAP * 2
        for name in SOLVE_NAMES:
            add(name, f"Giải bằng {LABELS[name]}", lambda name=name: on_solve(name), COLORS["solve"])
        add("compare", "So sánh", on_compare, COLORS["solve"])
        add("cancel", "Hủy", on_cancel, COLORS["cancel"])

        # Cụm điều khiển Camera 3D (GAME_UI_UX_SPECIFICATION.md §4): mỗi hàng hai nút nhỏ
        y -= GAP * 2
        self.cam_title = Text("CAMERA", parent=self, position=(x, y), origin=(0, 0), scale=0.75, color=COLORS["muted"])
        y -= 0.025
        self.cam_label = Text("CHÍNH DIỆN", parent=self, position=(x, y), origin=(0, 0), scale=0.8,
                              color=COLORS["accent"])
        y -= 0.032
        sub_w, sub_h = BUTTON_W / 2 - 0.003, BUTTON_H * 0.82

        def add_pair(left: tuple[str, str, Callable[[], None]], right: tuple[str, str, Callable[[], None]]) -> None:
            nonlocal y
            for (key, text, on_click), dx in ((left, -1), (right, 1)):
                btn = Button(text=text, parent=self, position=(x + dx * (sub_w / 2 + 0.003), y),
                             scale=(sub_w, sub_h), color=COLORS["cam"], text_size=0.72, radius=0.2, on_click=on_click)
                btn.highlight_color = COLORS["cam"].tint(0.2)
                btn.highlight_scale = HOVER_SCALE
                self.buttons[key] = btn
            y -= sub_h + GAP

        if on_rotate_cam is not None:
            add_pair(("cam_rot_l", "< Trái (Q)", lambda: on_rotate_cam(-1)),
                     ("cam_rot_r", "Phải (E) >", lambda: on_rotate_cam(1)))
        if on_tilt_cam is not None:
            add_pair(("cam_tilt_down", "Hạ thấp (Z)", lambda: on_tilt_cam(-1)),
                     ("cam_tilt_up", "Nâng cao (X)", lambda: on_tilt_cam(1)))
        if on_toggle_top_down is not None and on_reset_cam is not None:
            add_pair(("cam_top", "Đỉnh (T)", on_toggle_top_down), ("cam_reset", "Đặt lại (F)", on_reset_cam))

        # Khung kết quả ở góc trái dưới, nền tối để đọc được khi đè lên bàn; ẩn khi chưa có gì để hiện
        self.panel = Entity(parent=self, position=(window.left.x + 0.02, PANEL_TOP), enabled=False)
        self.panel_right = self.panel.x + PANEL_W
        self.panel_bg = Entity(parent=self.panel, model="quad", origin=(-0.5, 0.5), color=COLORS["panel"],
                               alpha=0.88, z=0.01, scale=(PANEL_W, 0.08))
        Text("H: ẩn", parent=self.panel, position=(PANEL_W - PAD, -PAD), origin=(0.5, 0.5), scale=0.7,
             color=COLORS["muted"])
        # text=" ": Ursina 7 lỗi khi đặt wordwrap cho Text rỗng; lỗi của solver có thể dài nên phải xuống dòng
        self.status = Text(" ", parent=self.panel, position=(PAD, -PAD), origin=(-0.5, 0.5), wordwrap=STATUS_WRAP)
        self.details = Text(" ", parent=self.panel, position=(PAD, -0.06), origin=(-0.5, 0.5), scale=0.85,
                            color=COLORS["muted"], wordwrap=DETAILS_WRAP)
        self.table = Entity(parent=self.panel, position=(PAD, -0.06))
        self.cells: List[List[Text]] = []   # ô của bảng So sánh, dựng lần đầu khi cần
        self.current_level = 0
        self.picker_buttons: List[Button] = []
        self.picker = self._build_picker(level_ids)
        self.set_current_level(0)
        self.set_running(False)

    # ---- chọn màn ----

    def _build_picker(self, level_ids: Sequence[str]) -> Entity:
        """Lưới nút mã màn nằm giữa màn hình; ẩn cho tới khi bấm "Chọn màn…"."""
        cols, size = 11, 0.07
        rows = (len(level_ids) + cols - 1) // cols
        width, height = cols * size + 0.06, rows * size + 0.13
        picker = Entity(parent=self, z=-0.5, enabled=False)
        # Lớp phủ tối che bàn chơi; bấm ra ngoài bảng thì đóng
        backdrop = Button(parent=picker, model="quad", color=color.rgba(0, 0, 0, 0.55), scale=(4, 2), z=0.02,
                          on_click=self.close_picker)
        backdrop.highlight_color = backdrop.pressed_color = backdrop.color
        Button(parent=picker, model="quad", color=COLORS["panel"], scale=(width, height), z=0.01,
               highlight_color=COLORS["panel"], pressed_color=COLORS["panel"])   # chặn click lọt xuống lớp phủ
        Text(parent=picker, text="Chọn màn", origin=(0, 0), y=height / 2 - 0.035, z=-0.01, scale=1.1)
        self.picker_buttons.clear()
        for i, level_id in enumerate(level_ids):
            r, c = divmod(i, cols)
            btn = Button(text=level_id, parent=picker, z=-0.01, scale=size * 0.85, color=COLORS["button"],
                         text_size=0.8, position=((c - (cols - 1) / 2) * size, height / 2 - 0.1 - r * size),
                         highlight_scale=HOVER_SCALE * 1.05, on_click=lambda i=i: self._pick(i))
            self.picker_buttons.append(btn)
        return picker

    def set_current_level(self, index: int) -> None:
        """Đổi màu ô màn hiện tại sang màu xanh dương để người chơi nhận biết."""
        self.current_level = index
        for i, btn in enumerate(self.picker_buttons):
            if i == index:
                btn.color = COLORS["solve"]
                btn.highlight_color = COLORS["solve"].tint(0.18)
            else:
                btn.color = COLORS["button"]
                btn.highlight_color = COLORS["button"].tint(0.18)

    def toggle_picker(self) -> None:
        self.picker.enabled = not self.picker.enabled
        if self.picker.enabled:
            self.set_current_level(self.current_level)

    def close_picker(self) -> None:
        self.picker.enabled = False

    def _pick(self, index: int) -> None:
        self.picker.enabled = False
        self.set_current_level(index)
        self.on_pick_level(index)

    def set_camera_view(self, name: str) -> None:
        """Cập nhật nhãn góc camera trên HUD khi người chơi xoay hoặc đổi góc."""
        if hasattr(self, "cam_label") and self.cam_label:
            self.cam_label.text = name

    # ---- trạng thái nút và kết quả ----

    def set_running(self, running: bool) -> None:
        """Đang có solver chạy: tắt các nút Solve và So sánh, bật nút Hủy."""
        for name in (*SOLVE_NAMES, "compare"):
            self.buttons[name].disabled = running
            self.buttons[name].alpha = 0.4 if running else 1.0
        self.buttons["cancel"].disabled = not running
        self.buttons["cancel"].alpha = 1.0 if running else 0.4

    def show_status(self, text: str, tint: Optional[color.Color] = None) -> None:
        """Dòng đầu của khung kết quả; chuỗi rỗng thì ẩn cả khung."""
        text = _wrap(text, STATUS_WRAP)
        if self.status.text != text:
            self.status.text = text
        self.status.color = tint or color.white
        if not self.details.text.strip() and not any(cell.text for row in self.cells for cell in row):
            # chỉ có dòng trạng thái (đang tìm, hoặc lỗi dài nhiều dòng)
            self._fit_panel(-PAD - _line_count(text) * LINE_H * 1.25)
        self._sync_panel()

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

    def _fit_panel(self, content_bottom: float) -> None:
        """Khung nền vừa đủ phủ nội dung, tính từ mép trên của khung."""
        self.panel_bg.scale_y = min(PANEL_TOP - PANEL_BOTTOM, -content_bottom + PAD)

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
            self._fit_panel(self.details.y - len(lines) * LINE_H)

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
                                    scale=TABLE_SCALE) for _, cx in TABLE_COLUMNS])
        for cells, row in zip(self.cells, rows):
            for cell, (text, tint) in zip(cells, row):
                if cell.text != text:
                    cell.text = text
                cell.color = tint
        self._fit_panel(self.details.y - _line_count(details) * LINE_H if errors else self.table.y - len(rows) * ROW_H)
