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

## Family integration

The family integration workflow installs ITAMAE and all four SASHIMI variants
in one clean environment. It verifies that every legacy module and opt-in
façade imports simultaneously and that the former generic migration-helper
module names are absent.

For a local equivalent:

```bash
uv venv .venv-family
uv pip install --python .venv-family/bin/python \
  ./itamae ./sashimi-c ./sashimi-si ./sashimi-w ./sashimi-f
```

Run each submodule's own test suite as well; the family smoke test detects
cross-package conflicts and does not replace variant-specific physics
regressions.
