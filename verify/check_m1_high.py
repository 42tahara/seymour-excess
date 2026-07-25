#!/usr/bin/env python3
"""Check the claim of the note, section 5.2, that above the surveyed band the
search falls short of the construction at some orders but never beats it.

Run from the repository root:  python3 verify/check_m1_high.py

The claim, stated there and in the README, is about the 50 orders
101 <= n <= 150: the best stored witness matches 3 + [3 nmid n] at 40 of them
and stands ABOVE it at 10, attaining 5 or 6 against a construction value of 4,
the largest excess over the construction being +2.

Every number in that sentence is re-derived here from the stored adjacency
lists, scored by verify/verify_ssnc.py, which shares no code with the search
that produced them.  Nothing below is read from a witness file's own recorded
score.

This direction of the claim is the informative one: it is a statement that
SEARCH FELL SHORT.  A witness BELOW the construction value would be a genuine
surprise -- it would beat the theorem's bound -- so that case fails loudly
rather than being folded into a count.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, 'verify')
from verify_ssnc import to_matrix, verify  # noqa: E402

LO, HI = 101, 150
DIR = 'data/sonar_high'


def theorem(n):
    return 3 + (0 if n % 3 == 0 else 1)


measured = {}
for path in sorted(glob.glob(os.path.join(DIR, '*.json'))):
    n = int(re.match(r'n(\d+)_', os.path.basename(path)).group(1))
    r = verify(to_matrix(json.load(open(path))))
    if r['n'] != n:
        sys.exit(f"FAIL: {path} has {r['n']} vertices, not {n}")
    if n in measured:
        sys.exit(f"FAIL: two stored witnesses for n={n}")
    measured[n] = r

gaps = [n for n in range(LO, HI + 1) if n not in measured]
if gaps:
    sys.exit(f"FAIL: orders missing from {DIR}: {gaps}")
extra = [n for n in measured if not LO <= n <= HI]
if extra:
    sys.exit(f"FAIL: orders outside {LO}..{HI} in {DIR}: {sorted(extra)}")

bad = [n for n, r in measured.items()
       if r['min_out_degree'] < 8 or not r['strongly_connected']]
if bad:
    sys.exit(f"FAIL: inadmissible stored witnesses (degree or connectivity): {bad}")

below = sorted(n for n, r in measured.items() if r['excess'] < theorem(n))
if below:
    sys.exit("FAIL: a stored witness beats the construction value, which would "
             f"be a new bound rather than a shortfall: {below}")

at = sorted(n for n, r in measured.items() if r['excess'] == theorem(n))
above = sorted(n for n, r in measured.items() if r['excess'] > theorem(n))
gap = max((measured[n]['excess'] - theorem(n)) for n in above) if above else 0
vals = sorted({measured[n]['excess'] for n in above})

print(f"orders {LO}..{HI}: {len(measured)} stored witnesses, no gaps")
print(f"  match 3+[3 nmid n]: {len(at)}")
print(f"  above it:           {len(above)} at n = {above}")
print(f"  values attained above: {vals}; largest excess over construction: +{gap}")
print(f"  below it:           0")

expect = (len(measured) == 50 and len(at) == 40 and len(above) == 10
          and vals == [5, 6] and gap == 2)
print(f"matches the sentence in note section 5.2 (50 = 40 + 10, values 5 or 6, "
      f"max +2): {expect}")
sys.exit(0 if expect else 1)
