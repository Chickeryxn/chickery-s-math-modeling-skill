#!/usr/bin/env python3
"""Tests for scripts/validate_upstream_assets.py (pure standard library)."""
from __future__ import annotations
import hashlib, json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_upstream_assets import parse_upstream_md, validate

VALID_UPSTREAM = """\
# Upstream X

- **Source repository**: https://example.com/repo
- **License**: MIT
- **Imported files**:
  - `a.md` — doc a
  - `b.py` — script b
"""


def make_root():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    sub = root / "references" / "upstream" / "src"
    sub.mkdir(parents=True)
    (root / "NOTICE.md").write_text(
        "# NOTICE\n\nSource: https://example.com/repo · commit deadbeef\n", encoding="utf-8")
    return td, root, sub


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class UpstreamAssetsTests(unittest.TestCase):
    def test_parse_upstream_md(self):
        p = parse_upstream_md(VALID_UPSTREAM)
        self.assertEqual(p["fields"]["License"], "MIT")
        self.assertEqual(p["fields"]["Source repository"], "https://example.com/repo")
        self.assertEqual(p["imported"], ["a.md", "b.py"])

    def test_valid_dir_passes(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM, encoding="utf-8")
        (sub / "a.md").write_text("x", encoding="utf-8")
        (sub / "b.py").write_text("x = 1", encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "PASS")
        td.cleanup()

    def test_missing_upstream_fails(self):
        td, root, sub = make_root()
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("missing UPSTREAM.md" in e for e in r["errors"]))
        td.cleanup()

    def test_missing_field_fails(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM.replace("- **Source repository**: https://example.com/repo\n", ""),
                                         encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("Source repository" in e for e in r["errors"]))
        td.cleanup()

    def test_disallowed_license_fails(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM.replace("MIT", "CC-BY-4.0"), encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("disallowed license" in e for e in r["errors"]))
        td.cleanup()

    def test_missing_imported_file_fails(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM, encoding="utf-8")
        (sub / "a.md").write_text("x", encoding="utf-8")  # b.py declared but missing
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("b.py" in e for e in r["errors"]))
        td.cleanup()

    def test_no_imported_files_fails(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM.replace("- `a.md` — doc a\n  - `b.py` — script b\n", ""),
                                         encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("no imported files" in e for e in r["errors"]))
        td.cleanup()

    def test_hash_match_passes_and_drift_fails(self):
        td, root, sub = make_root()
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM, encoding="utf-8")
        a = sub / "a.md"; a.write_text("x", encoding="utf-8")
        (sub / "b.py").write_text("x = 1", encoding="utf-8")
        (sub / "hashes.json").write_text(json.dumps({"a.md": sha(a), "b.py": "0" * 64}), encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("hash drift" in e for e in r["errors"]))
        # correct hashes -> pass
        (sub / "hashes.json").write_text(
            json.dumps({"a.md": sha(a), "b.py": sha(sub / "b.py")}), encoding="utf-8")
        self.assertEqual(validate(root)["status"], "PASS")
        td.cleanup()

    def test_notice_missing_mention_fails(self):
        td, root, sub = make_root()
        (root / "NOTICE.md").write_text("# NOTICE\nNo upstream mentioned.\n", encoding="utf-8")
        (sub / "UPSTREAM.md").write_text(VALID_UPSTREAM, encoding="utf-8")
        (sub / "a.md").write_text("x", encoding="utf-8")
        (sub / "b.py").write_text("x = 1", encoding="utf-8")
        r = validate(root)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("NOTICE.md does not mention" in e for e in r["errors"]))
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
