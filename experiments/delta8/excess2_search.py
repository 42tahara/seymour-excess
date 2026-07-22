#!/usr/bin/env python3
"""Direct CP-SAT search: does an oriented graph on n vertices exist with
minimum out-degree >= 8 and Seymour excess <= CAP?

  excess = sum_v max(0, |N++(v)| - |N+(v)| + 1)

CAP=0 is a Seymour counterexample; CAP=2 is one arc-battle away; the known
constructive upper bound is 3 (pure-ring construction, any n>=24 div. by 3).

Soundness: sec_{v,w} variables are forced to 1 whenever a 2-path exists and
no direct arc does; spurious 1s are possible assignments but never forced, so
INFEASIBLE is sound.  Every FEASIBLE model output must be re-verified exactly
(external numpy check) before being believed — run verify on the emitted
adjacency (the driver does this automatically).

Usage: python3 excess2_search.py --n 20 [--cap 2] [--time-limit 3600]
       python3 excess2_search.py --scan 17 30 [--cap 2]
"""
import argparse
import hashlib
import json
import time

import numpy as np
from ortools.sat.python import cp_model


def build(n, cap, delta=8, symmetry=True, tournament=False):
    m = cp_model.CpModel()
    arc = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                arc[(i, j)] = m.NewBoolVar(f"a{i}_{j}")
    for i in range(n):
        for j in range(i + 1, n):
            if tournament:      # exactly one arc per pair
                m.Add(arc[(i, j)] + arc[(j, i)] == 1)
            else:
                m.Add(arc[(i, j)] + arc[(j, i)] <= 1)
    out = [sum(arc[(i, j)] for j in range(n) if j != i) for i in range(n)]
    for i in range(n):
        m.Add(out[i] >= delta)

    sec = {}
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            sv = m.NewBoolVar(f"s{v}_{w}")
            sec[(v, w)] = sv
            m.Add(sv + arc[(v, w)] <= 1)
            for y in range(n):
                if y in (v, w):
                    continue
                m.AddBoolOr([arc[(v, y)].Not(), arc[(y, w)].Not(),
                             arc[(v, w)], sv])
    ex = []
    for v in range(n):
        e = m.NewIntVar(0, n, f"ex{v}")
        m.Add(e >= sum(sec[(v, w)] for w in range(n) if w != v)
              - out[v] + 1)
        ex.append(e)
    m.Add(sum(ex) <= cap)

    if symmetry:
        if tournament:
            # WLOG the score sequence is non-increasing.
            for i in range(n - 1):
                m.Add(out[i] >= out[i + 1])
        else:
            # WLOG vertex 0 has maximum out-degree and its out-neighbourhood
            # is the initial segment {1..d0}.
            for i in range(1, n):
                m.Add(out[0] >= out[i])
            for j in range(1, n - 1):
                m.Add(arc[(0, j)] >= arc[(0, j + 1)])
    return m, arc


def exact_excess(A):
    n = len(A)
    A = np.asarray(A).astype(int)
    out1 = A.sum(1)
    R2 = (A @ A > 0) & (A == 0) & ~np.eye(n, dtype=bool)
    d = R2.sum(1) - out1
    return int(np.maximum(0, d + 1).sum()), int(out1.min()), int((A & A.T).sum())


def solve_n(n, cap, time_limit, workers, tournament=False):
    model, arc = build(n, cap, tournament=tournament)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    t0 = time.time()
    status = solver.Solve(model)
    rec = {"n": n, "cap": cap, "status": solver.StatusName(status),
           "wall_time_seconds": time.time() - t0}
    if rec["status"] in ("FEASIBLE", "OPTIMAL"):
        A = [[1 if i != j and solver.Value(arc[(i, j)]) else 0
              for j in range(n)] for i in range(n)]
        exc, minout, digons = exact_excess(A)
        rec["exact_excess"] = exc
        rec["exact_minout"] = minout
        rec["digons"] = digons
        rec["adj"] = {i: [j for j in range(n) if A[i][j]] for i in range(n)}
        rec["sha1"] = hashlib.sha1(
            json.dumps(rec["adj"], sort_keys=True).encode()).hexdigest()
        rec["verified"] = (exc <= cap and minout >= 8 and digons == 0)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int)
    ap.add_argument("--scan", nargs=2, type=int, metavar=("LO", "HI"))
    ap.add_argument("--cap", type=int, default=2)
    ap.add_argument("--time-limit", type=float, default=3600.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--tournament", action="store_true")
    ap.add_argument("--out", default="excess2_results.jsonl")
    args = ap.parse_args()

    ns = range(args.scan[0], args.scan[1] + 1) if args.scan else [args.n]
    out = open(args.out, "a")
    for n in ns:
        rec = solve_n(n, args.cap, args.time_limit, args.workers,
                      tournament=args.tournament)
        rec["tournament"] = args.tournament
        print(json.dumps({k: rec.get(k) for k in
                          ("n", "cap", "status", "wall_time_seconds",
                           "exact_excess", "verified", "sha1")}))
        out.write(json.dumps(rec) + "\n")
        out.flush()
        if rec["status"] in ("FEASIBLE", "OPTIMAL") and rec.get("verified"):
            print(f"!!! VERIFIED excess<={args.cap} at n={n} — "
                  "independent confirmation required !!!")


if __name__ == "__main__":
    main()
