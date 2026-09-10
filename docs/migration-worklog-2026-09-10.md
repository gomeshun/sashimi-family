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
