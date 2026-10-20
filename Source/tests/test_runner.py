"""Kiểm thử module chạy nền (solvers/runner.py) không cần GUI: poll không chặn, hết giờ, Hủy, So sánh.

Mỗi test mở tiến trình con thật (multiprocessing kiểu spawn), nên mất vài giây.
"""
import time
import unittest

from solvers.base import NO_SOLUTION, SOLVED
from solvers.runner import COMPARE_NAMES, SolveJob, run_solver, start_compare, start_solver
from tests import fakes
from tests.helpers import make_level
from bloxorz.problem import Problem

PROBLEM = Problem(make_level(["S##G"]))
FAKES = {"fake": fakes.FakeSolver, "empty": fakes.EmptySolver, "slow": fakes.SleepySolver,
         "crash": fakes.CrashingSolver}


def wait_for(job, limit_s=30.0):
    """Gọi SolveJob.poll() như vòng update() của GUI, cho tới khi có kết quả."""
    deadline = time.perf_counter() + limit_s
    while time.perf_counter() < deadline:
        result = job.poll()
        if result is not None:
            return result
        time.sleep(0.02)
    raise AssertionError("job không xong trong thời gian chờ")


class StartSolverTests(unittest.TestCase):
    def test_poll_returns_result_without_blocking(self):
        job = start_solver(fakes.FakeSolver, PROBLEM, timeout_s=20)
        started = time.perf_counter()
        job.poll()
        self.assertLess(time.perf_counter() - started, 0.2, "poll() không được chặn")
        result = wait_for(job)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], SOLVED)
        self.assertEqual(len(result["path"]), 2)
        for key in ("expanded", "generated", "max_frontier", "visited", "path_cost",
                    "prepare_ms", "time_ms", "peak_kb"):
            self.assertIn(key, result)
        self.assertTrue(job.done)
        self.assertIs(job.poll(), result, "poll() sau khi xong trả lại đúng kết quả cũ")

    def test_elapsed_counts_up_then_stops(self):
        job = start_solver(fakes.EmptySolver, PROBLEM, timeout_s=20)
        result = wait_for(job)
        self.assertEqual(result["status"], NO_SOLUTION)
        frozen = job.elapsed
        self.assertGreater(frozen, 0)
        time.sleep(0.05)
        self.assertEqual(job.elapsed, frozen)

    def test_timeout_stops_process(self):
        job = start_solver(fakes.SleepySolver, PROBLEM, timeout_s=2)
        result = wait_for(job)
        self.assertFalse(result["ok"])
        self.assertTrue(result["timeout"])
        self.assertGreaterEqual(job.elapsed, 2)
        self.assertLess(job.elapsed, 10)
        self.assertFalse(job._process.is_alive())

    def test_cancel_stops_process(self):
        job = start_solver(fakes.SleepySolver, PROBLEM, timeout_s=20)
        time.sleep(0.5)
        job.cancel()
        result = wait_for(job, limit_s=10)
        self.assertTrue(result["cancelled"])
        self.assertFalse(job._process.is_alive())

    def test_solver_error_is_reported(self):
        result = wait_for(start_solver(fakes.CrashingSolver, PROBLEM, timeout_s=20))
        self.assertEqual(result["error"], "RuntimeError: boom")

    def test_poll_before_start_is_an_error(self):
        with self.assertRaises(RuntimeError):
            SolveJob().poll()

    def test_run_solver_still_blocks_until_done(self):
        result = run_solver(fakes.FakeSolver, PROBLEM, timeout_s=20)
        self.assertEqual(result["status"], SOLVED)


class CompareTests(unittest.TestCase):
    def test_default_names_include_both_heuristics(self):
        self.assertEqual(COMPARE_NAMES, ("bfs", "dfs", "ucs", "astar", "astar_m"))

    def test_runs_each_solver_in_order(self):
        job = start_compare(PROBLEM, names=("fake", "empty", "crash"), timeout_s=20, algorithms=FAKES)
        self.assertEqual(job.running, "fake")
        seen = []
        deadline = time.perf_counter() + 60
        while not job.done and time.perf_counter() < deadline:
            partial = job.poll()
            seen.append(tuple(partial))
            time.sleep(0.02)
        results = job.poll()
        self.assertTrue(job.done)
        self.assertIsNone(job.running)
        self.assertEqual(list(results), ["fake", "empty", "crash"])
        self.assertEqual(results["fake"]["status"], SOLVED)
        self.assertEqual(results["empty"]["status"], NO_SOLUTION)
        self.assertIn("boom", results["crash"]["error"])
        # Kết quả hiện dần từng thuật toán, không phải đợi cả lượt
        self.assertIn(("fake",), seen)

    def test_one_timeout_does_not_stop_the_rest(self):
        job = start_compare(PROBLEM, names=("slow", "fake"), timeout_s=2, algorithms=FAKES)
        deadline = time.perf_counter() + 30
        while not job.done and time.perf_counter() < deadline:
            job.poll()
            time.sleep(0.02)
        results = job.poll()
        self.assertTrue(results["slow"]["timeout"])
        self.assertEqual(results["fake"]["status"], SOLVED)

    def test_cancel_marks_current_and_remaining(self):
        job = start_compare(PROBLEM, names=("slow", "fake"), timeout_s=20, algorithms=FAKES)
        time.sleep(0.5)
        job.cancel()
        results = job.poll()
        self.assertTrue(job.done)
        self.assertTrue(results["slow"]["cancelled"])
        self.assertTrue(results["fake"]["cancelled"])

    def test_unknown_name_is_rejected(self):
        with self.assertRaises(KeyError):
            start_compare(PROBLEM, names=("fake", "nope"), algorithms=FAKES)


if __name__ == "__main__":
    unittest.main()
