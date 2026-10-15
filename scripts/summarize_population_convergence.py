#!/usr/bin/env python3
"""Audit saved C/SI sweeps and summarize one-variable resolution sensitivity.

No population is recalculated. Original report hashes, warnings and failures
are retained; fine grids are comparators, not continuum truth.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

import numpy as np
from itamae.types import WeightedSubhaloCatalog

SOURCES = {
    "sashimi-c": [
        "convergence-3fefa34",
        "convergence-fine-3fefa34",
        "eps-catalog-3a822be",
    ],
    "sashimi-si": [
        "convergence-b983435",
        "convergence-fine-a233326",
        "eps-catalog-31cfcad",
    ],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=list(SOURCES), required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    folder = root / "validation/science" / args.variant
    destination = folder / "summary.json"
    if destination.exists():
        raise FileExistsError(destination)
    sys.path.insert(0, str(root / args.variant))
    module = importlib.import_module(args.variant.replace("-", "_"))
    model = module.SubhaloProperties()
    reports, rows, duplicates = [], {}, []
    source_catalogs = {}
    for name in SOURCES[args.variant]:
        source = folder / name / "report.json"
        report = json.loads(source.read_text())
        reports.append(
            dict(
                path=str(source.relative_to(root)),
                sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                source_revisions=report["source_revisions"],
                dependencies=report["dependencies"],
                failure=report.get("failure"),
            )
        )
        for row in report["rows"]:
            label = row["label"]
            for state, values in row["states"].items():
                path = source.parent / values["file"]
                assert hashlib.sha256(path.read_bytes()).hexdigest() == values["sha256"]
                catalog = WeightedSubhaloCatalog.from_npz(path)
                weight = catalog.weight_final
                columns = catalog.columns
                assert np.all(weight >= 0)
                assert all(np.all(np.isfinite(a)) for a in [weight, *columns.values()])
                virial = (
                    model.Mvir_from_M200_fit(
                        columns["m200_acc"] * model.Msun, columns["z_acc"]
                    )
                    / model.Msun
                )
                assert np.all(columns["m_bound"] <= virial * (1 + 5e-14))
                recomputed = dict(
                    count=float(weight.sum()),
                    bound_mass_fraction=float(
                        weight @ columns["m_bound"] / row["parameters"]["M0"]
                    ),
                    count_above_1e7=float(weight[columns["m_bound"] > 1e7].sum()),
                )
                if "NFW_luminosity_sum" in values["metrics"]:
                    luminosity = (
                        columns["rho_s"] ** 2
                        * columns["r_s"] ** 3
                        * (1 - (1 + columns["c_t"]) ** -3)
                    )
                    recomputed["NFW_luminosity_sum"] = float(weight @ luminosity)
                else:
                    velocity = columns["v_max_sidm" if state == "sidm" else "v_max_cdm"]
                    recomputed["mean_vmax_km_s"] = float(
                        weight @ velocity / weight.sum()
                    )
                for metric, value in recomputed.items():
                    np.testing.assert_allclose(
                        value, values["metrics"][metric], rtol=2e-14, atol=0
                    )
                key = label, state
                if key in source_catalogs:
                    old = WeightedSubhaloCatalog.from_npz(source_catalogs[key])
                    assert (
                        old.columns.keys() == columns.keys()
                        and old.weights.keys() == catalog.weights.keys()
                    )
                    exact = all(
                        np.array_equal(old.columns[k], columns[k]) for k in columns
                    ) and all(
                        np.array_equal(old.weights[k], catalog.weights[k])
                        for k in catalog.weights
                    )
                    assert exact, key
                    duplicates.append(
                        dict(
                            label=label,
                            state=state,
                            before=str(source_catalogs[key].relative_to(root)),
                            after=str(path.relative_to(root)),
                            arrays_bitwise_equal=True,
                        )
                    )
                source_catalogs[key] = path
            rows[label] = {**row, "source_report": str(source.relative_to(root))}
    state = "default" if args.variant == "sashimi-c" else "sidm"
    comparisons = []
    for before, after in [
        ("N_ma-256", "N_ma-500"),
        ("dz-0.01", "dz-0.005"),
        ("N_herm-5", "N_herm-7"),
        ("N_hermNa-64", "N_hermNa-200"),
        ("baseline", "odeint"),
        ("odeint", "odeint-tight"),
    ]:
        a, b = (
            rows[before]["states"][state]["metrics"],
            rows[after]["states"][state]["metrics"],
        )
        comparisons.append(
            dict(
                before=before,
                after=after,
                state=state,
                relative_percent={k: 100 * (b[k] / a[k] - 1) for k in a},
            )
        )
    summary = dict(
        variant=args.variant,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        sources=reports,
        interpretation="One-variable finite-grid comparisons at fixed reduced settings; no extrapolation or default recalibration. Fitted accretion virial-mass bound, finite arrays, nonnegative weights and all displayed metrics checked for every saved catalog.",
        rows=rows,
        repeated_catalog_checks=duplicates,
        final_refinements=comparisons,
    )
    destination.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
