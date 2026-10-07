# CI validation frequency

The October 7 CI cleanup changes scheduling and artifact reuse, not physical
models, reference data, tolerances or the supported Python 3.11–3.13 range.
The sole recorded family set remains `compatibility.toml` plus its gitlinks.

## Component and documentation changes

Component regressions remain on all three supported Python versions. Packaging
and lint work need not be repeated for each interpreter. The same built wheels
can be installed into the separate regression environments. Single-package
checks remain distinct from family co-installation: the former catches missing
declared dependencies, while the latter catches collisions and integration errors.

The shared `changed-paths` action compares the latest PR update or push with its
preceding commit. It skips expensive work only when relevant files are unchanged
and the same workflow has a successful run at that preceding commit. Initial PRs
compare against their base. A merge can reuse its successful PR check only when
the entire Git tree matches a validated merge parent. Failed, pending or
unavailable history runs the checks. Manual dispatch always runs them, and its
success cannot substitute for automatic-check history: it may run a different
profile or skip the component jobs entirely.

This uses a lightweight successful job rather than workflow-level path filters:
PR-wide filters would still retrigger on documentation-only updates to a large
migration PR, and skipped required workflows can leave checks pending. The
action needs only `contents: read` and `actions: read`; it never writes to GitHub.
Outputs retain the original execution SHA when a check is reused.

Full walkthrough notebooks run when their code, data, packaging, execution
scripts, notebook source or own workflow changes, or on manual dispatch. Tests
and unrelated prose changes do not alone require rerunning a physical notebook.
Reduced CI frequency does not reduce the scientific grid or replace convergence
and calibration evidence.

## Family profiles

`scripts/validate_family_artifacts.py` provides the same procedure locally and in
CI. Each public/private family run builds every selected component once and
rebuilds each source archive once, outside its original Git checkout without
revision injection. It rejects non-universal wheels rather than silently applying
this policy to a future compiled extension. Original and rebuilt runtime, data
and distribution metadata must match; ZIP headers and the RECORD index need not.

| Check | Standard automatic family run | Full manual/release-candidate run |
| --- | --- | --- |
| Exact manifest, source SHA and artifact identity | Required | Required |
| Same original wheels, small physical calculation and save/load | Python 3.11, 3.12, 3.13 | Python 3.11, 3.12, 3.13 |
| Rebuilt-wheel calculation | Python 3.11 | Python 3.11, 3.12, 3.13 |
| Each standalone installation | Python 3.11 | Python 3.11 |
| Full shipped regression suite against installed wheels | Component CI owns the regressions | Python 3.11, 3.12, 3.13 |

Public family checks run when its manifest/gitlinks, validation helpers or CI
change. Private full-family checks are explicitly dispatched for candidate or
recorded-family validation; routine component updates use their component CI.
Before accepting a new recorded family, public and private runs still have to
use the same parent commit and the private promoted run must have no overrides.
Those are distinct integration scopes, even when public components overlap.

Manual family dispatch defaults to `full`. Use it for release candidates or
substantial packaging changes. Normal development uses `standard`; do not repeat
the full installed suite locally solely to duplicate already verified CI. A
local targeted test or an explicit full release rehearsal remains available.
The profiles do not test dependency lower bounds or publish to any package index.

The auditor supports both historical per-Python artifacts and the new shared
artifact layout. New reports state the profile, exact artifact hashes and the
Python versions actually used for each check. A standard run cannot be relabeled
as three rebuilt-wheel runs or as a full installed-regression run. Historical
reports and their source identities remain unchanged.
