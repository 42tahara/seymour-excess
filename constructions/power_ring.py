#!/usr/bin/env python3
"""C_m^k power-ring construction — GKZ-generalized blow-up for the desert map.

Background (GKZ = Guo–Kang–Zwaneveld, arXiv:2603.29626, Thm 4.6 + Lem 4.7):
the skeleton of a legal lexicographic-product construction need not be C_m;
the k-th power C_m^k works whenever 2k < m. Uniform layer sizes are always in
the kernel of S_D, so we implement the uniform case first (non-uniform
gcd(m,k)-striped sizes are a later generalization).

Construction B(m, k, t), n = m*t, layers L_0..L_{m-1} of size t:
  - blow-up arcs: all of L_i -> all of L_{i+1}, ..., L_{i+k}  (indices mod m)
  - in-star perturbation: every non-pure v in L_i gets the single extra arc
    v -> p_i, where p_i is the designated pure vertex of its own layer.

Paper check of the perturbation arithmetic (the 2k < m case; this is the
point flagged by the supervisor — the target's out-set must stay inside the
observer's N+ ∪ N++):

  Non-pure v in L_i:  N+(v) = L_{i+1..i+k} ∪ {p_i}, size kt+1.
    The only new 2-step source is p_i, and out(p_i) = L_{i+1..i+k} ⊆ N+(v),
    so nothing leaks into N++.  The in-star targets reachable through
    L_{i+1..i+k} are p_{i+1}..p_{i+k}, all inside N+(v) as well.  Hence
    N++(v) = L_{i+k+1..i+2k} exactly (2k < m keeps these k layers disjoint
    from L_i and from N+(v)), size kt.  d(v) = kt - (kt+1) = -1: violator.

  Pure p_i:  N+(p_i) = L_{i+1..i+k}, size kt.  Two-step reach =
    L_{i+2..i+2k} ∪ {p_{i+1}..p_{i+k}}; subtracting N+ leaves
    N++(p_i) = L_{i+k+1..i+2k}, size kt.  d(p_i) = 0: Seymour vertex with
    margin 0, contributing exactly 1 to the excess.

  Digon-freeness: L_i -> L_{i+j} has a reverse arc only if m-j <= k, but
    j <= k < m-k means m-j >= m-k > k.  In-star arcs all point at p_i, which
    has no intra-layer out-arc.  Strong connectivity via the k=1-step ring.

  Totals: excess = m (one pure vertex per layer), min out-degree = kt
    (pure vertices; non-pure have kt+1) — need kt >= 8 for the delta>=8 regime.

Unified upper bound (supersedes T1, which is the k=1 special case):
    E_{δ≥8}(n) <= min{ m >= 3 : m | n, ∃k >= 1 with 2k < m and k*(n/m) >= 8 }

Usage:
  python3 gkz_power_ring.py --m 7 --k 2 --t 7        # build + verify one graph
  python3 gkz_power_ring.py --targets                # desert targets 25/35/49
  python3 gkz_power_ring.py --bound-table 17 100     # unified bound vs old T1
"""
import argparse
import hashlib
import json

import numpy as np


def build(m, k, t):
    assert m >= 3 and k >= 1 and t >= 1 and 2 * k < m, "need 2k < m, m>=3"
    n = m * t
    A = np.zeros((n, n), dtype=np.int8)
    layer = lambda i: range((i % m) * t, (i % m) * t + t)
    for i in range(m):
        for j in range(1, k + 1):
            for u in layer(i):
                for w in layer(i + j):
                    A[u, w] = 1
    for i in range(m):          # in-star: non-pure vertices sink onto p_i
        p = i * t
        for u in layer(i):
            if u != p:
                A[u, p] = 1
    return A


def analyze(A):
    """Standalone numpy re-check (mirrors evaluate.py arithmetic, any n)."""
    n = len(A)
    A = np.asarray(A).astype(np.int32)
    assert not np.diag(A).any() and not (A & A.T).any(), "loop or digon"
    out1 = A.sum(axis=1)
    reach2 = (A @ A) > 0
    Ab = A.astype(bool)
    n2 = (reach2 & ~Ab & ~np.eye(n, dtype=bool)).sum(axis=1)
    d = n2 - out1
    R = Ab | np.eye(n, dtype=bool)
    for _ in range(int(np.ceil(np.log2(max(n, 2))))):
        R = R @ R
    strong = bool((R & R.T).all())
    return {
        "n": n,
        "excess": int(np.maximum(0, d + 1).sum()),
        "nsat": int((d >= 0).sum()),
        "min_outdeg": int(out1.min()),
        "strongly_connected": strong,
        "deficits_pure_expected0": None,   # filled by caller for structure check
    }


def structure_check(A, m, k, t):
    """Verify the paper arithmetic vertex-class by vertex-class."""
    n = m * t
    A = np.asarray(A).astype(np.int32)
    out1 = A.sum(axis=1)
    reach2 = (A @ A) > 0
    Ab = A.astype(bool)
    n2 = (reach2 & ~Ab & ~np.eye(n, dtype=bool)).sum(axis=1)
    d = n2 - out1
    ok = True
    for i in range(m):
        p = i * t
        if d[p] != 0 or out1[p] != k * t:
            ok = False
        for u in range(i * t, i * t + t):
            if u == p:
                continue
            if d[u] != -1 or out1[u] != k * t + 1:
                ok = False
    return ok


def run_one(m, k, t, save=None):
    A = build(m, k, t)
    rep = analyze(A)
    rep["m"], rep["k"], rep["t"] = m, k, t
    rep["structure_matches_paper"] = structure_check(A, m, k, t)
    del rep["deficits_pure_expected0"]
    adj = {i: [j for j in range(len(A)) if A[i][j]] for i in range(len(A))}
    rep["sha1"] = hashlib.sha1(
        json.dumps(adj, sort_keys=True).encode()).hexdigest()
    if save:
        json.dump(A.tolist(), open(save, "w"))
        rep["saved"] = save
    return rep


def unified_bound(n):
    """min m with the C_m^k family; also returns the witnessing (m,k)."""
    best = None
    for mm in range(3, n + 1):
        if n % mm:
            continue
        tt = n // mm
        for kk in range(1, (mm - 1) // 2 + 1):
            if kk * tt >= 8:
                best = (mm, kk, tt)
                break
        if best:
            break
    return best


def old_bound(n):
    """T1: min k>=3, k|n, n/k >= 8 (the k=1-skeleton special case)."""
    for kk in range(3, n + 1):
        if n % kk == 0 and n // kk >= 8:
            return kk
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int)
    ap.add_argument("--k", type=int)
    ap.add_argument("--t", type=int)
    ap.add_argument("--save")
    ap.add_argument("--targets", action="store_true")
    ap.add_argument("--bound-table", nargs=2, type=int, metavar=("LO", "HI"))
    args = ap.parse_args()

    if args.targets:
        for (m, k, t) in [(5, 2, 5), (5, 2, 7), (7, 2, 7)]:
            rep = run_one(m, k, t, save=f"gkz_ring_n{m*t}_m{m}k{k}.json")
            print(json.dumps(rep))
    elif args.bound_table:
        lo, hi = args.bound_table
        print("n\told_T1\tnew\twitness(m,k,t)")
        for n in range(lo, hi + 1):
            nb = unified_bound(n)
            print(f"{n}\t{old_bound(n)}\t{nb[0] if nb else None}\t{nb}")
    else:
        rep = run_one(args.m, args.k, args.t, save=args.save)
        print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
