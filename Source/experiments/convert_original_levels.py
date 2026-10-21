"""Chuyển 33 màn Bloxorz gốc từ bản port GBA sang định dạng file màn của nhóm (docs/03 mục 6).

Nguồn: game/levels.json của jacobcoughenour/bloxorz_gba, commit f57ebb6 (GPL-3.0).
Bản sao nằm ở experiments/data/bloxorz_gba/ để chạy lại không cần mạng.

Cách chạy (trong thư mục Source/):
    python -m experiments.convert_original_levels            # ghi file mới, bỏ qua file đã giống hệt
    python -m experiments.convert_original_levels --check    # chỉ kiểm tra, không ghi; lệch thì exit 1
    python -m experiments.convert_original_levels --force    # ghi đè file đã có nhưng khác nội dung

Mặc định không ghi đè file đã có. Chạy lại nhiều lần cho cùng kết quả (thứ tự khóa và định dạng cố định).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SOURCE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = SOURCE_DIR / "experiments" / "data" / "bloxorz_gba" / "levels.json"
DEFAULT_OUT = SOURCE_DIR / "levels" / "original"

SOURCE_REPO = "jacobcoughenour/bloxorz_gba"
SOURCE_COMMIT = "f57ebb6bd57e9d2b42ab478a3d19e53028e62b1d"
SOURCE_SHA256 = "f30ed31fd4259c336a7ecdd4870ab4f74b13c7c17055e9e6cc8a045eac6406fe"

ROWS, COLS = 10, 15
LEVEL_COUNT = 33

# Ký tự bản GBA -> ký tự của nhóm (docs/03 mục 6, bảng chuyển đổi).
TILE_MAP = {
    " ": ".",  # trống
    "b": "#",  # sàn
    "e": "G",  # đích
    "f": "F",  # ô dễ vỡ
    "s": "o",  # công tắc mềm
    "h": "x",  # công tắc nặng
    "v": "@",  # công tắc tách
    "l": "b",  # cầu, đóng lúc đầu (nửa trái của hình cây cầu)
    "r": "b",  # cầu, đóng lúc đầu (nửa phải)
    "k": "B",  # cầu, mở lúc đầu
    "q": "B",  # cầu, mở lúc đầu
}
MODE_MAP = {"onoff": "toggle", "on": "open", "off": "close"}
SWITCH_TILES = {"s", "h"}
SPLIT_TILE = "v"
BRIDGE_TILES = {"l", "r", "k", "q"}

# Nhóm độ khó (docs/03 mục 5).
GROUPS = {
    "G1": (1, 3, 6),
    "G2": (4, 13),
    "G3": (2, 5, 7, 11, 12, 14, 17, 18, 19, 21, 22, 25, 29, 32, 33),
    "G4": (27, 30, 31),
    "G5": (8, 9, 10, 15, 16, 20, 23, 24, 26, 28),
}
GROUP_OF = {n: g for g, levels in GROUPS.items() for n in levels}

# Số bước tối ưu tham khảo (docs/03 mục 4, cột "Bước tối ưu"). BFS của nhóm phải kiểm lại (test T24).
PAR = [7, 17, 19, 28, 33, 35, 44, 10, 24, 57, 47, 65, 46, 67, 57, 28, 106,
       85, 67, 56, 71, 65, 75, 57, 55, 104, 71, 100, 104, 114, 91, 129, 65]

# Hiệu chỉnh dữ liệu nguồn, có căn cứ (docs/03 mục 3). Mỗi mục: (hàng, cột) -> ký tự của nhóm.
# Chỉ áp dụng khi ô đó đang trống trong nguồn; nếu không thì báo lỗi để người chạy xem lại.
FIXES: Dict[int, Dict[Tuple[int, int], str]] = {
    3: {(6, 11): "#", (7, 12): "#", (7, 13): "#", (7, 14): "#"},
}
FIX_NOTES = {
    3: "bổ sung 4 ô sàn (6, 11), (7, 12), (7, 13), (7, 14) bị thiếu trong bản GBA (docs/03 mục 3)",
}


class ConvertError(ValueError):
    """Dữ liệu nguồn không chuyển được."""


def sha256_of(path: Path) -> str:
    """sha256 sau khi đổi CRLF thành LF: Git trên Windows (core.autocrlf) có thể đổi xuống dòng khi checkout."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_source(path: Path) -> List[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConvertError(f"không đọc được {path}: {exc}") from exc
    levels = data.get("levels") if isinstance(data, dict) else None
    if not isinstance(levels, list) or len(levels) != LEVEL_COUNT:
        raise ConvertError(f"{path}: cần danh sách 'levels' gồm đúng {LEVEL_COUNT} màn")
    return levels


