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


def render_main(template: Path, root: Path, section_refs: list[str], frozen: dict,
                ai_blocks: list[str]) -> str:
    template_text = template.read_text(encoding="utf-8")
    inputs = "\n".join(f"\\input{{{ref}}}" for ref in section_refs)
    macros = "\n".join(
        f"\\newcommand{{\\{sanitize_macro_name(cid)}}}"
        f"{{{c.get('value')}}}" + (f"\\text{{{c.get('unit','')}}}" if c.get("unit") else "")
        for cid, c in sorted(frozen.items())
    )
    ai = "\n\n".join(ai_blocks)
    return (
        template_text
        .replace("__INPUTS__", inputs)
        .replace("__FROZEN_MACROS__", macros)
        .replace("__AI_DECLARATION__", ai)
    )


def build_report(root: Path, section_refs: list[str], frozen: dict, sources: list[str]) -> dict:
    total_chars = sum((root / s).stat().st_size for s in section_refs if (root / s).is_file())
    return {
        "schema_version": 1,
        "sections": section_refs,
        "section_count": len(section_refs),
        "frozen_macros": sorted(sanitize_macro_name(cid) for cid in frozen),
        "frozen_count": len(frozen),
        "ai_declaration_sources": sources,
        "approx_paper_chars": total_chars,
        "approx_pages_est": max(1, round(total_chars / 1600)),  # rough CJK chars/page
        "note": "Page estimate is a rough guide; enforce contest limits with a LaTeX build audit.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--dry-run", action="store_true")
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
        if a.dry_run:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        main_tex = root / "paper" / "main.tex"
        main_tex.write_text(render_main(template, root, sections, frozen, ai_blocks), encoding="utf-8")
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
