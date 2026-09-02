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
    """Collect frozen claims across per-question files.

    Raises ValueError when the same claim_id appears in more than one frozen
    file (previously the later file silently overwrote the earlier claim).
    """
    out = {}
    seen_at = {}
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
                cid = c["claim_id"]
                if cid in out:
                    raise ValueError(
                        f"duplicate claim_id {cid!r} in {p} (first seen in "
                        f"{seen_at[cid]}) — frozen claim ids must be unique across "
                        "results/*/reports/frozen_numbers.json")
                out[cid] = c
                seen_at[cid] = p.relative_to(root).as_posix()
    return out


def sanitize_macro_name(name: str) -> str:
    import hashlib
    clean = re.sub(r"[^A-Za-z0-9]", "", name)
    if clean:
        if clean[0].isdigit():
            # LaTeX control words cannot start with a digit (\2000cap is
            # invalid); prefix so digit-led claim ids still compile.
            return "fz" + clean
        return clean
    # All-symbol ids would all collapse to the same name; make it unique.
    return "frozenvalue" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]


def macro_name_for(claim_id: str, used: set[str]) -> str:
    """Return a unique LaTeX macro name for a frozen claim.

    The name derives from the sanitized claim id (e.g. q1_main_rmse ->
    q1mainrmse) so existing papers keep compiling. When two claim ids fold
    onto the same sanitized name (q1_avg vs q1avg), the later one gets a
    short sha1 suffix instead of silently duplicating the \\newcommand.
    """
    base = sanitize_macro_name(claim_id)
    candidate = f"\\{base}"
    if candidate not in used:
        return candidate
    import hashlib
    digest = hashlib.sha1(claim_id.encode("utf-8")).hexdigest()[:8]
    return f"\\{base}{digest}"


