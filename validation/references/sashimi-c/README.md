# C: isolated constants and NFW-inversion comparisons

`A.json` runs the frozen C version without modifications. Both B patches are
small edits to that source and import no current product or ITAMAE code:

1. `01-backend-gravity`: replace the rounded cgs conversion with
   `G=4.30091e-9 Mpc (km/s)^2 / Msun`. Keep the fixed background, host-history,
   EPS and concentration parameters unchanged. Critical density follows
   `rho_crit=3 H^2/(8 pi G)` in the same internal units.
2. `02-nfw-analytic-inverse`: invert `f(c)=ln(1+c)-c/(1+c)` with the analytic
   relation `c=-1/W_0(-exp(-1-f))-1`, evaluated with mpmath at 50-digit precision.
   Derivation: set `u=1/(1+c)`; then `u exp(-u)=exp(-1-f)` with `0<u<=1`,
   which selects the principal branch. This is independent of the product's
   Brent root finder. It changes no mass or profile prescription.

Run `B-gravity.json`, `B-inverse.json` and `B-all.json` independently. Each uses
the same A source and numerical/environment inputs. Gravity and inverse patches
are also jointly applied for the product comparison.

## Recorded small-catalog result

The 1,280-node grid uses the existing reference's 32 masses, eight redshifts,
five concentration nodes, host-scatter order 16, `pert2_shanks` and `ct_th=0`.
No fixture tolerance was widened and no existing product golden was overwritten.

| Comparison | Maximum relative effect |
| --- | ---: |
| A → B gravity: scale radii | 1.079815e-4 |
| A → B gravity: scale densities | 3.238745e-4 |
| A → B gravity: mass/weight | 0 |
| A → B inverse: truncation concentration | 1.021292e-4 |
| A → B inverse: mass/weight/profile scales | 0 |
| B all → C: truncation concentration | 5.762170e-14 |
| B all → C: weight | 2.161158e-15 |

The product record `C-988b9f6` uses C
`988b9f69f522ded9a644bd20a0746461e5638b27` with core
`970cda1bdf6f556993f07f4c1b6bcac02323dd9d`, a separate clean-source process,
NumPy 2.4.6 and SciPy 1.17.1. See the sidecars and
`fixtures/ablation-metrics-20260910.json` for every column and probe. Subsequent
product revisions must be recorded separately.

All survival masks on this `ct_th=0` grid agree. That does not test arbitrary
survival-boundary sensitivity. Threshold, observables and grid/solver
convergence checks remain to be added before the scientific review is complete.

Failed reference attempt: the first analytic-inverse patch selected `W_-1`.
It produced negative concentrations and disagreed strongly with both A and C.
The domain `c>=0` identifies that as an algebraic error; it was rejected and
replaced with the principal-branch, high-precision patch. No product equation
or tolerance was changed to accommodate that failed attempt.

`B-all-worker-v2` is a separate revalidation after formatting the reference
worker. Every output array is bitwise identical to the initial `B-all`; its
sidecar records the committed worker's exact current hash. C's standard-API
fixture uses this revalidation. The original record is retained unchanged.
