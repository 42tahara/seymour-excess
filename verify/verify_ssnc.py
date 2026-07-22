#!/usr/bin/env python3
"""Independent verifier for Seymour-second-neighbourhood claims.

Pure-Python (sets + Kosaraju), deliberately sharing no code with the numpy
pipeline in experiments/ or the construction scripts: if either side has a
bug, the two must disagree.  JSON input only — this public version never
executes candidate code.

Accepted JSON formats:
  - list of 0/1 rows (adjacency matrix)
  - {"adj": {"0": [j, ...], ...}, ...}   (champion files)
  - {"0": [j, ...], ...}                 (bare adjacency dict)

Usage: python3 verify_ssnc.py FILE.json
Exit status 0 iff the graph is a valid oriented graph; the report prints
excess, margins, min out-degree and strong connectivity for external
comparison against the claimed values.
"""
import json
import sys


def to_matrix(obj):
    if isinstance(obj, list):
        return obj
    adj = obj.get("adj", obj) if isinstance(obj, dict) else None
    n = len(adj)
    A = [[0] * n for _ in range(n)]
    for i, nbrs in adj.items():
        for j in nbrs:
            A[int(i)][int(j)] = 1
    return A


def second_neighbourhood_deficits(A):
    n = len(A)
    outs = [set(j for j in range(n) if A[i][j]) for i in range(n)]
    deficits = []
    for v in range(n):
        n2 = set()
        for u in outs[v]:
            n2 |= outs[u]
        n2 -= outs[v]
        n2.discard(v)
        deficits.append(len(n2) - len(outs[v]))
    return deficits, outs


def scc_sizes(A):
    n = len(A)
    adj = [[j for j in range(n) if A[i][j]] for i in range(n)]
    radj = [[i for i in range(n) if A[i][j]] for j in range(n)]
    seen, order = [False] * n, []
    for s in range(n):
        if seen[s]:
            continue
        stack = [(s, iter(adj[s]))]
        seen[s] = True
        while stack:
            v, it = stack[-1]
            advanced = False
            for w in it:
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, iter(adj[w])))
                    advanced = True
                    break
            if not advanced:
                order.append(v)
                stack.pop()
    seen, sizes = [False] * n, []
    for s in reversed(order):
        if seen[s]:
            continue
        size, stack = 0, [s]
        seen[s] = True
        while stack:
            v = stack.pop()
            size += 1
            for w in radj[v]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def verify(A):
    n = len(A)
    for i, row in enumerate(A):
        assert len(row) == n, f"row {i} length {len(row)} != {n}"
        assert all(x in (0, 1) for x in row), f"non-0/1 entry in row {i}"
        assert not A[i][i], f"loop at {i}"
    for i in range(n):
        for j in range(i + 1, n):
            assert not (A[i][j] and A[j][i]), f"digon {i}<->{j}"
    deficits, outs = second_neighbourhood_deficits(A)
    outdegs = [len(o) for o in outs]
    sizes = scc_sizes(A)
    return {
        "n": n,
        "excess": sum(max(0, d + 1) for d in deficits),
        "margin0_vertices": sum(1 for d in deficits if d == 0),
        "positive_margin_vertices": sum(1 for d in deficits if d > 0),
        "nsat": sum(1 for d in deficits if d >= 0),
        "min_out_degree": min(outdegs),
        "strongly_connected": len(sizes) == 1,
        "is_counterexample": all(d <= -1 for d in deficits),
    }


if __name__ == "__main__":
    rep = verify(to_matrix(json.load(open(sys.argv[1]))))
    print(json.dumps(rep, indent=1))
