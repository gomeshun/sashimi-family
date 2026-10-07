# CI deduplication evidence — 2026-10-07

The recorded parent is `c35fa1d60639ff6ec6a21c36021bdbc92a9c6bf7`.
`public-summary.json` records the public CI audit and the exact PR/merge evidence.
The authoritative current revision set remains `compatibility.toml` and its
committed gitlinks. The [CI policy](../../../docs/ci-validation.md) defines the
standard and full profiles.

All five component changes contain only their two CI workflow files. Physical
code, test fixtures, data and numerical tolerances are unchanged from the
preceding family refresh. Existing scientific limits remain in the
[October 7 handoff](../../../docs/HANDOFF_20261007.md); this scheduling cleanup
adds no calibration or observational-limit claim.

## Evidence locations

- Public CI distributions, original/rebuilt/standalone calculations and logs:
  `review-artifacts/20261007-ci-dedup/recorded-ci/`.
- Public component PR checks, prospective/actual merge-tree checks and successful
  merge-push reuse logs: `review-artifacts/20261007-ci-dedup/component-ci/`.
- Public executed notebooks and cell/figure audits:
  `review-artifacts/20261007-ci-dedup/notebook-ci/`.
- Private full-family CI, F notebook, local all-five candidate artifacts,
  effective manifest and complete execution records:
  `sashimi-f/artifacts/ci-dedup-20261007/`.

Those directories are Git-ignored workspace evidence. The full combined audit
is `sashimi-f/artifacts/ci-dedup-20261007/recorded-ci-audit.json`; public tracked
summaries contain only the public projection. Successful notebooks keep their
actual PR-head generation identities; their output is not relabeled as generated
by the later merge commit.

## Re-audit

```sh
python3 scripts/summarize_recorded_family.py \
  --parent-sha c35fa1d60639ff6ec6a21c36021bdbc92a9c6bf7 \
  --public-evidence review-artifacts/20261007-ci-dedup/recorded-ci \
  --private-evidence sashimi-f/artifacts/ci-dedup-20261007/recorded-ci \
  --output /tmp/ci-dedup-reaudit.json
```

The public automatic run uses `standard`. The private promoted run uses `full`
and the same parent, with no overrides. The audit checks exact source identities,
manifest and archive hashes, actual Python coverage, standalone checks, shipped
regressions where requested, and equality of original/rebuilt results.
Historical per-Python-layout evidence remains supported and unchanged.

## Skip boundaries

Shared-helper tests cover missing/failed preceding validation, manual profiles,
source changes, rename sources and merge-tree mismatch. Actual merge-push logs
confirm reuse only after the same workflow succeeds at a parent with an identical
Git tree. Push and PR refs have separate concurrency groups. Manual family-only
success cannot qualify as component-regression success.

The PR head is the declared candidate source. The prospective merge tree was
checked against the tested PR head before each integration and the actual tree
was checked again after merging. No target-branch changes were accepted solely
on the strength of a passing head check.
