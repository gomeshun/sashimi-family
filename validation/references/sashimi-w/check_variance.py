"""Compare W sharp-k quadrature to adaptive integration on original table knots.

Run with the candidate ITAMAE environment and --family-root pointing to the
family checkout. The pre-repair integrator is exported from its immutable Git
object; the scientific spectrum is supplied explicitly by SASHIMI-W.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from scipy.integrate import quad


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.family_root.resolve()
    sys.path.insert(0, str(root / "sashimi-w"))
    from sashimi_w import h, k_file
    from sashimi_w_itamae_migration import (
        ItamaeSubhalos,
        PUBLISHED_Q5,
        STANDARD_T2_Q10,
    )
    from sashimi_w_itamae_variance import make_integrated_variance_model

    old_revision = "d439a46163d1e8b5e9513650aa3f6697bb38b9a7"
    source = subprocess.check_output(
        [
            "git",
            "-C",
            str(root / "itamae"),
            "show",
            old_revision + ":src/itamae/variance/integrated.py",
        ],
        text=True,
    )
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "old_integrated.py"
        path.write_text(source)
        spec = importlib.util.spec_from_file_location("old_integrated", path)
        old = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = old
        spec.loader.exec_module(old)
    results = {}
    for convention in (PUBLISHED_Q5, STANDARD_T2_Q10):
        model = ItamaeSubhalos(2.0, wdm_power_convention=convention)
        new = make_integrated_variance_model(model, n_k=4097)
        previous = old.IntegratedVarianceModel(
            power=new.power,
            window=new.window,
            rho_mean=new.rho_mean,
            k_min=new.k_min,
            k_max=new.k_max,
            n_k=4097,
            filter_scale=new.filter_scale,
        )
        masses = np.geomspace(1e-4, 1e14, 13)
        reference, errors = [], []
        for mass in masses:
            cutoff = min(
                new.filter_scale / (3 * mass / (4 * np.pi * new.rho_mean)) ** (1 / 3),
                new.k_max,
            )
            bounds = (np.log(new.k_min), np.log(cutoff))
            points = np.log(k_file * float(h))
            points = points[(points > bounds[0]) & (points < bounds[1])]
            value, error = quad(
                lambda t: float(np.exp(3 * t) * new.power(np.exp(t)) / (2 * np.pi**2)),
                *bounds,
                points=points,
                epsabs=1e-10,
                epsrel=1e-10,
                limit=len(points) + 100,
            )
            reference.append(value)
            errors.append(error)
        plateau = np.geomspace(1e-12, 1e14, 1000)
        derivative_mass = np.geomspace(1e9, 1e13, 24)
        upper, lower = derivative_mass * np.exp(1e-4), derivative_mass * np.exp(-1e-4)
        numerical = (
            model.sigmaMz(upper, 0.5) ** 2 - model.sigmaMz(lower, 0.5) ** 2
        ) / (upper - lower)
        results[convention] = {
            "mass_Msun": masses.tolist(),
            "reference_quad": reference,
            "quad_absolute_error": errors,
            "old4097": previous.variance(masses).tolist(),
            "new_by_nk": {
                str(n): make_integrated_variance_model(model, n_k=n)
                .variance(masses)
                .tolist()
                for n in (513, 1025, 2049, 4097, 8193)
            },
            "old_plateau_max_increase": float(
                np.diff(previous.variance(plateau)).max()
            ),
            "new_plateau_max_increase": float(np.diff(new.variance(plateau)).max()),
            "derivative_max_relative_difference": float(
                np.max(abs(model.dsdm(derivative_mass, 0.5) / numerical - 1))
            ),
            "variance_identifier": new.identifier,
        }
    metadata = {
        "old_integrator_revision": old_revision,
        "worker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "revisions": {
            name: subprocess.check_output(
                ["git", "-C", str(root / name), "rev-parse", "HEAD"], text=True
            ).strip()
            for name in ("itamae", "sashimi-w")
        },
        "tracked_changes": {
            name: subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(root / name),
                    "status",
                    "--porcelain",
                    "--untracked-files=no",
                ],
                text=True,
            )
            for name in ("itamae", "sashimi-w")
        },
        "results": results,
    }
    args.output.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
