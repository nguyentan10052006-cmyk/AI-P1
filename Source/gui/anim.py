"""Tiện ích hoạt ảnh dùng chung cho gui/ (chỉ vẽ, docs/07 §5).

`Entity.animate(..., delay=...)` của Ursina 7 hẹn giờ bằng invoke() nhưng không ghi lần hẹn vào đâu, nên
không dừng được: đổi màn hay chơi lại trong lúc còn hoạt ảnh hẹn giờ thì lần hẹn vẫn chạy trên entity đã bị
`destroy()`, Panda3D báo lỗi `!is_empty()` và cửa sổ dừng.

Lần hẹn ở đây được giữ trong danh sách riêng `_later` của entity (không phải `entity.animations`):
- stop_animations() dừng cả hoạt ảnh đang chạy lẫn lần hẹn;
- `destroy()` của Ursina gọi `finish()` cho mọi mục trong `entity.animations` trong lúc lặp danh sách đó;
  nếu lần hẹn nằm trong đó, nó sẽ khởi động một hoạt ảnh mới, xóa hoạt ảnh cũ khỏi danh sách đang lặp,
  và hoạt ảnh mới bị bỏ sót, tiếp tục chạy trên node đã xóa. Vì vậy không đặt lần hẹn vào `animations`;
- tới giờ mà entity đã bị hủy (node rỗng, `destroy()` gọi removeNode()) thì lần hẹn không làm gì.
"""
from __future__ import annotations

from typing import Any, Callable, List

from ursina import Entity, Sequence, curve, invoke


def _later(entity: Entity) -> List[Sequence]:
    pending = getattr(entity, "_later", None)
    if pending is None:
        pending = []
        entity._later = pending
    return pending


def stop_animations(entity: Entity) -> None:
    """Dừng mọi hoạt ảnh của entity, kể cả các lần hẹn của animate_later()."""
    for animation in entity.animations:
        animation.kill()
    entity.animations.clear()
    pending = _later(entity)
    for sequence in pending:
        sequence.kill()
    pending.clear()


def call_later(entity: Entity, func: Callable[[], Any], delay: float) -> None:
    """Gọi func sau delay giây nếu khi đó entity chưa bị hủy; stop_animations(entity) hủy lần hẹn."""
    def run() -> None:
        if not entity.is_empty():
            func()

    _later(entity).append(invoke(run, delay=delay))


def animate_later(entity: Entity, name: str, value: Any, duration: float, delay: float = 0.0,
                  curve_fn: Callable[[float], float] = curve.in_out_sine) -> None:
    """Như entity.animate(name, value, duration, delay=delay, curve=curve_fn), nhưng dừng được và an toàn khi
    entity bị hủy trước lúc tới giờ."""
    if delay <= 0:
        entity.animate(name, value, duration=duration, curve=curve_fn)
        return
    call_later(entity, lambda: entity.animate(name, value, duration=duration, curve=curve_fn), delay)
