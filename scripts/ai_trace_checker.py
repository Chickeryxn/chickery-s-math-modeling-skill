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
  - em dash (2+ consecutive hyphens count as one usage; a CJK `——`/`――`
    double-dash — one typographic unit — also counts once): <= 2 total

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
# Runs of CJK dashes (——, ――) or ASCII hyphens (--, ---) each count as ONE
# em-dash usage: a CJK double-dash is a single typographic unit, and upstream
# caps are per usage, not per character. Single —/– still count individually.
EM_DASH_RE = re.compile(r"[—–]{2,}|[—–]|(?<!-)-{2,}(?!-)")

def count_words(text: str) -> int:
    # CJK ideographs count as words; latin runs count as one word each.
    # CJK punctuation (、。！？；：""'' …—) is NOT a word and must not inflate
    # word counts used for abstract length bounds.
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text))
    return cjk + latin


def analyze(text: str, limits=None, groups=None, em_dash_limit: int = 2) -> dict:
    lower = text.lower()
    words = max(count_words(text), 1)
    limits = limits if limits is not None else LIMITS
    groups = groups if groups is not None else GROUPS
    hits = []
    for token, limit in limits.items():
        count = lower.count(token.lower())
        hits.append({"token": token, "count": count, "limit": limit, "ok": count <= limit})
    for group, limit in groups:
        count = sum(lower.count(t.lower()) for t in group)
        hits.append({"token": "+".join(group) + " (combined)", "count": count,
                     "limit": limit, "ok": count <= limit})
    em = len(EM_DASH_RE.findall(text))
    hits.append({"token": "em-dash", "count": em, "limit": em_dash_limit, "ok": em <= em_dash_limit})
    problems = [h for h in hits if not h["ok"]]
    verdict = "PASS" if not problems else "WARN"
    return {"word_count": words, "verdict": verdict, "hits": hits, "problems": problems}


def load_config(path: Path) -> dict:
    """Load an optional JSON config: {"limits": {...}, "groups": [[...], n], "em_dash_limit": n}."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    cfg = {}
    if isinstance(data.get("limits"), dict):
        cfg["limits"] = {str(k): int(v) for k, v in data["limits"].items()}
    raw_groups = data.get("groups")
    if isinstance(raw_groups, list):
        parsed_groups = []
        well_formed = True
        for g in raw_groups:
            if (isinstance(g, list) and len(g) == 2 and isinstance(g[0], list)
                    and all(isinstance(t, str) for t in g[0]) and isinstance(g[1], int)):
                parsed_groups.append(([str(t) for t in g[0]], int(g[1])))
            else:
                well_formed = False
                break
        if well_formed and parsed_groups:
            cfg["groups"] = parsed_groups
    if isinstance(data.get("em_dash_limit"), int):
        cfg["em_dash_limit"] = data["em_dash_limit"]
    return cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="text file to scan (default: stdin)")
    ap.add_argument("--strict", action="store_true", help="exit 2 when any limit is exceeded")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    ap.add_argument("--config", type=Path, default=None,
                    help="JSON config overriding limits/groups/em_dash_limit")
    a = ap.parse_args()
    if a.file:
        try:
            text = Path(a.file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read input file: {exc}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    cfg = load_config(a.config) if a.config else {}
    report = analyze(text, **cfg)
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
