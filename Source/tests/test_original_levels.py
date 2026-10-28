"""Kiểm tra 33 màn gốc trong levels/original/ (docs/01 NV4, docs/03 mục 4 và 6).

Đối chiếu ba chiều:
- với bảng chuẩn ở docs/03 mục 4 (passcode, nhóm, số ô từng loại, kiểu công tắc, bước tối ưu);
- với dữ liệu thô của bản GBA, đọc lại độc lập với script chuyển đổi (tọa độ, liên kết công tắc);
- với chính script chuyển đổi: chạy lại phải ra đúng nội dung file đã có.
"""
import json
import unittest
from pathlib import Path

from bloxorz.level import LevelError, Switch, parse_level
from experiments import convert_original_levels as conv

SOURCE_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DIR = SOURCE_DIR / "levels" / "original"
RAW_PATH = conv.DEFAULT_SOURCE

T, O, C = "toggle", "open", "close"
# docs/03 mục 4. Cột: passcode, nhóm, số ô (không trống, tính cả cầu), ô dễ vỡ,
# công tắc mềm, công tắc nặng, công tắc tách, ô cầu, các kiểu công tắc, bước tối ưu.
EXPECTED = {
    1: ("780464", "G1", 35, 0, 0, 0, 0, 0, set(), 7),
    2: ("290299", "G3", 63, 0, 1, 1, 0, 4, {T}, 17),
    3: ("918660", "G1", 48, 0, 0, 0, 0, 0, set(), 19),
    4: ("520967", "G2", 69, 31, 0, 0, 0, 0, set(), 28),
    5: ("028431", "G3", 73, 0, 4, 0, 0, 6, {T, O, C}, 33),
    6: ("524383", "G1", 55, 0, 0, 0, 0, 0, set(), 35),
    7: ("189493", "G3", 56, 0, 0, 1, 0, 1, {T}, 44),
    8: ("499707", "G5", 54, 0, 0, 0, 1, 0, set(), 10),
    9: ("074355", "G5", 39, 0, 0, 0, 1, 0, set(), 24),
    10: ("300590", "G5", 55, 0, 1, 1, 1, 6, {T}, 57),
    11: ("291709", "G3", 51, 0, 1, 0, 0, 2, {C}, 47),
    12: ("958640", "G3", 60, 0, 0, 2, 0, 2, {T}, 65),
    13: ("448106", "G2", 82, 22, 0, 0, 0, 0, set(), 46),
    14: ("210362", "G3", 68, 0, 0, 2, 0, 4, {T}, 67),
    15: ("098598", "G5", 72, 0, 3, 1, 1, 8, {T, C}, 57),
    16: ("000241", "G5", 42, 0, 0, 2, 5, 4, {O}, 28),
    17: ("683596", "G3", 70, 0, 1, 4, 0, 4, {T, O, C}, 106),
    18: ("284933", "G3", 59, 0, 5, 1, 0, 7, {T, O, C}, 85),
    19: ("119785", "G3", 66, 0, 3, 0, 0, 4, {T, O, C}, 67),
    20: ("543019", "G5", 66, 0, 5, 0, 1, 6, {T, C}, 56),
    21: ("728724", "G3", 61, 0, 0, 2, 0, 2, {T}, 71),
    22: ("987319", "G3", 59, 0, 2, 2, 0, 3, {T, C}, 65),
    23: ("293486", "G5", 89, 18, 3, 1, 1, 8, {T, O, C}, 75),
    24: ("088198", "G5", 59, 0, 0, 4, 1, 6, {O}, 57),
    25: ("250453", "G3", 62, 0, 2, 1, 0, 9, {T, O, C}, 55),
    26: ("426329", "G5", 56, 0, 1, 1, 1, 4, {O, C}, 104),
    27: ("660141", "G4", 88, 27, 2, 1, 0, 2, {C}, 71),
    28: ("769721", "G5", 69, 7, 1, 0, 1, 4, {C}, 100),
    29: ("691859", "G3", 65, 0, 3, 3, 0, 17, {O, C}, 104),
    30: ("280351", "G4", 87, 40, 0, 3, 0, 5, {T, O, C}, 114),
    31: ("138620", "G4", 80, 8, 2, 3, 0, 14, {T, O, C}, 91),
    32: ("879021", "G3", 63, 0, 0, 3, 0, 8, {T}, 129),
    33: ("614955", "G3", 99, 0, 12, 1, 0, 5, {O, C}, 65),
}
LEVEL3_FIX = {(6, 11), (7, 12), (7, 13), (7, 14)}
TILE_CHARS = set(".#SGFbBox@")
REQUIRED = {"name": str, "passcode": str, "group": str, "source": str, "par": int,
            "grid": list, "switches": list}


