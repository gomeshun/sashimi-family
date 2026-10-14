#!/usr/bin/env python3
"""Save controlled grid/solver sweeps and full catalogs from clean candidates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import warnings

import numpy as np


def main():
    r"""Run controlled catalogue grid and solver variations around one frozen halo setup.

    Notes
    -----
    The literature threshold rt/rs > 0.77 follows the Hayashi et al. disruption prescription
    adopted by Hiroshima et al. A caller-supplied threshold takes precedence in variants
    that expose it (C and SI currently default to 0). This is a model selection rule; an
    exact-boundary test does not calibrate disruption physics.

    The setup fixes M200=1e12 Msun at z=0 and the literature truncation cut ct>0.77, then varies one quadrature or solver control at a time. Finite nonnegative weights and a gross mass-increase bound are implementation sanity conditions; resolution differences measure finite-grid sensitivity, not model calibration. Output paths must be new, and source revisions and script hashes accompany every catalogue.

    References
    ----------

    .. [cite-survival] Hayashi et al. (2003), The Structural Evolution of Substructure, Section 2.1.
        https://arxiv.org/abs/astro-ph/0203004

    .. [cite-structure] Hiroshima, Ando & Ishiyama (2018), Modeling evolution of dark matter substructure and annihilation boost, Section II, Eqs. (4)-(9), (28), (34).
        https://arxiv.org/abs/1803.07691
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant", choices=["sashimi-c", "sashimi-si", "sashimi-f"], required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--particle-mass", type=float, default=1.0)
    parser.add_argument("--cases", nargs="+", help="Run only these named cases.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = [root / args.variant, root / "itamae"]
    revisions = {}
    for source in sources:
        if subprocess.check_output(
            ["git", "-C", str(source), "diff", "HEAD", "--", "*.py"], text=True
        ):
            raise RuntimeError(f"Uncommitted Python changes: {source}")
        revisions[source.name] = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
    sys.path.insert(0, str(sources[0] / "src"))
    if args.variant == "sashimi-c":
        from sashimi_c import SubhaloProperties
    elif args.variant == "sashimi-si":
        from sashimi_si import SubhaloProperties
    else:
        from sashimi_f import FDMSubhaloProperties as SubhaloProperties
    if args.output.exists():
        raise FileExistsError(f"Refusing to replace previous results: {args.output}")
    args.output.mkdir(parents=True)
    base = dict(
        M0=1e12,
        redshift=0.0,
        dz=0.25,
        zmax=3.0,
        N_ma=16,
        logmamin=6.0,
        logmamax=10.0,
        N_herm=3,
        N_hermNa=8,
        ct_th=0.77,
        method="pert2_shanks",
    )
    if args.variant == "sashimi-f":
        base["m_22"] = args.particle_mass
    cases = [("baseline", {})]
    for name, values in [
        ("N_ma", [32, 64, 128, 256, 500]),
        ("dz", [0.125, 0.0625, 0.03125, 0.015625, 0.01, 0.005]),
        ("N_herm", [5, 7]),
        ("N_hermNa", [16, 32, 64, 200]),
    ]:
        cases.extend((f"{name}-{value}", {name: value}) for value in values)
    cases.extend(
        [
            ("odeint", {"method": "odeint"}),
            ("odeint-tight", {"method": "odeint", "rtol": 1e-10, "atol": 1e-8}),
        ]
    )
    if args.cases:
        unknown = set(args.cases) - {name for name, _ in cases}
        if unknown:
            raise ValueError(f"Unknown cases: {sorted(unknown)}")
        cases = [(name, parameters) for name, parameters in cases if name in args.cases]
    report = dict(
        variant=args.variant,
        source_revisions=revisions,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        dependencies={
            n: importlib.metadata.version(n)
            for n in ["numpy", "scipy", "sashimi-itamae"]
        },
        interpretation="One variable at a time; finite-grid sensitivity, not a continuum truth or recalibration.",
        rows=[],
    )
    for label, override in cases:
        parameters = {**base, **override}
        start = time.perf_counter()
        model = SubhaloProperties()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            if args.variant == "sashimi-si":
                catalogs = model.subhalo_catalogs_calc(**parameters)
            else:
                catalogs = {"default": model.subhalo_catalog_calc(**parameters)}
        row = dict(
            label=label,
            parameters=parameters,
            seconds=time.perf_counter() - start,
            warnings=[str(w.message) for w in caught],
            states={},
        )
        for state, cat in catalogs.items():
            path = args.output / f"{label}-{state}.npz"
            cat.to_npz(path)
            w, columns = cat.weight_final, cat.columns
            if not all(np.all(np.isfinite(x)) for x in [w, *columns.values()]):
                raise AssertionError("nonfinite catalog")
            if np.any(w < 0) or np.any(columns["m_bound"] > columns["m200_acc"] * 2):
                raise AssertionError("invalid weight or gross mass increase")
            metrics = dict(
                count=float(w.sum()),
                bound_mass_fraction=float(w @ columns["m_bound"] / base["M0"]),
                count_above_1e7=float(w[columns["m_bound"] > 1e7].sum()),
            )
            if args.variant != "sashimi-si":
                luminosity = (
                    columns["rho_s"] ** 2
                    * columns["r_s"] ** 3
                    * (1 - (1 + columns["c_t"]) ** -3)
                )
                metrics["NFW_luminosity_sum"] = float(w @ luminosity)
            else:
                metrics["mean_vmax_km_s"] = float(
                    w
                    @ columns["v_max_sidm" if state == "sidm" else "v_max_cdm"]
                    / w.sum()
                )
            row["states"][state] = dict(
                metrics=metrics,
                nodes=len(w),
                file=path.name,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        report["rows"].append(row)
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
