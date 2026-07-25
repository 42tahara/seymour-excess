"""P2: bimodal-alpha attribution + pure-ring binary-alpha unit test.

For witnesses with bimodal alpha histograms (low band vs high band separated
by a gap), classify each arc's endpoints and check whether:
  * high-alpha arcs terminate at tight-SCC vertices or keystones
  * the low band = "skeleton" (structural arcs), high band = "shots" (bullets)

For pure-ring (n=24, k=3, t=8) we verify alpha takes only the values {0, t}
across ALL arcs (not just forward inter-layer).
"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
import numpy as np
from slack_lib import adj_from_dict, compute_alpha_np, pure_ring, is_pure


def classify_bimodal(A: np.ndarray, gap_lo: int, gap_hi: int, tight_scc_verts: set):
    """gap_lo..gap_hi is the empty band separating low/high modes."""
    N = A.shape[0]
    alphas, basic = compute_alpha_np(A)
    d1 = basic["d1"].astype(int)
    m = basic["m"].astype(int)
    # tight-vertex set already given; keystones defined as m(v) >= 0 (m>=+1 rare in our data)
    keystones = set(int(v) for v in range(N) if int(m[v]) >= 0)

    low_arcs = [(u, v) for (u, v), (a, _) in alphas.items() if a <= gap_lo]
    high_arcs = [(u, v) for (u, v), (a, _) in alphas.items() if a >= gap_hi]

    def profile(arcs, name):
        term_in_scc = sum(1 for _, v in arcs if v in tight_scc_verts)
        term_is_keystone = sum(1 for _, v in arcs if v in keystones)
        term_is_deep_deficit = sum(1 for _, v in arcs if m[v] <= -10)
        src_in_scc = sum(1 for u, _ in arcs if u in tight_scc_verts)
        src_is_keystone = sum(1 for u, _ in arcs if u in keystones)
        src_is_deep_deficit = sum(1 for u, _ in arcs if m[u] <= -10)
        total = len(arcs)
        return {
            "band": name,
            "arc_count": total,
            "src_in_tight_scc": src_in_scc,
            "src_is_keystone(m>=0)": src_is_keystone,
            "src_deep_deficit(m<=-10)": src_is_deep_deficit,
            "term_in_tight_scc": term_in_scc,
            "term_is_keystone(m>=0)": term_is_keystone,
            "term_deep_deficit(m<=-10)": term_is_deep_deficit,
            "term_in_scc_frac": (term_in_scc / total) if total else None,
            "term_keystone_frac": (term_is_keystone / total) if total else None,
        }
    return {
        "keystones_count": len(keystones),
        "tight_scc_count": len(tight_scc_verts),
        "low": profile(low_arcs, f"alpha<={gap_lo}"),
        "high": profile(high_arcs, f"alpha>={gap_hi}"),
    }


def test_pure_ring_binary_alpha():
    """Assert alpha(u,v) in {0, t} for every arc in pure_ring(3, 8)."""
    k, t = 3, 8
    A = pure_ring(k, t)
    alphas, _ = compute_alpha_np(A)
    vals = Counter(a for a, _ in alphas.values())
    seen = sorted(vals.keys())
    assert seen == [0, t], f"pure-ring alpha values not {{0,t}}: {vals}"
    print(f"[PASS] pure_ring(k={k}, t={t}): alpha in {{0, {t}}} with counts {dict(vals)}")
    return {"k": k, "t": t, "alpha_values": dict(vals)}


def main():
    # First: pure-ring binary alpha test
    pr = test_pure_ring_binary_alpha()

    # bimodal witness classifications
    cases = [
        {"label": "n50_17cd7dc8",
         "path": os.path.join(DATA, "champion_28da4a1e.json"),
         "gap_lo": 6, "gap_hi": 10,
         "scc": {4,5,8,12,14,15,16,18,23,24,28,29,30,31,34,36,37,40,44,47,48}},
        {"label": "n53_dc922e89",
         "path": os.path.join(DATA, "champion_n53_ca40b396.json"),
         "gap_lo": 4, "gap_hi": 17,
         "scc": {0,1,2,4,5,11,13,14,15,16,17,18,25,29,30,32,33,34,35,36,37,38,39,40,41,42,46,48,49,50,51,52}},
    ]
    out_records = [{"pure_ring_binary_alpha_test": pr}]
    for c in cases:
        w = json.load(open(c["path"]))
        adj = w["adj"]
        N = int(w["N"]) if w.get("N") else len(adj)
        A = adj_from_dict(adj, N)
        report = classify_bimodal(A, c["gap_lo"], c["gap_hi"], c["scc"])
        rec = {"label": c["label"], "N": N, "gap": (c["gap_lo"], c["gap_hi"]),
               "classification": report}
        out_records.append(rec)
        print(f"\n===== {c['label']} (N={N}, gap=({c['gap_lo']}, {c['gap_hi']})) =====")
        print(f"  tight-SCC size = {report['tight_scc_count']}, keystones (m>=0) = {report['keystones_count']}")
        for band in ["low", "high"]:
            p = report[band]
            print(f"  band {p['band']} : {p['arc_count']} arcs")
            print(f"    src in tight-SCC: {p['src_in_tight_scc']}, keystone: {p['src_is_keystone(m>=0)']}, deep-deficit: {p['src_deep_deficit(m<=-10)']}")
            print(f"    term in tight-SCC: {p['term_in_tight_scc']} (frac {p['term_in_scc_frac']:.3f})"
                  f", keystone: {p['term_is_keystone(m>=0)']} (frac {p['term_keystone_frac']:.3f})"
                  f", deep-deficit: {p['term_deep_deficit(m<=-10)']}")

    out = os.path.join(os.path.dirname(__file__), "p2_bimodal.json")
    with open(out, "w") as f:
        json.dump(out_records, f, indent=2, default=int)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
