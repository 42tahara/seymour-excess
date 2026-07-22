"""Post-hoc analysis of the evolution database: margin histograms, floors, history.

Genomes are stored as code in evolve_db.json and are deterministic, so any
statistic is recoverable after the fact without touching the running loop.

Usage: python3 analyze.py [top_k]     (default 6 distinct genomes)
"""
import hashlib
import json
import sys
from collections import Counter

import numpy as np

from evaluate import score, N

def margins(A):
    A = np.asarray(A).astype(np.int64)
    out1 = A.sum(1)
    R2 = (A @ A > 0) & (A == 0) & ~np.eye(N, dtype=bool)
    return R2.sum(1) - out1

def max_ratio(A):
    """max_v |N++(v)|/|N+(v)| — the mu-Seymour quantity. Proven floor for the
    max over v is gamma = 0.715538 (Huang-Peng 2024); conjectured floor is 1.
    A counterexample is exactly a graph where this max is < 1."""
    A = np.asarray(A).astype(np.int64)
    out1 = A.sum(1)
    R2 = (A @ A > 0) & (A == 0) & ~np.eye(N, dtype=bool)
    return float((R2.sum(1) / np.maximum(out1, 1)).max())

def main():
    import os
    top_k = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    db = json.load(open(os.environ.get('SEYMOUR_DB', 'evolve_db.json')))
    print(f"gen {db['gen']}")
    hist = db.get('history', [])
    if hist:
        marks = [hist[0]] + [h for i, h in enumerate(hist[1:], 1)
                             if h[1] != hist[i - 1][1]]
        print('champion trajectory (gen, total, nsat):', marks)

    entries = sorted((e for isl in db['islands'] for e in isl),
                     key=lambda e: e['score'][0])
    seen = set()
    print(f"\nmargin histograms of top {top_k} distinct genomes:")
    for e in entries:
        if len(seen) >= top_k:
            break
        key = hashlib.sha1(e['code'].encode()).hexdigest()[:8]
        if key in seen:
            continue
        seen.add(key)
        ns = {'np': np, 'N': N, 'score': score}
        try:
            exec(e['code'], ns)
            A = ns['construct']()
            d, r = margins(A), max_ratio(A)
        except Exception as ex:
            print(f"  {key}: exec failed ({type(ex).__name__})")
            continue
        pos = sorted((int(x) for x in d if x >= 0), reverse=True)
        cnt = Counter(int(x) for x in d)
        spread = '  '.join(f"d={k:+d}:{cnt[k]}" for k in sorted(cnt))
        print(f"  {key} gen {e['gen']:3d} total {e['score'][0]:6d} "
              f"excess {e['score'][2]:4d}  max-ratio {r:.3f}  "
              f"positive margins {pos or '(none!)'}")
        print(f"           full distribution: {spread}")
    print(f"\nE({N}) = min excess, r({N}) = min max-ratio over recorded genomes; "
          "proven bound: max-ratio >= 0.715538 (Huang-Peng 2024), conjectured >= 1.")

if __name__ == '__main__':
    main()
