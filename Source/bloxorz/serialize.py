"""Chuyển State, Action và Level qua lại giữa Python và JSON."""
from __future__ import annotations

from typing import Any, Dict

from .level import Level
from .state import Action, Dir, Orient, State, split_state, to_cell


def state_to_dict(state: State) -> Dict[str, Any]:
    return {
        "orient": state.orient.value,
        "pos": list(state.pos),
        "pos2": list(state.pos2) if state.pos2 is not None else None,
        "open": sorted(list(cell) for cell in state.open_bridges),
    }


def state_from_dict(data: Any) -> State:
    if not isinstance(data, dict):
        raise ValueError("state phải là object JSON")
    orient = Orient(data["orient"])
    pos = to_cell(data["pos"])
    open_bridges = frozenset(to_cell(cell) for cell in data.get("open", []))
    if orient is Orient.SPLIT:
        return split_state(pos, to_cell(data["pos2"]), open_bridges)
    return State(orient, pos, None, open_bridges)


def action_to_dict(action: Action) -> Dict[str, Any]:
    return {"dir": action.dir.value, "cube": action.cube}


def action_from_dict(data: Any) -> Action:
    if not isinstance(data, dict):
        raise ValueError("action phải là object JSON")
    cube = data.get("cube")
    if cube is not None and (not isinstance(cube, int) or isinstance(cube, bool)):
        raise ValueError("cube phải là số nguyên hoặc null")
    return Action(Dir(data["dir"]), cube)


def level_to_dict(level: Level) -> Dict[str, Any]:
    return {
        "id": level.id,
        "name": level.name,
        "group": level.group,
        "source": level.source,
        "grid": list(level.grid),
        "start": list(level.start),
        "goal": list(level.goal),
        "switches": [
            {
                "at": list(sw.at),
                "kind": sw.kind,
                "effect": sw.effect,
                "bridges": [list(b) for b in sw.bridges],
                "targets": [list(t) for t in sw.targets],
            }
            for sw in level.switches.values()
        ],
    }
