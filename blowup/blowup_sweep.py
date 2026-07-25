#!/usr/bin/env python3
"""Closed-form excess of capped-tournament BLOW-UPS, and an exhaustive sweep of
the quotient space.

    G = H[n_0, ..., n_{m-1}; c_0, ..., c_{m-1}]

is built from a quotient ORIENTED graph H on m vertices (no loops, no digons)
by replacing vertex a of H with a class C_a of n_a vertices
u_{a,0}, ..., u_{a,n_a-1} and taking the arcs

    (R)  u_{a,j} -> u_{b,l}   for all j, l, whenever a -> b in H   (complete
                              bipartite, "ring" arcs)
    (T)  u_{a,j} -> u_{a,l}   for l < min(j, c_a)                  (intra-class
                              transitive tournament, truncated at the cap c_a)

with 0 <= c_a <= n_a.  Vertices are laid out in class blocks in index order:
with st_a = n_0 + ... + n_{a-1}, the vertex u_{a,j} is st_a + j.  This is the
family of upper_bound_family.py generalised from H = C_3 (the directed
triangle) to an arbitrary oriented quotient; upper_bound_family.G_n is
exactly C_3[s_0,s_1,s_2; c_0,c_1,c_2] in this notation, and seed_ring(n,3) is
C_3[n/3,n/3,n/3; 1,1,1].

The point of the generalisation is COST: one candidate is evaluated by O(m^2)
integer arithmetic on the quotient instead of the O(n^3) boolean matrix
products of evaluate.py, so the whole space of quotients and class-size
vectors can be swept exhaustively.

--------------------------------------------------------------------- theory

Notation for H:  A(a) = out-neighbourhood of a in H,
                 B(a) = union of A(b) over b in A(a)  (the 2-step reach),
                 C(a) = B(a) minus A(a),
                 S1(a) = sum of n_b over b in A(a),
                 S2(a) = sum of n_c over c in C(a).

LEMMA Q0 (well-formedness).
  (a) No loops: (T) needs l < min(j, c_a) <= j.
  (b) No digons: a (T) arc goes strictly downwards in j inside one class, and
      a (R) arc between C_a and C_b would need both a->b and b->a in H, i.e. a
      digon of H.  (R) and (T) arcs never join the same pair.  So G is an
      oriented graph iff H is.
  (c) outdeg(u_{a,j}) = S1(a) + min(j, c_a), minimised at j = 0:
      delta(G) = min_a S1(a).  The caps do not affect the minimum out-degree.
  (d) The class partition is a congruence: reachability in G projects onto
      reachability in H, and if H is strongly connected with m >= 2 then from
      any u one reaches all of C_b for some b in A(a), hence (following a walk
      in H) every class entirely, and re-enters C_a completely along an (R)
      arc.  So G is strongly connected  <=>  H is strongly connected (m >= 2).

LEMMA Q1 (second neighbourhood).   N++(u_{a,j}) = union of C_c over c in C(a),
      hence  |N++(u_{a,j})| = S2(a),  INDEPENDENT of j and of every cap.

  Proof.  Write p = min(j, c_a), so N+(u_{a,j}) = U_{b in A(a)} C_b u P with
  P = {u_{a,0}, ..., u_{a,p-1}}.  Take out-neighbourhoods of everything in it.
    * An intra-class target u_{a,l} (l < p <= c_a) has
      N+(u_{a,l}) = U_{b in A(a)} C_b u {u_{a,0},...,u_{a,l-1}}  (min(l,c_a)=l
      because l < c_a), which is contained in N+(u_{a,j}) since l-1 < p.  So
      the (T) arcs contribute NOTHING new -- the "free out-degree" mechanism.
    * A vertex u_{b,l} with b in A(a) has
      N+(u_{b,l}) = U_{c in A(b)} C_c u {u_{b,0},...,u_{b,min(l,c_b)-1}}.
      Unioning over all l in [0, n_b) gives U_{c in A(b)} C_c u I_b with
      I_b = {u_{b,0}, ..., u_{b,min(n_b - 1, c_b) - 1}} contained in C_b.
  Hence the 2-step reach is  (U_{c in B(a)} C_c) u (U_{b in A(a)} I_b), and the
  second term is inside U_{b in A(a)} C_b, which is inside N+(u_{a,j}) and is
  therefore deleted.  Deleting N+(u_{a,j}) also removes U_{b in A(a)} C_b,
  leaving U_{c in B(a) minus A(a)} C_c.  Finally a is NOT in B(a): a in B(a) would
  mean a -> b -> a for some b, a digon of H, excluded by Q0(b).  So the deleted
  set P u {u_{a,j}} (which lives in C_a) is disjoint from what is left. []

  NOTE where this differs from the C_3 case of upper_bound_family: there
  B(a) = {a+2} and A(a) = {a+1} are disjoint singletons, so "N++ = the
  next-but-one layer".  In general B(a) and A(a) overlap and the SET
  DIFFERENCE is what survives; classes reachable in two steps that are also
  reachable in one step contribute nothing.

LEMMA Q2 (margins).   d(u_{a,j}) = Delta_a - min(j, c_a),  where

      Delta_a := S2(a) - S1(a) = sum_{c in C(a)} n_c - sum_{b in A(a)} n_b.

  Proof.  Q1 and |N+(u_{a,j})| = S1(a) + min(j, c_a). []

  In particular d(u_{a,0}) = Delta_a: G has excess 0 (i.e. IS a counterexample
  to Seymour, if additionally delta(G) >= 8 and G is strongly connected) if and
  only if  Delta_a <= -1  for every class a.  The blow-up question is thus a
  purely arithmetic condition on (H, n).

LEMMA Q3 (per-class excess, closed form).  With e = Delta_a + 1,
k = min(c_a, n_a), t = min(k, max(e, 0)):

      X(a) := sum_{j=0}^{n_a - 1} max(0, d(u_{a,j}) + 1)
            = t*e - t*(t-1)/2 + (n_a - c_a)^+ * max(0, e - c_a).

  Proof.  For j < k the summand is max(0, e - j), nonzero exactly for
  j <= e - 1, i.e. for the t values j = 0..t-1, giving e + (e-1) + ... +
  (e-t+1) = t*e - t(t-1)/2.  For j >= c_a (only when n_a > c_a) the summand is
  the constant max(0, e - c_a), occurring n_a - c_a times. []

  excess(G) = sum_a X(a),  and excess(G) = evaluate.score(G)[0] whenever
  delta(G) >= 8 and G is strongly connected (degdef = sccmiss = 0).

LEMMA Q4 (the caps collapse).  X(a) is NON-INCREASING in c_a and constant for
c_a >= min(n_a, max(0, Delta_a + 1)).  Hence the cap dimension of the search
space can be dropped: the optimal cap is

      c_a* = min(n_a, max(0, Delta_a + 1))

and every larger cap gives the same excess (with the same minimum out-degree,
by Q0(c), and the same strong connectivity, by Q0(d)).

  Proof.  Let f(c) = X(a) as a function of c in [0, n_a].  For c >= e the tail
  term vanishes and t = min(e, n_a) no longer depends on c, so f is constant
  there.  For c < min(e, n_a): f(c) = c*e - c(c-1)/2 + (n_a - c)(e - c) and
      f(c+1) - f(c) = (e - c) + [(n_a-c-1)(e-c-1) - (n_a-c)(e-c)]
                    = (e - c) - (n_a - c) - (e - c) + 1 = c + 1 - n_a <= 0
  for c + 1 <= n_a. []

  Sanity: with c_a = c_a* and Delta_a + 1 <= n_a one gets the triangular
  number X(a) = (Delta_a+1)(Delta_a+2)/2 = T(Delta_a) of upper_bound_family
  Lemma 3, so THEOREM there is the special case H = C_3, n = near-equal.

--------------------------------------------------------------------- sweep

For fixed n, the sweep runs over all non-isomorphic oriented H with m <= mmax
vertices that are strongly connected, and over all compositions n = n_0 + ...
+ n_{m-1} into positive parts, deduplicated by the action of Aut(H) and pruned
by  min_a S1(a) >= delta  (Q0(c)).  Caps are fixed to c* by Q4.  Nothing is
approximated: for the stated (n, m) range this is an exhaustive statement
about the whole blow-up family.

An excess strictly below the value 3 + [3 nmid n] proved in
upper_bound_family.py would IMPROVE that theorem; the sweep stops at the first
such hit, dumps the matrix and asks for evaluate.py / verify_ssnc.py
confirmation.

Usage (from the repository root):
  python3 blowup/blowup_sweep.py --verify           # all three calibrations
  python3 blowup/blowup_sweep.py --verify-family    # 1. reproduce G_n, n=24..150
  python3 blowup/blowup_sweep.py --verify-sha1      # 2. data/sonar_best/, 3|n
  python3 blowup/blowup_sweep.py --verify-random -k 2000   # 3. vs the judge
  python3 blowup/blowup_sweep.py --counts --mmax 5  # size of the quotient space
  python3 blowup/blowup_sweep.py --sweep --lo 24 --hi 40 --mmax 5
  python3 blowup/blowup_sweep.py --report
"""
import argparse
import glob
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))       # blowup/
ROOT = os.path.dirname(BASE)
EXPERIMENTS = os.path.join(ROOT, 'experiments')         # evaluate.py
CONSTRUCTIONS = os.path.join(ROOT, 'constructions')     # upper_bound_family.py
DATA = os.path.join(ROOT, 'data', 'blowup')
SONAR_BEST = os.path.join(ROOT, 'data', 'sonar_best')
RESULTS = os.path.join(DATA, 'blowup_sweep_results.jsonl')
DELTA = 8
# Calibration 2 compares the stored 3 | n witnesses against the C_3 construction.
# The guard below exists so that an empty or shrunken glob cannot pass silently.
# It is DERIVED from what is actually shipped, never hard-coded: a hard-coded
# floor has to be raised by hand whenever the witness set grows, and the one
# thing a guard must not do is quietly stop guarding.  Every stored witness with
# 3 | n and n >= 24 must be reached by the loop; one whose excess is not 3 would
# be skipped, and that is a failure too, since the family attains excess 3 at
# every such order.  See verify_sha1() for what this does and does not catch.


