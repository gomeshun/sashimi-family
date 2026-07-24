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
module and opt-in façade imports simultaneously and that the former generic
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
