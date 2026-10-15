# Actual-paper citation verification: family

Audit date: 2026-10-15 (JST). This supersedes the equation-attribution conclusions of the 2026-10-14 citation index; the old index remains a historical snapshot.

Inspected source revision: `1327482cbdade795176251a73a37cd43a77c7d05`. All cited definitions include private helpers, nested functions and tests. A moved function is traced through its retained qualified name; a move does not imply a new physical prescription.

Comparison baseline: `none` at `not applicable` (family integration support).

Coverage: 5 definitions, 13 original reference occurrences; 13 after correction. 8 reference keys / 8 unique papers. Every original occurrence has a reviewed source comparison, including citations removed as inapplicable.

The linked full texts were actually opened and the claimed equations, coefficients or contextual values inspected. Publisher landing-page reachability is separate from full-text access. Equation existence is separate from algebraic derivation, implementation adaptation and physical validation. PDF page numbers refer to the inspected version, not necessarily printed page numbers.

Categories: `printed` = applicable relation/value appears in the paper; `derived` = a documented algebraic/numerical consequence; `adopted` = reuse with explicit assumptions; `adapted` = an implementation convention or coefficient set differs; `context` = source supplies background rather than an equation; `unresolved` = the exact attribution is not established. Counts are citation uses, not counts of independent physical validations.

adopted: 5, derived: 3, printed: 3, unresolved: 2

## Source comparisons