# ------------------------------------------------------------ quotient basics
def out_sets(H):
    """A(a) as a list of frozensets.  H is an m x m 0/1 matrix (tuple/array)."""
    m = len(H)
    return [frozenset(b for b in range(m) if H[a][b]) for a in range(m)]


def second_sets(H):
    """C(a) = B(a) \\ A(a) with B(a) = union of A(b) for b in A(a)."""
    A = out_sets(H)
    return [frozenset().union(*(A[b] for b in A[a])) - A[a] if A[a]
            else frozenset() for a in range(len(H))]


def is_oriented(H):
    m = len(H)
    return all(not H[a][a] for a in range(m)) and \
        all(not (H[a][b] and H[b][a]) for a in range(m) for b in range(a + 1, m))


def is_strongly_connected(H):
    m = len(H)
    if m == 1:
        return True

    def reach(adj):
        seen, stack = {0}, [0]
        while stack:
            v = stack.pop()
            for w in range(m):
                if adj(v, w) and w not in seen:
                    seen.add(w)
                    stack.append(w)
        return len(seen) == m

    return reach(lambda v, w: H[v][w]) and reach(lambda v, w: H[w][v])


def indicator_matrices(H):
    """(M1, M2) with M1[a,b] = [b in A(a)], M2[a,c] = [c in C(a)]."""
    m = len(H)
    M1 = np.array([[1 if H[a][b] else 0 for b in range(m)] for a in range(m)],
                  dtype=np.int64)
    S = second_sets(H)
    M2 = np.array([[1 if c in S[a] else 0 for c in range(m)] for a in range(m)],
                  dtype=np.int64)
    return M1, M2


