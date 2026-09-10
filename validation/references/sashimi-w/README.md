# W: independent correction ablations

Frozen A is W `99dfc3632eec0126080c0273ddf78f84fe09216c`. The six
specified background/growth/unit/grid corrections are evaluated singly against
A, then together. Signed old weights are retained exactly; negative counts are
not fed into the product catalog or removed by clipping.

After B-six, integral-only and derivative-only changes isolate the old variance
representation. B-continuous applies both. B-inverse and B-quadrature each add
one numerical correction to B-continuous. B-all-q5/q10 combine all corrections
with an explicit power exponent; q10 is a separate physical choice, not a new
default. See each hash-verified patch/config for equations and assumptions.

| Reference | Signed total weight | Negative nodes |
| --- | ---: | ---: |
| A | 0.0208759455607 | 0 |
| B-01-flat-background | 0.0200254720426 | 0 |
| B-02-normalized-growth | 0.0201851133875 | 0 |
| B-03-variance-growth-square | 0.0195720912901 | 0 |
| B-04-physical-variance-mass | 0.00938045548664 | 4 |
| B-05-physical-concentration-mass | 0.0210648750129 | 0 |
| B-06-redshift-accretion-grid | 0.0213987888274 | 0 |
| B-six | 0.0101262846445 | 4 |
| B-integral | 0.00771424576043 | 4 |
| B-derivative | 0.00495497503691 | 0 |
| B-continuous | 0.00390595000344 | 0 |
| B-inverse | 0.00390595000344 | 0 |
| B-quadrature | 0.00388924426045 | 0 |
| B-all-q5 | 0.00388924426045 | 0 |
| B-all-q10 | 2.34129322849e-06 | 0 |

The adaptive reference integrates the original tabulated spectrum on its own
3,001 knots. Product fixed-cell quadrature also resolves interpolation knots;
`check_variance.py` verifies convergence and the moving-boundary derivative
independently. Inversion uses the principal Lambert-W branch at 50 digits,
independent of the product Brent solver. The quadrature patch derives the
modern Simpson last-interval rule, isolating the historical SciPy difference.

The numerical catalog comparison C uses W
`91aabb0a8307d6a1807727f3fa8a57e4faff4238` and ITAMAE
`ceb38eaf6ee57efb43ccb60005c68c1c4cf044ac` in a separate clean-source process.
All columns agree within existing tolerances (catalog 5e-10, weight 5e-12), and
both masks agree exactly. Full differences, warnings and identities are in the
sidecars and ablation JSON. q5/q10 abundances differ materially even when the
same numerical half-mode wavenumber is reported; their metadata defines the
different amplitude/power conditions explicitly.

These 16-node catalogs isolate implementation corrections. The remaining
scientific gate includes larger resolution convergence, satellite observables
and final standard-API/artifact verification. No conclusion about updated
simulation calibration or downstream likelihood constraints follows from the
compact migration agreement alone.
