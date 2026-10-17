"""Kiểm tra bộ màn chơi trong levels/: số lượng, chương, độ khó tăng dần, định dạng và thông tin hiển thị."""
import json
import unittest
from pathlib import Path

from bloxorz.level import SWITCH_KIND, load_levels
from bloxorz.serialize import level_to_dict

LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"
PLAIN_TILES = {"#", "S", "G", "."}


def features(level):
    """Các ký tự đặc biệt có trong màn (ô giòn, cầu, công tắc)."""
    return {ch for row in level.grid for ch in row} - PLAIN_TILES


class LevelFilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels = load_levels(LEVELS_DIR)

    def chapter(self, number):
        return sorted((lv for lv in self.levels.values() if lv.chapter == number), key=lambda lv: lv.order)

    def test_at_least_ten_levels(self):
        self.assertGreaterEqual(len(self.levels), 10)

    def test_eighteen_levels_in_three_kinds(self):
        kinds = [lv.kind for lv in self.levels.values()]
        self.assertEqual(kinds.count("main"), 15)
        self.assertEqual(kinds.count("challenge"), 2)
        self.assertEqual(kinds.count("bonus"), 1)

    def test_every_group_is_covered(self):
        groups = {level.group for level in self.levels.values()}
        self.assertTrue({"basic", "fragile", "switch", "combined"} <= groups)

    def test_chapters_have_consecutive_orders(self):
        for number in range(1, 6):
            with self.subTest(chapter=number):
                orders = [lv.order for lv in self.chapter(number)]
                self.assertEqual(orders, list(range(1, len(orders) + 1)))
                self.assertEqual(len(orders), 3)

    def test_challenge_and_bonus_are_after_main_chapters(self):
        for level in self.levels.values():
            if level.kind == "main":
                self.assertLessEqual(level.chapter, 5, level.id)
            else:
                self.assertGreaterEqual(level.chapter, 6, level.id)

    def test_bonus_is_locked_and_others_are_open(self):
        for level in self.levels.values():
            with self.subTest(level=level.id):
                if level.kind == "bonus":
                    self.assertGreater(level.unlock_stars, 0)
                else:
                    self.assertEqual(level.unlock_stars, 0)

    def test_every_level_has_par(self):
        for level in self.levels.values():
            with self.subTest(level=level.id):
                self.assertGreater(level.par, 0)

    def test_difficulty_rises_chapter_by_chapter(self):
        means = []
        for number in range(1, 6):
            pars = [lv.par for lv in self.chapter(number)]
            means.append(sum(pars) / len(pars))
        self.assertEqual(means, sorted(means))
        self.assertEqual(len(set(means)), len(means))

    def test_mechanics_are_introduced_in_order(self):
        """Chương 1 không có cơ chế nào, chương 2 chỉ có ô giòn, chương 3 chưa có công tắc tách."""
        for level in self.chapter(1):
            self.assertEqual(features(level), set(), level.id)
        for level in self.chapter(2):
            self.assertLessEqual(features(level), {"F"}, level.id)
        for level in self.chapter(3):
            self.assertNotIn("@", features(level), level.id)

    def test_first_level_of_each_mechanic_has_intro(self):
        for lid in ("1-1", "2-1", "3-1", "3-2", "4-1"):
            with self.subTest(level=lid):
                self.assertTrue(self.levels[lid].intro)

    def test_every_level_has_name_and_source(self):
        for level in self.levels.values():
            with self.subTest(level=level.id):
                self.assertTrue(level.name)
                self.assertTrue(level.source)

    def test_switch_chars_match_configured_kinds(self):
        for level in self.levels.values():
            for cell, sw in level.switches.items():
                self.assertEqual(SWITCH_KIND[level.tile(cell)], sw.kind)

    def test_level_serializes_to_json_types(self):
        for level in self.levels.values():
            json.dumps(level_to_dict(level))


if __name__ == "__main__":
    unittest.main()
