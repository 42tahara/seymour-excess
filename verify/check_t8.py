#!/usr/bin/env python3
"""Divergence-gate check of T8, a PROSE derivation, using the public verifier.

Run from the repository root:  python3 verify/check_t8.py
                              python3 verify/check_t8.py --full

Claim under test (elementary, no solver):

  Let k >= 1.  Every oriented graph G on n = 2k+1 vertices with minimum
  out-degree >= k satisfies excess(G) = n.  Hence E_{delta>=k}(2k+1) = 2k+1.
  In particular E_{delta>=8}(17) = 17.

  Proof.  Since n*k = C(n,2), the arc count of G is at least the maximum
  arc count of an oriented graph on n vertices, so equality holds throughout:
  G is a regular tournament of out-degree k.  Let v be any vertex and let
  w in N-(v).  Suppose w not in N++(v).  Then every y in N+(v) receives an
  arc from w (a tournament has no non-adjacent pairs, and y -> w would put
  w at distance exactly 2 from v), so N+(v) subset N+(w).  From w -> v we get
  v in N+(w), while v not in N+(v); hence N+(v) union {v} subset N+(w), i.e.
  |N+(w)| >= k+1 > k, a contradiction.  Therefore N-(v) subset N++(v) and
  |N++(v)| >= |N-(v)| = k.  On the other hand N++(v) is disjoint from
  N+(v) union {v}, so |N++(v)| <= n - 1 - k = k.  Thus |N++(v)| = k = |N+(v)|,
  i.e. the margin d(v) = |N++(v)| - |N+(v)| is 0 at every vertex, and
  excess(G) = sum_v max(0, d(v) + 1) = n.  QED

This script does NOT prove the claim; it is a spot-check of it.  The proof
above is the mathematical content, and the two checks below merely look for a
numerical divergence between that prose and an independent scorer.  The
verifier used is verify/verify_ssnc.py, which shares no code with the search
pipeline; excess is never recomputed here.

Check A -- all circulant tournaments, k = 4..8 (exhaustive within the class).
  For each k, n = 2k+1 and S picks one element of each pair {j, n-j},
  j = 1..k; C_n(S) has v -> (v+d) mod n for d in S.  All 2^k of them are
  regular tournaments of out-degree k.  Totals: 16+32+64+128+256 = 496 graphs,
  with excess 9, 11, 13, 15, 17 respectively.

Check B -- triangle-reversal walk at n = 17 (leaves the circulant class).
  Every circulant is vertex-transitive, so check A is a thin slice of the
  quantifier "all regular tournaments".  Starting from C_17(1..8) we repeatedly
  pick a directed triangle x -> y -> z -> x and reverse all three arcs; this
  preserves every out-degree, so the walk stays inside the space of regular
  tournaments on 17 vertices.  Each sample must satisfy excess == 17.
  Non-vertex-transitivity certificate: for each vertex v we compute the sorted
  out-degree sequence of the sub-tournament induced on N+(v).  A vertex-
  transitive graph has the same profile at every vertex, so two distinct
  profiles prove the sample is not vertex-transitive, hence not circulant.
  (The count of directed triangles through a vertex cannot be used for this:
  on a 17-vertex regular tournament it is the constant 36 at every vertex.)
  The walk is seeded deterministically via random.Random(seed).
"""
import argparse
import itertools
import random
import sys
import time

sys.path.insert(0, 'verify')
from verify_ssnc import verify  # noqa: E402

MAX_REPORT = 5


def circulant(n, S):
    A = [[0] * n for _ in range(n)]
    for v in range(n):
        for d in S:
            A[v][(v + d) % n] = 1
    return A


