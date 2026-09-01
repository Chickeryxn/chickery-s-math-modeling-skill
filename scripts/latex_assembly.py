#!/usr/bin/env python3
"""Assemble contest paper sections into a main LaTeX document.

Pure standard library. Behavior:
- Scans `paper/sections/*.tex` in filename order and builds a main document
  that inputs them (sections are expected to be input-ready fragments).
- Injects frozen numbers from `results/*/reports/frozen_numbers.json` as
  \\newcommand macros (one per claim_id) so the paper sources every number
  from the freeze contract.
- Emits an AI-use declaration block driven by the decision ledgers
  (`methods/*/q*_decisions.jsonl`, type `submission_authorization`) plus an
  optional user-provided `paper/ai_use_disclosure.md`.
- `--dry-run` prints the assembly plan without writing files.
- A custom template may be supplied with `--template`; the default is the
  clean-room baseline under `templates/paper/main.tex` (no upstream template
  code is vendored — see docs/paper-build.md).

Exit codes: 0 ok, 2 usage/environment error (missing LaTeX template guidance).
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SECTION_GLOB = "paper/sections/*.tex"
FROZEN_GLOB = "results/*/reports/frozen_numbers.json"
LEDGER_GLOB = "methods/*/q*_decisions.jsonl"


def scan_sections(root: Path) -> list[str]:
    paths = sorted(p for p in root.glob(SECTION_GLOB))
    return [p.relative_to(root).as_posix() for p in paths]


def load_frozen_numbers(root: Path) -> dict:
    out = {}
    for p in sorted(root.glob(FROZEN_GLOB)):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            raise ValueError(f"invalid frozen numbers file {p}: {exc}")
        claims = data.get("claims") if isinstance(data, dict) else None
        if not isinstance(claims, list):
            # tolerate {"claim_id": {...}, ...} maps as well as {"claims": [...]}
            claims = [v for k, v in data.items() if isinstance(v, dict) and "claim_id" in v] if isinstance(data, dict) else []
        for c in claims:
            if isinstance(c, dict) and c.get("claim_id") and "value" in c:
                out[c["claim_id"]] = c
    return out


def sanitize_macro_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name) or "frozenvalue"


def ai_declaration(root: Path) -> tuple[list[str], list[str]]:
    """Return (blocks, sources): AI-use declaration paragraphs + evidence paths."""
    blocks, sources = [], []
    disclosure = root / "paper" / "ai_use_disclosure.md"
    if disclosure.is_file():
        lines = [ln.strip() for ln in disclosure.read_text(encoding="utf-8").splitlines() if ln.strip()]
        blocks.append("\\section*{AI 工具使用声明}\n" + "\n\n".join(lines))
        sources.append(disclosure.relative_to(root).as_posix())
    for p in sorted(root.glob(LEDGER_GLOB)):
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("decision_type") == "submission_authorization" and rec.get("status") == "DECIDED":
                choice = str(rec.get("choice", ""))
                blocks.append(
                    "\\section*{AI 工具使用声明}\n"
                    "经参赛者确认：本文中的建模判断、结果判定、物理意义与贡献论述由作者完成；"
                    "AI 仅承担机械正确性工作（解析、编码、实验与整理）。"
                    + (f" 补充说明：{choice}" if choice and choice != "ok" else "")
                )
                src = p.relative_to(root).as_posix()
                if src not in sources:
                    sources.append(src)
                break
    return blocks, sources


LATEX_SPECIALS = str.maketrans({
    "\\": r"\textbackslash{}",
    "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}", "$": r"\$",
})


def latex_escape(s: str) -> str:
    """Escape LaTeX special characters in a string value."""
    return s.translate(LATEX_SPECIALS)


def macro_value(c: dict):
    """Return a LaTeX-safe string for a frozen claim value, or None if unsafe."""
    v = c.get("value")
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return latex_escape(v)
    return None  # dict / list / other structured values are skipped


def macros_for_frozen(frozen: dict) -> tuple[str, list[str]]:
    """Build the frozen-number macro block and the list of skipped claim ids."""
    lines, skipped = [], []
    for cid, c in sorted(frozen.items()):
        val = macro_value(c)
        if val is None:
            skipped.append(cid)
            continue
        unit = latex_escape(str(c.get("unit", ""))) if c.get("unit") else ""
        lines.append(f"\\newcommand{{\\{sanitize_macro_name(cid)}}}{{{val}}}"
                     + (f"\\text{{{unit}}}" if unit else ""))
    return "\n".join(lines), skipped


BIB_ENTRY_START_RE = re.compile(r"@(\w+)\s*\{")
BIB_FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^}]*)\}", flags=re.S)


def parse_bib_to_bibitems(path: Path) -> list[str]:
    """Parse a small .bib file into \\bibitem entries (balanced-brace scan)."""
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    items = []
    for m in BIB_ENTRY_START_RE.finditer(text):
        start = m.end()
        key_end = text.find(",", start)
        if key_end < 0:
            continue
        key = text[start:key_end].strip()
        depth, j = 1, key_end + 1
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        if depth:
            continue
        fields = {k.lower(): v.strip() for k, v in BIB_FIELD_RE.findall(text[key_end + 1:j - 1])}
        author = fields.get("author", "")
        title = fields.get("title", "")
        year = fields.get("year", "")
        venue = (fields.get("journal") or fields.get("booktitle")
                 or fields.get("publisher") or fields.get("howpublished") or "")
        parts = [p for p in (author, title, venue, year) if p]
        items.append(f"\\bibitem{{{key}}} {'. '.join(parts)}")
    return items


NUMBER_TOKEN_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
YEAR_RE = re.compile(r"^(19|20)\d{2}$")


def scan_bare_numbers(root: Path, section_refs: list[str], frozen: dict, cap: int = 20) -> dict:
    """Heuristically find bare numbers in the sections that do not match any
    frozen macro value. Advisory only: years and non-data numbers are skipped.
    Returns {count, sample: [...]}."""
    _, skipped = macros_for_frozen(frozen)
    macro_values = set()
    for cid, c in sorted(frozen.items()):
        if cid in skipped:
            continue
        v = c.get("value")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            macro_values.add(str(v))
        elif isinstance(v, str):
            macro_values.add(v)
    sample, total = [], 0
    for s in section_refs:
        p = root / s
        if not p.is_file():
            continue
        for no, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1):
            if "\\" in line:
                # strip LaTeX comments (naive: from % to end of line)
                line = line.split("%", 1)[0]
            for m in NUMBER_TOKEN_RE.finditer(line):
                token = m.group(1)
                if YEAR_RE.match(token) or token in macro_values:
                    continue
                total += 1
                if len(sample) < cap:
                    sample.append(f"{s}:{no}: {token}")
    return {"count": total, "sample": sample}


def check_frozen_references(root: Path, section_refs: list[str], frozen: dict) -> list[str]:
    """Warn when a frozen claim is never referenced via its macro, or when its
    raw value appears as a bare number in the sections."""
    if not frozen:
        return []
    _, skipped = macros_for_frozen(frozen)
    warnings = []
    text = "\n".join(
        (root / s).read_text(encoding="utf-8-sig") for s in section_refs if (root / s).is_file()
    )
    for cid, c in sorted(frozen.items()):
        if cid in skipped:
            continue
        macro = "\\" + sanitize_macro_name(cid)
        if macro in text:
            continue
        val = c.get("value")
        raw = str(val) if isinstance(val, (int, float, str)) and not isinstance(val, bool) else None
        if raw and raw in text:
            warnings.append(
                f"frozen claim {cid}: raw value {raw!r} appears in the text; reference {macro} instead")
        else:
            warnings.append(f"frozen claim {cid}: never referenced via {macro} in the sections")
    return warnings


def estimate_pages(root: Path, section_refs: list[str]) -> int:
    """Rough page estimate: CJK chars / 850 + latin tokens / 1100 per A4 page."""
    cjk = latin = 0
    for s in section_refs:
        p = root / s
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8-sig")
        cjk += len(re.findall(r"[\u4e00-\u9fff]", t))
        latin += len(re.findall(r"[A-Za-z0-9]+", t))
    return max(1, round(cjk / 850 + latin / 1100))


def render_main(template: Path, root: Path, section_refs: list[str], frozen: dict,
                ai_blocks: list[str], bib_items: list[str] | None = None) -> str:
    template_text = template.read_text(encoding="utf-8")
    inputs = "\n".join(f"\\input{{{ref}}}" for ref in section_refs)
    macros, _ = macros_for_frozen(frozen)
    ai = "\n\n".join(ai_blocks)
    refs = "\n".join(bib_items or [])
    return (
        template_text
        .replace("__INPUTS__", inputs)
        .replace("__FROZEN_MACROS__", macros)
        .replace("__AI_DECLARATION__", ai)
        .replace("__REFERENCES__", refs)
    )


def build_report(root: Path, section_refs: list[str], frozen: dict, sources: list[str]) -> dict:
    total_chars = sum((root / s).stat().st_size for s in section_refs if (root / s).is_file())
    _, skipped = macros_for_frozen(frozen)
    bibitems = parse_bib_to_bibitems(root / "paper" / "refs.bib")
    return {
        "schema_version": 1,
        "sections": section_refs,
        "section_count": len(section_refs),
        "frozen_macros": sorted(sanitize_macro_name(cid) for cid in frozen if cid not in skipped),
        "frozen_count": len(frozen),
        "skipped_claims": skipped,
        "frozen_reference_warnings": check_frozen_references(root, section_refs, frozen),
        "bare_number_scan": scan_bare_numbers(root, section_refs, frozen),
        "bibitem_count": len(bibitems),
        "ai_declaration_sources": sources,
        "approx_paper_chars": total_chars,
        "approx_pages_est": estimate_pages(root, section_refs),
        "note": "Page estimate is a rough guide; enforce contest limits with a LaTeX build audit.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-only", action="store_true",
                    help="run all checks and print the report without writing paper/main.tex")
    ap.add_argument("--strict", action="store_true",
                    help="with --check-only: exit 2 when frozen-reference or bare-number findings exist")
    ap.add_argument("--template", type=Path, default=None)
    a = ap.parse_args()
    root = a.root.resolve()
    try:
        sections = scan_sections(root)
        if not sections:
            raise ValueError("no sections found under paper/sections/*.tex — run paper-section-writer first")
        frozen = load_frozen_numbers(root)
        ai_blocks, ai_sources = ai_declaration(root)
        template = (a.template.resolve() if a.template else root / "templates" / "paper" / "main.tex")
        if not template.is_file():
            raise ValueError(
                f"template not found: {template}\n"
                "Default clean-room baseline ships as templates/paper/main.tex; "
                "or supply --template (e.g. your own CUMCMThesis-based main.tex fetched per docs/paper-build.md)."
            )
        report = build_report(root, sections, frozen, ai_sources)
        bibitems = parse_bib_to_bibitems(root / "paper" / "refs.bib")
        if a.dry_run or a.check_only:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            if a.check_only and a.strict and (report["frozen_reference_warnings"]
                                              or report["bare_number_scan"]["count"] > 0):
                return 2
            return 0
        main_tex = root / "paper" / "main.tex"
        main_tex.write_text(render_main(template, root, sections, frozen, ai_blocks, bibitems),
                            encoding="utf-8")
        (root / "paper" / "build_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "main_tex": str(main_tex.relative_to(root)),
                          **report}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
