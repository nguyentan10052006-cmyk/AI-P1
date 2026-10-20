"""Kiểm tra BFS (docs/01 NV5): quy ước đếm, lời giải ngắn nhất, trạng thái cầu, vô nghiệm, màn gốc 1, 3, 6."""
import unittest
from pathlib import Path

from bloxorz.level import load_level
from bloxorz.maze import MAZES, GridMaze
from bloxorz.problem import Problem
from bloxorz.state import Action, Dir, Orient, State
from solvers.base import NO_SOLUTION, SOLVED
from solvers.bfs import BFS
from tests.helpers import make_level

ORIGINAL_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
D = Action(Dir.DOWN)
L = Action(Dir.LEFT)
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

    def test_counts_on_branching_maze_by_hand(self):
        """Mê cung rẽ nhánh, thứ tự thử U, D, L, R (A = (0,0), M = (1,1), B = (0,2) không tới được):

            .#.
            S.G
            ###

        Lấy S ra (expanded 1): U sinh A, R sinh M; hàng đợi [A, M] dài 2.
        Lấy A ra (expanded 2): D sinh lại S (đã thăm, vẫn đếm generated).
        Lấy M ra (expanded 3): L sinh lại S (đã thăm), R sinh G là đích, dừng.
        generated = 5, visited = {S, A, M, G} = 4, max_frontier = 2 (kiểm cập nhật max_frontier).
        """
        result = BFS().search(GridMaze([".#.", "S.G", "###"]))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [R, R])
        self.assertEqual((result.expanded, result.generated, result.max_frontier, result.visited), (3, 5, 2, 4))

    def test_action_order_prefers_down_before_right_on_open_board(self):
        """Sân trống 4 x 5 có nhiều đường 7 bước; thứ tự U, D, L, R làm BFS ra đúng một đường.

        Mỗi lớp mở ô hàng dưới trước, nên ô nào cũng nhận cha qua R (nếu có), không thì qua D.
        Lần ngược từ G ra D, D, D, R, R, R, R.
        """
        result = BFS().search(GridMaze(MAZES["open"].grid))
        self.assertEqual(result.path, [D, D, D, R, R, R, R])
        self.assertEqual(result.path_cost, 7)

    def test_start_is_goal_returns_empty_path(self):
        """Trạng thái đầu đã là đích: không mở rộng gì, hàng đợi coi như dài 1 và đã thăm 1 trạng thái."""
        level = make_level(LEVEL_1)
        at_goal = State(Orient.STANDING, level.goal)
        result = BFS().search(Problem(level, start=at_goal))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [])
        self.assertEqual(result.path_cost, 0)
        self.assertEqual((result.expanded, result.generated, result.max_frontier, result.visited), (0, 0, 1, 1))


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

    def test_bridge_state_is_part_of_visited(self):
        """Cùng màn với test cầu của DFS (TV2): o#S#bG#, công tắc mềm ở (0,0) bật tắt cầu (0,4).

        Lời giải duy nhất: L (nằm lên công tắc, cầu mở), R (về đứng ở S), R, R (qua cầu tới G).
        Sau 2 bước khối đứng đúng ô S như lúc đầu nhưng cầu đã mở. Trạng thái gồm cả open_bridges
        nên đây là trạng thái mới; nếu tập đã thăm chỉ xét vị trí và tư thế, BFS sẽ bỏ nó và báo vô nghiệm.
        """
        level = make_level(["o#S#bG#"], [{"at": [0, 0], "bridges": [[0, 4]], "effect": "toggle"}])
        problem = Problem(level)
        result = BFS().search(problem)
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [L, R, R, R])
        start, back_at_s = problem.initial_state(), replay(problem, result.path[:2])
        self.assertEqual((back_at_s.orient, back_at_s.pos), (start.orient, start.pos))
        self.assertNotEqual(back_at_s.open_bridges, start.open_bridges)
        self.assertTrue(problem.is_goal(replay(problem, result.path)))

    def test_no_solution_when_gap_is_two_tiles(self):
        """Khe hở không có cầu chặn đường tới G: BFS duyệt hết rồi trả no_solution."""
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
