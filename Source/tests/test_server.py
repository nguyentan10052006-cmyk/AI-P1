"""Kiểm thử API và server HTTP. Solver dùng là solver giả trong tests/fakes.py."""
import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from bloxorz.serialize import state_to_dict
from server import api
from server.app import make_server
from solvers.runner import SolveJob
from tests import fakes
from tests.helpers import make_level

LEVEL = make_level(["S##G"], level_id="t1")
LEVELS = {"t1": LEVEL}
START = state_to_dict(LEVEL.initial_state())


def right():
    return {"dir": "right", "cube": None}


class ApiStepTests(unittest.TestCase):
    def test_step_then_win(self):
        code, first = api.step_level(LEVELS, {"level": "t1", "state": START, "action": right()})
        self.assertEqual(code, 200)
        self.assertEqual(first["status"], "ok")
        self.assertEqual(first["state"]["orient"], "horizontal")
        code, second = api.step_level(LEVELS, {"level": "t1", "state": first["state"], "action": right()})
        self.assertEqual(second["status"], "won")
        self.assertEqual(second["events"][-1], {"type": "won"})

    def test_bad_requests_return_400(self):
        self.assertEqual(api.step_level(LEVELS, {"level": "nope", "state": START, "action": right()})[0], 400)
        bad_action = {"level": "t1", "state": START, "action": {"dir": "sideways"}}
        self.assertEqual(api.step_level(LEVELS, bad_action)[0], 400)
        self.assertEqual(api.step_level(LEVELS, ["not", "a", "dict"])[0], 400)

    def test_level_listing_and_detail(self):
        code, listing = api.list_levels(LEVELS)
        self.assertEqual(listing["levels"][0]["id"], "t1")
        code, detail = api.get_level(LEVELS, "t1")
        self.assertEqual(code, 200)
        self.assertEqual(detail["start"]["pos"], [0, 0])
        self.assertEqual(api.get_level(LEVELS, "zzz")[0], 404)


class ApiSolveTests(unittest.TestCase):
    def solve(self, algorithms, timeout_s=20.0, name="fake"):
        body = {"level": "t1", "state": START, "algorithm": name}
        return api.solve_level(LEVELS, body, algorithms=algorithms, timeout_s=timeout_s)

    def test_valid_solution_is_replayed(self):
        code, data = self.solve({"fake": fakes.FakeSolver})
        self.assertEqual(code, 200)
        self.assertTrue(data["found"])
        self.assertEqual(data["stats"]["length"], 2)
        self.assertAlmostEqual(data["stats"]["cost"], 1.12 + 1.62)   # V13: đứng -> nằm -> đứng
        self.assertEqual(data["steps"][-1]["status"], "won")
        self.assertIn("time_ms", data["stats"])
        self.assertIn("prepare_ms", data["stats"])
        self.assertIn("peak_kb", data["stats"])
        for key, value in {"expanded": 3, "generated": 4, "max_frontier": 2, "visited": 4}.items():
            self.assertEqual(data["stats"][key], value)

    def test_no_solution(self):
        code, data = self.solve({"fake": fakes.EmptySolver})
        self.assertFalse(data["found"])
        self.assertEqual(data["stats"]["expanded"], 7)
        self.assertEqual(data["stats"]["generated"], 9)

    def test_wrong_return_type_is_reported(self):
        code, data = self.solve({"fake": fakes.WrongReturnSolver})
        self.assertIn("SearchResult", data["error"])

    def test_illegal_solution_is_reported(self):
        code, data = self.solve({"fake": fakes.IllegalSolver})
        self.assertIn("làm khối rơi", data["error"])

    def test_solver_exception_is_reported(self):
        code, data = self.solve({"fake": fakes.CrashingSolver})
        self.assertEqual(data["error"], "RuntimeError: boom")

    def test_not_implemented_is_reported(self):
        code, data = self.solve({"fake": fakes.NotImplementedSolver})
        self.assertIn("chưa được cài đặt", data["error"])

    def test_timeout_stops_solver(self):
        code, data = self.solve({"fake": fakes.SleepySolver}, timeout_s=3)
        self.assertIn("Quá 3 giây", data["error"])
        self.assertTrue(data["timeout"])

    def test_unknown_algorithm_is_400(self):
        code, _ = self.solve({"fake": fakes.FakeSolver}, name="xyz")
        self.assertEqual(code, 400)


    def test_cancel_stops_running_solver(self):
        job = SolveJob()
        result = {}
        body = {"level": "t1", "state": START, "algorithm": "slow"}
        worker = threading.Thread(target=lambda: result.update(api.solve_level(
            LEVELS, body, algorithms={"slow": fakes.SleepySolver}, timeout_s=20, job=job)[1]))
        worker.start()
        time.sleep(1.0)
        job.cancel()
        worker.join(timeout=15)
        self.assertFalse(worker.is_alive())
        self.assertTrue(result["cancelled"])


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        Path(cls._tmp.name, "index.html").write_text("<!doctype html><p>ok</p>", encoding="utf-8")
        cls.server = make_server(LEVELS, Path(cls._tmp.name), port=0, timeout_s=20,
                                 algorithms={"fake": fakes.FakeSolver})
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls._tmp.cleanup()

    def get(self, path):
        with urllib.request.urlopen(self.base + path) as res:
            return res.status, res.read()

    def post(self, path, body):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read())

    def test_static_index_is_served(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"ok", body)

    def test_api_levels_over_http(self):
        status, body = self.get("/api/levels")
        self.assertEqual(json.loads(body)["levels"][0]["id"], "t1")

    def test_step_and_solve_over_http(self):
        status, data = self.post("/api/step", {"level": "t1", "state": START, "action": right()})
        self.assertEqual(data["status"], "ok")
        status, data = self.post("/api/solve", {"level": "t1", "state": START, "algorithm": "fake"})
        self.assertTrue(data["found"])

    def test_bad_json_is_400(self):
        req = urllib.request.Request(self.base + "/api/step", data=b"{not json", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
