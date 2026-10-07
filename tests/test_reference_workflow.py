"""The reference workflow must use Git objects, not the changing worktree."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class ReferenceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="reference-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Reference test")
        self.git("config", "user.email", "reference@example.invalid")
        (self.repo / "toy.py").write_text(
            "class Model:\n    def calculate(self):\n        return ([1., 2.],)\n"
        )
        (self.repo / "input.txt").write_text("pinned input\n")
        self.git("add", "toy.py", "input.txt")
        self.git("commit", "--quiet", "-m", "frozen toy")
        self.config = {
            "role": "A",
            "repository": "local-test/toy",
            "source_revision": self.git("rev-parse", "HEAD").strip(),
            "module": "toy",
            "class": "Model",
            "method": "calculate",
            "parameters": {},
            "input_files": [
                {
                    "path": "input.txt",
                    "sha256": hashlib.sha256(b"pinned input\n").hexdigest(),
                }
            ],
        }

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True)

    def execute(self):
        config = self.root / "config.json"
        config.write_text(json.dumps(self.config))
        self.output = self.root / "result.npz"
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/run_reference.py"),
                "--repository",
                str(self.repo),
                "--config",
                str(config),
                "--python",
                sys.executable,
                "--output",
                str(self.output),
            ],
            capture_output=True,
            text=True,
        )

    def test_export_ignores_later_worktree_source_and_data_edits(self):
        (self.repo / "toy.py").write_text(
            "raise RuntimeError('uncommitted code ran')\n"
        )
        (self.repo / "input.txt").write_text("changed worktree input\n")
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        with np.load(self.output) as result:
            np.testing.assert_array_equal(result["tuple_0"], [1.0, 2.0])
        metadata = json.loads(self.output.with_suffix(".json").read_text())
        self.assertEqual(metadata["source_revision"], self.config["source_revision"])
        self.assertTrue(metadata["independent_process"])
        self.assertEqual(
            metadata["input_files"][0]["verified_sha256"],
            self.config["input_files"][0]["sha256"],
        )

    def test_mismatched_input_hash_fails_before_model_execution(self):
        self.config["input_files"][0]["sha256"] = "0" * 64
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("input digest mismatch", result.stderr)
        self.assertFalse(self.output.exists())

    def test_b_patch_content_is_verified_before_applying(self):
        patch = self.root / "correction.patch"
        patch.write_text("modified patch bytes\n")
        self.config["role"] = "B"
        self.config["patches"] = [
            {"id": "test", "path": patch.name, "sha256": "0" * 64}
        ]
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Patch digest mismatch", result.stderr)
        self.assertFalse(self.output.exists())

    def test_a_cannot_apply_corrections(self):
        self.config["patches"] = [{"id": "not-A"}]
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Frozen reference A must not have source patches", result.stderr)


if __name__ == "__main__":
    unittest.main()
