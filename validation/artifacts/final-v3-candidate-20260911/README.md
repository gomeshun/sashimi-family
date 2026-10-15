# Final v3 candidate artifacts — 2026-09-11

The [summary](summary.json) verifies the complete candidate with F migration
merge `98e1f91d3d0b55c8652518b507c0fec8044c2aff`. Candidate validation precedes
atomic parent recording; the final no-override CI evidence is linked from
[the handoff](../../../docs/HANDOFF_20260911.md). Earlier candidate records retain
their original identities and results.

- F is newly built from its clean merge source, with no source-revision environment
  injection. The unchanged four original wheel/sdist pairs are reused after
  SHA-256 verification against the previous merged-candidate record.
- All five sdists are rebuilt inside unrelated Git state. Embedded source
  identities, every runtime payload byte, METADATA and WHEEL match the original
  artifacts. ZIP/tar container byte identity is not the acceptance criterion.
- F's shipped 104 tests pass against its installed wheel on Python 3.11–3.13.
  Core/C/SI/W retain 309/95/49/87 passing installed tests on each version for
  the exact unchanged artifacts. This is 644 verified tests per version;
  the unchanged 540 were not rerun merely to repeat existing evidence.
- New original and rebuilt five-package environments pass physical catalogs,
  observables, weights, serialization, source provenance and runtime-file
  collision checks on all three Python versions. A fresh minimal core+F
  installation also passes on Python 3.11. Earlier unchanged standalone checks
  remain in the prior record.
- Private F push run [34549662699](https://github.com/gomeshun/sashimi-f/actions/runs/34549662699)
  passes regression and both artifact forms on all three Python versions.
  Downloaded artifacts confirm every candidate override and the exact five
  source revisions. It is explicitly candidate mode using base `97101de`.
- Core's final merge-SHA [walkthrough run](https://github.com/gomeshun/itamae/actions/runs/34493003890)
  executed all seven cells. Its [executed notebook](itamae-usage-walkthrough.executed.ipynb)
  is preserved here; both figures were visually inspected. All four variant
  usage/science notebooks have executed cells without error outputs.

Local retained artifacts:

- Public wheels/sdists: `review-artifacts/20260911-final-v3/dist/`.
- Private F wheels/sdists: `sashimi-f/artifacts/release-preparation-20260911-final-v3/dist/`.
- Full local tests, catalogs, logs and reconstruction evidence:
  `sashimi-f/artifacts/release-preparation-20260911-final-v3/full-evidence/`.
- Downloaded private candidate CI evidence: the sibling
  `candidate-ci-34549662699/` directory.

These retained artifact directories are ignored by Git. The public summary
contains hashes and validation status, not private F source or catalog arrays.
Original transient working files remain under
`/tmp/sashimi-migration-20260910/rc-packaging-v3-20260911/`.

Reproduction uses `scripts/build_candidate_artifacts.py`,
`scripts/check_artifact_provenance.py`, `scripts/check_sdist_rebuild.py`,
`scripts/check_installed_candidate.py` and `scripts/smoke_installed_family.py`.
The exact local orchestration script and effective manifest are preserved with
the private evidence. Required dependencies are normal package-version
requirements, supplied from the candidate wheelhouse. No index upload or
public-index installation is claimed.
