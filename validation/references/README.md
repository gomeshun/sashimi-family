# Independent references for migration

These are immutable numerical comparison inputs, not a second compatibility
manifest. `compatibility.toml` records the family candidate. No product imports
these references and they are not runtime dependencies of distribution wheels.

| Variant | Frozen A | Why this version | Reference environment |
| --- | --- | --- | --- |
| C | `9f6713b686805645da459e99522e2049e7dea793` | Existing documented historical catalog anchor; `pert2_shanks`, `ct_th=0` | Python 3.11.15, NumPy 1.26.4, SciPy 1.13.1 |
| SI | `e17d3664dac677b604fd4ff02fb2af105a6937fa` | Corrected SIDM equations, not the known erroneous pre-fix model | Python 3.11.15, NumPy 1.26.4, SciPy 1.13.1 |
| W | `99dfc3632eec0126080c0273ddf78f84fe09216c` | Historical WMAP7 WDM implementation, preserving signed weights | Python 3.10.20, NumPy 1.22.4, SciPy 1.10.1 |

F's reference and input-table records are maintained in its private repository
under `validation/references`. Its frozen source includes the user-computed
CAMB table; the export and the table content are verified before execution.
Private source, patches and data must remain there until separately authorized
publication.

Each `A.json` fixes constructor parameters, grids, redshifts, numerical method,
probe arguments, complete reference dependency versions and input-file hashes.
`requirements.txt` can recreate the environment. W needs its historical NumPy
because `np.alen` was removed; attempting NumPy 1.26 and 1.23 failed before any
W output was accepted. Product support remains Python 3.11–3.13.

## Running a reference

Create an environment with the Python patch version in its configuration and
install its exact requirements. For example, from the family checkout:

```sh
uv --cache-dir /tmp/uv-cache venv /tmp/sashimi-c-reference --python 3.11.15
uv --cache-dir /tmp/uv-cache pip install --python /tmp/sashimi-c-reference/bin/python \
  -r validation/references/sashimi-c/requirements.txt
python3 scripts/run_reference.py --repository sashimi-c \
  --config validation/references/sashimi-c/A.json \
  --python /tmp/sashimi-c-reference/bin/python --output /tmp/c-A.npz
```

The controller exports the exact Git object to a temporary directory. It applies
only the B configuration's hash-verified patches, checks input data hashes, and
runs the historical code with `-I` in a separate process using the supplied
interpreter. The worker rejects A/B execution that imports ITAMAE. It records
source/module/export/config/worker/patch/data hashes, actual dependencies,
parameters, warnings, array shapes/nonfinite counts and output artifact hashes.
The changing source checkout is not the numerical reference.

Product comparisons use `scripts/product_worker.py` in a different environment
and process, with explicit clean product/core revisions in a C configuration.
This is development evidence; final wheel and sdist evidence is separate.

## Preservation and interpretation

Do not overwrite a stored fixture's generating revision or relabel a legacy
calculation with the new specification. Revalidation gets a separate report and
records the new product revision. Tuple arrays preserve original ordering and
units. Historical warnings and signed weights remain visible in A; a finite
output does not establish scientific validity. Default/mode changes require
their own comparison and decision record.

The initial exports and all accepted A runs completed on 2026-09-10. These small
fixtures are inputs to the larger scientific validation, not evidence that
convergence, all observables or release artifacts have already passed.
