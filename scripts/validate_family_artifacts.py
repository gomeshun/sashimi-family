"""Build once and test the same family artifacts across supported Python versions.

The standard profile checks original wheels on every supported Python, rebuilds
each sdist once, and checks rebuilt/standalone installations on Python 3.11.
The full profile also runs shipped regression tests and rebuilt-wheel smoke on
every supported Python. Neither profile modifies sources or the family manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import zipfile

PACKAGES = ("itamae", "sashimi-c", "sashimi-si", "sashimi-w", "sashimi-f")
PYTHONS = ("3.11", "3.12", "3.13")
SCRIPTS = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def physical_results(report):
    return {
        package: {key: value for key, value in data.items() if key != "archive_sha256"}
        for package, data in report["results"].items()
    }


def require_universal_wheels(wheels):
    """Do not silently apply a single-build policy to a future native extension."""
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as bundle:
            metadata, = (name for name in bundle.namelist() if name.endswith(".dist-info/WHEEL"))
            lines = bundle.read(metadata).decode().splitlines()
            if "Root-Is-Purelib: true" not in lines or [s for s in lines if s.startswith("Tag:")] != ["Tag: py3-none-any"]:
                raise ValueError(f"Single-build validation requires a pure Python wheel: {wheel}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packages", nargs="+", choices=PACKAGES, default=list(PACKAGES))
    parser.add_argument("--profile", choices=("standard", "full"), default="standard")
    parser.add_argument("--workflow-tests", action="store_true",
                        help="Run the family's validation-helper tests once")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if "itamae" not in args.packages or len(set(args.packages)) != len(args.packages):
        parser.error("packages must include itamae and contain no duplicates")
    manifest = args.manifest.resolve()
    source_root = args.source_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = tomllib.loads(manifest.read_text())
    environment = {
        key: value for key, value in os.environ.items()
        if not key.endswith("_SOURCE_REVISION") and key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    environment.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MPLBACKEND="Agg")
    if args.offline:
        environment["UV_OFFLINE"] = "1"

    def run(command, log):
        with (output / log).open("w") as stream:
            result = subprocess.run([str(s) for s in command], cwd=output, env=environment,
                                    stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f"Validation failed; see {output / log}")
        print(f"Passed: {log}", flush=True)

    run([sys.executable, SCRIPTS / "build_candidate_artifacts.py",
         "--manifest", manifest, "--source-root", source_root, "--output", output / "build",
         "--packages", *args.packages], "build.log")
    dist = output / "build/dist"
    original = sorted(dist.glob("*.whl"))
    require_universal_wheels(original)
    rebuilt = []
    for package in args.packages:
        prefix = "sashimi_itamae" if package == "itamae" else package.replace("-", "_")
        archive, = dist.glob(prefix + "-*.tar.gz")
        wheel, = dist.glob(prefix + "-*.whl")
        target = output / "rebuilt" / package
        run([sys.executable, SCRIPTS / "check_sdist_rebuild.py", "--package", package,
             "--archive", archive, "--original-wheel", wheel,
             "--expected-revision", inputs[package]["ref"], "--output", target],
            f"rebuild-{package}.log")
        rebuilt.append(next(target.glob("*.whl")))

    result = dict(
        schema="sashimi-family:artifact-validation:v1", status="passed", profile=args.profile,
        source_revisions={p: inputs[p]["ref"] for p in args.packages},
        manifest_sha256=digest(manifest), script_sha256=digest(Path(__file__)),
        build_report_sha256=digest(output / "build/build-report.json"),
        build_python=sys.version, python_versions=list(PYTHONS),
        rebuilt_python_versions=list(PYTHONS if args.profile == "full" else PYTHONS[:1]),
        standalone_python_version=PYTHONS[0], original={}, rebuilt={}, standalone={},
        installed_regression={},
    )
    with tempfile.TemporaryDirectory(prefix="sashimi-family-environments-") as temporary:
        environments = Path(temporary)

        def install(name, version, wheels):
            directory = environments / name
            run(["uv", "venv", "--python", version, directory], f"{name}-venv.log")
            python = directory / "bin/python"
            run(["uv", "pip", "install", "--python", python, *wheels], f"{name}-install.log")
            return python

        def smoke(name, python, packages):
            run([python, "-I", SCRIPTS / "smoke_installed_family.py", "--manifest", manifest,
                 "--output", output / name, "--packages", *packages], name + ".log")
            return read(output / name / "report.json")

        for version in PYTHONS:
            name = f"original-{version}"
            python = install(name, version, original)
            data = smoke(name + "-smoke", python, args.packages)
            result["original"][version] = dict(report_sha256=digest(output / (name + "-smoke/report.json")))
            if args.workflow_tests and version == PYTHONS[0]:
                run([python, "-m", "unittest", "discover", "-s", SCRIPTS.parent / "tests"],
                    "workflow-tests.log")
            if version in result["rebuilt_python_versions"]:
                rebuilt_name = f"rebuilt-{version}"
                rebuilt_python = install(rebuilt_name, version, rebuilt)
                rebuilt_data = smoke(rebuilt_name + "-smoke", rebuilt_python, args.packages)
                if physical_results(data) != physical_results(rebuilt_data):
                    raise ValueError(f"Original/rebuilt physical quantities differ on Python {version}")
                result["rebuilt"][version] = dict(
                    report_sha256=digest(output / (rebuilt_name + "-smoke/report.json")),
                    original_rebuilt_quantities_equal=True,
                )
            if args.profile == "full":
                run(["uv", "pip", "install", "--python", python, "pytest", "hatchling",
                     "setuptools>=77", "hypothesis", "pytest-cov", "mpmath", "astropy", "colossus"],
                    f"tests-{version}-dependencies.log")
                target = output / f"tests-{version}"
                run([sys.executable, SCRIPTS / "check_installed_candidate.py", "--python", python,
                     "--sdists", dist, "--manifest", manifest, "--output", target,
                     "--packages", *args.packages], f"tests-{version}.log")
                report = read(target / "report.json")
                counts = {}
                for package in report["packages"]:
                    if any(int(s[key]) for s in package["suites"] for key in ("errors", "failures", "skipped")):
                        raise ValueError("Full validation requires no failing or skipped shipped tests")
                    counts[package["package"]] = sum(int(s["tests"]) for s in package["suites"])
                result["installed_regression"][version] = dict(
                    counts=counts, total=sum(counts.values()), report_sha256=digest(target / "report.json"),
                )

        core, = dist.glob("sashimi_itamae-*.whl")
        for package in args.packages:
            packages = ["itamae"] if package == "itamae" else ["itamae", package]
            wheels = [core]
            if package != "itamae":
                wheels.append(next(dist.glob(package.replace("-", "_") + "-*.whl")))
            name = f"standalone-{package}"
            python = install(name, PYTHONS[0], wheels)
            smoke(name + "-smoke", python, packages)
            result["standalone"][package] = dict(report_sha256=digest(output / (name + "-smoke/report.json")))
    (output / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Family artifact validation passed ({args.profile}); each package built/rebuilt once.")


if __name__ == "__main__":
    main()
