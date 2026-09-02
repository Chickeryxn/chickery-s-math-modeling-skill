#!/usr/bin/env python3
"""Run all repository-local tests without third-party dependencies."""
from __future__ import annotations
import sys, unittest
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
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
