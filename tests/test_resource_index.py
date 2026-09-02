#!/usr/bin/env python3
"""Tests for scripts/resource_index.py (pure standard library)."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from resource_index import scan


def make_lib():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "resource-library" / "papers").mkdir(parents=True)
    (root / "resource-library" / "figures").mkdir(parents=True)
    (root / "resource-library" / "papers" / "README.md").write_text("# papers", encoding="utf-8")
    (root / "resource-library" / "papers" / "a.md").write_text("x", encoding="utf-8")
    (root / "resource-library" / "figures" / "b.png").write_bytes(b"png")
    return td, root


class ResourceIndexTests(unittest.TestCase):
    def test_scan_categories(self):
        td, root = make_lib()
        d = scan(root)
        self.assertEqual(d["schema_version"], 2)
        self.assertEqual(set(d["categories"]), {"papers", "figures"})
        self.assertEqual(d["categories"]["papers"]["entries"], ["a.md"])
        self.assertIn("README.md", d["categories"]["papers"]["docs"])
        self.assertEqual(d["categories"]["papers"]["supporting"], [])
        self.assertEqual(d["categories"]["figures"]["entries"], ["b.png"])
        td.cleanup()

    def test_scan_missing_library(self):
        td = tempfile.TemporaryDirectory()
        d = scan(Path(td.name))
        self.assertEqual(d["categories"], {})
        td.cleanup()

    def test_index_roundtrip(self):
        td, root = make_lib()
        data = scan(root)
        idx = root / "resource-library" / "index.json"
        idx.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(json.loads(idx.read_text(encoding="utf-8")), data)
        td.cleanup()

    def test_entry_directory_readme_is_the_entry(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        entry = root / "resource-library" / "figures" / "example-rank-bar"
        (entry / "content").mkdir(parents=True)
        (entry / "code").mkdir(parents=True)
        (entry / "data").mkdir(parents=True)
        (root / "resource-library" / "figures" / "README.md").write_text("r", encoding="utf-8")
        (entry / "README.md").write_text("# entry", encoding="utf-8")
        (entry / "content" / "fig.png").write_bytes(b"png")
        (entry / "code" / "plot.py").write_text("print(1)", encoding="utf-8")
        (entry / "data" / "in.csv").write_text("a,b\n", encoding="utf-8")
        d = scan(root)
        figs = d["categories"]["figures"]
        self.assertEqual(figs["entries"], ["example-rank-bar/README.md"])
        self.assertEqual(sorted(figs["supporting"]),
                         ["example-rank-bar/code/plot.py",
                          "example-rank-bar/content/fig.png",
                          "example-rank-bar/data/in.csv"])
        td.cleanup()

    def test_support_dirs_at_category_root_are_not_entries(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        cat = root / "resource-library" / "tables"
        (cat / "code").mkdir(parents=True)
        (cat / "data").mkdir(parents=True)
        (cat / "README.md").write_text("r", encoding="utf-8")
        (cat / "code" / "make_table.py").write_text("x", encoding="utf-8")
        (cat / "data" / "table.csv").write_text("x", encoding="utf-8")
        d = scan(root)
        tables = d["categories"]["tables"]
        self.assertEqual(tables["entries"], [])
        self.assertEqual(sorted(tables["supporting"]),
                         ["code/make_table.py", "data/table.csv"])
        td.cleanup()

    def test_nested_subdirectories_included(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        nested = root / "resource-library" / "assets" / "problems"
        nested.mkdir(parents=True)
        (root / "resource-library" / "assets" / "README.md").write_text("r", encoding="utf-8")
        (nested / "README.md").write_text("problems index", encoding="utf-8")
        (nested / "smoke.txt").write_text("x", encoding="utf-8")
        d = scan(root)
        assets = d["categories"]["assets"]
        self.assertEqual(assets["entries"], ["problems/README.md"])
        self.assertEqual(assets["supporting"], ["problems/smoke.txt"])
        self.assertEqual(assets["docs"], ["README.md"])
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
