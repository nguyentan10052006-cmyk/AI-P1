"""Camera 3D cho Bloxorz Ursina GUI: luôn nhìn từ trên xuống, từ phía người chơi.

Camera chỉ được nghiêng trong vùng giới hạn để người chơi không lẫn hướng:
- Góc ngang (yaw) chỉ lệch tối đa ±MAX_YAW (40°, dưới 45°) so với chính diện, nên phím ↑ luôn đẩy khối
  ra xa màn hình và ← → luôn là trái phải trên màn hình, không cần ánh xạ lại phím.
- Góc cao (pitch, góc giữa mặt bàn và hướng nhìn) nằm trong [MIN_PITCH, MAX_PITCH]: lúc nào cũng nhìn
  từ trên xuống; người chơi hạ thấp dần để thấy rõ khối đứng và cầu, hoặc bấm T để nhìn thẳng từ đỉnh.

Điều khiển:
- Q / E (hoặc nút HUD): nghiêng sang trái / phải một nấc trong YAW_PRESETS.
- Z / X (hoặc nút HUD): hạ thấp / nâng cao góc nhìn một nấc trong PITCH_PRESETS.
- T: bật/tắt góc nhìn đỉnh (top-down, luôn thẳng hướng bàn).
- Giữ chuột phải và kéo: chỉnh góc tự do trong vùng giới hạn trên.
- Con lăn chuột: thu phóng.
- F: đặt lại góc mặc định.
Góc đã chọn được giữ khi đổi màn; chỉ F mới đặt lại.
"""
from __future__ import annotations

import math
from typing import Callable, Iterable, List, Optional, Sequence

from panda3d.core import Point2, Point3
from ursina import Vec3, application, camera, mouse, scene, time, window

MAX_YAW = 40.0
YAW_PRESETS = (-MAX_YAW, -20.0, 0.0, 20.0, MAX_YAW)
MAX_PITCH = 52.0
MIN_PITCH = 30.0
PITCH_PRESETS = (MAX_PITCH, 45.0, 38.0, MIN_PITCH)   # từ cao xuống thấp
DEFAULT_YAW, DEFAULT_PITCH = 0.0, MAX_PITCH
TOP_PITCH = 88.5        # không dùng đúng 90° để look_at không bị gimbal lock khi nhìn thẳng trục Y


def _step_preset(presets: Sequence[float], value: float, step: int) -> float:
    """Nấc kế bên của value trong presets (theo thứ tự của presets), dừng ở hai đầu."""
    nearest = min(range(len(presets)), key=lambda i: abs(presets[i] - value))
    return presets[max(0, min(len(presets) - 1, nearest + step))]


