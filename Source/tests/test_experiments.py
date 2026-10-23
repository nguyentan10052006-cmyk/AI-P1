"""Kiểm tra script đo thực nghiệm experiments/run.py (V23) bằng solver giả.

Mọi số liệu trong các test này là dữ liệu giả, sinh ra trong thư mục tạm; không phải kết quả thực nghiệm.
Mỗi lần chạy mở một tiến trình con (spawn), nên các test giữ repeat nhỏ.
"""
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments import run as exp

SOURCE_DIR = Path(__file__).resolve().parent.parent
TINY_LEVEL = {"name": "Thử S##G", "passcode": "012345", "group": "T", "grid": ["S##G"], "switches": []}


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def quiet(*_args, **_kwargs):
    pass


class ExperimentRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="v23-test-"))
        self.levels = self.tmp / "levels"
        self.levels.mkdir()
        (self.levels / "tiny.json").write_text(json.dumps(TINY_LEVEL), encoding="utf-8")
        self.out = self.tmp / "out"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_fake(self, solver, repeat=2, timeout=30.0, levels=None, out=None):
        exp.run_experiment(levels or [self.levels], [solver], out or self.out, repeat=repeat,
                           timeout_s=timeout, log=quiet)
        _, summary = read_csv((out or self.out) / "summary.csv")
        _, raw = read_csv((out or self.out) / "raw.csv")
        return summary, raw

    def test_solved_with_schema_and_metrics(self):
        summary, raw = self.run_fake("tests.fakes:FakeSolver", repeat=3)
        header, _ = read_csv(self.out / "summary.csv")
        self.assertEqual(header, exp.SUMMARY_COLUMNS)   # docs/04 §5, đúng thứ tự
        raw_header, _ = read_csv(self.out / "raw.csv")
        self.assertEqual(raw_header, exp.RAW_COLUMNS)
        self.assertEqual(len(summary), 1)
        row = summary[0]
        self.assertEqual((row["level"], row["passcode"], row["group"], row["algorithm"], row["heuristic"]),
                         ("tiny", "012345", "T", "tests.fakes:FakeSolver", ""))
        self.assertEqual(row["status"], "solved")
        self.assertEqual((row["steps"], row["path_cost"]), ("2", "2.0"))
        self.assertEqual([row[k] for k in exp.COUNTERS], ["3", "4", "2", "4"])
        self.assertGreaterEqual(float(row["total_ms"]), float(row["search_ms"]))
        self.assertGreaterEqual(float(row["peak_mem_kb"]), 0.0)
        self.assertRegex(row["search_ms"], r"^\d+\.\d{2}$")   # 2 chữ số thập phân (docs/04 §4)
        # 3 lần đo thời gian, rồi 1 lần đo bộ nhớ riêng
        self.assertEqual([(r["run"], r["kind"]) for r in raw], [("1", "time"), ("2", "time"), ("3", "time"),
                                                                ("4", "memory")])
        self.assertTrue(all(r["path"] == "R R" for r in raw))
        self.assertTrue(all(r["peak_mem_kb"] == "" for r in raw if r["kind"] == "time"))
        self.assertTrue(all(r["search_ms"] == "" for r in raw if r["kind"] == "memory"))
        info = json.loads((self.out / "run_info.json").read_text(encoding="utf-8"))
        self.assertEqual((info["repeat"], info["timeout_s"]), (3, 30.0))
        self.assertIn("python", info["machine"])

    def test_median_of_timed_runs(self):
        base = {"level": "x", "passcode": "", "group": "", "algorithm": "a", "heuristic": "", "commit": ""}
        timed = [{"status": "solved", "steps": 2, "path_cost": 2.0, "expanded": 1, "generated": 1,
                  "max_frontier": 1, "visited": 1, "search_ms": ms, "total_ms": ms + 1} for ms in (3.0, 1.0, 2.0)]
        warnings = []
        row = exp.summarize(base, timed, {"status": "solved", "peak_kb": 1.5}, warnings)
        self.assertEqual((row["search_ms"], row["total_ms"], row["peak_mem_kb"]), ("2.00", "3.00", "1.50"))
        self.assertEqual(warnings, [])

    def test_inconsistent_runs_are_flagged(self):
        base = {"level": "x", "passcode": "", "group": "", "algorithm": "a", "heuristic": "", "commit": ""}
        common = {"steps": None, "path_cost": None, "generated": 1, "max_frontier": 1, "visited": 1,
                  "search_ms": 1.0, "total_ms": 2.0}
        warnings = []
        row = exp.summarize(base, [{"status": "solved", "expanded": 1, **common},
                                   {"status": "no_solution", "expanded": 2, **common}], None, warnings)
        self.assertEqual(row["status"], "error")
        self.assertEqual(len(warnings), 2)   # status lẫn lộn và expanded khác nhau

    def test_no_solution(self):
        summary, _ = self.run_fake("tests.fakes:EmptySolver")
        row = summary[0]
        self.assertEqual(row["status"], "no_solution")
        self.assertEqual((row["steps"], row["path_cost"]), ("", ""))
        self.assertEqual(row["expanded"], "7")
        self.assertNotEqual(row["search_ms"], "")

    def test_invalid_path_and_wrong_cost(self):
        summary, raw = self.run_fake("tests.fakes:IllegalSolver")
        self.assertEqual(summary[0]["status"], "invalid")
        self.assertIn("làm khối rơi", raw[0]["error"])
        self.assertEqual(summary[0]["search_ms"], "")   # lời giải sai không đưa số đo vào bảng
        summary, raw = self.run_fake("tests.experiment_fakes:WrongCostSolver", out=self.tmp / "cost")
        self.assertEqual(summary[0]["status"], "invalid")
        self.assertIn("path_cost", raw[0]["error"])

    def test_timeout(self):
        summary, raw = self.run_fake("tests.fakes:SleepySolver", repeat=3, timeout=1.0)
        self.assertEqual(summary[0]["status"], "timeout")
        self.assertEqual(len(raw), 1)   # dừng sau lần hết giờ đầu tiên, không đo bộ nhớ
        self.assertEqual(summary[0]["search_ms"], "")

    def test_solver_errors(self):
        cases = {"tests.fakes:CrashingSolver": "boom", "tests.fakes:WrongReturnSolver": "SearchResult",
                 "tests.fakes:NotImplementedSolver": "NotImplementedError", "khong_co_thuat_toan": "KeyError"}
        for index, (spec, needle) in enumerate(cases.items()):
            with self.subTest(solver=spec):
                summary, raw = self.run_fake(spec, out=self.tmp / f"err{index}")
                self.assertEqual(summary[0]["status"], "error")
                self.assertIn(needle, raw[0]["error"])

    def test_bad_level_is_reported_and_others_still_run(self):
        (self.levels / "broken.json").write_text('{"grid": ["S#"]}', encoding="utf-8")   # thiếu ô đích
        summary, raw = self.run_fake("tests.fakes:FakeSolver", repeat=1)
        by_level = {r["level"]: r for r in summary}
        self.assertEqual(by_level["broken"]["status"], "error")
        self.assertIn("LevelError", [r for r in raw if r["level"] == "broken"][0]["error"])
        self.assertEqual(by_level["tiny"]["status"], "solved")

    def test_timing_runs_do_not_trace_memory(self):
        _, raw = self.run_fake("tests.experiment_fakes:TracingProbeSolver", repeat=2)
        self.assertEqual([(r["kind"], r["expanded"]) for r in raw], [("time", "0"), ("time", "0"), ("memory", "1")])

    def test_does_not_overwrite_existing_results(self):
        self.run_fake("tests.fakes:FakeSolver", repeat=1)
        before = {p.name: p.read_bytes() for p in self.out.iterdir()}
        with self.assertRaises(FileExistsError):
            exp.run_experiment([self.levels], ["tests.fakes:EmptySolver"], self.out, repeat=1, log=quiet)
        self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir()}, before)
        exp.run_experiment([self.levels], ["tests.fakes:EmptySolver"], self.out, repeat=1, force=True, log=quiet)
        _, summary = read_csv(self.out / "summary.csv")
        self.assertEqual(summary[0]["status"], "no_solution")
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ["raw.csv", "run_info.json", "summary.csv"])

    def test_commit_label_marks_uncommitted_code(self):
        repo = self.tmp / "repo"
        repo.mkdir()

        def git(*args):
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                           cwd=repo, check=True, capture_output=True)
        try:
            git("init", "-q")
            (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
            git("add", "a.py")
            git("commit", "-q", "-m", "init")
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("không có git để thử")
        self.assertNotIn("dirty", exp.git_commit(repo))
        (repo / "summary.csv").write_text("kết quả\n", encoding="utf-8")   # dữ liệu chưa theo dõi: không tính
        self.assertNotIn("dirty", exp.git_commit(repo))
        (repo / "b.py").write_text("y = 2\n", encoding="utf-8")            # code chưa theo dõi
        self.assertTrue(exp.git_commit(repo).endswith("-dirty"))
        (repo / "b.py").unlink()
        (repo / "a.py").write_text("x = 3\n", encoding="utf-8")            # code đã theo dõi bị sửa
        self.assertTrue(exp.git_commit(repo).endswith("-dirty"))

    def test_heuristic_column(self):
        self.assertEqual((exp.HEURISTIC["astar"], exp.HEURISTIC["astar_m"]), ("h_P", "h_M"))
        self.assertNotIn("bfs", exp.HEURISTIC)

    def test_real_dfs_on_level_1(self):
        """Tích hợp với solver thật: DFS màn 1 phải khớp test_dfs (37 bước, 63 nút mở rộng)."""
        summary, raw = self.run_fake("dfs", repeat=1, levels=[SOURCE_DIR / "levels" / "original" / "01.json"])
        row = summary[0]
        self.assertEqual((row["level"], row["passcode"], row["group"], row["status"]), ("01", "780464", "G1", "solved"))
        self.assertEqual((row["steps"], row["expanded"]), ("37", "63"))
        self.assertEqual(len(raw[0]["path"].split()), 37)

    def test_command_line(self):
        out = self.tmp / "cli"
        proc = subprocess.run([sys.executable, "-m", "experiments.run", "--levels", str(self.levels),
                               "--algorithms", "tests.fakes:FakeSolver", "--repeat", "1", "--out", str(out)],
                              cwd=SOURCE_DIR, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((out / "summary.csv").exists())
        again = subprocess.run([sys.executable, "-m", "experiments.run", "--levels", str(self.levels),
                                "--algorithms", "tests.fakes:FakeSolver", "--repeat", "1", "--out", str(out)],
                               cwd=SOURCE_DIR, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(again.returncode, 1)
        self.assertIn("không ghi đè", again.stderr)


if __name__ == "__main__":
    unittest.main()
