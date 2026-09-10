# ITAMAE migration review — 2026-09-04 UTC

The shared foundation and several adapters are implemented, but the family is
not yet a release candidate. The main remaining work is safe dependency
resolution, candidate CI, model decomposition, W/F execution integration, and
validation of the final combined branches and artifacts.

This is a dated audit of remote branch tips, PRs/issues, source, and CI. It is
not a second compatibility manifest or a claim that all experimental branches
have been scientifically validated. Active implementation guidance is in
[sashimi-migration-goal.md](../sashimi-migration-goal.md) and [epic #1](https://github.com/gomeshun/sashimi-family/issues/1).

## Compatible revisions versus development heads

Parent `main`: `a8e74be979a47d4a4bb293799840dbd772ce1a4a`.
The five pins in [compatibility.toml](../compatibility.toml) match its gitlinks.

| Component | Family pin | Migration head | Migration-only / main-only commits | Implementation state |
| --- | --- | --- | ---: | --- |
| ITAMAE | `1c5b1ad` | `1c5b1ad` | 7 / 0 | Shared types, numerics, variance, pipeline and provenance implemented; hardening/composition open |
| C | `4adc9af` | `4adc9af` | 35 / 6 | Pipeline connected; callbacks still need decomposition; main/Picard reconciliation required |
| SI | `56b5e50` | `56b5e50` | 21 / 0 | Pipeline connected with CDM/SIDM views; model/state decomposition remains |
| W | `6763869` | `6763869` | 19 / 0 | Catalog/variance migration implemented; pipeline execution not connected |
| F | `2091a50` | `76b4880` | 28 / 0 | Six commits beyond pin; structure-prior work added; pipeline execution not connected |

Commit counts describe ancestry, not effort or percentage completion. All four
variant migration PRs remain Draft. ITAMAE has no open migration umbrella: its
foundation PR #2 merged in July and its alternative PR #1 was closed unmerged.

## What the green checks actually establish

| Evidence | Result | Scope and limit |
| --- | --- | --- |
| [Family run 33485778815](https://github.com/gomeshun/sashimi-family/actions/runs/33485778815) | Success | Pinned ITAMAE/C/SI/W wheel co-install, imports, overlap and provenance; excludes private F and does not run full family numerical regression |
| [ITAMAE run 32918495108](https://github.com/gomeshun/itamae/actions/runs/32918495108) | Success | Current migration head `1c5b1ad` |
| [C run 32918719936](https://github.com/gomeshun/sashimi-c/actions/runs/32918719936) | Success | `4adc9af`, before the September main/Picard changes; not current combined-branch evidence |
| [SI run 32918720334](https://github.com/gomeshun/sashimi-si/actions/runs/32918720334) | Success | Current migration head `56b5e50` |
| [W run 32918719388](https://github.com/gomeshun/sashimi-w/actions/runs/32918719388) | Success | Current migration head `6763869` |
| [F run 33725013069](https://github.com/gomeshun/sashimi-f/actions/runs/33725013069) | Regression success; family failure | `76b4880`: log confirms 40 tests passed plus lint/build/smoke; family job fails at SHA comparison before building |
| [F manual run 32918883866](https://github.com/gomeshun/sashimi-f/actions/runs/32918883866) | Success | Older `2091a50` and its then-current family inputs; not latest-F validation |

The 165 passing tests recorded in epic #1 are an August 27 source-tree
snapshot, not a test run repeated by this review. This review inspected the
latest relevant GitHub jobs/logs and performed local manifest/document/source
checks; it did not rerun the expensive production science analyses.

## Findings and plan corrections

### 1. Historical tasks were being presented as current blockers

The historical implementation plan still asked the next agent to fix C Ruff,
resolve F's old duplicate-source install, create the manifest, and first wire
C/SI execution.
The current code already implements those steps. The plan now distinguishes
completed foundations from CORE-01/02, C-01/SI-01 decomposition and W-01/F-01
pipeline work. The four old umbrella descriptions also understated their scope
as a background-cosmology adapter only.

### 2. Candidate CI must precede compatibility promotion

F's family job reads parent `main` and requires its own checked-out SHA to equal
the old manifest pin. A new candidate fails by construction; a PR's synthetic
merge commit is an additional source of mismatch. Component regression and
candidate-family validation need independent inputs and a clearly chosen test
SHA. The corrected plan specifies a recorded parent commit, a temporary
effective candidate manifest, and separate promoted-set validation.

Existing owners: [F GOV-01](https://github.com/gomeshun/sashimi-f/issues/2),
[GOV-03 #4](https://github.com/gomeshun/sashimi-family/issues/4).
Do not advance the F pin just to silence the assertion. C's separate co-install
job also still uses SI `179d52d`, while the family pin is `56b5e50`.

### 3. Child PRs currently miss variant migration CI

C/SI/W/F migration workflows have `pull_request.branches: [main]`, but the
agreed implementation workflow targets `itamae-migration`. Checks triggered
only after merging a child PR cannot validate it beforehand. Track the small
workflow corrections and actual child-PR check evidence in
[GOV-07 #25](https://github.com/gomeshun/sashimi-family/issues/25).
ITAMAE already has an unrestricted pull-request trigger.

### 4. C main has moved independently

[C PR #4](https://github.com/gomeshun/sashimi-c/pull/4) merged the Picard table
into main on September 3. [C PR #5](https://github.com/gomeshun/sashimi-c/pull/5)
separately proposes the public `picard_table` default and remains open.
Migration and main diverge even though GitHub currently reports the umbrella
as textually mergeable. [SYNC-C #26](https://github.com/gomeshun/sashimi-family/issues/26)
requires reconciliation, preservation of both test suites/package contents,
and explicit historical solver/threshold/mode references before release.

Do not silently regenerate legacy fixtures to match a new public default.
Numerical-method adoption and a scientific/default decision have separate
acceptance criteria; a one-halo ODE comparison does not replace catalog tests.

### 5. Package identity remains unresolved

ITAMAE metadata still declares distribution `itamae`; the naming collision is
tracked in [ITAMAE #3](https://github.com/gomeshun/itamae/issues/3).
SI/W use unqualified version ranges and F uses `itamae>=0.1.0a4,<0.2`.
Their uv VCS overrides are not wheel `Requires-Dist` guarantees. C's explicit
VCS extras avoid that particular resolution ambiguity but must still be
updated when the distribution is renamed.

The plan now includes consumers, uv keys/locks, provenance distribution
lookups, artifact filename prefixes, and clean resolver tests in the rename.
REL-03 also needs an unpacked-sdist-to-wheel build without Git/environment
provenance fallback. Existing source builds and pre-supplied wheel co-installs
are useful but do not establish the full release installation contract.

### 6. Saved notebooks and scientific evidence are partial

| Migration demo | Non-empty code cells | Missing execution counts | Saved errors |
| --- | ---: | ---: | ---: |
| C | 8 | 0 | 0 |
| SI | 9 | 1 (code cell 7) | 0 |
| W | 7 | 1 (code cell 6) | 0 |
| F | 9 | 1 (code cell 9) | 0 |

Code-cell indices here count non-empty code cells only. A saved execution
count does not prove a clean sequential run. README's blanket claim that all
migration demos were executed is corrected; [GOV-05 #6](https://github.com/gomeshun/sashimi-family/issues/6)
remains open.

F has added a [structure-prior comparison report](https://github.com/gomeshun/sashimi-f/blob/76b4880496bd5d7c64def810cd3ab321f09f17c7/analysis/process_m22_physics_comparison/REPORT.md)
and recorded inputs/results. This is real progress for
[PHY-F](https://github.com/gomeshun/sashimi-f/issues/6), but its own report
states that changing `physics_mode` jointly changes three corrections. It
does not replace per-correction ablation or native/ITAMAE/Colossus cutoff tests.

### 7. Migration and new science need different completion gates

The September scientific epic already separates future work, but older plan
ordering still placed soliton/spatial/orbit features before release. The
corrected plan requires contracts that preserve existing C/SI/W/F states and
validation of existing migration differences. New soliton/core-halo,
phase-space, orbit, scatter, lensing and baryonic features remain under
[epic #18](https://github.com/gomeshun/sashimi-family/issues/18).

Use one vocabulary: A radial measure, B conditional phase space, B+ reduced
orbit-conditioned evolution, C optional explicit orbit integration. Host
environment queries support these levels. Generic orbit helpers do not by
themselves complete a spatial population implementation.

REL-05 must also distinguish atomic parent manifest/gitlink updates from
sequential cross-repository merges. Merge/squash can change source SHAs; final
artifacts and provenance must be revalidated after integration.

## Branch inventory

The tables below cover all 34 submodule branches returned by GitHub at the
snapshot. `Branch-only` and `migration-only` count commits relative to that
repository's `itamae-migration` tip. An ancestor needs no wholesale merge;
divergent experimental code requires a separate decision and validation.
Feature names and PR status are not evidence of completed migration.

ITAMAE's older alternative `agent/implement-roadmap` is deliberately not the
canonical base; [foundation-integration.md](https://github.com/gomeshun/itamae/blob/1c5b1ad67725671fd4dc1a2306d2731ba337e563/docs/foundation-integration.md)
records what was reimplemented and why the old branch must not be merged
wholesale. C spatial/non-Gaussian/variational branches and SI experiments are
reference work outside the current release path. SI's truncation PR #1 and
C's verbosity PR #2 remain open on their respective bases.

### itamae

| Branch | SHA | Branch-only | Migration-only |
| --- | --- | ---: | ---: |
| `agent/implement-roadmap` | [`3136d27`](https://github.com/gomeshun/itamae/commit/3136d277cb4082ead83b1cdf03702e1640b8767a) | 2 | 24 |
| `agent/initial-roadmap-implementation` | [`94d58dd`](https://github.com/gomeshun/itamae/commit/94d58dd2e56ad95e9212dc1f34d5c21cdb4df9a6) | 0 | 8 |
| `agent/phase-0-1-foundation` | [`4e022c5`](https://github.com/gomeshun/itamae/commit/4e022c530451cd7c581531e5582b51ec64e0e06b) | 0 | 24 |
| `itamae-migration` | [`1c5b1ad`](https://github.com/gomeshun/itamae/commit/1c5b1ad67725671fd4dc1a2306d2731ba337e563) | 0 | 0 |
| `main` | [`863cb06`](https://github.com/gomeshun/itamae/commit/863cb0643c61ca4ea7458d7a221f48e5c5bfe515) | 0 | 7 |

### sashimi-c

| Branch | SHA | Branch-only | Migration-only |
| --- | --- | ---: | ---: |
| `SASHIMI-spatial` | [`50cc400`](https://github.com/gomeshun/sashimi-c/commit/50cc400a31ff48f8ba09a57e97f0be993862c1ce) | 5 | 43 |
| `approx_odeint` | [`75c4297`](https://github.com/gomeshun/sashimi-c/commit/75c42976990ec47351e741223222f7cc4c180db5) | 0 | 43 |
| `codex/add-verbose-option-for-tqdm-output` | [`609ee13`](https://github.com/gomeshun/sashimi-c/commit/609ee1301a15914e2b6cf0ef26bcc3e218c63cf0) | 12 | 43 |
| `codex/普通のfor-loop選択肢を追加` | [`7eb1ea7`](https://github.com/gomeshun/sashimi-c/commit/7eb1ea7abcb81293a4d3472d21e13fca1024959e) | 10 | 43 |
| `feat/picard-default` | [`88ae730`](https://github.com/gomeshun/sashimi-c/commit/88ae730762fb153be7a7433bb563b0b8ab3ec2c2) | 15 | 35 |
| `feat/picard-tidal-stripping` | [`9779b63`](https://github.com/gomeshun/sashimi-c/commit/9779b63ef8ff58afb5814fc9f404c617d8254a7c) | 5 | 35 |
| `itamae-migration` | [`4adc9af`](https://github.com/gomeshun/sashimi-c/commit/4adc9af8ba14b7a3a5db39fdb55cb4fc7a5b1083) | 0 | 0 |
| `main` | [`e09571b`](https://github.com/gomeshun/sashimi-c/commit/e09571be7a1daaef343e97887e34449faf21db7b) | 6 | 35 |
| `minor_fix` | [`1acc42a`](https://github.com/gomeshun/sashimi-c/commit/1acc42a12108a5c0a64749e6ad240f79ed834477) | 1 | 43 |
| `ng` | [`7681f4f`](https://github.com/gomeshun/sashimi-c/commit/7681f4fd6bb4499c978343549a804f9067816249) | 6 | 43 |
| `r-dependent` | [`47f79c5`](https://github.com/gomeshun/sashimi-c/commit/47f79c5bb7bfbf8df59c6372084ddc2815080a14) | 25 | 43 |
| `sashimi_v2` | [`fea9733`](https://github.com/gomeshun/sashimi-c/commit/fea97336ba883008aa22a30225cf901f7c336013) | 24 | 41 |
| `variational_sashimi` | [`b60b71a`](https://github.com/gomeshun/sashimi-c/commit/b60b71a359edb934a5467d268039ec483f6d6457) | 1 | 66 |

### sashimi-si

| Branch | SHA | Branch-only | Migration-only |
| --- | --- | ---: | ---: |
| `concentration_sampling` | [`a275349`](https://github.com/gomeshun/sashimi-si/commit/a2753493ad9e474ba496ae3ac52cdfc6a3db6d9a) | 4 | 34 |
| `copilot/add-profile-truncation-option` | [`2f7f9b9`](https://github.com/gomeshun/sashimi-si/commit/2f7f9b9af9b350ceb16eaae24c065c074b1349ef) | 4 | 28 |
| `fix_cross_section` | [`6303f75`](https://github.com/gomeshun/sashimi-si/commit/6303f75a6952ea1bb001eec61f4fcc8462ee05da) | 0 | 31 |
| `for_large_t_collapse` | [`83d89a6`](https://github.com/gomeshun/sashimi-si/commit/83d89a6c28bd5774342b337a50ee8969fe59f50c) | 0 | 37 |
| `itamae-migration` | [`56b5e50`](https://github.com/gomeshun/sashimi-si/commit/56b5e509fe9da206d28e6a0371fcfc300f18a919) | 0 | 0 |
| `main` | [`e17d366`](https://github.com/gomeshun/sashimi-si/commit/e17d3664dac677b604fd4ff02fb2af105a6937fa) | 0 | 21 |
| `memory_usage_reduction` | [`3f59e56`](https://github.com/gomeshun/sashimi-si/commit/3f59e564abf289112faccf4cabf04b09fa7e2881) | 0 | 51 |
| `mzzi_inversion` | [`58e275d`](https://github.com/gomeshun/sashimi-si/commit/58e275de213e2a023e46c5c35c99649c7ddae0b5) | 0 | 34 |
| `optimize_Na_total_calculation` | [`17fcea8`](https://github.com/gomeshun/sashimi-si/commit/17fcea8d9433bab3c86d7666d905ddaa4bb58519) | 2 | 51 |
| `parallelization` | [`4d257cc`](https://github.com/gomeshun/sashimi-si/commit/4d257cc99c76ad320d48fac1a256fc9a4f7f585a) | 0 | 42 |
| `perturbative_solver` | [`83d89a6`](https://github.com/gomeshun/sashimi-si/commit/83d89a6c28bd5774342b337a50ee8969fe59f50c) | 0 | 37 |

### sashimi-w

| Branch | SHA | Branch-only | Migration-only |
| --- | --- | ---: | ---: |
| `itamae-migration` | [`6763869`](https://github.com/gomeshun/sashimi-w/commit/676386919f638a6f460a3ec50304384373e0d6fc) | 0 | 0 |
| `main` | [`99dfc36`](https://github.com/gomeshun/sashimi-w/commit/99dfc3632eec0126080c0273ddf78f84fe09216c) | 0 | 19 |

### sashimi-f

| Branch | SHA | Branch-only | Migration-only |
| --- | --- | ---: | ---: |
| `copilot/evaluate-numerical-integration` | [`0b04f72`](https://github.com/gomeshun/sashimi-f/commit/0b04f72ae474ea7e54ffd8154c4caf0c1d0a47f2) | 2 | 28 |
| `itamae-migration` | [`76b4880`](https://github.com/gomeshun/sashimi-f/commit/76b4880496bd5d7c64def810cd3ab321f09f17c7) | 0 | 0 |
| `main` | [`68d617e`](https://github.com/gomeshun/sashimi-f/commit/68d617e94d254054cf65bb9a92d6200fe1582dd8) | 0 | 28 |
