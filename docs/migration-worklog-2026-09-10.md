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
