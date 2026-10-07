# Merged-source candidate verification — 2026-09-11

This snapshot advances the earlier interim artifact set to actual migration
merge sources: core 6d8ee62 and F 3a34188. The complete source set and artifact
hashes are in `effective.toml` and `summary.json`; parent base is 97101de.
The temporary overrides are explicit. The canonical manifest/gitlinks have NOT
been promoted because F scientific adoption remains pending.

All 634 installed regression tests pass on each of Python 3.11–3.13 in newly
created all-five environments. Original and rebuilt wheels pass standard-API
physical catalogs/quantities, weight factors, serialization, exact provenance
and runtime-file non-collision. The two updated wheel runtime payloads equal
their prior artifacts except the embedded source descriptor; existing science
references and the earlier failed F collection evidence are retained unchanged.

Private F PR #28 makes these original/rebuilt checks part of the real family CI,
without build revision injection. Both PR head and merge-source workflows pass.
The downloaded merge run 34503343420 verifies the SAME parent base and five
source inputs on all three Python versions. Its raw catalogs, original reports
and rebuilt wheels remain in the private F review artifacts; this public summary
contains only provenance/check metadata. This remains candidate mode, not the
required final recorded-parent/no-override verification.

The F per-redshift mass-grid decision, dependent F science/convergence/notebook,
and final atomic parent recording with public/private no-override checks remain
open. No main integration, release tags, upload or visibility change is included.
