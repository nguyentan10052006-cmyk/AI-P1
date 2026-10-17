"""Đối chiếu luật với đề bài. Mỗi test trích nguyên câu tiếng Anh trong đề (docstring).

Các câu trong đề được trích từ "AI - Project 1.pdf", mục 2 (Gameplay).
"""
import unittest

from bloxorz.rules import FELL, OK, WON, step
from bloxorz.state import Action, Dir, Orient, State
from tests.helpers import make_level, open_board


def block(orient, pos, pos2=None, open_bridges=()):
    return State(orient, pos, pos2, frozenset(open_bridges))


def roll_from_start(level, *directions):
    """Lăn lần lượt từ trạng thái đầu. Trả về kết quả bước cuối."""
    result = None
    state = level.initial_state()
    for direction in directions:
        result = step(level, state, Action(direction))
        state = result.state
    return result


class BoardAndMovesTests(unittest.TestCase):
    def test_start_is_standing_on_s(self):
        """'The block starts standing upright on a designated starting tile.'"""
        level = make_level(["S#G"])
        state = level.initial_state()
        self.assertEqual(state.orient, Orient.STANDING)
        self.assertEqual(state.pos, (0, 0))

    def test_void_under_any_part_is_illegal(self):
        """'if any part of the block ends up over a void, the block falls and the move is illegal.'"""
        level = make_level(["S.#G"])
        self.assertEqual(step(level, level.initial_state(), Action(Dir.RIGHT)).status, FELL)

    def test_rolling_off_the_edge_is_a_loss(self):
        """'Rolling the block off the edge of the board results in a loss.'"""
        level = open_board(3, 3, (0, 0))
        self.assertEqual(step(level, level.initial_state(), Action(Dir.UP)).status, FELL)

    def test_standing_block_tips_over(self):
        """'a standing block tips over and ends up lying across the two cells in the rolling direction'"""
        level = open_board(9, 9, (0, 0))
        result = step(level, block(Orient.STANDING, (4, 4)), Action(Dir.RIGHT))
        self.assertEqual(set(result.state.cells()), {(4, 5), (4, 6)})
        self.assertEqual(result.state.orient, Orient.HORIZONTAL)

    def test_lying_along_direction_stands_up(self):
        """'a block lying along the rolling direction stands up onto a single cell'"""
        level = open_board(9, 9, (0, 0))
        result = step(level, block(Orient.HORIZONTAL, (4, 4)), Action(Dir.RIGHT))
        self.assertEqual(result.state, block(Orient.STANDING, (4, 6)))

    def test_lying_across_direction_rolls_sideways(self):
        """'a block lying across the rolling direction rolls sideways and remains lying, shifted by one cell.'"""
        level = open_board(9, 9, (0, 0))
        result = step(level, block(Orient.VERTICAL, (4, 4)), Action(Dir.RIGHT))
        self.assertEqual(result.state.orient, Orient.VERTICAL)
        self.assertEqual(set(result.state.cells()), {(4, 5), (5, 5)})

    def test_repeated_moves_follow_the_table(self):
        """'A move is illegal (not allowed) if, after rolling, any cell the block would occupy is a void cell
        or lies outside the board.'"""
        level = open_board(9, 9, (0, 0))
        state = block(Orient.STANDING, (4, 4))
        for direction in (Dir.RIGHT, Dir.RIGHT, Dir.DOWN):
            state = step(level, state, Action(direction)).state
        # đứng (4,4) -> nằm ngang (4,5) -> đứng (4,7) -> nằm dọc (5,7)
        self.assertEqual(state, block(Orient.VERTICAL, (5, 7)))


class WinTests(unittest.TestCase):
    def test_win_only_when_standing_on_goal(self):
        """'This happens only when the block is standing upright on the goal cell. A block that merely lies
        across the goal cell does not win.'"""
        lying = make_level(["S#G"])
        self.assertEqual(roll_from_start(lying, Dir.RIGHT).status, OK)
        standing = make_level(["S##G"])
        self.assertEqual(roll_from_start(standing, Dir.RIGHT, Dir.RIGHT).status, WON)


