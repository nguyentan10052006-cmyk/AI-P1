"""Cửa sổ GUI Ursina: vẽ bàn (V18) và chơi tay bằng engine thật (V19).

Chạy trong Source/: python main.py [mã màn, ví dụ 05], hoặc python -m gui.app [mã màn]
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from ursina import AmbientLight, DirectionalLight, Entity, Text, Ursina, Vec3, camera, color, destroy, invoke, window

from bloxorz.level import Level, LevelError, load_level
from bloxorz.rules import FELL, WON, StepResult, step
from bloxorz.state import DELTA, Action, Dir, Orient, State
from gui.block_view import BlockView
from gui.board_view import BoardView

LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
HELP = "Mũi tên / WASD: lăn   Space: đổi khối con   R: chơi lại   N / P: màn sau / trước"
KEY_DIRS = {
    "up arrow": Dir.UP, "w": Dir.UP,
    "down arrow": Dir.DOWN, "s": Dir.DOWN,
    "left arrow": Dir.LEFT, "a": Dir.LEFT,
    "right arrow": Dir.RIGHT, "d": Dir.RIGHT,
}
MOVE_TIME = 0.14   # giây cho một lần lăn
FALL_TIME = 0.7
WIN_TIME = 0.45


class Game(Entity):
    """Giữ trạng thái chơi; mọi luật đi qua bloxorz.rules.step(), GUI không tự tính (docs/07 §5)."""

    def __init__(self, paths: List[Path], start_index: int = 0) -> None:
        super().__init__()
        self.paths = paths
        self.index = start_index
        self.level: Optional[Level] = None
        self.board: Optional[BoardView] = None
        self.block: Optional[BlockView] = None
        self.state: Optional[State] = None
        self.active_cube = 0     # State không lưu khối con đang điều khiển, GUI tự giữ (docs/07 §5)
        self.steps = 0
        self.busy = False        # đang chạy hoạt ảnh: bỏ qua phím để state không đi trước hình (docs/07 §7)
        self.over = False        # đã thắng hoặc rơi: chờ R
        self.info = Text(parent=camera.ui, position=window.top_left + Vec3(0.02, -0.02, 0), scale=1.1)
        self.message = Text(parent=camera.ui, origin=(0, 0), y=0.38, scale=2)
        self.load(start_index)

    # ---- đổi màn, chơi lại ----

    def load(self, index: int) -> None:
        self.index = index % len(self.paths)
        path = self.paths[self.index]
        if self.board is not None:
            destroy(self.board)   # khối là con của bàn nên bị hủy cùng
        self.board = self.block = self.level = self.state = None
        try:
            self.level = load_level(path, path.stem)
        except LevelError as exc:
            self.info.text = f"Không nạp được {path.name}: {exc}\n{HELP}"
            self.message.text = ""
            return
        self.board = BoardView(self.level)
        self.board.fit_camera()
        self.block = BlockView(self.level.initial_state(), parent=self.board)
        self.restart()

    def restart(self) -> None:
        if self.level is None:
            return
        self.state = self.level.initial_state()
        self.active_cube = 0
        self.steps = 0
        self.busy = self.over = False
        self.board.set_open_bridges(self.state.open_bridges)
        self.block.show(self.state)
        self.message.text = ""
        self._update_info()

    def _update_info(self) -> None:
        level = self.level
        self.info.text = (f"{level.name}  ·  nhóm {level.group}  ·  bước đã đi {self.steps}"
                          f"  ·  tối ưu {level.par}\n{HELP}")

    # ---- phím ----

    def input(self, key: str) -> None:
        if key == "n":
            self.load(self.index + 1)
        elif key == "p":
            self.load(self.index - 1)
        elif key == "r":
            self.restart()
        elif self.state is None or self.busy or self.over:
            return
        elif key == "space" and self.state.orient is Orient.SPLIT:
            self.active_cube = 1 - self.active_cube
            self.block.show(self.state, self.active_cube)
        elif key in KEY_DIRS:
            self.roll(KEY_DIRS[key])

    # ---- một lượt đi ----

    def roll(self, direction: Dir) -> None:
        before = self.state
        cube = self.active_cube if before.orient is Orient.SPLIT else None
        result = step(self.level, before, Action(direction, cube))
        self.steps += 1
        self.busy = True
        self.block.show(result.moved, self._follow(before, direction, result.moved), duration=MOVE_TIME)
        self._update_info()
        invoke(self._settle, before, direction, result, delay=MOVE_TIME)

    def _settle(self, before: State, direction: Dir, result: StepResult) -> None:
        """Sau khi lăn xong: cập nhật cầu, rồi tách, ghép, thắng hoặc rơi theo kết quả của engine."""
        self.board.set_open_bridges(result.state.open_bridges)
        if result.status == FELL:
            self.over = True
            self.block.drop(12, FALL_TIME)
            self.message.text = "Rơi khỏi bàn! Bấm R để chơi lại"
            self.message.color = color.hex("#ff7b72")
            invoke(setattr, self, "busy", False, delay=FALL_TIME)
            return
        self.state = result.state
        self.active_cube = self._follow(before, direction, self.state)
        self.block.show(self.state, self.active_cube)
        if result.status == WON:
            self.over = True
            self.block.drop(2.2, WIN_TIME)
            self.message.text = f"Thắng sau {self.steps} bước! (tối ưu {self.level.par})"
            self.message.color = color.hex("#7ee787")
        self.busy = False

    def _follow(self, before: State, direction: Dir, after: State) -> int:
        """Chỉ số khối con đang điều khiển trong after.

        Engine sắp lại hai khối con sau mỗi bước, nên tìm lại khối vừa đi theo ô mới của nó.
        Vừa tách ra thì điều khiển khối thứ nhất.
        """
        if after.orient is not Orient.SPLIT:
            return 0
        if before.orient is not Orient.SPLIT:
            return 0
        r, c = before.cells()[self.active_cube]
        dr, dc = DELTA[direction]
        cells = after.cells()
        return cells.index((r + dr, c + dc)) if (r + dr, c + dc) in cells else 0


def setup_scene() -> None:
    window.color = color.hex("#1d2733")
    sun = DirectionalLight(shadows=False, color=color.hsv(0, 0, 0.7))
    sun.look_at(Vec3(0.4, -1, 0.7))
    AmbientLight(color=color.hsv(0, 0, 0.35))


def run(level_id: str = "01") -> int:
    paths = sorted(LEVELS_DIR.glob("*.json"))
    if not paths:
        print(f"Không có màn nào trong {LEVELS_DIR}", file=sys.stderr)
        return 1
    ids = [p.stem for p in paths]
    start = ids.index(level_id) if level_id in ids else 0

    app = Ursina(title="Bloxorz Solver", development_mode=False)
    setup_scene()
    Game(paths, start)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1] if len(sys.argv) > 1 else "01"))
