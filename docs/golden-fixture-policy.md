# Golden Fixture Policy

Golden fixtures are compact, versioned regression records for the SASHIMI
migration boundary. They protect published legacy behavior and reviewed
corrected behavior without making a physics correction implicit.

## Provenance schema

Every full-catalog fixture must contain a top-level `provenance` object, or a
same-name JSON sidecar when the regression values remain inline in a test. The
object uses the following fields:

- `fixture_schema`: `sashimi-family:golden-provenance:v1`
- `fixture_category`: the covered regression, normally `full_small_catalog_golden`
- `fixture_purpose`: the observable or catalog contract being protected
- `variant`: `sashimi-c`, `sashimi-si`, `sashimi-w`, or `sashimi-f`
- `generated_repository_revision`: the variant commit that generated the values
- `itamae_source_revision`: the ITAMAE commit used for generation
- `physics_modes`: every mode represented by the fixture
- `mode_policy`: whether each mode is strict legacy reproduction or reviewed
  consistent physics
- `parameters_key` and `units_key` when those records are in the same JSON
- `comparison`: tolerances and a short reason for them

Variant-specific provenance is allowed. For example, WDM fixtures also record
the explicit power convention, while FDM fixtures can distinguish the
historical generation revision from a later validation revision.

## Mode policy

A `legacy` entry reproduces the historical public result, including documented
numerical quirks. A `consistent` entry is a separately named reviewed result.
The two entries must not be merged or selected implicitly by a default change.
If their outputs differ, keep separate expected values and explain the reason
in `mode_policy`.

## Regeneration procedure

1. Run the compact fixture test with the exact intended variant and ITAMAE
   revisions.
2. Record all non-default parameters, unit conventions, backend choices, and
   comparison tolerances in the fixture or sidecar.
3. Record the full 40-character variant and ITAMAE revisions.
4. Review legacy and consistent outputs independently; do not overwrite one
   mode with the other.
5. Run the variant regression suite, package smoke test, and family co-install
   check before committing the fixture.

SASHIMI-S currently keeps its 27-array expected sums in the migration test, so
it uses `tests/golden/sidm_small_catalog_provenance.json` as the sidecar. This
keeps the compact numerical regression readable while giving it the same
provenance and regeneration contract as the JSON catalog fixtures.
