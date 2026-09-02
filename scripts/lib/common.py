#!/usr/bin/env python3
"""Shared stdlib helpers for scripts/ (import-safe).

Importing this module has NO side effects: it never reconfigures stream
encodings (scripts that want UTF-8 output should call `utf8_streams()` from
their `main()` or `if __name__` guard, never at import time — reconfiguring at
import time breaks GBK test captures, see resource_index/training_scorecard).
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path


def utf8_streams() -> None:
    """Force UTF-8 on stdout/stderr; safe to call once per process."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_path(root: Path, raw: str) -> Path:
    """Resolve a project-relative path and enforce containment inside root.

    Both sides are resolved before the containment check: on Windows a root
    carrying an 8.3 short name (RUNNER~1) vs a resolve()-expanded long-name
    candidate used to make relative_to() raise spuriously.
    """
    root = root.resolve()
    p = (root / raw).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        raise ValueError(f"path escapes project root: {raw}")
    return p


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def frozen_claims(data) -> list[dict]:
    """Normalize the two frozen_numbers shapes into a list of claim dicts.

    Accepts {"claims": [...]} and {claim_id: {...}} map shapes.
    """
    if not isinstance(data, dict):
        return []
    claims = data.get("claims")
    if isinstance(claims, list):
        return [c for c in claims if isinstance(c, dict) and c.get("claim_id")]
    return [v for k, v in data.items() if isinstance(v, dict) and "claim_id" in v]


FROZEN_GLOB = "results/*/reports/frozen_numbers.json"
