"""Kiểm thử luật chơi: bảng chuyển tư thế, rơi, thắng, công tắc, tách và ghép khối."""
import unittest

from bloxorz.level import LevelError
from bloxorz.problem import Problem
from bloxorz.rules import FELL, OK, WON, step
from bloxorz.state import Action, Dir, Orient, State, split_state
from tests.helpers import make_level, open_board
from tests.test_bfs import LEVEL_1


def block(orient, pos, pos2=None, open_bridges=()):
    return State(orient, pos, pos2, frozenset(open_bridges))


class RollTableTests(unittest.TestCase):
    """12 tổ hợp (tư thế, hướng). Kiểm tra theo tập ô khối chiếm sau khi lăn."""

    LEVEL = open_board(9, 9, (0, 0))
    # Khối đặt ở giữa bảng (4, 4) nên mọi nước đi đều nằm trong bảng.
    CASES = [
        (Orient.STANDING, (4, 4), Dir.UP, Orient.VERTICAL, {(2, 4), (3, 4)}),
        (Orient.STANDING, (4, 4), Dir.DOWN, Orient.VERTICAL, {(5, 4), (6, 4)}),
        (Orient.STANDING, (4, 4), Dir.LEFT, Orient.HORIZONTAL, {(4, 2), (4, 3)}),
        (Orient.STANDING, (4, 4), Dir.RIGHT, Orient.HORIZONTAL, {(4, 5), (4, 6)}),
        (Orient.HORIZONTAL, (4, 4), Dir.UP, Orient.HORIZONTAL, {(3, 4), (3, 5)}),
        (Orient.HORIZONTAL, (4, 4), Dir.DOWN, Orient.HORIZONTAL, {(5, 4), (5, 5)}),
        (Orient.HORIZONTAL, (4, 4), Dir.LEFT, Orient.STANDING, {(4, 3)}),
        (Orient.HORIZONTAL, (4, 4), Dir.RIGHT, Orient.STANDING, {(4, 6)}),
        (Orient.VERTICAL, (4, 4), Dir.UP, Orient.STANDING, {(3, 4)}),
        (Orient.VERTICAL, (4, 4), Dir.DOWN, Orient.STANDING, {(6, 4)}),
        (Orient.VERTICAL, (4, 4), Dir.LEFT, Orient.VERTICAL, {(4, 3), (5, 3)}),
        (Orient.VERTICAL, (4, 4), Dir.RIGHT, Orient.VERTICAL, {(4, 5), (5, 5)}),
    ]

    def test_all_twelve_transitions(self):
        """T01: đủ 12 trường hợp (tư thế, hướng) của bảng chuyển ở docs/02 §3."""
        for orient, pos, direction, want_orient, want_cells in self.CASES:
            with self.subTest(orient=orient.value, dir=direction.value):
                result = step(self.LEVEL, block(orient, pos), Action(direction))
                self.assertEqual(result.status, OK)
                self.assertEqual(result.moved.orient, want_orient)
                self.assertEqual(set(result.moved.cells()), want_cells)


