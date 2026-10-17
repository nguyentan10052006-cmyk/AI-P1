"""Kiểm tra bộ màn chơi trong levels/: đủ số lượng, đúng định dạng, đủ 4 nhóm."""
import unittest
from pathlib import Path

from bloxorz.level import SWITCH_KIND, load_levels
from bloxorz.serialize import level_to_dict

LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"


class LevelFilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels = load_levels(LEVELS_DIR)

    def test_at_least_ten_levels(self):
        self.assertGreaterEqual(len(self.levels), 10)

    def test_every_group_is_covered(self):
        groups = {level.group for level in self.levels.values()}
        self.assertTrue({"basic", "fragile", "switch", "combined"} <= groups)

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
        import json
        for level in self.levels.values():
            json.dumps(level_to_dict(level))


if __name__ == "__main__":
    unittest.main()