def switch_links(sw):
    """[(ô cầu, kiểu)] của một công tắc, đọc được cả hai cách ghi: bridges + effect, hoặc links."""
    if "links" in sw:
        return [(tuple(x["cell"]), x["effect"]) for x in sw["links"]]
    return [(tuple(b), sw["effect"]) for b in sw.get("bridges", [])]


class OriginalLevelFilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {int(p.stem): p for p in ORIGINAL_DIR.glob("*.json")}
        cls.data = {n: json.loads(p.read_text(encoding="utf-8")) for n, p in cls.files.items()}
        cls.raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))["levels"]

    def each(self):
        for n in sorted(self.data):
            with self.subTest(level=n):
                yield n, self.data[n]

    def test_exactly_33_files_named_01_to_33(self):
        names = sorted(p.name for p in ORIGINAL_DIR.glob("*.json"))
        self.assertEqual(names, [f"{n:02d}.json" for n in range(1, 34)])

    def test_required_fields_and_types(self):
        for n, d in self.each():
            for key, typ in REQUIRED.items():
                self.assertIsInstance(d.get(key), typ, key)
            self.assertEqual(d["name"], f"Màn {n}")
            self.assertIn("bloxorz_gba", d["source"])
            self.assertIn(conv.SOURCE_COMMIT[:7], d["source"])

    def test_grid_is_10_by_15_with_known_tiles(self):
        for n, d in self.each():
            self.assertEqual(len(d["grid"]), 10)
            for row in d["grid"]:
                self.assertIsInstance(row, str)
                self.assertEqual(len(row), 15)
                self.assertLessEqual(set(row), TILE_CHARS)

    def test_one_start_and_one_goal(self):
        for n, d in self.each():
            text = "".join(d["grid"])
            self.assertEqual(text.count("S"), 1)
            self.assertEqual(text.count("G"), 1)

    def test_passcode_group_par_match_table(self):
        for n, d in self.each():
            passcode, group, *_, par = EXPECTED[n]
            self.assertEqual(d["passcode"], passcode)  # chuỗi: giữ số 0 ở đầu (màn 5, 9, 15, 16, 24)
            self.assertRegex(d["passcode"], r"^\d{6}$")
            self.assertEqual(d["group"], group)
            self.assertEqual(d["par"], par)

    def test_tile_counts_match_table(self):
        for n, d in self.each():
            _, _, cells, fragile, soft, heavy, split, bridges, _, _ = EXPECTED[n]
            text = "".join(d["grid"])
            actual = (len(text) - text.count("."), text.count("F"), text.count("o"),
                      text.count("x"), text.count("@"), text.count("b") + text.count("B"))
            self.assertEqual(actual, (cells, fragile, soft, heavy, split, bridges))

    def test_switch_effect_kinds_match_table(self):
        for n, d in self.each():
            kinds = {e for sw in d["switches"] for _, e in switch_links(sw)}
            self.assertEqual(kinds, EXPECTED[n][8])

    def test_switches_point_to_valid_cells(self):
        for n, d in self.each():
            grid = d["grid"]

            def tile(cell):
                r, c = cell
                self.assertTrue(0 <= r < 10 and 0 <= c < 15, f"{cell} nằm ngoài bàn")
                return grid[r][c]

            seen = set()
            for sw in d["switches"]:
                at = tuple(sw["at"])
                self.assertNotIn(at, seen, f"công tắc {at} khai báo hai lần")
                seen.add(at)
                kind = tile(at)
                self.assertIn(kind, "ox@", f"{at} không phải ô công tắc")
                if kind == "@":
                    self.assertEqual(len(sw["targets"]), 2)
                    for t in sw["targets"]:
                        self.assertNotEqual(tile(tuple(t)), ".", f"ô đáp {t} là ô trống")
                else:
                    self.assertNotIn("targets", sw)
                    links = switch_links(sw)
                    self.assertTrue(links, f"công tắc {at} không nối cầu nào")
                    cells = [cell for cell, _ in links]
                    self.assertEqual(len(cells), len(set(cells)))
                    for cell, effect in links:
                        self.assertIn(tile(cell), "bB", f"{cell} không phải ô cầu")
                        self.assertIn(effect, (T, O, C))
                    # "links" chỉ dùng khi thật sự có nhiều kiểu khác nhau
                    self.assertEqual("links" in sw, len({e for _, e in links}) > 1)
            all_switch_cells = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch in "ox@"}
            self.assertEqual(seen, all_switch_cells)

    def test_matches_raw_source_independently(self):
        """Đọc lại levels.json của bản GBA, không qua script: (x, y) = (cột, hàng), khóa = x * 10 + y."""
        tile_map = {" ": ".", "b": "#", "e": "G", "f": "F", "s": "o", "h": "x", "v": "@",
                    "l": "b", "r": "b", "k": "B", "q": "B"}
        modes = {"onoff": T, "on": O, "off": C}
        for n, d in self.each():
            raw = self.raw[n - 1]
            self.assertEqual(f"{raw['code']:06d}", d["passcode"])
            sx, sy = raw["spawn"]
            self.assertEqual(d["grid"][sy][sx], "S")
            for r in range(10):
                for c in range(15):
                    expected = tile_map[raw["tiles"][r][c]]
                    if (r, c) == (sy, sx):
                        expected = "S"
                    if n == 3 and (r, c) in LEVEL3_FIX:
                        self.assertEqual(raw["tiles"][r][c], " ")
                        expected = "#"
                    self.assertEqual(d["grid"][r][c], expected, f"ô {(r, c)}")

            by_cell = {tuple(sw["at"]): sw for sw in d["switches"]}
            for key, links in raw.get("switches", {}).items():
                at = (int(key) % 10, int(key) // 10)
                self.assertEqual(sorted(switch_links(by_cell[at])),
                                 sorted(((by, bx), modes[m]) for bx, by, m in links))
            for key, (x1, y1, x2, y2) in raw.get("splits", {}).items():
                at = (int(key) % 10, int(key) // 10)
                self.assertEqual(by_cell[at]["targets"], [[y1, x1], [y2, x2]])
            self.assertEqual(len(by_cell), len(raw.get("switches", {})) + len(raw.get("splits", {})))

    def test_level_3_fix_is_documented(self):
        self.assertIn("hiệu chỉnh", self.data[3]["source"])
        for n, d in self.data.items():
            if n != 3:
                self.assertNotIn("hiệu chỉnh", d["source"], n)

    def test_converter_reproduces_files(self):
        outputs = conv.convert_all(RAW_PATH)
        for name, text in outputs.items():
            with self.subTest(file=name):
                self.assertEqual((ORIGINAL_DIR / name).read_text(encoding="utf-8"), text)

    def test_raw_source_is_pinned_commit(self):
        self.assertEqual(conv.sha256_of(RAW_PATH), conv.SOURCE_SHA256)

    def uses_links(self, d):
        return any("links" in sw for sw in d["switches"])

    def test_loader_reads_levels_without_links(self):
        for n, d in self.each():
            if self.uses_links(d):
                continue
            level = parse_level(d, f"{n:02d}", where=f"{n:02d}.json")
            self.assertEqual(level.par, d["par"])
            self.assertEqual(level.group, d["group"])

    def test_loader_reads_levels_with_links(self):
        """Bộ nạp màn (TV3) phải đọc được cả 6 màn dùng "links" (docs/03 mục 6)."""
        pending = [n for n, d in sorted(self.data.items()) if self.uses_links(d)]
        self.assertEqual(pending, [17, 23, 25, 29, 30, 31])
        if "links" not in getattr(Switch, "__dataclass_fields__", {}):
            self.skipTest(f"bộ nạp chưa đọc 'links'; chưa kiểm được màn {pending}")
        for n in pending:
            with self.subTest(level=n):
                parse_level(self.data[n], f"{n:02d}")

    def test_links_levels_are_rejected_loudly_until_supported(self):
        """Khi bộ nạp chưa hỗ trợ links, nó phải báo lỗi rõ chứ không âm thầm bỏ cầu."""
        if "links" in getattr(Switch, "__dataclass_fields__", {}):
            self.skipTest("bộ nạp đã hỗ trợ links")
        for n, d in self.each():
            if any("links" in sw for sw in d["switches"]):
                with self.assertRaises(LevelError):
                    parse_level(d, f"{n:02d}")


if __name__ == "__main__":
    unittest.main()
