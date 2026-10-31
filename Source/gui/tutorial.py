"""Bảng "Cách chơi" (mở từ trang chủ): 4 trang hướng dẫn, mỗi trang có bàn chữ nhật mô phỏng tự chạy.

Chỉ vẽ (docs/07 §5): bàn mô phỏng là hình 2D nhìn xiên 3/4, không dùng engine, không ảnh hưởng ván đang chơi.
Các ô khối đang chiếm được tô sáng; khối đứng nhô cao gấp đôi khối nằm và đổ bóng dài hơn.

Các trang trả lời đúng những gì người chơi muốn biết khi bấm "Cách chơi":
1. Mục tiêu: khối lăn tới lỗ đích và đứng thẳng lọt xuống thì thắng.
2. Cách lăn: phím mũi tên / WASD; đứng chiếm 1 ô, nằm chiếm 2 ô; lăn theo chiều dài thì đứng dậy.
3. Thua khi nào: một phần khối ra khỏi bàn là rơi; R chơi lại.
4. Ô đặc biệt và nhờ AI giải; nút mở bảng chú giải đầy đủ và nút Chơi ngay.

Trên bàn mô phỏng: mũi tên chỉ hướng sắp lăn, phím tương ứng sáng lên, dòng dưới bàn ghi tư thế hiện tại.
←/→ (A/D) chuyển trang, Esc hoặc bấm ra ngoài để đóng.
"""
from __future__ import annotations

import math
import textwrap
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ursina import Button, Entity, Mesh, Quad, Text, camera, color, destroy, time

from gui.hud import _tile_swatch
from gui.theme import ACCENT, FONT_BOLD, FONT_REGULAR, FONT_SEMIBOLD, MUTED, card

Cell = Tuple[int, int]
Pose = Tuple[Tuple[Cell, ...], bool]   # (các ô khối chiếm, đang đứng)

WIDTH, HEIGHT = 1.26, 0.72
CS = 0.074                 # cạnh một ô của bàn mô phỏng
# Nhìn gần như từ trên xuống: mặt trên của khối chỉ nhô lên một chút so với ô nó chiếm (đứng 2 tầng, nằm 1
# tầng), để người mới thấy rõ khối chiếm đúng những ô nào; nhìn xiên nhiều thì khối đứng trông như lấn sang hàng trên
HU = CS * 0.14
ROWS, COLS = 3, 7          # bàn chữ nhật 3 × 7
DEMO_X = -WIDTH / 2 + 0.33  # tâm ngang vùng mô phỏng
BOARD_TOP = 0.13
KEY_SIZE, KEY_GAP = 0.048, 0.008
TEXT_X = -WIDTH / 2 + 0.67
TEXT_WRAP = 46
HINT_TIME, MOVE_TIME, GAP_TIME = 0.5, 0.3, 0.12   # giây: hiện mũi tên và phím, lăn, nghỉ
END_TIME, PAUSE_TIME = 0.9, 1.1                   # hoạt ảnh thắng / rơi, nghỉ trước khi chạy lại

COLORS = {
    "floor": color.hex("#9aa3ad"),
    "floor_side": color.hex("#69717a"),
    "goal_rim": color.hex("#6b737c"),
    "goal_hole": color.hex("#0b0f14"),
    "goal_glow": color.hex("#f2c94c"),
    "void": color.hex("#5b6672"),
    "block_top": color.hex("#f0f6fc"),
    "block_front": color.hex("#7f8a97"),
    "edge": ACCENT,
    "key": color.hex("#2f3d4d"),
    "key_on": color.hex("#2f6fd6"),
    "arrow": color.hex("#f2c94c"),
    "ok": color.hex("#7ee787"),
    "bad": color.hex("#ff7b72"),
    "primary": color.hex("#2f6fd6"),
    "button": color.hex("#2f3d4d"),
    "dot": color.hex("#3a4b5e"),
}
DIRS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
ARROW_ANGLE = {"right": 0, "down": 90, "left": 180, "up": -90}   # rotation_z của Ursina: dương là quay thuận chiều kim đồng hồ


def S(r: int, c: int) -> Pose:
    return ((r, c),), True


def L(*cells: Cell) -> Pose:
    return tuple(cells), False


