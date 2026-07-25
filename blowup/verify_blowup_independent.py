#!/usr/bin/env python3
"""Independent verification of the blow-up sweep (blowup_inverse.py).

    CLAIM UNDER TEST.  Among blow-ups H[n; k] of oriented graphs H on m <= 6
    classes, with minimum out-degree >= 8, excess <= 3 is attainable only when
    3 | N.  Equivalently: for 3 nmid N the family gives excess >= 4.

This file re-derives that conclusion along paths that share no code with
blowup_inverse.py: checks B/C/D use their own construction of the matrix M and
their own closed form, and no polyhedral machinery at all in B.  Check A leaves
the arithmetic entirely and scores real adjacency matrices.

Background (established elsewhere, used here as given):

    A(a) = out-neighbour classes of a in H;  B(a) = classes reached in exactly
    two steps.  Then

      (F1)  N++(u_{a,j}) = union of C_c over c in B(a) \\ A(a)
      (F2)  d(u_{a,j}) = delta_a - min(j, k_a),
            delta_a = sum_{c in B(a)\\A(a)} n_c - sum_{b in A(a)} n_b
      (F3)  contribution of class a = G(n_a, delta_a)
            with G(n, x) = T(x) - T(x - n),  T(y) = (y+1)(y+2)/2 for y >= 0,
            T(y) = 0 for y < 0

G is the truncated form: it is valid for every (n, x), whereas the bare T(x) is
correct only while n > x.  Using T where G is meant OVERSTATES the cost of a
class with delta_a >= n_a, which would silently hide hits -- hence B recomputes
with G from scratch.

k_a = n_a is optimal throughout: d = delta_a - min(j, k_a) is non-increasing in
k_a, and by (F1) the second neighbourhood does not depend on k_a at all.  So no
check here sweeps k.

--------------------------------------------------------------------- results

Recorded from the run of 2026-07-25 (ortools 9.15.6755, numpy on darwin):

    A  73 / 73 witnesses agree, including every degenerate one (classes of
       size 1: (8,1,7,8), (8,1,7,1,7), (1,7,1,7,1,7), (8,1,1,1,5,8), ...)
    B  2,321,385 excess evaluations over all 4,313 quotients at
       N = 25,26,28,29,31,32 -- zero instances of excess <= 3.  171 s.
       This is the independent counterpart of the sweep's 385,622 "LP empty"
       verdicts, reached without any LP.
    C  357 irreducible elements across the 73 feasible recession cones, all
       with 1^T h = 0 (mod 3); largest coordinate 6, box bound 10
    D  146 CP-SAT feasibility models (73 patterns x residues {1,2}), all
       INFEASIBLE, no UNKNOWN, coordinates bounded by 40

--------------------------------------------------------- what is NOT proved

Every check is bounded: B sweeps a window of N, C searches a box, D bounds the
coordinates.  Together they say that no residue-shifting ray and no residue-1/2
base point exists WITHIN THOSE BOUNDS.  A certified "for all N" needs an exact
Hilbert basis (Normaliz / 4ti2), which is not attempted here.  The scope is also
m <= 6 and this construction family only; nothing is claimed about arbitrary
digraphs, for which a statement of this shape would be a lower bound strictly
stronger than Seymour's conjecture.

Usage (from the repository root):
  python3 blowup/verify_blowup_independent.py --check all
  python3 blowup/verify_blowup_independent.py --check b --n-values 25,26,28
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))       # blowup/
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data', 'blowup')
RESULTS = os.path.join(DATA, 'blowup_inverse_results.jsonl')
QUOTIENTS = os.path.join(DATA, 'blowup_inverse_quotients.json')

# N with 3 nmid N, low enough that every composition can be enumerated and high
# enough that a ray of small 1^T weight added to an N = 24 base point lands in
# the window.
DEFAULT_NS = [25, 26, 28, 29, 31, 32]
CONE_BOX = 10       # C: coordinates of a candidate cone element
BASE_BOUND = 40     # D: coordinates of a candidate base point


def T(x):
    """Triangular number, floored at zero below -1 (array-valued)."""
    return np.where(x >= 0, (x + 1) * (x + 2) // 2, 0)


def excess_of(sizes, deltas):
    """Per-class contributions G(n_a, delta_a), summed over the last axis."""
    return (T(deltas) - T(deltas - sizes)).sum(axis=-1)


def matrix_M(H):
    """delta = M n, with M_{a,c} = [c in B(a)\\A(a)] - [c in A(a)].

    Entries lie in {-1, 0, 1}: B(a)\\A(a) and A(a) are disjoint by construction,
    so no column can pick up both terms, and the intra-class tournament enters
    (F2) through min(j, k_a) rather than through delta -- there is no diagonal
    contribution.  Asserted rather than assumed, since a non-{-1,0,1} M would
    change what may be concluded about total unimodularity downstream.
    """
    A = np.array(H)
    direct = A.astype(bool)
    two_step = (A @ A) > 0
    m = len(A)
    M = np.array([[(1 if (two_step[a, c] and not direct[a, c]) else 0)
                   - (1 if direct[a, c] else 0)
                   for c in range(m)] for a in range(m)], dtype=np.int64)
    assert set(np.unique(M)).issubset({-1, 0, 1}), f'M outside {{-1,0,1}}: {M}'
    return M


def compositions(N, m):
    """All (n_1..n_m) with n_a >= 1 summing to N, as an (rows, m) array."""
    rows = []
    for cut in itertools.combinations(range(1, N), m - 1):
        prev, v = 0, []
        for x in cut:
            v.append(x - prev)
            prev = x
        v.append(N - prev)
        rows.append(v)
    return np.array(rows, dtype=np.int64) if rows else np.empty((0, m), np.int64)


def load_hits():
    rows = [json.loads(l) for l in open(RESULTS)]
    return [r for r in rows if r.get('kind') == 'hit' and 'H' in r]


def pattern_of(H, witness):
    """Read the delta-pattern off a witness, without using the sweep's labels.

    Returns (M, deltas, pinned, fixed, negative) where `pinned` are the classes
    whose size is forced to 1 (delta_a >= 1 costs delta_a + 1 already at j = 0,
    so excess <= 3 admits a class of size >= 2 only for delta_a <= 1), `fixed`
    are the classes whose delta is pinned to a non-negative value, and
    `negative` are the free ones with delta_a <= -1 and zero contribution.
    """
    M = matrix_M(H)
    n = np.array(witness)
    d = M @ n
    m = len(H)
    pinned = [a for a in range(m) if d[a] >= 1 and n[a] == 1]
    fixed = [a for a in range(m) if d[a] >= 0]
    negative = [a for a in range(m) if d[a] <= -1]
    return M, d, pinned, fixed, negative


# --------------------------------------------------------------- check A
def check_a():
    """Re-score every witness as a real adjacency matrix.

    Leaves the closed form entirely: builds the blow-up and hands it to
    sonar.score_n.  The construction here is not shared with blowup_inverse.py.
    """
    sys.path.insert(0, os.path.join(ROOT, 'experiments'))
    import sonar

    def build(H, sizes):
        m = len(sizes)
        start = np.cumsum([0] + list(sizes))
        A = np.zeros((int(start[-1]),) * 2, dtype=np.int8)
        for a in range(m):
            for b in range(m):
                if H[a][b]:
                    A[start[a]:start[a + 1], start[b]:start[b + 1]] = 1
            for j in range(sizes[a]):          # k_a = n_a: full transitive
                for l in range(j):             # tournament inside the class
                    A[start[a] + j, start[a] + l] = 1
        return A

    hits = load_hits()
    bad = 0
    for r in hits:
        s = sonar.score_n(build(r['H'], r['witness']))
        ok = s is not None and s[2] == r['excess'] and s[3] >= 8 and s[4] == 0
        if not ok:
            bad += 1
            print(f'  MISMATCH sizes={r["witness"]} closed form={r["excess"]} '
                  f'real graph={None if s is None else s[2]}')
    print(f'[A] witnesses re-scored: {len(hits) - bad}/{len(hits)} agree')
    return bad == 0


# --------------------------------------------------------------- check B
def check_b(ns):
    """Exhaustive sweep over every quotient and every size vector.

    No LP, no ILP, no polyhedra -- the independent counterpart of the sweep's
    "LP empty" verdicts.
    """
    Q = json.load(open(QUOTIENTS))
    hits, evaluated, t0 = [], 0, time.time()
    for m_s, Hs in sorted(Q.items(), key=lambda kv: int(kv[0])):
        m = int(m_s)
        for N in ns:
            C = compositions(N, m)
            if len(C) == 0:
                continue
            for H in Hs:
                A = np.array(H)
                keep = (C @ A.T >= 8).all(axis=1)      # min out-degree >= 8
                if not keep.any():
                    continue
                sizes = C[keep]
                deltas = sizes @ matrix_M(H).T
                # excess <= 3 forces every delta_a <= 2: class a contributes
                # delta_a + 1 from j = 0 alone.
                keep2 = (deltas <= 2).all(axis=1)
                if not keep2.any():
                    continue
                sizes, deltas = sizes[keep2], deltas[keep2]
                phi = excess_of(sizes, deltas)
                evaluated += len(sizes)
                if int(phi.min()) <= 3:
                    j = int(phi.argmin())
                    hits.append({'m': m, 'N': N, 'H': H,
                                 'sizes': sizes[j].tolist(),
                                 'excess': int(phi.min())})
                    print(f'  HIT m={m} N={N} sizes={sizes[j].tolist()} '
                          f'excess={int(phi.min())}')
    print(f'[B] {evaluated:,} excess evaluations over {sum(len(v) for v in Q.values())} '
          f'quotients at N in {ns}, {time.time() - t0:.0f}s')
    print(f'    excess <= 3 with 3 nmid N: {len(hits)} found')
    return not hits


# --------------------------------------------------------------- check C
def check_c(box=CONE_BOX):
    """Irreducible elements of each feasible recession cone.

    The cone is  { r >= 0 : r_a = 0 for pinned a, (Mr)_a = 0 for fixed a,
                             (Mr)_a <= 0 for negative a }.
    If every element h has 1^T h = 0 (mod 3) then no ray can move N between
    residue classes while holding the excess pattern.  Irreducibility inside the
    box is genuine irreducibility: a decomposition c = a + b has a, b <= c
    coordinatewise, so both summands are in the box whenever c is.
    """
    seen, irreducibles, offenders, largest = set(), 0, 0, 0
    for r in load_hits():
        M, d, pinned, fixed, negative = pattern_of(r['H'], r['witness'])
        m = len(r['H'])
        key = (tuple(map(tuple, r['H'])), tuple(d),
               tuple(np.array(r['witness']) == 1))
        if key in seen:
            continue
        seen.add(key)
        free = [a for a in range(m) if a not in pinned]
        grid = np.array(list(itertools.product(range(box + 1), repeat=len(free))),
                        dtype=np.int64)
        R = np.zeros((len(grid), m), dtype=np.int64)
        R[:, free] = grid
        D = R @ M.T
        ok = R.sum(axis=1) > 0
        if fixed:
            ok &= (D[:, fixed] == 0).all(axis=1)
        if negative:
            ok &= (D[:, negative] <= 0).all(axis=1)
        cone = set(map(tuple, R[ok]))
        for c in cone:
            ca = np.array(c)
            if any(tuple(ca - np.array(o)) in cone
                   for o in cone if o != c and all(np.array(o) <= ca)):
                continue
            irreducibles += 1
            largest = max(largest, max(c))
            if sum(c) % 3:
                offenders += 1
                print(f'  RESIDUE LEAK ray={c} 1^T r={sum(c)} delta={d.tolist()}')
    print(f'[C] {len(seen)} distinct patterns, {irreducibles} irreducible cone '
          f'elements in [0,{box}]')
    print(f'    largest coordinate {largest} (box {box}); '
          f'elements with 1^T h != 0 mod 3: {offenders}')
    if largest >= box:
        print('    WARNING: box may not contain the whole Hilbert basis')
    return offenders == 0 and largest < box


# --------------------------------------------------------------- check D
def check_d(bound=BASE_BOUND):
    """Base points: is any feasible size vector at residue 1 or 2 mod 3?

    Check C constrains the directions; this constrains the starting points.
    CP-SAT INFEASIBLE is sound (HANDOFF section 8), but only for the bounded
    model -- hence the explicit coordinate bound in the report.
    """
    from ortools.sat.python import cp_model

    seen, found, unknown = set(), [], 0
    for r in load_hits():
        H = r['H']
        M, d, pinned, _, _ = pattern_of(H, r['witness'])
        m, A = len(H), np.array(H)
        key = (tuple(map(tuple, H)), tuple(d), tuple(np.array(r['witness']) == 1))
        if key in seen:
            continue
        seen.add(key)
        for residue in (1, 2):
            mo = cp_model.CpModel()
            n = [mo.NewIntVar(1, bound, f'n{a}') for a in range(m)]
            for a in pinned:
                mo.Add(n[a] == 1)
            for a in range(m):
                lhs = sum(int(M[a, c]) * n[c] for c in range(m))
                mo.Add(lhs == int(d[a])) if d[a] >= 0 else mo.Add(lhs <= -1)
                mo.Add(sum(int(A[a, b]) * n[b] for b in range(m)) >= 8)
            N = mo.NewIntVar(m, m * bound, 'N')
            mo.Add(N == sum(n))
            q = mo.NewIntVar(0, m * bound, 'q')
            mo.Add(N == 3 * q + residue)
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 10
            status = solver.Solve(mo)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                found.append((H, d.tolist(), [solver.Value(x) for x in n], residue))
                print(f'  BASE POINT AT RESIDUE {residue}: '
                      f'{[solver.Value(x) for x in n]} delta={d.tolist()}')
            elif status != cp_model.INFEASIBLE:
                unknown += 1
    print(f'[D] {len(seen)} patterns x residues {{1,2}} = {len(seen) * 2} models, '
          f'coordinates <= {bound}')
    print(f'    feasible at residue 1 or 2: {len(found)}; UNKNOWN: {unknown}')
    return not found and unknown == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', default='all', choices=['all', 'a', 'b', 'c', 'd'])
    ap.add_argument('--n-values', default=','.join(map(str, DEFAULT_NS)),
                    help='comma-separated N for check B (all must satisfy 3 nmid N)')
    args = ap.parse_args()

    ns = [int(x) for x in args.n_values.split(',')]
    assert all(n % 3 for n in ns), 'check B is about 3 nmid N only'

    outcomes = {}
    if args.check in ('all', 'a'):
        outcomes['A'] = check_a()
    if args.check in ('all', 'b'):
        outcomes['B'] = check_b(ns)
    if args.check in ('all', 'c'):
        outcomes['C'] = check_c()
    if args.check in ('all', 'd'):
        outcomes['D'] = check_d()

    print()
    for name, ok in outcomes.items():
        print(f'  {name}: {"pass" if ok else "FAIL"}')
    return 0 if all(outcomes.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