class FallAndWinTests(unittest.TestCase):
    def test_rolling_off_board_falls(self):
        """T02: lăn ra ngoài bàn thì rơi."""
        level = open_board(3, 3, (0, 0))
        result = step(level, level.initial_state(), Action(Dir.LEFT))
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "off_board")

    def test_rolling_onto_void_falls(self):
        """T03: lăn xong khối nằm, một nửa trên ô trống thì rơi."""
        level = make_level(["S.#G"])
        result = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "void")

    def test_rolling_onto_closed_bridge_falls(self):
        level = make_level(["S#b", "..G"])
        result = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "bridge_closed")

    def test_lying_across_goal_does_not_win(self):
        """T05: nằm đè lên ô đích thì không thắng (cũng không rơi)."""
        level = make_level(["S#G"])
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(first.status, OK)
        self.assertEqual(first.state.orient, Orient.HORIZONTAL)
        # Lăn tiếp thì khối đứng ở (0, 3), ngoài bảng: rơi, không thắng.
        second = step(level, first.state, Action(Dir.RIGHT))
        self.assertEqual(second.status, FELL)

    def test_standing_on_goal_wins(self):
        """T04: đứng trên ô đích thì thắng."""
        level = make_level(["S##G"])
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        second = step(level, first.state, Action(Dir.RIGHT))
        self.assertEqual(second.status, WON)
        self.assertEqual(second.state.pos, (0, 3))
        self.assertEqual(second.events[-1], {"type": "won"})

    def test_lying_block_half_over_void_falls(self):
        """T03: khối đang nằm lăn sang hàng mới, một nửa trên ô trống thì rơi."""
        level = make_level(["S##", "G#."])
        result = step(level, block(Orient.HORIZONTAL, (0, 1)), Action(Dir.DOWN))
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "void")

    def test_level_1_reference_solution_wins_at_step_7(self):
        """T06: phát lại R D D R R D R trên màn 1, sáu bước đầu chưa thắng, bước 7 thắng."""
        level = make_level(LEVEL_1)
        moves = [Dir.RIGHT, Dir.DOWN, Dir.DOWN, Dir.RIGHT, Dir.RIGHT, Dir.DOWN, Dir.RIGHT]
        state = level.initial_state()
        for number, direction in enumerate(moves, start=1):
            with self.subTest(step=number, dir=direction.value):
                result = step(level, state, Action(direction))
                self.assertEqual(result.status, WON if number == len(moves) else OK)
            state = result.state
        self.assertEqual(state.orient, Orient.STANDING)
        self.assertEqual(state.pos, level.goal)

    def test_fragile_lying_is_safe_but_standing_breaks(self):
        level = make_level(["SFFF", "...G"])
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(first.status, OK)  # nằm trên hai ô F thì an toàn
        second = step(level, first.state, Action(Dir.RIGHT))  # đứng trên F ở (0, 3)
        self.assertEqual(second.status, FELL)
        self.assertEqual(second.events[-2], {"type": "fragile_broken", "at": (0, 3)})
        self.assertEqual(second.events[-1]["reason"], "fragile")


class SwitchTests(unittest.TestCase):
    def test_soft_switch_activated_by_standing_block_toggles_bridge(self):
        level = make_level(
            ["S##o", "..Gb"],
            [{"at": [0, 3], "effect": "toggle", "bridges": [[1, 3]]}],
        )
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        second = step(level, first.state, Action(Dir.RIGHT))
        self.assertEqual(second.status, OK)
        self.assertEqual(second.state.open_bridges, frozenset({(1, 3)}))
        self.assertEqual(second.events[0]["type"], "switch")

    def test_soft_switch_activated_by_lying_block(self):
        level = make_level(
            ["S#o#", "..bG"],
            [{"at": [0, 2], "effect": "open", "bridges": [[1, 2]]}],
        )
        result = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(result.state.orient, Orient.HORIZONTAL)
        self.assertEqual(result.state.open_bridges, frozenset({(1, 2)}))

    def test_heavy_switch_ignores_lying_block(self):
        level = make_level(
            ["#S#x", "..Gb"],
            [{"at": [0, 3], "effect": "open", "bridges": [[1, 3]]}],
        )
        result = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(result.state.orient, Orient.HORIZONTAL)  # nằm lên (0,2)-(0,3)
        self.assertEqual(result.state.open_bridges, frozenset())

    def test_heavy_switch_activated_by_standing_block(self):
        level = make_level(
            ["S##x", "..Gb"],
            [{"at": [0, 3], "effect": "open", "bridges": [[1, 3]]}],
        )
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        second = step(level, first.state, Action(Dir.RIGHT))
        self.assertEqual(second.state.open_bridges, frozenset({(1, 3)}))

    def test_closing_bridge_under_block_makes_it_fall(self):
        # Cầu (0,1) đang mở và nằm dưới khối khi khối nằm lên (0,1)-(0,2).
        # Công tắc (0,2) đóng chính cầu đó, nên khối rơi.
        level = make_level(
            ["SBo#", "...G"],
            [{"at": [0, 2], "effect": "close", "bridges": [[0, 1]]}],
        )
        result = step(level, level.initial_state(), Action(Dir.RIGHT))
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "bridge_closed")

    def test_split_switch_teleports_and_splits(self):
        level = make_level(
            ["S##@", "####", "...G"],
            [{"at": [0, 3], "targets": [[1, 0], [1, 2]]}],
        )
        first = step(level, level.initial_state(), Action(Dir.RIGHT))
        second = step(level, first.state, Action(Dir.RIGHT))
        self.assertEqual(second.status, OK)
        self.assertEqual(second.state.orient, Orient.SPLIT)
        self.assertEqual(second.state.cells(), ((1, 0), (1, 2)))
        self.assertEqual(second.events[0]["type"], "split")

    def test_split_cubes_merge_when_adjacent(self):
        level = make_level(
            ["S##@", "####", "...G"],
            [{"at": [0, 3], "targets": [[1, 0], [1, 2]]}],
        )
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        result = step(level, split, Action(Dir.RIGHT, cube=0))
        self.assertEqual(result.status, OK)
        self.assertEqual(result.moved.orient, Orient.SPLIT)  # trước khi ghép
        self.assertEqual(result.state.orient, Orient.HORIZONTAL)
        self.assertEqual(result.state.pos, (1, 1))
        self.assertEqual(result.events[-1], {"type": "merge"})

    def test_one_cube_falling_loses(self):
        level = make_level(
            ["S##@", "####", "...G"],
            [{"at": [0, 3], "targets": [[1, 0], [1, 2]]}],
        )
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        result = step(level, split, Action(Dir.LEFT, cube=0))
        self.assertEqual(result.status, FELL)


