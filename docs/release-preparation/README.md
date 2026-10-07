# Recorded-family validation and release boundary

The prepared final-family configuration is installed in
`.github/workflows/family-integration.yml` with the atomic manifest/gitlink
change. It selects the exact PR head, tests Python 3.11–3.13, builds both
artifact forms without revision injection, executes standard-API physical
calculations outside the source tree and verifies unrelated-Git sdist rebuilds.

F's scientific adoption and complete temporary-candidate verification are
finished. The final recorded-family runs passed against parent
`8184e572c37af051011b85f1b797bfda6d7dfb7d`: public run 34550691401 and private
F run 34550711351, using `family_mode=promoted` with no overrides. Downloaded
evidence verifies the exact input set and artifacts on Python 3.11–3.13.
See [the final CI record](../../validation/artifacts/recorded-family-20260911/README.md)
and [the handoff](../HANDOFF_20260911.md).

Private F's default workflow remains a component/candidate check using base
97101de, so an ordinary component push is not evidence of a recorded-family run.
F PR #29 and merge-source candidate run 34549662699 passed all checks after
the v3 accretion correction. [Candidate artifact evidence](../../validation/artifacts/final-v3-candidate-20260911/README.md)
preserves the exact identities and hashes.

Both active family workflows perform validation only. Publication examples in
each component's `docs/release-workflow.yml.example` remain inactive. Main
integration, release tags, PyPI/TestPyPI upload, index checks and F visibility
changes are later explicitly authorized steps after peer review.
