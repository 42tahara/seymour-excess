"""Generation 0: hand-written seed constructions for the Seymour search.

Each function is self-contained (only np / N / score from the exec namespace)
so its source can be transplanted into the evolution database as `construct()`.
"""
import numpy as np
from evaluate import score, N

def h1_circulant_consecutive():
    """circulant S={1..8}: the d(v)=0 plateau — every vertex ties exactly"""
    A = np.zeros((N, N), dtype=np.int8)
    for i in range(N):
        for d in range(1, 9):
            A[i, (i + d) % N] = 1
    return A

def h2_circulant_cosets():
    """circulant from 2 cosets of the index-10 'subgroup': also lands on the d=0 plateau"""
    A = np.zeros((N, N), dtype=np.int8)
    S = [x for x in range(1, N) if x % 10 in (1, 2)]
    for i in range(N):
        for d in S:
            A[i, (i + d) % N] = 1
    return A

def h3_blowup_balanced():
    """balanced cyclic blow-up (class count adapts to N): d=0 plateau again"""
    A = np.zeros((N, N), dtype=np.int8)
    k = max(2, min(5, N // 8))
    starts = [round(c * N / k) for c in range(k + 1)]
    for c in range(k):
        nc = (c + 1) % k
        for u in range(starts[c], starts[c + 1]):
            for v in range(starts[nc], starts[nc + 1]):
                A[u, v] = 1
    return A

def h4_blowup_descending():
    """UNBALANCED cyclic blow-up, descending class sizes (adapts to N): only the
    class before the size jump satisfies the conjecture"""
    k = max(2, min(5, N // 9))
    base = N // k
    off = (k - 1) // 2
    sizes = [base + off - c for c in range(k)]
    sizes[0] += N - sum(sizes)
    starts = [sum(sizes[:c]) for c in range(k + 1)]
    A = np.zeros((N, N), dtype=np.int8)
    for c in range(k):
        nc = (c + 1) % k
        for u in range(starts[c], starts[c + 1]):
            for v in range(starts[nc], starts[nc + 1]):
                A[u, v] = 1
    return A

def h5_random_orientation():
    """random orientation of G(N, 0.35), topped up to out-degree >= 8: sanity control"""
    rng = np.random.default_rng(7)
    A = np.zeros((N, N), dtype=np.int8)
    for i in range(N):
        for j in range(i + 1, N):
            r = rng.random()
            if r < 0.175:
                A[i, j] = 1
            elif r < 0.35:
                A[j, i] = 1
    for i in range(N):
        for j in rng.permutation(N):
            if int(A[i].sum()) >= 8:
                break
            if j != i and not A[i, j] and not A[j, i]:
                A[i, j] = 1
    return A

def h6_random_outregular():
    """every vertex picks 9 random out-neighbours (2-cycles skipped)"""
    rng = np.random.default_rng(3)
    A = np.zeros((N, N), dtype=np.int8)
    for i in range(N):
        for j in rng.permutation(N):
            if int(A[i].sum()) >= 9:
                break
            if j != i and not A[j, i]:
                A[i, j] = 1
    return A

def h7_descending_polish():
    """h4 + 4000 hill-climbing single-arc flips on the score"""
    rng = np.random.default_rng(7)
    k = max(2, min(5, N // 9))
    base = N // k
    off = (k - 1) // 2
    sizes = [base + off - c for c in range(k)]
    sizes[0] += N - sum(sizes)
    starts = [sum(sizes[:c]) for c in range(k + 1)]
    A = np.zeros((N, N), dtype=np.int8)
    for c in range(k):
        nc = (c + 1) % k
        for u in range(starts[c], starts[c + 1]):
            for v in range(starts[nc], starts[nc + 1]):
                A[u, v] = 1
    best = score(A)[0]
    for _ in range(4000):
        i, j = rng.integers(N, size=2)
        if i == j:
            continue
        old = int(A[i, j])
        if old:
            A[i, j] = 0
        else:
            if A[j, i]:
                continue
            A[i, j] = 1
        s = score(A)
        if s is not None and s[0] <= best:
            best = s[0]
        else:
            A[i, j] = old
    return A

def h8_circulant_polish():
    """circulant {1..8} skeleton + 6000 greedy single-arc flips on the score"""
    rng = np.random.default_rng(11)
    A = np.zeros((N, N), dtype=np.int8)
    for i in range(N):
        for d in range(1, 9):
            A[i, (i + d) % N] = 1
    best = score(A)[0]
    for _ in range(6000):
        i, j = rng.integers(N, size=2)
        if i == j:
            continue
        old = int(A[i, j])
        if old:
            A[i, j] = 0
        else:
            if A[j, i]:
                continue
            A[i, j] = 1
        s = score(A)
        if s is not None and s[0] <= best:
            best = s[0]
        else:
            A[i, j] = old
    return A


def h9_divisor_ring():
    """k-layer pure ring for the smallest usable ring length (k | N, N//k >= 8):
    equal layers, complete bipartite to next layer, impure -> own pure vertex.
    Constructive bound E <= k; falls back to near-equal 3 layers otherwise."""
    k = None
    for kk in range(3, N):
        if N % kk == 0 and N // kk >= 8:
            k = kk
            break
    A = np.zeros((N, N), dtype=np.int8)
    if k is None:
        sizes = [N - 2 * (N // 3), N // 3, N // 3]
        starts = [0, sizes[0], sizes[0] + sizes[1], N]
        for c in range(3):
            nc = (c + 1) % 3
            for u in range(starts[c], starts[c + 1]):
                for v in range(starts[nc], starts[nc + 1]):
                    A[u, v] = 1
            for w in range(starts[c] + 1, starts[c + 1]):
                A[w, starts[c]] = 1
        return A
    t = N // k
    for c in range(k):
        lo, nlo = c * t, ((c + 1) % k) * t
        for u in range(lo, lo + t):
            for v in range(nlo, nlo + t):
                A[u, v] = 1
        for w in range(lo + 1, lo + t):
            A[w, lo] = 1
    return A

if __name__ == '__main__':
    import json
    results = {}
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith('h') and callable(v)}.items()):
        try:
            s = score(fn())
            results[name] = {'doc': fn.__doc__, 'score': list(s)}
            print(f"{name:24s} total {s[0]:7d}  (nsat {s[1]:3d} / excess {s[2]:5d}"
                  f" / minout {s[3]:3d} / sccmiss {s[4]:3d})")
        except Exception as ex:
            print(f"{name:24s} FAILED: {ex}")
    json.dump(results, open('gen0_results.json', 'w'), indent=1)
