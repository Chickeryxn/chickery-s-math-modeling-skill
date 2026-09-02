#!/usr/bin/env python3
"""Check that frozen numbers are fresh: every frozen claim's canonical source
must still exist and must not be newer than the claim's frozen_at timestamp.

Closes the previously documented gap (AGENTS.md: "the frozen_at freshness rule
has no automatic checker yet"). Pure standard library.

Exit codes: 0 = all frozen claims current; 2 = at least one claim STALE
(missing source, source newer than frozen_at, or unparsable frozen_at).
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

FROZEN_GLOB = "results/*/reports/frozen_numbers.json"


def _parse_iso(value) -> datetime | None:
    try:
        s = str(value).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _claim_items(frozen_file: Path) -> list[dict]:
    """Accept the {"claims": [...]} shape and the {claim_id: {...}} map shape
    used by the rest of the toolchain."""
    try:
        data = json.loads(frozen_file.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    claims = data.get("claims")
    if isinstance(claims, list):
        return [c for c in claims if isinstance(c, dict) and c.get("claim_id")]
    return [v for k, v in data.items() if isinstance(v, dict) and "claim_id" in v]


def audit(root: Path) -> dict:
    stale, checked = [], 0
    files = sorted(root.glob(FROZEN_GLOB))
    for frozen_file in files:
        for claim in _claim_items(frozen_file):
            checked += 1
            claim_id = claim.get("claim_id")
            source = claim.get("source_file")
            frozen_at = claim.get("frozen_at")
            rel = frozen_file.relative_to(root).as_posix()
            if not isinstance(source, str) or not source.strip():
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": "missing source_file"})
                continue
            src = (root / source)
            if not src.is_file():
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"source missing: {source}"})
                continue
            parsed = _parse_iso(frozen_at) if frozen_at else None
            if parsed is None:
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"invalid or missing frozen_at: {frozen_at!r}"})
                continue
            if _mtime_utc(src) > parsed:
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"source newer than frozen_at: {source} "
                                        f"(mtime {_mtime_utc(src).isoformat()} > {parsed.isoformat()})"})
    return {"status": "PASS" if not stale else "FAIL",
            "frozen_files": [p.relative_to(root).as_posix() for p in files],
            "claims_checked": checked,
            "stale": stale}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    a = ap.parse_args()
    r = a.root.resolve()
    try:
        out = audit(r)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
