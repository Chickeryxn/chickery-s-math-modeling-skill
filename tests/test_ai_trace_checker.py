#!/usr/bin/env python3
"""Tests for scripts/ai_trace_checker.py (pure standard library)."""
from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ai_trace_checker import analyze, count_words, load_config


def hit(report, token):
    for h in report["hits"]:
        if h["token"] == token:
            return h
    return None


class AiTraceCheckerTests(unittest.TestCase):
    def test_clean_text_passes(self):
        r = analyze("The model was fitted with 200 iterations and cross-validated.")
        self.assertEqual(r["verdict"], "PASS")

    def test_empty_text_passes(self):
        r = analyze("")
        self.assertEqual(r["verdict"], "PASS")
        # count_words("") == 0 is floored to 1 (max(..., 1)) so per-word rate
        # thresholds never divide by zero; the guard is intentional.
        self.assertEqual(r["word_count"], 1)

    def test_furthermore_over_limit_warns(self):
        r = analyze("Furthermore, one. Furthermore, two. Furthermore, three.")
        self.assertEqual(r["verdict"], "WARN")
        self.assertFalse(hit(r, "furthermore")["ok"])

    def test_combined_moreover_furthermore_limit(self):
        # 2 furthermore + 1 moreover in a short text: each <= 2 but combined > 2
        r = analyze("Furthermore a. Furthermore b. Moreover c.")
        self.assertEqual(r["verdict"], "WARN")
        self.assertTrue(hit(r, "furthermore")["ok"])          # 2 vs absolute limit 2
        self.assertTrue(hit(r, "moreover")["ok"])
        self.assertFalse(hit(r, "furthermore+moreover (combined)")["ok"])

    def test_cjk_tokens(self):
        r = analyze("此外，此外，此外，结果如下。")
        self.assertEqual(r["verdict"], "WARN")
        self.assertFalse(hit(r, "此外")["ok"])
        self.assertEqual(hit(r, "此外")["count"], 3)

    def test_zero_tolerance_phrases(self):
        r = analyze("It is worth noting that we delve into details.")
        self.assertEqual(r["verdict"], "WARN")
        self.assertFalse(hit(r, "delve")["ok"])
        self.assertFalse(hit(r, "it is worth noting")["ok"])

    def test_em_dash_limit(self):
        r = analyze("A -- B -- C -- D -- E")
        self.assertEqual(r["verdict"], "WARN")
        self.assertEqual(hit(r, "em-dash")["count"], 4)

    def test_new_cjk_phrases(self):
        r = analyze("重要的是，不可忽视的影响，高度复杂的系统，值得深入探讨。")
        self.assertEqual(r["verdict"], "WARN")
        for t in ("重要的是", "不可忽视的", "高度复杂的", "深入探讨"):
            self.assertFalse(hit(r, t)["ok"], t)

    def test_count_words_mixed(self):
        self.assertEqual(count_words("abc def"), 2)
        self.assertEqual(count_words("模型A与B"), 3 + 2)  # 3 CJK + 2 latin tokens

    def test_count_words_excludes_cjk_punctuation(self):
        # Regression: 、。！？etc. (U+3000-303F) were counted as words, inflating
        # abstract length bounds ("模型。结果、分析！" used to report 8 words).
        self.assertEqual(count_words("模型。结果、分析！"), 6)
        self.assertEqual(count_words("模型：结果；分析？"), 6)
        self.assertEqual(count_words("（模型）—结果"), 4)

    def test_em_dash_run_counts_once(self):
        # Regression: '---'/'----' matched zero times (only '--' counted).
        r = analyze("A --- B ---- C")
        self.assertEqual(hit(r, "em-dash")["count"], 2)
        self.assertEqual(r["verdict"], "PASS")  # 2 runs == limit 2
        # a single hyphen is not an em dash
        r2 = analyze("well-known result state-of-the-art")
        self.assertEqual(hit(r2, "em-dash")["count"], 0)

    def test_cjk_double_dash_counts_once(self):
        # Regression: each — of a CJK —— double dash was counted separately,
        # so two normal —— pairs already broke the limit of 2. One typographic
        # —— is a single em-dash usage.
        r = analyze("结果显著——误差很小——结论一致。")
        self.assertEqual(hit(r, "em-dash")["count"], 2)
        self.assertEqual(r["verdict"], "PASS")  # 2 usages == limit 2
        r2 = analyze("第一——第二——第三——第四。")
        self.assertEqual(hit(r2, "em-dash")["count"], 3)
        self.assertEqual(r2["verdict"], "WARN")

    def test_config_overrides_limits(self):
        cfg = load_config(Path(__import__("tempfile").mkdtemp()) / "x")
        self.assertEqual(cfg, {})
        import json, tempfile
        td = tempfile.TemporaryDirectory()
        p = Path(td.name) / "cfg.json"
        p.write_text(json.dumps({"limits": {"furthermore": 5},
                                 "groups": [[["notably", "crucially"], 0]],
                                 "em_dash_limit": 5}), encoding="utf-8")
        cfg = load_config(p)
        self.assertEqual(cfg["limits"]["furthermore"], 5)
        self.assertEqual(cfg["groups"], [(['notably', 'crucially'], 0)])
        self.assertEqual(cfg["em_dash_limit"], 5)
        r = analyze("Furthermore a. Furthermore b. Furthermore c.", **cfg)
        self.assertEqual(r["verdict"], "PASS")  # 3 <= 5 under custom limit
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
