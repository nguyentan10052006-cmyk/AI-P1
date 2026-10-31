"""So hai lần chạy run.py để kiểm tra tái lập (TV2, V24).

Cách chạy (trong Source/):
    python -m experiments.compare_runs <summary.csv lần A> <summary.csv lần B>

Số đếm của thuật toán là tất định (cùng commit, cùng thứ tự hành động thì ra cùng số), nên phải TRÙNG HẲN:
    status, steps, path_cost, expanded, generated, max_frontier, visited
Thời gian và bộ nhớ đổi theo máy và lần chạy: chỉ báo tỉ lệ B / A (trung vị, nhỏ nhất, lớn nhất), không xét đạt.
Cặp (màn, thuật toán) có ở một bên mà không có ở bên kia cũng tính là lệch.
Hai lần chạy khác chế độ chi phí (cost trong run_info.json cạnh summary.csv: energy hay unit) không so được:
báo rõ và exit 1. Thiếu run_info.json thì chỉ cảnh báo và vẫn so.

Exit 0 nếu mọi số đếm trùng, 1 nếu có lệch, 2 nếu không đọc được file.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from experiments.check_results import cost_status, load

EXACT = ("status", "steps", "path_cost", "expanded", "generated", "max_frontier", "visited")
TIMING = ("search_ms", "total_ms", "peak_mem_kb")
PATH_COST_EPS = 1e-9


def _same(column: str, a: str, b: str) -> bool:
    if a == b:
        return True
    if column == "path_cost" and a and b:   # 7 và 7.0 là một
        return abs(float(a) - float(b)) < PATH_COST_EPS
    if a and b:
        try:
            return float(a) == float(b)
        except ValueError:
            return False
    return False


def compare(rows_a: Sequence[Dict[str, str]], rows_b: Sequence[Dict[str, str]]) -> Tuple[List[str], List[str]]:
    """(các dòng lệch, các dòng tóm tắt thời gian và bộ nhớ)."""
    a = {(r["level"], r["algorithm"]): r for r in rows_a}
    b = {(r["level"], r["algorithm"]): r for r in rows_b}
    diffs = [f"{lv}/{al}: chỉ có ở lần A" for lv, al in sorted(a.keys() - b.keys())]
    diffs += [f"{lv}/{al}: chỉ có ở lần B" for lv, al in sorted(b.keys() - a.keys())]
    ratios: Dict[str, List[float]] = {c: [] for c in TIMING}
    for key in sorted(a.keys() & b.keys()):
        ra, rb = a[key], b[key]
        for c in EXACT:
            if not _same(c, ra.get(c, ""), rb.get(c, "")):
                diffs.append(f"{key[0]}/{key[1]}: {c} {ra.get(c, '')!r} ≠ {rb.get(c, '')!r}")
        for c in TIMING:
            if ra.get(c) and rb.get(c) and float(ra[c]) > 0:
                ratios[c].append(float(rb[c]) / float(ra[c]))
    summary = []
    for c in TIMING:
        values = ratios[c]
        if values:
            summary.append(f"{c}: B/A trung vị {statistics.median(values):.2f}, nhỏ nhất {min(values):.2f}, "
                           f"lớn nhất {max(values):.2f} ({len(values)} cặp)")
        else:
            summary.append(f"{c}: không có cặp nào để so")
    return diffs, summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("a", type=Path, help="summary.csv lần A")
    parser.add_argument("b", type=Path, help="summary.csv lần B")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        rows_a, rows_b = load(args.a), load(args.b)
    except (OSError, ValueError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2
    (mode_a, why_a), (mode_b, why_b) = cost_status(args.a), cost_status(args.b)
    modes = mode_a, mode_b
    commits = sorted({r["commit"] for r in rows_a}), sorted({r["commit"] for r in rows_b})
    print(f"A: {args.a} ({len(rows_a)} dòng, commit {', '.join(commits[0])})")
    print(f"B: {args.b} ({len(rows_b)} dòng, commit {', '.join(commits[1])})")
    print(f"Chế độ chi phí: A {mode_a or 'không rõ (' + why_a + ')'}, B {mode_b or 'không rõ (' + why_b + ')'}")
    if modes[0] and modes[1] and modes[0] != modes[1]:
        print("KHÁC CHẾ ĐỘ CHI PHÍ: hai lần chạy dùng hàm chi phí khác nhau nên không tương đương; không so.")
        return 1
    if not (modes[0] and modes[1]):
        print("Lưu ý: không xác định được chế độ chi phí của cả hai lần chạy, nên không loại trừ được việc chúng khác "
              "hàm chi phí. Cột path_cost vẫn được so, nên khác hàm chi phí sẽ hiện thành lệch, không ra TRÙNG nhầm.")
    if commits[0] != commits[1]:
        print("Lưu ý: hai lần chạy khác commit; số đếm chỉ phải trùng nếu code solver và file màn không đổi.")
    diffs, summary = compare(rows_a, rows_b)
    for line in summary:
        print(line)
    if diffs:
        print(f"LỆCH {len(diffs)} chỗ ở số đếm:")
        for line in diffs[:50]:
            print(f"  {line}")
        if len(diffs) > 50:
            print(f"  … và {len(diffs) - 50} chỗ nữa")
        return 1
    print(f"TRÙNG: mọi số đếm của {len(rows_a)} cặp giống hệt nhau.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
