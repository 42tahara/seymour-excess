#!/usr/bin/env python3
"""Priority 2: exact accounting of the shot-arc identity (candidate 2).

Identity (one line from definitions, to be verified numerically):
    alpha(u,v) = m(u) + d1(u) - d1(v) + o(u,v)
              = d2(u) - d1(v) + o(u,v)
              = d2(u) - |N+(v) \\ N+(u)|          (r := |N+(v) \\ N+(u)|)

Tests, per witness:
  T1  identity check on EVERY arc, three independent implementation
      families (np / pp / sd from dist2core for d1,d2,o vs direct set
      computation of r). Mismatch = implementation bug.
  T2  distribution of r on high-alpha-band arcs (prediction: concentrated
      at r <= 2 — "perfect shots").
  T3  exact band accounting: high-band lower edge should equal
      min over high-band arcs of (d2(u) - r); and compare with
      min_{r=0 arcs} d2(u) (the pure perfect-shot floor). Explain n47's +1.
  T4  the gap's nature: verify NO arcs of intermediate character exist —
      per-arc scatter of (r, alpha); the gap [band_lo_absent .. band_hi_absent]
      must contain zero arcs, and we identify which (d2(u), r) combinations
      are absent.

Output: experiments/beast_trail/shot_arc_results.json + stdout summary.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from lib.dist2core import (                                   # noqa: E402
    adj_from_dict,
    d1_np, d1_pp, d1_sd,
    d2_np, d2_pp, d2_sd,
    o_np, o_pp, o_sd,
)
from slack_lib import pure_ring                               # noqa: E402

WITNESSES = [
    ("n47_ad1a1ee5", "data/champion_n47_a76a5072.json", None),
    ("n49_ead3c3c3", "data/champion_n49_ad5efc8b.json", None),
    ("n50_17cd7dc8", None, "n50-special"),
    ("n53_dc922e89", "data/champion_n53_ca40b396.json", None),
    ("n59_c44e402b", "data/champion_n59_24dc568c.json", None),
    ("pure_ring_n24", None, "pure-ring"),
]


def load_witness(path, special):
    if special == "pure-ring":
        return pure_ring(3, 8)
    if special == "n50-special":
        p = os.path.join(ROOT, "data", "champion_28da4a1e.json")
        w = json.load(open(p))
        return adj_from_dict(w["adj"], len(w["adj"]))
    w = json.load(open(os.path.join(ROOT, path)))
    adj = w["adj"]
    return adj_from_dict(adj, int(w["N"]) if w.get("N") else len(adj))


def r_direct(A, u, v):
    """|N+(v) \\ N+(u)| computed directly from row sets (4th implementation)."""
    n = len(A)
    Nv = {w for w in range(n) if A[v][w]}
    Nu = {w for w in range(n) if A[u][w]}
    return len(Nv - Nu)


def band_split(alpha_by_arc):
    """Find the largest contiguous absent run in the alpha histogram;
    return (gap_list, low_band_max, high_band_min)."""
    vals = sorted(set(alpha_by_arc.values()))
    present = set(vals)
    runs, cur = [], []
    for a in range(min(vals), max(vals) + 1):
        if a not in present:
            cur.append(a)
        else:
            if cur:
                runs.append(cur)
                cur = []
    if cur:
        runs.append(cur)
    big = max(runs, key=len) if runs else []
    if not big:
        return [], None, None
    return big, big[0] - 1, big[-1] + 1


def analyze(label, A):
    A = np.asarray(A)
    n = A.shape[0]
    Al = A.tolist()

    # --- three implementation families for alpha, plus direct-r formula ---
    fam = {}
    for name, (f1, f2, fo) in {
        "np": (d1_np, d2_np, o_np),
        "pp": (d1_pp, d2_pp, o_pp),
        "sd": (d1_sd, d2_sd, o_sd),
    }.items():
        d1 = list(f1(Al)) if name != "np" else f1(A).tolist()
        d2 = list(f2(Al)) if name != "np" else f2(A).tolist()
        o = fo(Al) if name != "np" else fo(A)
        alpha = {(u, v): d2[u] - d1[v] + o[(u, v)] for (u, v) in o}
        fam[name] = (d1, d2, alpha)

    d1, d2, alpha = fam["np"]
    arcs = list(alpha.keys())

    # T1: identity on every arc, all families vs direct r
    t1_mismatches = 0
    r_by_arc = {}
    for (u, v) in arcs:
        r = r_direct(Al, u, v)
        r_by_arc[(u, v)] = r
        for name, (d1f, d2f, alphaf) in fam.items():
            if alphaf[(u, v)] != d2f[u] - r:
                t1_mismatches += 1
    # cross-family agreement
    for (u, v) in arcs:
        assert fam["np"][2][(u, v)] == fam["pp"][2][(u, v)] == fam["sd"][2][(u, v)]

    # band structure
    gap, low_max, high_min = band_split(alpha)
    high_arcs = [(u, v) for (u, v) in arcs if alpha[(u, v)] >= high_min] \
        if high_min is not None else []
    low_arcs = [(u, v) for (u, v) in arcs if high_min is None
                or alpha[(u, v)] <= low_max]

    # T2: r distribution on high band vs low band
    from collections import Counter
    r_high = Counter(r_by_arc[a] for a in high_arcs)
    r_low = Counter(r_by_arc[a] for a in low_arcs)

    # T3: exact accounting
    if high_arcs:
        edge_from_accounting = min(d2[u] - r_by_arc[(u, v)] for (u, v) in high_arcs)
        r0_arcs = [(u, v) for (u, v) in high_arcs if r_by_arc[(u, v)] == 0]
        pure_shot_floor = min((d2[u] for (u, v) in r0_arcs), default=None)
        min_d2 = int(min(d2))
        argmin_edge = min(high_arcs, key=lambda a: d2[a[0]] - r_by_arc[a])
    else:
        edge_from_accounting = pure_shot_floor = min_d2 = argmin_edge = None

    # T4: gap nature — which (r, alpha) pairs exist; verify zero arcs in gap
    arcs_in_gap = [a for a in arcs if gap and gap[0] <= alpha[a] <= gap[-1]]
    # for the gap to be explained mechanically: high band = small r, low band = large r?
    r_ranges = {
        "high_band_r": [int(min(r_high)), int(max(r_high))] if r_high else None,
        "low_band_r": [int(min(r_low)), int(max(r_low))] if r_low else None,
    }

    return {
        "label": label, "n": int(n), "num_arcs": len(arcs),
        "t1_identity_mismatches": t1_mismatches,
        "gap": [int(g) for g in gap],
        "low_band_max": low_max, "high_band_min": high_min,
        "min_out_degree": int(min(d1)),
        "min_d2": min_d2,
        "t2_r_distribution_high_band": {str(k): r_high[k] for k in sorted(r_high)},
        "t2_r_distribution_low_band_head": {str(k): r_low[k] for k in sorted(r_low)[:6]},
        "t3_edge_from_accounting": edge_from_accounting,
        "t3_edge_matches_band": (edge_from_accounting == high_min),
        "t3_pure_shot_floor_min_d2_over_r0": pure_shot_floor,
        "t3_argmin_edge_arc": {"u": int(argmin_edge[0]), "v": int(argmin_edge[1]),
                               "d2_u": int(d2[argmin_edge[0]]),
                               "r": int(r_by_arc[argmin_edge])} if argmin_edge else None,
        "t4_arcs_in_gap": len(arcs_in_gap),
        "t4_r_ranges": r_ranges,
    }


def main():
    results = []
    for label, path, special in WITNESSES:
        A = load_witness(path, special)
        r = analyze(label, A)
        results.append(r)
        print(f"--- {label} (n={r['n']}, arcs={r['num_arcs']}) ---")
        print(f"  T1 identity mismatches: {r['t1_identity_mismatches']} (must be 0)")
        print(f"  band: low<= {r['low_band_max']}  gap={r['gap']}  high>= {r['high_band_min']}"
              f"  | min_out={r['min_out_degree']}  min_d2={r['min_d2']}")
        print(f"  T2 r dist (high band): {r['t2_r_distribution_high_band']}")
        print(f"  T3 edge accounting: min(d2(u)-r)={r['t3_edge_from_accounting']}"
              f"  matches band edge: {r['t3_edge_matches_band']}"
              f"  pure-shot floor (r=0): {r['t3_pure_shot_floor_min_d2_over_r0']}"
              f"  argmin arc: {r['t3_argmin_edge_arc']}")
        print(f"  T4 arcs in gap: {r['t4_arcs_in_gap']}  r ranges: {r['t4_r_ranges']}")
    out = os.path.join(HERE, "shot_arc_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=int)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
