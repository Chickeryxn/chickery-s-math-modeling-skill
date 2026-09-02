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
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SECTIONS_GLOB = "paper/sections/*"
FIGURES_DIR = "paper/figures"


def _norm(name: str) -> str:
    n = name.strip()
    n = n.replace("\\", "/")
    n = n.split("#")[0].split("?")[0]
    n = n.lstrip("./")
    if n.startswith("paper/figures/"):
        n = n[len("paper/figures/"):]
    elif n.startswith("figures/"):
        n = n[len("figures/"):]
    return n


def audit(root: Path) -> dict:
    r = root.resolve()
    figures_dir = r / FIGURES_DIR
    present = {}
    if figures_dir.is_dir():
        for p in figures_dir.glob("*"):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                present[p.name] = p
    referenced, errors, advisory = [], [], []
    for section in sorted(r.glob(SECTIONS_GLOB)):
        if not section.is_file() or section.suffix.lower() not in {".tex", ".md", ".txt"}:
            continue
        text = section.read_text(encoding="utf-8-sig")
        names = (_norm(m) for m in
                 INCLUDEGRAPHICS_RE.findall(text) + MARKDOWN_IMAGE_RE.findall(text))
        for name in names:
            if not name:
                continue
            referenced.append({"figure": name,
                               "section": section.relative_to(r).as_posix()})
            fig = present.get(name) or present.get(Path(name).name)
            if fig is None:
                errors.append({"figure": name,
                               "section": section.relative_to(r).as_posix(),
                               "reason": "referenced figure not found under paper/figures"})
                continue
            evidence = fig.parent / (fig.name + ".render.json")
            if not evidence.is_file():
                errors.append({"figure": name,
                               "section": section.relative_to(r).as_posix(),
                               "reason": "missing render evidence " + evidence.relative_to(r).as_posix()})
                continue
            try:
                ev = json.loads(evidence.read_text(encoding="utf-8-sig"))
            except Exception:
                errors.append({"figure": name, "section": section.relative_to(r).as_posix(),
                               "reason": "render evidence is not valid JSON"})
                continue
            if ev.get("status") != "PASS" or not ev.get("rendered_at"):
                errors.append({"figure": name, "section": section.relative_to(r).as_posix(),
                               "reason": "render evidence not PASS or missing rendered_at"})
    referenced_names = {x["figure"] for x in referenced}
    unreferenced = sorted(set(present) - referenced_names)
    return {"status": "PASS" if not errors else "FAIL",
            "referenced": referenced,
            "unreferenced_figures": unreferenced,
            "errors": errors,
            "checked_figures": len(present)}


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
