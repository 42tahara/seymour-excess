#!/usr/bin/env python3
"""Independent verifier for Pisa-structure-conjecture counterexample candidates.

Definitions (Halkiewicz, arXiv:2601.21563, Conjecture 5.1):
  margin(v) = |N++(v)| - |N+(v)|  (N++ = directed distance exactly 2)
  Pisa graph = strongly connected oriented graph (no digons) with
               Delta(D) = max_v margin(v) = 0
  Conjecture: the underlying undirected graph of a Pisa graph is either C_n
              or K_n minus a matching (every vertex has at most 1 non-neighbour).

A counterexample = Pisa graph whose underlying graph is neither.
Everything below is computed from these definitions only (no shared code with
the paper's repository).
"""
import hashlib
import json

import numpy as np


def analyze(name, A):
    A = np.asarray(A).astype(np.int8)
    n = len(A)
    assert not np.diag(A).any()
    digons = int((A & A.T).sum()) // 2

    out1 = A.sum(1).astype(int)
    R2 = (A.astype(int) @ A.astype(int) > 0) & (A == 0) & ~np.eye(n, dtype=bool)
    margins = R2.sum(1).astype(int) - out1
    delta = int(margins.max())
    zeros = int((margins == 0).sum())

    R = (A | np.eye(n, dtype=np.int8)).astype(bool)
    for _ in range(int(np.ceil(np.log2(n))) + 1):
        R = (R.astype(np.uint8) @ R.astype(np.uint8)) > 0
    strong = bool((R & R.T).all())

    U = ((A | A.T) > 0)
    deg = U.sum(1).astype(int)
    nonadj = (n - 1 - deg).astype(int)

    def is_cn():
        if not (deg == 2).all():
            return False
        seen, v, prev = {0}, 0, -1        # walk the cycle from vertex 0
        for _ in range(n - 1):
            nxt = [w for w in np.nonzero(U[v])[0] if w != prev]
            if not nxt:
                return False
            prev, v = v, int(nxt[0])
            seen.add(v)
        return len(seen) == n

    is_knm = bool((nonadj <= 1).all())
    cn = is_cn()
    pisa = (digons == 0 and strong and delta == 0)
    counterexample = pisa and not cn and not is_knm

    adj = {int(i): sorted(int(j) for j in np.nonzero(A[i])[0]) for i in range(n)}
    sha = hashlib.sha1(json.dumps(adj, sort_keys=True).encode()).hexdigest()

    print(f"=== {name} (n={n}, sha1 {sha[:8]}) ===")
    print(f"  digons {digons} / strongly_connected {strong} / Delta {delta} "
          f"/ margin-0 vertices {zeros}")
    print(f"  underlying degree min-max {deg.min()}-{deg.max()} / "
          f"max non-adjacency {nonadj.max()}")
    print(f"  is C_n: {cn} / is K_n-minus-matching: {is_knm}")
    print(f"  PISA: {pisa}  ->  COUNTEREXAMPLE to Conj 5.1: {counterexample}")
    return {"name": name, "n": n, "sha1": sha, "digons": digons,
            "strong": strong, "Delta": delta, "zeros": zeros,
            "deg_min": int(deg.min()), "deg_max": int(deg.max()),
            "nonadj_max": int(nonadj.max()), "is_Cn": cn,
            "is_Kn_minus_matching": is_knm, "pisa": pisa,
            "counterexample": counterexample, "adj": adj}


def blowup_cycle(m, t):
    """t-fold blow-up of directed C_m: layers of size t, complete bipartite
    arcs layer i -> layer i+1 (mod m)."""
    n = m * t
    A = np.zeros((n, n), dtype=np.int8)
    for c in range(m):
        for u in range(c * t, (c + 1) * t):
            nc = (c + 1) % m
            for v in range(nc * t, (nc + 1) * t):
                A[u, v] = 1
    return A


def pure_ring(n):
    """3-layer cyclic blow-up, one pure vertex per layer, impure -> pure moat."""
    assert n % 3 == 0
    t = n // 3
    A = blowup_cycle(3, t)
    for c in range(3):
        lo = c * t
        for w in range(lo + 1, lo + t):
            A[w, lo] = 1
    return A


if __name__ == "__main__":
    results = []
    results.append(analyze("candidate1_C4_blowup2_n8", blowup_cycle(4, 2)))
    results.append(analyze("candidate2_pure_ring_n48", pure_ring(48)))

    import os
    here = os.path.dirname(os.path.abspath(__file__))
    champ = json.load(open(os.path.join(here, "..", "data", "champion_d74d6509.json")))
    n = len(champ["adj"])
    A = np.zeros((n, n), dtype=np.int8)
    for i, nbrs in champ["adj"].items():
        for j in nbrs:
            A[int(i), j] = 1
    results.append(analyze("candidate3_champion_d74d6509_n50", A))

    results.append(analyze("recon_octahedron_C3_blowup2_n6", blowup_cycle(3, 2)))
    results.append(analyze("recon_K333_C3_blowup3_n9", blowup_cycle(3, 3)))

    ok = [r["counterexample"] for r in results[:3]]
    assert all(ok), f"expected 3 counterexamples, got {ok}"
    print("\nPASS: all 3 candidates confirmed as Conjecture 5.1 counterexamples")
