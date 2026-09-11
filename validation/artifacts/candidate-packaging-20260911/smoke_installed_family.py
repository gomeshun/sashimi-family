#!/usr/bin/env python3
"""Check exact installed provenance and small standard-API physical calculations.

Run with an isolated Python interpreter outside the source tree. The output
contains numerical catalogs, so keep runs including a private variant private.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as metadata
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import tomllib
import warnings

import numpy as np

from itamae.halo import invert_nfw_mass_function, nfw_mass_function
from itamae.provenance import source_revision
from itamae.types import WeightedSubhaloCatalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packages", nargs="+", default=[
        "itamae", "sashimi-c", "sashimi-si", "sashimi-w", "sashimi-f"
    ])
    args = parser.parse_args()
    manifest = tomllib.loads(args.manifest.read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    installations = {}
    runtime_files = {}
    for package in args.packages:
        dist_name = "sashimi-itamae" if package == "itamae" else package
        module = importlib.import_module(package.replace("-", "_"))
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(Path(sys.prefix).resolve()), path
        revision = source_revision(dist_name)
        assert revision == manifest[package]["ref"], (package, revision)
        dist = metadata.distribution(dist_name)
        installations[package] = dict(version=dist.version, source_revision=revision,
                                      import_path=str(path), wheel_install=json.loads(dist.read_text("direct_url.json")))
        assert installations[package]["wheel_install"]["url"].endswith(".whl")
        runtime_files[package] = {str(p) for p in dist.files or () if ".dist-info" not in str(p)}
    for a, b in itertools.combinations(runtime_files, 2):
        assert not runtime_files[a] & runtime_files[b], (a, b)
    for retired in ("itamae_migration", "itamae_variance", "itamae_catalog_migration"):
        assert importlib.util.find_spec(retired) is None
    try:
        metadata.distribution("itamae")
    except metadata.PackageNotFoundError:
        pass
    else:
        raise AssertionError("Unrelated itamae distribution is installed")
    radii = np.geomspace(1e-6, 1e3, 100)
    np.testing.assert_allclose(invert_nfw_mass_function(nfw_mass_function(radii)), radii, rtol=3e-12)
    options = dict(M0=1e10, redshift=0.0, dz=0.5, zmax=1.0, N_ma=4,
                   N_herm=2, N_hermNa=2, logmamin=6.0, logmamax=8.0)
    catalogs = {}
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always", RuntimeWarning)
        if "sashimi-c" in args.packages:
            from sashimi_c import SubhaloProperties
            catalogs["c"] = SubhaloProperties().subhalo_catalog_calc(**options)
        if "sashimi-si" in args.packages:
            from sashimi_si import SubhaloProperties
            states = SubhaloProperties().subhalo_catalogs_calc(**options)
            for state, catalog in states.items():
                catalogs[f"si-{state}"] = catalog
            np.testing.assert_array_equal(states["cdm_reference"].columns["m200_acc"], states["sidm"].columns["m200_acc"])
        if "sashimi-w" in args.packages:
            from sashimi_w import Subhalos
            model = Subhalos(2.0)
            assert model.wdm_power_q == 10
            catalogs["w"] = model.rs_rhos_catalog_calc(**options)
        if "sashimi-f" in args.packages:
            from sashimi_f import FDMSubhaloProperties
            catalogs["f"] = FDMSubhaloProperties(power_cache_dir=output / "power-cache").subhalo_catalog_calc(m_22=1.0, **options)
    if observed:
        raise AssertionError([str(w.message) for w in observed])
    results = {}
    for name, catalog in catalogs.items():
        assert catalog.shape[0] > 0
        assert all(np.all(np.isfinite(v)) for v in catalog.columns.values())
        assert all(np.all(np.isfinite(v)) and np.all(v >= 0) for v in catalog.weights.values())
        expected = np.prod(list(catalog.weights.values()), axis=0)
        np.testing.assert_array_equal(catalog.weight_final, expected)
        assert catalog.metadata["itamae_source_revision"] == manifest["itamae"]["ref"]
        assert catalog.metadata["sashimi_source_revision"] == manifest[catalog.metadata["sashimi_variant"]]["ref"]
        assert "physics_mode" not in catalog.metadata
        archive = output / f"{name}.npz"
        catalog.to_npz(archive)
        restored = WeightedSubhaloCatalog.from_npz(archive)
        for column, values in catalog.columns.items():
            np.testing.assert_array_equal(restored.columns[column], values)
        np.testing.assert_array_equal(restored.weight_final, catalog.weight_final)
        assert dict(restored.metadata) == dict(catalog.metadata)
        results[name] = dict(rows=catalog.shape[0], count=float(catalog.weight_final.sum()),
                             bound_mass=float(np.sum(catalog.columns["m_bound"] * catalog.weight_final)),
                             count_above_1e6=float(catalog.weight_final[catalog.columns["m_bound"] >= 1e6].sum()),
                             archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    (output / "report.json").write_text(json.dumps(dict(
        python=sys.version, executable=sys.executable, calculation=options,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        installations=installations, results=results, warnings=[]), indent=2) + "\n")
    print(f"Installed provenance, collision and physical smoke passed: {args.packages}")


if __name__ == "__main__":
    main()