def deltas(H, sizes):
    """Delta_a = S2(a) - S1(a)  (Lemma Q2)."""
    M1, M2 = indicator_matrices(H)
    n = np.asarray(sizes, dtype=np.int64)
    return (M2 @ n - M1 @ n).tolist()


def out_sums(H, sizes):
    """S1(a) = sum of n_b over b in A(a); min over a is delta(G) (Q0(c))."""
    M1, _ = indicator_matrices(H)
    return (M1 @ np.asarray(sizes, dtype=np.int64)).tolist()


def optimal_caps(H, sizes, D=None):
    """c_a* = min(n_a, max(0, Delta_a + 1))  (Lemma Q4)."""
    D = deltas(H, sizes) if D is None else D
    return [int(min(sizes[a], max(0, D[a] + 1))) for a in range(len(H))]


def class_excess(delta_a, cap, size):
    """X(a) of Lemma Q3."""
    e = delta_a + 1
    k = min(cap, size)
    t = min(k, max(e, 0))
    tail = (size - cap) * max(0, e - cap) if size > cap else 0
    return t * e - t * (t - 1) // 2 + tail


def excess_closed(H, sizes, caps=None):
    """excess(G) = sum_a X(a) by the closed form; no matrix is built."""
    D = deltas(H, sizes)
    caps = optimal_caps(H, sizes, D) if caps is None else caps
    return sum(class_excess(D[a], caps[a], sizes[a]) for a in range(len(H)))


def margins_closed(H, sizes, caps=None):
    """d(v) for every vertex in the block layout (Lemma Q2)."""
    D = deltas(H, sizes)
    caps = optimal_caps(H, sizes, D) if caps is None else caps
    out = []
    for a in range(len(H)):
        out += [D[a] - min(j, caps[a]) for j in range(sizes[a])]
    return np.array(out, dtype=np.int64)


