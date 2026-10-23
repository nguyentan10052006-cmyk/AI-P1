"""Bảng điều khiển (V21): New Game, Restart, chọn màn, 4 nút Solve, So sánh, Hủy và bảng kết quả.

Chỉ vẽ và gọi lại các hàm do app.py truyền vào; không giữ trạng thái chơi, không gọi solver (docs/07 §5).
"""
from __future__ import annotations

from typing import Callable, Dict, List, Mapping, Optional, Sequence

from ursina import Button, Entity, Text, Vec3, camera, color, window

# Tên hiện trên nút và trong bảng So sánh, theo khóa của solvers.ALGORITHMS
LABELS = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A*", "astar_m": "A* (h_M)"}
SOLVE_NAMES = ("bfs", "dfs", "ucs", "astar")

COLORS = {
    "button": color.hex("#2f3d4d"),
    "solve": color.hex("#2f6fd6"),
    "cancel": color.hex("#b0413e"),
    "panel": color.hex("#141b23"),
    "ok": color.hex("#7ee787"),
    "warn": color.hex("#f2c94c"),
    "bad": color.hex("#ff7b72"),
    "muted": color.hex("#9aa3ad"),
}
BUTTON_W, BUTTON_H, GAP = 0.2, 0.045, 0.008
PANEL_TOP, PANEL_W, PANEL_H = -0.1, 0.9, 0.38
ROW_H = 0.035             # chiều cao một dòng của bảng So sánh
COMPARE_DETAILS_Y = -0.28  # lỗi của các thuật toán ghi dưới bảng So sánh
TABLE_COLUMNS = (("Thuật toán", 0.0), ("Kết quả", 0.13), ("Bước", 0.33), ("Chi phí", 0.42),
                 ("Mở rộng", 0.52), ("Thời gian", 0.65), ("Bộ nhớ", 0.78))


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


def _time_and_memory(outcome: Mapping) -> tuple[str, str]:
    return f"{outcome['time_ms'] / 1000:.2f} s", f"{outcome['peak_kb'] / 1024:.1f} MB"


