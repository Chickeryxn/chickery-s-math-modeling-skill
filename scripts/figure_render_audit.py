#!/usr/bin/env python3
"""Audit paper figures: every figure referenced by a paper section must exist
under paper/figures and carry a sibling <name>.render.json render-evidence
record produced by math-figure-generator (status PASS + rendered_at).

Advisory: figures present under paper/figures but never referenced are listed,
not failed. Pure standard library. Exit codes: 0 = clean; 2 = blocking issues.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps", ".tif", ".tiff"}
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\*)?(?:\[[^\]]*\])?\{([^}]+)\}")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SECTIONS_GLOB = "paper/sections/*"
FIGURES_DIR = "paper/figures"


def _strip_tex_comments(text: str) -> str:
    """Remove LaTeX comments (un-escaped % to end of line) and \\verb spans so
    commented-out or verbatim \\includegraphics calls are not counted."""
    import re as _re
    out_lines = []
    for line in text.splitlines():
        # drop \\verb|...| spans first (content is literal)
        line = _re.sub(r"\\verb[^a-zA-Z].*?[^a-zA-Z]", "", line)
        out = []
        i = 0
        while i < len(line):
            if line[i] == "%":
                backslashes = 0
                j = i - 1
                while j >= 0 and line[j] == "\\":
                    backslashes += 1
                    j -= 1
                if backslashes % 2 == 0:
                    break
            out.append(line[i])
            i += 1
        out_lines.append("".join(out))
    return "\n".join(out_lines)


def _norm(name: str):
    """Normalize a figure reference to a figures-relative posix path.

    Returns (path_or_None, reason_or_None). Leading './' is removed with
    removeprefix semantics; lstrip would also strip every leading '.' and '/'
    and fold '../outside.png' into 'outside.png'. References that are absolute
    or contain '..' components escape paper/figures and are rejected.
    """
    n = name.strip().replace("\\", "/")
    n = n.split("#")[0].split("?")[0].strip()
    if not n:
        return None, "empty figure reference"
    while n.startswith("./"):
        n = n[2:]
    if n.startswith("paper/figures/"):
        n = n[len("paper/figures/"):]
    elif n.startswith("figures/"):
        n = n[len("figures/"):]
    if n.startswith("/") or re.match(r"^[A-Za-z]:[/\\]", n):
        return None, f"absolute figure reference not allowed: {name!r}"
    if ".." in n.split("/"):
        return None, f"escaping figure reference not allowed: {name!r}"
    if not n:
        return None, "empty figure reference"
    return n, None


def audit(root: Path) -> dict:
    r = root.resolve()
    figures_dir = r / FIGURES_DIR
    present_rel: dict[str, Path] = {}
    base_counts: dict[str, int] = {}
    if figures_dir.is_dir():
        for p in figures_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                rel = p.relative_to(figures_dir).as_posix()
                present_rel[rel] = p
                base_counts[p.name] = base_counts.get(p.name, 0) + 1
    referenced, errors, advisory = [], [], []
    for section in sorted(r.glob(SECTIONS_GLOB)):
        if not section.is_file() or section.suffix.lower() not in {".tex", ".md", ".txt"}:
            continue
        text = section.read_text(encoding="utf-8-sig")
        if section.suffix.lower() == ".tex":
            text = _strip_tex_comments(text)
        raw_names = (INCLUDEGRAPHICS_RE.findall(text)
                     + MARKDOWN_IMAGE_RE.findall(text))
        for raw in raw_names:
            norm, reason = _norm(raw)
            if norm is None:
                errors.append({"figure": raw,
                               "section": section.relative_to(r).as_posix(),
                               "reason": reason})
                continue
            referenced.append({"figure": norm,
                               "section": section.relative_to(r).as_posix()})
            fig = present_rel.get(norm)
            if fig is None and Path(norm).suffix not in IMAGE_EXTS:
                # LaTeX frequently omits the extension: \includegraphics{q1_a}
                matches = []
                for ext in sorted(IMAGE_EXTS):
                    cand = norm + ext
                    if cand in present_rel:
                        matches.append(present_rel[cand])
                if len(matches) == 1:
                    fig = matches[0]
                elif len(matches) > 1:
                    errors.append({"figure": raw,
                                   "section": section.relative_to(r).as_posix(),
                                   "reason": "ambiguous extensionless reference"})
                    continue
            if fig is None and base_counts.get(Path(norm).name) == 1:
                # legacy basename-only lookup (unique basename)
                for k, p in present_rel.items():
                    if p.name == Path(norm).name:
                        fig = p
                        break
            elif fig is None and Path(norm).name in base_counts and base_counts[Path(norm).name] > 1:
                errors.append({"figure": raw,
                               "section": section.relative_to(r).as_posix(),
                               "reason": "ambiguous basename reference (duplicate figure names)"})
                continue
            if fig is None:
                errors.append({"figure": raw,
                               "section": section.relative_to(r).as_posix(),
                               "reason": "referenced figure not found under paper/figures"})
                continue
            evidence = fig.parent / (fig.name + ".render.json")
            if not evidence.is_file():
                errors.append({"figure": norm,
                               "section": section.relative_to(r).as_posix(),
                               "reason": "missing render evidence " + evidence.relative_to(r).as_posix()})
                continue
            try:
                ev = json.loads(evidence.read_text(encoding="utf-8-sig"))
            except Exception:
                errors.append({"figure": norm, "section": section.relative_to(r).as_posix(),
                               "reason": "render evidence is not valid JSON"})
                continue
            if ev.get("status") != "PASS" or not ev.get("rendered_at"):
                errors.append({"figure": norm, "section": section.relative_to(r).as_posix(),
                               "reason": "render evidence not PASS or missing rendered_at"})
    referenced_names = {x["figure"] for x in referenced}
    unreferenced = sorted(set(present_rel) - referenced_names)
    return {"status": "PASS" if not errors else "FAIL",
            "referenced": referenced,
            "unreferenced_figures": unreferenced,
            "errors": errors,
            "checked_figures": len(present_rel)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = audit(a.root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
