# Recorded-family verification — 2026-09-11

**Passed; migration release preparation is ready for peer review.**

Recorded parent: `8184e572c37af051011b85f1b797bfda6d7dfb7d`.
It commits `compatibility.toml` and all five gitlinks together. The
[machine-readable audit](summary.json) records their exact identities and the
downloaded evidence for:

- [Public run 34550691401](https://github.com/gomeshun/sashimi-family/actions/runs/34550691401):
  all four public packages, Python 3.11–3.13, original and rebuilt wheels.
- [Private run 34550711351](https://github.com/gomeshun/sashimi-f/actions/runs/34550711351):
  all five packages, the SAME parent SHA, Python 3.11–3.13,
  `family_mode=promoted`, `overrides={}`, original and rebuilt wheels.

This is not a candidate-override run. The auditor checks the recorded gitlinks,
both manifests, workflow/source heads, completed jobs, all three interpreters,
embedded installed source identities, numerical smoke success, original/rebuilt
physical equality, original artifact hashes, rebuilt wheel file hashes, sdist
source retention without revision injection, and private regression JUnit
results (104 tests per version, no failures/errors/skips).

Raw downloaded evidence is retained locally at:

- `review-artifacts/20260911-final-v3/public-recorded-ci-34550691401/`.
- `sashimi-f/artifacts/release-preparation-20260911-final-v3/private-recorded-ci-34550711351/`.

The latter contains private numerical catalogs and stays private. Public
summaries retain only identity, hash and status information. The local candidate
artifacts and 644 verified installed tests per Python version are separately
described in [the candidate record](../final-v3-candidate-20260911/README.md).

Re-audit the downloaded records from this repository with:

```bash
python3 scripts/summarize_recorded_family.py \
  --parent-sha 8184e572c37af051011b85f1b797bfda6d7dfb7d \
  --public-evidence review-artifacts/20260911-final-v3/public-recorded-ci-34550691401 \
  --private-evidence sashimi-f/artifacts/release-preparation-20260911-final-v3/private-recorded-ci-34550711351 \
  --output /tmp/recorded-family-audit.json
```

Later evidence/documentation commits do not replace the tested parent identity.
The manifest, gitlinks and existing CI/numerical runners stay unchanged.
Main integration and index publication remain later separately authorized
operations; [the handoff](../../../docs/HANDOFF_20260911.md) lists those steps
and the scientific limitations.
