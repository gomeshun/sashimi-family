# Next-generation SASHIMI scientific roadmap

This document defines the post-migration scientific and competitive direction of the SASHIMI family.

The ITAMAE migration remains governed by [migration_plan.md](../migration_plan.md) and the migration epic [#1](https://github.com/gomeshun/sashimi-family/issues/1). That work is intentionally focused on reproducibility, architecture, packaging, scientific validation of migration differences, and a coherent release.

The roadmap here starts from that foundation. It is tracked by the scientific roadmap epic [#18](https://github.com/gomeshun/sashimi-family/issues/18).

## 1. Strategic position

SASHIMI should be developed as a **fast, theory-driven, inference-ready subhalo population backend**.

Its core task is:

> Given cosmology, host-halo properties, and dark-matter physics, rapidly predict a physically correlated distribution of subhalo properties, preserving deterministic weighted predictions for inference while also supporting stochastic realizations for downstream observables.

SASHIMI should not aim to reproduce every capability of a full semi-analytic galaxy-formation model or to require explicit high-resolution orbit integration for every subhalo.

The canonical computational picture is the weighted-measure architecture already adopted by ITAMAE:

```text
x = (m_acc, z_acc, concentration_node, host_history_node, orbit_node, ...)
y = T_model(x)
E[O] = sum_i w_i O(y_i)
```

The deterministic weighted population is the canonical representation. Monte-Carlo catalogs are generated as a separate operation when an observation-facing application requires individual realizations.

## 2. Competitive landscape

### Galacticus

Galacticus is the reference for broad, modular semi-analytic evolution, including explicit satellite/orbital evolution and extensive galaxy-formation physics.

SASHIMI should not compete on breadth. It should compete on:

- accuracy per computational cost;
- inference-loop throughput;
- extreme dynamic range in subhalo mass;
- direct comparison across dark-matter models;
- transparent deterministic population statistics.

### SatGen

SatGen is a closer reference for merger-tree plus orbit-resolved satellite evolution.

SASHIMI should use SatGen as a physical benchmark for orbital correlations and tidal evolution, but should avoid making explicit orbit integration the default execution strategy. Reduced or conditional orbital models should be preferred where they reproduce the required joint statistics at much lower computational cost.

### pyHalo

pyHalo is a reference for fast stochastic halo realizations and strong-lensing-oriented interoperability.

SASHIMI should not duplicate pyHalo's lensing-specific realization, line-of-sight, or lenstronomy-facing machinery. Instead, SASHIMI should provide a more theory-driven physical population backend and export sampled populations to pyHalo through an optional adapter.

## 3. Development hierarchy

The intended hierarchy is:

```text
ITAMAE migration / release foundation
    |
    +-- P0: competitive benchmark suite
    |
    +-- Level A: radial population models
    |
    +-- Level B: conditional phase-space population models
    |
    +-- Level B+: reduced/orbit-conditioned structural evolution
    |
    +-- correlated host-to-host realizations and scatter
    |
    +-- observation-facing interoperability (pyHalo first)
    |
    +-- optional baryonic host potentials
    |
    +-- Level C: explicit orbit integration as an optional high-fidelity backend
```

The explicit **Level B+** layer is important. The project should not jump directly from a radial PDF to full orbit integration.

## 4. Target population representation

The long-term population state should be able to expose, when supported by a model:

```text
m_acc
z_acc
concentration_acc
m_bound
profile / structural parameters
Vmax
rmax
truncation state
position
radial velocity
tangential velocity
pericenter / apocenter or equivalent reduced orbital descriptors
survival / disruption state
factorized weights
calibration and provenance metadata
```

Not every backend or SASHIMI variant must populate every field. Missing information must remain explicit rather than being silently synthesized.

The data model should continue to separate:

- generic state/protocol/execution machinery owned by ITAMAE;
- CDM/SIDM/WDM/FDM prescriptions and calibrations owned by the SASHIMI variants;
- observation-specific likelihoods and forward models owned by downstream projects.

## 5. Priority work

### P0 — Competitive benchmark

Tracked in [#19](https://github.com/gomeshun/sashimi-family/issues/19).

Compare SASHIMI with Galacticus, SatGen, pyHalo, and suitable simulation references in both scientific statistics and computational cost.

Core quantities should include, where available:

```text
dN/dm
N(>m)
p(z_acc)
n(r)
Sigma_sub(R)
p(m/m_acc | r)
p(Vmax, rmax | r)
survival fractions
```

Later phase-space benchmarks should include:

```text
p(v_r, v_t | r)
p(r_peri, r_apo)
p(f_bound | orbit descriptors)
```

The benchmark must define reproducible runtime and memory targets for inference-scale workloads.

### P1 — Conditional phase space

Tracked in [#20](https://github.com/gomeshun/sashimi-family/issues/20), building on ITAMAE SPATIAL-01.

The target is not merely an unconditional radial distribution,

```text
p(r | M_host),
```

but a correlated population model such as

```text
p(r, v_r, v_t | m_acc, z_acc, c_acc, M_host, z, ...)
```

or an equivalent reduced representation in orbital variables.

The model should retain correlations between current location, accretion history, stripping state, and internal structure when they are supported by calibration data.

### P1 — Reduced orbit-conditioned evolution

Tracked in [#21](https://github.com/gomeshun/sashimi-family/issues/21).

This Level B+ model should predict mass loss, survival, and structural response conditionally on compact orbital/environment descriptors without requiring fine-grained orbit integration for every weighted population element.

A schematic target is

```text
K_tide(
    f_bound,
    Vmax,
    rmax,
    truncation_state,
    survival,
    ...
  | m_acc, c_acc, z_acc, orbit_descriptors, host_state, ...
)
```

Candidate implementations may include orbit-averaged conditional laws, pericenter-event updates, response tables, or other calibrated reduced kernels.

### P2 — Correlated host-to-host scatter

Tracked in [#22](https://github.com/gomeshun/sashimi-family/issues/22).

SASHIMI should distinguish physically meaningful sources of population variance, including where possible:

```text
Poisson variance
host mass-accretion-history variance
concentration scatter
orbital/infall scatter
structural-evolution/disruption scatter
variant-specific model scatter
```

The deterministic weighted expectation must remain a first-class output. Stochastic realizations should be reproducible and preserve calibrated correlations rather than reducing all uncertainty to independent Poisson noise.

### P2 — Observation-facing interoperability

Tracked in [#23](https://github.com/gomeshun/sashimi-family/issues/23).

The first target is an optional SASHIMI-to-pyHalo adapter. The adapter should preserve units, cosmology, mass definitions, profile/truncation state, spatial normalization, dark-matter-model provenance, and RNG provenance.

This should establish a general pattern for later adapters without coupling core ITAMAE catalogs to strong-lensing-specific concepts.

### P3 — Baryonic host potentials

Tracked in [#24](https://github.com/gomeshun/sashimi-family/issues/24).

Baryons should enter as optional host/environment components, for example

```text
Phi_host = Phi_DM + Phi_disk + Phi_bulge + ...
```

with calibrated effects on phase space, stripping, and survival. SASHIMI should not become a self-consistent galaxy-formation SAM.

### P3 — Explicit orbit integration

Tracked by ITAMAE [ORBIT-01](https://github.com/gomeshun/itamae/issues/8).

Explicit Level C orbit integration should remain an optional high-fidelity backend unless benchmark evidence demonstrates that it is required for a target observable. Its purpose is to provide a reference and a higher-fidelity execution mode, not to erase SASHIMI's reduced-model speed advantage.

## 6. Scientific validation philosophy

Every new model should be validated in joint distributions, not only one-dimensional mass functions.

Examples include:

```text
p(m/m_acc, r)
p(Vmax, rmax, r)
p(z_acc, r)
p(v_r, v_t | r)
p(f_bound | orbit descriptors)
```

A radial model that reproduces `n(r)` but destroys the correlation between accretion time, mass loss, and position is not sufficient for the next-generation target.

Likewise, a faster model should only replace a higher-fidelity model when the relevant observable-level accuracy is quantified.

## 7. Design constraints

- Keep deterministic weighted catalogs first-class.
- Keep stochastic realization a separate explicit operation.
- Preserve explicit model/backend/calibration provenance.
- Keep variant-specific physics outside ITAMAE.
- Keep observation-specific likelihoods outside ITAMAE.
- Do not add detailed galaxy formation merely for feature parity with Galacticus.
- Do not make full orbit integration mandatory merely for feature parity with SatGen.
- Prefer interoperability over duplicating pyHalo's strong-lensing ecosystem.
- Make all claims of speed and accuracy reproducible through BENCH-01.

## 8. Long-term success criterion

The desired position is approximately:

> SASHIMI rapidly predicts physically correlated dark-matter substructure populations across dark-matter models, from cosmological accretion to internal structure and phase space, with deterministic weighted predictions for inference and stochastic realizations for downstream observables.

The competitive value of this position must be demonstrated by benchmark evidence rather than by feature count alone.
