"""Hình mê cung trong docs/gridmaze/ phải khớp MAZES. Sửa MAZES thì chạy lại: python tools/draw_mazes.py"""
import unittest
from pathlib import Path

from bloxorz.maze import MAZES
from tools.draw_mazes import to_markdown, to_svg

DOCS = Path(__file__).resolve().parents[2] / "docs" / "gridmaze"


class DrawMazeTests(unittest.TestCase):
    def test_every_maze_draws(self):
        for name, case in MAZES.items():
            with self.subTest(name):
                self.assertIn("<svg", to_svg(case, name))
        self.assertIn("## `open`", to_markdown(list(MAZES)))

    @unittest.skipUnless(DOCS.is_dir(), "không có thư mục docs/gridmaze (ví dụ trong file nộp)")
    def test_docs_are_up_to_date(self):
        hint = "hình đã cũ, chạy lại: python tools/draw_mazes.py"
        for name, case in MAZES.items():
            with self.subTest(name):
                path = DOCS / f"{name}.svg"
                self.assertTrue(path.is_file(), hint)
                self.assertEqual(path.read_text(encoding="utf-8"), to_svg(case, name), hint)
        self.assertEqual((DOCS / "README.md").read_text(encoding="utf-8"), to_markdown(list(MAZES)), hint)


if __name__ == "__main__":
    unittest.main()
