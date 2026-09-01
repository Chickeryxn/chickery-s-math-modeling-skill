#!/usr/bin/env python3
"""Tests for scripts/latex_assembly.py (no LaTeX runtime required)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from latex_assembly import (scan_sections, load_frozen_numbers, ai_declaration,
                            render_main, build_report, sanitize_macro_name,
                            macros_for_frozen, macro_value, latex_escape,
                            parse_bib_to_bibitems, check_frozen_references, estimate_pages,
                            scan_bare_numbers)


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
        "A __INPUTS__\nB __FROZEN_MACROS__\nC __AI_DECLARATION__\nD __REFERENCES__\n", encoding="utf-8")
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
        self.assertEqual(report["skipped_claims"], [])
        td.cleanup()

    def test_macro_value_skips_unsafe_and_escapes(self):
        self.assertEqual(macro_value({"value": 2.4}), "2.4")
        self.assertEqual(macro_value({"value": "0.88"}), "0.88")
        self.assertIsNone(macro_value({"value": {"a": 1}}))
        self.assertIsNone(macro_value({"value": None}))
        self.assertIsNone(macro_value({"value": True}))
        self.assertIsNone(macro_value({}))
        self.assertEqual(latex_escape("a&b_%c#d{e}f~g^h$i\\j"),
                         r"a\&b\_\%c\#d\{e\}f\textasciitilde{}g\textasciicircum{}h\$i\textbackslash{}j")

    def test_macros_for_frozen_skips_bad_values(self):
        frozen = {"ok": {"value": 1.5, "unit": "m"},
                  "bad": {"value": {"x": 1}},
                  "txt": {"value": "a%b", "unit": ""}}
        macros, skipped = macros_for_frozen(frozen)
        self.assertEqual(skipped, ["bad"])
        self.assertIn("\\newcommand{\\ok}{1.5}\\text{m}", macros)
        self.assertIn("\\newcommand{\\txt}{a\\%b}", macros)
        self.assertNotIn("bad", macros)

    def test_parse_bib_to_bibitems(self):
        td, root = make_workspace()
        bib = root / "paper" / "refs.bib"
        bib.write_text("""@article{Wang2023,
  author = {Wang, X.},
  title = {A method},
  journal = {J. Modeling},
  year = {2023}
}
@misc{COMAP2026,
  title = {Problem Statement},
  howpublished = {Contest},
  year = {2026}
}""", encoding="utf-8")
        items = parse_bib_to_bibitems(bib)
        self.assertEqual(len(items), 2)
        self.assertTrue(any(i.startswith("\\bibitem{Wang2023}") and "Wang, X." in i for i in items))
        self.assertTrue(any(i.startswith("\\bibitem{COMAP2026}") for i in items))
        td.cleanup()

    def test_parse_bib_missing_returns_empty(self):
        td, root = make_workspace()
        self.assertEqual(parse_bib_to_bibitems(root / "paper" / "refs.bib"), [])
        td.cleanup()

    def test_check_frozen_references_warns(self):
        td, root = make_workspace()
        # q1.tex currently references \\q1mainrmse -> no warning for it
        (root / "paper" / "sections" / "q2.tex").write_text("裸数字 2.4 出现。", encoding="utf-8")
        frozen = {"q1_main_rmse": {"value": 2.4}, "q2_other": {"value": 9.9}}
        warns = check_frozen_references(root, ["paper/sections/q1.tex", "paper/sections/q2.tex"], frozen)
        self.assertFalse(any("q1_main_rmse" in w for w in warns))      # referenced via macro
        self.assertTrue(any("q2_other" in w for w in warns))           # never referenced
        td.cleanup()

    def test_render_main_injects_references(self):
        td, root = make_workspace()
        out = render_main(root / "templates" / "paper" / "main.tex", root,
                          ["paper/sections/q1.tex"], {}, [], ["\\bibitem{k} A. T. 2023"])
        self.assertIn("\\bibitem{k} A. T. 2023", out)
        self.assertNotIn("__REFERENCES__", out)
        td.cleanup()

    def test_estimate_pages(self):
        td, root = make_workspace()
        (root / "paper" / "sections" / "long.tex").write_text("字" * 1700, encoding="utf-8")
        self.assertEqual(estimate_pages(root, ["paper/sections/long.tex"]), 2)
        td.cleanup()

    def test_scan_bare_numbers_skips_frozen_and_years(self):
        td, root = make_workspace()
        (root / "paper" / "sections" / "q1.tex").write_text(
            "结果 \\q1mainrmse 与 2026 年；另有裸值 3.14 与 2.4（应被冻结宏覆盖）。", encoding="utf-8")
        frozen = {"q1_main_rmse": {"value": 2.4}}
        r = scan_bare_numbers(root, ["paper/sections/q1.tex"], frozen)
        self.assertGreaterEqual(r["count"], 1)
        self.assertTrue(any("3.14" in s for s in r["sample"]))
        self.assertFalse(any("2026" in s for s in r["sample"]))
        td.cleanup()

    def test_build_report_includes_bare_scan(self):
        td, root = make_workspace()
        report = build_report(root, ["paper/sections/q1.tex"], load_frozen_numbers(root), [])
        self.assertIn("bare_number_scan", report)
        self.assertIn("frozen_reference_warnings", report)
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
