"""Flip-sensitivity analysis: are the surviving margins independent battles or a
tensioned membrane?

For the champion's satisfying vertices S (d >= 0), enumerate every valid
single-arc flip (add / delete / reverse, keeping out-degree >= 8 and no
digons). For each target t in S, collect the flips that lower d(t) by >= 1 and
measure their side effects on the rest of S:

  M[t][u] = mean over those flips of delta d(u)

Nearly-diagonal M -> independent battles (optimism justified).
Fat off-diagonal M -> membrane: sinking one survivor lifts its neighbours.

Also reports, per target, the single flip minimising the TOTAL excess change
(collateral counted over all 50 vertices, since a flip can push a currently
negative vertex up to 0), and the N++ co-membership table among S — the
suspected carrier of the membrane tension.

Usage: python3 sensitivity.py [sha1-prefix]   (default: current champion)
"""
import hashlib
import json
import os
import sys

import numpy as np

from evaluate import score, N

def margins(A):
    out1 = A.sum(1)
    R2 = (A @ A > 0) & (A == 0) & ~np.eye(N, dtype=bool)
    return R2.sum(1) - out1

def main():
    db = json.load(open(os.environ.get('SEYMOUR_DB', 'evolve_db.json')))
    entries = sorted((e for isl in db['islands'] for e in isl),
                     key=lambda e: e['score'][0])
    if len(sys.argv) > 1:
        pref = sys.argv[1]
        entries = [e for e in entries
                   if hashlib.sha1(e['code'].encode()).hexdigest().startswith(pref)]
        if not entries:
            print(f"no genome with hash prefix {pref}")
            sys.exit(1)
    e = entries[0]
    key = hashlib.sha1(e['code'].encode()).hexdigest()[:8]
    ns = {'np': np, 'N': N, 'score': score}
    exec(e['code'], ns)
    A0 = (np.asarray(ns['construct']()) != 0).astype(np.int64)
    d0 = margins(A0)
    excess0 = int(np.maximum(0, d0 + 1).sum())
    S = sorted((int(v) for v in np.nonzero(d0 >= 0)[0]),
               key=lambda v: -d0[v])
    print(f"genome {key} (gen {e['gen']}), excess {excess0}")
    print("survivors:", {v: f"{int(d0[v]):+d}" for v in S})

    out0 = A0.sum(1)
    flips = []
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if A0[i, j]:
                if out0[i] > 8:
                    flips.append(('del', i, j))
                    flips.append(('rev', i, j))
            elif not A0[j, i]:
                flips.append(('add', i, j))

    deltas = {}          # flip -> (delta margins vector, delta excess)
    for f in flips:
        kind, i, j = f
        A = A0.copy()
        if kind == 'del':
            A[i, j] = 0
        elif kind == 'add':
            A[i, j] = 1
        else:
            A[i, j] = 0
            A[j, i] = 1
        d = margins(A)
        deltas[f] = (d - d0, int(np.maximum(0, d + 1).sum()) - excess0)

    print(f"\n{len(flips)} valid flips enumerated")
    print("\nsensitivity matrix M[t][u] = mean delta d(u) over flips with "
          "delta d(t) <= -1  (rows: target t, cols: u; diag = own effect)")
    header = "        " + "".join(f"v{u:<7}" for u in S)
    print(header)
    for t in S:
        F = [f for f, (dd, _) in deltas.items() if dd[t] <= -1]
        if not F:
            print(f"v{t:<4} NO margin-reducing flip exists")
            continue
        row = [np.mean([deltas[f][0][u] for f in F]) for u in S]
        print(f"v{t:<4}" + "".join(f"{x:+7.2f} " for x in row)
              + f"   ({len(F)} flips)")

    print("\nbest single flip per target (minimum TOTAL excess change):")
    for t in S:
        F = [f for f, (dd, _) in deltas.items() if dd[t] <= -1]
        if not F:
            continue
        best = min(F, key=lambda f: deltas[f][1])
        dd, dE = deltas[best]
        side = {u: int(dd[u]) for u in S if u != t and dd[u]}
        print(f"  v{t:3d}: {best}  dE_total {dE:+d}, own {int(dd[t]):+d}, "
              f"side-effects on S {side or 'none'}")

    B = (A0 @ A0 > 0) & (A0 == 0) & ~np.eye(N, dtype=bool)
    print("\nN++ co-membership among survivors (t row: which u are in N++(t)):")
    for t in S:
        inn = [u for u in S if u != t and B[t, u]]
        outn = [u for u in S if u != t and A0[t, u]]
        print(f"  v{t:3d}: N++ contains {inn or '-'}   N+ contains {outn or '-'}")

if __name__ == '__main__':
    main()
