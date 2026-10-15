#!/usr/bin/env python3
"""Build clean exact component revisions named by an effective manifest.

This verifies packaging only; it does not change the authoritative family
manifest or imply scientific adoption of unresolved prescriptions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = tomllib.loads(args.manifest.read_text())
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    environment = {
        k: v for k, v in os.environ.items() if not k.endswith("_SOURCE_REVISION")
    }
    records = []
    for package in ["itamae", "sashimi-c", "sashimi-si", "sashimi-w", "sashimi-f"]:
        entry = manifest[package]
        source = root / entry["path"]
        actual = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != entry["ref"] or subprocess.check_output(
            ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"],
            text=True,
        ):
            raise RuntimeError(
                f"{package}: source must be clean at the manifest revision"
            )
        command = [
            "uv",
            "build",
            "--python",
            sys.executable,
            "--out-dir",
            str(output / "dist"),
            str(source),
        ]
        if args.offline:
            command.append("--offline")
        process = subprocess.run(
            command, env=environment, capture_output=True, text=True
        )
        (output / f"{package}-build.log").write_text(process.stdout + process.stderr)
        if process.returncode:
            raise RuntimeError(f"Build failed: {package}; see saved log")
        records.append(dict(package=package, source_revision=actual))
        print(f"Built {package} at {actual}", flush=True)
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/check_artifact_provenance.py"),
            "--directory",
            str(output / "dist"),
            "--manifest",
            str(args.manifest.resolve()),
            "--require-sdist",
        ],
        check=True,
    )
    report = dict(
        manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=sys.version,
        revision_environment_injected=False,
        source_revisions=records,
        artifacts={
            p.name: dict(
                sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                bytes=p.stat().st_size,
            )
            for p in sorted((output / "dist").iterdir())
            if p.suffix in [".whl", ".gz"]
        },
    )
    (output / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
