#!/usr/bin/env python3
"""Guard tests: README/CHANGELOG numeric claims must match the repository.

This regression net exists because script/skill/test counts drifted in the
past ("14"/"16" scripts, "28" skills, "124" tests). Every claim below is
derived from disk so the docs cannot silently rot.
"""
from __future__ import annotations
import json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def count_skills() -> int:
    return len([d for d in (ROOT / ".codex" / "skills").iterdir() if d.is_dir()])


def count_tests() -> int:
    n = 0
    for p in (ROOT / "tests").glob("test_*.py"):
        n += len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
    return n


def count_scripts() -> int:
    """Executable scripts: .py files under scripts/ plus the bash wrapper."""
    py = sum(1 for p in (ROOT / "scripts").glob("*.py"))
    sh = 1 if (ROOT / "scripts" / "sync-plugin.sh").is_file() else 0
    return py + sh


def readme_zh() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def readme_en() -> str:
    return (ROOT / "README.en.md").read_text(encoding="utf-8")


class DocClaimTests(unittest.TestCase):
    def test_skill_counts(self):
        n = count_skills()
        for label, text in (("zh", readme_zh()), ("en", readme_en())):
            self.assertIn(f"{n} 个", text) if label == "zh" else self.assertTrue(
                re.search(rf"\b{n}\b.*skills|skills.*\b{n}\b", text),
                f"{label} README missing skill count {n}")

    def test_test_counts(self):
        n = count_tests()
        for text in (readme_zh(), readme_en()):
            self.assertIn(str(n), text, f"README missing test count {n}")

    def test_script_counts(self):
        n = count_scripts()
        for text in (readme_zh(), readme_en()):
            self.assertIn(str(n), text, f"README missing script count {n}")

    def test_plugin_versions_match(self):
        codex = json.loads((ROOT / "plugins" / "mathmodeling-skills" / ".codex-plugin" / "plugin.json")
                           .read_text(encoding="utf-8"))
        claude = json.loads((ROOT / "plugins" / "mathmodeling-skills" / ".claude-plugin" / "plugin.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(codex["version"], claude["version"])
        for text in (readme_zh(), readme_en()):
            self.assertIn(codex["version"], text)

    def test_skill_tree_dirs_exist(self):
        for tree in (".codex", ".claude", ".agents"):
            self.assertTrue((ROOT / tree / "skills").is_dir(), f"missing {tree}/skills")


if __name__ == "__main__":
    unittest.main()
