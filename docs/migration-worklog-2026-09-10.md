# Migration and release preparation work record

This is execution evidence for [the agreed goal](../sashimi-migration-goal.md),
not a second compatibility manifest. `compatibility.toml` remains the sole
recorded compatible family. The dated JSON beside this file inventories the
starting sources and public methods; those are audit inputs, not validated
release candidates.

## Scope and starting state

- Parent base: `1112d1c` (the agreed goal); all submodule working trees were clean.
- The local submodule checkouts were older than both recorded pins and migration
  heads. Fetched all six remotes, then created `codex/migration-release-20260910`
  in the parent from main and in each child from its remote migration head.
- Main integration, package uploads, release triggers, visibility changes and
  release tags are outside this work. Existing main-targeted PR #33 stays unmerged.
- Read the current epic and child issues/PRs. Distribution identity and child-PR
  triggers are implemented. CORE/variant composition, scientific ablations,
  standard imports, independent references, packaging and release metadata remain.
- Existing `legacy` fixture generation records are historical evidence and will
  not be overwritten. Production mode removal is the newly agreed target.

## User decisions

| Topic | Decision | Implementation status |
| --- | --- | --- |
| ITAMAE/F license | User requested the same license as C/SI/W, which is MIT | Agreed for release preparation |
| CAMB table origin | User reports computing the table themselves | User-generated numerical data, proposed for MIT inclusion |
| Copyright/canonical F source | ITAMAE: Shunichi Horigome; F: Shin'ichiro Ando, Shunichi Horigome **and Elisa**; canonical `gomeshun/sashimi-f` | User added Elisa and will confirm with her before making the repository public; that is a publication gate, not permission to change visibility now |
| Candidate versions | C `2.0.0rc1`, ITAMAE/SI/W/F `0.2.0rc1` | User accepted these provisional candidate versions |
| Missing prompt-cusp spectrum | `data/powerspectrum31.txt` is absent locally, in the sibling C checkout, and in the upstream C tree | User explicitly deferred calculations requiring the missing table and requested a clear runtime error; do not substitute a different spectrum or claim this scientific validation passed |