# Mỗi trang: tiêu đề, nội dung, và (nếu có) kịch bản mô phỏng: ô có sàn, lỗ đích, tư thế đầu, các bước, kết thúc
PAGES = (
    {
        "title": "Mục tiêu",
        "body": ("Bạn điều khiển một khối hộp 1 × 1 × 2 trên một bàn lơ lửng.",
                 "Đưa khối tới LỖ ĐÍCH (ô có viền vàng) và để khối ĐỨNG THẲNG lọt xuống lỗ là thắng màn.",
                 "Khối nằm ngang qua lỗ thì không lọt, phải lăn sao cho khối dựng đứng đúng trên lỗ.",
                 "Cố gắng thắng với ít bước nhất: mỗi màn có ghi số bước tối ưu."),
        "floor": [(r, c) for r in range(ROWS) for c in range(COLS)],
        "goal": (1, 6),
        "start": S(1, 0),
        "steps": [("right", L((1, 1), (1, 2))), ("right", S(1, 3)), ("right", L((1, 4), (1, 5))),
                  ("right", S(1, 6))],
        "end": "win",
    },
    {
        "title": "Cách lăn khối",
        "body": ("Dùng phím mũi tên hoặc W A S D để lăn khối, mỗi lần một bước.",
                 "Khối ĐỨNG chiếm 1 ô; lăn một bước thì ngã xuống thành NẰM, chiếm 2 ô.",
                 "Khối nằm lăn theo chiều dài thì dựng đứng dậy; lăn theo chiều ngang thì vẫn nằm và chỉ dời sang một hàng.",
                 "Mẹo: khối đứng lại sau mỗi 3 ô nếu cứ lăn thẳng một hướng."),
        "floor": [(r, c) for r in range(ROWS) for c in range(COLS)],
        "goal": None,
        "start": S(1, 1),
        "steps": [("right", L((1, 2), (1, 3))), ("up", L((0, 2), (0, 3))), ("right", S(0, 4)),
                  ("down", L((1, 4), (2, 4))), ("left", L((1, 3), (2, 3))), ("up", S(0, 3)),
                  ("left", L((0, 1), (0, 2))), ("down", L((1, 1), (1, 2))), ("left", S(1, 0))],
        "end": None,
    },
    {
        "title": "Đừng để khối rơi",
        "body": ("Chỉ cần một phần khối ra khỏi bàn (ô trống, viền đứt) là khối rơi và bạn thua màn đó.",
                 "Thua thì bấm R để chơi lại từ đầu màn, không mất gì cả.",
                 "Trước khi lăn, hãy nhìn trước khối sẽ chiếm những ô nào: đứng 1 ô, nằm 2 ô."),
        "floor": [(r, c) for r in range(ROWS) for c in range(5)],
        "void": [(r, c) for r in range(ROWS) for c in (5, 6)],
        "goal": None,
        "start": S(1, 1),
        "steps": [("right", L((1, 2), (1, 3))), ("right", S(1, 4)), ("right", L((1, 5), (1, 6)))],
        "end": "fall",
    },
    {
        "title": "Ô đặc biệt và trợ giúp AI",
        "body": ("Các màn sau có thêm ô đặc biệt (xem hình bên trái). Bấm G trong game để xem chú giải đầy đủ.",
                 "Bí rồi? Bấm BFS, DFS, UCS hoặc A* ở cột phải: AI tìm lời giải và tự lăn khối cho bạn xem.",
                 "Nút So sánh chạy cả 5 thuật toán và so số bước, chi phí, thời gian, bộ nhớ.",
                 "Phím hay dùng: R chơi lại · N / P màn sau, trước · Space đổi khối con · M về trang chủ."),
        "legend": (("fragile", "Ô dễ vỡ", "Khối đứng lên là vỡ, rơi"),
                   ("soft", "Công tắc mềm", "Chạm vào là bật / tắt cầu"),
                   ("heavy", "Công tắc nặng", "Phải đứng thẳng lên mới bật"),
                   ("bridge_open", "Cầu", "Đi được khi đang mở"),
                   ("split", "Công tắc tách", "Tách khối thành 2 khối nhỏ")),
    },
)


def _wrap(text: str, width: int = TEXT_WRAP) -> str:
    return "\n".join(textwrap.wrap(text, width))


