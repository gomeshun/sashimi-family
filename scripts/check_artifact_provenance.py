"""Verify source revisions embedded in built Python artifacts."""

from __future__ import annotations

import argparse
import re
import tarfile
import tomllib
import zipfile
from pathlib import Path

SOURCE_REVISION_PATTERN = re.compile(r"SOURCE_REVISION\s*=\s*['\"]([0-9a-f]{40})['\"]")
ARTIFACT_TARGETS = {
    "itamae": "itamae/_build_provenance.py",
    "sashimi-c": "_sashimi_c_build_provenance.py",
    "sashimi-si": "_sashimi_si_build_provenance.py",
    "sashimi-w": "_sashimi_w_build_provenance.py",
    "sashimi-f": "_sashimi_f_build_provenance.py",
}
ARTIFACT_PREFIXES = {
    "itamae": ("sashimi_itamae-", "itamae-"),
    "sashimi-c": ("sashimi_c-",),
    "sashimi-si": ("sashimi_si-",),
    "sashimi-w": ("sashimi_w-",),
    "sashimi-f": ("sashimi_f-",),
}


def _artifact_text(artifact: Path, target: str) -> str:
    """Read one embedded provenance module from a wheel or source archive."""
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            return archive.read(target).decode("utf-8")
    if artifact.name.endswith(".tar.gz"):
        with tarfile.open(artifact) as archive:
            member = next(
                info
                for info in archive.getmembers()
                if info.name.endswith(f"/{target}") or info.name == target
            )
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ValueError(f"Cannot read {target!r} from {artifact}")
            return extracted.read().decode("utf-8")
    raise ValueError(f"Unsupported artifact {artifact}")


def _check_artifact(artifact: Path, target: str, expected: str) -> None:
    """Assert that one artifact contains the expected full source SHA."""
    text = _artifact_text(artifact, target)
    match = SOURCE_REVISION_PATTERN.fullmatch(text.strip())
    if match is None:
        raise ValueError(
            f"{artifact.name} does not contain a valid embedded source revision"
        )
    if match.group(1) != expected:
        raise ValueError(
            f"{artifact.name} contains {match.group(1)}, expected {expected}"
        )


def _matching_artifacts(directory: Path, prefixes: tuple[str, ...], suffix: str) -> list[Path]:
    """Return artifacts matching any supported distribution filename prefix."""
    return sorted(
        {
            artifact
            for prefix in prefixes
            for artifact in directory.glob(f"{prefix}*{suffix}")
        }
    )


def main() -> int:
    """Check wheel artifacts and any available source distributions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--packages", nargs="+", choices=sorted(ARTIFACT_TARGETS))
    parser.add_argument("--require-sdist", action="store_true")
    args = parser.parse_args()

    with args.manifest.open("rb") as stream:
        manifest = tomllib.load(stream)
    packages = args.packages or tuple(ARTIFACT_TARGETS)
    for package in packages:
        entry = manifest.get(package)
        if not isinstance(entry, dict) or not isinstance(entry.get("ref"), str):
            raise ValueError(f"Manifest has no exact ref for {package!r}")
        expected = entry["ref"]
        prefixes = ARTIFACT_PREFIXES[package]
        wheels = _matching_artifacts(args.directory, prefixes, ".whl")
        sdists = _matching_artifacts(args.directory, prefixes, ".tar.gz")
        if len(wheels) != 1:
            raise ValueError(
                f"Expected exactly one wheel for {package!r}; found {wheels}"
            )
        if args.require_sdist and len(sdists) != 1:
            raise ValueError(
                f"Expected exactly one sdist for {package!r}; found {sdists}"
            )
        target = ARTIFACT_TARGETS[package]
        for artifact in [*wheels, *sdists]:
            _check_artifact(artifact, target, expected)
            print(f"{artifact.name}: {expected}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
