"""Chi phí của bước làm khối tách đôi (V13, bloxorz/costs.py).

Khối chỉ tách khi ĐỨNG lên công tắc tách (rules._activate), và theo bảng chuyển BLOCK_MOVES chỉ khối nằm mới
lăn thành đứng. Vì vậy bước tách luôn là nằm -> (đứng lên công tắc) -> hai khối con, tức cặp tư thế
(HORIZONTAL | VERTICAL, SPLIT), và chi phí vật lý là nằm -> đứng (1.62). Trước khi sửa, hai cặp này không có
trong ENERGY_COSTS nên rơi về COST_BASE = 1.0.
"""
import math
import unittest
from collections import deque
from pathlib import Path

from bloxorz.costs import (COST_BASE, COST_FRAGILE_RISK, COST_LIE_TO_LIE, COST_LIE_TO_STAND, COST_SPLIT_CUBE,
                           COST_STAND_TO_LIE, ENERGY_COSTS, compute_step_cost)
from bloxorz.level import FRAGILE, load_level
from bloxorz.problem import Problem
from bloxorz.state import Orient
from solvers import ALGORITHMS

ORIGINAL = Path(__file__).resolve().parents[1] / "levels" / "original"
LYING = (Orient.HORIZONTAL, Orient.VERTICAL)


def reachable_edges(problem):
    """Mọi cạnh (s, a, s') tới được từ trạng thái đầu."""
    seen = {problem.initial_state()}
    queue = deque(seen)
    while queue:
        state = queue.popleft()
        for action in problem.actions(state):
            child = problem.result(state, action)
            if child is None:
                continue
            yield state, action, child
            if child not in seen:
                seen.add(child)
                queue.append(child)


def replay_cost(problem, path):
    state, total = problem.initial_state(), 0.0
    for action in path:
        child = problem.result(state, action)
        total += problem.step_cost(state, action, child)
        state = child
    return state, total


class SplitCostTests(unittest.TestCase):
    def test_lying_to_split_costs_like_lying_to_standing(self):
        for lying in LYING:
            self.assertEqual(ENERGY_COSTS[(lying, Orient.SPLIT)], COST_LIE_TO_STAND)
            self.assertEqual(COST_LIE_TO_STAND, 1.62)

    def test_other_costs_unchanged(self):
        """Chỉ thêm hai cặp nằm -> tách; mọi cặp có từ trước giữ nguyên giá trị."""
        before = {
            (Orient.STANDING, Orient.HORIZONTAL): COST_STAND_TO_LIE, (Orient.STANDING, Orient.VERTICAL): COST_STAND_TO_LIE,
            (Orient.STANDING, Orient.SPLIT): COST_STAND_TO_LIE,
            (Orient.HORIZONTAL, Orient.STANDING): COST_LIE_TO_STAND, (Orient.VERTICAL, Orient.STANDING): COST_LIE_TO_STAND,
            (Orient.HORIZONTAL, Orient.HORIZONTAL): COST_LIE_TO_LIE, (Orient.VERTICAL, Orient.VERTICAL): COST_LIE_TO_LIE,
            (Orient.HORIZONTAL, Orient.VERTICAL): COST_LIE_TO_LIE, (Orient.VERTICAL, Orient.HORIZONTAL): COST_LIE_TO_LIE,
            (Orient.SPLIT, Orient.SPLIT): COST_SPLIT_CUBE, (Orient.SPLIT, Orient.HORIZONTAL): COST_SPLIT_CUBE,
            (Orient.SPLIT, Orient.VERTICAL): COST_SPLIT_CUBE,
        }
        self.assertEqual({k: v for k, v in ENERGY_COSTS.items() if k not in {(o, Orient.SPLIT) for o in LYING}}, before)
        self.assertEqual((COST_STAND_TO_LIE, COST_LIE_TO_STAND, COST_LIE_TO_LIE, COST_SPLIT_CUBE, COST_FRAGILE_RISK,
                          COST_BASE), (1.12, 1.62, 1.21, 1.10, 0.50, 1.0))

    def test_every_reachable_edge_uses_energy_table(self):
        """Duyệt mọi cạnh tới được của 33 màn: không cặp tư thế nào rơi về COST_BASE; chi phí = bảng (+0.5 nếu
        khối hoặc khối con nằm trên ô dễ vỡ), kể cả bước tách đáp lên ô dễ vỡ; không có cạnh đứng -> tách."""
        missing, wrong, split_edges, standing_split = set(), [], 0, 0
        for path in sorted(ORIGINAL.glob("*.json")):
            problem = Problem(load_level(path, path.stem), cost_fn=compute_step_cost)
            for state, action, child in reachable_edges(problem):
                pair = (state.orient, child.orient)
                if pair not in ENERGY_COSTS:
                    missing.add((path.stem, state.orient.name, child.orient.name))
                    continue
                if child.orient is Orient.SPLIT and state.orient is not Orient.SPLIT:
                    split_edges += 1
                    standing_split += state.orient is Orient.STANDING
                fragile = any(problem.level.tile(cell) == FRAGILE for cell in child.cells())
                want = round(ENERGY_COSTS[pair] + (COST_FRAGILE_RISK if fragile else 0.0), 2)
                if problem.step_cost(state, action, child) != want:
                    wrong.append((path.stem, pair))
        self.assertEqual(missing, set())
        self.assertEqual(wrong, [])
        self.assertGreater(split_edges, 0)
        self.assertEqual(standing_split, 0)

    def test_split_step_and_path_total_on_level_08(self):
        """Màn 08: lời giải UCS có đúng một bước tách giá 1.62; tổng chi phí = tổng từng bước = 12.60."""
        problem = Problem(load_level(ORIGINAL / "08.json", "08"), cost_fn=compute_step_cost)
        result = ALGORITHMS["ucs"]().search(problem)
        state, split_costs = problem.initial_state(), []
        for action in result.path:
            child = problem.result(state, action)
            if child.orient is Orient.SPLIT and state.orient is not Orient.SPLIT:
                split_costs.append(problem.step_cost(state, action, child))
            state = child
        self.assertEqual(split_costs, [COST_LIE_TO_STAND])
        final, total = replay_cost(problem, result.path)
        self.assertTrue(problem.is_goal(final))
        self.assertAlmostEqual(total, result.path_cost, places=9)
        self.assertAlmostEqual(result.path_cost, 12.60, places=9)

    def test_all_algorithms_report_path_cost_with_same_cost_function(self):
        """Ở mọi màn G5 (có công tắc tách), path_cost của cả 5 cấu hình bằng chi phí phát lại theo V13."""
        for stem in ("08", "09", "10", "15", "16", "20", "23", "24", "26", "28"):
            level = load_level(ORIGINAL / f"{stem}.json", stem)
            for name, solver_cls in ALGORITHMS.items():
                with self.subTest(level=stem, algorithm=name):
                    problem = Problem(level, cost_fn=compute_step_cost)
                    solver = solver_cls()
                    solver.prepare(problem)
                    result = solver.search(problem)
                    _, total = replay_cost(problem, result.path)
                    self.assertTrue(math.isclose(total, result.path_cost, rel_tol=1e-9, abs_tol=1e-9))


if __name__ == "__main__":
    unittest.main()