def _triangle() -> Mesh:
    """Tam giác mũi tên chỉ sang phải, tâm ở gốc; vẽ cả hai mặt để xoay hướng nào cũng thấy."""
    return Mesh(vertices=[(0.5, 0, 0), (-0.5, 0.5, 0), (-0.5, -0.5, 0)], triangles=[(0, 1, 2), (0, 2, 1)])


def _smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class HowToPlay(Entity):
    """Bảng hướng dẫn nhiều trang. on_play: nút "Chơi ngay" ở trang cuối; on_legend: mở bảng chú giải ô."""

    def __init__(self, on_play: Callable[[], None], on_legend: Callable[[], None]) -> None:
        super().__init__(parent=camera.ui, z=-0.6, enabled=False)
        self.on_play, self.on_legend = on_play, on_legend
        backdrop = Button(parent=self, model="quad", color=color.rgba(0, 0, 0, 0.6), scale=(4, 2), z=0.05,
                          on_click=self.close)
        backdrop.highlight_color = backdrop.pressed_color = backdrop.color
        blocker = Button(parent=self, model="quad", color=color.clear, scale=(WIDTH, HEIGHT), z=0.04,
                         highlight_color=color.clear, pressed_color=color.clear)   # bấm trong bảng không đóng bảng
        blocker.highlight_scale = 1
        card(self, -WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT, alpha=0.98)

        Text("CÁCH CHƠI", parent=self, position=(-WIDTH / 2 + 0.035, HEIGHT / 2 - 0.035), origin=(-0.5, 0.5),
             z=-0.01, scale=0.75, color=ACCENT, font=FONT_SEMIBOLD)
        self.close_button = self._button("Đóng  Esc", self.close, (WIDTH / 2 - 0.075, HEIGHT / 2 - 0.04),
                                         (0.11, 0.04), COLORS["button"], 0.7)
        self.title = Text("", parent=self, position=(TEXT_X, HEIGHT / 2 - 0.09), origin=(-0.5, 0.5), z=-0.01,
                          scale=1.45, font=FONT_BOLD)
        self.body = Text("", parent=self, position=(TEXT_X, HEIGHT / 2 - 0.165), origin=(-0.5, 0.5), z=-0.01,
                         scale=0.82, line_height=1.3, font=FONT_REGULAR)

        # ---- điều hướng trang ----
        bottom = -HEIGHT / 2 + 0.05
        self.prev_button = self._button("‹ Trước", lambda: self.show_page(self.page - 1),
                                        (TEXT_X + 0.07, bottom), (0.13, 0.05), COLORS["button"], 0.8)
        self.next_button = self._button("Tiếp ›", self._next, (WIDTH / 2 - 0.1, bottom), (0.15, 0.05),
                                        COLORS["primary"], 0.85)
        self.dots: List[Entity] = []
        dots_x = (TEXT_X + 0.14 + WIDTH / 2 - 0.18) / 2
        for i in range(len(PAGES)):
            self.dots.append(Entity(parent=self, model=Quad(radius=0.5), scale=0.014, z=-0.01,
                                    position=(dots_x + (i - (len(PAGES) - 1) / 2) * 0.03, bottom)))

        self.demo = Entity(parent=self)   # mọi thứ của trang hiện tại, dựng lại mỗi lần đổi trang
        self.page = 0
        self._script: Optional[dict] = None
        self._block: Dict[str, Entity] = {}
        self._keys: Dict[str, Entity] = {}
        self._arrow: Optional[Entity] = None
        self._caption: Optional[Text] = None
        self._goal_glow: Optional[Entity] = None
        self._phase, self._clock, self._step = "idle", 0.0, 0
        self._from: Tuple[float, ...] = (0, 0, 0, 0, 0)
        self._to: Tuple[float, ...] = (0, 0, 0, 0, 0)
        self._pose: Optional[Pose] = None

    # ---- mở, đóng, đổi trang ----

    @property
    def visible(self) -> bool:
        return self.enabled

    def open(self, page: int = 0) -> None:
        self.enabled = True
        self.show_page(page)

    def close(self) -> None:
        self.enabled = False

    def _next(self) -> None:
        if self.page == len(PAGES) - 1:
            self.close()
            self.on_play()
        else:
            self.show_page(self.page + 1)

    def show_page(self, page: int) -> None:
        self.page = max(0, min(len(PAGES) - 1, page))
        data = PAGES[self.page]
        self.title.text = data["title"]
        self.body.text = "\n\n".join(_wrap(f"•  {line}") for line in data["body"])
        last = self.page == len(PAGES) - 1
        self.next_button.text = "Chơi ngay" if last else "Tiếp ›"
        self.prev_button.enabled = self.page > 0
        for i, dot in enumerate(self.dots):
            dot.color = ACCENT if i == self.page else COLORS["dot"]
            dot.scale = 0.018 if i == self.page else 0.014
        for child in list(self.demo.children):
            destroy(child)
        self._block, self._keys, self._arrow, self._caption, self._goal_glow = {}, {}, None, None, None
        self._script = None
        if "steps" in data:
            self._build_demo(data)
        else:
            self._build_legend_page(data)

    # ---- dựng bàn mô phỏng ----

    def _cell_center(self, cell: Cell) -> Tuple[float, float]:
        r, c = cell
        x0 = DEMO_X - COLS * CS / 2
        return x0 + (c + 0.5) * CS, BOARD_TOP - (r + 0.5) * CS

    def _build_demo(self, data: dict) -> None:
        demo = self.demo
        goal = data.get("goal")
        for cell in data["floor"]:
            x, y = self._cell_center(cell)
            Entity(parent=demo, model=Quad(radius=0.12), color=COLORS["floor_side"], scale=CS * 0.9,
                   position=(x, y - CS * 0.13, -0.010))
            top = COLORS["goal_rim"] if cell == goal else COLORS["floor"]
            Entity(parent=demo, model=Quad(radius=0.12), color=top, scale=CS * 0.9, position=(x, y, -0.011))
            if cell == goal:
                Entity(parent=demo, model="quad", color=COLORS["goal_hole"], scale=CS * 0.66, position=(x, y, -0.012))
                self._goal_glow = Entity(parent=demo, model=Quad(mode="line", thickness=2.5),
                                         color=COLORS["goal_glow"], scale=CS * 0.72, position=(x, y, -0.013))
        for cell in data.get("void", ()):
            x, y = self._cell_center(cell)
            Entity(parent=demo, model=Quad(radius=0.12, mode="line", thickness=1.5), color=COLORS["void"],
                   scale=CS * 0.86, position=(x, y, -0.011))
        if data.get("void"):
            vx = sum(self._cell_center(c)[0] for c in data["void"]) / len(data["void"])
            Text("trống", parent=demo, position=(vx, BOARD_TOP + 0.022), origin=(0, 0), z=-0.02, scale=0.66,
                 color=MUTED)

        # khối: bóng, mặt trước, mặt trên, viền mặt trên
        self._block = {
            "foot": Entity(parent=demo, model=Quad(radius=0.12), color=ACCENT, z=-0.012),
            "shadow": Entity(parent=demo, model="quad", color=color.rgba(0, 0, 0, 0.35), z=-0.014),
            "front": Entity(parent=demo, model="quad", color=COLORS["block_front"], z=-0.016),
            "top": Entity(parent=demo, model="quad", color=COLORS["block_top"], z=-0.017),
        }
        self._block["edge"] = Entity(parent=self._block["top"], model=Quad(mode="line", thickness=2),
                                     color=COLORS["edge"], z=-0.001)
        # mũi tên hướng sắp lăn
        self._arrow = Entity(parent=demo, z=-0.03, enabled=False)
        Entity(parent=self._arrow, model="quad", color=COLORS["arrow"], scale=(CS * 0.55, CS * 0.13),
               x=CS * 0.28)
        Entity(parent=self._arrow, model=_triangle(), color=COLORS["arrow"], scale=CS * 0.36, x=CS * 0.66)

        # dòng tư thế và bàn phím mũi tên
        board_bottom = BOARD_TOP - ROWS * CS
        self._caption = Text("", parent=demo, position=(DEMO_X, board_bottom - 0.05), origin=(0, 0), z=-0.02,
                             scale=0.82, font=FONT_SEMIBOLD)
        kx, ky = DEMO_X, board_bottom - 0.17
        step = KEY_SIZE + KEY_GAP
        for name, (dx, dy) in {"up": (0, step), "left": (-step, 0), "down": (0, 0), "right": (step, 0)}.items():
            key = Entity(parent=demo, model=Quad(radius=0.2), color=COLORS["key"], scale=KEY_SIZE,
                         position=(kx + dx, ky + dy, -0.02))
            glyph = Entity(parent=key, model=_triangle(), color=color.white, scale=0.4, z=-0.001,
                           rotation_z=ARROW_ANGLE[name])
            key.glyph = glyph
            self._keys[name] = key
        Text("hoặc  W A S D", parent=demo, position=(kx + step * 1.5 + 0.02, ky), origin=(-0.5, 0), z=-0.02,
             scale=0.7, color=MUTED)

        self._script = data
        self._reset_demo()

    def _build_legend_page(self, data: dict) -> None:
        y = BOARD_TOP + 0.03
        for kind, name, rule in data["legend"]:
            x = -WIDTH / 2 + 0.08
            _tile_swatch(self.demo, kind, x, y, 0.06)
            Text(name, parent=self.demo, position=(x + 0.05, y + 0.014), origin=(-0.5, 0.5), z=-0.02, scale=0.8,
                 font=FONT_SEMIBOLD)
            Text(rule, parent=self.demo, position=(x + 0.05, y - 0.012), origin=(-0.5, 0.5), z=-0.02, scale=0.68,
                 color=MUTED)
            y -= 0.085
        self._button("Xem chú giải đầy đủ  G", self._open_legend, (DEMO_X, y - 0.005), (0.3, 0.048),
                     COLORS["button"], 0.75, parent=self.demo)

    def _open_legend(self) -> None:
        self.close()
        self.on_legend()

    # ---- hoạt ảnh ----

    def _pose_box(self, pose: Pose) -> Tuple[float, float, float, float, float]:
        """(tâm x, đáy chân khối y, rộng, sâu, chiều cao) của khối ở tư thế pose."""
        cells, standing = pose
        m = CS * 0.09
        xs = [self._cell_center(c)[0] for c in cells]
        ys = [self._cell_center(c)[1] for c in cells]
        left, right = min(xs) - CS / 2 + m, max(xs) + CS / 2 - m
        top, bottom = max(ys) + CS / 2 - m, min(ys) - CS / 2 + m
        return (left + right) / 2, bottom, right - left, top - bottom, 2.0 if standing else 1.0

    def _draw_block(self, box: Sequence[float], drop: float = 0.0, alpha: float = 1.0) -> None:
        cx, bottom, w, d, h = box
        bottom -= drop
        b = self._block
        foot_bottom = bottom + drop
        b["foot"].position = (cx, foot_bottom + d / 2, -0.012)   # ô khối chiếm: không rơi theo khối
        b["foot"].scale = (w + CS * 0.12, d + CS * 0.12)
        b["foot"].alpha = 0.45 * alpha
        # bóng lệch xuống dưới bên phải, khối càng cao bóng càng dài
        b["shadow"].position = (cx + h * CS * 0.06, foot_bottom + d / 2 - h * CS * 0.08, -0.014)
        b["shadow"].scale = (w, d)
        b["shadow"].alpha = 0.4 * alpha * (1 - min(1.0, drop * 8))
        b["front"].position = (cx, bottom + h * HU / 2, -0.016)
        b["front"].scale = (w, max(0.0001, h * HU))
        b["top"].position = (cx, bottom + d / 2 + h * HU, -0.017)
        b["top"].scale = (w, d)
        for part in ("front", "top"):
            b[part].alpha = alpha
        b["edge"].alpha = alpha

    def _reset_demo(self) -> None:
        data = self._script
        self._pose = data["start"]
        self._step = 0
        self._phase, self._clock = "idle", 0.0
        self._draw_block(self._pose_box(self._pose))
        self._update_caption()
        if self._goal_glow is not None:
            self._goal_glow.color = COLORS["goal_glow"]
            self._goal_glow.scale = CS * 0.72

    def _update_caption(self, text: Optional[str] = None, tint: color.Color = color.white) -> None:
        if self._caption is None:
            return
        if text is None:
            standing = self._pose[1]
            text = "Khối đang ĐỨNG: chiếm 1 ô" if standing else "Khối đang NẰM: chiếm 2 ô"
            tint = color.white
        self._caption.text = text
        self._caption.color = tint

    def _light_key(self, name: Optional[str]) -> None:
        for key_name, key in self._keys.items():
            on = key_name == name
            key.color = COLORS["key_on"] if on else COLORS["key"]
            key.scale = KEY_SIZE * (1.1 if on else 1.0)

    def _show_arrow(self, name: str) -> None:
        cx, bottom, w, d, h = self._pose_box(self._pose)
        dr, dc = DIRS[name]
        # mũi tên bắt đầu ở mép khối theo hướng lăn (mặt trên khối nâng lên h tầng)
        x = cx + dc * w / 2
        y = bottom + d / 2 + h * HU - dr * d / 2
        self._arrow.position = (x, y, -0.03)
        self._arrow.rotation_z = ARROW_ANGLE[name]
        self._arrow.enabled = True

    def update(self) -> None:
        if self._script is None:
            return
        self._clock += time.dt
        data = self._script
        steps = data["steps"]
        if self._phase == "idle":
            if self._clock >= GAP_TIME:
                if self._step < len(steps):
                    name, _ = steps[self._step]
                    self._show_arrow(name)
                    self._light_key(name)
                    self._phase, self._clock = "hint", 0.0
                else:
                    self._phase, self._clock = "end", 0.0
                    self._start_end(data.get("end"))
        elif self._phase == "hint":
            if self._clock >= HINT_TIME:
                _, target = steps[self._step]
                self._from, self._to = self._pose_box(self._pose), self._pose_box(target)
                self._arrow.enabled = False
                self._phase, self._clock = "move", 0.0
        elif self._phase == "move":
            t = _smooth(self._clock / MOVE_TIME)
            # nhích lên một chút giữa chừng để thấy khối lật qua chứ không trượt
            box = [a + (b - a) * t for a, b in zip(self._from, self._to)]
            box[4] += 0.6 * math.sin(math.pi * t)
            self._draw_block(box)
            if self._clock >= MOVE_TIME:
                self._pose = steps[self._step][1]
                self._step += 1
                self._draw_block(self._pose_box(self._pose))
                self._light_key(None)
                self._update_caption()
                self._phase, self._clock = "idle", 0.0
        elif self._phase == "end":
            self._animate_end(data.get("end"), min(1.0, self._clock / END_TIME))
            if self._clock >= END_TIME:
                self._phase, self._clock = "pause", 0.0
        elif self._phase == "pause":
            if self._clock >= PAUSE_TIME:
                self._reset_demo()

    def _start_end(self, kind: Optional[str]) -> None:
        if kind == "win":
            self._update_caption("Đứng thẳng trên lỗ đích: THẮNG!", COLORS["ok"])
        elif kind == "fall":
            self._update_caption("Khối rơi khỏi bàn: THUA. Bấm R để chơi lại", COLORS["bad"])

    def _animate_end(self, kind: Optional[str], t: float) -> None:
        box = self._pose_box(self._pose)
        if kind == "win":
            # khối lọt xuống lỗ: thấp dần rồi biến mất, viền lỗ đích lóe sáng
            cx, bottom, w, d, h = box
            self._draw_block((cx, bottom, w * (1 - 0.2 * t), d * (1 - 0.2 * t), h * (1 - t)), alpha=1 - t ** 2)
            if self._goal_glow is not None:
                self._goal_glow.scale = CS * (0.72 + 0.5 * math.sin(math.pi * t))
        elif kind == "fall":
            self._draw_block(box, drop=0.25 * t * t, alpha=1 - t)

    # ---- tiện ích ----

    def _button(self, label: str, on_click: Callable[[], None], position: Tuple[float, float],
                size: Tuple[float, float], tint: color.Color, text_size: float,
                parent: Optional[Entity] = None) -> Button:
        button = Button(text=label, parent=parent or self, position=(position[0], position[1], -0.02), scale=size,
                        color=tint, radius=0.25, text_size=text_size, on_click=on_click)
        button.text_entity.font = FONT_SEMIBOLD
        button.highlight_color = tint.tint(0.15)
        button.pressed_color = tint.tint(-0.12)
        button.highlight_scale = 1.03
        return button

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        if key in ("right arrow", "d"):
            self.show_page(self.page + 1)
        elif key in ("left arrow", "a"):
            self.show_page(self.page - 1)
        elif key == "escape":
            self.close()
        elif key == "enter":
            self._next()
