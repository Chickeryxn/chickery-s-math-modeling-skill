#!/usr/bin/env python3
"""Claim coverage check: every subquestion must have a paper section, frozen
numbers, and an abstract that states at least one of its frozen numbers.

Reads:
- planning/parse/problem_parse.json  -> subquestions[].id (Qx list);
- paper/sections/*.tex               -> sections (filename `q1.tex` or section
  headings containing 问题一 / Q1 / Q1.);
- results/*/reports/frozen_numbers.json -> claim values (prefix `q1_` maps to Q1);
- the abstract (LaTeX abstract env or Markdown Abstract/摘要 heading) for
  per-subquestion number coverage.

The abstract check only reads the abstract region. When no abstract region
exists, or when the parse file is missing, that is reported explicitly as
"unverifiable" instead of silently passing on whole-text numbers or a Q1
fallback.

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

SECTION_RE = re.compile(r"\\section\*?\{([^}]*)\}", flags=re.S)
LATEX_ABSTRACT_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", flags=re.S)
MD_ABSTRACT_RE = re.compile(
    r"(?:^|\n)(#{1,3}\s*(?:Abstract|摘要)\s*\n+)(.*?)(?=\n#{1,3}|\Z)", flags=re.S)
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
# A number immediately followed by % / ％ denotes a percentage in the text.
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[%％]")

# Chinese numerals used in section headings such as 问题一 / 问题十二.
_CN_DIGITS = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn_num_to_arabic(token: str) -> str:
    """Map a small Chinese numeral token (1..99) to Arabic digits.

    Handles single digits (一..九), tens (十, 二十, 十二, 二十一), and bare
    ASCII digits (already Arabic). Larger numbers are not expected in contest
    subquestion labels; on any unhandled shape the token is returned as-is so
    callers keep a stable, non-crashing fallback.
    """
    t = token.strip()
    if not t:
        return t
    if t.isdigit():
        return t
    if "十" not in t:
        if len(t) == 1 and t in _CN_DIGITS:
            return str(_CN_DIGITS[t])
        return t  # unhandled shape (e.g. 百/千) -> keep verbatim
    head, _, tail = t.partition("十")
    tens = _CN_DIGITS.get(head, 1) if head else 1
    units = _CN_DIGITS.get(tail, 0) if tail else 0
    return str(tens * 10 + units)


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
                found.append("Q" + cn_num_to_arabic(mm.group(1)))
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


def frozen_values_per_qid(root: Path) -> dict[str, list[float]]:
    """Map each subquestion to the numeric values of its frozen claims."""
    out: dict[str, list[float]] = {}
    for p in sorted((root / "results").glob("*/reports/frozen_numbers.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        claims = data.get("claims") if isinstance(data, dict) else None
        if not isinstance(claims, list):
            claims = [v for k, v in data.items()
                      if isinstance(v, dict) and "claim_id" in v] if isinstance(data, dict) else []
        for c in claims:
            if not isinstance(c, dict):
                continue
            cid = c.get("claim_id")
            v = c.get("value")
            if not cid:
                continue
            m = re.match(r"(q\d+|Q\d+)", str(cid))
            qid = m.group(1).upper() if m else "GLOBAL"
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.setdefault(qid, []).append(float(v))
    return out


def extract_abstract_region(sections_text: str) -> str | None:
    """Return the abstract region only, or None when no abstract exists."""
    m = LATEX_ABSTRACT_RE.search(sections_text)
    if m:
        return m.group(1)
    m = MD_ABSTRACT_RE.search(sections_text)
    if m:
        return m.group(2)
    return None


def _round_candidates(v: float) -> list[float]:
    """Values a paper may legitimately write for frozen value v by rounding it
    to 0..6 decimal places (0.1234 -> 0.123, 2.4 -> 2.4)."""
    return [round(v, d) for d in range(7)]


def _abstract_states_frozen_number(abstract: str, values: list[float]) -> bool:
    """True when the abstract restates at least one frozen value.

    Accepts exact matches, values rounded to a plausible number of decimals
    (abstracts routinely write 0.123 for a frozen 0.1234), and percentage
    restatements (a frozen proportion 0.05 written as "低于5%"). A plain
    *different* number (9.99 for 2.4) still fails.
    """
    plain = [float(t) for t in NUMBER_RE.findall(abstract)]
    percent = [float(t) / 100.0 for t in PERCENT_RE.findall(abstract)]
    for v in values:
        if any(abs(t - v) <= max(1e-9, 1e-6 * abs(v)) for t in plain):
            return True
        candidates = _round_candidates(v)
        if any(abs(t - c) <= 1e-9 for c in candidates for t in plain):
            return True
        if any(abs(t - v) <= max(1e-9, 1e-6 * abs(v)) for t in percent):
            return True
    return False


def coverage(root: Path) -> dict:
    qids = load_subquestions(root)
    sections = section_qids(root)
    frozen = frozen_per_qid(root)
    values = frozen_values_per_qid(root)
    section_files = sorted((root / "paper" / "sections").glob("*.tex"))
    sections_text = "".join(p.read_text(encoding="utf-8-sig") for p in section_files)
    abstract = extract_abstract_region(sections_text)
    abstract_numbers = len(NUMBER_RE.findall(abstract)) if abstract else 0
    matrix = []
    missing = []
    if abstract is None:
        missing.append("abstract section not found "
                       "(per-subquestion number coverage unverifiable)")
    if not qids:
        if not (root / "planning" / "parse" / "problem_parse.json").is_file():
            missing.append("planning/parse/problem_parse.json missing "
                           "(cannot verify per-subquestion coverage)")
        else:
            missing.append("problem_parse.json declares no subquestions "
                           "(cannot verify per-subquestion coverage)")
    for qid in qids:
        has_section = any(qid in v for v in sections.values())
        q_values = values.get(qid, [])
        n_frozen = len(frozen.get(qid, []))
        stated = (abstract is not None and q_values
                  and _abstract_states_frozen_number(abstract, q_values))
        row = {"question": qid, "section": "PRESENT" if has_section else "MISSING",
               "frozen_count": n_frozen, "frozen_ok": n_frozen > 0,
               "abstract_states_frozen_number": stated}
        matrix.append(row)
        if not has_section:
            missing.append(f"{qid}: no paper section")
        if n_frozen == 0:
            missing.append(f"{qid}: no frozen numbers")
        elif abstract is not None and not stated:
            sample = ", ".join(str(v) for v in q_values[:3])
            missing.append(f"{qid}: abstract states none of its frozen numbers ({sample})")
    if abstract is not None and abstract_numbers == 0:
        missing.append("abstract has no numbers")
    return {"subquestions": qids, "abstract_numbers": abstract_numbers,
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
