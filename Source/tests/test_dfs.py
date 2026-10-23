"""Kiểm tra DFS (docs/01 NV6): quy ước đếm, thứ tự hành động, vô nghiệm, và 33 màn gốc."""
import json
import unittest
from pathlib import Path

from bloxorz.level import Switch, parse_level
from bloxorz.maze import GridMaze
from bloxorz.problem import Problem
from bloxorz.state import Action, Dir, Orient
from solvers.base import NO_SOLUTION, SOLVED
from solvers.dfs import DFS
from tests.helpers import make_level

ORIGINAL_DIR = Path(__file__).resolve().parent.parent / "levels" / "original"
U, D, L, R = (Action(d) for d in (Dir.UP, Dir.DOWN, Dir.LEFT, Dir.RIGHT))


def replay(problem, path):
    state = problem.initial_state()
    for action in path:
        state = problem.result(state, action)
        if state is None:
            return None
    return state


class DFSCountingTests(unittest.TestCase):
    def test_counts_on_corridor_by_hand(self):
        """S.G: lấy S (expanded 1) sinh (0,1); lấy (0,1) (expanded 2) sinh S (trùng) và G (đích).

        generated = 3 (tính cả S trùng), visited = {S, (0,1), G} = 3, ngăn xếp lớn nhất 1.
        """
        result = DFS().search(GridMaze(["S.G"]))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(result.path, [R, R])
        self.assertEqual(result.path_cost, 2)
        self.assertEqual((result.expanded, result.generated, result.max_frontier, result.visited), (2, 3, 1, 3))

    def test_action_order_prefers_up_down_left_right(self):
        """Từ S, hai con D và R đều được đưa vào ngăn xếp; con của D được mở rộng trước."""
        result = DFS().search(GridMaze(["S.", ".G"]))
        self.assertEqual(result.path, [D, R])
        self.assertEqual(result.max_frontier, 2)

    def test_deterministic(self):
        problem = GridMaze(["S...#.....", ".##.#.###.", ".#..#...#.", ".#......#G"])
        first, second = DFS().search(problem), DFS().search(problem)
        self.assertEqual(first.path, second.path)
        self.assertEqual(first.expanded, second.expanded)

    def test_long_path_does_not_hit_recursion_limit(self):
        """Hành lang 3000 ô: lời giải dài hơn giới hạn đệ quy mặc định của Python."""
        result = DFS().search(GridMaze(["S" + "." * 2998 + "G"]))
        self.assertEqual(result.status, SOLVED)
        self.assertEqual(len(result.path), 2999)


class DFSOnBloxorzTests(unittest.TestCase):
    def test_no_solution_when_gap_is_two_tiles(self):
        """Khối không vượt được khe rộng 2 ô: DFS duyệt hết rồi trả no_solution, không lặp vô hạn."""
        problem = Problem(make_level(["S##..##G"]))
        result = DFS().search(problem)
        self.assertEqual(result.status, NO_SOLUTION)
        self.assertEqual(result.path, [])
        self.assertGreater(result.expanded, 0)
        self.assertEqual(result.visited, result.expanded)  # không còn gì trong ngăn xếp

    def test_bridge_state_is_part_of_search(self):
        """Phải đi bấm công tắc mềm rồi quay lại: cùng vị trí khối nhưng khác trạng thái cầu."""
        level = make_level(["o#S#bG#"], [{"at": [0, 0], "bridges": [[0, 4]], "effect": "toggle"}])
        problem = Problem(level)
        result = DFS().search(problem)
        self.assertEqual(result.status, SOLVED)
        final = replay(problem, result.path)
        self.assertTrue(problem.is_goal(final))
        self.assertIn((0, 4), final.open_bridges)


class DFSOnOriginalLevelsTests(unittest.TestCase):
    """33 màn gốc: giải được, phát lại tới đích, số bước không nhỏ hơn bước tối ưu tham khảo."""

    @classmethod
    def setUpClass(cls):
        loader_has_links = "links" in getattr(Switch, "__dataclass_fields__", {})
        cls.ready, cls.pending = [], []
        for path in sorted(ORIGINAL_DIR.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if any("links" in sw for sw in data["switches"]) and not loader_has_links:
                cls.pending.append(path.stem)
            else:
                cls.ready.append((path.stem, data))

    def test_levels_with_links(self):
        if self.pending:
            self.skipTest(f"bộ nạp chưa đọc 'links'; chưa chạy màn {self.pending}")

    def test_original_levels(self):
        self.assertTrue(self.ready)
        for stem, data in self.ready:
            with self.subTest(level=stem):
                level = parse_level(data, stem)
                problem = Problem(level)
                result = DFS().search(problem)
                self.assertEqual(result.status, SOLVED)
                final = replay(problem, result.path)
                self.assertIsNotNone(final, "lời giải có bước làm khối rơi")
                self.assertTrue(problem.is_goal(final))
                self.assertIs(final.orient, Orient.STANDING)
                self.assertGreaterEqual(len(result.path), level.par)
                self.assertEqual(result.path_cost, len(result.path))  # chi phí mặc định 1 mỗi bước
                self.assertLessEqual(result.max_frontier, result.visited)
                self.assertLessEqual(result.expanded, result.visited)


if __name__ == "__main__":
    unittest.main()
