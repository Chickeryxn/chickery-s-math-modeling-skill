#!/usr/bin/env python3
"""Tests for scripts/abstract_checker.py (pure standard library)."""
from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from abstract_checker import extract_abstract, check

LATEX_GOOD = r"""\begin{abstract}
本文对问题一建立了熵权-TOPSIS 模型，得分 0.83；问题二采用遗传算法，结果 12.4 分钟。
结果表明模型有效。
\end{abstract}"""


class AbstractCheckerTests(unittest.TestCase):
    def test_extract_latex_abstract(self):
        out = extract_abstract(LATEX_GOOD)
        self.assertIn("TOPSIS", out)
        self.assertNotIn("\\begin", out)

    def test_extract_markdown_abstract(self):
        md = "# Paper\n\n## Abstract\n\nWe built a model with RMSE 2.4.\n\n## Next\n"
        self.assertIn("RMSE 2.4", extract_abstract(md))

    def test_good_abstract_passes(self):
        r = check(LATEX_GOOD, min_numbers=2, min_words=10)
        self.assertEqual(r["issues"], [])
        self.assertGreaterEqual(r["numbers"], 2)

    def test_missing_numbers_fails(self):
        r = check("本文仅描述方法，不包含任何数字。", min_numbers=2)
        self.assertTrue(any("number" in i for i in r["issues"]))

    def test_ai_trace_flagged(self):
        r = check("It is worth noting that the model is significantly better, furthermore, moreover, notably.")
        self.assertTrue(any("AI-trace" in i for i in r["issues"]))

    def test_length_bounds(self):
        self.assertTrue(any("too short" in i for i in check("短。")["issues"]))
        long = "字" * 950
        self.assertTrue(any("too long" in i for i in check(long)["issues"]))


if __name__ == "__main__":
    unittest.main()
