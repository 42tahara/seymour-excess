#!/usr/bin/env python3
"""Divergence gate for T7: rebuild the family G_n from its written SPECIFICATION
and score it with the public independent verifier.  No code is shared with the
construction pipeline; this file is written only from the prose below.

Run from the repository root:  python3 verify/check_t7_from_spec.py
                              python3 verify/check_t7_from_spec.py --lo 24 --hi 60

Specification (as published in the T7 claim):
  m = floor(n/3), r = n mod 3, layer sizes s_a = m + [a < r] for a = 0,1,2,
  st_a = s_0 + ... + s_{a-1}, and the j-th vertex of layer L_a is st_a + j.
  All layer indices are mod 3.  Put delta_a = s_{a+2} - s_{a+1} and take the
  cap c_a = max(0, delta_a + 1).  Arcs:
    (R)  u_{a,j} -> w                for every w in L_{a+1}
    (T)  u_{a,j} -> u_{a,l}          for every l < min(j, c_a)

Prose claims checked here, per n:
  1. excess(G_n) == 3 + [3 does not divide n]
  2. min out-degree == floor(n/3)          (so delta+ >= 8 exactly when n >= 24)
  3. G_n is strongly connected
  4. the number of vertices of margin > 0 is 0 when 3 | n and 1 when 3 does not
     divide n  -- i.e. G_n is a Pisa graph only in the 3 | n case, so the
     reading "E_delta(n) counts margin-0 vertices" holds only there
"""
import argparse
import sys

sys.path.insert(0, 'verify')
from verify_ssnc import verify  # noqa: E402


def build(n):
    m, r = divmod(n, 3)
    s = [m + (1 if a < r else 0) for a in range(3)]
    st = [0, s[0], s[0] + s[1]]
    delta = [s[(a + 2) % 3] - s[(a + 1) % 3] for a in range(3)]
    cap = [max(0, delta[a] + 1) for a in range(3)]
    A = [[0] * n for _ in range(n)]
    for a in range(3):
        b = (a + 1) % 3
        for j in range(s[a]):
            u = st[a] + j
            for l in range(s[b]):                     # (R)
                A[u][st[b] + l] = 1
            for l in range(min(j, cap[a])):           # (T)
                A[u][st[a] + l] = 1
    return A


ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('--lo', type=int, default=24, help='lowest order (default 24)')
ap.add_argument('--hi', type=int, default=60, help='highest order (default 60)')
args = ap.parse_args()
lo, hi = args.lo, args.hi

bad = []
for n in range(lo, hi + 1):
    r = verify(build(n))
    want_excess = 3 + (1 if n % 3 else 0)
    want_pos = 0 if n % 3 == 0 else 1
    ok = (r['excess'] == want_excess
          and r['min_out_degree'] == n // 3
          and r['strongly_connected']
          and r['positive_margin_vertices'] == want_pos)
    if not ok:
        bad.append((n, want_excess, want_pos, r))

print(f"orders tested: {lo}..{hi} ({hi - lo + 1} values)")
print("excess == 3+[3 nmid n], min out-degree == floor(n/3), strong,")
print("and positive-margin count == [3 nmid n], at every order:", len(bad) == 0)
for n, we, wp, r in bad[:5]:
    print(f"  MISMATCH n={n} want excess {we} pos {wp} got {r}")
sys.exit(1 if bad else 0)
