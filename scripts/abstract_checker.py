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
CONCLUSION_RE = re.compile(r"(?:#{1,3}\s*(?:结论|总结|Conclusion)\s*\n+|\\section\*?\{[^}]*结论[^}]*\})(.*?)(?=\n#{1,3}|\Z)", flags=re.S)

Q_KEYWORDS = {  # subquestion id -> keywords that identify it in the conclusion
    "Q1": ("Q1", "问题一", "问题 1", "第1问", "第一问"),
    "Q2": ("Q2", "问题二", "问题 2", "第2问", "第二问"),
    "Q3": ("Q3", "问题三", "问题 3", "第3问", "第三问"),
    "Q4": ("Q4", "问题四", "问题 4", "第4问", "第四问"),
    "Q5": ("Q5", "问题五", "问题 5", "第5问", "第五问"),
    "Q6": ("Q6", "问题六", "问题 6", "第6问", "第六问"),
}


def check_conclusion_coverage(text: str, subquestions: list[str] | None) -> list[str]:
    """Return issues when the conclusion section does not mention every subquestion."""
    if not subquestions:
        return []
    m = CONCLUSION_RE.search(text)
    if not m:
        return []  # no conclusion section found; the section-structure check owns that
    seg = m.group(1)
    issues = []
    for qid in subquestions:
        keys = Q_KEYWORDS.get(qid, (qid,))
        if not any(k in seg for k in keys):
            issues.append(f"conclusion does not cover {qid}")
    return issues


def extract_abstract(text: str) -> str:
    m = LATEX_ABSTRACT_RE.search(text)
    if m:
        return m.group(1)
    m = MD_ABSTRACT_RE.search(text)
    if m:
        return m.group(2)
    return text


def check(text: str, min_numbers: int = 1, min_words: int = 50, max_words: int = 900,
          subquestions: list[str] | None = None) -> dict:
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
    issues.extend(check_conclusion_coverage(text, subquestions))
    return {"abstract_words": words, "numbers": numbers, "ai_verdict": ai["verdict"], "issues": issues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="LaTeX or Markdown file containing the abstract")
    ap.add_argument("--min-numbers", type=int, default=1)
    ap.add_argument("--min-words", type=int, default=50)
    ap.add_argument("--max-words", type=int, default=900)
    ap.add_argument("--subquestions", default=None,
                    help="comma-separated subquestion ids (Q1,Q2) to require conclusion coverage for")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = Path(a.file).read_text(encoding="utf-8")
    subs = [s.strip().upper() for s in a.subquestions.split(",") if s.strip()] if a.subquestions else None
    report = check(text, a.min_numbers, a.min_words, a.max_words, subs)
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