class CameraController:
    """Máy quay xoay quanh tâm bàn, chuyển góc mượt bằng nội suy."""

    def __init__(self) -> None:
        self.target = Vec3(0, 0, 0)   # tâm bàn, camera xoay quanh điểm này
        self.screen_shift = 0.0        # dời điểm nhìn sang phải màn hình bấy nhiêu đơn vị (chừa cột nút HUD)
        self.size = 15.0
        self.base_distance = 20.0
        self.distance = self.target_distance = 20.0
        self.yaw = self.target_yaw = DEFAULT_YAW
        self.pitch = self.target_pitch = DEFAULT_PITCH
        self.is_top_down = False
        # Khung khi bảng kết quả chiếm một phần màn hình (set_frame): lùi xa và dịch hình sang vùng trống
        self.frame_scale = self.target_frame_scale = 1.0
        self.film_shift = self.target_film_shift = 0.0
        self.saved_view = (DEFAULT_YAW, DEFAULT_PITCH)   # góc trước khi bật top-down, để T lần nữa quay về
        self.on_view_change: Optional[Callable[[str], None]] = None

    def setup(self, target: Vec3, size: float, screen_shift: float = 0.0) -> None:
        """Căn máy quay theo kích thước bàn chơi (gọi khi nạp màn); giữ góc người chơi đã chọn."""
        self.target = target
        self.screen_shift = screen_shift
        self.size = size
        self.base_distance = max(12.0, size * 1.42)   # bao quát cả bàn, chừa lề cho HUD
        self.distance = self.target_distance = self.base_distance
        self.yaw, self.pitch = self.target_yaw, self.target_pitch
        self._apply_position()
        self._notify_change()

    def reset_view(self) -> None:
        """Về góc mặc định: chính diện, góc cao MAX_PITCH."""
        self.target_yaw = DEFAULT_YAW
        self.target_pitch = DEFAULT_PITCH
        self.target_distance = self.base_distance
        self.is_top_down = False
        self._notify_change()

    def rotate_preset(self, step: float) -> None:
        """Q (step < 0) / E (step > 0): nghiêng sang nấc kế bên trong YAW_PRESETS."""
        if self.is_top_down:
            self.toggle_top_down()
        self.target_yaw = _step_preset(YAW_PRESETS, self.target_yaw, 1 if step > 0 else -1)
        self._notify_change()

    def tilt_preset(self, step: float) -> None:
        """Z (step < 0: hạ thấp) / X (step > 0: nâng cao): sang nấc kế bên trong PITCH_PRESETS."""
        if self.is_top_down:
            self.toggle_top_down()
        self.target_pitch = _step_preset(PITCH_PRESETS, self.target_pitch, -1 if step > 0 else 1)
        self._notify_change()

    def toggle_top_down(self) -> None:
        """Bật/tắt góc nhìn đỉnh; top-down luôn để yaw = 0 cho bàn thẳng hàng với màn hình."""
        self.is_top_down = not self.is_top_down
        if self.is_top_down:
            self.saved_view = (self.target_yaw, self.target_pitch)
            self.target_yaw, self.target_pitch = 0.0, TOP_PITCH
        else:
            self.target_yaw, self.target_pitch = self.saved_view
        self._notify_change()

    def set_frame(self, scale: float, film_shift: float) -> None:
        """Thu bàn vào một phần màn hình: khoảng cách nhân scale, hình dịch film_shift (tỉ lệ bề rộng màn hình,
        dương là sang phải). Dịch bằng film offset của lens nên góc nhìn không đổi, chỉ hình trượt ngang."""
        self.target_frame_scale = scale
        self.target_film_shift = film_shift

    def project_unframed(self, points: Iterable[Vec3]) -> List[float]:
        """Hoành độ trên màn hình (đơn vị camera.ui) của các điểm, khi camera ở góc đích và chưa căn theo khung
        kết quả (set_frame(1, 0)). Dùng để biết bàn có bị khung che không và cần dịch, thu bao nhiêu.
        Điểm nằm sau camera thì bỏ qua."""
        saved = (self.yaw, self.pitch, self.distance, self.frame_scale, self.film_shift)
        self.yaw, self.pitch, self.distance = self.target_yaw, self.target_pitch, self.target_distance
        self.frame_scale, self.film_shift = 1.0, 0.0
        self._apply_position()
        xs: List[float] = []
        for point in points:
            local = application.base.cam.getRelativePoint(scene, Point3(point.x, point.y, point.z))
            screen = Point2()
            if camera.lens.project(local, screen):
                xs.append(screen.x * window.aspect_ratio / 2)
        self.yaw, self.pitch, self.distance, self.frame_scale, self.film_shift = saved
        self._apply_position()
        return xs

    def zoom(self, delta: float) -> None:
        """Thu phóng (delta > 0: lại gần, delta < 0: ra xa)."""
        min_dist = max(5.0, self.base_distance * 0.45)
        max_dist = self.base_distance * 2.3
        self.target_distance = max(min_dist, min(max_dist, self.target_distance - delta * (self.size * 0.12)))

    def update(self) -> None:
        """Gọi mỗi frame: nhận kéo chuột phải (trừ khi đang nhìn từ đỉnh) rồi nội suy về góc đích."""
        if mouse.right and not self.is_top_down:
            vx, vy = mouse.velocity[0], mouse.velocity[1]
            if abs(vx) > 0.0001 or abs(vy) > 0.0001:
                self.target_yaw = max(-MAX_YAW, min(MAX_YAW, self.target_yaw + vx * 120.0))
                self.target_pitch = max(MIN_PITCH, min(MAX_PITCH, self.target_pitch - vy * 120.0))
                self._notify_change()

        lerp_factor = min(1.0, time.dt * 14.0)
        self.yaw += (self.target_yaw - self.yaw) * lerp_factor
        self.pitch += (self.target_pitch - self.pitch) * lerp_factor
        self.distance += (self.target_distance - self.distance) * lerp_factor
        self.frame_scale += (self.target_frame_scale - self.frame_scale) * lerp_factor
        self.film_shift += (self.target_film_shift - self.film_shift) * lerp_factor
        self._apply_position()

    def _apply_position(self) -> None:
        """Đổi tọa độ cầu (yaw, pitch, distance) sang vị trí camera; camera ở phía z âm, nhìn vào tâm bàn.

        Điểm nhìn dời theo trục ngang của màn hình (vuông góc hướng nhìn) nên khi nghiêng trái phải
        bàn vẫn nằm giữa vùng trống bên trái cột nút, không trôi ra mép.
        """
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        look = self.target + Vec3(math.cos(rad_yaw), 0, math.sin(rad_yaw)) * self.screen_shift
        # nghiêng ngang thì bàn chiếm chỗ theo đường chéo, lùi xa thêm để bàn không tràn ra mép
        distance = self.distance * self.frame_scale * (1 + 0.35 * abs(math.sin(rad_yaw)))
        dist_xz = distance * math.cos(rad_pitch)
        camera.position = Vec3(look.x + dist_xz * math.sin(rad_yaw),
                               look.y + distance * math.sin(rad_pitch),
                               look.z - dist_xz * math.cos(rad_yaw))
        # up mặc định của Ursina là trục "lên" hiện tại của camera, roll sẽ dồn dần qua mỗi frame; ghim theo trục Y
        camera.look_at(look, up=Vec3(0, 1, 0))
        # film offset dương dời khung nhìn sang phải, tức hình trượt sang trái; đổi dấu để dương là hình sang phải
        camera.lens.setFilmOffset(-self.film_shift * camera.lens.getFilmSize()[0], 0)

    def _notify_change(self) -> None:
        if self.on_view_change is not None:
            self.on_view_change(self.view_name)

    @property
    def view_name(self) -> str:
        """Mô tả góc đích để hiện trên HUD, ví dụ "TRÁI 20° · CAO 45°"."""
        if self.is_top_down:
            return "TỪ ĐỈNH"
        yaw = round(self.target_yaw)
        side = "CHÍNH DIỆN" if yaw == 0 else f"{'TRÁI' if yaw < 0 else 'PHẢI'} {abs(yaw)}°"
        return f"{side} · CAO {round(self.target_pitch)}°"