def build(H, sizes, caps=None):
    """Adjacency matrix of the blow-up, block layout, int8."""
    m = len(H)
    caps = optimal_caps(H, sizes) if caps is None else caps
    st = [int(sum(sizes[:a])) for a in range(m + 1)]
    n = st[m]
    A = np.zeros((n, n), dtype=np.int8)
    for a in range(m):
        for b in range(m):
            if H[a][b]:
                A[st[a]:st[a + 1], st[b]:st[b + 1]] = 1
        for j in range(sizes[a]):
            for l in range(min(j, caps[a])):
                A[st[a] + j, st[a] + l] = 1
    return A


def margins_numpy(A):
    """d(v) measured on the matrix (local mirror of evaluate.py's arithmetic)."""
    n = len(A)
    A = np.asarray(A).astype(np.int32)
    out1 = A.sum(axis=1)
    reach2 = (A @ A) > 0
    Ab = A.astype(bool)
    return (reach2 & ~Ab & ~np.eye(n, dtype=bool)).sum(axis=1) - out1


def graph_sha1(A):
    """Repo convention: sha1 of json.dumps(INT-keyed adjacency, sort_keys)."""
    adj = {int(i): [int(j) for j in np.nonzero(A[i])[0]] for i in range(len(A))}
    return adj, hashlib.sha1(
        json.dumps(adj, sort_keys=True).encode()).hexdigest()


def theorem_excess(n):
    """upper_bound_family: E_{delta>=8}(n) <= 3 + [3 nmid n] for n >= 24."""
    return 3 + (1 if n % 3 else 0)


# ------------------------------------------------- enumeration of quotients H
_ORIENTED_CACHE = {}


def _pairs(m):
    return [(i, j) for i in range(m) for j in range(i + 1, m)]


def _decode(code, m):
    arcs = []
    for (i, j) in _pairs(m):
        t, code = code % 3, code // 3
        if t == 1:
            arcs.append((i, j))
        elif t == 2:
            arcs.append((j, i))
    return frozenset(arcs)


def _encode(arcs, m):
    code = 0
    for k, (i, j) in enumerate(_pairs(m)):
        code += (1 if (i, j) in arcs else 2 if (j, i) in arcs else 0) * 3 ** k
    return code


def _matrix(arcs, m):
    return tuple(tuple(1 if (a, b) in arcs else 0 for b in range(m))
                 for a in range(m))


def enumerate_oriented(m):
    """All oriented graphs on m labelled-then-canonicalised vertices.

    Returns [(H, auts)] with one representative per isomorphism class and
    auts = the list of permutations p with p(H) = H (i.e. Aut(H)).

    Method: orbit marking over the 3^C(m,2) trit encodings (0 = no arc,
    1 = i->j, 2 = j->i).  Total work is (#classes) * m!, not 3^C(m,2) * m!.
    """
    if m in _ORIENTED_CACHE:
        return _ORIENTED_CACHE[m]
    perms = list(itertools.permutations(range(m)))
    total = 3 ** len(_pairs(m))
    seen = bytearray(total)
    reps = []
    for code in range(total):
        if seen[code]:
            continue
        arcs = _decode(code, m)
        auts, orbit = [], set()
        for p in perms:
            c2 = _encode(frozenset((p[u], p[v]) for u, v in arcs), m)
            orbit.add(c2)
            if c2 == code:
                auts.append(p)
        for c in orbit:
            seen[c] = 1
        reps.append((_matrix(arcs, m), auts))
    _ORIENTED_CACHE[m] = reps
    return reps


def enumerate_quotients(m, strongly_connected=True):
    reps = enumerate_oriented(m)
    if strongly_connected:
        reps = [(H, g) for H, g in reps if is_strongly_connected(H)]
    return reps


# ------------------------------------------------------- size-vector machinery
_COMP_CACHE = {}


def compositions(n, m):
    """All (n_0,...,n_{m-1}) with n_a >= 1 and sum n_a = n, as an int64 array."""
    if (n, m) in _COMP_CACHE:
        return _COMP_CACHE[(n, m)]
    out = []
    cur = [0] * m

    def rec(pos, rem):
        if pos == m - 1:
            cur[pos] = rem
            out.append(tuple(cur))
            return
        for v in range(1, rem - (m - 1 - pos) + 1):
            cur[pos] = v
            rec(pos + 1, rem - v)

    if n >= m >= 1:
        rec(0, n)
    arr = np.array(out, dtype=np.int64).reshape(-1, m)
    _COMP_CACHE[(n, m)] = arr
    return arr


def _canonical_mask(comps, auts, base):
    """Rows that are lexicographically minimal in their Aut(H) orbit."""
    m = comps.shape[1]
    w = base ** np.arange(m - 1, -1, -1, dtype=np.int64)
    key = comps @ w
    mask = np.ones(len(comps), dtype=bool)
    for p in auts:
        if p == tuple(range(m)):
            continue
        mask &= key <= (comps[:, list(p)] @ w)
    return mask


