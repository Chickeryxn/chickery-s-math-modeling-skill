#!/usr/bin/env python3
"""Tests for scripts/latex_assembly.py (no LaTeX runtime required)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from latex_assembly import (scan_sections, load_frozen_numbers, ai_declaration,
                            render_main, build_report, sanitize_macro_name)


def make_workspace():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "paper" / "sections").mkdir(parents=True)
    (root / "results" / "Q1" / "reports").mkdir(parents=True)
    (root / "methods" / "Q1").mkdir(parents=True)
    (root / "templates" / "paper").mkdir(parents=True)
    (root / "paper" / "sections" / "q1.tex").write_text("\\section{问题一}\n结果 \q1mainrmse。\n", encoding="utf-8")
    (root / "results" / "Q1" / "reports" / "frozen_numbers.json").write_text(json.dumps(
        {"claims": [{"claim_id": "q1_main_rmse", "value": 2.4, "unit": "m"}]}), encoding="utf-8")
    (root / "methods" / "Q1" / "q1_decisions.jsonl").write_text(
        json.dumps({"decision_id": "d", "decision_type": "submission_authorization",
                    "status": "DECIDED", "choice": "ok"}) + "\n", encoding="utf-8")
    (root / "templates" / "paper" / "main.tex").write_text(
        "A __INPUTS__\nB __FROZEN_MACROS__\nC __AI_DECLARATION__\n", encoding="utf-8")
    return td, root


class LatexAssemblyTests(unittest.TestCase):
    def test_scan_sections(self):
        td, root = make_workspace()
        self.assertEqual(scan_sections(root), ["paper/sections/q1.tex"])
        td.cleanup()

    def test_load_frozen_numbers(self):
        td, root = make_workspace()
        frozen = load_frozen_numbers(root)
        self.assertIn("q1_main_rmse", frozen)
        self.assertEqual(frozen["q1_main_rmse"]["value"], 2.4)
        td.cleanup()

    def test_ai_declaration_from_ledger(self):
        td, root = make_workspace()
        blocks, sources = ai_declaration(root)
        self.assertEqual(len(blocks), 1)
        self.assertIn("AI 工具使用声明", blocks[0])
        self.assertEqual(sources, ["methods/Q1/q1_decisions.jsonl"])
        td.cleanup()

    def test_render_main_substitutes_placeholders(self):
        td, root = make_workspace()
        frozen = load_frozen_numbers(root)
        out = render_main(root / "templates" / "paper" / "main.tex", root,
                          ["paper/sections/q1.tex"], frozen, ["\\section*{AI 工具使用声明}\nx"])
        self.assertIn("\\input{paper/sections/q1.tex}", out)
        self.assertIn("\\newcommand{\\q1mainrmse}{2.4}", out)
        self.assertIn("AI 工具使用声明", out)
        self.assertNotIn("__INPUTS__", out)
        td.cleanup()

    def test_sanitize_macro_name(self):
        self.assertEqual(sanitize_macro_name("q1_main_rmse"), "q1mainrmse")
        self.assertEqual(sanitize_macro_name("!!!"), "frozenvalue")

    def test_build_report_counts(self):
        td, root = make_workspace()
        frozen = load_frozen_numbers(root)
        report = build_report(root, ["paper/sections/q1.tex"], frozen, ["methods/Q1/q1_decisions.jsonl"])
        self.assertEqual(report["section_count"], 1)
        self.assertEqual(report["frozen_count"], 1)
        self.assertEqual(report["frozen_macros"], ["q1mainrmse"])
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
