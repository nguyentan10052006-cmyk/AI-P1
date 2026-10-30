"""Mesh dùng chung cho bàn và khối: hộp vát cạnh, tạo một lần rồi dùng lại (chỉ vẽ, docs/07 §5).

Hộp vát cạnh gồm 6 mặt chính lùi vào một đoạn `bevel`, 12 dải vát ở các cạnh và 8 tam giác ở các góc.
Mỗi mặt có pháp tuyến riêng (shading phẳng) nên cạnh vát bắt sáng, khối trông có độ dày thay vì một
hình hộp phẳng màu. Màu đỉnh (vertex color) tô sẵn theo hướng mặt; Ursina nhân màu này với `entity.color`.
Mỗi Mesh là một node của Panda3D, chỉ gắn được vào một entity, nên chỉ cache dữ liệu đỉnh, còn Mesh tạo mới
mỗi lần gọi.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product
from typing import List, Sequence, Tuple

from ursina import Color, Mesh, Vec3

Shade = Tuple[float, float, float]   # độ sáng của mặt trên, mặt bên, mặt dưới (1 = giữ nguyên màu)
FLAT: Shade = (1.0, 1.0, 1.0)


def _brightness(normal: Vec3, shade: Shade) -> float:
    """Mặt hướng lên dùng shade[0], hướng xuống shade[2], còn lại nội suy về shade[1] theo thành phần y."""
    top, side, bottom = shade
    y = normal.y
    return side + (top - side) * y if y >= 0 else side + (side - bottom) * y


Geometry = Tuple[Tuple[Vec3, ...], Tuple[Vec3, ...], Tuple[Color, ...]]


def _box(half: Sequence[float], bevel: float, shade: Shade) -> Geometry:
    hx, hy, hz = half
    inner = (hx - bevel, hy - bevel, hz - bevel)
    vertices: List[Vec3] = []
    normals: List[Vec3] = []
    colors: List[Color] = []

    def add(points: Sequence[Vec3], normal: Vec3) -> None:
        """Thêm một đa giác lồi (3 hoặc 4 đỉnh), tự sắp chiều đỉnh để mặt hướng ra ngoài.

        Ursina dùng hệ tọa độ tay trái: mặt trước là mặt có các đỉnh theo chiều kim đồng hồ khi nhìn từ ngoài
        vào, tức tích có hướng (b - a) × (c - a) ngược chiều pháp tuyến.
        """
        normal = normal.normalized()
        for a, b, c in ((points[0], points[1], points[2]),) + (((points[0], points[2], points[3]),)
                                                                 if len(points) == 4 else ()):
            if (b - a).cross(c - a).dot(normal) > 0:
                b, c = c, b
            value = _brightness(normal, shade)
            for point in (a, b, c):
                vertices.append(point)
                normals.append(normal)
                colors.append(Color(value, value, value, 1))

    def point(axis_values: dict) -> Vec3:
        return Vec3(axis_values[0], axis_values[1], axis_values[2])

    full = (hx, hy, hz)
    for axis in range(3):                          # 6 mặt chính
        j, k = [a for a in range(3) if a != axis]
        for sign in (-1, 1):
            corners = []
            for sj, sk in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                corners.append(point({axis: sign * full[axis], j: sj * inner[j], k: sk * inner[k]}))
            normal = point({axis: sign, j: 0, k: 0})
            add(corners, normal)
    if bevel > 0:
        for i, j in ((0, 1), (0, 2), (1, 2)):      # 12 dải vát ở cạnh
            k = 3 - i - j
            for si, sj in product((-1, 1), repeat=2):
                quad = [point({i: si * full[i], j: sj * inner[j], k: -inner[k]}),
                        point({i: si * full[i], j: sj * inner[j], k: inner[k]}),
                        point({i: si * inner[i], j: sj * full[j], k: inner[k]}),
                        point({i: si * inner[i], j: sj * full[j], k: -inner[k]})]
                add(quad, point({i: si, j: sj, k: 0}))
        for sx, sy, sz in product((-1, 1), repeat=3):   # 8 góc
            signs = (sx, sy, sz)
            tri = []
            for axis in range(3):
                tri.append(point({a: signs[a] * (full[a] if a == axis else inner[a]) for a in range(3)}))
            add(tri, Vec3(sx, sy, sz))
    return tuple(vertices), tuple(normals), tuple(colors)


@lru_cache(maxsize=None)
def _cached_box(size: Tuple[float, float, float], bevel: float, shade: Shade) -> Geometry:
    return _box([s / 2 for s in size], min(bevel, *(s / 2 for s in size)), shade)


def beveled_box(size: Sequence[float], bevel: float, shade: Shade = FLAT) -> Mesh:
    """Hộp kích thước size = (x, y, z), tâm ở gốc tọa độ, vát cạnh bevel. Cùng tham số thì dùng chung dữ liệu đỉnh."""
    key = tuple(round(float(s), 4) for s in size)
    vertices, normals, colors = _cached_box(key, round(float(bevel), 4), tuple(shade))
    return Mesh(vertices=list(vertices), normals=list(normals), colors=list(colors), static=True)