def _key_to_cell(key: str, where: str) -> Tuple[int, int]:
    """Khóa công tắc của bản GBA là x * 10 + y, với x là cột và y là hàng."""
    try:
        k = int(key)
    except ValueError as exc:
        raise ConvertError(f"{where}: khóa công tắc {key!r} không phải số") from exc
    return (k % 10, k // 10)  # (hàng, cột)


def _xy(value: Any, where: str) -> Tuple[int, int]:
    """[x, y] của bản GBA -> (hàng, cột)."""
    if not (isinstance(value, (list, tuple)) and len(value) == 2 and all(isinstance(v, int) for v in value)):
        raise ConvertError(f"{where}: tọa độ không hợp lệ {value!r}")
    x, y = value
    return (y, x)


def convert_level(number: int, raw: Dict[str, Any]) -> Dict[str, Any]:
    """Chuyển một màn (đánh số từ 1 theo thứ tự trong levels.json) sang dict theo định dạng của nhóm."""
    where = f"màn {number} (id {raw.get('id')!r})"
    tiles = raw.get("tiles")
    if not isinstance(tiles, list) or len(tiles) != ROWS or any(
            not isinstance(row, str) or len(row) != COLS for row in tiles):
        raise ConvertError(f"{where}: 'tiles' phải là {ROWS} chuỗi, mỗi chuỗi {COLS} ký tự")
    unknown = {ch for row in tiles for ch in row} - set(TILE_MAP)
    if unknown:
        raise ConvertError(f"{where}: ký tự lạ {sorted(unknown)}")

    def src(cell):
        r, c = cell
        return tiles[r][c] if 0 <= r < ROWS and 0 <= c < COLS else None

    grid = [[TILE_MAP[ch] for ch in row] for row in tiles]

    start = _xy(raw.get("spawn"), f"{where}, spawn")
    if src(start) != "b":
        raise ConvertError(f"{where}: ô xuất phát {start} phải là sàn, nguồn ghi {src(start)!r}")
    grid[start[0]][start[1]] = "S"

    for cell, ch in FIXES.get(number, {}).items():
        if src(cell) != " ":
            raise ConvertError(f"{where}: hiệu chỉnh tại {cell} cần ô trống, nguồn ghi {src(cell)!r}")
        grid[cell[0]][cell[1]] = ch

    switches: List[Dict[str, Any]] = []
    configured = set()
    for key, links in (raw.get("switches") or {}).items():
        at = _key_to_cell(key, where)
        if src(at) not in SWITCH_TILES:
            raise ConvertError(f"{where}: công tắc khóa {key} trỏ tới {at}, nguồn ghi {src(at)!r}")
        if not isinstance(links, list) or not links:
            raise ConvertError(f"{where}: công tắc {at} không có liên kết nào")
        cells, effects = [], []
        for link in links:
            if not (isinstance(link, list) and len(link) == 3 and link[2] in MODE_MAP):
                raise ConvertError(f"{where}: liên kết {link!r} của công tắc {at} không hợp lệ")
            cell = _xy(link[:2], f"{where}, công tắc {at}")
            if src(cell) not in BRIDGE_TILES:
                raise ConvertError(f"{where}: công tắc {at} trỏ tới {cell}, không phải ô cầu")
            if cell in cells:
                raise ConvertError(f"{where}: công tắc {at} nối ô cầu {cell} hai lần")
            cells.append(cell)
            effects.append(MODE_MAP[link[2]])
        entry: Dict[str, Any] = {"at": list(at)}
        if len(set(effects)) == 1:
            entry["bridges"] = [list(c) for c in cells]
            entry["effect"] = effects[0]
        else:
            # Một công tắc, nhiều kiểu tác động: định dạng "links" (docs/03 mục 6).
            entry["links"] = [{"cell": list(c), "effect": e} for c, e in zip(cells, effects)]
        switches.append(entry)
        configured.add(at)

    for key, value in (raw.get("splits") or {}).items():
        at = _key_to_cell(key, where)
        if src(at) != SPLIT_TILE:
            raise ConvertError(f"{where}: công tắc tách khóa {key} trỏ tới {at}, nguồn ghi {src(at)!r}")
        if at in configured:
            raise ConvertError(f"{where}: ô {at} vừa là công tắc vừa là công tắc tách")
        if not (isinstance(value, list) and len(value) == 4):
            raise ConvertError(f"{where}: công tắc tách {at} cần [x1, y1, x2, y2]")
        targets = [_xy(value[:2], where), _xy(value[2:], where)]
        for t in targets:
            if src(t) is None or src(t) == " ":
                raise ConvertError(f"{where}: ô đáp {t} của công tắc tách {at} là ô trống")
        switches.append({"at": list(at), "targets": [list(t) for t in targets]})
        configured.add(at)

    switch_cells = {(r, c) for r, row in enumerate(tiles) for c, ch in enumerate(row)
                    if ch in SWITCH_TILES or ch == SPLIT_TILE}
    missing = sorted(switch_cells - configured)
    if missing:
        raise ConvertError(f"{where}: ô công tắc chưa có cấu hình: {missing}")

    code = raw.get("code")
    if not isinstance(code, int) or not 0 <= code <= 999999:
        raise ConvertError(f"{where}: passcode {code!r} không hợp lệ")

    source = (f"Bloxorz (D. Clarke, 2007), màn {number}; dữ liệu: {SOURCE_REPO} (GPL-3.0), "
              f"commit {SOURCE_COMMIT[:7]}")
    if number in FIX_NOTES:
        source += f"; hiệu chỉnh: {FIX_NOTES[number]}"

    return {
        "name": f"Màn {number}",
        "passcode": f"{code:06d}",  # bản GBA lưu số nguyên nên mất số 0 ở đầu
        "group": GROUP_OF[number],
        "source": source,
        "par": PAR[number - 1],
        "grid": ["".join(row) for row in grid],
        "switches": switches,
    }


def dump_level(level: Dict[str, Any]) -> str:
    """JSON ổn định, dễ đọc: mỗi hàng của lưới và mỗi công tắc trên một dòng."""
    def one(value):
        return json.dumps(value, ensure_ascii=False)

    lines = ["{"]
    for key in ("name", "passcode", "group", "source", "par"):
        lines.append(f"  {one(key)}: {one(level[key])},")
    lines.append('  "grid": [')
    lines.append(",\n".join(f"    {one(row)}" for row in level["grid"]))
    lines.append("  ],")
    if level["switches"]:
        lines.append('  "switches": [')
        lines.append(",\n".join(f"    {one(sw)}" for sw in level["switches"]))
        lines.append("  ]")
    else:
        lines.append('  "switches": []')
    lines.append("}")
    return "\n".join(lines) + "\n"


def convert_all(source: Path) -> Dict[str, str]:
    """Tên file -> nội dung. Gom mọi lỗi rồi báo một lần để biết hết các màn bị lỗi."""
    raws = load_source(source)
    outputs, errors = {}, []
    for number, raw in enumerate(raws, start=1):
        try:
            outputs[f"{number:02d}.json"] = dump_level(convert_level(number, raw))
        except ConvertError as exc:
            errors.append(str(exc))
    if errors:
        raise ConvertError("chuyển đổi lỗi:\n  " + "\n  ".join(errors))
    return outputs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="file levels.json của bản GBA")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="thư mục ghi 33 file màn")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="chỉ so sánh với file đã có, không ghi")
    mode.add_argument("--force", action="store_true", help="ghi đè file đã có nhưng khác nội dung")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # console Windows mặc định cp1252, không in được tiếng Việt
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    digest = sha256_of(args.source)
    print(f"Nguồn: {args.source}\n  sha256 {digest}")
    if digest != SOURCE_SHA256:
        print(f"  CẢNH BÁO: khác sha256 của commit {SOURCE_COMMIT[:7]} ({SOURCE_SHA256})")

    try:
        outputs = convert_all(args.source)
    except ConvertError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2

    counts = {"new": 0, "unchanged": 0, "changed": 0, "written": 0}
    conflicts = []
    if not args.check:
        args.out.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        path = args.out / name
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old == text:
            counts["unchanged"] += 1
            continue
        counts["new" if old is None else "changed"] += 1
        if args.check:
            print(f"  {name}: {'chưa có' if old is None else 'khác nội dung'}")
            continue
        if old is not None and not args.force:
            conflicts.append(name)
            continue
        path.write_text(text, encoding="utf-8", newline="\n")
        counts["written"] += 1

    print(f"Đã chuyển {len(outputs)} màn -> {args.out}")
    print(f"  mới {counts['new']}, giống hệt {counts['unchanged']}, khác {counts['changed']}, "
          f"đã ghi {counts['written']}")
    if conflicts:
        print(f"Không ghi đè {len(conflicts)} file khác nội dung (dùng --force nếu chắc chắn): "
              + ", ".join(conflicts), file=sys.stderr)
        return 1
    if args.check and (counts["new"] or counts["changed"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
