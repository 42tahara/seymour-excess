"""Invariants with three independent implementations each.

Input convention: A is an n x n adjacency structure, A[i][j] = 1 iff arc i->j.
Numpy implementations take np.ndarray; the pure-python (_pp) and
stdlib-from-definitions (_sd) implementations accept any nested indexable
(list-of-lists or ndarray) and use only builtins.

Definitions (valid with or without digons; loops are never allowed):
  d1(v)      = |N+(v)|                       out-degree
  d_minus(v) = |N-(v)|                       in-degree
  d2(v)      = |N++(v)|  where N++(v) = { w != v : w not in N+(v),
                                          exists y in N+(v) with w in N+(y) }
               (vertices at out-distance exactly 2)
  dpp        = d2  (alias; Sullivan's d^{++} — AGGWYZ arXiv:2306.03493 use the
               same "exactly distance 2" definition)
  o(u,v)     = |N+(u) cap N+(v)|             per ordered pair; on an arc u->v
               this counts transitive triangles with base u->v
  tt(G)      = sum over arcs (u,v) of o(u,v) (transitive triangle count;
               in an oriented graph each transitive triangle u->v->w, u->w
               is counted exactly once, at its base arc (u,v))
  exc(G)     = sum_v max(0, d2(v) - d1(v) + 1)        Seymour excess
  exc_minus  = sum_v max(0, d2(v) - d_minus(v) + 1)   Sullivan excess
"""
import numpy as np


# ---------- conversion helpers ----------

def adj_from_dict(adj_dict, n=None):
    """{u: [v, ...]} (str or int keys) -> np.int8 matrix."""
    if n is None:
        n = len(adj_dict)
    A = np.zeros((n, n), dtype=np.int8)
    for u, nbrs in adj_dict.items():
        for v in nbrs:
            A[int(u), int(v)] = 1
    return A


def dict_from_adj(A):
    n = len(A)
    return {i: [j for j in range(n) if A[i][j]] for i in range(n)}


# ---------- numpy implementations ----------

def d1_np(A):
    return np.asarray(A).sum(axis=1, dtype=np.int64)


def d_minus_np(A):
    return np.asarray(A).sum(axis=0, dtype=np.int64)


def d2_np(A):
    A = np.asarray(A)
    n = A.shape[0]
    Ab = A.astype(bool)
    reach2 = (A.astype(np.int64) @ A.astype(np.int64)) > 0
    strict = reach2 & ~Ab & ~np.eye(n, dtype=bool)
    return strict.sum(axis=1).astype(np.int64)


dpp_np = d2_np


def o_np(A):
    """dict {(u,v): o(u,v)} over arcs u->v."""
    A = np.asarray(A).astype(np.int64)
    O = A @ A.T
    out = {}
    for u, v in np.argwhere(A):
        out[(int(u), int(v))] = int(O[u, v])
    return out


def tt_np(A):
    A = np.asarray(A).astype(np.int64)
    O = A @ A.T
    return int((A * O).sum())


def exc_np(A):
    d = d2_np(A) - d1_np(A)
    return int(np.maximum(0, d + 1).sum())


def exc_minus_np(A):
    d = d2_np(A) - d_minus_np(A)
    return int(np.maximum(0, d + 1).sum())


# ---------- pure-python implementations (loop accumulators) ----------

def _n(A):
    return len(A)


def d1_pp(A):
    n = _n(A)
    res = []
    for i in range(n):
        c = 0
        for j in range(n):
            if A[i][j]:
                c += 1
        res.append(c)
    return res


def d_minus_pp(A):
    n = _n(A)
    res = []
    for j in range(n):
        c = 0
        for i in range(n):
            if A[i][j]:
                c += 1
        res.append(c)
    return res


def d2_pp(A):
    n = _n(A)
    res = []
    for v in range(n):
        cnt = 0
        for w in range(n):
            if w == v or A[v][w]:
                continue
            found = False
            for y in range(n):
                if A[v][y] and A[y][w]:
                    found = True
                    break
            if found:
                cnt += 1
        res.append(cnt)
    return res


dpp_pp = d2_pp


def o_pp(A):
    n = _n(A)
    out = {}
    for u in range(n):
        for v in range(n):
            if not A[u][v]:
                continue
            c = 0
            for w in range(n):
                if A[u][w] and A[v][w]:
                    c += 1
            out[(u, v)] = c
    return out


def tt_pp(A):
    return sum(o_pp(A).values())


def exc_pp(A):
    d1 = d1_pp(A)
    d2 = d2_pp(A)
    total = 0
    for v in range(_n(A)):
        val = d2[v] - d1[v] + 1
        if val > 0:
            total += val
    return total


def exc_minus_pp(A):
    dm = d_minus_pp(A)
    d2 = d2_pp(A)
    total = 0
    for v in range(_n(A)):
        val = d2[v] - dm[v] + 1
        if val > 0:
            total += val
    return total


# ---------- stdlib-from-definitions implementations (set comprehensions) ----------

def _out_sets(A):
    n = _n(A)
    return [frozenset(j for j in range(n) if A[i][j]) for i in range(n)]


def d1_sd(A):
    return [len(s) for s in _out_sets(A)]


def d_minus_sd(A):
    n = _n(A)
    return [len({i for i in range(n) if A[i][j]}) for j in range(n)]


def d2_sd(A):
    n = _n(A)
    Nout = _out_sets(A)
    res = []
    for v in range(n):
        second = frozenset().union(*(Nout[y] for y in Nout[v])) if Nout[v] else frozenset()
        res.append(len(second - Nout[v] - {v}))
    return res


dpp_sd = d2_sd


def o_sd(A):
    Nout = _out_sets(A)
    return {(u, v): len(Nout[u] & Nout[v])
            for u in range(_n(A)) for v in Nout[u]}


def tt_sd(A):
    return sum(o_sd(A).values())


def exc_sd(A):
    d1 = d1_sd(A)
    d2 = d2_sd(A)
    return sum(max(0, d2[v] - d1[v] + 1) for v in range(_n(A)))


def exc_minus_sd(A):
    dm = d_minus_sd(A)
    d2 = d2_sd(A)
    return sum(max(0, d2[v] - dm[v] + 1) for v in range(_n(A)))


# ---------- cross-check ----------

_TRIPLES = {
    "d1": (d1_np, d1_pp, d1_sd),
    "d_minus": (d_minus_np, d_minus_pp, d_minus_sd),
    "d2": (d2_np, d2_pp, d2_sd),
    "o": (o_np, o_pp, o_sd),
    "tt": (tt_np, tt_pp, tt_sd),
    "exc": (exc_np, exc_pp, exc_sd),
    "exc_minus": (exc_minus_np, exc_minus_pp, exc_minus_sd),
}


def cross_check(A):
    """Assert all three implementations agree on every invariant; return the
    numpy results as a dict."""
    results = {}
    for name, (f_np, f_pp, f_sd) in _TRIPLES.items():
        r_np, r_pp, r_sd = f_np(A), f_pp(A), f_sd(A)
        if isinstance(r_np, np.ndarray):
            r_np = r_np.tolist()
        assert r_np == r_pp == r_sd, (
            f"{name} mismatch: np={r_np} pp={r_pp} sd={r_sd}")
        results[name] = r_np
    return results
