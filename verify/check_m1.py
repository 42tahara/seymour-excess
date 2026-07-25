#!/usr/bin/env python3
"""M1: re-score the measured witnesses in data/sonar_best/ with the public
independent verifier.

Claim checked, for every n = 24..100 (77 files, one per order):

    excess(G)        == 3 + [3 does not divide n]
    min out-degree   >= 8
    G is strongly connected
    G is an oriented graph (no loop, no digon -- verify_ssnc asserts)

The witnesses were produced by the CPU hill-climbing sweep (experiments/sonar.py)
and are stored as adjacency-dict JSON; the file name records the order and the
excess claimed at save time, and the embedded graph_sha1 is checked against
data/manifest.json by verify/check_hashes.py.  This script ignores the claimed
score and recomputes everything from the adjacency list.

Nothing here is a lower bound: these are upper-bound witnesses, so the check is
that each realises 3 + [3 nmid n] and none does better (a strictly smaller
excess would be news, and is reported as a MISMATCH so it cannot pass silently).

Usage (from the repository root):
  python3 verify/check_m1.py
  python3 verify/check_m1.py --lo 24 --hi 100
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_ssnc import to_matrix, verify  # noqa: E402

BEST_DIR = os.path.join(HERE, "..", "data", "sonar_best")
NAME = re.compile(r"n(\d+)_excess(\d+)_([0-9a-f]+)\.json$")


def witnesses(lo, hi):
    """{n: (filename, excess claimed by the file name)} for lo <= n <= hi."""
    found = {}
    for f in sorted(os.listdir(BEST_DIR)):
        m = NAME.match(f)
        if not m:
            continue
        n, e = int(m.group(1)), int(m.group(2))
        if not lo <= n <= hi:
            continue
        if n in found:
            sys.exit(f"FAIL: two witnesses for n={n}: {found[n][0]} and {f}")
        found[n] = (f, e)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lo", type=int, default=24)
    ap.add_argument("--hi", type=int, default=100)
    args = ap.parse_args()

    found = witnesses(args.lo, args.hi)
    missing = [n for n in range(args.lo, args.hi + 1) if n not in found]
    bad = []
    print(f"orders {args.lo}..{args.hi}: {len(found)} witnesses in data/sonar_best/")
    print("columns: n  excess/predicted  minout  scc  file")
    for n in sorted(found):
        f, claimed = found[n]
        obj = json.load(open(os.path.join(BEST_DIR, f)))
        r = verify(to_matrix(obj))
        want = 3 + (1 if n % 3 else 0)
        ok = (r["n"] == n and r["excess"] == want and claimed == want
              and r["min_out_degree"] >= 8 and r["strongly_connected"])
        if not ok:
            bad.append((n, want, f, r))
        print(f"{n:4d}  {r['excess']}/{want}  deg{r['min_out_degree']:3d}  "
              f"{'scc' if r['strongly_connected'] else 'SPLIT'}  {f}"
              f"{'' if ok else '   ***FAIL***'}")
    print("-" * 70)
    print(f"witnesses scored: {len(found)}, failures: {len(bad)}, "
          f"orders with no witness: {len(missing)}")
    print("excess == 3+[3 nmid n], min out-degree >= 8, strongly connected, "
          f"at every order: {not bad and not missing}")
    for n, want, f, r in bad[:5]:
        print(f"  MISMATCH n={n} want {want} got {r} ({f})")
    if missing:
        print(f"  MISSING orders: {missing}")
    sys.exit(1 if bad or missing else 0)


if __name__ == "__main__":
    main()
