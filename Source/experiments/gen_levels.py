"""Sinh bộ màn tự sinh S1–S3 cho thực nghiệm (TV3, việc V40, docs/01 NV10 và docs/04 §8).

3 nhóm màn chơi phục vụ đánh giá thực nghiệm:
1. Nhóm S1 (Sân trống lớn): Bàn N x N toàn sàn; S tại góc trên trái (0, 0), G tại góc dưới phải (N-1, N-1).
   Tham số N in {10, 25, 50, 100, 150, 200}. Đánh giá độ co giãn (scalability).
2. Nhóm S2 (Cầu & công tắc): Bàn 8 x 12 cố định, rải k công tắc mềm; mỗi công tắc đảo một ô cầu ở mép bàn.
   Tham số k in {0, 2, 4, 6, 8, 10}. Đánh giá sự bùng nổ tổ hợp trạng thái cầu 2^k.
3. Nhóm S3 (Không lời giải): Hai vùng sàn ngăn bởi một cột ô trống rộng 1 ô; S ở vùng trái, G ở vùng phải.
   Tham số kích thước vùng trái 10 x 10 và 50 x 50. Đánh giá chi phí tìm kiếm vét cạn (exhaustive search).

Cách chạy:
    python -m experiments.gen_levels                 # Sinh 14 màn vào Source/levels/gen/
    python -m experiments.gen_levels --out <dir>     # Chỉ định thư mục lưu
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from bloxorz.level import parse_level
from bloxorz.problem import Problem
from solvers.base import NO_SOLUTION, SOLVED
from solvers.bfs import BFS

DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "levels" / "gen"

S1_SIZES = (10, 25, 50, 100, 150, 200)
S2_COUNTS = (0, 2, 4, 6, 8, 10)
S3_SIZES = (10, 50)


def generate_s1(n: int) -> Dict[str, Any]:
    """Sinh màn S1: sân trống N x N toàn sàn."""
    grid = [list("#" * n) for _ in range(n)]
    grid[0][0] = "S"
    grid[n - 1][n - 1] = "G"
    return {
        "name": f"S1 Sân trống {n}x{n}",
        "passcode": "000000",
        "group": "S1",
        "source": "tự sinh bằng gen_levels.py",
        "par": 0,
        "grid": ["".join(row) for row in grid],
        "switches": [],
    }


def generate_s2(k: int) -> Dict[str, Any]:
    """Sinh màn S2: sân 8 x 12 cố định với k công tắc cầu ở mép sân."""
    rows, cols = 8, 12
    grid = [list("#" * cols) for _ in range(rows)]

    # Hàng 0 là mép biên ngoài: đặt ô trống '.', chỉ đặt ô cầu 'b' tại các cột có công tắc
    for c in range(cols):
        grid[0][c] = "."

    grid[3][1] = "S"
    grid[3][10] = "G"

    switches: List[Dict[str, Any]] = []
    # Rải tối đa 10 công tắc tại hàng 1 (cột 1 đến 10), mỗi công tắc nối cầu ở hàng 0
    for i in range(k):
        col = i + 1
        grid[0][col] = "b"  # cầu đóng lúc đầu
        grid[1][col] = "o"  # công tắc mềm
        switches.append({
            "at": [1, col],
            "bridges": [[0, col]],
            "effect": "toggle",
        })

    return {
        "name": f"S2 Cầu k={k}",
        "passcode": "000000",
        "group": "S2",
        "source": "tự sinh bằng gen_levels.py",
        "par": 0,
        "grid": ["".join(row) for row in grid],
        "switches": switches,
    }


def generate_s3(w: int) -> Dict[str, Any]:
    """Sinh màn S3: vùng trái w x w ngăn cách với vùng phải bằng khe rộng 1 ô trống."""
    h = w
    right_cols = 3  # vùng phải nhỏ chứa đích G
    total_cols = w + 1 + right_cols

    grid = []
    for r in range(h):
        row = list("#" * w + "." + "#" * right_cols)
        grid.append(row)

    grid[1][1] = "S"
    grid[1][w + 2] = "G"

    return {
        "name": f"S3 Không lời giải {w}x{w}",
        "passcode": "000000",
        "group": "S3",
        "source": "tự sinh bằng gen_levels.py",
        "par": 0,
        "grid": ["".join(row) for row in grid],
        "switches": [],
    }


def build_all_levels() -> Dict[str, Dict[str, Any]]:
    """Tạo dữ liệu cho toàn bộ 14 màn chơi tự sinh."""
    levels: Dict[str, Dict[str, Any]] = {}

    for n in S1_SIZES:
        level_id = f"s1_{n:03d}"
        levels[level_id] = generate_s1(n)

    for k in S2_COUNTS:
        level_id = f"s2_{k:02d}"
        levels[level_id] = generate_s2(k)

    for w in S3_SIZES:
        level_id = f"s3_{w:02d}"
        levels[level_id] = generate_s3(w)

    return levels


def validate_and_save(out_dir: Path, log: bool = True) -> Dict[str, Dict[str, Any]]:
    """Tạo màn, dùng BFS kiểm tra tính giải được, tính par và ghi ra đĩa."""
    out_dir.mkdir(parents=True, exist_ok=True)
    levels = build_all_levels()
    bfs = BFS()

    if log:
        print(f"Đang sinh và kiểm định {len(levels)} màn tự sinh vào {out_dir}...")

    for level_id, data in sorted(levels.items()):
        # Nạp thử nghiệm bằng engine
        parsed = parse_level(data, level_id)
        res = bfs.search(Problem(parsed))

        group = data["group"]
        if group in ("S1", "S2"):
            if res.status != SOLVED:
                raise RuntimeError(f"Màn {level_id} ({group}) phải giải được, nhưng BFS trả {res.status}")
            data["par"] = len(res.path)
            if log:
                print(f"  [OK] {level_id:<7} ({group}): giải được sau {data['par']} bước (expanded={res.expanded})")
        else:  # S3
            if res.status != NO_SOLUTION:
                raise RuntimeError(f"Màn {level_id} ({group}) phải vô nghiệm, nhưng BFS trả {res.status}")
            data["par"] = 0
            if log:
                print(f"  [OK] {level_id:<7} ({group}): vô nghiệm đúng như kỳ vọng (visited={res.visited})")

        # Ghi file JSON tất định
        file_path = out_dir / f"{level_id}.json"
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        file_path.write_text(text, encoding="utf-8")

    if log:
        print(f"Đã hoàn thành sinh và xác thực {len(levels)} màn chơi tự sinh.")

    return levels


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Sinh bộ màn chơi tự sinh S1-S3 cho thực nghiệm (V40)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR, help="Thư mục xuất file JSON")
    args = parser.parse_args()
    validate_and_save(args.out)


if __name__ == "__main__":
    main()
