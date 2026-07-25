#!/usr/bin/env python3
"""INVERSE sweep of the blow-up family: enumerate the excess profiles first,
then decide (exactly, with NO upper bound on n) whether a class-size vector
realising them exists.

blowup_sweep.py sweeps FORWARD -- for one fixed n it runs over every quotient
H and every class-size vector and evaluates the closed form.  That costs one
pass per n, so the statement it produces is bounded to the swept orders
(24 <= n <= 40 in the recorded run).  The observation that removes the bound
(Raa) is that

        Delta = N s        with     N = M2 - M1

is a SINGLE AFFINE (here: linear) map of the size vector s -- not a piecewise
one -- and the per-class excess at the optimal cap depends on the class only
through (Delta_a, n_a).  So the sweep can be run backwards:

    1. enumerate the finitely many per-class REGIMES (Delta_a, n_a-range) whose
       excess contribution is small enough,
    2. for each quotient H and each assignment of regimes to classes with
       total excess <= E, decide whether the linear system

            N s = / <= d   (the regime),   M1 s >= 8   (delta >= 8),
            s_a >= 1       (or s_a = 1 / s_a >= 2, from the regime)

       has an INTEGER solution -- with n = sum_a s_a completely free.

Step 2 is a 6-variable integer feasibility problem, and the answer is a
statement about ALL n at once.

--------------------------------------------------------- 1. the regime table

By Q3/Q4 of blowup_sweep.py the per-class excess at the optimal cap
c* = min(n_a, max(0, Delta+1)) is

    g(Delta, n) = 0                                   if Delta <= -1
                = t*(Delta+1) - t*(t-1)/2,  t = min(n, Delta+1)   otherwise
                = (Delta+1) + Delta + ... + (Delta+2-t)          [t terms]

(the cap may be taken optimal without loss: by Q0(c),(d) the caps change
neither delta(G) nor strong connectivity, and by Q4 every other cap gives a
LARGER-or-equal excess, so a lower bound proved at the optimal cap holds for
every cap).  Two monotonicity facts make the enumeration finite and complete:

    (i)  for Delta >= 0 every one of the t summands is >= Delta+2-t >= 1, so
         g(Delta, n) >= Delta + 1;  hence  Delta >= E  =>  g > E;
    (ii) g(Delta, .) is constant for n >= Delta+1  (t saturates at Delta+1).

Therefore the classes with g <= E fall into finitely many regimes:
"Delta <= -1, n >= 1" (cost 0), and, for each 0 <= Delta <= E-1, the regimes
"n = 1", ..., "n = Delta", "n >= Delta+1", of which we keep those with cost
<= E.  For E = 3 this is the complete list

    name  Delta        size      cost
    NEG   <= -1        >= 1        0
    D0M   = 0          >= 1        1
    D1S1  = 1          = 1         2
    D1M   = 1          >= 2        3
    D2S1  = 2          = 1         3

The unit of enumeration is therefore NOT the Delta profile but the pair
(Delta_a, min(n_a, Delta_a + 1)): the truncation point, i.e. how much of the
intra-class tournament the class is long enough to carry.  Enumerating Delta
alone would be WRONG for a general H, because the minimum-out-degree
constraint binds sum_{b in A(a)} n_b, not n_a, so single-vertex classes are
allowed and do occur (the smallest excess-3 blow-up on 4 classes found by the
run below has sizes [8,1,7,8]).  These are the DEGENERATE classes flagged as
unanalysed in REPORT_BLOWUP section 9: a class of size 1 has no intra-class
arcs at all and its excess is Delta+1, not the triangular number T(Delta).
Ignoring them would make the enumeration INCOMPLETE.  (The naive polynomial
T(x) = (x+1)(x+2)/2 is a trap in two directions: it is wrong for x < 0, where
the truth is 0, and it OVER-counts whenever n_a <= Delta_a, e.g. T(3) = 10
against the true 7 at n_a = 2.  blowup_sweep.class_excess is the truncated
sum and is used verbatim; --test item 1 checks it against the direct sum and
against g on a full grid.)

The cap does not need to be enumerated either: X(a) is non-increasing in c_a
(Q4), so BOTH c_a = n_a and c_a = min(n_a, max(0,Delta+1)) attain the minimum
g(Delta, n), and a LOWER bound proved at the minimising cap holds for all caps.

------------------------------------------------ 2. no bound on n: how and why

CP-SAT needs bounded domains, so a bound B is DERIVED per instance instead of
assumed.  Let

    P = {s in R^m : s >= lo, s <= hi, M1 s >= 8, (N s)_a  in the regime range}

Every constraint is of the form (row).s <= const, so P is a rational
polyhedron, and P is contained in the non-negative orthant, hence POINTED.
By Minkowski-Weyl, P = conv(V) + cone(R) with V the vertices and R the
(finitely many, integral, primitive) extreme rays; both are computed EXACTLY,
in integer arithmetic, by the double-description method on the homogenisation
of P (function extreme_rays).  If s is an integer point of P, write
s = q + sum_i mu_i r_i and put

    s' = s - sum_i 3*floor(mu_i / 3) * r_i .

Then s' is integral (the r_i are), lies in P (the coefficients stay >= 0),
has the SAME sum modulo 3 as s, and

    sum(s') <= max_{q in V} sum(q) + 3 * sum_i sum(r_i)  =:  B .

So: if any integer point with sum(s) = rho (mod 3) exists at all -- at any n,
however large -- then one exists with sum(s) <= B.  Enumerating the integer
points of P with sum(s) <= B (CP-SAT) is therefore an EXHAUSTIVE decision for
every n, and the residues mod 3 obtained are exactly the residues realisable
over all n.  If V is empty then P is empty and the instance is infeasible over
the rationals, a fortiori over the integers.

(The mod-3 refinement is what lets the conclusion be split into the 3|n and
3 nmid n cases, which is the shape of the theorem in upper_bound_family.py.)

------------------------------------------- 3. the conserving quotients, free

Before any integer programming, one family of quotients is settled by hand for
ALL n.  Column c of N sums to |{a : c in C(a)}| - indeg_H(c), so

    sum_a Delta_a = 0 for every size vector   <=>   1^T N = 0   ("conserving")

is a property of H alone (function conserves).  On a conserving H, with
S = {a : Delta_a >= 0},  sum_{a in S} Delta_a = -sum_{a not in S} Delta_a
>= m - |S|, and each a in S contributes at least Delta_a + 1 by (i), so

    excess >= |S| + sum_{a in S} Delta_a >= m           (any n, any cap).

For m = 3 this IS the hand calculation of REPORT_BLOWUP section 9 (H = C_3
conserves, both sides of the column identity being 1), now valid for every
conserving quotient; for m >= 4 it already excludes excess <= 3 outright.
Of the 4313 strongly connected oriented quotients with m <= 6 exactly 7
conserve (1, 1, 2, 3 for m = 3, 4, 5, 6), so this disposes of 7 of them with
no ILP -- and the ILP sweep agrees: its only feasible instances on conserving
quotients are excess 3 on C_3 and excess 4 on the m = 4 one (--conserve).

-------------------------------------------------------------- 4. the result

Run of 2026-07-25, mmax = 6 (all 4313 strongly connected oriented quotients),
delta >= 8, no bound on n:

  E <= 3:  385,695 instances, 385,622 LP-empty, 0 unknown, 73 feasible,
           max derived bound B = 222, 218s on 4 workers.
           EVERY feasible instance has excess exactly 3 and n = 0 (mod 3);
           its profile is three D0M classes and the rest NEG.  No instance
           with excess 0, 1 or 2 is feasible for ANY n.
  E <= 4:  1,052,936 instances, 972 feasible (73 with excess 3, 899 with
           excess 4), max B = 224, 547s.  Excess 4 occurs in all three
           residues; smallest n with excess <= 4 anywhere in the family is 24.

So, WITHIN the blow-up family with m <= 6:  excess <= 2 is impossible for
every n; excess 3 forces 3 | n; and (--cross-check) the minimum over the
family is exactly 3 + [3 nmid n] for every 24 <= n <= 60 tested one by one,
agreeing with the forward sweep on all 11 of its recorded orders.

------------------------------------------------------------------ 5. what is
------------------------------------------------------------- NOT covered

Exactly as in blowup_sweep.py: quotients with m >= 7, and everything that is
not a capped-tournament blow-up (the vast majority of oriented graphs).  The
n-range restriction is the ONE thing this tool removes.

Usage (from the repository root):
  python3 blowup/blowup_inverse.py --test           # 7 self-tests
  python3 blowup/blowup_inverse.py --c3             # section 9 by machine
  python3 blowup/blowup_inverse.py --run --mmax 6 [--max-cost 4]
  python3 blowup/blowup_inverse.py --report
  python3 blowup/blowup_inverse.py --cross-check --lo 18 --hi 60
  python3 blowup/blowup_inverse.py --witnesses --dump 1
  python3 blowup/blowup_inverse.py --conserve       # the hand-settled group

The independent re-derivation of the same conclusion, sharing no code with
this file, is blowup/verify_blowup_independent.py --check all.
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))       # blowup/
ROOT = os.path.dirname(BASE)
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(ROOT, 'verify'))         # verify_ssnc.py

import blowup_sweep as BS                                        # noqa: E402

DELTA = 8
DATA = os.path.join(ROOT, 'data', 'blowup')
RESULTS = os.path.join(DATA, 'blowup_inverse_results.jsonl')
HCACHE = os.path.join(DATA, 'blowup_inverse_quotients.json')


# --------------------------------------------------------------- 1. regimes
def g_excess(delta, size):
    """Per-class excess at the optimal cap (Q3 + Q4 of blowup_sweep)."""
    if delta < 0:
        return 0
    t = min(size, delta + 1)
    return t * (delta + 1) - t * (t - 1) // 2


def regimes(max_cost=3):
    """All per-class regimes with cost <= max_cost.

    A regime is (name, dlo, dhi, slo, shi, cost) with None = unbounded.
    Completeness: g(delta, n) >= delta+1 for delta >= 0 (so delta < max_cost),
    and g(delta, .) is constant for n >= delta+1.
    """
    out = [('NEG', None, -1, 1, None, 0)]
    for d in range(0, max_cost):
        for n in range(1, d + 1):                       # the degenerate sizes
            c = g_excess(d, n)
            if c <= max_cost:
                out.append((f'D{d}S{n}', d, d, n, n, c))
        c = g_excess(d, d + 1)
        if c <= max_cost:
            out.append((f'D{d}M', d, d, d + 1, None, c))
    return out


def profiles(m, regs, max_cost=3):
    """All assignments of regimes to the m classes with total cost <= max_cost."""
    costs = [r[5] for r in regs]
    out = []

    def rec(a, acc, chosen):
        if a == m:
            out.append(tuple(chosen))
            return
        for i, c in enumerate(costs):
            if acc + c <= max_cost:
                chosen.append(i)
                rec(a + 1, acc + c, chosen)
                chosen.pop()

    rec(0, 0, [])
    return out


# ------------------------------------- 1b. the conservation law (Sum Delta=0)
def conserves(H):
    """Is 1^T (M2 - M1) = 0, i.e. is sum_a Delta_a = 0 for EVERY size vector?

    Column c of N = M2 - M1 sums to  |{a : c in C(a)}| - indeg_H(c),  so the
    condition is  |{a : c in B(a)\\A(a)}| = indeg_H(c)  for every class c.
    For H = C_3 both sides are 1; this is the origin of delta_0+delta_1+
    delta_2 = 0 in REPORT_BLOWUP section 9.  It is neither automatic nor
    exclusive to C_3, and it is a property of H alone.
    """
    M1, M2 = BS.indicator_matrices(H)
    return bool(((M2 - M1).sum(axis=0) == 0).all())


def conservation_lower_bound(H):
    """excess >= m for every conserving H, every size vector and every cap.

    Proof.  Let S = {a : Delta_a >= 0}.  Conservation gives
    sum_{a in S} Delta_a = - sum_{a not in S} Delta_a >= m - |S|, because
    every Delta_a outside S is <= -1.  The per-class excess is 0 for a not in
    S and, by monotonicity fact (i) of the header, at least Delta_a + 1 for a
    in S (at the OPTIMAL cap, hence for every cap).  Therefore

        excess >= sum_{a in S} (Delta_a + 1) = |S| + sum_{a in S} Delta_a
               >= |S| + (m - |S|) = m .

    Consequences, for ALL n, with no integer programming at all:
      * conserving H with m >= 4  ->  excess >= 4  (excess <= 3 impossible),
      * conserving H with m  = 3  ->  excess >= 3  (this is section 9's
        "excess <= 2 is impossible for H = C_3", now for every conserving H).
    """
    return len(H) if conserves(H) else None


def cmd_conserve(mmax=6, path=RESULTS, quiet=False):
    """[E] classify the quotients by the conservation law and check that the
    ILP sweep never contradicts the hand bound excess >= m on that group."""
    qs = quotients(mmax)
    per = {}
    for m, H in qs:
        c = conserves(H)
        d = per.setdefault(m, [0, 0, 0])
        d[0] += 1
        d[1 if c else 2] += 1
    print(f'{"m":>3} {"quotients":>10} {"conserving":>11} {"not":>8}   '
          f'hand bound on the conserving group')
    for m in sorted(per):
        t, c, nc = per[m]
        print(f'{m:3d} {t:10d} {c:11d} {nc:8d}   excess >= {m}'
              f'{"  (so excess <= 3 impossible, all n)" if m > 3 else ""}')
    tot = [sum(v[i] for v in per.values()) for i in range(3)]
    print(f'tot {tot[0]:10d} {tot[1]:11d} {tot[2]:8d}')
    # [D] strong connectivity already forces every out-neighbourhood non-empty
    bad_d = sum(1 for _, H in qs if any(not any(r) for r in H))
    print(f'[D] quotients with an empty out-neighbourhood (S1 = 0 < delta): '
          f'{bad_d} (strong connectivity rules them out)')
    # consistency: sweep hits on conserving quotients must obey excess >= m
    bad = 0
    if os.path.exists(path):
        hits = [json.loads(l) for l in open(path)
                if l.strip() and json.loads(l)['kind'] == 'hit']
        con = [h for h in hits
               if conserves(tuple(tuple(r) for r in h['H']))]
        for h in con:
            if h['excess'] < h['m']:
                bad += 1
        print(f'[E] cross-check vs {os.path.basename(path)}: {len(con)} of the '
              f'{len(hits)} feasible instances sit on a conserving quotient, '
              f'{len(con) - bad}/{len(con)} obey excess >= m'
              + (f' -- {bad} VIOLATIONS' if bad else ''))
        by = {}
        for h in hits:
            by.setdefault((h['m'], conserves(tuple(tuple(r) for r in h['H']))),
                          []).append(h['excess'])
        for (m, c), es in sorted(by.items()):
            print(f'    m={m} {"conserving" if c else "non-conserving":>15}: '
                  f'{len(es)} instances, excess {sorted(set(es))}')
    return bad


# ------------------------------------------------------- 2. the linear system
def system(H, prof, regs, delta=DELTA):
    """Rows (a, rhs) meaning  a . s <= rhs,  plus per-class (lo, hi) bounds."""
    m = len(H)
    M1, M2 = BS.indicator_matrices(H)
    N = (M2 - M1).tolist()
    M1 = M1.tolist()
    rows = []
    lo, hi = [], []
    for a in range(m):
        name, dlo, dhi, slo, shi, cost = regs[prof[a]]
        lo.append(slo)
        hi.append(shi)
        if dhi is not None:                                  # (N s)_a <= dhi
            rows.append((list(N[a]), dhi))
        if dlo is not None:                                  # -(N s)_a <= -dlo
            rows.append(([-x for x in N[a]], -dlo))
        rows.append(([-x for x in M1[a]], -delta))           # (M1 s)_a >= delta
    return rows, lo, hi


def profile_cost(prof, regs):
    return sum(regs[i][5] for i in prof)


# --------------------------------------------- double description (exact, int)
def _dot(u, v):
    return sum(x * y for x, y in zip(u, v))


def _prim(v):
    g = 0
    for x in v:
        g = math.gcd(g, abs(x))
    if g == 0:
        return None
    return tuple(x // g for x in v)


def extreme_rays(rows, d):
    """Extreme rays of C = {x in R^d : rows[i] . x <= 0 for all i}.

    rows[0:d] MUST be -e_0, ..., -e_{d-1} (so C is inside the orthant and the
    double-description recursion can start from the simplicial cone spanned by
    the unit vectors).  Exact integer arithmetic; output rays are primitive.
    """
    gens = [tuple(1 if k == i else 0 for k in range(d)) for i in range(d)]
    masks = []
    for g in gens:
        mk = 0
        for j in range(d):
            if _dot(rows[j], g) == 0:
                mk |= 1 << j
        masks.append(mk)
    for j in range(d, len(rows)):
        r = rows[j]
        vals = [_dot(r, g) for g in gens]
        newg, newm, seen = [], [], {}
        for i, v in enumerate(vals):
            if v <= 0:
                seen[gens[i]] = len(newg)
                newg.append(gens[i])
                newm.append(masks[i] | ((1 << j) if v == 0 else 0))
        pos = [i for i, v in enumerate(vals) if v > 0]
        neg = [i for i, v in enumerate(vals) if v < 0]
        for p in pos:
            for q in neg:
                common = masks[p] & masks[q]
                adjacent = True
                for i in range(len(gens)):
                    if i != p and i != q and (masks[i] & common) == common:
                        adjacent = False
                        break
                if not adjacent:
                    continue
                comb = _prim(tuple(vals[p] * gens[q][k] - vals[q] * gens[p][k]
                                   for k in range(d)))
                if comb is None or comb in seen:
                    continue
                mk = 0
                for jj in range(j + 1):
                    if _dot(rows[jj], comb) == 0:
                        mk |= 1 << jj
                seen[comb] = len(newg)
                newg.append(comb)
                newm.append(mk)
        gens, masks = newg, newm
        if not gens:
            break
    return gens


def homogenise(rows, lo, hi, m):
    """Rows of the homogenised cone in R^{1+m}: x = (x0, s)."""
    d = m + 1
    out = [tuple(-1 if k == i else 0 for k in range(d)) for i in range(d)]
    for a in range(m):
        e = [0] * d
        e[1 + a] = -1
        e[0] = lo[a]
        out.append(tuple(e))                                  # -s_a + lo*x0<=0
        if hi[a] is not None:
            e = [0] * d
            e[1 + a] = 1
            e[0] = -hi[a]
            out.append(tuple(e))                              # s_a - hi*x0 <=0
    for coef, rhs in rows:
        out.append(tuple([-rhs] + list(coef)))                # a.s - rhs*x0<=0
    return out, d


def bound(rows, lo, hi, m, period=3):
    """(B, n_vertices, n_rays) with B a valid cap on sum(s) as in the header.

    Returns B = None iff the LP relaxation P is empty (then P has no integer
    point either, for any n).
    """
    hrows, d = homogenise(rows, lo, hi, m)
    gens = extreme_rays(hrows, d)
    verts = [g for g in gens if g[0] > 0]
    rays = [g for g in gens if g[0] == 0]
    if not verts:
        return None, 0, len(rays)
    top = max(Fraction(sum(g[1:]), g[0]) for g in verts)
    rs = sum(sum(g[1:]) for g in rays)
    return int(math.floor(top)) + period * rs, len(verts), len(rays)


# ------------------------------------------------------------- 3. the decision
def solve_instance(H, prof, regs, B, delta=DELTA, fixed_n=None, period=3,
                   time_limit=30.0):
    """Integer feasibility.  Returns dict with, per residue mod `period`, the
    minimum n (or None), plus a witness size vector for the best one."""
    from ortools.sat.python import cp_model
    m = len(H)
    rows, lo, hi = system(H, prof, regs, delta)
    res = {'residues': {}, 'witness': None, 'min_n': None, 'unknown': 0}
    todo = [None] if fixed_n is not None else list(range(period))
    for rho in todo:
        model = cp_model.CpModel()
        s = [model.NewIntVar(lo[a], B if hi[a] is None else min(hi[a], B),
                             f's{a}') for a in range(m)]
        for coef, rhs in rows:
            model.Add(sum(int(c) * s[a] for a, c in enumerate(coef)) <= int(rhs))
        tot = sum(s)
        if fixed_n is not None:
            model.Add(tot == fixed_n)
        else:
            model.Add(tot <= B)
            if period > 1:
                k = model.NewIntVar(0, B // period + 1, 'k')
                model.Add(tot == period * k + rho)
            model.Minimize(tot)
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.max_time_in_seconds = time_limit
        st = solver.Solve(model)
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            sizes = [int(solver.Value(v)) for v in s]
            n = sum(sizes)
            res['residues'][rho] = n
            if res['min_n'] is None or n < res['min_n']:
                res['min_n'] = n
                res['witness'] = sizes
        elif st == cp_model.INFEASIBLE:
            res['residues'][rho] = None
        else:
            res['unknown'] += 1
            res['residues'][rho] = 'UNKNOWN'
    return res


def scan_quotient(args):
    """One quotient H: every profile with cost <= max_cost.  Worker entry."""
    H, mmax_cost, delta = args
    H = tuple(tuple(r) for r in H)
    m = len(H)
    regs = regimes(mmax_cost)
    hits, stats = [], {'instances': 0, 'lp_empty': 0, 'int_infeasible': 0,
                       'feasible': 0, 'unknown': 0, 'max_B': 0}
    for prof in profiles(m, regs, mmax_cost):
        cost = profile_cost(prof, regs)
        stats['instances'] += 1
        rows, lo, hi = system(H, prof, regs, delta)
        B, nv, nr = bound(rows, lo, hi, m)
        if B is None:
            stats['lp_empty'] += 1
            continue
        stats['max_B'] = max(stats['max_B'], B)
        r = solve_instance(H, prof, regs, B, delta)
        if r['unknown']:
            stats['unknown'] += r['unknown']
        live = {k: v for k, v in r['residues'].items() if v is not None}
        if not live:
            stats['int_infeasible'] += 1
            continue
        stats['feasible'] += 1
        hits.append({'m': m, 'H': [list(x) for x in H],
                     'profile': [regs[i][0] for i in prof], 'excess': cost,
                     'B': B, 'vertices': nv, 'rays': nr,
                     'residues': {str(k): v for k, v in r['residues'].items()},
                     'min_n': r['min_n'], 'witness': r['witness']})
    return hits, stats


# ------------------------------------------------------------ quotient supply
def quotients(mmax, cache=HCACHE):
    """[(m, H)] for 3 <= m <= mmax, strongly connected oriented, cached.

    m = 1: the blow-up is a capped transitive tournament, S1 = 0 < delta.
    m = 2: no strongly connected ORIENTED graph exists (it would need a digon).
    """
    have = {}
    if os.path.exists(cache):
        have = {int(k): v for k, v in json.load(open(cache)).items()}
    out, dirty = [], False
    for m in range(3, mmax + 1):
        if m not in have:
            have[m] = [[list(r) for r in H]
                       for H, _ in BS.enumerate_quotients(m)]
            dirty = True
        out += [(m, tuple(tuple(r) for r in H)) for H in have[m]]
    if dirty:
        json.dump({str(k): v for k, v in have.items()}, open(cache, 'w'))
    return out


# ------------------------------------------------------------------- 4. tests
def test_regimes(quiet=False):
    """1. The regime table is exactly {(Delta,n) : min-over-caps excess <= E}
    and g agrees with blowup_sweep.class_excess minimised over the cap."""
    bad = 0
    for E in (0, 1, 2, 3, 4, 5):
        regs = regimes(E)
        for dlt in range(-30, 31):
            for n in range(1, 61):
                want = min(BS.class_excess(dlt, c, n) for c in range(0, n + 1))
                if want != g_excess(dlt, n):
                    bad += 1
                    print(f'  g mismatch Delta={dlt} n={n}: {g_excess(dlt, n)}'
                          f' vs class_excess min {want}')
                cov = [r for r in regs
                       if (r[1] is None or dlt >= r[1]) and
                          (r[2] is None or dlt <= r[2]) and
                          (r[3] is None or n >= r[3]) and
                          (r[4] is None or n <= r[4])]
                if (want <= E) != (len(cov) == 1):
                    bad += 1
                    print(f'  coverage E={E} Delta={dlt} n={n}: excess {want}, '
                          f'{len(cov)} regimes match')
                elif cov and cov[0][5] != want:
                    bad += 1
                    print(f'  cost E={E} Delta={dlt} n={n}: {cov[0]} vs {want}')
        # optimal cap of blowup_sweep really attains the minimum
        for dlt in range(-5, 6):
            for n in range(1, 12):
                c = min(n, max(0, dlt + 1))
                if BS.class_excess(dlt, c, n) != g_excess(dlt, n):
                    bad += 1
    if not quiet:
        print(f'1. regime table: g == min_cap class_excess and the table covers'
              f' exactly {{excess <= E}}, Delta in [-30,30], n in [1,60], '
              f'E <= 5 -- {"OK" if not bad else str(bad) + " FAILURES"}')
        print(f'   E=3 table: ' +
              ', '.join(f'{r[0]}(cost {r[5]})' for r in regimes(3)))
    return bad


def test_linear_map(trials=400, seed=7, quiet=False):
    """2. Delta = (M2-M1) s really is the Delta of blowup_sweep, and the
    per-class excess at the optimal cap is g(Delta_a, n_a)."""
    rng = np.random.default_rng(seed)
    bad = 0
    for _ in range(trials):
        H, sizes, _ = BS.random_case(rng, mlo=2, mhi=7, slo=1, shi=7)
        m = len(H)
        M1, M2 = BS.indicator_matrices(H)
        N = M2 - M1
        want = BS.deltas(H, sizes)
        got = (N @ np.array(sizes)).tolist()
        if want != got:
            bad += 1
            continue
        caps = BS.optimal_caps(H, sizes)
        for a in range(m):
            if BS.class_excess(want[a], caps[a], sizes[a]) != \
                    g_excess(want[a], sizes[a]):
                bad += 1
        if sum(g_excess(want[a], sizes[a]) for a in range(m)) != \
                BS.excess_closed(H, sizes):
            bad += 1
        if (N < -1).any() or (N > 1).any():
            bad += 1
    if not quiet:
        print(f'2. Delta = (M2-M1)s and excess = sum g(Delta_a, n_a): '
              f'{trials - bad}/{trials} random (H, s)')
    return bad


def _brute_rays(rows, d):
    """Independent extreme-ray enumeration: every extreme ray of a pointed cone
    is the (1-dimensional) null space of d-1 independent tight constraints."""
    out = set()
    for S in itertools.combinations(range(len(rows)), d - 1):
        A = [[Fraction(x) for x in rows[i]] for i in S]
        # Gaussian elimination -> null space
        piv, r = [], 0
        for c in range(d):
            p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
            if p is None:
                continue
            A[r], A[p] = A[p], A[r]
            inv = A[r][c]
            A[r] = [x / inv for x in A[r]]
            for i in range(len(A)):
                if i != r and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [x - f * y for x, y in zip(A[i], A[r])]
            piv.append(c)
            r += 1
        free = [c for c in range(d) if c not in piv]
        if len(free) != 1:
            continue
        f = free[0]
        v = [Fraction(0)] * d
        v[f] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -A[i][f]
        den = 1
        for x in v:
            den = den * x.denominator // math.gcd(den, x.denominator)
        iv = tuple(int(x * den) for x in v)
        for cand in (iv, tuple(-x for x in iv)):
            if all(_dot(rw, cand) <= 0 for rw in rows):
                p = _prim(cand)
                if p is not None and any(p):
                    out.add(p)
    return out


def _random_sc(rng, m):
    while True:
        H = BS.random_case(rng, mlo=m, mhi=m)[0]
        if BS.is_strongly_connected(H):
            return H


def test_dd(trials=60, seed=11, quiet=False):
    """3. The double-description output equals a brute-force enumeration of
    extreme rays (independent implementation) on random small instances --
    both on real (H, profile) systems and on random cones."""
    rng = np.random.default_rng(seed)
    regs = regimes(3)
    bad = 0
    for t in range(trials):
        m = int(rng.integers(3, 6))
        H = _random_sc(rng, m)
        pr = profiles(m, regs, 3)
        prof = pr[int(rng.integers(0, len(pr)))]
        rows, lo, hi = system(H, prof, regs)
        hrows, d = homogenise(rows, lo, hi, m)
        if set(extreme_rays(hrows, d)) != _brute_rays(hrows, d):
            bad += 1
            print(f'  DD mismatch on a real system, m={m}')
    rnd = 0
    for t in range(trials):
        d = int(rng.integers(3, 6))
        rows = [tuple(-1 if k == i else 0 for k in range(d)) for i in range(d)]
        for _ in range(int(rng.integers(1, 8))):
            rows.append(tuple(int(x) for x in rng.integers(-3, 4, size=d)))
        rnd += 1
        if set(extreme_rays(rows, d)) != _brute_rays(rows, d):
            bad += 1
            print(f'  DD mismatch on a random cone d={d}: {rows}')
    if not quiet:
        print(f'3. double description vs brute-force extreme rays: '
              f'{trials + rnd - bad}/{trials + rnd} cones identical '
              f'({trials} real systems, {rnd} random cones)')
    return bad


def test_bound(trials=200, seed=13, quiet=False, blow=20):
    """4. The derived bound B is not a lie: the set of residues mod 3 that are
    realisable with sum(s) <= B is the same as the set realisable with
    sum(s) <= 20B+50 (a domain 20x larger), and the test has teeth -- we count
    the instances that DO have solutions above B."""
    from ortools.sat.python import cp_model
    rng = np.random.default_rng(seed)
    regs = regimes(3)
    bad = tested = teeth = 0
    while tested < trials:
        m = int(rng.integers(3, 7))
        H = _random_sc(rng, m)
        pr = profiles(m, regs, 3)
        for prof in [pr[int(rng.integers(0, len(pr)))] for _ in range(6)]:
            rows, lo, hi = system(H, prof, regs)
            B, nv, nr = bound(rows, lo, hi, m)
            if B is None:
                continue
            tested += 1
            small = solve_instance(H, prof, regs, B, DELTA)
            got = {k for k, v in small['residues'].items()
                   if v not in (None, 'UNKNOWN')}
            big, above = set(), False
            for rho in range(3):
                model = cp_model.CpModel()
                s = [model.NewIntVar(lo[a], blow * B + 50 if hi[a] is None
                                     else hi[a], f's{a}') for a in range(m)]
                for coef, rhs in rows:
                    model.Add(sum(int(c) * s[a] for a, c in enumerate(coef))
                              <= int(rhs))
                tot = sum(s)
                model.Add(tot <= blow * B + 50)
                k = model.NewIntVar(0, blow * B + 50, 'k')
                model.Add(tot == 3 * k + rho)
                model.Maximize(tot)              # push above B if possible
                sol = cp_model.CpSolver()
                sol.parameters.num_search_workers = 1
                sol.parameters.max_time_in_seconds = 10
                st = sol.Solve(model)
                if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    big.add(rho)
                    if sum(sol.Value(v) for v in s) > B:
                        above = True
            teeth += 1 if above else 0
            if got != big:
                bad += 1
                print(f'  BOUND FAILURE m={m} H={H} '
                      f'prof={[regs[i][0] for i in prof]} B={B}: '
                      f'residues <= B {sorted(got)} vs <= {blow}B {sorted(big)}')
    if not quiet:
        print(f'4. derived bound B: {tested - bad}/{tested} LP-feasible '
              f'instances have the same residue set at B and at {blow}B+50 '
              f'({teeth} of them do have solutions above B)')
    return bad


def test_witness(quiet=False, mmax=5, k=40):
    """5. Feasible instances really are blow-ups with the claimed excess:
    build the matrix and score it with evaluate.py (independent judge).
    evaluate.score = (total, nsat, excess, min out-degree, sccmiss)."""
    regs = regimes(3)
    cases = []
    for m, H in quotients(mmax):
        for prof in profiles(m, regs, 3):
            rows, lo, hi = system(H, prof, regs)
            B, _, _ = bound(rows, lo, hi, m)
            if B is None:
                continue
            r = solve_instance(H, prof, regs, B, DELTA)
            for rho, n in sorted(r['residues'].items()):
                if n in (None, 'UNKNOWN'):
                    continue
                w = solve_instance(H, prof, regs, n, DELTA, fixed_n=n)['witness']
                if w:
                    cases.append((H, w, profile_cost(prof, regs)))
            if len(cases) >= k:
                break
        if len(cases) >= k:
            break
    bad = 0
    by_n = {}
    for i, (H, sizes, cost) in enumerate(cases):
        by_n.setdefault(sum(sizes), []).append(i)
    for n, idx in sorted(by_n.items()):
        mats = [BS.build(cases[i][0], cases[i][1]) for i in idx]
        scores = BS.evaluate_batch(mats, n)
        for i, sc in zip(idx, scores):
            H, sizes, cost = cases[i]
            if sc is None or sc[2] != cost or sc[0] != cost or sc[3] < DELTA \
                    or sc[4] != 0:
                bad += 1
                print(f'  witness mismatch H={H} sizes={sizes}: evaluate {sc} '
                      f'vs claimed excess {cost}')
    if not quiet:
        print(f'5. feasible witnesses vs evaluate.py: {len(cases) - bad}/'
              f'{len(cases)} matrices scored (excess = claim, degdef = 0, '
              f'sccmiss = 0, min out-degree >= {DELTA})')
    return bad


def test_c3(quiet=False):
    """6. H = C_3 reproduces the hand calculation of REPORT_BLOWUP section 9."""
    regs = regimes(4)
    m = 3
    H = BS.C3
    found = {}
    for prof in profiles(m, regs, 4):
        cost = profile_cost(prof, regs)
        rows, lo, hi = system(H, prof, regs)
        B, _, _ = bound(rows, lo, hi, m)
        if B is None:
            continue
        r = solve_instance(H, prof, regs, B, DELTA)
        live = {k: v for k, v in r['residues'].items() if v not in (None,
                                                                   'UNKNOWN')}
        if live:
            found.setdefault(cost, []).append(
                ([regs[i][0] for i in prof], live, r['min_n']))
    bad = 0
    reach = sorted(found)
    if any(c <= 2 for c in reach):
        bad += 1
    if 3 not in reach or 4 not in reach:
        bad += 1
    res3 = set()
    for _, live, _ in found.get(3, []):
        res3 |= set(live)
    res4 = set()
    for _, live, _ in found.get(4, []):
        res4 |= set(live)
    if res3 != {0}:
        bad += 1
    if not quiet:
        print(f'6. H = C_3 (section 9 of REPORT_BLOWUP, by machine, all n):')
        print(f'   attainable excess values <= 4 : {reach}  '
              f'(excess <= 2 impossible: {"yes" if all(c > 2 for c in reach) else "NO"})')
        for c in reach:
            for prof, live, mn in found[c]:
                print(f'   excess {c}: profile {prof}, n mod 3 in '
                      f'{sorted(live)} (min n per residue {live})')
        print(f'   -> minimum is 3 (n = 0 mod 3 only), next is 4 '
              f'(residues {sorted(res4)}) -- '
              f'{"matches" if not bad else "DOES NOT MATCH"} the hand calculation')
    return bad


def test_conservation(trials=4000, seed=23, quiet=False):
    """7. The conservation law and the hand bound it gives.

    (a) 1^T (M2-M1) = 0  <=>  sum_a Delta_a = 0 for every size vector,
    (b) on a conserving H, excess >= m for every size vector and every cap,
    (c) the regime table is indexed by (Delta, min(n, Delta+1)) -- the
        truncation point -- which is the correction demanded in [B]."""
    rng = np.random.default_rng(seed)
    bad = con = 0
    for _ in range(trials):
        m = int(rng.integers(3, 7))
        H, sizes, caps = BS.random_case(rng, mlo=m, mhi=m, slo=1, shi=9)
        D = BS.deltas(H, sizes)
        c = conserves(H)
        if c != (sum(D) == 0):
            # a single size vector can have sum 0 by accident; only the
            # implication conserving => sum 0 is an identity
            if c and sum(D) != 0:
                bad += 1
        if c:
            con += 1
            if BS.excess_closed(H, sizes) < m:
                bad += 1
                print(f'  conserving bound violated: H={H} sizes={sizes}')
            if BS.excess_closed(H, sizes, caps) < m:
                bad += 1
    # (c) the regime cost depends on (Delta, min(n, Delta+1)) only
    for d in range(0, 6):
        for n1 in range(1, 30):
            for n2 in range(1, 30):
                if min(n1, d + 1) == min(n2, d + 1) and \
                        g_excess(d, n1) != g_excess(d, n2):
                    bad += 1
    if not quiet:
        print(f'7. conservation law: {con}/{trials} random quotients conserve, '
              f'all of them satisfy sum Delta = 0 and excess >= m (any cap); '
              f'cost depends on (Delta, min(n, Delta+1)) only -- '
              f'{"OK" if not bad else str(bad) + " FAILURES"}')
    return bad


def run_tests():
    bad = 0
    bad += test_regimes()
    bad += test_linear_map()
    bad += test_dd()
    bad += test_bound()
    bad += test_witness()
    bad += test_c3()
    bad += test_conservation()
    print('RESULT:', 'ALL OK' if bad == 0 else f'{bad} FAILURES')
    return bad


# --------------------------------------------------------------------- 5. run
def cmd_run(mmax, max_cost, out, workers=4, delta=DELTA):
    from concurrent.futures import ProcessPoolExecutor
    qs = quotients(mmax)
    print(f'inverse sweep: {len(qs)} strongly connected oriented quotients '
          f'(3 <= m <= {mmax}), excess <= {max_cost}, delta >= {delta}, '
          f'n UNBOUNDED', flush=True)
    for m in range(3, mmax + 1):
        k = sum(1 for mm, _ in qs if mm == m)
        p = len(profiles(m, regimes(max_cost), max_cost))
        print(f'   m={m}: {k} quotients x {p} profiles = {k * p} instances',
              flush=True)
    t0 = time.time()
    agg = {'instances': 0, 'lp_empty': 0, 'int_infeasible': 0, 'feasible': 0,
           'unknown': 0, 'max_B': 0}
    fh = open(out, 'w')
    fh.write(json.dumps({'kind': 'header', 'mmax': mmax, 'max_cost': max_cost,
                         'delta': delta, 'quotients': len(qs)}) + '\n')
    tasks = [([list(r) for r in H], max_cost, delta) for _, H in qs]
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for hits, st in ex.map(scan_quotient, tasks, chunksize=8):
            done += 1
            for k in agg:
                agg[k] = max(agg[k], st[k]) if k == 'max_B' else agg[k] + st[k]
            for h in hits:
                fh.write(json.dumps({'kind': 'hit', **h}) + '\n')
            if hits:
                fh.flush()
            if done % 200 == 0:
                print(f'   {done}/{len(qs)} quotients, {agg["instances"]} '
                      f'instances, {agg["feasible"]} feasible, '
                      f'{time.time() - t0:.0f}s', flush=True)
    agg['seconds'] = round(time.time() - t0, 1)
    fh.write(json.dumps({'kind': 'summary', **agg}) + '\n')
    fh.close()
    print(json.dumps(agg, indent=1))
    return agg


def cmd_report(path, lo=24, hi=60):
    """Digest the run: which excess values are attainable, at which n."""
    recs = [json.loads(l) for l in open(path) if l.strip()]
    hits = [r for r in recs if r['kind'] == 'hit']
    summ = [r for r in recs if r['kind'] == 'summary']
    head = [r for r in recs if r['kind'] == 'header']
    if head:
        print(f'header: {head[0]}')
    print(f'{len(hits)} feasible instances')
    by = {}
    for h in hits:
        by.setdefault(h['excess'], []).append(h)
    print(f'\n{"excess":>7} {"instances":>10} {"n residues mod 3":>18} '
          f'{"min n":>7}  quotient sizes m')
    for e in sorted(by):
        res = set()
        mn = None
        ms = set()
        for h in by[e]:
            for k, v in h['residues'].items():
                if v not in (None, 'UNKNOWN'):
                    res.add(int(k))
                    mn = v if mn is None else min(mn, v)
            ms.add(h['m'])
        print(f'{e:7d} {len(by[e]):10d} {str(sorted(res)):>18} {str(mn):>7}  '
              f'{sorted(ms)}')
    if summ:
        print(f'\nsummary: {summ[0]}')
    print('\nThe residue column is the exhaustive statement over ALL n: an\n'
          'excess value absent from a residue class is unattainable at every n\n'
          'in that class.  For the attainable side per individual n (a residue\n'
          'being attainable does not mean every n in it is), run --cross-check.')


def cmd_cross_check(path, lo=24, hi=40, workers=4):
    """Ask the FEASIBLE instances for each specific n and compare with the
    forward exhaustive sweep in blowup_sweep_results.jsonl."""
    recs = [json.loads(l) for l in open(path) if l.strip()]
    hits = [r for r in recs if r['kind'] == 'hit']
    head = [r for r in recs if r['kind'] == 'header']
    mc = head[0]['max_cost'] if head else 3
    regs = regimes(mc)
    print(f'cross-check: {len(hits)} feasible instances, n = {lo}..{hi}, '
          f'excess enumerated up to {mc}')
    best = {}
    for h in hits:
        H = tuple(tuple(r) for r in h['H'])
        names = h['profile']
        prof = tuple(next(i for i, r in enumerate(regs) if r[0] == nm)
                     for nm in names)
        for n in range(lo, hi + 1):
            if best.get(n, 99) <= h['excess']:
                continue
            r = solve_instance(H, prof, regs, n, DELTA, fixed_n=n)
            if r['witness']:
                best[n] = h['excess']
    fwd = {}
    fp = os.path.join(DATA, 'blowup_sweep_results.jsonl')
    if os.path.exists(fp):
        for line in open(fp):
            if line.strip():
                r = json.loads(line)
                fwd[r['n']] = r['min_excess']
    print(f'{"n":>4} {"inverse":>10} {"forward":>10}  verdict')
    bad = 0
    for n in range(lo, hi + 1):
        inv = best.get(n)
        f = fwd.get(n)
        if f is None:
            v = 'no forward datum'
        elif inv is None:
            v = f'agree (both > {mc})' if f > mc else 'MISMATCH'
        else:
            v = 'agree' if inv == f else 'MISMATCH'
        if 'MISMATCH' in v:
            bad += 1
        print(f'{n:4d} {str(inv) if inv is not None else ">" + str(mc):>10} '
              f'{str(f) if f is not None else "-":>10}  {v}')
    print('cross-check:', 'OK' if not bad else f'{bad} MISMATCHES')
    return bad


def cmd_witnesses(path, dump=0):
    """Score every feasible instance's witness with evaluate.py AND with
    verify_ssnc.py (the two independent judges of the repo)."""
    import verify_ssnc as V
    hits = [json.loads(l) for l in open(path)
            if l.strip() and json.loads(l)['kind'] == 'hit']
    cases, by_n = [], {}
    for h in hits:
        H = tuple(tuple(r) for r in h['H'])
        cases.append((H, h['witness'], h['excess'], h['profile']))
        by_n.setdefault(sum(h['witness']), []).append(len(cases) - 1)
    bad_e = bad_v = 0
    for n, idx in sorted(by_n.items()):
        mats = [BS.build(cases[i][0], cases[i][1]) for i in idx]
        scores = BS.evaluate_batch(mats, n)
        for i, sc, A in zip(idx, scores, mats):
            H, sizes, cost, prof = cases[i]
            if sc is None or sc[2] != cost or sc[0] != cost or sc[3] < DELTA \
                    or sc[4] != 0:
                bad_e += 1
                print(f'  evaluate.py mismatch {H} {sizes}: {sc} vs {cost}')
            L = [[int(x) for x in row] for row in A]
            # verify_ssnc asserts on loops/digons, so reaching here means valid
            rep = V.verify(L)
            d, _ = V.second_neighbourhood_deficits(L)
            exc = sum(max(0, x + 1) for x in d)
            if exc != cost or not rep['strongly_connected'] \
                    or rep['min_out_degree'] < DELTA:
                bad_v += 1
                print(f'  verify_ssnc.py mismatch {H} {sizes}: excess {exc}, '
                      f'{rep["strongly_connected"]}, {rep["min_out_degree"]}')
    print(f'{len(cases)} witnesses: evaluate.py {len(cases) - bad_e}/'
          f'{len(cases)}, verify_ssnc.py {len(cases) - bad_v}/{len(cases)} '
          f'(excess = claim, strongly connected, min out-degree >= {DELTA})')
    if dump:
        seen = set()
        for i, (H, sizes, cost, prof) in enumerate(cases):
            if len(H) in seen:
                continue
            seen.add(len(H))
            A = BS.build(H, sizes)
            p = os.path.join(DATA, f'blowup_inverse_witness_m{len(H)}.json')
            json.dump([[int(x) for x in row] for row in A], open(p, 'w'))
            print(f'  m={len(H)} sizes={sizes} n={sum(sizes)} excess={cost} '
                  f'profile={prof} -> {p}  '
                  f'(python3 verify/verify_ssnc.py {p})')
    return bad_e + bad_v


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--test', action='store_true')
    ap.add_argument('--c3', action='store_true')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--cross-check', action='store_true')
    ap.add_argument('--witnesses', action='store_true')
    ap.add_argument('--conserve', action='store_true')
    ap.add_argument('--dump', type=int, default=0)
    ap.add_argument('--mmax', type=int, default=6)
    ap.add_argument('--max-cost', type=int, default=3)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--lo', type=int, default=24)
    ap.add_argument('--hi', type=int, default=40)
    ap.add_argument('--out', default=RESULTS)
    a = ap.parse_args()
    if a.test:
        sys.exit(1 if run_tests() else 0)
    elif a.c3:
        sys.exit(1 if test_c3() else 0)
    elif a.run:
        cmd_run(a.mmax, a.max_cost, a.out, a.workers)
    elif a.report:
        cmd_report(a.out, a.lo, a.hi)
    elif a.cross_check:
        sys.exit(1 if cmd_cross_check(a.out, a.lo, a.hi, a.workers) else 0)
    elif a.witnesses:
        sys.exit(1 if cmd_witnesses(a.out, a.dump) else 0)
    elif a.conserve:
        sys.exit(1 if cmd_conserve(a.mmax, a.out) else 0)
    else:
        ap.error('pick --test / --c3 / --run / --report / --cross-check'
                 ' / --witnesses / --conserve')


if __name__ == '__main__':
    main()
