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

The existing migration implementation still has legacy/opt-in APIs and separate
physics modes. These are the starting point, not the target release contract.
WDM's `published-q5` and `standard-t2-q10` remain explicit physical choices,
independent of the numerical corrections; removing legacy mode must not silently
change that choice. Historical signed weights belong to the independent
reference and cannot be clipped or silently relabeled as nonnegative counts.

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

Each variant contains an `itamae_migration_demo.ipynb`:

| Variant | Comparison shown |
| --- | --- |
| [SASHIMI-C](sashimi-c/itamae_migration_demo.ipynb) | true old, migrated legacy, and consistent CDM catalogs |
| [SASHIMI-SI](sashimi-si/itamae_migration_demo.ipynb) | corrected public SI model and both migration labels |
| [SASHIMI-W](sashimi-w/itamae_migration_demo.ipynb) | published legacy q5, consistent q5, and explicit q10 |
| [SASHIMI-F](sashimi-f/itamae_migration_demo.ipynb) | true old, migrated legacy, and corrected FDM mode |

At the reviewed revisions, C has execution counts for all eight non-empty code
cells. SI, W, and F each contain one unexecuted non-empty code cell, with no
saved error outputs. These saved states do not prove a fresh clean-kernel run.
Full execution and a notebook-state CI gate remain tracked in
[GOV-05 #6](https://github.com/gomeshun/sashimi-family/issues/6). F's separate
structure-prior comparison notebook does not complete this migration-demo gate.

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
