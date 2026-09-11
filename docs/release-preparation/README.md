# Recorded-family validation and release boundary

The prepared final-family configuration is installed in
`.github/workflows/family-integration.yml` with the atomic manifest/gitlink
change. It selects the exact PR head, tests Python 3.11–3.13, builds both
artifact forms without revision injection, executes standard-API physical
calculations outside the source tree and verifies unrelated-Git sdist rebuilds.

F's scientific adoption and complete temporary-candidate verification are
finished. The final recorded-family run must use the same exact parent commit
in public CI and the private F workflow's `family_base_ref`, with
`family_mode=promoted`. This mode applies no overrides. The resulting evidence
and status belong in [the handoff](../HANDOFF_20260911.md).

Private F's default workflow remains a component/candidate check using base
97101de, so an ordinary component push is not evidence of a recorded-family run.
F PR #29 and merge-source candidate run 34549662699 passed all checks after
the v3 accretion correction. [Candidate artifact evidence](../../validation/artifacts/final-v3-candidate-20260911/README.md)
preserves the exact identities and hashes.

Both active family workflows perform validation only. Publication examples in
each component's `docs/release-workflow.yml.example` remain inactive. Main
integration, release tags, PyPI/TestPyPI upload, index checks and F visibility
changes are later explicitly authorized steps after peer review.
