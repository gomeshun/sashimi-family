#!/usr/bin/env python3
"""Export a fixed W revision and save q10 numerical controls in a fresh process.

Run separately for the old and adopted revisions, using the same installed core
and dependency environment. Artifacts are never overwritten.
"""

from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import warnings
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ["git", "-C", str(root / "sashimi-w"), "rev-parse", args.revision], text=True
    ).strip()
    core_revision = subprocess.check_output(
        ["git", "-C", str(root / "itamae"), "rev-parse", "HEAD"], text=True
    ).strip()
    if subprocess.check_output(
        ["git", "-C", str(root / "itamae"), "diff", "HEAD", "--", "*.py"], text=True
    ):
        raise RuntimeError("Core Python source is not clean")
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    archive = subprocess.check_output(
        ["git", "-C", str(root / "sashimi-w"), "archive", revision]
    )
    with tempfile.TemporaryDirectory(prefix="sashimi-w-q10-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as handle:
            handle.extractall(directory, filter="data")
        sys.path.insert(0, str(Path(directory) / "src" if (Path(directory) / "src").is_dir() else Path(directory)))
        from sashimi_w import Subhalos, Msolar
        import itamae

        if Path(itamae.__file__).resolve().parents[2] != root / "itamae":
            raise RuntimeError("Expected the recorded editable core")
        parameters = dict(
            M0=1e12,
            redshift=0.0,
            dz=0.25,
            zmax=1.0,
            N_ma=16,
            logmamin=7.0,
            logmamax=10.0,
            N_herm=3,
            N_hermNa=4,
        )
        mass = np.geomspace(1e6, 1e14, 81)
        k = np.geomspace(1e-4, 1e3, 101)
        redshift = np.array([0.0, 0.5, 1.0, 3.0])[:, None]
        report = dict(
            schema="sashimi-w:q10-adoption-control:v1",
            source_revision=revision,
            source_archive_sha256=hashlib.sha256(archive).hexdigest(),
            itamae_source_revision=core_revision,
            python=sys.version,
            dependencies={
                name: importlib.metadata.version(name)
                for name in ["numpy", "scipy", "sashimi-itamae"]
            },
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            parameters=parameters,
            rows=[],
        )
        for particle_mass in [0.5, 2.0, 5.0]:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model = Subhalos(particle_mass, wdm_power_convention="standard-t2-q10")
                catalog = model.rs_rhos_catalog_calc(**parameters)
                arrays = dict(
                    mass=mass,
                    k_h_per_Mpc=k,
                    redshift=redshift,
                    power_ratio=model._wdm_power_ratio(k),
                    sigma=model.sigmaMz(mass, redshift),
                    derivative=model.dsdm(mass, redshift),
                    concentration=model.conc200(mass * Msolar, 0.5),
                    half_mode=np.asarray(model.half_mode_wavenumber()),
                    weight_final=catalog.weight_final,
                )
                arrays.update(
                    {"column_" + name: value for name, value in catalog.columns.items()}
                )
                arrays.update(
                    {"weight_" + name: value for name, value in catalog.weights.items()}
                )
                if not all(np.all(np.isfinite(value)) for value in arrays.values()):
                    raise AssertionError("Nonfinite q10 control")
                output = args.output / f"q10-{particle_mass:g}keV.npz"
                np.savez_compressed(output, **arrays)
                row = dict(
                    mass_wdm_keV=particle_mass,
                    file=output.name,
                    sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                    metadata=dict(catalog.metadata),
                    warnings=[str(w.message) for w in caught],
                    count=float(catalog.weight_final.sum()),
                    bound_mass_fraction=float(
                        catalog.weight_final
                        @ catalog.columns["m_bound"]
                        / parameters["M0"]
                    ),
                    arrays={
                        name: dict(shape=list(value.shape), dtype=str(value.dtype))
                        for name, value in arrays.items()
                    },
                )
                report["rows"].append(row)
                (args.output / "report.json").write_text(
                    json.dumps(report, indent=2) + "\n"
                )
                print(
                    f"{particle_mass:g} keV: count={row['count']:.17g}, warnings={len(caught)}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
