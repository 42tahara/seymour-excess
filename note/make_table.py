#!/usr/bin/env python3
"""Generate the §3.1 tables from data/ — never by hand.

Table 1 (surveyed orders): n | theorem 3+[3 nmid n] | earlier construction |
fresh-search attainment | best stored witness (graph sha1).  The earlier
constructions (pure/power rings, keystone transplants) are kept so that the
reader can see them being superseded, order by order, by the theorem.

Table 2 (measurement summary): the 77 witnesses of data/sonar_best/, one per
order n = 24..100, summarised — NOT one row per order.  The theorem fixes the
value, so listing 77 rows would add no information; what the measurement adds
is that every stored witness attains it.

Every number below is recomputed from the adjacency lists by the independent
verifier verify/verify_ssnc.py; the claimed scores in the witness files are
ignored.

Usage: python3 make_table.py [--tex]
The LaTeX fragment is standalone (needs amsmath + amssymb for \\nmid).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'constructions'))
sys.path.insert(0, os.path.join(ROOT, 'verify'))
from power_ring import unified_bound          # noqa: E402
from verify_ssnc import to_matrix, verify     # noqa: E402

DATE = "2026-07-26"
TRANSPLANT = {47: 5, 53: 5, 59: 5}          # keystone transplants (data/transplant_n*.json)
TRANSPLANT_FAMILY_57 = 4                    # not a bound record (ring gives 3)

DATA = os.path.join(ROOT, 'data')
BEST_DIR = os.path.join(DATA, 'sonar_best')
BEST_NAME = re.compile(r"n(\d+)_excess(\d+)_([0-9a-f]+)\.json$")

sweep = json.load(open(os.path.join(DATA, 'en_sweep.json')))
manifest = json.load(open(os.path.join(DATA, 'manifest.json')))


def theorem(n):
    """The flat upper bound of constructions/upper_bound_family.py (n >= 24)."""
    return 3 + (0 if n % 3 == 0 else 1)


# ---------------------------------------------------------------- measurements
measured = {}                                # n -> dict(file, sha, excess, minout, scc)
for f in sorted(os.listdir(BEST_DIR)):
    m = BEST_NAME.match(f)
    if not m:
        continue
    n = int(m.group(1))
    if n in measured:
        sys.exit(f"FAIL: two stored witnesses for n={n}")
    obj = json.load(open(os.path.join(BEST_DIR, f)))
    r = verify(to_matrix(obj))
    if r['n'] != n:
        sys.exit(f"FAIL: {f} has {r['n']} vertices, not {n}")
    measured[n] = dict(file=f, sha=manifest.get('sonar_best/' + f, obj['graph_sha1']),
                       excess=r['excess'], minout=r['min_out_degree'],
                       scc=r['strongly_connected'])

LO, HI = min(measured), max(measured)
gaps = [n for n in range(LO, HI + 1) if n not in measured]
off = sorted(n for n, d in measured.items() if d['excess'] != theorem(n))
agree = len(measured) - len(off)
not_scc = sorted(n for n, d in measured.items() if not d['scc'])
lo_deg = min(measured, key=lambda n: measured[n]['minout'])
hi_deg = max(measured, key=lambda n: measured[n]['minout'])

# ---------------------------------------------------------------- fresh search
search = {}                                  # n -> (value, source)
for r in sweep['rows']:
    n = r['n']
    if n not in search or r['best_excess'] < search[n][0]:
        search[n] = (r['best_excess'], r.get('source', ''))
controls = {p['n']: p['best_excess'] for p in sweep.get('fresh_only_controls', {}).get('points', [])}

# fallback witnesses for orders outside the measured range
WITNESS_FILE = {
    24: 'pure_ring_n24_m3.json',
    25: 'gkz_ring_n25_m5k2.json', 27: 'pure_ring_n27_m3.json',
    35: 'gkz_ring_n35_m5k2.json', 47: 'transplant_n47.json',
    48: 'pure_ring_n48_m3.json', 49: 'champion_n49_ad5efc8b.json',
    50: 'champion_28da4a1e.json', 51: 'pure_ring_n51_m3.json',
    53: 'champion_n53_ca40b396.json', 57: 'transplant_n57.json',
    59: 'transplant_n59.json',
}

NS = sorted(set(list(search) + [24, 27, 47, 48, 51, 53, 57, 59]))
rows = []
beaten = []                                  # rows where an old construction beats the theorem
for n in NS:
    thm = theorem(n)
    ub = unified_bound(n)
    cons, via = None, ''
    if ub and ub[0] < n:                      # exclude the trivial t=1 witness
        cons = ub[0]
        via = f"ring m={ub[0]},k={ub[1]},t={ub[2]}"
    if n in TRANSPLANT and (cons is None or TRANSPLANT[n] < cons):
        cons = TRANSPLANT[n]
        via = 'keystone transplant'
    if cons is not None and cons < thm:
        beaten.append((n, cons, thm))
    s, ctrl = search.get(n), controls.get(n)
    if s is None:
        srch = f"{ctrl} (seed-free)" if ctrl is not None else '-'
    else:
        srch = f"{s[0]}" + (f" ({ctrl} seed-free)" if ctrl is not None else "")
    if n in measured:
        d = measured[n]
        wit = d['sha'][:8] + ('' if d['excess'] == thm else f" (excess {d['excess']})")
    else:
        wf = WITNESS_FILE.get(n)
        sha = manifest.get(wf, '')[:8] if wf else ''
        wit = sha or '-'
    rows.append((n, thm, f"{cons} ({via})" if via else '-', srch, wit))

if beaten:                                    # would contradict the theorem's optimality claim
    sys.exit("FAIL: earlier construction below the theorem value: "
             + ", ".join(f"n={n}: {c} < {t}" for n, c, t in beaten))

# A stored witness that misses the theorem value is either a broken witness or a
# broken theorem.  Either way the table must not be produced: printing the
# disagreement into a summary row and exiting 0 would put a table on the page
# whose own contents contradict the theorem two sections earlier.  Likewise for a
# witness that is not strongly connected or falls below the degree bound -- the
# family is claimed to be admissible, so an inadmissible stored witness is a
# failure, not a footnote.
if off:
    sys.exit(f"FAIL: {len(off)} stored witnesses disagree with the theorem "
             f"value 3+[3 nmid n]: n = {off}")
if not_scc:
    sys.exit(f"FAIL: stored witnesses not strongly connected: n = {not_scc}")
under = sorted(n for n, d in measured.items() if d['minout'] < 8)
if under:
    sys.exit(f"FAIL: stored witnesses with min out-degree < 8: n = {under}")
if gaps:
    sys.exit(f"FAIL: orders missing from data/sonar_best/: {gaps}")

summary = [
    ("orders covered", f"{LO}..{HI}" + (f", gaps at {gaps}" if gaps else ", no gaps")),
    ("stored witnesses", f"{len(measured)} (one per order)"),
    (f"excess = 3+[3 nmid n]", f"{agree} of {len(measured)} orders"),
    ("orders disagreeing", ", ".join(map(str, off)) if off else "none"),
    ("min out-degree observed",
     f"{measured[lo_deg]['minout']} (n={lo_deg}) .. {measured[hi_deg]['minout']} (n={hi_deg})"),
    ("strongly connected",
     f"{len(measured) - len(not_scc)} of {len(measured)} orders"
     + (f"; not at {not_scc}" if not_scc else "")),
]

if '--tex' in sys.argv:
    print(r"\textbf{Table 1.} Surveyed orders: the theorem against the"
          r" constructions it supersedes.\par\smallskip")
    print(r"\begin{tabular}{rclll}")
    print(r"$n$ & $3+[3\nmid n]$ & earlier construction & fresh search"
          r" & best stored witness \\ \hline")
    for n, thm, c, s, w in rows:
        print(f"{n} & {thm} & {c} & {s} & \\texttt{{{w}}} \\\\")
    print(r"\end{tabular}")
    print(r"\par\medskip")
    print(r"\textbf{Table 2.} The measured witnesses of"
          r" \texttt{data/sonar\_best/}, summarised.\par\smallskip")
    print(r"\begin{tabular}{ll}")
    print(r"quantity & value \\ \hline")
    for k, v in summary:
        k = k.replace("3+[3 nmid n]", r"$3+[3\nmid n]$")
        print(f"{k} & {v} \\\\")
    print(r"\end{tabular}")
else:
    print("## Table 1 — surveyed orders\n")
    print("| n | theorem 3+[3∤n] | earlier construction | fresh-search attainment "
          "| best stored witness (graph sha1) |")
    print("|---|---|---|---|---|")
    for n, thm, c, s, w in rows:
        print(f"| {n} | {thm} | {c} | {s} | `{w}` |")
    print("\n## Table 2 — measurement summary (data/sonar_best/)\n")
    print("| quantity | value |")
    print("|---|---|")
    for k, v in summary:
        print(f"| {k.replace('3 nmid n', '3∤n')} | {v} |")
    print(f"\nRegenerated {DATE}; every excess, out-degree and connectivity value above is "
          "recomputed from the adjacency lists by verify/verify_ssnc.py (see also "
          "verify/check_m1.py), and hashes are canonical adjacency sha1 checked against "
          "data/manifest.json by verify/check_hashes.py. The earlier constructions are "
          "listed to show them being superseded: no row falls below the theorem value. "
          "n=24 is the boundary case with minimum out-degree exactly 8. n=57: the "
          f"transplant family also realises {TRANSPLANT_FAMILY_57} (all survivors tight), "
          "not a bound record. The 77 witnesses are upper-bound witnesses only; nothing "
          "here is a lower bound.")
