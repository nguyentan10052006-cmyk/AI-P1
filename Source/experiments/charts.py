"""Vẽ biểu đồ thực nghiệm (V25, TV2) từ summary.csv của experiments/run.py (docs/04 §7.2).

Cách chạy (trong Source/):
    python -m experiments.charts --summary experiments/summary.csv --out experiments/figures

Mỗi hình là một file PNG (matplotlib, backend Agg) kèm một file CSV cùng tên chứa đúng số liệu đã vẽ, để
đọc được khi màu khó phân biệt (in đen trắng, mù màu) và để truy lại số liệu. Không ghi đè file đã có,
trừ khi dùng --force.

    H1  số nút mở rộng theo màn gốc (log nếu lớn nhất gấp > 100 lần nhỏ nhất)
    H2  thời gian tìm kiếm (ms) theo màn gốc
    H3  bộ nhớ đỉnh (KB) theo màn gốc
    H4  số bước DFS / số bước BFS theo màn gốc
    H5  số nút A* / số nút UCS theo màn gốc, với h_M và h_P
    H6  trung vị số nút mở rộng theo nhóm G1–G5
    H8  số nút mở rộng theo kích thước sân N (nhóm S1)
    H9  số trạng thái đã thăm theo số công tắc k (nhóm S2), kèm đường visited(k=0) × 2^k để so

Chỉ dùng các dòng status = solved. Hình nào không đủ dữ liệu thì bỏ qua và nêu lý do; không vẽ từ số
liệu thay thế. Màu cố định theo thuật toán trong mọi hình (palette mặc định, đã chạy validator).
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from experiments.check_results import NUMERIC, REQUIRED_WHEN_SOLVED, cost_line, cost_status  # noqa: E402
from experiments.run import SUMMARY_COLUMNS  # noqa: E402

SOURCE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SUMMARY = SOURCE_DIR / "experiments" / "summary.csv"
DEFAULT_OUT = SOURCE_DIR / "experiments" / "figures"

# Thứ tự cố định, không xoay vòng: thuật toán chính dùng ô 1–5; thuật toán khác (ví dụ solver thử) ô 6–8.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
ALGORITHM_ORDER = ["bfs", "dfs", "ucs", "astar", "astar_m"]
LABELS = {"bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "astar": "A* (h_P)", "astar_m": "A* (h_M)"}
# Mã hóa phụ ngoài màu (in đen trắng, mù màu, hai đường trùng nhau): ký hiệu điểm và kiểu nét riêng
LINE_STYLE = {"bfs": ("o", "-"), "dfs": ("s", "-"), "ucs": ("^", "-"), "astar": ("D", "--"), "astar_m": ("v", ":")}
GROUPS = ["G1", "G2", "G3", "G4", "G5"]
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


class ChartDataError(ValueError):
    """summary.csv thiếu cột, sai định dạng hoặc trùng dòng."""


def read_summary(path: Path) -> List[Dict]:
    """Đọc và kiểm tra summary.csv. Ô số rỗng thành None; ô số không đọc được thì báo lỗi kèm dòng."""
    if not path.exists():
        raise FileNotFoundError(f"không có file {path}")
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in SUMMARY_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ChartDataError(f"{path.name}: thiếu cột {missing}")
        rows, seen = [], set()
        for line, raw in enumerate(reader, start=2):
            row = dict(raw)
            for name in NUMERIC:
                value = (row.get(name) or "").strip()
                try:
                    row[name] = float(value) if value else None
                except ValueError:
                    raise ChartDataError(f"{path.name} dòng {line}: cột {name} không phải số: {value!r}") from None
            empty = [c for c in REQUIRED_WHEN_SOLVED if row[c] is None]
            if row["status"] == "solved" and empty:
                raise ChartDataError(f"{path.name} dòng {line}: dòng solved thiếu {empty}")
            key = (row["level"], row["algorithm"])
            if key in seen:
                raise ChartDataError(f"{path.name} dòng {line}: trùng cặp màn/thuật toán {key}")
            seen.add(key)
            rows.append(row)
    return rows


def algorithms_in(rows: Sequence[Dict]) -> List[str]:
    found = {r["algorithm"] for r in rows}
    known = [a for a in ALGORITHM_ORDER if a in found]
    others = sorted(found - set(ALGORITHM_ORDER))
    if len(known) + len(others) > len(PALETTE):
        raise ChartDataError(f"quá {len(PALETTE)} thuật toán; tách thành nhiều lần vẽ")
    return known + others


def color_of(algorithm: str, rows: Sequence[Dict]) -> str:
    """Màu theo thuật toán, không theo thứ hạng: thuật toán chính luôn cùng một ô màu."""
    if algorithm in ALGORITHM_ORDER:
        return PALETTE[ALGORITHM_ORDER.index(algorithm)]
    others = sorted({r["algorithm"] for r in rows} - set(ALGORITHM_ORDER))
    return PALETTE[len(ALGORITHM_ORDER) + others.index(algorithm)]


def label_of(algorithm: str) -> str:
    return LABELS.get(algorithm, algorithm)


def _style(ax, xlabel: str, ylabel: str, title: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=26)
    ax.set_xlabel(xlabel, color=INK_2)
    ax.set_ylabel(ylabel, color=INK_2)
    ax.tick_params(colors=INK_2, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def _width(bars: int) -> float:
    """Chiều rộng hình (inch) theo số cột, giới hạn 8–14 để vừa trang báo cáo."""
    return min(14.0, max(8.0, 2 + 0.07 * bars))


def _legend(ax, columns: int) -> None:
    """Chú giải đặt trên vùng vẽ, không đè lên dữ liệu."""
    legend = ax.legend(frameon=False, fontsize=8, ncol=columns, loc="lower left", bbox_to_anchor=(0, 1.0),
                       labelcolor=INK, borderaxespad=0.2)
    rows = -(-len(legend.get_texts()) // columns)
    ax.set_title(ax.get_title("left"), color=INK, fontsize=11, loc="left", pad=10 + 14 * rows)   # chừa chỗ cho chú giải


def _log_if_wide(ax, values: Sequence[float]) -> bool:
    positive = [v for v in values if v and v > 0]
    if positive and max(positive) / min(positive) > 100:
        ax.set_yscale("log")
        return True
    return False


def original_levels(rows: Sequence[Dict]) -> List[str]:
    """Màn gốc (nhóm G1–G5), xếp theo nhóm rồi theo mã."""
    levels = {r["level"]: r["group"] for r in rows if r["group"] in GROUPS}
    return sorted(levels, key=lambda lv: (GROUPS.index(levels[lv]), lv))


def short(level: str) -> str:
    return level.rsplit("/", 1)[-1]


# Chú thích góc dưới phải mỗi hình, đặt trong make_charts(): chế độ chi phí của lần chạy. Số nút, thời gian và bộ nhớ
# của UCS, A* phụ thuộc hàm chi phí, nên hình tách khỏi báo cáo vẫn phải cho biết vẽ theo chế độ nào.
_FOOTNOTE = ""


class Figure:
    """Một hình: PNG cộng CSV số liệu đã vẽ."""

    def __init__(self, key: str, title: str):
        self.key, self.title = key, title
        self.table: List[Dict] = []

    def save(self, fig, out_dir: Path) -> Tuple[Path, Path]:
        png, data = out_dir / f"{self.key}.png", out_dir / f"{self.key}.csv"
        if _FOOTNOTE:
            fig.text(0.995, 0.005, _FOOTNOTE, ha="right", va="bottom", fontsize=7, color=INK_2)
        fig.savefig(png, dpi=150, facecolor=SURFACE)
        plt.close(fig)
        columns = list(self.table[0]) if self.table else []
        with data.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(self.table)
        return png, data


def _grouped_bars(rows, metric: str, ylabel: str, key: str, title: str, out_dir: Path):
    solved = [r for r in rows if r["status"] == "solved" and r[metric] is not None]
    levels = original_levels(solved)
    algos = [a for a in algorithms_in(solved)]
    if not levels or not algos:
        return None, f"không có dòng solved có {metric} cho màn gốc"
    figure = Figure(key, title)
    width = 0.8 / len(algos)
    fig, ax = plt.subplots(figsize=(_width(len(levels) * len(algos)), 4.2), facecolor=SURFACE)
    values = []
    for i, algo in enumerate(algos):
        xs, ys = [], []
        for x, level in enumerate(levels):
            value = next((r[metric] for r in solved if r["level"] == level and r["algorithm"] == algo), None)
            if value is not None:
                xs.append(x + (i - (len(algos) - 1) / 2) * width)
                ys.append(value)
                figure.table.append({"level": level, "algorithm": algo, metric: value})
        values += ys
        ax.bar(xs, ys, width * 0.92, color=color_of(algo, rows), label=label_of(algo),
               edgecolor=SURFACE, linewidth=0.6)
    log = _log_if_wide(ax, values)
    ax.set_xticks(range(len(levels)), [short(lv) for lv in levels])
    _style(ax, "Màn (xếp theo nhóm G1–G5)", ylabel + (" (thang log)" if log else ""), title)
    if len(algos) > 1:
        _legend(ax, len(algos))
    fig.tight_layout()
    return figure.save(fig, out_dir), None


def h1(rows, out):
    return _grouped_bars(rows, "expanded", "Số nút mở rộng", "H1", "H1. Số nút mở rộng trên từng màn gốc", out)


def h2(rows, out):
    return _grouped_bars(rows, "search_ms", "Thời gian tìm kiếm (ms)", "H2", "H2. Thời gian tìm kiếm, trung vị", out)


def h3(rows, out):
    return _grouped_bars(rows, "peak_mem_kb", "Bộ nhớ đỉnh (KB)", "H3", "H3. Bộ nhớ đỉnh (tracemalloc)", out)


def _ratio_bars(rows, pairs, key, title, ylabel, out_dir, reference=1.0):
    """pairs: [(thuật toán tử, thuật toán mẫu, chỉ số)]; một cột cho mỗi cặp trên mỗi màn gốc."""
    solved = {(r["level"], r["algorithm"]): r for r in rows if r["status"] == "solved"}
    levels = [lv for lv in original_levels(rows)
              if any((lv, a) in solved and (lv, b) in solved for a, b, _ in pairs)]
    if not levels:
        return None, "không có màn nào có đủ cả hai thuật toán cần so"
    figure = Figure(key, title)
    width = 0.8 / len(pairs)
    fig, ax = plt.subplots(figsize=(_width(len(levels) * len(pairs)), 4.0), facecolor=SURFACE)
    for i, (num, den, metric) in enumerate(pairs):
        xs, ys = [], []
        for x, level in enumerate(levels):
            a, b = solved.get((level, num)), solved.get((level, den))
            if a and b and a[metric] is not None and b[metric]:
                ratio = a[metric] / b[metric]
                xs.append(x + (i - (len(pairs) - 1) / 2) * width)
                ys.append(ratio)
                figure.table.append({"level": level, "numerator": num, "denominator": den, "metric": metric,
                                     "ratio": round(ratio, 6)})
        ax.bar(xs, ys, width * 0.92, color=color_of(num, rows), label=f"{label_of(num)} / {label_of(den)}",
               edgecolor=SURFACE, linewidth=0.6)
    ax.axhline(reference, color=INK_2, linewidth=1, linestyle="--")
    ax.set_xticks(range(len(levels)), [short(lv) for lv in levels])
    _style(ax, "Màn (xếp theo nhóm G1–G5)", ylabel, title)
    if len(pairs) > 1:
        _legend(ax, len(pairs))
    fig.tight_layout()
    return figure.save(fig, out_dir), None


def h4(rows, out):
    return _ratio_bars(rows, [("dfs", "bfs", "steps")], "H4", "H4. Số bước DFS so với tối ưu (BFS)",
                       "Số bước DFS / số bước BFS", out)


def h5(rows, out):
    return _ratio_bars(rows, [("astar_m", "ucs", "expanded"), ("astar", "ucs", "expanded")], "H5",
                       "H5. Số nút A* so với UCS", "Số nút A* / số nút UCS", out)


def h6(rows, out):
    solved = [r for r in rows if r["status"] == "solved" and r["expanded"] is not None and r["group"] in GROUPS]
    groups = [g for g in GROUPS if any(r["group"] == g for r in solved)]
    algos = algorithms_in(solved)
    if not groups:
        return None, "không có dòng solved thuộc G1–G5"
    figure = Figure("H6", "H6. Trung vị số nút mở rộng theo nhóm màn")
    width = 0.8 / len(algos)
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=SURFACE)
    values = []
    for i, algo in enumerate(algos):
        xs, ys = [], []
        for x, group in enumerate(groups):
            data = [r["expanded"] for r in solved if r["group"] == group and r["algorithm"] == algo]
            if data:
                median = statistics.median(data)
                xs.append(x + (i - (len(algos) - 1) / 2) * width)
                ys.append(median)
                figure.table.append({"group": group, "algorithm": algo, "levels": len(data),
                                     "median_expanded": median})
        values += ys
        ax.bar(xs, ys, width * 0.92, color=color_of(algo, rows), label=label_of(algo), edgecolor=SURFACE,
               linewidth=0.6)
    log = _log_if_wide(ax, values)
    ax.set_xticks(range(len(groups)), groups)
    _style(ax, "Nhóm màn", "Trung vị số nút mở rộng" + (" (thang log)" if log else ""), figure.title)
    if len(algos) > 1:
        _legend(ax, len(algos))
    fig.tight_layout()
    return figure.save(fig, out), None


# Tham số N (S1) và k (S2) đọc từ tên màn; nhận cả S1-010, S2-k04 (bản tạm của TV2) và s1_010, s2_04 (TV3, V40)
S1_NAME = r"(?i)^s1[-_](\d+)$"
S2_NAME = r"(?i)^s2[-_]k?(\d+)$"


def _param(level: str, pattern: str) -> Optional[int]:
    match = re.search(pattern, short(level))
    return int(match.group(1)) if match else None


def _lines(rows, group, pattern, metric, key, title, xlabel, ylabel, out_dir, reference=False):
    solved = [r for r in rows if r["status"] == "solved" and r["group"] == group and r[metric] is not None
              and _param(r["level"], pattern) is not None]
    if not solved:
        return None, f"không có dòng solved thuộc {group}"
    figure = Figure(key, title)
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=SURFACE)
    for algo in algorithms_in(solved):
        points = sorted((_param(r["level"], pattern), r[metric]) for r in solved if r["algorithm"] == algo)
        marker, dash = LINE_STYLE.get(algo, ("o", "-"))
        ax.plot([p for p, _ in points], [v for _, v in points], color=color_of(algo, rows), linewidth=2,
                linestyle=dash, marker=marker, markersize=6, markeredgecolor=SURFACE, label=label_of(algo))
        for p, v in points:
            figure.table.append({"param": p, "algorithm": algo, metric: v})
    if reference:
        # Neo đường 2^k vào BFS ở k = 0 (BFS duyệt theo lớp, gần với cả không gian trạng thái nhất);
        # không có BFS thì lấy giá trị nhỏ nhất. Ghi tên thuật toán neo lên hình và điểm của đường vào CSV.
        base = [r for r in solved if _param(r["level"], pattern) == 0]
        ks = sorted({_param(r["level"], pattern) for r in solved})
        if base:
            anchor = next((r for r in base if r["algorithm"] == "bfs"), min(base, key=lambda r: r[metric]))
            name = f"{label_of(anchor['algorithm'])} ở k = 0 × 2^k"
            ax.plot(ks, [anchor[metric] * 2 ** k for k in ks], color=INK_2, linewidth=1, linestyle="--", label=name)
            for k in ks:
                figure.table.append({"param": k, "algorithm": name, metric: anchor[metric] * 2 ** k})
    ax.set_yscale("log")
    _style(ax, xlabel, ylabel + " (thang log)", title)
    _legend(ax, 3)
    fig.tight_layout()
    return figure.save(fig, out_dir), None


def h8(rows, out):
    return _lines(rows, "S1", S1_NAME, "expanded", "H8", "H8. Công tìm kiếm theo kích thước sân (S1)",
                  "Kích thước sân N (N × N)", "Số nút mở rộng", out)


def h9(rows, out):
    return _lines(rows, "S2", S2_NAME, "visited", "H9", "H9. Trạng thái cầu làm tăng số trạng thái (S2)",
                  "Số công tắc–cầu k", "Số trạng thái đã thăm", out, reference=True)


FIGURES = {"H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "H6": h6, "H8": h8, "H9": h9}


def make_charts(summary: Path, out_dir: Path, force: bool = False, only: Sequence[str] = ()) -> Dict[str, Dict]:
    """Vẽ các hình; trả về {mã hình: {'png', 'csv'} hoặc {'skipped': lý do}}.

    Mỗi hình có chú thích chế độ chi phí đọc từ run_info.json cạnh summary.csv ("không rõ" nếu không đọc được)."""
    global _FOOTNOTE
    rows = read_summary(summary)
    keys = list(only) or list(FIGURES)
    unknown = [k for k in keys if k not in FIGURES]
    if unknown:
        raise ChartDataError(f"không có hình {unknown}; chọn trong {list(FIGURES)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = [str(out_dir / f"{k}.{ext}") for k in keys for ext in ("png", "csv") if (out_dir / f"{k}.{ext}").exists()]
    if existing and not force:
        raise FileExistsError("không ghi đè hình đã có (dùng --force nếu chắc chắn): " + ", ".join(existing))
    report: Dict[str, Dict] = {}
    mode, _ = cost_status(summary)
    _FOOTNOTE = f"Chế độ chi phí: {mode or 'không rõ'} · {summary.name}"
    try:
        for key in keys:
            saved, reason = FIGURES[key](rows, out_dir)
            report[key] = {"png": str(saved[0]), "csv": str(saved[1])} if saved else {"skipped": reason}
    finally:
        _FOOTNOTE = ""
    return report


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--only", default="", help="chỉ vẽ các hình này, ví dụ H1,H6")
    parser.add_argument("--force", action="store_true", help="ghi đè hình đã có")
    args = parser.parse_args(argv)
    only = [k.strip() for k in args.only.split(",") if k.strip()]
    try:
        report = make_charts(args.summary, args.out, args.force, only)
    except (FileNotFoundError, FileExistsError, ChartDataError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    print(cost_line(args.summary))
    for key, info in report.items():
        print(f"{key}: {info.get('png') or 'bỏ qua — ' + info['skipped']}")
    excluded = [f"{r['level']}/{r['algorithm']}={r['status']}" for r in read_summary(args.summary)
                if r["status"] != "solved"]
    if excluded:   # các cặp này không có trên hình; nêu ra để không ai tưởng hình đủ mọi cặp
        print(f"Không vẽ {len(excluded)} cặp không solved: {', '.join(excluded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