def _excess_vectorised(comps, M1, M2):
    """(S1, Delta, excess-at-optimal-cap) for every row of comps."""
    S1 = comps @ M1.T
    D = comps @ M2.T - S1
    e = D + 1
    t = np.minimum(comps, np.maximum(e, 0))
    X = t * e - t * (t - 1) // 2
    return S1, D, X.sum(axis=1)


# --------------------------------------------------------------------- sweep
def sweep_n(n, mmax, delta=DELTA, alarm_below=None, allow_disconnected=False,
            verbose=False, dedup=True):
    """Exhaustive sweep of the blow-up family at order n, m <= mmax.

    Returns a record dict; 'alarm' is set as soon as a candidate beats
    alarm_below (default: the upper_bound_family value for this n).
    dedup=False keeps the Aut(H)-equivalent size vectors (test knob: the
    minimum must not depend on it, only the candidate count).
    """
    if alarm_below is None:
        alarm_below = theorem_excess(n)
    t0 = time.time()
    best = None
    by_m = {}
    total = 0
    alarm = None
    for m in range(1, mmax + 1):
        # m = 1 is strongly connected as a QUOTIENT but its blow-up is a capped
        # transitive tournament, which is not (it also has S1 = 0 < delta, so
        # the degree prune below removes it anyway -- this is belt and braces).
        reps = [] if (m == 1 and not allow_disconnected) else \
            enumerate_quotients(m, not allow_disconnected)
        comps = compositions(n, m)
        cnt = 0
        if len(comps) == 0 or not reps:
            by_m[m] = {'quotients': len(reps), 'compositions': int(len(comps)),
                       'candidates': 0}
            continue
        base = int(comps.max()) + 1
        for H, auts in reps:
            M1, M2 = indicator_matrices(H)
            S1, D, X = _excess_vectorised(comps, M1, M2)
            sel = (S1 >= delta).all(axis=1)
            if not sel.any():
                continue
            if dedup:
                sel &= _canonical_mask(comps, auts, base)
            k = int(sel.sum())
            if not k:
                continue
            cnt += k
            idx = np.flatnonzero(sel)
            i = idx[int(np.argmin(X[idx]))]
            val = int(X[i])
            if best is None or val < best[0]:
                best = (val, H, comps[i].tolist(), D[i].tolist(),
                        int(S1[i].min()))
            if val < alarm_below and alarm is None:
                alarm = (val, H, comps[i].tolist())
                by_m[m] = {'quotients': len(reps),
                           'compositions': int(len(comps)), 'candidates': cnt}
                return _record(n, mmax, delta, best, by_m, total + cnt, t0,
                               alarm, alarm_below, partial=True)
        by_m[m] = {'quotients': len(reps), 'compositions': int(len(comps)),
                   'candidates': cnt}
        total += cnt
        if verbose:
            print(f'  n={n} m={m}: {len(reps)} quotients, {len(comps)} '
                  f'compositions, {cnt} candidates, best so far '
                  f'{best[0] if best else None}', flush=True)
    return _record(n, mmax, delta, best, by_m, total, t0, alarm, alarm_below)


def _record(n, mmax, delta, best, by_m, total, t0, alarm, alarm_below,
            partial=False):
    rec = {'n': n, 'mmax': mmax, 'delta': delta,
           'theorem_excess': theorem_excess(n), 'alarm_below': alarm_below,
           'candidates': int(total), 'by_m': by_m,
           'seconds': round(time.time() - t0, 2), 'partial': partial,
           'alarm': alarm is not None}
    if best is not None:
        val, H, sizes, D, minout = best
        caps = optimal_caps(H, sizes)
        rec['min_excess'] = val
        rec['best'] = {'m': len(H), 'H': [list(r) for r in H],
                       'sizes': sizes, 'caps': caps, 'deltas': D,
                       'min_outdeg': minout}
    else:
        rec['min_excess'] = None
        rec['best'] = None
    return rec


def dump_witness(H, sizes, caps, path):
    """Write the blow-up as a witness JSON (for verify/verify_ssnc.py)."""
    A = build(H, sizes, caps)
    adj, sha = graph_sha1(A)
    json.dump({'N': int(len(A)), 'delta': DELTA, 'sha1_kind': 'adjacency_json',
               'graph_sha1': sha, 'source': 'blowup_sweep',
               'quotient': {'H': [list(r) for r in H], 'sizes': list(sizes),
                            'caps': list(caps)},
               'excess_closed_form': excess_closed(H, sizes, caps),
               'adj': adj}, open(path, 'w'))
    return sha


