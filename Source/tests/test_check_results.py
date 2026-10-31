"""Kiểm tra experiments/check_results.py (docs/04 §6) bằng các dòng summary tổng hợp, không phải số liệu thật."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.check_results import check, cost_mode, level_pars, load, main, original_stems, run_info_for
from experiments.run import SUMMARY_COLUMNS


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
                row("original/01", "astar_m", steps=7, cost=7, expanded=20)] + [
            row("gen/S3-010", a, status="no_solution", group="S3") for a in ("bfs", "dfs", "ucs", "astar", "astar_m")]

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

    def test_k8_missing_rows_and_unsolved_original_levels(self):
        rows = self.good()
        del rows[4]                                            # original/01 thiếu astar_m
        v = check(rows, {"original/01": 7})
        self.assertEqual({c: x for c, x, _ in v}["K8"], "FAIL")
        self.assertIn("original/01: thiếu astar_m", dict((c, d) for c, _, d in v)["K8"])
        rows = self.good()
        rows[1].update(status="timeout", steps="", path_cost="")  # màn gốc nào cũng có lời giải
        self.assertEqual(verdicts(rows, {"original/01": 7})["K8"], "FAIL")

    def test_k8_requires_every_original_level_and_default_algorithm(self):
        self.assertEqual(verdicts(self.good(), {"original/01": 7})["K8"], "PASS")    # không truyền originals
        self.assertEqual({c: x for c, x, _ in check(self.good(), {"original/01": 7}, ["01"])}["K8"], "PASS")
        details = {c: (x, d) for c, x, d in check(self.good(), {"original/01": 7}, ["01", "02"])}
        self.assertEqual(details["K8"][0], "FAIL")
        self.assertIn("thiếu màn gốc 02", details["K8"][1])
        rows = [r for r in self.good() if r["algorithm"] != "astar_m"]                # cả file không có astar_m
        self.assertEqual(verdicts(rows, {"original/01": 7})["K8"], "PASS")
        self.assertEqual({c: x for c, x, _ in check(rows, {"original/01": 7}, ["01"])}["K8"], "FAIL")

    def test_par_and_original_levels_read_from_files_with_both_id_formats(self):
        root = Path(tempfile.mkdtemp(prefix="v24-check-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / "original").mkdir()
        (root / "gen").mkdir()
        (root / "original" / "01.json").write_text(json.dumps({"par": 7}), encoding="utf-8")
        (root / "gen" / "S1-010.json").write_text(json.dumps({"par": 12}), encoding="utf-8")
        rows = [row("original/01", "bfs"), row("01", "dfs"), row("gen/S1-010", "bfs"), row("S1-010", "dfs")]
        self.assertEqual(level_pars(rows, root), {"original/01": 7, "01": 7, "gen/S1-010": 12, "S1-010": 12})
        self.assertEqual(original_stems(root), ["01"])

    def test_path_cost_compared_relatively(self):
        """Chi phí V13 là số lẻ: lời giải rất dài (35 287 bước) lệch tuyệt đối 1e-5 nhưng tương đối 3e-10 do thứ tự
        cộng, không phải lỗi; lệch 0,01 thì là lỗi."""
        rows = self.good()
        for r in rows[:5]:
            r.update(path_cost="35287.0")
        rows[3].update(path_cost="35287.00001")   # A* (h_P)
        rows[0].update(path_cost="35286.99999")   # BFS rẻ hơn UCS một chút do thứ tự cộng
        v = verdicts(rows, {"original/01": 7})
        self.assertEqual((v["K4"], v["K5"]), ("PASS", "PASS"))
        rows[3].update(path_cost="35287.01")
        self.assertEqual(verdicts(rows, {"original/01": 7})["K4"], "FAIL")

    def test_missing_data_is_not_run_not_pass(self):
        rows = [row("original/01", "bfs", steps=7, cost=7, expanded=48)]
        v = verdicts(rows, {"original/01": 7})
        self.assertEqual(v["K2"], "PASS")
        for code in ("K3", "K4", "K5", "K6", "K7"):
            self.assertEqual(v[code], "NOT RUN", code)


class LoadTests(unittest.TestCase):
    """Dữ liệu hỏng phải dừng với thông báo rõ (exit 2), không để K2–K6 bỏ qua hoặc văng TypeError."""

    def write(self, rows):
        root = Path(tempfile.mkdtemp(prefix="v24-load-"))
        self.addCleanup(shutil.rmtree, root, True)
        path = root / "summary.csv"
        lines = [",".join(SUMMARY_COLUMNS)] + [",".join(r.get(c, "") for c in SUMMARY_COLUMNS) for r in rows]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def base(self):
        return [{"level": "original/01", "group": "G1", "algorithm": a, "status": "solved", "steps": "7",
                 "path_cost": "7", "expanded": "48"} for a in ("bfs", "dfs")]

    def test_bad_files_are_rejected_with_line_number(self):
        cases = {
            "dòng 3: dòng solved thiếu ['steps']": lambda r: r[1].update(steps=""),
            "dòng 3: cột expanded không phải số: 'abc'": lambda r: r[1].update(expanded="abc"),
            "dòng 4: trùng cặp màn/thuật toán": lambda r: r.append(dict(r[1])),   # dòng trùng nằm cuối file
        }
        for message, mutate in cases.items():
            with self.subTest(message):
                rows = self.base()
                mutate(rows)
                path = self.write(rows)
                with self.assertRaises(ValueError) as caught:
                    load(path)
                self.assertIn(message, str(caught.exception))
                self.assertEqual(main([str(path)]), 2)

    def test_cost_mode_read_from_run_info(self):
        path = self.write(self.base())
        self.assertIsNone(cost_mode(run_info_for(path)))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main([str(path)])
        self.assertIn("Chế độ chi phí: KHÔNG RÕ", out.getvalue())
        (path.parent / "run_info.json").write_text(json.dumps({"cost": "energy"}), encoding="utf-8")
        self.assertEqual(cost_mode(run_info_for(path)), "energy")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main([str(path)])
        self.assertIn("Chế độ chi phí: energy", out.getvalue())
        (path.parent / "run_info.json").write_text("{hỏng", encoding="utf-8")
        self.assertIsNone(run_info_for(path))

    def test_unsolved_rows_may_have_empty_numbers(self):
        rows = self.base()
        rows[1].update(status="timeout", steps="", path_cost="", expanded="")
        self.assertEqual(len(load(self.write(rows))), 2)


if __name__ == "__main__":
    unittest.main()
