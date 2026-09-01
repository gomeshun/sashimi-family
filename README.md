# sashimi-family

This repository pins and validates the repositories in the SASHIMI family:

| Submodule | Responsibility |
| --- | --- |
| `itamae` | Shared numerical mechanisms, backend protocols, and catalog schema |
| `sashimi-c` | Cold-dark-matter model |
| `sashimi-si` | Self-interacting-dark-matter model |
| `sashimi-w` | Warm-dark-matter model |
| `sashimi-f` | Fuzzy-dark-matter model |

Each entry is a Git submodule. Clone the complete family with:

```bash
git clone --recurse-submodules git@github.com:gomeshun/sashimi-family.git
```

For an existing checkout:

```bash
git submodule update --init --recursive
```

## Compatibility revisions

[`compatibility.toml`](compatibility.toml) is the authoritative record of the
ITAMAE and SASHIMI revisions tested together. The validation script compares
each recorded SHA with the corresponding committed submodule gitlink:

```bash
python3 scripts/check_compatibility.py
```

Update a family revision by moving the submodule, recording its full SHA in the
manifest, and running the validator before changing the integration workflow.
The public workflow reads its checkout repositories and revisions from this
manifest. SASHIMI-F's private family workflow uses the same revision set for
its five-wheel co-install check.

Each wheel and source distribution embeds its exact source revision in a small
runtime provenance module. Family CI checks that embedded value against the
manifest before installing the wheels; installed-package provenance therefore
does not depend on environment variables or an enclosing Git checkout.

To check locally built artifacts directly:

```bash
python3 scripts/check_artifact_provenance.py \
  --directory dist-family \
  --manifest compatibility.toml \
  --packages itamae sashimi-c sashimi-si sashimi-w sashimi-f
```

## ITAMAE migration

Migration work is developed on the `itamae-migration` branch of each
submodule. The family-level policy is:

- established SASHIMI public APIs retain their published behavior;
- ITAMAE-backed APIs are separate, explicit opt-ins;
- each variant continues to own its physical prescriptions and calibrations;
- shared numerical mechanisms and weighted-catalog contracts come from a
  reviewed, pinned public ITAMAE commit;
- CI installs that public commit directly rather than exchanging repository
  snapshots;
- installable helper modules use variant-specific names so all SASHIMI wheels
  can coexist in one Python environment.

