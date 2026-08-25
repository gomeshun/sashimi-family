# ITAMAE migration implementation plan

This document is the execution plan for migrating the SASHIMI family to use
[ITAMAE](https://github.com/gomeshun/itamae) as the shared computational
infrastructure while preserving each SASHIMI variant's scientific ownership,
legacy reproducibility, and public behavior.

It is written primarily for coding agents and maintainers who will implement the
remaining migration. Treat the requirements, ordering, compatibility rules,
and acceptance criteria below as part of the implementation contract. Do not
make opportunistic scientific changes while performing a software-extraction
step unless the relevant section explicitly calls for a new `consistent`
physics mode and corresponding validation.

---

## 1. Goal and definition of success

The migration succeeds when the following dependency structure is real in the
code rather than only conceptual:

```text
                         +------------------+
                         |      ITAMAE      |
                         | shared numerical |
                         | infrastructure   |
                         +---------+--------+
                                   |
             +---------------------+---------------------+
             |                     |                     |
      +------v------+       +------v------+       +------v------+
      |  SASHIMI-C  |       | SASHIMI-SI  |       | SASHIMI-W/F |
      | CDM physics |       | SIDM physics |       | WDM/FDM     |
      +-------------+       +-------------+       +-------------+
```

ITAMAE must own reusable computational mechanisms and data contracts. The
SASHIMI repositories must continue to own their scientific prescriptions and
default model compositions.

The migration is complete only when all of the following are true:

1. common numerical and structural code is no longer copied independently
   between SASHIMI-C, SASHIMI-SI, SASHIMI-W, and SASHIMI-F;
2. each SASHIMI variant remains independently installable and explicitly owns
   its physical model choices;
3. historical public APIs remain available for published-result reproduction;
4. migrated APIs return the shared ITAMAE weighted-catalog representation;
5. legacy and intentionally corrected physics are never mixed silently;
6. golden regression tests protect historical numerical behavior;
7. family-level tests verify that all packages can be co-installed without
   overwriting each other's runtime files;
8. CI tests the exact ITAMAE/SASHIMI commit set that is declared as compatible;
9. ITAMAE can eventually be released and consumed as a normal versioned package
   rather than as a collection of copied helpers;
10. the `*_itamae_migration.py` modules become thin variant adapters rather than
    a second long-lived layer of duplicated SASHIMI implementation.

A useful litmus test is:

> A new SASHIMI variant should be able to reuse ITAMAE's catalog construction,
> numerical solvers, variance interfaces, backend conventions, and execution
> machinery while providing its own physical prescriptions as explicit model
> components.

---

## 2. Non-goals and boundaries

Do **not** use this migration to move model-specific physics into ITAMAE.

ITAMAE should not silently choose or own:

- the canonical SASHIMI-C accretion/concentration/tidal prescriptions;
- SIDM cross sections, gravothermal evolution, profile response, or disruption
  calibration;
- WDM transfer-function convention, filtering calibration, or WDM
  concentration prescription;
- FDM transfer functions, cutoff/filter calibration, or soliton/core-halo
  physics;
- dSph Jeans likelihoods, observational priors, or downstream inference code;
- project-specific plotting, publication, or analysis notebooks.

ITAMAE may define protocols and reusable numerical machinery consumed by these
physical components, but it must not select them implicitly.

Do not redesign all public APIs at once. The migration is incremental and must
preserve reproducibility first. API cleanup may follow only after regression
coverage and family integration are stable.

---

## 3. Current implementation state

As of the migration state reviewed in July/August 2026, the repositories have
already progressed substantially beyond the initial adapter-only stage.

### 3.1 ITAMAE

The ITAMAE foundation is implemented and installable. The current migration
branch contains, among other pieces:

- native and Astropy unit backends;
- native flat-LCDM and Colossus cosmology backends;
- immutable backend configuration and protocol interfaces;
- typed host/accretion/subhalo/orbital/catalog objects;
- NFW primitives and robust inversion;
- numerical grids and Gauss-Hermite quadrature;
- generic ODE and perturbative evolution machinery with Shanks acceleration;
- `WeightedSubhaloCatalog` with factorized weights and provenance metadata;
- serialization, concatenation, weighted reductions, and Poisson realization;
- tabulated power spectra and window-function protocols;
- integrated top-hat and sharp-k variance support;
- exact moving-boundary derivative for ideal sharp-k filtering;
- variance cache helpers;
- radial-measure and initial orbit infrastructure;
- CI on supported Python versions and optional backend combinations.

The ITAMAE public API is still provisional. Do not freeze or release it until
family golden regressions and adapter boundaries are stable.

### 3.2 SASHIMI-C

The C migration branch already contains:

- opt-in `sashimi_c_itamae` facade;
- legacy tuple compatibility;
- ITAMAE structured-catalog conversion;
- `legacy` and `consistent` physics modes;
- ITAMAE variance adapter;
- migration diagnostics and demonstration notebook;
- golden regression fixture(s);
- migration-specific CI and packaging.

The established `sashimi_c` import remains the historical API and must remain
unchanged until migration equivalence is proven and an explicit compatibility
policy is adopted.

### 3.3 SASHIMI-SI

The SI migration branch already contains:

- opt-in `sashimi_si_itamae` facade;
- preservation of the historical 27-array public return contract;
- named structured catalog views for the CDM reference and SIDM states;
- factorized ITAMAE weights and provenance metadata;
- migrated shared background/NFW/variance/solver mechanisms;
- regression tests and an executable comparison notebook.

SIDM cross sections, gravothermal evolution, SIDM profile response, and
survival/disruption physics remain in SASHIMI-SI and must stay there.

### 3.4 SASHIMI-W

The W migration branch already contains:

- opt-in `sashimi_w_itamae` facade;
- legacy tuple reproduction;
- ITAMAE structured catalogs;
- explicit `legacy` and `consistent` physics modes;
- explicit WDM spectrum convention separate from physics mode;
- documented `published-q5` and `standard-t2-q10` choices;
- integrated ITAMAE sharp-k variance path;
- full-catalog golden fixtures;
- migration and variance regression tests;
- migration comparison notebook.

Several historical inconsistencies are deliberately preserved in `legacy` and
corrected only in `consistent`; see Section 8.3 below.

### 3.5 SASHIMI-F

The F migration branch already contains:

- opt-in `sashimi_f_itamae` facade;
- legacy tuple reproduction;
- ITAMAE structured catalog conversion;
- legacy/consistent derivative modes;
- accurate ITAMAE NFW inversion in consistent mode;
- FDM power-cache provenance;
- callable and integrated ITAMAE variance paths;
- golden fixtures and invariants;
- migration comparison notebook.

Current SASHIMI-F still assigns NFW profiles and does not yet implement a
soliton/core-halo relation. Do not pretend that profile migration is complete.

### 3.6 SASHIMI-family

The family repository currently exists as the integration and orchestration
repository. It includes the SASHIMI/ITAMAE repositories as submodules and has a
family co-install workflow that builds wheels and checks for runtime-file
collisions.

The family workflow currently uses explicitly pinned commits. The pins are a
reproducibility feature, but they must be synchronized with the intended
migration heads. A green family CI result is only meaningful if the workflow is
checking the exact revisions that are being declared compatible.

---

## 4. Global migration rules

Coding agents must follow these rules in every implementation PR.

### 4.1 Preserve legacy behavior before refactoring it

Before replacing a legacy mechanism:

1. identify the exact legacy public behavior;
2. add or verify a compact regression fixture/test;
3. document units, normalizations, array shapes, interpolation behavior, and
   known numerical quirks;
4. make the migrated implementation reproduce that behavior in `legacy` mode;
5. only then extract or replace the mechanism.

Never infer historical intent from a formula and silently "fix" the code while
performing an extraction.

### 4.2 Separate legacy reproduction from corrected physics

If a historical implementation is physically or numerically inconsistent and
changing it materially affects outputs:

- `legacy` must remain a faithful published-result reproduction path;
- `consistent` may implement the corrected convention;
- mode selection must be explicit;
- metadata must identify the mode;
- golden fixtures for the two modes must be separate when outputs differ;
- documentation must explain the difference;
- a corrected mode must not silently change the old public import path.

### 4.3 Mechanism versus prescription

Use the following ownership test:

- if the code answers **how to numerically perform a generic operation**, it is
  a candidate for ITAMAE;
- if the code answers **which physical relation/calibration/model is used**, it
  belongs to a SASHIMI variant.

Examples:

| Functionality | Owner |
|---|---|
| generic quadrature | ITAMAE |
| generic ODE/perturbative solver | ITAMAE |
| weighted catalog schema | ITAMAE |
| NFW primitive/inversion | ITAMAE |
| power-spectrum protocol | ITAMAE |
| variance integration/cache mechanism | ITAMAE |
| SASHIMI-C Yang-type accretion formula | SASHIMI-C |
| SASHIMI-C stripping coefficients | SASHIMI-C |
| SIDM cross section and gravothermal equations | SASHIMI-SI |
| WDM q5/q10 convention | SASHIMI-W |
| WDM concentration calibration | SASHIMI-W |
| FDM transfer function | SASHIMI-F |
| FDM soliton/core-halo prescription | SASHIMI-F |

### 4.4 No hidden global state

Do not introduce calculations whose result depends on mutable global cosmology,
unit, cache, random, or backend state.

- backend configuration must be explicit or immutable;
- Colossus adapters must restore or isolate global state;
- randomized APIs must receive an explicit `numpy.random.Generator` or seed;
- cache keys must include all physical/numerical/backend identifiers required to
  prevent cross-model reuse.

### 4.5 Canonical units at the ITAMAE boundary

The ITAMAE-facing representation uses documented canonical units. Variant
adapters are responsible for converting historical representations to and from
those units.

Do not mix historical floating-unit conventions and ITAMAE canonical values in
one array without an explicit conversion boundary. Metadata should identify
both the legacy and canonical units where a compatibility facade exposes both.

### 4.6 Weight semantics are explicit

Do not collapse all population logic into one anonymous `weight` field inside
ITAMAE.

Use factorized weights where applicable:

```text
weight_base
weight_host_history
weight_concentration
weight_orbit
weight_survival
weight_final = product of independent factors
```

Variant-specific additional factors are allowed if they use explicit
`weight_*` names and their semantics are documented.

### 4.7 Negative weights are not silently repaired

`WeightedSubhaloCatalog` represents nonnegative effective counts. If a legacy
numerical path produces negative weights because of interpolation/integration
noise:

- keep the signed values in the exact legacy tuple path if required for
  historical reproduction;
- do not clip, absolute-value, or silently renormalize them when creating an
  ITAMAE catalog;
- either choose a reviewed nonnegative regression grid or reject catalog
  construction with an informative error;
- correct the numerical mechanism only in an explicitly documented consistent
  path.

---

## 5. Branch, commit, and dependency policy

### 5.1 Migration branches

Until a repository's migration is regression-clean and accepted, continue to
use its dedicated `itamae-migration` branch. Avoid mixing unrelated feature
work into these branches.

### 5.2 Pinning ITAMAE

Before ITAMAE is released as a normal versioned dependency, each SASHIMI
migration branch should refer to one reviewed ITAMAE revision.

For CI, do **not** install the same `itamae` package simultaneously from two
different URLs (for example both a local checkout and a Git dependency). Pick
one source per job.

Recommended rule:

- repository-local regression CI: checkout the pinned ITAMAE commit and install
  that local checkout;
- lock files/package metadata: record the same tested revision where a VCS
  source is needed for ordinary developer installation;
- family CI: build the exact pinned ITAMAE revision and the exact compatible
  SASHIMI revisions.

### 5.3 SASHIMI-family as compatibility manifest

The family repository should become the authoritative record of a mutually
compatible set of revisions.

Add or maintain a machine-readable manifest in a future PR, for example:

```toml
[itamae]
repo = "gomeshun/itamae"
ref = "<sha>"

[sashimi-c]
repo = "gomeshun/sashimi-c"
ref = "<sha>"

[sashimi-si]
repo = "gomeshun/sashimi-si"
ref = "<sha>"

[sashimi-w]
repo = "gomeshun/sashimi-w"
ref = "<sha>"

[sashimi-f]
repo = "gomeshun/sashimi-f"
ref = "<sha>"
```

The exact filename may be `compatibility.toml` or similar. The family workflow
should read from this one source rather than duplicating hard-coded SHAs in
multiple places.

### 5.4 Submodule policy

When updating family compatibility:

1. update submodule revisions;
2. update the compatibility manifest;
3. ensure the family workflow reads the same revisions;
4. run the full family integration suite;
5. commit these changes together.

Do not allow `.gitmodules`, gitlink revisions, a compatibility manifest, and CI
pins to describe different states.

---

## 6. PR roadmap overview

Implement the remaining migration in the following order. Do not start a later
physics-extraction milestone while the earlier stabilization milestones are
red.

```text
PR 0A  Fix SASHIMI-C CI
PR 0B  Fix SASHIMI-F CI
PR 0C  Synchronize family compatibility pins
PR 0D  Add single-source compatibility manifest + CI consumption

PR 1A  Freeze regression/metadata contracts across variants
PR 1B  Consolidate test helpers and golden provenance conventions

PR 2A  Extract generic C execution pipeline into ITAMAE protocols/mechanisms
PR 2B  Thin SASHIMI-C migration adapter
PR 2C  Reuse the C/common pipeline from SASHIMI-SI

PR 3A  Stabilize generic power/variance interfaces for W/F
PR 3B  Thin SASHIMI-W adapter
PR 3C  Thin SASHIMI-F adapter

PR 4A  Common profile/state-view abstractions
PR 4B  SIDM structured state integration
PR 4C  FDM soliton/core-halo integration when the scientific model is selected

PR 5A  Spatial Level A/B integration
PR 5B  Optional orbit-averaged research backend integration

PR 6A  ITAMAE public-API freeze and prerelease preparation
PR 6B  Versioned dependency migration and family release validation
```

Each PR below includes an implementation contract.

---

## 7. Milestone 0: make the current migration trustworthy

This milestone is blocking. Do not perform new model migration until all jobs in
this milestone are green.

### PR 0A — Fix current SASHIMI-C migration CI

**Repository:** `gomeshun/sashimi-c`

**Branch:** `itamae-migration`

**Known current problem:** the migration workflow reaches the Ruff step and
fails on formatting/import-order issues before running the regression suite.
The observed issues are mechanical and autofixable, including:

- unsorted `__all__` in `sashimi_c_itamae.py`;
- import ordering in `sashimi_c_itamae_migration.py`;
- `Mapping` imported from `typing` rather than `collections.abc` for the active
  Ruff rule set;
- import ordering in `sashimi_c_itamae_variance.py`;
- import ordering in `tests/test_itamae_migration.py`.

**Required changes:**

1. run the repository's Ruff configuration locally against the same files as CI;
2. apply only mechanical lint/import fixes unless a test reveals another issue;
3. ensure the workflow continues after lint and actually executes all migration
   regression tests on every configured Python version;
4. confirm packaging and family co-install jobs remain green;
5. do not change scientific outputs in this PR.

**Acceptance criteria:**

- `ruff check` passes without suppressing the relevant rules;
- migration regression tests run rather than being skipped;
- all configured Python matrix jobs pass;
- wheel/source build and clean import smoke tests pass;
- golden outputs are unchanged.

### PR 0B — Fix current SASHIMI-F migration CI

**Repository:** `gomeshun/sashimi-f`

**Branch:** `itamae-migration`

**Known current problem:** CI installs ITAMAE both as a checked-out local source
and as the VCS URL declared by the project, causing uv to reject conflicting
URLs for the same package.

**Required changes:**

1. choose one ITAMAE source for the regression job;
2. recommended: checkout the pinned ITAMAE commit and install the local checkout
   together with SASHIMI-F in a way that does not make project resolution request
   the second VCS URL;
3. if necessary, split the workflow into:
   - a local-pinned regression environment;
   - a separate packaging/install job that validates the package's declared
     dependency source;
4. do not loosen dependency resolution with an unsafe workaround;
5. rerun lint, regression tests, build, wheel install, smoke tests, and family
   co-install.

**Acceptance criteria:**

- uv resolves exactly one ITAMAE source in each job;
- migration regression tests run and pass;
- FDM golden and invariant tests pass;
- cache tests and Colossus-state isolation tests pass;
- wheel and source distribution build successfully;
- family co-install remains green.

### PR 0C — Synchronize SASHIMI-family compatibility revisions

**Repository:** `gomeshun/sashimi-family`

**Required changes:**

1. update the pinned revisions used by family integration to the intended
   migration heads after PR 0A/0B are green;
2. include SASHIMI-F in the same compatibility policy even if visibility or
   repository permissions require a separate/private CI path;
3. update submodule gitlinks to the same revisions;
4. verify that the family test builds the exact current migration code, not an
   older commit;
5. keep the runtime-file overlap assertion.

**Important:** SASHIMI-W has had code-level changes after an older family pin,
including separation of exact legacy behavior from corrected WDM physics. A
family test using the older pin does not validate the current W migration.

**Acceptance criteria:**

- every family pin equals the declared compatible migration revision;
- every submodule gitlink equals the declared compatible revision;
- all wheels build from those exact revisions;
- all legacy and opt-in modules import from one clean environment;
- no two distributions install the same runtime file;
- family CI is green.

### PR 0D — Single-source compatibility manifest

**Repository:** `gomeshun/sashimi-family`

**Goal:** eliminate SHA drift between documentation, workflow YAML, and
submodule revisions.

**Required changes:**

1. add `compatibility.toml` (or an equivalently simple machine-readable file);
2. record repository names and full commit SHAs for ITAMAE and each SASHIMI
   variant;
3. modify the family workflow so checkout revisions are read from this manifest
   rather than duplicated as literals;
4. add a validation script/test that checks the manifest against the checked-in
   submodule gitlinks;
5. fail CI on mismatch;
6. document the update procedure in the family README or this file.

**Acceptance criteria:** one edit location controls the tested compatibility
set, and CI rejects any mismatch.

---

## 8. Milestone 1: freeze compatibility and scientific provenance contracts

The migration cannot safely extract more code until every variant agrees on
what is being preserved and how provenance is encoded.

### PR 1A — Standardize migration mode and metadata contracts

**Repositories:** ITAMAE + C/SI/W/F as required.

Define a common metadata vocabulary. At minimum, migrated catalogs should
record enough information to answer:

- which SASHIMI variant/model produced this catalog?
- which physics mode was used?
- which ITAMAE version/commit was used?
- which SASHIMI version/commit was used?
- which cosmology backend and parameters were used?
- which unit schema was used?
- which variance/power implementation and convention were used?
- which mass/concentration/host-history/solver conventions were used?
- which disruption/survival threshold was used?
- which catalog schema version applies?

Recommended common keys include:

```text
model_identifier
physics_mode
backend_identifier
itamae_version
itamae_source_revision
sashimi_version
sashimi_source_revision
canonical_unit_schema
variance_identifier
power_identifier
solver_identifier
catalog_schema_version
```

Variant-specific keys remain allowed and should be namespaced or clearly
named.

Do not overfit the core ITAMAE metadata class to every variant field. Stable
common identifiers belong in ITAMAE; detailed physical provenance may live in
`extra` metadata.

### PR 1B — Golden fixture provenance and testing policy

Create one documented golden-fixture convention shared by C/SI/W/F.

Each fixture must record or be accompanied by:

- generating repository commit;
- ITAMAE commit if applicable;
- physics mode;
- all non-default parameters required to regenerate it;
- cosmology and unit convention;
- fixture purpose;
- comparison tolerances and why they are appropriate;
- whether it is a strict legacy-reproduction fixture or a reviewed consistent
  result.

Prefer compact fixtures that cover the full pipeline over very large default
resolution outputs. Expensive high-resolution convergence tests should live in
scheduled CI rather than every PR.

**Minimum test categories per variant:**

1. public legacy tuple regression;
2. migrated legacy tuple parity;
3. migrated structured-catalog mapping;
4. full small-catalog golden comparison;
5. scalar/array behavior where applicable;
6. unit conversion invariants;
7. weight factorization invariants;
8. finite/nonnegative structured weights;
9. serialization round trip;
10. package import from outside the source checkout.

---

## 9. Milestone 2: complete the common C/SI execution pipeline

This is the main software-extraction milestone. SASHIMI-C is the reference
migration because much of the family execution structure originates there.

### 9.1 Target architecture

The following conceptual pipeline should be represented by explicit interfaces
and reusable ITAMAE mechanisms:

```text
host configuration
    -> host history
    -> accretion mass/redshift measure
    -> EPS/accretion rate
    -> concentration quadrature
    -> initial structure assignment
    -> post-accretion evolution
    -> survival/disruption evaluation
    -> weighted catalog
    -> observables / legacy tuple adapter
```

The pipeline controller and data transport may be shared. The individual
physical prescriptions remain in the variant.

### 9.2 Interfaces to stabilize

Use structural typing (`Protocol`) where practical. The exact names can evolve,
but the responsibilities should map to interfaces equivalent to:

```python
class HostHistoryModel(Protocol):
    def m200(self, host_reference, z, cosmology): ...
    def dmvir_dz(self, host_reference, z, cosmology): ...

class VarianceModel(Protocol):
    def sigma(self, mass, z=0.0): ...
    def variance(self, mass, z=0.0): ...
    def dvariance_dmass(self, mass, z=0.0): ...

class AccretionRateModel(Protocol):
    def differential_number(self, m_acc, z_acc, host, variance): ...

class ConcentrationModel(Protocol):
    def median(self, m200, z, cosmology): ...

class InitialStructureModel(Protocol):
    def assign(self, m200, z, concentration_nodes, context): ...

class MassLossLaw(Protocol):
    def rhs(self, state, host_state, orbital_state=None): ...

class ProfileEvolutionModel(Protocol):
    def evolve(self, initial_profile, mass_history, context): ...

class SurvivalModel(Protocol):
    def evaluate(self, state, context): ...
```

Do not move SASHIMI-C formulae into default implementations merely to make the
interfaces convenient.

### PR 2A — ITAMAE execution primitives

**Repository:** `gomeshun/itamae`

Implement only generic pieces that are required to make the C migration adapter
thin.

Potential tasks, after comparing current code against the adapter:

- generalized construction of accretion batches with independent weights;
- reusable expansion/broadcast/flatten helpers for mass/redshift/concentration
  nodes;
- generic application of a concentration quadrature to a population measure;
- generic execution of a model-supplied mass-loss RHS with existing ODE or
  perturbative solvers;
- explicit solver diagnostics/provenance;
- reusable catalog assembly from an evolved state;
- chunked execution if required by current C memory behavior;
- protocol definitions for host history, accretion rate, concentration, mass
  loss, profile evolution, and survival.

**Do not implement:** C-specific EPS coefficients, concentration relation,
stripping coefficients, disruption threshold, or observable formulae.

Every new ITAMAE mechanism must have unit tests independent of SASHIMI-C and at
least one integration test using a minimal toy physical model.

### PR 2B — Thin the SASHIMI-C adapter

**Repository:** `gomeshun/sashimi-c`

Refactor `sashimi_c_itamae_migration.py` so it primarily:

1. wraps/expresses SASHIMI-C physical prescriptions as components satisfying the
   ITAMAE interfaces;
2. converts historical units/conventions at the boundary;
3. assembles the physical model composition;
4. maps the ITAMAE catalog back to the historical tuple for compatibility;
5. records C-specific provenance.

A useful code-quality target is that generic loops, broadcasting, solver
orchestration, catalog assembly, and generic weight manipulation disappear from
this module when equivalent ITAMAE mechanisms exist.

Do **not** use line count as the only criterion, but the current large migration
module should substantially shrink.

#### C-specific physics requirements

- `physics_mode="legacy"` must preserve the historical rounded constants and
  critical-density normalization required for exact regression;
- `physics_mode="consistent"` must use one self-consistent constant convention;
- do not allow arbitrary cosmology merely by swapping the background backend
  while host-history/concentration/EPS coefficients remain calibrated for the
  canonical C cosmology;
- reject unsupported mixed cosmologies explicitly until the complete dependent
  physical components are parameterized.

### PR 2C — Reuse the common pipeline from SASHIMI-SI

**Repository:** `gomeshun/sashimi-si`

After C is thin, migrate SI onto the same ITAMAE execution machinery.

SI-specific requirements:

- retain SIDM cross sections and their interpolation/asymptotic treatment in SI;
- retain gravothermal/profile evolution in SI;
- support two named state views (`cdm_reference` and `sidm`) sharing the same
  initial population nodes/weights where physically appropriate;
- retain explicit `weight_survival` for each state when survival differs;
- do not use `physics_mode="legacy"` to resurrect known-bad pre-fix equations;
  it should continue to mean the current corrected historical public model
  unless a separate archival mode is intentionally introduced;
- remove avoidable RuntimeWarnings by computing stable branches lazily rather
  than evaluating invalid discarded expressions first;
- tests must assert final catalogs are finite and physical.

**Acceptance criteria for Milestone 2:** C and SI adapters use shared ITAMAE
execution machinery and no longer carry independent copies of generic
population/evolution/catalog loops.

---

## 10. Milestone 3: stabilize WDM/FDM power and variance integration

W and F share the need for non-CDM spectra and filter-aware variance, but their
physical transfer functions and calibrations remain variant-owned.

### PR 3A — Finalize generic ITAMAE power/variance contracts

**Repository:** `gomeshun/itamae`

Required generic responsibilities:

- power-spectrum callable/protocol with stable identifier;
- tabulated spectrum with documented interpolation/extrapolation rules;
- composable transfer functions supplied by the variant;
- top-hat and sharp-k window mechanisms;
- integrated variance;
- exact moving-boundary derivative for ideal sharp-k;
- explicit finite integration domain behavior;
- content-addressed cache keys including power identity, filter, mass grid,
  cosmology/backend, and numerical resolution;
- cache mismatch/corruption rejection;
- derivative tests against analytic or high-accuracy independent references.

Do not put the WDM q5/q10 choice or FDM transfer formula inside a hidden ITAMAE
default.

### PR 3B — Thin the SASHIMI-W adapter

**Repository:** `gomeshun/sashimi-w`

Preserve the following explicit independent choices:

```text
physics_mode = legacy | consistent
wdm_power_convention = published-q5 | standard-t2-q10
```

Do not couple these settings implicitly.

#### Legacy inconsistencies that must remain reproducible

The migration currently identifies at least these historical issues:

1. `OmegaL` omitted the baryon contribution when constructing the historical
   background, producing a non-flat sum;
2. the resulting growth approximation is not normalized to `D(0)=1`;
3. `dS/dM` historically scales with one power of `D` although
   `S(M,z)=D(z)^2 S(M,0)` requires two;
4. physical masses were passed directly into a table whose numerical coordinate
   was `Msun/h`;
5. concentration-boundary mass conversion used the inverse `h` convention;
6. the accretion loop reused the final-redshift virial-mass grid in `Na_calc`
   for all accretion redshifts.

`legacy` must preserve these when reproducing the historical implementation.
`consistent` applies the reviewed corrections together and records the mode.

#### q5/q10 rule

- `published-q5` reproduces the historical SASHIMI-W power-ratio use;
- `standard-t2-q10` uses the standard transfer-amplitude-squared
  interpretation;
- neither becomes the public default solely because it is mathematically more
  conventional;
- changing q must alter metadata and golden identity;
- scientific default changes require the validation milestone below.

#### W acceptance tests

- legacy tuple parity;
- legacy q5 golden catalog;
- consistent q5 golden catalog;
- consistent q10 golden catalog;
- no implicit mixed q5/q10 variance/concentration usage;
- exact unit-coordinate conversions at the spectrum boundary;
- nonnegative ITAMAE catalog weights;
- expected rejection or explicit handling of legacy negative-weight grids;
- half-mode metadata semantics tested.

### PR 3C — Thin the SASHIMI-F adapter

**Repository:** `gomeshun/sashimi-f`

Keep FDM-specific ownership in F:

- transfer-function formula;
- filter/cutoff defaults;
- FDM-specific normalization/calibration;
- eventual soliton/core-halo relation;
- scientific choice of native versus experimental Colossus variance.

Generic integration/cache mechanics should use ITAMAE.

#### F physics-mode requirements

- legacy derivative path preserves historical `D(z)` scaling where required;
- consistent path uses `D(z)^2` for `dS/dM` when
  `S(M,z)=D(z)^2 S(M,0)`;
- legacy host-history derivative behavior remains reproducible;
- consistent host-history derivative should differentiate the selected growth
  factor consistently;
- legacy NFW inversion remains available if needed to protect binary survival
  decisions near `ct_th`;
- consistent mode uses accurate ITAMAE inversion.

#### Colossus rule

The Colossus variance path is experimental where derivative-sign differences
remain below the FDM cutoff. Do not advertise it as interchangeable with the
native path until independent validation resolves this difference. Require an
explicit opt-in flag and provenance identifier.

---

## 11. Scientific validation milestone

Software equivalence and physical-model validation are separate tasks. Do not
promote a corrected mode to a scientific default merely because its code is
cleaner.

### 11.1 SASHIMI-C

Validate that consistent constants/conventions do not introduce unintended
changes beyond the documented normalization difference. Compare at minimum:

- full small catalog;
- subhalo mass function;
- cumulative abundance;
- representative profile quantities;
- annihilation-related outputs where prompt-cusp paths interact with migrated
  shared mechanisms.

### 11.2 SASHIMI-SI

Validate:

- CDM reference catalog against C where the model definitions coincide;
- SIDM effective cross-section interpolation against direct calculations;
- gravothermal limiting behavior;
- collapsed/non-collapsed state boundaries;
- finite results around asymptotic branches;
- survival and weight normalization.

### 11.3 SASHIMI-W

Before changing any recommended/default WDM convention, compare q5 and q10
against independent scientific targets, preferably including:

- the published SASHIMI-W results;
- WDM simulation subhalo mass functions or satellite populations for a matched
  cosmology/model;
- half-mode/cutoff behavior;
- final satellite-likelihood consequences if this code will be used for
  constraints.

Record the source simulation/model, exact transfer convention, cosmology, and
mass definitions. Do not infer equivalence from a shared half-mode mass alone.

### 11.4 SASHIMI-F

Validate:

- transfer-function implementation against its source formula;
- sharp-k derivative around oscillatory FDM nodes;
- native versus integrated ITAMAE variance;
- native versus Colossus differences;
- resulting accretion abundance;
- downstream FDM prior/likelihood outputs used in real analysis.

The integrated sharp-k path may intentionally differ from a sparsely tabulated
legacy derivative near transfer-function nodes. Such differences require
scientific interpretation, not forced numerical matching.

---

## 12. Milestone 4: profile and multi-state abstractions

Do this only after the population/evolution migration is stable.

### PR 4A — Generic profile/state contracts in ITAMAE

ITAMAE should support generic named physical state/profile data without owning
SIDM or FDM prescriptions.

Needed capabilities may include:

- extensible profile parameter containers;
- named state views (for example `cdm_reference`, `sidm`, `fdm`);
- state-specific survival/validity flags;
- shared initial node identity;
- model-specific extra columns with schema/provenance;
- generic enclosed-mass/velocity interfaces where useful.

Avoid a class hierarchy that assumes every model is a modified NFW profile.
Use protocols/composition so future profile families remain possible.

### PR 4B — SIDM state integration

Refactor SI to use the generic named-state representation while keeping all SIDM
formulas local. Verify CDM and SIDM views remain aligned on shared accretion
nodes and base weights.

### PR 4C — FDM soliton/core-halo integration

This is a **scientific feature**, not merely a software refactor. Implement only
when the intended FDM profile prescription is explicitly selected and cited.

Required work before implementation:

1. document the chosen soliton/core-halo relation and literature source;
2. define the matching/transition convention to the outer halo;
3. define how tidal evolution modifies or preserves the core;
4. define the catalog columns and units;
5. add independent analytic/limiting tests;
6. add regression fixtures for representative FDM masses;
7. validate against downstream dSph uses.

Do not silently retrofit a soliton into historical SASHIMI-F legacy mode.

---

## 13. Milestone 5: spatial information

Spatial migration is intentionally downstream of the non-spatial core.

### 13.1 Level A — conditional radial measure

Represent spatial information as a normalized conditional measure, not as an
unexplained `radius` column.

Required invariants:

```text
integral dq P(q | x) = 1
sum child spatial weights = parent population weight
integral dV n(r) = total surviving weight
```

Metadata must identify:

- spatial representation;
- epoch;
- radius convention;
- host profile/backend;
- spatial weight semantics.

### 13.2 Level B — local environment

Provide generic host-environment queries such as:

```text
rho_host(r, z)
M_host(<r, z)
Phi(r, z)
Vcirc(r, z)
tdyn_local(r, z)
```

Variant-specific radius-dependent stripping/disruption laws remain outside
ITAMAE.

### 13.3 Level C — orbit-averaged research backend

Only after Levels A/B are validated, integrate the existing orbit scaffold for
turning points, radial periods, radial kernels, and optional `(E,L)`/action-like
transport.

Conservation/normalization tests are mandatory. Do not make this backend part of
the first stable ITAMAE API unless it is already required by production
SASHIMI analyses.

---

## 14. Testing requirements for every migration PR

Every PR must state which of the following categories apply and include tests as
needed.

### 14.1 Unit tests

Cover individual functions, validation, edge cases, scalar/array behavior, and
failure modes.

### 14.2 Integration tests

Cover interactions among backends, physical components, solvers, catalogs, and
package installation.

### 14.3 Golden regression tests

Protect legacy and reviewed consistent outputs. Golden data must be compact and
provenanced.

### 14.4 Invariant/property tests

Examples:

- finite nonnegative structured weights;
- normalized quadrature;
- `m_bound <= m_acc` for monotonic stripping models;
- NFW/profile inversion consistency;
- scalar/array equivalence;
- serial/chunked equivalence;
- native/Astropy-unit equivalence;
- backend state restoration;
- deterministic seeded realizations;
- finite values or explicit flags instead of silent NaNs.

### 14.5 Convergence tests

For numerical integrations/solvers, compare grid and quadrature refinements.
Expensive tests may run on scheduled CI but must exist before a numerical method
is declared stable.

### 14.6 Failure-mode tests

Test invalid units, negative masses/radii, invalid modes, unsupported custom
cosmologies, cache mismatch/corruption, missing optional dependencies, invalid
backend state, and out-of-domain interpolation behavior.

### 14.7 Packaging tests

Every migrated repository must test:

1. build wheel and sdist;
2. install built wheel in a clean environment;
3. import legacy API outside the source tree;
4. import opt-in ITAMAE API outside the source tree;
5. run at least one minimal numerical smoke calculation.

---

## 15. CI requirements

### 15.1 ITAMAE

Required checks before merge should include at least:

```text
ruff check
ruff format --check
mypy
pytest + coverage
minimal dependency tests
Astropy backend tests
Colossus backend tests
supported Python matrix
build wheel/sdist
clean-wheel smoke test
```

### 15.2 Each SASHIMI migration repository

Required checks should include:

- migration lint;
- golden regression suite;
- supported Python version(s);
- pinned ITAMAE compatibility check;
- wheel/sdist build;
- clean import/smoke test;
- no accidental import-time selection of the migrated path for legacy users.

### 15.3 SASHIMI-family

Family CI must test the exact compatibility manifest revisions and verify:

- all distributions build;
- all distributions co-install in one clean environment;
- legacy and opt-in imports coexist;
- no runtime file overlap;
- catalog schema version expectations are compatible;
- the manifest and submodule gitlinks match;
- the tested ITAMAE version is the declared one.

When feasible, add a compact cross-variant smoke test that constructs one small
catalog per variant and checks required metadata and finite weights.

---

## 16. Documentation requirements

Do not treat documentation as cleanup after migration.

Every new public mechanism/interface must document:

- responsibility and ownership boundary;
- parameters and return values;
- array shapes and broadcasting;
- canonical units;
- physical/comoving convention;
- factors of `h`;
- mass definition;
- valid parameter/redshift range;
- interpolation/extrapolation behavior;
- numerical algorithm and convergence assumptions;
- references for nontrivial physical formulas.

Use comments to explain why numerical workarounds, Jacobians, asymptotic
branches, root brackets, cache components, and legacy conversions are required.
Do not add comments that merely restate the code.

Migration documentation must always distinguish:

```text
historical public behavior
migrated legacy reproduction
migrated consistent/reviewed behavior
experimental alternatives
```

---

## 17. Performance work comes after equivalence

Do not optimize a migrated mechanism before golden equivalence and invariants
are established, unless the legacy implementation is too slow to make the
regression practical.

After equivalence is stable, prioritize:

1. avoiding repeated spectrum/variance integration;
2. vectorizing mass/redshift/concentration evaluation;
3. chunking large catalogs;
4. content-addressed caching;
5. avoiding repeated NFW inversions;
6. reducing unnecessary copies during legacy tuple conversion;
7. optional parallel execution with deterministic ordering;
8. only later, evaluating JAX/differentiable backends.

Any optimization must retain an unambiguous numerical regression against the
pre-optimization migrated implementation.

---

## 18. API deprecation strategy

Do not remove historical import paths during the migration branch phase.

Recommended release strategy:

1. first ITAMAE-compatible SASHIMI releases keep the old import/API stable;
2. expose structured catalogs through explicit opt-in modules or explicit new
   methods;
3. collect usage/validation experience;
4. only after a versioned compatibility period consider making structured
   catalogs the primary API;
5. if old tuple APIs are eventually deprecated, provide a documented mapping
   from each tuple position to named catalog fields and a multi-release warning
   period.

Never silently reorder a legacy tuple.

---

## 19. ITAMAE prerelease checklist

Do not publish the first public ITAMAE prerelease until all of the following are
complete:

- C/SI/W/F compatibility revisions are recorded and family CI is green;
- all required golden regressions pass;
- current migration adapters use shared ITAMAE mechanisms rather than copied
  generic loops;
- canonical unit schema is documented and versioned;
- catalog schema is documented and versioned;
- backend/cosmology state behavior is deterministic;
- package license is selected and included;
- `CITATION.cff` is added;
- `CHANGELOG.md` is added;
- public API is reviewed and intentionally exported;
- documentation builds without unresolved warnings for the supported API;
- wheel and sdist install cleanly;
- TestPyPI publication is validated;
- `uv add itamae` (and optional extras) is tested in clean environments;
- release workflow uses trusted publishing where possible;
- release artifacts are exactly the artifacts that passed CI.

Prefer an alpha/prerelease version until several real SASHIMI workflows have
used the packaged dependency.

---

## 20. Coding-agent workflow for each task

When an automated coding agent takes one item from this plan, it should follow
this procedure.

### Step 1 — Read before modifying

Inspect:

- this `migration_plan.md`;
- ITAMAE `PLAN.md` and relevant API modules;
- the target variant's legacy implementation;
- its `*_itamae*.py` adapter modules;
- existing regression/golden tests;
- current CI workflow;
- recent migration commits and open PR description.

Do not implement from this plan alone without checking the current branch; the
repository may have advanced since this document was written.

### Step 2 — State the ownership boundary

Before editing, identify in the PR description:

- generic mechanism being moved or reused;
- physical prescription that remains in the variant;
- legacy behavior that must remain unchanged;
- any intentionally changed consistent-mode behavior.

### Step 3 — Add/verify a failing protection test

For refactors, verify the existing golden would fail if behavior changed. For a
bug fix, add a regression test that fails before the fix. For a new mechanism,
add an independent unit/integration test.

### Step 4 — Make the smallest coherent change

Do not simultaneously:

- extract a mechanism;
- alter a physical formula;
- change units;
- rename the public API;
- and optimize the implementation.

Split these into separate PRs unless they are mathematically inseparable and the
combined change is explicitly documented.

### Step 5 — Run local-equivalent CI commands

Use the same `uv`, Ruff, mypy, pytest, and build commands as CI. Do not rely on a
CI-only environment to make the code work.

### Step 6 — Update provenance/docs

If behavior, mode identity, cache identity, schema, or a scientific convention
changes, update metadata identifiers and documentation in the same PR.

### Step 7 — Update family compatibility only after repository CI is green

Do not point `sashimi-family` to a red migration revision.

---

## 21. PR template for migration work

Agents should use a PR body with at least the following information:

```markdown
## Migration scope

Generic mechanism moved/reused:
- ...

Variant-owned physics left unchanged:
- ...

## Compatibility

Legacy public API affected: yes/no
Legacy numerical result affected: yes/no
Consistent-mode result affected: yes/no
Catalog schema affected: yes/no
Cache/provenance identity affected: yes/no

## Validation

- [ ] legacy tuple regression
- [ ] migrated legacy parity
- [ ] structured catalog regression
- [ ] invariant/property tests
- [ ] lint/type checks
- [ ] wheel/sdist build
- [ ] clean install/import
- [ ] family co-install, if compatibility pin is updated

## Scientific notes

Any intentional physical/numerical difference:
- ...

Relevant references/conventions:
- ...
```

---

## 22. Immediate next actions

The next coding agent should **not** start a new physics migration. Execute these
in order:

1. fix SASHIMI-C migration CI so the regression suite actually runs;
2. fix SASHIMI-F uv dependency-source conflict so the regression suite runs;
3. rerun and confirm ITAMAE, C, SI, W, and F migration CI at the intended heads;
4. update `sashimi-family` submodule revisions and family CI pins to exactly
   those green heads;
5. add a single-source compatibility manifest and a mismatch check;
6. freeze common metadata/golden provenance conventions;
7. only then begin thinning SASHIMI-C's migration layer into reusable ITAMAE
   execution mechanisms.

After each step, update this document if the implementation reveals a different
boundary or invalidates an assumption. The plan is a living execution contract,
but changes to it should be explicit and reviewable rather than silently
ignored.
