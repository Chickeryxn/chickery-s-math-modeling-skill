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
    """Executable scripts: top-level .py files under scripts/ plus the bash wrapper."""
    py = sum(1 for p in (ROOT / "scripts").glob("*.py"))
    sh = 1 if (ROOT / "scripts" / "sync-plugin.sh").is_file() else 0
    return py + sh

def readme_zh() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def readme_en() -> str:
    return (ROOT / "README.en.md").read_text(encoding="utf-8")


def reference_doc() -> str:
    return (ROOT / "docs" / "reference.md").read_text(encoding="utf-8")


def dsh_doc() -> str:
    return (ROOT / "docs" / "dsh-compatibility.md").read_text(encoding="utf-8")


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

    def test_reference_and_dsh_test_counts(self):
        # Regression: docs/reference.md's directory-tree note and
        # docs/dsh-compatibility.md smoke counts both drifted to older test
        # counts (171/215) after releases; the README badge alone was guarded.
        n = count_tests()
        ref = reference_doc()
        dsh = dsh_doc()
        self.assertIn(f"{n} 个用例", ref,
                      "docs/reference.md missing current test count in coverage section")
        self.assertRegex(ref, rf"tests/\s+# {n} 个测试用例",
                         "docs/reference.md directory-tree test count drifted")
        self.assertIn(f"{n} 用例", dsh,
                      "docs/dsh-compatibility.md smoke count drifted")

    def test_archify_index_skill_count(self):
        # The committed archify gallery page once advertised "28 skills".
        html = (ROOT / "docs" / "diagrams" / "archify" / "index.html").read_text(
            encoding="utf-8")
        self.assertIn(f"展示 {count_skills()} 个 skills", html)

    def test_script_counts(self):
        n = count_scripts()
        # Assert the exact labeled phrase so the bare number cannot match an
        # unrelated claim (the "28-skill skeleton" once masked a wrong count).
        zh = readme_zh()
        en = readme_en()
        self.assertIn(f"{n} 个纯标准库脚本", zh, f"README zh missing exact script phrase {n}")
        self.assertIn(f"{n} standard-library-only", en, f"README en missing exact script phrase {n}")

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