def check_a(bad):
    total = 0
    for k in range(4, 9):
        n = 2 * k + 1
        count = 0
        for signs in itertools.product([0, 1], repeat=k):
            S = {(j if s == 0 else n - j) for j, s in zip(range(1, k + 1), signs)}
            r = verify(circulant(n, S))
            ok = (r['excess'] == n
                  and r['min_out_degree'] == k
                  and r['margin0_vertices'] == n
                  and r['positive_margin_vertices'] == 0
                  and r['strongly_connected'])
            if not ok:
                bad.append(f"A: k={k} n={n} S={sorted(S)} -> {r}")
            count += 1
        total += count
        print(f"[A] k={k} n={n}: {count} circulant tournaments, "
              f"excess=={n} & delta+=={k} & all tight & strong: "
              f"{not any(s.startswith(f'A: k={k} ') for s in bad)}")
    print(f"[A] total circulant tournaments tested: {total} "
          f"(expected 496), mismatches: "
          f"{sum(1 for s in bad if s.startswith('A: '))}")


def local_profile(A, n, v):
    out = [u for u in range(n) if A[v][u]]
    return tuple(sorted(sum(1 for w in out if A[u][w]) for u in out))


def is_certified_non_transitive(A, n):
    first = local_profile(A, n, 0)
    for v in range(1, n):
        if local_profile(A, n, v) != first:
            return True
    return False


def reverse_a_triangle(A, n, rng):
    while True:
        x, y, z = rng.sample(range(n), 3)
        if A[x][y] and A[y][z] and A[z][x]:
            A[x][y] = A[y][z] = A[z][x] = 0
            A[y][x] = A[z][y] = A[x][z] = 1
            return
        if A[x][z] and A[z][y] and A[y][x]:
            A[x][z] = A[z][y] = A[y][x] = 0
            A[z][x] = A[y][z] = A[x][y] = 1
            return


def rows_of(A):
    return [''.join(str(x) for x in row) for row in A]


def check_b(bad, samples, seed, burn_in, steps):
    n = 17
    rng = random.Random(seed)
    A = circulant(n, range(1, 9))
    for _ in range(burn_in):
        reverse_a_triangle(A, n, rng)
    certified = 0
    for i in range(samples):
        for _ in range(steps):
            reverse_a_triangle(A, n, rng)
        r = verify(A)
        ok = (r['excess'] == n
              and r['min_out_degree'] == 8
              and r['margin0_vertices'] == n
              and r['positive_margin_vertices'] == 0
              and r['strongly_connected'])
        if not ok:
            bad.append(f"B: sample={i} seed={seed} burn_in={burn_in} "
                       f"steps={steps} -> {r} rows={rows_of(A)}")
        if is_certified_non_transitive(A, n):
            certified += 1
    print(f"[B] n=17 triangle-reversal walk: samples={samples} seed={seed} "
          f"burn_in={burn_in} steps/sample={steps}")
    print(f"[B] excess==17 & delta+==8 & all 17 tight & strong at every "
          f"sample: {not any(s.startswith('B: ') for s in bad)}")
    print(f"[B] certified non-vertex-transitive (hence non-circulant) "
          f"samples: {certified}/{samples}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--samples', type=int, default=2000,
                    help='check B samples (default 2000)')
    ap.add_argument('--full', action='store_true',
                    help='check B with 25000 samples')
    ap.add_argument('--seed', type=int, default=20260725,
                    help='deterministic seed for the walk (default 20260725)')
    ap.add_argument('--burn-in', type=int, default=500,
                    help='triangle reversals before the first sample')
    ap.add_argument('--steps', type=int, default=20,
                    help='triangle reversals between samples')
    args = ap.parse_args()
    samples = 25000 if args.full else args.samples

    t0 = time.time()
    bad = []
    check_a(bad)
    check_b(bad, samples, args.seed, args.burn_in, args.steps)
    print(f"elapsed: {time.time() - t0:.1f} s")

    if bad:
        print(f"MISMATCHES: {len(bad)} (showing up to {MAX_REPORT})")
        for s in bad[:MAX_REPORT]:
            print("  " + s)
        return 1
    print("T8 spot-check: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
