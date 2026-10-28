"""Kiểm tra chéo summary.csv trước khi dùng số liệu (docs/04 §6). TV2, V24.

Cách chạy (trong Source/):
    python -m experiments.check_results experiments/summary.csv

Mỗi kiểm tra ghi PASS, FAIL hoặc NOT RUN (thiếu dữ liệu để kiểm). Exit 1 nếu có FAIL.
Phát lại lời giải đã làm sẵn trong run.py: dòng nào phát lại sai đã có status = invalid.

    K1  không có dòng error hay invalid
    K2  steps của BFS = par của màn (màn có par > 0)
    K3  steps của DFS, UCS, A* (cả hai heuristic) không nhỏ hơn BFS
    K4  path_cost của UCS = A* (h_P) = A* (h_M), chênh nhỏ hơn 1e-9
    K5  path_cost của BFS và DFS không nhỏ hơn UCS
    K6  expanded của A* không lớn hơn UCS (cả hai heuristic)
    K7  màn S3 (không lời giải): BFS, DFS, UCS, A* đều no_solution; không thuật toán nào trả lời giải
Các kiểm tra cần hàm chi phí riêng hoặc heuristic (04 §6: "đặt mọi chi phí bằng 1", "0 vi phạm") nằm ở
test của UCS và tools/check_heuristics.py, không ở đây.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from experiments.run import SUMMARY_COLUMNS

SOURCE_DIR = Path(__file__).resolve().parent.parent
EPS = 1e-9


def load(summary: Path) -> List[Dict[str, str]]:
    with summary.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in SUMMARY_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{summary.name}: thiếu cột {missing}")
        return list(reader)


def level_pars(rows: List[Dict[str, str]], levels_root: Path) -> Dict[str, int]:
    """par của từng màn, đọc từ file màn theo mã (original/01 -> levels/original/01.json)."""
    pars = {}
    for level in {r["level"] for r in rows}:
        path = levels_root / f"{level}.json"
        if path.exists():
            pars[level] = json.loads(path.read_text(encoding="utf-8")).get("par", 0)
    return pars


def check(rows: List[Dict[str, str]], pars: Dict[str, int]) -> List[Tuple[str, str, str]]:
    """[(mã, kết quả, chi tiết)]."""
    by = {(r["level"], r["algorithm"]): r for r in rows}
    levels = sorted({r["level"] for r in rows})
    num = lambda r, k: float(r[k]) if r and r.get(k) not in (None, "") else None  # noqa: E731
    solved = lambda lv, a: by.get((lv, a)) if by.get((lv, a), {}).get("status") == "solved" else None  # noqa: E731
    results = []

    def record(code, failures, checked, what):
        if not checked:
            results.append((code, "NOT RUN", f"không có cặp nào để kiểm: {what}"))
        elif failures:
            results.append((code, "FAIL", f"{len(failures)}/{checked} lệch: " + "; ".join(failures[:8])))
        else:
            results.append((code, "PASS", f"{checked} cặp: {what}"))

    bad = [f"{r['level']}/{r['algorithm']}={r['status']}" for r in rows if r["status"] in ("error", "invalid")]
    results.append(("K1", "FAIL" if bad else "PASS", ("; ".join(bad[:8]) + f" (tổng {len(bad)})") if bad
                    else f"{len(rows)} dòng, không có error/invalid"))

    fails, n = [], 0
    for lv in levels:
        b = solved(lv, "bfs")
        if b and pars.get(lv, 0) > 0:
            n += 1
            if num(b, "steps") != pars[lv]:
                fails.append(f"{lv}: BFS {num(b, 'steps'):.0f} ≠ par {pars[lv]}")
    record("K2", fails, n, "BFS = par")

    fails, n = [], 0
    for lv in levels:
        b = solved(lv, "bfs")
        for a in ("dfs", "ucs", "astar", "astar_m"):
            o = solved(lv, a)
            if b and o:
                n += 1
                if num(o, "steps") < num(b, "steps"):
                    fails.append(f"{lv}: {a} {num(o, 'steps'):.0f} < BFS {num(b, 'steps'):.0f}")
    record("K3", fails, n, "steps ≥ BFS")

    fails, n = [], 0
    for lv in levels:
        u = solved(lv, "ucs")
        for a in ("astar", "astar_m"):
            o = solved(lv, a)
            if u and o:
                n += 1
                if abs(num(o, "path_cost") - num(u, "path_cost")) >= EPS:
                    fails.append(f"{lv}: {a} {num(o, 'path_cost')} ≠ UCS {num(u, 'path_cost')}")
    record("K4", fails, n, "path_cost A* = UCS")

    fails, n = [], 0
    for lv in levels:
        u = solved(lv, "ucs")
        for a in ("bfs", "dfs"):
            o = solved(lv, a)
            if u and o:
                n += 1
                if num(o, "path_cost") < num(u, "path_cost") - EPS:
                    fails.append(f"{lv}: {a} {num(o, 'path_cost')} < UCS {num(u, 'path_cost')}")
    record("K5", fails, n, "path_cost BFS, DFS ≥ UCS")

    fails, n = [], 0
    for lv in levels:
        u = solved(lv, "ucs")
        for a in ("astar", "astar_m"):
            o = solved(lv, a)
            if u and o:
                n += 1
                if num(o, "expanded") > num(u, "expanded"):
                    fails.append(f"{lv}: {a} {num(o, 'expanded'):.0f} > UCS {num(u, 'expanded'):.0f}")
    record("K6", fails, n, "expanded A* ≤ UCS")

    fails, n = [], 0
    for r in rows:
        if r["group"] == "S3":
            n += 1
            if r["status"] != "no_solution":
                fails.append(f"{r['level']}/{r['algorithm']}={r['status']}")
    record("K7", fails, n, "S3 đều no_solution")
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--levels-root", type=Path, default=SOURCE_DIR / "levels")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        rows = load(args.summary)
    except (OSError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2
    results = check(rows, level_pars(rows, args.levels_root))
    for code, verdict, detail in results:
        print(f"{code} {verdict:<7} {detail}")
    return 1 if any(v == "FAIL" for _, v, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
