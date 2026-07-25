"""Part B: LP relaxation of the CP-SAT model M_{n,c} for min-excess.

Base LP (mirrors excess2_search.build):
  a[i,j]              in [0,1]           (i != j)
  a[i,j] + a[j,i]     <= 1               (no digon)
  out[v]              = sum_j a[v,j]
  out[v]              >= 8                (min out-degree)
  s[v,w]              in [0,1]           (v != w)   (fractional N++ indicator)
  s[v,w] + a[v,w]     <= 1                (N++ excludes N+)
  s[v,w]              >= a[v,y] + a[y,w] - 1 - a[v,w]   (for each y != v,w)
  ex[v]               >= sum_w s[v,w] - out[v] + 1
  ex[v]               >= 0
  minimize sum_v ex[v]

Optional arc-inequality family:
  o[u,v,w]            in [0,1]
  o[u,v,w]            <= a[u,w]
  o[u,v,w]            <= a[v,w]
  o[u,v,w]            >= a[u,w] + a[v,w] - 1
  For each ordered pair (u,v):
    sum_w s[u,w] - out[v] + sum_w o[u,v,w] + n * (1 - a[u,v]) >= 0
  (Big-M form: active only when a[u,v] = 1, else vacuous.)

Reports LP-min excess with and without the arc-inequality family for n in the
given range.
"""
import argparse, json, os, sys, time
from ortools.linear_solver import pywraplp


def build_lp(n: int, delta: int = 8, add_arc_ineq: bool = False):
    S = pywraplp.Solver.CreateSolver("GLOP")
    S.SuppressOutput()
    INF = S.infinity()
    a = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                a[(i, j)] = S.NumVar(0.0, 1.0, f"a_{i}_{j}")
    # no digon
    for i in range(n):
        for j in range(i + 1, n):
            S.Add(a[(i, j)] + a[(j, i)] <= 1)
    # out-degree
    out = {}
    for v in range(n):
        out[v] = S.NumVar(0.0, n - 1, f"out_{v}")
        S.Add(out[v] == sum(a[(v, j)] for j in range(n) if j != v))
        S.Add(out[v] >= delta)
    # sec[v,w]
    s = {}
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            s[(v, w)] = S.NumVar(0.0, 1.0, f"s_{v}_{w}")
            S.Add(s[(v, w)] + a[(v, w)] <= 1)
            for y in range(n):
                if y in (v, w):
                    continue
                S.Add(s[(v, w)] >= a[(v, y)] + a[(y, w)] - 1 - a[(v, w)])
    # excess per vertex
    ex = {}
    for v in range(n):
        ex[v] = S.NumVar(0.0, n, f"ex_{v}")
        S.Add(ex[v] >= sum(s[(v, w)] for w in range(n) if w != v) - out[v] + 1)

    # optional arc-ineq family via big-M
    o_var = {}
    if add_arc_ineq:
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                for w in range(n):
                    if w in (u, v):
                        continue
                    y = S.NumVar(0.0, 1.0, f"o_{u}_{v}_{w}")
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
                # (d2u - out[v] + o(u,v)) + n * (1 - a[u,v]) >= 0
                S.Add(d2u - out[v] + ovw_sum + n * (1 - a[(u, v)]) >= 0)

    S.Minimize(sum(ex[v] for v in range(n)))
    return S, a, s, ex, out, o_var


def solve(n: int, delta: int = 8, add_arc_ineq: bool = False,
          time_limit: float = 300.0):
    S, a, s, ex, out, o_var = build_lp(n, delta, add_arc_ineq)
    S.SetTimeLimit(int(time_limit * 1000))
    t0 = time.time()
    status = S.Solve()
    dt = time.time() - t0
    status_name = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }[status]
    obj = S.Objective().Value() if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE) else None
    return {
        "n": n, "delta": delta, "add_arc_ineq": add_arc_ineq,
        "status": status_name, "lp_obj": obj, "wall_seconds": dt,
        "num_vars": S.NumVariables(), "num_constraints": S.NumConstraints(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=12)
    ap.add_argument("--nmax", type=int, default=20)
    ap.add_argument("--delta", type=int, default=8)
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--out", default="lp_excess_results.json")
    args = ap.parse_args()

    results = []
    for n in range(args.nmin, args.nmax + 1):
        r0 = solve(n, args.delta, add_arc_ineq=False,
                   time_limit=args.time_limit)
        print(f"n={n:2d}  base       obj={r0['lp_obj']}  t={r0['wall_seconds']:.1f}s"
              f"  vars={r0['num_vars']}  cons={r0['num_constraints']}")
        r1 = solve(n, args.delta, add_arc_ineq=True,
                   time_limit=args.time_limit)
        print(f"n={n:2d}  +arc-ineq  obj={r1['lp_obj']}  t={r1['wall_seconds']:.1f}s"
              f"  vars={r1['num_vars']}  cons={r1['num_constraints']}")
        results.append({"n": n, "base": r0, "arc_ineq": r1})

    out_path = os.path.join(os.path.dirname(__file__), args.out)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
