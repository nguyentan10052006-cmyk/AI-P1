"""Bảng thực nghiệm (V25, TV2) từ summary.csv của experiments/run.py (docs/04 §7.1).

Cách chạy (trong Source/):
    python -m experiments.tables --summary experiments/summary.csv --out experiments/tables.md

Ghi một file Markdown gồm:
    T3  trung vị số nút mở rộng, thời gian tìm kiếm, bộ nhớ đỉnh theo nhóm G1–G5 × thuật toán
    T4  chất lượng lời giải trên 33 màn gốc: số màn giải được, tối ưu về số bước (so với BFS),
        tối ưu về chi phí (so với UCS), số bước trung bình so với tối ưu
    T5  trung vị số nút mở rộng của UCS, A* (h_M), A* (h_P) theo nhóm, kèm trung vị b*
    Phụ lục A  mọi dòng của summary.csv
Số viết theo quy ước của báo cáo: dấu phẩy thập phân, dấu cách phân nghìn. Trung vị chỉ tính trên các
dòng status = solved; ô ghi (n/m) khi chỉ n trong m màn của nhóm giải được. Không ghi đè file đã có,
trừ khi dùng --force. Đọc summary.csv bằng charts.read_summary (cùng cách kiểm tra cột và dòng trùng).
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from experiments.charts import ChartDataError, GROUPS, algorithms_in, label_of, read_summary
from experiments.check_results import cost_mode, run_info_for, same_cost

SOURCE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SUMMARY = SOURCE_DIR / "experiments" / "summary.csv"
DEFAULT_OUT = SOURCE_DIR / "experiments" / "tables.md"
GROUP_ORDER = GROUPS + ["S1", "S2", "S3"]
T3_METRICS = (("expanded", "số nút mở rộng", 0), ("search_ms", "thời gian tìm kiếm (ms)", 2),
              ("peak_mem_kb", "bộ nhớ đỉnh (KB)", 1))
T5_ALGORITHMS = ("ucs", "astar_m", "astar")
APPENDIX_COLUMNS = ("level", "group", "algorithm", "status", "steps", "path_cost", "expanded", "generated",
                    "max_frontier", "visited", "peak_mem_kb", "search_ms", "total_ms")


def fmt(value: Optional[float], digits: int = 0) -> str:
    """1234567.891 -> '1 234 567,89' (digits = 2); None -> '—'."""
    if value is None:
        return "—"
    text = f"{value:,.{digits}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", " ")


def effective_branching(generated: float, depth: int) -> Optional[float]:
    """b* là nghiệm của N + 1 = 1 + b + b² + … + b^d (04 §2, theo Russell và Norvig). None nếu d = 0."""
    if depth < 1 or generated is None:
        return None
    target = generated + 1

    def total(b: float) -> float:
        s, term = 0.0, 1.0
        for _ in range(depth + 1):
            s += term
            if s > target:
                break   # đủ để biết b quá lớn; tránh tràn số khi d lớn
            term *= b
        return s

    low, high = 0.0, max(1.0, target)
    for _ in range(200):
        mid = (low + high) / 2
        if total(mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _solved(rows: Sequence[Dict], algorithm: str, group: str) -> List[Dict]:
    return [r for r in rows if r["algorithm"] == algorithm and r["group"] == group and r["status"] == "solved"]


def _levels(rows: Sequence[Dict], group: str) -> int:
    return len({r["level"] for r in rows if r["group"] == group})


def _median_cell(values: List[float], total: int, digits: int) -> str:
    if not values:
        return "—"
    cell = fmt(statistics.median(values), digits)
    return cell if len(values) == total else f"{cell} ({len(values)}/{total})"


def table_t3(rows: Sequence[Dict], algorithms: Sequence[str]) -> List[str]:
    out = []
    for metric, title, digits in T3_METRICS:
        out += [f"**T3. Trung vị {title} theo nhóm.**", "",
                "| Nhóm | Số màn | " + " | ".join(label_of(a) for a in algorithms) + " |",
                "|---|---" + "|---" * len(algorithms) + "|"]
        for group in GROUPS:
            total = _levels(rows, group)
            if not total:
                continue
            cells = [_median_cell([r[metric] for r in _solved(rows, a, group) if r[metric] is not None], total, digits)
                     for a in algorithms]
            out.append(f"| {group} | {total} | " + " | ".join(cells) + " |")
        out.append("")
    return out


def table_t4(rows: Sequence[Dict], algorithms: Sequence[str]) -> List[str]:
    original = [r for r in rows if r["group"] in GROUPS]
    by = {(r["level"], r["algorithm"]): r for r in original}
    levels = sorted({r["level"] for r in original})
    out = ["**T4. Chất lượng lời giải trên các màn gốc.** Tối ưu về số bước: bằng số bước của BFS. "
           "Tối ưu về chi phí: bằng tổng chi phí của UCS.", "",
           "| Thuật toán | Giải được | Tối ưu về số bước | Tối ưu về chi phí | Số bước trung bình so với tối ưu |",
           "|---|---|---|---|---|"]
    for a in algorithms:
        solved = [lv for lv in levels if by.get((lv, a), {}).get("status") == "solved"]
        step_ok, cost_ok, ratios = 0, 0, []
        for lv in solved:
            row, bfs, ucs = by[(lv, a)], by.get((lv, "bfs")), by.get((lv, "ucs"))
            if bfs and bfs["status"] == "solved" and bfs["steps"]:
                step_ok += row["steps"] == bfs["steps"]
                ratios.append(row["steps"] / bfs["steps"])
            if ucs and ucs["status"] == "solved" and same_cost(row["path_cost"], ucs["path_cost"]):
                cost_ok += 1
        has_ucs = any(r["algorithm"] == "ucs" for r in original)
        mean = f"{fmt(100 * statistics.mean(ratios), 1)} %" if ratios else "—"
        out.append(f"| {label_of(a)} | {len(solved)}/{len(levels)} | {step_ok}/{len(solved)} | "
                   f"{f'{cost_ok}/{len(solved)}' if has_ucs else '—'} | {mean} |")
    out.append("")
    return out


def table_t5(rows: Sequence[Dict]) -> List[str]:
    algorithms = [a for a in T5_ALGORITHMS if any(r["algorithm"] == a for r in rows)]
    if not algorithms:
        return ["**T5.** Không có dòng UCS hoặc A* trong summary.csv.", ""]
    out = ["**T5. Trung vị số nút mở rộng của UCS và A* theo nhóm, và trung vị hệ số phân nhánh hiệu dụng b\\*.**", "",
           "| Nhóm | " + " | ".join(label_of(a) for a in algorithms) + " |",
           "|---" + "|---" * len(algorithms) + "|"]
    for group in GROUPS:
        total = _levels(rows, group)
        if total:
            out.append(f"| {group} | " + " | ".join(
                _median_cell([r["expanded"] for r in _solved(rows, a, group)], total, 0) for a in algorithms) + " |")
    stars = []
    for a in algorithms:
        values = [effective_branching(r["generated"], int(r["steps"])) for g in GROUPS for r in _solved(rows, a, g)]
        values = [v for v in values if v is not None]
        stars.append(fmt(statistics.median(values), 3) if values else "—")
    out += ["| b\\* (trung vị, màn gốc) | " + " | ".join(stars) + " |", ""]
    return out


def appendix_a(rows: Sequence[Dict], algorithms: Sequence[str]) -> List[str]:
    order = {g: i for i, g in enumerate(GROUP_ORDER)}
    ranked = sorted(rows, key=lambda r: (order.get(r["group"], len(order)), r["group"], r["level"],
                                         algorithms.index(r["algorithm"])))
    digits = {"path_cost": 2, "peak_mem_kb": 1, "search_ms": 2, "total_ms": 2}
    out = ["**Phụ lục A. Kết quả đầy đủ.**", "",
           "| " + " | ".join(APPENDIX_COLUMNS) + " |", "|" + "---|" * len(APPENDIX_COLUMNS)]
    for r in ranked:
        cells = []
        for c in APPENDIX_COLUMNS:
            value = r[c]
            if c == "algorithm":
                cells.append(label_of(value))
            elif isinstance(value, float) or value is None:
                cells.append(fmt(value, digits.get(c, 0)))
            else:
                cells.append(str(value))
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    return out


def build(rows: Sequence[Dict], source: str, cost: Optional[str] = None) -> str:
    """cost: chế độ chi phí của lần chạy (run_info.json); None là không rõ, đầu file sẽ có cảnh báo."""
    if not rows:
        raise ChartDataError("summary.csv không có dòng nào")
    algorithms = algorithms_in(rows)
    commits = sorted({r["commit"] for r in rows})
    header = [f"<!-- Sinh bằng experiments/tables.py từ {source}; không sửa tay. -->", "",
              f"Nguồn: `{source}`, commit {', '.join(f'`{c}`' for c in commits)}, {len(rows)} dòng.", "",
              f"Chế độ chi phí: `{cost}` (energy là hàm chi phí V13, unit là 1 mỗi bước)." if cost else
              "> **Cảnh báo:** không rõ chế độ chi phí (thiếu `run_info.json` cạnh summary.csv, hoặc run.py cũ chưa "
              "ghi khóa `cost`); cột chi phí và bảng T4, T5 không xác định được hàm chi phí.", ""]
    if len(commits) > 1 or any(c.endswith("-dirty") or not c for c in commits):
        header += ["> **Cảnh báo:** số liệu đến từ nhiều commit hoặc commit có thay đổi chưa lưu; "
                   "không dùng làm số liệu chính thức (04 §4).", ""]
    return "\n".join(header + table_t3(rows, algorithms) + table_t4(rows, algorithms) + table_t5(rows)
                     + appendix_a(rows, algorithms))


def main(argv: Optional[Sequence[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.csv của run.py")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="file Markdown ghi bảng")
    parser.add_argument("--force", action="store_true", help="ghi đè file đã có")
    args = parser.parse_args(argv)
    if args.out.exists() and not args.force:
        print(f"LỖI: không ghi đè {args.out} (dùng --force nếu chắc chắn)", file=sys.stderr)
        return 2
    try:
        text = build(read_summary(args.summary), args.summary.name, cost_mode(run_info_for(args.summary)))
    except (FileNotFoundError, ChartDataError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Đã ghi {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
