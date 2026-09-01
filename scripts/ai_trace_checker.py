#!/usr/bin/env python3
"""Quantifiable AI-trace checker for academic text.

Counts AI-sounding words/phrases and em-dash frequency against per-1000-word
limits inspired by de-AI-writing methodology (see
`references/upstream/lupynow-writing/de-ai-writing.md`). Pure standard library.

Rules (self-authored, advisory):
  - `furthermore` / `moreover` / 此外 : <= 2 per 1000 words
  - `notably` / `crucially` / 值得一提的是 / 值得注意的是 : <= 1 per 1000 words
  - `significantly` / 显著地 (without a stated test) : <= 1 per 1000 words
  - zero-tolerance phrases: `delve`, `it is worth noting`, `it should be noted`,
    `in conclusion`, `综上所述`
  - em dash `--`/`—` : <= 2 per 1000 words

Usage:
  python scripts/ai_trace_checker.py path/to/section.md [--strict] [--json]
Exit code: 0 = PASS, 1 = WARN (non-strict, limits exceeded), 2 = FAIL (strict).
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# token -> per-1000-word limit
LIMITS = {
    "furthermore": 2.0, "moreover": 2.0, "此外": 2.0, "其次，": 2.0,
    "notably": 1.0, "crucially": 1.0, "值得一提的是": 1.0, "值得注意的是": 1.0,
    "significantly": 1.0, "显著地": 1.0,
    "delve": 0.0, "it is worth noting": 0.0, "it should be noted": 0.0,
    "in conclusion": 0.0, "综上所述": 0.0,
}
EM_DASH_RE = re.compile(r"[—–]|(?<!-)--(?!-)")

def count_words(text: str) -> int:
    # CJK chars count as words; latin runs count as one word each
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3000-\u303f]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text))
    return cjk + latin


def analyze(text: str) -> dict:
    lower = text.lower()
    words = max(count_words(text), 1)
    hits = []
    for token, limit in LIMITS.items():
        count = lower.count(token.lower())
        allowed = limit * words / 1000.0
        ok = count <= allowed
        hits.append({"token": token, "count": count, "limit_per_1k": limit,
                     "observed_per_1k": round(count * 1000.0 / words, 2), "ok": ok})
    em = len(EM_DASH_RE.findall(text))
    em_limit = 2.0 * words / 1000.0
    hits.append({"token": "em-dash", "count": em, "limit_per_1k": 2.0,
                 "observed_per_1k": round(em * 1000.0 / words, 2), "ok": em <= em_limit})
    problems = [h for h in hits if not h["ok"]]
    verdict = "PASS" if not problems else "WARN"
    return {"word_count": words, "verdict": verdict, "hits": hits, "problems": problems}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="text file to scan (default: stdin)")
    ap.add_argument("--strict", action="store_true", help="exit 2 when any limit is exceeded")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    a = ap.parse_args()
    text = Path(a.file).read_text(encoding="utf-8") if a.file else sys.stdin.read()
    report = analyze(text)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for h in report["hits"]:
            flag = "OK " if h["ok"] else ">> "
            print(f"{flag}{h['token']:<24} {h['count']:>3}  (limit {h['limit_per_1k']}/1k, "
                  f"observed {h['observed_per_1k']}/1k)")
        print(f"verdict: {report['verdict']}")
    if not report["problems"]:
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