class FragileTests(unittest.TestCase):
    def test_standing_block_breaks_fragile_tile(self):
        """'If the block stands on a fragile tile, the tile breaks and the block falls.'"""
        level = make_level(["SFFF", "...G"])
        # Đứng trên ô F ở (0, 3) sau hai nước: khối rơi.
        result = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(result.status, FELL)
        self.assertEqual(result.events[-1]["reason"], "fragile")

    def test_block_may_lie_across_fragile_tiles(self):
        """'The block may safely lie across fragile tiles.'"""
        level = make_level(["SFF#", "...G"])
        self.assertEqual(roll_from_start(level, Dir.RIGHT).status, OK)

    def test_single_cube_does_not_break_fragile_tile(self):
        """Đề chỉ đặt luật ô giòn cho 'the block' (khối 1×1×2). Khối con không nằm trong luật này,
        nên không làm vỡ ô (quyết định ghi trong README, mục 'Luật chơi và các giả định')."""
        level = make_level(["S##@", "F#.#", "...G"], [{"at": [0, 3], "targets": [[1, 1], [1, 3]]}])
        split = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(split.state.orient, Orient.SPLIT)
        moved = step(level, split.state, Action(Dir.LEFT, cube=0))
        self.assertEqual(moved.status, OK)
        self.assertEqual(set(moved.state.cells()), {(1, 0), (1, 3)})


class BridgeTests(unittest.TestCase):
    def test_closed_bridge_behaves_like_empty_space(self):
        """'A closed bridge behaves like empty space, while an open bridge behaves like a normal floor tile.'"""
        closed = make_level(["S#b", "..G"])
        self.assertEqual(roll_from_start(closed, Dir.RIGHT).status, FELL)
        opened = make_level(["SBG"])  # cầu mở đi được như nền thường
        self.assertEqual(roll_from_start(opened, Dir.RIGHT).status, OK)

    def test_closing_bridge_under_block_makes_it_fall(self):
        """'the block must always be fully supported by floor tiles.'"""
        level = make_level(["SBo#", "...G"], [{"at": [0, 2], "effect": "close", "bridges": [[0, 1]]}])
        self.assertEqual(roll_from_start(level, Dir.RIGHT).status, FELL)

    def test_states_differ_by_bridge_configuration(self):
        """'states with the same block placement but different bridge configurations are different states.'"""
        a = block(Orient.STANDING, (0, 0), open_bridges=[(1, 1)])
        b = block(Orient.STANDING, (0, 0))
        self.assertNotEqual(a, b)

    def test_split_switch_may_link_bridges(self):
        """'Each switch is linked to one or more bridge tiles.'"""
        level = make_level(
            ["S##@", "####", "G##b"],
            [{"at": [0, 3], "targets": [[1, 0], [2, 2]], "effect": "open", "bridges": [[2, 3]]}],
        )
        result = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(result.state.orient, Orient.SPLIT)
        self.assertEqual(result.state.open_bridges, frozenset({(2, 3)}))


