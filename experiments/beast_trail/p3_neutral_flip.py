#!/usr/bin/env python3
"""Candidate 3 test: neutral-flip rate by alpha band (rigidity reading).

For the n=50 witness (17cd7dc8): for every arc, try (a) deleting it and
(b) reversing it (when no digon results). A flip is NEUTRAL if the Seymour
excess is unchanged. Prediction (self-stress analogy): neutral rate is
significantly higher on high-alpha ("redundant cable") arcs than on
tight-SCC-internal ("stress skeleton") arcs.

Bands: tight-SCC-internal arcs (both ends in the 21-vertex tight SCC and
alpha=0) / other low-band arcs (alpha <= 6) / high-band arcs (alpha > 6;
for THIS witness the gap 7-9 is empty so this equals alpha >= 10 --
asserted below).

Output: experiments/beast_trail/p3_neutral_flip_results.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from lib.dist2core import adj_from_dict, exc_np               # noqa: E402
from slack_lib import compute_alpha_np                        # noqa: E402

# Source: experiments/beast_trail/slack_n50_17cd7dc8.json
# -> tight_nontrivial_sccs[0] (21-vertex tight SCC of witness graph_sha1
#    17cd7dc814daf872bab854419ace0c0bc0f5881b, file champion_28da4a1e.json)
TIGHT_SCC = {4, 5, 8, 12, 14, 15, 16, 18, 23, 24, 28, 29, 30, 31, 34, 36,
             37, 40, 44, 47, 48}


def main():
    w = json.load(open("/Users/srm/dev/seymour-excess/data/champion_28da4a1e.json"))
    A = adj_from_dict(w["adj"], len(w["adj"]))
    n = A.shape[0]
    base_exc = exc_np(A)
    alphas, _ = compute_alpha_np(A)
    # band-definition guard: this witness has an empty alpha gap at 7..9,
    # so "alpha > 6" and "alpha >= 10" coincide (audit fix 3)
    assert not any(7 <= a <= 9 for (a, _o) in alphas.values()), \
        "gap 7..9 not empty -- band definition must be revisited"

    def band(u, v, a):
        if a == 0 and u in TIGHT_SCC and v in TIGHT_SCC:
            return "tight_scc_internal"
        if a <= 6:
            return "low_other"
        return "high"

    stats = {b: {"arcs": 0, "del_neutral": 0, "rev_neutral": 0, "rev_possible": 0}
             for b in ("tight_scc_internal", "low_other", "high")}

    for (u, v), (a, _o) in alphas.items():
        b = band(u, v, a)
        stats[b]["arcs"] += 1
        # delete flip
        A[u, v] = 0
        if exc_np(A) == base_exc:
            stats[b]["del_neutral"] += 1
        A[u, v] = 1
        # reverse flip (only if no digon results)
        if not A[v, u]:
            stats[b]["rev_possible"] += 1
            A[u, v] = 0
            A[v, u] = 1
            if exc_np(A) == base_exc:
                stats[b]["rev_neutral"] += 1
            A[v, u] = 0
            A[u, v] = 1

    print(f"base excess = {base_exc}")
    out = {"witness_file": "champion_28da4a1e.json",
           "graph_sha1": "17cd7dc814daf872bab854419ace0c0bc0f5881b",
           "tight_scc_source": "slack_n50_17cd7dc8.json tight_nontrivial_sccs[0]",
           "base_excess": int(base_exc), "bands": {}}
    for b, s in stats.items():
        dr = s["del_neutral"] / s["arcs"] if s["arcs"] else None
        rr = s["rev_neutral"] / s["rev_possible"] if s["rev_possible"] else None
        out["bands"][b] = {**s, "del_neutral_rate": round(dr, 4) if dr is not None else None,
                           "rev_neutral_rate": round(rr, 4) if rr is not None else None}
        print(f"{b:20s}: arcs={s['arcs']:4d}  del-neutral={s['del_neutral']:4d} "
              f"({dr:.1%})  rev-neutral={s['rev_neutral']:4d}/{s['rev_possible']} "
              f"({rr:.1%})" if rr is not None else f"{b}: {s}")

    path = os.path.join(HERE, "p3_neutral_flip_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
