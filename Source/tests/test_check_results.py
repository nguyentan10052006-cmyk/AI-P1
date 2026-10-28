"""Kiểm tra experiments/check_results.py (docs/04 §6) bằng các dòng summary tổng hợp, không phải số liệu thật."""
import unittest

from experiments.check_results import check


def row(level, algorithm, status="solved", steps="", cost="", expanded="", group="G1"):
    return {"level": level, "algorithm": algorithm, "status": status, "steps": str(steps), "path_cost": str(cost),
            "expanded": str(expanded), "group": group}


def verdicts(rows, pars):
    return {code: verdict for code, verdict, _ in check(rows, pars)}


class CheckResultsTests(unittest.TestCase):
    def good(self):
        return [row("original/01", "bfs", steps=7, cost=7, expanded=48),
                row("original/01", "dfs", steps=37, cost=37, expanded=63),
                row("original/01", "ucs", steps=7, cost=7, expanded=64),
                row("original/01", "astar", steps=7, cost=7, expanded=20),
                row("original/01", "astar_m", steps=7, cost=7, expanded=20),
                row("gen/S3-010", "bfs", status="no_solution", group="S3"),
                row("gen/S3-010", "dfs", status="no_solution", group="S3")]

    def test_all_pass_on_consistent_rows(self):
        self.assertEqual(set(verdicts(self.good(), {"original/01": 7}).values()), {"PASS"})

    def test_each_violation_is_caught(self):
        cases = {
            "K1": lambda r: r.append(row("original/02", "ucs", status="error")),
            "K2": lambda r: r[0].update(steps="8"),
            "K3": lambda r: r[1].update(steps="5"),
            "K4": lambda r: r[3].update(path_cost="8"),
            "K5": lambda r: r[1].update(path_cost="6"),
            "K6": lambda r: r[3].update(expanded="99"),
            "K7": lambda r: r[5].update(status="solved", steps="3", path_cost="3"),
        }
        for code, mutate in cases.items():
            with self.subTest(check=code):
                rows = self.good()
                mutate(rows)
                self.assertEqual(verdicts(rows, {"original/01": 7})[code], "FAIL")

    def test_missing_data_is_not_run_not_pass(self):
        rows = [row("original/01", "bfs", steps=7, cost=7, expanded=48)]
        v = verdicts(rows, {"original/01": 7})
        self.assertEqual(v["K2"], "PASS")
        for code in ("K3", "K4", "K5", "K6", "K7"):
            self.assertEqual(v[code], "NOT RUN", code)


if __name__ == "__main__":
    unittest.main()
