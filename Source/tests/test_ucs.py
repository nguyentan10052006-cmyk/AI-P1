"""Kiểm thử UCS (docs/01 NV7, việc V12 & V14): quy ước đếm, tối ưu chi phí, 33 màn gốc, lazy deletion."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from bloxorz.costs import compute_step_cost
from bloxorz.level import parse_level
from bloxorz.maze import MAZES, GridMaze
from bloxorz.problem import Problem
from bloxorz.state import Action, Dir, Orient, State
from solvers.base import NO_SOLUTION, SOLVED
from solvers.bfs import BFS
from solvers.ucs import UCS
from tests.helpers import make_level

ORIGINAL_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
D = Action(Dir.DOWN)
L = Action(Dir.LEFT)
R = Action(Dir.RIGHT)


def replay(problem: Problem, path: list[Action]) -> State | None:
    """Phát lại path trên engine; trả về trạng thái cuối, hoặc None nếu có bước làm khối rơi."""
    state = problem.initial_state()
    for action in path:
        state = problem.result(state, action)
        if state is None:
            return None
    return state


class UCSCountingTests(unittest.TestCase):
    def test_start_is_goal_returns_empty_path(self):
        """Trạng thái đầu đã là đích: không mở rộng gì, path rỗng, cost = 0."""
        level = make_level(["S#G"])
        at_goal = State(Orient.STANDING, level.goal, None, frozenset())
        problem = Problem(level, start=at_goal)
        result = UCS().search(problem)
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [])
        self.assertEqual(result.path_cost, 0)
        self.assertEqual(result.expanded, 0)
        self.assertEqual(result.visited, 1)


    def test_counts_on_corridor_by_hand(self):
        """S.G trên GridMaze: lấy S ra (expanded 1), sinh (0,1); lấy (0,1) ra (expanded 2), đích."""
        result = UCS().search(GridMaze(["S.G"]))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [R, R])
        self.assertEqual(result.path_cost, 2)
        self.assertEqual(result.expanded, 2)
        self.assertEqual(result.visited, 3)

    def test_no_solution_when_gap_is_two_tiles(self):
        """Khe hở 2 ô không có cầu: UCS duyệt hết không gian rồi trả NO_SOLUTION."""
        level = make_level(["S..G"])
        problem = Problem(level)
        result = UCS().search(problem)
        self.assertEqual(result.status, NO_SOLUTION)
        self.assertEqual(result.path, [])
        self.assertGreater(result.expanded, 0)

    def test_all_mazes_match_expected_cost(self):
        """Kiểm tra UCS trên toàn bộ 4 mê cung mẫu trong MAZES."""
        solver = UCS()
        for name, case in MAZES.items():
            with self.subTest(maze=name):
                maze = GridMaze(case.grid)
                res = solver.search(maze)
                if case.cost is None:
                    self.assertEqual(res.status, NO_SOLUTION)
                else:
                    self.assertEqual(res.status, SOLVED)
                    self.assertEqual(res.path_cost, case.cost)


@unittest.skipUnless(ORIGINAL_DIR.is_dir(), "chưa có levels/original/ (33 màn gốc của TV2) trên nhánh này")
class UCSOnOriginalLevelsTests(unittest.TestCase):
    """V14: UCS giải 33 màn gốc, đối chiếu par khi cost=1 và kiểm tra tính tối ưu khi dùng cost V13."""

    @classmethod
    def setUpClass(cls):
        cls.data = {
            int(p.stem): json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(ORIGINAL_DIR.glob("*.json"))
        }

    def test_ucs_uniform_cost_matches_par_on_all_33_levels(self):
        """Khi cost = 1, số bước của UCS phải bằng đúng cột par (BFS) ở cả 33/33 màn (docs/01 NV7 bước 6)."""
        solver = UCS()
        for n in range(1, 34):
            with self.subTest(level=n):
                level = parse_level(self.data[n], f"{n:02d}")
                problem = Problem(level)  # default uniform cost = 1
                result = solver.search(problem)

                self.assertEqual(result.status, SOLVED)
                self.assertEqual(len(result.path), level.par, f"Màn {n}: số bước {len(result.path)} != par {level.par}")
                final = replay(problem, result.path)
                self.assertIsNotNone(final, f"Màn {n}: lời giải làm khối rơi")
                self.assertTrue(problem.is_goal(final), f"Màn {n}: lời giải không tới đích")

    def test_ucs_energy_cost_optimality_on_all_33_levels(self):
        """Với hàm chi phí năng lượng V13, tổng chi phí của UCS không được lớn hơn chi phí của BFS (docs/04 §6)."""
        ucs = UCS()
        bfs = BFS()
        for n in range(1, 34):
            with self.subTest(level=n):
                level = parse_level(self.data[n], f"{n:02d}")
                problem = Problem(level, cost_fn=compute_step_cost)

                res_bfs = bfs.search(problem)
                res_ucs = ucs.search(problem)

                self.assertEqual(res_ucs.status, SOLVED)
                final = replay(problem, res_ucs.path)
                self.assertIsNotNone(final)
                self.assertTrue(problem.is_goal(final))

                # UCS tối ưu chi phí: path_cost của UCS <= path_cost của BFS
                self.assertLessEqual(
                    res_ucs.path_cost,
                    res_bfs.path_cost + 1e-9,
                    f"Màn {n}: Chi phí UCS {res_ucs.path_cost} lớn hơn BFS {res_bfs.path_cost}"
                )

    def test_branching_decisions_on_levels_17_and_23(self):
        """Màn 17 và 23: UCS tìm ra đường đi tối ưu năng lượng khác với BFS (tiết kiệm công dựng khối)."""
        ucs = UCS()
        bfs = BFS()
        for n, want_ucs_cost, want_bfs_cost in ((17, 140.10, 140.42), (23, 99.96, 100.96)):
            with self.subTest(level=n):
                level = parse_level(self.data[n], f"{n:02d}")
                problem = Problem(level, cost_fn=compute_step_cost)

                res_bfs = bfs.search(problem)
                res_ucs = ucs.search(problem)

                self.assertAlmostEqual(res_bfs.path_cost, want_bfs_cost, places=2)
                self.assertAlmostEqual(res_ucs.path_cost, want_ucs_cost, places=2)
                self.assertLess(res_ucs.path_cost, res_bfs.path_cost)


if __name__ == "__main__":
    unittest.main()
