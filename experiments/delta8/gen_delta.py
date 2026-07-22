#!/usr/bin/env python3
"""Generalized CP-SAT feasibility model for local Seymour counterexample cores.

Generalizes the Sadhukhan-Sandeep-Sen delta=7 models (arXiv:2606.30588,
github.com/rbsandeep/Seymour-Vertex-delta7) to parametric delta.

Setup (all layers defined in the ORIGINAL digraph, then trimmed):
  s  = a vertex of minimum out-degree delta;  A = N+(s), |A| = delta
  a1 = argmin over A of |N+(a) cap A|;  A1 = N+(a1) cap A, |A1| = k
  B  = N+(A) \\ A, |B| = b;  in a counterexample ceil(delta/2) < b < delta
  (Prop 2.6) and 1 <= k <= ceil(delta/2)-1 (Lemma 2.4); also k >= delta-b
  since d+(a1) >= delta must fit inside A1 and B.
  r  = |N+(a1) cap B|, so delta-k <= r <= b.  P = the r hit B-vertices,
  Q = the b-r unhit ones (WLOG by symmetry).
  X  = A-vertices (outside A1) reached from A1 u B;  R = the rest of A.
  C  = N+(B) \\ (A u B) minus s; s itself is an explicit vertex.

Soundness notes:
- Q's out-arcs are deleted entirely (Trimming lemma: tails outside the
  witness set W preserve non-Seymourness of W).  Q is excluded from W.
- C-vertices are trimmed to out-degree exactly delta; their arcs leaving
  L are compressed by exact outside signatures n_S (S a nonempty subset of
  C): n_S = number of outside terminals receiving from exactly the C-subset
  S.  A witness that hits any c in S gains n_S second-neighbours.
- For r < b we OMIT the "X reached from A1 u P" and "C reached from P"
  constraints (their pre-trim justification may involve Q's deleted arcs);
  omission weakens the model, so INFEASIBLE verdicts remain sound.
- Aggregate lower bounds (redundant cuts, tight cases only) re-derived in
  general form and verified to reproduce every published delta=7 constant:
    e(U,B) >= delta*h - C(h,2) - x - x*(delta-1-k-x),   h = k+x
    e(B,C) >= delta*b - (b*h - e(U,B)) - C(b,2)

Usage:
  python3 gen_delta.py --delta 7 --validate   (reproduce known cases)
  python3 gen_delta.py --delta 8 --all
  python3 gen_delta.py --delta 8 --b 7 --k 1 --r 7 --x 2 --M 3
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time

import ortools
from ortools.sat.python import cp_model


def case_rows(delta: int):
    """Superset enumeration of (b, k, r, x, M) cases for a counterexample."""
    kmax = math.ceil(delta / 2) - 1
    for b in range(math.ceil(delta / 2) + 1, delta):
        for k in range(max(1, delta - b), kmax + 1):
            for r in range(delta - k, b + 1):
                for x in range(0, delta - k):          # |R| = delta-1-k-x >= 0
                    for M in range(0, k + r - x):      # x+M <= d+(a1)-1 = k+r-1
                        yield (b, k, r, x, M)


class GeneralModel:
    def __init__(self, delta, b, k, r, x, M, enforce_nonseymour=True,
                 symmetry_breaking=True, redundant_cuts=True,
                 fix_eBC=None, fix_eUB=None):
        self.fix_eBC, self.fix_eUB = fix_eBC, fix_eUB
        self.params = (delta, b, k, r, x, M)
        d = self.delta = delta
        self.model = cp_model.CpModel()
        m = self.model

        self.s = "s"
        self.a1 = "a1"
        self.A1 = [f"u{i}" for i in range(k)]
        self.X = [f"x{i}" for i in range(x)]
        self.R = [f"r{i}" for i in range(d - 1 - k - x)]
        self.A = [self.a1] + self.A1 + self.X + self.R
        self.P = [f"p{i}" for i in range(r)]
        self.Q = [f"q{i}" for i in range(b - r)]
        self.B = self.P + self.Q
        self.C = [f"c{i}" for i in range(M)]
        self.L = [self.s] + self.A + self.B + self.C
        self.W = self.A + self.P            # witnesses: non-Seymour enforced

        self.arc = {}
        for v in self.L:
            for w in self.L:
                if v != w:
                    self.arc[(v, w)] = m.NewBoolVar(f"a_{v}_{w}")

        E = self._a = lambda t, h: self.arc[(t, h)]
        L = self.L

        # Orientation: no digons.
        for i, v in enumerate(L):
            for w in L[i + 1:]:
                m.Add(E(v, w) + E(w, v) <= 1)

        # s sends exactly to A (d+(s) = delta = |A|).
        for w in L:
            if w != self.s:
                m.Add(E(self.s, w) == (1 if w in self.A else 0))

        # a1 sends exactly to A1 u P (definition of A1, k, and r).
        for w in L:
            if w != self.a1:
                m.Add(E(self.a1, w) == (1 if (w in self.A1 or w in self.P) else 0))

        # Trimming: Q keeps no out-arcs.
        for q in self.Q:
            for w in L:
                if w != q:
                    m.Add(E(q, w) == 0)

        # Layer containment: A sends only within A u B (definition of B);
        # equivalently no A -> C and no A -> s (s->A gives digons anyway).
        for a in self.A:
            for c in self.C:
                m.Add(E(a, c) == 0)
            m.Add(E(a, self.s) == 0)

        # Every B-vertex is reached from A (definition of B).
        for bv in self.B:
            m.Add(sum(E(a, bv) for a in self.A) >= 1)

        # R is unreached from A1 u B (definition of X/R split; sound for the
        # trimmed graph because deleting Q's arcs only removes in-arcs).
        for rv in self.R:
            for v in self.A1 + self.B:
                m.Add(E(v, rv) == 0)
        # B never sends back into a1's coneighbourhood... only definitional
        # part we keep: B -> a1 is impossible for P (digon with a1 -> P).
        # (implied by orientation; stated for clarity in audits)

        # Reachability of X and C from the surviving layer (tight cases only).
        if r == b:
            for xv in self.X:
                m.Add(sum(E(v, xv) for v in self.A1 + self.P) >= 1)
            for c in self.C:
                m.Add(sum(E(p, c) for p in self.P) >= 1)

        # Internal out-degree in A is at least k for every A-vertex
        # (a1 attains the minimum k).
        for a in self.A:
            m.Add(sum(E(a, t) for t in self.A if t != a) >= k)

        # Minimum out-degree delta for all live vertices.
        outdeg = lambda v: sum(E(v, w) for w in L if w != v)
        for v in self.W:
            m.Add(outdeg(v) >= d)

        # C-vertices: out-degree trimmed to exactly delta, with exact outside
        # signatures n_S over nonempty subsets S of C.
        self.nsig = {}
        for size in range(1, M + 1):
            for S in itertools.combinations(range(M), size):
                self.nsig[S] = m.NewIntVar(0, d, "n_" + "_".join(map(str, S)))
        for ci, c in enumerate(self.C):
            m.Add(outdeg(c)
                  + sum(v for S, v in self.nsig.items() if ci in S) == d)

        # Redundant aggregate cuts (tight cases; verified against delta=7).
        h = k + x
        U = self.A1 + self.X
        eUB = sum(E(u, bv) for u in U for bv in self.B)
        eBC = sum(E(bv, c) for bv in self.B for c in self.C)
        if redundant_cuts and r == b:
            eUB_low = d * h - h * (h - 1) // 2 - x - x * (d - 1 - k - x)
            m.Add(eUB >= eUB_low)
            m.Add(eBC >= d * b - (b * h - eUB_low) - b * (b - 1) // 2
                  - sum(E(bv, self.s) for bv in self.B) * 1)
        # Optional split equalities (for UNKNOWN rows, mirroring the
        # delta=7 final_leaf_plan strategy).
        if fix_eBC is not None:
            m.Add(eBC == fix_eBC)
        if fix_eUB is not None:
            m.Add(eUB == fix_eUB)

        # Symmetry breaking on interchangeable C (and Q is fully symmetric,
        # nothing to break: all-zero rows).
        if symmetry_breaking and self.C:
            cin = [sum(E(bv, c) for bv in self.B) for c in self.C]
            for i in range(len(cin) - 1):
                m.Add(cin[i] >= cin[i + 1])

        # Second-neighbourhood variables and non-Seymour inequalities.
        if enforce_nonseymour:
            for v in self.W:
                sec = {}
                for w in L:
                    if w == v:
                        continue
                    sv = m.NewBoolVar(f"sec_{v}_{w}")
                    sec[w] = sv
                    m.Add(sv + E(v, w) <= 1)
                    for y in L:
                        if y in (v, w):
                            continue
                        m.AddBoolOr([E(v, y).Not(), E(y, w).Not(),
                                     E(v, w), sv])
                local_second = sum(sec.values())
                outside = []
                for S, nS in self.nsig.items():
                    arcs = [E(v, self.C[ci]) for ci in S]
                    if not arcs:
                        continue
                    hit = m.NewBoolVar(f"hit_{v}_" + "_".join(map(str, S)))
                    for a_ in arcs:
                        m.AddImplication(a_, hit)
                    m.AddBoolOr(arcs + [hit.Not()])
                    p_ = m.NewIntVar(0, d, f"os_{v}_" + "_".join(map(str, S)))
                    m.Add(p_ == nS).OnlyEnforceIf(hit)
                    m.Add(p_ == 0).OnlyEnforceIf(hit.Not())
                    outside.append(p_)
                m.Add(local_second + sum(outside) <= outdeg(v) - 1)

    def proto_hash(self):
        return hashlib.sha256(str(self.model.Proto()).encode()).hexdigest()


def solve_case(delta, b, k, r, x, M, time_limit, workers):
    built = GeneralModel(delta, b, k, r, x, M)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    t0 = time.time()
    status = solver.Solve(built.model)
    rec = {
        "delta": delta, "b": b, "k": k, "r": r, "x": x, "M": M,
        "status": solver.StatusName(status),
        "wall_time_seconds": time.time() - t0,
        "model_hash": built.proto_hash(),
        "validation_error": built.model.Validate(),
        "ortools_version": ortools.__version__,
    }
    if rec["status"] == "FEASIBLE" or rec["status"] == "OPTIMAL":
        sol = {}
        for (v, w), var in built.arc.items():
            if solver.Value(var):
                sol.setdefault(v, []).append(w)
        rec["solution_arcs"] = sol
        rec["solution_hash"] = hashlib.sha256(
            json.dumps(sol, sort_keys=True).encode()).hexdigest()[:16]
        rec["signatures"] = {"_".join(map(str, S)): solver.Value(v)
                             for S, v in built.nsig.items() if solver.Value(v)}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=int, required=True)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--validate", action="store_true",
                    help="delta=7 known-case validation subset (b=6,k=1,r=6)")
    ap.add_argument("--b", type=int); ap.add_argument("--k", type=int)
    ap.add_argument("--r", type=int); ap.add_argument("--x", type=int)
    ap.add_argument("--M", type=int)
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    if args.all:
        rows = list(case_rows(args.delta))
    elif args.validate:
        rows = [(6, 1, 6, x, M) for (b_, k_, r_, x, M) in
                [r for r in case_rows(args.delta) if r[:3] == (6, 1, 6)]
                for _ in [0]]
        rows = [r for r in case_rows(args.delta) if r[:3] == (6, 1, 6)]
    else:
        rows = [(args.b, args.k, args.r, args.x, args.M)]

    out = open(args.out, "a") if args.out else None
    for (b, k, r, x, M) in rows:
        rec = solve_case(args.delta, b, k, r, x, M,
                         args.time_limit, args.workers)
        line = json.dumps(rec, sort_keys=True)
        print(json.dumps({kk: rec[kk] for kk in
                          ("delta", "b", "k", "r", "x", "M", "status",
                           "wall_time_seconds")}, sort_keys=True))
        if out:
            out.write(line + "\n")
            out.flush()


if __name__ == "__main__":
    main()
