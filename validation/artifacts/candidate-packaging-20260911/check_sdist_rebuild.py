"""Rebuild a pinned sdist inside unrelated Git state, without revision injection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile

TARGETS = {
    "itamae": "itamae/_build_provenance.py",
    **{
        f"sashimi-{variant}": f"_sashimi_{variant}_build_provenance.py"
        for variant in ("c", "si", "w", "f")
    },
}
REVISION = re.compile(r"SOURCE_REVISION\s*=\s*['\"]([0-9a-f]{40})['\"]")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, choices=TARGETS)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if re.fullmatch("[0-9a-f]{40}", args.expected_revision) is None:
        parser.error("expected-revision must be a complete source SHA")
    archive = args.archive.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = TARGETS[args.package]
    with tempfile.TemporaryDirectory(
        prefix="archive-rebuild-", dir=output
    ) as temporary:
        parent = Path(temporary)

        def git(*arguments):
            return subprocess.check_output(
                ["git", "-C", str(parent), *arguments], text=True
            ).strip()

        git("init", "--quiet")
        (parent / "unrelated.txt").write_text("Unrelated build-directory source.\n")
        git("add", "unrelated.txt")
        git(
            "-c",
            "user.name=Build verification",
            "-c",
            "user.email=build@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Unrelated build repository",
        )
        unrelated = git("rev-parse", "HEAD")
        with tarfile.open(archive) as stream:
            stream.extractall(parent, filter="data")
        sources = [p for p in parent.iterdir() if p.is_dir() and p.name != ".git"]
        if len(sources) != 1:
            raise RuntimeError(
                "Source archive must contain exactly one package directory."
            )
        source = sources[0]
        descriptors = [source / target, source / "src" / target]
        descriptor = next((p for p in descriptors if p.is_file()), None)
        match = REVISION.search(descriptor.read_text()) if descriptor else None
        if match is None or match.group(1) != args.expected_revision:
            raise RuntimeError("Archive does not embed the expected source revision.")
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.endswith("_SOURCE_REVISION")
        }
        command = [
            "uv",
            "build",
            "--wheel",
            "--python",
            sys.executable,
            "--out-dir",
            str(output),
            str(source),
        ]
        if args.offline:
            command.append("--offline")
        result = subprocess.run(
            command, env=environment, capture_output=True, text=True
        )
        (output / "build.log").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(
                f"Source-archive rebuild failed; see {output / 'build.log'}"
            )
        wheels = list(output.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("Expected one rebuilt wheel in the output directory.")
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as stream:
            match = REVISION.search(stream.read(target).decode())
            if match is None or match.group(1) != args.expected_revision:
                raise RuntimeError("Rebuilt wheel lost the original source revision.")
        report = {
            "package": args.package,
            "source_revision": args.expected_revision,
            "unrelated_parent_revision": unrelated,
            "revision_environment_injected": False,
            "python": sys.version,
            "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "wheel": wheel.name,
            "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "result": "source identity preserved",
        }
        (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report))


if __name__ == "__main__":
    main()
