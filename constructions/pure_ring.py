#!/usr/bin/env python3
"""Pure m-ring construction: the k=1 special case of the C_m^k power ring.

B(m, 1, t) on n = m*t vertices realises excess = m whenever t = n/m >= 8
(delta >= 8 regime).  This is the construction behind claim T1:

    E_{delta>=8}(n) <= min{ m >= 3 : m | n, n/m >= 8 }.

See constructions/power_ring.py for the full arithmetic (its docstring proves
the general 2k < m case; k=1 needs only m >= 3).

Usage:
  python3 pure_ring.py --n 48            # m = smallest valid divisor
  python3 pure_ring.py --n 48 --m 3 --save ../data/pure_ring_n48_m3.json
"""
import argparse
import json

from power_ring import run_one


def best_m(n):
    for m in range(3, n + 1):
        if n % m == 0 and n // m >= 8:
            return m
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--m", type=int)
    ap.add_argument("--save")
    args = ap.parse_args()
    m = args.m or best_m(args.n)
    if m is None:
        raise SystemExit(f"no valid m for n={args.n} (needs m|n with n/m>=8)")
    assert args.n % m == 0
    rep = run_one(m, 1, args.n // m, save=args.save)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
