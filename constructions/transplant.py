#!/usr/bin/env python3
"""Keystone-cluster transplant: turn the one-off n=53 champion into stock.

The survivor cluster of ca40b396 is a reusable design: wings 34/35 carry an
exact copy of keystone 18's out-set plus the arc to the keystone (the in-star
trick, asymmetric edition), terminal 36 closes the loop at distance 2.
This script transplants the WHOLE graph to nearby n by bulk surgery that
leaves the cluster untouched:

  n < 53 : greedily delete bulk vertices (choose, at each step, the deletion
           minimising total excess; out-degree slack is huge, delta stays >=8)
  n > 53 : greedily clone bulk vertices (new vertex inherits the in/out
           neighbourhood of its template; no arc between twin and template)

Usage: python3 transplant.py 47 [--polish-seed out.json]
       python3 transplant.py 59
"""
import json
import sys

import numpy as np

CLUSTER = [18, 34, 35, 36]


def load53():
    rec = json.load(open('champion_n53_ca40b396.json'))
    n = 53
    A = np.zeros((n, n), dtype=int)
    for i, nb in rec['adj'].items():
        for j in nb:
            A[int(i), j] = 1
    return A


def excess_of(A):
    out1 = A.sum(1)
    R2 = (A @ A > 0) & (A == 0) & ~np.eye(len(A), dtype=bool)
    d = R2.sum(1) - out1
    return int(np.maximum(0, d + 1).sum()), int(out1.min())


def strongly_connected(A):
    n = len(A)
    R = (A | np.eye(n, dtype=int)).astype(bool)
    for _ in range(int(np.ceil(np.log2(n))) + 1):
        R = (R @ R)
    return bool((R & R.T).all())


def delete_towards(A, target, keep):
    while len(A) > target:
        best = None
        for x in range(len(A)):
            if x in keep:
                continue
            B = np.delete(np.delete(A, x, 0), x, 1)
            e, mo = excess_of(B)
            if mo < 8 or not strongly_connected(B):
                continue
            if best is None or e < best[0]:
                best = (e, x, B)
        e, x, A = best
        keep = [k - (1 if k > x else 0) for k in keep]
        print(f"  n={len(A)}: deleted {x}, excess {e}")
    return A, keep


def clone_towards(A, target, keep):
    while len(A) < target:
        n = len(A)
        best = None
        cands = [x for x in range(n) if x not in keep]
        for x in cands:
            B = np.zeros((n + 1, n + 1), dtype=int)
            B[:n, :n] = A
            B[n, :n] = A[x, :]          # same out-neighbourhood
            B[:n, n] = A[:, x]          # same in-neighbourhood
            e, mo = excess_of(B)
            if mo < 8 or (B & B.T).any():
                continue
            if best is None or e < best[0]:
                best = (e, x, B)
        e, x, A = best
        print(f"  n={len(A)}: cloned {x}, excess {e}")
    return A, keep


def main():
    target = int(sys.argv[1])
    A = load53()
    e0, _ = excess_of(A)
    print(f"start n=53 excess {e0}, cluster {CLUSTER}")
    keep = list(CLUSTER)
    if target < 53:
        A, keep = delete_towards(A, target, keep)
    else:
        A, keep = clone_towards(A, target, keep)
    e, mo = excess_of(A)
    print(f"transplant n={target}: excess {e}, min outdeg {mo}, "
          f"strong {strongly_connected(A)}, cluster now at {keep}")
    out = f'transplant_n{target}.json'
    json.dump(A.tolist(), open(out, 'w'))
    print(f"saved {out}")


if __name__ == '__main__':
    main()
