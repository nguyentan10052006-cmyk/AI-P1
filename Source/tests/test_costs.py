"""Kiểm thử hàm chi phí không đồng nhất (TV3, việc V13, docs/01 NV7)."""
import unittest

from bloxorz.costs import (
    COST_BASE,
    COST_FRAGILE_RISK,
    COST_LIE_TO_LIE,
    COST_LIE_TO_STAND,
    COST_SPLIT_CUBE,
    COST_STAND_TO_LIE,
    compute_step_cost,
)
from bloxorz.level import Level
from bloxorz.problem import Problem
from bloxorz.state import Action, Dir, Orient, State
from tests.helpers import make_level


class CostFunctionTests(unittest.TestCase):
    def test_all_costs_at_least_one(self):
        """Bất biến sống còn cho A* (docs/01 NV7 bước 4): mọi bước có chi phí >= 1.0."""
        s_standing = State(Orient.STANDING, (0, 0), None, frozenset())
        s_horiz = State(Orient.HORIZONTAL, (0, 0), None, frozenset())
        s_vert = State(Orient.VERTICAL, (0, 0), None, frozenset())
        s_split = State(Orient.SPLIT, (0, 0), (0, 2), frozenset())

        states = [s_standing, s_horiz, s_vert, s_split]
        for s1 in states:
            for s2 in states:
                cost = compute_step_cost(s1, Action(Dir.RIGHT), s2)
                self.assertGreaterEqual(cost, 1.0, f"Chi phí từ {s1.orient} sang {s2.orient} < 1.0")

    def test_standing_to_lying_cost(self):
        s1 = State(Orient.STANDING, (0, 0), None, frozenset())
        s2 = State(Orient.HORIZONTAL, (0, 1), None, frozenset())
        self.assertEqual(compute_step_cost(s1, Action(Dir.RIGHT), s2), COST_STAND_TO_LIE)

    def test_lying_to_standing_cost(self):
        s1 = State(Orient.HORIZONTAL, (0, 0), None, frozenset())
        s2 = State(Orient.STANDING, (0, 2), None, frozenset())
        self.assertEqual(compute_step_cost(s1, Action(Dir.RIGHT), s2), COST_LIE_TO_STAND)

    def test_lying_to_lying_cost(self):
        s1 = State(Orient.HORIZONTAL, (0, 0), None, frozenset())
        s2 = State(Orient.HORIZONTAL, (1, 0), None, frozenset())
        self.assertEqual(compute_step_cost(s1, Action(Dir.DOWN), s2), COST_LIE_TO_LIE)

    def test_split_cubes_cost(self):
        s1 = State(Orient.SPLIT, (0, 0), (0, 2), frozenset())
        s2 = State(Orient.SPLIT, (0, 1), (0, 2), frozenset())
        self.assertEqual(compute_step_cost(s1, Action(Dir.RIGHT, cube=0), s2), COST_SPLIT_CUBE)

    def test_fragile_tile_penalty(self):
        level = make_level(["S#F", "..G"])
        s1 = State(Orient.STANDING, (0, 0), None, frozenset())
        s2 = State(Orient.HORIZONTAL, (0, 1), None, frozenset())  # nằm đè lên (0,1)-(0,2), có F ở (0,2)
        cost = compute_step_cost(s1, Action(Dir.RIGHT), s2, level)
        self.assertEqual(cost, round(COST_STAND_TO_LIE + COST_FRAGILE_RISK, 2))

    def test_problem_step_cost_integration(self):
        level = make_level(["S##G"])
        problem_default = Problem(level)
        s1 = problem_default.initial_state()
        s2 = problem_default.result(s1, Action(Dir.RIGHT))

        # next_state is None -> 1
        self.assertEqual(problem_default.step_cost(s1, Action(Dir.RIGHT), None), 1)

        # Mặc định cost_fn là None -> 1
        self.assertEqual(problem_default.step_cost(s1, Action(Dir.RIGHT), s2), 1)

        # Truyền cost_fn=compute_step_cost -> non-uniform cost
        problem_energy = Problem(level, cost_fn=compute_step_cost)
        self.assertEqual(problem_energy.step_cost(s1, Action(Dir.RIGHT), s2), COST_STAND_TO_LIE)



if __name__ == "__main__":
    unittest.main()
