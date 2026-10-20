"""Vẽ các mê cung mẫu (bloxorz/maze.py, MAZES) ra SVG và một trang Markdown để cả nhóm xem.

Chạy trong Source/ mỗi khi sửa MAZES:
    python tools/draw_mazes.py            # ghi vào ../docs/gridmaze/
    python tools/draw_mazes.py OUT_DIR    # ghi vào thư mục khác

Chỉ dùng thư viện chuẩn. Không vẽ lời giải: đáp án chỉ ghi số bước và chi phí.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bloxorz.maze import MAZES, START, GOAL, WALL, MazeCase  # noqa: E402

CELL = 36      # cạnh một ô, tính bằng px
MARGIN = 26    # chỗ cho số hàng, số cột
COLORS = {
    "bg": "#ffffff",
    "label": "#6b7280",
    "grid": "#d1d5db",
    "wall": "#374151",
    "open": "#f9fafb",
    "start": "#16a34a",
    "goal": "#dc2626",
    "text_light": "#ffffff",
    "text_dark": "#111827",
}
# Ô chữ số: càng tốn càng đậm (1 nhạt, 9 đậm)
WEIGHT_FILLS = ["#fef3c7", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b",
                "#d97706", "#b45309", "#92400e", "#78350f"]


def cell_style(ch: str) -> Tuple[str, str, str]:
    """(màu nền, chữ hiện trong ô, màu chữ) của một ký tự trong lưới."""
    if ch == WALL:
        return COLORS["wall"], "", COLORS["text_light"]
    if ch == START:
        return COLORS["start"], "S", COLORS["text_light"]
    if ch == GOAL:
        return COLORS["goal"], "G", COLORS["text_light"]
    if ch.isdigit():
        weight = int(ch)
        text = COLORS["text_light"] if weight >= 6 else COLORS["text_dark"]
        return WEIGHT_FILLS[weight - 1], ch, text
    return COLORS["open"], "", COLORS["text_dark"]


def to_svg(case: MazeCase, title: str) -> str:
    rows, cols = len(case.grid), len(case.grid[0])
    width, height = MARGIN + cols * CELL + 2, MARGIN + rows * CELL + 2
    out: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, Menlo, monospace">',
        f"<title>GridMaze {title}</title>",
        f'<rect width="{width}" height="{height}" fill="{COLORS["bg"]}"/>',
    ]
    # Số cột ở trên, số hàng bên trái: tọa độ (hàng, cột) như trong code
    for c in range(cols):
        x = MARGIN + c * CELL + CELL / 2
        out.append(f'<text x="{x}" y="{MARGIN - 9}" font-size="12" fill="{COLORS["label"]}" '
                   f'text-anchor="middle">{c}</text>')
    for r in range(rows):
        y = MARGIN + r * CELL + CELL / 2 + 4
        out.append(f'<text x="{MARGIN - 8}" y="{y}" font-size="12" fill="{COLORS["label"]}" '
                   f'text-anchor="end">{r}</text>')
    for r, row in enumerate(case.grid):
        for c, ch in enumerate(row):
            fill, text, text_color = cell_style(ch)
            x, y = MARGIN + c * CELL, MARGIN + r * CELL
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{fill}" '
                       f'stroke="{COLORS["grid"]}" stroke-width="1"/>')
            if text:
                out.append(f'<text x="{x + CELL / 2}" y="{y + CELL / 2 + 6}" font-size="17" '
                           f'font-weight="bold" fill="{text_color}" text-anchor="middle">{text}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def answer(case: MazeCase) -> str:
    if case.steps is None:
        return "không có lời giải (`NO_SOLUTION`)"
    return f"ít nhất **{case.steps}** bước · chi phí nhỏ nhất **{case.cost:g}**"


def to_markdown(names: List[str]) -> str:
    lines = [
        "# Các mê cung mẫu của GridMaze",
        "",
        "Trang này do `Source/tools/draw_mazes.py` sinh ra từ `MAZES` trong "
        "[`Source/bloxorz/maze.py`](../../Source/bloxorz/maze.py). Đừng sửa tay: sửa `MAZES` rồi chạy lại "
        "`python tools/draw_mazes.py` trong `Source/`.",
        "",
        "Dùng để thử BFS, DFS, UCS, A* trước khi chạy Bloxorz (01 NV1, NV5–NV8). "
        "Kiểm tra tự động: `python -m unittest tests.test_solvers -v`. "
        "Xem nhanh trong terminal: `python -m bloxorz.maze`.",
        "",
        "**Chú giải:** ô xám đậm là tường; ô trắng đi vào tốn 1; "
        "**S** (xanh) là xuất phát, **G** (đỏ) là đích, đi vào cũng tốn 1; "
        "ô vàng có chữ số 1–9 đi vào tốn đúng số đó (càng đậm càng tốn). "
        "Số trên đầu là cột, số bên trái là hàng: tọa độ (hàng, cột) như trong code. "
        "Thứ tự hành động: U, D, L, R.",
        "",
    ]
    for name in names:
        case = MAZES[name]
        rows, cols = len(case.grid), len(case.grid[0])
        problem = case.problem()
        lines += [
            f"## `{name}`",
            "",
            f"![GridMaze {name}]({name}.svg)",
            "",
            f"- Kích thước {rows} × {cols}; xuất phát {problem.initial_state()}, đích {problem.goal}.",
            f"- Đáp án: {answer(case)}.",
            f"- {case.note}",
            "",
            "```text",
            *case.grid,
            "```",
            "",
        ]
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    out_dir = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[2] / "docs" / "gridmaze"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = list(MAZES)
    for name in names:
        (out_dir / f"{name}.svg").write_text(to_svg(MAZES[name], name), encoding="utf-8", newline="\n")
    (out_dir / "README.md").write_text(to_markdown(names), encoding="utf-8", newline="\n")
    print(f"Đã vẽ {len(names)} mê cung vào {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
