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
    K8  đủ dòng (01 NV10 "Xong khi"): mỗi màn có dòng của mọi thuật toán có trong file; đủ các màn trong
        levels/original và đủ 5 thuật toán mặc định của run.py; mọi dòng của màn gốc (G1–G5, màn nào
        cũng có lời giải) đều solved
Mã màn đọc được cả dạng run.py hiện tại (original/01) lẫn dạng cũ (01).
In chế độ chi phí (cost: energy là V13, unit là 1 mỗi bước) đọc từ run_info.json nằm cạnh summary.csv;
so path_cost tương đối (math.isclose), vì chi phí V13 là số lẻ.
Các kiểm tra cần hàm chi phí riêng hoặc heuristic (04 §6: "đặt mọi chi phí bằng 1", "0 vi phạm") nằm ở
test của UCS và tools/check_heuristics.py, không ở đây.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from experiments.run import DEFAULT_ALGORITHMS, SUMMARY_COLUMNS

SOURCE_DIR = Path(__file__).resolve().parent.parent
EPS = 1e-9
GROUPS = ("G1", "G2", "G3", "G4", "G5")   # màn gốc; S1–S3 là màn tự sinh
NUMERIC = ("steps", "path_cost", "expanded", "generated", "max_frontier", "visited", "peak_mem_kb",
           "search_ms", "total_ms")
# run.py luôn ghi các cột này cho dòng solved; thiếu nghĩa là file hỏng, các kiểm tra K2–K6 sẽ so sai
REQUIRED_WHEN_SOLVED = ("steps", "path_cost", "expanded")


def load(summary: Path) -> List[Dict[str, str]]:
    """Đọc summary.csv; dữ liệu hỏng thì báo ValueError kèm số dòng, không để kiểm tra nào bỏ qua nó."""
    with summary.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in SUMMARY_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{summary.name}: thiếu cột {missing}")
        rows, seen = [], set()
        for line, row in enumerate(reader, start=2):
            for name in NUMERIC:
                value = (row.get(name) or "").strip()
                try:
                    float(value) if value else None
                except ValueError:
                    raise ValueError(f"{summary.name} dòng {line}: cột {name} không phải số: {value!r}") from None
            if row["status"] == "solved":
                empty = [c for c in REQUIRED_WHEN_SOLVED if not (row.get(c) or "").strip()]
                if empty:
                    raise ValueError(f"{summary.name} dòng {line}: dòng solved thiếu {empty}")
            key = (row["level"], row["algorithm"])
            if key in seen:
                raise ValueError(f"{summary.name} dòng {line}: trùng cặp màn/thuật toán {key}")
            seen.add(key)
            rows.append(row)
        return rows


KNOWN_COSTS = ("energy", "unit")   # giá trị --cost của run.py: energy là V13 (bloxorz/costs.py), unit là 1 mỗi bước


def run_info_for(summary: Path) -> Optional[Dict[str, Any]]:
    """run_info.json cùng thư mục với summary.csv (run.py ghi cả hai), hoặc None nếu không có hay hỏng."""
    path = summary.parent / "run_info.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def cost_mode(info: Optional[Dict[str, Any]]) -> Optional[str]:
    """Chế độ chi phí ("energy", "unit") ghi trong run_info; None nếu không có, hoặc là giá trị lạ (không đoán)."""
    mode = info.get("cost") if isinstance(info, dict) else None
    return mode if mode in KNOWN_COSTS else None


def cost_status(summary: Path) -> Tuple[Optional[str], str]:
    """(chế độ chi phí, lý do khi không xác định được). Lý do nêu rõ trường hợp nào, để người dùng biết cách sửa."""
    path = summary.parent / "run_info.json"
    if not path.exists():
        return None, f"không có {path.name} cạnh {summary.name}"
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.name} không đọc được ({type(exc).__name__}: {exc})"
    if not isinstance(info, dict) or "cost" not in info:
        return None, f"{path.name} không có khóa cost, tức run.py trước khi nối V13"
    if info["cost"] not in KNOWN_COSTS:
        return None, f"{path.name} có cost = {info['cost']!r}, không thuộc {KNOWN_COSTS}"
    return info["cost"], ""


def cost_line(summary: Path) -> str:
    mode, why = cost_status(summary)
    return f"Chế độ chi phí: {mode}" if mode else f"Chế độ chi phí: KHÔNG RÕ ({why})"


def same_cost(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=EPS, abs_tol=EPS)


def level_pars(rows: List[Dict[str, str]], levels_root: Path) -> Dict[str, int]:
    """par của từng màn, đọc từ file màn theo mã: original/01 -> levels/original/01.json; mã cũ (01, S1-010)
    thì tìm trong levels/original/ rồi levels/gen/."""
    pars = {}
    for level in {r["level"] for r in rows}:
        for path in (levels_root / f"{level}.json", levels_root / "original" / f"{level}.json",
                     levels_root / "gen" / f"{level}.json"):
            if path.exists():
                pars[level] = json.loads(path.read_text(encoding="utf-8")).get("par", 0)
                break
    return pars


def original_stems(levels_root: Path) -> List[str]:
    """Tên các file màn gốc (01 … 33), để K8 biết màn nào phải có trong summary."""
    return sorted(p.stem for p in (levels_root / "original").glob("*.json"))


def check(rows: List[Dict[str, str]], pars: Dict[str, int],
          originals: Optional[Sequence[str]] = None) -> List[Tuple[str, str, str]]:
    """[(mã, kết quả, chi tiết)]. originals: tên file màn gốc phải có; khi có thì K8 cũng đòi đủ 5 thuật toán
    mặc định của run.py. None thì K8 chỉ kiểm các màn và thuật toán có trong file."""
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
                if not same_cost(num(o, "path_cost"), num(u, "path_cost")):
                    fails.append(f"{lv}: {a} {num(o, 'path_cost')} ≠ UCS {num(u, 'path_cost')}")
    record("K4", fails, n, "path_cost A* = UCS")

    fails, n = [], 0
    for lv in levels:
        u = solved(lv, "ucs")
        for a in ("bfs", "dfs"):
            o = solved(lv, a)
            if u and o:
                n += 1
                cost_o, cost_u = num(o, "path_cost"), num(u, "path_cost")
                if cost_o < cost_u and not same_cost(cost_o, cost_u):
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

    algorithms = sorted({r["algorithm"] for r in rows} | (set(DEFAULT_ALGORITHMS) if originals is not None else set()))
    present = set(levels)
    absent = [stem for stem in (originals or ()) if f"original/{stem}" not in present and stem not in present]
    fails = [f"{lv}: thiếu {a}" for lv in levels for a in algorithms if (lv, a) not in by]
    fails += [f"thiếu màn gốc {stem} (cả {len(algorithms)} thuật toán)" for stem in absent]
    fails += [f"{r['level']}/{r['algorithm']}={r['status']}" for r in rows
              if r["group"] in GROUPS and r["status"] != "solved"]
    expected = (len(levels) + len(absent)) * len(algorithms)   # số cặp (màn, thuật toán) phải có
    record("K8", fails, expected, f"{len(levels)} màn × {len(algorithms)} thuật toán, màn gốc đều solved")
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
    print(cost_line(args.summary))
    results = check(rows, level_pars(rows, args.levels_root), original_stems(args.levels_root))
    for code, verdict, detail in results:
        print(f"{code} {verdict:<7} {detail}")
    return 1 if any(v == "FAIL" for _, v, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
