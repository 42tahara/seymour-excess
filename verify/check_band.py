#!/usr/bin/env python3
"""Check the upper bounds in the band 18 <= n <= 23, where the family G_n of
Theorem 2.6 does not reach.

Run from the repository root:  python3 verify/check_band.py
                               python3 verify/check_band.py --full   (~90 s)

The default run is witness-based and takes under a second: it scores the
stored graphs in data/band/ with verify/verify_ssnc.py and confirms

    E_{>=8}(20) <= 5,  E_{>=8}(21) <= 6,  E_{>=8}(22) <= 6,  E_{>=8}(23) <= 6,

each witness being an oriented, strongly connected graph of minimum out-degree
at least 8.  That is the whole of what the bounds rest on: four explicit
graphs, scored by an implementation that shares no code with the one that
built them.

--full additionally re-runs the exhaustive sweep of the capped-tournament
blow-up family over 18 <= n <= 23, which is a strictly stronger statement:
that 5, 6, 6, 6 are the MINIMA over that family, and that the family is EMPTY
at n = 18 and n = 19.  The bounds above do not depend on it.

Why this file exists.  Version 2.0 of the note described this band as having
"no construction", which was true of the family G_n -- it needs n >= 24 -- and
false of the blow-up family, whose smallest member has n = 20.  The claim was
written before the smallest member was known and was not revisited afterwards.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, 'verify')
from verify_ssnc import to_matrix, verify  # noqa: E402

EXPECT = {20: 5, 21: 6, 22: 6, 23: 6}
EMPTY = (18, 19)
DIR = 'data/band'

ap = argparse.ArgumentParser()
ap.add_argument('--full', action='store_true',
                help='also re-run the exhaustive family sweep over 18..23')
a = ap.parse_args()

found = {}
for path in sorted(glob.glob(os.path.join(DIR, '*.json'))):
    n = int(re.match(r'n(\d+)_', os.path.basename(path)).group(1))
    obj = json.load(open(path))
    r = verify(to_matrix(obj))
    if r['n'] != n:
        sys.exit(f"FAIL: {path} has {r['n']} vertices, not {n}")
    if n in found:
        sys.exit(f"FAIL: two stored witnesses for n={n}")
    if not r['strongly_connected']:
        sys.exit(f"FAIL: {path} is not strongly connected")
    if r['min_out_degree'] < 8:
        sys.exit(f"FAIL: {path} has min out-degree {r['min_out_degree']} < 8")
    found[n] = r
    print(f"  n={n}: excess {r['excess']}, min out-degree {r['min_out_degree']}, "
          f"strongly connected")

if sorted(found) != sorted(EXPECT):
    sys.exit(f"FAIL: witnesses present for {sorted(found)}, expected "
             f"{sorted(EXPECT)}")
off = {n: (found[n]['excess'], EXPECT[n]) for n in EXPECT
       if found[n]['excess'] != EXPECT[n]}
if off:
    sys.exit(f"FAIL: excess differs from the published bound: {off}")
print("upper bounds 5, 6, 6, 6 at n = 20, 21, 22, 23: confirmed from the "
      "stored graphs")

if not a.full:
    print("(run with --full to re-derive that these are the family minima "
          "and that n = 18, 19 admit no member)")
    sys.exit(0)

out = subprocess.run(
    [sys.executable, 'blowup/blowup_sweep.py', '--sweep', '--lo', '18',
     '--hi', '23', '--mmax', '6', '--include', 'all', '--out', os.devnull],
    capture_output=True, text=True)
if out.returncode != 0:
    sys.exit("FAIL: the family sweep did not run\n" + out.stderr[-2000:])
print(out.stdout.rstrip())

sweep = {}
for line in out.stdout.splitlines():
    m = re.match(r'\s*n=\s*(\d+)\s+min excess\s+(\S+)', line)
    if m:
        sweep[int(m.group(1))] = (None if m.group(2) == 'None'
                                  else int(m.group(2)))
bad = []
for n in EMPTY:
    if sweep.get(n, 'missing') is not None:
        bad.append(f"n={n} should admit no member, sweep says {sweep.get(n)}")
for n, e in EXPECT.items():
    if sweep.get(n) != e:
        bad.append(f"n={n} minimum should be {e}, sweep says {sweep.get(n)}")
if bad:
    sys.exit("FAIL: " + "; ".join(bad))
print("family minima 5, 6, 6, 6 at n = 20..23, and no member at n = 18, 19: "
      "confirmed by the exhaustive sweep")
