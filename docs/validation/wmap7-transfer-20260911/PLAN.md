# WMAP7 thermal-WDM transfer comparison — frozen before execution

This follow-up tests the published Viel (2005) and Vogel & Abazajian (2023)
thermal-WDM fits against independent CLASS calculations at the cosmology stored
in the current SASHIMI-W input table. No coefficient is fitted to these results.
The earlier Planck-like calculation remains a separate, immutable reference.

## Inputs and controls

- Read `Omega_b=0.0469`, `Omega_m=0.27`, `h=0.7`, `n_s=0.95`, and
  `sigma8=0.82` from the existing SASHIMI-W table. These imply
  `omega_b=0.022981` and `omega_dm=0.109319`.
- Flat cosmology; massless active neutrinos with `N_ur=3.046`,
  `T_cmb=2.7255`, `tau_reio=0.0544`, as in the earlier CLASS control.
  Radiation/reionization settings are not recorded in the SASHIMI table header;
  this does not claim to reproduce every original CAMB setting or its table.
- CLASS v3.3.4, source `e85808324f51fc694d12e3ed7439552a3c3f9540`.
  Record executable hash, source manifest, Python environment, and input hashes.
- Determine a common primordial amplitude from a CDM-only pilot targeting
  `sigma8=0.82`. Apply this exact amplitude to CDM and all WDM spectra.
  Never normalize WDM separately to the CDM sigma8.
- Pure thermal Fermi–Dirac WDM, two internal states, zero chemical potential.
  Determine each temperature from the desired present density, verifying the
  final density against CLASS's background output.

## Fixed comparison

- Masses: 1, 2, 5 keV. Start with 2 keV; 1 keV is outside Vogel's calibrated
  mass range and cannot establish its superiority there.
- Redshifts: 0 and 99. Comparison domain: 0.01–80 h/Mpc without extrapolation.
- Compare `Q=P_WDM/P_CDM` to each published **squared** transfer amplitude.
  Both analytic fits receive the same h and dark-matter density as CLASS.
- Primary diagnostics: maximum absolute Q error where CLASS has
  `0.05 <= Q <= 0.95`, and fractional error of the `Q=0.5` crossing.
  Also report each fit evaluated at CLASS's `Q=0.5` crossing.
  State when the finite k domain does not cover the full transition.
- Keep the historical q5 only as a labeled diagnostic, not as an adoption option.
- Preserve the earlier Planck-like summaries for comparison of cosmologies;
  do not mix a WMAP7 fit with the earlier CLASS spectra.

## Numerical check

Repeat the 2 keV CDM/WDM pair with `tol_ncdm_synchronous=1e-5`,
`l_max_ncdm=40`, `k_per_decade_for_pk=60`, and perturbation tolerance `2e-7`.
The baseline uses `1e-4`, 24, 30, and `1e-6`, respectively. Both disable the
ncdm fluid approximation (`ncdm_fluid_approximation=3`).
Require maximum absolute Q change below 0.001 and fractional power-half
crossing change below 0.001 before interpreting differences at the percent level.
This is a numerical check at a representative mass, not an error bound at all
masses. Refine another mass only if an observed concern warrants doing so.

## Scope of the decision

This establishes local accuracy of the analytic linear-power approximations.
It does not validate nonlinear subhalo counts, halo-model calibration, a general
cosmology dependence, or observational mass limits. Product coefficients and
completed release artifacts remain identified by their original revisions.

References: Viel et al. (2005), Eqs. (4), (6), (7),
https://arxiv.org/abs/astro-ph/0501562;
Vogel & Abazajian (2023), Eqs. (7)–(9), Table II,
https://arxiv.org/abs/2210.10753, DOI 10.1103/PhysRevD.108.043520.
