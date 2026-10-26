"""Kiểm thử A* và heuristic trên Bloxorz (V16, V17). Thử trên mê cung ở tests/test_solvers.py."""
import math
import unittest
from pathlib import Path

from bloxorz.level import LevelError, load_level
from bloxorz.problem import Problem
from bloxorz.state import Orient, split_state
from solvers import ALGORITHMS
from solvers.base import NO_SOLUTION, SOLVED
from solvers.heuristics import make_heuristic, pattern_distances
from tests.helpers import make_level
from tools.check_heuristics import consistency_violations

ORIGINAL = Path(__file__).resolve().parents[1] / "levels" / "original"

# Bẫy ở docs/01 NV8 bước 3: khối đứng ở (5, 0), công tắc tách ở (5, 3), hai ô đáp (1, 10) và (1, 12),
# đích (1, 13). Lời giải thật 4 bước (R, R, R1 rồi tự ghép, R); Manhattan thuần cho ⌈17/2⌉ = 9.
TRAP = make_level(
    ["..............",
     "..........###G",
     "..............",
     "..............",
     "..............",
     "S##@.........."],
    switches=[{"at": [5, 3], "targets": [[1, 10], [1, 12]]}],
)
# Khối không bao giờ tới được đích: hai vùng sàn tách rời
ISLANDS = make_level(["S##..##G"])


def solve(key, level):
    solver = ALGORITHMS[key]()
    problem = Problem(level)
    solver.prepare(problem)
    return problem, solver.search(problem)


class SplitShortcutTests(unittest.TestCase):
    def test_trap_is_solved_optimally_by_both(self):
        for key in ("astar", "astar_m"):
            with self.subTest(key):
                _, result = solve(key, TRAP)
                self.assertEqual(result.status, SOLVED)
                self.assertEqual(len(result.path), 4)

    def test_heuristics_do_not_overestimate_the_trap(self):
        problem = Problem(TRAP)
        start = problem.initial_state()
        self.assertEqual(make_heuristic(problem, "pattern")(start), 2)
        self.assertLessEqual(make_heuristic(problem, "manhattan")(start), 4)

    def test_switch_is_no_farther_than_its_landing_cells(self):
        dist = pattern_distances(Problem(TRAP))
        self.assertEqual(dist[(1, 12)], 1)
        self.assertEqual(dist[(5, 3)], min(dist[(1, 10)], dist[(1, 12)]))

    def test_split_state_has_finite_heuristic(self):
        problem = Problem(TRAP)
        state = split_state((1, 10), (1, 12), frozenset())
        self.assertIs(state.orient, Orient.SPLIT)
        for kind in ("pattern", "manhattan"):
            with self.subTest(kind):
                self.assertEqual(make_heuristic(problem, kind)(state), 1)


class DeadEndTests(unittest.TestCase):
    def test_pattern_prunes_unreachable_start(self):
        _, result = solve("astar", ISLANDS)
        self.assertEqual(result.status, NO_SOLUTION)
        self.assertEqual(result.expanded, 0)

    def test_manhattan_still_finds_no_solution(self):
        _, result = solve("astar_m", ISLANDS)
        self.assertEqual(result.status, NO_SOLUTION)
        self.assertGreater(result.expanded, 0)

    def test_unreachable_cell_is_infinite(self):
        self.assertEqual(make_heuristic(Problem(ISLANDS), "pattern")(Problem(ISLANDS).initial_state()), math.inf)


class OriginalLevelTests(unittest.TestCase):
    """Một phần 33 màn gốc, cho nhanh. Đủ 33 màn: python tools/check_heuristics.py"""

    LEVELS = ("01", "02", "03", "04", "05", "08", "09", "13", "16")

    def load(self, name):
        try:
            return load_level(ORIGINAL / f"{name}.json", name)
        except (OSError, LevelError) as exc:
            self.skipTest(f"không nạp được màn {name}: {exc}")

    def test_both_heuristics_match_par(self):
        for name in self.LEVELS:
            level = self.load(name)
            for key in ("astar", "astar_m"):
                with self.subTest(level=name, solver=key):
                    problem, result = solve(key, level)
                    self.assertEqual(result.status, SOLVED)
                    self.assertEqual(len(result.path), level.par)

    def test_no_consistency_violation(self):
        for name in self.LEVELS:
            with self.subTest(level=name):
                problem = Problem(self.load(name))
                heuristics = {kind: make_heuristic(problem, kind) for kind in ("pattern", "manhattan")}
                self.assertEqual(consistency_violations(problem, heuristics)["violations"],
                                 {"pattern": 0, "manhattan": 0})


if __name__ == "__main__":
    unittest.main()
