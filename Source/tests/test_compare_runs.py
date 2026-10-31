"""Kiểm tra experiments/compare_runs.py bằng các dòng summary tổng hợp, không phải số liệu thật."""
import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.compare_runs import compare, main
from experiments.run import SUMMARY_COLUMNS


def rows(search_ms="1.00"):
    return [{"level": "original/01", "group": "G1", "algorithm": a, "status": "solved", "steps": s,
             "path_cost": s, "expanded": e, "generated": "130", "max_frontier": "21", "visited": "65",
             "search_ms": search_ms, "total_ms": "2.00", "peak_mem_kb": "28.1", "commit": "abc1234"}
            for a, s, e in (("bfs", "7", "48"), ("dfs", "37", "63"))]


class CompareRunsTests(unittest.TestCase):
    def write(self, name, data):
        path = self.tmp / name
        lines = [",".join(SUMMARY_COLUMNS)] + [",".join(r.get(c, "") for c in SUMMARY_COLUMNS) for r in data]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="v24-compare-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_main(self, a, b):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(self.write("a.csv", a)), str(self.write("b.csv", b))])
        return code, out.getvalue()

    def test_same_counts_pass_and_times_are_only_reported(self):
        b = rows(search_ms="1.50")
        b[0]["path_cost"] = "7.0"   # cùng giá trị, khác cách viết
        code, out = self.run_main(rows(), b)
        self.assertEqual(code, 0)
        self.assertIn("search_ms: B/A trung vị 1.50", out)
        self.assertIn("TRÙNG: mọi số đếm của 2 cặp", out)

    def test_count_difference_and_missing_pair_fail(self):
        b = rows()
        b[1]["expanded"] = "64"
        diffs, _ = compare(rows(), b)
        self.assertEqual(diffs, ["original/01/dfs: expanded '63' ≠ '64'"])
        diffs, _ = compare(rows(), rows()[:1])
        self.assertEqual(diffs, ["original/01/dfs: chỉ có ở lần A"])
        code, out = self.run_main(rows(), b)
        self.assertEqual(code, 1)
        self.assertIn("LỆCH 1 chỗ", out)

    def test_different_cost_modes_are_not_compared(self):
        (self.tmp / "a").mkdir(); (self.tmp / "b").mkdir()
        for name, mode in (("a", "energy"), ("b", "unit")):
            (self.tmp / name / "run_info.json").write_text(f'{{"cost": "{mode}"}}', encoding="utf-8")
        a, b = self.write("a/summary.csv", rows()), self.write("b/summary.csv", rows())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(a), str(b)])
        self.assertEqual(code, 1)
        self.assertIn("KHÁC CHẾ ĐỘ CHI PHÍ", out.getvalue())

    def test_strange_cost_value_is_reported_with_reason(self):
        (self.tmp / "a").mkdir()
        (self.tmp / "a" / "run_info.json").write_text('{"cost": "free"}', encoding="utf-8")
        a, b = self.write("a/summary.csv", rows()), self.write("b.csv", rows())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(a), str(b)])
        self.assertEqual(code, 0)   # số đếm vẫn so được; path_cost giống nhau nên TRÙNG
        self.assertIn("A không rõ (run_info.json có cost = 'free'", out.getvalue())
        self.assertIn("không loại trừ được việc chúng khác hàm chi phí", out.getvalue())

    def test_unknown_cost_mode_is_noted(self):
        code, out = self.run_main(rows(), rows())
        self.assertEqual(code, 0)
        self.assertIn("không xác định được chế độ chi phí", out)

    def test_status_difference_fails(self):
        b = rows()
        b[1].update(status="timeout", steps="", path_cost="", expanded="")
        diffs, _ = compare(rows(), b)
        self.assertIn("original/01/dfs: status 'solved' ≠ 'timeout'", diffs)


if __name__ == "__main__":
    unittest.main()
