#!/usr/bin/env python3
"""Scan resource-library/ and (re)build index.json (pure standard library).

Categories are the subdirectories of resource-library (papers/ideas/figures/
formulas/tables/assets/...). Each entry is a file under a category; README.md
files are treated as documentation and listed separately.

Commands:
  python scripts/resource_index.py <root>            # rebuild index.json
  python scripts/resource_index.py <root> --check    # verify index matches disk
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


def _utf8_streams() -> None:
    """Force UTF-8 on std streams when run as a CLI (import-time safe).

    Never call this at import time: tests import this module, and changing
    the test process's stream encoding would break GBK-decodable output
    captured by scripts/validate_repo.py.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DOC_FILES = {"README.md", "index.json"}
SKIP_NAMES = {".gitkeep", ".DS_Store"}


def scan(root: Path) -> dict:
    lib = root / "resource-library"
    categories = {}
    if lib.is_dir():
        for sub in sorted(p for p in lib.iterdir() if p.is_dir()):
            entries, docs = [], []
            for f in sorted(sub.iterdir()):
                if not f.is_file() or f.name in SKIP_NAMES:
                    continue
                if f.name in DOC_FILES:
                    docs.append(f.name)
                else:
                    entries.append(f.name)
            if entries or docs:
                categories[sub.name] = {"entries": entries, "docs": docs}
    return {"schema_version": 1, "categories": categories}


def main():
    _utf8_streams()
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--check", action="store_true", help="verify index.json matches disk")
    a = ap.parse_args()
    root = a.root.resolve()
    lib = root / "resource-library"
    if not lib.is_dir():
        print("resource-library/ missing", file=sys.stderr)
        return 2
    data = scan(root)
    index = lib / "index.json"
    if a.check:
        if not index.is_file():
            print("index.json missing", file=sys.stderr)
            return 2
        try:
            existing = json.loads(index.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            print(f"index.json invalid: {exc}", file=sys.stderr)
            return 2
        if existing != data:
            print("index.json out of sync - run resource_index.py (no --check)", file=sys.stderr)
            return 2
        print(json.dumps({"status": "PASS", "categories": len(data["categories"])}, ensure_ascii=False))
        return 0
    index.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "WRITTEN", "categories": {k: len(v["entries"]) for k, v in data["categories"].items()}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
