"""Kiểm thử GridMaze: luật đi, chi phí và đáp án của các mê cung mẫu."""
import unittest

from bloxorz.maze import MAZES, GridMaze
from bloxorz.state import Action, Dir

U, D, L, R = (Action(d) for d in Dir)


class GridMazeTests(unittest.TestCase):
    MAZE = GridMaze(["S.#",
                     ".3G"])

    def test_start_and_goal(self):
        self.assertEqual(self.MAZE.initial_state(), (0, 0))
        self.assertEqual(self.MAZE.goal, (1, 2))
        self.assertTrue(self.MAZE.is_goal((1, 2)))
        self.assertFalse(self.MAZE.is_goal((0, 0)))

    def test_actions_are_the_four_directions_in_order(self):
        self.assertEqual(self.MAZE.actions((0, 0)), [U, D, L, R])

    def test_wall_and_edge_give_none(self):
        self.assertIsNone(self.MAZE.result((0, 0), U))
        self.assertIsNone(self.MAZE.result((0, 0), L))
        self.assertIsNone(self.MAZE.result((0, 1), R))  # tường
        self.assertEqual(self.MAZE.result((0, 0), R), (0, 1))

    def test_digit_cells_cost_their_value(self):
        self.assertEqual(self.MAZE.step_cost((0, 1), D, (1, 1)), 3)
        self.assertEqual(self.MAZE.step_cost((1, 1), R, (1, 2)), 1)

    def test_bad_grids_are_rejected(self):
        with self.assertRaises(ValueError):
            GridMaze(["S.", "."])
        with self.assertRaises(ValueError):
            GridMaze(["S..", "..."])
        with self.assertRaises(ValueError):
            GridMaze(["S?G"])

    def test_presets_parse(self):
        for name, case in MAZES.items():
            with self.subTest(name):
                case.problem()


if __name__ == "__main__":
    unittest.main()
