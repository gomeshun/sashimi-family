"""Validate the family compatibility manifest against committed gitlinks."""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "compatibility.toml"
REPOSITORIES = ("itamae", "sashimi-c", "sashimi-si", "sashimi-w", "sashimi-f")
EXPECTED_REPOSITORIES = {
    "itamae": "gomeshun/itamae",
    "sashimi-c": "gomeshun/sashimi-c",
    "sashimi-si": "gomeshun/sashimi-si",
    "sashimi-w": "gomeshun/sashimi-w",
    "sashimi-f": "gomeshun/sashimi-f",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")


def committed_gitlink(path: str) -> str:
    """Return the object ID recorded for a submodule path in HEAD."""
    result = subprocess.run(
        ["git", "ls-tree", "-z", "HEAD", "--", path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=False,
    )
    entries = result.stdout.rstrip(b"\0").split(b"\0")
    if len(entries) != 1:
        raise ValueError(f"expected one gitlink for {path!r}")
    mode, object_type, value = entries[0].decode().split(" ", 2)
    sha, recorded_path = value.split("\t", 1)
    if mode != "160000" or object_type != "commit" or recorded_path != path:
        raise ValueError(f"{path!r} is not a submodule gitlink")
    return sha


def gitmodules_entries() -> dict[str, dict[str, str]]:
    """Return submodule path and URL values from the checked-in git config."""
    result = subprocess.run(
        [
            "git",
            "config",
            "--file",
            str(ROOT / ".gitmodules"),
            "--get-regexp",
            r"^submodule\..*\.(path|url)$",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    entries: dict[str, dict[str, str]] = {}
    for line in result.stdout.splitlines():
        key, value = line.split(maxsplit=1)
        match = re.fullmatch(r"submodule\.(.+)\.(path|url)", key)
        if match is None:
            raise ValueError(f"unexpected .gitmodules key {key!r}")
        name, field = match.groups()
        entries.setdefault(name, {})[field] = value
    return entries


def main() -> int:
    """Validate all manifest entries and return a process status."""
    with MANIFEST.open("rb") as stream:
        manifest = tomllib.load(stream)

    errors: list[str] = []
    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict) or compatibility.get("schema") != 1:
        errors.append("compatibility.schema must be 1")

    try:
        submodules = gitmodules_entries()
    except (subprocess.CalledProcessError, ValueError) as error:
        errors.append(f"cannot read .gitmodules: {error}")
        submodules = {}

    for name in REPOSITORIES:
        entry = manifest.get(name)
        if not isinstance(entry, dict):
            errors.append(f"missing [{name}] entry")
            continue
        repo = entry.get("repo")
        path = entry.get("path")
        ref = entry.get("ref")
        if repo != EXPECTED_REPOSITORIES[name]:
            errors.append(
                f"[{name}].repo must be {EXPECTED_REPOSITORIES[name]!r}; received {repo!r}"
            )
        if path != name:
            errors.append(f"[{name}].path must be {name!r}; received {path!r}")
        if not isinstance(path, str) or not path:
            continue
        if not isinstance(ref, str) or SHA_PATTERN.fullmatch(ref) is None:
            errors.append(f"[{name}].ref must be a 40-character lowercase SHA")
            continue
        try:
            actual = committed_gitlink(path)
        except (subprocess.CalledProcessError, ValueError) as error:
            errors.append(f"[{name}] cannot read gitlink {path!r}: {error}")
            continue
        if actual != ref:
            errors.append(
                f"[{name}] manifest ref {ref} does not match gitlink {path}: {actual}"
            )

        submodule = submodules.get(name)
        if submodule is None:
            errors.append(f".gitmodules is missing submodule {name!r}")
        else:
            expected_url = f"git@github.com:{EXPECTED_REPOSITORIES[name]}.git"
            if submodule.get("path") != name:
                errors.append(
                    f".gitmodules submodule {name!r} path must be {name!r}; "
                    f"received {submodule.get('path')!r}"
                )
            if submodule.get("url") != expected_url:
                errors.append(
                    f".gitmodules submodule {name!r} URL must be {expected_url!r}; "
                    f"received {submodule.get('url')!r}"
                )

    unexpected_submodules = set(submodules) - set(REPOSITORIES)
    for name in sorted(unexpected_submodules):
        errors.append(f".gitmodules contains unexpected submodule {name!r}")

    if errors:
        print("Compatibility manifest validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Compatibility manifest matches {len(REPOSITORIES)} committed gitlinks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
