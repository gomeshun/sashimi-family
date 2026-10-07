"""Failure boundaries for shared artifact validation and CI change selection."""

import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rebuild = load("sdist_rebuild", "scripts/check_sdist_rebuild.py")
validation = load("family_validation", "scripts/validate_family_artifacts.py")
changes = load("ci_changes", ".github/actions/changed-paths/changed_paths.py")
audit = load("recorded_ci", "scripts/summarize_recorded_family.py")


class ArtifactValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def wheel(self, name, changes=None):
        members = {
            "example/__init__.py": b"VALUE = 1\n",
            "example/data/table.txt": b"1 2 3\n",
            "example-1.dist-info/WHEEL": b"Root-Is-Purelib: true\nTag: py3-none-any\n",
            "example-1.dist-info/METADATA": b"Name: example\nVersion: 1\n",
            "example-1.dist-info/RECORD": b"index bytes",
        }
        members.update(changes or {})
        path = self.root / name
        with zipfile.ZipFile(path, "w") as bundle:
            for member, content in members.items():
                bundle.writestr(member, content)
        return path

    def test_record_order_does_not_require_repeating_physics(self):
        first = self.wheel("first.whl")
        second = self.wheel("second.whl", {"example-1.dist-info/RECORD": b"other index"})
        self.assertTrue(rebuild.compare_wheels(first, second)["runtime_data_metadata_equal"])

    def test_missing_or_changed_runtime_data_metadata_is_rejected(self):
        first = self.wheel("first.whl")
        for member in ("example/__init__.py", "example/data/table.txt", "example-1.dist-info/METADATA"):
            with self.subTest(member=member):
                second = self.wheel("second.whl", {member: b"different"})
                with self.assertRaisesRegex(ValueError, "differs"):
                    rebuild.compare_wheels(first, second)

    def test_native_wheel_cannot_use_single_universal_build_policy(self):
        wheel = self.wheel("native.whl", {"example-1.dist-info/WHEEL": b"Root-Is-Purelib: false\nTag: cp311-cp311-linux_x86_64\n"})
        with self.assertRaisesRegex(ValueError, "pure Python"):
            validation.require_universal_wheels([wheel])

    def test_docs_change_requires_a_successful_preceding_run(self):
        self.assertTrue(changes.needs_validation(["docs/notes.md"], ["src/**"], False))
        self.assertFalse(changes.needs_validation(["docs/notes.md"], ["src/**"], True))

    def test_manual_family_success_cannot_stand_in_for_component_success(self):
        revision = "a" * 40
        environment = dict(GITHUB_WORKFLOW_REF="owner/repo/.github/workflows/test.yml@main",
                           GITHUB_REPOSITORY="owner/repo", CI_READ_TOKEN="test-token")
        manual = dict(head_sha=revision, conclusion="success", event="workflow_dispatch")
        for runs, expected in (
            ([manual], False),
            ([manual, dict(manual, event="push", conclusion="failure")], False),
            ([manual, dict(manual, event="pull_request", head_sha="b" * 40)], False),
            ([manual, dict(manual, event="pull_request")], True),
            ([dict(manual, event="push")], True),
        ):
            with self.subTest(runs=runs), mock.patch.object(
                changes.urllib.request, "urlopen",
                return_value=io.StringIO(json.dumps(dict(workflow_runs=runs))),
            ):
                self.assertEqual(changes.succeeded_before(revision, environment), expected)

    def test_source_data_and_workflow_changes_always_run(self):
        patterns = ["src/**", "*.py", ".github/workflows/test.yml"]
        for path in ("src/example/data/table.txt", "setup.py", ".github/workflows/test.yml"):
            self.assertTrue(changes.needs_validation([path], patterns, True))
        self.assertFalse(changes.matches("notebooks/archive/old.py", ["*.py"]))

    def test_initial_event_compares_whole_pr_and_manual_event_forces_validation(self):
        pull = {"head": {"sha": "a" * 40}, "base": {"sha": "b" * 40}}
        self.assertEqual(changes.revisions("pull_request", {"action": "opened", "pull_request": pull})[0], "b" * 40)
        self.assertIsNone(changes.revisions("workflow_dispatch", {})[0])
        self.assertEqual(changes.revisions("pull_request", {"action": "synchronize", "before": "c" * 40, "pull_request": pull}), ("c" * 40, "a" * 40))

    def test_merge_reuse_requires_both_identical_tree_and_success(self):
        commit = f"tree {'d' * 40}\nparent {'b' * 40}\nparent {'c' * 40}\n\nmerge\n"
        with mock.patch.object(changes.subprocess, "check_output", return_value=commit), \
             mock.patch.object(changes, "changed_paths", return_value=[]) as diff, \
             mock.patch.object(changes, "succeeded_before", return_value=True) as success:
            self.assertEqual(changes.validated_merge_parent("a" * 40, {}), "c" * 40)
            success.return_value = False
            self.assertIsNone(changes.validated_merge_parent("a" * 40, {}))
            success.return_value = True
            diff.return_value = ["src/conflict_resolution.py"]
            self.assertIsNone(changes.validated_merge_parent("a" * 40, {}))

    def test_reduced_rebuild_coverage_cannot_be_reported_as_full(self):
        report = dict(status="passed", profile="standard", python_versions=["3.11", "3.12", "3.13"],
                      original={v: {} for v in ("3.11", "3.12", "3.13")},
                      rebuilt_python_versions=["3.11"], rebuilt={"3.11": {}},
                      standalone_python_version="3.11", installed_regression={})
        audit.validate_coverage(report)
        report["profile"] = "full"
        with self.assertRaises(AssertionError):
            audit.validate_coverage(report)
        report["profile"] = "standard"
        del report["original"]["3.13"]
        with self.assertRaises(AssertionError):
            audit.validate_coverage(report)


if __name__ == "__main__":
    unittest.main()
