"""Hàm chi phí không đồng nhất cho bài toán Bloxorz (TV3, docs/01 NV7).

Mô hình chi phí dựa trên công nâng trọng tâm khi lật khối và rủi ro bề mặt:
1. Chi phí cơ sở: 1.0 cho mỗi lần di chuyển (bảo đảm c >= 1.0 để heuristic của A* luôn admissible).
2. Công nâng trọng tâm khi lật khối (khối hộp chữ nhật 1x1x2, khối lượng W = 1):
   - Đứng -> Nằm (STANDING -> HORIZONTAL/VERTICAL):
     Trọng tâm từ độ cao 1.0 nâng lên đỉnh sqrt(5)/2 ~= 1.118 rồi hạ xuống 0.5.
     Delta h = sqrt(5)/2 - 1.0 ~= 0.118 -> Chi phí: 1 + 0.12 = 1.12.
   - Nằm -> Đứng (HORIZONTAL/VERTICAL -> STANDING):
     Trọng tâm từ độ cao 0.5 nâng lên đỉnh sqrt(5)/2 ~= 1.118.
     Delta h = sqrt(5)/2 - 0.5 ~= 0.618 -> Chi phí: 1 + 0.62 = 1.62.
     (Đây là hành động tốn sức nhất; UCS sẽ tránh dựng khối đứng nếu có thể lăn ngang).
   - Nằm -> Nằm (HORIZONTAL <-> VERTICAL hoặc lăn quanh trục dài):
     Trọng tâm từ độ cao 0.5 nâng lên đỉnh sqrt(2)/2 ~= 0.707.
     Delta h = sqrt(2)/2 - 0.5 ~= 0.207 -> Chi phí: 1 + 0.21 = 1.21.
   - Khối con 1x1x1 khi đã tách (SPLIT, khối lượng W = 0.5):
     Delta h = sqrt(2)/2 - 0.5 ~= 0.207. Công nâng = 0.5 * 0.207 ~= 0.104 -> Chi phí: 1 + 0.10 = 1.10.
3. Phụ phí rủi ro bề mặt:
   - Nếu ô tiếp theo là ô dễ vỡ (FRAGILE - cam): phụ phí +0.50 (sàn mỏng, rung lắc, rủi ro cao).
"""
from __future__ import annotations

from typing import Optional

from .level import FRAGILE, Level
from .state import Action, Orient, State

COST_BASE = 1.0
COST_STAND_TO_LIE = 1.12
COST_LIE_TO_STAND = 1.62
COST_LIE_TO_LIE = 1.21
COST_SPLIT_CUBE = 1.10
COST_FRAGILE_RISK = 0.50

# Bảng tra nhanh công nâng trọng tâm theo chuyển đổi tư thế
ENERGY_COSTS = {
    (Orient.STANDING, Orient.HORIZONTAL): COST_STAND_TO_LIE,
    (Orient.STANDING, Orient.VERTICAL): COST_STAND_TO_LIE,
    # Khối tách khi ĐỨNG lên công tắc tách, tức là bước lăn nằm -> đứng rồi mới dịch chuyển: tính như nằm -> đứng.
    # Trước đây hai cặp này không có trong bảng nên rơi về COST_BASE = 1.0, rẻ hơn mọi bước khác.
    (Orient.HORIZONTAL, Orient.SPLIT): COST_LIE_TO_STAND,
    (Orient.VERTICAL, Orient.SPLIT): COST_LIE_TO_STAND,
    (Orient.STANDING, Orient.SPLIT): COST_STAND_TO_LIE,
    (Orient.HORIZONTAL, Orient.STANDING): COST_LIE_TO_STAND,
    (Orient.VERTICAL, Orient.STANDING): COST_LIE_TO_STAND,
    (Orient.HORIZONTAL, Orient.HORIZONTAL): COST_LIE_TO_LIE,
    (Orient.VERTICAL, Orient.VERTICAL): COST_LIE_TO_LIE,
    (Orient.HORIZONTAL, Orient.VERTICAL): COST_LIE_TO_LIE,
    (Orient.VERTICAL, Orient.HORIZONTAL): COST_LIE_TO_LIE,
    (Orient.SPLIT, Orient.SPLIT): COST_SPLIT_CUBE,
    (Orient.SPLIT, Orient.HORIZONTAL): COST_SPLIT_CUBE,
    (Orient.SPLIT, Orient.VERTICAL): COST_SPLIT_CUBE,
}


def compute_step_cost(
    state: State,
    action: Action,
    next_state: Optional[State] = None,
    level: Optional[Level] = None,
) -> float:
    """Tính chi phí của một bước di chuyển.

    Mọi bước hợp lệ luôn có chi phí >= 1.0.
    """
    if next_state is None:
        return COST_BASE

    cost = ENERGY_COSTS.get((state.orient, next_state.orient), COST_BASE)

    # Phụ phí rủi ro: đi lên ô dễ vỡ (FRAGILE)
    if level is not None:
        for cell in next_state.cells():
            if level.tile(cell) == FRAGILE:
                cost += COST_FRAGILE_RISK
                break

    return round(cost, 2)
