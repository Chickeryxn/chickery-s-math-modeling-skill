#!/usr/bin/env python3
"""polish_stats metrics tests (0.8.0)."""
from __future__ import annotations
import subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from polish_stats import analyze


LONG_SENTENCE = " ".join(["word"] * 45) + "."
SHORT_SENTENCE = "Results were stable."


class PolishStatsTests(unittest.TestCase):
    def test_metrics_shape(self):
        out = analyze(SHORT_SENTENCE + " " + LONG_SENTENCE)
        self.assertEqual(out['sentences'], 2)
        self.assertEqual(out['long_sentences_over_30_words'], 1)
        self.assertGreater(out['long_sentence_ratio'], 0.25)

    def test_filler_detection(self):
        text = "It is important to note that the result improved. 值得注意的是误差可控。"
        out = analyze(text)
        self.assertEqual(out['filler_total'], 2)
        self.assertIn('it is important to note', out['filler_phrases'])
        self.assertIn('值得注意的是', out['filler_phrases'])

    def test_strict_exit_code(self):
        text = " ".join([" ".join(["word"] * 45) + "."] * 4)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'sample.txt'
            p.write_text(text, encoding='utf-8')
            r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'polish_stats.py'),
                                str(p), '--strict'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(r.returncode, 2, r.stdout)

    def test_clean_text_passes_strict(self):
        out = analyze("We applied the method and compared it with the baseline. "
                      "The error improved from 3.1 to 2.4.")
        self.assertEqual(out['filler_total'], 0)
        self.assertLessEqual(out['long_sentence_ratio'], 0.25)


if __name__ == '__main__':
    unittest.main()
