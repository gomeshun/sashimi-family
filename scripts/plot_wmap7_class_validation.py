#!/usr/bin/env python3
"""Export a standalone scientific figure from reviewed CLASS comparison data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = args.directory
    report = json.loads((directory / "comparison.json").read_text())
    spectra = directory / "spectra.npz"
    if hashlib.sha256(spectra.read_bytes()).hexdigest() != report["spectra_sha256"]:
        raise RuntimeError("Spectra do not match the reviewed comparison")
    data = np.load(spectra)
    k = data["k_h_per_Mpc"]
    selected = k >= 1
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": "#202020", "text.color": "#202020"})
    colors = {"Viel2005_q10": "#236192", "Vogel2023_q10": "#B56826"}
    names = {"Viel2005_q10": "Viel (2005), squared", "Vogel2023_q10": "Vogel (2023), squared"}
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.5), sharex=True,
                             gridspec_kw={"height_ratios": [1.5, 1]})
    handles = {}
    for column, mass in enumerate([1, 2, 5]):
        top, bottom = axes[:, column]
        reference = data[f"m{mass}_z0_CLASS_Q"]
        pick = np.where(selected)[0][::18]
        handles["CLASS"], = top.plot(k[pick], reference[pick], "o", ms=3,
                                      color="#202020", label="CLASS")
        for name in ["Viel2005_q10", "Vogel2023_q10"]:
            values = data[f"m{mass}_z0_{name}"]
            style = "-" if name == "Viel2005_q10" else "--"
            # Deliberately display the 1-keV extrapolation in light grey, with
            # an explicit panel annotation; it does not enter adoption claims.
            color = "#969696" if mass == 1 and name == "Vogel2023_q10" else colors[name]
            line, = top.plot(k[selected], values[selected], color=color, ls=style, lw=1.8)
            if mass == 2:
                handles[name] = line
            bottom.plot(k[selected], (values - reference)[selected], color=color, ls=style, lw=1.8)
        if mass == 2:
            fine = data["m2_z0_CLASS_Q_fine"]
            handles["refinement"], = bottom.plot(k[selected], (fine - reference)[selected],
                color="#202020", ls=":", lw=1.5, label="CLASS refinement change (2 keV)")
        title = "1 keV (Vogel extrapolated)" if mass == 1 else f"{mass} keV"
        top.set_title(title, pad=9)
        top.axhline(0.5, color="#d4d4d4", lw=0.7, zorder=0)
        top.set_ylim(-0.02, 1.04)
        bottom.axhline(0, color="#777777", lw=0.8, zorder=0)
        bottom.set_ylim(-0.085, 0.035)
        bottom.set_xlabel(r"$k\ [h\,\mathrm{Mpc}^{-1}]$")
        for ax in [top, bottom]:
            ax.set_xscale("log")
            ax.set_xlim(1, 80)
            ax.set_xticks([1, 10, 80], ["1", "10", "80"])
            ax.grid(axis="y", color="#ededed", lw=0.6)
            if column:
                ax.tick_params(labelleft=False)
    axes[0, 0].set_ylabel(r"$Q=P_{\rm WDM}/P_{\rm CDM}$")
    axes[1, 0].set_ylabel(r"$Q_{\rm fit}-Q_{\rm CLASS}$")
    fig.suptitle("Thermal-WDM transfer fits at SASHIMI-W's WMAP7 cosmology",
                 x=0.075, y=0.985, ha="left", fontsize=14)
    fig.text(0.075, 0.925,
             r"$z=0$; $h=0.7$, $\Omega_m=0.27$, $\Omega_b=0.0469$; matched primordial amplitude and DM density",
             fontsize=9)
    order = ["CLASS", "Viel2005_q10", "Vogel2023_q10", "refinement"]
    labels = ["CLASS", names[order[1]], names[order[2]], "CLASS refinement change (2 keV)"]
    fig.legend([handles[name] for name in order], labels, loc="upper left",
               bbox_to_anchor=(0.068, 0.90), ncol=2, frameon=False, fontsize=9)
    fig.text(0.075, 0.025,
             "Pure two-state thermal relic; massless active neutrinos. Coefficients are fixed to the literature; no refitting.",
             fontsize=8.5)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.77, bottom=0.12, hspace=0.17, wspace=0.15)
    fig.savefig(directory / "comparison.png", dpi=180)
    fig.savefig(directory / "comparison.pdf")
    plt.close(fig)
    metadata = dict(
        matplotlib_version=matplotlib.__version__,
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_comparison_sha256=hashlib.sha256((directory / "comparison.json").read_bytes()).hexdigest(),
        output_sha256={name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                       for name in ["comparison.png", "comparison.pdf"]},
    )
    (directory / "render-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