class StateAndProblemTests(unittest.TestCase):
    def test_same_placement_different_bridges_are_different_states(self):
        a = block(Orient.STANDING, (0, 0), open_bridges=[(1, 1)])
        b = block(Orient.STANDING, (0, 0), open_bridges=[])
        self.assertNotEqual(a, b)
        self.assertEqual(len({a, b}), 2)

    def test_split_state_is_normalized(self):
        self.assertEqual(split_state((1, 2), (1, 0), frozenset()).pos, (1, 0))

    def test_actions_and_results_through_problem(self):
        level = make_level(["S#G"])
        problem = Problem(level)
        self.assertEqual(len(problem.actions(problem.initial_state())), 4)
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        self.assertEqual(len(problem.actions(split)), 8)
        self.assertIsNone(problem.result(problem.initial_state(), Action(Dir.LEFT)))
        self.assertFalse(problem.is_goal(problem.initial_state()))
        self.assertEqual(problem.step_cost(problem.initial_state(), Action(Dir.RIGHT), None), 1)

    def test_invalid_cube_index_is_rejected(self):
        level = make_level(["S#G"])
        with self.assertRaises(ValueError):
            step(level, level.initial_state(), Action(Dir.RIGHT, cube=0))
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        with self.assertRaises(ValueError):
            step(make_level(["S##", "###", "##G"]), split, Action(Dir.RIGHT))


class LevelValidationTests(unittest.TestCase):
    def test_missing_goal_is_rejected(self):
        with self.assertRaises(LevelError):
            make_level(["S##"])

    def test_switch_tile_without_config_is_rejected(self):
        with self.assertRaises(LevelError):
            make_level(["S#o", "..G"])

    def test_bridge_target_must_be_a_bridge(self):
        with self.assertRaises(LevelError):
            make_level(["S#o#", "...G"], [{"at": [0, 2], "effect": "toggle", "bridges": [[0, 3]]}])

    def test_split_needs_two_targets(self):
        with self.assertRaises(LevelError):
            make_level(["S##@", "...G"], [{"at": [0, 3], "targets": [[1, 0]]}])


if __name__ == "__main__":
    unittest.main()
