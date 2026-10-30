"""Cửa sổ GUI Ursina: vẽ bàn (V18), chơi tay bằng engine thật (V19), thông báo và hoạt ảnh ô đặc biệt (V20),
nút Solve, So sánh, Hủy và khối tự lăn theo lời giải (V21); khối lật quanh cạnh, đổ nghiêng khi rơi,
mở màn, khử răng cưa (GAME_UI_UX_SPECIFICATION §6, §9).

Chạy trong Source/: python main.py [mã màn, ví dụ 05], hoặc python -m gui.app [mã màn]
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Union

from ursina import (AmbientLight, DirectionalLight, Entity, Mesh, Text, Ursina, Vec3, camera, color, curve, destroy,
                    invoke, time, window)
from panda3d.core import AntialiasAttrib, loadPrcFileData
from ursina.shaders import unlit_shader

from bloxorz.costs import compute_step_cost
from bloxorz.level import Level, LevelError, load_level
from bloxorz.problem import Problem
from bloxorz.rules import FELL, WON, StepResult, step
from bloxorz.state import DELTA, Action, Dir, Orient, State
from gui.block_view import BlockView
from gui.board_view import BoardView
from gui.camera_controller import CameraController
from gui.hud import LABELS, Hud
from gui.popup import ResultPopup
from gui.theme import FONT_BOLD, FONT_SEMIBOLD, use_fonts
from solvers import ALGORITHMS                                   # docs/07 §2: gui chỉ dùng ALGORITHMS và runner
from solvers.runner import CompareJob, SolveJob, start_compare, start_solver

LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
# Dòng phím tắt dưới đáy chỉ ghi các phím hay dùng; F1 mở bảng đầy đủ (hud.SHORTCUTS)
HELP = ("WASD / mũi tên: lăn   ·   Space: đổi khối   ·   R: chơi lại   ·   N / P: màn sau / trước"
        "   ·   H: ẩn kết quả   ·   F1: tất cả phím tắt")
# Bảng màu theo GAME_UI_UX_SPECIFICATION.md §2.1
THEME = {
    "bg_top": color.hex("#18212b"),   # nền gradient: xám đậm ở trên xuống đen ở dưới
    "bg_bottom": color.hex("#0b0f14"),
    "accent": color.hex("#38bdf8"),
    "muted": color.hex("#9aa3ad"),
    "ok": color.hex("#7ee787"),
    "warn": color.hex("#f2c94c"),
    "bad": color.hex("#ff7b72"),
}
KEY_DIRS = {
    "up arrow": Dir.UP, "w": Dir.UP,
    "down arrow": Dir.DOWN, "s": Dir.DOWN,
    "left arrow": Dir.LEFT, "a": Dir.LEFT,
    "right arrow": Dir.RIGHT, "d": Dir.RIGHT,
}
MOVE_TIME = 0.17   # giây cho một lần lật khối
FALL_TIME = 0.8
WIN_TIME = 0.45
SPLIT_TIME = 0.36  # hai khối con bay theo vòng cung tới ô đích của công tắc tách
BRIDGE_TIME = 0.3
SPAWN_TIME = 0.4   # khối rơi xuống chỗ xuất phát khi vào màn hoặc chơi lại
NOTICE_TIME = 2.0  # thông báo sự kiện tự tắt sau chừng này giây
NOTICE_FADE = 0.3
NOTICE_Y = 0.31
REPLAY_PAUSE = 0.06   # giây nghỉ giữa hai bước khi khối tự lăn theo lời giải
FPS_INTERVAL = 0.5    # giây giữa hai lần cập nhật bộ đếm FPS
SOLVE_TIMEOUT = 60.0  # docs/07 §6 quy tắc 3
# Hàm chi phí V13 cho nút Giải và So sánh (docs/04 §2: path_cost tính bằng hàm chi phí của UCS).
# Tạm bật ngày 30/10, chờ nhóm chốt; đổi thành None để quay về chi phí 1 mỗi bước.
COST_FN = compute_step_cost

SWITCH_KINDS = {"soft": "Công tắc mềm", "heavy": "Công tắc nặng", "split": "Công tắc tách"}
# Công tắc dùng "links" với hiệu ứng khác nhau cho từng cầu có effect rỗng (V03)
SWITCH_EFFECTS = {"toggle": "đổi trạng thái cầu", "open": "mở cầu", "close": "đóng cầu", "": "đổi trạng thái các cầu"}
# Hộp kết thúc khi rơi: (tiêu đề, giải thích) theo lý do rơi của engine (sự kiện "fell")
FALL_TEXTS = {
    "fragile": ("Ô dễ vỡ bị vỡ", "Khối đứng thẳng trên ô cam nên ô vỡ."),
    "bridge_closed": ("Cầu đang đóng", "Khối đi vào ô cầu chưa mở."),
}
FALL_DEFAULT = ("Khối rơi khỏi bàn", "Có phần khối không còn ô đỡ bên dưới.")
POPUP_DELAY = 0.15   # hộp kết thúc hiện sau khi hoạt ảnh rơi hoặc lọt lỗ gần xong


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
        self.turn = 0            # tăng mỗi lần đổi màn hoặc chơi lại; lệnh invoke của lượt cũ thấy lệch thì bỏ qua
        # Góc trái trên: tên màn (đậm), nhóm và số bước tối ưu, số bước đã đi
        self.info = Text(parent=camera.ui, position=window.top_left + Vec3(0.02, -0.018, 0), scale=1.6,
                         font=FONT_BOLD)
        self.subtitle = Text(parent=camera.ui, position=window.top_left + Vec3(0.022, -0.068, 0), scale=0.82,
                             color=THEME["muted"])
        self.moves = Text(parent=camera.ui, position=window.top_left + Vec3(0.022, -0.1, 0), scale=1.15,
                          color=THEME["accent"], font=FONT_SEMIBOLD)
        self.help = Text(HELP, parent=camera.ui, origin=(0, 0), y=window.bottom.y + 0.022, scale=0.76,
                         color=THEME["muted"])
        # Thông báo sự kiện (công tắc, tách, ghép) ở phía trên vùng bàn; kết thúc màn dùng hộp popup
        self.notice = Text(parent=camera.ui, origin=(0, 0), y=NOTICE_Y, scale=1.2, color=THEME["warn"],
                           font=FONT_SEMIBOLD)
        self._notice_id = 0
        self.fps = Text(parent=camera.ui, position=window.bottom_left + Vec3(0.02, 0.022, 0), origin=(-0.5, 0),
                        scale=0.65, color=THEME["muted"])
        self.popup = ResultPopup()
        self.board_center_x = 0.0   # tâm ngang vùng bàn trên màn hình (đổi khi khung kết quả hiện hay ẩn)
        self._fps_frames, self._fps_time = 0, 0.0
        # Solver chạy ở tiến trình riêng; GUI chỉ giữ job và gọi poll() trong update() (docs/07 §6 quy tắc 2)
        self.job: Optional[Union[SolveJob, CompareJob]] = None
        self.job_name = ""                       # khóa ALGORITHMS của nút Solve đang chạy; rỗng khi So sánh
        self.replay: Optional[List[Action]] = None   # lời giải đang được tự lăn
        self.replay_index = 0
        self.replay_wait = 0.0
        self.replay_label = ""                   # tên thuật toán của lời giải đang tự lăn (hiện trong hộp thắng)
        self.camera_ctrl = CameraController()
        self.hud = Hud([p.stem for p in paths], on_new_game=lambda: self.load(0), on_restart=self.restart,
                       on_pick_level=self.load, on_solve=self.solve, on_compare=self.compare,
                       on_prev=lambda: self.load(self.index - 1), on_next=lambda: self.load(self.index + 1),
                       on_cancel=self.cancel,
                       on_rotate_cam=self.camera_ctrl.rotate_preset,
                       on_tilt_cam=self.camera_ctrl.tilt_preset,
                       on_toggle_top_down=self.camera_ctrl.toggle_top_down,
                       on_reset_cam=self.camera_ctrl.reset_view)
        self.camera_ctrl.on_view_change = self._on_view_change
        self.hud.on_panel_change = self._frame_board
        self.load(start_index)

    # ---- đổi màn, chơi lại ----

    def load(self, index: int) -> None:
        self.index = index % len(self.paths)
        path = self.paths[self.index]
        self.turn += 1   # màn nạp lỗi thì restart() không chạy, vẫn phải hủy lượt đang dở
        self._stop_job()   # lời giải của màn cũ không dùng được cho màn mới
        self.replay = None
        self.hud.clear_results()
        self.hud.set_current_level(self.index)
        if self.board is not None:
            destroy(self.board)   # khối là con của bàn nên bị hủy cùng
        self.board = self.block = self.level = self.state = None
        try:
            self.level = load_level(path, path.stem)
        except LevelError as exc:
            self.info.text = f"Không nạp được {path.name}"
            self.subtitle.text = str(exc)
            self.moves.text = ""
            self.popup.hide()
            return
        self.board = BoardView(self.level)
        self.board.fit_camera(self.camera_ctrl)
        self.block = BlockView(self.level.initial_state(), parent=self.board)
        intro = self.board.play_intro()
        self.restart(spawn_delay=intro * 0.7)   # khối rơi xuống khi phần lớn các ô đã vào chỗ

    def restart(self, spawn_delay: float = 0.0) -> None:
        if self.level is None:
            return
        self.turn += 1
        self.replay = None   # solver đang chạy thì vẫn để chạy: bài toán luôn tính từ trạng thái đầu của màn
        self.state = self.level.initial_state()
        self.active_cube = 0
        self.steps = 0
        self.over = False
        self.board.reset(self.state.open_bridges)
        # khối rơi xuống chỗ xuất phát; bỏ qua phím tới khi khối chạm sàn (khối tự lăn cũng chờ, docs/07 §7)
        self.busy = True
        self.block.spawn(self.state, SPAWN_TIME, delay=spawn_delay)
        invoke(self._unbusy, self.turn, delay=spawn_delay + SPAWN_TIME)
        self.popup.hide()
        self.show_notice("")
        self._update_info()

    def _frame_board(self, panel_visible: bool) -> None:
        """Khung kết quả hiện thì chỉ dời hoặc thu bàn khi bàn thật sự bị khung che; ẩn thì trả về như cũ.

        Đo hoành độ trên màn hình của các góc ô ở góc nhìn hiện tại (chưa căn), được đoạn [L, R]. Vùng trống
        là [A, B] giữa mép phải khung và mép trái cột thẻ. Lùi camera xa k lần thì hình co về tâm màn hình k lần
        (k = 1 nếu bàn đã vừa vùng trống), sau đó dịch ngang s (film offset) ít nhất có thể để [L/k + s, R/k + s]
        nằm trong [A, B]. Bàn vốn không chạm khung thì k = 1, s = 0: không đổi gì.
        """
        if not panel_visible or self.board is None:
            self.camera_ctrl.set_frame(1.0, 0.0)
            center_x = 0.0
        else:
            xs = self.camera_ctrl.project_unframed(self.board.corners())
            left, right = min(xs), max(xs)
            area_left, area_right = self.hud.panel_right + 0.03, self.hud.dock_left - 0.02
            scale = max(1.0, (right - left) / (area_right - area_left))
            low, high = area_left - left / scale, area_right - right / scale
            shift = min(max(0.0, low), high)
            self.camera_ctrl.set_frame(scale, shift / window.aspect_ratio)
            center_x = (left + right) / 2 / scale + shift
        self.board_center_x = center_x
        self.notice.animate_x(center_x, duration=0.2, curve=curve.out_quad)   # thông báo và hộp kết thúc
        self.popup.move_to(center_x)                                         # nằm giữa vùng bàn

    def _on_view_change(self, name: str) -> None:
        """Đổi góc camera: cập nhật nhãn; khung kết quả đang hiện thì đo và căn lại bàn ở góc mới."""
        self.hud.set_camera_view(name)
        if self.hud.panel.enabled and self.board is not None:
            self._frame_board(True)

    def _update_info(self) -> None:
        level = self.level
        cube = ""
        if self.state is not None and self.state.orient is Orient.SPLIT:
            cube = f"   ·   khối con {self.active_cube + 1}/2 (Space để đổi)"
        self.info.text = f"Màn {level.id}"
        self.subtitle.text = f"Nhóm {level.group.upper()}   ·   tối ưu {level.par} bước"
        moves = f"Số bước: {self.steps}{cube}"
        if self.moves.text != moves:
            bump = self.steps > 0 and not self.moves.text.startswith(f"Số bước: {self.steps}")
            self.moves.text = moves
            if bump:   # số bước vừa tăng: nảy nhẹ 1 → 1.15 → 1 (§3.1)
                self.moves.scale = 1.15 * 1.15
                self.moves.animate_scale(1.15, duration=0.12, curve=curve.out_quad)

    def show_notice(self, text: str) -> None:
        """Dòng thông báo sự kiện dưới dòng thắng/thua: trượt xuống khi hiện, mờ dần sau NOTICE_TIME giây."""
        self._notice_id += 1
        for animation in self.notice.animations:
            animation.kill()
        self.notice.animations.clear()
        self.notice.text = text
        self.notice.alpha, self.notice.y = 1.0, NOTICE_Y
        if text:
            self.notice.alpha, self.notice.y = 0.0, NOTICE_Y + 0.02
            self.notice.animate("alpha", 1.0, duration=0.18, curve=curve.out_quad)
            self.notice.animate_y(NOTICE_Y, duration=0.18, curve=curve.out_quad)
            invoke(self._clear_notice, self._notice_id, delay=NOTICE_TIME)

    def _clear_notice(self, notice_id: int) -> None:
        if notice_id == self._notice_id:   # chưa có thông báo mới đè lên
            self.notice.animate("alpha", 0.0, duration=NOTICE_FADE, curve=curve.in_quad)
            invoke(self._erase_notice, notice_id, delay=NOTICE_FADE)

    def _erase_notice(self, notice_id: int) -> None:
        if notice_id == self._notice_id:
            self.notice.text = ""
            self.notice.alpha = 1.0

    # ---- phím ----

    def input(self, key: str) -> None:
        if key == "n":
            self.load(self.index + 1)
        elif key == "p":
            self.load(self.index - 1)
        elif key == "r":
            self.restart()
        elif key == "q":
            self.camera_ctrl.rotate_preset(-1)
        elif key == "e":
            self.camera_ctrl.rotate_preset(1)
        elif key == "z":
            self.camera_ctrl.tilt_preset(-1)
        elif key == "x":
            self.camera_ctrl.tilt_preset(1)
        elif key == "h":
            self.hud.toggle_panel()
        elif key == "escape":
            if self.hud.overlay_open:
                self.hud.close_picker()
                self.hud.close_help()
            else:
                self.popup.hide()
        elif key == "control+k":
            self.hud.toggle_picker()
        elif key == "f1":
            self.hud.toggle_help()
        elif key == "enter":
            self.popup.press_primary()
        elif key == "t":
            self.camera_ctrl.toggle_top_down()
        elif key == "f":
            self.camera_ctrl.reset_view()
        elif key in ("scroll up", "wheel_up"):
            self.camera_ctrl.zoom(1.0)
        elif key in ("scroll down", "wheel_down"):
            self.camera_ctrl.zoom(-1.0)
        elif self.state is None or self.busy or self.over or self.replay is not None or self.hud.overlay_open:
            return   # đang tự lăn hoặc đang mở bảng chọn màn, phím tắt: không nhận phím lăn; R, N, P, camera vẫn được
        elif key == "space" and self.state.orient is Orient.SPLIT:
            self.active_cube = 1 - self.active_cube
            self.block.show(self.state, self.active_cube)
            self._update_info()
        elif key in KEY_DIRS:
            self.roll(KEY_DIRS[key])   # camera không lệch quá ±40° (dưới 45°) nên hướng phím luôn khớp màn hình

    # ---- Solve, So sánh, Hủy (V21) ----

    def solve(self, name: str) -> None:
        if self.level is None or self.job is not None:
            return
        self.hud.clear_results()
        self.popup.hide()   # kết quả mới thay cho hộp kết thúc của lượt trước
        self.job, self.job_name = start_solver(ALGORITHMS[name], self._problem(), SOLVE_TIMEOUT), name
        self.hud.set_running(True)
        self.hud.highlight_solver(name)

    def compare(self) -> None:
        if self.level is None or self.job is not None:
            return
        self.hud.clear_results()
        self.popup.hide()   # kết quả mới thay cho hộp kết thúc của lượt trước
        self.job, self.job_name = start_compare(self._problem(), timeout_s=SOLVE_TIMEOUT), ""
        self.hud.set_running(True)

    def _problem(self) -> Problem:
        """Bài toán cho solver: luôn tính từ trạng thái đầu của màn, chi phí theo COST_FN."""
        return Problem(self.level, cost_fn=COST_FN)

    def cancel(self) -> None:
        """Nút Hủy: dừng solver đang chạy (lần poll() sau trả kết quả đã hủy) hoặc dừng khối đang tự lăn."""
        if self.job is not None:
            self.job.cancel()
        elif self.replay is not None:
            self.replay = None
            self.hud.show_status("Đã dừng tự lăn. Bấm R để chơi lại", THEME["muted"])

    def _stop_job(self) -> None:
        if self.job is not None:
            self.job.cancel()
            self.job = None
            self.hud.set_running(False)

    def update(self) -> None:
        self.camera_ctrl.update()
        self._update_fps()
        if self.job is not None:
            self._poll_job()
        if self.replay is not None:
            self._replay_step()

    def _poll_job(self) -> None:
        job = self.job
        if isinstance(job, CompareJob):
            results = job.poll()
            self.hud.show_compare(job.names, results, job.running, job.elapsed)
            if job.done:
                self.job = None
                self.hud.set_running(False)
                self.hud.show_status("Đã hủy So sánh" if job.cancelled else f"So sánh xong trên {self.level.name}")
            else:
                self.hud.show_status(f"So sánh: {LABELS[job.running]} đang tìm… {job.elapsed:.1f} s")
                self.hud.highlight_solver(job.running)
            return
        outcome = job.poll()
        if outcome is None:
            self.hud.show_status(f"{LABELS[self.job_name]} đang tìm… {job.elapsed:.1f} s")
            return
        self.job = None
        self.hud.set_running(False)
        self.hud.show_result(self.job_name, outcome)
        if outcome.get("ok") and outcome["status"] == "solved":
            self.restart()   # lời giải tính từ trạng thái đầu
            self.replay, self.replay_index, self.replay_wait = list(outcome["path"]), 0, REPLAY_PAUSE
            self.replay_label = LABELS[self.job_name]

    def _replay_step(self) -> None:
        """Khối tự lăn: mỗi bước gọi rules.step() như khi chơi tay (docs/07 §5), chờ hoạt ảnh xong mới đi tiếp."""
        if self.busy:
            return
        if self.over or self.replay_index >= len(self.replay):
            self.replay = None
            return
        if self.replay_wait > 0:
            self.replay_wait -= time.dt
            return
        action = self.replay[self.replay_index]
        if action.cube is not None:
            self.active_cube = action.cube   # Action.cube đã tính theo thứ tự khối con của trạng thái lúc đó
        self.replay_index += 1
        self.replay_wait = REPLAY_PAUSE
        self.roll(action.dir)

    # ---- một lượt đi ----

    def roll(self, direction: Dir) -> None:
        before = self.state
        cube = self.active_cube if before.orient is Orient.SPLIT else None
        result = step(self.level, before, Action(direction, cube))
        self.steps += 1
        self.busy = True
        self.block.roll(before, direction, result.moved, self._follow(before, direction, result.moved),
                        MOVE_TIME, active_before=cube)
        self._update_info()
        invoke(self._settle, self.turn, before, direction, result, delay=MOVE_TIME)

    def _settle(self, turn: int, before: State, direction: Dir, result: StepResult) -> None:
        """Sau khi lăn xong: cập nhật cầu, rồi tách, ghép, thắng hoặc rơi theo kết quả của engine."""
        if turn != self.turn:   # đã bấm R hoặc đổi màn trong lúc khối đang lăn
            return
        self.board.set_open_bridges(result.state.open_bridges, duration=BRIDGE_TIME)
        for event in result.events:
            if event["type"] in ("switch", "split"):
                self.board.press_switch(event["at"] if event["type"] == "switch" else event["from"])
        self._announce(result.events)
        if result.status == FELL:
            fell = next(e for e in result.events if e["type"] == "fell")
            if fell["reason"] == "fragile":
                self.board.break_tile(fell["at"], FALL_TIME)
            self.over = True
            hanging = [cell for cell in result.state.cells()
                       if not self.board.supports(cell, result.state.open_bridges)]
            self.block.fall(result.state, hanging, FALL_TIME)
            invoke(self._show_fall, turn, fell["reason"], delay=FALL_TIME * 0.7)
            invoke(self._unbusy, turn, delay=FALL_TIME)
            return
        self.state = result.state
        self.active_cube = self._follow(before, direction, self.state)
        split = any(e["type"] == "split" for e in result.events)
        if split:
            self.block.split(self.state, self.active_cube, SPLIT_TIME)
        else:
            self.block.show(self.state, self.active_cube, pulse=any(e["type"] == "merge" for e in result.events))
        self._update_info()
        if result.status == WON:
            self.over = True
            self.block.sink(WIN_TIME)
            self.board.celebrate_goal()
            self.hud.mark_solved(self.index)
            invoke(self._show_win, turn, self.replay_label if self.replay is not None else "",
                   delay=WIN_TIME + POPUP_DELAY)
        if split:
            invoke(self._unbusy, turn, delay=SPLIT_TIME)
        else:
            self.busy = False

    # ---- hộp kết thúc màn ----

    def _show_win(self, turn: int, solver: str) -> None:
        if turn != self.turn:   # đã chơi lại hoặc đổi màn trước khi hộp kịp hiện
            return
        par, extra = self.level.par, self.steps - self.level.par
        if extra <= 0:
            verdict = ("Đúng số bước tối ưu!", THEME["ok"])
        else:
            verdict = (f"Nhiều hơn tối ưu {extra} bước, thử lại để rút ngắn?", THEME["warn"])
        first = f"Lời giải của {solver}: {self.steps} bước" if solver else f"Hoàn thành sau {self.steps} bước"
        last = self.index == len(self.paths) - 1
        self.popup.show("win", f"Hoàn thành màn {self.level.id}!",
                        [(f"{first}  ·  tối ưu {par}", color.white), verdict],
                        [("Chơi lại", self.restart, False),
                         ("Về màn 01" if last else "Màn tiếp  ›", lambda: self.load(self.index + 1), True)],
                        "Enter: màn tiếp   ·   R: chơi lại   ·   Esc: đóng", x=self.board_center_x)

    def _show_fall(self, turn: int, reason: str) -> None:
        if turn != self.turn:
            return
        title, why = FALL_TEXTS.get(reason, FALL_DEFAULT)
        self.popup.show("fall", title, [(why, color.white), (f"Đã đi {self.steps} bước.", THEME["muted"])],
                        [("Chọn màn", self.hud.toggle_picker, False), ("Chơi lại", self.restart, True)],
                        "Enter hoặc R: chơi lại   ·   Esc: đóng", x=self.board_center_x)

    def _update_fps(self) -> None:
        self._fps_frames += 1
        self._fps_time += time.dt
        if self._fps_time >= FPS_INTERVAL:
            self.fps.text = f"FPS {round(self._fps_frames / self._fps_time)}"
            self._fps_frames, self._fps_time = 0, 0.0

    def _unbusy(self, turn: int) -> None:
        if turn == self.turn:
            self.busy = False

    def _announce(self, events: List[dict]) -> None:
        """Đổi sự kiện của engine (docs/07 §5) thành một dòng thông báo cho người chơi."""
        parts = []
        for event in events:
            if event["type"] == "switch":
                effect = SWITCH_EFFECTS.get(event["effect"], SWITCH_EFFECTS[""])
                parts.append(f"{SWITCH_KINDS.get(event['kind'], 'Công tắc')}: {effect}")
            elif event["type"] == "split":
                parts.append("Khối tách đôi, bấm Space để đổi khối con")
            elif event["type"] == "merge":
                parts.append("Hai khối con đã ghép lại")
        if parts:
            self.show_notice("  ·  ".join(parts))

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
    """Font, nền và ánh sáng theo GAME_UI_UX_SPECIFICATION.md §2 (không đổ bóng)."""
    use_fonts()
    window.color = THEME["bg_bottom"]
    # Tấm nền gradient gắn vào camera, đặt thật xa nên luôn nằm sau bàn chơi
    Entity(parent=camera, model=Mesh(vertices=[(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)],
                                     triangles=[(0, 1, 2), (0, 2, 3)],
                                     colors=[THEME["bg_bottom"], THEME["bg_bottom"], THEME["bg_top"], THEME["bg_top"]]),
           shader=unlit_shader, z=900, scale=(3000, 800))
    sun = DirectionalLight(shadows=False, color=color.hsv(40, 0.03, 0.62))   # #fdfbf7 hạ sáng để sàn không bị cháy
    sun.look_at(Vec3(1, -2, 1))
    AmbientLight(color=color.hex("#3d444d"))


def run(level_id: str = "01") -> int:
    paths = sorted(LEVELS_DIR.glob("*.json"))
    if not paths:
        print(f"Không có màn nào trong {LEVELS_DIR}", file=sys.stderr)
        return 1
    ids = [p.stem for p in paths]
    start = ids.index(level_id) if level_id in ids else 0

    # Khử răng cưa 4× cho cạnh ô và khối; phải đặt trước khi mở cửa sổ
    loadPrcFileData("", "framebuffer-multisample 1\nmultisamples 4")
    app = Ursina(title="Bloxorz Solver", development_mode=False)
    app.render.setAntialias(AntialiasAttrib.MMultisample)
    setup_scene()
    Game(paths, start)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1] if len(sys.argv) > 1 else "01"))
