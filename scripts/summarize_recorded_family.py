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


def read_json(path):
    return json.loads(path.read_text())


def quantities(report):
    return {p: {k: v for k, v in values.items() if k != "archive_sha256"}
            for p, values in report["results"].items()}


def validate_coverage(report):
    """Reduced rebuild frequency must not masquerade as three rebuilt runs."""
    versions = ["3.11", "3.12", "3.13"]
    assert report["status"] == "passed"
    assert report["profile"] in ("standard", "full")
    assert report["python_versions"] == versions
    assert set(report["original"]) == set(versions)
    rebuilt = versions if report["profile"] == "full" else versions[:1]
    assert report["rebuilt_python_versions"] == rebuilt
    assert set(report["rebuilt"]) == set(rebuilt)
    assert report["standalone_python_version"] == "3.11"
    assert set(report["installed_regression"]) == (set(versions) if report["profile"] == "full" else set())


def audit_single_build(scope, directory, parent_sha, manifest, manifest_bytes, revisions, script_hashes):
    """Audit the shared-artifact layout, while retaining the older layout below."""
    read = read_json
    run, jobs = read(directory / "run.json"), read(directory / "jobs.json")["jobs"]
    assert run["status"] == "completed" and run["conclusion"] == "success"
    assert run["head_sha"] == (parent_sha if scope == "public" else revisions["sashimi-f"])
    assert jobs and all(j["status"] == "completed" and j["conclusion"] in ("success", "skipped") for j in jobs)
    prefix = "public-family-validation" if scope == "public" else "family-validation-inputs"
    base = directory / prefix
    if scope == "public":
        assert any(j["name"] == "public-coinstall" and j["conclusion"] == "success" for j in jobs)
        assert (base / "parent-revision.txt").read_text().strip() == parent_sha
        assert (base / "compatibility.toml").read_bytes() == manifest_bytes
        effective = dict(family_base_ref=parent_sha, overrides={})
        manifest_path = base / "compatibility.toml"
    else:
        assert any(j["name"] == "family-coinstall" and j["conclusion"] == "success" for j in jobs)
        assert run["event"] == "workflow_dispatch"
        effective = read(base / "effective.json")
        assert effective["family_base_ref"] == parent_sha
        assert effective["validation_mode"] == "promoted" and effective["overrides"] == {}
        assert effective["effective_revisions"] == revisions
        assert effective["workflow_source_ref"] == revisions["sashimi-f"]
        assert tomllib.loads((base / "base.toml").read_text()) == manifest
        assert tomllib.loads((base / "effective.toml").read_text()) == manifest
        manifest_path = base / "effective.toml"
    target_revisions = {p: r for p, r in revisions.items() if scope == "private" or p != "sashimi-f"}
    artifacts = base / "artifacts"
    report = read(artifacts / "validation.json")
    assert report["schema"] == "sashimi-family:artifact-validation:v1"
    validate_coverage(report)
    assert report["source_revisions"] == target_revisions
    assert report["manifest_sha256"] == digest(manifest_path)
    assert report["script_sha256"] == script_hashes["scripts/validate_family_artifacts.py"]
    build_path = artifacts / "build/build-report.json"
    assert report["build_report_sha256"] == digest(build_path)
    build = read(build_path)
    assert build["script_sha256"] == script_hashes["scripts/build_candidate_artifacts.py"]
    assert build["manifest_sha256"] == digest(manifest_path)
    assert build["revision_environment_injected"] is False
    assert {d["package"]: d["source_revision"] for d in build["source_revisions"]} == target_revisions
    assert len(build["artifacts"]) == len(target_revisions) * 2
    for name, value in build["artifacts"].items():
        assert Path(name).name == name
        assert digest(artifacts / "build/dist" / name) == value["sha256"]
    result = dict(
        layout="single-build", profile=report["profile"], run_id=run["id"], url=run["html_url"],
        event=run["event"], workflow_head=run["head_sha"], conclusion=run["conclusion"],
        run_record_sha256=digest(directory / "run.json"), validation_report_sha256=digest(artifacts / "validation.json"),
        effective=effective, jobs=[dict(name=j["name"], conclusion=j["conclusion"]) for j in jobs],
        original_artifacts_sha256={name: data["sha256"] for name, data in build["artifacts"].items()},
        build_python=build["python"], rebuilds={}, python={}, standalone={},
    )
    for package, revision in target_revisions.items():
        path = artifacts / "rebuilt" / package / "verification.json"
        data = read(path)
        assert data["source_revision"] == revision and data["revision_environment_injected"] is False
        assert data["runtime_data_metadata_equal"] is True
        assert data["result"] == "source identity preserved"
        assert digest(path.parent / data["wheel"]) == data["wheel_sha256"]
        assert data["original_wheel_sha256"] == build["artifacts"][data["wheel"]]["sha256"]
        prefix = "sashimi_itamae" if package == "itamae" else package.replace("-", "_")
        archive, = (name for name in build["artifacts"] if name.startswith(prefix + "-") and name.endswith(".tar.gz"))
        assert data["archive_sha256"] == build["artifacts"][archive]["sha256"]
        result["rebuilds"][package] = data

    def smoke(path, expected, version, reported):
        data = read(path)
        assert data["python"].startswith(version + ".")
        assert {p: v["source_revision"] for p, v in data["installations"].items()} == expected
        assert data["manifest_sha256"] == digest(manifest_path)
        assert data["script_sha256"] == script_hashes["scripts/smoke_installed_family.py"]
        assert data["warnings"] == [] and reported["report_sha256"] == digest(path)
        return data

    for version in report["python_versions"]:
        original = smoke(artifacts / f"original-{version}-smoke/report.json", target_revisions, version, report["original"][version])
        item = dict(original=report["original"][version], rebuilt=None)
        if version in report["rebuilt_python_versions"]:
            rebuilt = smoke(artifacts / f"rebuilt-{version}-smoke/report.json", target_revisions, version, report["rebuilt"][version])
            assert quantities(original) == quantities(rebuilt)
            assert report["rebuilt"][version]["original_rebuilt_quantities_equal"] is True
            item["rebuilt"] = report["rebuilt"][version]
        if report["profile"] == "full":
            path = artifacts / f"tests-{version}/report.json"
            regression = read(path)
            assert regression["manifest_sha256"] == digest(manifest_path)
            assert regression["script_sha256"] == script_hashes["scripts/check_installed_candidate.py"]
            counts = {}
            for package in regression["packages"]:
                name = package["package"]
                assert package["exit_code"] == 0 and package["installation"]["source_revision"] == target_revisions[name]
                xml_path = path.parent / name / "result.xml"
                suites = [s.attrib for s in ET.parse(xml_path).getroot().iter("testsuite")]
                assert suites and all(int(s[k]) == 0 for s in suites for k in ("failures", "errors", "skipped"))
                counts[name] = sum(int(s["tests"]) for s in suites)
            assert set(counts) == set(target_revisions)
            expected = report["installed_regression"][version]
            assert expected["counts"] == counts and expected["total"] == sum(counts.values())
            assert expected["report_sha256"] == digest(path)
            item["installed_regression"] = expected
        result["python"][version] = item
    assert set(report["standalone"]) == set(target_revisions)
    for package in target_revisions:
        expected = {p: r for p, r in target_revisions.items() if p in ("itamae", package)}
        smoke(artifacts / f"standalone-{package}-smoke/report.json", expected, "3.11", report["standalone"][package])
        result["standalone"][package] = report["standalone"][package]
    return result


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
    if subprocess.check_output(["git", "-C", str(root), "ls-tree", "--name-only", args.parent_sha,
                                "scripts/validate_family_artifacts.py"], text=True).strip():
        for path in ("scripts/validate_family_artifacts.py", "scripts/build_candidate_artifacts.py",
                     "scripts/check_installed_candidate.py"):
            script_hashes[path] = hashlib.sha256(committed(path)).hexdigest()
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
        prefix = "public-family-validation" if scope == "public" else "family-validation-inputs"
        if (directory / prefix / "artifacts/validation.json").exists():
            report["schema"] = "sashimi-family:recorded-ci:v2"
            report[scope] = audit_single_build(scope, directory, args.parent_sha, manifest,
                                               manifest_bytes, revisions, script_hashes)
            continue
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
