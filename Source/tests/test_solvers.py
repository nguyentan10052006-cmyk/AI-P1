"""Chạy 4 solver trên các mê cung mẫu (bloxorz/maze.py) và kiểm tra kết quả.

Solver nào còn raise NotImplementedError thì test của nó được bỏ qua (skip), không tính là lỗi.
Chạy riêng: python -m unittest tests.test_solvers -v
"""
import unittest

from bloxorz.maze import MAZES
from solvers import ALGORITHMS
from solvers.base import NO_SOLUTION, SOLVED, SearchResult

# Thuật toán phải cho lời giải ít bước nhất / chi phí nhỏ nhất
SHORTEST = {"bfs"}
CHEAPEST = {"ucs", "astar", "astar_m"}


def replay(problem, path):
    """Phát lại path, trả về (trạng thái cuối, tổng chi phí); None nếu có bước không hợp lệ."""
    state, cost = problem.initial_state(), 0.0
    for action in path:
        nxt = problem.result(state, action)
        if nxt is None:
            return None
        cost += problem.step_cost(state, action, nxt)
        state = nxt
    return state, cost


class SolverOnMazeTests(unittest.TestCase):
    def run_solver(self, key, case):
        solver = ALGORITHMS[key]()
        problem = case.problem()
        try:
            solver.prepare(problem)
            result = solver.search(problem)
        except NotImplementedError:
            self.skipTest(f"{solver.name} chưa cài đặt")
        self.assertIsInstance(result, SearchResult)
        return problem, result

    def check(self, key):
        for name, case in MAZES.items():
            with self.subTest(maze=name):
                problem, result = self.run_solver(key, case)
                self.assertGreater(result.visited, 0)
                for counter in ("expanded", "generated", "max_frontier"):
                    self.assertGreaterEqual(getattr(result, counter), 0, counter)
                if case.steps is None:
                    # Heuristic biết trước là không tới được đích thì có thể dừng ngay, không mở rộng nút nào
                    self.assertEqual(result.status, NO_SOLUTION)
                    self.assertEqual(result.path, [])
                    continue
                self.assertEqual(result.status, SOLVED)
                self.assertGreater(result.expanded, 0)
                self.assertGreater(result.max_frontier, 0)
                replayed = replay(problem, result.path)
                self.assertIsNotNone(replayed, "lời giải có bước đâm vào tường")
                final, cost = replayed
                self.assertTrue(problem.is_goal(final), "lời giải không tới đích")
                self.assertAlmostEqual(result.path_cost, cost, msg="path_cost khác tổng chi phí khi phát lại")
                self.assertGreaterEqual(len(result.path), case.steps)
                if key in SHORTEST:
                    self.assertEqual(len(result.path), case.steps)
                if key in CHEAPEST:
                    self.assertAlmostEqual(result.path_cost, case.cost)

    def test_bfs(self):
        self.check("bfs")

    def test_dfs(self):
        self.check("dfs")

    def test_ucs(self):
        self.check("ucs")

    def test_astar(self):
        self.check("astar")

    def test_astar_m(self):
        self.check("astar_m")


if __name__ == "__main__":
    unittest.main()
