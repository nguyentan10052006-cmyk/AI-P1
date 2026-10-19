"""Các hàm API thuần (không phụ thuộc HTTP). Mỗi hàm trả về (mã HTTP, dữ liệu JSON)."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple

from bloxorz.level import Level
from bloxorz.problem import Problem
from bloxorz.rules import FELL, step
from bloxorz.serialize import (
    action_from_dict,
    action_to_dict,
    level_to_dict,
    state_from_dict,
    state_to_dict,
)
from bloxorz.state import Action
from solvers import ALGORITHMS
from solvers.base import NO_SOLUTION
from solvers.runner import SolveJob, run_solver

Response = Tuple[int, Dict[str, Any]]

# Ký hiệu của các ô đặc biệt, để thẻ chọn màn hiện biểu tượng tương ứng
FEATURE_CHARS = set("FBbox@")


class BadRequest(Exception):
    """Yêu cầu từ GUI sai (thiếu trường, màn không tồn tại...)."""


def list_levels(levels: Mapping[str, Level]) -> Response:
    ordered = sorted(levels.values(), key=lambda lv: (lv.chapter, lv.order, lv.id))
    return 200, {
        "levels": [
            {
                "id": lv.id,
                "name": lv.name,
                "group": lv.group,
                "kind": lv.kind,
                "chapter": lv.chapter,
                "order": lv.order,
                "par": lv.par,
                "unlock_stars": lv.unlock_stars,
                "features": sorted({ch for row in lv.grid for ch in row if ch in FEATURE_CHARS}),
            }
            for lv in ordered
        ],
    }


def get_level(levels: Mapping[str, Level], level_id: str) -> Response:
    level = levels.get(level_id)
    if level is None:
        return 404, {"error": f"Không có màn {level_id}"}
    data = level_to_dict(level)
    data["start"] = state_to_dict(level.initial_state())
    return 200, data


def step_level(levels: Mapping[str, Level], body: Any) -> Response:
    try:
        level = _level_from(levels, body)
        state = state_from_dict(body["state"])
        action = action_from_dict(body["action"])
        outcome = step(level, state, action)
    except (BadRequest, KeyError, ValueError, TypeError) as exc:
        return 400, {"error": f"Yêu cầu không hợp lệ: {exc}"}
    return 200, {
        "state": state_to_dict(outcome.state),
        "moved": state_to_dict(outcome.moved),
        "status": outcome.status,
        "events": outcome.events,
    }


def solve_level(
    levels: Mapping[str, Level],
    body: Any,
    algorithms: Mapping[str, Any] = ALGORITHMS,
    timeout_s: float = 60.0,
    job: Optional[SolveJob] = None,
) -> Response:
    try:
        level = _level_from(levels, body)
        start = state_from_dict(body["state"])
        name = body["algorithm"]
    except (BadRequest, KeyError, ValueError, TypeError) as exc:
        return 400, {"error": f"Yêu cầu không hợp lệ: {exc}"}

    solver_cls = algorithms.get(name)
    if solver_cls is None:
        return 400, {"error": f"Thuật toán không hợp lệ: {name!r}"}

    problem = Problem(level, start)
    outcome = run_solver(solver_cls, problem, timeout_s, job=job)
    if not outcome["ok"]:
        return 200, {"algorithm": name, "error": outcome["error"],
                     "cancelled": bool(outcome.get("cancelled")), "timeout": bool(outcome.get("timeout"))}

    stats: Dict[str, Any] = {
        "time_ms": round(outcome["time_ms"], 3),
        "prepare_ms": round(outcome["prepare_ms"], 3),
        "peak_kb": round(outcome["peak_kb"], 1),
        "expanded": outcome["expanded"],
        "generated": outcome["generated"],
        "max_frontier": outcome["max_frontier"],
        "visited": outcome["visited"],
    }
    if outcome["status"] == NO_SOLUTION:
        stats.update(length=0, cost=0)
        return 200, {"algorithm": name, "found": False, "stats": stats}
    actions: List[Action] = outcome["path"]

    try:
        steps, cost, error = _replay(problem, start, actions)
    except (TypeError, ValueError, AttributeError) as exc:
        return 200, {"algorithm": name, "error": f"Lời giải không hợp lệ: {exc}"}
    if error is not None:
        return 200, {"algorithm": name, "error": error}

    stats.update(length=len(actions), cost=cost)
    return 200, {"algorithm": name, "found": True, "stats": stats, "steps": steps}


def _replay(problem: Problem, start, actions) -> Tuple[List[dict], float, Optional[str]]:
    """Chạy lại lời giải bằng luật chơi để lấy trạng thái, sự kiện từng bước và kiểm tra tính đúng."""
    steps: List[dict] = []
    cost = 0.0
    current = start
    for index, action in enumerate(actions, start=1):
        outcome = step(problem.level, current, action)
        if outcome.status == FELL:
            return [], 0.0, f"Lời giải không hợp lệ: bước {index} làm khối rơi"
        cost += problem.step_cost(current, action, outcome.state)
        steps.append({
            "action": action_to_dict(action),
            "state": state_to_dict(outcome.state),
            "moved": state_to_dict(outcome.moved),
            "status": outcome.status,
            "events": outcome.events,
        })
        current = outcome.state
    if not problem.is_goal(current):
        return [], 0.0, "Lời giải không dẫn tới đích"
    return steps, cost, None


def _level_from(levels: Mapping[str, Level], body: Any) -> Level:
    if not isinstance(body, dict):
        raise BadRequest("nội dung phải là object JSON")
    level_id = body["level"]
    level = levels.get(level_id)
    if level is None:
        raise BadRequest(f"không có màn {level_id!r}")
    return level
