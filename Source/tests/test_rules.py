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
        """T18: khối đứng trên công tắc tách thì thành hai khối con ở đúng hai ô trong file màn."""
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
        """T21: hai khối con kề cạnh cùng hàng thì ghép thành H neo ô trái."""
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


class SplitMergeTests(unittest.TestCase):
    """V06: tách và ghép khối (docs/02 §4, mã T17–T23)."""

    BOARD = open_board(4, 4, (0, 0))

    def test_lying_block_on_split_switch_does_not_split(self):
        """T17: khối nằm đè lên công tắc tách thì không tách (chỉ khối đứng mới tách)."""
        level = make_level(["S#@#", "####", "...G"], [{"at": [0, 2], "targets": [[1, 0], [1, 3]]}])
        for name, start, want in (
            ("H", level.initial_state(), Orient.HORIZONTAL),        # S lăn R: nằm ngang (0,1)-(0,2)
            ("V", block(Orient.VERTICAL, (0, 1)), Orient.VERTICAL),  # nằm dọc lăn R: (0,2)-(1,2)
        ):
            with self.subTest(orient=name):
                result = step(level, start, Action(Dir.RIGHT))
                self.assertEqual(result.status, OK)
                self.assertEqual(result.state.orient, want)
                self.assertIn((0, 2), result.state.cells())
                self.assertNotIn("split", [e["type"] for e in result.events])

    def test_adjacent_cubes_merge_with_correct_orient_and_anchor(self):
        """T21: kề cạnh thì ghép; cùng hàng thành H neo ô trái, cùng cột thành V neo ô trên."""
        cases = [
            # (khối con 0, khối con 1, lệnh, tư thế sau ghép, ô neo)
            ((1, 0), (1, 2), Action(Dir.LEFT, cube=1), Orient.HORIZONTAL, (1, 0)),
            ((0, 2), (2, 2), Action(Dir.UP, cube=1), Orient.VERTICAL, (0, 2)),
            ((0, 2), (2, 2), Action(Dir.DOWN, cube=0), Orient.VERTICAL, (1, 2)),
        ]
        for a, b, action, want_orient, want_anchor in cases:
            with self.subTest(cubes=(a, b), action=(action.dir.value, action.cube)):
                result = step(self.BOARD, block(Orient.SPLIT, a, b), action)
                self.assertEqual(result.status, OK)
                self.assertEqual(result.moved.orient, Orient.SPLIT)  # trước khi ghép
                self.assertEqual(result.state.orient, want_orient)
                self.assertEqual(result.state.pos, want_anchor)
                self.assertIsNone(result.state.pos2)
                self.assertEqual(result.events[-1], {"type": "merge"})

    def test_diagonal_cubes_do_not_merge(self):
        """T22: hai khối con kề chéo thì không ghép, vẫn là trạng thái đã tách."""
        result = step(self.BOARD, block(Orient.SPLIT, (0, 2), (2, 1)), Action(Dir.DOWN, cube=0))
        self.assertEqual(result.status, OK)
        self.assertEqual(result.state.orient, Orient.SPLIT)
        self.assertEqual(result.state.cells(), ((1, 2), (2, 1)))
        self.assertEqual(result.events, [])

    def test_cube_closing_bridge_under_other_cube_falls(self):
        """T23: khối con 0 bấm công tắc mềm đóng cầu đang đỡ khối con 1, hành động bị loại."""
        level = make_level(["S###", "o#B#", "...G"], [{"at": [1, 0], "effect": "close", "bridges": [[1, 2]]}])
        split = block(Orient.SPLIT, (0, 0), (1, 2), open_bridges=[(1, 2)])
        action = Action(Dir.DOWN, cube=0)
        result = step(level, split, action)
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1], {"type": "fell", "reason": "bridge_closed", "at": (1, 2)})
        self.assertIsNone(Problem(level).result(split, action))

    def test_actions_when_split_are_u_d_l_r_of_cube_0_then_cube_1(self):
        """Thứ tự hành động cố định khi đã tách: U D L R của khối con 0, rồi của khối con 1."""
        problem = Problem(self.BOARD)
        order = [Dir.UP, Dir.DOWN, Dir.LEFT, Dir.RIGHT]
        self.assertEqual(problem.actions(problem.initial_state()), [Action(d) for d in order])
        want = [Action(d, 0) for d in order] + [Action(d, 1) for d in order]
        self.assertEqual(problem.actions(block(Orient.SPLIT, (0, 2), (2, 1))), want)

    def test_cube_numbers_follow_sorted_cells(self):
        """Khối con 0 luôn là ô nhỏ hơn theo (hàng, cột), nên sau một bước hai số có thể đổi chỗ."""
        result = step(self.BOARD, block(Orient.SPLIT, (2, 0), (2, 3)), Action(Dir.UP, cube=1))
        self.assertEqual(result.state.pos, (1, 3))   # khối vừa đi lên giờ là khối con 0
        self.assertEqual(result.state.pos2, (2, 0))


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
