"""Hệ thống Camera 3D đa góc nhìn cho Bloxorz Ursina GUI (GAME_UI_UX_SPECIFICATION.md).

Hỗ trợ:
- Preset 4 góc 90° (Q / E hoặc nút bấm HUD).
- Góc nhìn chiến thuật từ đỉnh 90° Top-down (phím T).
- Free Orbit Camera bằng cách giữ chuột phải và kéo rê (Mouse RMB drag).
- Thu phóng Camera (Zoom In / Out) bằng con lăn chuột.
- Reset Camera về vị trí chuẩn theo kích thước bàn (phím F hoặc Space).
- Ánh xạ phím điều khiển theo hướng nhìn màn hình (Screen-Relative Input Mapping).
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from ursina import Vec3, camera, mouse, time

from bloxorz.state import Dir


class CameraController:
    """Điều khiển máy quay 3D mượt mà xoay quanh tâm bàn cờ."""

    def __init__(self) -> None:
        self.target = Vec3(0, 0, 0)
        self.size = 15.0
        self.base_distance = 20.0
        self.distance = 20.0
        self.target_distance = 20.0

        # Góc xoay theo tọa độ cầu: yaw (ngang) và pitch (dọc) tính bằng độ
        self.yaw = 0.0
        self.pitch = 48.0
        self.target_yaw = 0.0
        self.target_pitch = 48.0

        self.is_top_down = False
        self.saved_pitch = 48.0
        self.on_view_change: Optional[Callable[[str], None]] = None

    def setup(self, target: Vec3, size: float) -> None:
        """Căn chỉnh máy quay ban đầu tương thích với kích thước bàn chơi."""
        self.target = target
        self.size = size
        # Khoảng cách tối ưu bao quát bàn cờ có chừa lề HUD
        self.base_distance = max(12.0, size * 1.42)
        self.distance = self.target_distance = self.base_distance
        self.yaw = self.target_yaw = 0.0
        self.pitch = self.target_pitch = 48.0
        self.is_top_down = False
        self._apply_position()
        self._notify_change()

    def reset_view(self) -> None:
        """Khôi phục về góc nhìn mặc định (North 0°, pitch 48°)."""
        self.target_yaw = 0.0
        self.target_pitch = 48.0
        self.target_distance = self.base_distance
        self.is_top_down = False
        self._notify_change()

    def rotate_preset(self, delta_yaw: float) -> None:
        """Xoay các góc trực giao 90° (Q: -90°, E: +90°)."""
        if self.is_top_down:
            self.toggle_top_down()
        # Làm tròn về bội số của 90 độ gần nhất rồi cộng delta
        nearest_step = round(self.target_yaw / 90.0) * 90.0
        self.target_yaw = (nearest_step + delta_yaw) % 360.0
        self._notify_change()

    def set_preset_angle(self, angle: float) -> None:
        """Đặt góc nhìn trực tiếp theo độ (0, 90, 180, 270)."""
        if self.is_top_down:
            self.toggle_top_down()
        self.target_yaw = angle % 360.0
        self.target_pitch = 48.0
        self._notify_change()

    def toggle_top_down(self) -> None:
        """Chuyển đổi qua lại giữa góc phối cảnh 3D và góc nhìn đỉnh 2D (phím T)."""
        self.is_top_down = not self.is_top_down
        if self.is_top_down:
            self.saved_pitch = self.target_pitch if self.target_pitch < 80.0 else 48.0
            # 88.5° tránh hiện tượng gimbal lock của camera khi nhìn thẳng trục Y
            self.target_pitch = 88.5
        else:
            self.target_pitch = self.saved_pitch
        self._notify_change()

    def zoom(self, delta: float) -> None:
        """Thu phóng khoảng cách máy quay (con lăn chuột)."""
        min_dist = max(5.0, self.base_distance * 0.45)
        max_dist = self.base_distance * 2.3
        # delta > 0 là zoom in (lại gần), delta < 0 là zoom out (ra xa)
        self.target_distance = max(min_dist, min(max_dist, self.target_distance - delta * (self.size * 0.12)))

    def update(self) -> None:
        """Cập nhật chuyển động nội suy và nhận tương tác chuột trong game loop."""
        # Chuột phải kéo để xoay tự do (Free Orbit)
        if mouse.right:
            # mouse.velocity là độ dịch chuyển của chuột trong frame
            vx, vy = mouse.velocity[0], mouse.velocity[1]
            if abs(vx) > 0.0001 or abs(vy) > 0.0001:
                self.target_yaw = (self.target_yaw + vx * 160.0) % 360.0
                new_pitch = self.target_pitch - vy * 140.0
                self.target_pitch = max(12.0, min(88.5, new_pitch))
                if self.is_top_down and self.target_pitch < 82.0:
                    self.is_top_down = False
                self._notify_change()

        # Nội suy mượt mà (Smooth lerp)
        lerp_factor = min(1.0, time.dt * 14.0)
        # Xử lý khoảng cách góc xoay quanh 0°/360° để không bị quay vòng ngược
        diff_yaw = (self.target_yaw - self.yaw + 180.0) % 360.0 - 180.0
        self.yaw = (self.yaw + diff_yaw * lerp_factor) % 360.0

        self.pitch += (self.target_pitch - self.pitch) * lerp_factor
        self.distance += (self.target_distance - self.distance) * lerp_factor

        self._apply_position()

    def _apply_position(self) -> None:
        """Tính toán tọa độ Descartes từ tọa độ cầu và hướng camera nhìn vào tâm bàn."""
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        dist_xz = self.distance * math.cos(rad_pitch)
        x = self.target.x + dist_xz * math.sin(rad_yaw)
        y = self.target.y + self.distance * math.sin(rad_pitch)
        z = self.target.z - dist_xz * math.cos(rad_yaw)

        camera.position = Vec3(x, y, z)
        camera.look_at(self.target)

    def _notify_change(self) -> None:
        if self.on_view_change is not None:
            self.on_view_change(self.view_name)

    @property
    def view_name(self) -> str:
        """Tên ngắn của góc nhìn hiện tại để hiển thị trên HUD."""
        if self.is_top_down or self.pitch >= 82.0:
            return "TOP"
        sector = self.current_sector
        names = {0: "NORTH", 1: "EAST", 2: "SOUTH", 3: "WEST"}
        return names.get(sector, "3D")

    @property
    def current_sector(self) -> int:
        """Xác định cung phần tư hiện tại (0: North, 1: East, 2: South, 3: West)."""
        normalized_yaw = (self.yaw + 45.0) % 360.0
        return int(normalized_yaw // 90.0)

    def map_input_direction(self, raw_dir: Dir) -> Dir:
        """Ánh xạ phím bấm sang hướng lăn tương đối theo góc nhìn màn hình.

        Bấm phím 'W / Up' luôn lăn khối về phía xa màn hình, bất kể xoay camera góc nào!
        """
        sector = self.current_sector
        if sector == 0:
            # North (Góc mặc định nhìn từ z âm): giữ nguyên
            return raw_dir

        # Bảng quay vòng theo chiều kim đồng hồ khi nhìn từ mạn phải/sau/trái:
        # Sector 1 (East, nhìn từ x+): W đi về phía -x (LEFT), S về +x (RIGHT), A về -z (DOWN), D về +z (UP)
        # Sector 2 (South, nhìn từ z+): Đảo ngược hoàn toàn
        # Sector 3 (West, nhìn từ x-): W đi về phía +x (RIGHT), S về -x (LEFT), A về +z (UP), D về -z (DOWN)
        mappings = {
            1: {Dir.UP: Dir.LEFT, Dir.DOWN: Dir.RIGHT, Dir.LEFT: Dir.DOWN, Dir.RIGHT: Dir.UP},
            2: {Dir.UP: Dir.DOWN, Dir.DOWN: Dir.UP, Dir.LEFT: Dir.RIGHT, Dir.RIGHT: Dir.LEFT},
            3: {Dir.UP: Dir.RIGHT, Dir.DOWN: Dir.LEFT, Dir.LEFT: Dir.UP, Dir.RIGHT: Dir.DOWN},
        }
        return mappings.get(sector, {}).get(raw_dir, raw_dir)
