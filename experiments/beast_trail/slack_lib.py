"""Arc-slack computation for Seymour-style oriented graphs.

Definitions
-----------
Given a simple oriented graph (no loops, no 2-cycles) on vertex set [N]:
  d1(v)  = |N+(v)|              (out-degree)
  d2(v)  = |N++(v)|             (strict second out-nbhd:
                                 reach-in-2-steps, minus N+(v), minus {v})
  m(v)   = d2(v) - d1(v)        (Seymour deficit; m<0 means "赤字")
  o(u,v) = |N+(u) ∩ N+(v)|      (common out-neighbors of u,v;
                                 for arc u->v this counts transitive triangles
                                 with base u->v)

For every arc u->v the arc-inequality
      alpha(u,v) := m(u) + d1(u) - d1(v) + o(u,v) >= 0
holds elementarily: v in N+(u), and every w in N+(v) is either u (digon,
impossible), a common out-neighbor of u,v (o), or lands in N++_strict(u).
Telescoping d1 along a directed cycle C gives
      sum_{v in C} m(v) >= - sum_{arc in C} o(arc).

Two independent implementations are provided to cross-check:
  * compute_alpha_np : numpy dense adjacency
  * compute_alpha_pp : pure-python from definitions
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Tuple


def adj_from_dict(adj_dict: Dict, N: int) -> np.ndarray:
    A = np.zeros((N, N), dtype=np.int8)
    for u, nbrs in adj_dict.items():
        u = int(u)
        for v in nbrs:
            A[u, int(v)] = 1
    return A


def compute_basic_np(A: np.ndarray) -> Dict[str, np.ndarray]:
    """d1, d2 (strict), m via dense numpy."""
    N = A.shape[0]
    Ab = A.astype(bool)
    d1 = A.sum(axis=1, dtype=np.int32)
    reach2 = (A.astype(np.int32) @ A.astype(np.int32)) > 0
    # strict N++: exclude N+(v) and v itself
    n2 = (reach2 & ~Ab & ~np.eye(N, dtype=bool)).sum(axis=1)
    m = n2.astype(np.int32) - d1
    return {"d1": d1, "d2": n2.astype(np.int32), "m": m}


def compute_alpha_np(A: np.ndarray):
    """Return dict of arcs (u,v) -> (alpha, o) for every arc, plus basic vecs."""
    N = A.shape[0]
    Ab = A.astype(bool)
    basic = compute_basic_np(A)
    d1, m = basic["d1"], basic["m"]
    # o(u,v) = |N+(u) & N+(v)| for arc u->v: use A @ A.T? No.
    # Common out-neighbors: (N+(u) ∩ N+(v)) = row u & row v of A.
    # Efficient: O_mat = A @ A.T (entry [u,v] = sum_w A[u,w]*A[v,w]).
    Ai = A.astype(np.int32)
    O = Ai @ Ai.T  # O[u,v] = |N+(u) ∩ N+(v)|
    arcs = np.argwhere(Ab)
    out = {}
    for u, v in arcs:
        u = int(u); v = int(v)
        o = int(O[u, v])
        alpha = int(m[u]) + int(d1[u]) - int(d1[v]) + o
        out[(u, v)] = (alpha, o)
    return out, basic


# ---------- pure-python cross-check ----------

def adj_lists(A: np.ndarray):
    N = A.shape[0]
    out = [[] for _ in range(N)]
    for u in range(N):
        for v in range(N):
            if A[u, v]:
                out[u].append(v)
    return out


def compute_basic_pp(A: np.ndarray):
    N = A.shape[0]
    Nout = adj_lists(A)
    d1 = [len(s) for s in Nout]
    d2 = [0] * N
    m = [0] * N
    for u in range(N):
        Sout = set(Nout[u])
        two = set()
        for x in Nout[u]:
            for y in Nout[x]:
                two.add(y)
        two -= Sout
        two.discard(u)
        d2[u] = len(two)
        m[u] = d2[u] - d1[u]
    return d1, d2, m, Nout


def compute_alpha_pp(A: np.ndarray):
    N = A.shape[0]
    d1, d2, m, Nout = compute_basic_pp(A)
    Sout = [set(s) for s in Nout]
    out = {}
    for u in range(N):
        for v in Nout[u]:
            o = len(Sout[u] & Sout[v])
            alpha = m[u] + d1[u] - d1[v] + o
            out[(u, v)] = (alpha, o)
    return out, {"d1": d1, "d2": d2, "m": m}


def cross_check(A: np.ndarray):
    """Both implementations agree on every arc; raise if not."""
    a1, b1 = compute_alpha_np(A)
    a2, b2 = compute_alpha_pp(A)
    keys = set(a1.keys()) | set(a2.keys())
    for k in keys:
        assert a1[k] == a2[k], f"mismatch at {k}: {a1[k]} vs {a2[k]}"
    return True


# ---------- pure-ring construction ----------

def pure_ring(k: int, t: int) -> np.ndarray:
    """h9_divisor_ring style: k layers of size t.
    Cross-layer complete bipartite forward; intra-layer impure->pure only.
    Vertex 0 in each layer is 'pure' (in-only from other impure vertices of
    the same layer); vertices 1..t-1 are 'impure'.
    Returns adjacency of an oriented graph on N=k*t vertices.
    """
    N = k * t
    A = np.zeros((N, N), dtype=np.int8)
    for c in range(k):
        lo = c * t
        nlo = ((c + 1) % k) * t
        for u in range(lo, lo + t):
            for v in range(nlo, nlo + t):
                A[u, v] = 1
        for w in range(lo + 1, lo + t):
            A[w, lo] = 1
    return A


def is_pure(v: int, t: int) -> bool:
    return (v % t) == 0
