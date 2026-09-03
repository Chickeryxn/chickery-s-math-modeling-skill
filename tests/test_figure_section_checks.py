#!/usr/bin/env python3
"""Tests for scripts/figure_consistency_check.py and section_structure_check.py."""
from __future__ import annotations
import json, tempfile, unittest, struct, zlib
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from figure_consistency_check import scan as fscan, png_size
from section_structure_check import check as scheck, slot_of


def make_png(path: Path, w: int, h: int):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x00" * w * 3 for _ in range(h))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class FigureConsistencyTests(unittest.TestCase):
    def test_consistent_group_passes(self):
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        make_png(d / "q1_b.png", 800, 600)
        r = fscan(d, None)
        self.assertEqual(r["status"], "PASS")
        td.cleanup()

    def test_inconsistent_width_fails(self):
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        make_png(d / "q1_b.png", 1000, 600)
        r = fscan(d, None)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("inconsistent" in f for f in r["findings"]))
        td.cleanup()

    def test_same_aspect_family_different_widths_passes(self):
        # Regression: only pixel widths were compared although the docstring
        # promises "same width or same aspect family". A full-width and a
        # half-width rendering of the same figure keep the same aspect ratio
        # and are consistent.
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        make_png(d / "q1_b.png", 400, 300)
        r = fscan(d, None)
        self.assertEqual(r["status"], "PASS", r["findings"])
        td.cleanup()

    def test_different_aspect_families_still_fail(self):
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        make_png(d / "q1_b.png", 600, 800)
        r = fscan(d, None)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("inconsistent" in f for f in r["findings"]))
        td.cleanup()

    def test_manifest_missing_fails(self):
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        m = d / "figs.json"
        m.write_text(json.dumps({"figures": ["q1_a.png", "q1_missing.png"]}), encoding="utf-8")
        r = fscan(d, m)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("declared figure missing" in f for f in r["findings"]))
        td.cleanup()

    def test_png_size_parser(self):
        td = tempfile.TemporaryDirectory()
        p = Path(td.name) / "x.png"
        make_png(p, 640, 480)
        self.assertEqual(png_size(p), (640, 480))
        td.cleanup()

    def test_case_insensitive_duplicate_names_flagged(self):
        import os
        if os.path.normcase("q1_a.png") == os.path.normcase("Q1_A.PNG"):
            self.skipTest("case-insensitive filesystem cannot hold both names")
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        make_png(d / "Q1_A.PNG", 800, 600)
        r = fscan(d, None)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("duplicate figure names" in f for f in r["findings"]), r["findings"])
        td.cleanup()

    def test_manifest_extensionless_declared_resolves(self):
        # Regression: manifest entries may omit the extension (LaTeX style);
        # a unique match must not be reported as missing.
        td = tempfile.TemporaryDirectory()
        d = Path(td.name)
        make_png(d / "q1_a.png", 800, 600)
        m = d / "figs.json"
        m.write_text(json.dumps({"figures": ["q1_a"]}), encoding="utf-8")
        r = fscan(d, m)
        self.assertEqual(r["status"], "PASS", r["findings"])
        td.cleanup()


class SectionStructureTests(unittest.TestCase):
    def test_full_skeleton_passes(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "paper" / "sections").mkdir(parents=True)
        titles = ["摘要", "问题重述", "模型假设", "符号说明", "模型构建", "模型求解",
                  "结果分析", "稳健性分析", "结论", "参考文献", "AI 工具使用声明"]
        for i, t in enumerate(titles):
            (root / "paper" / "sections" / f"s{i}.tex").write_text(
                f"\\section{{{t}}}\n内容。\n", encoding="utf-8")
        r = scheck(root)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["missing"], [])
        td.cleanup()

    def test_missing_conclusion_fails(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "paper" / "sections").mkdir(parents=True)
        (root / "paper" / "sections" / "a.tex").write_text("\\section{结果分析}\n", encoding="utf-8")
        r = scheck(root)
        self.assertTrue(any("missing section: conclusion" in f for f in r["findings"]))
        td.cleanup()

    def test_slot_of(self):
        self.assertEqual(slot_of("摘要"), "abstract")
        self.assertEqual(slot_of("模型构建"), "model")
        self.assertIsNone(slot_of("任意其他"))
        # English titles whose words merely contain ASCII substrings of a slot
        # keyword must not be swallowed by that slot (e.g. "ai" inside
        # "main analysis"); only genuine keyword hits classify.
        self.assertIsNone(slot_of("Main analysis"))
        self.assertIsNone(slot_of("Data details"))
        self.assertIsNone(slot_of("Certain aspects"))
        self.assertEqual(slot_of("Model Construction"), "model")
        self.assertEqual(slot_of("Robustness analysis"), "robustness")