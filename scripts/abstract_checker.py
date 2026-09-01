#!/usr/bin/env python3
"""Abstract quality checker for contest papers.

Mechanical checks on the abstract (extracted from a LaTeX `abstract` environment
or a Markdown `Abstract`/`摘要` heading; falls back to the whole text):
1. length bounds (default 50–900 words);
2. every subquestion should carry a number (`--min-numbers`, default 1);
3. AI-trace scan (reuses ai_trace_checker rules).

Pure standard library. Exit: 0 pass, 1 issues (non-strict), 2 strict.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from ai_trace_checker import analyze as ai_analyze, count_words

LATEX_ABSTRACT_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", flags=re.S)
MD_ABSTRACT_RE = re.compile(r"(?:^|\n)(#{1,3}\s*(?:Abstract|摘要)\s*\n+)(.*?)(?=\n#{1,3}|\Z)", flags=re.S)


def extract_abstract(text: str) -> str:
    m = LATEX_ABSTRACT_RE.search(text)
    if m:
        return m.group(1)
    m = MD_ABSTRACT_RE.search(text)
    if m:
        return m.group(2)
    return text


def check(text: str, min_numbers: int = 1, min_words: int = 50, max_words: int = 900) -> dict:
    abstract = extract_abstract(text)
    words = count_words(abstract)
    numbers = len(re.findall(r"\d+(?:\.\d+)?", abstract))
    ai = ai_analyze(abstract)
    issues = []
    if words < min_words:
        issues.append(f"abstract too short: {words} words (min {min_words})")
    if words > max_words:
        issues.append(f"abstract too long: {words} words (max {max_words})")
    if numbers < min_numbers:
        issues.append(f"abstract has {numbers} number(s) (min {min_numbers}; every subquestion should carry one)")
    if ai["verdict"] == "WARN":
        tokens = [h["token"] for h in ai["hits"] if not h["ok"]][:5]
        issues.append("AI-trace hits: " + ", ".join(tokens))
    return {"abstract_words": words, "numbers": numbers, "ai_verdict": ai["verdict"], "issues": issues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="LaTeX or Markdown file containing the abstract")
    ap.add_argument("--min-numbers", type=int, default=1)
    ap.add_argument("--min-words", type=int, default=50)
    ap.add_argument("--max-words", type=int, default=900)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = Path(a.file).read_text(encoding="utf-8")
    report = check(text, a.min_numbers, a.min_words, a.max_words)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for i in report["issues"]:
            print(">>", i)
        print(f"verdict: {'PASS' if not report['issues'] else 'ISSUES'}")
    if not report["issues"]:
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
