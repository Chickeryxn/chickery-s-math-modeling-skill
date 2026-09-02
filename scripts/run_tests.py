#!/usr/bin/env python3
"""Run all repository-local tests without third-party dependencies."""
from __future__ import annotations
import re
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'
if not TESTS.is_dir():
    print(f"tests directory not found: {TESTS}", file=sys.stderr)
    raise SystemExit(2)
suite = unittest.defaultTestLoader.discover(str(TESTS))
if suite.countTestCases() == 0:
    # discover() returns an empty suite (and would report success) when no
    # tests are found; refuse the false-green pass instead.
    print("no tests discovered under tests/ — refusing a false-green pass", file=sys.stderr)
    raise SystemExit(2)
# Static definition count mirrors tests/test_doc_claims.count_tests() so the
# two counting methods cannot drift apart. A method that is defined but never
# discovered (e.g. accidentally nested inside another method by a bad dedent)
# would previously pass every suite while silently not running; any mismatch
# between what unittest executes and what the docs-counting regex sees must
# fail the run.
static = sum(
    len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
    for p in sorted(TESTS.glob("test_*.py")))
discovered = suite.countTestCases()
if static != discovered:
    print(
        f"test definition/discovery mismatch: {static} static test methods "
        f"but unittest discovers {discovered} — a test is defined but not "
        f"collected (check indentation/nesting in tests/); refusing to run",
        file=sys.stderr)
    raise SystemExit(2)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.testsRun != static:
    print(
        f"executed {result.testsRun} tests but {static} were defined — "
        "a test silently did not execute; refusing a false-green pass",
        file=sys.stderr)
    raise SystemExit(2)
raise SystemExit(0 if result.wasSuccessful() else 1)