# --------------------------------------------------------- evaluate.py bridge
_BATCH = ('import json,sys,numpy as np,evaluate\n'
          'out=[]\n'
          'for M in json.load(sys.stdin):\n'
          '    s=evaluate.score(np.array(M,dtype=np.int8))\n'
          '    out.append(None if s is None else list(s))\n'
          'sys.stdout.write(json.dumps(out))\n')


def evaluate_batch(mats, n, delta=DELTA):
    """evaluate.score for many n x n matrices in ONE subprocess (it fixes N at
    import time, so one call per distinct n)."""
    env = dict(os.environ, SEYMOUR_N=str(n), SEYMOUR_DELTA=str(delta))
    r = subprocess.run([sys.executable, '-c', _BATCH],
                       input=json.dumps([np.asarray(M).tolist() for M in mats]),
                       capture_output=True, text=True, env=env,
                       cwd=EXPERIMENTS, check=True)
    return json.loads(r.stdout)


# --------------------------------------------------------------- calibration
C3 = ((0, 1, 0), (0, 0, 1), (1, 0, 0))       # the directed triangle


def verify_family(lo=24, hi=150, quiet=False):
    """1. Reproduce upper_bound_family.G_n exactly, both variants."""
    sys.path.insert(0, CONSTRUCTIONS)
    import upper_bound_family as U
    bad = 0
    for n in range(lo, hi + 1):
        sizes, _ = U.layers(n)
        for variant in U.VARIANTS:
            caps = U.caps(n, variant)
            errs = []
            if not (build(C3, sizes, caps) == U.construct(n, variant)).all():
                errs.append('matrix')
            if (margins_closed(C3, sizes, caps)
                    != U.predicted_margins(n, variant)).any():
                errs.append('margins')
            if excess_closed(C3, sizes, caps) != U.predicted_excess(n):
                errs.append('excess')
            if deltas(C3, sizes) != U.imbalances(n):
                errs.append('deltas')
            if excess_closed(C3, sizes) != U.predicted_excess(n):
                errs.append('optimal-cap-excess')
            if min(out_sums(C3, sizes)) < 8:
                errs.append('mindeg')
            if errs:
                bad += 1
                print(f'  n={n} {variant}: MISMATCH {errs}')
    if not quiet:
        print(f'1. family reproduction, n={lo}..{hi}, 2 variants: '
              f'{2 * (hi - lo + 1) - bad}/{2 * (hi - lo + 1)} exact '
              f'(matrix, margins, deltas, excess, optimal-cap excess)')
    return bad


