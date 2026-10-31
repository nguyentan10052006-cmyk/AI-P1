"""Kiểm tra h_M và h_P bằng số liệu (docs/01 NV8 bước 6, 7; V16, V17). Chạy trong Source/:

    python tools/check_heuristics.py                       # 33 màn gốc trong levels/original/
    python tools/check_heuristics.py levels levels/gen     # thư mục khác (có thể nhiều)
    python tools/check_heuristics.py --csv kq.csv          # ghi thêm bảng ra CSV
    python tools/check_heuristics.py --cost unit           # chi phí 1 mỗi bước, để đối chiếu với V13

Với mỗi màn và mỗi heuristic, đếm:
- vi phạm chấp nhận được: trạng thái trên một lời giải tối ưu có h(s) > chi phí thật còn lại;
- vi phạm nhất quán: cạnh (s, a, s') trong toàn bộ không gian trạng thái tới được có h(s) > c(s, a, s') + h(s');
- A* có cùng tổng chi phí với mốc so sánh không, và có mở rộng nhiều nút hơn mốc không.

Mốc so sánh là A* với h = 0 (chạy như UCS, cùng code A*), nên không phụ thuộc UCS của TV3. Nếu
solvers/ucs.py đã cài, công cụ so thêm tổng chi phí với UCS thật. Chi phí lấy từ problem.step_cost():
mặc định hàm chi phí V13 (bloxorz.costs.compute_step_cost) như GUI và experiments/run.py, --cost unit thì
1 mỗi bước. Có vi phạm hoặc lệch chi phí thì thoát với mã 1.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bloxorz.costs import compute_step_cost  # noqa: E402
from bloxorz.level import LevelError, load_level  # noqa: E402
from bloxorz.problem import Problem  # noqa: E402
from solvers import ALGORITHMS  # noqa: E402
from solvers.astar import AStar  # noqa: E402
from solvers.base import SOLVED, SearchResult  # noqa: E402
from solvers.heuristics import make_heuristic  # noqa: E402

HEURISTICS = {"manhattan": "h_M", "pattern": "h_P"}
EPS = 1e-9
COSTS = {"energy": compute_step_cost, "unit": None}   # cùng tên với --cost của experiments/run.py


def same_cost(a: float, b: float) -> bool:
    """Hai tổng chi phí bằng nhau. Chi phí V13 là số lẻ, cộng theo thứ tự khác nhau thì lệch ở chữ số cuối,
    nên so tương đối thay cho hiệu tuyệt đối."""
    return a == b or math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)


class _AStarZero(AStar):
    name = "A* (h = 0)"
    heuristic = "zero"


def run(solver: AStar, problem: Problem) -> SearchResult:
    solver.prepare(problem)
    return solver.search(problem)


def ucs_cost(problem: Problem) -> Optional[float]:
    """Tổng chi phí của UCS thật (TV3), hoặc None nếu UCS chưa cài."""
    try:
        result = run(ALGORITHMS["ucs"](), problem)
    except NotImplementedError:
        return None
    return result.path_cost if result.status == SOLVED else math.inf


def admissibility_violations(problem: Problem, h, path) -> int:
    """Dọc một lời giải tối ưu: h(s) không được lớn hơn chi phí thật còn lại từ s."""
    states, costs = [problem.initial_state()], []
    for action in path:
        nxt = problem.result(states[-1], action)
        costs.append(problem.step_cost(states[-1], action, nxt))
        states.append(nxt)
    remaining, violations = 0.0, 0
    for state, cost in zip(reversed(states), [0.0] + list(reversed(costs))):
        remaining += cost
        if h(state) > remaining + EPS:
            violations += 1
    return violations


def consistency_violations(problem: Problem, heuristics: Dict[str, object]) -> Dict[str, object]:
    """Duyệt toàn bộ không gian trạng thái tới được một lần, kiểm tra mọi cạnh với mọi heuristic."""
    start = problem.initial_state()
    seen, queue = {start}, deque([start])
    edges = 0
    violations = {name: 0 for name in heuristics}
    while queue:
        state = queue.popleft()
        if problem.is_goal(state):
            continue
        h_state = {name: h(state) for name, h in heuristics.items()}
        for action in problem.actions(state):
            child = problem.result(state, action)
            if child is None:
                continue
            edges += 1
            cost = problem.step_cost(state, action, child)
            for name, h in heuristics.items():
                # Từ s đã là ngõ cụt (h = vô cùng) thì s' cũng là ngõ cụt, không tính là vi phạm
                if h_state[name] != math.inf and h_state[name] > cost + h(child) + EPS:
                    violations[name] += 1
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return {"states": len(seen), "edges": edges, "violations": violations}


def check_level(path: Path, cost_fn=compute_step_cost) -> List[dict]:
    level = load_level(path, path.stem)
    problem = Problem(level, cost_fn=cost_fn)
    reference = run(_AStarZero(), problem)
    ref_cost = reference.path_cost if reference.status == SOLVED else math.inf
    real_ucs = ucs_cost(problem)
    heuristics = {name: make_heuristic(problem, name) for name in HEURISTICS}
    space = consistency_violations(problem, heuristics)

    rows = []
    for name, label in HEURISTICS.items():
        solver = AStar() if name == "pattern" else ALGORITHMS["astar_m"]()
        started = time.perf_counter()
        result = run(solver, problem)
        elapsed_ms = (time.perf_counter() - started) * 1000
        cost = result.path_cost if result.status == SOLVED else math.inf
        rows.append({
            "level": path.stem,
            "heuristic": label,
            "status": result.status,
            "steps": len(result.path),
            "cost": cost,
            "ref_cost": ref_cost,
            "ucs_cost": "" if real_ucs is None else real_ucs,
            "expanded": result.expanded,
            "ref_expanded": reference.expanded,
            "saved_pct": 100 * (1 - result.expanded / reference.expanded) if reference.expanded else 0.0,
            "h_start": heuristics[name](problem.initial_state()),
            "admissible_violations": admissibility_violations(problem, heuristics[name], reference.path)
            if reference.status == SOLVED else 0,
            "consistency_violations": space["violations"][name],
            "states": space["states"],
            "edges": space["edges"],
            "time_ms": elapsed_ms,
            "cost_ok": same_cost(cost, ref_cost),
            "ucs_ok": real_ucs is None or same_cost(cost, real_ucs),
            "not_more_nodes": result.expanded <= reference.expanded,
        })
    return rows


def main(argv: List[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dirs", nargs="*", default=["levels/original"], help="thư mục chứa file màn")
    parser.add_argument("--csv", help="ghi bảng kết quả ra file CSV")
    parser.add_argument("--cost", choices=COSTS, default="energy",
                        help="hàm chi phí: energy là V13 (mặc định), unit là 1 mỗi bước")
    args = parser.parse_args(argv[1:])

    rows, skipped = [], []
    for directory in args.dirs:
        for path in sorted(Path(directory).glob("*.json")):
            try:
                rows += check_level(path, COSTS[args.cost])
            except LevelError as exc:
                skipped.append(f"{path}: {exc}")

    header = (f"{'màn':>4} {'h':4} {'bước':>4} {'chi phí':>8} {'mốc':>8} {'UCS':>8} {'mở rộng':>8} "
              f"{'mốc mở':>8} {'bớt %':>6} {'h(đầu)':>6} {'VP chấp':>7} {'VP nhất':>7} {'cạnh':>7}")
    print(header)
    print("-" * len(header))
    for r in rows:
        ucs = "-" if r["ucs_cost"] == "" else f"{r['ucs_cost']:g}"
        print(f"{r['level']:>4} {r['heuristic']:4} {r['steps']:>4} {r['cost']:>8g} {r['ref_cost']:>8g} {ucs:>8} "
              f"{r['expanded']:>8} {r['ref_expanded']:>8} {r['saved_pct']:>6.1f} {r['h_start']:>6g} "
              f"{r['admissible_violations']:>7} {r['consistency_violations']:>7} {r['edges']:>7}")

    problems = [r for r in rows if r["admissible_violations"] or r["consistency_violations"]
                or not r["cost_ok"] or not r["ucs_ok"]]
    more_nodes = [r for r in rows if not r["not_more_nodes"]]
    print()
    print(f"Đã kiểm tra {len(rows) // len(HEURISTICS)} màn × {len(HEURISTICS)} heuristic.")
    print(f"Vi phạm chấp nhận được: {sum(r['admissible_violations'] for r in rows)}; "
          f"vi phạm nhất quán: {sum(r['consistency_violations'] for r in rows)} "
          f"(trên {sum(r['edges'] for r in rows) // len(HEURISTICS)} cạnh).")
    print(f"Lệch chi phí so với mốc hoặc UCS: {sum(1 for r in rows if not r['cost_ok'] or not r['ucs_ok'])}.")
    if more_nodes:
        print("Mở rộng nhiều nút hơn mốc (do cách phá hòa, không phải lỗi): "
              + ", ".join(f"{r['level']} {r['heuristic']}" for r in more_nodes))
    if rows and all(r["ucs_cost"] == "" for r in rows):
        print("UCS (solvers/ucs.py) chưa cài: mới so với mốc A* với h = 0.")
    for line in skipped:
        print("Bỏ qua", line)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Đã ghi {args.csv}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
