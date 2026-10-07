#!/usr/bin/env python3
"""Run shipped regression tests against wheels in an isolated interpreter.

The interpreter must already contain the candidate wheels and test dependencies.
Only tests, frozen references and build hooks are copied out of the sdists;
production modules are always imported from that interpreter's site-packages.
Private component test material stays in the caller-selected output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tomllib
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--sdists", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packages", nargs="+", default=[
        "itamae", "sashimi-c", "sashimi-si", "sashimi-w", "sashimi-f"
    ])
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = tomllib.loads(args.manifest.read_text())
    environment = {
        k: v for k, v in os.environ.items()
        if not k.endswith("_SOURCE_REVISION") and k not in {"PYTHONPATH", "PYTHONHOME"}
    }
    environment.update(
        SASHIMI_F_CACHE_DIR=str(output / "cache-f"),
        MPLCONFIGDIR=str(output / "matplotlib"), MPLBACKEND="Agg",
    )
    records = []
    for package in args.packages:
        distribution = "sashimi-itamae" if package == "itamae" else package
        archives = list(args.sdists.glob(distribution.replace("-", "_") + "-*.tar.gz"))
        if len(archives) != 1:
            raise ValueError(f"Expected one sdist for {package}, found {archives}")
        archive = archives[0]
        test_root = output / package
        test_root.mkdir()
        inputs = {}
        with tarfile.open(archive) as bundle:
            for member in bundle.getmembers():
                relative = Path(*Path(member.name).parts[1:])
                if not member.isfile() or ".." in relative.parts:
                    continue
                if relative.parts[0] not in {"tests", "validation"} and str(relative) not in {"setup.py", "hatch_build.py"}:
                    continue
                data = bundle.extractfile(member).read()
                target = test_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                inputs[str(relative)] = hashlib.sha256(data).hexdigest()
        module = package.replace("-", "_")
        probe = """
import importlib, importlib.metadata as md, json, pathlib, sys
from itamae.provenance import source_revision
package, module, expected = sys.argv[1:]
loaded = importlib.import_module(module)
path = pathlib.Path(loaded.__file__).resolve()
assert path.is_relative_to(pathlib.Path(sys.prefix).resolve()), path
assert source_revision(package) == expected
dist = md.distribution(package)
direct = json.loads(dist.read_text('direct_url.json'))
assert direct['url'].endswith('.whl'), direct
assert not direct.get('dir_info', {}).get('editable', False)
print(json.dumps(dict(python=sys.version, executable=sys.executable,
    module_path=str(path), version=dist.version, source_revision=expected,
    wheel_install=direct, dependencies={d.metadata['Name']: d.version for d in md.distributions()})))
"""
        identity = subprocess.check_output(
            [str(args.python.absolute()), "-I", "-c", probe, distribution, module, manifest[package]["ref"]],
            cwd=test_root, env=environment, text=True,
        )
        command = [str(args.python.absolute()), "-I", "-m", "pytest", "tests", "-q",
                   "--import-mode=importlib", "--junitxml=result.xml"]
        with (test_root / "pytest.log").open("w") as log:
            process = subprocess.run(command, cwd=test_root, env=environment, stdout=log, stderr=subprocess.STDOUT)
        xml_path = test_root / "result.xml"
        suites = [] if not xml_path.exists() else [dict(e.attrib) for e in ET.parse(xml_path).getroot().iter("testsuite")]
        record = dict(package=package, installation=json.loads(identity),
                      sdist_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      shipped_test_inputs=inputs, exit_code=process.returncode, suites=suites)
        records.append(record)
        (output / "report.json").write_text(json.dumps(dict(
            manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            packages=records), indent=2) + "\n")
        print(f"{package}: exit {process.returncode}; {suites}", flush=True)
    if any(r["exit_code"] for r in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
