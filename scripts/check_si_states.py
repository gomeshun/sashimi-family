import sys, json, time, subprocess, hashlib, warnings, argparse, importlib.metadata
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for name in ["sashimi-c", "sashimi-si"]:
    sys.path.insert(0, str(ROOT / name))
from sashimi_si import SubhaloProperties, TidalStrippingSolver as SISolver
from sashimi_si_itamae_components import SIDMAccretionSlices
from sashimi_c import HaloModel as CHalo, TidalStrippingSolver as CSolver
from sashimi_c_itamae_components import (
    CDMAccretionSlices,
    NFWInitialStructure,
    TidalProfileEvolution,
)

parser = argparse.ArgumentParser(
    description="Compare SI states and matched C nodes from clean source candidates."
)
parser.add_argument("--output", type=Path, required=True)
OUT = parser.parse_args().output
if OUT.exists():
    raise FileExistsError(OUT)
OUT.mkdir(parents=True)


def relative(a, b):
    a, b = np.broadcast_arrays(a, b)
    return float(np.max(abs(a - b) / np.maximum(abs(b), 1e-300), initial=0))


base = dict(
    M0=1e12,
    redshift=0.0,
    dz=0.25,
    zmax=2.0,
    N_ma=16,
    logmamin=6.0,
    logmamax=10.0,
    N_herm=3,
    N_hermNa=8,
    ct_th=0.77,
    method="pert2_shanks",
)
rows = []
for sigma in [1e-8, 147.1, 1e4]:
    model = SubhaloProperties(sigma0_m=sigma)
    slices = []
    build = SIDMAccretionSlices.build

    def record(self, index):
        result = build(self, index)
        slices.append(result)
        return result

    SIDMAccretionSlices.build = record
    start = time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            catalogs = model.subhalo_catalogs_calc(**base)
    finally:
        SIDMAccretionSlices.build = build
    cdm, sidm = catalogs["cdm_reference"], catalogs["sidm"]
    sidm.to_npz(OUT / f"sigma-{sigma}.npz")
    formed = cdm.columns["valid_accretion"]
    alive = sidm.weight_final > 0
    row = dict(
        sigma0=sigma,
        seconds=time.perf_counter() - start,
        parameters=base,
        cdm_count=float(cdm.weight_final.sum()),
        sidm_count=float(sidm.weight_final.sum()),
        cdm_mass_fraction=float(cdm.weighted_sum(cdm.columns["m_bound"]) / base["M0"]),
        sidm_mass_fraction=float(
            sidm.weighted_sum(sidm.columns["m_bound"]) / base["M0"]
        ),
        formed=int(formed.sum()),
        nodes=len(formed),
        warnings=[str(w.message) for w in caught],
        weak_differences={
            k: relative(
                sidm.columns[k + "_sidm"][alive], sidm.columns[k + "_cdm"][alive]
            )
            for k in ["r_s", "rho_s", "r_max", "v_max"]
        },
        core_radius_fraction=float(
            np.max(
                abs(sidm.columns["r_c_sidm"][alive] / sidm.columns["r_s_sidm"][alive]),
                initial=0,
            )
        ),
        collapse_ratio_range=[
            float(cdm.columns["collapse_time_ratio"][formed].min()),
            float(cdm.columns["collapse_time_ratio"][formed].max()),
        ],
        negative_weight=bool(np.any(sidm.weight_final < 0)),
        base_weights_identical=all(
            np.array_equal(cdm.weights[k], sidm.weights[k])
            for k in ["weight_base", "weight_concentration"]
        ),
    )
    if sigma == 1e-8:
        comparisons = []
        for density_mode in [
            "native-C",
            "matched-SI-density",
            "matched-SI-density-and-NFW-mass",
        ]:
            c = CHalo()
            if density_mode != "native-C":
                c.rhocrit0 = model.rhocrit0
            solver = CSolver(M0=base["M0"], z_min=0, z_max=base["zmax"], n_z_interp=64)
            arrays = {
                name: [] for name in ["r_s_acc", "rho_s_acc", "m_bound", "r_s", "rho_s"]
            }
            for batch, context in slices:
                m200 = batch.m200_acc.reshape(base["N_herm"], -1)[0]
                stage = CDMAccretionSlices(
                    c,
                    m200,
                    np.array([context["za"]]),
                    np.ones((1, len(m200))),
                    0.128,
                    base["N_herm"],
                )
                cb, cc = stage.build(0)
                initial = NFWInitialStructure(c, base["N_herm"]).initialize(cb, cc)
                if density_mode == "matched-SI-density-and-NFW-mass":
                    # Match SI's M200 normalization at each concentration node.
                    # C's native normalization instead fixes median-converted Mvir.
                    r200 = (
                        3
                        * cb.m200_acc
                        / (4 * np.pi * c.rhocrit0 * c.g(context["za"]) * 200)
                    ) ** (1 / 3)
                    concentration = r200 / initial["r_s_acc"]
                    enclosed = np.log1p(concentration) - concentration / (
                        1 + concentration
                    )
                    initial["rho_s_acc"] = cb.m200_acc / (
                        4 * np.pi * initial["r_s_acc"] ** 3 * enclosed
                    )
                evolved = TidalProfileEvolution(
                    c, solver, 0.0, "pert2_shanks", base["N_herm"], True, {}
                ).evolve(cb, initial, cc)
                for k in arrays:
                    arrays[k].append(initial[k] if k in initial else evolved[k])
            differences = {
                k: relative(
                    np.concatenate(v),
                    cdm.columns[
                        {
                            "r_s_acc": "r_s_cdm_acc",
                            "rho_s_acc": "rho_s_cdm_acc",
                            "m_bound": "m_bound",
                            "r_s": "r_s_cdm",
                            "rho_s": "rho_s_cdm",
                        }[k]
                    ],
                )
                for k, v in arrays.items()
            }
            comparisons.append(
                dict(
                    density_mode=density_mode,
                    differences=differences,
                    C_G=c.G,
                    SI_G=model.G,
                    C_rhocrit0=c.rhocrit0,
                    SI_rhocrit0=model.rhocrit0,
                )
            )
        row["matched_nodes_C"] = comparisons
    rows.append(row)
    print(json.dumps(row), flush=True)
report = dict(
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    dependencies={
        n: importlib.metadata.version(n) for n in ["numpy", "scipy", "sashimi-itamae"]
    },
    rows=rows,
    source_revisions={
        n: subprocess.check_output(
            ["git", "-C", str(ROOT / n), "rev-parse", "HEAD"], text=True
        ).strip()
        for n in ["itamae", "sashimi-c", "sashimi-si"]
    },
    files={
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("*.npz")
    },
)
(OUT / "states-and-cdm.json").write_text(json.dumps(report, indent=2) + "\n")
