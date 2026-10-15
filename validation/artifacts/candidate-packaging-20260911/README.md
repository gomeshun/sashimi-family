# Interim candidate artifact verification — 2026-09-11

This immutable evidence snapshot uses a temporary effective manifest based on parent
`7d4e244f61929b3b670385bb20da9d816af4bffe`. It does not replace the authoritative
root compatibility manifest or claim final scientific/release readiness.

All five exact wheel/sdist pairs preserve source identity. Unrelated-Git sdist
rebuilds preserve runtime payloads bitwise and retain equivalent distribution
metadata, without source-revision environment injection. Full installed tests on
Python 3.11–3.13 pass: core 309, C 95, SI 49, W 87, F 94 (634 per version).
Original and rebuilt five-package installations pass standard-API physical
catalog/count/mass, weight, serialization, provenance and collision checks on all
three versions. Minimal standalone core/variant environments pass on Python 3.11.

F's original c90b002 test collection failed outside its checkout. PR #27 isolated
the product regression from the unshipped historical analysis runner. The new F
artifact is dc1b305. The four unchanged artifacts were reused by exact hash;
their full regressions are not repeated for a change confined to F tests/CI/docs.
New all-five physical smoke runs use the new F artifact. The historical failure
is preserved in summary.json rather than hidden by successful follow-up runs.

The summary retains environment and artifact hashes but excludes private F raw
catalogs and test sources. Complete local evidence and wheelhouses are retained
under the locations recorded in the release handoff. Copied audit scripts are the
exact bytes used, including the original build-script hash. Numerical convergence
and scientific decisions are separate from these packaging checks. F's mass-grid
adoption/final convergence and the recorded-parent checks without overrides are
still open. No upload, release tag, main merge or visibility change was performed.