Elisa's verified name is **Elisa Gouvea Mauricio Ferreira**, as listed in
[Kavli IPMU's official member directory](https://db.ipmu.jp/member/memberen.html).
The institute also uses [Elisa Ferreira](https://www.ipmu.jp/en/20260220-Award).
Use the full name in release metadata; the user's pre-publication confirmation
with her remains a separate publication gate.

## Baseline evidence

Python 3.11.15, ITAMAE's locked full-extra environment (NumPy 2.4.6, SciPy
1.17.1), plus the variants' numerical/notebook dependencies. All runs used the
explicit local ITAMAE source. Logs are initially under
`/tmp/sashimi-migration-20260910`; durable summaries accompany each review unit.

| Component | Before changes | Meaning |
| --- | ---: | --- |
| ITAMAE | 59 passed; branch coverage 78% | Existing core regression |
| C | 53 passed | Existing migration/Picard regression |
| SI | 14 passed | Existing corrected-SI regression |
| W | 38 passed | Existing q5/q10 migration regression |
| F | 40 passed | Existing FDM migration regression |

These successes are a baseline, not completion of independent scientific
validation, final artifact validation, or the Python matrix.

## CORE-01: fail before mixing incompatible batches

Problem: the executor copied only the first batch's metadata; non-binary numeric
survival values were silently converted to truth values; callback failures lacked
batch/stage context. Column insertion order was treated as a schema difference.

Protection tests before the fix: **18 failed, 3 passed**. The failures demonstrate
metadata mixing, truthy non-masks, missing failure context, column-order rejection,
late optional-factor validation and an unclear scalar-axis failure.

Change: compare all nested batch metadata exactly before invoking physical
components; validate optional-factor presence and the flat population axis;
require real finite stage values and boolean/0-or-1 masks; report the batch,
stage and callback while retaining the original exception. Allow mapping order
to vary with identical named schemas. Empty node batches retain their schema;
an empty batch iterable is an explicit error. C/SI's per-slice redshift index is
moved to their existing context objects, with constant model metadata on batches.

No physical equation, solver, quadrature, threshold, fixture or external package
version is changed by this review unit. Partition equivalence uses an independent
toy model and exact array equality, including factorized weights and seeded draws.

Validation: Ruff lint/format and mypy pass; ITAMAE **80 passed**, branch coverage
**79%**; C **53 passed**, SI **14 passed**, with unchanged historical goldens.
The C/SI context changes must accompany adoption of this stricter ITAMAE contract.

## CORE-02/03 and explicit C/SI stages

- ITAMAE PR #14 and matching C #12 / SI #6 were merged into migration after
  all declared CI checks passed. No main branch was changed.
- Cache integrity: ITAMAE PR #15, head `f28d72d`, merged into migration
  `970cda1`. Eight newly failing cases now pass; core 88 tests pass. Spectrum
  content and extrapolation affect identity, derivative resolution is recorded,
  and schema 2 cache payloads are verified. Numerical formulae are unchanged.
- NFW boundaries: ITAMAE PR #16, head `d439a46`, merged after all Python/backend,
  quality, walkthrough and artifact checks passed. Before: 13 failing/2 passing
  protection cases. After: all 15 and full core 103 pass, branch coverage 80%.
  C 54, SI 15, W 38 and F 40 unchanged regressions pass. The new evaluation
  uses a small-radius series and log-radius root bracket; profile parameters,
  radii and central-potential handling have explicit valid domains.
- C PR #13 (`b94817c`) and SI PR #7 (`e3199d0`) were merged into migration after
  all their declared checks passed. Accretion preparation, initialization,
  evolution, survival and columns are variant-owned components composed through
  ITAMAE. C mass loss now belongs to evolution. SI preserves independent CDM
  and SIDM masks and shared node identity. No physical formula or default changed.
- CI failures were investigated before merging: C's newer CI Ruff required
  sorted imports/exports; SI's old pinned ITAMAE did not expose PopulationComponents.
  C sorting was fixed and tested. SI's CI/walkthrough/development lock now use
  the exact tested `970cda1` input. Neither failure was bypassed.

## Independent scientific references: progress, not final validation

The source-export harness verifies immutable Git objects, input data, dependency
versions and patch hashes, then runs A/B in a separate process that rejects an
ITAMAE import. Its four boundary tests pass, including a changed worktree that
must not affect the reference. All four frozen A sources now execute. Full
parameters and artifacts live under `validation/references` (F in its private
repository). The F CAMB table is already tracked by the frozen A commit; the
initial missing-file observation came from the preliminary export, not from the
Git object. Its content hash agrees with the later user-computed table exactly;
no supplemental or substituted spectrum is required.

C's gravity and exact-inverse patches have been run singly and together. The
full 1,280-node B/C comparison has maximum c_t relative discrepancy 5.77e-14
and weight discrepancy 2.17e-15. Scientific thresholds, full observable coverage
and convergence remain separate required checks. A failed Lambert-W branch
selection in the first B trial was detected and rejected; the physical
principal branch at 50-digit precision is recorded in the accepted reference.

W's six specified corrections have been run singly and jointly on frozen A.
The old variance/slope representation still produces signed weights after the
unit corrections; those signs are preserved in the reference. A shared sharp-k
integration repair is in progress: fixed complete log-k cells plus the physical
partial endpoint eliminate the moving-grid plateau fluctuations without
projecting the variance. This has independent analytic and original-table-knot
adaptive-quadrature comparisons. Adoption into W and final B/C comparisons are
not complete yet.

## Standard API preparation and W numerical closure

ITAMAE PR #17 (ceb38eaf6ee57efb43ccb60005c68c1c4cf044ac) resolved the
remaining sharp-k interpolation-knot error. The fixed-cell-only intermediate
was insufficient for derivative consistency and remains documented separately.
The final q5/q10 integrals agree with independent adaptive knot-partitioned
integration to 1.12e-15; 513–8193 fixed-node refinement changes variance by at
most 2e-15. No variance projection is used. All 106 core tests and supported
Python/backend/build/walkthrough CI passed. One Python 3.13 dependency install
stalled; ordinary cancellation did not complete, force cancellation and a
same-input retry succeeded. The child was merged only after every check passed.

W PR #5 (91aabb0a8307d6a1807727f3fa8a57e4faff4238) removes the projected
100-node sigma interpolation and fixes the remaining redshift-resolved mass
integration coordinate. The full independent q5/q10 B/C catalogs agree at the
original 5e-10 catalog / 5e-12 weight tolerances, with identical survival masks.
39 tests pass; W's existing 3.11/3.13 matrix, package and walkthrough CI passed
before merging to migration. The full 3.11–3.13 release matrix remains a later
gate. Continuous variance, moving-boundary slope, exact inverse and modern
quadrature corrections were also run as separate B ablations; old signed
weights remain in A/B data, without clipping. The portable independent
integrator check records exact product/core revisions and clean status.

ITAMAE PR #18 (5da8dbbbd88f3f45dd7d2fbe66f11203d9632fa7) adds versioned
calculation provenance while preserving historical migration records unchanged.
New records cannot inject physics_mode. All 114 tests and complete CI passed;
it was merged to migration.

C standard-API source 503697a replaces dynamic legacy-class composition with
explicit CDM physics, solver and observable classes. It removes the duplicate
catalog and mode branches, leaving one PopulationComponents path and a minimal
tuple conversion. All 1,280 entries agree with independent B at roundoff;
50 product tests and 10 effective-manifest tests pass. The five-cell usage and
three-cell scientific notebooks execute in fresh kernels. Their first local
execution exposed a missing explicit module path for editable-install revision
lookup; this was fixed and rerun. Product/golden API checks were changed to test
standard behavior and frozen references, not runtime legacy coexistence.

This is still an intermediate state. C auxiliary data and seeded MC, SI/W/F
standard APIs, W/F execution stages, scientific limits/convergence, final
artifact/source-external runs, rights notices and review handoff remain open.
No authoritative parent compatibility revisions have been changed.

## C runtime inputs and SI standard API / numerical evidence

C PR #14 final head `c62c50b3e8e213cd193ec113420694a8050fd122` passed all eight
checks after updating the standalone Picard workflow to Python 3.11 and its
explicit ITAMAE input. It was merged into migration. Runtime PR #15
`3ce4202f04dda1c9345a7be0f9cac892afbac20f` then passed 53 local tests and all
eight CI checks before migration merge. External spectra use an explicit
`data_dir`, then `SASHIMI_C_DATA_DIR`, then the user cache directory. Missing
prompt-cusp spectra raise an error listing the required path; their scientific
validation remains deferred by the user's explicit decision. C's Poisson MC
now accepts a Generator or seed and does not consume global random state. It
preserves the Poisson point-process law, but not the old seed sequence or
random node ordering. Higher-order boost table preparation still needs review.

SI PR #8 (`949ba4f957083304c74b1b8f2bbbd5836b134e7d`) restores original
formation and CDM truncation gates in the SIDM weights, preserves shared node
identity, and avoids evaluating invalid reversed-time SIDM histories. Two
protection tests failed before the fix. Its active-domain EPS change removes
17,580 nonfinite trial evaluations outside physical support in a 30-mass /
200-host-node audit; no active nonfinite value was encountered. A/B changes
are independently isolated. All supported Python and walkthrough CI passed.

SI PR #9 final head `6ccb3e6ab2fde504542dc8363ca4f5135c997165` replaces the
legacy runtime with explicit physical kernels and the primary paired catalog.
The migration mode argument is removed; old fixtures remain historical.
SI's rounded gravitational constant is retained and recorded rather than
silently borrowing C's different constant. Fresh usage and science notebooks
execute. A Python 3.12 CI density discrepancy of 5.0414e-12 was investigated;
the same dependency versions locally did not reproduce the platform difference.
An independent 65-digit calculation did establish cancellation in the defining
effective-cross-section expression (up to 5.76e-11 on its interpolation nodes).
The same expression is now evaluated as a positive integral on 20 <= a <= 703,
with the original high-a asymptote retained. This numerical change is its own
commit and independent B patch; no tolerance was widened. Final 36 tests,
Python 3.11–3.13 CI, artifacts and walkthrough passed before migration merge.
The total-cross-section formula question remains pending and was not changed.
See `validation/references/sashimi-si/README.md` for A/B/C provenance and effects.

## ODE adapter and W structural migration in progress

A larger W audit (M0=1e12, zmax=7, dz=0.5, eight masses, three concentration
nodes, four host nodes) was interrupted after several minutes with no result.
The stack was in repeatedly evaluated top-hat concentration integrals inside
the historical odeint RHS. This is not a successful convergence/survival test.
The small, previously frozen q5/q10 catalog is the structural regression input.

## Common ODE contract, W standard API and F execution

ITAMAE PR #19 head `a601177e7996f6798b9a1f1d109bc6b2837d9cc6` passed all
132 tests, quality checks, the complete Python 3.11–3.13/backend matrix, build
and walkthrough before migration merge. It adds explicit odeint/LSODA with
SciPy's own tolerance defaults, while preserving the existing RK45 default.
The same-environment direct odeint results are bitwise equal in both time
directions. Eighteen new boundary cases failed before the change.

W PR #6 head `a5359a55c31d190e000552ed160181d8787e872b` uses explicit WDM
components and canonical stage arrays. Its tuple output derives from the
primary execution result; independent population/concentration factors are
retained without division. The 39 existing tests plus a new analytical
half-mass and batching case pass. Every declared CI passed before migration
merge. W PR #7 head `2ddaac5576e9a50c164d58419e481580d04f2879` then removed
runtime legacy branches, made Subhalos available through the standard import,
and added calculation-specification metadata. The unused historical sharp-k
initialization was removed; the separate top-hat concentration calibration
remains. All 35 standard-API tests and all declared CI passed before migration
merge. Frozen A/B fixtures and tolerances are unchanged.

W's four-cell usage notebook executes outside the source tree, and the separate
two-cell science notebook compares B/C and finite-difference derivatives. Both
ran in fresh kernels and plots were inspected. The first science execution
failed because Hatch's editable force-included modules lived in site-packages;
the scientific runner now starts in an explicit validation bundle. This did
not alter numerical calculations.

The W observable-count decision is pending: historical N_sat includes destroyed
nodes and drops the first histogram bin. For a constructed population with
weights 2,3,5 and only the middle node destroyed, it returns 8 rather than the
surviving total 7 (all-node total 10). The proposed separation is surviving
weights for current-time distributions/counts and generation weights for
accretion-time distributions, with correct cumulative totals and propagation
of profile_change. No such policy was adopted without a user answer.

F PR #14 head `a44f2cb` connects its named catalog to shared execution and
separates concentration weights. Existing exporter tests caught a missing
factor in process_m_22 and its analysis consumer; the consumers now retain the
complete weight. All 42 local physical/exporter tests and ten effective-manifest
tests pass. All private CI checks passed and the PR merged to migration at
`512502c384e40b9d58fc360b3ba83a26f456e64f`. The job enumerates coordinated
core/C/SI/W inputs before building and numerically checking all five packages.
Independent F A/B patches and full-C evidence stay in F's private repository.
The three isolated corrections affect native derivative scaling, the selected
growth derivative and exact NFW inversion. The latter changes one flag in a
constructed full-catalog threshold test and correctly resolves both sides of
c_t=0.77 in an analytic test. These are numerical checks, not a replacement for
the still-pending cutoff/backend/accretion/convergence science.

The current work is still not release-ready: F standard API/legacy removal,
user decisions for SI total cross section and W counts, remaining observable
inputs and scientific convergence, rights/version documentation, final exact
artifact matrix and the recorded parent candidate remain open.

## W standard-product references and F standard API

W clean standard-API product `2ddaac5` with ITAMAE `a601177` is recorded in
separate q5/q10 C artifacts. Relative B/C differences remain within original
limits (structure at most 7.75e-11; weights 9.94e-13), with exact survival masks.

F standard API commit `fe4a603` replaces the old population runtime and dynamic
migration inheritance with explicit standard classes. It exposes all existing
observables and packages process_m_22. New metadata uses a calculation
specification and preserves historical fixture identities. The physical
choices and EPS mass convention remain unchanged. All 35 local tests pass,
including the independent full B catalog at unchanged rtol=2e-11. Fresh installed
usage and scientific notebooks pass; observable outputs, structure-prior export
and three figures were checked. Candidate private CI is pending. The old-mode
production campaign is explicitly historical and refuses use on the standard API.

Remaining release requirements and both user questions above remain open.


## Runtime boundaries, prepared histories and source-archive identity

ITAMAE PR #20 (`d752306`) and W PR #8 (`186366a`) passed all declared CI before
migration merge. Direct catalogs/NPZ, canonical units and native cosmology now
reject invalid numerical inputs explicitly. W removes non-real formation
trials before growth evaluation while retaining the same valid trials.

F standard API PR #15 and seeded-realization PR #16 passed all private CI and
merged. The standard import exposes the existing observables and packages the
structure-prior helper. The native variance interpolation decision remains
pending; independent exploratory evidence is preserved in private F PR #17,
without adopting the proposed physical/numerical change.

W PR #9 (`d5b7f17`) reuses one identical virial-mass evaluation per ODE call.
All q5/q10 arrays and probes remain bitwise equal to `186366a`. Small-catalog
single-run times changed from 30.56/47.55 seconds to 6.62/10.19 seconds.
W PR #10 (`dcc4379`) then prepares fixed host-history coefficients once per
population call. All q5/q10 arrays/probes remain bitwise equal, including the
wider M0=1e12, zmax=7 case. That wider case changed from about 93 to 15 seconds.
There is no persistent model/table cache, and both PRs passed all CI before
migration merge. The top-hat-cache scratch prototype was not adopted.

The ten-case coarse W convergence sweep completed on fixed sources. Increasing
mass nodes from 16 to 32 changes bound mass fraction by about -11%; decreasing
dz from .5 to .25 changes it by +63–65% and total count by +15–16%. Host and
concentration quadrature effects are separately recorded. These coarse grids
are not certified as converged. Further .1/.05 redshift, 64–500 mass-node and
16–200 host-node runs use detached clean `dcc4379` plus ITAMAE `d752306` and a
separate Python 3.11/NumPy 2.4.6/SciPy 1.17.1 environment. No default changed.

The shared source-identity defect was reproduced independently in all five
build hooks: source archives unpacked under unrelated Git state could inherit
the enclosing HEAD. Each hook now preserves embedded archive identity,
requires an exact package Git root, and rejects malformed/conflicting explicit
revision overrides. Five new tests failed before each fix; seven pass after.
Real sdist-to-wheel rebuilds without revision injection, both ordinary and
inside unrelated Git repositories, succeed. Public evidence is under
validation/artifacts/build-source-identity, using scripts/check_sdist_rebuild.py.
These are intermediate build checks, not the final release-version matrix.
C PR #16 and SI PR #10 merged after all CI. SI's first CI attempt found a missing
setup.py in its outside-source test bundle; staging that build test input fixes
it, and all supported Python jobs pass. ITAMAE and W hook PR CI is pending.
F PR #18 (MIT/data attribution) and #19 (source identity) passed all private CI
and merged. ITAMAE MIT/citation preparation is committed and locally verified;
its candidate PR remains to be opened. The maintainer's public-release
confirmation with Elisa is retained for the later publication stage.

Remaining user decisions: SI total cross section, W observable counts and F
native variance evaluation. Other remaining work includes shared numerical
controls, remaining observable data/generators, scientific boundary/backend
checks and convergence, release versions/docs, exact wheel/sdist Python matrix,
and the recorded parent candidate plus no-override family verification.
Main, release tags, repository visibility and public package indexes remain
unchanged. This work is not release-ready.

## Redshift refinement and shared tidal controls

The further W runs at dz=.025/.0125 completed on the detached clean sources
specified above. For M0=1e12 Msun, WDM mass 2 keV, zmax=7, N_ma=16,
N_herm=3 and N_hermNa=4, changing only dz=.1 to .0125 increases surviving
catalog count by 4.940% (q5) / 5.000% (q10), and bound mass fraction by
17.199% / 17.663%. These are finite-grid comparisons at fixed representative
settings, not a measured error for all default settings or a continuum truth.
The final .025 to .0125 step still changes count about .7% and mass fraction
about 2.3%. `redshift-convergence.json` and the full configurations/catalogs
record the evidence. The user has been asked whether to retain the current
default with explicit accuracy limits or include changing the default step in
this preparation. No step or quadrature rule has been changed pending reply.

All five build-source identity fixes and the ITAMAE MIT license preparation
passed their complete CI and merged to migration. ITAMAE PR #23, final source
`e5c77cdf2832104752d641dd553902fc507885ba`, adds explicit LSODA options and
explicit repeated-output support. Twenty-one initial cases failed before the
extension; all 203 tests, quality checks and full Python/backend CI pass.
Direct SciPy comparisons include both time directions, dense/banded Jacobians,
repeated grids, zero evolution and failure controls. The default strict-grid,
solver and tolerance contracts are preserved. The PR merged to migration.

Consumer C/SI/F PRs now use that exact ITAMAE input. Their tidal equations,
100 output times and original Jacobian argument order are preserved; the
shared controller owns numerical execution and errors. Existing regression
suites and focused direct-odeint comparisons pass, including SI multi-output
and all three variants' zero-evolution/Jacobian cases. Consumer CI is pending.
Private F family CI names the coordinated C/SI/W inputs explicitly.


## Confirmed scope decisions: boost approximation and W redshift resolution

On 2026-09-10 the user explicitly approved exactly these two recommendations
(relayed through the monitoring conversation):

1. C/F higher-order annihilation boost keeps the historical undefined-table
   zero approximation only through explicit opt-in. Default calls reject
   incomplete tables. Warnings, invalid-point counts and provenance are
   mandatory. Developing a new low-mass boundary prescription is outside this
   preparation scope.
2. W keeps its existing redshift-step default. The measured step dependence,
   accuracy limits and convergence procedure must accompany peer review.
   Improving the default step is not an added completion condition.

These approvals do not apply to the three unanswered scientific decisions:
SI total cross section, W observable counts and F native variance interpolation.
No such prescription has been adopted while waiting.

C/SI/F shared-ODE consumer PRs #17/#11/#20 all passed CI and merged to their
migration branches. ITAMAE variance-boundary PR #24 (`cfaf4f5`) also passed
all 15 CI checks and merged. Full local suites were ITAMAE 260, C 65, SI 29,
W 44 and F 50; physical formulas and existing reference tolerances are unchanged.

A frozen C A run at the old ordinary boost generator's `1e-5 Msun`, z=0
zero-width resolved-mass grid gives exactly fsh=Bsh=0 and luminosity ratio=1,
without importing ITAMAE. Its full input/environment/export provenance is in
`validation/references/sashimi-c/A-boost-zero-width.json` and the corresponding
fixture. This preserves a historical numerical boundary result, not calibration
of a new low-mass prescription. C/F boost input implementation is in progress.

## Remaining scientific decisions received

The user adopted SI total cross section, F native direct top-hat, and W survivor-based observables after independent review. The W accretion display describes the same current survivors by accretion mass, confirmed against C/F. See [adoption record](adoption-2026-09-10.md) for exact scope and hashes of the received evidence. These three questions are no longer pending; implementation and verification continue.

## Adopted numerical contracts and observables: completed review units

C boost PR #18 (3fefa3426c33945ce4af63a472812ac6f9e4517c), private F boost
PR #21 (84e6cd8257712e7f33a106fae5e3194681eb91e8), core profile/window input
PR #25 (c2d7b9afb9773bc8cb5b2ee142d70d95cc3afe3b), SI total-cross-section
PR #12 (efa37c2a84e3c7a80e6436df48f3ff9232e3a232), W surviving-observable
PR #13 (09322feb1e348f40fa93d0514f42dd02171a7282), and private F direct-native
variance PR #22 (692587cf2a626b425f656573d5b64567c3387904) all passed their
complete CI and merged into migration. The authorized boost approximation is
explicit, warned, counted and recorded; the default rejects incomplete inputs.
W's accretion display describes current survivors. Native F sigma and derivative
now use the same direct integral and cache/query order is invariant. F raw
reference data and scientific patches remain in its private repository.

The F direct-native wheel and source archive were built at exact 692587c. The
sdist rebuilt without source-revision injection outside its repository, and
25 copied boost/direct-variance tests passed against installed artifacts. Both
F notebooks ran in fresh kernels (3 science cells, 4 usage cells); all figures
were inspected. Full F regression passed 75 tests before the next adapter unit.

SI stage-unit PR #13 (b9834354d565046a782d84285476f0f60c4248f8) passed all
Python 3.11–3.13 CI and merged. Intermediate shared states now use km/s, just
like the named catalog, with explicit conversions into SI-owned history kernels.
The real NFW stage identity failed before the fix; 38 migration and 20 established
physics tests passed afterward at unchanged reference tolerances.

## Controlled C/SI science and the normalized EPS limit

`scripts/check_population_convergence.py` saves complete catalogs for one-variable
sweeps. The original script bytes remain `validation/science/population-convergence-v1.py`.
The source SHA and actual script hash accompany every report. Public C/SI data
are under `validation/science`; these files are candidate validation, not the
parent's authoritative compatibility set.

C and SI now have mass grids through 500 points, redshift steps through .005,
concentration orders 3/5/7, host orders through 200, and direct ODE/tight-ODE
comparisons. At the representative M0=1e12 Msun, zmax=3, log-mass range 6–10,
ct_th=.77, changing dz=.01 to .005 changes count by about .26% and bound mass
fraction by .75–.77%. This is a finite-grid sensitivity with the other settings
held fixed, not an error guarantee. At dz=.25, N_ma=16, the default perturbative
solver differs from direct ODE by about 3.8% in bound mass fraction. Solver and
physical defaults remain fixed; these limitations require explicit review.

The SI sweep initially failed at host order 64 because the finite auxiliary
redshift search assigned an exactly zero barrier gap to 57 active nodes. Their
raw Hermite weights were 5.54e-49 to 3.42e-39. The existing nonfinite guard raised;
that failure is preserved. SI PR #14 (a233326f9be6c6436e368272adc42e56546ae571)
uses the analytic finite limit of the normalized Yang kernel, without clipping
or deleting weights. Seven new before-failing tests and all 45 migration tests
pass. All Python CI passed and the PR merged. Orders 64 and 200 subsequently
completed without warnings. C/F audits identified their remaining `nan_to_num`
paths at the same boundary; repairs are being reviewed separately.

`scripts/check_si_states.py` compares weak/default/strong interaction states and
C structure on identical accretion nodes. At sigma0/m=1e-8 cm2/g, paired weights
agree exactly and profile differences are below 4.7e-8; the maximum rc/rs is
4.6e-5. The strong case remains finite and has fewer valid SIDM survivors. The
native C/SI density difference is about 2.2% on these nodes. Matching background
density and each node's M200 NFW normalization reduces structure differences to
2.3e-15; tidal bound masses agree exactly. This diagnoses different concentration-
scatter/mass normalization conventions, not a reason to change either product's
calibration or equate their full population distributions.

## Current decisions and remaining work

A new F accretion-grid decision is pending. The existing F EPS calculation uses
the final redshift's virial-mass array at every time. A private controlled probe
changes only that array to the per-redshift conversion in both EPS and its
log-mass integral. At m22=.1/1/10, surviving counts decrease .23–.26%, bound mass
fractions decrease .85–1.51%, and individual weights differ by up to 3.06%.
The user has been asked whether to adopt this repair or retain the documented
limitation. No dependent product change is made before the reply.

Private F variance-snapshot PR #23 prevents changing an adapter's values through
later mutations of its source model and binds integrated cache identity to
particle mass and actual spectrum arrays. Local tests pass (78 total). The first
CI found only last-bit literal boost-reference differences in unchanged arithmetic;
CI now runs the frozen pre-loader method bitwise on identical population arrays.
Original fixtures and full-catalog tolerances remain unchanged. Final CI is pending.

Remaining release preparation still includes F cutoff/backend and population
convergence evidence, completed C/F EPS contracts, final scientific notebooks
and review documentation, release-candidate versions and distribution dependencies,
exact wheel/sdist verification across Python 3.11–3.13, full five-package private
CI, and the parent manifest/gitlink candidate plus no-override verification.
This work is not yet release-ready. Main, publication, tags and visibility remain
outside this preparation step.


## EPS completion, cutoff/backend evidence and candidate metadata

C PR #19 (3a822be2c5d83f5fa00a7ec49fc08d0fed40d505), SI PR #15
(31cfcadf7ed275967679b460d1a7fe5c7643d6dc) and private F PR #24
(0c5822bea88379503bc15ca507f70b9ba5213721) passed all CI and merged into
migration. Normalized EPS limits are evaluated on active support; prescriptions
1/2 use the zero reciprocal of the divergent lower-bound integral. Invalid
active variance gaps fail; no weights are clipped. Local full tests: C 95,
SI 49, F 92 followed by 15/15 focused EPS tests including its new matrix check
(93 total in CI). All three variants' frozen-before summed rates agree bitwise
at host orders 4/64/200 for each accretion prescription, with warnings removed.
The script, original outputs and execution-provenance companions are preserved.

C's first CI failed only literal boost-reference equality at up to 5.5e-16 in
3.11/3.13. The source population regression remained within its unchanged gates.
As for F, the boost refactor now runs its exact pre-loader method on identical
current population arrays and requires bitwise equality. The old JSON literal
fixture remains untouched; no tolerance was widened. Final C CI passed all
8 checks. F snapshot PR #23 also passed and merged previously.

Core PR #26 (6d0c74181afe067f87063e64e77565a9287d5de0) passed all 15 CI checks
and merged. It rejects lossy complex/string/bool power inputs, malformed transfer
shapes and product overflow. Fourteen tests failed before; all 309 core tests,
Ruff/format and mypy pass. Supported real-valued calculations are unchanged.

Private F cutoff/backend evidence at 0c5822b/core 6d0c741 is preserved with full
arrays and hashes. The Nadler Eq. 8–10 transfer agrees with an independently
written expression at 2.23e-16 absolute; its analytic ln-k derivative agrees
with finite differences at 3.46e-10 absolute, including neighborhoods of five
oscillatory nodes. Native derivatives remain negative. Colossus retains sign
failures and yields negative diagnostic EPS rates; no clipping or exchangeable-
backend claim is made. Low-resolution ITAMAE finite differences also show
isolated very-low-mass sign failures that disappear in the finer sampled run.
These are documented limits, with native direct top-hat kept as the product
choice. Private F PR #25 carries the evidence. The per-redshift F mass-grid
question remains pending and its product implementation is unchanged.

Core candidate PR #27 at dfa083d0d46181c376947ac7b2da829facaf2e8b passed all
15 CI checks. The agreed 0.2.0rc1 version, citation, changelog and wheelhouse
installation agree. Existing yanked build 1.5.1 was replaced in the developer
lock by non-yanked 1.6.1. The upload workflow is only an inactive documentation
template outside .github/workflows. It registers no upload trigger. C/SI/W
candidate version/dependency/CI metadata is being updated next; W gains Python
3.12 coverage. Final artifacts and exact five-package verification remain open.

### 2026-09-11: q10 adoption and review-candidate preparation

Received the user's independent W power audit and adopted the existing-coefficient
thermal q10 prescription (see adoption record). W e3017d9 removes q5 normal API
selection with explicit errors, retains the existing amplitude-half scale, adds
explicit power-half diagnostics and versions calculation/cache identities.
All 21 arrays per mass at 0.5/2/5 keV are bitwise equal to fixed old q10 09322fe
under core dfa083d and one unchanged environment. Full source exports, arrays,
input/dependency records and original runner bytes are preserved at
`validation/science/sashimi-w`; the editable distribution-metadata caveat is
explicit. All 87 W tests pass; both notebooks execute and all figures were
visually inspected. No CLASS rerun, coefficient fit or mass-limit inference.

Core 0.2.0rc1 metadata is merged in migration dfa083d. W rc metadata merged at
8a6cc66; F cutoff/EPS audit records merged at 8c03823. C/SI release metadata
and scientific summaries are being finalized; F rc metadata expands regression
and private coinstallation to Python 3.11–3.13. These are candidate preparation,
not a completed recorded-family compatibility set or a public release.

Post-EPS C (3a822be) and SI (31cfcad) catalogs at host-Hermite orders 64 and 200
now complete without warnings. The full arrays remain bitwise equal to the
prior successful calculation outputs; warnings/failures in the original sweep
are preserved, and the new successful execution is a separate record.

The user permits pausing at a safe boundary if unresolved decisions accumulate
before sleep. Do not infer answers. F's accretion mass-grid adoption remains
pending; its dependent implementation/final scientific comparison must wait.
Continue already-authorized work independent of that decision, and retain exact
source/process/restart state if a pause becomes necessary.


### 2026-09-11: exact installed artifacts and decision-wait handoff

The candidate versions and metadata are merged in all components. Final current
candidate SHAs are listed in `validation/artifacts/candidate-packaging-20260911/effective.toml`;
this is a dated temporary effective manifest, not a replacement canonical set.
C/SI/W notebooks and scientific summaries are complete at the current inputs.
F's mass-grid adoption, dependent final scientific notebook/convergence and the
recorded-parent public/private matrix remain open.

Exact clean-source wheels and sdists were built without revision injection.
Every unrelated-Git sdist rebuild preserves its runtime payload bitwise and
retains equivalent package metadata. All standalone packages pass minimal
Python 3.11 checks. Full installed regression on Python 3.11–3.13 passes 309
core + 95 C + 49 SI + 87 W + 94 F = 634 tests per version. Original and rebuilt
all-five environments pass standard-API physical catalogs, quantities, weights,
serialization, exact provenance and runtime-file non-collision.

The first F c90b002 sdist test collection failed because a test imported a
checkout-only historical analysis runner. F PR #27 removes that dependency,
retains inverse truth/tolerances and checks installed prior moments against an
independent formula; no product formula changed. All seven child CI checks
passed, followed by full installed tests at merged dc1b30574bf732f195b0777b6e64981d858d4c92.
The unchanged four artifacts are reused by hash; final all-five smoke uses the
new F wheel. Original failed results remain preserved.

Updated family issues #1 and #5–#17, core #4/#5 and F #4/#5/#6 to current
acceptance gates, archiving the superseded bodies in expandable history.
Updated the four draft variant umbrellas and created core draft PR #28;
none is merged into main or enabled for auto-merge. Public/private final-family
workflow drafts are prepared but inactive until the appropriate candidate inputs
and atomic parent recording are ready. The underlying smoke/rebuild scripts are
locally verified; the pending workflow templates themselves have not run in CI.

`docs/HANDOFF_20260911.md` records the pending F question, recommendation and
controls, candidate branches/SHAs, local artifact locations, known limitations,
canonical-source/rights policy and exact restart order. Public four-component
archives and private F archives/full evidence are also preserved in ignored
workspace directories so the handoff does not rely only on temporary files.
The goal remains incomplete; main, tags, publication and F visibility are unchanged.


Core SHA clarification: the tested artifact/component pin is topic head dfa083d;
the merged migration head used by umbrella PR #28 is 6d8ee62. Both have Git tree
1bf4f4bd4bdf74228041b711d4651056d66bedd1, but distinct embedded source identities.
The artifact summary correctly belongs to dfa083d and is not relabeled. Final
source alignment must rebuild any newly selected merge-SHA artifact. The new
umbrella CI succeeds and remains draft/open with auto-merge disabled.


### Continuation: align merge identities and execute the private artifact CI

Core is now checked out at migration merge 6d8ee62b65793df9b799977cbf1859b5233d4059,
with new wheel/sdist and rebuild evidence. Its runtime payload is identical to
the prior dfa083d artifact except embedded source identity. F PR #28 implements
the prepared original/rebuilt all-five numerical CI, explicit PR-head selection,
no build revision injection and the fixed parent runner input 97101de. The core
CI/developer pin is the actual merge SHA; locked resolution is verified offline.

PR head f6bad87 passed all seven checks and merged as
3a34188347ccc6e795e6fb640f9db1870ff4383b. Both merge workflows pass; downloaded
run 34503343420 proves the same resolved parent base and exact five sources for
original/rebuilt catalogs, quantities, weights, serialization and provenance on
Python 3.11–3.13. It is still candidate mode, not final no-override validation.

The exact merged-source local family was rebuilt/assembled and all 634 installed
tests passed again on each Python version. Original/rebuilt numerical smoke and
updated standalone core/F checks pass. New immutable public summaries are under
validation/artifacts/merged-candidate-packaging-20260911; private raw CI/local
records and new artifacts are preserved in the ignored workspace locations in
the updated handoff. The old artifact snapshot remains unchanged.

F's scientific mass-grid decision has not been answered or applied. Its dependent
final science/convergence and the atomic recorded-parent/public-private checks
remain the stopping gates. No main merge, auto-merge, publication or visibility
change occurred. The goal remains incomplete.

### Final continuation: user-approved F redshift accretion grid and candidate

The user identified the last-redshift grid reuse as a likely known mistake and
explicitly authorized correction. F PR #29 changes only the EPS mass argument
and its logarithmic mass integration to per-accretion-redshift virial grids,
versions calculation identity to v3, and rejects stale or mismatched prior
output reuse. Independent patch 05 on frozen A and all five corrections together
are preserved separately from every existing fixture. The new 0.1/1/10 B/C
full-catalog controls pass the unchanged rtol=2e-11; maximum weight discrepancy
is 8.08e-12. Pre/post structure and survival are bitwise equal; only weights and
dependent quantities change. Preserved results report count shifts about
-0.23 to -0.26 percent, mass-fraction shifts -0.85 to -1.51 percent, and maximum
individual-weight change 3.06 percent.

All 60 F population-resolution/solver catalogs completed, with every archived
array/hash reopened for the summary, finite nonnegative weights, applicable
bound-mass limits and zero RuntimeWarnings. Final one-variable mass/redshift
changes in mass fraction reach about 0.28/0.87 percent; coarse perturbative/ODE
differences remain about 3.9 percent. These do not prove joint continuum or
physical calibration. The usage/science notebooks execute in clean kernels
and all figures were inspected. New fixture editorial adoption labels were
corrected with the original execution metadata preserved explicitly; source,
patch and numerical-array identities were not relabeled.

All seven PR checks passed at cf29c16 before migration merge
98e1f91d3d0b55c8652518b507c0fec8044c2aff. Both merge-source workflows passed.
F artifacts were rebuilt from this clean SHA. All 104 shipped F tests pass
against installed wheels on Python 3.11–3.13. The unchanged public artifacts
reuse their 540 tests per version by hash, giving 644 verified tests per
version. New original/rebuilt all-five physical checks pass on all three
versions; unrelated-Git rebuilds preserve runtime payload, metadata and source
identity. Fresh minimal core+F installation passes. Candidate push CI
34549662699 has downloaded/verified exact source inputs and original/rebuilt
evidence. Core's final merge-source walkthrough 34493003890 is also preserved,
with seven executed cells and two visually inspected figures.

The final candidate summary is
validation/artifacts/final-v3-candidate-20260911/summary.json. Public four-package
artifacts and private F artifacts/full evidence are preserved in the workspace
locations named in the revised handoff. The prior handoff is an unchanged
historical checkpoint. No scientific user decision remains pending. The
candidate is now ready for atomic parent manifest/gitlink recording and the
same-parent no-override public/private CI, before declaring review readiness.

### Recorded family: release preparation complete, peer review pending

Parent commit 8184e572c37af051011b85f1b797bfda6d7dfb7d records the manifest and
all five gitlinks atomically and activates the prepared public family CI.
Committed-HEAD validation passes. Parent draft PR #34 is open for review.
Public run 34550691401 and private F dispatch 34550711351 both pass against
that exact parent on Python 3.11–3.13. Downloaded private input records report
family_mode=promoted, overrides={}, workflow source 98e1f91 and all five
manifest sources exactly. The final audit checks recorded gitlinks, manifest,
source and artifact hashes, every original/rebuilt smoke and reconstruction,
plus the private component regression (104 tests per version). Original and
rebuilt physical quantities agree. All raw evidence is preserved in the
workspace, keeping F outputs private; the public summary is under
validation/artifacts/recorded-family-20260911.

The goal's migration-branch stopping point is reached: preparation is complete
and awaiting peer review. C prompt-cusp scientific validation remains explicitly
deferred by the user, finite-resolution/solver limits are documented, F Colossus
remains experimental, and later coauthor/publication gates remain unperformed.
Main integration, auto-merge, tags, uploads and visibility changes were not
performed. This evidence/documentation update does not relabel the tested
parent SHA or alter the validated component sources or existing CI runners.
