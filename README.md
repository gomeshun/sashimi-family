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

First validate proposed revisions with an explicit temporary effective manifest.
After the complete candidate set passes, commit the manifest and submodule
gitlinks together on the migration branch, then run the validator against that
committed HEAD without overrides. Main integration follows peer review.
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

[`sashimi-migration-goal.md`](sashimi-migration-goal.md) is the single execution
plan for migration and release preparation, tracked by
[epic #1](https://github.com/gomeshun/sashimi-family/issues/1). It combines the
implementation requirements and the agreed development goal:

- retain each variant's physical prescriptions and existing calculated quantities;
- use ITAMAE's shared execution, numerical mechanisms, catalogs and provenance;
- make the migrated named-catalog API primary and remove production legacy paths;
- preserve old-result reproduction in an independent, pinned validation workflow;
- validate candidate wheel/sdist artifacts for all five distributions and stop
  for peer review before publication.

Implementation stays on `itamae-migration` or topic branches. Main integration
and PyPI publication require a subsequent explicit user instruction. The
user-authorized publication of this consolidated plan to the parent main is a
documentation change, not permission to merge component implementations.

The [2026-09-04 review](docs/migration-status-2026-09-04.md) is historical evidence,
not current task status. The goal records a later dated checkpoint and requires
checking current code/CI before work; `compatibility.toml` remains the only
persistent compatible revision set.

The core distribution is named `sashimi-itamae`, while its Python import remains
`itamae`. Do not install the unrelated PyPI distribution named `itamae` as the
SASHIMI core. Local-wheel validation does not prove public-index resolution.

The [independent reference workflow](validation/references/README.md) freezes
old sources and keeps individual correction patches separate from product
execution. The [current work record](docs/migration-worklog-2026-09-10.md)
distinguishes completed review units from the remaining scientific and release
checks; neither document replaces the compatibility manifest. The
[current handoff](docs/HANDOFF_20260911.md) records the final candidate,
artifact locations, scientific limits and review procedure.

The migration candidates now expose named catalogs through the standard
`sashimi_c`, `sashimi_si`, `sashimi_w`, and `sashimi_f` imports. Production
`physics_mode` selection has been removed; legacy calculations survive only in
the frozen validation references. Following the
[2026-09-11 adoption decision](docs/adoption-2026-09-10.md), the current Viel
thermal-WDM model supports q10 only. `published-q5` raises an explicit error;
historical q5 results and caches are not relabeled as q10. The default half-mode
definition remains amplitude one-half (power one-quarter); power one-half is
available as an explicit threshold. Historical signed weights remain in the
independent reference and cannot be clipped or relabeled as nonnegative counts.

The user-approved FDM accretion correction now uses a virial-mass grid for
each accretion redshift, with specification v3 and independent reference and
convergence evidence. The validated five-component candidate is recorded in
`compatibility.toml` together with all five gitlinks. Final checks against this
recorded parent run without overrides in both public and private CI; their
results and the review status are recorded in the current handoff.

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

## Usage and scientific comparisons

Each variant separates the standard API walkthrough from the scientific
comparison of frozen A/B references and the product:

| Variant | Usage | Scientific comparison |
| --- | --- | --- |
| C | [Walkthrough](sashimi-c/notebooks/usage_walkthrough.ipynb) | [Comparison](sashimi-c/notebooks/scientific_validation.ipynb) |
| SI | [Walkthrough](sashimi-si/notebooks/usage_walkthrough.ipynb) | [Comparison](sashimi-si/notebooks/scientific_validation.ipynb) |
| W | [Walkthrough](sashimi-w/notebooks/usage_walkthrough.ipynb) | [Comparison](sashimi-w/notebooks/scientific_validation.ipynb) |
| F (private) | [Walkthrough](sashimi-f/notebooks/usage_walkthrough.ipynb) | [Comparison](sashimi-f/notebooks/scientific_validation.ipynb) |

The walkthrough CI executes a fresh kernel and checks the resulting notebook.
Scientific comparisons retain the generation provenance of each reference,
document individual corrections, and distinguish numerical agreement from
scientific validation. C/SI include resolution and solver checks; SI includes
state and weak-interaction limits; W records the q10 adoption with unchanged
fixed-control arrays. F's final convergence evidence depends on the pending
mass-grid decision. The root-level `itamae_migration_demo.ipynb` files are
retained entry points to these standard-API examples.

## Family integration

The public family integration workflow installs ITAMAE together with
SASHIMI-C, SASHIMI-SI, and SASHIMI-W in one clean environment. Because
SASHIMI-F is private, its own migration workflow repeats that check with all
five wheels; this avoids granting a cross-repository private access token to
the public family workflow. The release goal requires standard-API calculations,
named-catalog and observable checks, runtime-file non-collision, and exact
artifact provenance. Successful checks on earlier recorded revisions do not
certify the current migration candidates. Final public and private CI must use
the same recorded parent commit without candidate overrides.

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
