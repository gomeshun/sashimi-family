"""Audit the finite EPS normalization limit against a frozen pre-fix method."""
import argparse
import ast
import hashlib
import inspect
import json
import subprocess
import sys
import textwrap
import warnings
from pathlib import Path

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=['c', 'si', 'f'], required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    repo = root / f'sashimi-{args.variant}'
    if subprocess.check_output(['git', '-C', str(repo), 'diff', 'HEAD', '--', '*.py'], text=True):
        raise RuntimeError('Commit the implementation before scientific auditing.')
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(repo))
    if args.variant == 'c':
        from sashimi_c import SubhaloProperties
        model, filename = SubhaloProperties(), 'sashimi_c.py'
    elif args.variant == 'si':
        from sashimi_si import SubhaloProperties
        model, filename = SubhaloProperties(), 'sashimi_si.py'
    else:
        from sashimi_f import FDMSubhaloProperties
        model, filename = FDMSubhaloProperties(power_cache_dir=args.output / 'power-cache'), 'sashimi_f_physics.py'
        model.m_22 = 1.
    original = subprocess.check_output(['git', '-C', str(repo), 'show', f'{args.base}:{filename}'], text=True)
    node = next(n for n in ast.walk(ast.parse(original)) if isinstance(n, ast.FunctionDef) and n.name == 'Na_calc')
    old_method = textwrap.dedent('\n'.join(original.splitlines()[node.lineno-1:node.end_lineno])) + '\n'
    new_method = textwrap.dedent(inspect.getsource(model.Na_calc))
    (args.output / 'before-method.txt').write_text(old_method)
    (args.output / 'after-method.txt').write_text(new_method)
    namespace = dict(model.Na_calc.__func__.__globals__)
    exec(compile(old_method, '<frozen-EPS-method>', 'exec'), namespace)
    redshift = np.arange(.25, 3.25, .25)
    mass = np.geomspace(1e6, 1e10, 16)
    rows = []
    for prescription in [1, 2, 3]:
        for order in [4, 64, 200]:
            values, recorded_warnings = {}, {}
            for label, method in [('before', namespace['Na_calc']), ('after', model.Na_calc.__func__)]:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    values[label] = method(model, mass, redshift, 1e12, N_herm=order, Na_model=prescription)
                recorded_warnings[label] = [str(w.message) for w in caught]
            before, after = values['before'], values['after']
            if not np.all(np.isfinite(after)) or np.any(after < 0) or recorded_warnings['after']:
                raise AssertionError('The repaired calculation must be finite/nonnegative and warning-free.')
            npz = args.output / f'prescription-{prescription}-order-{order}.npz'
            np.savez_compressed(npz, before=before, after=after, mass=mass, redshift=redshift)
            common = (before != 0) & np.isfinite(before)
            rows.append(dict(prescription=prescription, order=order, warnings=recorded_warnings,
                             max_relative_change=float(np.max(np.abs(after[common]/before[common]-1))) if np.any(common) else None,
                             newly_nonzero_count=int(np.count_nonzero((before == 0) & (after != 0))),
                             max_absolute_change=float(np.max(np.abs(after-before))),
                             file=npz.name, sha256=digest(npz)))
    report = dict(variant=args.variant, base_revision=args.base,
                  source_revision=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
                  script_sha256=digest(Path(__file__)), before_method_sha256=digest(args.output/'before-method.txt'),
                  after_method_sha256=digest(args.output/'after-method.txt'),
                  parameters=dict(host_mass=1e12, redshifts=redshift.tolist(), masses=mass.tolist(), m22=1. if args.variant=='f' else None), rows=rows)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