class SwitchTests(unittest.TestCase):
    def test_soft_switch_fires_for_any_part_of_block(self):
        """'Activated when any part of the block presses it, regardless of orientation (standing or lying).'"""
        level = make_level(["S#o#", "..bG"], [{"at": [0, 2], "effect": "open", "bridges": [[1, 2]]}])
        result = roll_from_start(level, Dir.RIGHT)  # nằm lên (0,1)-(0,2), ô (0,2) là công tắc mềm
        self.assertEqual(result.state.open_bridges, frozenset({(1, 2)}))

    def test_heavy_switch_ignores_lying_block(self):
        """'Activated only when the block is standing on it; lying on it does not trigger the switch.'"""
        level = make_level(["#S#x", "..Gb"], [{"at": [0, 3], "effect": "open", "bridges": [[1, 3]]}])
        result = roll_from_start(level, Dir.RIGHT)
        self.assertEqual(result.state.open_bridges, frozenset())

    def test_heavy_switch_fires_when_standing(self):
        """'Activated only when the block is standing on it'"""
        level = make_level(["S##x", "..Gb"], [{"at": [0, 3], "effect": "open", "bridges": [[1, 3]]}])
        result = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(result.state.open_bridges, frozenset({(1, 3)}))

    def test_split_switch_only_when_standing_then_teleports(self):
        """'It teleports the block to predefined positions and splits it into two 1×1×1 cubes.'"""
        level = make_level(["S##@", "####", "...G"], [{"at": [0, 3], "targets": [[1, 0], [1, 2]]}])
        result = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(result.state.orient, Orient.SPLIT)
        self.assertEqual(set(result.state.cells()), {(1, 0), (1, 2)})

    def test_toggle_flips_bridges_each_time(self):
        """'toggle (each activation switches the bridges between open and closed states)'"""
        level = make_level(["S##o", "..Gb"], [{"at": [0, 3], "effect": "toggle", "bridges": [[1, 3]]}])
        result = roll_from_start(level, Dir.RIGHT, Dir.RIGHT)
        self.assertEqual(result.state.open_bridges, frozenset({(1, 3)}))

    def test_permanent_sets_fixed_state(self):
        """'permanent (the bridges are set to a fixed state after activation)'"""
        level = make_level(["SBo#", "...G"], [{"at": [0, 2], "effect": "close", "bridges": [[0, 1]]}])
        start = level.initial_state()
        self.assertEqual(start.open_bridges, frozenset({(0, 1)}))
        self.assertEqual(step(level, start, Action(Dir.RIGHT)).status, FELL)


class SplitTests(unittest.TestCase):
    LEVEL = make_level(["S##@", "####", "...G"], [{"at": [0, 3], "targets": [[1, 0], [1, 2]]}])

    def test_cubes_are_controlled_one_at_a_time(self):
        """'they are controlled one at a time (e.g., switching control with the spacebar)'"""
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        result = step(self.LEVEL, split, Action(Dir.UP, cube=0))
        self.assertEqual(set(result.moved.cells()), {(0, 0), (1, 2)})

    def test_cubes_merge_on_adjacent_tiles(self):
        """'merge back into a standard 1×1×2 block when positioned on adjacent tiles.'"""
        split = block(Orient.SPLIT, (1, 0), (1, 2))
        result = step(self.LEVEL, split, Action(Dir.RIGHT, cube=0))
        self.assertEqual(result.state.orient, Orient.HORIZONTAL)

    def test_single_cube_activates_soft_switch(self):
        """'A single cube can activate soft switches'"""
        level = make_level(["S##@", "#o.#", "..bG"], [
            {"at": [0, 3], "targets": [[1, 0], [1, 3]]},
            {"at": [1, 1], "effect": "open", "bridges": [[2, 2]]},
        ])
        split = block(Orient.SPLIT, (1, 0), (1, 3))
        result = step(level, split, Action(Dir.RIGHT, cube=0))
        self.assertEqual(result.state.open_bridges, frozenset({(2, 2)}))

    def test_single_cube_cannot_activate_heavy_switch(self):
        """'but cannot activate heavy switches'"""
        level = make_level(["S##@", "#x.#", "..bG"], [
            {"at": [0, 3], "targets": [[1, 0], [1, 3]]},
            {"at": [1, 1], "effect": "open", "bridges": [[2, 2]]},
        ])
        split = block(Orient.SPLIT, (1, 0), (1, 3))
        result = step(level, split, Action(Dir.RIGHT, cube=0))
        self.assertEqual(result.state.open_bridges, frozenset())

    def test_single_cube_cannot_complete_stage(self):
        """'A single cube can activate soft switches but cannot activate heavy switches or complete the stage.'"""
        level = make_level(["S##@", "G#.#", "...."], [{"at": [0, 3], "targets": [[1, 1], [1, 3]]}])
        split = block(Orient.SPLIT, (1, 1), (1, 3))
        result = step(level, split, Action(Dir.LEFT, cube=0))  # khối con đặt lên ô G (1,0)
        self.assertEqual(result.status, OK)
        self.assertNotEqual(result.status, WON)


if __name__ == "__main__":
    unittest.main()