def verify_sha1(quiet=False):
    """2. graph_sha1 of C_3[n/3,n/3,n/3; 1,1,1] vs the stored 3|n witnesses."""
    hits = bad = expected = 0
    for path in sorted(glob.glob(os.path.join(SONAR_BEST, '*.json'))):
        d = json.load(open(path))
        n = int(d['N'])
        if n % 3 or n < 24:
            continue
        expected += 1          # every such witness must be reached below
        if d['score'][2] != 3:
            bad += 1
            print(f'  {os.path.basename(path)}: 3|n witness has excess '
                  f'{d["score"][2]}, expected 3')
            continue
        sizes = [n // 3] * 3
        sha = graph_sha1(build(C3, sizes, [1, 1, 1]))[1]
        hits += 1
        if sha != d['graph_sha1']:
            bad += 1
            print(f'  {os.path.basename(path)}: sha1 {sha[:8]} != '
                  f'{d["graph_sha1"][:8]}')
        elif excess_closed(C3, sizes, [1, 1, 1]) != d['score'][2]:
            bad += 1
            print(f'  {os.path.basename(path)}: closed-form excess mismatch')
    # This guard catches an EMPTY glob only -- both counts are derived from the
    # files present, so deleting a witness lowers both and passes here.  That is
    # deliberate: deletion is caught by verify-hashes (the manifest lists the
    # file) and by verify-m1 (which reports the order as missing), both of which
    # were checked to exit non-zero on a removed witness.  Duplicating it here
    # would need a hard-coded count, which is the thing being avoided.
    if hits != expected or expected == 0:
        bad += 1
        print(f'  guard: reached {hits} of {expected} stored 3|n witnesses '
              f'(n >= 24); the glob is empty')
    if not quiet:
        print(f'2. stored 3|n witnesses (data/sonar_best/): {hits - bad}/{hits} '
              f'graph_sha1 identical to the quotient construction')
    return bad, hits


def random_case(rng, mlo=2, mhi=7, slo=1, shi=6):
    """A random (H, sizes, caps): oriented H (not necessarily connected)."""
    m = int(rng.integers(mlo, mhi + 1))
    H = [[0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            t = int(rng.integers(0, 3))
            if t == 1:
                H[i][j] = 1
            elif t == 2:
                H[j][i] = 1
    H = tuple(tuple(r) for r in H)
    sizes = [int(rng.integers(slo, shi + 1)) for _ in range(m)]
    if int(rng.integers(0, 4)) == 0:
        caps = optimal_caps(H, sizes)
    else:
        caps = [int(rng.integers(0, s + 1)) for s in sizes]
    return H, sizes, caps


def verify_random(trials=2000, seed=20260725, quiet=False):
    """3. Closed form vs the judge, on random (H, sizes, caps)."""
    rng = np.random.default_rng(seed)
    cases, by_n = [], {}
    for _ in range(trials):
        H, sizes, caps = random_case(rng)
        A = build(H, sizes, caps)
        cases.append((H, sizes, caps, A))
        by_n.setdefault(len(A), []).append(len(cases) - 1)
    bad_margin = bad_excess = bad_n2 = bad_deg = 0
    # local numpy check first (per-vertex, free)
    for H, sizes, caps, A in cases:
        if (margins_numpy(A) != margins_closed(H, sizes, caps)).any():
            bad_margin += 1
        st = [int(sum(sizes[:a])) for a in range(len(H) + 1)]
        S = second_sets(H)
        want = [sum(sizes[c] for c in S[a]) for a in range(len(H))]
        outs = [set(np.nonzero(A[v])[0].tolist()) for v in range(len(A))]
        for a in range(len(H)):
            for j in range(sizes[a]):
                v = st[a] + j
                n2 = set().union(*(outs[u] for u in outs[v])) if outs[v] else set()
                n2 -= outs[v]
                n2.discard(v)
                if len(n2) != want[a]:
                    bad_n2 += 1
        if min(out_sums(H, sizes)) != int(A.sum(axis=1).min()):
            bad_deg += 1
    # the judge, batched by n
    for n, idxs in sorted(by_n.items()):
        scores = evaluate_batch([cases[i][3] for i in idxs], n)
        for i, sc in zip(idxs, scores):
            H, sizes, caps, _ = cases[i]
            if sc is None or sc[2] != excess_closed(H, sizes, caps):
                bad_excess += 1
                print(f'  MISMATCH H={H} sizes={sizes} caps={caps}: '
                      f'evaluate {sc} vs closed form '
                      f'{excess_closed(H, sizes, caps)}')
    if not quiet:
        print(f'3. random calibration, {trials} cases '
              f'(n={min(by_n)}..{max(by_n)}, {len(by_n)} distinct orders):')
        print(f'   excess vs evaluate.py : {trials - bad_excess}/{trials}')
        print(f'   per-vertex margins    : {trials - bad_margin}/{trials}')
        print(f'   |N++| = S2(a) (Q1)    : '
              f'{"OK" if not bad_n2 else str(bad_n2) + " BAD vertices"}')
        print(f'   min out-degree (Q0c)  : {trials - bad_deg}/{trials}')
    return bad_excess + bad_margin + bad_n2 + bad_deg


# --------------------------------------------------------------------- CLI
def cmd_counts(mmax, lo, hi, delta=DELTA):
    print(f'oriented quotients up to isomorphism (no loops, no digons):')
    print(f'{"m":>3} {"labelled":>10} {"non-isomorphic":>15} '
          f'{"strongly conn.":>15}')
    for m in range(1, mmax + 1):
        reps = enumerate_oriented(m)
        sc = sum(1 for H, _ in reps if is_strongly_connected(H))
        print(f'{m:3d} {3 ** len(_pairs(m)):10d} {len(reps):15d} {sc:15d}')
    print('\ncomposition counts C(n-1, m-1) per n (before Aut-dedup and '
          f'before the delta>={delta} prune):')
    print(f'{"n":>4} ' + ' '.join(f'{"m=" + str(m):>9}' for m in
                                  range(1, mmax + 1)) + f' {"total":>10}')
    for n in range(lo, hi + 1):
        row = [len(compositions(n, m)) for m in range(1, mmax + 1)]
        print(f'{n:4d} ' + ' '.join(f'{v:9d}' for v in row) +
              f' {sum(row):10d}')


def cmd_sweep(lo, hi, mmax, include, out, delta=DELTA, allow_disconnected=False,
              verbose=False):
    ns = [n for n in range(lo, hi + 1)
          if include == 'all' or (include == 'div3') == (n % 3 == 0)]
    print(f'sweep: n in {ns}\n       m <= {mmax}, delta >= {delta}, '
          f'oriented quotients{"" if allow_disconnected else " (strongly connected)"}'
          f', caps at the optimum (Lemma Q4)')
    print(f'       results -> {out}', flush=True)
    fh = open(out, 'a')
    stopped = False
    for n in ns:
        rec = sweep_n(n, mmax, delta, allow_disconnected=allow_disconnected,
                      verbose=verbose)
        fh.write(json.dumps(rec) + '\n')
        fh.flush()
        os.fsync(fh.fileno())
        b = rec['best']
        print(f'n={n:3d}  min excess {rec["min_excess"]}  '
              f'(theorem {rec["theorem_excess"]})  candidates '
              f'{rec["candidates"]:8d}  {rec["seconds"]:6.1f}s  '
              f'best m={b["m"] if b else "-"} sizes={b["sizes"] if b else "-"}',
              flush=True)
        if rec['alarm']:
            H = tuple(tuple(r) for r in b['H'])
            path = os.path.join(DATA, f'quotient_alarm_n{n}.json')
            sha = dump_witness(H, b['sizes'], b['caps'], path)
            print('\n' + '!' * 72)
            print(f'ALARM: excess {rec["min_excess"]} < {rec["alarm_below"]} '
                  f'at n={n} -- this BEATS upper_bound_family')
            print(f'  H = {b["H"]}  sizes = {b["sizes"]}  caps = {b["caps"]}')
            print(f'  witness written to {path}  graph_sha1 {sha}')
            print(f'  CONFIRM NOW:  python3 verify/verify_ssnc.py {path}')
            print('!' * 72, flush=True)
            stopped = True
            break
    fh.close()
    return stopped


def cmd_report(path):
    if not os.path.exists(path):
        print(f'no results file {path}')
        return
    recs = {}
    for line in open(path):
        line = line.strip()
        if line:
            r = json.loads(line)
            recs[r['n']] = r
    print(f'{"n":>4} {"min E":>6} {"thm":>4} {"m*":>3} {"sizes":>18} '
          f'{"caps":>14} {"deltas":>14} {"deg":>4} {"candidates":>11} '
          f'{"sec":>7}')
    print('-' * 96)
    for n in sorted(recs):
        r = recs[n]
        b = r['best'] or {}
        print(f'{n:4d} {str(r["min_excess"]):>6} {r["theorem_excess"]:4d} '
              f'{b.get("m", "-"):>3} {str(b.get("sizes", "-")):>18} '
              f'{str(b.get("caps", "-")):>14} {str(b.get("deltas", "-")):>14} '
              f'{str(b.get("min_outdeg", "-")):>4} {r["candidates"]:11d} '
              f'{r["seconds"]:7.1f}'
              + ('   *** ALARM ***' if r['alarm'] else ''))
    tot = sum(r['candidates'] for r in recs.values())
    print('-' * 96)
    print(f'{len(recs)} orders swept, {tot} candidates, '
          f'{sum(r["seconds"] for r in recs.values()):.1f}s total')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--verify', action='store_true', help='all calibrations')
    ap.add_argument('--verify-family', action='store_true')
    ap.add_argument('--verify-sha1', action='store_true')
    ap.add_argument('--verify-random', action='store_true')
    ap.add_argument('--counts', action='store_true')
    ap.add_argument('--sweep', action='store_true')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--lo', type=int, default=24)
    ap.add_argument('--hi', type=int, default=40)
    ap.add_argument('--mmax', type=int, default=5)
    ap.add_argument('--include', choices=('nondiv3', 'div3', 'all'),
                    default='nondiv3')
    ap.add_argument('-k', '--trials', type=int, default=2000)
    ap.add_argument('--seed', type=int, default=20260725)
    ap.add_argument('--out', default=RESULTS)
    ap.add_argument('--allow-disconnected', action='store_true')
    ap.add_argument('-v', '--verbose', action='store_true')
    a = ap.parse_args()

    bad = 0
    if a.verify or a.verify_family:
        bad += verify_family(24, 150)
    if a.verify or a.verify_sha1:
        b, _hits = verify_sha1()   # the empty-glob guard is inside verify_sha1
        bad += b
    if a.verify or a.verify_random:
        bad += verify_random(a.trials, a.seed)
    if a.verify or a.verify_family or a.verify_sha1 or a.verify_random:
        print('RESULT:', 'ALL OK' if bad == 0 else f'{bad} FAILURES')
        sys.exit(1 if bad else 0)
    if a.counts:
        cmd_counts(a.mmax, a.lo, a.hi)
    elif a.sweep:
        sys.exit(2 if cmd_sweep(a.lo, a.hi, a.mmax, a.include, a.out,
                                allow_disconnected=a.allow_disconnected,
                                verbose=a.verbose) else 0)
    elif a.report:
        cmd_report(a.out)
    else:
        ap.error('pick one of --verify / --counts / --sweep / --report')


if __name__ == '__main__':
    main()
