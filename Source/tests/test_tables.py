"""Kiểm tra experiments/tables.py (V25) bằng DỮ LIỆU TỔNG HỢP; không phải kết quả thực nghiệm.

Bỏ qua nếu chưa cài matplotlib (tables.py đọc summary.csv bằng charts.read_summary).
"""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

HAS_MPL = importlib.util.find_spec("matplotlib") is not None
if HAS_MPL:
    from experiments import tables
    from tests.test_charts import write_summary


def row(level, group, algorithm, status="solved", **values):
    base = {"level": level, "group": group, "algorithm": algorithm, "status": status, "commit": "abc1234"}
    return {**base, **values}


def small_rows():
    """Hai màn G1 (01, 03), một màn G5 (08); expanded chọn để trung vị tính tay được."""
    rows = []
    for level, group, bfs_steps in (("original/01", "G1", 7), ("original/03", "G1", 19), ("original/08", "G5", 10)):
        n = int(level[-2:])
        rows += [
            row(level, group, "bfs", steps=bfs_steps, path_cost=bfs_steps, expanded=10 * n, generated=20 * n,
                peak_mem_kb=1.5 * n, search_ms=0.25 * n),
            row(level, group, "dfs", steps=2 * bfs_steps, path_cost=2 * bfs_steps, expanded=30 * n, generated=60 * n),
            row(level, group, "ucs", steps=bfs_steps, path_cost=bfs_steps, expanded=12 * n, generated=24 * n),
            row(level, group, "astar", steps=bfs_steps, path_cost=bfs_steps, expanded=6 * n, generated=6),
        ]
    rows[-1]["status"] = "timeout"   # A* ở màn 08 không giải được: ô T5 của G5 phải ghi —
    rows.append(row("gen/S3-010", "S3", "bfs", status="no_solution", expanded=280))
    return rows


@unittest.skipUnless(HAS_MPL, "chưa cài matplotlib")
class TablesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="v25-tables-"))
        self.summary = self.tmp / "summary.csv"
        self.out = self.tmp / "tables.md"
        write_summary(self.summary, small_rows())
        (self.tmp / "run_info.json").write_text('{"cost": "energy"}', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_number_format_matches_report(self):
        self.assertEqual(tables.fmt(1234567.891, 2), "1 234 567,89")
        self.assertEqual(tables.fmt(48.0), "48")
        self.assertEqual(tables.fmt(None), "—")

    def test_effective_branching(self):
        self.assertAlmostEqual(tables.effective_branching(6, 2), 2.0, places=9)    # 1 + 2 + 4 = 7
        self.assertAlmostEqual(tables.effective_branching(3, 3), 1.0, places=9)    # 1 + 1 + 1 + 1 = 4
        self.assertIsNone(tables.effective_branching(5, 0))
        self.assertGreater(tables.effective_branching(10 ** 6, 266), 1.0)          # d lớn: không tràn số

    def test_tables_from_summary(self):
        self.assertEqual(tables.main(["--summary", str(self.summary), "--out", str(self.out)]), 0)
        text = self.out.read_text(encoding="utf-8")
        lines = text.splitlines()
        # T3 số nút mở rộng: G1 có 2 màn (01, 03); BFS 10 và 30 -> trung vị 20; DFS 30 và 90 -> 60
        self.assertIn("| G1 | 2 | 20 | 60 | 24 | 12 |", lines)
        # T3 thời gian: BFS ở G1 là 0,25 và 0,75 -> 0,50
        self.assertIn("| G1 | 2 | 0,50 | — | — | — |", lines)
        # T4: DFS giải 3/3, không màn nào tối ưu về số bước, dài gấp đôi BFS
        self.assertIn("| DFS | 3/3 | 0/3 | 0/3 | 200,0 % |", lines)
        self.assertIn("| A* (h_P) | 2/3 | 2/2 | 2/2 | 100,0 % |", lines)
        # T5: A* ở G5 timeout -> không có trung vị; UCS ở G5 = 96
        self.assertIn("| G5 | 96 | — |", lines)
        # Phụ lục A: mọi dòng, nhóm gốc trước nhóm tự sinh
        appendix = lines[lines.index("**Phụ lục A. Kết quả đầy đủ.**"):]
        self.assertEqual(sum(1 for line in appendix if line.startswith("| original/") or line.startswith("| gen/")), 13)
        self.assertLess(text.index("| original/08 |"), text.index("| gen/S3-010 |"))
        self.assertNotIn("Cảnh báo", text)   # một commit, không -dirty, biết chế độ chi phí
        self.assertIn("Chế độ chi phí: `energy`", text)

    def test_unknown_cost_mode_is_warned(self):
        (self.tmp / "run_info.json").unlink()
        self.assertEqual(tables.main(["--summary", str(self.summary), "--out", str(self.out)]), 0)
        self.assertIn("không rõ chế độ chi phí", self.out.read_text(encoding="utf-8"))

    def test_cost_optimality_is_compared_relatively(self):
        rows = small_rows()
        rows[0]["path_cost"], rows[2]["path_cost"] = 35287.0, 35287.00001   # BFS, UCS màn 01: lệch tương đối 3e-10
        text = tables.build([tables.read_summary(self._write(rows))][0], "x", "energy")
        self.assertIn("| BFS | 3/3 | 3/3 | 3/3 | 100,0 % |", text.splitlines())

    def _write(self, rows):
        write_summary(self.summary, rows)
        return self.summary

    def test_refuses_to_overwrite_and_warns_on_dirty(self):
        self.out.write_text("cũ", encoding="utf-8")
        self.assertEqual(tables.main(["--summary", str(self.summary), "--out", str(self.out)]), 2)
        self.assertEqual(self.out.read_text(encoding="utf-8"), "cũ")
        rows = small_rows()
        rows[0]["commit"] = "abc1234-dirty"
        write_summary(self.summary, rows)
        self.assertEqual(tables.main(["--summary", str(self.summary), "--out", str(self.out), "--force"]), 0)
        self.assertIn("Cảnh báo", self.out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
