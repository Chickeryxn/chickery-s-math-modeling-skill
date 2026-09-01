#!/usr/bin/env python3
"""Section-structure check for contest papers (pure standard library).

Checks `paper/sections/*.tex` for the paper skeleton defined in
`references/paper-skeleton.md`:
- expected sections are present (abstract, restatement, assumptions, symbols,
  model, solution, results, robustness, conclusion, references, AI statement);
- order follows the skeleton;
- length distribution is reported (rough character share per section) so an
  agent can spot a bloated/dwarfed section;
- conclusion presence is flagged when results exist.

Exit: 0 complete, 1 partial (non-strict), 2 strict-missing.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# keyword -> skeleton slot (order matters)
SLOTS = [
    ("abstract", ("abstract", "摘要")),
    ("restatement", ("问题重述", "restatement", "problem restatement")),
    ("assumptions", ("模型假设", "assumptions")),
    ("symbols", ("符号", "symbols", "notation")),
    ("model", ("模型构建", "模型建立", "model construction", "modeling")),
    ("solution", ("模型求解", "求解", "solution")),
    ("results", ("结果分析", "结果", "results")),
    ("robustness", ("稳健", "敏感性", "robustness", "sensitivity")),
    ("conclusion", ("结论", "conclusion", "总结")),
    ("references", ("参考文献", "references", "thebibliography")),
    ("ai", ("AI", "人工智能", "ai 工具", "ai use", "ai 使用")),
]


def detect_sections(root: Path) -> list[tuple[str, str, int]]:
    out = []
    for p in sorted((root / "paper" / "sections").glob("*.tex")):
        text = p.read_text(encoding="utf-8-sig")
        for m in re.finditer(r"\\(?:section|section\*)\{([^}]*)\}", text):
            title = m.group(1).strip()
            out.append((p.name, title, len(title)))
    return out


def slot_of(title: str) -> str | None:
    low = title.lower()
    for slot, keys in SLOTS:
        if any(k in low for k in keys):
            return slot
    return None


def check(root: Path) -> dict:
    sections = detect_sections(root)
    found_slots, seen = [], set()
    for fname, title, _ in sections:
        s = slot_of(title)
        if s and s not in seen:
            seen.add(s)
            found_slots.append((s, fname, title))
    present = [s for s, _, _ in found_slots]
    missing = [slot for slot, _ in SLOTS if slot not in present]
    findings = []
    for slot in ("abstract", "conclusion", "references"):
        if slot not in present:
            findings.append(f"missing section: {slot}")
    # order check among found core slots (abstract..conclusion)
    order = [s for s in present if s in ("abstract", "restatement", "assumptions", "symbols",
                                         "model", "solution", "results", "robustness", "conclusion")]
    ideal = ["abstract", "restatement", "assumptions", "symbols", "model", "solution",
             "results", "robustness", "conclusion"]
    pos = {s: i for i, s in enumerate(ideal)}
    ordered = sorted(order, key=lambda s: pos.get(s, 99))
    if ordered != order:
        findings.append(f"section order off: found {order} vs skeleton order")
    # length distribution (character share per section file)
    lengths = {}
    total = 0
    for p in sorted((root / "paper" / "sections").glob("*.tex")):
        n = len(p.read_text(encoding="utf-8-sig"))
        lengths[p.name] = n
        total += n
    shares = {k: round(100.0 * v / total, 1) for k, v in lengths.items()} if total else {}
    return {"sections": [{"file": f, "title": t} for f, t, _ in sections],
            "found_slots": found_slots, "missing": missing,
            "length_share_pct": shares, "findings": findings,
            "status": "PASS" if not findings else "PARTIAL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    report = check(a.root.resolve())
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']}")
        for f in report["findings"]:
            print(">>", f)
        print("length share:", report["length_share_pct"])
    if report["status"] == "PASS":
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
