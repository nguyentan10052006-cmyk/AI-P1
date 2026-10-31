"""Kiểm tra độc lập một lần đo: phát lại lời giải, tính lại trung vị bảng T3, đối chiếu CSV của hình với summary.csv.

Chạy: python -I verify_benchmark.py <Source của commit đo> <thư mục kết quả>
Không dùng tables.py hay charts.py để tính; chỉ đọc file chúng sinh ra để so.
"""
import csv
import math
import re
import statistics
import sys
from pathlib import Path

source, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(source))
from bloxorz.costs import compute_step_cost  # noqa: E402
from bloxorz.level import load_level  # noqa: E402
from bloxorz.problem import Problem  # noqa: E402
from bloxorz.state import Action, Dir  # noqa: E402

LETTER = {"U": Dir.UP, "D": Dir.DOWN, "L": Dir.LEFT, "R": Dir.RIGHT}
summary = {(r["level"], r["algorithm"]): r for r in csv.DictReader((out / "summary.csv").open(encoding="utf-8"))}

# 1. Phát lại lời giải trong raw.csv (lần đo thời gian thứ nhất), so số bước và tổng chi phí với summary.csv
bad, replayed = [], 0
for r in csv.DictReader((out / "raw.csv").open(encoding="utf-8")):
    if r["kind"] != "time" or r["run"] != "1" or r["status"] != "solved":
        continue
    problem = Problem(load_level(source / "levels" / f"{r['level']}.json", r["level"]), cost_fn=compute_step_cost)
    state, cost = problem.initial_state(), 0.0
    for token in r["path"].split():
        action = Action(LETTER[token[0]], int(token[1:]) - 1 if len(token) > 1 else None)
        nxt = problem.result(state, action)
        if nxt is None:
            bad.append((r["level"], r["algorithm"], "rơi"))
            break
        cost += problem.step_cost(state, action, nxt)
        state = nxt
    else:
        s = summary[(r["level"], r["algorithm"])]
        if not problem.is_goal(state):
            bad.append((r["level"], r["algorithm"], "không tới đích"))
        elif int(s["steps"]) != len(r["path"].split()) or not math.isclose(cost, float(s["path_cost"]), rel_tol=1e-9, abs_tol=1e-9):
            bad.append((r["level"], r["algorithm"], cost, s["path_cost"]))
    replayed += 1
print(f"1. Phát lại {replayed} lời giải: lệch {len(bad)}", bad[:5])

# 2. Tính lại trung vị bảng T3 và so với tables.md
tables = (out / "tables.md").read_text(encoding="utf-8")
algos = ["bfs", "dfs", "ucs", "astar", "astar_m"]
mismatch = []
for metric, title, digits in (("expanded", "số nút mở rộng", 0), ("search_ms", "thời gian tìm kiếm (ms)", 2),
                              ("peak_mem_kb", "bộ nhớ đỉnh (KB)", 1)):
    block = tables.split(f"**T3. Trung vị {title} theo nhóm.**")[1].split("\n\n**")[0]
    for group in ("G1", "G2", "G3", "G4", "G5"):
        line = next(l for l in block.splitlines() if l.startswith(f"| {group} |"))
        cells = [c.strip() for c in line.strip("|").split("|")][2:]
        for algo, cell in zip(algos, cells):
            values = [float(r[metric]) for r in summary.values()
                      if r["group"] == group and r["algorithm"] == algo and r["status"] == "solved"]
            mine = round(statistics.median(values), digits)
            theirs = float(cell.split(" (")[0].replace(" ", "").replace(",", "."))
            if not math.isclose(mine, theirs, abs_tol=10 ** -digits / 2 + 1e-12):
                mismatch.append((metric, group, algo, mine, theirs))
print(f"2. Trung vị T3 tính lại (3 chỉ số × 5 nhóm × 5 thuật toán = 75 ô): lệch {len(mismatch)}", mismatch[:5])

# 3. CSV của từng hình so với summary.csv
LABEL = {"BFS": "bfs", "DFS": "dfs", "UCS": "ucs", "A* (h_P)": "astar", "A* (h_M)": "astar_m"}
fig_bad, fig_rows = [], 0
for key, metric in (("H1", "expanded"), ("H2", "search_ms"), ("H3", "peak_mem_kb")):
    for r in csv.DictReader((out / "figures" / f"{key}.csv").open(encoding="utf-8")):
        algo = LABEL.get(r["algorithm"], r["algorithm"])
        fig_rows += 1
        if float(r[metric]) != float(summary[(r["level"], algo)][metric]):
            fig_bad.append((key, r["level"], algo))
for key, group, metric, pattern in (("H8", "S1", "expanded", r"s1_(\d+)"), ("H9", "S2", "visited", r"s2_(\d+)")):
    for r in csv.DictReader((out / "figures" / f"{key}.csv").open(encoding="utf-8")):
        algo = LABEL.get(r["algorithm"], r["algorithm"])
        if algo not in algos:
            continue   # đường tham chiếu 2^k
        level = next(k[0] for k in summary if summary[k]["group"] == group
                     and int(re.search(pattern, k[0]).group(1)) == int(float(r["param"])))
        fig_rows += 1
        if float(r[metric]) != float(summary[(level, algo)][metric]):
            fig_bad.append((key, level, algo))
print(f"3. Giá trị trong CSV của H1, H2, H3, H8, H9 đối chiếu summary.csv: {fig_rows} giá trị, lệch {len(fig_bad)}", fig_bad[:5])
