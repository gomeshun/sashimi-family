#!/usr/bin/env python3
"""Run independent thermal-WDM CLASS controls at SASHIMI-W's stored cosmology.

Requires an existing CLASS executable and NumPy; this never imports SASHIMI
physics or supplies a fitted transfer function to CLASS. Inputs and completed
outputs are immutable. Repeating an identical run verifies hashes and reuses it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_once(path, value):
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise RuntimeError(f"Refusing changed metadata: {path}")
    else:
        path.write_text(text)


def sigma8(folder):
    match = re.search(r"sigma8=([\d.eE+-]+) for total matter", (folder / "run.log").read_text())
    if match is None:
        raise RuntimeError(f"No CLASS total-matter sigma8: {folder}")
    return float(match.group(1))


def omega_ncdm(folder):
    files = list(folder.glob("spectrum_*background.dat"))
    if len(files) != 1:
        raise RuntimeError(f"Expected one background file in {folder}")
    header = next(line for line in files[0].read_text().splitlines() if "1:z" in line)
    match = re.search(r"(\d+):\(\.\)rho_ncdm\[0\]", header)
    if match is None:
        raise RuntimeError("Missing WDM background density column")
    rho = np.loadtxt(files[0])[-1, int(match.group(1)) - 1]
    # CLASS stores 8 pi G rho / (3 c^2) in Mpc^-2. This converts to Omega h^2.
    return float(rho / (100 / 299792.458) ** 2)


class Runner:
    def __init__(self, args):
        self.args = args
        self.output = args.output.resolve()
        self.output.mkdir(parents=True, exist_ok=True)
        self.executable = args.class_executable.resolve()
        self.root = Path(__file__).resolve().parents[1]
        source = self.root / "sashimi-w/WMAP7_camb_matterpower_z0_extrapolated.dat"
        ob, om, h, ns, s8 = map(float, np.loadtxt(source, max_rows=5))
        self.cosmology = dict(Omega_b=ob, Omega_m=om, h=h, n_s=ns,
                              sigma8_cdm_target=s8, omega_b=ob * h**2,
                              omega_dm=(om - ob) * h**2)
        self.common = dict(
            h=h, omega_b=ob * h**2, n_s=ns, A_s=2.1e-9,
            # These are explicit control assumptions, absent from the five-line
            # SASHIMI spectrum header, and held at the previous CLASS baseline.
            tau_reio=0.0544, T_cmb=2.7255, N_ur=3.046, Omega_k=0,
            output="mPk", z_pk="0, 99", **{"P_k_max_h/Mpc": 80},
            ncdm_fluid_approximation=3, k_per_decade_for_pk=30,
            tol_ncdm_bg=1e-7, tol_ncdm_synchronous=1e-4,
            l_max_ncdm=24, tol_perturbations_integration=1e-6,
            write_background="yes", write_parameters="yes", write_warnings="yes",
            background_verbose=2, perturbations_verbose=1, fourier_verbose=1,
        )
        self.identity = dict(
            schema="sashimi-w:wmap7-class-validation:v1",
            cosmology=self.cosmology,
            spectrum_header_source=str(source), spectrum_sha256=digest(source),
            class_executable=str(self.executable), class_executable_sha256=digest(self.executable),
            class_source=json.loads(args.class_source_manifest.read_text()),
            family_revision=self.git_revision(self.root),
            w_revision=self.git_revision(self.root / "sashimi-w"),
            runner_sha256=digest(__file__), python=sys.version,
            numpy=importlib.metadata.version("numpy"),
            assumptions={"active_neutrinos": "massless, N_ur=3.046",
                         "WDM": "pure thermal Fermi-Dirac, two internal states, zero chemical potential",
                         "normalization": "CDM sigma8 target once; identical A_s for all WDM masses and precisions",
                         "stored_CAMB_table": "background header matched; original radiation/reionization settings unavailable"},
        )
        save_once(self.output / "provenance.json", self.identity)

    @staticmethod
    def git_revision(path):
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()

    def run(self, name, changes, *, fine=False):
        folder = self.output / name
        folder.mkdir(exist_ok=True)
        config = dict(self.common)
        if fine:
            config.update(k_per_decade_for_pk=60, tol_ncdm_synchronous=1e-5,
                          l_max_ncdm=40, tol_perturbations_integration=2e-7)
        config.update(changes)
        config["root"] = str(folder / "spectrum_")
        text = "\n".join(f"{k} = {v}" for k, v in config.items()) + "\n"
        ini = folder / "input.ini"
        if ini.exists() and ini.read_text() != text:
            raise RuntimeError(f"Refusing changed input: {ini}")
        if (folder / "complete.json").exists():
            saved = json.loads((folder / "complete.json").read_text())
            if saved["config"] != config:
                raise RuntimeError(f"Completed config mismatch: {folder}")
            for filename, expected in saved["sha256"].items():
                if digest(folder / filename) != expected:
                    raise RuntimeError(f"Changed output: {folder / filename}")
            print(name, "verified cached output", flush=True)
            return folder
        if any(folder.glob("spectrum_*")) or (folder / "run.log").exists():
            raise RuntimeError(f"Incomplete previous attempt retained; use a fresh output directory: {folder}")
        ini.write_text(text)
        print(name, "started", flush=True)
        start = time.monotonic()
        with (folder / "run.log").open("w") as log:
            status = subprocess.run(
                [str(self.executable), str(ini)], cwd=self.executable.parent,
                env=dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="1"),
                stdout=log, stderr=subprocess.STDOUT,
            )
        log = (folder / "run.log").read_text()
        if status.returncode or "Error" in log:
            raise RuntimeError(f"CLASS failure {folder}:\n{log[-5000:]}")
        complete = dict(config=config, elapsed_seconds=time.monotonic() - start,
                        class_executable_sha256=self.identity["class_executable_sha256"],
                        sha256={p.name: digest(p) for p in sorted(folder.iterdir()) if p.is_file()})
        save_once(folder / "complete.json", complete)
        print(name, "complete", round(complete["elapsed_seconds"], 2), "s", flush=True)
        return folder

    def execute(self):
        dm = self.cosmology["omega_dm"]
        normalization = self.output / "normalization.json"
        if normalization.exists():
            norm = json.loads(normalization.read_text())
        else:
            pilot = self.run("cdm_amplitude_pilot", dict(omega_cdm=dm, N_ncdm=0))
            initial = sigma8(pilot)
            target = self.cosmology["sigma8_cdm_target"]
            norm = dict(initial_A_s=self.common["A_s"], sigma8_pilot_log=initial,
                        sigma8_target=target, A_s=self.common["A_s"] * (target / initial)**2,
                        method="Linear-power amplitude scaling from CDM only; CLASS log has six significant digits")
            save_once(normalization, norm)
        self.common["A_s"] = norm["A_s"]
        fine = self.args.precision == "fine"
        suffix = "_fine" if fine else ""
        cold = self.run("cdm" + suffix, dict(omega_cdm=dm, N_ncdm=0), fine=fine)
        if abs(sigma8(cold) / self.cosmology["sigma8_cdm_target"] - 1) > 2e-5:
            raise RuntimeError("CDM normalization failed")
        for mass in self.args.masses:
            temperature_path = self.output / f"temperature_m{mass:g}.json"
            if temperature_path.exists():
                temperature = json.loads(temperature_path.read_text())
            else:
                # CLASS deg_ncdm=1 already includes particle and antiparticle:
                # background_ncdm_distribution() sums the two Fermi-Dirac terms.
                guess = 0.71611 * (93.14 * dm / (mass * 1000))**(1 / 3)
                base = self.run(f"background_m{mass:g}", dict(
                    output="", omega_cdm=0, N_ncdm=1, m_ncdm=mass * 1000,
                    T_ncdm=f"{guess:.16g}", deg_ncdm=1, ksi_ncdm=0))
                initial_dm = omega_ncdm(base)
                temp = guess * (dm / initial_dm)**(1 / 3)
                temperature = dict(mass_keV=mass, target_omega=dm, initial_temperature=guess,
                                   initial_omega=initial_dm, temperature=temp)
                save_once(temperature_path, temperature)
            warm = self.run(f"wdm_m{mass:g}" + suffix, dict(
                omega_cdm=0, N_ncdm=1, m_ncdm=mass * 1000,
                T_ncdm=f"{temperature['temperature']:.16g}", deg_ncdm=1, ksi_ncdm=0), fine=fine)
            achieved = omega_ncdm(warm)
            if abs(achieved / dm - 1) > 1e-8:
                raise RuntimeError(f"WDM density mismatch: {achieved} versus {dm}")
            save_once(warm / "physical_checks.json", dict(
                achieved_omega_wdm=achieved, relative_density_error=achieved / dm - 1,
                sigma8_total_log=sigma8(warm), matched_A_s=self.common["A_s"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class-executable", type=Path, required=True)
    parser.add_argument("--class-source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--masses", type=float, nargs="+", default=[2, 1, 5])
    parser.add_argument("--precision", choices=["baseline", "fine"], default="baseline")
    args = parser.parse_args()
    if any(not np.isfinite(m) or m <= 0 for m in args.masses):
        parser.error("masses must be positive and finite")
    Runner(args).execute()
