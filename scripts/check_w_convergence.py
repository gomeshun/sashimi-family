"""Reconcile the reported W redshift sweep with every frozen full catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    summary_path = root / "redshift-convergence.json"
    summary = json.loads(summary_path.read_text())
    reports = []
    for q in (5, 10):
        fixed = None
        for label, step in (
            ("dz010", 0.1),
            ("dz005", 0.05),
            ("dz0025", 0.025),
            ("dz00125", 0.0125),
        ):
            name = f"C-dcc4379-convergence-q{q}-{label}"
            config_path = root / f"{name}.json"
            config = json.loads(config_path.read_text())
            artifact = root / "fixtures" / f"{name}.npz"
            sidecar = json.loads(artifact.with_suffix(".json").read_text())
            assert digest(artifact) == sidecar["artifact_sha256"]
            assert config == sidecar["calculation"]
            assert config["source_revision"] == summary["source_revision"]
            assert config["itamae_source_revision"] == summary["core_revision"]
            assert sidecar["source_checkouts_clean"] and sidecar["independent_process"]
            parameters = dict(config["parameters"])
            assert parameters.pop("dz") == step
            if fixed is None:
                fixed = parameters
            assert parameters == fixed
            assert parameters["redshift"] == 0.0
            with np.load(artifact, allow_pickle=False) as values:
                assert all(np.all(np.isfinite(values[key])) for key in values.files)
                weight = values["tuple_8"] * values["tuple_9"]
                bound_mass = values["tuple_4"]
                assert np.all(weight >= 0.0)
                calculated = {
                    "count_surviving": float(np.sum(weight)),
                    "bound_mass_fraction": float(
                        np.sum(bound_mass * weight) / parameters["M0"]
                    ),
                    "count_above_1e7": float(np.sum(weight[bound_mass > 1.0e7])),
                }
            expected = summary["metrics"][f"q{q}"][str(step)]
            for key, value in calculated.items():
                np.testing.assert_allclose(value, expected[key], rtol=2.0e-14, atol=0.0)
            reports.append(
                {
                    "q": q,
                    "dz": step,
                    "artifact_sha256": digest(artifact),
                    "config_sha256": digest(config_path),
                    "metrics": calculated,
                    "dependencies": sidecar["dependencies"],
                }
            )
        metrics = summary["metrics"][f"q{q}"]
        for key in metrics["0.1"]:
            ratio = metrics["0.0125"][key] / metrics["0.1"][key] - 1.0
            np.testing.assert_allclose(
                ratio,
                summary[f"q{q}_relative_00125_vs_01"][key],
                rtol=2.0e-14,
                atol=0.0,
            )
    return {
        "status": "share with finite-resolution caveats",
        "summary_sha256": digest(summary_path),
        "worker_sha256": digest(Path(__file__)),
        "checks": reports,
        "scope": "Recomputed metrics from eight frozen full catalogs; not a continuum or simulation calibration.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path("validation/references/sashimi-w")
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.root)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Verified {len(report['checks'])} frozen catalogs: {args.output}")