def ai_declaration(root: Path) -> tuple[list[str], list[str]]:
    """Return (blocks, sources): AI-use declaration paragraphs + evidence paths.

    Only the first block carries the section heading; every additional block is
    a plain paragraph so multiple ledgers/disclosures never emit several
    same-named sections.
    """
    paragraphs, sources = [], []
    disclosure = root / "paper" / "ai_use_disclosure.md"
    if disclosure.is_file():
        lines = [ln.strip() for ln in disclosure.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if lines:
            paragraphs.append("\n\n".join(lines))
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
                paragraphs.append(
                    "经参赛者确认：本文中的建模判断、结果判定、物理意义与贡献论述由作者完成；"
                    "AI 仅承担机械正确性工作（解析、编码、实验与整理）。"
                    + (f" 补充说明：{latex_escape(choice)}" if choice and choice != "ok" else "")
                )
                src = p.relative_to(root).as_posix()
                if src not in sources:
                    sources.append(src)
                break
    if not paragraphs:
        return [], []
    blocks = ["\\section*{AI 工具使用声明}\n" + paragraphs[0]] + paragraphs[1:]
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


def frozen_macro_map(frozen: dict) -> dict[str, str]:
    """Return {claim_id: "\\FZ..."} unique macro names for every claim whose
    value can be rendered as a macro (skipping dict/list/bool/None values)."""
    used: set[str] = set()
    out: dict[str, str] = {}
    for cid, c in sorted(frozen.items()):
        if macro_value(c) is None:
            continue
        name = macro_name_for(cid, used)
        used.add(name)
        out[cid] = name
    return out


def macros_for_frozen(frozen: dict) -> tuple[str, list[str]]:
    """Build the frozen-number macro block and the list of skipped claim ids."""
    lines, skipped = [], []
    mapping = frozen_macro_map(frozen)
    for cid, c in sorted(frozen.items()):
        val = macro_value(c)
        if val is None:
            skipped.append(cid)
            continue
        unit = latex_escape(str(c.get("unit", ""))) if c.get("unit") else ""
        # Embed any unit inside the macro body: appending it after the closing
        # brace would emit stray text at the definition site (e.g. in the
        # preamble) instead of traveling with the value.
        body = f"{val}\\,{unit}" if unit else val
        lines.append(f"\\newcommand{{{mapping[cid]}}}{{{body}}}")
    return "\n".join(lines), skipped


BIB_ENTRY_START_RE = re.compile(r"@(\w+)\s*\{")
BIB_SKIP_TYPES = {"comment", "string", "preamble", "xdata"}
# entry types allowed as citations (everything else, incl. @string/@preamble
# and any @xxx comment-like entries, is not a bibliography item)
BIB_ALLOWED_TYPES = {"article", "book", "booklet", "inbook", "incollection",
                     "inproceedings", "conference", "manual", "mastersthesis",
                     "misc", "phdthesis", "proceedings", "techreport", "unpublished",
                     "online", "electronic", "www"}


def _bib_field_scan(segment: str) -> dict:
    """Extract top-level `key = {value}` fields from a bib entry body.

    Handles nested braces inside values (e.g. title with \\emph{...}) by
    scanning balanced braces instead of the flat regex the previous parser
    used (which truncated nested values at the first closing brace).
    """
    fields: dict[str, str] = {}
    i = 0
    n = len(segment)
    while i < n:
        while i < n and (segment[i].isspace() or segment[i] == ","):
            i += 1
        m = re.match(r"([A-Za-z0-9_\-]+)\s*=\s*\{", segment[i:])
        if not m:
            break
        key = m.group(1).lower()
        start = i + m.end()
        depth, j = 1, start
        while j < n and depth:
            if segment[j] == "{":
                depth += 1
            elif segment[j] == "}":
                depth -= 1
            j += 1
        if depth:
            break
        fields[key] = segment[start:j - 1].strip()
        i = j
    return fields


def parse_bib_to_bibitems(path: Path) -> list[str]:
    """Parse a small .bib file into \\bibitem entries (balanced-brace scan).

    Only real citation entry types are converted; @comment/@string/@preamble
    and other non-citation entries are ignored.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    items = []
    for m in BIB_ENTRY_START_RE.finditer(text):
        entry_type = m.group(1).lower()
        if entry_type not in BIB_ALLOWED_TYPES:
            continue
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
        fields = _bib_field_scan(text[key_end + 1:j - 1])
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


def strip_latex_comment(line: str) -> str:
    """Strip a trailing LaTeX comment (% to end of line).

    A '%' introduced by an even number of preceding backslashes is literal
    (e.g. \\% in text); an odd-count backslash (\\%) is an escaped percent
    that does not start a comment, so only a '%' preceded by an even number
    of backslashes (including zero) starts a comment.
    """
    for i, ch in enumerate(line):
        if ch != "%":
            continue
        backslashes = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return line[:i]
    return line


def scan_bare_numbers(root: Path, section_refs: list[str], frozen: dict, cap: int = 20) -> dict:
    """Heuristically find bare numbers in the sections that do not match any
    frozen macro value. Advisory only: years and non-data numbers are skipped.
    Returns {count, sample: [...]}."""
    macro_values = set()
    for cid, c in sorted(frozen.items()):
        if macro_value(c) is None:
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
            # strip LaTeX comments so commented-out numbers are not reported
            line = strip_latex_comment(line)
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
    warnings = []
    text = "\n".join(
        (root / s).read_text(encoding="utf-8-sig") for s in section_refs if (root / s).is_file()
    )
    mapping = frozen_macro_map(frozen)
    for cid, macro in sorted(mapping.items()):
        if macro in text:
            continue
        val = frozen[cid].get("value")
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
    placeholders = ("__INPUTS__", "__FROZEN_MACROS__", "__AI_DECLARATION__", "__REFERENCES__")
    missing = [p for p in placeholders if p not in template_text]
    if missing:
        raise ValueError(
            f"template {template} is missing injection point(s): {', '.join(missing)} — "
            "refusing to assemble a document with unresolved placeholders")
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
    total_chars = sum(len((root / s).read_text(encoding="utf-8-sig"))
                      for s in section_refs if (root / s).is_file())
    mapping = frozen_macro_map(frozen)
    skipped = [cid for cid in frozen if cid not in mapping]
    bibitems = parse_bib_to_bibitems(root / "paper" / "refs.bib")
    return {
        "schema_version": 1,
        "sections": section_refs,
        "section_count": len(section_refs),
        "frozen_macros": sorted(mapping[cid].lstrip("\\") for cid in mapping),
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
                            encoding="utf-8", newline="\n")
        (root / "paper" / "build_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
            newline="\n")
        print(json.dumps({"status": "PASS", "main_tex": str(main_tex.relative_to(root)),
                          **report}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