class Hud(Entity):
    """Cột nút bên phải, bảng chọn màn ở giữa, khung kết quả ở góc trái dưới."""

    def __init__(self, level_ids: Sequence[str], *, on_new_game: Callable[[], None],
                 on_restart: Callable[[], None], on_pick_level: Callable[[int], None],
                 on_solve: Callable[[str], None], on_compare: Callable[[], None],
                 on_cancel: Callable[[], None]) -> None:
        super().__init__(parent=camera.ui)
        self.on_pick_level = on_pick_level
        x = window.right.x - BUTTON_W / 2 - 0.02
        y = 0.45
        self.buttons: Dict[str, Button] = {}

        def add(key: str, text: str, on_click: Callable[[], None], tint: color.Color) -> None:
            nonlocal y
            self.buttons[key] = Button(text=text, parent=self, position=(x, y), scale=(BUTTON_W, BUTTON_H),
                                       color=tint, text_size=0.8, radius=0.25, on_click=on_click)
            y -= BUTTON_H + GAP

        add("new", "Màn mới (màn 01)", on_new_game, COLORS["button"])
        add("restart", "Chơi lại", on_restart, COLORS["button"])
        add("pick", "Chọn màn…", self.toggle_picker, COLORS["button"])
        y -= GAP * 2
        for name in SOLVE_NAMES:
            add(name, f"Giải bằng {LABELS[name]}", lambda name=name: on_solve(name), COLORS["solve"])
        add("compare", "So sánh", on_compare, COLORS["solve"])
        add("cancel", "Hủy", on_cancel, COLORS["cancel"])

        # Khung kết quả ở góc trái dưới, nền tối để đọc được khi đè lên bàn; ẩn khi chưa có gì để hiện
        self.panel = Entity(parent=self, position=(window.left.x + 0.02, PANEL_TOP), enabled=False)
        self.panel_bg = Entity(parent=self.panel, model="quad", origin=(-0.5, 0.5), color=COLORS["panel"],
                               alpha=0.88, z=0.01, scale=(PANEL_W, PANEL_H))
        # text=" ": Ursina 7 lỗi khi đặt wordwrap cho Text rỗng; lỗi của solver có thể dài nên phải xuống dòng
        self.status = Text(" ", parent=self.panel, position=(0.015, -0.015), origin=(-0.5, 0.5), wordwrap=60)
        self.details = Text(" ", parent=self.panel, position=(0.015, -0.06), origin=(-0.5, 0.5), scale=0.85,
                            color=COLORS["muted"], wordwrap=72)
        self.table = Entity(parent=self.panel, position=(0.015, -0.06))
        self.cells: List[List[Text]] = []   # ô của bảng So sánh, dựng lần đầu khi cần
        self.picker = self._build_picker(level_ids)
        self.set_running(False)

    # ---- chọn màn ----

    def _build_picker(self, level_ids: Sequence[str]) -> Entity:
        """Lưới nút mã màn nằm giữa màn hình; ẩn cho tới khi bấm "Chọn màn…"."""
        cols, size = 11, 0.07
        rows = (len(level_ids) + cols - 1) // cols
        width, height = cols * size + 0.06, rows * size + 0.13
        picker = Entity(parent=self, z=-0.5, enabled=False)
        Entity(parent=picker, model="quad", color=COLORS["panel"], scale=(width, height))
        Text(parent=picker, text="Chọn màn", origin=(0, 0), y=height / 2 - 0.035, z=-0.01, scale=1.1)
        for i, level_id in enumerate(level_ids):
            r, c = divmod(i, cols)
            Button(text=level_id, parent=picker, z=-0.01, scale=size * 0.85, color=COLORS["button"],
                   text_size=0.8, position=((c - (cols - 1) / 2) * size, height / 2 - 0.1 - r * size),
                   on_click=lambda i=i: self._pick(i))
        return picker

    def toggle_picker(self) -> None:
        self.picker.enabled = not self.picker.enabled

    def _pick(self, index: int) -> None:
        self.picker.enabled = False
        self.on_pick_level(index)

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
        if self.status.text != text:
            self.status.text = text
        self.status.color = tint or color.white
        self.panel.enabled = bool(text)
        if not self.details.text.strip() and not any(cell.text for row in self.cells for cell in row):
            self.panel_bg.scale_y = 0.08   # chỉ có dòng trạng thái (đang tìm, hoặc lỗi dài tối đa 2 dòng)

    def _fit_panel(self, content_bottom: float) -> None:
        """Khung nền vừa đủ phủ nội dung, tính từ mép trên của khung."""
        self.panel_bg.scale_y = min(PANEL_H, -content_bottom + 0.02)

    def clear_results(self) -> None:
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
            self._fit_panel(self.details.y - len(lines) * 0.026)

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
                state = (f"đang chạy {elapsed:.1f} s", COLORS["warn"]) if name == running else ("chờ", COLORS["muted"])
                rows.append([(LABELS[name], color.white), state] + [("", color.white)] * 5)
                continue
            summary, tint = outcome_summary(outcome)
            if summary.startswith("Lỗi"):   # lỗi dài không vừa ô: ô ghi "Lỗi", nội dung ghi ở phần chi tiết
                errors.append(f"{LABELS[name]}: {outcome.get('error', '')}")
                summary = "Lỗi"
            cells = [(LABELS[name], color.white), (summary, tint)]
            if outcome.get("ok"):
                seconds, memory = _time_and_memory(outcome)
                cells += [(str(len(outcome["path"])), color.white), (f"{outcome['path_cost']:g}", color.white),
                          (str(outcome["expanded"]), color.white), (seconds, color.white), (memory, color.white)]
            else:
                cells += [("", color.white)] * 5
            rows.append(cells)
        details = "\n".join(errors)
        self.details.y = COMPARE_DETAILS_Y
        if self.details.text != details:
            self.details.text = details
        while len(self.cells) < len(rows):
            r = len(self.cells)
            self.cells.append([Text(parent=self.table, position=(cx, -r * ROW_H), origin=(-0.5, 0.5), scale=0.85)
                               for _, cx in TABLE_COLUMNS])
        for cells, row in zip(self.cells, rows):
            for cell, (text, tint) in zip(cells, row):
                if cell.text != text:
                    cell.text = text
                cell.color = tint
        self._fit_panel(COMPARE_DETAILS_Y - len(errors) * 0.026 if errors else self.table.y - len(rows) * ROW_H)
