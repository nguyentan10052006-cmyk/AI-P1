"""Unit tests for synthetic levels S1-S3 generator (TV3, Task V40)."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from bloxorz.level import load_level
from bloxorz.problem import Problem
from experiments.gen_levels import (
    DEFAULT_OUT_DIR,
    S1_SIZES,
    S2_COUNTS,
    S3_SIZES,
    generate_s1,
    generate_s2,
    generate_s3,
)
from solvers.base import NO_SOLUTION, SOLVED
from solvers.bfs import BFS
from solvers.ucs import UCS


class TestSyntheticLevels(unittest.TestCase):
    """Kiểm thử tính đúng đắn của bộ sinh và các file màn tự sinh S1-S3."""

    def test_all_14_files_exist_on_disk(self):
        """14 file JSON phải tồn tại đầy đủ trong Source/levels/gen/."""
        expected_files = (
            [f"s1_{n:03d}.json" for n in S1_SIZES]
            + [f"s2_{k:02d}.json" for k in S2_COUNTS]
            + [f"s3_{w:02d}.json" for w in S3_SIZES]
        )
        self.assertEqual(len(expected_files), 14)
        for fname in expected_files:
            file_path = DEFAULT_OUT_DIR / fname
            self.assertTrue(file_path.exists(), f"Thiếu file tự sinh: {fname}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("grid", data)
            self.assertIn("group", data)
            self.assertIn("par", data)

    def test_s1_schema_and_generator(self):
        """Kiểm thử cấu trúc màn S1 (sân trống N x N)."""
        data = generate_s1(10)
        self.assertEqual(data["group"], "S1")
        self.assertEqual(len(data["grid"]), 10)
        self.assertEqual(len(data["grid"][0]), 10)
        self.assertEqual(data["grid"][0][0], "S")
        self.assertEqual(data["grid"][9][9], "G")
        self.assertEqual(data["switches"], [])

    def test_s2_schema_and_generator(self):
        """Kiểm thử cấu trúc màn S2 (cầu và k công tắc)."""
        data = generate_s2(4)
        self.assertEqual(data["group"], "S2")
        self.assertEqual(len(data["grid"]), 8)
        self.assertEqual(len(data["grid"][0]), 12)
        self.assertEqual(len(data["switches"]), 4)
        for sw in data["switches"]:
            self.assertEqual(sw["effect"], "toggle")
            self.assertEqual(len(sw["bridges"]), 1)

    def test_s3_schema_and_generator(self):
        """Kiểm thử cấu trúc màn S3 (bị chia cắt bởi khe trống, không lời giải)."""
        data = generate_s3(10)
        self.assertEqual(data["group"], "S3")
        self.assertEqual(len(data["grid"]), 10)
        self.assertEqual(data["grid"][1][1], "S")
        # Cột thứ 10 (chỉ số 10) là khe trống '.'
        for row in data["grid"]:
            self.assertEqual(row[10], ".")

    def test_loadable_and_solvable_via_bfs_and_ucs(self):
        """Nạp qua load_level và kiểm tra tính giải được trên đại diện mỗi nhóm."""
        # S1 nhỏ: s1_010
        lvl_s1 = load_level(DEFAULT_OUT_DIR / "s1_010.json", "s1_010")
        prob_s1 = Problem(lvl_s1)
        res_bfs_s1 = BFS().search(prob_s1)
        res_ucs_s1 = UCS().search(prob_s1)
        self.assertEqual(res_bfs_s1.status, SOLVED)
        self.assertEqual(res_ucs_s1.status, SOLVED)
        self.assertEqual(len(res_bfs_s1.path), lvl_s1.par)
        self.assertEqual(len(res_ucs_s1.path), lvl_s1.par)

        # S2 nhỏ: s2_02
        lvl_s2 = load_level(DEFAULT_OUT_DIR / "s2_02.json", "s2_02")
        prob_s2 = Problem(lvl_s2)
        res_bfs_s2 = BFS().search(prob_s2)
        self.assertEqual(res_bfs_s2.status, SOLVED)
        self.assertEqual(len(res_bfs_s2.path), lvl_s2.par)

        # S3 nhỏ: s3_10 phải vô nghiệm
        lvl_s3 = load_level(DEFAULT_OUT_DIR / "s3_10.json", "s3_10")
        prob_s3 = Problem(lvl_s3)
        res_bfs_s3 = BFS().search(prob_s3)
        res_ucs_s3 = UCS().search(prob_s3)
        self.assertEqual(res_bfs_s3.status, NO_SOLUTION)
        self.assertEqual(res_ucs_s3.status, NO_SOLUTION)


if __name__ == "__main__":
    unittest.main()
