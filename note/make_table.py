#!/usr/bin/env python3
"""Generate the full measurement table (§3.1) from data/ — never by hand.

Columns: n | constructive bound (source) | fresh-search attainment |
best overall (witness graph-sha1 prefix) | date.

Usage: python3 make_table.py [--tex]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'constructions'))
from power_ring import unified_bound  # noqa: E402

DATE = "2026-07-22"
TRANSPLANT = {47: 5, 53: 5, 59: 5}          # keystone transplants (data/transplant_n*.json)
TRANSPLANT_FAMILY_57 = 4                    # not a bound record (ring gives 3)

sweep = json.load(open(os.path.join(ROOT, 'data', 'en_sweep.json')))
manifest = json.load(open(os.path.join(ROOT, 'data', 'manifest.json')))

search = {}                                  # n -> (value, witness file or None, note)
for r in sweep['rows']:
    n = r['n']
    if n not in search or r['best_excess'] < search[n][0]:
        search[n] = (r['best_excess'], r.get('source', ''), '')
controls = {p['n']: p['best_excess'] for p in sweep.get('fresh_only_controls', {}).get('points', [])}

WITNESS_FILE = {
    25: 'gkz_ring_n25_m5k2.json', 27: 'pure_ring_n27_m3.json',
    35: 'gkz_ring_n35_m5k2.json', 47: 'transplant_n47.json',
    48: 'pure_ring_n48_m3.json', 49: 'champion_n49_ad5efc8b.json',
    50: 'champion_28da4a1e.json', 51: 'pure_ring_n51_m3.json',
    53: 'champion_n53_ca40b396.json', 57: 'transplant_n57.json',
    59: 'transplant_n59.json',
}

NS = sorted(set(list(search) + [27, 47, 48, 51, 53, 57, 59]))
rows = []
for n in NS:
    ub = unified_bound(n)
    cons = None
    via = ''
    if ub and ub[0] < n:                      # exclude the trivial t=1 witness
        cons = ub[0]
        via = f"ring m={ub[0]},k={ub[1]},t={ub[2]}"
    if n in TRANSPLANT and (cons is None or TRANSPLANT[n] < cons):
        cons = TRANSPLANT[n]
        via = 'keystone transplant'
    s = search.get(n)
    sval = s[0] if s else None
    ctrl = controls.get(n)
    best = min(x for x in (cons, sval) if x is not None)
    wf = WITNESS_FILE.get(n)
    sha = manifest.get(wf, '')[:8] if wf else ''
    if sval is None:
        srch = f"{ctrl} (seed-free)" if ctrl is not None else '-'
    else:
        srch = f"{sval}" + (f" ({ctrl} seed-free)" if ctrl is not None else "")
    rows.append((n, f"{cons if cons is not None else '-'} ({via})" if via else '-',
                 srch, f"{best}", sha or '(theorem)'))

if '--tex' in sys.argv:
    print(r"\begin{tabular}{rllll}")
    print(r"$n$ & construction & search & best & witness \\ \hline")
    for n, c, s, b, w in rows:
        w = w.replace('(theorem)', r'\emph{(thm)}')
        print(f"{n} & {c} & {s} & {b} & \\texttt{{{w}}} \\\\")
    print(r"\end{tabular}")
else:
    print("| n | construction bound | fresh-search attainment | best | witness (graph sha1) |")
    print("|---|---|---|---|---|")
    for n, c, s, b, w in rows:
        print(f"| {n} | {c} | {s} | {b} | `{w}` |")
    print(f"\nAll witnesses (re)verified {DATE}; hashes are canonical adjacency sha1 "
          "(see verify/check_hashes.py). n=57: transplant family also realises 4 "
          "(all survivors tight), not a bound record.")
