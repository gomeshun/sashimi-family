# Literature citation audit: family — started 2026-10-14 UTC

Inventoried **96 active definitions**, including inherited/moved functions, private/nested helpers, constructors and tests. Updated **5 docstrings**, of which **5** receive or complete local paper references. The remaining edits clarify units, assumptions or NumPy structure.

The executable baseline before this citation edit is `e8fc3f5b038c8366a2e6ef99b269f3cf42fbe7f2`. Comparison baseline: family support scripts; no author-upstream baseline. Moving a definition does not make it new; this citation pass also includes inherited definitions.

The audit screens numerical literals and existing attributions, then matches adopted values to primary equations/tables. Generic algorithms, numerical controls, unit conversions and frozen regression outputs do not receive invented physical calibrations. The full [definition index and hash evidence](literature-citation-audit-20261014.json) distinguish edited definitions, unchanged references and archived evidence. An inventory entry is not proof of physical calibration.

## Findings and limits

- Active WMAP7/CLASS helpers cite Viel, Vogel, Planck, Fixsen and Mangano where they adopt numerical parameters. Initial A_s is a normalization starting value; matching the CDM sigma8 target is explicit.
- The cosmology controls do not reconstruct undocumented original CAMB settings. Vogel coefficients in the comparison remain an external alternative curve, not an adopted production change.
- The compatibility manifest and all five gitlinks retain the recorded family set. These independent candidate documentation edits do not promote a mixed family.

## Verification

- All 5 changed docstrings parse as NumPy style, cover explicit arguments and contain their assigned paper identifiers.
- All 42 inventoried tracked Python files have identical executable ASTs after removing only docstrings; assertions, tolerances and equations are unchanged. 18 historical Python files remain byte-identical.
- 14 distinct existing local pytest cases pass on Python 3.11.15. This is source-checkout testing, not a new scientific catalogue or a new calibration.
- Eight additional unittest subtests pass. The recorded compatibility manifest and gitlinks are unchanged.
- Historical numerical results keep their original calculation revisions. The docstring edit changes source bytes and build identity; executable equivalence does not permit relabeling old outputs. No tests are deleted or weakened.

## Changed definitions and paper mapping

| Definition | References / change |
| --- | --- |
| [`published_fits`](../scripts/analyze_wmap7_class_validation.py#L25) | [viel](https://arxiv.org/abs/astro-ph/0501562), [vogel](https://arxiv.org/abs/2210.10753) |
| [`published_fits.q`](../scripts/analyze_wmap7_class_validation.py#L63) | [viel](https://arxiv.org/abs/astro-ph/0501562), [vogel](https://arxiv.org/abs/2210.10753) |
| [`main`](../scripts/check_population_convergence.py#L19) | [survival](https://arxiv.org/abs/astro-ph/0203004), [structure](https://arxiv.org/abs/1803.07691) |
| [`main`](../scripts/plot_wmap7_class_validation.py#L17) | [viel](https://arxiv.org/abs/astro-ph/0501562), [vogel](https://arxiv.org/abs/2210.10753), [wmap](https://arxiv.org/abs/1001.4538) |
| [`Runner.__init__`](../scripts/run_wmap7_class_validation.py#L59) | [planck](https://arxiv.org/abs/1807.06209), [cmb](https://arxiv.org/abs/0911.1955), [neutrinos](https://arxiv.org/abs/hep-ph/0506164), [wmap](https://arxiv.org/abs/1001.4538) |

## Bibliography

- **cmb**: [Fixsen (2009), The Temperature of the Cosmic Microwave Background.](https://arxiv.org/abs/0911.1955)
- **neutrinos**: [Mangano et al. (2005), Relic neutrino decoupling including flavour oscillations.](https://arxiv.org/abs/hep-ph/0506164)
- **planck**: [Planck Collaboration (2020), Planck 2018 results. VI. Cosmological parameters, Table 2.](https://arxiv.org/abs/1807.06209)
- **structure**: [Hiroshima, Ando & Ishiyama (2018), Modeling evolution of dark matter substructure and annihilation boost, Section II, Eqs. (5)-(9).](https://arxiv.org/abs/1803.07691)
- **survival**: [Hayashi et al. (2003), The Structural Evolution of Substructure.](https://arxiv.org/abs/astro-ph/0203004)
- **viel**: [Viel et al. (2005), Constraining warm dark matter candidates including sterile neutrinos and light gravitinos with WMAP and the Lyman-alpha forest, Eqs. (6)-(7).](https://arxiv.org/abs/astro-ph/0501562)
- **vogel**: [Vogel & Abazajian (2023), Entering the Era of Measuring Sub-Galactic Dark Matter Structure: Accurate Transfer Functions for Axino, Gravitino & Sterile Neutrino Thermal Warm Dark Matter, Eqs. (7)-(9), Table II (v2).](https://arxiv.org/abs/2210.10753)
- **wmap**: [Komatsu et al. (2011), Seven-Year Wilkinson Microwave Anisotropy Probe Observations: Cosmological Interpretation.](https://arxiv.org/abs/1001.4538)