| Key | Primary full text and inspected location | Result |
|---|---|---|
| planck | [Planck Collaboration (2020), Planck 2018 results. VI. Cosmological parameters, Table 2.](https://arxiv.org/pdf/1807.06209) — 1807.06209v4 [astro-ph.CO] 9 Aug 2021; Table 2, p.16 (TT,TE,EE+lowE+lensing column) | **adopted**. H0=67.36, Omega_m=0.3153, omega_b=0.02237, tau=0.0544 and A_s=2.100e-9 support the rounded native/control inputs. Omega_b is obtained by dividing omega_b by h^2. The Colossus planck18 preset selects a different data combination; its name does not make it identical to the native parameter vector. |
| wmap | [Komatsu et al. (2011), Seven-Year Wilkinson Microwave Anisotropy Probe Observations: Cosmological Interpretation.](https://arxiv.org/pdf/1001.4538) — 1001.4538v3 [astro-ph.CO] 9 Nov 2010; Table 1, p.3 | **unresolved**. The paper is real and reachable, but the input header (Omega_b=0.0469, Omega_m=0.27, h=0.7, n_s=0.95, sigma8=0.82) is not a literal Table 1 column. In particular 0.0469 and 0.95 are absent as the cited best-fit values. The WMAP7 label is contextual; exact table-generation parameters are not established by this citation. |
| structure | [Hiroshima, Ando & Ishiyama (2018), Modeling evolution of dark matter substructure and annihilation boost, Section II, Eqs. (5)-(9).](https://arxiv.org/pdf/1803.07691) — 1803.07691v2 [astro-ph.CO] 23 May 2018; Section II, pp.2-3; Eqs. (4)-(9), (28), (34) | **adopted**. The paper gives the concentration prescription, NFW speed/radius conversion and tidal structural response. Section II adopts scatter 0.13 dex; the disruption discussion and later selection factors use r_t/r_s=0.77. C/SI defaults allowing zero cutoff and all public 0.128-dex scatter defaults are explicit implementation choices, not literal copies of every population setting. |
| survival | [Hayashi et al. (2003), The Structural Evolution of Substructure.](https://arxiv.org/pdf/astro-ph/0203004) — astro-ph/0203004v2 6 Dec 2002; Section 2.1, p.3 | **adopted**. The approximately 0.77*r_s bound concerns instantaneously truncated isotropic NFW systems. Adopting it as a subhalo survival selection follows the later Hiroshima prescription; it is not a universal empirical disruption threshold. Tests at the exact boundary establish mask and inversion behavior only. |
| viel | [Viel et al. (2005), Constraining warm dark matter candidates including sterile neutrinos and light gravitinos with WMAP and the Lyman-alpha forest, Eqs. (6)-(7).](https://arxiv.org/pdf/astro-ph/0501562) — astro-ph/0501562v2 1 Apr 2005; Eqs. (6)-(7), p.3 | **derived**. The amplitude T=[1+(alpha*k)^(2*nu)]^(-5/nu), nu=1.12 and alpha=0.049*(m/keV)^-1.11*(Omega_WDM/0.25)^0.11*(h/0.7)^1.22 h^-1 Mpc are printed. The power ratio has exponent -10/nu by squaring. The paper states k<5 h/Mpc for this fit. A q5 power control is historical and does not reproduce the squared transfer law. |
| vogel | [Vogel & Abazajian (2023), Entering the Era of Measuring Sub-Galactic Dark Matter Structure: Accurate Transfer Functions for Axino, Gravitino & Sterile Neutrino Thermal Warm Dark Matter, Eqs. (7)-(9), Table II (v2).](https://arxiv.org/pdf/2210.10753) — 2210.10753v2 [hep-ph] 12 Apr 2023; Eqs. (7)-(9), pp.3-5; Table II, p.6 (v2) | **printed**. The amplitude definition, scale fit and spin-1/2 values a=0.0437, b=-1.188, nu=1.049, theta=2.012, eta=0.2463 are printed. Calibration uses 2,5,10,20,100 keV; the 1-keV comparison is extrapolation. The code correctly squares the amplitude for a power ratio. |
| cmb | [Fixsen (2009), The Temperature of the Cosmic Microwave Background.](https://arxiv.org/pdf/0911.1955) — 0911.1955v2 [astro-ph.CO] 10 Nov 2009; Abstract, p.1 | **adopted**. The measured temperature is 2.72548 +/- 0.00057 K. The control input 2.7255 K is a rounded value. This supports the temperature choice only, not the recovery of every original CAMB setting. |
| neutrinos | [Mangano et al. (2005), Relic neutrino decoupling including flavour oscillations.](https://arxiv.org/pdf/hep-ph/0506164) — hep-ph/0506164v1 16 Jun 2005; Abstract, p.1 | **adopted**. The paper reports N_eff=3.046 from non-instantaneous neutrino decoupling. The control puts that value into a massless-radiation setting. The all-massless treatment is a separate modelling choice, not a conclusion about neutrino masses in the cited paper. |

The companion JSON records URL status, UTC retrieval time and the SHA-256 of each full-text file. Original identifiers were retained where an alternative full-text link was added. No third-party paper files are redistributed with this report.

## Definition coverage

| Definition at inspected revision | Original baseline definition | References before → after | Classification after correction |
|---|---|---|---|
| [scripts/analyze_wmap7_class_validation.py::published_fits](https://github.com/gomeshun/sashimi-family/blob/1327482cbdade795176251a73a37cd43a77c7d05/scripts/analyze_wmap7_class_validation.py#L25) | family integration support | viel, vogel | viel: derived; vogel: printed |
| [scripts/analyze_wmap7_class_validation.py::published_fits.q](https://github.com/gomeshun/sashimi-family/blob/1327482cbdade795176251a73a37cd43a77c7d05/scripts/analyze_wmap7_class_validation.py#L63) | family integration support | viel, vogel | viel: derived; vogel: printed |
| [scripts/check_population_convergence.py::main](https://github.com/gomeshun/sashimi-family/blob/1327482cbdade795176251a73a37cd43a77c7d05/scripts/check_population_convergence.py#L19) | family integration support | survival, structure | survival: adopted; structure: adopted |
| [scripts/plot_wmap7_class_validation.py::main](https://github.com/gomeshun/sashimi-family/blob/1327482cbdade795176251a73a37cd43a77c7d05/scripts/plot_wmap7_class_validation.py#L17) | family integration support | viel, vogel, wmap | viel: derived; vogel: printed; wmap: unresolved |
| [scripts/run_wmap7_class_validation.py::Runner.__init__](https://github.com/gomeshun/sashimi-family/blob/1327482cbdade795176251a73a37cd43a77c7d05/scripts/run_wmap7_class_validation.py#L59) | family integration support | planck, cmb, neutrinos, wmap | planck: adopted; cmb: adopted; neutrinos: adopted; wmap: unresolved |

## Source and validation boundaries

Compared all 42 tracked Python files in this checkout after stripping only leading docstrings: executable syntax is unchanged. All 18 sealed historical Python files are byte-identical. No model coefficients, numerical controls, assertions or tolerances were altered.

Original qualified-name links record the author/owner baseline even when the current file or containing class moved. A missing one-to-one name mapping is reported as such; it is not evidence that a physical equation is new. The companion JSON preserves baseline source-file hashes.

The retained test results from the previous citation audit belong to their recorded source revisions. They are not relabelled as new physical runs. This audit checks documentation, paper correspondence and executable-source identity; it does not establish convergence, observational calibration or validity outside the published domains. Source-file hashes can change when documentation changes, so persisted output/restart identity checks must not be bypassed.
