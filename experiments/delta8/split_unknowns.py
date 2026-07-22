#!/usr/bin/env python3
"""Resolve UNKNOWN rows of the delta-8 table by eBC / eUB splitting.

Mirrors the delta=7 final_leaf_plan strategy: solve the row once per fixed
value of e(B,C); any sub-leaf that stays UNKNOWN is split further by fixed
e(U,B).  A row is resolved INFEASIBLE only if every sub-leaf is INFEASIBLE;
any FEASIBLE sub-leaf resolves the row FEASIBLE (solution recorded).

Usage: python3 split_unknowns.py delta8_table.jsonl [--time-limit 600]
Appends resolved leaves to delta8_splits.jsonl.
"""
import argparse
import json
import sys

from gen_delta import GeneralModel, solve_case
from ortools.sat.python import cp_model
import time


def solve_fixed(delta, b, k, r, x, M, fix_eBC, fix_eUB, time_limit, workers):
    built = GeneralModel(delta, b, k, r, x, M, fix_eBC=fix_eBC, fix_eUB=fix_eUB)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    t0 = time.time()
    status = solver.Solve(built.model)
    rec = {"delta": delta, "b": b, "k": k, "r": r, "x": x, "M": M,
           "eBC": fix_eBC, "eUB": fix_eUB,
           "status": solver.StatusName(status),
           "wall_time_seconds": time.time() - t0}
    if rec["status"] in ("FEASIBLE", "OPTIMAL"):
        sol = {}
        for (v, w), var in built.arc.items():
            if solver.Value(var):
                sol.setdefault(v, []).append(w)
        rec["solution_arcs"] = sol
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="delta8_splits.jsonl")
    args = ap.parse_args()

    unknowns = [json.loads(l) for l in open(args.table)]
    unknowns = [u for u in unknowns if u["status"] == "UNKNOWN"]
    print(f"{len(unknowns)} UNKNOWN rows to resolve")
    done = set()
    try:
        for l in open(args.out):
            r = json.loads(l)
            done.add((r["b"], r["k"], r["r"], r["x"], r["M"],
                      r.get("eBC"), r.get("eUB")))
    except FileNotFoundError:
        pass
    print(f"resume: {len(done)} leaves already logged, will be skipped")
    out = open(args.out, "a")
    for u in unknowns:
        d, b, k, r, x, M = (u[f] for f in ("delta", "b", "k", "r", "x", "M"))
        h = k + x
        eUB_low = d * h - h * (h - 1) // 2 - x - x * (d - 1 - k - x)
        eBC_low = max(0, d * b - (b * h - eUB_low) - b * (b - 1) // 2 - b)
        eBC_cap = b * M
        row_status = "INFEASIBLE"
        for ebc in range(eBC_low, eBC_cap + 1):
            if (b, k, r, x, M, ebc, None) in done:
                continue
            rec = solve_fixed(d, b, k, r, x, M, ebc, None,
                              args.time_limit, args.workers)
            if rec["status"] == "UNKNOWN":
                sub = "INFEASIBLE"
                for eub in range(eUB_low, h * b + 1):
                    rec2 = solve_fixed(d, b, k, r, x, M, ebc, eub,
                                       args.time_limit, args.workers)
                    print(json.dumps({kk: rec2.get(kk) for kk in
                                      ("b", "k", "r", "x", "M", "eBC", "eUB",
                                       "status", "wall_time_seconds")}))
                    out.write(json.dumps(rec2) + "\n"); out.flush()
                    if rec2["status"] != "INFEASIBLE":
                        sub = rec2["status"]
                        if sub in ("FEASIBLE", "OPTIMAL"):
                            break
                rec["status"] = sub if sub != "INFEASIBLE" else "INFEASIBLE_split"
            print(json.dumps({kk: rec.get(kk) for kk in
                              ("b", "k", "r", "x", "M", "eBC", "eUB",
                               "status", "wall_time_seconds")}))
            out.write(json.dumps(rec) + "\n"); out.flush()
            if rec["status"] in ("FEASIBLE", "OPTIMAL"):
                row_status = "FEASIBLE"
                break
            if rec["status"] == "UNKNOWN":
                row_status = "UNKNOWN"
        print(f"ROW RESOLVED: (b{b} k{k} r{r} x{x} M{M}) -> {row_status}")


if __name__ == "__main__":
    main()