The detailed migration plan is in [`migration_plan.md`](migration_plan.md), and
its source-of-truth tracking issue is [#1](https://github.com/gomeshun/sashimi-family/issues/1).
The migration roadmap is intentionally kept separate from new scientific feature
development so that reproducibility, packaging, and release work can converge.

SASHIMI-W additionally distinguishes two explicit power-spectrum conventions.
`published-q5` reproduces the 2022 code, while `standard-t2-q10` applies the
standard relation \(P_{\rm WDM}=T^2P_{\rm CDM}\). The choice is independent of
the migration's growth, unit, and mass-coordinate corrections; it must not be
changed implicitly by selecting another physics mode.

The q10 convention remains an explicit validation path rather than a new
default: it changes the EPS derivative and full-catalog abundance by orders of
magnitude even when the numerical half-mode scale is matched. Existing
q5-calibrated constraints therefore require a complete analysis rerun before
they can be compared with q10 results.

Within either power convention, SASHIMI-W's `legacy` mode remains a complete
reproduction path, including historical signed weights and reuse of the final
redshift's virial-mass grid. The `consistent` mode removes both behaviors with
the monotonic moving-boundary derivative and a per-redshift mass grid. Signed
legacy tuples remain available, but the nonnegative weighted-catalog contract
rejects them instead of clipping or silently renormalizing them.

## Scientific roadmap

The post-migration development strategy is documented in
[`docs/scientific-roadmap.md`](docs/scientific-roadmap.md) and tracked by
[#18](https://github.com/gomeshun/sashimi-family/issues/18).

The intended position of SASHIMI is a **fast, theory-driven, inference-ready
subhalo population backend**. Relative to Galacticus, SatGen, and pyHalo, the
project should emphasize accuracy per computational cost, deterministic weighted
population predictions, extreme dynamic range, dark-matter-model scans, and
clean interoperability with observation-facing tools.

The main scientific hierarchy is:

```text
competitive benchmarks
  -> radial spatial populations
  -> conditional phase-space populations
  -> reduced/orbit-conditioned tidal evolution
  -> correlated host-to-host realizations
  -> observation-facing adapters (pyHalo first)
  -> optional baryonic host potentials
  -> explicit orbit integration as an optional high-fidelity backend
```

In particular, the roadmap adds an explicit intermediate layer between simple
radial modeling and full orbit integration. SASHIMI should first test whether
compact orbital descriptors and calibrated response kernels can preserve the
joint position/stripping/structure correlations needed by observables while
retaining the speed advantage of the weighted-population approach.

The first roadmap issues are:

- [BENCH-01 #19](https://github.com/gomeshun/sashimi-family/issues/19): competitive scientific/performance benchmarks;
- [PHASESPACE-01 #20](https://github.com/gomeshun/sashimi-family/issues/20): conditional phase-space population models;
- [TIDE-01 #21](https://github.com/gomeshun/sashimi-family/issues/21): reduced orbit-conditioned tidal and structural evolution;
- [SCATTER-01 #22](https://github.com/gomeshun/sashimi-family/issues/22): correlated host-to-host variance and realizations;
- [INTEROP-01 #23](https://github.com/gomeshun/sashimi-family/issues/23): pyHalo interoperability;
- [BARYON-01 #24](https://github.com/gomeshun/sashimi-family/issues/24): optional baryonic host potentials.

## Visual migration demonstrations

Each variant contains an executed `itamae_migration_demo.ipynb`:

| Variant | Comparison shown |
| --- | --- |
| [SASHIMI-C](sashimi-c/itamae_migration_demo.ipynb) | true old, migrated legacy, and consistent CDM catalogs |
| [SASHIMI-SI](sashimi-si/itamae_migration_demo.ipynb) | corrected public SI model and both migration labels |
| [SASHIMI-W](sashimi-w/itamae_migration_demo.ipynb) | published legacy q5, consistent q5, and explicit q10 |
| [SASHIMI-F](sashimi-f/itamae_migration_demo.ipynb) | true old, migrated legacy, and corrected FDM mode |

They show the old tuple API beside the named weighted-catalog API, and compare
subhalo mass functions, accumulated satellite counts, and representative
catalog content. Before a migrated legacy curve is used as the old baseline,
the corresponding test suite compares it directly with the true old
implementation at catalog and derived-observable level.

## Family integration

The public family integration workflow installs ITAMAE together with
SASHIMI-C, SASHIMI-SI, and SASHIMI-W in one clean environment. Because
SASHIMI-F is private, its own migration workflow repeats that check with all
five wheels; this avoids granting a cross-repository private access token to
the public family workflow. Both workflows verify that every relevant legacy
module and opt-in facade imports simultaneously and that the former generic
migration-helper module names are absent.

For a local equivalent:

```bash
uv venv --python 3.11 .venv-family
uv build --wheel --out-dir dist-family ./itamae
uv build --wheel --out-dir dist-family ./sashimi-c
uv build --wheel --out-dir dist-family ./sashimi-si
uv build --wheel --out-dir dist-family ./sashimi-w
uv build --wheel --out-dir dist-family ./sashimi-f
uv pip install --python .venv-family/bin/python dist-family/*.whl
```

Run each submodule's own test suite as well; the family smoke test detects
cross-package conflicts and does not replace variant-specific physics
regressions.

Golden fixture provenance and regeneration rules are documented in
[docs/golden-fixture-policy.md](docs/golden-fixture-policy.md).
