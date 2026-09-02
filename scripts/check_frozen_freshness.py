#!/usr/bin/env python3
"""Check that frozen numbers are fresh: every frozen claim's canonical source
must still exist and must not be newer than the claim's frozen_at timestamp.

Closes the previously documented gap (AGENTS.md: "the frozen_at freshness rule
has no automatic checker yet"). Pure standard library.

Freshness semantics (mtime based):
- The check compares the source file's filesystem mtime (UTC) against
  `frozen_at` (ISO-8601). A git checkout, unpack, or copy that resets mtimes
  can produce false STALE verdicts; re-freeze after such operations or treat
  a STALE result as "verify and re-freeze", not as proof of tampering.
- `frozen_at` should carry an explicit timezone. Naive timestamps are
  interpreted as UTC and produce an advisory warning; if the freezing tool
  wrote local time, use an explicit offset to avoid misjudged verdicts.
- `source_file` must be a project-relative path that resolves inside the
  workspace root; absolute paths and escaping `..` references are rejected.

Exit codes: 0 = all frozen claims current; 2 = at least one claim STALE
(missing source, escaping source, source newer than frozen_at, or
unparsable frozen_at).
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from common import frozen_claims

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

FROZEN_GLOB = "results/*/reports/frozen_numbers.json"


def _parse_iso(value) -> tuple[datetime | None, bool]:
    """Parse an ISO-8601 timestamp.

    Returns (dt, naive_flag): dt is a tz-aware datetime (naive inputs get a
    UTC tzinfo so ordering vs mtime is well defined), naive_flag records
    whether the input carried no timezone. Accepts 'Z', '+00:00', and the
    Python 3.10-incompatible '+0800' (no-colon) offset. Returns (None, False)
    when unparsable.
    """
    try:
        s = str(value).strip()
        if not s:
            return None, False
        naive = True
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
            naive = False
        m = re.match(r"^(.+[+-])(\d{2})(\d{2})$", s)
        if m and ":" not in m.group(2) + m.group(3):
            # normalize '+0800' -> '+08:00' (Python 3.10 fromisoformat
            # rejects the no-colon offset form that strftime('%z') emits)
            s = m.group(1) + m.group(2) + ":" + m.group(3)
            naive = False
        if re.search(r"[+-]\d{2}:\d{2}$", s):
            naive = False
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt, naive
    except Exception:
        return None, False


def _resolve_under(root: Path, raw: str) -> Path | None:
    """Resolve a project-relative path and enforce it stays inside root.

    Returns None when the reference is missing, empty, or escapes the root
    (absolute paths and '..' components are rejected the same way the other
    validators' safe() helpers reject them).
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        candidate = (root / raw).resolve()
        candidate.relative_to(root.resolve())
    except (ValueError, OSError):
        return None
    return candidate


def _mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _claim_items(frozen_file: Path) -> list[dict]:
    """Accept the {"claims": [...]} shape and the {claim_id: {...}} map shape
    used by the rest of the toolchain (delegates to lib/common.frozen_claims)."""
    try:
        data = json.loads(frozen_file.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    return frozen_claims(data)


def audit(root: Path) -> dict:
    stale, checked, warnings = [], 0, []
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
            src = _resolve_under(root, source)
            if src is None:
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"source escapes project root or is invalid: {source}"})
                continue
            if not src.is_file():
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"source missing: {source}"})
                continue
            parsed, naive = _parse_iso(frozen_at) if frozen_at else (None, False)
            if parsed is None:
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"invalid or missing frozen_at: {frozen_at!r}"})
                continue
            if naive:
                warnings.append({"claim_id": claim_id, "file": rel,
                                 "reason": "frozen_at has no timezone; interpreted as UTC — "
                                           "if the freezing tool wrote local time, this claim "
                                           "may be misjudged stale/fresh (use an explicit offset)"})
            mtime = _mtime_utc(src)
            if mtime > parsed:
                stale.append({"claim_id": claim_id, "file": rel,
                              "reason": f"source newer than frozen_at: {source} "
                                        f"(mtime {mtime.isoformat()} > {parsed.isoformat()})"})
    return {"status": "PASS" if not stale else "FAIL",
            "frozen_files": [p.relative_to(root).as_posix() for p in files],
            "claims_checked": checked,
            "stale": stale,
            "warnings": warnings}


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
    for w in out.get("warnings", []):
        print(f"warning: {w['file']}: {w['reason']}", file=sys.stderr)
    return 0 if out["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
