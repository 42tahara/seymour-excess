"""Deterministic judge for Seymour second-neighbourhood counterexample search.

A valid candidate is an oriented graph on N vertices: 0/1 matrix, zero diagonal,
no 2-cycles (A[i,j] and A[j,i] never both 1). A[i,j]=1 means arc i->j.

For each vertex v:  d(v) = |N++(v)| - |N+(v)|   (second minus first out-neighbourhood).
The conjecture says some v has d(v) >= 0; a counterexample needs d(v) <= -1 for ALL v.

score = 1000000 * degdef + 10000 * sccmiss + excess, where
  excess  = sum_v max(0, d(v) + 1)    (PRIMARY objective: excess == 0 is exactly
                                       'every vertex has d(v) <= -1', i.e. a
                                       counterexample; smooth gradient, unlike the
                                       step function nsat, which is kept in the
                                       tuple for reporting only)
  degdef  = sum_v max(0, 8 - outdeg(v))
  sccmiss = N - (size of the largest strongly connected component)
Lower is better; 0 = counterexample to an open conjecture.

sccmiss is a HARD-grade penalty (10000/vertex): a minimal counterexample has
no proper closed out-set, i.e. is strongly connected (equivalently: the
reduction theorem of Espuny Diaz et al., arXiv:2403.02842), so the search
space is provably strongly connected digraphs only.

The degdef term is essential, not cosmetic: sinks satisfy the conjecture
irreducibly (d=0), an in-star reaches nsat=1 trivially, and it is a theorem
(Kaneko-Locke 2001 + 2026 for out-degree 7) that any counterexample has
minimum out-degree >= 8. Without the penalty the search collapses into
sink-based trivialities.
"""
import os
import numpy as np

N = int(os.environ.get('SEYMOUR_N', '50'))

def score(A):
    A = np.asarray(A)
    if A.ndim != 2 or A.shape != (N, N):
        return None
    A = (A != 0).astype(np.int8)
    if np.diag(A).any() or (A & A.T).any():      # loops or 2-cycles
        return None
    out1 = A.sum(axis=1, dtype=np.int32)
    reach2 = (A.astype(np.int32) @ A.astype(np.int32)) > 0
    Ab = A.astype(bool)
    n2 = (reach2 & ~Ab & ~np.eye(N, dtype=bool)).sum(axis=1)
    d = n2.astype(np.int32) - out1
    nsat = int((d >= 0).sum())
    excess = int(np.maximum(0, d + 1).sum())
    degdef = int(np.maximum(0, 8 - out1).sum())
    R = Ab | np.eye(N, dtype=bool)               # reachability by repeated squaring
    for _ in range(int(np.ceil(np.log2(N))) + 1):
        R = (R.astype(np.uint8) @ R.astype(np.uint8)) > 0
    sccmiss = N - int((R & R.T).sum(axis=1).max())
    total = 1000000 * degdef + 10000 * sccmiss + excess
    return total, nsat, excess, int(out1.min()), sccmiss

def circulant(S, n=N):
    """helper: adjacency matrix of the circulant digraph on Z_n with connection set S"""
    A = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for s in S:
            A[i, (i + s) % n] = 1
    return A
