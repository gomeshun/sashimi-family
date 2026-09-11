"""Audit downloaded public/private CI against one recorded parent commit.

The output includes identities, hashes and pass/fail evidence only. Numerical
catalogs and private package sources remain in the input evidence directories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-sha", required=True)
    parser.add_argument("--public-evidence", type=Path, required=True)
    parser.add_argument("--private-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    def committed(path):
        return subprocess.check_output(
            ["git", "-C", str(root), "show", f"{args.parent_sha}:{path}"]
        )

    manifest_bytes = committed("compatibility.toml")
    manifest = tomllib.loads(manifest_bytes.decode())
    revisions = {
        name: entry["ref"] for name, entry in manifest.items()
        if name != "compatibility"
    }
    assert len(args.parent_sha) == 40 and len(revisions) == 5
    for package, revision in revisions.items():
        line = subprocess.check_output(
            ["git", "-C", str(root), "ls-tree", args.parent_sha, package],
            text=True,
        )
        assert line.split()[:3] == ["160000", "commit", revision]
    script_hashes = {
        path: hashlib.sha256(committed(path)).hexdigest()
        for path in (
            "scripts/check_compatibility.py",
            "scripts/check_artifact_provenance.py",
            "scripts/check_sdist_rebuild.py",
            "scripts/smoke_installed_family.py",
            ".github/workflows/family-integration.yml",
        )
    }
    report = dict(
        schema="sashimi-family:recorded-ci:v1",
        status="passed",
        recorded_parent=args.parent_sha,
        source_revisions=revisions,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        tested_scripts_sha256=script_hashes,
        auditor_sha256=digest(Path(__file__)),
        public={}, private={},
    )
    for scope, directory in (
        ("public", args.public_evidence), ("private", args.private_evidence)
    ):
        run = json.loads((directory / "run.json").read_text())
        jobs = json.loads((directory / "jobs.json").read_text())["jobs"]
        assert run["status"] == "completed" and run["conclusion"] == "success"
        expected_head = args.parent_sha if scope == "public" else revisions["sashimi-f"]
        assert run["head_sha"] == expected_head
        assert len(jobs) == (3 if scope == "public" else 6)
        assert all(j["status"] == "completed" and j["conclusion"] == "success" for j in jobs)
        target_revisions = {
            p: r for p, r in revisions.items()
            if scope == "private" or p != "sashimi-f"
        }
        result = dict(
            run_id=run["id"], url=run["html_url"], event=run["event"],
            workflow_head=run["head_sha"], conclusion=run["conclusion"],
            run_record_sha256=digest(directory / "run.json"),
            jobs=[dict(name=j["name"], conclusion=j["conclusion"]) for j in jobs],
            python={},
        )
        for version in ("3.11", "3.12", "3.13"):
            prefix = "public-family-validation" if scope == "public" else "family-validation-inputs"
            base = directory / f"{prefix}-{version}"
            if scope == "public":
                assert (base / "parent-revision.txt").read_text().strip() == args.parent_sha
                assert (base / "compatibility.toml").read_bytes() == manifest_bytes
                effective = dict(family_base_ref=args.parent_sha, overrides={})
            else:
                assert run["event"] == "workflow_dispatch"
                effective = json.loads((base / "effective.json").read_text())
                assert effective["family_base_ref"] == args.parent_sha
                assert effective["validation_mode"] == "promoted"
                assert effective["overrides"] == {}
                assert effective["effective_revisions"] == revisions
                assert effective["workflow_source_ref"] == revisions["sashimi-f"]
                assert tomllib.loads((base / "base.toml").read_text()) == manifest
                assert tomllib.loads((base / "effective.toml").read_text()) == manifest
            hashes = {
                Path(name).name: value
                for value, name in (line.split() for line in (base / "artifact-sha256.txt").read_text().splitlines())
            }
            assert len(hashes) == len(target_revisions) * 2
            item = dict(effective=effective, original_artifacts_sha256=hashes, smoke={}, rebuilds={})
            physical = []
            for kind in ("original", "rebuilt"):
                path = base / f"{kind}-smoke/report.json"
                data = json.loads(path.read_text())
                assert data["python"].startswith(version + ".")
                assert {p: v["source_revision"] for p, v in data["installations"].items()} == target_revisions
                assert data["script_sha256"] == script_hashes["scripts/smoke_installed_family.py"]
                assert data["warnings"] == []
                item["smoke"][kind] = dict(
                    result="passed", report_sha256=digest(path), python=data["python"],
                    source_revisions=target_revisions,
                )
                physical.append({
                    p: {k: v for k, v in values.items() if k != "archive_sha256"}
                    for p, values in data["results"].items()
                })
            assert physical[0] == physical[1]
            item["original_rebuilt_quantities_equal"] = True
            for package, revision in target_revisions.items():
                path = base / "rebuilt" / package / "verification.json"
                data = json.loads(path.read_text())
                assert data["source_revision"] == revision
                assert data["revision_environment_injected"] is False
                assert data["result"] == "source identity preserved"
                wheel = path.parent / data["wheel"]
                assert digest(wheel) == data["wheel_sha256"]
                name = "sashimi_itamae" if package == "itamae" else package.replace("-", "_")
                archive, = (n for n in hashes if n.startswith(name + "-") and n.endswith(".tar.gz"))
                assert data["archive_sha256"] == hashes[archive]
                item["rebuilds"][package] = data
            if scope == "private":
                path = directory / f"migration-test-results-{version}" / "test-results.xml"
                suites = [s.attrib for s in ET.parse(path).getroot().iter("testsuite")]
                assert suites and all(int(s["failures"]) == int(s["errors"]) == int(s["skipped"]) == 0 for s in suites)
                item["component_regression"] = dict(
                    tests=sum(int(s["tests"]) for s in suites),
                    result="passed", junit_sha256=digest(path),
                )
            result["python"][version] = item
        report[scope] = result
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Verified public/private original/rebuilt family at {args.parent_sha}; no overrides.")


if __name__ == "__main__":
    main()
