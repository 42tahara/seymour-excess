"""Quasi-kernel checking and minimization.

Adopted convention (P2-a, fixed for this project):
  G is a digraph (digons allowed, loops not).  Q subset V is a QUASI-KERNEL iff
    (i)  Q is independent in the underlying graph
         (no arc u->v with both u, v in Q, in either direction), and
    (ii) every v not in Q has a directed path of length 1 or 2 FROM v TO Q
         (i.e. Q subset is reachable: exists q in Q with v->q, or v->y->q).
  This is the convention of Ai-Gerke-Gutin-Yeo-Zhou 2022 and the
  Erdos-Gyori-Mezei-Salia-Tyomkyn survey; the Chvatal-Lovasz theorem
  guarantees existence for every digraph.  The Small QK conjecture
  (P.L. Erdos-Szekely 1976) asks: every SINK-FREE digraph has a QK with
  |Q| <= n/2.  A counterexample needs qk_min(G) > n/2.

qk_check has the standard three implementations; qk_min is exact CP-SAT ILP
(single implementation) cross-checked by qk_min_brute for small n.
"""
import numpy as np
from ortools.sat.python import cp_model


# ---------- reach-within-2 helpers ----------

def _reach2_sets(A):
    """R(v) = set of w != v reachable from v by a path of length 1 or 2."""
    n = len(A)
    Nout = [frozenset(j for j in range(n) if A[i][j]) for i in range(n)]
    R = []
    for v in range(n):
        r = set(Nout[v])
        for y in Nout[v]:
            r |= Nout[y]
        r.discard(v)
        R.append(frozenset(r))
    return R


# ---------- qk_check: three implementations ----------

def qk_check_np(A, Q):
    A = np.asarray(A)
    n = A.shape[0]
    q = np.zeros(n, dtype=bool)
    q[list(Q)] = True
    U = (A.astype(bool) | A.astype(bool).T)
    if U[np.ix_(q, q)].any():                       # independence
        return False
    Ab = A.astype(bool)
    reach = Ab | ((A.astype(np.int64) @ A.astype(np.int64)) > 0)
    np.fill_diagonal(reach, False)
    for v in range(n):
        if not q[v] and not reach[v][q].any():      # coverage
            return False
    return True


def qk_check_pp(A, Q):
    n = len(A)
    Qs = set(Q)
    for u in Qs:                                    # independence
        for v in Qs:
            if u != v and (A[u][v] or A[v][u]):
                return False
    for v in range(n):                              # coverage
        if v in Qs:
            continue
        ok = False
        for q in Qs:
            if A[v][q]:
                ok = True
                break
            for y in range(n):
                if A[v][y] and A[y][q]:
                    ok = True
                    break
            if ok:
                break
        if not ok:
            return False
    return True


def qk_check_sd(A, Q):
    n = len(A)
    Qs = frozenset(Q)
    under = {frozenset((u, v)) for u in range(n) for v in range(n)
             if u != v and A[u][v]}
    if any(frozenset((u, v)) in under for u in Qs for v in Qs if u < v):
        return False
    R = _reach2_sets(A)
    return all(R[v] & Qs for v in range(n) if v not in Qs)


# ---------- qk_min ----------

def qk_min(A, time_limit=600.0, workers=4):
    """Exact minimum quasi-kernel size via CP-SAT.  Returns (size, Q, status).

    Model: x_v in {0,1};
      independence: x_u + x_v <= 1 for every underlying edge {u,v};
      coverage:     x_v + sum_{w in R(v)} x_w >= 1  (R = reach within 2).
    Exact encoding (no relaxation): both constraints are literal transcriptions
    of the definition, so OPTIMAL means qk_min exactly.
    """
    n = len(A)
    R = _reach2_sets(A)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{v}") for v in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if A[u][v] or A[v][u]:
                m.Add(x[u] + x[v] <= 1)
    for v in range(n):
        m.Add(x[v] + sum(x[w] for w in R[v]) >= 1)
    m.Minimize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    status = solver.Solve(m)
    name = solver.StatusName(status)
    if name in ("OPTIMAL", "FEASIBLE"):
        Q = [v for v in range(n) if solver.Value(x[v])]
        return len(Q), Q, name
    return None, None, name


def qk_min_brute(A):
    """Brute force over subsets by increasing size (n <= ~16)."""
    from itertools import combinations
    n = len(A)
    for k in range(0, n + 1):
        for Q in combinations(range(n), k):
            if qk_check_sd(A, Q):
                return k, list(Q)
    return None, None
