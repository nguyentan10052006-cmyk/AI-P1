"""Kiểm tra experiments/charts.py (V25) bằng DỮ LIỆU TỔNG HỢP trong thư mục tạm.

Số liệu ở đây chỉ để kiểm tra pipeline vẽ, không phải kết quả thực nghiệm. Bỏ qua nếu chưa cài matplotlib
(engine, solver và các test khác không cần matplotlib, docs/07 §2).
"""
import contextlib
import csv
import io
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

HAS_MPL = importlib.util.find_spec("matplotlib") is not None
if HAS_MPL:
    from experiments import charts
    from experiments.run import SUMMARY_COLUMNS


def synthetic_rows():
    rows = []
    algos = {"bfs": 1.0, "dfs": 0.8, "ucs": 1.1, "astar": 0.6, "astar_m": 0.7}
    for i, group in enumerate(["G1", "G1", "G2", "G3", "G4", "G5"], start=1):
        for algo, factor in algos.items():
            rows.append({"level": f"original/{i:02d}", "group": group, "algorithm": algo, "status": "solved",
                         "steps": 10 * i * (3 if algo == "dfs" else 1), "path_cost": 10 * i,
                         "expanded": int(50 * i ** 2 * factor), "visited": int(60 * i ** 2 * factor),
                         "peak_mem_kb": 5.0 * i, "search_ms": 0.5 * i})
    for n in (10, 50, 200):
        for algo in ("bfs", "dfs"):
            rows.append({"level": f"gen/S1-{n:03d}", "group": "S1", "algorithm": algo, "status": "solved",
                         "steps": n, "path_cost": n, "expanded": n * n, "visited": 3 * n * n})
    for k in (0, 2, 4):
        rows.append({"level": f"gen/S2-k{k:02d}", "group": "S2", "algorithm": "bfs", "status": "solved",
                     "steps": 13, "path_cost": 13, "expanded": 200 * 2 ** k, "visited": 260 * 2 ** k})
    rows.append({"level": "gen/S3-010", "group": "S3", "algorithm": "bfs", "status": "no_solution",
                 "expanded": 280, "visited": 280})
    rows.append({"level": "original/07", "group": "G5", "algorithm": "ucs", "status": "error"})   # bị bỏ qua
    return rows


def write_summary(path, rows, columns=None):
    columns = columns or SUMMARY_COLUMNS
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


@unittest.skipUnless(HAS_MPL, "chưa cài matplotlib")
class ChartsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="v25-test-"))
        self.summary = self.tmp / "summary.csv"
        self.out = self.tmp / "figures"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_full_data_draws_every_figure_with_data_table(self):
        write_summary(self.summary, synthetic_rows())
        report = charts.make_charts(self.summary, self.out)
        self.assertEqual(set(report), set(charts.FIGURES))
        for key, info in report.items():
            with self.subTest(figure=key):
                self.assertNotIn("skipped", info)
                png, data = Path(info["png"]), Path(info["csv"])
                self.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                with data.open(encoding="utf-8") as f:
                    self.assertGreater(len(list(csv.DictReader(f))), 0)

    def test_values_in_data_table_come_from_summary(self):
        write_summary(self.summary, synthetic_rows())
        charts.make_charts(self.summary, self.out, only=["H4", "H6"])
        with (self.out / "H4.csv").open(encoding="utf-8") as f:
            ratios = {r["level"]: float(r["ratio"]) for r in csv.DictReader(f)}
        self.assertEqual(set(ratios.values()), {3.0})            # DFS = 3 × BFS trong dữ liệu tổng hợp
        with (self.out / "H6.csv").open(encoding="utf-8") as f:
            g1_bfs = [r for r in csv.DictReader(f) if r["group"] == "G1" and r["algorithm"] == "bfs"]
        self.assertEqual(float(g1_bfs[0]["median_expanded"]), (50 + 200) / 2)   # trung vị màn 1 và 2
        self.assertFalse((self.out / "H1.png").exists())          # --only chỉ vẽ hình được chọn

    def test_single_algorithm_skips_comparisons(self):
        write_summary(self.summary, [r for r in synthetic_rows() if r["algorithm"] == "bfs"])
        report = charts.make_charts(self.summary, self.out)
        for key in ("H1", "H2", "H3", "H6", "H8", "H9"):
            self.assertNotIn("skipped", report[key], key)
        for key in ("H4", "H5"):                                  # cần DFS, UCS, A*: không có thì bỏ qua
            self.assertIn("skipped", report[key], key)

    def test_missing_data_is_skipped_not_invented(self):
        rows = [r for r in synthetic_rows() if r["group"] in ("G1", "G2")]
        for r in rows:
            r["peak_mem_kb"] = None
        write_summary(self.summary, rows)
        report = charts.make_charts(self.summary, self.out)
        for key in ("H3", "H8", "H9"):
            self.assertIn("skipped", report[key], key)
        self.assertFalse((self.out / "H3.png").exists())

    def test_format_errors_are_reported(self):
        write_summary(self.summary, synthetic_rows(), columns=SUMMARY_COLUMNS[:-1])   # thiếu cột commit
        with self.assertRaises(charts.ChartDataError):
            charts.make_charts(self.summary, self.out)
        rows = synthetic_rows()
        rows[0]["expanded"] = "nhiều"
        write_summary(self.summary, rows)
        with self.assertRaisesRegex(charts.ChartDataError, "dòng 2.*expanded"):
            charts.make_charts(self.summary, self.out)
        write_summary(self.summary, synthetic_rows() + synthetic_rows()[:1])
        with self.assertRaisesRegex(charts.ChartDataError, "trùng"):
            charts.make_charts(self.summary, self.out)
        with self.assertRaises(FileNotFoundError):
            charts.make_charts(self.tmp / "khong-co.csv", self.out)
        rows = synthetic_rows()
        rows[0]["steps"] = ""   # dòng solved mà thiếu số: file hỏng, không được lặng lẽ bỏ khỏi hình
        write_summary(self.summary, rows)
        with self.assertRaisesRegex(charts.ChartDataError, "dòng 2.*solved thiếu"):
            charts.make_charts(self.summary, self.out)

    def test_unsolved_pairs_are_listed(self):
        write_summary(self.summary, synthetic_rows())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(charts.main(["--summary", str(self.summary), "--out", str(self.out)]), 0)
        self.assertIn("Không vẽ 2 cặp không solved: gen/S3-010/bfs=no_solution, original/07/ucs=error", out.getvalue())

    def test_does_not_overwrite_and_colors_follow_algorithm(self):
        write_summary(self.summary, synthetic_rows())
        charts.make_charts(self.summary, self.out, only=["H1"])
        with self.assertRaises(FileExistsError):
            charts.make_charts(self.summary, self.out, only=["H1"])
        charts.make_charts(self.summary, self.out, only=["H1"], force=True)
        rows = synthetic_rows()
        only_dfs = [r for r in rows if r["algorithm"] == "dfs"]
        self.assertEqual(charts.color_of("dfs", rows), charts.color_of("dfs", only_dfs))   # không đổi màu theo tập


if __name__ == "__main__":
    unittest.main()
