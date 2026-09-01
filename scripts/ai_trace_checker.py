#!/usr/bin/env python3
"""Quantifiable AI-trace checker for academic text.

Counts AI-sounding words/phrases and em-dash frequency against absolute
whole-text limits inspired by de-AI-writing methodology (see
`references/upstream/lupynow-writing/de-ai-writing.md`). Pure standard library.

Rules (self-authored subset, aligned with the upstream caps):
  - `furthermore` / `moreover` / 此外 : <= 2 total; furthermore+moreover combined <= 2
  - `notably` / `crucially` / 值得一提的是 / 值得注意的是 : <= 1 total
  - `significantly` / 显著地 / 关键的 : <= 1 total
  - zero-tolerance phrases: `delve`, `it is worth noting`, `it should be noted`,
    `in conclusion`, `综上所述`, `深入探讨`, `重要的是`, `不可忽视的`, `高度复杂的`
  - em dash `--`/`—` : <= 2 total

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

# token -> absolute count limit for the whole text (aligned with the upstream
# de-ai-writing caps, e.g. "此外 全文 ≤2 次", "moreover+furthermore 合计 ≤2")
LIMITS = {
    "furthermore": 2, "moreover": 2, "此外": 2, "其次，": 2,
    "notably": 1, "crucially": 1, "值得一提的是": 1, "值得注意的是": 1,
    "significantly": 1, "显著地": 1, "关键的": 1,
    "delve": 0, "it is worth noting": 0, "it should be noted": 0,
    "in conclusion": 0, "综上所述": 0,
    "深入探讨": 0, "重要的是": 0, "不可忽视的": 0, "高度复杂的": 0,
}
# grouped tokens -> combined absolute limit
GROUPS = [
    (["furthermore", "moreover"], 2),   # upstream de-ai-writing: moreover+furthermore <= 2 total
]
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
        hits.append({"token": token, "count": count, "limit": limit, "ok": count <= limit})
    for group, limit in GROUPS:
        count = sum(lower.count(t.lower()) for t in group)
        hits.append({"token": "+".join(group) + " (combined)", "count": count,
                     "limit": limit, "ok": count <= limit})
    em = len(EM_DASH_RE.findall(text))
    hits.append({"token": "em-dash", "count": em, "limit": 2, "ok": em <= 2})
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
            print(f"{flag}{h['token']:<32} {h['count']:>3}  (limit {h['limit']})")
        print(f"verdict: {report['verdict']}")
    if not report["problems"]:
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
