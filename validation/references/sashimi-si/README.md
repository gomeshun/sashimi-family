# Independent SIDM references

A is the corrected historical SI source at `e17d3664dac677b604fd4ff02fb2af105a6937fa`.
It does not restore the older, scientifically incorrect SI formulae. The JSON
configurations freeze dependencies, model inputs and source revision. Each
fixture sidecar records its archive, configuration, patches and worker hashes.
The reference worker rejects imports from ITAMAE and the current product.

The small catalog has 16 nodes. The formation-boundary case has 168 nodes,
164 valid accretions and four nodes not yet formed at accretion. Old A has NaN
SIDM accreted-core values at those four zero-weight nodes. Those NaNs are
preserved as historical evidence; the product emits zeros plus an explicit
`valid_accretion` flag and never evolves a reversed SIDM time history.

| B patch | Independent check | Effect and decision |
| --- | --- | --- |
| 01 exact NFW inverse | Principal Lambert-W expression at 50 decimal digits | Only truncation concentration changes in this catalog (old interpolation difference about 2.23e-5); masks here remain identical |
| 02 stable branch | Evaluate exponential only below the original asymptotic threshold | Arrays unchanged; avoid warnings from discarded exponential branches |
| 03 active EPS domain | Evaluate Yang Phi only for mmax > ma | Arrays unchanged, including reference NaNs outside formation; active nonfinite results are errors |
| 04 accurate effective cross section | Original closed expression at 65 decimal digits | Product uses an independently equivalent positive integral; preserves physical prescription and original large-a asymptotic branch |

Single-patch configurations isolate numerical effects. `B-all` combines 01/02;
`B-domain-formation` also includes 03; `B-accurate` and
`B-accurate-formation` include 04. Earlier fixtures remain separate artifacts.
`C-58701d5-*` and `C-6ccb3e6-*` identify exact clean product revisions and exact
ITAMAE inputs. Final release-candidate regeneration is a separate gate.

The effective-cross-section expression suffers subtraction cancellation.
`effective-cross-section-accuracy.json` compares its defining positive integral
at 16/32/64/128 quadrature orders against 65-digit arithmetic over 51 points
20 <= a <= 703: maximum relative discrepancy 4.45e-16. In the single-patch
catalog, CDM quantities, both weights, masks, growth and variance probes are
unchanged; the largest SIDM density, core-radius and collapse-ratio effects are
3.43e-12, 1.87e-11 and 4.37e-11. The original 5e-12 B/C tolerance is retained.
Product tests include an independent high-precision cross-section fixture.

The new primary paired catalog preserves node identity and base weights;
SIDM weights require the original formation gate, CDM truncation gate and its
additional profile gate. Previously the shared executor omitted the first two
SIDM gates. New protection cases failed before repair and pass afterward.

A separate discrepancy in the public **total** cross section remains awaiting
user selection: the historical squared denominator differs from the angular
integral and Yang & Yu (2022). No adoption decision is inferred from the
absence of an answer. This does not affect the effective/viscosity cross section
used in the catalog. See SI's detailed physical review and the pending decision.

Reproduce with `scripts/run_reference.py --repository sashimi-si --config
validation/references/sashimi-si/B-accurate.json --python <pinned-reference-python>
--output <directory>` from the family checkout. Product C uses
`scripts/product_worker.py`; its config demands clean, exact source revisions.
