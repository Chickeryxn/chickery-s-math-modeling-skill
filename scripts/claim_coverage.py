#!/usr/bin/env python3
"""Claim coverage check: every subquestion must have a paper section, frozen
numbers, and abstract coverage.

Reads:
- planning/parse/problem_parse.json  -> subquestions[].id (Qx list);
- paper/sections/*.tex               -> sections (filename `q1.tex` or section
  headings containing 问题一 / Q1 / Q1.);
- results/*/reports/frozen_numbers.json -> claim_ids (prefix `q1_` maps to Q1);
- the abstract (LaTeX abstract env or Markdown Abstract/摘要 heading) for
  per-subquestion number coverage.

Pure standard library. Exit: 0 all covered, 1 partial, 2 strict-missing.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import sys as _sys
from pathlib import Path as _P
if str(_P(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(_P(__file__).resolve().parent))
from abstract_checker import extract_abstract

SECTION_RE = re.compile(r"\\section\*?\{([^}]*)\}", flags=re.S)


def load_subquestions(root: Path) -> list[str]:
    p = root / "planning" / "parse" / "problem_parse.json"
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    subs = data.get("subquestions") or []
    return [str(s.get("id")) for s in subs if isinstance(s, dict) and s.get("id")]


def section_qids(root: Path) -> dict[str, str]:
    """Map section path -> detected subquestion id(s) from filename and headings."""
    out = {}
    for p in sorted((root / "paper" / "sections").glob("*.tex")):
        text = p.read_text(encoding="utf-8-sig")
        found = []
        name = p.stem.lower()
        m = re.search(r"q(\d+)", name)
        if m:
            found.append("Q" + m.group(1))
        for title in SECTION_RE.findall(text):
            t = title.strip()
            mm = re.search(r"(?:问题|Q)\s*([一二三四五六七八九十0-9]+)", t)
            if mm:
                found.append("Q" + mm.group(1))
        out[p.name] = sorted(set(found))
    return out


def frozen_per_qid(root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted((root / "results").glob("*/reports/frozen_numbers.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        claims = data.get("claims") if isinstance(data, dict) else None
        if not isinstance(claims, list):
            claims = [v for k, v in data.items() if isinstance(v, dict) and "claim_id" in v] if isinstance(data, dict) else []
        for c in claims:
            cid = c.get("claim_id") if isinstance(c, dict) else None
            if not cid:
                continue
            m = re.match(r"(q\d+|Q\d+)", str(cid))
            qid = m.group(1).upper() if m else "GLOBAL"
            out.setdefault(qid, []).append(str(cid))
    return out


def coverage(root: Path) -> dict:
    qids = load_subquestions(root)
    sections = section_qids(root)
    frozen = frozen_per_qid(root)
    # abstract numbers
    abstract_text = ""
    for p in sorted((root / "paper" / "sections").glob("*.tex")):
        abstract_text += extract_abstract(p.read_text(encoding="utf-8-sig")) + "\n"
    abstract_numbers = len(re.findall(r"\d+(?:\.\d+)?", abstract_text))
    matrix = []
    missing = []
    for qid in qids or ["Q1"]:
        has_section = any(qid in v for v in sections.values())
        n_frozen = len(frozen.get(qid, []))
        row = {"question": qid, "section": "PRESENT" if has_section else "MISSING",
               "frozen_count": n_frozen, "frozen_ok": n_frozen > 0}
        matrix.append(row)
        if not has_section:
            missing.append(f"{qid}: no paper section")
        if n_frozen == 0:
            missing.append(f"{qid}: no frozen numbers")
    if abstract_numbers == 0:
        missing.append("abstract has no numbers (per-subquestion coverage unverifiable)")
    return {"subquestions": qids or ["Q1"], "abstract_numbers": abstract_numbers,
            "matrix": matrix, "missing": missing,
            "status": "PASS" if not missing else "PARTIAL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit 2 when anything is missing")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    report = coverage(a.root.resolve())
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for row in report["matrix"]:
            print(f"{row['question']}: section={row['section']} frozen={row['frozen_count']}")
        print(f"abstract numbers: {report['abstract_numbers']}")
        for m in report["missing"]:
            print(">>", m)
    if report["status"] == "PASS":
        return 0
    return 2 if a.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
