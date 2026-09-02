#!/usr/bin/env python3
"""Optional vcs block in run snapshots (0.8.0)."""
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from create_run_snapshot import vcs_snapshot

COMMAND = "python -c \"from pathlib import Path; Path('result.json').write_text('r'); Path('validation.json').write_text('v')\""


def run_snapshot_cli(root: Path, run_dir: str) -> int:
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "create_run_snapshot.py"),
                        "run", str(root), run_dir,
                        "--planned-budget", '{"i":1}', "--actual-budget", '{"i":1}',
                        "--command", COMMAND,
                        "--result-ref", "result.json", "--validation-ref", "validation.json"],
                       capture_output=True, text=True, encoding="utf-8", cwd=root)
    return p.returncode


class VcsSnapshotTests(unittest.TestCase):
    def test_non_git_workspace_has_no_vcs_block(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertIsNone(vcs_snapshot(root))
            (root / "result.json").write_text("old", encoding="utf-8")
            self.assertEqual(run_snapshot_cli(root, "runs/r1"), 0, "snapshot run failed")
            meta = json.loads((root / "runs/r1/run_metadata.json").read_text(encoding="utf-8-sig"))
            self.assertIsNone(meta.get("vcs"))
            p = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_run_snapshot.py"),
                                str(root), str(root / "runs/r1")],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_git_workspace_records_head_and_dirty(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for cmd in (["git", "init", "-b", "main"], ["git", "config", "user.email", "t@t"],
                        ["git", "config", "user.name", "t"]):
                subprocess.run(cmd, cwd=root, check=True, capture_output=True, text=True)
            (root / "base.txt").write_text("base", encoding="utf-8")
            subprocess.run(["git", "add", "base.txt"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True,
                           capture_output=True, text=True)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  capture_output=True, text=True).stdout.strip()
            self.assertEqual(run_snapshot_cli(root, "runs/r1"), 0, "snapshot run failed")
            meta = json.loads((root / "runs/r1/run_metadata.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(meta.get("vcs", {}).get("head"), head)
            # the run produced untracked outputs -> dirty list non-empty
            self.assertGreaterEqual(meta.get("vcs", {}).get("dirty_count", 0), 1)
            p = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_run_snapshot.py"),
                                str(root), str(root / "runs/r1")],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__":
    unittest.main()
