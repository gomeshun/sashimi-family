"""Evaluate a pinned product checkout in a process separate from references A/B.

This development comparison uses clean source checkouts. Final release evidence
must additionally run the built wheels outside all source repositories.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import warnings

import numpy as np


def checked_revision(source, expected):
    actual = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    status = subprocess.check_output(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    )
    if actual != expected or status:
        raise ValueError(
            f"Product source must be clean at the requested revision: {source}"
        )
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if config["role"] != "C":
        raise ValueError("Product worker requires comparison role C.")
    source = args.source.resolve()
    checked_revision(source, config["source_revision"])
    sys.path.insert(0, str(source / "src" if (source / "src").is_dir() else source))
    import itamae

    core = Path(itamae.__file__).resolve().parents[2]
    checked_revision(core, config["itamae_source_revision"])
    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as observed:
        module = importlib.import_module(config["module"])
        if not Path(module.__file__).resolve().is_relative_to(source):
            raise ValueError("Unexpected product import path.")
        warnings.simplefilter("always", RuntimeWarning)
        model = getattr(module, config["class"])(**config.get("constructor", {}))
        result = getattr(model, config["method"])(**config["parameters"])
        payload = {f"tuple_{i}": np.asarray(value) for i, value in enumerate(result)}
        for probe in config.get("probes", []):
            payload["probe_" + probe["name"]] = np.asarray(
                getattr(model, probe["method"])(
                    *[
                        np.asarray(x) if isinstance(x, list) else x
                        for x in probe.get("args", [])
                    ],
                    **probe.get("kwargs", {}),
                )
            )
    metadata = {
        "schema": "sashimi-family:product-comparison:v1",
        "role": "C",
        "source_revision": config["source_revision"],
        "itamae_source_revision": config["itamae_source_revision"],
        "calculation": config,
        "python": sys.version,
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "sashimi-itamae")
        },
        "worker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "wall_seconds": time.perf_counter() - started,
        "warnings": sorted({str(w.message) for w in observed}),
        "source_checkouts_clean": True,
        "independent_process": True,
        "arrays": {
            name: {
                "shape": list(a.shape),
                "dtype": str(a.dtype),
                "nonfinite": int(np.sum(~np.isfinite(a))),
            }
            for name, a in payload.items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **payload)
    metadata["artifact_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False) + "\n"
    )


if __name__ == "__main__":
    main()
