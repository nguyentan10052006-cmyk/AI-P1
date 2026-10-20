"""Kiểm tra BFS (docs/01 NV5): quy ước đếm, lời giải ngắn nhất, vô nghiệm, màn gốc 1, 3, 6."""
import unittest
from pathlib import Path

from bloxorz.level import load_level
from bloxorz.maze import GridMaze
from bloxorz.problem import Problem
from bloxorz.state import Action, Dir
from solvers.base import NO_SOLUTION, SOLVED
from solvers.bfs import BFS
from tests.helpers import make_level

ORIGINAL_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
R = Action(Dir.RIGHT)

# Màn 1 của Bloxorz (D. Clarke, 2007), chép từ levels/original/01.json của TV2
# (dữ liệu: jacobcoughenour/bloxorz_gba, GPL-3.0), để test chạy được trước khi 33 màn gốc vào main.
LEVEL_1 = [
    "...............",
    "...............",
    "..###..........",
    "..#S####.......",
    "..#########....",
    "...#########...",
    ".......##G##...",
    "........###....",
    "...............",
    "...............",
]


def replay(problem, path):
    """Phát lại path trên engine; trả về trạng thái cuối, hoặc None nếu có bước làm khối rơi."""
    state = problem.initial_state()
    for action in path:
        state = problem.result(state, action)
        if state is None:
            return None
    return state


class BFSCountingTests(unittest.TestCase):
    def test_counts_on_corridor_by_hand(self):
        """S.G: lấy S ra (expanded 1), sinh (0,1); lấy (0,1) ra (expanded 2), sinh S (đã thăm) và G (đích).

        generated = 3 (tính cả S đã thăm), visited = {S, (0,1), G} = 3, hàng đợi dài nhất là 1.
        """
        result = BFS().search(GridMaze(["S.G"]))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [R, R])
        self.assertEqual(result.path_cost, 2)
        self.assertEqual((result.expanded, result.generated, result.max_frontier, result.visited), (2, 3, 1, 3))


class BFSOnBloxorzTests(unittest.TestCase):
    def test_level_1_typed_by_hand(self):
        """Màn 1 có lời giải ngắn nhất 7 bước (docs/03 mục 4)."""
        problem = Problem(make_level(LEVEL_1))
        result = BFS().search(problem)
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(len(result.path), 7)
        final = replay(problem, result.path)
        self.assertIsNotNone(final, "lời giải có bước làm khối rơi")
        self.assertTrue(problem.is_goal(final))

    def test_no_solution_when_gap_is_two_tiles(self):
        """Khối không vượt được khe rộng 2 ô: BFS duyệt hết rồi trả no_solution."""
        problem = Problem(make_level(["S##..##G"]))
        result = BFS().search(problem)
        self.assertEqual(result.status, NO_SOLUTION)
        self.assertEqual(result.path, [])
        self.assertGreater(result.expanded, 0)


@unittest.skipUnless(ORIGINAL_DIR.is_dir(), "chưa có levels/original/ (33 màn gốc của TV2) trên nhánh này")
class BFSOnOriginalLevelsTests(unittest.TestCase):
    """Mốc M1 (docs/01 NV5): màn 1, 3, 6 ra đúng 7, 19, 35 bước."""

    def test_levels_1_3_6(self):
        for name, steps in (("01", 7), ("03", 19), ("06", 35)):
            with self.subTest(level=name):
                level = load_level(ORIGINAL_DIR / f"{name}.json", name)
                problem = Problem(level)
                result = BFS().search(problem)
                self.assertEqual(result.status, SOLVED)
                self.assertEqual(len(result.path), steps)
                final = replay(problem, result.path)
                self.assertIsNotNone(final, "lời giải có bước làm khối rơi")
                self.assertTrue(problem.is_goal(final))


if __name__ == "__main__":
    unittest.main()
