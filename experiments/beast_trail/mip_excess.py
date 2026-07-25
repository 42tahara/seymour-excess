"""MIP version of the same M_{n,c} model: a[i,j] integer in {0,1}.

Compares LP-relax bound (obj=0 for all reachable n) with true integer min
excess for small n (17..20). Uses SCIP.
"""
import argparse, json, os, sys, time
from ortools.linear_solver import pywraplp


def build_mip(n: int, delta: int = 8, add_arc_ineq: bool = False):
    S = pywraplp.Solver.CreateSolver("SCIP")
    S.SuppressOutput()
    a = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                a[(i, j)] = S.IntVar(0, 1, f"a_{i}_{j}")
    for i in range(n):
        for j in range(i + 1, n):
            S.Add(a[(i, j)] + a[(j, i)] <= 1)
    out = {}
    for v in range(n):
        out[v] = S.IntVar(0, n - 1, f"out_{v}")
        S.Add(out[v] == sum(a[(v, j)] for j in range(n) if j != v))
        S.Add(out[v] >= delta)
    s = {}
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            s[(v, w)] = S.IntVar(0, 1, f"s_{v}_{w}")
            S.Add(s[(v, w)] + a[(v, w)] <= 1)
            for y in range(n):
                if y in (v, w):
                    continue
                S.Add(s[(v, w)] >= a[(v, y)] + a[(y, w)] - 1 - a[(v, w)])
    ex = {}
    for v in range(n):
        ex[v] = S.IntVar(0, n, f"ex_{v}")
        S.Add(ex[v] >= sum(s[(v, w)] for w in range(n) if w != v) - out[v] + 1)

    if add_arc_ineq:
        o_var = {}
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                for w in range(n):
                    if w in (u, v):
                        continue
                    y = S.IntVar(0, 1, f"o_{u}_{v}_{w}")
                    o_var[(u, v, w)] = y
                    S.Add(y <= a[(u, w)])
                    S.Add(y <= a[(v, w)])
                    S.Add(y >= a[(u, w)] + a[(v, w)] - 1)
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                d2u = sum(s[(u, w)] for w in range(n) if w != u)
                ovw_sum = sum(o_var[(u, v, w)] for w in range(n) if w not in (u, v))
                S.Add(d2u - out[v] + ovw_sum + n * (1 - a[(u, v)]) >= 0)
    S.Minimize(sum(ex[v] for v in range(n)))
    return S


def solve(n: int, delta: int = 8, add_arc_ineq: bool = False,
          time_limit: float = 300.0):
    S = build_mip(n, delta, add_arc_ineq)
    S.SetTimeLimit(int(time_limit * 1000))
    t0 = time.time()
    status = S.Solve()
    dt = time.time() - t0
    name = {pywraplp.Solver.OPTIMAL: "OPTIMAL",
            pywraplp.Solver.FEASIBLE: "FEASIBLE",
            pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
            pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
            pywraplp.Solver.UNBOUNDED: "UNBOUNDED"}.get(status, str(status))
    obj = S.Objective().Value() if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE) else None
    return {"n": n, "delta": delta, "add_arc_ineq": add_arc_ineq,
            "status": name, "mip_obj": obj, "wall_seconds": dt,
            "num_vars": S.NumVariables(), "num_constraints": S.NumConstraints()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=17)
    ap.add_argument("--nmax", type=int, default=20)
    ap.add_argument("--delta", type=int, default=8)
    ap.add_argument("--time-limit", type=float, default=180.0)
    ap.add_argument("--out", default="mip_excess_results.json")
    args = ap.parse_args()

    results = []
    for n in range(args.nmin, args.nmax + 1):
        r = solve(n, args.delta, add_arc_ineq=False,
                  time_limit=args.time_limit)
        print(f"n={n:2d}  MIP  status={r['status']}  obj={r['mip_obj']}"
              f"  t={r['wall_seconds']:.1f}s")
        results.append({"n": n, "mip": r})

    out_path = os.path.join(os.path.dirname(__file__), args.out)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
