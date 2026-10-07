#!/usr/bin/env python3
"""Compare immutable CLASS controls with published thermal-WDM transfer fits.

No fit coefficients are estimated from these outputs. k is in h/Mpc and P in
(Mpc/h)^3 throughout. The saved spectra and sampled curves accompany the report.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import brentq


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def published_fits(mass, k, h, omega_dm):
    """Return power ratios Q=T^2, with explicit matching cosmology.

    Viel et al., Phys. Rev. D 71, 063534 (2005), Eqs. (4), (6), (7),
    https://arxiv.org/abs/astro-ph/0501562: alpha uses Omega_WDM, not omega_WDM.

    Vogel & Abazajian, Phys. Rev. D 108, 043520 (2023), Eqs. (7)-(9),
    Table II, https://arxiv.org/abs/2210.10753 (v2): spin-1/2 thermal relic.
    alpha uses omega_WDM=Omega_WDM*h^2. The published coefficient set must be
    used together, including nu=1.049. Their mass calibration starts at 2 keV;
    evaluating 1 keV below is an explicitly labeled extrapolation diagnostic.
    Both alpha values are in h^-1 Mpc, paired with k in h/Mpc.
    """
    old_alpha = 0.049 * mass**-1.11 * (omega_dm / h**2 / 0.25)**0.11 * (h / 0.7)**1.22
    new_alpha = 0.0437 * mass**-1.188 * (omega_dm / 0.12)**0.2463 * (h / 0.6736)**2.012

    def q(alpha, nu, power_exponent=10):
        # The literature fits a transfer amplitude; its square is a power ratio.
        return np.exp(-power_exponent / nu * np.log1p((alpha * np.asarray(k))**(2 * nu)))

    return {
        "Viel2005_q10": q(old_alpha, 1.12),
        "Vogel2023_q10": q(new_alpha, 1.049),
        "historical_q5": q(old_alpha, 1.12, 5),
    }


def fit_crossing(mass, h, omega_dm, name, power=0.5):
    return float(brentq(lambda k: float(published_fits(mass, k, h, omega_dm)[name]) - power,
                       1e-6, 1e6, xtol=1e-11))


class Analysis:
    def __init__(self, raw):
        self.raw = raw
        self.provenance = json.loads((raw / "provenance.json").read_text())
        self.cosmology = self.provenance["cosmology"]
        self.spectra = {}
        self.run_metadata = {}

    def read(self, name, z):
        key = (name, z)
        if key in self.spectra:
            return self.spectra[key]
        folder = self.raw / name
        complete = json.loads((folder / "complete.json").read_text())
        for filename, expected in complete["sha256"].items():
            if digest(folder / filename) != expected:
                raise RuntimeError(f"Changed CLASS output: {folder / filename}")
        self.run_metadata[name] = complete
        candidates = list(folder.glob(f"spectrum_*_z{1 if z == 0 else 2}_pk.dat"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected exactly one total matter spectrum: {name}, z={z}")
        k, p = np.loadtxt(candidates[0]).T
        if np.any(np.diff(k) <= 0) or np.any(~np.isfinite(p)) or np.any(p <= 0):
            raise RuntimeError(f"Invalid spectrum: {candidates[0]}")
        self.spectra[key] = k, p
        return k, p

    def ratio(self, mass, z, suffix="", interpolator=CubicSpline):
        kw, pw = self.read(f"wdm_m{mass:g}" + suffix, z)
        kc, pc = self.read("cdm" + suffix, z)
        low, high = max(kw[0], kc[0]), min(kw[-1], kc[-1])
        if low > 0.01 or high < 80:
            raise RuntimeError("Spectra do not cover the frozen comparison domain")
        warm = interpolator(np.log(kw), np.log(pw), extrapolate=False)
        cold = interpolator(np.log(kc), np.log(pc), extrapolate=False)
        return lambda k: np.exp(warm(np.log(k)) - cold(np.log(k)))

    def run(self):
        h, dm = self.cosmology["h"], self.cosmology["omega_dm"]
        k = np.geomspace(0.01, 80, 1601)
        summaries, arrays = [], {"k_h_per_Mpc": k}
        for mass in [1, 2, 5]:
            for z in [0, 99]:
                calc = self.ratio(mass, z)
                truth = calc(k)
                if np.any(~np.isfinite(truth)):
                    raise RuntimeError("Nonfinite interpolated power ratio")
                half = float(brentq(lambda x: float(calc(x)) - 0.5, 0.01, 80, xtol=1e-11))
                transition = (truth >= 0.05) & (truth <= 0.95)
                fits = published_fits(mass, k, h, dm)
                metrics = {}
                for name, values in fits.items():
                    metrics[name] = dict(
                        power_ratio_at_CLASS_half=float(published_fits(mass, half, h, dm)[name]),
                        max_absolute_Q_error=float(np.max(np.abs(values[transition] - truth[transition]))),
                        fit_k_power_half_h_per_Mpc=fit_crossing(mass, h, dm, name),
                        fractional_k_power_half_error=fit_crossing(mass, h, dm, name) / half - 1,
                    )
                    arrays[f"m{mass}_z{z}_{name}"] = values
                pchip = self.ratio(mass, z, interpolator=PchipInterpolator)(k)
                summaries.append(dict(
                    mass_keV=mass, redshift=z, CLASS_k_power_half_h_per_Mpc=half,
                    CLASS_Q_at_k_min=float(truth[0]), CLASS_Q_at_k_max=float(truth[-1]),
                    full_transition_005_to_095_covered=bool(truth[0] >= 0.95 and truth[-1] <= 0.05),
                    transition_k_range=[float(k[transition][0]), float(k[transition][-1])],
                    transition_sample_count=int(transition.sum()),
                    Vogel_mass_within_calibration=mass >= 2,
                    max_absolute_interpolator_difference=float(np.max(np.abs(pchip - truth))),
                    fits=metrics,
                ))
                arrays[f"m{mass}_z{z}_CLASS_Q"] = truth
        checks = []
        for z in [0, 99]:
            coarse, fine = self.ratio(2, z), self.ratio(2, z, "_fine")
            c, f = coarse(k), fine(k)
            region = (f >= 0.05) & (f <= 0.95)
            c_half = float(brentq(lambda x: float(coarse(x)) - 0.5, 0.01, 80))
            f_half = float(brentq(lambda x: float(fine(x)) - 0.5, 0.01, 80))
            delta_q = float(np.max(np.abs(f - c)))
            delta_half = f_half / c_half - 1
            checks.append(dict(
                mass_keV=2, redshift=z, max_absolute_Q_change=delta_q,
                max_relative_Q_change_transition=float(np.max(np.abs(f[region] / c[region] - 1))),
                k_power_half_baseline=c_half, k_power_half_fine=f_half,
                fractional_k_power_half_change=delta_half,
                passed_frozen_thresholds=bool(delta_q < 0.001 and abs(delta_half) < 0.001),
            ))
            arrays[f"m2_z{z}_CLASS_Q_fine"] = f
        for (name, z), (ks, ps) in self.spectra.items():
            arrays[f"raw_{name}_z{z}_k"] = ks
            arrays[f"raw_{name}_z{z}_P"] = ps
        common_amplitudes = {run["config"]["A_s"] for run in self.run_metadata.values()}
        if len(common_amplitudes) != 1:
            raise RuntimeError("CDM and WDM primordial amplitudes were not matched")
        return dict(
            schema="sashimi-w:wmap7-transfer-comparison:v1", source=self.provenance,
            analysis_sha256=digest(__file__), dependencies={
                name: importlib.metadata.version(name) for name in ["numpy", "scipy"]},
            normalization=json.loads((self.raw / "normalization.json").read_text()),
            summaries=summaries, precision_checks=checks, run_metadata=self.run_metadata,
            common_A_s=next(iter(common_amplitudes)),
            interpolation="CubicSpline(log P versus log k) for each spectrum, no extrapolation; PCHIP cross-check",
            units=dict(k="h/Mpc", P="(Mpc/h)^3", Q="dimensionless power ratio, not transfer amplitude"),
            references={"Viel2005": "https://arxiv.org/abs/astro-ph/0501562",
                        "Vogel2023": "https://doi.org/10.1103/PhysRevD.108.043520"},
        ), arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous-comparison", type=Path, required=True)
    args = parser.parse_args()
    result, arrays = Analysis(args.raw.resolve()).run()
    previous = json.loads(args.previous_comparison.read_text())
    result["previous_Planck_like"] = dict(
        source=str(args.previous_comparison.resolve()), sha256=digest(args.previous_comparison),
        cosmology=previous["cosmology"], summaries=previous["summaries"],
        precision_checks=previous["precision_checks"],
        note="Immutable previous run; different cosmology, no claim of original CAMB reproduction",
    )
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "comparison.json"
    spectra = args.output / "spectra.npz"
    if target.exists() or spectra.exists():
        raise RuntimeError("Use a fresh analysis directory; existing analyses are immutable")
    np.savez_compressed(spectra, **arrays)
    result["spectra_sha256"] = digest(spectra)
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ["summaries", "precision_checks"]}, indent=2))
    if not all(check["passed_frozen_thresholds"] for check in result["precision_checks"]):
        raise SystemExit("Numerical gate failed; results retained without endorsing adoption")


if __name__ == "__main__":
    main()
