#!/usr/bin/env python3
"""Check product/independent-fit agreement, CLASS densities, and run warnings.

This runs only after the independent spectra have been computed. Importing the
current W product here does not supply any SASHIMI ingredients to CLASS.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from analyze_wmap7_class_validation import published_fits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # Select the recorded working source, not an unrelated installed W package.
    sys.path[:0] = [str(root / "sashimi-w/src"), str(root / "itamae/src")]
    import sashimi_w
    from sashimi_w import Subhalos

    provenance = json.loads((args.raw / "provenance.json").read_text())
    actual_revision = subprocess.check_output(
        ["git", "-C", str(root / "sashimi-w"), "rev-parse", "HEAD"], text=True).strip()
    if actual_revision != provenance["w_revision"]:
        raise RuntimeError("Current W source differs from the recorded revision")
    if Path(sashimi_w.__file__).resolve() != root / "sashimi-w/src/sashimi_w/__init__.py":
        raise RuntimeError("Imported unexpected SASHIMI-W source")
    result = dict(product_module=str(Path(sashimi_w.__file__).resolve()), checks=[],
                  physical_checks={}, background_warnings={}, spectrum_warnings={})
    k = np.concatenate(([0.0], np.geomspace(0.01, 80, 1601)))
    cosmology = provenance["cosmology"]
    for mass in [1, 2, 5]:
        actual = Subhalos(mass).power_ratio(k)
        expected = published_fits(mass, k, cosmology["h"], cosmology["omega_dm"])["Viel2005_q10"]
        error = float(np.max(np.abs(actual - expected)))
        if error >= 5e-15:
            raise RuntimeError("Independent Viel fit does not reproduce current product")
        result["checks"].append(dict(mass_keV=mass, max_absolute_product_vs_independent_Viel_Q=error))
    for path in sorted(args.raw.glob("*/physical_checks.json")):
        result["physical_checks"][path.parent.name] = json.loads(path.read_text())
    if set(result["physical_checks"]) != {"wdm_m1", "wdm_m2", "wdm_m5", "wdm_m2_fine"}:
        raise RuntimeError("Expected physical checks for all four WDM runs")
    for path in sorted(args.raw.glob("*/run.log")):
        warnings = [line for line in path.read_text().splitlines() if "warning" in line.lower()]
        destination = "background_warnings" if path.parent.name.startswith("background_") else "spectrum_warnings"
        if warnings:
            result[destination][path.parent.name] = warnings
    if result["spectrum_warnings"]:
        raise RuntimeError("Review spectrum run warnings before accepting these checks")
    if any(abs(row["relative_density_error"]) >= 1e-8 for row in result["physical_checks"].values()):
        raise RuntimeError("WDM density does not match the CDM reference")
    result["all_checks_passed"] = True
    text = json.dumps(result, indent=2) + "\n"
    if args.output.exists() and args.output.read_text() != text:
        raise RuntimeError("Refusing to overwrite different quality-check results")
    args.output.write_text(text)
    print("Product, density and warning checks passed")


if __name__ == "__main__":
    main()
