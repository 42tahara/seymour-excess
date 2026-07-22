#!/usr/bin/env python3
"""Finite verification / counterexample search for GKZ Conjecture 8.2
(Guo–Kang–Zwaneveld, arXiv:2603.29626).

Claim: if every vertex of an oriented graph has
    |N1-(v)| = |N1+(v)| = |N2+(v)| = k,
then every vertex also has |N2-(v)| = k.  Proved for k = 1, 2 (their
Lem 4.8/4.9); k = 3 open.  We search for a k=3 counterexample at fixed n.

Reduction (double counting): sum_v |N2+(v)| = #{ordered pairs at distance
exactly 2} = sum_v |N2-(v)|.  Under the hypothesis both sums equal k*n, so a
counterexample (some vertex off k) forces some vertex BELOW k.  WLOG (relabel)
that vertex is 0, so it suffices to search with the single extra constraint
    |N2-(0)| <= k-1.
INFEASIBLE therefore verifies the conjecture for that (k, n) — over oriented
graphs (no digons); use --allow-digons for the general-digraph variant.

Soundness note: unlike the excess models, every indicator here is reified in
BOTH directions (t2 <=> arc-and-arc, p2 <=> OR, s2 <=> p2 and no-arc), so
equality cardinality constraints are exact — FEASIBLE output is still
re-verified with independent numpy arithmetic before being reported.

Usage: python3 gkz_conj82.py --n 7 [--k 3] [--time-limit 3600] [--workers 4]
       python3 gkz_conj82.py --scan 7 12
"""
import argparse
import hashlib
import json
import time

import numpy as np
from ortools.sat.python import cp_model


def build(n, k, allow_digons=False, hypothesis_only=False):
    m = cp_model.CpModel()
    a = {(i, j): m.NewBoolVar(f"a{i}_{j}")
         for i in range(n) for j in range(n) if i != j}
    if not allow_digons:
        for i in range(n):
            for j in range(i + 1, n):
                m.Add(a[(i, j)] + a[(j, i)] <= 1)
    for v in range(n):
        m.Add(sum(a[(v, j)] for j in range(n) if j != v) == k)
        m.Add(sum(a[(j, v)] for j in range(n) if j != v) == k)

    # s2[v][w] <=> dist(v,w) == 2, exact two-way reification
    s2 = {}
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            ts = []
            for y in range(n):
                if y in (v, w):
                    continue
                t2 = m.NewBoolVar(f"t{v}_{y}_{w}")
                m.Add(t2 <= a[(v, y)])
                m.Add(t2 <= a[(y, w)])
                m.Add(t2 >= a[(v, y)] + a[(y, w)] - 1)
                ts.append(t2)
            p2 = m.NewBoolVar(f"p{v}_{w}")
            for t2 in ts:
                m.Add(p2 >= t2)
            m.Add(p2 <= sum(ts))
            s = m.NewBoolVar(f"s{v}_{w}")
            m.Add(s <= p2)
            m.Add(s + a[(v, w)] <= 1)
            m.Add(s >= p2 - a[(v, w)])
            s2[(v, w)] = s
    for v in range(n):
        m.Add(sum(s2[(v, w)] for w in range(n) if w != v) == k)

    # counterexample condition at WLOG vertex 0 (skipped in hypothesis-only
    # mode, which just asks whether hypothesis graphs exist at this n at all —
    # INFEASIBLE there would make the main INFEASIBLE vacuous)
    if not hypothesis_only:
        m.Add(sum(s2[(w, 0)] for w in range(n) if w != 0) <= k - 1)

    # symmetry: out-neighbours of 0 are 1..k
    for j in range(1, k + 1):
        m.Add(a[(0, j)] == 1)
    return m, a


def exact_check(A, k):
    """Independent numpy re-check of hypothesis and conclusion."""
    n = len(A)
    A = np.asarray(A).astype(np.int32)
    out1, in1 = A.sum(1), A.sum(0)
    dist2 = ((A @ A) > 0) & (A == 0) & ~np.eye(n, dtype=bool)
    n2out, n2in = dist2.sum(1), dist2.sum(0)
    hyp = (out1 == k).all() and (in1 == k).all() and (n2out == k).all()
    return {"hypothesis_ok": bool(hyp),
            "digons": int((A & A.T).sum()),
            "n2in": n2in.tolist(),
            "is_counterexample": bool(hyp and (n2in != k).any())}


def solve_n(n, k, time_limit, workers, allow_digons=False,
            hypothesis_only=False):
    model, a = build(n, k, allow_digons, hypothesis_only)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    t0 = time.time()
    status = solver.Solve(model)
    rec = {"conjecture": "GKZ-8.2", "k": k, "n": n,
           "allow_digons": allow_digons, "hypothesis_only": hypothesis_only,
           "status": solver.StatusName(status),
           "wall_time_seconds": time.time() - t0}
    if rec["status"] in ("FEASIBLE", "OPTIMAL"):
        A = [[1 if i != j and solver.Value(a[(i, j)]) else 0
              for j in range(n)] for i in range(n)]
        rec.update(exact_check(A, k))
        adj = {i: [j for j in range(n) if A[i][j]] for i in range(n)}
        rec["adj"] = adj
        rec["sha1"] = hashlib.sha1(
            json.dumps(adj, sort_keys=True).encode()).hexdigest()
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int)
    ap.add_argument("--scan", nargs=2, type=int, metavar=("LO", "HI"))
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--time-limit", type=float, default=3600.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--allow-digons", action="store_true")
    ap.add_argument("--hypothesis-only", action="store_true")
    ap.add_argument("--out", default="gkz82_results.jsonl")
    args = ap.parse_args()

    ns = range(args.scan[0], args.scan[1] + 1) if args.scan else [args.n]
    out = open(args.out, "a")
    for n in ns:
        rec = solve_n(n, args.k, args.time_limit, args.workers,
                      args.allow_digons, args.hypothesis_only)
        print(json.dumps({kk: rec.get(kk) for kk in
                          ("n", "k", "status", "wall_time_seconds",
                           "is_counterexample", "sha1")}))
        out.write(json.dumps(rec) + "\n")
        out.flush()
        if not args.hypothesis_only and rec.get("is_counterexample"):
            print(f"!!! COUNTEREXAMPLE to GKZ Conj 8.2 at n={n} — "
                  "independent verification required !!!")


if __name__ == "__main__":
    main()
